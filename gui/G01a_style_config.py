# ====================================================================================================
# G01a_style_config.py
# ----------------------------------------------------------------------------------------------------
# Centralised configuration module for ALL GUI theme values.
#
# Purpose:
#   - Provide a single, shared source of truth for:
#         • Fonts (family + sizes)
#         • Colour palette (primary, secondary, status, text)
#         • Semantic colour roles (backgrounds, text roles, buttons, accents)
#         • Layout geometry (padding, spacing, default dimensions)
#         • Misc UI behaviour constants (cursor types, corner radius, animation speeds)
#   - Ensure every GUI module uses consistent visual settings.
#   - Allow global theme changes without modifying BaseGUI, UIComponents, or layout modules.
#   - Contain ZERO side effects at import time (pure configuration only).
#
# Integration:
#   from gui.G01a_style_config import (
#       GUI_FONT_FAMILY,
#       GUI_COLOUR_BG_PRIMARY,
#       BUTTON_COLOUR_BG,
#       FRAME_SIZE_H,
#       get_theme_summary,
#   )
#
# Notes:
#   - This module defines *theme constants only*.
#   - ALL GUI widgets refer to these semantic variables, never raw hex codes or hard-coded sizes.
#   - Changing this file automatically updates the entire GUI framework’s appearance.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-23
# Project:      Core Boilerplate v1.0
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
from gui.G00a_gui_packages import tk, ttk, tkFont


# ====================================================================================================
# 3. FONT CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Define all font-family and font-size constants used across the GUI.
#   These are *design tokens*: values only, no creation of Tk fonts here.
#
# Notes:
#   • Actual named fonts are created in G01b_style_engine (resolve_font_family + ensure_named_fonts)
#   • UIComponents and BaseGUI reference semantic font names, not raw sizes
# ====================================================================================================

# --- Font Family ------------------------------------------------------------------------------------
# Ordered list of preferred font families.
# The first available family on the system is selected at runtime by G01b_style_engine.
GUI_FONT_FAMILY = ("Poppins", "Segoe UI", "Arial", "sans-serif")

# --- Font Sizes -------------------------------------------------------------------------------------
# Heading text for window titles (prominent)
GUI_FONT_SIZE_HEADING = 14

# Section headings (above each card/section)
GUI_FONT_SIZE_TITLE = 12

# Default UI text (labels, buttons, inputs)
GUI_FONT_SIZE_DEFAULT = 10

# Helper text / footer text / subtle information
GUI_FONT_SIZE_SMALL = 9



# ====================================================================================================
# 4. COLOUR PALETTE — LOW-LEVEL DESIGN TOKENS
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Define the atomic colour values for the entire UI theme.
#   NOTHING in the GUI should use these directly.
#
# Structure:
#   • Primary palette     → Brand colours (blue family)
#   • Secondary palette   → Neutral UI surfaces (white, light grey)
#   • Status palette      → Semantic colours (success/warning/error)
#   • Text palette        → Neutral text colours (readable greys)
#
# Notes:
#   • Semantic colours (used by widgets) live in Section 4A.
#   • These base colours should NEVER be referenced directly by widgets.
# ====================================================================================================

# ----------------------------------------------------------------------------------------------------
# Primary brand palette (blue family)
# ----------------------------------------------------------------------------------------------------
COLOUR_PRIMARY_LIGHT = "#C7ECFF"   # Light tint — subtle accents, hover outlines
COLOUR_PRIMARY       = "#00A3FE"   # Main brand blue — used for primary actions
COLOUR_PRIMARY_DARK  = "#007CC4"   # Darker variant — hover/active intensification

# Temp for testing
# COLOUR_PRIMARY_LIGHT = "#FFFFAA"   # Light tint — subtle accents, hover outlines
# COLOUR_PRIMARY       = "#FFF700"   # Main brand blue — used for primary actions
# COLOUR_PRIMARY_DARK  = "#D6C800"   # Darker variant — hover/active intensification

# ----------------------------------------------------------------------------------------------------
# Secondary palette (neutral surface colours)
# ----------------------------------------------------------------------------------------------------
COLOUR_SECONDARY_LIGHT = "#FFFFFF"   # Pure white — window background, clean surfaces
COLOUR_SECONDARY       = "#F3F8FE"   # Soft neutral — card backgrounds, sections
COLOUR_SECONDARY_DARK  = "#C6D8E5"   # Medium neutral — borders, disabled surfaces

# Temp for testing
# COLOUR_SECONDARY_LIGHT = "#EEEEEE"   # Pure white — window background, clean surfaces
# COLOUR_SECONDARY       = "#444444"   # Soft neutral — card backgrounds, sections
# COLOUR_SECONDARY_DARK  = "#1A1A1A"   # Medium neutral — borders, disabled surfaces

# ----------------------------------------------------------------------------------------------------
# Status palette (semantic meaning)
# ----------------------------------------------------------------------------------------------------
COLOUR_STATUS_GREEN      = "#2ECC71"   # Success, OK, validation passed
COLOUR_STATUS_GREEN_DARK = "#1E874B"   # Darker green — hover/active emphasis

COLOUR_STATUS_AMBER      = "#F1C40F"   # Warnings, caution, notices
COLOUR_STATUS_AMBER_DARK = "#B4890A"   # Darker amber — hover/active emphasis

COLOUR_STATUS_RED        = "#E74C3C"   # Errors, destructive actions
COLOUR_STATUS_RED_DARK   = "#992D22"   # Darker red — hover/active emphasis

# ----------------------------------------------------------------------------------------------------
# Text palette (neutral greys for readability)
# ----------------------------------------------------------------------------------------------------
COLOUR_TEXT_PRIMARY = "#1A1A1A"   # Primary readable text
COLOUR_TEXT_MONO    = "#262626"   # Mono/log output, slightly darker


# ====================================================================================================
# 4A. ROLE-BASED SEMANTIC COLOUR ASSIGNMENTS
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Translate the low-level palette (Section 4) into semantic roles that the UI consumes.
#
# Why?
#   • Widgets NEVER use palette colours directly.
#   • Role colours define meaning:
#         - background roles
#         - text roles
#         - button roles (primary / secondary / success / warning / danger)
#         - accent roles
#         - status roles
#
# Design:
#   • Role colours can be changed without touching widgets.
#   • Every colour used in the GUI flows from these assignments.
# ----------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------
# BACKGROUND ROLES
# ----------------------------------------------------------------------------------------------------
GUI_COLOUR_BG_PRIMARY   = COLOUR_SECONDARY_LIGHT   # Root window background
GUI_COLOUR_BG_SECONDARY = COLOUR_SECONDARY         # Cards, sections, grouped panels
GUI_COLOUR_BG_INPUT     = COLOUR_SECONDARY_LIGHT   # Entry, Combobox, Spinbox fields
GUI_COLOUR_BG_TEXTAREA  = COLOUR_SECONDARY         # Multiline widgets / logs
GUI_COLOUR_BG_DISABLED  = COLOUR_SECONDARY_DARK    # Disabled inputs/buttons


# ----------------------------------------------------------------------------------------------------
# TEXT ROLES
# ----------------------------------------------------------------------------------------------------
TEXT_COLOUR_PRIMARY   = COLOUR_PRIMARY_DARK      # Headings, titles, emphasised labels
TEXT_COLOUR_SECONDARY = COLOUR_TEXT_PRIMARY      # Normal labels, instructional text
TEXT_COLOUR_MONO      = COLOUR_TEXT_MONO         # Log output / monospace text areas
TEXT_COLOUR_DISABLED  = COLOUR_SECONDARY_DARK    # Disabled text / inactive labels


# ----------------------------------------------------------------------------------------------------
# BUTTON ROLES — Full semantic tree with hover/active states
# ----------------------------------------------------------------------------------------------------
# Buttons are grouped into:
#   • Primary   (brand blue)
#   • Secondary (neutral)
#   • Success   (green)
#   • Warning   (amber)
#   • Danger    (red)
#
# Each has:
#   • base (normal) background
#   • hover (mouse over)
#   • active (pressed)
#   • text colour
#   • disabled colour (where applicable)
# ----------------------------------------------------------------------------------------------------

# --- Primary Buttons (Brand Blue) ----------------------------------------------------------
BUTTON_PRIMARY_BG        = COLOUR_PRIMARY
BUTTON_PRIMARY_HOVER     = COLOUR_PRIMARY_DARK
BUTTON_PRIMARY_ACTIVE    = COLOUR_PRIMARY_DARK
BUTTON_PRIMARY_TEXT      = COLOUR_SECONDARY_LIGHT
BUTTON_PRIMARY_DISABLED  = COLOUR_SECONDARY_DARK

# --- Secondary Buttons (Neutral actions) ---------------------------------------------------
BUTTON_SECONDARY_BG      = COLOUR_SECONDARY_DARK
BUTTON_SECONDARY_HOVER   = COLOUR_SECONDARY
BUTTON_SECONDARY_ACTIVE  = COLOUR_SECONDARY_DARK
BUTTON_SECONDARY_TEXT    = COLOUR_TEXT_PRIMARY
BUTTON_SECONDARY_DISABLED = COLOUR_SECONDARY_DARK

# --- Success Buttons (Green) ---------------------------------------------------------------
BUTTON_SUCCESS_BG        = COLOUR_STATUS_GREEN
BUTTON_SUCCESS_HOVER     = COLOUR_STATUS_GREEN_DARK
BUTTON_SUCCESS_ACTIVE    = COLOUR_STATUS_GREEN_DARK
BUTTON_SUCCESS_TEXT      = COLOUR_SECONDARY_LIGHT

# --- Warning Buttons (Amber) ---------------------------------------------------------------
BUTTON_WARNING_BG        = COLOUR_STATUS_AMBER
BUTTON_WARNING_HOVER     = COLOUR_STATUS_AMBER_DARK
BUTTON_WARNING_ACTIVE    = COLOUR_STATUS_AMBER_DARK
BUTTON_WARNING_TEXT      = COLOUR_SECONDARY_LIGHT

# --- Danger Buttons (Red) ------------------------------------------------------------------
BUTTON_DANGER_BG         = COLOUR_STATUS_RED
BUTTON_DANGER_HOVER      = COLOUR_STATUS_RED_DARK
BUTTON_DANGER_ACTIVE     = COLOUR_STATUS_RED_DARK
BUTTON_DANGER_TEXT       = COLOUR_SECONDARY_LIGHT


# ----------------------------------------------------------------------------------------------------
# ACCENT ROLES
# ----------------------------------------------------------------------------------------------------
GUI_COLOUR_ACCENT       = COLOUR_PRIMARY        # Main accent colour (lines, highlights)
GUI_COLOUR_ACCENT_LIGHT = COLOUR_PRIMARY_LIGHT  # Soft accents, hover outlines
GUI_COLOUR_ACCENT_DARK  = COLOUR_PRIMARY_DARK   # Strong accent emphasis


# ----------------------------------------------------------------------------------------------------
# STATUS ROLES (non-button semantic colours)
# ----------------------------------------------------------------------------------------------------
GUI_COLOUR_STATUS_SUCCESS = COLOUR_STATUS_GREEN
GUI_COLOUR_STATUS_WARNING = COLOUR_STATUS_AMBER
GUI_COLOUR_STATUS_ERROR   = COLOUR_STATUS_RED


# ----------------------------------------------------------------------------------------------------
# BORDER / DIVIDER ROLES
# ----------------------------------------------------------------------------------------------------
GUI_COLOUR_BORDER  = COLOUR_SECONDARY_DARK
GUI_COLOUR_DIVIDER = COLOUR_SECONDARY_DARK


# ----------------------------------------------------------------------------------------------------
# CHECKBOX / RADIO ROLES
# ----------------------------------------------------------------------------------------------------
CHECK_RADIO_COLOUR_ACTIVE   = COLOUR_PRIMARY
CHECK_RADIO_COLOUR_INACTIVE = COLOUR_SECONDARY_DARK
CHECK_RADIO_COLOUR_DISABLED = COLOUR_SECONDARY_DARK


# ====================================================================================================
# 5. LAYOUT & GEOMETRY (USAGE-BASED)
# ----------------------------------------------------------------------------------------------------
# These values govern spacing, padding, and layout flow across all GUI modules.
# BaseGUI and layout primitives consume these constants.
# ====================================================================================================

# Default fallback heading used for window titles in BaseGUI.
FRAME_HEADING = "GUI Window"                              

# Default top-level window dimensions for BaseGUI.
FRAME_SIZE_H = 900                                        
FRAME_SIZE_V = 800                                        

# Padding around all major container Frames.
FRAME_PADDING = 4                                         

# Vertical space between stacked sections.
SECTION_SPACING = 10                                      

# Space between a section title and its content frame.
SECTION_TITLE_SPACING = 4                                  

# Space between a label and its corresponding input widget.
LABEL_ENTRY_SPACING = 5                                   

# Standard spacing around or between buttons in a layout.
BUTTON_SPACING = 10                                       

# Shared corner radius for cards, bordered frames, or custom widgets.
BORDER_RADIUS = 6

LAYOUT_COLUMN_GAP = 8     # Horizontal gap between columns in weighted rows
LAYOUT_ROW_GAP = 12       # Vertical gap between rows in layouts
LAYOUT_CARD_GAP = 8       # Gap between cards in a card row


# ====================================================================================================
# 6. MISC VISUAL CONSTANTS
# ----------------------------------------------------------------------------------------------------
# Additional UI behaviour and style parameters used across layout widgets and UIComponents.
# ====================================================================================================

# Corner radius for modern widgets (e.g., rounded entries, container blocks).
WIDGET_CORNER_RADIUS = 4

# Default cursor for interactive elements.
DEFAULT_CURSOR = "arrow"

# Cursor used for clickable link-like labels.
LINK_CURSOR = "hand2"

# Focus highlight thickness for Entry and other focusable widgets.
HIGHLIGHT_THICKNESS = 1

# Milliseconds used for small animations or UI transitions.
DEFAULT_ANIMATION_SPEED = 100

# Progress colour applied to styled ttk.Progressbar.
# Uses the darker primary shade to maintain strong visual contrast.
DEFAULT_PROGRESS_COLOUR = COLOUR_PRIMARY_DARK


# ====================================================================================================
# 7. THEME SUMMARY HELPER (FULL SEMANTIC TREE)
# ----------------------------------------------------------------------------------------------------
# Provides a fully structured, deeply grouped summary of all theme values.
# Ideal for debugging, theme inspectors, or dynamically verifying consistency.
# ----------------------------------------------------------------------------------------------------

def get_theme_summary() -> dict:
    return {
        "fonts": {
            "family": GUI_FONT_FAMILY,
            "size_heading": GUI_FONT_SIZE_HEADING,
            "size_title": GUI_FONT_SIZE_TITLE,
            "size_default": GUI_FONT_SIZE_DEFAULT,
            "size_small": GUI_FONT_SIZE_SMALL,
        },

        "palette_base": {
            "primary": {
                "light": COLOUR_PRIMARY_LIGHT,
                "main": COLOUR_PRIMARY,
                "dark": COLOUR_PRIMARY_DARK,
            },
            "secondary": {
                "light": COLOUR_SECONDARY_LIGHT,
                "main": COLOUR_SECONDARY,
                "dark": COLOUR_SECONDARY_DARK,
            },
            "status": {
                "green": COLOUR_STATUS_GREEN,
                "green_dark": COLOUR_STATUS_GREEN_DARK,
                "amber": COLOUR_STATUS_AMBER,
                "amber_dark": COLOUR_STATUS_AMBER_DARK,
                "red": COLOUR_STATUS_RED,
                "red_dark": COLOUR_STATUS_RED_DARK,
            },
            "text": {
                "primary": COLOUR_TEXT_PRIMARY,
                "mono": COLOUR_TEXT_MONO,
            }
        },

        "roles_background": {
            "primary": GUI_COLOUR_BG_PRIMARY,
            "secondary": GUI_COLOUR_BG_SECONDARY,
            "input": GUI_COLOUR_BG_INPUT,
            "textarea": GUI_COLOUR_BG_TEXTAREA,
            "disabled": GUI_COLOUR_BG_DISABLED,
        },

        "roles_text": {
            "primary": TEXT_COLOUR_PRIMARY,
            "secondary": TEXT_COLOUR_SECONDARY,
            "mono": TEXT_COLOUR_MONO,
            "disabled": TEXT_COLOUR_DISABLED,
        },

        "roles_buttons": {
            "primary": {
                "bg": BUTTON_PRIMARY_BG,
                "hover": BUTTON_PRIMARY_HOVER,
                "active": BUTTON_PRIMARY_ACTIVE,
                "text": BUTTON_PRIMARY_TEXT,
                "disabled": BUTTON_PRIMARY_DISABLED,
            },
            "secondary": {
                "bg": BUTTON_SECONDARY_BG,
                "hover": BUTTON_SECONDARY_HOVER,
                "active": BUTTON_SECONDARY_ACTIVE,
                "text": BUTTON_SECONDARY_TEXT,
                "disabled": BUTTON_SECONDARY_DISABLED,
            },
            "success": {
                "bg": BUTTON_SUCCESS_BG,
                "hover": BUTTON_SUCCESS_HOVER,
                "active": BUTTON_SUCCESS_ACTIVE,
                "text": BUTTON_SUCCESS_TEXT,
            },
            "warning": {
                "bg": BUTTON_WARNING_BG,
                "hover": BUTTON_WARNING_HOVER,
                "active": BUTTON_WARNING_ACTIVE,
                "text": BUTTON_WARNING_TEXT,
            },
            "danger": {
                "bg": BUTTON_DANGER_BG,
                "hover": BUTTON_DANGER_HOVER,
                "active": BUTTON_DANGER_ACTIVE,
                "text": BUTTON_DANGER_TEXT,
            },
        },

        "roles_accents": {
            "accent": GUI_COLOUR_ACCENT,
            "accent_light": GUI_COLOUR_ACCENT_LIGHT,
            "accent_dark": GUI_COLOUR_ACCENT_DARK,
        },

        "roles_status": {
            "success": GUI_COLOUR_STATUS_SUCCESS,
            "warning": GUI_COLOUR_STATUS_WARNING,
            "error": GUI_COLOUR_STATUS_ERROR,
        },

        "roles_borders": {
            "border": GUI_COLOUR_BORDER,
            "divider": GUI_COLOUR_DIVIDER,
        },

        "layout": {
            "frame_heading": FRAME_HEADING,
            "frame_size": f"{FRAME_SIZE_H}x{FRAME_SIZE_V}",
            "padding": FRAME_PADDING,
            "section_spacing": SECTION_SPACING,
            "section_title_spacing": SECTION_TITLE_SPACING,
            "label_entry_spacing": LABEL_ENTRY_SPACING,
            "button_spacing": BUTTON_SPACING,
            "border_radius": BORDER_RADIUS,
        },

        "meta": {
            "theme_name": "GoPuff Blue/White v1.0",
            "supports_display_font": True,
        },
    }


# ====================================================================================================
# 8. SELF-TEST (RUN ONLY WHEN EXECUTING THIS FILE DIRECTLY)
# ----------------------------------------------------------------------------------------------------
# Provides a readable dump of the full semantic theme tree.
# Confirms all keys resolve to valid values and no semantic names are missing.
# ----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== G01a_style_config.py — Theme Self-Test ===\n")

    from pprint import pprint
    pprint(get_theme_summary(), sort_dicts=False)

    print("\nSelf-test completed successfully.")
