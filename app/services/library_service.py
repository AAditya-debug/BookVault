"""
Library Service for BookVault.
Orchestrates core business rules: book catalog management, member registrations,
borrowing workflows, returns, availability tracking, and overdue checks.
"""
from typing import List, Optional, Dict, Any
from app.database import DatabaseManager
from app.models.book import Book
from app.models.member import Member, DEFAULT_MAX_BOOKS
from app.models.loan import Loan, LoanStatus
from app.services.validator import InputValidator
from app.utils.exceptions import (
    NotFoundError,
    ValidationError,
    BookUnavailableError,
    MemberLimitExceededError,
    ActiveLoanExistsError,
    LoanAlreadyReturnedError,
    DatabaseError,
)
from app.utils.date_helper import (
    get_current_date_str,
    calculate_due_date,
    DEFAULT_LOAN_DAYS,
)


class LibraryService:
    """Core domain service for managing the library's day-to-day operations."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    # -------------------------------------------------------------------------
    # BOOK MANAGEMENT
    # -------------------------------------------------------------------------

    def add_book(
        self,
        title: str,
        author: str,
        isbn: str,
        category: str,
        total_copies: int = 1,
        published_year: Optional[int] = None,
    ) -> Book:
        """Adds a new book to the library catalog."""
        clean_title = InputValidator.validate_non_empty_str(title, "Title")
        clean_author = InputValidator.validate_non_empty_str(author, "Author")
        clean_isbn = InputValidator.validate_isbn(isbn)
        clean_cat = InputValidator.validate_non_empty_str(category, "Category")
        clean_copies = InputValidator.validate_positive_int(total_copies, "Total copies", min_val=1)
        clean_year = InputValidator.validate_publication_year(published_year) if published_year else None

        # Check if ISBN already exists
        existing = self.db.fetchone("SELECT id FROM books WHERE isbn = ?", (clean_isbn,))
        if existing:
            raise ValidationError(f"A book with ISBN '{clean_isbn}' already exists (ID: {existing['id']}).")

        from app.utils.date_helper import get_current_timestamp_str
        now = get_current_timestamp_str()

        query = """
        INSERT INTO books (title, author, isbn, category, total_copies, available_copies, published_year, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        book_id = self.db.execute(
            query,
            (clean_title, clean_author, clean_isbn, clean_cat, clean_copies, clean_copies, clean_year, now),
        )
        return self.get_book_by_id(book_id)

    def get_book_by_id(self, book_id: int) -> Book:
        """Retrieves a single book by its primary key ID."""
        row = self.db.fetchone("SELECT * FROM books WHERE id = ?", (book_id,))
        if not row:
            raise NotFoundError(f"Book with ID {book_id} not found.")
        return Book.from_row(row)

    def get_book_by_isbn(self, isbn: str) -> Book:
        """Retrieves a single book by its ISBN."""
        clean_isbn = InputValidator.validate_isbn(isbn)
        row = self.db.fetchone("SELECT * FROM books WHERE isbn = ?", (clean_isbn,))
        if not row:
            raise NotFoundError(f"Book with ISBN '{clean_isbn}' not found.")
        return Book.from_row(row)

    def edit_book(
        self,
        book_id: int,
        title: Optional[str] = None,
        author: Optional[str] = None,
        isbn: Optional[str] = None,
        category: Optional[str] = None,
        total_copies: Optional[int] = None,
        published_year: Optional[int] = None,
    ) -> Book:
        """Edits existing book attributes while maintaining inventory consistency."""
        existing = self.get_book_by_id(book_id)

        new_title = InputValidator.validate_non_empty_str(title, "Title") if title is not None else existing.title
        new_author = InputValidator.validate_non_empty_str(author, "Author") if author is not None else existing.author
        new_cat = InputValidator.validate_non_empty_str(category, "Category") if category is not None else existing.category
        new_year = InputValidator.validate_publication_year(published_year) if published_year is not None else existing.published_year

        new_isbn = existing.isbn
        if isbn is not None:
            clean_isbn = InputValidator.validate_isbn(isbn)
            if clean_isbn != existing.isbn:
                dup = self.db.fetchone("SELECT id FROM books WHERE isbn = ? AND id != ?", (clean_isbn, book_id))
                if dup:
                    raise ValidationError(f"ISBN '{clean_isbn}' is already registered to another book.")
            new_isbn = clean_isbn

        # Calculate new copy counts
        new_total_copies = existing.total_copies
        new_available_copies = existing.available_copies

        if total_copies is not None:
            clean_total = InputValidator.validate_positive_int(total_copies, "Total copies", min_val=1)
            borrowed_count = existing.borrowed_copies
            if clean_total < borrowed_count:
                raise ValidationError(
                    f"Cannot reduce total copies to {clean_total}. There are currently {borrowed_count} copies actively borrowed."
                )
            new_total_copies = clean_total
            new_available_copies = clean_total - borrowed_count

        query = """
        UPDATE books
        SET title = ?, author = ?, isbn = ?, category = ?, total_copies = ?, available_copies = ?, published_year = ?
        WHERE id = ?
        """
        self.db.execute(
            query,
            (new_title, new_author, new_isbn, new_cat, new_total_copies, new_available_copies, new_year, book_id),
        )
        return self.get_book_by_id(book_id)

    def delete_book(self, book_id: int) -> bool:
        """
        Deletes a book from the library.
        Fails if there are active loans for the book.
        """
        self.get_book_by_id(book_id)  # Validate exists
        active_loans = self.db.fetchone(
            "SELECT COUNT(*) as count FROM loans WHERE book_id = ? AND status IN ('ACTIVE', 'OVERDUE')",
            (book_id,),
        )
        if active_loans and active_loans["count"] > 0:
            raise ValidationError(
                f"Cannot delete book ID {book_id}: It has {active_loans['count']} active loan(s). Please return all copies first."
            )

        with self.db.transaction() as conn:
            cursor = conn.cursor()
            # Clean up past returned loan history for this book to satisfy FK constraint
            cursor.execute("DELETE FROM loans WHERE book_id = ?", (book_id,))
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        return True

    def get_all_books(self) -> List[Book]:
        """Returns all books ordered by title."""
        rows = self.db.fetchall("SELECT * FROM books ORDER BY title ASC")
        return [Book.from_row(r) for r in rows]

    def get_available_books(self) -> List[Book]:
        """Returns all books that currently have at least one copy available."""
        rows = self.db.fetchall("SELECT * FROM books WHERE available_copies > 0 ORDER BY title ASC")
        return [Book.from_row(r) for r in rows]

    def get_borrowed_books(self) -> List[Book]:
        """Returns all books where at least one copy is currently borrowed."""
        rows = self.db.fetchall("SELECT * FROM books WHERE available_copies < total_copies ORDER BY title ASC")
        return [Book.from_row(r) for r in rows]

    def search_books(self, query: str) -> List[Book]:
        """Searches across title, author, isbn, and category."""
        term = f"%{query.strip()}%"
        rows = self.db.fetchall(
            """
            SELECT * FROM books 
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ?
            ORDER BY title ASC
            """,
            (term, term, term, term),
        )
        return [Book.from_row(r) for r in rows]

    def search_books_by_title(self, title: str) -> List[Book]:
        """Searches specifically by title substring."""
        term = f"%{title.strip()}%"
        rows = self.db.fetchall("SELECT * FROM books WHERE title LIKE ? ORDER BY title ASC", (term,))
        return [Book.from_row(r) for r in rows]

    def search_books_by_author(self, author: str) -> List[Book]:
        """Searches specifically by author substring."""
        term = f"%{author.strip()}%"
        rows = self.db.fetchall("SELECT * FROM books WHERE author LIKE ? ORDER BY title ASC", (term,))
        return [Book.from_row(r) for r in rows]

    def search_books_by_category(self, category: str) -> List[Book]:
        """Searches specifically by category."""
        term = f"%{category.strip()}%"
        rows = self.db.fetchall("SELECT * FROM books WHERE category LIKE ? ORDER BY title ASC", (term,))
        return [Book.from_row(r) for r in rows]

    # -------------------------------------------------------------------------
    # MEMBER MANAGEMENT
    # -------------------------------------------------------------------------

    def register_member(
        self,
        name: str,
        email: str,
        phone: str,
        address: Optional[str] = None,
        max_books_allowed: int = DEFAULT_MAX_BOOKS,
    ) -> Member:
        """Registers a new library member."""
        clean_name = InputValidator.validate_non_empty_str(name, "Name")
        clean_email = InputValidator.validate_email(email)
        clean_phone = InputValidator.validate_phone(phone)
        clean_address = address.strip() if address else ""
        clean_limit = InputValidator.validate_positive_int(max_books_allowed, "Borrowing limit", min_val=1, max_val=20)

        existing = self.db.fetchone("SELECT id FROM members WHERE email = ?", (clean_email,))
        if existing:
            raise ValidationError(f"A member with email '{clean_email}' already exists (ID: {existing['id']}).")

        from app.utils.date_helper import get_current_timestamp_str
        now = get_current_timestamp_str()

        query = """
        INSERT INTO members (name, email, phone, address, max_books_allowed, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, 1, ?)
        """
        member_id = self.db.execute(
            query,
            (clean_name, clean_email, clean_phone, clean_address, clean_limit, now),
        )
        return self.get_member_by_id(member_id)

    def get_member_by_id(self, member_id: int) -> Member:
        """Retrieves a single member by ID."""
        row = self.db.fetchone("SELECT * FROM members WHERE id = ?", (member_id,))
        if not row:
            raise NotFoundError(f"Member with ID {member_id} not found.")
        return Member.from_row(row)

    def get_member_by_email(self, email: str) -> Member:
        """Retrieves a single member by email."""
        clean_email = InputValidator.validate_email(email)
        row = self.db.fetchone("SELECT * FROM members WHERE email = ?", (clean_email,))
        if not row:
            raise NotFoundError(f"Member with email '{clean_email}' not found.")
        return Member.from_row(row)

    def edit_member(
        self,
        member_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        max_books_allowed: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Member:
        """Edits an existing member profile."""
        existing = self.get_member_by_id(member_id)

        new_name = InputValidator.validate_non_empty_str(name, "Name") if name is not None else existing.name
        new_phone = InputValidator.validate_phone(phone) if phone is not None else existing.phone
        new_address = address.strip() if address is not None else existing.address
        new_active = int(is_active) if is_active is not None else int(existing.is_active)

        new_email = existing.email
        if email is not None:
            clean_email = InputValidator.validate_email(email)
            if clean_email != existing.email:
                dup = self.db.fetchone("SELECT id FROM members WHERE email = ? AND id != ?", (clean_email, member_id))
                if dup:
                    raise ValidationError(f"Email '{clean_email}' is already used by another member.")
            new_email = clean_email

        new_limit = existing.max_books_allowed
        if max_books_allowed is not None:
            new_limit = InputValidator.validate_positive_int(max_books_allowed, "Borrowing limit", min_val=1, max_val=20)

        query = """
        UPDATE members
        SET name = ?, email = ?, phone = ?, address = ?, max_books_allowed = ?, is_active = ?
        WHERE id = ?
        """
        self.db.execute(query, (new_name, new_email, new_phone, new_address, new_limit, new_active, member_id))
        return self.get_member_by_id(member_id)

    def remove_member(self, member_id: int) -> bool:
        """
        Removes a member from the library system.
        Fails if member currently has active unreturned loans.
        """
        self.get_member_by_id(member_id)  # Validate exists
        active_loans = self.db.fetchone(
            "SELECT COUNT(*) as count FROM loans WHERE member_id = ? AND status IN ('ACTIVE', 'OVERDUE')",
            (member_id,),
        )
        if active_loans and active_loans["count"] > 0:
            raise ValidationError(
                f"Cannot remove member ID {member_id}: They currently have {active_loans['count']} unreturned book(s)."
            )

        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM loans WHERE member_id = ?", (member_id,))
            cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
        return True

    def get_all_members(self) -> List[Member]:
        """Returns all registered members."""
        rows = self.db.fetchall("SELECT * FROM members ORDER BY name ASC")
        return [Member.from_row(r) for r in rows]

    def search_members(self, query: str) -> List[Member]:
        """Searches members by name, email, or phone."""
        term = f"%{query.strip()}%"
        rows = self.db.fetchall(
            """
            SELECT * FROM members 
            WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
            ORDER BY name ASC
            """,
            (term, term, term),
        )
        return [Member.from_row(r) for r in rows]

    # -------------------------------------------------------------------------
    # BORROWING & LOAN WORKFLOW
    # -------------------------------------------------------------------------

    def borrow_book(
        self,
        book_id: int,
        member_id: int,
        loan_days: int = DEFAULT_LOAN_DAYS,
        custom_borrow_date: Optional[str] = None,
    ) -> Loan:
        """
        Executes a complete book borrowing transaction:
        1. Validates member existence and active status.
        2. Validates book existence and availability.
        3. Checks member's active loan count against max allowance.
        4. Verifies member doesn't already hold an active copy of the book.
        5. Atomically creates loan and decrements book inventory.
        """
        member = self.get_member_by_id(member_id)
        if not member.is_active:
            raise ValidationError(f"Member '{member.name}' is deactivated and cannot borrow books.")

        book = self.get_book_by_id(book_id)
        if not book.is_available:
            raise BookUnavailableError(
                f"Book '{book.title}' is currently unavailable (0 of {book.total_copies} copies available)."
            )

        # Count active loans for member
        active_loans = self.db.fetchone(
            "SELECT COUNT(*) as count FROM loans WHERE member_id = ? AND status IN ('ACTIVE', 'OVERDUE')",
            (member_id,),
        )
        current_borrowed = active_loans["count"] if active_loans else 0
        if current_borrowed >= member.max_books_allowed:
            raise MemberLimitExceededError(
                f"Member '{member.name}' has reached their borrowing limit of {member.max_books_allowed} books "
                f"(currently holding {current_borrowed} books)."
            )

        # Check if member already has an active copy of this exact book
        existing_loan = self.db.fetchone(
            "SELECT id FROM loans WHERE member_id = ? AND book_id = ? AND status IN ('ACTIVE', 'OVERDUE')",
            (member_id, book_id),
        )
        if existing_loan:
            raise ActiveLoanExistsError(
                f"Member '{member.name}' already has an active loan (ID: {existing_loan['id']}) for '{book.title}'."
            )

        borrow_date = custom_borrow_date or get_current_date_str()
        if custom_borrow_date:
            InputValidator.validate_date_string(custom_borrow_date, "Borrow date")

        due_date = calculate_due_date(borrow_date, days=loan_days)

        with self.db.transaction() as conn:
            cursor = conn.cursor()
            # Insert loan record
            cursor.execute(
                """
                INSERT INTO loans (book_id, member_id, borrow_date, due_date, return_date, status)
                VALUES (?, ?, ?, ?, NULL, 'ACTIVE')
                """,
                (book_id, member_id, borrow_date, due_date),
            )
            loan_id = cursor.lastrowid

            # Decrement available copies
            cursor.execute(
                """
                UPDATE books 
                SET available_copies = available_copies - 1 
                WHERE id = ? AND available_copies > 0
                """,
                (book_id,),
            )
            if cursor.rowcount == 0:
                raise BookUnavailableError("Failed to reserve copy: Book is no longer available.")

        return self.get_loan_by_id(loan_id)

    def return_book(self, loan_id: int, custom_return_date: Optional[str] = None) -> Loan:
        """
        Executes a complete book return transaction:
        1. Validates loan exists and is active.
        2. Sets return date and marks status as RETURNED.
        3. Atomically increments book available inventory.
        """
        loan = self.get_loan_by_id(loan_id)
        if loan.return_date is not None or loan.status == LoanStatus.RETURNED:
            raise LoanAlreadyReturnedError(
                f"Loan ID {loan_id} was already returned on {loan.return_date}."
            )

        return_date = custom_return_date or get_current_date_str()
        if custom_return_date:
            InputValidator.validate_date_string(custom_return_date, "Return date")

        with self.db.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE loans 
                SET return_date = ?, status = 'RETURNED'
                WHERE id = ?
                """,
                (return_date, loan_id),
            )
            cursor.execute(
                """
                UPDATE books 
                SET available_copies = available_copies + 1 
                WHERE id = ?
                """,
                (loan.book_id,),
            )

        return self.get_loan_by_id(loan_id)

    def return_book_by_member_and_book(self, member_id: int, book_id: int) -> Loan:
        """Convenience method to return a book using member ID and book ID."""
        row = self.db.fetchone(
            """
            SELECT id FROM loans 
            WHERE member_id = ? AND book_id = ? AND status IN ('ACTIVE', 'OVERDUE')
            ORDER BY id DESC LIMIT 1
            """,
            (member_id, book_id),
        )
        if not row:
            raise NotFoundError(f"No active loan found for Member ID {member_id} and Book ID {book_id}.")
        return self.return_book(row["id"])

    def get_loan_by_id(self, loan_id: int) -> Loan:
        """Retrieves a loan with joined book and member details."""
        query = """
        SELECT 
            l.id, l.book_id, l.member_id, l.borrow_date, l.due_date, l.return_date, l.status,
            b.title AS book_title, b.isbn AS book_isbn,
            m.name AS member_name, m.email AS member_email
        FROM loans l
        JOIN books b ON l.book_id = b.id
        JOIN members m ON l.member_id = m.id
        WHERE l.id = ?
        """
        row = self.db.fetchone(query, (loan_id,))
        if not row:
            raise NotFoundError(f"Loan record with ID {loan_id} not found.")
        return Loan.from_row(row)

    def get_all_loans(self) -> List[Loan]:
        """Returns all loans across history, newest first."""
        query = """
        SELECT 
            l.id, l.book_id, l.member_id, l.borrow_date, l.due_date, l.return_date, l.status,
            b.title AS book_title, b.isbn AS book_isbn,
            m.name AS member_name, m.email AS member_email
        FROM loans l
        JOIN books b ON l.book_id = b.id
        JOIN members m ON l.member_id = m.id
        ORDER BY l.id DESC
        """
        rows = self.db.fetchall(query)
        return [Loan.from_row(r) for r in rows]

    def get_active_loans(self) -> List[Loan]:
        """Returns currently active loans."""
        self.sync_overdue_statuses()
        query = """
        SELECT 
            l.id, l.book_id, l.member_id, l.borrow_date, l.due_date, l.return_date, l.status,
            b.title AS book_title, b.isbn AS book_isbn,
            m.name AS member_name, m.email AS member_email
        FROM loans l
        JOIN books b ON l.book_id = b.id
        JOIN members m ON l.member_id = m.id
        WHERE l.status IN ('ACTIVE', 'OVERDUE')
        ORDER BY l.due_date ASC
        """
        rows = self.db.fetchall(query)
        return [Loan.from_row(r) for r in rows]

    def get_overdue_loans(self) -> List[Loan]:
        """
        Returns all active loans where due_date is before today.
        Automatically syncs status in the database.
        """
        self.sync_overdue_statuses()
        today = get_current_date_str()
        query = """
        SELECT 
            l.id, l.book_id, l.member_id, l.borrow_date, l.due_date, l.return_date, l.status,
            b.title AS book_title, b.isbn AS book_isbn,
            m.name AS member_name, m.email AS member_email
        FROM loans l
        JOIN books b ON l.book_id = b.id
        JOIN members m ON l.member_id = m.id
        WHERE l.status IN ('ACTIVE', 'OVERDUE') AND l.due_date < ?
        ORDER BY l.due_date ASC
        """
        rows = self.db.fetchall(query, (today,))
        return [Loan.from_row(r) for r in rows]

    def get_member_borrowing_history(self, member_id: int) -> List[Loan]:
        """Returns complete borrowing history for a specific member."""
        self.get_member_by_id(member_id)  # Validate member exists
        self.sync_overdue_statuses()
        query = """
        SELECT 
            l.id, l.book_id, l.member_id, l.borrow_date, l.due_date, l.return_date, l.status,
            b.title AS book_title, b.isbn AS book_isbn,
            m.name AS member_name, m.email AS member_email
        FROM loans l
        JOIN books b ON l.book_id = b.id
        JOIN members m ON l.member_id = m.id
        WHERE l.member_id = ?
        ORDER BY l.id DESC
        """
        rows = self.db.fetchall(query, (member_id,))
        return [Loan.from_row(r) for r in rows]

    def sync_overdue_statuses(self) -> int:
        """
        Scans all active loans and updates status to 'OVERDUE' if due_date < today.
        Returns the count of loans updated.
        """
        today = get_current_date_str()
        query = """
        UPDATE loans
        SET status = 'OVERDUE'
        WHERE return_date IS NULL AND status = 'ACTIVE' AND due_date < ?
        """
        return self.db.execute(query, (today,))
