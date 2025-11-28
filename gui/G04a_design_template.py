# ====================================================================================================
# G04a_design_template.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   High-level DESIGN TEMPLATE and LEARNING AID for the GUI Framework.
#
#   This module demonstrates:
#       • How to correctly structure a GUI “page” using the BaseGUI window shell.
#       • How to use the G01-layer primitives (widget & layout factories).
#       • How to use the G02-layer container patterns (cards, sections, grids).
#       • How to assemble multi-row, multi-column layouts in a clean, repeatable way.
#       • How page-level classes should be structured (e.g., GUIDesign(BaseGUI)).
#
#   This file is NOT a production view. It is:
#       • A teaching file.
#       • A reference for future page authors.
#       • A safe sandbox to experiment with container patterns.
#       • A starting point for real GUI view modules.
#
#   You can use this template to:
#       ✓ Build new GUI layouts quickly.
#       ✓ Understand the responsibilities of each GUI layer (G00/G01/G02/G03).
#       ✓ Swap out layout rows / columns without rewriting boilerplate.
#       ✓ Explore the visual design tokens and style engine in practice.
#
# Architectural Notes:
#   • G04x is intentionally not part of the “core” GUI framework.
#     It is a *design layer* that helps developers learn the system.
#
#   • No business logic should ever be added to this file.
#     It is a pure layout/template module.
#
#   • The structure mirrors real production pages:
#         class GUIDesign(BaseGUI):
#             def build_widgets(self):
#                 ...
#
#   • The template is free to reference any of the GUI framework layers:
#         G00  – GUI import hub (tk, ttk, tkFont)
#         G01  – widget & layout primitives
#         G02  – container patterns & layout helpers
#         G03  – navigation, page controller, app state (if needed)
#
#   • The template intentionally includes /rTODO markers for:
#         - top-level row configuration
#         - dynamic column weighting
#         - heading/subheading styles
#         - user-selectable fullscreen behaviour
#
# How to Use This Template:
#   1. Copy this file into a new module (e.g., G10a_my_feature_page.py).
#   2. Replace headings / labels with your content.
#   3. Use G02 container patterns to build the layout skeleton.
#   4. Fill card bodies with G01 primitives (labels, buttons, inputs, radios, etc.)
#   5. If needed, integrate G03 NavigationController and AppState.
#
# This is the recommended starting point for ANY new page in the GUI Framework.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-26
# Project:      Core Boilerplate v1.0 — GUI Framework
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
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
from gui.G00a_gui_packages import tk, ttk, tkFont
from gui.G01b_style_engine import configure_ttk_styles # TODO: What is this? What does it actually import?
from gui.G01c_widget_primitives import (
    UIPrimitives, # TODO: What is this? What does it actually import?
    make_button, 
    make_card_label, 
    make_checkbox, 
    make_combobox, 
    make_divider, 
    make_entry, 
    make_frame, 
    make_heading,
    make_label,
    make_radio,
    make_section_heading,
    make_spacer,
    make_status_label,
    make_subheading,
    make_switch,
    make_textarea) 
from gui.G01d_layout_primitives import heading, subheading
from gui.G01e_gui_base import BaseGUI # TODO: What is this? What does it actually import?


# ====================================================================================================
# 3. CONSTANTS
# ----------------------------------------------------------------------------------------------------
OPEN_FULLSCREEN = True # TODO: Link this so that user can choose.
PAGE_HEADING = "Connection Launcher — Sandbox"
PAGE_SUBHEADING = "Developer-only layout sandbox for the Connection Launcher window."
# TOP_ROW = {0, 30; 1, 70} # TODO: Can we use something like this to help build the number of columns in a row
# SECOND_ROW = 
# THIRD_ROW = 
# LAST_ROW = 

# ====================================================================================================
# 4. GUI PAGE CLASS
# ----------------------------------------------------------------------------------------------------
class GUIDesign(BaseGUI):
    """
    Developer-facing template page used to learn and validate the GUI framework.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        logger.info("Launching GUIDesign layout sandbox.")
        super().__init__(*args, **kwargs)

        # Attach UI primitive factory to this page
        self.ui = UIPrimitives(self.main_frame)

        # Build the widget tree
        # self.build_widgets()

    # ------------------------------------------------------------------------------------------------
    def apply_window_settings(self) -> None:
        """
        Apply top-level window behaviour (fullscreen, sizing, etc.)
        based on module-level constants such as OPEN_FULLSCREEN.
        """
        if OPEN_FULLSCREEN:
            self.open_fullscreen()

    # Debug: what fonts does the style engine give us?
    style = ttk.Style()
    print("[DEBUG] Available Label Styles:")
    for s in style.layout("TLabel"), style.lookup("TLabel", "font"):
        print("   ", s)

    print("[DEBUG] WindowHeading.Primary.Bold.TLabel →",
        style.lookup("WindowHeading.Primary.Bold.TLabel", "font"))   
    
    # ------------------------------------------------------------------------------------------------
    def build_widgets(self) -> None:
        """
        Build all widgets for this page.
        This function is intentionally small and readable so developers
        learning the system can clearly see the structure of a page.
        """
        logger.info("[G04a] Building widget tree.")

        print(ttk.Style().lookup("Primary.TLabel", "font"))

        # --------------------------------------------------------------------------------------------
        # 4.1 WINDOW HEADING
        # --------------------------------------------------------------------------------------------
        heading(self.main_frame, PAGE_HEADING, surface="Secondary", weight="Normal").pack(anchor="n", pady=(0, 4))
        subheading(self.main_frame, PAGE_SUBHEADING, surface="Primary", weight="Normal").pack(anchor="n", pady=(0, 12))

        # --------------------------------------------------------------------------------------------
        # 4.2 TOP ROW
        # --------------------------------------------------------------------------------------------
        logger.info("[G04a] Building top row.")
        # TODO: Build top-row grid using G02 patterns

        # --------------------------------------------------------------------------------------------
        # 4.3 SECOND ROW
        # --------------------------------------------------------------------------------------------
        logger.info("[G04a] Building second row.")
        # TODO: Build second-row cards

        # --------------------------------------------------------------------------------------------
        # 4.4 THIRD ROW
        # --------------------------------------------------------------------------------------------
        logger.info("[G04a] Building third row.")
        # TODO: Build third-row cards

        # --------------------------------------------------------------------------------------------
        # 4.5 BOTTOM ROW
        # --------------------------------------------------------------------------------------------
        logger.info("[G04a] Building bottom row.")
        # TODO: Build bottom-row provider tiles
            

# ====================================================================================================
# 7. MAIN GUARD
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging()
    logger.info("=== SP2 Connection Launcher Sandbox — Start ===")

    app = GUIDesign(title=PAGE_HEADING)
    app.apply_window_settings()

    app.mainloop()

    logger.info("=== SP2 Connection Launcher Sandbox — End ===")
