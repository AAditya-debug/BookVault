# 📖 BookVault — Library Management System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Database-SQLite3](https://img.shields.io/badge/database-SQLite3-003B57.svg?logo=sqlite)](https://www.sqlite.org/)
[![Tests-Pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC.svg?logo=pytest)](https://docs.pytest.org/)
[![Architecture-Clean%20OOP](https://img.shields.io/badge/architecture-Clean%20OOP%20%26%20Service%20Layer-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**BookVault** is a production-grade, object-oriented Library Management System built in pure Python and SQLite. It simulates a modern library ecosystem—orchestrating catalog inventory, membership records, checkout/checkin transactions, real-time availability tracking, automated overdue auditing, statistical reporting, and CSV data export pipelines.

---

## 📌 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [Key Features](#-key-features)
- [Architecture & Design Principles](#-architecture--design-principles)
- [Database Design & Schema](#-database-design--schema)
- [Directory Structure](#-directory-structure)
- [Technology Stack](#-technology-stack)
- [Installation & Quickstart](#-installation--quickstart)
- [User Guide & CLI Walkthrough](#-user-guide--cli-walkthrough)
- [Testing Suite](#-testing-suite)
- [Comprehensive PDF Interview & Project Guide](#-comprehensive-pdf-interview--project-guide)
- [Future Roadmap](#-future-roadmap)
- [License](#-license)

---

## 🎯 Problem Statement

Small-to-medium libraries and resource centers often struggle with:
1. **Manual Record Keeping**: Paper logbooks or disorganized spreadsheets lead to inventory drift, lost books, and unreturned items.
2. **Double Borrowing & Inaccurate Stock**: Inability to prevent members from borrowing books that are already checked out or borrowing duplicates.
3. **No Overdue Visibility**: Lack of automated tracking for overdue loans and patron accountability.
4. **Data Isolation**: Difficulties in exporting clean analytical data and generating administrative KPIs.

---

## 💡 Solution Overview

**BookVault** provides a clean, robust, and ACID-compliant software solution:
- **Relational Integrity**: Enforced through SQLite foreign keys, unique constraints, and check constraints (`CHECK(available_copies >= 0)`).
- **Atomic Transactions**: Context-managed database transactions guarantee that book copy decrementing and loan creation happen together or fail safely.
- **Rich Interactive CLI**: Intuitive menu interface with dynamic ASCII table formatting, clear user feedback, and robust error trapping.
- **Audit & Analytics**: Real-time KPI summaries, top borrowed books leaderboard, category distribution, and one-click CSV exports.

---

## ✨ Key Features

### 📚 1. Book Management
- **Add New Books**: Title, author, unique ISBN-10/ISBN-13 validation, category, publication year, and total copies.
- **Edit Book Details**: Update title, author, category, ISBN, and adjust copy counts safely without violating active loan counts.
- **Delete Book**: Cascade-safe deletion with automatic checks preventing deletion if copies are actively checked out.
- **Multi-Vector Search**: Universal search across all attributes, plus targeted filtering by title, author, or category.
- **Real-Time Inventory**: Filter instant views for *Available Books* vs. *Currently Borrowed Books*.

### 👥 2. Member Management
- **Patron Registration**: Validate name, unique email address, international/local phone number, address, and customizable borrowing limit (default: 5 books).
- **Edit Member Profile**: Update contact details, borrowing limits, or toggle member activation status.
- **Remove Member**: Block deletion if member holds unreturned books.
- **Search Members**: Substring search by name, email, or phone.
- **Patron History**: View a complete chronological timeline of every book a member has borrowed and returned.

### 🔄 3. Borrowing & Return Operations
- **Borrow Workflow (Checkout)**:
  1. Validates member exists and is active.
  2. Verifies book exists and `available_copies > 0`.
  3. Enforces patron borrowing quota (`max_books_allowed`).
  4. Prevents duplicate concurrent loans of the same title by the same member.
  5. Atomically creates the `Loan` record and decrements available inventory.
- **Return Workflow (Checkin)**:
  1. Locates active loan by Loan ID or (Member ID + Book ID).
  2. Records return date and sets status to `RETURNED`.
  3. Atomically increments book available copies.
  4. Calculates overdue days if returned past the due date.
- **Overdue Detection**: Scans active loans where `due_date < current_date` and calculates overdue durations.

### 📊 4. Reports & Analytics
- **Executive KPI Dashboard**: Total titles, physical copies, borrowed copies, active members, active loans, and overdue counts.
- **Overdue Audit Report**: Detailed listing of patrons with delinquent books and days overdue.
- **Popularity Leaderboard**: Top most borrowed books based on historical checkout counts.
- **Category Breakdown**: Inventory distribution across book genres/categories.

### 💾 5. CSV Data Export
- Export **Books Catalog**, **Members Directory**, **Active Loans**, **Full History Ledger**, **Overdue Audit**, and **Most Borrowed Books**.
- **One-Click Batch Export**: Generates all 6 reports simultaneously with timestamped filenames in `data/exports/`.

---

## 🏛 Architecture & Design Principles

BookVault follows the **Layered Architecture** and **Single Responsibility Principle (SRP)**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│             app/cli/menu.py (Interactive CLI)               │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                      Service Layer                          │
│  app/services/library_service.py  •  report_service.py      │
│  app/services/validator.py (Input & Business Rule Engine)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    Domain Model Layer                       │
│    app/models/book.py  •  member.py  •  loan.py              │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  Data Access & Persistence                  │
│  app/database.py (DatabaseManager, Connection & TX Manager) │
│  data/bookvault.db (SQLite Relational Store)                │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Patterns Used:
- **Service Layer Pattern**: Decouples presentation logic from database queries and domain rules.
- **Unit of Work / Transaction Context**: `with db.transaction():` ensures ACID compliance for multi-table updates.
- **Domain Model Pattern**: Rich models (`Book`, `Member`, `Loan`) encapsulate business logic (e.g., `is_available`, `dynamic_status`, `overdue_days`).
- **Data Validation Strategy**: Centralized `InputValidator` ensures consistent regex and constraint checks across the system.

---

## 🗄 Database Design & Schema

BookVault uses a relational SQLite database with strict foreign key constraints enabled via `PRAGMA foreign_keys = ON;`.

### Entity Relationship Diagram (ERD)

```
       ┌────────────────────────┐
       │         books          │
       ├────────────────────────┤
       │ PK  id                 │◄───────────┐
       │     title              │            │
       │     author             │            │
       │ UK  isbn               │            │
       │     category           │            │ 1:N
       │     total_copies       │            │
       │     available_copies   │            │
       │     published_year     │            │
       │     created_at         │            │
       └────────────────────────┘            │
                                             │
                                   ┌─────────┴──────────────┐
                                   │         loans          │
                                   ├────────────────────────┤
                                   │ PK  id                 │
                                   │ FK  book_id            │
                                   │ FK  member_id          │
                                   │     borrow_date        │
                                   │     due_date           │
                                   │     return_date        │
                                   │     status             │
                                   └─────────┬──────────────┘
                                             │
       ┌────────────────────────┐            │ 1:N
       │        members         │            │
       ├────────────────────────┤            │
       │ PK  id                 │◄───────────┘
       │     name               │
       │ UK  email              │
       │     phone              │
       │     address            │
       │     max_books_allowed  │
       │     is_active          │
       │     created_at         │
       └────────────────────────┘
```

### SQL Schema Definition

```sql
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    total_copies INTEGER NOT NULL CHECK (total_copies >= 1),
    available_copies INTEGER NOT NULL CHECK (available_copies >= 0 AND available_copies <= total_copies),
    published_year INTEGER,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    address TEXT,
    max_books_allowed INTEGER NOT NULL DEFAULT 5 CHECK (max_books_allowed >= 1),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE RESTRICT,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE RESTRICT,
    borrow_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    return_date TEXT,
    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'RETURNED', 'OVERDUE'))
);

CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_members_email ON members(email);
CREATE INDEX IF NOT EXISTS idx_loans_book_id ON loans(book_id);
CREATE INDEX IF NOT EXISTS idx_loans_member_id ON loans(member_id);
CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);
```

---

## 📁 Directory Structure

```
BookVault/
├── app/
│   ├── __init__.py               # Package metadata and version info
│   ├── database.py               # DatabaseManager, connections, schemas, transactions
│   ├── models/                   # Domain entity models
│   │   ├── __init__.py
│   │   ├── book.py               # Book entity & inventory calculations
│   │   ├── member.py             # Member entity & borrowing limits
│   │   └── loan.py               # Loan entity, overdue logic, joined metadata
│   ├── services/                 # Business logic and coordination
│   │   ├── __init__.py
│   │   ├── library_service.py    # Book/Member CRUD, checkout, checkin, validation
│   │   ├── report_service.py     # Metrics aggregation, leaderboards, CSV bridge
│   │   └── validator.py          # Input validation (ISBN, email, phone, ranges)
│   ├── utils/                    # Common helper modules
│   │   ├── __init__.py
│   │   ├── csv_exporter.py       # Generic & typed CSV export pipeline
│   │   ├── date_helper.py        # Date calculations, due dates, overdue delta
│   │   └── exceptions.py         # Custom domain exceptions hierarchy
│   └── cli/                      # Interactive terminal presentation
│       ├── __init__.py
│       └── menu.py               # ASCII banner, table renderer, interactive menus
├── data/
│   ├── bookvault.db              # SQLite relational database (auto-created)
│   └── exports/                  # Directory for generated CSV files
├── tests/                        # Comprehensive automated test suite
│   ├── __init__.py
│   ├── conftest.py               # In-memory database & service fixtures
│   ├── test_models.py            # Unit tests for domain models
│   ├── test_validators.py        # Unit tests for regex & data validation
│   ├── test_database.py          # Database integrity & transaction tests
│   ├── test_library_service.py   # Business logic & borrowing workflow tests
│   ├── test_reports.py           # Report analytics & aggregation tests
│   └── test_csv_exporter.py      # CSV export file creation & structure tests
├── docs/                         # Documentation scripts
│   └── generate_guide_pdf.py     # PDF Interview & Project Guide generator
├── BookVault_Project_Understanding_and_Interview_Guide.pdf # Complete 12-page guide
├── main.py                       # Application bootstrap entry point
├── requirements.txt              # Project dependencies
├── .gitignore                    # Version control ignore rules
├── LICENSE                       # MIT License
└── README.md                     # Project documentation
```

---

## 🛠 Technology Stack

| Technology | Purpose | Rationale |
| :--- | :--- | :--- |
| **Python 3.10+** | Core Programming Language | Clean syntax, robust standard library, strong OOP capabilities. |
| **SQLite 3** | Relational Database Engine | Zero-configuration, serverless, atomic ACID guarantees, native Python support. |
| **SQL** | Data Definition & Querying | Declarative querying, JOIN operations, foreign key constraints, indexes. |
| **pytest** | Automated Testing | Industry standard for scalable, clean unit and integration testing. |
| **ReportLab** | PDF Generation | Programmatic PDF creation for the project and interview guide. |
| **Git / GitHub** | Version Control | Industry standard tracking and portfolio presentation. |

---

## 🚀 Installation & Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/bookvault.git
cd bookvault
```

### 2. Set Up Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```
*(On first launch, BookVault will automatically initialize the database schema and populate realistic demo data).*

---

## 🖥 User Guide & CLI Walkthrough

When you launch `python main.py`, the interactive terminal interface appears:

```
========================================================================
       📖  BOOKVAULT — LIBRARY MANAGEMENT SYSTEM  📖       
           Clean Python Architecture • SQLite Relational DB
========================================================================

[MAIN MENU]
  1. 📚 Book Management
  2. 👥 Member Management
  3. 🔄 Borrow & Return Operations
  4. 📊 Analytics & Reports
  5. 💾 CSV Data Export
  6. ⚙️  Database & Demo Seeding
  0. 🚪 Exit Application

Enter your choice (0-6): 
```

### Example 1: Borrowing a Book (Checkout)
1. Select **3 (Borrow & Return Operations)** -> **1 (Borrow a Book)**.
2. Enter Member ID (e.g., `1`) and Book ID (e.g., `4`).
3. Set loan duration in days (e.g., `14`).
4. BookVault automatically verifies member active status, borrowing quota, book availability, records the loan, and updates available stock.

### Example 2: Viewing the KPI Dashboard
1. Select **4 (Analytics & Reports)** -> **1 (Library KPI Dashboard Summary)**.
2. Displays instant snapshot:
```
--- [ LIBRARY KPI DASHBOARD ] -------------------------------------------

📚 [BOOKS INVENTORY]
   • Total Unique Titles : 10
   • Total Physical Copies: 47
   • Available Copies     : 44
   • Borrowed Copies      : 3

👥 [MEMBERSHIP STATS]
   • Total Registered     : 5
   • Active Members       : 5
   • Inactive Members     : 0

🔄 [LOAN TRANSACTIONS]
   • Total Transactions   : 4
   • Currently Active     : 2
   • Successfully Returned: 1
   • Currently Overdue    : 1 ⚠️
```

---

## 🧪 Testing Suite

BookVault includes a 100% passing automated test suite with **28 tests** covering all layers using in-memory SQLite fixtures.

Run all tests:
```bash
pytest -v
```

Run test suite with execution details:
```bash
pytest -v --tb=short
```

---

## 📄 Comprehensive PDF Interview & Project Guide

A complete, 12-page PDF document entitled **`BookVault — Project Understanding & Interview Guide.pdf`** is included with the project.

It provides:
- Complete breakdown of all 22 system architecture components in simple English.
- End-to-end data lifecycle trace: *User Input → Python CLI → Validator → Service Layer → Database Transaction → Result Output*.
- **Interview Elevator Pitches**: 30-second, 1-minute, and 2-minute project overviews.
- **20+ Technical Interview Questions & Answers** covering SQLite concurrency, OOP principles, foreign keys, and transaction management.
- **Emergency One-Page Revision Sheet** for rapid interview prep.

To re-generate the PDF at any time:
```bash
python docs/generate_guide_pdf.py
```

---

## 🔮 Future Roadmap

- [ ] **Web Interface**: REST API with FastAPI and responsive frontend dashboard.
- [ ] **Email Notifications**: Automated email reminders for upcoming and overdue returns.
- [ ] **Fine Management System**: Configurable monetary penalty calculations for late returns.
- [ ] **Barcode & QR Code Scanning**: Camera / scanner input for ISBN and patron ID cards.

---

## 📜 License

This project is open-source software licensed under the [MIT License](LICENSE).
