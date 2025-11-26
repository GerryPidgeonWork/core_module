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
from gui.G01c_widget_primitives import UIPrimitives, make_label, make_card_label
from gui.G01d_layout_primitives import heading, subheading, body_text, divider, spacer
from gui.G01e_gui_base import BaseGUI

# ====================================================================================================
# TEMP FUNCTION, TO BE REPLACED
# ====================================================================================================
def make_card(parent, min_height: int = 260) -> ttk.Frame:
    card = ttk.Frame(parent, style="SectionBody.TFrame", padding=(14, 10))
    card.pack_propagate(False)         # Enforce fixed height
    card.configure(height=min_height)
    return card


# ====================================================================================================
# USER INPUTS
# ====================================================================================================
PAGE_HEADING = "Connection Launcher (SP1)"
PAGE_SUBHEADING = "Configure connection and execution settings for your data pipelines."

# ====================================================================================================
# MAIN TEST WINDOW
# ====================================================================================================
class GUIDesign(BaseGUI):

    def build_widgets(self):
        # --------------------------------------------------------------------------------------------
        # 1. WINDOW HEADING
        # --------------------------------------------------------------------------------------------
        heading(self.main_frame, PAGE_HEADING, surface="Primary").pack(anchor="c", pady=(0, 4))
        body_text(self.main_frame, PAGE_SUBHEADING, surface="Primary").pack(anchor="c", pady=(0, 12))

        # --------------------------------------------------------------------------------------------
        # 2. TOP SECTION
        # --------------------------------------------------------------------------------------------
        # This builds the frame for the section
        top_row = ttk.Frame(self.main_frame, padding=4)
        top_row.pack(fill="x", pady=(0, 16))

        # This builds columns in Top Row. weight should add up to 10
        top_row.columnconfigure(0, weight=3)
        top_row.columnconfigure(1, weight=7)

        # --------------------------------------------------------------------------------------------
        # 2.1. FIRST COMPONENT
        # --------------------------------------------------------------------------------------------
        overview_card = make_card(top_row, min_height=200)
        overview_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # TODO: Check how to make the a Frame Label, so that it appears outside of frame
        make_label(overview_card, "Overview", category="SectionHeading", surface="Secondary", weight="Bold").pack(anchor="w")
        body_text(overview_card,
                  "Review and confirm your high-level settings before running any jobs.\n"
                  "Use the configuration cards below to adjust periods, credentials, and provider selection.\n"
                  "The console on the right shows recent execution logs and connection tests.",
            surface="Secondary", wraplength=350).pack(anchor="w", pady=(4, 4))
        
        # --------------------------------------------------------------------------------------------
        # 2.2. SECOND COMPONENT
        # --------------------------------------------------------------------------------------------
        console_card = make_card(top_row, min_height=200) # TODO: Should this be a different widget?
        console_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0)) # Why is this on (8,0) and the one in FIRST COMPONENT (0,8)

        make_label(console_card, "Console", category="SectionHeading", surface="Secondary", weight="Bold").pack(anchor="w")

        # --------------------------------------------------------------------------------------------
        # 3. MIDDLE SECTION
        # --------------------------------------------------------------------------------------------
        mid_row = ttk.Frame(self.main_frame, padding=4)
        mid_row.pack(fill="x", pady=(0, 20))

        for col in range(4):
            mid_row.columnconfigure(col, weight=1)

        # --------------------------------------------------------------------------------------------
        # 3.1. FIRST COMPONENT
        # --------------------------------------------------------------------------------------------
        gdrive = make_card(mid_row)
        gdrive.grid(row=0, column=0, sticky="nsew", padx=6)

        make_label(gdrive, "Google Drive Mapping", category="SectionHeading", surface="Secondary", weight='Bold').pack(anchor="w")

        # --------------------------------------------------------------------------------------------
        # 3.2. SECOND COMPONENT
        # --------------------------------------------------------------------------------------------
        snowflake = make_card(mid_row)
        snowflake.grid(row=0, column=1, sticky="nsew", padx=6)

        make_label(snowflake, "Snowflake Connector", category="SectionHeading", surface="Secondary", weight='Bold').pack(anchor="w")

        # --------------------------------------------------------------------------------------------
        # 3.3. THIRD COMPONENT
        # --------------------------------------------------------------------------------------------
        accounting = make_card(mid_row)
        accounting.grid(row=0, column=2, sticky="nsew", padx=6)

        make_label(accounting, "Accounting Period", category="SectionHeading", surface="Secondary", weight='Bold').pack(anchor="w")

        # --------------------------------------------------------------------------------------------
        # 3.4. FOURTH COMPONENT
        # --------------------------------------------------------------------------------------------
        dwh = make_card(mid_row)
        dwh.grid(row=0, column=3, sticky="nsew", padx=6)

        make_label(dwh, "DWH Period", category="SectionHeading", surface="Secondary", weight='Bold').pack(anchor="w")





# ====================================================================================================
# MAIN GUARD
# ====================================================================================================
if __name__ == "__main__":
    init_logging()
    app = GUIDesign(title=PAGE_HEADING)
    app.open_fullscreen()
    app.mainloop()