"""
Unit tests for input validation logic.
"""
import pytest
from app.services.validator import InputValidator
from app.utils.exceptions import ValidationError


def test_validate_non_empty_str():
    assert InputValidator.validate_non_empty_str("  Harry Potter  ", "Title") == "Harry Potter"
    with pytest.raises(ValidationError):
        InputValidator.validate_non_empty_str("", "Title")
    with pytest.raises(ValidationError):
        InputValidator.validate_non_empty_str("   ", "Title")


def test_validate_isbn():
    # Valid ISBN-10 and ISBN-13
    assert InputValidator.validate_isbn("978-0-13-235088-4") == "9780132350884"
    assert InputValidator.validate_isbn("0-201-61622-X") == "020161622X"

    # Invalid ISBNs
    with pytest.raises(ValidationError):
        InputValidator.validate_isbn("12345")  # Too short
    with pytest.raises(ValidationError):
        InputValidator.validate_isbn("abcdefghijklm")  # Invalid characters


def test_validate_email():
    assert InputValidator.validate_email("test@example.com") == "test@example.com"
    assert InputValidator.validate_email(" USER.NAME+TAG@DOMAIN.CO.UK ") == "user.name+tag@domain.co.uk"

    with pytest.raises(ValidationError):
        InputValidator.validate_email("invalid-email")
    with pytest.raises(ValidationError):
        InputValidator.validate_email("@missinguser.com")


def test_validate_phone():
    assert InputValidator.validate_phone("+1-555-0199") == "+1-555-0199"
    assert InputValidator.validate_phone("(555) 234-5678") == "(555) 234-5678"

    with pytest.raises(ValidationError):
        InputValidator.validate_phone("123")  # Too short
    with pytest.raises(ValidationError):
        InputValidator.validate_phone("abc-phone-xyz")


def test_validate_positive_int():
    assert InputValidator.validate_positive_int(5, "Copies", min_val=1) == 5
    assert InputValidator.validate_positive_int("10", "Copies") == 10

    with pytest.raises(ValidationError):
        InputValidator.validate_positive_int(0, "Copies", min_val=1)
    with pytest.raises(ValidationError):
        InputValidator.validate_positive_int(-3, "Copies", min_val=1)
    with pytest.raises(ValidationError):
        InputValidator.validate_positive_int("not_a_number", "Copies")


def test_validate_publication_year():
    assert InputValidator.validate_publication_year(2021) == 2021
    with pytest.raises(ValidationError):
        InputValidator.validate_publication_year(999)  # Too old
    with pytest.raises(ValidationError):
        InputValidator.validate_publication_year(3000)  # Future beyond sanity
