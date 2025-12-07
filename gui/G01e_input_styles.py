# ====================================================================================================
# G01e_input_styles.py
# ----------------------------------------------------------------------------------------------------
# Input style resolver for ttk.Entry, ttk.Combobox, ttk.Spinbox and similar field widgets.
#
# Purpose:
#   - Provide a parametric, cached input-style engine for the GUI framework.
#   - Turn high-level semantic parameters (role, shade, border, padding)
#     into concrete ttk styles for form controls.
#   - Keep ALL input/field styling logic in one place.
#
# Relationships:
#   - G01a_style_config  → pure design tokens (colours, spacing, borders).
#   - G01b_style_base    → shared utilities (fonts, colour utilities, cache keys).
#   - G01c_text_styles   → text/label style resolution.
#   - G01d_container_styles → container style resolution.
#   - G01e_input_styles  → input/field style resolution (THIS MODULE).
#
# Design principles:
#   - Single responsibility: only input/field styles live here.
#   - Parametric generation: one resolver, many styles.
#   - Idempotent caching: repeated calls with the same parameters return
#     the same style name.
#   - No raw hex values: ALL colours come from G01a tokens.
#
# Style naming pattern (via build_style_cache_key in G01b), e.g.:
#   Input_ENTRY_role_SECONDARY_LIGHT_border_THIN_pad_SM
#
#   CONTROL TYPE:
#       ENTRY, COMBOBOX, SPINBOX
#   ROLE values:
#       PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR
#   SHADE values:
#       LIGHT, MID, DARK, XDARK
#   BORDER WEIGHTS:
#       NONE, THIN, MEDIUM, THICK
#   PADDING TOKENS:
#       XS, SM, MD, LG, XL, XXL, NONE
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

# --- Prevent creation of __pycache__ folders --------------------------------------------------------
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
    ColourFamily,
    BorderWeightType,
    SpacingType,
    InputControlType,
    InputRoleType,
    # Utilities
    build_style_cache_key,
    resolve_text_font,
    SPACING_SCALE,
    BORDER_WEIGHTS,
    # Design tokens (re-exported from G01a)
    GUI_PRIMARY,
    GUI_SECONDARY,
    GUI_SUCCESS,
    GUI_WARNING,
    GUI_ERROR,
    GUI_TEXT,
)


# ====================================================================================================
# 4. INPUT STYLE CACHE
# ----------------------------------------------------------------------------------------------------
# Dedicated cache for storing all resolved ttk input style names.
#
# Purpose:
#   - Ensure idempotent behaviour: repeated calls with identical parameters
#     return the same style name.
#   - Prevent duplicate ttk.Style registrations.
#   - Act as the single source of truth for input/field styles.
# ====================================================================================================
INPUT_STYLE_CACHE: dict[str, str] = {}

# Mapping of control_type → base ttk style
INPUT_BASE_STYLES: dict[str, str] = {
    "ENTRY": "TEntry",
    "COMBOBOX": "TCombobox",
    "SPINBOX": "TSpinbox",
}

# Semantic mapping of roles → colour families (for field background + border)
INPUT_ROLE_FAMILIES: dict[str, ColourFamily] = {
    "PRIMARY": GUI_PRIMARY,
    "SECONDARY": GUI_SECONDARY,
    "SUCCESS": GUI_SUCCESS,
    "WARNING": GUI_WARNING,
    "ERROR": GUI_ERROR,
}

# Disabled state foreground colour (neutral)
INPUT_DISABLED_FG_HEX = GUI_TEXT["GREY"]


# ====================================================================================================
# 5. INTERNAL HELPERS
# ----------------------------------------------------------------------------------------------------
# Pure internal utilities supporting input-style resolution.
#
# Purpose:
#   - Provide style-name generation via build_input_style_name().
#   - Map control types to base ttk styles.
#   - Resolve border widths and padding tokens into pixel values.
#   - DO NOT create ttk styles or modify global state.
# ====================================================================================================
def build_input_style_name(
    control_type: str,
    role_name: str,
    shade: str,
    border_weight: str,
    padding_token: str,
) -> str:
    """
    Description:
        Construct the canonical input-style name using the shared
        build_style_cache_key() helper from G01b.

    Args:
        control_type:
            Input control type token ("ENTRY", "COMBOBOX", "SPINBOX").
        role_name:
            Semantic role token ("PRIMARY", "SECONDARY", etc.).
        shade:
            Shade token within the role's colour family.
        border_weight:
            Border weight token ("NONE", "THIN", "MEDIUM", "THICK").
        padding_token:
            Padding token ("NONE", "XS", "SM", "MD", "LG", "XL", "XXL").

    Returns:
        str:
            Deterministic, human-readable style name.

    Raises:
        None.

    Notes:
        - Uses build_style_cache_key from G01b for consistency.
        - Relief is NOT encoded in the style name; it derives from border width.
    """
    return build_style_cache_key(
        "Input",
        control_type.upper(),
        f"role_{role_name.upper()}",
        shade.upper(),
        f"border_{border_weight.upper()}",
        f"pad_{padding_token.upper()}",
    )


def resolve_control_base_style(control_type: str) -> str:
    """
    Description:
        Map logical control type to a ttk base style.

    Args:
        control_type:
            Input control type token ("ENTRY", "COMBOBOX", "SPINBOX").

    Returns:
        str:
            The ttk base style name (e.g., "TEntry").

    Raises:
        KeyError:
            If control_type is not recognised.

    Notes:
        - Used to clone layout from the base style.
    """
    key = control_type.upper()
    if key not in INPUT_BASE_STYLES:
        raise KeyError(
            f"[G01e] Unknown control_type '{control_type}'. "
            f"Available: {list(INPUT_BASE_STYLES.keys())}"
        )
    return INPUT_BASE_STYLES[key]


def resolve_border_width_internal(border: BorderWeightType | None) -> int:
    """
    Description:
        Convert a BorderWeightType token into a numeric pixel border width.

    Args:
        border:
            Border weight token or None.

    Returns:
        int:
            Pixel width (0 for NONE or None).

    Raises:
        KeyError:
            If border is not a valid BORDER_WEIGHTS key.

    Notes:
        - Returns 0 for None or "NONE".
    """
    if border is None or str(border).upper() == "NONE":
        return 0

    token = str(border).upper()
    if token not in BORDER_WEIGHTS:
        raise KeyError(
            f"[G01e] Invalid border token '{token}'. "
            f"Available: {list(BORDER_WEIGHTS.keys())}"
        )

    return BORDER_WEIGHTS[token]


def resolve_padding_internal(padding: SpacingType | None) -> tuple[int, int]:
    """
    Description:
        Resolve a spacing token into symmetric (pad_x, pad_y) pixel values.

    Args:
        padding:
            Spacing token (XS, SM, MD, LG, XL, XXL) or None.

    Returns:
        tuple[int, int]:
            Symmetric padding values (pad_x, pad_y).

    Raises:
        KeyError:
            If padding is not a valid SPACING_SCALE key.

    Notes:
        - Returns (0, 0) for None.
    """
    if padding is None:
        return (0, 0)

    token = str(padding).upper()
    if token not in SPACING_SCALE:
        raise KeyError(
            f"[G01e] Invalid padding token '{token}'. "
            f"Available: {list(SPACING_SCALE.keys())}"
        )

    px = SPACING_SCALE[token]
    return (px, px)


# ====================================================================================================
# 6. INPUT STYLE RESOLUTION (PUBLIC API – CORE ENGINE)
# ----------------------------------------------------------------------------------------------------
# The main input-style resolver: resolve_input_style().
#
# Purpose:
#   - Convert high-level semantic parameters (role, shade, border, padding)
#     into concrete ttk input styles.
#   - Apply deterministic naming and idempotent caching.
#   - Register styles with ttk.Style(), including padding, border, and font.
#
# Notes:
#   - This is the ONLY place that creates ttk styles for input/field widgets.
#   - Text colour is derived from GUI_TEXT for readability.
# ====================================================================================================
def resolve_input_style(
    control_type: InputControlType = "ENTRY",
    role: InputRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
) -> str:
    """
    Description:
        Resolve a complete ttk input style (Entry, Combobox, Spinbox) with
        foreground, background, border, padding, and font. Styles are created
        lazily and cached by a deterministic key.

    Args:
        control_type:
            The input widget type. One of: "ENTRY", "COMBOBOX", "SPINBOX".
            Defaults to "ENTRY".
        role:
            Semantic colour role for the field surface and border.
            One of: "PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR".
            Defaults to "SECONDARY".
        shade:
            Shade within the role's colour family. One of:
            "LIGHT", "MID", "DARK", "XDARK". Defaults to "LIGHT".
        border:
            Border weight token. One of: "NONE", "THIN", "MEDIUM", "THICK",
            or None. Defaults to "THIN".
        padding:
            Internal padding token. One of: "XS", "SM", "MD", "LG", "XL",
            "XXL", or None. Defaults to "SM".

    Returns:
        str:
            The registered ttk style name. Use directly on input widgets:
                ttk.Entry(parent, style=style_name)

    Raises:
        KeyError:
            If role is invalid or shade is not valid for the role's family,
            or if border/padding tokens are invalid.

    Notes:
        - SECONDARY/LIGHT + THIN border is the default for neutral inputs.
        - SUCCESS / WARNING / ERROR roles can be used for status feedback.
        - Border width 0 effectively hides borders regardless of relief.
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("———[G01e DEBUG START]———————————————————————————")
        logger.debug(
            "INPUT → control_type=%s, role=%s, shade=%s, border=%s, padding=%s",
            control_type, role, shade, border, padding
        )

    role_key = role.upper()
    if role_key not in INPUT_ROLE_FAMILIES:
        raise KeyError(
            f"[G01e] Invalid role '{role_key}'. "
            f"Expected: {list(INPUT_ROLE_FAMILIES.keys())}"
        )

    colour_family = INPUT_ROLE_FAMILIES[role_key]

    # Normalise shade token to uppercase before validation
    shade_normalised: str = shade.upper()

    if shade_normalised not in colour_family:
        raise KeyError(
            f"[G01e] Invalid shade '{shade_normalised}' for role '{role_key}'. "
            f"Available: {list(colour_family.keys())}"
        )

    # Resolve colours
    bg_hex = colour_family[shade_normalised]
    fg_hex = GUI_TEXT["BLACK"]

    # Border width + padding
    border_width = resolve_border_width_internal(border)
    pad_x, pad_y = resolve_padding_internal(padding)

    border_token = "NONE" if border_width == 0 else str(border).upper()
    padding_token = "NONE" if padding is None else str(padding).upper()

    # Build deterministic style name
    style_name = build_input_style_name(
        control_type=control_type,
        role_name=role_key,
        shade=shade_normalised,
        border_weight=border_token,
        padding_token=padding_token,
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("STYLE NAME BUILT → %s", style_name)

    # Cache hit
    if style_name in INPUT_STYLE_CACHE:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01e] Cache hit for %s", style_name)
            logger.debug("———[G01e DEBUG END]—————————————————————————————")
        return INPUT_STYLE_CACHE[style_name]

    # Base ttk style
    base_style = resolve_control_base_style(control_type)

    # Create ttk.Style and derive layout
    style = ttk.Style()
    try:
        style.layout(style_name, style.layout(base_style))
    except Exception as exc:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01e] WARNING — could not apply layout: %s", exc)

    # Font – use BODY neutral font
    font_key = resolve_text_font(
        size="BODY",
        bold=False,
        underline=False,
        italic=False,
    )

    # Relief derived from border width
    relief = "solid" if border_width > 0 else "flat"

    # Apply configuration
    style.configure(
        style_name,
        foreground=fg_hex,
        fieldbackground=bg_hex,
        background=bg_hex,
        borderwidth=border_width,
        relief=relief,
        padding=(pad_x, pad_y),
        font=font_key,
    )

    # Focus / disabled state behaviour
    focus_hex = colour_family.get("MID", bg_hex)
    style.map(
        style_name,
        bordercolor=[("focus", focus_hex)],
        foreground=[("disabled", INPUT_DISABLED_FG_HEX), ("!disabled", fg_hex)],
    )

    # Cache it
    INPUT_STYLE_CACHE[style_name] = style_name

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("[G01e] Created input style: %s", style_name)
        logger.debug("  Background: %s, Border width: %s, Relief: %s", bg_hex, border_width, relief)
        logger.debug("———[G01e DEBUG END]—————————————————————————————")

    return style_name


# ====================================================================================================
# 7. CONVENIENCE HELPERS
# ----------------------------------------------------------------------------------------------------
# Simple semantic presets wrapping resolve_input_style().
#
# Purpose:
#   - Reduce boilerplate in higher-level GUI components.
#   - Keep construction clean.
# ====================================================================================================
def input_style_entry_default() -> str:
    """
    Description:
        Default entry style with neutral colours.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses role=SECONDARY, shade=LIGHT, border=THIN, padding=SM.
        - Relief is automatically derived from border width
          (“solid” when border > 0, otherwise “flat”).
    """
    return resolve_input_style(
        control_type="ENTRY",
        role="SECONDARY",
        shade="LIGHT",
        border="THIN",
        padding="SM",
    )


def input_style_entry_error() -> str:
    """
    Description:
        Entry style with error-indicating surface and border.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses role=ERROR, shade=LIGHT, border=MEDIUM.
    """
    return resolve_input_style(
        control_type="ENTRY",
        role="ERROR",
        shade="LIGHT",
        border="MEDIUM",
        padding="SM",
    )


def input_style_entry_success() -> str:
    """
    Description:
        Entry style with success-indicating surface and border.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses role=SUCCESS, shade=LIGHT, border=THIN.
    """
    return resolve_input_style(
        control_type="ENTRY",
        role="SUCCESS",
        shade="LIGHT",
        border="THIN",
        padding="SM",
    )


def input_style_combobox_default() -> str:
    """
    Description:
        Default combobox style with neutral colours.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses same defaults as entry: SECONDARY/LIGHT with THIN border.
    """
    return resolve_input_style(
        control_type="COMBOBOX",
        role="SECONDARY",
        shade="LIGHT",
        border="THIN",
        padding="SM",
    )


def input_style_spinbox_default() -> str:
    """
    Description:
        Default spinbox style with neutral colours.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses same defaults as entry: SECONDARY/LIGHT with THIN border.
    """
    return resolve_input_style(
        control_type="SPINBOX",
        role="SECONDARY",
        shade="LIGHT",
        border="THIN",
        padding="SM",
    )


# ====================================================================================================
# 8. CACHE INTROSPECTION
# ----------------------------------------------------------------------------------------------------
# Diagnostic functions for inspecting and managing the input style cache.
#
# Purpose:
#   - Enable runtime cache inspection for debugging.
#   - Support cache clearing for theme switching or testing.
# ====================================================================================================
def get_input_style_cache_info() -> dict[str, int | list[str]]:
    """
    Description:
        Return diagnostic information about the input style cache.

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
        "count": len(INPUT_STYLE_CACHE),
        "keys": list(INPUT_STYLE_CACHE.keys()),
    }


def clear_input_style_cache() -> None:
    """
    Description:
        Clear all entries from the input style cache.

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
    INPUT_STYLE_CACHE.clear()
    logger.info("[G01e] Cleared input style cache")


# ====================================================================================================
# 9. PUBLIC API
# ----------------------------------------------------------------------------------------------------
# Expose resolver + convenience helpers.
# ====================================================================================================
__all__ = [
    # Main engine
    "resolve_input_style",
    # Convenience helpers
    "input_style_entry_default",
    "input_style_entry_error",
    "input_style_entry_success",
    "input_style_combobox_default",
    "input_style_spinbox_default",
    # Cache introspection
    "get_input_style_cache_info",
    "clear_input_style_cache",
]


# ====================================================================================================
# 10. SELF-TEST
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging()
    logger.info("[G01e] Running G01e_input_styles self-test...")

    root = tk.Tk()
    root.title("G01e Input Styles — Self-test")

    try:
        root.geometry("450x320")
        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        s_default = input_style_entry_default()
        s_error = input_style_entry_error()
        s_success = input_style_entry_success()
        s_combo = input_style_combobox_default()

        ttk.Label(frame, text="Default Entry:").pack(anchor="w")
        e1 = ttk.Entry(frame, style=s_default)
        e1.insert(0, "Default Entry")
        e1.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Error Entry:").pack(anchor="w")
        e2 = ttk.Entry(frame, style=s_error)
        e2.insert(0, "Error Entry")
        e2.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Success Entry:").pack(anchor="w")
        e3 = ttk.Entry(frame, style=s_success)
        e3.insert(0, "Success Entry")
        e3.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Combobox:").pack(anchor="w")
        c1 = ttk.Combobox(frame, style=s_combo, values=["Option A", "Option B", "Option C"])
        c1.set("Select...")
        c1.pack(fill="x", pady=(0, 10))

        logger.info("Cache info: %s", get_input_style_cache_info())

        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G01e self-test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G01e] Self-test complete.")