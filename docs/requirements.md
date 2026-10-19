# Requirements Specification: Library Management System

## 1. Purpose
A small system that lets a library librarian manage books, members and loans, and
calculates fines for late returns.

## 2. Stakeholders
| Stakeholder | Interest |
|---|---|
| Librarian | Add books/members, issue and receive books |
| Library member | Borrow and return books |

## 3. Functional requirements
| ID | Requirement | Priority |
|---|---|---|
| FR-1 | The system shall allow adding a book with title, author, ISBN and number of copies. | Must |
| FR-2 | The system shall reject a book whose ISBN already exists. | Must |
| FR-3 | The system shall allow registering a member with name and a unique e-mail. | Must |
| FR-4 | The system shall allow searching books by title, author or ISBN. | Must |
| FR-5 | The system shall set the due date to 14 days after borrowing. | Must |
| FR-6 | The system shall allow a member at most 3 active loans. | Must |
| FR-7 | The system shall not allow borrowing when no copy is available. | Must |
| FR-8 | The system shall charge a fine of 2 units per day for late returns. | Must |
| FR-9 | The system shall list all overdue loans. | Should |
| FR-10 | The system shall not allow the same loan to be returned twice. | Must |

## 4. Non-functional requirements
| ID | Requirement |
|---|---|
| NFR-1 | Maintainability: presentation, business logic and data access are separate layers. |
| NFR-2 | Testability: business rules are covered by automated unit tests. |
| NFR-3 | Portability: runs on any OS with Python 3.10+ and no external services. |
| NFR-4 | Data integrity: the database enforces unique ISBN/e-mail and non-negative stock. |

## 5. Use cases
| Use case | Actor | Main flow |
|---|---|---|
| Borrow a book | Librarian | Find member and book, system checks rules (FR-5 to FR-7), loan is created, stock decreases. |
| Return a book | Librarian | Enter loan ID, system records return date, increases stock, shows fine (FR-8). |
| Search books | Librarian | Enter query, system shows matching books and availability. |

## 6. Out of scope (possible future work)
Authentication, reservations, a web interface, e-mail reminders.

## 7. Traceability
Each requirement is implemented in `library/services.py` and verified in `tests/test_services.py`.
