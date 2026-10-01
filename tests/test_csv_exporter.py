"""
Unit tests for CSV export operations.
"""
import os
import csv
import pytest
from app.utils.csv_exporter import CSVExporter


def test_export_dicts_to_csv(tmp_path):
    """Verifies that dictionary records export properly to CSV."""
    sample_data = [
        {"id": 1, "title": "Book One", "author": "Author A"},
        {"id": 2, "title": "Book Two", "author": "Author B"},
    ]
    export_file = str(tmp_path / "test_books.csv")

    output_path = CSVExporter.export_dicts_to_csv(sample_data, filepath=export_file)
    assert os.path.exists(output_path)

    # Read back and verify CSV content
    with open(output_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["title"] == "Book One"
        assert rows[1]["author"] == "Author B"


def test_report_service_csv_exports(sample_seeded_service, report_service, tmp_path):
    """Tests all export functions on ReportService."""
    b_path = report_service.export_books_to_csv(filepath=str(tmp_path / "books.csv"))
    m_path = report_service.export_members_to_csv(filepath=str(tmp_path / "members.csv"))
    l_path = report_service.export_loans_to_csv(filepath=str(tmp_path / "loans.csv"))
    o_path = report_service.export_overdue_to_csv(filepath=str(tmp_path / "overdue.csv"))
    pop_path = report_service.export_most_borrowed_to_csv(filepath=str(tmp_path / "popular.csv"))

    for path in [b_path, m_path, l_path, o_path, pop_path]:
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
