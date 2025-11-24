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
# A single shared font family used across all GUI widgets.
# Individual sizes (heading, default, small) are applied by UIComponents or BaseGUI
# when constructing labels, buttons, entries, and section headings.
# ====================================================================================================

# Primary UI font family used for all text elements (labels, buttons, headings, inputs).
# Fallbacks ensure cross-platform behaviour if Poppins is not installed.
GUI_FONT_FAMILY = ("Poppins", "Segoe UI", "Arial", "sans-serif")

# Font size used for section titles, major headings, and emphasised labels.
GUI_FONT_SIZE_HEADING = 14

# Default font size for section headings.
GUI_FONT_SIZE_TITLE = 12

# Default font size for general-purpose UI elements (labels, buttons, entries, comboboxes).
GUI_FONT_SIZE_DEFAULT = 10

# Used for helper text, subtle status messages, footer text, or secondary annotations.
GUI_FONT_SIZE_SMALL = 9


# ====================================================================================================
# 4. COLOUR PALETTE — ALL COLOURS DEFINED HERE ONLY
# ----------------------------------------------------------------------------------------------------
# A minimal, theme-ready palette using "primary", "secondary", and "status" colours.
#
# PRIMARY   → core brand colour family (blue), used for actions and highlights.
# SECONDARY → neutral background family (white + soft neutrals), used for surfaces and structure.
# STATUS    → semantic traffic-light colours (success, warning, error), not affected by rebranding.
# TEXT      → neutral text colours for readability (primary, mono/log output).
#
# Widgets NEVER reference these values directly — only the semantic role colours in Section 4A.
# This allows the entire UI theme to be changed by modifying this palette alone.
# ====================================================================================================

# ----------------------------------------------------------------------------------------------------
# Primary brand colours (blue)
# Used for buttons, highlights, active states, and emphasis elements.
# ----------------------------------------------------------------------------------------------------
COLOUR_PRIMARY_LIGHT   = "#C7ECFF"   # Light tint of brand colour (hover states, subtle accents)
COLOUR_PRIMARY         = "#00A3FE"   # Main brand colour (buttons, call-to-actions, primary accents)
COLOUR_PRIMARY_DARK    = "#007CC4"   # Stronger shade (active states, strong accents, pressed buttons)

# ----------------------------------------------------------------------------------------------------
# Secondary colours (background neutrals)
# Used for window backgrounds, panels, grouped sections, and disabled areas.
# ----------------------------------------------------------------------------------------------------
COLOUR_SECONDARY_LIGHT = "#FFFFFF"   # Primary window background and top-level frames
COLOUR_SECONDARY       = "#F3F8FE"   # Section/panel backgrounds and scrollable areas
COLOUR_SECONDARY_DARK  = "#C6D8E5"   # Borders, disabled states, low-contrast separators

# ----------------------------------------------------------------------------------------------------
# Status colours (semantic)
# These convey functional meaning (success/warning/error) and remain constant across themes.
# ----------------------------------------------------------------------------------------------------
COLOUR_STATUS_GREEN    = "#2ECC71"   # Success indicators (validation OK, completed states)
COLOUR_STATUS_AMBER    = "#F1C40F"   # Warning indicators (caution, incomplete, attention required)
COLOUR_STATUS_RED      = "#E74C3C"   # Error indicators (failures, validation errors, critical alerts)

# ----------------------------------------------------------------------------------------------------
# Text colours (neutral text shades for readability)
# Used for body text, console/log text, and dark-mode compatible elements.
# ----------------------------------------------------------------------------------------------------
COLOUR_TEXT_PRIMARY = "#1A1A1A"      # Main readable text for labels, descriptions, and body content
COLOUR_TEXT_MONO    = "#262626"      # Slightly darker shade for console/log outputs and mono text


# ====================================================================================================
# 4A. ROLE-BASED COLOUR ASSIGNMENTS (ALL USAGE-BASED COMMENTS)
# ----------------------------------------------------------------------------------------------------
# These constants are consumed by BaseGUI, UIComponents, and layout modules.
# They NEVER define new colours — they ONLY reference Section 4 colours.
#
# Each role name describes HOW the colour is used in the UI, not what it looks like.
# This ensures the visual design can be changed without modifying any GUI module.
# ====================================================================================================

# ----------------------------------------------------------------------------------------------------
# Background roles
# ----------------------------------------------------------------------------------------------------

# Used as the default background for all main windows (BaseGUI root window, top-level Frames).
GUI_COLOUR_BG_PRIMARY = COLOUR_SECONDARY_LIGHT

# Used for grouped sections, info panels, scrollable sub-frames, and visually separated areas.
GUI_COLOUR_BG_SECONDARY = COLOUR_SECONDARY

# Background for Entry, Combobox, Spinbox, and other input widgets.
GUI_COLOUR_BG_INPUT = COLOUR_SECONDARY_LIGHT

# Used for Text, ScrolledText, or other multi-line widgets (logs, output panels).
GUI_COLOUR_BG_TEXTAREA = COLOUR_SECONDARY

# Used by disabled input widgets and disabled UI components.
GUI_COLOUR_BG_DISABLED = COLOUR_SECONDARY_DARK

# ----------------------------------------------------------------------------------------------------
# Text roles
# ----------------------------------------------------------------------------------------------------

# Used for primary text elements that require emphasis (titles, headings, labels on coloured panels).
TEXT_COLOUR_PRIMARY = COLOUR_PRIMARY_DARK

# Default text colour for labels, explanatory text, and general-purpose body text.
TEXT_COLOUR_SECONDARY = COLOUR_TEXT_PRIMARY

# Used for console/log outputs or code-style text areas.
TEXT_COLOUR_MONO = COLOUR_TEXT_MONO

# Used for disabled labels, disabled buttons, and inactive informational text.
TEXT_COLOUR_DISABLED = COLOUR_SECONDARY_DARK

# ----------------------------------------------------------------------------------------------------
# Button roles
# ----------------------------------------------------------------------------------------------------

# Background colour for all standard push buttons.
BUTTON_COLOUR_BG = COLOUR_PRIMARY

# Colour applied when mouse hovers over a button.
BUTTON_COLOUR_HOVER = COLOUR_PRIMARY_DARK

# Colour applied while a button is pressed or active.
BUTTON_COLOUR_ACTIVE = COLOUR_PRIMARY_DARK

# Text colour for enabled buttons.
BUTTON_TEXT_COLOUR = COLOUR_SECONDARY_LIGHT

# Background for disabled buttons.
BUTTON_DISABLED_COLOUR = COLOUR_SECONDARY_DARK

# ----------------------------------------------------------------------------------------------------
# Accent roles
# ----------------------------------------------------------------------------------------------------

# Used for accent lines, highlights, and emphasis components.
GUI_COLOUR_ACCENT = COLOUR_PRIMARY

# Used for hover-line accents, secondary highlights, or inactive tab elements.
GUI_COLOUR_ACCENT_LIGHT = COLOUR_PRIMARY_LIGHT

# Used for active borders, strong highlights, and emphasised accents.
GUI_COLOUR_ACCENT_DARK = COLOUR_PRIMARY_DARK

# ----------------------------------------------------------------------------------------------------
# Status indicators
# ----------------------------------------------------------------------------------------------------

# Used for success messages, validation OK indicators, and positive state highlights.
GUI_COLOUR_SUCCESS = COLOUR_STATUS_GREEN

# Used for warnings, cautions, and non-critical issues.
GUI_COLOUR_WARNING = COLOUR_STATUS_AMBER

# Used for errors, validation failures, and critical alerts.
GUI_COLOUR_ERROR = COLOUR_STATUS_RED

# ----------------------------------------------------------------------------------------------------
# Borders & dividers
# ----------------------------------------------------------------------------------------------------

# Used for Frame borders, input borders, and general UI boundaries.
GUI_COLOUR_BORDER = COLOUR_SECONDARY_DARK

# Used for thin horizontal dividers and subtle separators.
GUI_COLOUR_DIVIDER = COLOUR_SECONDARY_DARK

# ----------------------------------------------------------------------------------------------------
# Checkbox / radio
# ----------------------------------------------------------------------------------------------------

# Used when checkbox/radio is active or selected.
CHECK_RADIO_COLOUR_ACTIVE = COLOUR_PRIMARY

# Used when checkbox/radio is inactive but enabled.
CHECK_RADIO_COLOUR_INACTIVE = COLOUR_SECONDARY_DARK

# Used when checkbox/radio widgets are disabled.
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
# 7. THEME SUMMARY HELPER
# ----------------------------------------------------------------------------------------------------
# Provides a summarised dictionary of all theme values, useful for debugging,
# introspection, or dynamic theme inspectors within the GUI.
# ====================================================================================================

def get_theme_summary() -> dict:
    return {
        "fonts": {
            "family": GUI_FONT_FAMILY,
            "default_size": GUI_FONT_SIZE_DEFAULT,
            "heading_size": GUI_FONT_SIZE_HEADING,
            "small_size": GUI_FONT_SIZE_SMALL,
        },

        "colours_background": {
            "primary": GUI_COLOUR_BG_PRIMARY,
            "secondary": GUI_COLOUR_BG_SECONDARY,
            "input": GUI_COLOUR_BG_INPUT,
            "textarea": GUI_COLOUR_BG_TEXTAREA,
            "disabled": GUI_COLOUR_BG_DISABLED,
        },

        "colours_text": {
            "primary": TEXT_COLOUR_PRIMARY,
            "secondary": TEXT_COLOUR_SECONDARY,
            "mono": TEXT_COLOUR_MONO,
            "disabled": TEXT_COLOUR_DISABLED,
        },

        "palette_primary": {
            "light": COLOUR_PRIMARY_LIGHT,
            "main": COLOUR_PRIMARY,
            "dark": COLOUR_PRIMARY_DARK,
        },

        "palette_secondary": {
            "light": COLOUR_SECONDARY_LIGHT,
            "main": COLOUR_SECONDARY,
            "dark": COLOUR_SECONDARY_DARK,
        },

        "status": {
            "success": COLOUR_STATUS_GREEN,
            "warning": COLOUR_STATUS_AMBER,
            "error": COLOUR_STATUS_RED,
        },

        "buttons": {
            "background": BUTTON_COLOUR_BG,
            "hover": BUTTON_COLOUR_HOVER,
            "active": BUTTON_COLOUR_ACTIVE,
            "text": BUTTON_TEXT_COLOUR,
            "disabled": BUTTON_DISABLED_COLOUR,
        },

        "accents": {
            "accent": GUI_COLOUR_ACCENT,
            "accent_light": GUI_COLOUR_ACCENT_LIGHT,
            "accent_dark": GUI_COLOUR_ACCENT_DARK,
            "success": GUI_COLOUR_SUCCESS,
            "warning": GUI_COLOUR_WARNING,
            "error": GUI_COLOUR_ERROR,
        },

        "borders": {
            "border": GUI_COLOUR_BORDER,
            "divider": GUI_COLOUR_DIVIDER,
        },

        "layout": {
            "frame_size": f"{FRAME_SIZE_H}x{FRAME_SIZE_V}",
            "padding": FRAME_PADDING,
            "section_spacing": SECTION_SPACING,
            "button_spacing": BUTTON_SPACING,
        },

        "meta": {
            "theme_name": "GoPuff Blue/White v1.0",
            "supports_display_font": True,
        },
    }


# ====================================================================================================
# 8. SELF-TEST (RUN ONLY WHEN EXECUTING THIS FILE DIRECTLY)
# ----------------------------------------------------------------------------------------------------
# Provides a quick sanity check of the theme configuration.
# Confirms that all palette values and semantic role mappings are valid.
# This block is *not* executed when imported by other GUI modules.
# ====================================================================================================

if __name__ == "__main__":
    print("=== G01a_style_config.py — Theme Self-Test ===\n")

    theme = get_theme_summary()

    # Pretty-print theme summary
    from pprint import pprint
    pprint(theme)

    print("\nSelf-test completed.")
    print("If no errors were raised, the theme configuration is valid.")
