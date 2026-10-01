"""
Book model representing a library book entity.
"""
from typing import Optional, Dict, Any
from app.utils.date_helper import get_current_timestamp_str


class Book:
    """Represents a book in the library catalog."""

    def __init__(
        self,
        title: str,
        author: str,
        isbn: str,
        category: str,
        total_copies: int = 1,
        available_copies: Optional[int] = None,
        published_year: Optional[int] = None,
        book_id: Optional[int] = None,
        created_at: Optional[str] = None,
    ):
        self.id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.category = category
        self.total_copies = total_copies
        self.available_copies = total_copies if available_copies is None else available_copies
        self.published_year = published_year
        self.created_at = created_at or get_current_timestamp_str()

    @property
    def is_available(self) -> bool:
        """Returns True if there is at least one copy available to borrow."""
        return self.available_copies > 0

    @property
    def borrowed_copies(self) -> int:
        """Returns the number of copies currently out on loan."""
        return max(0, self.total_copies - self.available_copies)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Book instance to a dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category": self.category,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "borrowed_copies": self.borrowed_copies,
            "published_year": self.published_year,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row: Any) -> "Book":
        """Constructs a Book instance from a sqlite3.Row or dict."""
        return cls(
            book_id=row["id"],
            title=row["title"],
            author=row["author"],
            isbn=row["isbn"],
            category=row["category"],
            total_copies=row["total_copies"],
            available_copies=row["available_copies"],
            published_year=row["published_year"],
            created_at=row["created_at"],
        )

    def __repr__(self) -> str:
        return (
            f"<Book id={self.id} title='{self.title}' author='{self.author}' "
            f"available={self.available_copies}/{self.total_copies}>"
        )
