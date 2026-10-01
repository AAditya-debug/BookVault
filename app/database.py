"""
Database Manager for BookVault.
Handles SQLite connection pooling, schema initialization, PRAGMA enforcement,
transactions, and parameterized query execution.
"""
import os
import sqlite3
from typing import Any, List, Optional, Tuple, Dict
from contextlib import contextmanager
from app.utils.exceptions import DatabaseError


DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "bookvault.db"
)


class DatabaseManager:
    """Manages SQLite database lifecycle, schema, and SQL execution."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._mem_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._mem_conn = sqlite3.connect(":memory:")
            self._mem_conn.row_factory = sqlite3.Row
            self._mem_conn.execute("PRAGMA foreign_keys = ON;")
        else:
            self._ensure_data_directory()
        self.initialize_schema()


    def _ensure_data_directory(self) -> None:
        """Ensures the parent folder for the database file exists."""
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """
        Creates and returns a SQLite connection with foreign keys enabled
        and sqlite3.Row row_factory.
        """
        if self.db_path == ":memory:":
            return self._mem_conn

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to connect to database at {self.db_path}: {exc}") from exc

    @contextmanager
    def transaction(self):
        """Context manager providing an atomic database transaction."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as exc:
            conn.rollback()
            raise exc
        finally:
            if self.db_path != ":memory:":
                conn.close()

    def initialize_schema(self) -> None:
        """Initializes tables, constraints, and indexes if they do not exist."""
        schema_sql = """
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
        CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
        CREATE INDEX IF NOT EXISTS idx_books_category ON books(category);
        CREATE INDEX IF NOT EXISTS idx_members_email ON members(email);
        CREATE INDEX IF NOT EXISTS idx_loans_book_id ON loans(book_id);
        CREATE INDEX IF NOT EXISTS idx_loans_member_id ON loans(member_id);
        CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);
        """
        with self.transaction() as conn:
            conn.executescript(schema_sql)

    def execute(self, query: str, params: Tuple[Any, ...] = ()) -> int:
        """
        Executes an INSERT, UPDATE, or DELETE query.
        Returns the lastrowid for INSERTs, or rowcount for updates/deletes.
        """
        with self.transaction() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
            except sqlite3.IntegrityError as exc:
                raise DatabaseError(f"Database integrity violation: {exc}") from exc
            except sqlite3.Error as exc:
                raise DatabaseError(f"Database query error: {exc}") from exc

    def fetchone(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
        """Executes a SELECT query and returns a single sqlite3.Row or None."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to fetch record: {exc}") from exc
        finally:
            if self.db_path != ":memory:":
                conn.close()

    def fetchall(self, query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        """Executes a SELECT query and returns all matching sqlite3.Row records."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Failed to fetch records: {exc}") from exc
        finally:
            if self.db_path != ":memory:":
                conn.close()

    def reset_database(self) -> None:
        """Drops all tables and recreates the schema. Use for clean testing."""
        drop_sql = """
        DROP TABLE IF EXISTS loans;
        DROP TABLE IF EXISTS members;
        DROP TABLE IF EXISTS books;
        """
        with self.transaction() as conn:
            conn.executescript(drop_sql)
        self.initialize_schema()

    def seed_sample_data(self) -> Dict[str, int]:
        """Seeds initial realistic sample books and members if database is empty."""
        existing_books = self.fetchone("SELECT COUNT(*) as count FROM books")
        if existing_books and existing_books["count"] > 0:
            return {"books": 0, "members": 0, "loans": 0}

        sample_books = [
            ("Clean Code", "Robert C. Martin", "9780132350884", "Software Engineering", 5, 5, 2008),
            ("The Pragmatic Programmer", "Andrew Hunt & David Thomas", "9780201616224", "Software Engineering", 4, 4, 1999),
            ("Design Patterns: Elements of Reusable Object-Oriented Software", "Erich Gamma et al.", "9780201633610", "Computer Science", 3, 3, 1994),
            ("Fluent Python", "Luciano Ramalho", "9781491946008", "Programming", 4, 4, 2015),
            ("Introduction to Algorithms", "Thomas H. Cormen et al.", "9780262033848", "Computer Science", 3, 3, 2009),
            ("Sapiens: A Brief History of Humankind", "Yuval Noah Harari", "9780062316097", "History", 6, 6, 2014),
            ("Atomic Habits", "James Clear", "9780735211292", "Self-Help", 8, 8, 2018),
            ("1984", "George Orwell", "9780451524935", "Fiction", 5, 5, 1949),
            ("To Kill a Mockingbird", "Harper Lee", "9780060935467", "Fiction", 4, 4, 1960),
            ("Thinking, Fast and Slow", "Daniel Kahneman", "9780374533557", "Psychology", 5, 5, 2011),
        ]

        sample_members = [
            ("Alice Johnson", "alice.johnson@example.com", "+1-555-0101", "124 Maple St, Springfield", 5),
            ("Bob Smith", "bob.smith@example.com", "+1-555-0102", "456 Oak Ave, Springfield", 5),
            ("Charlie Brown", "charlie.brown@example.com", "+1-555-0103", "789 Pine Rd, Metropolis", 3),
            ("Diana Prince", "diana.prince@example.com", "+1-555-0104", "101 Gateway Blvd, Gotham", 5),
            ("Ethan Hunt", "ethan.hunt@example.com", "+1-555-0105", "202 Mission Way, Langley", 4),
        ]

        from app.utils.date_helper import get_current_timestamp_str, get_current_date_str, calculate_due_date
        now = get_current_timestamp_str()
        today = get_current_date_str()

        with self.transaction() as conn:
            cursor = conn.cursor()
            for title, author, isbn, cat, total, avail, yr in sample_books:
                cursor.execute(
                    """
                    INSERT INTO books (title, author, isbn, category, total_copies, available_copies, published_year, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (title, author, isbn, cat, total, avail, yr, now),
                )

            for name, email, phone, addr, limit in sample_members:
                cursor.execute(
                    """
                    INSERT INTO members (name, email, phone, address, max_books_allowed, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                    """,
                    (name, email, phone, addr, limit, now),
                )

            # Insert sample loans: 1 active, 1 returned, 1 overdue
            # Active loan: Alice borrows Clean Code
            cursor.execute(
                """
                INSERT INTO loans (book_id, member_id, borrow_date, due_date, return_date, status)
                VALUES (1, 1, ?, ?, NULL, 'ACTIVE')
                """,
                (today, calculate_due_date(today, 14)),
            )
            cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE id = 1")

            # Overdue loan: Bob borrowed Pragmatic Programmer 30 days ago
            past_date = "2026-08-01"
            past_due = "2026-08-15"
            cursor.execute(
                """
                INSERT INTO loans (book_id, member_id, borrow_date, due_date, return_date, status)
                VALUES (2, 2, ?, ?, NULL, 'OVERDUE')
                """,
                (past_date, past_due),
            )
            cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE id = 2")

            # Returned loan: Charlie borrowed & returned Sapiens
            cursor.execute(
                """
                INSERT INTO loans (book_id, member_id, borrow_date, due_date, return_date, status)
                VALUES (6, 3, '2026-08-10', '2026-08-24', '2026-08-20', 'RETURNED')
                """
            )

        return {
            "books": len(sample_books),
            "members": len(sample_members),
            "loans": 3,
        }
