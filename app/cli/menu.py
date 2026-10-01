"""
Interactive CLI Interface for BookVault.
Provides text-based navigation, formatted tables, prompts, and actions.
"""
import sys
import os
from typing import List, Dict, Any, Optional
from app.database import DatabaseManager
from app.services.library_service import LibraryService
from app.services.report_service import ReportService
from app.utils.exceptions import BookVaultError
from app.models.book import Book
from app.models.member import Member
from app.models.loan import Loan


class CLI:
    """Console User Interface for BookVault."""

    def __init__(self, db_path: Optional[str] = None):
        self.db = DatabaseManager(db_path)
        self.library = LibraryService(self.db)
        self.reports = ReportService(self.db, self.library)

    # -------------------------------------------------------------------------
    # FORMATTING UTILITIES
    # -------------------------------------------------------------------------

    def clear_screen(self) -> None:
        """Clears terminal screen across OS."""
        os.system("cls" if os.name == "nt" else "clear")

    def print_banner(self) -> None:
        """Displays application header."""
        print("=" * 72)
        print("       📖  BOOKVAULT — LIBRARY MANAGEMENT SYSTEM  📖       ")
        print("           Clean Python Architecture • SQLite Relational DB")
        print("=" * 72)

    def print_header(self, title: str) -> None:
        """Prints a section header."""
        print(f"\n--- [ {title.upper()} ] " + "-" * max(5, 68 - len(title)))

    def prompt(self, message: str, default: Optional[str] = None) -> str:
        """Prompts user for input with optional default value."""
        if default is not None:
            val = input(f"{message} [{default}]: ").strip()
            return val if val else default
        return input(f"{message}: ").strip()

    def print_success(self, message: str) -> None:
        """Prints success feedback."""
        print(f"\n[SUCCESS] {message}")

    def print_error(self, message: str) -> None:
        """Prints error feedback."""
        print(f"\n[ERROR] {message}")

    def print_table(self, headers: List[str], rows: List[List[Any]]) -> None:
        """Renders formatted ASCII table with dynamic column sizing."""
        if not rows:
            print("\n  (No records found)")
            return

        col_widths = [len(h) for h in headers]
        str_rows = []
        for row in rows:
            str_row = [str(cell) if cell is not None else "" for cell in row]
            str_rows.append(str_row)
            for i, cell in enumerate(str_row):
                col_widths[i] = max(col_widths[i], len(cell))

        # Add small padding
        col_widths = [w + 2 for w in col_widths]

        separator = "+" + "+".join(["-" * w for w in col_widths]) + "+"
        header_row = "|" + "|".join([f" {headers[i]}".ljust(col_widths[i]) for i in range(len(headers))]) + "|"

        print()
        print(separator)
        print(header_row)
        print(separator)
        for row in str_rows:
            row_str = "|" + "|".join([f" {row[i]}".ljust(col_widths[i]) for i in range(len(row))]) + "|"
            print(row_str)
        print(separator)
        print(f"Total: {len(rows)} record(s)\n")

    # -------------------------------------------------------------------------
    # MAIN EVENT LOOP
    # -------------------------------------------------------------------------

    def run(self) -> None:
        """Starts main interactive loop."""
        while True:
            self.print_banner()
            print("\n[MAIN MENU]")
            print("  1. 📚 Book Management")
            print("  2. 👥 Member Management")
            print("  3. 🔄 Borrow & Return Operations")
            print("  4. 📊 Analytics & Reports")
            print("  5. 💾 CSV Data Export")
            print("  6. ⚙️  Database & Demo Seeding")
            print("  0. 🚪 Exit Application")

            choice = input("\nEnter your choice (0-6): ").strip()

            if choice == "1":
                self.menu_book_management()
            elif choice == "2":
                self.menu_member_management()
            elif choice == "3":
                self.menu_loan_operations()
            elif choice == "4":
                self.menu_reports()
            elif choice == "5":
                self.menu_csv_export()
            elif choice == "6":
                self.menu_database_admin()
            elif choice == "0":
                print("\nThank you for using BookVault. Goodbye!\n")
                sys.exit(0)
            else:
                self.print_error("Invalid option. Please enter a number between 0 and 6.")
                input("\nPress Enter to continue...")

    # -------------------------------------------------------------------------
    # 1. BOOK MANAGEMENT MENU
    # -------------------------------------------------------------------------

    def menu_book_management(self) -> None:
        while True:
            self.print_header("Book Management")
            print("  1. View All Books")
            print("  2. View Available Books Only")
            print("  3. View Currently Borrowed Books")
            print("  4. Search Books (Universal Query)")
            print("  5. Search Books by Title")
            print("  6. Search Books by Author")
            print("  7. Search Books by Category")
            print("  8. Add New Book")
            print("  9. Edit Existing Book")
            print("  10. Delete Book")
            print("  0. Back to Main Menu")

            choice = input("\nEnter choice (0-10): ").strip()
            try:
                if choice == "1":
                    books = self.library.get_all_books()
                    self._display_books_table(books, "All Books in Catalog")
                elif choice == "2":
                    books = self.library.get_available_books()
                    self._display_books_table(books, "Available Books")
                elif choice == "3":
                    books = self.library.get_borrowed_books()
                    self._display_books_table(books, "Borrowed Books")
                elif choice == "4":
                    query = self.prompt("Enter search term (title, author, isbn, category)")
                    if query:
                        books = self.library.search_books(query)
                        self._display_books_table(books, f"Search Results for '{query}'")
                elif choice == "5":
                    title = self.prompt("Enter title keyword")
                    if title:
                        books = self.library.search_books_by_title(title)
                        self._display_books_table(books, f"Books matching title '{title}'")
                elif choice == "6":
                    author = self.prompt("Enter author name")
                    if author:
                        books = self.library.search_books_by_author(author)
                        self._display_books_table(books, f"Books by author '{author}'")
                elif choice == "7":
                    category = self.prompt("Enter category name")
                    if category:
                        books = self.library.search_books_by_category(category)
                        self._display_books_table(books, f"Books in category '{category}'")
                elif choice == "8":
                    self._action_add_book()
                elif choice == "9":
                    self._action_edit_book()
                elif choice == "10":
                    self._action_delete_book()
                elif choice == "0":
                    break
                else:
                    self.print_error("Invalid choice. Please select 0-10.")
            except BookVaultError as e:
                self.print_error(str(e))
            except Exception as e:
                self.print_error(f"Unexpected error: {e}")

            input("\nPress Enter to continue...")

    def _display_books_table(self, books: List[Book], title: str) -> None:
        self.print_header(title)
        headers = ["ID", "Title", "Author", "ISBN", "Category", "Copies (Avail/Total)", "Year"]
        rows = [
            [
                b.id,
                b.title,
                b.author,
                b.isbn,
                b.category,
                f"{b.available_copies}/{b.total_copies}",
                b.published_year or "N/A",
            ]
            for b in books
        ]
        self.print_table(headers, rows)

    def _action_add_book(self) -> None:
        self.print_header("Add New Book")
        title = self.prompt("Book Title")
        author = self.prompt("Author")
        isbn = self.prompt("ISBN (10 or 13 digits)")
        category = self.prompt("Category/Genre")
        copies_str = self.prompt("Total Copies", default="1")
        year_str = self.prompt("Publication Year (Optional)", default="")

        copies = int(copies_str) if copies_str else 1
        year = int(year_str) if year_str else None

        book = self.library.add_book(
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            total_copies=copies,
            published_year=year,
        )
        self.print_success(f"Book '{book.title}' added successfully with ID #{book.id}!")

    def _action_edit_book(self) -> None:
        self.print_header("Edit Book")
        book_id_str = self.prompt("Enter Book ID to edit")
        if not book_id_str.isdigit():
            self.print_error("Book ID must be numeric.")
            return

        book = self.library.get_book_by_id(int(book_id_str))
        print(f"\nEditing: #{book.id} - '{book.title}' by {book.author}")
        print("Leave blank to keep existing value.\n")

        title = input(f"New Title [{book.title}]: ").strip() or None
        author = input(f"New Author [{book.author}]: ").strip() or None
        isbn = input(f"New ISBN [{book.isbn}]: ").strip() or None
        category = input(f"New Category [{book.category}]: ").strip() or None
        copies_input = input(f"New Total Copies [{book.total_copies}]: ").strip()
        copies = int(copies_input) if copies_input else None
        year_input = input(f"New Year [{book.published_year or ''}]: ").strip()
        year = int(year_input) if year_input else None

        updated = self.library.edit_book(
            book_id=book.id,
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            total_copies=copies,
            published_year=year,
        )
        self.print_success(f"Book #{updated.id} updated successfully!")

    def _action_delete_book(self) -> None:
        self.print_header("Delete Book")
        book_id_str = self.prompt("Enter Book ID to delete")
        if not book_id_str.isdigit():
            self.print_error("Book ID must be numeric.")
            return
        book_id = int(book_id_str)
        book = self.library.get_book_by_id(book_id)

        confirm = self.prompt(f"Are you sure you want to delete '{book.title}'? (y/N)", default="N")
        if confirm.lower() == "y":
            self.library.delete_book(book_id)
            self.print_success(f"Book ID #{book_id} ('{book.title}') deleted successfully.")
        else:
            print("Deletion cancelled.")

    # -------------------------------------------------------------------------
    # 2. MEMBER MANAGEMENT MENU
    # -------------------------------------------------------------------------

    def menu_member_management(self) -> None:
        while True:
            self.print_header("Member Management")
            print("  1. View All Registered Members")
            print("  2. Search Members (Name, Email, Phone)")
            print("  3. Register New Member")
            print("  4. Edit Member Details")
            print("  5. Remove Member")
            print("  6. View Member Borrowing History")
            print("  0. Back to Main Menu")

            choice = input("\nEnter choice (0-6): ").strip()
            try:
                if choice == "1":
                    members = self.library.get_all_members()
                    self._display_members_table(members, "Registered Members")
                elif choice == "2":
                    query = self.prompt("Enter member search query")
                    if query:
                        members = self.library.search_members(query)
                        self._display_members_table(members, f"Members matching '{query}'")
                elif choice == "3":
                    self._action_register_member()
                elif choice == "4":
                    self._action_edit_member()
                elif choice == "5":
                    self._action_remove_member()
                elif choice == "6":
                    self._action_member_history()
                elif choice == "0":
                    break
                else:
                    self.print_error("Invalid choice. Please select 0-6.")
            except BookVaultError as e:
                self.print_error(str(e))
            except Exception as e:
                self.print_error(f"Unexpected error: {e}")

            input("\nPress Enter to continue...")

    def _display_members_table(self, members: List[Member], title: str) -> None:
        self.print_header(title)
        headers = ["ID", "Name", "Email", "Phone", "Max Allowed", "Status", "Joined"]
        rows = [
            [
                m.id,
                m.name,
                m.email,
                m.phone,
                m.max_books_allowed,
                "Active" if m.is_active else "Inactive",
                m.created_at[:10] if m.created_at else "N/A",
            ]
            for m in members
        ]
        self.print_table(headers, rows)

    def _action_register_member(self) -> None:
        self.print_header("Register New Member")
        name = self.prompt("Member Full Name")
        email = self.prompt("Email Address")
        phone = self.prompt("Phone Number")
        address = self.prompt("Mailing Address (Optional)", default="")
        max_str = self.prompt("Max Books Allowed", default="5")
        max_books = int(max_str) if max_str else 5

        member = self.library.register_member(
            name=name,
            email=email,
            phone=phone,
            address=address,
            max_books_allowed=max_books,
        )
        self.print_success(f"Member '{member.name}' registered successfully with ID #{member.id}!")

    def _action_edit_member(self) -> None:
        self.print_header("Edit Member")
        member_id_str = self.prompt("Enter Member ID to edit")
        if not member_id_str.isdigit():
            self.print_error("Member ID must be numeric.")
            return

        member = self.library.get_member_by_id(int(member_id_str))
        print(f"\nEditing Member: #{member.id} - {member.name}")
        print("Leave blank to keep existing value.\n")

        name = input(f"New Name [{member.name}]: ").strip() or None
        email = input(f"New Email [{member.email}]: ").strip() or None
        phone = input(f"New Phone [{member.phone}]: ").strip() or None
        address = input(f"New Address [{member.address}]: ").strip() or None
        max_input = input(f"New Max Books [{member.max_books_allowed}]: ").strip()
        max_books = int(max_input) if max_input else None
        active_input = input(f"Is Active? (y/n) [{'y' if member.is_active else 'n'}]: ").strip()
        is_active = (active_input.lower() == "y") if active_input else None

        updated = self.library.edit_member(
            member_id=member.id,
            name=name,
            email=email,
            phone=phone,
            address=address,
            max_books_allowed=max_books,
            is_active=is_active,
        )
        self.print_success(f"Member #{updated.id} updated successfully!")

    def _action_remove_member(self) -> None:
        self.print_header("Remove Member")
        member_id_str = self.prompt("Enter Member ID to remove")
        if not member_id_str.isdigit():
            self.print_error("Member ID must be numeric.")
            return
        member_id = int(member_id_str)
        member = self.library.get_member_by_id(member_id)

        confirm = self.prompt(f"Are you sure you want to remove member '{member.name}'? (y/N)", default="N")
        if confirm.lower() == "y":
            self.library.remove_member(member_id)
            self.print_success(f"Member #{member_id} ('{member.name}') removed successfully.")
        else:
            print("Removal cancelled.")

    def _action_member_history(self) -> None:
        member_id_str = self.prompt("Enter Member ID to view borrowing history")
        if not member_id_str.isdigit():
            self.print_error("Member ID must be numeric.")
            return
        member = self.library.get_member_by_id(int(member_id_str))
        loans = self.library.get_member_borrowing_history(member.id)
        self._display_loans_table(loans, f"Borrowing History for {member.name} (ID #{member.id})")

    # -------------------------------------------------------------------------
    # 3. BORROWING & LOAN OPERATIONS MENU
    # -------------------------------------------------------------------------

    def menu_loan_operations(self) -> None:
        while True:
            self.print_header("Borrow & Return Operations")
            print("  1. Borrow a Book (Checkout)")
            print("  2. Return a Book (Checkin by Loan ID)")
            print("  3. Return a Book (by Member ID & Book ID)")
            print("  4. View All Active Loans")
            print("  5. View Overdue Loans")
            print("  6. View Complete Historical Loan Ledger")
            print("  0. Back to Main Menu")

            choice = input("\nEnter choice (0-6): ").strip()
            try:
                if choice == "1":
                    self._action_borrow_book()
                elif choice == "2":
                    self._action_return_by_loan_id()
                elif choice == "3":
                    self._action_return_by_member_and_book()
                elif choice == "4":
                    loans = self.library.get_active_loans()
                    self._display_loans_table(loans, "Currently Active Loans")
                elif choice == "5":
                    loans = self.library.get_overdue_loans()
                    self._display_loans_table(loans, "⚠️ Overdue Loans")
                elif choice == "6":
                    loans = self.library.get_all_loans()
                    self._display_loans_table(loans, "Complete Loan History Ledger")
                elif choice == "0":
                    break
                else:
                    self.print_error("Invalid choice. Please select 0-6.")
            except BookVaultError as e:
                self.print_error(str(e))
            except Exception as e:
                self.print_error(f"Unexpected error: {e}")

            input("\nPress Enter to continue...")

    def _display_loans_table(self, loans: List[Loan], title: str) -> None:
        self.print_header(title)
        headers = ["Loan ID", "Book Title", "Member Name", "Borrow Date", "Due Date", "Return Date", "Status"]
        rows = [
            [
                l.id,
                l.book_title or f"Book #{l.book_id}",
                l.member_name or f"Member #{l.member_id}",
                l.borrow_date,
                l.due_date,
                l.return_date or "---",
                l.dynamic_status + (f" (+{l.overdue_days}d)" if l.is_currently_overdue else ""),
            ]
            for l in loans
        ]
        self.print_table(headers, rows)

    def _action_borrow_book(self) -> None:
        self.print_header("Borrow a Book")
        member_id_str = self.prompt("Enter Member ID")
        book_id_str = self.prompt("Enter Book ID")
        duration_str = self.prompt("Loan Duration in Days", default="14")

        if not member_id_str.isdigit() or not book_id_str.isdigit() or not duration_str.isdigit():
            self.print_error("Member ID, Book ID, and Duration must all be numeric.")
            return

        loan = self.library.borrow_book(
            book_id=int(book_id_str),
            member_id=int(member_id_str),
            loan_days=int(duration_str),
        )
        self.print_success(
            f"Loan #{loan.id} recorded! Book '{loan.book_title}' checked out to '{loan.member_name}'.\n"
            f"Due Date: {loan.due_date}"
        )

    def _action_return_by_loan_id(self) -> None:
        self.print_header("Return Book by Loan ID")
        loan_id_str = self.prompt("Enter Loan ID to return")
        if not loan_id_str.isdigit():
            self.print_error("Loan ID must be numeric.")
            return

        loan = self.library.return_book(int(loan_id_str))
        status_note = f" (Overdue by {loan.overdue_days} days)" if loan.is_currently_overdue else ""
        self.print_success(
            f"Book '{loan.book_title}' returned successfully by '{loan.member_name}' on {loan.return_date}!{status_note}"
        )

    def _action_return_by_member_and_book(self) -> None:
        self.print_header("Return Book by Member & Book ID")
        member_id_str = self.prompt("Enter Member ID")
        book_id_str = self.prompt("Enter Book ID")
        if not member_id_str.isdigit() or not book_id_str.isdigit():
            self.print_error("Member ID and Book ID must be numeric.")
            return

        loan = self.library.return_book_by_member_and_book(int(member_id_str), int(book_id_str))
        self.print_success(
            f"Book '{loan.book_title}' returned successfully by '{loan.member_name}' on {loan.return_date}!"
        )

    # -------------------------------------------------------------------------
    # 4. REPORTS MENU
    # -------------------------------------------------------------------------

    def menu_reports(self) -> None:
        while True:
            self.print_header("Analytics & Reports")
            print("  1. Library KPI Dashboard Summary")
            print("  2. Overdue Loans Audit Report")
            print("  3. Most Borrowed Books Leaderboard")
            print("  4. Category Distribution Breakdown")
            print("  0. Back to Main Menu")

            choice = input("\nEnter choice (0-4): ").strip()
            try:
                if choice == "1":
                    self._display_dashboard_kpis()
                elif choice == "2":
                    overdue_data = self.reports.get_overdue_report_data()
                    self.print_header("Overdue Loans Audit")
                    headers = ["Loan ID", "Book Title", "Member Name", "Borrow Date", "Due Date", "Days Overdue"]
                    rows = [
                        [d["id"], d["book_title"], d["member_name"], d["borrow_date"], d["due_date"], f"+{d['overdue_days']} days"]
                        for d in overdue_data
                    ]
                    self.print_table(headers, rows)
                elif choice == "3":
                    limit_str = self.prompt("Leaderboard size limit", default="10")
                    limit = int(limit_str) if limit_str.isdigit() else 10
                    ranking = self.reports.get_most_borrowed_books(limit=limit)
                    self.print_header(f"Top {limit} Most Borrowed Books")
                    headers = ["Rank", "Book Title", "Author", "Category", "Times Borrowed", "Current Available"]
                    rows = [
                        [idx + 1, r["title"], r["author"], r["category"], r["borrow_count"], f"{r['available_copies']}/{r['total_copies']}"]
                        for idx, r in enumerate(ranking)
                    ]
                    self.print_table(headers, rows)
                elif choice == "4":
                    dist = self.reports.get_category_distribution()
                    self.print_header("Category Distribution Breakdown")
                    headers = ["Category", "Unique Titles", "Total Copies", "Available Copies"]
                    rows = [[r["category"], r["titles_count"], r["total_copies"], r["available_copies"]] for r in dist]
                    self.print_table(headers, rows)
                elif choice == "0":
                    break
                else:
                    self.print_error("Invalid choice. Please select 0-4.")
            except Exception as e:
                self.print_error(f"Failed to generate report: {e}")

            input("\nPress Enter to continue...")

    def _display_dashboard_kpis(self) -> None:
        metrics = self.reports.get_summary_metrics()
        b = metrics["books"]
        m = metrics["members"]
        l = metrics["loans"]

        self.print_header("Library KPI Dashboard")
        print(f"\n📚 [BOOKS INVENTORY]")
        print(f"   • Total Unique Titles : {b['total_titles']}")
        print(f"   • Total Physical Copies: {b['total_copies']}")
        print(f"   • Available Copies     : {b['available_copies']}")
        print(f"   • Borrowed Copies      : {b['borrowed_copies']}")

        print(f"\n👥 [MEMBERSHIP STATS]")
        print(f"   • Total Registered     : {m['total_members']}")
        print(f"   • Active Members       : {m['active_members']}")
        print(f"   • Inactive Members     : {m['inactive_members']}")

        print(f"\n🔄 [LOAN TRANSACTIONS]")
        print(f"   • Total Transactions   : {l['total_transactions']}")
        print(f"   • Currently Active     : {l['active_loans']}")
        print(f"   • Successfully Returned: {l['returned_loans']}")
        print(f"   • Currently Overdue    : {l['overdue_loans']} ⚠️")

    # -------------------------------------------------------------------------
    # 5. CSV EXPORT MENU
    # -------------------------------------------------------------------------

    def menu_csv_export(self) -> None:
        while True:
            self.print_header("CSV Data Export")
            print("  1. Export Books Catalog to CSV")
            print("  2. Export Members Directory to CSV")
            print("  3. Export Active Loans to CSV")
            print("  4. Export Full Loan History Ledger to CSV")
            print("  5. Export Overdue Audit Report to CSV")
            print("  6. Export Most Borrowed Books to CSV")
            print("  7. Export Complete Library Snapshot (All 6 Reports)")
            print("  0. Back to Main Menu")

            choice = input("\nEnter choice (0-7): ").strip()
            try:
                if choice == "1":
                    path = self.reports.export_books_to_csv()
                    self.print_success(f"Books exported to:\n  {path}")
                elif choice == "2":
                    path = self.reports.export_members_to_csv()
                    self.print_success(f"Members exported to:\n  {path}")
                elif choice == "3":
                    path = self.reports.export_loans_to_csv(only_active=True)
                    self.print_success(f"Active loans exported to:\n  {path}")
                elif choice == "4":
                    path = self.reports.export_loans_to_csv(only_active=False)
                    self.print_success(f"Full loan history exported to:\n  {path}")
                elif choice == "5":
                    path = self.reports.export_overdue_to_csv()
                    self.print_success(f"Overdue report exported to:\n  {path}")
                elif choice == "6":
                    path = self.reports.export_most_borrowed_to_csv()
                    self.print_success(f"Most borrowed report exported to:\n  {path}")
                elif choice == "7":
                    p1 = self.reports.export_books_to_csv()
                    p2 = self.reports.export_members_to_csv()
                    p3 = self.reports.export_loans_to_csv(only_active=True)
                    p4 = self.reports.export_loans_to_csv(only_active=False)
                    p5 = self.reports.export_overdue_to_csv()
                    p6 = self.reports.export_most_borrowed_to_csv()
                    self.print_success("All 6 CSV reports exported successfully:")
                    for p in [p1, p2, p3, p4, p5, p6]:
                        print(f"  • {p}")
                elif choice == "0":
                    break
                else:
                    self.print_error("Invalid choice. Please select 0-7.")
            except Exception as e:
                self.print_error(f"CSV Export failed: {e}")

            input("\nPress Enter to continue...")

    # -------------------------------------------------------------------------
    # 6. DATABASE ADMIN & SEEDING MENU
    # -------------------------------------------------------------------------

    def menu_database_admin(self) -> None:
        while True:
            self.print_header("Database Administration & Demo Data")
            print("  1. Seed Realistic Sample Demo Data (Books, Members, Loans)")
            print("  2. Reset Database (Wipes all tables and recreates schema)")
            print("  3. View Database Connection & File Information")
            print("  0. Back to Main Menu")

            choice = input("\nEnter choice (0-3): ").strip()
            try:
                if choice == "1":
                    stats = self.db.seed_sample_data()
                    if stats["books"] == 0 and stats["members"] == 0:
                        print("\nDatabase already contains data. No new seeds added.")
                    else:
                        self.print_success(
                            f"Demo data seeded successfully: {stats['books']} books, "
                            f"{stats['members']} members, {stats['loans']} loans."
                        )
                elif choice == "2":
                    confirm = self.prompt("WARNING: This will erase all data! Type 'CONFIRM' to proceed")
                    if confirm == "CONFIRM":
                        self.db.reset_database()
                        self.print_success("Database has been reset to an empty state.")
                    else:
                        print("Reset aborted.")
                elif choice == "3":
                    self.print_header("Database Info")
                    print(f"  Location : {self.db.db_path}")
                    exists = os.path.exists(self.db.db_path)
                    size = os.path.getsize(self.db.db_path) if exists else 0
                    print(f"  Exists   : {exists}")
                    print(f"  File Size: {size} bytes")
                elif choice == "0":
                    break
                else:
                    self.print_error("Invalid choice. Please select 0-3.")
            except Exception as e:
                self.print_error(f"Database admin operation failed: {e}")

            input("\nPress Enter to continue...")
