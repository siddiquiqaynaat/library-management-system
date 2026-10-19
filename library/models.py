"""Domain models (plain data classes, no database code here)."""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Book:
    id: int
    title: str
    author: str
    isbn: str
    copies_total: int
    copies_available: int


@dataclass
class Member:
    id: int
    name: str
    email: str


@dataclass
class Loan:
    id: int
    book_id: int
    member_id: int
    borrowed_on: date
    due_on: date
    returned_on: Optional[date] = None
