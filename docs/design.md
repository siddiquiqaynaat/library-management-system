# Design: Library Management System

## Architecture
Three layers, each depending only on the layer below it.

```mermaid
flowchart TD
    CLI["cli.py (presentation)"] --> SVC["services.py (business rules)"]
    SVC --> DB["database.py (SQLite data access)"]
    SVC --> M["models.py (domain objects)"]
```

## Class diagram
```mermaid
classDiagram
    class Book {
        +int id
        +str title
        +str author
        +str isbn
        +int copies_total
        +int copies_available
    }
    class Member {
        +int id
        +str name
        +str email
    }
    class Loan {
        +int id
        +int book_id
        +int member_id
        +date borrowed_on
        +date due_on
        +date returned_on
    }
    class LibraryService {
        +add_book()
        +add_member()
        +search_books()
        +borrow_book()
        +return_book()
        +list_overdue()
        +calculate_fine()
    }
    Member "1" --> "0..3" Loan : has active
    Book "1" --> "0..*" Loan : lent in
    LibraryService ..> Book
    LibraryService ..> Member
    LibraryService ..> Loan
```

## Sequence: borrowing a book
```mermaid
sequenceDiagram
    actor L as Librarian
    participant C as CLI
    participant S as LibraryService
    participant D as Database
    L->>C: borrow member_id book_id
    C->>S: borrow_book()
    S->>D: member exists? book available?
    S->>S: check loan limit (max 3)
    S->>D: insert loan, decrease copies
    S-->>C: Loan (due in 14 days)
    C-->>L: "Loan created. Due on ..."
```

## Design decisions
- **Layering** keeps business rules independent from the CLI, so a web UI can be added later.
- **Custom exceptions** (`NotFoundError`, `DuplicateError`, `RuleViolationError`) make errors explicit and testable.
- **Date injection** (`today` parameter) makes time-dependent rules such as fines easy to test.
- **SQLite constraints** are a second safety net behind the Python checks.
