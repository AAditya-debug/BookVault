"""
Unit tests for ReportService analytics and metrics aggregation.
"""
import pytest


def test_summary_metrics(sample_seeded_service, report_service):
    """Verifies aggregate KPI calculations across inventory, members, and loans."""
    metrics = report_service.get_summary_metrics()

    books = metrics["books"]
    members = metrics["members"]
    loans = metrics["loans"]

    assert books["total_titles"] == 10
    assert books["total_copies"] > 0
    assert books["available_copies"] > 0
    assert members["total_members"] == 5
    assert members["active_members"] == 5
    assert loans["total_transactions"] >= 3
    assert loans["overdue_loans"] >= 1


def test_most_borrowed_ranking(sample_seeded_service, report_service):
    """Verifies calculation and sorting of most borrowed books."""
    rankings = report_service.get_most_borrowed_books(limit=5)
    assert isinstance(rankings, list)
    assert len(rankings) <= 5
    # Ensure rankings are sorted descending by borrow_count
    for i in range(len(rankings) - 1):
        assert rankings[i]["borrow_count"] >= rankings[i + 1]["borrow_count"]


def test_category_distribution(sample_seeded_service, report_service):
    """Verifies category breakdown aggregation."""
    dist = report_service.get_category_distribution()
    assert len(dist) > 0
    categories = [d["category"] for d in dist]
    assert "Software Engineering" in categories
    assert "Fiction" in categories
