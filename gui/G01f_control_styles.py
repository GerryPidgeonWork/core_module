# ====================================================================================================
# G01f_control_styles.py
# ----------------------------------------------------------------------------------------------------
# Control style resolver for buttons, checkboxes, radios, and switches.
#
# Purpose:
#   - Provide a parametric, cached control-style engine for the GUI framework.
#   - Turn high-level semantic parameters (widget type, variant, colours, borders)
#     into concrete ttk styles with state handling (normal, hover, active, disabled, focus).
#   - Keep ALL stateful control styling logic in one place.
#
# Relationships:
#   - G01a_style_config   → pure design tokens (colours, typography, spacing).
#   - G01b_style_base     → shared utilities (cache keys, tokens, type aliases).
#   - G01f_control_styles → control style resolution (THIS MODULE).
#
# Design principles:
#   - Single responsibility: only control (interactive) styles live here.
#   - Parametric generation: one resolver, many styles.
#   - Idempotent caching: repeated calls with the same parameters return
#     the same style name.
#   - No raw hex values: ALL colours come from G01a tokens.
#
# State behaviour (per T03 Section 7.6, with parametric overrides):
#   - Normal:   background = bg_shade_normal (default: MID)
#   - Hover:    background = bg_shade_hover  (default: DARK)
#   - Active:   background = bg_shade_pressed (default: XDARK)
#   - Disabled: background = bg_shade_normal, foreground = gray
#   - Focus:    bordercolor = DARK shade of border family (or explicit family)
#
# Style naming pattern (via build_style_cache_key in G01b), e.g.:
#   Control_BUTTON_variant_PRIMARY_fg_TEXT_DARK_bg_PRIMARY_norm_MID_hover_DARK_press_XDARK
#       _bd_PRIMARY_DARK_bw_THIN_pad_SM_relief_RAISED
#
#   WIDGETTYPE values:
#       BUTTON, CHECKBOX, RADIO, SWITCH
#   VARIANT values:
#       PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR
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
from gui.G00a_gui_packages import tk, ttk, init_gui_theme, is_gui_theme_initialised

# Shared utilities, type aliases, and design tokens from G01b (single source of truth)
from gui.G01b_style_base import (
    # Type aliases
    ShadeType,
    TextShadeType,
    ColourFamily,
    BorderWeightType,
    SpacingType,
    ControlWidgetType,
    ControlVariantType,
    # Utilities
    BORDER_WEIGHTS,
    SPACING_SCALE,
    build_style_cache_key,
    detect_colour_family_name,
    resolve_text_font,
    # Design tokens (re-exported from G01a)
    GUI_PRIMARY,
    GUI_SECONDARY,
    GUI_SUCCESS,
    GUI_WARNING,
    GUI_ERROR,
    GUI_TEXT,
    # Additional tokens for G01f
    TEXT_COLOUR_GREY,
    TEXT_COLOUR_WHITE,
    CONTROL_INDICATOR_GAP,
)


# ====================================================================================================
# 4. CONTROL STYLE CACHE
# ----------------------------------------------------------------------------------------------------
# A dedicated cache for storing all resolved ttk control style names.
#
# Purpose:
#   - Ensure idempotent behaviour: repeated calls with identical parameters
#     return the same style name.
#   - Prevent duplicate ttk.Style registrations.
#   - Act as the single source of truth for created control styles.
# ====================================================================================================
CONTROL_STYLE_CACHE: dict[str, str] = {}


# ====================================================================================================
# 4b. WINDOWS THEME INITIALISATION
# ----------------------------------------------------------------------------------------------------
# On Windows 11 (and other Windows versions), the native "vista" and "winnative"
# themes render ttk.Button using OS-native controls that ignore the `background`
# property. This means custom button colours are discarded.
#
# Solution:
#   - Call init_gui_theme() from G00a which switches to the "clam" theme.
#   - This is called automatically when resolving control styles.
#
# Notes:
#   - The "clam" theme is cross-platform and provides consistent behaviour.
#   - For best results, call init_gui_theme() immediately after creating
#     the Tk root window, BEFORE any styles are registered.
# ====================================================================================================
def ensure_button_theme_initialised() -> None:
    """
    Description:
        Ensure the ttk theme is configured to honour button background colours.
        Delegates to init_gui_theme() from G00a.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Called automatically when resolving control styles.
        - For best results, call init_gui_theme() at application startup.
    """
    if not is_gui_theme_initialised():
        init_gui_theme()


# ====================================================================================================
# 5. INTERNAL HELPERS
# ----------------------------------------------------------------------------------------------------
# Pure internal utilities supporting control-style resolution.
#
# Purpose:
#   - Provide semantic helpers (variant → colour family, base layout lookup).
#   - Perform name construction via build_control_style_name().
#   - Resolve padding / border tokens.
#   - DO NOT create ttk styles or modify global state.
#
# Notes:
#   - detect_colour_family_name() is imported from G01b (single source of truth).
# ====================================================================================================

# Semantic mapping of variants → colour families
CONTROL_VARIANT_MAP: dict[str, ColourFamily] = {
    "PRIMARY": GUI_PRIMARY,
    "SECONDARY": GUI_SECONDARY,
    "SUCCESS": GUI_SUCCESS,
    "WARNING": GUI_WARNING,
    "ERROR": GUI_ERROR,
}

# Disabled state foreground colour (from G01a)
DISABLED_FG_HEX = TEXT_COLOUR_GREY


def build_control_style_name(
    widget_type: str,
    variant_name: str,
    fg_family_name: str,
    fg_shade: str,
    bg_family_name: str,
    bg_shade_normal: str,
    bg_shade_hover: str,
    bg_shade_pressed: str,
    border_family_name: str,
    border_shade: str,
    border_weight_token: str,
    padding_token: str,
    relief_token: str,
) -> str:
    """
    Description:
        Construct the canonical style name for control widgets using the shared
        build_style_cache_key helper from G01b.

    Args:
        widget_type:
            Logical widget type token ("BUTTON", "CHECKBOX", "RADIO", "SWITCH").
        variant_name:
            Semantic variant token ("PRIMARY", "SUCCESS", etc.).
        fg_family_name:
            Foreground colour family name (e.g., "TEXT").
        fg_shade:
            Foreground shade token (e.g., "DARK").
        bg_family_name:
            Background colour family name (e.g., "PRIMARY").
        bg_shade_normal:
            Background shade token used for the normal state.
        bg_shade_hover:
            Background shade token used for the hover/active state.
        bg_shade_pressed:
            Background shade token used for the pressed state.
        border_family_name:
            Border colour family name.
        border_shade:
            Border shade token.
        border_weight_token:
            Border weight token ("NONE", "THIN", "MEDIUM", "THICK").
        padding_token:
            Padding token ("NONE", "XS", "SM", "MD", "LG", "XL", "XXL").
        relief_token:
            Relief token for visual elevation ("FLAT", "RAISED", etc.).

    Returns:
        str:
            Deterministic, human-readable style name.

    Raises:
        None.

    Notes:
        - Uses build_style_cache_key from G01b for consistency.
        - Order of segments is stable to maximise cache hits.
    """
    return build_style_cache_key(
        "Control",
        widget_type.upper(),
        f"variant_{variant_name.upper()}",
        f"fg_{fg_family_name}",
        fg_shade.upper(),
        f"bg_{bg_family_name}",
        f"norm_{bg_shade_normal.upper()}",
        f"hover_{bg_shade_hover.upper()}",
        f"press_{bg_shade_pressed.upper()}",
        f"bd_{border_family_name}",
        border_shade.upper(),
        f"bw_{border_weight_token.upper()}",
        f"pad_{padding_token.upper()}",
        f"relief_{relief_token.upper()}",
    )


def get_variant_base_family(variant_name: str) -> ColourFamily:
    """
    Description:
        Resolve the base colour family for a given variant token.

    Args:
        variant_name:
            Variant token ("PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR").

    Returns:
        ColourFamily:
            The corresponding colour family dictionary.

    Raises:
        KeyError:
            If variant_name is not registered in CONTROL_VARIANT_MAP.

    Notes:
        - All families originate from G01a_style_config.
    """
    key = variant_name.upper()
    if key not in CONTROL_VARIANT_MAP:
        raise KeyError(
            f"[G01f] Invalid variant '{key}'. "
            f"Expected one of: {list(CONTROL_VARIANT_MAP.keys())}"
        )
    return CONTROL_VARIANT_MAP[key]


def get_base_layout_name(widget_type: str) -> str:
    """
    Description:
        Return the base ttk layout name appropriate for the given widget type.

    Args:
        widget_type:
            "BUTTON", "CHECKBOX", "RADIO", "SWITCH".

    Returns:
        str:
            Base ttk style name whose layout will be cloned.

    Raises:
        ValueError:
            If widget_type is not one of the recognised tokens.

    Notes:
        - Switches share the Checkbutton layout.
    """
    widget_key = widget_type.upper()

    if widget_key == "BUTTON":
        return "TButton"
    if widget_key == "CHECKBOX":
        return "TCheckbutton"
    if widget_key == "RADIO":
        return "TRadiobutton"
    if widget_key == "SWITCH":
        return "TCheckbutton"

    raise ValueError(
        f"[G01f] Unsupported widget_type '{widget_type}'. "
        "Expected one of: BUTTON, CHECKBOX, RADIO, SWITCH."
    )


def resolve_border_width_internal(border_weight: BorderWeightType | None) -> int:
    """
    Description:
        Convert a BorderWeightType token into a numeric pixel border width.

    Args:
        border_weight:
            Border weight token or None.

    Returns:
        int:
            Pixel width (0 for NONE or None).

    Raises:
        KeyError:
            If border_weight is not a valid BORDER_WEIGHTS key.

    Notes:
        - Returns 0 for None or "NONE".
    """
    if border_weight is None:
        return 0

    token = str(border_weight).upper()
    if token == "NONE":
        return 0

    if token not in BORDER_WEIGHTS:
        raise KeyError(
            f"[G01f] Invalid border_weight '{token}'. "
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
            f"[G01f] Invalid padding token '{token}'. "
            f"Available: {list(SPACING_SCALE.keys())}"
        )

    px = SPACING_SCALE[token]
    return (px, px)


# ====================================================================================================
# 6. CONTROL STYLE RESOLUTION (PUBLIC API – CORE ENGINE)
# ----------------------------------------------------------------------------------------------------
# The main control-style resolver: resolve_control_style().
#
# Purpose:
#   - Convert high-level semantic parameters (widget type, variant) and
#     explicit overrides (fg/bg/border/padding/relief) into concrete ttk
#     control styles.
#   - Apply deterministic naming and idempotent caching.
#   - Register styles with ttk.Style(), including colours, padding, borders
#     and comprehensive state mappings per T03 Section 7.6.
#
# Notes:
#   - This is the ONLY place that creates ttk styles for interactive controls.
#   - All concrete styling work lives here (background, foreground, padding).
#   - Semantic parameters provide defaults; explicit parameters always win.
# ====================================================================================================
def resolve_control_style(
    widget_type: ControlWidgetType = "BUTTON",
    variant: ControlVariantType = "PRIMARY",
    fg_colour: ColourFamily | None = None,
    fg_shade: ShadeType | TextShadeType = "BLACK",
    bg_colour: ColourFamily | None = None,
    bg_shade_normal: ShadeType | None = None,
    bg_shade_hover: ShadeType | None = None,
    bg_shade_pressed: ShadeType | None = None,
    border_colour: ColourFamily | None = None,
    border_shade: ShadeType | None = None,
    border_weight: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
    relief: str | None = None,
) -> str:
    """
    Description:
        Resolve a control style (Buttons, Checkbuttons, Radiobuttons, Switches)
        with full parametric control. Styles are created lazily and cached using
        a deterministic, semantic name.

    Args:
        widget_type:
            Logical widget type token. One of:
                - "BUTTON"
                - "CHECKBOX"
                - "RADIO"
                - "SWITCH"
            Defaults to "BUTTON".
        variant:
            Semantic role / colour variant. One of:
                - "PRIMARY"
                - "SECONDARY"
                - "SUCCESS"
                - "WARNING"
                - "ERROR"
            Defaults to "PRIMARY".
        fg_colour:
            Foreground (text/icon) colour family. Defaults to GUI_TEXT.
        fg_shade:
            Shade within the foreground family. For TEXT family:
                "BLACK", "WHITE", "DARK", "LIGHT".
            For status/brand families:
                "LIGHT", "MID", "DARK", "XDARK".
            Defaults to "DARK".
        bg_colour:
            Background colour family for the control face. Defaults to the
            family implied by `variant` (PRIMARY, SECONDARY, etc.).
        bg_shade_normal:
            Shade used for the normal background state. Defaults to "MID".
        bg_shade_hover:
            Shade used for hover/active background state. Defaults to "DARK".
        bg_shade_pressed:
            Shade used for the pressed background state. Defaults to "XDARK"
            or "DARK" if XDARK is not present.
        border_colour:
            Border colour family. Defaults to bg_colour.
        border_shade:
            Shade within the border family. Defaults to "DARK" where available,
            otherwise falls back to bg_shade_normal.
        border_weight:
            Border weight token. One of:
                "NONE", "THIN", "MEDIUM", "THICK" or None.
            Defaults to "THIN".
        padding:
            Internal padding token. One of:
                "XS", "SM", "MD", "LG", "XL", "XXL" or None.
            Defaults to "SM".
        relief:
            Tcl/Tk relief style. Common values:
                "flat", "raised", "sunken", "solid", "ridge", "groove".
            If None, defaults to:
                - "raised" for BUTTON
                - "flat"   for CHECKBOX/RADIO/SWITCH

    Returns:
        str:
            The ttk style name to use on ttk controls, for example:
                ttk.Button(parent, text="OK", style=style_name)

    Raises:
        KeyError:
            If any shade token is invalid for its colour family or if padding /
            border_weight is invalid.
        ValueError:
            If widget_type or variant are unsupported.

    Notes:
        - State behaviour per T03 Section 7.6:
            * Normal: bg_shade_normal
            * Hover (active): bg_shade_hover
            * Pressed: bg_shade_pressed
            * Disabled: bg_shade_normal, DISABLED_FG_HEX
        - Semantic parameters (`variant`) provide defaults only; explicit
          fg/bg/border overrides always win.
    """
    # Ensure theme supports button backgrounds (Windows fix)
    ensure_button_theme_initialised()

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("———[G01f DEBUG START]———————————————————————————")
        logger.debug(
            "INPUT → widget_type=%s, variant=%s", widget_type, variant
        )
        logger.debug(
            "INPUT → fg=%s/%s, bg=%s/(%s,%s,%s), border=%s/%s, weight=%s, pad=%s, relief=%s",
            detect_colour_family_name(fg_colour),
            fg_shade,
            detect_colour_family_name(bg_colour),
            bg_shade_normal,
            bg_shade_hover,
            bg_shade_pressed,
            detect_colour_family_name(border_colour),
            border_shade,
            border_weight,
            padding,
            relief,
        )

    widget_key = widget_type.upper()
    variant_key = variant.upper()

    # Validate widget_type and variant semantics
    if widget_key not in {"BUTTON", "CHECKBOX", "RADIO", "SWITCH"}:
        raise ValueError(
            f"[G01f] Invalid widget_type '{widget_key}'. "
            "Expected one of: BUTTON, CHECKBOX, RADIO, SWITCH."
        )

    # Base background family from variant if not explicitly set
    if bg_colour is None:
        bg_colour = get_variant_base_family(variant_key)

    # Foreground defaults to GUI_TEXT
    if fg_colour is None:
        fg_colour = GUI_TEXT

    # Border defaults to background family
    if border_colour is None:
        border_colour = bg_colour

    # Normalise shade tokens to uppercase before validation
    fg_shade_normalised: str = fg_shade.upper()
    bg_shade_normal_normalised: str | None = bg_shade_normal.upper() if bg_shade_normal is not None else None
    bg_shade_hover_normalised: str | None = bg_shade_hover.upper() if bg_shade_hover is not None else None
    bg_shade_pressed_normalised: str | None = bg_shade_pressed.upper() if bg_shade_pressed is not None else None
    border_shade_normalised: str | None = border_shade.upper() if border_shade is not None else None

    # Validate shades for each family
    if fg_shade_normalised not in fg_colour:
        raise KeyError(
            f"[G01f] Invalid fg_shade '{fg_shade_normalised}'. "
            f"Available: {list(fg_colour.keys())}"
        )

    # Default background shades (if not explicitly supplied)
    if bg_shade_normal_normalised is None:
        bg_shade_normal_normalised = "MID"
    if bg_shade_hover_normalised is None:
        bg_shade_hover_normalised = "DARK"
    if bg_shade_pressed_normalised is None:
        # Prefer XDARK, fall back to DARK, then MID
        if "XDARK" in bg_colour:
            bg_shade_pressed_normalised = "XDARK"
        elif "DARK" in bg_colour:
            bg_shade_pressed_normalised = "DARK"
        else:
            bg_shade_pressed_normalised = "MID"

    for shade_token, label in [
        (bg_shade_normal_normalised, "bg_shade_normal"),
        (bg_shade_hover_normalised, "bg_shade_hover"),
        (bg_shade_pressed_normalised, "bg_shade_pressed"),
    ]:
        if shade_token not in bg_colour:
            raise KeyError(
                f"[G01f] Invalid {label} '{shade_token}'. "
                f"Available for bg_colour: {list(bg_colour.keys())}"
            )

    # Border shade default
    if border_shade_normalised is None:
        if "DARK" in border_colour:
            border_shade_normalised = "DARK"
        else:
            border_shade_normalised = bg_shade_normal_normalised

    if border_shade_normalised not in border_colour:
        raise KeyError(
            f"[G01f] Invalid border_shade '{border_shade_normalised}'. "
            f"Available: {list(border_colour.keys())}"
        )

    # Border width + tokens
    border_width = resolve_border_width_internal(border_weight)
    border_weight_token = "NONE" if border_width == 0 else str(border_weight).upper()

    # Padding resolution
    pad_x, pad_y = resolve_padding_internal(padding)
    padding_token = "NONE" if padding is None else str(padding).upper()

    # Relief resolution
    if relief is None:
        # Sensible defaults per control type
        relief_token = "raised" if widget_key == "BUTTON" and border_width > 0 else "flat"
    else:
        relief_token = relief

    # Resolve hex colours
    fg_hex = fg_colour[fg_shade_normalised]
    bg_hex_normal = bg_colour[bg_shade_normal_normalised]
    bg_hex_hover = bg_colour[bg_shade_hover_normalised]
    bg_hex_pressed = bg_colour[bg_shade_pressed_normalised]
    border_hex = border_colour[border_shade_normalised]

    # Foreground family names
    fg_family_name = detect_colour_family_name(fg_colour)
    bg_family_name = detect_colour_family_name(bg_colour)
    border_family_name = detect_colour_family_name(border_colour)

    # Build deterministic style name
    style_name = build_control_style_name(
        widget_type=widget_key,
        variant_name=variant_key,
        fg_family_name=fg_family_name,
        fg_shade=fg_shade_normalised,
        bg_family_name=bg_family_name,
        bg_shade_normal=bg_shade_normal_normalised,
        bg_shade_hover=bg_shade_hover_normalised,
        bg_shade_pressed=bg_shade_pressed_normalised,
        border_family_name=border_family_name,
        border_shade=border_shade_normalised,
        border_weight_token=border_weight_token,
        padding_token=padding_token,
        relief_token=str(relief_token),
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("STYLE NAME BUILT → %s", style_name)

    # Cache lookup
    if style_name in CONTROL_STYLE_CACHE:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01f] Cache hit for style: %s", style_name)
            logger.debug("———[G01f DEBUG END]—————————————————————————————")
        return CONTROL_STYLE_CACHE[style_name]

    style = ttk.Style()

    # Clone base layout for this control type
    base_layout_name = get_base_layout_name(widget_key)
    try:
        base_layout = style.layout(base_layout_name)
        style.layout(style_name, base_layout)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "[G01f] Layout applied to %s (from %s)",
                style_name,
                base_layout_name,
            )
    except Exception as exc:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "[G01f] WARNING — could not apply layout for %s: %s",
                style_name,
                exc,
            )

    # Configure normal state
    # Resolve font for buttons (BODY size, not bold for standard buttons)
    button_font = resolve_text_font(size="BODY", bold=False)

    configure_kwargs: dict[str, Any] = {
        "background": bg_hex_normal,
        "foreground": fg_hex,
        "font": button_font,
        "padding": (pad_x, pad_y),
        "borderwidth": border_width,
        "relief": relief_token,
        "focusthickness": 1,
        "focuscolor": border_hex,
    }

    # For checkbuttons and radiobuttons, set indicator colours and spacing
    if widget_key in ("CHECKBOX", "RADIO", "SWITCH"):
        configure_kwargs["indicatorcolor"] = bg_hex_normal
        configure_kwargs["indicatorbackground"] = TEXT_COLOUR_WHITE
        # Add margin around indicator (left, top, right, bottom) - right margin creates gap to text
        configure_kwargs["indicatormargin"] = (0, 0, CONTROL_INDICATOR_GAP, 0)

    style.configure(style_name, **configure_kwargs)

    # State mappings per T03 Section 7.6
    focus_border_hex = border_colour.get("XDARK", border_colour.get("DARK", border_hex))

    map_kwargs: dict[str, list] = {
        "background": [
            ("pressed", bg_hex_pressed),     # Active/pressed state
            ("active", bg_hex_hover),        # Hover state
            ("disabled", bg_hex_normal),     # Disabled keeps normal bg
        ],
        "foreground": [
            ("disabled", DISABLED_FG_HEX),
            ("!disabled", fg_hex),
        ],
        "bordercolor": [
            ("focus", focus_border_hex),
            ("!focus", border_hex),
        ],
    }

    # For checkbuttons and radiobuttons, map indicator colours for states
    if widget_key in ("CHECKBOX", "RADIO", "SWITCH"):
        map_kwargs["indicatorcolor"] = [
            ("selected", bg_hex_normal),      # When checked, use variant colour
            ("!selected", TEXT_COLOUR_WHITE), # When unchecked, white
            ("disabled", DISABLED_FG_HEX),
        ]

    style.map(style_name, **map_kwargs)  # type: ignore[arg-type]

    CONTROL_STYLE_CACHE[style_name] = style_name

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("[G01f] Created control style: %s", style_name)
        logger.debug(
            "  Backgrounds → normal=%s, hover=%s, pressed=%s",
            bg_hex_normal,
            bg_hex_hover,
            bg_hex_pressed,
        )
        logger.debug("  Border → hex=%s, width=%s, relief=%s", border_hex, border_width, relief_token)
        logger.debug("———[G01f DEBUG END]—————————————————————————————")

    return style_name


# ====================================================================================================
# 7. CONVENIENCE HELPERS (SEMANTIC CONTROL ROLES)
# ----------------------------------------------------------------------------------------------------
# Simple wrappers around resolve_control_style() that provide commonly used
# semantic presets (primary/secondary buttons, status controls, etc.).
#
# Purpose:
#   - Reduce boilerplate when creating frequently-used control styles.
#   - Keep component construction clean.
#
# Notes:
#   - All helpers must defer to resolve_control_style() internally.
#   - No direct ttk.Style manipulation belongs here.
# ====================================================================================================
def control_button_primary() -> str:
    """
    Description:
        Primary button style for main actions.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses PRIMARY variant with white text for contrast on blue background.
    """
    return resolve_control_style(widget_type="BUTTON", variant="PRIMARY", fg_shade="WHITE")


def control_button_secondary() -> str:
    """
    Description:
        Secondary button style for auxiliary actions.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses SECONDARY variant.
    """
    return resolve_control_style(widget_type="BUTTON", variant="SECONDARY")


def control_button_success() -> str:
    """
    Description:
        Success button style for positive confirmations.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses SUCCESS variant with white text for contrast on green background.
    """
    return resolve_control_style(widget_type="BUTTON", variant="SUCCESS", fg_shade="WHITE")


def control_button_warning() -> str:
    """
    Description:
        Warning button style for cautionary actions.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses WARNING variant.
    """
    return resolve_control_style(widget_type="BUTTON", variant="WARNING")


def control_button_error() -> str:
    """
    Description:
        Error button style for destructive actions.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses ERROR (ERROR) variant with white text for contrast on red background.
    """
    return resolve_control_style(widget_type="BUTTON", variant="ERROR", fg_shade="WHITE")


def control_checkbox_primary() -> str:
    """
    Description:
        Primary checkbox style.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses PRIMARY variant.
    """
    return resolve_control_style(widget_type="CHECKBOX", variant="PRIMARY")


def control_checkbox_success() -> str:
    """
    Description:
        Success checkbox style for positive selections.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses SUCCESS variant.
    """
    return resolve_control_style(widget_type="CHECKBOX", variant="SUCCESS")


def control_radio_primary() -> str:
    """
    Description:
        Primary radio button style.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses PRIMARY variant.
    """
    return resolve_control_style(widget_type="RADIO", variant="PRIMARY")


def control_radio_warning() -> str:
    """
    Description:
        Warning radio button style.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses WARNING variant.
    """
    return resolve_control_style(widget_type="RADIO", variant="WARNING")


def control_switch_primary() -> str:
    """
    Description:
        Primary switch/toggle style.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses PRIMARY variant (Checkbutton layout).
    """
    return resolve_control_style(widget_type="SWITCH", variant="PRIMARY")


def control_switch_error() -> str:
    """
    Description:
        Error switch/toggle style for critical toggles.

    Args:
        None.

    Returns:
        str:
            Registered ttk style name.

    Raises:
        None.

    Notes:
        - Uses ERROR variant.
    """
    return resolve_control_style(widget_type="SWITCH", variant="ERROR")


# ====================================================================================================
# 8. CACHE INTROSPECTION
# ----------------------------------------------------------------------------------------------------
# Diagnostic functions for inspecting and managing the control style cache.
#
# Purpose:
#   - Enable runtime cache inspection for debugging.
#   - Support cache clearing for theme switching or testing.
# ====================================================================================================
def get_control_style_cache_info() -> dict[str, int | list[str]]:
    """
    Description:
        Return diagnostic information about the control-style cache.

    Args:
        None.

    Returns:
        dict[str, int | list[str]]:
            Dictionary containing:
            - "count": Number of cached styles.
            - "keys": List of all cached style names.

    Raises:
        None.

    Notes:
        - Useful for debugging and verifying cache behaviour.
    """
    return {
        "count": len(CONTROL_STYLE_CACHE),
        "keys": list(CONTROL_STYLE_CACHE.keys()),
    }


def clear_control_style_cache() -> None:
    """
    Description:
        Clear all entries from the control-style cache.

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
    CONTROL_STYLE_CACHE.clear()
    logger.info("[G01f] Cleared control style cache")


def debug_dump_button_styles() -> None:
    """
    Description:
        Log detailed diagnostic information about all registered button styles.
        Useful for verifying that background colours are correctly configured.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Outputs to logger at INFO level for visibility.
        - Shows theme, style names, and configured properties.
    """
    style = ttk.Style()
    current_theme = style.theme_use()

    logger.info("=" * 80)
    logger.info("G01f BUTTON STYLE DEBUG DUMP")
    logger.info("=" * 80)
    logger.info("Current theme: %s", current_theme)
    logger.info("Platform: %s", sys.platform)
    logger.info("Theme initialised: %s", is_gui_theme_initialised())
    logger.info("Cached styles: %d", len(CONTROL_STYLE_CACHE))
    logger.info("-" * 80)

    for cache_key, style_name in CONTROL_STYLE_CACHE.items():
        if "BUTTON" in cache_key:
            logger.info("Style: %s", style_name)
            try:
                bg = style.lookup(style_name, "background")
                fg = style.lookup(style_name, "foreground")
                bd = style.lookup(style_name, "borderwidth")
                relief = style.lookup(style_name, "relief")
                logger.info("  background: %s", bg)
                logger.info("  foreground: %s", fg)
                logger.info("  borderwidth: %s", bd)
                logger.info("  relief: %s", relief)

                # Show state mappings
                bg_map = style.map(style_name, "background")
                if bg_map:
                    logger.info("  background map: %s", bg_map)
            except Exception as exc:
                logger.warning("  (Error reading style: %s)", exc)

    logger.info("=" * 80)


# ====================================================================================================
# 9. PUBLIC API
# ----------------------------------------------------------------------------------------------------
# Expose the main control-style resolver along with convenience helpers.
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
    "resolve_control_style",
    # Button helpers
    "control_button_primary",
    "control_button_secondary",
    "control_button_success",
    "control_button_warning",
    "control_button_error",
    # Checkbox helpers
    "control_checkbox_primary",
    "control_checkbox_success",
    # Radio helpers
    "control_radio_primary",
    "control_radio_warning",
    # Switch helpers
    "control_switch_primary",
    "control_switch_error",
    # Cache introspection
    "get_control_style_cache_info",
    "clear_control_style_cache",
    "debug_dump_button_styles",
]


# ====================================================================================================
# 10. SELF-TEST
# ----------------------------------------------------------------------------------------------------
# Minimal manual smoke test for the control-style engine.
#
# Purpose:
#   - Validate ttk style creation in an isolated environment.
#   - Provide quick visual confirmation of button/checkbox/radio rendering.
#
# Notes:
#   - Not executed during normal imports.
#   - Wraps all behaviour in try/except/finally with proper logging.
# ====================================================================================================
if __name__ == "__main__":
    init_logging()
    logger.info("[G01f] Running G01f_control_styles self-test...")

    root = tk.Tk()
    root.title("G01f Control Styles — Self-test")

    try:
        frame = ttk.Frame(root, padding=SPACING_SCALE["MD"])
        frame.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Buttons
        ttk.Label(frame, text="Buttons:").grid(row=0, column=0, sticky="w", pady=(0, 5))

        btn_primary = ttk.Button(frame, text="Primary", style=control_button_primary())
        btn_secondary = ttk.Button(frame, text="Secondary", style=control_button_secondary())
        btn_success = ttk.Button(frame, text="Success", style=control_button_success())
        btn_warning = ttk.Button(frame, text="Warning", style=control_button_warning())
        btn_error = ttk.Button(frame, text="Error", style=control_button_error())

        btn_primary.grid(row=1, column=0, sticky="w", pady=SPACING_SCALE["XS"])
        btn_secondary.grid(row=2, column=0, sticky="w", pady=SPACING_SCALE["XS"])
        btn_success.grid(row=3, column=0, sticky="w", pady=SPACING_SCALE["XS"])
        btn_warning.grid(row=4, column=0, sticky="w", pady=SPACING_SCALE["XS"])
        btn_error.grid(row=5, column=0, sticky="w", pady=SPACING_SCALE["XS"])

        # Checkboxes
        ttk.Label(frame, text="Checkboxes:").grid(row=6, column=0, sticky="w", pady=(15, 5))

        chk_primary_var = tk.BooleanVar(value=True)
        chk_primary = ttk.Checkbutton(
            frame,
            text="Primary checkbox",
            style=control_checkbox_primary(),
            variable=chk_primary_var,
        )
        chk_primary.grid(row=7, column=0, sticky="w", pady=SPACING_SCALE["XS"])

        chk_success_var = tk.BooleanVar(value=False)
        chk_success = ttk.Checkbutton(
            frame,
            text="Success checkbox",
            style=control_checkbox_success(),
            variable=chk_success_var,
        )
        chk_success.grid(row=8, column=0, sticky="w", pady=SPACING_SCALE["XS"])

        # Radio buttons
        ttk.Label(frame, text="Radio buttons:").grid(row=9, column=0, sticky="w", pady=(15, 5))

        radio_var = tk.StringVar(value="primary")
        radio_primary = ttk.Radiobutton(
            frame,
            text="Primary radio",
            style=control_radio_primary(),
            value="primary",
            variable=radio_var,
        )
        radio_warning = ttk.Radiobutton(
            frame,
            text="Warning radio",
            style=control_radio_warning(),
            value="warning",
            variable=radio_var,
        )
        radio_primary.grid(row=10, column=0, sticky="w", pady=SPACING_SCALE["XS"])
        radio_warning.grid(row=11, column=0, sticky="w", pady=SPACING_SCALE["XS"])

        # Cache info
        logger.info("Cache info: %s", get_control_style_cache_info())

        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G01f self-test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G01f] Self-test complete.")