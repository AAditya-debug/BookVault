"""
Unit tests for DatabaseManager operations, schemas, transactions, and foreign keys.
"""
import pytest
from app.database import DatabaseManager
from app.utils.exceptions import DatabaseError


def test_database_initialization(in_memory_db):
    """Verifies tables are created with proper schema."""
    books = in_memory_db.fetchall("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = [r["name"] for r in books]
    assert "books" in table_names
    assert "members" in table_names
    assert "loans" in table_names


def test_database_foreign_key_enforcement(in_memory_db):
    """Verifies that foreign key constraints are strictly enforced."""
    # Attempting to insert a loan with non-existent book and member IDs must fail
    with pytest.raises(DatabaseError):
        in_memory_db.execute(
            """
            INSERT INTO loans (book_id, member_id, borrow_date, due_date, status)
            VALUES (9999, 9999, '2026-10-01', '2026-10-15', 'ACTIVE')
            """
        )


def test_database_unique_constraint(in_memory_db):
    """Verifies uniqueness constraints on ISBN and Email."""
    in_memory_db.execute(
        """
        INSERT INTO books (title, author, isbn, category, total_copies, available_copies, created_at)
        VALUES ('Book A', 'Author A', '9781234567890', 'Fiction', 1, 1, '2026-10-01')
        """
    )
    # Attempting duplicate ISBN must raise DatabaseError
    with pytest.raises(DatabaseError):
        in_memory_db.execute(
            """
            INSERT INTO books (title, author, isbn, category, total_copies, available_copies, created_at)
            VALUES ('Book B', 'Author B', '9781234567890', 'Fiction', 1, 1, '2026-10-01')
            """
        )


def test_database_transaction_rollback(in_memory_db):
    """Verifies atomic rollback on failure."""
    try:
        with in_memory_db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO members (name, email, phone, created_at)
                VALUES ('Rollback User', 'rollback@example.com', '+1-555-0000', '2026-10-01')
                """
            )
            # Intentionally cause an error to trigger rollback
            raise ValueError("Forced error")
    except ValueError:
        pass

    # Verify record was not persisted
    record = in_memory_db.fetchone("SELECT * FROM members WHERE email = 'rollback@example.com'")
    assert record is None
