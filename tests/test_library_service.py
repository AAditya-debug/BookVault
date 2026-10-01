"""
Unit and integration tests for LibraryService business workflows.
"""
import pytest
from app.utils.exceptions import (
    NotFoundError,
    ValidationError,
    BookUnavailableError,
    MemberLimitExceededError,
    ActiveLoanExistsError,
    LoanAlreadyReturnedError,
)
from app.models.loan import LoanStatus


def test_book_crud_and_search(library_service):
    """Tests creating, editing, searching, and deleting books."""
    # Add Book
    book = library_service.add_book(
        title="Refactoring",
        author="Martin Fowler",
        isbn="9780201485677",
        category="Programming",
        total_copies=3,
        published_year=1999,
    )
    assert book.id is not None
    assert book.title == "Refactoring"
    assert book.available_copies == 3

    # Search books
    results = library_service.search_books("fowler")
    assert len(results) == 1
    assert results[0].title == "Refactoring"

    # Search by Category
    results_cat = library_service.search_books_by_category("Programming")
    assert len(results_cat) == 1

    # Edit book
    edited = library_service.edit_book(book.id, title="Refactoring (2nd Edition)", total_copies=5)
    assert edited.title == "Refactoring (2nd Edition)"
    assert edited.total_copies == 5
    assert edited.available_copies == 5

    # Delete book
    assert library_service.delete_book(book.id) is True
    with pytest.raises(NotFoundError):
        library_service.get_book_by_id(book.id)


def test_member_registration_and_validation(library_service):
    """Tests member registration, email duplication, and updates."""
    member = library_service.register_member(
        name="Sarah Connor",
        email="sarah@resistance.org",
        phone="+1-555-0987",
        address="Cyberdyne Rd",
        max_books_allowed=3,
    )
    assert member.id is not None
    assert member.name == "Sarah Connor"
    assert member.max_books_allowed == 3

    # Duplicate email prevention
    with pytest.raises(ValidationError):
        library_service.register_member(
            name="Sarah Duplicate",
            email="sarah@resistance.org",
            phone="+1-555-0988",
        )

    # Search member
    found = library_service.search_members("sarah")
    assert len(found) == 1
    assert found[0].email == "sarah@resistance.org"


def test_borrowing_and_returning_lifecycle(library_service):
    """Tests the full borrowing and returning cycle and inventory updates."""
    # Setup book and member
    book = library_service.add_book(
        title="The Rust Programming Language",
        author="Steve Klabnik",
        isbn="9781718500440",
        category="Systems",
        total_copies=2,
    )
    member = library_service.register_member(
        name="Rustacean",
        email="ferris@rust-lang.org",
        phone="+1-555-7878",
        max_books_allowed=2,
    )

    # 1. Borrow book
    loan = library_service.borrow_book(book_id=book.id, member_id=member.id, loan_days=14)
    assert loan.id is not None
    assert loan.status == LoanStatus.ACTIVE
    assert loan.book_title == "The Rust Programming Language"

    # Verify inventory decrement
    refreshed_book = library_service.get_book_by_id(book.id)
    assert refreshed_book.available_copies == 1
    assert refreshed_book.borrowed_copies == 1

    # 2. Prevent duplicate borrow of same book by same member
    with pytest.raises(ActiveLoanExistsError):
        library_service.borrow_book(book_id=book.id, member_id=member.id)

    # 3. Return book
    returned_loan = library_service.return_book(loan.id)
    assert returned_loan.return_date is not None
    assert returned_loan.status == LoanStatus.RETURNED

    # Verify inventory increment
    refreshed_book_after_return = library_service.get_book_by_id(book.id)
    assert refreshed_book_after_return.available_copies == 2
    assert refreshed_book_after_return.borrowed_copies == 0

    # 4. Attempting to return already returned loan must fail
    with pytest.raises(LoanAlreadyReturnedError):
        library_service.return_book(loan.id)


def test_borrowing_limit_enforcement(library_service):
    """Verifies that members cannot borrow beyond max_books_allowed."""
    book1 = library_service.add_book("Book 1", "Author 1", "9781111111111", "Cat", 5)
    book2 = library_service.add_book("Book 2", "Author 2", "9782222222222", "Cat", 5)
    book3 = library_service.add_book("Book 3", "Author 3", "9783333333333", "Cat", 5)

    member = library_service.register_member(
        name="Limited Patron",
        email="limited@example.com",
        phone="+1-555-9999",
        max_books_allowed=2,
    )

    # Borrow 2 books (allowed)
    library_service.borrow_book(book_id=book1.id, member_id=member.id)
    library_service.borrow_book(book_id=book2.id, member_id=member.id)

    # Borrow 3rd book (must be rejected)
    with pytest.raises(MemberLimitExceededError):
        library_service.borrow_book(book_id=book3.id, member_id=member.id)


def test_out_of_stock_borrow_rejection(library_service):
    """Verifies that borrowing is rejected when available_copies is 0."""
    book = library_service.add_book("Single Copy Book", "Author", "9784444444444", "Cat", 1)
    member_a = library_service.register_member("User A", "usera@example.com", "+1-555-1111")
    member_b = library_service.register_member("User B", "userb@example.com", "+1-555-2222")

    # Member A borrows the only copy
    library_service.borrow_book(book_id=book.id, member_id=member_a.id)

    # Member B attempts to borrow unavailable book
    with pytest.raises(BookUnavailableError):
        library_service.borrow_book(book_id=book.id, member_id=member_b.id)


def test_inactive_member_borrow_rejection(library_service):
    """Verifies that deactivated members cannot borrow books."""
    book = library_service.add_book("Test Book", "Author", "9785555555555", "Cat", 2)
    member = library_service.register_member("Inactive User", "inactive@example.com", "+1-555-3333")
    library_service.edit_member(member.id, is_active=False)

    with pytest.raises(ValidationError):
        library_service.borrow_book(book_id=book.id, member_id=member.id)


def test_overdue_detection_and_history(library_service):
    """Tests overdue loan identification and member history retrieval."""
    book = library_service.add_book("Ancient History", "Author", "9786666666666", "History", 2)
    member = library_service.register_member("Historian", "historian@example.com", "+1-555-4444")

    # Borrow with past date
    past_borrow = "2026-08-01"
    loan = library_service.borrow_book(
        book_id=book.id,
        member_id=member.id,
        loan_days=14,
        custom_borrow_date=past_borrow,
    )

    # Check overdue loans
    overdue_list = library_service.get_overdue_loans()
    assert len(overdue_list) >= 1
    assert any(l.id == loan.id for l in overdue_list)

    # Check member history
    history = library_service.get_member_borrowing_history(member.id)
    assert len(history) == 1
    assert history[0].id == loan.id


def test_member_edit_and_delete_constraints(library_service):
    """Tests updating member profile and deletion safety checks."""
    member = library_service.register_member("John Member", "johnm@example.com", "+1-555-5555")
    book = library_service.add_book("Python Secrets", "Dev", "9787777777777", "Tech", 2)

    # Edit member
    updated = library_service.edit_member(
        member.id,
        name="Johnathan Member",
        phone="+1-555-6666",
        max_books_allowed=6,
    )
    assert updated.name == "Johnathan Member"
    assert updated.phone == "+1-555-6666"
    assert updated.max_books_allowed == 6

    # Borrow a book
    loan = library_service.borrow_book(book.id, member.id)

    # Cannot delete member while loan is active
    with pytest.raises(ValidationError):
        library_service.remove_member(member.id)

    # Cannot delete book while loan is active
    with pytest.raises(ValidationError):
        library_service.delete_book(book.id)

    # Return book
    library_service.return_book(loan.id)

    # Now deletion should succeed
    assert library_service.remove_member(member.id) is True
    with pytest.raises(NotFoundError):
        library_service.get_member_by_id(member.id)


def test_return_book_by_member_and_book(library_service):
    """Tests returning a book using member ID and book ID lookup."""
    book = library_service.add_book("Architecture Patterns", "Dev", "9788888888888", "Tech", 2)
    member = library_service.register_member("Architect", "arch@example.com", "+1-555-9090")

    library_service.borrow_book(book.id, member.id)
    returned = library_service.return_book_by_member_and_book(member.id, book.id)
    assert returned.status == LoanStatus.RETURNED

    # Attempting to return again must fail with NotFoundError (no active loan found)
    with pytest.raises(NotFoundError):
        library_service.return_book_by_member_and_book(member.id, book.id)

