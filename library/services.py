"""Business logic layer. All rules from docs/requirements.md live here."""
import sqlite3
from datetime import date, timedelta
from typing import List, Optional

from .database import Database
from .models import Book, Loan, Member

LOAN_DAYS = 14          # FR-5: loan period
MAX_ACTIVE_LOANS = 3    # FR-6: limit per member
FINE_PER_DAY = 2        # FR-8: fine per overdue day


class LibraryError(Exception):
    """Base class for all business rule violations."""


class NotFoundError(LibraryError):
    pass


class DuplicateError(LibraryError):
    pass


class RuleViolationError(LibraryError):
    pass


def _book(row) -> Book:
    return Book(row["id"], row["title"], row["author"], row["isbn"],
                row["copies_total"], row["copies_available"])


def _loan(row) -> Loan:
    returned = date.fromisoformat(row["returned_on"]) if row["returned_on"] else None
    return Loan(row["id"], row["book_id"], row["member_id"],
                date.fromisoformat(row["borrowed_on"]),
                date.fromisoformat(row["due_on"]), returned)


class LibraryService:
    def __init__(self, db: Database):
        self.db = db

    # ---- books -------------------------------------------------------
    def add_book(self, title: str, author: str, isbn: str, copies: int = 1) -> Book:
        if not title.strip() or not author.strip() or not isbn.strip():
            raise RuleViolationError("Title, author and ISBN are required.")
        if copies < 1:
            raise RuleViolationError("A book needs at least one copy.")
        try:
            cur = self.db.conn.execute(
                "INSERT INTO books (title, author, isbn, copies_total, copies_available) "
                "VALUES (?, ?, ?, ?, ?)", (title.strip(), author.strip(), isbn.strip(), copies, copies))
            self.db.conn.commit()
        except sqlite3.IntegrityError:
            raise DuplicateError(f"A book with ISBN {isbn} already exists.")
        return self.get_book(cur.lastrowid)

    def get_book(self, book_id: int) -> Book:
        row = self.db.conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
        if row is None:
            raise NotFoundError(f"Book {book_id} not found.")
        return _book(row)

    def search_books(self, query: str) -> List[Book]:
        like = f"%{query.strip()}%"
        rows = self.db.conn.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? ORDER BY title",
            (like, like, like)).fetchall()
        return [_book(r) for r in rows]

    # ---- members -----------------------------------------------------
    def add_member(self, name: str, email: str) -> Member:
        if not name.strip() or "@" not in email:
            raise RuleViolationError("A valid name and e-mail are required.")
        try:
            cur = self.db.conn.execute(
                "INSERT INTO members (name, email) VALUES (?, ?)", (name.strip(), email.strip()))
            self.db.conn.commit()
        except sqlite3.IntegrityError:
            raise DuplicateError(f"A member with e-mail {email} already exists.")
        return Member(cur.lastrowid, name.strip(), email.strip())

    def _require_member(self, member_id: int) -> None:
        if self.db.conn.execute("SELECT 1 FROM members WHERE id = ?", (member_id,)).fetchone() is None:
            raise NotFoundError(f"Member {member_id} not found.")

    # ---- loans -------------------------------------------------------
    def active_loans_of(self, member_id: int) -> int:
        return self.db.conn.execute(
            "SELECT COUNT(*) FROM loans WHERE member_id = ? AND returned_on IS NULL",
            (member_id,)).fetchone()[0]

    def borrow_book(self, member_id: int, book_id: int, today: Optional[date] = None) -> Loan:
        today = today or date.today()
        self._require_member(member_id)
        book = self.get_book(book_id)
        if book.copies_available < 1:
            raise RuleViolationError("No copies of this book are available.")
        if self.active_loans_of(member_id) >= MAX_ACTIVE_LOANS:
            raise RuleViolationError(f"Member already has {MAX_ACTIVE_LOANS} active loans.")
        due = today + timedelta(days=LOAN_DAYS)
        cur = self.db.conn.execute(
            "INSERT INTO loans (book_id, member_id, borrowed_on, due_on) VALUES (?, ?, ?, ?)",
            (book_id, member_id, today.isoformat(), due.isoformat()))
        self.db.conn.execute(
            "UPDATE books SET copies_available = copies_available - 1 WHERE id = ?", (book_id,))
        self.db.conn.commit()
        return Loan(cur.lastrowid, book_id, member_id, today, due)

    def return_book(self, loan_id: int, today: Optional[date] = None) -> int:
        """Return a book and get back the fine (0 if on time)."""
        today = today or date.today()
        row = self.db.conn.execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone()
        if row is None:
            raise NotFoundError(f"Loan {loan_id} not found.")
        loan = _loan(row)
        if loan.returned_on is not None:
            raise RuleViolationError("This loan was already returned.")
        self.db.conn.execute(
            "UPDATE loans SET returned_on = ? WHERE id = ?", (today.isoformat(), loan_id))
        self.db.conn.execute(
            "UPDATE books SET copies_available = copies_available + 1 WHERE id = ?", (loan.book_id,))
        self.db.conn.commit()
        return self.calculate_fine(loan.due_on, today)

    @staticmethod
    def calculate_fine(due_on: date, returned_on: date) -> int:
        late_days = (returned_on - due_on).days
        return max(0, late_days) * FINE_PER_DAY

    def list_overdue(self, today: Optional[date] = None) -> List[Loan]:
        today = today or date.today()
        rows = self.db.conn.execute(
            "SELECT * FROM loans WHERE returned_on IS NULL AND due_on < ? ORDER BY due_on",
            (today.isoformat(),)).fetchall()
        return [_loan(r) for r in rows]
