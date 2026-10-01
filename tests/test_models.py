"""
Unit tests for domain models (Book, Member, Loan).
"""
import pytest
from app.models.book import Book
from app.models.member import Member
from app.models.loan import Loan, LoanStatus


def test_book_initialization():
    """Tests Book instance attributes and availability helpers."""
    book = Book(
        title="The Pragmatic Programmer",
        author="David Thomas",
        isbn="9780201616224",
        category="Programming",
        total_copies=3,
        available_copies=2,
        published_year=1999,
        book_id=1,
    )
    assert book.id == 1
    assert book.title == "The Pragmatic Programmer"
    assert book.author == "David Thomas"
    assert book.isbn == "9780201616224"
    assert book.category == "Programming"
    assert book.total_copies == 3
    assert book.available_copies == 2
    assert book.is_available is True
    assert book.borrowed_copies == 1

    # Test dictionary serialization
    data = book.to_dict()
    assert data["id"] == 1
    assert data["title"] == "The Pragmatic Programmer"
    assert data["borrowed_copies"] == 1


def test_book_unavailability():
    """Tests Book properties when all copies are borrowed."""
    book = Book(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="9780132350884",
        category="Software Engineering",
        total_copies=2,
        available_copies=0,
    )
    assert book.is_available is False
    assert book.borrowed_copies == 2


def test_member_initialization():
    """Tests Member instance creation and defaults."""
    member = Member(
        name="John Doe",
        email="john.doe@example.com",
        phone="+1-555-1234",
        address="123 Elm St",
        max_books_allowed=4,
        member_id=10,
    )
    assert member.id == 10
    assert member.name == "John Doe"
    assert member.email == "john.doe@example.com"
    assert member.phone == "+1-555-1234"
    assert member.address == "123 Elm St"
    assert member.max_books_allowed == 4
    assert member.is_active is True

    data = member.to_dict()
    assert data["name"] == "John Doe"
    assert data["max_books_allowed"] == 4


def test_loan_overdue_and_status():
    """Tests Loan status detection and overdue calculation."""
    # Active, not overdue
    active_loan = Loan(
        book_id=1,
        member_id=1,
        borrow_date="2026-10-01",
        due_date="2026-10-15",
        status=LoanStatus.ACTIVE,
        loan_id=100,
    )
    assert active_loan.return_date is None
    assert active_loan.status == LoanStatus.ACTIVE

    # Overdue loan
    overdue_loan = Loan(
        book_id=1,
        member_id=1,
        borrow_date="2026-08-01",
        due_date="2026-08-15",
        status=LoanStatus.ACTIVE,
        loan_id=101,
    )
    assert overdue_loan.is_currently_overdue is True
    assert overdue_loan.overdue_days > 0
    assert overdue_loan.dynamic_status == LoanStatus.OVERDUE

    # Returned loan
    returned_loan = Loan(
        book_id=1,
        member_id=1,
        borrow_date="2026-08-01",
        due_date="2026-08-15",
        return_date="2026-08-10",
        status=LoanStatus.RETURNED,
        loan_id=102,
    )
    assert returned_loan.is_currently_overdue is False
    assert returned_loan.overdue_days == 0
    assert returned_loan.dynamic_status == LoanStatus.RETURNED
