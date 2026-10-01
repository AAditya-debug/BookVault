"""
Loan model representing a book borrowing transaction.
"""
from typing import Optional, Dict, Any
from app.utils.date_helper import (
    get_current_date_str,
    calculate_due_date,
    is_overdue,
    get_overdue_days,
    DEFAULT_LOAN_DAYS,
)


class LoanStatus:
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


class Loan:
    """Represents a loan record linking a Member to a Book."""

    def __init__(
        self,
        book_id: int,
        member_id: int,
        borrow_date: Optional[str] = None,
        due_date: Optional[str] = None,
        return_date: Optional[str] = None,
        status: str = LoanStatus.ACTIVE,
        loan_id: Optional[int] = None,
        book_title: Optional[str] = None,
        book_isbn: Optional[str] = None,
        member_name: Optional[str] = None,
        member_email: Optional[str] = None,
    ):
        self.id = loan_id
        self.book_id = book_id
        self.member_id = member_id
        self.borrow_date = borrow_date or get_current_date_str()
        self.due_date = due_date or calculate_due_date(self.borrow_date, DEFAULT_LOAN_DAYS)
        self.return_date = return_date
        self.status = status
        
        # Joined display fields
        self.book_title = book_title
        self.book_isbn = book_isbn
        self.member_name = member_name
        self.member_email = member_email

    @property
    def is_currently_overdue(self) -> bool:
        """Returns True if loan is active and current date exceeds due date."""
        if self.return_date is not None:
            return False
        return is_overdue(self.due_date)

    @property
    def overdue_days(self) -> int:
        """Calculates days overdue."""
        if self.return_date is not None:
            return 0
        return get_overdue_days(self.due_date)

    @property
    def dynamic_status(self) -> str:
        """Computes current real-time status."""
        if self.return_date is not None:
            return LoanStatus.RETURNED
        if is_overdue(self.due_date):
            return LoanStatus.OVERDUE
        return LoanStatus.ACTIVE

    def to_dict(self) -> Dict[str, Any]:
        """Converts loan to dictionary format."""
        return {
            "id": self.id,
            "book_id": self.book_id,
            "member_id": self.member_id,
            "book_title": self.book_title,
            "book_isbn": self.book_isbn,
            "member_name": self.member_name,
            "member_email": self.member_email,
            "borrow_date": self.borrow_date,
            "due_date": self.due_date,
            "return_date": self.return_date,
            "status": self.dynamic_status,
            "overdue_days": self.overdue_days,
        }

    @classmethod
    def from_row(cls, row: Any) -> "Loan":
        """Constructs a Loan instance from a sqlite3.Row or dict."""
        row_keys = row.keys() if hasattr(row, "keys") else row
        return cls(
            loan_id=row["id"],
            book_id=row["book_id"],
            member_id=row["member_id"],
            borrow_date=row["borrow_date"],
            due_date=row["due_date"],
            return_date=row["return_date"],
            status=row["status"],
            book_title=row["book_title"] if "book_title" in row_keys else None,
            book_isbn=row["book_isbn"] if "book_isbn" in row_keys else None,
            member_name=row["member_name"] if "member_name" in row_keys else None,
            member_email=row["member_email"] if "member_email" in row_keys else None,
        )

    def __repr__(self) -> str:
        return (
            f"<Loan id={self.id} book_id={self.book_id} member_id={self.member_id} "
            f"due={self.due_date} status={self.dynamic_status}>"
        )
