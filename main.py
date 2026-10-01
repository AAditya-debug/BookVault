"""
Main entry point for BookVault Library Management System.
Run with: python main.py
"""
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.cli.menu import CLI


def main():
    """Initializes and runs the BookVault interactive CLI application."""
    try:
        app = CLI()
        # Seed initial sample data automatically on first launch if empty
        app.db.seed_sample_data()
        app.run()
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user. Exiting BookVault.")
        sys.exit(0)
    except Exception as exc:
        print(f"\n[FATAL ERROR] An unexpected error occurred: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
