# ====================================================================================================
# G01b_style_engine.py
# ----------------------------------------------------------------------------------------------------
# Centralised ttk style engine for the entire GUI framework.
#
# Purpose:
#   - Convert the theme constants defined in G01a_style_config (fonts, colours,
#     spacing, semantic roles) into concrete ttk.Style configurations.
#   - Provide a SINGLE entry point for all ttk style definitions, ensuring:
#         • consistent structure across all widgets
#         • zero duplication of colour/spacing/font logic
#         • full separation of “design tokens” (G01a) from “style application” (G01b)
#   - Resolve and register named Tk fonts required by the UI (base, heading,
#     section-heading).
#   - Apply fully-expanded style dictionaries to all core ttk widget types
#     (Labels, Buttons, Frames, Notebook, Treeview, Progressbar, Cards, Sections).
#
# Integration:
#     from gui.G01b_style_engine import configure_ttk_styles
#
#     style = ttk.Style()
#     configure_ttk_styles(style)
#
# Relationship to G01a:
#   - G01a_style_config defines ALL THEME VALUES:
#         • GUI_FONT_FAMILY, font sizes, colour palette, semantic colour roles
#         • layout parameters (padding, section spacing, border radius)
#   - G01b_style_engine consumes those values and builds:
#         • named fonts
#         • a complete set of ttk.Style() configurations
#         • a uniform style template used to create consistent style blocks
#
# Rules:
#   - No hard-coded colours or sizes appear in this module except where required
#     by ttk itself; all values originate from G01a_style_config.
#   - No GUI widgets are created here — only style configuration.
#   - No side effects at import time (configuration only occurs when the caller
#     invokes configure_ttk_styles()).
#
# Notes:
#   - STYLE_TEMPLATE ensures every style dict shares the same key structure.
#   - build_style(...) + clean_style_dict(...) guarantee safe, consistent
#     merging of template → base → overrides.
#   - run_self_test() provides a non-visual diagnostic to validate theme loading.
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
from gui.G00a_gui_packages import *          # tk, ttk, tkFont, etc.
from gui.G01a_style_config import *          # Full theme + semantic tree


# ====================================================================================================
# 3. FONT RESOLUTION & NAMED FONTS
# ----------------------------------------------------------------------------------------------------
# This section handles ALL font-related logic for the GUI framework.
#
# Architectural Role:
#   • G01a_style_config defines abstract design tokens (sizes, preferred families).
#   • This module (G01b) turns those tokens into real Tkinter named font objects.
#   • Higher layers (G01c primitives, G01d layout, G02 pages, G03 controllers) NEVER
#     touch raw font sizes or families — they reference styles that use these fonts.
#
# Responsibilities:
#   1. Provide canonical Tk named font identifiers (GP.UI.*).
#   2. Resolve which system-installed font family to use at runtime.
#   3. Create/update all named fonts safely and idempotently.
#
# Result:
#   Typography is defined once → and used consistently everywhere in the GUI.
# ====================================================================================================

# ----------------------------------------------------------------------------------------------------
# Named Tk font identifiers
# ----------------------------------------------------------------------------------------------------
# These become actual Tk font objects once ensure_named_fonts() executes.
# They are globally registered in the Tk interpreter and can be referenced
# by style configuration and widget primitives using the `font="Name"` syntax.
#
# Naming scheme:
#   GP.UI.Base            → Default body font
#   GP.UI.BaseBold        → Default bold body font
#   GP.UI.Heading         → Large top-level window/page headings
#   GP.UI.SectionHeading  → Section/card headings (smaller than main heading)
# ----------------------------------------------------------------------------------------------------
FONT_NAME_BASE = "GP.UI.Base"
FONT_NAME_BASE_BOLD = "GP.UI.BaseBold"
FONT_NAME_HEADING = "GP.UI.Heading"
FONT_NAME_SECTION_HEADING = "GP.UI.SectionHeading"


# ----------------------------------------------------------------------------------------------------
# FONT FAMILY RESOLUTION
# ----------------------------------------------------------------------------------------------------
# Determines which font family should be used for all named fonts.
#
# Strategy:
#   • Iterate through GUI_FONT_FAMILY from G01a_style_config:
#         ("Poppins", "Segoe UI", "Arial", "sans-serif")
#   • Attempt to instantiate a Tk font for each family.
#   • Return the first one that works on the current OS.
#   • If everything fails, fall back to "Segoe UI" as a last resort.
#
# Purpose:
#   • Ensures robust cross-platform behaviour (Windows / macOS / Linux / WSL / Docker).
#   • Avoids Tk runtime crashes caused by missing font families.
#   • Allows theme designers to prefer custom brand fonts but degrade gracefully.
# ----------------------------------------------------------------------------------------------------
def resolve_font_family() -> str:
    """
    Resolve the active GUI font family for the current environment.
    """
    families = GUI_FONT_FAMILY
    logger.debug("[G01b] Resolving font family from GUI_FONT_FAMILY=%r", families)

    if isinstance(families, (tuple, list)):
        for fam in families:
            try:
                tkFont.Font(family=fam, size=GUI_FONT_SIZE_DEFAULT)  # type: ignore[name-defined]
                logger.info("[G01b] Resolved GUI font family: %s", fam)
                return fam
            except Exception:  # noqa: BLE001
                logger.debug("[G01b] Font family '%s' not available; trying next.", fam)
    else:
        try:
            tkFont.Font(family=families, size=GUI_FONT_SIZE_DEFAULT)  # type: ignore[name-defined]
            logger.info("[G01b] Resolved GUI font family: %s", families)
            return families
        except Exception:  # noqa: BLE001
            logger.debug("[G01b] Font family '%s' not available; falling back.", families)

    fallback = "Segoe UI"
    logger.warning(
        "[G01b] No configured GUI_FONT_FAMILY fonts available; using fallback %s",
        fallback,
    )
    return fallback


# ----------------------------------------------------------------------------------------------------
# CREATE / UPDATE NAMED FONTS
# ----------------------------------------------------------------------------------------------------
# Converts the resolved font family and size tokens into REAL Tk named fonts.
#
# Behaviour:
#   • Idempotent — you may call this repeatedly; existing fonts are updated,
#     non-existent fonts are created.
#   • Ensures consistent typography across the entire GUI.
#   • All widgets that use ttk styles referencing these names update automatically.
#
# Named fonts created/updated:
#   GP.UI.Base            → Body font (size=GUI_FONT_SIZE_DEFAULT)
#   GP.UI.BaseBold        → Bold body font
#   GP.UI.Heading         → Top-level window/page headings (size=GUI_FONT_SIZE_HEADING)
#   GP.UI.SectionHeading  → Sub-section headings (size=GUI_FONT_SIZE_TITLE)
# ----------------------------------------------------------------------------------------------------
def ensure_named_fonts(family: str) -> None:
    """
    Create or update the core named Tk fonts used by the GUI framework.
    """
    logger.debug("[G01b] Ensuring named fonts exist (family=%s).", family)

    # -----------------------------------------------------------------------------------------------
    # Base font (normal body text)
    # -----------------------------------------------------------------------------------------------
    try:
        base_font_obj = tkFont.nametofont(FONT_NAME_BASE)  # type: ignore[name-defined]
        base_font_obj.configure(family=family, size=GUI_FONT_SIZE_DEFAULT)
        logger.debug("[G01b] Updated existing base font '%s'.", FONT_NAME_BASE)
    except Exception:
        tkFont.Font(  # type: ignore[name-defined]
            name=FONT_NAME_BASE,
            family=family,
            size=GUI_FONT_SIZE_DEFAULT,
        )
        logger.debug("[G01b] Created new base font '%s'.", FONT_NAME_BASE)

    # -----------------------------------------------------------------------------------------------
    # Bold base font (normal text, bold weight)
    # -----------------------------------------------------------------------------------------------
    try:
        bold_font_obj = tkFont.nametofont(FONT_NAME_BASE_BOLD)  # type: ignore[name-defined]
        bold_font_obj.configure(
            family=family,
            size=GUI_FONT_SIZE_DEFAULT,
            weight="bold",
        )
        logger.debug("[G01b] Updated existing base bold font '%s'.", FONT_NAME_BASE_BOLD)
    except Exception:
        tkFont.Font(  # type: ignore[name-defined]
            name=FONT_NAME_BASE_BOLD,
            family=family,
            size=GUI_FONT_SIZE_DEFAULT,
            weight="bold",
        )
        logger.debug("[G01b] Created new base bold font '%s'.", FONT_NAME_BASE_BOLD)

    # -----------------------------------------------------------------------------------------------
    # Main heading font (large window/page titles)
    # -----------------------------------------------------------------------------------------------
    try:
        heading_font_obj = tkFont.nametofont(FONT_NAME_HEADING)  # type: ignore[name-defined]
        heading_font_obj.configure(
            family=family,
            size=GUI_FONT_SIZE_HEADING,
            weight="bold",
        )
        logger.debug("[G01b] Updated existing heading font '%s'.", FONT_NAME_HEADING)
    except Exception:
        tkFont.Font(  # type: ignore[name-defined]
            name=FONT_NAME_HEADING,
            family=family,
            size=GUI_FONT_SIZE_HEADING,
            weight="bold",
        )
        logger.debug("[G01b] Created new heading font '%s'.", FONT_NAME_HEADING)

    # -----------------------------------------------------------------------------------------------
    # Section heading font (smaller subsection titles)
    # -----------------------------------------------------------------------------------------------
    try:
        section_font_obj = tkFont.nametofont(FONT_NAME_SECTION_HEADING)  # type: ignore[name-defined]
        section_font_obj.configure(
            family=family,
            size=GUI_FONT_SIZE_TITLE,
            weight="bold",
        )
        logger.debug(
            "[G01b] Updated existing section heading font '%s'.",
            FONT_NAME_SECTION_HEADING,
        )
    except Exception:
        tkFont.Font(  # type: ignore[name-defined]
            name=FONT_NAME_SECTION_HEADING,
            family=family,
            size=GUI_FONT_SIZE_TITLE,
            weight="bold",
        )
        logger.debug(
            "[G01b] Created new section heading font '%s'.",
            FONT_NAME_SECTION_HEADING,
        )


# ====================================================================================================
# 4. UNIFORM STYLE TEMPLATE (TTK STYLE DICTIONARY SYSTEM)
# ----------------------------------------------------------------------------------------------------
# ttk styles are configured using dictionary keys such as:
#   background=, foreground=, font=, padding=, borderwidth=, relief=, etc.
#
# Every widget style in this module is built from one shared template:
#       STYLE_TEMPLATE
#
# Why a template?
#   • Ensures ALL styles share the same key set (colour, typography, spacing, borders).
#   • Prevents style blocks from drifting apart over time.
#   • Forces style definitions to be explicit, readable, and consistent.
#
# How it works:
#   • STYLE_TEMPLATE defines ALL possible supported ttk keys, initialised to None.
#   • build_style(...) merges:
#         1) STYLE_TEMPLATE     (full key set)
#         2) base style dict    (style-specific defaults)
#         3) overrides dict     (rare, state-specific adjustments)
#   • clean_style_dict(...) removes all None values before calling ttk.Style.configure().
#
# Result:
#   Every ttk style in the framework:
#       - Has consistent structure
#       - Documents all supported keys
#       - Only passes valid, non-None keys to ttk
# ====================================================================================================

STYLE_TEMPLATE: Dict[str, Any] = {
    # -----------------------------------------------------------------------------------------------
    # COLOURS
    # -----------------------------------------------------------------------------------------------
    "background": None,         # Base widget background colour (frames, labels, buttons)
    "foreground": None,         # Primary text/foreground colour
    "fieldbackground": None,    # Internal background for Entry/Combobox fields
    "arrowcolor": None,         # Arrow colour (Combobox, Spinbox, etc.)
    "selectforeground": None,   # Foreground colour when row/item is selected
    "selectbackground": None,   # Background colour when row/item is selected
    "troughcolor": None,        # Background of trough areas (Progressbar, Scale)
    "lightcolor": None,         # Light edge for classic 3D shadowing (not used often)
    "darkcolor": None,          # Dark edge for classic 3D effects (not used often)
    "bordercolor": None,        # Explicit border colour (when supported by theme engine)

    # -----------------------------------------------------------------------------------------------
    # TYPOGRAPHY
    # -----------------------------------------------------------------------------------------------
    "font": None,               # Named Tk font or tuple (family, size, weight)

    # -----------------------------------------------------------------------------------------------
    # SPACING & INTERNAL LAYOUT
    # -----------------------------------------------------------------------------------------------
    "padding": None,            # Internal padding (left, top, right, bottom)

    # -----------------------------------------------------------------------------------------------
    # BORDER APPEARANCE
    # -----------------------------------------------------------------------------------------------
    "borderwidth": None,        # Width of widget border (in pixels)
    "relief": None,             # Border type: flat / raised / sunken / solid / groove / ridge
}


# ----------------------------------------------------------------------------------------------------
# STYLE BUILDER
# ----------------------------------------------------------------------------------------------------
# build_style(...) constructs a complete style definition from:
#
#   STYLE_TEMPLATE  →  base  →  overrides
#
# This ensures:
#   - All styles share one guaranteed, unified structure.
#   - Styles remain readable, succinct, and easy to diff.
#   - Rare overrides (hover, active, disabled states) do not repeat entire style blocks.
#
# This function returns a dict **including** None values.
# ttk.Style.configure(...) cannot handle None, so clean_style_dict(...) must be called next.
# ----------------------------------------------------------------------------------------------------
def build_style(base: Dict[str, Any], overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Build a complete ttk style dictionary using STYLE_TEMPLATE as the foundation.

    Args:
        base:
            Core style attributes (colours, font, spacing, borders).
            Keys must be a subset of STYLE_TEMPLATE.

        overrides:
            Values that override both the template and the base block.
            Used rarely — typically for hover/active state tweaks.

    Returns:
        dict[str, Any]:
            The merged style dict containing None keys, ready to be cleaned
            with clean_style_dict(...).
    """
    merged: Dict[str, Any] = STYLE_TEMPLATE.copy()
    merged.update(base)

    if overrides:
        merged.update(overrides)

    return merged


# ----------------------------------------------------------------------------------------------------
# STYLE CLEANER
# ----------------------------------------------------------------------------------------------------
# ttk.Style.configure() cannot accept keys where the value is None — Tk raises Tcl errors.
#
# clean_style_dict(...) filters out all None entries so that only valid,
# explicitly-set style values are passed to ttk.
#
# This approach allows:
#   • Rich, explicit style templates (good for documentation)
#   • Safety when configuring ttk styles
# ----------------------------------------------------------------------------------------------------
def clean_style_dict(values: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strip None values from a style dict before passing it into ttk.Style.configure().

    Args:
        values:
            The style dictionary produced by build_style(...).

    Returns:
        dict[str, Any]:
            A shallow copy of `values` without any None entries.
    """
    return {k: v for k, v in values.items() if v is not None}


# ----------------------------------------------------------------------------------------------------
# STYLE REGISTRY (Diagnostics / Debugging Only)
# ----------------------------------------------------------------------------------------------------
# Fully updated to match ALL 4-way style variants:
#   • Primary/Secondary × Normal/Bold
#   • Success/Warning/Error
#   • Card labels
#   • Window headings
#   • Page headings
#   • Section headings
#   • All buttons, inputs, frames, cards, notebook, treeview, etc.
# ----------------------------------------------------------------------------------------------------
STYLE_BLOCKS: Dict[str, str] = {

    # ================================================================================================
    # A. LABEL MATRIX — PRIMARY/SECONDARY × NORMAL/BOLD
    # ================================================================================================
    "Primary.Normal.TLabel":   "Primary background, normal font label",
    "Primary.Bold.TLabel":     "Primary background, bold font label",
    "Secondary.Normal.TLabel": "Secondary background, normal font label",
    "Secondary.Bold.TLabel":   "Secondary background, bold font label",

    # ================================================================================================
    # B. STATUS LABELS — PRIMARY/SECONDARY × NORMAL/BOLD × SUCCESS/WARNING/ERROR
    # ================================================================================================
    # Success
    "Primary.Success.Normal.TLabel":     "Success label (primary, normal)",
    "Primary.Success.Bold.TLabel":       "Success label (primary, bold)",
    "Secondary.Success.Normal.TLabel":   "Success label (secondary, normal)",
    "Secondary.Success.Bold.TLabel":     "Success label (secondary, bold)",

    # Warning
    "Primary.Warning.Normal.TLabel":     "Warning label (primary, normal)",
    "Primary.Warning.Bold.TLabel":       "Warning label (primary, bold)",
    "Secondary.Warning.Normal.TLabel":   "Warning label (secondary, normal)",
    "Secondary.Warning.Bold.TLabel":     "Warning label (secondary, bold)",

    # Error
    "Primary.Error.Normal.TLabel":       "Error label (primary, normal)",
    "Primary.Error.Bold.TLabel":         "Error label (primary, bold)",
    "Secondary.Error.Normal.TLabel":     "Error label (secondary, normal)",
    "Secondary.Error.Bold.TLabel":       "Error label (secondary, bold)",

    # ================================================================================================
    # C. CARD LABELS — PRIMARY/SECONDARY × NORMAL/BOLD
    # ================================================================================================
    "Primary.Card.Normal.TLabel":     "Card label (primary, normal)",
    "Primary.Card.Bold.TLabel":       "Card label (primary, bold)",
    "Secondary.Card.Normal.TLabel":   "Card label (secondary, normal)",
    "Secondary.Card.Bold.TLabel":     "Card label (secondary, bold)",

    # ================================================================================================
    # D. WINDOW HEADINGS — PRIMARY/SECONDARY × NORMAL/BOLD
    # ================================================================================================
    "Primary.WindowHeading.Normal.TLabel":   "Primary window heading (normal)",
    "Primary.WindowHeading.Bold.TLabel":     "Primary window heading (bold)",
    "Secondary.WindowHeading.Normal.TLabel": "Secondary window heading (normal)",
    "Secondary.WindowHeading.Bold.TLabel":   "Secondary window heading (bold)",

    # ================================================================================================
    # E. PAGE HEADINGS — PRIMARY/SECONDARY × NORMAL/BOLD
    # ================================================================================================
    "Primary.Heading.Normal.TLabel":   "Primary page heading (normal)",
    "Primary.Heading.Bold.TLabel":     "Primary page heading (bold)",
    "Secondary.Heading.Normal.TLabel": "Secondary page heading (normal)",
    "Secondary.Heading.Bold.TLabel":   "Secondary page heading (bold)",

    # ================================================================================================
    # F. SECTION HEADINGS — PRIMARY/SECONDARY × NORMAL/BOLD
    # ================================================================================================
    "Primary.SectionHeading.Normal.TLabel":   "Primary section heading (normal)",
    "Primary.SectionHeading.Bold.TLabel":     "Primary section heading (bold)",
    "Secondary.SectionHeading.Normal.TLabel": "Secondary section heading (normal)",
    "Secondary.SectionHeading.Bold.TLabel":   "Secondary section heading (bold)",

    # ================================================================================================
    # BUTTONS
    # ================================================================================================
    "TButton":           "Base neutral button",
    "Primary.TButton":   "Primary action button",
    "Secondary.TButton": "Secondary neutral button",
    "Success.TButton":   "Success button",
    "Warning.TButton":   "Warning button",
    "Danger.TButton":    "Danger button",

    # ================================================================================================
    # INPUT CONTROLS
    # ================================================================================================
    "TEntry":        "Text entry field",
    "TCombobox":     "Dropdown combobox",
    "TCheckbutton":  "Checkbox",
    "TRadiobutton":  "Radio button",

    # ================================================================================================
    # NOTEBOOK / TABS
    # ================================================================================================
    "TNotebook":     "Notebook container",
    "TNotebook.Tab": "Notebook tab",

    # ================================================================================================
    # TREEVIEW
    # ================================================================================================
    "Treeview":         "Treeview table",
    "Treeview.Heading": "Treeview column heading",

    # ================================================================================================
    # MENU BUTTON
    # ================================================================================================
    "TMenubutton": "Menu button",

    # ================================================================================================
    # PROGRESSBAR
    # ================================================================================================
    "Horizontal.TProgressbar": "Horizontal progress bar",

    # ================================================================================================
    # FRAMES
    # ================================================================================================
    "TFrame":               "Base frame",
    "SectionOuter.TFrame":  "Section outer container",
    "SectionBody.TFrame":   "Section body container",

    # ================================================================================================
    # CARDS
    # ================================================================================================
    "Card.TFrame":       "Card container frame",
    "Card.TRadiobutton": "Card radio selector",

    # ================================================================================================
    # DIVIDER
    # ================================================================================================
    "ToolbarDivider.TFrame": "Toolbar divider",
}



# ====================================================================================================
# 5. MAIN STYLE ENGINE
# ----------------------------------------------------------------------------------------------------
def configure_ttk_styles(style: ttk.Style) -> None:  # type: ignore[name-defined]
    """
    Apply the full ttk style configuration for the GUI framework.

    This function is the single entry point for styling in the framework.
    """

    logger.info("[G01b] Starting ttk style configuration.")

    # 0. Force stable base theme
    try:
        style.theme_use("clam")
    except Exception:
        for fallback in ("alt", "default", "classic"):
            try:
                style.theme_use(fallback)
                break
            except Exception:
                continue

    # 1. Resolve fonts + ensure named fonts
    fam = resolve_font_family()
    ensure_named_fonts(fam)

    BASE_FONT = FONT_NAME_BASE
    BOLD_FONT = FONT_NAME_BASE_BOLD
    HEADING_FONT = FONT_NAME_HEADING
    SECTION_HEADING_FONT = FONT_NAME_SECTION_HEADING

    # ================================================================================================
    # A. LABEL MATRIX — PRIMARY/SECONDARY × NORMAL/BOLD
    # ================================================================================================
    LABEL_MATRIX = [
        ("Primary.Normal.TLabel",   GUI_COLOUR_BG_PRIMARY,   BASE_FONT, TEXT_COLOUR_SECONDARY),
        ("Secondary.Normal.TLabel", GUI_COLOUR_BG_SECONDARY, BASE_FONT, TEXT_COLOUR_SECONDARY),
        ("Primary.Bold.TLabel",     GUI_COLOUR_BG_PRIMARY,   BOLD_FONT, TEXT_COLOUR_SECONDARY),
        ("Secondary.Bold.TLabel",   GUI_COLOUR_BG_SECONDARY, BOLD_FONT, TEXT_COLOUR_SECONDARY),
    ]

    for style_name, bg, font, fg in LABEL_MATRIX:
        style.configure(
            style_name,
            **clean_style_dict(
                build_style(
                    base={
                        "background": bg,
                        "foreground": fg,
                        "fieldbackground": None,
                        "arrowcolor": None,
                        "selectforeground": None,
                        "selectbackground": None,
                        "troughcolor": None,
                        "lightcolor": None,
                        "darkcolor": None,
                        "bordercolor": None,
                        "font": font,
                        "padding": None,
                        "borderwidth": None,
                        "relief": None,
                    }
                )
            ),
        )

    # ================================================================================================
    # B. SEMANTIC STATUS LABELS — PRIMARY/SECONDARY × NORMAL/BOLD × SUCCESS/WARNING/ERROR
    # ================================================================================================
    STATUS_MATRIX = [
        # ------------------------- SUCCESS -------------------------
        ("Primary.Success.Normal.TLabel",     GUI_COLOUR_BG_PRIMARY,   BASE_FONT, GUI_COLOUR_STATUS_SUCCESS),
        ("Primary.Success.Bold.TLabel",       GUI_COLOUR_BG_PRIMARY,   BOLD_FONT, GUI_COLOUR_STATUS_SUCCESS),
        ("Secondary.Success.Normal.TLabel",   GUI_COLOUR_BG_SECONDARY, BASE_FONT, GUI_COLOUR_STATUS_SUCCESS),
        ("Secondary.Success.Bold.TLabel",     GUI_COLOUR_BG_SECONDARY, BOLD_FONT, GUI_COLOUR_STATUS_SUCCESS),

        # ------------------------- WARNING -------------------------
        ("Primary.Warning.Normal.TLabel",     GUI_COLOUR_BG_PRIMARY,   BASE_FONT, GUI_COLOUR_STATUS_WARNING),
        ("Primary.Warning.Bold.TLabel",       GUI_COLOUR_BG_PRIMARY,   BOLD_FONT, GUI_COLOUR_STATUS_WARNING),
        ("Secondary.Warning.Normal.TLabel",   GUI_COLOUR_BG_SECONDARY, BASE_FONT, GUI_COLOUR_STATUS_WARNING),
        ("Secondary.Warning.Bold.TLabel",     GUI_COLOUR_BG_SECONDARY, BOLD_FONT, GUI_COLOUR_STATUS_WARNING),

        # ------------------------- ERROR ---------------------------
        ("Primary.Error.Normal.TLabel",       GUI_COLOUR_BG_PRIMARY,   BASE_FONT, GUI_COLOUR_STATUS_ERROR),
        ("Primary.Error.Bold.TLabel",         GUI_COLOUR_BG_PRIMARY,   BOLD_FONT, GUI_COLOUR_STATUS_ERROR),
        ("Secondary.Error.Normal.TLabel",     GUI_COLOUR_BG_SECONDARY, BASE_FONT, GUI_COLOUR_STATUS_ERROR),
        ("Secondary.Error.Bold.TLabel",       GUI_COLOUR_BG_SECONDARY, BOLD_FONT, GUI_COLOUR_STATUS_ERROR),
    ]

    for style_name, bg, font, fg in STATUS_MATRIX:
        style.configure(
            style_name,
            **clean_style_dict(
                build_style(
                    base={
                        "background": bg,
                        "foreground": fg,
                        "font": font,
                        "padding": None,
                        "borderwidth": None,
                        "relief": None,
                        "fieldbackground": None,
                        "arrowcolor": None,
                        "selectforeground": None,
                        "selectbackground": None,
                        "troughcolor": None,
                        "lightcolor": None,
                        "darkcolor": None,
                        "bordercolor": None,
                    }
                )
            ),
    )


    # ================================================================================================
    # C. CARD LABEL — PRIMARY/SECONDARY × NORMAL/BOLD
    # ================================================================================================
    CARD_LABEL_MATRIX = [
        ("Primary.Card.Normal.TLabel",     GUI_COLOUR_BG_PRIMARY,   BASE_FONT, TEXT_COLOUR_SECONDARY),
        ("Primary.Card.Bold.TLabel",       GUI_COLOUR_BG_PRIMARY,   BOLD_FONT, TEXT_COLOUR_SECONDARY),
        ("Secondary.Card.Normal.TLabel",   GUI_COLOUR_BG_SECONDARY, BASE_FONT, TEXT_COLOUR_SECONDARY),
        ("Secondary.Card.Bold.TLabel",     GUI_COLOUR_BG_SECONDARY, BOLD_FONT, TEXT_COLOUR_SECONDARY),
    ]

    for style_name, bg, font, fg in CARD_LABEL_MATRIX:
        style.configure(
            style_name,
            **clean_style_dict(
                build_style(
                    base={
                        "background": bg,
                        "foreground": fg,
                        "font": font,
                        "padding": None,
                        "borderwidth": None,
                        "relief": None,
                        "fieldbackground": None,
                        "arrowcolor": None,
                        "selectforeground": None,
                        "selectbackground": None,
                        "troughcolor": None,
                        "lightcolor": None,
                        "darkcolor": None,
                        "bordercolor": None,
                    }
                )
            ),
        )


    # ================================================================================================
    # D. WINDOW HEADING — PRIMARY/SECONDARY × NORMAL/BOLD
    # ================================================================================================
    WINDOW_HEADING_MATRIX = [
        # Primary surface
        ("Primary.WindowHeading.Normal.TLabel", GUI_COLOUR_BG_PRIMARY,   TEXT_COLOUR_PRIMARY, HEADING_FONT),
        ("Primary.WindowHeading.Bold.TLabel",   GUI_COLOUR_BG_PRIMARY,   TEXT_COLOUR_PRIMARY, FONT_NAME_BASE_BOLD),

        # Secondary surface
        ("Secondary.WindowHeading.Normal.TLabel", GUI_COLOUR_BG_SECONDARY, TEXT_COLOUR_PRIMARY, HEADING_FONT),
        ("Secondary.WindowHeading.Bold.TLabel",   GUI_COLOUR_BG_SECONDARY, TEXT_COLOUR_PRIMARY, FONT_NAME_BASE_BOLD),
    ]

    for style_name, bg, fg, font in WINDOW_HEADING_MATRIX:
        style.configure(
            style_name,
            **clean_style_dict(
                build_style(
                    base={
                        "background": bg,
                        "foreground": fg,
                        "font": font,
                        "padding": (0, 0, 0, SECTION_SPACING),
                        "borderwidth": None,
                        "relief": None,
                        "fieldbackground": None,
                        "arrowcolor": None,
                        "selectforeground": None,
                        "selectbackground": None,
                        "troughcolor": None,
                        "lightcolor": None,
                        "darkcolor": None,
                        "bordercolor": None,
                    }
                )
            ),
        )


    # ================================================================================================
    # E. PAGE-LEVEL HEADINGS — PRIMARY/SECONDARY × NORMAL/BOLD
    # ================================================================================================
    PAGE_HEADING_MATRIX = [
        # Primary surface
        ("Primary.Heading.Normal.TLabel",   GUI_COLOUR_BG_PRIMARY,   TEXT_COLOUR_PRIMARY,   SECTION_HEADING_FONT),
        ("Primary.Heading.Bold.TLabel",     GUI_COLOUR_BG_PRIMARY,   TEXT_COLOUR_PRIMARY,   FONT_NAME_BASE_BOLD),

        # Secondary surface
        ("Secondary.Heading.Normal.TLabel", GUI_COLOUR_BG_SECONDARY, TEXT_COLOUR_SECONDARY, SECTION_HEADING_FONT),
        ("Secondary.Heading.Bold.TLabel",   GUI_COLOUR_BG_SECONDARY, TEXT_COLOUR_SECONDARY, FONT_NAME_BASE_BOLD),
    ]

    for style_name, bg, fg, font in PAGE_HEADING_MATRIX:
        style.configure(
            style_name,
            **clean_style_dict(
                build_style(
                    base={
                        "background": bg,
                        "foreground": fg,
                        "font": font,
                        "padding": (0, 0, 0, SECTION_SPACING),
                        "borderwidth": None,
                        "relief": None,
                        "fieldbackground": None,
                        "arrowcolor": None,
                        "selectforeground": None,
                        "selectbackground": None,
                        "troughcolor": None,
                        "lightcolor": None,
                        "darkcolor": None,
                        "bordercolor": None,
                    }
                )
            ),
        )


    # ================================================================================================
    # F. SECTION-LEVEL HEADINGS — PRIMARY/SECONDARY × NORMAL/BOLD
    # ================================================================================================
    SECTION_HEADING_MATRIX = [
        # Primary surface
        ("Primary.SectionHeading.Normal.TLabel",   GUI_COLOUR_BG_PRIMARY,   TEXT_COLOUR_PRIMARY,   SECTION_HEADING_FONT),
        ("Primary.SectionHeading.Bold.TLabel",     GUI_COLOUR_BG_PRIMARY,   TEXT_COLOUR_PRIMARY,   FONT_NAME_BASE_BOLD),

        # Secondary surface
        ("Secondary.SectionHeading.Normal.TLabel", GUI_COLOUR_BG_SECONDARY, TEXT_COLOUR_SECONDARY, SECTION_HEADING_FONT),
        ("Secondary.SectionHeading.Bold.TLabel",   GUI_COLOUR_BG_SECONDARY, TEXT_COLOUR_SECONDARY, FONT_NAME_BASE_BOLD),
    ]

    for style_name, bg, fg, font in SECTION_HEADING_MATRIX:
        style.configure(
            style_name,
            **clean_style_dict(
                build_style(
                    base={
                        "background": bg,
                        "foreground": fg,
                        "font": font,
                        "padding": (0, 0, 0, SECTION_SPACING),
                        "borderwidth": None,
                        "relief": None,
                        "fieldbackground": None,
                        "arrowcolor": None,
                        "selectforeground": None,
                        "selectbackground": None,
                        "troughcolor": None,
                        "lightcolor": None,
                        "darkcolor": None,
                        "bordercolor": None,
                    }
                )
            ),
        )


    # ================================================================================================
    # G. GLOBAL DEFAULT FRAME — TFrame
    # ================================================================================================
    # This overrides the system-default beige/grey TFrame background from the "clam" theme.
    # Any frame using style="TFrame" (including structural containers, spacers, and root-level
    # defaults) will now inherit the proper primary surface background.
    style.configure(
        "TFrame",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": None,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": None,
                    "padding": None,
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )


    # ================================================================================================
    # H. BASE BUTTON (TButton)
    # ================================================================================================
    style.configure(
        "TButton",
        **clean_style_dict(
            build_style(
                base={
                    "background": None,
                    "foreground": None,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": BASE_FONT,
                    "padding": (6, 4),
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )


    # ================================================================================================
    # I. PRIMARY BUTTON — Brand Blue
    # ================================================================================================
    style.configure(
        "Primary.TButton",
        **clean_style_dict(
            build_style(
                base={
                    "background": BUTTON_PRIMARY_BG,
                    "foreground": BUTTON_PRIMARY_TEXT,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": BUTTON_PRIMARY_TEXT,
                    "selectbackground": BUTTON_PRIMARY_BG,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": BASE_FONT,
                    "padding": (10, 6),
                    "borderwidth": 1,
                    "relief": "flat",
                }
            )
        ),
    )

    style.map(
        "Primary.TButton",
        background=[
            ("disabled", BUTTON_PRIMARY_DISABLED),
            ("pressed", BUTTON_PRIMARY_ACTIVE),
            ("active", BUTTON_PRIMARY_HOVER),
            ("!disabled", BUTTON_PRIMARY_BG),
        ],
        foreground=[
            ("disabled", TEXT_COLOUR_DISABLED),
            ("!disabled", BUTTON_PRIMARY_TEXT),
        ],
    )


    # ================================================================================================
    # J. SECONDARY BUTTON — Neutral
    # ================================================================================================
    style.configure(
        "Secondary.TButton",
        **clean_style_dict(
            build_style(
                base={
                    "background": BUTTON_SECONDARY_BG,
                    "foreground": BUTTON_SECONDARY_TEXT,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": BUTTON_SECONDARY_TEXT,
                    "selectbackground": BUTTON_SECONDARY_BG,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": BASE_FONT,
                    "padding": (10, 6),
                    "borderwidth": 1,
                    "relief": "flat",
                }
            )
        ),
    )

    style.map(
        "Secondary.TButton",
        background=[
            ("disabled", BUTTON_SECONDARY_DISABLED),
            ("pressed", BUTTON_SECONDARY_ACTIVE),
            ("active", BUTTON_SECONDARY_HOVER),
            ("!disabled", BUTTON_SECONDARY_BG),
        ],
        foreground=[
            ("disabled", TEXT_COLOUR_DISABLED),
            ("!disabled", BUTTON_SECONDARY_TEXT),
        ],
    )


    # ================================================================================================
    # K. SUCCESS BUTTON — Green
    # ================================================================================================
    style.configure(
        "Success.TButton",
        **clean_style_dict(
            build_style(
                base={
                    "background": BUTTON_SUCCESS_BG,
                    "foreground": BUTTON_SUCCESS_TEXT,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": BUTTON_SUCCESS_TEXT,
                    "selectbackground": BUTTON_SUCCESS_BG,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": BASE_FONT,
                    "padding": (10, 6),
                    "borderwidth": 1,
                    "relief": "flat",
                }
            )
        ),
    )

    style.map(
        "Success.TButton",
        background=[
            ("pressed", BUTTON_SUCCESS_ACTIVE),
            ("active", BUTTON_SUCCESS_HOVER),
            ("!disabled", BUTTON_SUCCESS_BG),
        ],
        foreground=[
            ("disabled", TEXT_COLOUR_DISABLED),
            ("!disabled", BUTTON_SUCCESS_TEXT),
        ],
    )


    # ================================================================================================
    # L. WARNING BUTTON — Amber
    # ================================================================================================
    style.configure(
        "Warning.TButton",
        **clean_style_dict(
            build_style(
                base={
                    "background": BUTTON_WARNING_BG,
                    "foreground": BUTTON_WARNING_TEXT,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": BUTTON_WARNING_TEXT,
                    "selectbackground": BUTTON_WARNING_BG,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": BASE_FONT,
                    "padding": (10, 6),
                    "borderwidth": 1,
                    "relief": "flat",
                }
            )
        ),
    )

    style.map(
        "Warning.TButton",
        background=[
            ("pressed", BUTTON_WARNING_ACTIVE),
            ("active", BUTTON_WARNING_HOVER),
            ("!disabled", BUTTON_WARNING_BG),
        ],
        foreground=[
            ("disabled", TEXT_COLOUR_DISABLED),
            ("!disabled", BUTTON_WARNING_TEXT),
        ],
    )


    # ================================================================================================
    # M. DANGER BUTTON — Red
    # ================================================================================================
    style.configure(
        "Danger.TButton",
        **clean_style_dict(
            build_style(
                base={
                    "background": BUTTON_DANGER_BG,
                    "foreground": BUTTON_DANGER_TEXT,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": BUTTON_DANGER_TEXT,
                    "selectbackground": BUTTON_DANGER_BG,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": BASE_FONT,
                    "padding": (10, 6),
                    "borderwidth": 1,
                    "relief": "flat",
                }
            )
        ),
    )

    style.map(
        "Danger.TButton",
        background=[
            ("pressed", BUTTON_DANGER_ACTIVE),
            ("active", BUTTON_DANGER_HOVER),
            ("!disabled", BUTTON_DANGER_BG),
        ],
        foreground=[
            ("disabled", TEXT_COLOUR_DISABLED),
            ("!disabled", BUTTON_DANGER_TEXT),
        ],
    )


    # ================================================================================================
    # N. TENTRY (Single-Line Input)
    # ================================================================================================
    style.configure(
        "TEntry",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_INPUT,
                    "foreground": TEXT_COLOUR_SECONDARY,
                    "fieldbackground": GUI_COLOUR_BG_INPUT,
                    "arrowcolor": None,
                    "selectforeground": TEXT_COLOUR_SECONDARY,
                    "selectbackground": GUI_COLOUR_BG_SECONDARY,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": GUI_COLOUR_BORDER,
                    "font": BASE_FONT,
                    "padding": None,
                    "borderwidth": 1,
                    "relief": "solid",
                }
            )
        ),
    )


    # ================================================================================================
    # O. TCOMBOBOX (Dropdown)
    # ================================================================================================
    style.configure(
        "TCombobox",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_INPUT,
                    "foreground": TEXT_COLOUR_SECONDARY,
                    "fieldbackground": GUI_COLOUR_BG_INPUT,
                    "arrowcolor": TEXT_COLOUR_PRIMARY,
                    "selectforeground": TEXT_COLOUR_SECONDARY,
                    "selectbackground": GUI_COLOUR_BG_SECONDARY,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": GUI_COLOUR_BORDER,
                    "font": BASE_FONT,
                    "padding": None,
                    "borderwidth": 1,
                    "relief": "solid",
                }
            )
        ),
    )

    style.map(
        "TCombobox",
        fieldbackground=[
            ("readonly", GUI_COLOUR_BG_INPUT),
            ("active", GUI_COLOUR_BG_INPUT),
            ("pressed", GUI_COLOUR_BG_INPUT),
            ("focus", GUI_COLOUR_BG_INPUT),
            ("!disabled", GUI_COLOUR_BG_INPUT),
        ],
        background=[
            ("readonly", GUI_COLOUR_BG_INPUT),
            ("active", GUI_COLOUR_BG_INPUT),
            ("pressed", GUI_COLOUR_BG_INPUT),
            ("focus", GUI_COLOUR_BG_INPUT),
            ("!disabled", GUI_COLOUR_BG_INPUT),
        ],
        foreground=[
            ("disabled", TEXT_COLOUR_DISABLED),
            ("!disabled", TEXT_COLOUR_SECONDARY),
        ],
        arrowcolor=[
            ("disabled", GUI_COLOUR_BG_DISABLED),
            ("active", TEXT_COLOUR_PRIMARY),
            ("pressed", TEXT_COLOUR_PRIMARY),
            ("!disabled", TEXT_COLOUR_PRIMARY),
        ],
    )


    # ================================================================================================
    # P. CHECKBUTTON
    # ================================================================================================
    style.configure(
        "TCheckbutton",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": TEXT_COLOUR_SECONDARY,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": BASE_FONT,
                    "padding": None,
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )


    # ================================================================================================
    # Q. RADIOBUTTON
    # ================================================================================================
    style.configure(
        "TRadiobutton",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": TEXT_COLOUR_SECONDARY,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": BASE_FONT,
                    "padding": None,
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )


    # ================================================================================================
    # R. NOTEBOOK + TABS
    # ================================================================================================
    style.configure(
        "TNotebook",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": None,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": BASE_FONT,
                    "padding": None,
                    "borderwidth": 0,
                    "relief": None,
                }
            )
        ),
    )

    style.configure(
        "TNotebook.Tab",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_SECONDARY,
                    "foreground": TEXT_COLOUR_SECONDARY,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": TEXT_COLOUR_PRIMARY,
                    "selectbackground": GUI_COLOUR_BG_PRIMARY,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": BASE_FONT,
                    "padding": (10, 6),
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )

    style.map(
        "TNotebook.Tab",
        background=[("selected", GUI_COLOUR_BG_PRIMARY)],
        foreground=[("selected", TEXT_COLOUR_PRIMARY)],
    )


    # ================================================================================================
    # S. TREEVIEW + HEADINGS
    # ================================================================================================
    style.configure(
        "Treeview",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_SECONDARY,
                    "foreground": TEXT_COLOUR_SECONDARY,
                    "fieldbackground": GUI_COLOUR_BG_SECONDARY,
                    "arrowcolor": None,
                    "selectforeground": TEXT_COLOUR_SECONDARY,
                    "selectbackground": GUI_COLOUR_ACCENT_LIGHT,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": GUI_COLOUR_BORDER,
                    "font": BASE_FONT,
                    "padding": None,
                    "borderwidth": 1,
                    "relief": "solid",
                }
            )
        ),
    )

    style.configure(
        "Treeview.Heading",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": TEXT_COLOUR_PRIMARY,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": TEXT_COLOUR_PRIMARY,
                    "selectbackground": GUI_COLOUR_BG_PRIMARY,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": GUI_COLOUR_BORDER,
                    "font": SECTION_HEADING_FONT,
                    "padding": None,
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )


    # ================================================================================================
    # T. MENU BUTTON
    # ================================================================================================
    style.configure(
        "TMenubutton",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": TEXT_COLOUR_SECONDARY,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": BASE_FONT,
                    "padding": None,
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )


    # ================================================================================================
    # U. PROGRESS BAR
    # ================================================================================================
    style.configure(
        "Horizontal.TProgressbar",
        **clean_style_dict(
            build_style(
                base={
                    "background": DEFAULT_PROGRESS_COLOUR,
                    "foreground": DEFAULT_PROGRESS_COLOUR,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": GUI_COLOUR_BG_SECONDARY,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": None,
                    "padding": None,
                    "borderwidth": 0,
                    "relief": "flat",
                }
            )
        ),
    )


    # ================================================================================================
    # V. SECTION FRAMES — OUTER + BODY
    # ================================================================================================
    style.configure(
        "SectionOuter.TFrame",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": None,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": None,
                    "padding": FRAME_PADDING,
                    "borderwidth": 0,
                    "relief": "flat",
                }
            )
        ),
    )

    style.configure(
        "SectionBody.TFrame",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_SECONDARY,
                    "foreground": None,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": GUI_COLOUR_BORDER,
                    "font": None,
                    "padding": FRAME_PADDING,
                    "borderwidth": 1,
                    "relief": "solid",
                }
            )
        ),
    )


    # ================================================================================================
    # W. CARD FRAMES (Card.TFrame + Card.TRadiobutton)
    # ================================================================================================
    style.configure(
        "Card.TFrame",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_SECONDARY,
                    "foreground": None,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": GUI_COLOUR_BORDER,
                    "font": None,
                    "padding": FRAME_PADDING,
                    "borderwidth": 1,
                    "relief": "solid",
                }
            )
        ),
    )

    style.configure(
        "Card.TRadiobutton",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_SECONDARY,
                    "foreground": TEXT_COLOUR_SECONDARY,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": BASE_FONT,
                    "padding": None,
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )


    # ================================================================================================
    # X. TOOLBAR DIVIDER
    # ================================================================================================
    style.configure(
        "ToolbarDivider.TFrame",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_DIVIDER,
                    "foreground": None,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": None,
                    "padding": None,
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )


    # ================================================================================================
    # END OF STYLE ENGINE
    # ================================================================================================
    logger.info("[G01b] ttk style configuration completed successfully.")


# ====================================================================================================
# 6. SELF-TEST (RUN ONLY WHEN EXECUTING THIS FILE DIRECTLY)
# ----------------------------------------------------------------------------------------------------
# Provides a quick verification that:
#   • The theme loads without raising Tcl errors
#   • All style blocks pass through clean_style_dict correctly
#   • Named fonts are created and usable
#   
# This block is not executed when imported by other modules.
# ====================================================================================================
def run_self_test() -> None:
    """
    Run a minimal non-visual validation of the style engine.

    This function:
        • Creates a hidden Tk root window.
        • Instantiates a ttk.Style and applies configure_ttk_styles(...).
        • Logs the presence/absence of key styles and their font settings.
        • Destroys the root window on completion.

    It is intended for developer diagnostics only and is safe to call
    repeatedly during development; it should not be used in production
    runtime code.
    """
    logger.info("=== G01b_style_engine.py — Self-Test Start ===")

    # Create a headless Tk root to allow style creation safely
    try:
        root = tk.Tk()  # type: ignore[name-defined]
        root.withdraw()     # Hide the root window
    except Exception as e:  # noqa: BLE001
        logger.exception("[G01b] Failed to initialise Tk for self-test: %s", e)
        return

    try:
        style = ttk.Style()  # type: ignore[name-defined]
        configure_ttk_styles(style)

        logger.debug("[G01b][DEBUG] ----- Diagnostics start -----")
        try:
            logger.debug("[G01b][DEBUG] Active theme name: %s", style.theme_use())
        except Exception:  # noqa: BLE001
            logger.debug("[G01b][DEBUG] Could not query active theme name.")

        # Market
        key_styles = [
            # --- LABEL MATRIX (Primary/Secondary × Normal/Bold) ---
            "Primary.Normal.TLabel",
            "Primary.Bold.TLabel",
            "Secondary.Normal.TLabel",
            "Secondary.Bold.TLabel",

            # --- STATUS LABELS (Primary/Secondary × Normal/Bold × Success/Warning/Error) ---
            "Primary.Success.Normal.TLabel",
            "Primary.Success.Bold.TLabel",
            "Secondary.Success.Normal.TLabel",
            "Secondary.Success.Bold.TLabel",

            "Primary.Warning.Normal.TLabel",
            "Primary.Warning.Bold.TLabel",
            "Secondary.Warning.Normal.TLabel",
            "Secondary.Warning.Bold.TLabel",

            "Primary.Error.Normal.TLabel",
            "Primary.Error.Bold.TLabel",
            "Secondary.Error.Normal.TLabel",
            "Secondary.Error.Bold.TLabel",

            # --- CARD LABELS (Primary/Secondary × Normal/Bold) ---
            "Primary.Card.Normal.TLabel",
            "Primary.Card.Bold.TLabel",
            "Secondary.Card.Normal.TLabel",
            "Secondary.Card.Bold.TLabel",

            # --- WINDOW HEADINGS (Primary/Secondary × Normal/Bold) ---
            "Primary.WindowHeading.Normal.TLabel",
            "Primary.WindowHeading.Bold.TLabel",
            "Secondary.WindowHeading.Normal.TLabel",
            "Secondary.WindowHeading.Bold.TLabel",

            # --- PAGE HEADINGS (Primary/Secondary × Normal/Bold) ---
            "Primary.Heading.Normal.TLabel",
            "Primary.Heading.Bold.TLabel",
            "Secondary.Heading.Normal.TLabel",
            "Secondary.Heading.Bold.TLabel",

            # --- SECTION HEADINGS (Primary/Secondary × Normal/Bold) ---
            "Primary.SectionHeading.Normal.TLabel",
            "Primary.SectionHeading.Bold.TLabel",
            "Secondary.SectionHeading.Normal.TLabel",
            "Secondary.SectionHeading.Bold.TLabel",

            # --- BUTTONS ---
            "TButton",
            "Primary.TButton",
            "Secondary.TButton",
            "Success.TButton",
            "Warning.TButton",
            "Danger.TButton",

            # --- INPUTS ---
            "TEntry",
            "TCombobox",
            "TCheckbutton",
            "TRadiobutton",

            # --- NOTEBOOK ---
            "TNotebook",
            "TNotebook.Tab",

            # --- TREEVIEW ---
            "Treeview",
            "Treeview.Heading",

            # --- MENU BUTTON ---
            "TMenubutton",

            # --- PROGRESSBAR ---
            "Horizontal.TProgressbar",

            # --- STRUCTURAL FRAMES ---
            "TFrame",

            # --- SECTIONS ---
            "SectionOuter.TFrame",
            "SectionBody.TFrame",

            # --- CARDS ---
            "Card.TFrame",
            "Card.TRadiobutton",

            # --- STRUCTURAL ---
            "ToolbarDivider.TFrame",
        ]

        for name in key_styles:
            try:
                style.configure(name)
                defined = True
            except Exception:  # noqa: BLE001
                defined = False
            logger.debug("[G01b][DEBUG] Style '%s' defined: %s", name, defined)

        # Font descriptor for SectionHeading
        section_font_desc = style.lookup("SectionHeading.TLabel", "font")
        logger.debug(
            "[G01b][DEBUG] SectionHeading.TLabel raw font lookup: %r",
            section_font_desc,
        )

        # Try resolving as named font (informational only)
        try:
            f_obj = tkFont.nametofont(section_font_desc)  # type: ignore[name-defined]
            logger.debug(
                "[G01b][DEBUG] SectionHeading named font resolved -> "
                "family=%s size=%s weight=%s",
                f_obj.cget("family"),
                f_obj.cget("size"),
                f_obj.cget("weight"),
            )
        except Exception:
            logger.debug(
                "[G01b][DEBUG] SectionHeading font is not a named Tk font "
                "(descriptor=%r); this is acceptable if the style uses a "
                "direct font descriptor.",
                section_font_desc,
            )

        logger.debug(
            "[G01b][DEBUG] Using font family preference: %s",
            resolve_font_family(),
        )
        logger.debug("[G01b][DEBUG] ----- Diagnostics end -----")

    except Exception as e:  # noqa: BLE001
        logger.exception("[G01b] ERROR applying theme during self-test: %s", e)
        raise
    finally:
        root.destroy()

    logger.info("[G01b] Theme applied successfully for self-test.")
    logger.info("=== G01b_style_engine.py — Self-Test Complete ===")


if __name__ == "__main__":
    # Initialize logging so we can see the test output
    init_logging()

    print("=" * 80)
    print("G01b_style_engine.py — Self-Test")
    print("=" * 80)

    try:
        run_self_test()
        print("\n✅ Self-test PASSED - All ttk styles configured successfully")
        print(f"   • {len(STYLE_BLOCKS)} style blocks defined:")
        for style_name, desc in STYLE_BLOCKS.items():
            print(f"     - {style_name}: {desc}")
    except Exception as e:
        print(f"\n❌ Self-test FAILED: {e}")
        raise

    print("=" * 80)
