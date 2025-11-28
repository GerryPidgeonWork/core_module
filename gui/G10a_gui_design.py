# ====================================================================================================
# G10a_gui_design.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   High-fidelity prototype page to validate the new 3-row / 4-column layout system:
#
#       • Top Row    → 30% Overview  + 70% Console Log
#       • Middle Row → 4 × 25% configuration cards (Google Drive, Snowflake, Accounting Period, DWH)
#       • Bottom Row → 4 × 25% provider tiles (medium-tall: 180–220px)
#
#   This file is for layout testing only — SP1 scripts are temporary/non-production.
# ----------------------------------------------------------------------------------------------------
# Author: Gerry Pidgeon
# Created: 2025-11-26
# Project: GUIBoilerplatePython — Scratchpad
# ====================================================================================================

# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# These imports (sys, pathlib.Path) are required to correctly initialise the project environment,
# ensure the core library can be imported safely (including C00_set_packages.py),
# and prevent project-local paths from overriding installed site-packages.
# ----------------------------------------------------------------------------------------------------

# --- Future behaviour & type system enhancements -----------------------------------------------------
from __future__ import annotations           # Future-proof type hinting (PEP 563 / PEP 649)

# --- Required for dynamic path handling and safe importing of core modules ---------------------------
import sys                                   # Python interpreter access (path, environment, runtime)
from pathlib import Path                     # Modern, object-oriented filesystem path handling

# --- Ensure project root DOES NOT override site-packages --------------------------------------------
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# --- Remove '' (current working directory) which can shadow installed packages -----------------------
if "" in sys.path:
    sys.path.remove("")

# --- Prevent creation of __pycache__ folders ---------------------------------------------------------
sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Bring in shared external packages from the central import hub.
#
# CRITICAL ARCHITECTURE RULE:
#   ALL external + stdlib packages MUST be imported exclusively via:
#       from core.C00_set_packages import *
#   No other script may import external libraries directly.
#
# C01_set_file_paths is a pure core module and must not import GUI packages.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
from gui.G00a_gui_packages import tk, ttk
from gui.G01a_style_config import *
from gui.G01b_style_engine import configure_ttk_styles
from gui.G01c_widget_primitives import UIPrimitives, make_label, make_card_label, make_radio, make_button, make_status_label, make_entry
from gui.G01d_layout_primitives import heading, subheading, body_text, divider, spacer
from gui.G01e_gui_base import BaseGUI
from gui.G02b_container_patterns import create_page_header, create_weighted_row, create_card_row, make_radio_group

# ====================================================================================================
# 3. PAGE CONFIGURATION
# ====================================================================================================
PAGE_TITLE = "Connection Launcher"
PAGE_SUBTITLE = "Configure connection and execution settings for your data pipelines."


# ====================================================================================================
# 4. MAIN GUI CLASS
# ====================================================================================================
class GUIDesign(BaseGUI):
    """
    Main application page demonstrating the G01c + G02b composition pattern.
    """

    def build_widgets(self) -> None:
        """
        Build the page layout using G02b container patterns and G01c widget primitives.
        """
        # Store tk variables for radio groups
        self.drive_mode = tk.StringVar(value="api")
        self.snowflake_user = tk.StringVar(value="user1")
        self.accounting_mode = tk.StringVar(value="default")
        self.dwh_mode = tk.StringVar(value="default")

        # ----------------------------------------------------------------------------------------
        # PAGE HEADER
        # ----------------------------------------------------------------------------------------
        next_row = create_page_header(
            self.main_frame,
            row=0,
            title=PAGE_TITLE,
            subtitle=PAGE_SUBTITLE,
        )

        # ----------------------------------------------------------------------------------------
        # TOP ROW: Overview (30%) + Console (70%)
        # ----------------------------------------------------------------------------------------
        top_row = create_weighted_row(
            self.main_frame,
            row=next_row,
            weights=[30, 70],
            titles=["Overview", "Console"],
        )
        next_row += 1

        # Overview card content
        self._build_overview_card(top_row[0].body)

        # Console card content
        self._build_console_card(top_row[1].body)

        # ----------------------------------------------------------------------------------------
        # MIDDLE ROW: 4 × 25% Configuration Cards
        # ----------------------------------------------------------------------------------------
        middle_row = create_card_row(
            self.main_frame,
            row=next_row,
            columns=4,
            titles=["Google Drive", "Snowflake", "Accounting Period", "DWH Period"],
        )
        next_row += 1

        # Populate each card
        self._build_google_drive_card(middle_row[0].body)
        self._build_snowflake_card(middle_row[1].body)
        self._build_accounting_card(middle_row[2].body)
        self._build_dwh_card(middle_row[3].body)

        # ----------------------------------------------------------------------------------------
        # BOTTOM ROW: 4 × 25% Provider Tiles
        # ----------------------------------------------------------------------------------------
        bottom_row = create_card_row(
            self.main_frame,
            row=next_row,
            columns=4,
            titles=["Braintree", "Uber Eats", "Deliveroo", "Just Eat"],
        )
        next_row += 1

        # Populate provider tiles
        self._build_provider_tile(bottom_row[0].body, "Braintree")
        self._build_provider_tile(bottom_row[1].body, "Uber Eats")
        self._build_provider_tile(bottom_row[2].body, "Deliveroo")
        self._build_provider_tile(bottom_row[3].body, "Just Eat")

    # ============================================================================================
    # CARD BUILDERS
    # ============================================================================================

    def _build_overview_card(self, body: ttk.Frame) -> None:
        """Build the Overview card content."""
        make_label(
            body,
            "Review and confirm your high-level settings before running any jobs.\n\n"
            "Use the configuration cards below to adjust periods, credentials, "
            "and provider selection.\n\n"
            "The console on the right shows recent execution logs and connection tests.",
            category="Body",
            surface="Secondary",
            wraplength=350,
        ).pack(anchor="w", pady=(0, 8))

    def _build_console_card(self, body: ttk.Frame) -> None:
        """Build the Console card content."""
        make_label(
            body,
            "Console output will appear here...",
            category="Body",
            surface="Secondary",
        ).pack(anchor="w", pady=(0, 8))

    def _build_google_drive_card(self, body: ttk.Frame) -> None:
        """Build the Google Drive configuration card."""
        # Radio group
        radio_group = make_radio_group(
            body,
            options=[
                ("Use Google Drive API", "api"),
                ("Use Local Mapped Drive", "local"),
            ],
            variable=self.drive_mode,
        )
        radio_group.pack(anchor="w", pady=(0, 8))

        # Browse button
        make_button(body, text="Browse Local Folder").pack(anchor="w", pady=(0, 8))

        # Path display
        make_label(body, "Local Path: Not set", category="Body", surface="Secondary").pack(anchor="w", pady=(0, 4))

        # Status
        make_status_label(body, "Status: Not Mapped", status="error").pack(anchor="w", pady=(0, 4))

    def _build_snowflake_card(self, body: ttk.Frame) -> None:
        """Build the Snowflake configuration card."""
        # Radio group for user selection
        radio_group = make_radio_group(
            body,
            options=[
                ("User 1 (Primary)", "user1"),
                ("User 2 (Secondary)", "user2"),
                ("Custom Email", "custom"),
            ],
            variable=self.snowflake_user,
        )
        radio_group.pack(anchor="w", pady=(0, 8))

        # Custom email entry
        make_entry(body, width=25).pack(anchor="w", pady=(0, 8))

        # Connect button
        make_button(body, text="Connect to Snowflake").pack(anchor="w", pady=(0, 8))

        # Status
        make_status_label(body, "Status: Not Connected", status="error").pack(anchor="w", pady=(0, 4))

    def _build_accounting_card(self, body: ttk.Frame) -> None:
        """Build the Accounting Period configuration card."""
        # Current period display
        make_label(body, "Default: November 2025", category="Body", surface="Secondary").pack(anchor="w", pady=(0, 4))
        make_label(
            body,
            "The accounting period determines which financial data is processed.",
            category="Body",
            surface="Secondary",
            wraplength=200,
        ).pack(anchor="w", pady=(0, 8))

        # Radio group
        radio_group = make_radio_group(
            body,
            options=[
                ("Use Default Period", "default"),
                ("Override Period", "override"),
            ],
            variable=self.accounting_mode,
        )
        radio_group.pack(anchor="w", pady=(0, 8))

        # Override entry
        make_label(body, "Override (YYYY-MM):", category="Body", surface="Secondary").pack(anchor="w", pady=(0, 2))
        make_entry(body, width=15).pack(anchor="w", pady=(0, 4))

    def _build_dwh_card(self, body: ttk.Frame) -> None:
        """Build the DWH Period configuration card."""
        # Current period display
        make_label(body, "Default: November 2025", category="Body", surface="Secondary").pack(anchor="w", pady=(0, 4))
        make_label(
            body,
            "The DWH period controls data warehouse synchronisation scope.",
            category="Body",
            surface="Secondary",
            wraplength=200,
        ).pack(anchor="w", pady=(0, 8))

        # Radio group
        radio_group = make_radio_group(
            body,
            options=[
                ("Use Default DWH Period", "default"),
                ("Override DWH Period", "override"),
            ],
            variable=self.dwh_mode,
        )
        radio_group.pack(anchor="w", pady=(0, 8))

        # Override entry
        make_label(body, "Override (YYYY-MM):", category="Body", surface="Secondary").pack(anchor="w", pady=(0, 2))
        make_entry(body, width=15).pack(anchor="w", pady=(0, 4))

    def _build_provider_tile(self, body: ttk.Frame, provider_name: str) -> None:
        """Build a provider tile with placeholder content."""
        make_label(
            body,
            f"{provider_name} integration settings will appear here.",
            category="Body",
            surface="Secondary",
            wraplength=200,
        ).pack(anchor="w", pady=(0, 8))

        make_button(body, text=f"Configure {provider_name}").pack(anchor="w", pady=(0, 4))

        make_status_label(body, "Status: Not Configured", status="warning").pack(anchor="w", pady=(0, 4))


# ====================================================================================================
# 5. MAIN GUARD
# ====================================================================================================
if __name__ == "__main__":
    init_logging()
    logger.info("=== G10a_gui_design.py — Starting ===")

    app = GUIDesign(title=PAGE_TITLE)
    app.open_fullscreen()

    logger.info("=== G10a_gui_design.py — Entering mainloop ===")
    app.mainloop()
    logger.info("=== G10a_gui_design.py — End ===")
