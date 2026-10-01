"""
Validation service for BookVault.
Validates input data before domain operations and database persistence.
"""
import re
from typing import Optional
from app.utils.exceptions import ValidationError
from app.utils.date_helper import parse_and_validate_date


class InputValidator:
    """Provides reusable validation methods for books, members, and loans."""

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,20}$")

    @classmethod
    def validate_non_empty_str(cls, value: str, field_name: str, max_length: int = 255) -> str:
        """Validates that a string is non-empty and does not exceed max length."""
        if value is None or not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{field_name} cannot be empty.")
        clean_value = value.strip()
        if len(clean_value) > max_length:
            raise ValidationError(f"{field_name} must not exceed {max_length} characters (got {len(clean_value)}).")
        return clean_value

    @classmethod
    def validate_positive_int(cls, value: int, field_name: str, min_val: int = 1, max_val: Optional[int] = None) -> int:
        """Validates that an integer falls within allowed bounds."""
        try:
            val_int = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid integer.")
        if val_int < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val}.")
        if max_val is not None and val_int > max_val:
            raise ValidationError(f"{field_name} must not exceed {max_val}.")
        return val_int

    @classmethod
    def validate_isbn(cls, isbn: str) -> str:
        """
        Validates ISBN (supports ISBN-10 or ISBN-13 format, alphanumeric check).
        """
        if not isbn or not isinstance(isbn, str):
            raise ValidationError("ISBN cannot be empty.")
        clean_isbn = isbn.strip().replace("-", "").replace(" ", "").upper()
        if len(clean_isbn) not in (10, 13):
            raise ValidationError("ISBN must contain 10 or 13 characters (excluding hyphens).")
        if not re.match(r"^[0-9]{9}[0-9X]$|^[0-9]{13}$", clean_isbn):
            raise ValidationError(f"Invalid ISBN format '{isbn}'.")
        return clean_isbn

    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validates email format."""
        if not email or not isinstance(email, str):
            raise ValidationError("Email cannot be empty.")
        clean_email = email.strip().lower()
        if not cls.EMAIL_REGEX.match(clean_email):
            raise ValidationError(f"Invalid email address: '{email}'.")
        return clean_email

    @classmethod
    def validate_phone(cls, phone: str) -> str:
        """Validates phone number format."""
        if not phone or not isinstance(phone, str):
            raise ValidationError("Phone number cannot be empty.")
        clean_phone = phone.strip()
        if not cls.PHONE_REGEX.match(clean_phone):
            raise ValidationError(f"Invalid phone number format: '{phone}'.")
        return clean_phone

    @classmethod
    def validate_publication_year(cls, year: int) -> int:
        """Validates publication year within historical and reasonable future limit."""
        import datetime
        current_year = datetime.date.today().year + 1
        return cls.validate_positive_int(year, "Publication year", min_val=1000, max_val=current_year)

    @classmethod
    def validate_date_string(cls, date_str: str, field_name: str = "Date") -> str:
        """Validates date format (YYYY-MM-DD)."""
        if not parse_and_validate_date(date_str):
            raise ValidationError(f"{field_name} must be a valid date in YYYY-MM-DD format.")
        return date_str.strip()
