# ====================================================================================================
# SP1.py — Connection Launcher (Prototype Layout Test)
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

from __future__ import annotations

# ----------------------------------------------------------------------------------------------------
# Import base framework
# ----------------------------------------------------------------------------------------------------
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from core.C00_set_packages import *
from core.C03_logging_handler import get_logger, init_logging
logger = get_logger(__name__)

# GUI packages
from gui.G00a_gui_packages import tk, ttk
from gui.G01a_style_config import *
from gui.G01b_style_engine import configure_ttk_styles
from gui.G01c_widget_primitives import UIPrimitives, make_label, make_radio
from gui.G01d_layout_primitives import heading, subheading, body_text, divider, spacer
from gui.G01e_gui_base import BaseGUI


# ====================================================================================================
# HELPER — Create a uniform card frame
# ====================================================================================================
def make_card(parent, min_height: int = 260) -> ttk.Frame:
    card = ttk.Frame(parent, style="SectionBody.TFrame", padding=(14, 10))
    card.pack_propagate(False)         # Enforce fixed height
    card.configure(height=min_height)
    return card


# ====================================================================================================
# MAIN TEST WINDOW
# ====================================================================================================
class SP1Window(BaseGUI):

    def build_widgets(self):
        # --------------------------------------------------------------------------------------------
        # 1. WINDOW HEADING
        # --------------------------------------------------------------------------------------------
        heading(self.main_frame, "Connection Launcher (SP1)", surface="Primary").pack(
            anchor="w", pady=(0, 4)
        )
        body_text(
            self.main_frame,
            "Configure connection and execution settings for your data pipelines.",
            surface="Primary",
        ).pack(anchor="w", pady=(0, 12))

        # --------------------------------------------------------------------------------------------
        # 2. TOP ROW — Overview (30%) + Console (70%)
        # --------------------------------------------------------------------------------------------
        top_row = ttk.Frame(self.main_frame, padding=4)
        top_row.pack(fill="x", pady=(0, 16))

        top_row.columnconfigure(0, weight=3)
        top_row.columnconfigure(1, weight=7)

        # --- LEFT: Overview -------------------------------------------------------------------------
        overview_card = make_card(top_row, min_height=160)
        overview_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        make_label(
            overview_card, "Overview",
            category="SectionHeading", surface="Secondary", weight="Bold"
        ).pack(anchor="w")

        body_text(
            overview_card,
            "Review and confirm your high-level settings before running any jobs.\n"
            "Use the configuration cards below to adjust periods, credentials, and provider selection.\n"
            "The console on the right shows recent execution logs and connection tests.",
            surface="Secondary",
            wraplength=350
        ).pack(anchor="w", pady=(4, 4))

        # --- RIGHT: Console -------------------------------------------------------------------------
        console_card = make_card(top_row, min_height=160)
        console_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        make_label(
            console_card, "Console Log",
            category="SectionHeading", surface="Secondary", weight="Bold"
        ).pack(anchor="w")

        console_box = tk.Text(
            console_card,
            height=6,
            wrap="word",
            font=(GUI_FONT_FAMILY[0], GUI_FONT_SIZE_DEFAULT),
            background=GUI_COLOUR_BG_SECONDARY,
            borderwidth=1,
            relief="solid",
        )
        console_box.pack(fill="both", expand=True, pady=(4, 0))
        console_box.insert("1.0", "(Console) Ready.\n")

        # --------------------------------------------------------------------------------------------
        # 3. MIDDLE ROW — 4 Cards × 25%
        # --------------------------------------------------------------------------------------------
        mid_row = ttk.Frame(self.main_frame, padding=4)
        mid_row.pack(fill="x", pady=(0, 20))

        for col in range(4):
            mid_row.columnconfigure(col, weight=1)

        # ============================================================================================
        # 3A. GOOGLE DRIVE CARD
        # ============================================================================================
        gdrive = make_card(mid_row)
        gdrive.grid(row=0, column=0, sticky="nsew", padx=6)

        make_label(gdrive, "Google Drive / Local", category="SectionHeading",
                   surface="Secondary", weight="Bold").pack(anchor="w")

        spacer(gdrive, height=6).pack()

        # make_radio(gdrive, "Use Google Drive API").pack(anchor="w")
        # make_radio(gdrive, "Use Local Mapped Drive").pack(anchor="w")

        spacer(gdrive, height=6).pack()

        # make_button(gdrive, "Browse Local Folder", width=22).pack(anchor="w")

        body_text(gdrive, "Local path: (not selected)", surface="Secondary").pack(anchor="w", pady=(6, 0))
        body_text(gdrive, "Status: Not mapped", surface="Secondary", weight="Bold").pack(anchor="w")

        # ============================================================================================
        # 3B. SNOWFLAKE LOGIN CARD
        # ============================================================================================
        snow = make_card(mid_row)
        snow.grid(row=0, column=1, sticky="nsew", padx=6)

        make_label(snow, "Snowflake Login", category="SectionHeading",
                   surface="Secondary", weight="Bold").pack(anchor="w")

        spacer(snow, height=6).pack()

        rb1 = make_radio(snow, "Use default connection profile")
        rb1.pack(anchor="w")

        rb2 = make_radio(snow, "Use secondary connection profile")
        rb2.pack(anchor="w")

        rb3 = make_radio(snow, "Use custom login email")
        rb3.pack(anchor="w")

        entry_custom = make_entry(snow, width=28)
        entry_custom.pack(anchor="w", pady=(4, 6))

        make_button(snow, "Connect to Snowflake").pack(anchor="w", pady=(6, 4))

        body_text(snow, "Status: Not connected", surface="Secondary", weight="Bold").pack(anchor="w")

        # ============================================================================================
        # 3C. ACCOUNTING PERIOD — Summary block + Options block
        # ============================================================================================
        acct = make_card(mid_row)
        acct.grid(row=0, column=2, sticky="nsew", padx=6)

        # Heading
        make_label(acct, "Accounting Period", category="SectionHeading",
                   surface="Secondary", weight="Bold").pack(anchor="w")

        spacer(acct, height=4).pack()

        # Summary Block
        summary_acct = ttk.Frame(acct, padding=(0, 2))
        summary_acct.pack(fill="x", pady=(0, 6))

        body_text(summary_acct,
                  "Current accounting period: November 2025",
                  surface="Secondary", weight="Bold").pack(anchor="w")

        body_text(summary_acct,
                  "Use the default period or override with a specific YYYY-MM.",
                  surface="Secondary", wraplength=280).pack(anchor="w", pady=(4, 0))

        divider(acct).pack(fill="x", pady=6)

        # Options Block
        opt_acct = ttk.Frame(acct)
        opt_acct.pack(fill="x")

        rb_def = make_radio(opt_acct, "Use default accounting period")
        rb_def.pack(anchor="w")

        rb_override = make_radio(opt_acct, "Override accounting period")
        rb_override.pack(anchor="w", pady=(2, 0))

        entry_acct = make_entry(opt_acct, width=18)
        entry_acct.pack(anchor="w", pady=(4, 0))

        # ============================================================================================
        # 3D. DATA WAREHOUSE PERIOD — Same layout style
        # ============================================================================================
        dwh = make_card(mid_row)
        dwh.grid(row=0, column=3, sticky="nsew", padx=6)

        make_label(dwh, "Data Warehouse Period", category="SectionHeading",
                   surface="Secondary", weight="Bold").pack(anchor="w")

        spacer(dwh, height=4).pack()

        summary_dwh = ttk.Frame(dwh, padding=(0, 2))
        summary_dwh.pack(fill="x", pady=(0, 6))

        body_text(summary_dwh,
                  "Current DWH period: November 2025",
                  surface="Secondary", weight="Bold").pack(anchor="w")

        body_text(summary_dwh,
                  "Use the default DWH period or override with a specific YYYY-MM.",
                  surface="Secondary", wraplength=280).pack(anchor="w", pady=(4, 0))

        divider(dwh).pack(fill="x", pady=6)

        opt_dwh = ttk.Frame(dwh)
        opt_dwh.pack(fill="x")

        make_radio(opt_dwh, "Use default DWH period").pack(anchor="w")
        make_radio(opt_dwh, "Override DWH period").pack(anchor="w", pady=(2, 0))

        make_entry(opt_dwh, width=18).pack(anchor="w", pady=(4, 0))

        # --------------------------------------------------------------------------------------------
        # 4. BOTTOM ROW — 4 Cards × 25% × 260px
        # --------------------------------------------------------------------------------------------
        bottom = ttk.Frame(self.main_frame, padding=4)
        bottom.pack(fill="x", pady=(0, 8))

        for col in range(4):
            bottom.columnconfigure(col, weight=1)

        # Provider cards
        providers = ["Braintree", "Uber Eats", "Deliveroo", "Just Eat"]

        for i, name in enumerate(providers):
            card = make_card(bottom)
            card.grid(row=0, column=i, sticky="nsew", padx=6)

            make_label(card, name, category="SectionHeading",
                       surface="Secondary", weight="Bold").pack(anchor="w")

            spacer(card, height=6).pack()

            body_text(
                card,
                "Provider configuration coming soon.",
                surface="Secondary"
            ).pack(anchor="w")


# ====================================================================================================
# MAIN GUARD
# ====================================================================================================
if __name__ == "__main__":
    init_logging()
    app = SP1Window(title="Connection Launcher (SP1)")
    app.open_fullscreen()
    app.mainloop()
