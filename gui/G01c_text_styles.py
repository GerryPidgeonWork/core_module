# ====================================================================================================
# G01c_text_styles.py
# ----------------------------------------------------------------------------------------------------
# Text style resolver for ttk.Label and other text-based widgets.
#
# Purpose:
#   - Provide a parametric, cached text-style engine for the GUI framework.
#   - Turn high-level semantic parameters (family, shade, size, weight)
#     into concrete ttk styles.
#   - Keep ALL text/label styling logic in one place.
#
# Relationships:
#   - G01a_style_config → pure design tokens (colours, typography, spacing).
#   - G01b_style_base   → shared utilities (fonts, colour utilities, cache keys).
#   - G01c_text_styles  → text/label style resolution (THIS MODULE).
#
# Design principles:
#   - Single responsibility: only text/label styles live here.
#   - Parametric generation: one resolver, many styles.
#   - Idempotent caching: repeated calls with the same parameters return
#     the same style name.
#   - No raw hex values: ALL colours come from G01a tokens.
#
# Style naming pattern (via build_style_cache_key in G01b):
#   Text_fg_<FAMILY>_<SHADE>_bg_<FAMILY|NONE>_<SHADE|NONE>_font_<SIZE>_[FLAGS]
#
#   FAMILY values:
#       PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR, TEXT, CUSTOM, NONE
#   SHADE values:
#       LIGHT, MID, DARK, XDARK (or BLACK/WHITE/GREY/PRIMARY/SECONDARY for TEXT family)
#   FLAGS:
#       B, U, I (in any combination), omitted when no flags are set.
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

# --- Remove '' (current working directory) which can shadow installed packages ----------------------
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

# Shared utilities, type aliases, and design tokens from G01b (single source of truth)
from gui.G01b_style_base import (
    # Type aliases
    ShadeType,
    TextShadeType,
    SizeType,
    ColourFamily,
    # Utilities
    SPACING_SCALE,
    resolve_text_font,
    build_style_cache_key,
    detect_colour_family_name,
    # Design tokens (re-exported from G01a)
    GUI_PRIMARY,
    GUI_SECONDARY,
    GUI_SUCCESS,
    GUI_WARNING,
    GUI_ERROR,
    GUI_TEXT,
)


# ====================================================================================================
# 4. TEXT STYLE CACHE
# ----------------------------------------------------------------------------------------------------
# A dedicated cache for storing all resolved ttk text style names.
#
# Purpose:
#   - Ensure idempotent behaviour: repeated calls with identical parameters
#     return the same style name.
#   - Prevent duplicate ttk.Style registrations.
#   - Act as the single source of truth for created text styles.
# ====================================================================================================
TEXT_STYLE_CACHE: dict[str, str] = {}


# ====================================================================================================
# 5. INTERNAL HELPERS
# ----------------------------------------------------------------------------------------------------
# Pure internal utilities supporting text-style resolution.
#
# Purpose:
#   - Perform name construction via build_text_style_name().
#   - DO NOT create ttk styles or modify global state.
#
# Notes:
#   - detect_colour_family_name() is now imported from G01b (single source of truth).
# ====================================================================================================

def build_text_style_name(
    fg_family_name: str,
    fg_shade: str,
    bg_family_name: str,
    bg_shade: str,
    size_token: str,
    bold: bool,
    underline: bool,
    italic: bool,
) -> str:
    """
    Description:
        Construct the canonical text style name using the shared
        build_style_cache_key helper from G01b.

    Args:
        fg_family_name:
            Foreground colour family name (e.g., "PRIMARY", "TEXT").
        fg_shade:
            Foreground shade token (e.g., "MID" for brand families, "BLACK" for TEXT).
        bg_family_name:
            Background colour family name or "NONE".
        bg_shade:
            Background shade token or "NONE".
        size_token:
            Font size token (DISPLAY, HEADING, TITLE, BODY, SMALL).
        bold:
            Whether the style is bold.
        underline:
            Whether the style is underlined.
        italic:
            Whether the style is italic.

    Returns:
        str:
            Deterministic, human-readable style name.

    Raises:
        None.

    Notes:
        - Flags are encoded as a compact suffix (B, I, U), omitted if no flags.
        - Order is always B, I, U for consistency.
    """
    fg_shade = fg_shade.upper()
    bg_shade = bg_shade.upper()
    size_token = size_token.upper()

    flags_list: list[str] = []
    if bold:
        flags_list.append("B")
    if italic:
        flags_list.append("I")
    if underline:
        flags_list.append("U")

    segments: list[str] = [
        "Text",
        f"fg_{fg_family_name}",
        fg_shade,
        f"bg_{bg_family_name}",
        bg_shade,
        f"font_{size_token}",
    ]

    if flags_list:
        segments.append("".join(flags_list))

    return build_style_cache_key(*segments)


# ====================================================================================================
# 6. TEXT STYLE RESOLUTION (PUBLIC API – CORE ENGINE)
# ----------------------------------------------------------------------------------------------------
# The main text-style resolver: resolve_text_style().
#
# Purpose:
#   - Convert high-level semantic parameters (family, shade, size, weight)
#     into concrete ttk text styles.
#   - Apply deterministic naming and idempotent caching.
#   - Register styles with ttk.Style(), including font selection and layout binding.
#
# Notes:
#   - This is the ONLY place that creates ttk styles for text/label widgets.
#   - All concrete styling work lives here (foreground, background, font, padding).
# ====================================================================================================
def resolve_text_style(
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK",
    bg_colour: ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
    size: SizeType = "BODY",
    bold: bool = False,
    underline: bool = False,
    italic: bool = False,
) -> str:
    """
    Description:
        Resolve a complete ttk text style with foreground, background, and font.
        Styles are created lazily and cached by a deterministic, semantic key.

    Args:
        fg_colour:
            Foreground colour family dictionary. Expected values are one of:
            GUI_PRIMARY, GUI_SECONDARY, GUI_SUCCESS, GUI_WARNING, GUI_ERROR, GUI_TEXT.
            If None, defaults to GUI_TEXT for neutral, readable text.
        fg_shade:
            Shade token within the foreground family.
            For PRIMARY/SECONDARY/STATUS: "LIGHT", "MID", "DARK", "XDARK".
            For TEXT: "BLACK", "WHITE", "GREY", "PRIMARY", "SECONDARY".
            Defaults to "BLACK".
        bg_colour:
            Background colour family dictionary. If None, background is inherited
            from the parent widget (no explicit background forced).
        bg_shade:
            Shade token for the background family. Must be provided if bg_colour
            is provided. Must be None if bg_colour is None.
        size:
            Font size token: "DISPLAY", "HEADING", "TITLE", "BODY", "SMALL".
            Defaults to "BODY".
        bold:
            Whether the font weight is bold.
        underline:
            Whether the text is underlined.
        italic:
            Whether the text is italic.

    Returns:
        str:
            The registered ttk style name. This can be used directly:
                ttk.Label(parent, text="Hello", style=style_name)

    Raises:
        KeyError:
            If fg_shade or bg_shade are not valid keys for their respective
            colour families.
        ValueError:
            If bg_shade is provided while bg_colour is None, or vice versa.

    Notes:
        - Default body text uses GUI_TEXT["BLACK"] for neutral, readable text.
        - Use fg_colour=GUI_PRIMARY explicitly when brand-coloured text is desired.
        - Background inheritance (bg_colour=None) is recommended for most labels.
        - Font resolution is delegated to resolve_text_font() in G01b.
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("———[G01c DEBUG START]———————————————————————————")
        logger.debug("INPUT → fg_colour: %s, fg_shade: %s", 
                     detect_colour_family_name(fg_colour), fg_shade)
        logger.debug("INPUT → bg_colour: %s, bg_shade: %s",
                     detect_colour_family_name(bg_colour), bg_shade)
        logger.debug("INPUT → size: %s, bold/underline/italic: %s/%s/%s",
                     size, bold, underline, italic)

    # Default: GUI_TEXT for neutral readable text (per T04 spec)
    if fg_colour is None:
        fg_colour = GUI_TEXT

    # Validate bg_colour/bg_shade consistency
    if bg_colour is None and bg_shade is not None:
        raise ValueError(
            "[G01c] bg_shade must be None when bg_colour is None. "
            "Specify a background colour family if you want explicit background."
        )

    if bg_colour is not None and bg_shade is None:
        raise ValueError(
            "[G01c] bg_shade must be provided when bg_colour is provided."
        )

    # Normalise shade tokens to uppercase before validation
    fg_shade_normalised: str = fg_shade.upper()
    bg_shade_normalised: str | None = bg_shade.upper() if bg_shade is not None else None

    # Validate and resolve foreground hex
    if fg_shade_normalised not in fg_colour:
        raise KeyError(
            f"[G01c] Invalid fg_shade '{fg_shade_normalised}' for this colour family. "
            f"Available shades: {list(fg_colour.keys())}"
        )
    fg_hex = fg_colour[fg_shade_normalised]

    # Validate and resolve background hex
    if bg_colour is not None and bg_shade_normalised is not None:
        if bg_shade_normalised not in bg_colour:
            raise KeyError(
                f"[G01c] Invalid bg_shade '{bg_shade_normalised}' for this colour family. "
                f"Available shades: {list(bg_colour.keys())}"
            )
        bg_hex = bg_colour[bg_shade_normalised]
    else:
        bg_hex = None

    size_token = size.upper()

    # Determine semantic family names for key-building
    fg_family_name = detect_colour_family_name(fg_colour)
    bg_family_name = detect_colour_family_name(bg_colour)
    bg_shade_label = bg_shade_normalised if bg_shade_normalised is not None else "NONE"

    # Build deterministic style name
    style_name = build_text_style_name(
        fg_family_name=fg_family_name,
        fg_shade=fg_shade_normalised,
        bg_family_name=bg_family_name,
        bg_shade=bg_shade_label,
        size_token=size_token,
        bold=bold,
        underline=underline,
        italic=italic,
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("STYLE NAME BUILT → %s", style_name)

    # Cache check
    if style_name in TEXT_STYLE_CACHE:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01c] Cache hit for %s", style_name)
            logger.debug("———[G01c DEBUG END]—————————————————————————————")
        return TEXT_STYLE_CACHE[style_name]

    # Resolve Tk font via G01b
    font_key = resolve_text_font(
        size=size_token,
        bold=bold,
        underline=underline,
        italic=italic,
    )

    # Create ttk style
    style = ttk.Style()

    # Base spacing from spacing scale
    padding_x = SPACING_SCALE["XS"]
    padding_y = 0

    # Configure style
    configure_kwargs: dict[str, Any] = {
        "foreground": fg_hex,
        "font": font_key,
        "padding": (padding_x, padding_y),
    }

    if bg_hex is not None:
        configure_kwargs["background"] = bg_hex

    style.configure(style_name, **configure_kwargs)

    # Apply TLabel layout so ttk can render the style
    try:
        base_layout = style.layout("TLabel")
        style.layout(style_name, base_layout)
    except Exception as exc:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01c] WARNING — could not apply layout: %s", exc)

    TEXT_STYLE_CACHE[style_name] = style_name

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("[G01c] Created text style: %s", style_name)
        logger.debug("———[G01c DEBUG END]—————————————————————————————")

    return style_name


# ====================================================================================================
# 7. CONVENIENCE HELPERS
# ----------------------------------------------------------------------------------------------------
# Simple wrappers around resolve_text_style() that provide commonly used
# semantic presets (error text, success text, headings, small captions, etc.).
#
# Purpose:
#   - Reduce boilerplate when creating frequently-used text styles.
#   - Keep component construction clean.
#
# Notes:
#   - All helpers must defer to resolve_text_style() internally.
#   - No caching or style creation logic belongs here.
# ====================================================================================================
def text_style_error(
    shade: ShadeType = "DARK",
    bold: bool = False,
    size: SizeType = "BODY",
) -> str:
    """
    Description:
        Convenience wrapper for error text styles using GUI_ERROR.

    Args:
        shade:
            Shade within GUI_ERROR. Defaults to "DARK".
        bold:
            Whether to render the text in bold.
        size:
            Font size token. Defaults to "BODY".

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If shade is invalid for GUI_ERROR.

    Notes:
        - Background is inherited.
    """
    return resolve_text_style(
        fg_colour=GUI_ERROR,
        fg_shade=shade,
        size=size,
        bold=bold,
    )


def text_style_success(
    shade: ShadeType = "DARK",
    bold: bool = False,
    size: SizeType = "BODY",
) -> str:
    """
    Description:
        Convenience wrapper for success text styles using GUI_SUCCESS.

    Args:
        shade:
            Shade within GUI_SUCCESS. Defaults to "DARK".
        bold:
            Whether to render the text in bold.
        size:
            Font size token. Defaults to "BODY".

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If shade is invalid for GUI_SUCCESS.

    Notes:
        - Background is inherited.
    """
    return resolve_text_style(
        fg_colour=GUI_SUCCESS,
        fg_shade=shade,
        size=size,
        bold=bold,
    )


def text_style_warning(
    shade: ShadeType = "DARK",
    bold: bool = False,
    size: SizeType = "BODY",
) -> str:
    """
    Description:
        Convenience wrapper for warning text styles using GUI_WARNING.

    Args:
        shade:
            Shade within GUI_WARNING. Defaults to "DARK".
        bold:
            Whether to render the text in bold.
        size:
            Font size token. Defaults to "BODY".

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If shade is invalid for GUI_WARNING.

    Notes:
        - Background is inherited.
    """
    return resolve_text_style(
        fg_colour=GUI_WARNING,
        fg_shade=shade,
        size=size,
        bold=bold,
    )


def text_style_heading(
    fg_colour: ColourFamily | None = None,
    fg_shade: str | None = None,
    bold: bool = True,
) -> str:
    """
    Description:
        Convenience wrapper for section headings.

    Args:
        fg_colour:
            Foreground family. Defaults to GUI_TEXT for neutral headings.
        fg_shade:
            Optional shade override.
            Defaults to:
                - "BLACK" for GUI_TEXT
                - "MID" for brand/status families (PRIMARY, SUCCESS, WARNING, ERROR)
        bold:
            Whether to apply bold. Defaults to True.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If fg_shade is invalid for the selected colour family.

    Notes:
        - Uses HEADING size.
        - For brand-coloured headings, pass fg_colour=GUI_PRIMARY explicitly.
    """

    # Determine default shade if not provided
    if fg_shade is None:
        if fg_colour is None or fg_colour is GUI_TEXT:
            fg_shade = "BLACK"
        else:
            fg_shade = "MID"

    # Convert to Literal union for clean type checking
    shade_literal = cast(ShadeType | TextShadeType, fg_shade)

    return resolve_text_style(
        fg_colour=fg_colour,
        fg_shade=shade_literal,
        size="HEADING",
        bold=bold,
    )


def text_style_body(
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK",
) -> str:
    """
    Description:
        Convenience wrapper for standard body text.

    Args:
        fg_colour:
            Foreground family. Defaults to GUI_TEXT.
        fg_shade:
            Shade within the family. Defaults to "BLACK".

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If fg_shade is invalid for the colour family.

    Notes:
        - Uses BODY size.
        - Normal weight (not bold).
    """
    return resolve_text_style(
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        size="BODY",
        bold=False,
    )


def text_style_small(
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK",
) -> str:
    """
    Description:
        Convenience wrapper for small text (captions, hints, meta labels).

    Args:
        fg_colour:
            Foreground family. Defaults to GUI_TEXT.
        fg_shade:
            Shade within the family. Defaults to "BLACK".

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If fg_shade is invalid for the colour family.

    Notes:
        - Uses SMALL size.
        - Normal weight (not bold).
    """
    return resolve_text_style(
        fg_colour=fg_colour,
        fg_shade=fg_shade,
        size="SMALL",
        bold=False,
    )


# ====================================================================================================
# 8. CACHE INTROSPECTION
# ----------------------------------------------------------------------------------------------------
# Diagnostic functions for inspecting and managing the text style cache.
#
# Purpose:
#   - Enable runtime cache inspection for debugging.
#   - Support cache clearing for theme switching or testing.
# ====================================================================================================
def get_text_style_cache_info() -> dict[str, int | list[str]]:
    """
    Description:
        Return diagnostic information about the text style cache.

    Args:
        None.

    Returns:
        dict[str, int | list[str]]:
            Dictionary containing:
            - "count": Number of cached styles
            - "keys": List of all cached style names

    Raises:
        None.

    Notes:
        - Useful for debugging and verifying cache behaviour.
    """
    return {
        "count": len(TEXT_STYLE_CACHE),
        "keys": list(TEXT_STYLE_CACHE.keys()),
    }


def clear_text_style_cache() -> None:
    """
    Description:
        Clear all entries from the text style cache.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Use for theme switching or testing.
        - Does NOT unregister styles from ttk.Style().
    """
    TEXT_STYLE_CACHE.clear()
    logger.info("[G01c] Cleared text style cache")


# ====================================================================================================
# 9. PUBLIC API
# ----------------------------------------------------------------------------------------------------
# Expose the main text-style resolver along with convenience helpers.
#
# Purpose:
#   - Define the module's public interface via __all__.
#   - Ensure IDE auto-completion and clean external imports.
#
# Notes:
#   - Only stable, externally-safe functions should be exported.
# ====================================================================================================
__all__ = [
    # Main engine
    "resolve_text_style",
    # Convenience helpers
    "text_style_error",
    "text_style_success",
    "text_style_warning",
    "text_style_heading",
    "text_style_body",
    "text_style_small",
    # Cache introspection
    "get_text_style_cache_info",
    "clear_text_style_cache",
]


# ====================================================================================================
# 10. SELF-TEST
# ----------------------------------------------------------------------------------------------------
# Minimal manual smoke test for the text-style engine.
#
# Purpose:
#   - Validate ttk style creation in an isolated environment.
#   - Provide quick visual confirmation of text rendering (body, heading, error).
#
# Notes:
#   - Not executed during normal imports.
#   - Wraps all behaviour in try/except/finally with proper logging.
# ====================================================================================================
if __name__ == "__main__":
    init_logging()
    logger.info("[G01c] Running G01c_text_styles self-test...")

    root = tk.Tk()
    root.title("G01c Self-test")

    try:
        # Test styles
        style_body = text_style_body()
        logger.info("Body style: %s", style_body)

        style_heading = text_style_heading()
        logger.info("Heading style: %s", style_heading)

        style_error = text_style_error()
        logger.info("Error style: %s", style_error)

        # Visual smoke test — 3 labels
        lbl1 = ttk.Label(root, text="Body text sample (neutral)", style=style_body)
        lbl1.pack(padx=20, pady=10)

        lbl2 = ttk.Label(root, text="Heading text sample (neutral bold)", style=style_heading)
        lbl2.pack(padx=20, pady=10)

        lbl3 = ttk.Label(root, text="Error text sample (red)", style=style_error)
        lbl3.pack(padx=20, pady=10)

        # Brand-coloured heading
        style_brand = text_style_heading(fg_colour=GUI_PRIMARY)
        lbl4 = ttk.Label(root, text="Brand heading (blue)", style=style_brand)
        lbl4.pack(padx=20, pady=10)

        # Cache info
        logger.info("Cache info: %s", get_text_style_cache_info())

        logger.info("[G01c] Visual labels created; entering mainloop...")
        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G01c self-test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G01c] Self-test complete.")