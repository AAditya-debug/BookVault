"""
Pytest configuration and shared test fixtures for BookVault.
"""
import pytest
from app.database import DatabaseManager
from app.services.library_service import LibraryService
from app.services.report_service import ReportService


@pytest.fixture
def in_memory_db():
    """Provides an isolated, in-memory SQLite database instance for each test."""
    db = DatabaseManager(db_path=":memory:")
    yield db


@pytest.fixture
def library_service(in_memory_db):
    """Provides a fresh LibraryService connected to the in-memory database."""
    return LibraryService(in_memory_db)


@pytest.fixture
def report_service(in_memory_db, library_service):
    """Provides a fresh ReportService connected to the in-memory database."""
    return ReportService(in_memory_db, library_service)


@pytest.fixture
def sample_seeded_service(in_memory_db):
    """Provides a LibraryService with pre-populated sample test records."""
    in_memory_db.seed_sample_data()
    return LibraryService(in_memory_db)
