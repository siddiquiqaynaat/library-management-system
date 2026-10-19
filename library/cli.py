"""Presentation layer: a command line interface on top of LibraryService."""
import argparse
import sys

from .database import Database
from .services import LibraryError, LibraryService


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="library", description="Library Management System")
    p.add_argument("--db", default="library.db", help="path to the SQLite file")
    sub = p.add_subparsers(dest="command", required=True)

    b = sub.add_parser("add-book", help="add a book")
    b.add_argument("title")
    b.add_argument("author")
    b.add_argument("isbn")
    b.add_argument("--copies", type=int, default=1)

    m = sub.add_parser("add-member", help="register a member")
    m.add_argument("name")
    m.add_argument("email")

    br = sub.add_parser("borrow", help="borrow a book")
    br.add_argument("member_id", type=int)
    br.add_argument("book_id", type=int)

    r = sub.add_parser("return", help="return a book")
    r.add_argument("loan_id", type=int)

    s = sub.add_parser("search", help="search books")
    s.add_argument("query")

    sub.add_parser("overdue", help="list overdue loans")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    db = Database(args.db)
    service = LibraryService(db)
    try:
        if args.command == "add-book":
            book = service.add_book(args.title, args.author, args.isbn, args.copies)
            print(f"Added book #{book.id}: {book.title} ({book.copies_total} copies)")
        elif args.command == "add-member":
            member = service.add_member(args.name, args.email)
            print(f"Registered member #{member.id}: {member.name}")
        elif args.command == "borrow":
            loan = service.borrow_book(args.member_id, args.book_id)
            print(f"Loan #{loan.id} created. Due on {loan.due_on}.")
        elif args.command == "return":
            fine = service.return_book(args.loan_id)
            print("Returned on time." if fine == 0 else f"Returned late. Fine: {fine}")
        elif args.command == "search":
            for b in service.search_books(args.query):
                print(f"#{b.id} {b.title} by {b.author} [{b.copies_available}/{b.copies_total} available]")
        elif args.command == "overdue":
            for loan in service.list_overdue():
                print(f"Loan #{loan.id}: book {loan.book_id}, member {loan.member_id}, due {loan.due_on}")
        return 0
    except LibraryError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
