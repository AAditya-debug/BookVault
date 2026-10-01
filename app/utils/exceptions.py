"""
Custom exceptions for the BookVault application.
Provides meaningful domain error handling across all layers.
"""


class BookVaultError(Exception):
    """Base exception for all BookVault domain errors."""
    pass


class ValidationError(BookVaultError):
    """Raised when user input fails validation rules."""
    pass


class NotFoundError(BookVaultError):
    """Raised when a requested resource (Book, Member, Loan) is not found."""
    pass


class BookUnavailableError(BookVaultError):
    """Raised when attempting to borrow a book with zero available copies."""
    pass


class MemberLimitExceededError(BookVaultError):
    """Raised when a member attempts to borrow more books than their allowed limit."""
    pass


class ActiveLoanExistsError(BookVaultError):
    """Raised when a member tries to borrow another copy of the same book while currently holding one."""
    pass


class LoanAlreadyReturnedError(BookVaultError):
    """Raised when an operation attempts to return a loan that has already been returned."""
    pass


class DatabaseError(BookVaultError):
    """Raised when an unrecoverable database operation failure occurs."""
    pass
