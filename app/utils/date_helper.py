"""
Date helper functions for BookVault.
Standardizes date calculations, loan durations, and overdue checks.
"""
from datetime import datetime, date, timedelta
from typing import Optional


DEFAULT_LOAN_DAYS = 14
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_current_date_str() -> str:
    """Returns today's date formatted as YYYY-MM-DD."""
    return date.today().strftime(DATE_FORMAT)


def get_current_timestamp_str() -> str:
    """Returns current date and time formatted as YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime(DATETIME_FORMAT)


def calculate_due_date(borrow_date_str: Optional[str] = None, days: int = DEFAULT_LOAN_DAYS) -> str:
    """
    Calculates due date given a start date (or today) and duration in days.
    
    :param borrow_date_str: Starting date string (YYYY-MM-DD). If None, uses today.
    :param days: Number of days for the loan (must be positive).
    :return: Due date string (YYYY-MM-DD).
    """
    if borrow_date_str:
        base_date = datetime.strptime(borrow_date_str, DATE_FORMAT).date()
    else:
        base_date = date.today()
    due = base_date + timedelta(days=days)
    return due.strftime(DATE_FORMAT)


def is_overdue(due_date_str: str, return_date_str: Optional[str] = None) -> bool:
    """
    Checks if a loan is overdue.
    If already returned, compares return date with due date.
    If active, compares current date with due date.
    """
    try:
        due = datetime.strptime(due_date_str, DATE_FORMAT).date()
    except (ValueError, TypeError):
        return False

    if return_date_str:
        try:
            ret = datetime.strptime(return_date_str, DATE_FORMAT).date()
            return ret > due
        except (ValueError, TypeError):
            return False
    else:
        return date.today() > due


def get_overdue_days(due_date_str: str, return_date_str: Optional[str] = None) -> int:
    """
    Returns the number of days a loan is overdue. Returns 0 if not overdue.
    """
    try:
        due = datetime.strptime(due_date_str, DATE_FORMAT).date()
    except (ValueError, TypeError):
        return 0

    if return_date_str:
        try:
            ret = datetime.strptime(return_date_str, DATE_FORMAT).date()
            delta = (ret - due).days
            return max(0, delta)
        except (ValueError, TypeError):
            return 0
    else:
        delta = (date.today() - due).days
        return max(0, delta)


def parse_and_validate_date(date_str: str) -> bool:
    """Validates that a string matches YYYY-MM-DD and is a real calendar date."""
    if not date_str or not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str.strip(), DATE_FORMAT)
        return True
    except ValueError:
        return False
