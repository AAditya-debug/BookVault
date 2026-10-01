"""
CSV Exporter utility for BookVault.
Exports catalog, members, loan records, and reports into standard CSV format.
"""
import csv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


DEFAULT_EXPORT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "exports"
)


class CSVExporter:
    """Handles exporting data structures and query results to CSV files."""

    @staticmethod
    def ensure_export_dir(export_dir: Optional[str] = None) -> str:
        """Ensures export directory exists and returns its path."""
        target_dir = export_dir or DEFAULT_EXPORT_DIR
        os.makedirs(target_dir, exist_ok=True)
        return target_dir

    @classmethod
    def generate_filename(cls, prefix: str, export_dir: Optional[str] = None) -> str:
        """Generates a timestamped export filepath."""
        target_dir = cls.ensure_export_dir(export_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(target_dir, f"{prefix}_{timestamp}.csv")

    @classmethod
    def export_dicts_to_csv(
        cls,
        data: List[Dict[str, Any]],
        headers: Optional[List[str]] = None,
        filepath: Optional[str] = None,
        prefix: str = "export",
    ) -> str:
        """
        Exports a list of dictionaries to a CSV file.
        Returns the absolute path of the generated CSV file.
        """
        if not data:
            target_path = filepath or cls.generate_filename(prefix)
            cls.ensure_export_dir(os.path.dirname(target_path) if os.path.dirname(target_path) else None)
            with open(target_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if headers:
                    writer.writerow(headers)
            return target_path

        target_path = filepath or cls.generate_filename(prefix)
        cls.ensure_export_dir(os.path.dirname(target_path) if os.path.dirname(target_path) else None)

        fieldnames = headers if headers is not None else list(data[0].keys())

        with open(target_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in data:
                writer.writerow(row)

        return target_path
