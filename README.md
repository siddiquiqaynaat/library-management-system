# Library Management System

A command-line library system built with Python and SQLite to practise requirements
engineering, layered design and automated testing.

![CI](https://github.com/siddiquiqaynaat/library-management-system/actions/workflows/ci.yml/badge.svg)

> Learning project built with AI assistance (Claude) as a starting point, then reviewed and extended by me.

## Features
- Add books (with multiple copies) and register members
- Search by title, author or ISBN
- Borrow and return books with a 14-day loan period
- Limit of 3 active loans per member
- Automatic fine calculation for late returns
- List of overdue loans

## Technologies
Python 3.10+, SQLite, argparse, pytest, GitHub Actions (CI)

## Getting started
```bash
git clone https://github.com/siddiquiqaynaat/library-management-system.git
cd library-management-system
pip install -r requirements.txt

python -m library add-book "Clean Code" "Robert C. Martin" 9780132350884 --copies 2
python -m library add-member "Asha" asha@example.com
python -m library borrow 1 1
python -m library search clean
python -m library overdue
python -m library return 1
```

## Run the tests
```bash
pytest -v
```

## Project structure
```
library/      models.py, database.py, services.py, cli.py
tests/        unit tests for all business rules
docs/         requirements.md, design.md (UML diagrams)
.github/      CI workflow that runs the tests on every push
```

## Software engineering documentation
- [Requirements specification](docs/requirements.md)
- [Design and UML diagrams](docs/design.md)

## What I learned
- Writing requirements first and tracing them to code and tests
- Separating presentation, business logic and data access
- Testing business rules, including time-dependent behaviour

## Future work
Web interface, authentication, reservations, e-mail reminders.
