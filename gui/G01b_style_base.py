# ====================================================================================================
# G01b_style_base.py
# ----------------------------------------------------------------------------------------------------
# Shared utilities module for the GUI Framework design system.
#
# Purpose:
#   - Provide type aliases for type-safe style resolution parameters.
#   - Resolve the active font family from the font family cascade.
#   - Create and cache Tk named fonts for text styling.
#   - Provide colour utilities (reverse lookup from hex to semantic names).
#   - Provide a shared cache-key builder for all G01c–G01f resolvers.
#   - Re-export commonly needed constants and registries from G01a.
#
# Architecture:
#   - G01a  → design tokens (pure data, all colours + typography)
#   - G01b  → shared internal engine (fonts, colour classification, cache keys)
#   - G01c–f → domain-specific style resolvers using G01b utilities
#
# This module contains:
#   • NO hex values
#   • NO widget creation
#   • NO ttk.Style registration
#   • NO design tokens (all come from G01a)
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-02
# Project:      GUI Framework v1.0
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
from gui.G00a_gui_packages import tkFont, ttk
from gui.G01a_style_config import (
    GUI_FONT_FAMILY,
    FONT_SIZES,
    GUI_PRIMARY,
    GUI_SECONDARY,
    GUI_SUCCESS,
    GUI_WARNING,
    GUI_ERROR,
    GUI_TEXT,
    COLOUR_FAMILIES,
    SHADE_NAMES,
    TEXT_SHADE_NAMES,
    BORDER_WEIGHTS,
    SPACING_SCALE,
    # Re-exports for G01f (control styles)
    TEXT_COLOUR_GREY,
    TEXT_COLOUR_WHITE,
    CONTROL_INDICATOR_GAP,
)


# ====================================================================================================
# 3. TYPE ALIASES
# ----------------------------------------------------------------------------------------------------
# G01b is the SINGLE SOURCE OF TRUTH for all Literal type aliases in the GUI framework.
# All other modules (G01c-f, G02a, G03) must import these types from G01b.
# ====================================================================================================

# --- Shade and size types ---
ShadeType = Literal["LIGHT", "MID", "DARK", "XDARK"]
TextShadeType = Literal["BLACK", "WHITE", "GREY", "PRIMARY", "SECONDARY"]
SizeType = Literal["DISPLAY", "HEADING", "TITLE", "BODY", "SMALL"]

# --- Colour family types ---
ColourFamily = dict[str, str]
ColourFamilyName = Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR", "TEXT"]

# --- Border and spacing types ---
BorderWeightType = Literal["NONE", "THIN", "MEDIUM", "THICK"]
SpacingType = Literal["XS", "SM", "MD", "LG", "XL", "XXL"]

# --- Container types (used by G01d, G02a, G03b) ---
ContainerRoleType = Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR"]
ContainerKindType = Literal["SURFACE", "CARD", "PANEL", "SECTION"]

# --- Input types (used by G01e, G02a) ---
InputControlType = Literal["ENTRY", "COMBOBOX", "SPINBOX"]
INPUT_CONTROLS: tuple[InputControlType, ...] = ("ENTRY", "COMBOBOX", "SPINBOX")

InputRoleType = Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR"]
INPUT_ROLES: tuple[InputRoleType, ...] = ("PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR")

# --- Control types (used by G01f, G02a) ---
ControlWidgetType = Literal["BUTTON", "CHECKBOX", "RADIO", "SWITCH"]
CONTROL_WIDGETS: tuple[ControlWidgetType, ...] = ("BUTTON", "CHECKBOX", "RADIO", "SWITCH")

ControlVariantType = Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR"]
CONTROL_VARIANTS: tuple[ControlVariantType, ...] = ("PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR")


# ====================================================================================================
# 4. CONSTANTS
# ----------------------------------------------------------------------------------------------------

FONT_FAMILY_FALLBACK: str = "Arial"
TEXT_COLOURS = GUI_TEXT  # Alias required by spec


# ====================================================================================================
# 5. FONT RESOLUTION & FONT CACHE
# ----------------------------------------------------------------------------------------------------

FONT_FAMILY_RESOLVED: str | None = None
FONT_CACHE: dict[str, tkFont.Font] = {}


def resolve_font_family() -> str:
    """
    Description:
        Resolve the first available font family from GUI_FONT_FAMILY.
        Falls back to FONT_FAMILY_FALLBACK if no preferred font is present.

    Returns:
        str: Active font family name.

    Notes:
        - Requires an existing Tk root.
        - Cached after first resolution.
    """
    global FONT_FAMILY_RESOLVED

    if FONT_FAMILY_RESOLVED is not None:
        return FONT_FAMILY_RESOLVED

    try:
        available = set(tkFont.families())
    except Exception as exc:
        logger.warning(f"[G01b] Unable to query font families: {exc}")
        FONT_FAMILY_RESOLVED = FONT_FAMILY_FALLBACK
        return FONT_FAMILY_RESOLVED

    for name in GUI_FONT_FAMILY:
        if name in available:
            FONT_FAMILY_RESOLVED = name
            return name

    FONT_FAMILY_RESOLVED = FONT_FAMILY_FALLBACK
    return FONT_FAMILY_RESOLVED


def make_font_key(
    size: str = "BODY",
    bold: bool = False,
    underline: bool = False,
    italic: bool = False,
) -> str:
    """
    Description:
        Construct a deterministic key for naming Tk fonts. This ensures that
        fonts with identical configuration share the same cache entry.

    Args:
        size (str):
            The size token ("DISPLAY", "HEADING", "TITLE", "BODY", "SMALL").
        bold (bool):
            Whether the font is bold.
        underline (bool):
            Whether the font has an underline.
        italic (bool):
            Whether the font is italic.

    Returns:
        str:
            A canonical font key, e.g. "Font_BODY", "Font_TITLE_BU".

    Raises:
        None.

    Notes:
        - Used by resolve_text_font() to ensure caching correctness.
        - Keys are human-readable and stable across sessions.
    """
    size_token = size.upper()
    flags = "".join(
        flag for cond, flag in [(bold, "B"), (underline, "U"), (italic, "I")] if cond
    )
    return f"Font_{size_token}" if not flags else f"Font_{size_token}_{flags}"


def create_named_font(
    key: str,
    size: str = "BODY",
    bold: bool = False,
    underline: bool = False,
    italic: bool = False,
) -> tkFont.Font:
    """
    Description:
        Create a Tk named font using the resolved font family and the pixel
        sizes defined in FONT_SIZES.

    Args:
        key (str):
            The name to assign to the Tk named font.
        size (str):
            A size token from FONT_SIZES (e.g., "BODY", "TITLE").
        bold (bool):
            Whether the font should be rendered in bold weight.
        underline (bool):
            Whether the font should include an underline.
        italic (bool):
            Whether the font should use an italic slant.

    Returns:
        tkFont.Font:
            The created Tk named font instance.

    Raises:
        None.

    Notes:
        - Assumes that a Tk root has already been created.
        - The returned font is registered globally under the specified name.
        - No caching is performed here; caching is handled by resolve_text_font().
    """
    family = resolve_font_family()
    pixel_size = FONT_SIZES.get(size.upper(), FONT_SIZES["BODY"])

    return tkFont.Font(
        name=key,
        family=family,
        size=pixel_size,
        weight="bold" if bold else "normal",
        slant="italic" if italic else "roman",
        underline=underline,
    )


def resolve_text_font(
    size: str = "BODY",
    bold: bool = False,
    underline: bool = False,
    italic: bool = False,
) -> str:
    """
    Description:
        Get or create a Tk named font and return its font key.

    Returns:
        str: Tk font name.
    """
    key = make_font_key(size, bold, underline, italic)

    if key in FONT_CACHE:
        return key

    FONT_CACHE[key] = create_named_font(key, size, bold, underline, italic)
    return key


def get_font_cache_info() -> dict:
    """
    Description:
        Inspect current font cache contents.

    Returns:
        dict: Summary info.
    """
    return {
        "count": len(FONT_CACHE),
        "keys": list(FONT_CACHE.keys()),
        "family": FONT_FAMILY_RESOLVED,
    }


def clear_font_cache() -> None:
    """
    Description:
        Clear both resolved font family and font cache.
    """
    global FONT_FAMILY_RESOLVED
    FONT_FAMILY_RESOLVED = None
    FONT_CACHE.clear()
    logger.debug("[G01b] Font cache cleared")


# ====================================================================================================
# 6. COLOUR UTILITIES
# ----------------------------------------------------------------------------------------------------

def detect_colour_family_name(colour_family: ColourFamily | None) -> str:
    """
    Description:
        Infer the logical family name for a given colour-family dictionary,
        using COLOUR_FAMILIES from G01a.

    Args:
        colour_family:
            A colour family dictionary (e.g., GUI_PRIMARY, GUI_TEXT), or None.

    Returns:
        str:
            The registered family name ("PRIMARY", "SECONDARY", "SUCCESS",
            "WARNING", "ERROR", "TEXT"), or "CUSTOM" if unrecognised,
            or "NONE" if colour_family is None.

    Raises:
        None.

    Notes:
        - This is the single source of truth for family-name detection.
        - G01c, G01d, G01e, G01f should all import this function.
    """
    if colour_family is None:
        return "NONE"

    for family_name, family_dict in COLOUR_FAMILIES.items():
        if family_dict is colour_family:
            return family_name

    return "CUSTOM"


def classify_colour(col: str | None) -> tuple[str, str] | None:
    """
    Description:
        Map a hex colour to (FAMILY, SHADE). Returns ("CUSTOM", value_without_hash)
        if the colour doesn't belong to any family.

    Args:
        col:
            A hex colour string (e.g., "#00A3FE") or None.

    Returns:
        tuple[str, str] | None:
            A tuple of (FAMILY_NAME, SHADE_NAME), or None if col is None.

    Raises:
        None.

    Notes:
        - Returns ("CUSTOM", hex_without_hash) for unrecognised colours.
    """
    if col is None:
        return None

    col = col.strip().upper()
    if not col.startswith("#"):
        col = f"#{col}"

    for fam, shades in COLOUR_FAMILIES.items():
        for shade_name, hex_val in shades.items():
            if hex_val.upper() == col:
                return fam, shade_name

    return "CUSTOM", col.lstrip("#")


def get_colour_family(name: str) -> ColourFamily | None:
    """
    Description:
        Retrieve a colour family dictionary from COLOUR_FAMILIES by name.

    Args:
        name (str):
            The name of the colour family ("PRIMARY", "TEXT", etc.).

    Returns:
        dict | None:
            The corresponding colour family dictionary, or None if not found.

    Raises:
        None.

    Notes:
        - Name lookup is case-insensitive.
        - Returned dictionaries should be treated as read-only.
    """
    return COLOUR_FAMILIES.get(name.upper())


# ====================================================================================================
# 7. SHARED STYLE CACHE KEY BUILDER
# ----------------------------------------------------------------------------------------------------

def build_style_cache_key(category: str, *segments: str) -> str:
    """
    Description:
        Combine a primary category with ordered detail segments to produce
        a deterministic style-cache key used by G01c–G01f.

    Args:
        category (str):
            The top-level key, such as "Text", "Container", "Input".
        *segments (str):
            Any number of additional identifying strings such as family,
            shade, size tokens, or booleans rendered as letters.

    Returns:
        str:
            A stable key in the format "Category_seg1_seg2_...".

    Raises:
        None.

    Notes:
        - Empty strings and None values are ignored.
        - Order of segments is preserved to avoid collisions.
        - All calls across the framework must use this canonical key builder.
    """
    cleaned = [s for s in segments if s not in (None, "")]
    return category if not cleaned else f"{category}_{'_'.join(cleaned)}"


# ====================================================================================================
# 9. PUBLIC API
# ----------------------------------------------------------------------------------------------------

__all__ = [
    # Type aliases - core
    "ShadeType",
    "TextShadeType",
    "SizeType",
    "ColourFamily",
    "ColourFamilyName",
    "BorderWeightType",
    "SpacingType",
    # Type aliases - container (G01d, G02a, G03b)
    "ContainerRoleType",
    "ContainerKindType",
    # Type aliases - input (G01e, G02a)
    "InputControlType",
    "InputRoleType",
    # Type aliases - control (G01f, G02a)
    "ControlWidgetType",
    "ControlVariantType",
    # Value tuples (for iteration)
    "INPUT_CONTROLS",
    "INPUT_ROLES",
    "CONTROL_WIDGETS",
    "CONTROL_VARIANTS",
    # Constants
    "FONT_FAMILY_FALLBACK",
    "TEXT_COLOURS",
    # Font engine
    "resolve_font_family",
    "make_font_key",
    "create_named_font",
    "resolve_text_font",
    "get_font_cache_info",
    "clear_font_cache",
    # Colour utilities
    "detect_colour_family_name",
    "classify_colour",
    "get_colour_family",
    # Shared cache key builder
    "build_style_cache_key",
    # Re-exports from G01a
    "GUI_PRIMARY",
    "GUI_SECONDARY",
    "GUI_SUCCESS",
    "GUI_WARNING",
    "GUI_ERROR",
    "GUI_TEXT",
    "COLOUR_FAMILIES",
    "FONT_SIZES",
    "SHADE_NAMES",
    "TEXT_SHADE_NAMES",
    "BORDER_WEIGHTS",
    "SPACING_SCALE",
    # Re-exports for G01f (control styles)
    "TEXT_COLOUR_GREY",
    "TEXT_COLOUR_WHITE",
    "CONTROL_INDICATOR_GAP",
]


# ====================================================================================================
# 10. SELF-TEST
# ----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    from gui.G00a_gui_packages import tk

    init_logging()
    logger.info("[G01b] Running self-test...")

    root = tk.Tk()
    root.withdraw()

    logger.info("Resolved font family: %s", resolve_font_family())
    logger.info("Font key BODY: %s", resolve_text_font("BODY"))
    logger.info("Font key HEADING/B: %s", resolve_text_font("HEADING", bold=True))

    logger.info("colour classification (PRIMARY MID): %s",
                classify_colour(GUI_PRIMARY["MID"]))
    logger.info("colour classification (TEXT BLACK): %s",
                classify_colour(GUI_TEXT["BLACK"]))

    logger.info("Sample style key: %s",
                build_style_cache_key("Text", "fgPRIMARY", "MID", "BODY", "B"))

    logger.info("[G01b] Self-test complete.")
    root.destroy()