"""
Report Service for BookVault.
Generates statistical reports, metrics, overdue audits, popularity rankings,
and handles exporting reports to CSV.
"""
from typing import Dict, Any, List, Optional
from app.database import DatabaseManager
from app.services.library_service import LibraryService
from app.utils.csv_exporter import CSVExporter
from app.utils.date_helper import get_current_date_str


class ReportService:
    """Provides statistical aggregations, reporting, and export pipelines."""

    def __init__(self, db_manager: DatabaseManager, library_service: Optional[LibraryService] = None):
        self.db = db_manager
        self.lib_service = library_service or LibraryService(db_manager)

    def get_summary_metrics(self) -> Dict[str, Any]:
        """
        Calculates high-level KPIs:
        - Total titles & total physical copies
        - Total available copies & total borrowed copies
        - Total registered members & active members
        - Total active loans & overdue loans
        - Total historical transactions
        """
        # Books aggregations
        book_stats = self.db.fetchone(
            """
            SELECT 
                COUNT(*) as total_titles,
                COALESCE(SUM(total_copies), 0) as total_copies,
                COALESCE(SUM(available_copies), 0) as available_copies,
                COALESCE(SUM(total_copies - available_copies), 0) as borrowed_copies
            FROM books
            """
        )

        # Members aggregations
        member_stats = self.db.fetchone(
            """
            SELECT 
                COUNT(*) as total_members,
                COALESCE(SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END), 0) as active_members,
                COALESCE(SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END), 0) as inactive_members
            FROM members
            """
        )

        # Loans aggregations
        today = get_current_date_str()
        loan_stats = self.db.fetchone(
            """
            SELECT 
                COUNT(*) as total_loans,
                COALESCE(SUM(CASE WHEN return_date IS NULL THEN 1 ELSE 0 END), 0) as active_loans,
                COALESCE(SUM(CASE WHEN return_date IS NOT NULL THEN 1 ELSE 0 END), 0) as returned_loans,
                COALESCE(SUM(CASE WHEN return_date IS NULL AND due_date < ? THEN 1 ELSE 0 END), 0) as overdue_loans
            FROM loans
            """,
            (today,),
        )

        return {
            "books": {
                "total_titles": book_stats["total_titles"] if book_stats else 0,
                "total_copies": book_stats["total_copies"] if book_stats else 0,
                "available_copies": book_stats["available_copies"] if book_stats else 0,
                "borrowed_copies": book_stats["borrowed_copies"] if book_stats else 0,
            },
            "members": {
                "total_members": member_stats["total_members"] if member_stats else 0,
                "active_members": member_stats["active_members"] if member_stats else 0,
                "inactive_members": member_stats["inactive_members"] if member_stats else 0,
            },
            "loans": {
                "total_transactions": loan_stats["total_loans"] if loan_stats else 0,
                "active_loans": loan_stats["active_loans"] if loan_stats else 0,
                "returned_loans": loan_stats["returned_loans"] if loan_stats else 0,
                "overdue_loans": loan_stats["overdue_loans"] if loan_stats else 0,
            },
        }

    def get_most_borrowed_books(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves the top most borrowed books based on historical loan volume.
        """
        query = """
        SELECT 
            b.id AS book_id,
            b.title,
            b.author,
            b.category,
            b.isbn,
            b.total_copies,
            b.available_copies,
            COUNT(l.id) AS borrow_count
        FROM books b
        LEFT JOIN loans l ON b.id = l.book_id
        GROUP BY b.id
        ORDER BY borrow_count DESC, b.title ASC
        LIMIT ?
        """
        rows = self.db.fetchall(query, (limit,))
        return [dict(r) for r in rows]

    def get_overdue_report_data(self) -> List[Dict[str, Any]]:
        """
        Fetches detailed overdue loan records with overdue day calculations.
        """
        overdue_loans = self.lib_service.get_overdue_loans()
        report = []
        for loan in overdue_loans:
            data = loan.to_dict()
            report.append(data)
        return report

    def get_category_distribution(self) -> List[Dict[str, Any]]:
        """Returns distribution of books and copies by category."""
        query = """
        SELECT 
            category,
            COUNT(*) AS titles_count,
            SUM(total_copies) AS total_copies,
            SUM(available_copies) AS available_copies
        FROM books
        GROUP BY category
        ORDER BY titles_count DESC, category ASC
        """
        rows = self.db.fetchall(query)
        return [dict(r) for r in rows]

    # -------------------------------------------------------------------------
    # CSV EXPORT METHODS
    # -------------------------------------------------------------------------

    def export_books_to_csv(self, filepath: Optional[str] = None) -> str:
        """Exports all books in catalog to CSV."""
        books = self.lib_service.get_all_books()
        data = [b.to_dict() for b in books]
        return CSVExporter.export_dicts_to_csv(data, filepath=filepath, prefix="books_catalog")

    def export_members_to_csv(self, filepath: Optional[str] = None) -> str:
        """Exports all members to CSV."""
        members = self.lib_service.get_all_members()
        data = [m.to_dict() for m in members]
        return CSVExporter.export_dicts_to_csv(data, filepath=filepath, prefix="members_list")

    def export_loans_to_csv(self, filepath: Optional[str] = None, only_active: bool = False) -> str:
        """Exports loans history or active loans to CSV."""
        loans = self.lib_service.get_active_loans() if only_active else self.lib_service.get_all_loans()
        data = [l.to_dict() for l in loans]
        prefix = "active_loans" if only_active else "all_loans"
        return CSVExporter.export_dicts_to_csv(data, filepath=filepath, prefix=prefix)

    def export_overdue_to_csv(self, filepath: Optional[str] = None) -> str:
        """Exports overdue loans report to CSV."""
        data = self.get_overdue_report_data()
        return CSVExporter.export_dicts_to_csv(data, filepath=filepath, prefix="overdue_report")

    def export_most_borrowed_to_csv(self, limit: int = 20, filepath: Optional[str] = None) -> str:
        """Exports top borrowed books to CSV."""
        data = self.get_most_borrowed_books(limit=limit)
        return CSVExporter.export_dicts_to_csv(data, filepath=filepath, prefix="most_borrowed_books")
