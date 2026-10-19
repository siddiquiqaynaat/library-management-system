from datetime import date, timedelta

import pytest

from library.database import Database
from library.services import (
    DuplicateError, LibraryService, NotFoundError, RuleViolationError,
    FINE_PER_DAY, LOAN_DAYS, MAX_ACTIVE_LOANS,
)

TODAY = date(2026, 1, 10)


@pytest.fixture
def service():
    db = Database(":memory:")
    yield LibraryService(db)
    db.close()


@pytest.fixture
def setup(service):
    book = service.add_book("Clean Code", "Robert C. Martin", "9780132350884", copies=2)
    member = service.add_member("Asha", "asha@example.com")
    return service, book, member


def test_add_book_and_search(service):
    service.add_book("Clean Code", "Robert C. Martin", "111")
    assert len(service.search_books("clean")) == 1
    assert service.search_books("nothing") == []


def test_duplicate_isbn_rejected(service):
    service.add_book("A", "B", "111")
    with pytest.raises(DuplicateError):
        service.add_book("C", "D", "111")


def test_invalid_book_rejected(service):
    with pytest.raises(RuleViolationError):
        service.add_book("", "Author", "1")
    with pytest.raises(RuleViolationError):
        service.add_book("T", "A", "1", copies=0)


def test_invalid_member_rejected(service):
    with pytest.raises(RuleViolationError):
        service.add_member("Name", "not-an-email")


def test_borrow_reduces_available_copies(setup):
    service, book, member = setup
    loan = service.borrow_book(member.id, book.id, today=TODAY)
    assert loan.due_on == TODAY + timedelta(days=LOAN_DAYS)
    assert service.get_book(book.id).copies_available == 1


def test_cannot_borrow_when_no_copies(setup):
    service, book, member = setup
    other = service.add_member("Ravi", "ravi@example.com")
    service.borrow_book(member.id, book.id, today=TODAY)
    service.borrow_book(other.id, book.id, today=TODAY)
    third = service.add_member("Meera", "meera@example.com")
    with pytest.raises(RuleViolationError):
        service.borrow_book(third.id, book.id, today=TODAY)


def test_loan_limit_per_member(service):
    member = service.add_member("Asha", "asha@example.com")
    for i in range(MAX_ACTIVE_LOANS):
        book = service.add_book(f"Book {i}", "Author", f"isbn-{i}")
        service.borrow_book(member.id, book.id, today=TODAY)
    extra = service.add_book("One too many", "Author", "isbn-x")
    with pytest.raises(RuleViolationError):
        service.borrow_book(member.id, extra.id, today=TODAY)


def test_unknown_member_or_book(setup):
    service, book, member = setup
    with pytest.raises(NotFoundError):
        service.borrow_book(999, book.id)
    with pytest.raises(NotFoundError):
        service.borrow_book(member.id, 999)


def test_return_on_time_has_no_fine(setup):
    service, book, member = setup
    loan = service.borrow_book(member.id, book.id, today=TODAY)
    fine = service.return_book(loan.id, today=TODAY + timedelta(days=LOAN_DAYS))
    assert fine == 0
    assert service.get_book(book.id).copies_available == 2


def test_return_late_has_fine(setup):
    service, book, member = setup
    loan = service.borrow_book(member.id, book.id, today=TODAY)
    fine = service.return_book(loan.id, today=TODAY + timedelta(days=LOAN_DAYS + 3))
    assert fine == 3 * FINE_PER_DAY


def test_cannot_return_twice(setup):
    service, book, member = setup
    loan = service.borrow_book(member.id, book.id, today=TODAY)
    service.return_book(loan.id, today=TODAY)
    with pytest.raises(RuleViolationError):
        service.return_book(loan.id, today=TODAY)


def test_overdue_list(setup):
    service, book, member = setup
    loan = service.borrow_book(member.id, book.id, today=TODAY)
    assert service.list_overdue(today=TODAY) == []
    overdue = service.list_overdue(today=TODAY + timedelta(days=LOAN_DAYS + 1))
    assert [l.id for l in overdue] == [loan.id]
