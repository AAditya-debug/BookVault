"""
Member model representing a library patron.
"""
from typing import Optional, Dict, Any
from app.utils.date_helper import get_current_timestamp_str


DEFAULT_MAX_BOOKS = 5


class Member:
    """Represents a registered library member."""

    def __init__(
        self,
        name: str,
        email: str,
        phone: str,
        address: Optional[str] = None,
        max_books_allowed: int = DEFAULT_MAX_BOOKS,
        is_active: bool = True,
        member_id: Optional[int] = None,
        created_at: Optional[str] = None,
    ):
        self.id = member_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address or ""
        self.max_books_allowed = max_books_allowed
        self.is_active = is_active
        self.created_at = created_at or get_current_timestamp_str()

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Member instance to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "max_books_allowed": self.max_books_allowed,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row: Any) -> "Member":
        """Constructs a Member instance from a sqlite3.Row or dict."""
        return cls(
            member_id=row["id"],
            name=row["name"],
            email=row["email"],
            phone=row["phone"],
            address=row["address"],
            max_books_allowed=row["max_books_allowed"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
        )

    def __repr__(self) -> str:
        status = "Active" if self.is_active else "Inactive"
        return f"<Member id={self.id} name='{self.name}' email='{self.email}' status={status}>"
