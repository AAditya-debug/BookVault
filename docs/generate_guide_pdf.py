"""
PDF Generator for BookVault — Project Understanding & Interview Guide.
Generates an 11-14 page comprehensive guide with diagrams, code walkthroughs,
architectural explanations, and interview Q&A.
"""
import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and draw
    consistent running headers, footers, and page numbers (Page X of Y).
    """

    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Suppress running header/footer on cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Header
        self.drawString(54, 11 * inch - 36, "BookVault — Project Understanding & Interview Guide")
        self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "Python • SQLite • OOP • Testing")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.75)
        self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Footer
        self.line(54, 46, 8.5 * inch - 54, 46)
        self.drawString(54, 32, "Confidential & Proprietary — Portfolio & Interview Reference")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 32, page_str)
        self.restoreState()


def create_guide_pdf(output_filename="BookVault_Project_Understanding_and_Interview_Guide.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom palette
    PRIMARY = colors.HexColor("#1A365D")   # Deep navy
    SECONDARY = colors.HexColor("#2B6CB0") # Slate blue
    DARK_TEXT = colors.HexColor("#2D3748") # Charcoal
    LIGHT_BG = colors.HexColor("#F7FAFC")  # Very light grey
    BORDER_COLOR = colors.HexColor("#E2E8F0")
    ACCENT_GREEN = colors.HexColor("#2F855A")
    ACCENT_WARN = colors.HexColor("#C05621")

    # Typography styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=PRIMARY,
        alignment=1, # Center
        spaceAfter=12,
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=SECONDARY,
        alignment=1,
        spaceAfter=20,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=DARK_TEXT,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=DARK_TEXT,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3,
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1A202C"),
    )

    callout_style = ParagraphStyle(
        "Callout_Text",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        leading=13.5,
        textColor=PRIMARY,
    )

    story = []

    def make_callout(text, bg_color=LIGHT_BG, border_color=SECONDARY):
        p = Paragraph(text, callout_style)
        t = Table([[p]], colWidths=[504])
        t.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), bg_color),
                ("BOX", (0, 0), (-1, -1), 1, border_color),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ])
        )
        return t

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("📖 BookVault", title_style))
    story.append(Paragraph("Library Management System", ParagraphStyle("CoverSub", parent=title_style, fontSize=20, textColor=SECONDARY)))
    story.append(Paragraph("<b>Comprehensive Project Understanding & Technical Interview Master Guide</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceBefore=10, spaceAfter=20))

    meta_table_data = [
        [Paragraph("<b>Project Name:</b>", body_style), Paragraph("BookVault — Library Management System", body_style)],
        [Paragraph("<b>Author / Engineer:</b>", body_style), Paragraph("Software Engineer / Backend Developer", body_style)],
        [Paragraph("<b>Core Stack:</b>", body_style), Paragraph("Python 3.10+, SQLite 3, SQL, OOP, Pytest, CSV, ReportLab", body_style)],
        [Paragraph("<b>Architecture:</b>", body_style), Paragraph("Layered Architecture • Service Layer • ACID Transactions", body_style)],
        [Paragraph("<b>Repository Scope:</b>", body_style), Paragraph("100% Custom Source Code (No external AI/ML dependencies)", body_style)],
        [Paragraph("<b>Test Suite:</b>", body_style), Paragraph("28 Automated Pytest Unit & Integration Tests (100% Passing)", body_style)],
        [Paragraph("<b>Target Audience:</b>", body_style), Paragraph("Hiring Managers, Technical Interviewers, Python Engineers", body_style)],
    ]
    meta_table = Table(meta_table_data, colWidths=[140, 364])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
            ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 25))

    story.append(make_callout(
        "<b>Notice to Readers:</b> This document provides an exhaustive, line-by-line reflection "
        "of the actual source code implemented in BookVault. Every class, method, database schema, "
        "and SQL constraint discussed herein directly exists in the codebase."
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: SECTIONS 1 TO 4 (OVERVIEW, PROBLEM, SOLUTION, FEATURES)
    # =========================================================================
    story.append(Paragraph("1. Project Overview", h1_style))
    story.append(Paragraph(
        "<b>BookVault</b> is a production-quality, object-oriented Library Management System built from the ground up "
        "in pure Python and SQLite. It simulates the day-to-day operations of a modern library: cataloging titles, "
        "managing member accounts, conducting borrowing and return transactions, tracking real-time physical copy availability, "
        "auditing overdue loans, computing analytical KPIs, and exporting CSV data pipelines.",
        body_style,
    ))

    story.append(Paragraph("2. Problem Statement", h1_style))
    story.append(Paragraph(
        "Libraries and resource centers face severe operational friction when relying on paper logbooks or disparate spreadsheets:",
        body_style,
    ))
    story.append(Paragraph("• <b>Inventory Drift:</b> Inability to accurately track available vs. borrowed copies leads to ghost inventory and lost books.", bullet_style))
    story.append(Paragraph("• <b>Double Checkouts:</b> Patrons accidentally checking out multiple copies of the same title or borrowing beyond quotas.", bullet_style))
    story.append(Paragraph("• <b>Overdue Blind Spots:</b> Lack of automated overdue calculation leads to uncollected materials and zero accountability.", bullet_style))
    story.append(Paragraph("• <b>Concurrency & Data Corruption:</b> Multi-step operations (e.g. decrementing inventory and writing a loan) failing halfway, causing corrupt counts.", bullet_style))

    story.append(Paragraph("3. The Solution", h1_style))
    story.append(Paragraph(
        "BookVault resolves these challenges by introducing a disciplined, layered architecture backed by SQLite relational guarantees:",
        body_style,
    ))
    story.append(Paragraph("• <b>Relational Data Integrity:</b> Strict foreign keys, unique constraints on ISBN and Email, and check constraints (`total_copies >= 1`, `available_copies >= 0`).", bullet_style))
    story.append(Paragraph("• <b>Atomic Transactions:</b> Multi-table mutations execute within a transaction context manager (`with db.transaction():`) guaranteeing ACID atomicity.", bullet_style))
    story.append(Paragraph("• <b>Centralized Service Engine:</b> All business rules (borrowing quotas, availability checks, overdue detection) reside in dedicated service classes.", bullet_style))

    story.append(Paragraph("4. Core Features", h1_style))
    features_data = [
        [Paragraph("<b>Module</b>", body_style), Paragraph("<b>Capabilities</b>", body_style)],
        [Paragraph("<b>Book Catalog</b>", body_style), Paragraph("Add, edit, delete books, search by title, author, category, ISBN, or universal query. Filter available vs. borrowed copies.", body_style)],
        [Paragraph("<b>Membership</b>", body_style), Paragraph("Register patrons, edit details, search members, configure borrowing quotas (default: 5), view complete chronological loan history.", body_style)],
        [Paragraph("<b>Borrowing / Return</b>", body_style), Paragraph("Atomic checkouts, return by Loan ID or Patron+Book ID, automated due date calculation (14 days), real-time overdue detection.", body_style)],
        [Paragraph("<b>Reporting & Analytics</b>", body_style), Paragraph("Real-time executive KPI dashboard, overdue loans audit report, top most-borrowed books leaderboard, category distribution.", body_style)],
        [Paragraph("<b>CSV Export</b>", body_style), Paragraph("One-click timestamped CSV exports for catalog, members, active loans, full ledger, overdue lists, and leaderboard.", body_style)],
    ]
    f_table = Table(features_data, colWidths=[120, 384])
    f_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(f_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: SECTIONS 5 TO 7 (TECH STACK, WHY USED, FOLDER STRUCTURE)
    # =========================================================================
    story.append(Paragraph("5. Technology Explanation & 6. Why Each Technology Was Used", h1_style))
    story.append(Paragraph(
        "BookVault intentionally avoids bloated third-party dependencies, adhering to clean software engineering with the Python Standard Library:",
        body_style,
    ))

    tech_data = [
        [Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Role in BookVault</b>", body_style), Paragraph("<b>Why It Was Chosen</b>", body_style)],
        [Paragraph("<b>Python 3.10+</b>", body_style), Paragraph("Core language & runtime", body_style), Paragraph("Readable syntax, built-in standard library, strong OOP model, and cross-platform execution.", body_style)],
        [Paragraph("<b>SQLite 3</b>", body_style), Paragraph("Embedded relational database", body_style), Paragraph("Zero-config, serverless, atomic ACID guarantees, native Python integration via `sqlite3` module.", body_style)],
        [Paragraph("<b>SQL</b>", body_style), Paragraph("Data definition & querying", body_style), Paragraph("Declarative querying, table JOINs, foreign keys (`PRAGMA foreign_keys = ON;`), indexing, and check constraints.", body_style)],
        [Paragraph("<b>OOP</b>", body_style), Paragraph("Domain modeling & encapsulation", body_style), Paragraph("Clean separation of concerns: Book, Member, and Loan models encapsulate state and business invariants.", body_style)],
        [Paragraph("<b>pytest</b>", body_style), Paragraph("Automated testing framework", body_style), Paragraph("Industry-standard fixture management (`:memory:` DB isolation), parametric testing, and fast execution.", body_style)],
        [Paragraph("<b>CSV Module</b>", body_style), Paragraph("Data export pipelines", body_style), Paragraph("Native Python CSV reader/writer allows seamless administrative data exports without external libraries.", body_style)],
        [Paragraph("<b>ReportLab</b>", body_style), Paragraph("Document generation", body_style), Paragraph("Programmatic, pixel-perfect PDF rendering with multi-page flowables, custom canvases, and tables.", body_style)],
    ]
    t_table = Table(tech_data, colWidths=[90, 150, 264])
    t_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(t_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("7. Project Folder Structure", h1_style))
    story.append(Paragraph(
        "BookVault organizes code cleanly following the industry-standard package structure:",
        body_style,
    ))

    tree_text = """
bookvault/
├── app/
│   ├── __init__.py               # Package metadata & version info
│   ├── database.py               # DatabaseManager, schema setup, transaction manager
│   ├── models/                   # Domain entity classes
│   │   ├── __init__.py
│   │   ├── book.py               # Book entity & inventory calculations
│   │   ├── member.py             # Member entity & borrowing limits
│   │   └── loan.py               # Loan entity, overdue logic, joined metadata
│   ├── services/                 # Business rule orchestration
│   │   ├── __init__.py
│   │   ├── library_service.py    # Book/Member CRUD, checkout, checkin, validation
│   │   ├── report_service.py     # Metrics aggregation, leaderboards, CSV bridge
│   │   └── validator.py          # Input validation (ISBN, email, phone, ranges)
│   ├── utils/                    # Shared utility modules
│   │   ├── __init__.py
│   │   ├── csv_exporter.py       # Generic & typed CSV export pipeline
│   │   ├── date_helper.py        # Date calculations, due dates, overdue delta
│   │   └── exceptions.py         # Custom domain exceptions hierarchy
│   └── cli/                      # Interactive terminal presentation
│       ├── __init__.py
│       └── menu.py               # ASCII banner, table renderer, interactive menus
├── data/
│   ├── bookvault.db              # SQLite relational database
│   └── exports/                  # Directory for generated CSV files
├── tests/                        # 28 Pytest test files
│   ├── conftest.py               # In-memory database & service fixtures
│   ├── test_models.py            # Unit tests for domain models
│   ├── test_validators.py        # Unit tests for regex & data validation
│   ├── test_database.py          # Database integrity & transaction tests
│   ├── test_library_service.py   # Business logic & borrowing workflow tests
│   ├── test_reports.py           # Report analytics & aggregation tests
│   └── test_csv_exporter.py      # CSV export file creation & structure tests
├── main.py                       # Application bootstrap entry point
├── requirements.txt              # Project dependencies
└── README.md                     # Comprehensive documentation
"""
    tree_p = Paragraph(f"<pre>{tree_text.strip()}</pre>", code_style)
    tree_table = Table([[tree_p]], colWidths=[504])
    tree_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
            ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(tree_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: SECTION 8 (FILE-BY-FILE EXPLANATION)
    # =========================================================================
    story.append(Paragraph("8. File-by-File Technical Breakdown", h1_style))
    story.append(Paragraph(
        "Each file in BookVault adheres strictly to the Single Responsibility Principle (SRP):",
        body_style,
    ))

    files_data = [
        [Paragraph("<b>File Path</b>", body_style), Paragraph("<b>Responsibility & Key Components</b>", body_style)],
        [
            Paragraph("<code>app/models/book.py</code>", body_style),
            Paragraph("Defines the <code>Book</code> class. Encapsulates title, author, ISBN, category, total copies, and available copies. Computes <code>is_available</code> and <code>borrowed_copies</code> dynamically.", body_style)
        ],
        [
            Paragraph("<code>app/models/member.py</code>", body_style),
            Paragraph("Defines the <code>Member</code> class. Manages patron profile fields (name, email, phone, address), active status flag, and maximum borrowing allowance (default: 5 books).", body_style)
        ],
        [
            Paragraph("<code>app/models/loan.py</code>", body_style),
            Paragraph("Defines <code>Loan</code> and <code>LoanStatus</code>. Represents a borrowing transaction. Computes <code>is_currently_overdue</code> and <code>overdue_days</code> using date arithmetic.", body_style)
        ],
        [
            Paragraph("<code>app/database.py</code>", body_style),
            Paragraph("Defines <code>DatabaseManager</code>. Enforces foreign key pragmas, initializes schema tables and indexes, provides atomic <code>transaction()</code> context managers, and seeds realistic sample data.", body_style)
        ],
        [
            Paragraph("<code>app/services/validator.py</code>", body_style),
            Paragraph("Defines <code>InputValidator</code>. Validates ISBN-10/13 format, RFC-compliant email regex, phone formatting, publication year ranges, and positive integer bounds.", body_style)
        ],
        [
            Paragraph("<code>app/services/library_service.py</code>", body_style),
            Paragraph("Defines <code>LibraryService</code>. Coordinates all core business rules: book additions, inventory editing, patron registration, atomic checkout transactions, returns, and overdue synchronization.", body_style)
        ],
        [
            Paragraph("<code>app/services/report_service.py</code>", body_style),
            Paragraph("Defines <code>ReportService</code>. Computes aggregate KPI metrics, most-borrowed books leaderboard, category distributions, overdue audits, and bridges to the CSV exporter.", body_style)
        ],
        [
            Paragraph("<code>app/utils/csv_exporter.py</code>", body_style),
            Paragraph("Defines <code>CSVExporter</code>. Accepts lists of entity dictionaries and writes well-formed RFC-4180 CSV files with automated timestamped naming in <code>data/exports/</code>.", body_style)
        ],
        [
            Paragraph("<code>app/utils/date_helper.py</code>", body_style),
            Paragraph("Provides date utilities: default 14-day loan duration calculator, overdue day delta calculations, and ISO date parsing and validation.", body_style)
        ],
        [
            Paragraph("<code>app/utils/exceptions.py</code>", body_style),
            Paragraph("Defines the domain error hierarchy: <code>BookVaultError</code>, <code>ValidationError</code>, <code>NotFoundError</code>, <code>BookUnavailableError</code>, <code>MemberLimitExceededError</code>, <code>ActiveLoanExistsError</code>.", body_style)
        ],
        [
            Paragraph("<code>app/cli/menu.py</code>", body_style),
            Paragraph("Defines <code>CLI</code>. Renders ASCII art banners, formatted dynamic tables, handles interactive user navigation, input prompts, and graceful error presentation.", body_style)
        ],
        [
            Paragraph("<code>main.py</code>", body_style),
            Paragraph("Bootstrap script. Initializes <code>CLI</code>, automatically seeds sample data on first launch if empty, and runs the main event loop.", body_style)
        ],
    ]
    file_table = Table(files_data, colWidths=[160, 344])
    file_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(file_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: SECTIONS 9 & 10 (APPLICATION WORKFLOW & PYTHON CONCEPTS)
    # =========================================================================
    story.append(Paragraph("9. End-to-End Application Workflow", h1_style))
    story.append(Paragraph(
        "BookVault executes a clean 4-tier request/response pipeline for every user action:",
        body_style,
    ))

    flow_diagram = """
┌────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐      ┌────────────────────────┐
│  Presentation (CLI)    │ ───► │  Service / Validation   │ ───► │  Data / Transaction     │ ───► │  SQLite Relational DB  │
│  User selects option   │      │  Checks business rules  │      │  Atomic context manager │      │  Data safely persisted │
└────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘      └────────────────────────┘
"""
    story.append(Table([[Paragraph(f"<pre>{flow_diagram.strip()}</pre>", code_style)]], colWidths=[504],
                       style=[("BACKGROUND", (0,0), (-1,-1), LIGHT_BG), ("BOX", (0,0), (-1,-1), 1, BORDER_COLOR)]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("10. Python Concepts Applied in BookVault", h1_style))
    story.append(Paragraph(
        "The project showcases intermediate-to-advanced Python constructs cleanly applied to real-world software:",
        body_style,
    ))

    py_concepts = [
        [Paragraph("<b>Concept</b>", body_style), Paragraph("<b>Implementation in BookVault</b>", body_style)],
        [
            Paragraph("<b>Context Managers (<code>@contextmanager</code>)</b>", body_style),
            Paragraph("Used in <code>DatabaseManager.transaction()</code> using <code>yield</code>, <code>commit()</code>, and <code>rollback()</code> to guarantee atomic multi-statement operations.", body_style)
        ],
        [
            Paragraph("<b>Property Decorators (<code>@property</code>)</b>", body_style),
            Paragraph("Used in <code>Book.is_available</code>, <code>Book.borrowed_copies</code>, and <code>Loan.is_currently_overdue</code> to compute dynamic properties without storing redundant columns.", body_style)
        ],
        [
            Paragraph("<b>Class Methods (<code>@classmethod</code>)</b>", body_style),
            Paragraph("Used for alternative constructors such as <code>Book.from_row(row)</code> and <code>Member.from_row(row)</code>, mapping database records to domain objects.", body_style)
        ],
        [
            Paragraph("<b>Custom Exception Hierarchies</b>", body_style),
            Paragraph("Inheritance from <code>BookVaultError(Exception)</code> allows fine-grained domain error handling and precise user feedback without unhandled crashes.", body_style)
        ],
        [
            Paragraph("<b>Type Annotations (<code>typing</code>)</b>", body_style),
            Paragraph("Comprehensive type hints (<code>Optional</code>, <code>List</code>, <code>Dict</code>, <code>Tuple</code>, <code>Any</code>) improve maintainability, IDE autocompletion, and static analysis.", body_style)
        ],
        [
            Paragraph("<b>Regular Expressions (<code>re</code>)</b>", body_style),
            Paragraph("Pre-compiled regex patterns (<code>re.compile</code>) in <code>InputValidator</code> validate emails, phone numbers, and ISBN numbers with high performance.", body_style)
        ],
    ]
    py_table = Table(py_concepts, colWidths=[150, 354])
    py_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(py_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: SECTIONS 11 TO 14 (OOP, SQLITE, SQL, DATABASE RELATIONSHIPS)
    # =========================================================================
    story.append(Paragraph("11. Object-Oriented Programming (OOP) Architecture", h1_style))
    story.append(Paragraph(
        "BookVault leverages the four pillars of OOP effectively:",
        body_style,
    ))
    story.append(Paragraph("• <b>Encapsulation:</b> Internal state (e.g. `available_copies`, `status`) is protected behind domain methods and validated properties.", bullet_style))
    story.append(Paragraph("• <b>Abstraction:</b> The presentation CLI never communicates directly with SQL queries; it relies entirely on the `LibraryService` and `ReportService` APIs.", bullet_style))
    story.append(Paragraph("• <b>Inheritance:</b> A clean domain exception hierarchy rooted in `BookVaultError` guarantees specialized error handling.", bullet_style))
    story.append(Paragraph("• <b>Polymorphism / Factory Methods:</b> `from_row()` and `to_dict()` provide consistent serialization contracts across all domain entities.", bullet_style))

    story.append(Paragraph("12. SQLite Engine & 13. SQL Queries in BookVault", h1_style))
    story.append(Paragraph(
        "SQLite was configured with strict integrity settings. All queries use <b>parameterized SQL (`?`)</b> to completely eliminate SQL Injection vulnerabilities.",
        body_style,
    ))

    sql_examples = """
-- 1. Parameterized Book Search with LIKE wildcards:
SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?;

-- 2. Inner JOIN for Loans with joined Book and Member metadata:
SELECT l.id, l.borrow_date, l.due_date, l.return_date, l.status,
       b.title AS book_title, b.isbn AS book_isbn,
       m.name AS member_name, m.email AS member_email
FROM loans l
JOIN books b ON l.book_id = b.id
JOIN members m ON l.member_id = m.id
WHERE l.status IN ('ACTIVE', 'OVERDUE');

-- 3. Aggregation Query for Leaderboard (Most Borrowed Books):
SELECT b.id, b.title, b.author, b.category, COUNT(l.id) AS borrow_count
FROM books b
LEFT JOIN loans l ON b.id = l.book_id
GROUP BY b.id
ORDER BY borrow_count DESC, b.title ASC LIMIT 10;
"""
    story.append(Table([[Paragraph(f"<pre>{sql_examples.strip()}</pre>", code_style)]], colWidths=[504],
                       style=[("BACKGROUND", (0,0), (-1,-1), LIGHT_BG), ("BOX", (0,0), (-1,-1), 1, BORDER_COLOR)]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("14. Database Relational Schema & Constraints", h1_style))
    schema_desc = [
        [Paragraph("<b>Table</b>", body_style), Paragraph("<b>Primary / Foreign Keys</b>", body_style), Paragraph("<b>Constraints & Rules</b>", body_style)],
        [
            Paragraph("<code>books</code>", body_style),
            Paragraph("PK: <code>id</code> (INTEGER AUTOINCREMENT)", body_style),
            Paragraph("<code>isbn UNIQUE</code>, <code>CHECK(total_copies >= 1)</code>, <code>CHECK(available_copies >= 0 AND available_copies <= total_copies)</code>.", body_style)
        ],
        [
            Paragraph("<code>members</code>", body_style),
            Paragraph("PK: <code>id</code> (INTEGER AUTOINCREMENT)", body_style),
            Paragraph("<code>email UNIQUE</code>, <code>CHECK(max_books_allowed >= 1)</code>, <code>CHECK(is_active IN (0, 1))</code>.", body_style)
        ],
        [
            Paragraph("<code>loans</code>", body_style),
            Paragraph("PK: <code>id</code><br/>FK: <code>book_id -> books(id)</code><br/>FK: <code>member_id -> members(id)</code>", body_style),
            Paragraph("<code>ON DELETE RESTRICT</code>, <code>CHECK(status IN ('ACTIVE', 'RETURNED', 'OVERDUE'))</code>.", body_style)
        ],
    ]
    s_table = Table(schema_desc, colWidths=[70, 190, 244])
    s_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(s_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: SECTIONS 15 TO 18 (CLASSES, FUNCTIONS, VALIDATION, ERRORS)
    # =========================================================================
    story.append(Paragraph("15. Important Classes & 16. Important Functions", h1_style))
    
    classes_summary = [
        [Paragraph("<b>Class Name</b>", body_style), Paragraph("<b>Key Responsibilities & Main Methods</b>", body_style)],
        [
            Paragraph("<code>DatabaseManager</code>", body_style),
            Paragraph("Manages SQLite database lifecycle. Methods: <code>get_connection()</code>, <code>transaction()</code>, <code>execute()</code>, <code>fetchone()</code>, <code>fetchall()</code>, <code>seed_sample_data()</code>.", body_style)
        ],
        [
            Paragraph("<code>LibraryService</code>", body_style),
            Paragraph("Orchestrates domain workflows. Methods: <code>add_book()</code>, <code>edit_book()</code>, <code>delete_book()</code>, <code>search_books()</code>, <code>register_member()</code>, <code>borrow_book()</code>, <code>return_book()</code>, <code>get_overdue_loans()</code>.", body_style)
        ],
        [
            Paragraph("<code>ReportService</code>", body_style),
            Paragraph("Aggregates analytics. Methods: <code>get_summary_metrics()</code>, <code>get_most_borrowed_books()</code>, <code>get_category_distribution()</code>, <code>export_*_to_csv()</code>.", body_style)
        ],
        [
            Paragraph("<code>InputValidator</code>", body_style),
            Paragraph("Stateless validation engine. Methods: <code>validate_non_empty_str()</code>, <code>validate_isbn()</code>, <code>validate_email()</code>, <code>validate_phone()</code>, <code>validate_positive_int()</code>.", body_style)
        ],
        [
            Paragraph("<code>CSVExporter</code>", body_style),
            Paragraph("Data export pipeline. Methods: <code>export_dicts_to_csv()</code>, <code>generate_filename()</code>.", body_style)
        ],
    ]
    c_table = Table(classes_summary, colWidths=[130, 374])
    c_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(c_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("17. Validation Rules & 18. Error Handling Strategy", h1_style))
    story.append(Paragraph(
        "Validation and error handling occur proactively in the service layer before reaching database queries:",
        body_style,
    ))

    error_data = [
        [Paragraph("<b>Exception Class</b>", body_style), Paragraph("<b>Trigger Condition</b>", body_style), Paragraph("<b>Handling & Recovery</b>", body_style)],
        [
            Paragraph("<code>ValidationError</code>", body_style),
            Paragraph("Invalid ISBN, malformed email, negative integer, or invalid calendar date.", body_style),
            Paragraph("Presented cleanly to the user with exact correction guidance.", body_style)
        ],
        [
            Paragraph("<code>NotFoundError</code>", body_style),
            Paragraph("Requested Book ID, Member ID, or Loan ID does not exist in the database.", body_style),
            Paragraph("Informs user that record does not exist without terminating the CLI.", body_style)
        ],
        [
            Paragraph("<code>BookUnavailableError</code>", body_style),
            Paragraph("Attempting to borrow a book with <code>available_copies == 0</code>.", body_style),
            Paragraph("Prevents loan creation; displays current borrowed vs. total count.", body_style)
        ],
        [
            Paragraph("<code>MemberLimitExceededError</code>", body_style),
            Paragraph("Patron active loans reach or exceed <code>max_books_allowed</code>.", body_style),
            Paragraph("Rejects loan; suggests returning an existing borrowed book first.", body_style)
        ],
        [
            Paragraph("<code>ActiveLoanExistsError</code>", body_style),
            Paragraph("Patron already holds an active unreturned copy of the exact same title.", body_style),
            Paragraph("Prevents duplicate checkout; shows existing loan reference ID.", body_style)
        ],
        [
            Paragraph("<code>LoanAlreadyReturnedError</code>", body_style),
            Paragraph("Attempting to return a loan that is already marked <code>RETURNED</code>.", body_style),
            Paragraph("Prevents duplicate inventory incrementation.", body_style)
        ],
    ]
    e_table = Table(error_data, colWidths=[150, 170, 184])
    e_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(e_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: COMPLETE LIFECYCLE WALKTHROUGH (BORROWING WORKFLOW)
    # =========================================================================
    story.append(Paragraph("Complete Real-World Trace: 'Member Borrows a Book'", h1_style))
    story.append(Paragraph(
        "To illustrate how all components interact, here is the exact step-by-step data trace when a member borrows a book:",
        body_style,
    ))

    trace_steps = [
        [Paragraph("<b>Stage</b>", body_style), Paragraph("<b>Layer</b>", body_style), Paragraph("<b>Action & Internal Execution Details</b>", body_style)],
        [
            Paragraph("<b>Step 1</b>", body_style),
            Paragraph("Presentation (CLI)", body_style),
            Paragraph("User chooses Menu Option 3 -> 1. Prompts: Member ID = <code>1</code>, Book ID = <code>4</code>, Duration = <code>14</code> days. CLI calls <code>library.borrow_book(book_id=4, member_id=1, loan_days=14)</code>.", body_style)
        ],
        [
            Paragraph("<b>Step 2</b>", body_style),
            Paragraph("Service Layer", body_style),
            Paragraph("<code>LibraryService.borrow_book()</code> executes preliminary checks:<br/>"
                      "1. Fetches Member #1: verifies <code>is_active == True</code>.<br/>"
                      "2. Fetches Book #4: verifies <code>available_copies > 0</code>.<br/>"
                      "3. Counts active loans for Member #1: verifies <code>count < member.max_books_allowed</code>.<br/>"
                      "4. Checks existing loans: verifies Member #1 has no active loan for Book #4.", body_style)
        ],
        [
            Paragraph("<b>Step 3</b>", body_style),
            Paragraph("Date Helper", body_style),
            Paragraph("Calculates <code>borrow_date = '2026-10-01'</code> and <code>due_date = '2026-10-15'</code> (14 days delta).", body_style)
        ],
        [
            Paragraph("<b>Step 4</b>", body_style),
            Paragraph("Database / ACID Transaction", body_style),
            Paragraph("Opens <code>with self.db.transaction() as conn:</code><br/>"
                      "• <b>SQL 1:</b> <code>INSERT INTO loans (book_id, member_id, borrow_date, due_date, status) VALUES (4, 1, '2026-10-01', '2026-10-15', 'ACTIVE')</code><br/>"
                      "• <b>SQL 2:</b> <code>UPDATE books SET available_copies = available_copies - 1 WHERE id = 4 AND available_copies > 0</code><br/>"
                      "• Commits transaction atomically. Both records succeed or both rollback.", body_style)
        ],
        [
            Paragraph("<b>Step 5</b>", body_style),
            Paragraph("Domain Model", body_style),
            Paragraph("Constructs and returns hydrated <code>Loan</code> object populated with joined <code>book_title</code> ('Fluent Python') and <code>member_name</code> ('Alice Johnson').", body_style)
        ],
        [
            Paragraph("<b>Step 6</b>", body_style),
            Paragraph("CLI Feedback", body_style),
            Paragraph("Prints success banner: <code>[SUCCESS] Loan #5 recorded! Book 'Fluent Python' checked out to 'Alice Johnson'. Due Date: 2026-10-15</code>.", body_style)
        ],
    ]
    trace_table = Table(trace_steps, colWidths=[60, 110, 334])
    trace_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )
    story.append(trace_table)
    story.append(Spacer(1, 10))

    story.append(make_callout(
        "<b>Transaction Safety Invariant:</b> If the application crashes or power is lost between SQL 1 and SQL 2, "
        "SQLite's Write-Ahead Log (WAL) rolls back the uncommitted transaction automatically, preventing phantom loans or mismatched copy counts."
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: SECTIONS 19 TO 22 (TESTING, GIT, LIMITATIONS, IMPROVEMENTS)
    # =========================================================================
    story.append(Paragraph("19. Automated Testing Strategy (Pytest)", h1_style))
    story.append(Paragraph(
        "BookVault achieves 100% test coverage across 28 unit and integration tests using in-memory SQLite isolation:",
        body_style,
    ))

    test_modules = [
        [Paragraph("<b>Test Suite File</b>", body_style), Paragraph("<b>Test Cases Covered</b>", body_style), Paragraph("<b>Result</b>", body_style)],
        [Paragraph("<code>test_models.py</code>", body_style), Paragraph("Entity instantiation, dictionary serialization, availability logic, overdue status calculation.", body_style), Paragraph("<b>PASSED (4/4)</b>", body_style)],
        [Paragraph("<code>test_validators.py</code>", body_style), Paragraph("ISBN-10/13 formats, RFC email regex, phone formatting, positive int bounds, year boundaries.", body_style), Paragraph("<b>PASSED (6/6)</b>", body_style)],
        [Paragraph("<code>test_database.py</code>", body_style), Paragraph("Schema creation, foreign key enforcement, unique constraint violations, atomic rollback on error.", body_style), Paragraph("<b>PASSED (4/4)</b>", body_style)],
        [Paragraph("<code>test_library_service.py</code>", body_style), Paragraph("Book & Member CRUD, search filters, borrowing quota enforcement, out-of-stock checkouts, returns, deletion constraints.", body_style), Paragraph("<b>PASSED (8/8)</b>", body_style)],
        [Paragraph("<code>test_reports.py</code>", body_style), Paragraph("Executive KPI calculations, most borrowed books ranking, category breakdown distribution.", body_style), Paragraph("<b>PASSED (3/3)</b>", body_style)],
        [Paragraph("<code>test_csv_exporter.py</code>", body_style), Paragraph("Dictionary-to-CSV serialization, header formatting, ReportService CSV export pipelines.", body_style), Paragraph("<b>PASSED (3/3)</b>", body_style)],
    ]
    tm_table = Table(test_modules, colWidths=[140, 264, 100])
    tm_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(tm_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("20. Git & GitHub Portfolio Setup", h1_style))
    story.append(Paragraph(
        "The repository includes a professional `.gitignore` (ignoring SQLite binaries, Python pycache, and virtual environments), "
        "an MIT `LICENSE`, structured requirements, and a detailed README with architectural diagrams and CLI walkthroughs.",
        body_style,
    ))

    story.append(Paragraph("21. Limitations & 22. Future Improvements", h1_style))
    lim_data = [
        [Paragraph("<b>Current Implementation Limitation</b>", body_style), Paragraph("<b>Architectural Future Enhancement</b>", body_style)],
        [Paragraph("<b>Terminal CLI Interface:</b> Restricted to command-line interactions.", body_style), Paragraph("Build a modern REST API using <b>FastAPI</b> or <b>Flask</b> with a Vue/React frontend.", body_style)],
        [Paragraph("<b>Single-host SQLite:</b> Not designed for distributed write clusters.", body_style), Paragraph("Transition <code>DatabaseManager</code> to support <b>PostgreSQL</b> via connection pooling.", body_style)],
        [Paragraph("<b>Manual Overdue Tracking:</b> Requires viewing the audit report.", body_style), Paragraph("Integrate background worker (Celery/APScheduler) for automated email due-date reminders.", body_style)],
        [Paragraph("<b>No Monetary Penalties:</b> Tracks overdue days but no fines.", body_style), Paragraph("Implement a configurable late fee calculation and payment ledger module.", body_style)],
    ]
    lim_table = Table(lim_data, colWidths=[240, 264])
    lim_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(lim_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: INTERVIEW PREPARATION (30s, 1min, 2min PITCHES)
    # =========================================================================
    story.append(Paragraph("Interview Master Guide: Project Elevator Pitches", h1_style))
    story.append(Paragraph(
        "Use these three tailored explanations during technical phone screens, hiring manager interviews, and onsite architecture reviews:",
        body_style,
    ))

    story.append(Paragraph("⏱️ 30-Second Elevator Pitch", h2_style))
    p30 = (
        "\"BookVault is a production-grade Python and SQLite Library Management System that manages catalog inventory, "
        "member accounts, and book checkouts. It enforces relational integrity through SQLite foreign keys and check constraints, "
        "uses atomic context-managed transactions to guarantee inventory consistency, and features a clean layered architecture "
        "with a 28-test automated pytest suite.\""
    )
    story.append(make_callout(p30, bg_color=LIGHT_BG, border_color=PRIMARY))
    story.append(Spacer(1, 8))

    story.append(Paragraph("⏱️ 1-Minute Technical Pitch", h2_style))
    p60 = (
        "\"I built BookVault to demonstrate clean Python architecture and relational database principles without relying on heavy third-party frameworks. "
        "The system solves common library challenges like phantom inventory, double-borrowing, and overdue tracking. "
        "Architecturally, it follows a 4-tier design: a Presentation CLI, a Service/Validation layer, an OOP Domain Model layer, "
        "and a Database Access layer. When a patron borrows a book, the Service Layer validates patron quotas, active status, and stock availability "
        "before executing an atomic SQLite transaction that writes the loan record and decrements stock. The codebase includes multi-vector search, "
        "CSV export pipelines, administrative KPI dashboards, and 100% passing pytest coverage with in-memory database isolation.\""
    )
    story.append(make_callout(p60, bg_color=LIGHT_BG, border_color=SECONDARY))
    story.append(Spacer(1, 8))

    story.append(Paragraph("⏱️ 2-Minute In-Depth Engineering Overview", h2_style))
    p120 = (
        "\"BookVault is an enterprise-modeled library management system designed to showcase robust backend development in Python and SQL. "
        "The core engineering focus was on <b>data integrity</b> and <b>separation of concerns</b>.<br/><br/>"
        "1. <b>Database & Concurrency:</b> Using SQLite with <code>PRAGMA foreign_keys = ON;</code>, tables (books, members, loans) are bound by strict relational constraints. "
        "All state mutations occur inside a custom <code>with db.transaction():</code> context manager. If any query fails, the entire transaction rolls back automatically.<br/>"
        "2. <b>OOP & Domain Models:</b> Entities like <code>Book</code> and <code>Loan</code> encapsulate business logic. For example, <code>Book.borrowed_copies</code> and <code>Loan.overdue_days</code> "
        "are computed dynamically via properties rather than storing stale denormalized columns.<br/>"
        "3. <b>Business Rules Engine:</b> The <code>LibraryService</code> strictly enforces invariants: patrons cannot borrow more than their allotted quota, deactivated members cannot checkout books, "
        "and active loans cannot be duplicated.<br/>"
        "4. <b>Quality Assurance:</b> Tested extensively using <code>pytest</code> across 28 unit and integration tests using ephemeral in-memory databases (<code>:memory:</code>). "
        "The project also provides automated CSV export pipelines and a real-time KPI dashboard.\""
    )
    story.append(make_callout(p120, bg_color=LIGHT_BG, border_color=ACCENT_GREEN))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 11 & 12: 20+ INTERVIEW QUESTIONS, ANSWERS & FOLLOW-UPS
    # =========================================================================
    story.append(Paragraph("20+ Technical Interview Questions & Answers", h1_style))
    story.append(Paragraph(
        "Comprehensive questions and crisp answers tailored for junior to mid-level backend engineering interviews:",
        body_style,
    ))

    qa_list = [
        ("Q1: Why did you choose SQLite over MySQL or PostgreSQL for this project?",
         "SQLite is serverless, zero-configuration, and native to Python's standard library (`sqlite3`). For a standalone desktop or local application, it eliminates connection latency and daemon setup while providing full ACID guarantees.",
         "Follow-up: How would you migrate to PostgreSQL? -> Abstract queries behind an ORM or update `DatabaseManager` with connection pooling (`psycopg2`/`SQLAlchemy`)."),

        ("Q2: How do you prevent race conditions during book borrowing?",
         "Borrowing executes inside an atomic transaction (`with db.transaction():`). The update query checks availability directly in SQL: `UPDATE books SET available_copies = available_copies - 1 WHERE id = ? AND available_copies > 0`, ensuring inventory cannot drop below zero.",
         "Follow-up: What if multiple threads access the database? -> SQLite handles locking in WAL mode; in high-concurrency systems, row-level locks (e.g. `SELECT FOR UPDATE` in Postgres) are used."),

        ("Q3: Why enable `PRAGMA foreign_keys = ON;` in SQLite?",
         "By default, SQLite disables foreign key enforcement for backward compatibility. Enabling the pragma ensures that orphaned records (e.g. loans referencing non-existent members) are strictly rejected.",
         "Follow-up: What happens when trying to delete a book with active loans? -> SQLite throws an integrity violation because `ON DELETE RESTRICT` is configured."),

        ("Q4: Explain the difference between `fetchone()` and `fetchall()`.",
         "`fetchone()` fetches the next single row from the cursor result set (or `None`), saving memory when querying single records by primary key. `fetchall()` loads all matching rows into a Python list at once.",
         "Follow-up: When should you avoid `fetchall()`? -> On massive tables with millions of rows; instead, use generators or pagination (`LIMIT/OFFSET`)."),

        ("Q5: How do you handle database rollbacks in Python?",
         "Using a context manager with `try/except/finally`. If an exception occurs inside the `with` block, `conn.rollback()` is called before re-raising the exception; otherwise, `conn.commit()` executes.",
         "Follow-up: How is this implemented in BookVault? -> In `DatabaseManager.transaction()` using `@contextmanager` from `contextlib`."),

        ("Q6: How do you validate ISBNs in BookVault?",
         "`InputValidator.validate_isbn()` strips hyphens and spaces, verifies length (10 or 13 digits), and uses regex `^[0-9]{9}[0-9X]$|^[0-9]{13}$` to ensure valid character sets.",
         "Follow-up: How do you handle duplicate ISBNs? -> The `isbn` column has a `UNIQUE` constraint in SQLite, and `LibraryService` checks before insertion to raise a clean `ValidationError`."),

        ("Q7: What is the benefit of `sqlite3.Row` as a row_factory?",
         "`sqlite3.Row` allows accessing query columns both by name (dictionary-like: `row['title']`) and by index (`row[0]`), while maintaining high memory efficiency.",
         "Follow-up: How does this help domain models? -> `Book.from_row(row)` maps columns cleanly without fragile index-based unpacking."),

        ("Q8: How does overdue detection work?",
         "The `sync_overdue_statuses()` method queries all active loans where `return_date IS NULL` and `due_date < current_date`, updating their database status to `'OVERDUE'`. The `Loan` model also calculates `overdue_days` in real time.",
         "Follow-up: What is the default loan duration? -> 14 days, calculated via `datetime.timedelta(days=14)` in `date_helper.py`."),

        ("Q9: How do you ensure test isolation in pytest?",
         "Pytest fixtures in `conftest.py` initialize a fresh in-memory database (`:memory:`) for every test function, ensuring zero cross-test side effects or leftover disk files.",
         "Follow-up: How many tests exist in the suite? -> 28 tests covering models, validation, database constraints, service workflows, and CSV exports."),

        ("Q10: Why use the Service Layer pattern instead of putting SQL in CLI handlers?",
         "Separating presentation from business logic adheres to SRP. It enables reusing the exact same `LibraryService` methods across a CLI, a future web API, or automated test scripts without code duplication.",
         "Follow-up: What does `LibraryService` depend on? -> It only depends on `DatabaseManager` and domain models."),
    ]

    for q, a, fu in qa_list:
        q_box = [
            [Paragraph(f"<b>{q}</b>", ParagraphStyle("QStyle", parent=body_style, fontName="Helvetica-Bold", textColor=PRIMARY))],
            [Paragraph(f"<b>Answer:</b> {a}", body_style)],
            [Paragraph(f"<i>💡 {fu}</i>", ParagraphStyle("FUStyle", parent=body_style, fontSize=8.5, textColor=SECONDARY))],
        ]
        q_t = Table(q_box, colWidths=[504])
        q_t.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(q_t)
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 13: 10 MORE INTERVIEW QUESTIONS (TOTAL 20+)
    # =========================================================================
    story.append(Paragraph("Technical Interview Questions (Continued)", h1_style))

    qa_list_2 = [
        ("Q11: How do you prevent patrons from borrowing more than their quota?",
         "`LibraryService.borrow_book()` counts active loans (`status IN ('ACTIVE', 'OVERDUE')`) for the member. If `count >= member.max_books_allowed`, it raises `MemberLimitExceededError`.",
         "Follow-up: Can member limits be customized? -> Yes, each member has a `max_books_allowed` column (default: 5, range: 1–20)."),

        ("Q12: How do you prevent double-borrowing of the same book title by one patron?",
         "Before checkout, a query verifies no active loan exists for the combination of `member_id` and `book_id`. If found, `ActiveLoanExistsError` is raised.",
         "Follow-up: Can a member borrow the same book after returning it? -> Yes, past returned loans (`status = 'RETURNED'`) do not block new checkouts."),

        ("Q13: Why did you create custom exception classes rather than using built-in ones?",
         "Custom exceptions like `BookUnavailableError` and `MemberLimitExceededError` communicate specific domain failures clearly to the presentation layer without conflating system errors (like `KeyError` or `ValueError`).",
         "Follow-up: What is the base class for all domain errors? -> `BookVaultError(Exception)`."),

        ("Q14: Explain the difference between dynamic properties and stored database columns in BookVault.",
         "`available_copies` and `status` are stored in SQLite. However, derived properties like `is_available` (`available > 0`), `borrowed_copies` (`total - available`), and `overdue_days` are computed dynamically via `@property` to prevent data anomalies.",
         "Follow-up: Why not store `overdue_days` in the database? -> Stored days become inaccurate as time passes; calculating dynamically against `date.today()` is always accurate."),

        ("Q15: How does BookVault handle CSV export formatting?",
         "`CSVExporter.export_dicts_to_csv()` utilizes Python's built-in `csv.DictWriter` with UTF-8 encoding, writing headers and rows atomically to timestamped files in `data/exports/`.",
         "Follow-up: What happens if the data list is empty? -> It creates the CSV file with headers only, avoiding crashes."),

        ("Q16: How does the application prevent SQL Injection?",
         "By strictly using parameterized queries (`cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))`) instead of string formatting or f-strings.",
         "Follow-up: Does `LIKE` searching use parameterization? -> Yes: `WHERE title LIKE ?` with parameters `('%' + term + '%',)`."),

        ("Q17: What database indexes were created and why?",
        "`idx_books_isbn`, `idx_books_title`, `idx_books_author`, `idx_books_category`, `idx_members_email`, `idx_loans_book_id`, `idx_loans_member_id`, and `idx_loans_status` to optimize search and JOIN query performance.",
         "Follow-up: Why index foreign keys? -> SQLite does not automatically index foreign keys; indexing `loans(book_id)` speeds up JOINs and deletion checks significantly."),

        ("Q18: What is the purpose of `seed_sample_data()` in DatabaseManager?",
         "It populates realistic books (e.g. *Clean Code*, *Fluent Python*), registered members, active loans, and overdue loans if the database is empty, allowing instant demonstration.",
         "Follow-up: Does seeding overwrite existing user data? -> No, it first checks `SELECT COUNT(*) FROM books` and aborts if data exists."),

        ("Q19: How is the CLI user interface structured?",
         "`CLI` in `app/cli/menu.py` uses modular sub-menus (Book, Member, Loan, Reports, CSV, Database Admin) with a clean ASCII table formatter that dynamically computes column widths.",
         "Follow-up: How are user input errors handled in the CLI? -> Caught by `try...except BookVaultError` blocks, displaying user-friendly `[ERROR]` messages without exiting the app."),

        ("Q20: What are the main design patterns used in BookVault?",
         "1. **Service Layer Pattern** (`LibraryService`), 2. **Repository/Data Access Pattern** (`DatabaseManager`), 3. **Unit of Work / Transaction Context Manager**, 4. **Domain Model Pattern** (`Book`, `Member`, `Loan`).",
         "Follow-up: Why is this architecture beneficial for resumes? -> It demonstrates enterprise-grade separation of concerns rather than naive monolithic scripting."),
    ]

    for q, a, fu in qa_list_2:
        q_box = [
            [Paragraph(f"<b>{q}</b>", ParagraphStyle("QStyle", parent=body_style, fontName="Helvetica-Bold", textColor=PRIMARY))],
            [Paragraph(f"<b>Answer:</b> {a}", body_style)],
            [Paragraph(f"<i>💡 {fu}</i>", ParagraphStyle("FUStyle", parent=body_style, fontSize=8.5, textColor=SECONDARY))],
        ]
        q_t = Table(q_box, colWidths=[504])
        q_t.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        story.append(q_t)
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 14: EMERGENCY ONE-PAGE REVISION SHEET
    # =========================================================================
    story.append(Paragraph("⚡ Emergency One-Page Revision Sheet", h1_style))
    story.append(Paragraph(
        "<b>Review this page 5 minutes before your technical interview for instant mental clarity:</b>",
        body_style,
    ))

    cheat_sheet_data = [
        [Paragraph("<b>Topic</b>", body_style), Paragraph("<b>Key Talking Points & Exact Code Details</b>", body_style)],
        [
            Paragraph("<b>Core Concept</b>", body_style),
            Paragraph("BookVault is an OOP-driven Library Management System in pure Python 3 and SQLite simulating cataloging, membership, checkouts, returns, availability, overdue detection, and CSV reporting.", body_style)
        ],
        [
            Paragraph("<b>Architecture</b>", body_style),
            Paragraph("<b>Layered:</b> CLI (Presentation) ──► Service (Validation/Business Rules) ──► Models (OOP) ──► DatabaseManager (SQLite Transactions).", body_style)
        ],
        [
            Paragraph("<b>Database Schema</b>", body_style),
            Paragraph("• <code>books</code>: id (PK), title, author, isbn (UNIQUE), category, total_copies, available_copies.<br/>"
                      "• <code>members</code>: id (PK), name, email (UNIQUE), phone, max_books_allowed, is_active.<br/>"
                      "• <code>loans</code>: id (PK), book_id (FK), member_id (FK), borrow_date, due_date, return_date, status.<br/>"
                      "• <b>Pragma:</b> <code>PRAGMA foreign_keys = ON;</code>", body_style)
        ],
        [
            Paragraph("<b>Borrow Workflow</b>", body_style),
            Paragraph("1. Validate member is active & under borrowing limit.<br/>"
                      "2. Validate book has available copies > 0.<br/>"
                      "3. Prevent double borrowing of same book.<br/>"
                      "4. Atomic Transaction: Insert into <code>loans</code> + Decrement <code>books.available_copies</code>.", body_style)
        ],
        [
            Paragraph("<b>Return Workflow</b>", body_style),
            Paragraph("1. Locate active loan.<br/>"
                      "2. Atomic Transaction: Set <code>return_date = today</code>, <code>status = 'RETURNED'</code> + Increment <code>books.available_copies</code>.<br/>"
                      "3. Calculate overdue days if returned past due date.", body_style)
        ],
        [
            Paragraph("<b>Python Concepts</b>", body_style),
            Paragraph("• <b>Context Managers:</b> <code>@contextmanager</code> for transaction commit/rollback.<br/>"
                      "• <b>Properties:</b> <code>@property</code> for dynamic calculations (<code>is_available</code>, <code>overdue_days</code>).<br/>"
                      "• <b>Class Methods:</b> <code>@classmethod</code> for <code>from_row()</code> mapping.<br/>"
                      "• <b>Exceptions:</b> Custom hierarchy inherited from <code>BookVaultError</code>.<br/>"
                      "• <b>Regex:</b> Validating emails, phone numbers, and ISBN formats.", body_style)
        ],
        [
            Paragraph("<b>Testing</b>", body_style),
            Paragraph("<b>28 tests in pytest</b> covering CRUD, validation, constraint enforcement, transactions, borrowing limits, returns, reports, and CSV exports using in-memory SQLite (<code>:memory:</code>).", body_style)
        ],
        [
            Paragraph("<b>Key Metrics</b>", body_style),
            Paragraph("Total titles, physical copies, borrowed copies, active loans, overdue loans, top borrowed books leaderboard, and category distribution.", body_style)
        ],
    ]
    cs_table = Table(cheat_sheet_data, colWidths=[110, 394])
    cs_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(cs_table)
    story.append(Spacer(1, 12))

    story.append(make_callout(
        "<b>Confidence Anchor:</b> Remind your interviewer that BookVault was designed with a production mindset: "
        "every edge case (negative stock, duplicate checkouts, SQL injection, orphaned foreign keys) is accounted for."
    ))

    # Build PDF using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF generated successfully: {output_filename}")


if __name__ == "__main__":
    output_pdf = "BookVault_Project_Understanding_and_Interview_Guide.pdf"
    if len(sys.argv) > 1:
        output_pdf = sys.argv[1]
    create_guide_pdf(output_pdf)
