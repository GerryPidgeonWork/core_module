# ====================================================================================================
# G01c_widget_primitives.py
# ----------------------------------------------------------------------------------------------------
# Centralised widget *primitive* factory for the entire GUI framework.
#
# Purpose:
#   - Provide a unified, theme-aware construction layer for ALL widget types used
#     throughout the GUI. This module turns abstract “design tokens” (G01a) and
#     concrete ttk styles (G01b) into actual GUI widgets.
#
# Responsibilities:
#   • Supply consistent, DRY factory functions for:
#         - textual widgets     (labels, headings, subheadings, status labels)
#         - input widgets       (buttons, entries, textareas, comboboxes)
#         - choice controls     (checkboxes, radios, switches)
#         - structural widgets  (frames, spacers, dividers)
#   • Normalise geometry kwargs (padx/pady/ipadx/ipady) so layout utilities in G02a
#     can reliably apply placement rules.
#   • Apply theme defaults:
#         - fonts resolved by G01b_style_engine
#         - colours from G01a_style_config
#         - ttk styles from G01b_style_engine
#   • Translate tk/ttk differences for the few classic Tk widgets used (e.g. ScrolledText).
#   • Expose an object-oriented wrapper (UIPrimitives) for clean, readable page code.
#
# Integration:
#     from gui.G01c_widget_primitives import UIPrimitives
#
#     ui = UIPrimitives(root)
#     ui.heading(frame, "Title")
#     ui.entry(frame)
#     ui.checkbox(frame, "Enable feature", var)
#
# Relationship to Other G01 Modules:
#   - G01a_style_config:
#         Defines ALL theme constants (fonts, colours, spacing, tokens).
#
#   - G01b_style_engine:
#         Converts theme constants into ttk styles + named fonts.
#
#   - G01c_widget_primitives (THIS MODULE):
#         Builds the actual widgets, applying:
#             • style names from G01b
#             • layout abstraction from G02a
#
# CRITICAL RULES:
#   - No hard-coded colours/sizes for ttk widgets; all ttk appearance comes from styles.
#   - No direct ttk font/fg/bg overrides except where ttk does not support styles (e.g. tk.Text).
#   - No creation of windows or styles at import time — all configuration by callers.
#   - Geometry hints are stored as `widget.geometry_kwargs` and consumed later by G02a.
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
from gui.G00a_gui_packages import tk, ttk, tkFont, scrolledtext
from gui.G01a_style_config import (
    FRAME_SIZE_H,
    FRAME_SIZE_V,
    FRAME_PADDING,
    GUI_COLOUR_BG_PRIMARY,
    GUI_COLOUR_BG_TEXTAREA,
    TEXT_COLOUR_SECONDARY,
)
from gui.G01b_style_engine import (
    FONT_NAME_BASE,
    configure_ttk_styles,
)
from gui.G02a_layout_utils import attach_layout_helpers


# ====================================================================================================
# 3. INTERNAL HELPER FUNCTIONS (GEOMETRY, FONT, STYLE NORMALISATION)
# ----------------------------------------------------------------------------------------------------
# These helpers are internal in intent but named without underscores to comply with
# Global Coding Standards (no functions starting with an underscore).
# ====================================================================================================

def extract_geometry_kwargs(options: MutableMapping[str, Any]) -> Dict[str, Any]:
    """
    Extract geometry-related keyword arguments from a widget options mapping.

    Geometry keys (padx, pady, ipadx, ipady) are NOT passed into widget constructors.
    Instead, they are stored on the created widget as `widget.geometry_kwargs` so that
    layout utilities (G02a_layout_utils) can apply them consistently.

    Args:
        options (MutableMapping[str, Any]):
            Mapping of options that will be passed to the widget constructor.
            This mapping is modified in-place; geometry keys are removed.

    Returns:
        Dict[str, Any]:
            A dictionary containing only geometry-related keys.
            Example: {"padx": 4, "pady": 2}

    Notes:
        - Any unknown geometry-like keys are ignored safely.
        - Values are normalised to int where possible for consistency.
    """
    geometry_keys = ("padx", "pady", "ipadx", "ipady")
    geometry: Dict[str, Any] = {}

    for key in geometry_keys:
        if key in options:
            val = options.pop(key)

            # Normalise numeric values safely
            try:
                val = int(val)
            except Exception:
                pass

            geometry[key] = val

    logger.debug("[G01c] extract_geometry_kwargs: %r", geometry)
    return geometry


def get_tk_body_font() -> str | None:
    """
    Determine a Tk font to use for classic Tk widgets (e.g. ScrolledText).

    Behaviour:
        - Prefer the named base font from G01b_style_engine (FONT_NAME_BASE) if it
          has been created via configure_ttk_styles(..).
        - If the named font is not yet registered, fall back to 'TkDefaultFont'.
        - Any errors during lookup fall back to None, allowing Tk to choose defaults.

    Returns:
        str | None:
            Name of a Tk named font to apply to tk-based widgets, or None to allow
            Tk to choose its own default font.
    """
    try:
        if FONT_NAME_BASE:
            try:
                tkFont.nametofont(FONT_NAME_BASE)  # type: ignore[name-defined]
                logger.debug("[G01c] get_tk_body_font: using named font %s", FONT_NAME_BASE)
                return FONT_NAME_BASE
            except Exception:
                logger.debug(
                    "[G01c] get_tk_body_font: named font %s not registered yet; "
                    "falling back to TkDefaultFont.",
                    FONT_NAME_BASE,
                )

        try:
            tkFont.nametofont("TkDefaultFont")  # type: ignore[name-defined]
            logger.debug("[G01c] get_tk_body_font: using 'TkDefaultFont'.")
            return "TkDefaultFont"
        except Exception:
            logger.debug(
                "[G01c] get_tk_body_font: 'TkDefaultFont' not available; letting Tk choose."
            )

    except Exception as exc:
        logger.debug("[G01c] get_tk_body_font: error during font resolution: %s", exc)

    return None


def strip_colour_and_font_kwargs(options: MutableMapping[str, Any]) -> None:
    """
    Remove direct colour and font overrides from a ttk widget options mapping.

    Purpose:
        - Enforce that all ttk widgets derive appearance from ttk styles defined
          in G01b_style_engine, rather than from per-widget overrides.
        - Remove tk-style aliases (fg/bg) and ttk equivalents (foreground/background,
          font) to keep visual configuration centralised.

    Args:
        options (MutableMapping[str, Any]):
            Mapping of options passed to a widget constructor. Modified in-place.

    Returns:
        None.
    """
    for bad in ("fg", "bg", "foreground", "background", "font"):
        if bad in options:
            logger.debug(
                "[G01c] strip_colour_and_font_kwargs: dropping option %s=%r",
                bad,
                options[bad],
            )
            options.pop(bad, None)


def normalise_label_style_name(
    style_name: str,
    *,
    category_hint: str | None = None,
    surface_hint: str | None = None,
    weight_hint: str | None = None,
) -> str:
    """
    Normalise ttk.Label style names into the canonical format used by G01b.

    Canonical patterns:
        Body labels:
            "{Surface}.{Weight}.TLabel"
        Other label categories:
            "{Surface}.{Category}.{Weight}.TLabel"

    Examples repaired:
        - "WindowHeading.Primary.Bold.TLabel"
              → "Primary.WindowHeading.Bold.TLabel"
        - "Heading.Secondary.TLabel"        (no weight)
              → "Secondary.Heading.Bold.TLabel"
        - "Primary.SectionHeading.TLabel"   (no weight)
              → "Primary.SectionHeading.Bold.TLabel"

    Non-label styles (not ending in ".TLabel") are returned unchanged.

    Args:
        style_name (str):
            Raw style name provided by the caller.
        category_hint (str | None):
            Optional semantic category hint (Body, Heading, SectionHeading, etc.).
        surface_hint (str | None):
            Optional Surface hint (Primary/Secondary).
        weight_hint (str | None):
            Optional Weight hint (Normal/Bold).

    Returns:
        str:
            Canonicalised style name safe for lookup in the G01b style engine.
    """
    if not style_name.endswith(".TLabel"):
        return style_name

    # Strip suffix and split into tokens (e.g. "WindowHeading.Primary.Bold")
    base = style_name[:-len(".TLabel")]
    parts = [p for p in base.split(".") if p]

    surfaces = {"Primary", "Secondary"}
    weights = {"Normal", "Bold"}
    categories = set(LABEL_CATEGORIES)

    found_surface: str | None = None
    found_weight: str | None = None
    found_category: str | None = None

    for token in parts:
        if token in surfaces:
            found_surface = token
        elif token in weights:
            found_weight = token
        elif token in categories:
            found_category = token

    # Fallbacks from hints or sensible defaults
    surface = found_surface or surface_hint or "Primary"
    weight = found_weight or weight_hint or "Bold"
    category = found_category or category_hint or "Body"

    # Normalise category for Body (2-part scheme) vs others (3-part scheme)
    if category == "Body":
        canonical = f"{surface}.{weight}.TLabel"
    else:
        canonical = f"{surface}.{category}.{weight}.TLabel"

    if canonical != style_name:
        logger.debug(
            "[G01c] normalise_label_style_name: repaired %r → %r "
            "(surface=%s, category=%s, weight=%s)",
            style_name,
            canonical,
            surface,
            category,
            weight,
        )

    return canonical


# ====================================================================================================
# 4. TEXTUAL WIDGET PRIMITIVES
# ----------------------------------------------------------------------------------------------------
# Core primitives for rendering text: labels, headings, subheadings, and status messages.
# These are the foundation for most static and dynamic text in the GUI.
#
# IMPORTANT:
#   - All ttk visual appearance (font, colours, padding) is provided by styles
#     defined in G01b_style_engine.
#   - These primitives only set the style name (with override support) and logical
#     options such as `text=`.
#
# Label style matrix (from G01b):
#   • Primary.Normal.TLabel          – BASE_FONT, primary background
#   • Secondary.Normal.TLabel        – BASE_FONT, secondary background
#   • Primary.Bold.TLabel            – BOLD_FONT, primary background
#   • Secondary.Bold.TLabel          – BOLD_FONT, secondary background
#
# Heading system (5-tier):
#   • WindowHeading.TLabel           – Top of window/page
#   • Primary.Heading.TLabel         – Major heading (primary surface)
#   • Secondary.Heading.TLabel       – Major heading (secondary/card surface)
#   • Primary.SectionHeading.TLabel  – Section heading (primary surface)
#   • Secondary.SectionHeading.TLabel– Section heading (secondary/card surface)
#
# make_label(...) is the generic builder; UIPrimitives will expose wrappers.
# ====================================================================================================

# ----------------------------------------------------------------------------------------------------
# Valid parameter values (for validation and documentation)
# ----------------------------------------------------------------------------------------------------
LABEL_CATEGORIES = (
    "Body",
    "Heading",
    "SectionHeading",
    "WindowHeading",
    "Card",
    "Success",
    "Warning",
    "Error",
)
LABEL_SURFACES = ("Primary", "Secondary")
LABEL_WEIGHTS = ("Normal", "Bold")


def make_label(
    parent: tk.Misc,
    text: str = "",
    *,
    category: str = "Body",
    surface: str = "Primary",
    weight: str = "Normal",
    style: str | None = None,
    **kwargs: Any,
) -> ttk.Label:  # type: ignore[name-defined]
    """
    Create a themed ttk Label with style derived from semantic parameters.

    Description:
        Unified factory for all label types. The ttk style name is constructed
        dynamically from category, surface, and weight parameters, ensuring
        consistency with the G01b style matrix.

        Any explicit or legacy style name passed via `style=` or kwargs["style"]
        is automatically normalised into the canonical G01b format, so older
        code such as "WindowHeading.Primary.Bold.TLabel" continues to work and
        maps to "Primary.WindowHeading.Bold.TLabel".

    Args:
        parent (tk.Misc):
            Parent container widget.
        text (str):
            Label text content.
        category (str):
            Semantic label type. One of: Body, Heading, SectionHeading,
            WindowHeading, Card, Success, Warning, Error. Default: "Body".
        surface (str):
            Background surface context. One of: Primary, Secondary.
            Default: "Primary".
        weight (str):
            Font weight. One of: Normal, Bold. Default: "Normal".
        style (str | None):
            Explicit style override. If provided, category/surface/weight
            are used as hints for normalisation. Default: None.
        **kwargs (Any):
            Additional ttk.Label options (e.g., anchor, justify, wraplength).

    Returns:
        ttk.Label:
            The created label widget with .geometry_kwargs metadata attached.

    Raises:
        None.

    Notes:
        - Geometry kwargs (padx, pady, ipadx, ipady) are extracted and stored
          on widget.geometry_kwargs for layout utilities (G02a).
        - Direct colour/font kwargs are stripped to enforce style-only appearance.
        - Canonical style name format:
            Body:  "{Surface}.{Weight}.TLabel"
            Other: "{Surface}.{Category}.{Weight}.TLabel"
    """
    geometry = extract_geometry_kwargs(kwargs)
    strip_colour_and_font_kwargs(kwargs)

    # Build base style name from parameters (if no explicit override is given)
    if style is not None:
        style_name = style
    elif category == "Body":
        style_name = f"{surface}.{weight}.TLabel"
    else:
        style_name = f"{surface}.{category}.{weight}.TLabel"

    # Allow style in kwargs to override (legacy usage), then normalise
    raw_style_from_kwargs = kwargs.pop("style", None)
    if raw_style_from_kwargs is not None:
        style_name = raw_style_from_kwargs

    style_name = normalise_label_style_name(
        style_name,
        category_hint=category,
        surface_hint=surface,
        weight_hint=weight,
    )

    options: Dict[str, Any] = {
        "text": text,
        "style": style_name,
    }
    options.update(kwargs)

    logger.debug(
        "[G01c] make_label: text=%r category=%s surface=%s weight=%s style=%s geometry=%r",
        text,
        category,
        surface,
        weight,
        style_name,
        geometry,
    )

    widget: ttk.Label = ttk.Label(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


# ----------------------------------------------------------------------------------------------------
# LEGACY WRAPPER FUNCTIONS (Backward Compatibility)
# ----------------------------------------------------------------------------------------------------
# These functions wrap make_label() with appropriate category/surface/weight parameters.
# They are retained for backward compatibility but new code should use make_label() directly.
# ----------------------------------------------------------------------------------------------------

def make_heading(parent: tk.Misc, text: str, **kwargs: Any) -> ttk.Label:  # type: ignore[name-defined]
    """
    Create a window-level heading.

    Description:
        Legacy wrapper for make_label() with category="WindowHeading".
        New code should use make_label() directly.

    Args:
        parent (tk.Misc):
            Parent container widget.
        text (str):
            Heading text.
        **kwargs (Any):
            Optional ttk.Label override parameters (anchor, justify, surface, weight).

    Returns:
        ttk.Label:
            The created top-level heading label with .geometry_kwargs.

    Raises:
        None.

    Notes:
        Default style: "Primary.WindowHeading.Bold.TLabel"
    """
    surface = kwargs.pop("surface", "Primary")
    weight = kwargs.pop("weight", "Bold")
    return make_label(parent, text, category="WindowHeading", surface=surface, weight=weight, **kwargs)


def make_section_heading(
    parent: tk.Misc,
    text: str,
    *,
    style: str | None = None,
    **kwargs: Any,
) -> ttk.Label:  # type: ignore[name-defined]
    """
    Create a section-level heading.

    Description:
        Legacy wrapper for make_label() with category="SectionHeading".
        New code should use make_label() directly.

    Args:
        parent (tk.Misc):
            Parent widget.
        text (str):
            Section heading text.
        style (str | None):
            Optional explicit style override.
        **kwargs (Any):
            Additional ttk.Label options (surface, weight, anchor, etc.).

    Returns:
        ttk.Label:
            Section heading widget with .geometry_kwargs metadata.

    Raises:
        None.

    Notes:
        Default style: "Primary.SectionHeading.Bold.TLabel"
    """
    if style is not None:
        return make_label(parent, text, category="SectionHeading", style=style, **kwargs)
    surface = kwargs.pop("surface", "Primary")
    weight = kwargs.pop("weight", "Bold")
    return make_label(parent, text, category="SectionHeading", surface=surface, weight=weight, **kwargs)


def make_subheading(parent: tk.Misc, text: str, **kwargs: Any) -> ttk.Label:  # type: ignore[name-defined]
    """
    Create a subheading inside a section or panel.

    Description:
        Legacy wrapper for make_label() with category="SectionHeading".
        Functionally identical to make_section_heading(). New code should use
        make_label() directly.

    Args:
        parent (tk.Misc):
            Parent container.
        text (str):
            Subheading text.
        **kwargs (Any):
            Optional ttk.Label overrides (surface, weight, anchor, etc.).

    Returns:
        ttk.Label:
            Subheading label with .geometry_kwargs metadata.

    Raises:
        None.

    Notes:
        Default style: "Primary.SectionHeading.Bold.TLabel"
    """
    surface = kwargs.pop("surface", "Primary")
    weight = kwargs.pop("weight", "Bold")
    return make_label(parent, text, category="SectionHeading", surface=surface, weight=weight, **kwargs)


def make_card_label(
    parent: tk.Misc,
    text: str,
    **kwargs: Any,
) -> ttk.Label:  # type: ignore[name-defined]
    """
    Create a label designed for use inside Card.TFrame containers.

    Description:
        Legacy wrapper for make_label() with category="Card".
        New code should use make_label() directly.

    Args:
        parent (tk.Misc):
            Card container widget.
        text (str):
            Label text.
        **kwargs (Any):
            Optional ttk.Label overrides (surface, weight, anchor, etc.).

    Returns:
        ttk.Label:
            Card-surface label with .geometry_kwargs metadata.

    Raises:
        None.

    Notes:
        Default style: "Secondary.Card.Normal.TLabel"
        Cards typically use Secondary surface as they have a distinct background.
    """
    surface = kwargs.pop("surface", "Secondary")
    weight = kwargs.pop("weight", "Normal")
    return make_label(parent, text, category="Card", surface=surface, weight=weight, **kwargs)


def make_status_label(
    parent: tk.Misc,
    text: str = "",
    status: str = "info",
    **kwargs: Any,
) -> ttk.Label:  # type: ignore[name-defined]
    """
    Create a label for dynamic status/feedback messages.

    Description:
        Legacy wrapper for make_label() with category derived from status parameter.
        New code should use make_label() directly with appropriate category.

    Args:
        parent (tk.Misc):
            Parent container widget.
        text (str):
            Status text to display.
        status (str):
            One of: "info", "success", "warning", "error".
        **kwargs (Any):
            Optional ttk.Label overrides (surface, weight, anchor, etc.).

    Returns:
        ttk.Label:
            Status label with .geometry_kwargs metadata.

    Raises:
        None.

    Notes:
        Status to category mapping:
            - info    → Body   (uses "{Surface}.Normal.TLabel")
            - success → Success
            - warning → Warning
            - error   → Error
    """
    surface = kwargs.pop("surface", "Primary")
    weight = kwargs.pop("weight", "Normal")

    status_to_category = {
        "info": "Body",
        "success": "Success",
        "warning": "Warning",
        "error": "Error",
    }
    category = status_to_category.get(status, "Body")

    return make_label(parent, text, category=category, surface=surface, weight=weight, **kwargs)


# ====================================================================================================
# 5. INPUT WIDGET PRIMITIVES
# ----------------------------------------------------------------------------------------------------
# Widgets that accept user input: buttons, single-line entries, multi-line text areas,
# and comboboxes.
#
# IMPORTANT:
#   • ttk widgets (Button, Entry, Combobox) derive ALL visual appearance from the
#     ttk style engine (G01b_style_engine). No ttk widget may receive direct bg/fg/font.
#   • Text areas use classic Tk widgets (ScrolledText) and therefore may apply
#     colour/font tokens directly from G01a_style_config.
#   • Geometry kwargs (padx/pady/ipadx/ipady) are removed and stored as
#       widget.geometry_kwargs
#     so layout rules (G02a) can apply them consistently.
# ====================================================================================================

def make_button(parent: tk.Misc, text: str = "", **kwargs: Any) -> ttk.Button:  # type: ignore[name-defined]
    """
    Create a themed push button.

    Default style:
        - "Primary.TButton"

    Other available semantic styles (from G01b_style_engine):
        - "Secondary.TButton"
        - "Success.TButton"
        - "Warning.TButton"
        - "Danger.TButton"

    Geometry kwargs are stored in .geometry_kwargs.
    Direct colour/font overrides (bg/fg/foreground/background/font) are removed.

    Args:
        parent (tk.Misc):
            Parent container widget.
        text (str):
            Button label text.
        **kwargs (Any):
            Additional ttk.Button options (e.g. command=..., style=...).

    Returns:
        ttk.Button:
            The created button with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    callback = kwargs.pop("command", None)
    style_name = kwargs.pop("style", "Primary.TButton")
    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {
        "text": text,
        "style": style_name,
    }
    if callback is not None:
        options["command"] = callback

    options.update(kwargs)

    logger.debug(
        "[G01c] make_button: text=%r style=%s options=%r geometry=%r",
        text, style_name, options, geometry,
    )
    widget: ttk.Button = ttk.Button(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


def make_entry(parent: tk.Misc, **kwargs: Any) -> ttk.Entry:  # type: ignore[name-defined]
    """
    Create a themed single-line text entry.

    Default style:
        - "TEntry"

    Direct colours/fonts are stripped to enforce style-driven appearance.

    Args:
        parent (tk.Misc):
            Parent container widget.
        **kwargs (Any):
            Additional ttk.Entry options.

    Returns:
        ttk.Entry:
            Entry widget with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    style_name = kwargs.pop("style", "TEntry")
    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {"style": style_name}
    options.update(kwargs)

    logger.debug(
        "[G01c] make_entry: style=%s options=%r geometry=%r",
        style_name, options, geometry,
    )
    widget: ttk.Entry = ttk.Entry(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


def make_textarea(parent: tk.Misc, **kwargs: Any) -> "scrolledtext.ScrolledText":  # type: ignore[name-defined]
    """
    Create a scrolled multi-line text area.

    This uses the classic Tk ScrolledText widget (NOT ttk), so it cannot consume ttk
    styles. Instead it uses semantic tokens from G01a_style_config:
        - GUI_COLOUR_BG_TEXTAREA
        - TEXT_COLOUR_SECONDARY
        - FONT_NAME_BASE (if registered)

    Args:
        parent (tk.Misc):
            Parent container widget.
        **kwargs (Any):
            ScrolledText options (height, width, wrap, etc.).

    Returns:
        scrolledtext.ScrolledText:
            Textarea widget with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    default_font = get_tk_body_font()
    default_wrap = kwargs.pop("wrap", "word")

    # Convert ttk-style fg/bg to Tk equivalents
    if "foreground" in kwargs and "fg" not in kwargs:
        kwargs["fg"] = kwargs.pop("foreground")
    if "background" in kwargs and "bg" not in kwargs:
        kwargs["bg"] = kwargs.pop("background")

    options: Dict[str, Any] = {
        "wrap": default_wrap,
        "fg": kwargs.pop("fg", TEXT_COLOUR_SECONDARY),
        "bg": kwargs.pop("bg", GUI_COLOUR_BG_TEXTAREA),
    }
    if default_font is not None:
        options["font"] = default_font

    options.update(kwargs)

    logger.debug("[G01c] make_textarea: options=%r geometry=%r", options, geometry)
    widget = scrolledtext.ScrolledText(parent, **options)  # type: ignore[name-defined]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


def make_combobox(
    parent: tk.Misc,
    values: Optional[list[Any]] = None,
    **kwargs: Any,
) -> ttk.Combobox:  # type: ignore[name-defined]
    """
    Create a themed Combobox.

    Default style:
        - "TCombobox"

    Args:
        parent (tk.Misc):
            Parent container.
        values (Optional[list[Any]]):
            List of dropdown values.
        **kwargs (Any):
            Additional ttk.Combobox options.

    Returns:
        ttk.Combobox:
            Combobox with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    if values is not None and "values" not in kwargs:
        kwargs["values"] = values

    style_name = kwargs.pop("style", "TCombobox")
    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {"style": style_name}
    options.update(kwargs)

    logger.debug(
        "[G01c] make_combobox: style=%s options=%r geometry=%r",
        style_name, options, geometry,
    )
    widget: ttk.Combobox = ttk.Combobox(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


# ====================================================================================================
# 6. CHOICE CONTROL PRIMITIVES
# ----------------------------------------------------------------------------------------------------
# Boolean and single-choice controls: checkboxes, radio buttons, and switches.
#
# IMPORTANT:
#   • These widgets derive ALL visual appearance from ttk styles defined in
#       G01b_style_engine (e.g. TCheckbutton, TRadiobutton).
#   • Direct colour/font overrides (bg/fg/foreground/background/font) are removed
#     to enforce style-driven appearance.
#   • Geometry kwargs (padx/pady/ipadx/ipady) are extracted and stored on the widget
#     as widget.geometry_kwargs for layout utilities (G02a).
#
# Styles supported (from G01b):
#   - "TCheckbutton"
#   - "TRadiobutton"
#   - Any future semantic variants (e.g., "Primary.TCheckbutton") via style override.
# ----------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------
# CHECKBOX
# ----------------------------------------------------------------------------------------------------

@overload
def make_checkbox(
    parent: tk.Misc,
    text: str,
    variable: tk.Variable,  # type: ignore[name-defined]
    *,
    command: Callable[[], Any],
    **kwargs: Any,
) -> ttk.Checkbutton:  # type: ignore[name-defined]
    ...


@overload
def make_checkbox(
    parent: tk.Misc,
    text: str,
    variable: tk.Variable,  # type: ignore[name-defined]
    *,
    command: None = None,
    **kwargs: Any,
) -> ttk.Checkbutton:  # type: ignore[name-defined]
    ...


def make_checkbox(
    parent: tk.Misc,
    text: str,
    variable: tk.Variable,  # type: ignore[name-defined]
    *,
    command: Optional[Callable[[], Any]] = None,
    **kwargs: Any,
) -> ttk.Checkbutton:  # type: ignore[name-defined]
    """
    Create a themed Checkbutton used for boolean toggles.

    Default style:
        - "TCheckbutton"

    Args:
        parent (tk.Misc):
            Parent widget.
        text (str):
            Label text.
        variable (tk.Variable):
            Linked Tk variable (BooleanVar / IntVar).
        command (Optional[Callable]):
            Optional callback when toggled.
        **kwargs:
            Additional ttk.Checkbutton options.

    Returns:
        ttk.Checkbutton:
            Created checkbox with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    style_name = kwargs.pop("style", "TCheckbutton")
    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {
        "text": text,
        "variable": variable,
        "style": style_name,
    }
    if command is not None:
        options["command"] = command

    options.update(kwargs)

    logger.debug(
        "[G01c] make_checkbox: text=%r style=%s options=%r geometry=%r",
        text, style_name, options, geometry,
    )
    widget: ttk.Checkbutton = ttk.Checkbutton(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


# ----------------------------------------------------------------------------------------------------
# RADIO BUTTON
# ----------------------------------------------------------------------------------------------------

@overload
def make_radio(
    parent: tk.Misc,
    text: str,
    variable: tk.Variable,  # type: ignore[name-defined]
    value: Any,
    *,
    command: Callable[[], Any],
    **kwargs: Any,
) -> ttk.Radiobutton:  # type: ignore[name-defined]
    ...


@overload
def make_radio(
    parent: tk.Misc,
    text: str,
    variable: tk.Variable,  # type: ignore[name-defined]
    value: Any,
    *,
    command: None = None,
    **kwargs: Any,
) -> ttk.Radiobutton:  # type: ignore[name-defined]
    ...


def make_radio(
    parent: tk.Misc,
    text: str,
    variable: tk.Variable,  # type: ignore[name-defined]
    value: Any,
    *,
    command: Optional[Callable[[], Any]] = None,
    **kwargs: Any,
) -> ttk.Radiobutton:  # type: ignore[name-defined]
    """
    Create a themed Radiobutton for mutually exclusive choices.

    Default style:
        - "TRadiobutton"

    Args:
        parent (tk.Misc):
            Parent container widget.
        text (str):
            Label text.
        variable (tk.Variable):
            Shared Tk variable for the radio group.
        value (Any):
            The value this radio button represents.
        command (Optional[Callable]):
            Callback when selection changes.
        **kwargs:
            Additional ttk.Radiobutton options.

    Returns:
        ttk.Radiobutton:
            Created radio button with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    style_name = kwargs.pop("style", "TRadiobutton")
    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {
        "text": text,
        "variable": variable,
        "value": value,
        "style": style_name,
    }
    if command is not None:
        options["command"] = command

    options.update(kwargs)

    logger.debug(
        "[G01c] make_radio: text=%r value=%r style=%s options=%r geometry=%r",
        text, value, style_name, options, geometry,
    )
    widget: ttk.Radiobutton = ttk.Radiobutton(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


# ----------------------------------------------------------------------------------------------------
# SWITCH (CHECKBUTTON VARIANT)
# ----------------------------------------------------------------------------------------------------

@overload
def make_switch(
    parent: tk.Misc,
    text: str,
    variable: tk.Variable,  # type: ignore[name-defined]
    *,
    command: Callable[[], Any],
    **kwargs: Any,
) -> ttk.Checkbutton:  # type: ignore[name-defined]
    ...


@overload
def make_switch(
    parent: tk.Misc,
    text: str,
    variable: tk.Variable,  # type: ignore[name-defined]
    *,
    command: None = None,
    **kwargs: Any,
) -> ttk.Checkbutton:  # type: ignore[name-defined]
    ...


def make_switch(
    parent: tk.Misc,
    text: str,
    variable: tk.Variable,  # type: ignore[name-defined]
    *,
    command: Optional[Callable[[], Any]] = None,
    **kwargs: Any,
) -> ttk.Checkbutton:  # type: ignore[name-defined]
    """
    Create a switch-style toggle control.

    Default behaviour:
        - Uses "TCheckbutton" style unless overridden.
        - Works identically to a checkbox unless a specialised style is assigned
          (e.g., a Switch.TCheckbutton from ttkbootstrap or custom G01b styles).

    Args:
        parent (tk.Misc):
            Parent widget.
        text (str):
            Switch label.
        variable (tk.Variable):
            BooleanVar / IntVar linked to toggle state.
        command (Optional[Callable]):
            Callback when toggled.
        **kwargs:
            Additional ttk.Checkbutton options.

    Returns:
        ttk.Checkbutton:
            Switch widget with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    style_name = kwargs.pop("style", "TCheckbutton")
    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {
        "text": text,
        "variable": variable,
        "style": style_name,
    }
    if command is not None:
        options["command"] = command

    options.update(kwargs)

    logger.debug(
        "[G01c] make_switch: text=%r style=%s options=%r geometry=%r",
        text, style_name, options, geometry,
    )
    widget: ttk.Checkbutton = ttk.Checkbutton(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


# ====================================================================================================
# 7A. STRUCTURAL WIDGET PRIMITIVES
# ----------------------------------------------------------------------------------------------------
# Low-level containers that support layout and visual separation:
#   • Frames      → generic structural containers (Primary, Secondary, Card, etc.)
#   • Dividers    → 1px separators between content blocks
#   • Spacers     → fixed vertical breathing room
#
# IMPORTANT:
#   • ttk Frames derive ALL appearance from ttk styles defined in G01b_style_engine.
#   • No direct fg/bg/font overrides are allowed — always style-driven.
#   • Geometry kwargs (padx/pady/ipadx/ipady) are extracted and stored as
#       widget.geometry_kwargs for G02 layout utilities.
# ----------------------------------------------------------------------------------------------------

def make_frame(parent: tk.Misc, **kwargs: Any) -> ttk.Frame:  # type: ignore[name-defined]
    """
    Create a themed structural frame container.

    Default style:
        - "TFrame" (generic themed container)

    Used for:
        • Form sections
        • Layout blocks
        • Containers for labels, entries, controls

    Args:
        parent (tk.Misc):
            Parent container widget.
        **kwargs:
            Additional Frame options (style override, padding, etc.).

    Returns:
        ttk.Frame:
            The created frame with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    style_name = kwargs.pop("style", "TFrame")
    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {"style": style_name}
    options.update(kwargs)

    logger.debug(
        "[G01c] make_frame: style=%s options=%r geometry=%r",
        style_name, options, geometry,
    )
    widget: ttk.Frame = ttk.Frame(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


def make_divider(
    parent: tk.Misc,
    *,
    height: int = 1,
    style: Optional[str] = None,
    **kwargs: Any,
) -> ttk.Frame:  # type: ignore[name-defined]
    """
    Create a 1px visual divider line between content groups.

    Default style:
        - "ToolbarDivider.TFrame"
          (configured in G01b_style_engine to use GUI_COLOUR_DIVIDER)

    Notes:
        • Implemented as a ttk.Frame so the background colour is style-driven.
        • Height defaults to 1px (modern thin divider).
        • Caller may override style (e.g., "Card.Divider.TFrame").

    Args:
        parent (tk.Misc):
            Parent widget.
        height (int):
            Divider thickness in pixels.
        style (Optional[str]):
            Optional ttk style override.
        **kwargs:
            Additional Frame options (no direct fg/bg overrides allowed).

    Returns:
        ttk.Frame:
            Divider frame with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    style_name = style or "ToolbarDivider.TFrame"
    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {
        "height": height,
        "style": style_name,
    }
    options.update(kwargs)

    logger.debug(
        "[G01c] make_divider: style=%s options=%r geometry=%r",
        style_name, options, geometry,
    )
    widget: ttk.Frame = ttk.Frame(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


def make_spacer(
    parent: tk.Misc,
    height: int = 8,
    **kwargs: Any,
) -> ttk.Frame:  # type: ignore[name-defined]
    """
    Create a vertical spacer used to introduce breathing room.

    Default style:
        - "TFrame" (so background matches container)

    Notes:
        • Spacers avoid embedding magic numbers inside pack/grid calls.
        • Height controls visual rhythm in stacked layouts.

    Args:
        parent (tk.Misc):
            Parent container.
        height (int):
            Spacer height in pixels (default=8).
        **kwargs:
            Optional Frame options (style override, etc.).

    Returns:
        ttk.Frame:
            Spacer frame with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    style_name = kwargs.pop("style", "TFrame")
    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {
        "height": height,
        "style": style_name,
    }
    options.update(kwargs)

    logger.debug(
        "[G01c] make_spacer: style=%s height=%s options=%r geometry=%r",
        style_name, height, options, geometry,
    )
    widget: ttk.Frame = ttk.Frame(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


# ----------------------------------------------------------------------------------------------------
# LAYOUT CONTAINER PRIMITIVES
# ----------------------------------------------------------------------------------------------------
# These factories create pre-configured container frames for common layout patterns.
# Unlike raw frames, they have semantic roles and sensible defaults.
#
# USAGE PATTERN:
#   container = make_button_bar(parent)
#   make_button(container, "Cancel", style="Secondary.TButton").pack(side="right")
#   make_button(container, "Save").pack(side="right", padx=(8, 0))
#   container.pack(fill="x", side="bottom")
# ----------------------------------------------------------------------------------------------------

def make_button_bar(
    parent: tk.Misc,
    *,
    style: str = "TFrame",
    **kwargs: Any,
) -> ttk.Frame:  # type: ignore[name-defined]
    """
    Create a container frame for horizontal button layouts.

    Provides a semantic container for action buttons (Save, Cancel, etc.).
    Buttons should be created as children of this container and packed
    with side="right" or side="left".

    Default style:
        - "TFrame" (inherits parent background)

    Args:
        parent (tk.Misc):
            Parent widget.
        style (str):
            Optional ttk style override.
        **kwargs:
            Additional Frame options.

    Returns:
        ttk.Frame:
            Button bar container with:
                - .geometry_kwargs: Extracted geometry hints
                - .g01c_role: "button_bar" (semantic identifier)

    Example:
        bar = make_button_bar(form_frame)
        make_button(bar, "Cancel", style="Secondary.TButton").pack(side="right")
        make_button(bar, "Save").pack(side="right", padx=(8, 0))
        bar.pack(fill="x", side="bottom", pady=(12, 0))
    """
    geometry = extract_geometry_kwargs(kwargs)

    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {"style": style}
    options.update(kwargs)

    logger.debug(
        "[G01c] make_button_bar: style=%s options=%r geometry=%r",
        style, options, geometry,
    )
    widget: ttk.Frame = ttk.Frame(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    widget.g01c_role = "button_bar"  # type: ignore[attr-defined]
    return widget


def make_horizontal_group(
    parent: tk.Misc,
    *,
    style: str = "TFrame",
    **kwargs: Any,
) -> ttk.Frame:  # type: ignore[name-defined]
    """
    Create a container for horizontally arranged widgets.

    Children should be packed with side="left" and appropriate padx for spacing.

    Default style:
        - "TFrame"

    Args:
        parent (tk.Misc):
            Parent widget.
        style (str):
            Optional ttk style override.
        **kwargs:
            Additional Frame options.

    Returns:
        ttk.Frame:
            Horizontal group container with:
                - .geometry_kwargs: Extracted geometry hints
                - .g01c_role: "horizontal_group"

    Example:
        row = make_horizontal_group(content)
        make_label(row, "Status:", category="Body", weight="Bold").pack(side="left")
        make_label(row, "Connected", category="Body").pack(side="left", padx=(4, 0))
        row.pack(anchor="w")
    """
    geometry = extract_geometry_kwargs(kwargs)

    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {"style": style}
    options.update(kwargs)

    logger.debug(
        "[G01c] make_horizontal_group: style=%s options=%r geometry=%r",
        style, options, geometry,
    )
    widget: ttk.Frame = ttk.Frame(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    widget.g01c_role = "horizontal_group"  # type: ignore[attr-defined]
    return widget


def make_vertical_group(
    parent: tk.Misc,
    *,
    style: str = "TFrame",
    **kwargs: Any,
) -> ttk.Frame:  # type: ignore[name-defined]
    """
    Create a container for vertically stacked widgets.

    Children should be packed with side="top" or anchor="w" and appropriate pady.

    Default style:
        - "TFrame"

    Args:
        parent (tk.Misc):
            Parent widget.
        style (str):
            Optional ttk style override.
        **kwargs:
            Additional Frame options.

    Returns:
        ttk.Frame:
            Vertical group container with:
                - .geometry_kwargs: Extracted geometry hints
                - .g01c_role: "vertical_group"

    Example:
        col = make_vertical_group(sidebar)
        make_label(col, "Dashboard", category="Body").pack(anchor="w")
        make_label(col, "Settings", category="Body").pack(anchor="w", pady=(4, 0))
        col.pack(fill="y")
    """
    geometry = extract_geometry_kwargs(kwargs)

    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {"style": style}
    options.update(kwargs)

    logger.debug(
        "[G01c] make_vertical_group: style=%s options=%r geometry=%r",
        style, options, geometry,
    )
    widget: ttk.Frame = ttk.Frame(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    widget.g01c_role = "vertical_group"  # type: ignore[attr-defined]
    return widget


def make_card(
    parent: tk.Misc,
    *,
    style: str = "Card.TFrame",
    **kwargs: Any,
) -> ttk.Frame:  # type: ignore[name-defined]
    """
    Create a styled card container with distinct background.

    Cards are used to visually group related content with a secondary
    background colour. Content inside should use Secondary surface labels.

    Default style:
        - "Card.TFrame" (uses GUI_COLOUR_BG_SECONDARY from G01a)

    Args:
        parent (tk.Misc):
            Parent widget.
        style (str):
            Optional ttk style override.
        **kwargs:
            Additional Frame options (e.g., padding).

    Returns:
        ttk.Frame:
            Card container with:
                - .geometry_kwargs: Extracted geometry hints
                - .g01c_role: "card"

    Example:
        card = make_card(content, padding=12)
        make_label(card, "User Info", category="SectionHeading", surface="Secondary").pack(anchor="w")
        make_label(card, "Name: John", category="Body", surface="Secondary").pack(anchor="w")
        card.pack(fill="x", pady=(8, 0))
    """
    geometry = extract_geometry_kwargs(kwargs)

    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {"style": style}
    options.update(kwargs)

    logger.debug(
        "[G01c] make_card: style=%s options=%r geometry=%r",
        style, options, geometry,
    )
    widget: ttk.Frame = ttk.Frame(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    widget.g01c_role = "card"  # type: ignore[attr-defined]
    return widget


def make_sidebar(
    parent: tk.Misc,
    *,
    width: int = 200,
    style: str = "Secondary.TFrame",
    **kwargs: Any,
) -> ttk.Frame:  # type: ignore[name-defined]
    """
    Create a sidebar container with fixed width and secondary background.

    Sidebars are typically used for navigation or tool panels alongside
    main content areas.

    Default style:
        - "Secondary.TFrame" (uses GUI_COLOUR_BG_SECONDARY)

    Args:
        parent (tk.Misc):
            Parent widget.
        width (int):
            Fixed sidebar width in pixels (default=200).
        style (str):
            Optional ttk style override.
        **kwargs:
            Additional Frame options.

    Returns:
        ttk.Frame:
            Sidebar container with:
                - .geometry_kwargs: Extracted geometry hints
                - .g01c_role: "sidebar"
                - .g01c_width: Configured width

    Example:
        sidebar = make_sidebar(main_frame, width=220)
        make_label(sidebar, "Navigation", category="SectionHeading", surface="Secondary").pack(anchor="w", padx=8)
        sidebar.pack(side="left", fill="y")
    """
    geometry = extract_geometry_kwargs(kwargs)

    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {
        "style": style,
        "width": width,
    }
    options.update(kwargs)

    logger.debug(
        "[G01c] make_sidebar: style=%s width=%d options=%r geometry=%r",
        style, width, options, geometry,
    )
    widget: ttk.Frame = ttk.Frame(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    widget.g01c_role = "sidebar"  # type: ignore[attr-defined]
    widget.g01c_width = width  # type: ignore[attr-defined]
    return widget


def make_toolbar(
    parent: tk.Misc,
    *,
    height: int = 40,
    style: str = "Secondary.TFrame",
    **kwargs: Any,
) -> ttk.Frame:  # type: ignore[name-defined]
    """
    Create a toolbar container for action buttons and controls.

    Toolbars are typically placed at the top of a content area and contain
    action buttons, search fields, or filter controls.

    Default style:
        - "Secondary.TFrame"

    Args:
        parent (tk.Misc):
            Parent widget.
        height (int):
            Toolbar height in pixels (default=40).
        style (str):
            Optional ttk style override.
        **kwargs:
            Additional Frame options.

    Returns:
        ttk.Frame:
            Toolbar container with:
                - .geometry_kwargs: Extracted geometry hints
                - .g01c_role: "toolbar"
                - .g01c_height: Configured height

    Example:
        toolbar = make_toolbar(content, height=48)
        make_button(toolbar, "New").pack(side="left", padx=4)
        make_button(toolbar, "Save").pack(side="left")
        toolbar.pack(fill="x", side="top")
    """
    geometry = extract_geometry_kwargs(kwargs)

    strip_colour_and_font_kwargs(kwargs)

    options: Dict[str, Any] = {
        "style": style,
        "height": height,
    }
    options.update(kwargs)

    logger.debug(
        "[G01c] make_toolbar: style=%s height=%d options=%r geometry=%r",
        style, height, options, geometry,
    )
    widget: ttk.Frame = ttk.Frame(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    widget.g01c_role = "toolbar"  # type: ignore[attr-defined]
    widget.g01c_height = height  # type: ignore[attr-defined]
    return widget


# ====================================================================================================
# 7B. PUBLIC UI WRAPPER CLASS (REQUIRED BY G03 FRAMEWORK)
# ----------------------------------------------------------------------------------------------------
# Provides an object-oriented interface over the primitive widget functions.
#
# Pages receive `ui = UIPrimitives(self)` from the G03 Controller and call:
#
#       ui.heading_primary(frame, "Section Title")
#       ui.label_primary(frame, "Body text")
#       ui.button(frame, "Run", command=...)
#
# This keeps page code clean, declarative, and style-driven.
# ====================================================================================================

class UIPrimitives:
    """
    Thin OO wrapper around the primitive widget functions.

    This class does NOT create widgets by itself. It exposes simple, predictable
    helper methods that call the Section 4–7 primitive builders.
    """

    def __init__(self, root: tk.Misc) -> None:  # type: ignore[name-defined]
        """
        Initialise a UIPrimitives interface.

        Args:
            root (tk.Misc):
                Root or top-level widget. Stored for potential future use.
        """
        self.root = root

    # ================================================================================================
    # TEXT LABELS — PRIMARY SURFACE
    # ================================================================================================
    def label_primary(
        self,
        parent: tk.Misc,
        text: str = "",
        **kwargs: Any,
    ) -> ttk.Label:
        return make_label(parent, text, category="Body", surface="Primary", weight="Normal", **kwargs)

    def label_primary_bold(
        self,
        parent: tk.Misc,
        text: str = "",
        **kwargs: Any,
    ) -> ttk.Label:
        return make_label(parent, text, category="Body", surface="Primary", weight="Bold", **kwargs)

    # ================================================================================================
    # TEXT LABELS — SECONDARY SURFACE
    # ================================================================================================
    def label_secondary(
        self,
        parent: tk.Misc,
        text: str = "",
        **kwargs: Any,
    ) -> ttk.Label:
        return make_label(parent, text, category="Body", surface="Secondary", weight="Normal", **kwargs)

    def label_secondary_bold(
        self,
        parent: tk.Misc,
        text: str = "",
        **kwargs: Any,
    ) -> ttk.Label:
        return make_label(parent, text, category="Body", surface="Secondary", weight="Bold", **kwargs)

    # ================================================================================================
    # CARD LABELS (inside Card.TFrame)
    # ================================================================================================
    def label_card(
        self,
        parent: tk.Misc,
        text: str = "",
        **kwargs: Any
    ) -> ttk.Label:
        return make_label(parent, text, category="Card", surface="Secondary", weight="Normal", **kwargs)

    def label_card_bold(
        self,
        parent: tk.Misc,
        text: str = "",
        **kwargs: Any
    ) -> ttk.Label:
        return make_label(parent, text, category="Card", surface="Secondary", weight="Bold", **kwargs)

    # ================================================================================================
    # HEADINGS — COMPLETE 5-TIER HEADING SYSTEM
    # ================================================================================================

    # Window-level (top of page)
    def heading_window(
        self,
        parent: tk.Misc,
        text: str,
        **kwargs: Any,
    ) -> ttk.Label:
        return make_label(parent, text, category="WindowHeading", surface="Primary", weight="Bold", **kwargs)

    # Page-level headings (Primary/Secondary)
    def heading_primary(
        self,
        parent: tk.Misc,
        text: str,
        **kwargs: Any,
    ) -> ttk.Label:
        return make_label(parent, text, category="Heading", surface="Primary", weight="Bold", **kwargs)

    def heading_secondary(
        self,
        parent: tk.Misc,
        text: str,
        **kwargs: Any,
    ) -> ttk.Label:
        return make_label(parent, text, category="Heading", surface="Secondary", weight="Bold", **kwargs)

    # Section-level headings (Primary/Secondary)
    def section_heading_primary(
        self,
        parent: tk.Misc,
        text: str,
        **kwargs: Any,
    ) -> ttk.Label:
        return make_label(parent, text, category="SectionHeading", surface="Primary", weight="Bold", **kwargs)

    def section_heading_secondary(
        self,
        parent: tk.Misc,
        text: str,
        **kwargs: Any,
    ) -> ttk.Label:
        return make_label(parent, text, category="SectionHeading", surface="Secondary", weight="Bold", **kwargs)

    # ================================================================================================
    # STATUS LABELS
    # ================================================================================================
    def status(
        self,
        parent: tk.Misc,
        text: str = "",
        status: str = "info",
        surface: str = "Primary",
        **kwargs: Any,
    ) -> ttk.Label:
        """Create a status label with category derived from status parameter."""
        status_to_category = {"info": "Body", "success": "Success", "warning": "Warning", "error": "Error"}
        category = status_to_category.get(status, "Body")
        return make_label(parent, text, category=category, surface=surface, weight="Normal", **kwargs)

    def success(self, parent: tk.Misc, text: str = "", surface: str = "Primary", **kwargs: Any) -> ttk.Label:
        return make_label(parent, text, category="Success", surface=surface, weight="Normal", **kwargs)

    def warning(self, parent: tk.Misc, text: str = "", surface: str = "Primary", **kwargs: Any) -> ttk.Label:
        return make_label(parent, text, category="Warning", surface=surface, weight="Normal", **kwargs)

    def error(self, parent: tk.Misc, text: str = "", surface: str = "Primary", **kwargs: Any) -> ttk.Label:
        return make_label(parent, text, category="Error", surface=surface, weight="Normal", **kwargs)

    # ================================================================================================
    # INPUT WIDGETS
    # ================================================================================================
    def button(self, parent: tk.Misc, text: str = "", **kwargs: Any) -> ttk.Button:
        return make_button(parent, text=text, **kwargs)

    def entry(self, parent: tk.Misc, **kwargs: Any) -> ttk.Entry:
        return make_entry(parent, **kwargs)

    def textarea(self, parent: tk.Misc, **kwargs: Any) -> scrolledtext.ScrolledText:
        return make_textarea(parent, **kwargs)

    def combobox(
        self,
        parent: tk.Misc,
        values: Optional[list[Any]] = None,
        **kwargs: Any,
    ) -> ttk.Combobox:
        return make_combobox(parent, values=values, **kwargs)

    # ================================================================================================
    # CHOICE CONTROLS (checkbox, radio, switch)
    # ================================================================================================
    def checkbox(
        self,
        parent: tk.Misc,
        text: str,
        variable: tk.Variable,
        **kwargs: Any,
    ) -> ttk.Checkbutton:
        return make_checkbox(parent, text, variable, **kwargs)

    def radio(
        self,
        parent: tk.Misc,
        text: str,
        variable: tk.Variable,
        value: Any,
        **kwargs: Any,
    ) -> ttk.Radiobutton:
        return make_radio(parent, text, variable, value, **kwargs)

    def switch(
        self,
        parent: tk.Misc,
        text: str,
        variable: tk.Variable,
        **kwargs: Any,
    ) -> ttk.Checkbutton:
        return make_switch(parent, text, variable, **kwargs)

    # ================================================================================================
    # STRUCTURAL PRIMITIVES
    # ================================================================================================
    def frame(self, parent: tk.Misc, **kwargs: Any) -> ttk.Frame:
        return make_frame(parent, **kwargs)

    def divider(self, parent: tk.Misc, **kwargs: Any) -> ttk.Frame:
        return make_divider(parent, **kwargs)

    def spacer(
        self,
        parent: tk.Misc,
        height: int = 8,
        **kwargs: Any,
    ) -> ttk.Frame:
        return make_spacer(parent, height=height, **kwargs)

    # ================================================================================================
    # LAYOUT CONTAINER PRIMITIVES
    # ================================================================================================
    def button_bar(self, parent: tk.Misc, **kwargs: Any) -> ttk.Frame:
        """Create a button bar container. Pack buttons inside with side='right'."""
        return make_button_bar(parent, **kwargs)

    def horizontal_group(self, parent: tk.Misc, **kwargs: Any) -> ttk.Frame:
        """Create a horizontal group container. Pack children with side='left'."""
        return make_horizontal_group(parent, **kwargs)

    def vertical_group(self, parent: tk.Misc, **kwargs: Any) -> ttk.Frame:
        """Create a vertical group container. Pack children with anchor='w'."""
        return make_vertical_group(parent, **kwargs)

    def card(self, parent: tk.Misc, **kwargs: Any) -> ttk.Frame:
        """Create a card container with secondary background."""
        return make_card(parent, **kwargs)

    def sidebar(self, parent: tk.Misc, width: int = 200, **kwargs: Any) -> ttk.Frame:
        """Create a sidebar container with fixed width."""
        return make_sidebar(parent, width=width, **kwargs)

    def toolbar(self, parent: tk.Misc, height: int = 40, **kwargs: Any) -> ttk.Frame:
        """Create a toolbar container."""
        return make_toolbar(parent, height=height, **kwargs)


# ====================================================================================================
# 8. SANDBOX / MAIN TEST WINDOW
# ----------------------------------------------------------------------------------------------------
# Developer-only sandbox:
#   - Demonstrates each primitive in a simple test window.
#   - Not used by production code; runs only when this file is executed directly.
# ====================================================================================================

def sandbox() -> None:
    """
    Minimal sandbox window to exercise widget primitives.

    Demonstrates:
        - Text labels (primary/secondary, normal/bold, card labels).
        - Full 5-tier heading system (window, page, section on primary/secondary).
        - Status labels (info/success/warning/error).
        - Input widgets (entry, combobox, textarea, button).
        - Choice controls (checkbox, radio, switch).
        - Structural primitives (frame, divider, spacer).

    Notes:
        - This function creates its own Tk root and ttk.Style instance.
        - It applies configure_ttk_styles(...) to ensure the theme is active.
        - Intended for developer QA only — not used by production code.
    """
    logger.info("=== G01c_widget_primitives.py — Sandbox Start ===")

    # Window & style initialisation
    root = tk.Tk()  # type: ignore[name-defined]
    style_obj = ttk.Style()  # type: ignore[name-defined]

    root.title("G01c Widget Primitives Sandbox")
    root.geometry(f"{FRAME_SIZE_H}x{FRAME_SIZE_V}")
    root.configure(bg=GUI_COLOUR_BG_PRIMARY)

    # Apply global ttk styles
    configure_ttk_styles(style_obj)  # type: ignore[arg-type]
    logger.info("[G01c] Sandbox: configure_ttk_styles applied successfully.")

    ui = UIPrimitives(root)

    # ================================================================================================
    # SCROLLABLE OUTER CONTAINER
    # ================================================================================================
    # Create a canvas with scrollbar for the entire content
    outer_frame = ui.frame(root)
    outer_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(outer_frame, bg=GUI_COLOUR_BG_PRIMARY, highlightthickness=0)  # type: ignore[name-defined]
    scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)  # type: ignore[name-defined]
    
    canvas.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Inner frame that holds all content
    container = ui.frame(canvas)
    canvas_window = canvas.create_window((0, 0), window=container, anchor="nw")

    # Configure canvas scrolling
    def on_frame_configure(event: Any) -> None:
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event: Any) -> None:
        canvas.itemconfig(canvas_window, width=event.width)

    container.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    # Enable mousewheel scrolling
    def on_mousewheel(event: Any) -> None:
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # Add padding inside the container
    content = ui.frame(container)
    content.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)

    # ================================================================================================
    # HEADINGS DEMO
    # ================================================================================================
    ui.heading_window(content, "G01c Widget Primitives — Live Sandbox").pack(
        anchor="w",
        pady=(0, 10),
    )

    ui.heading_primary(content, "Primary Surface — Headings & Labels").pack(
        anchor="w",
        pady=(0, 4),
    )

    ui.section_heading_primary(content, "Primary Section Heading").pack(
        anchor="w",
        pady=(0, 8),
    )

    # Primary labels
    ui.label_primary(
        content,
        "Primary label — normal body text on primary surface.",
    ).pack(anchor="w", pady=2)

    ui.label_primary_bold(
        content,
        "Primary label — bold body text on primary surface.",
    ).pack(anchor="w", pady=2)

    ui.spacer(content, height=6).pack(fill="x")

    # Status labels
    ui.status(content, "Info status (Primary.Normal.TLabel)", status="info").pack(
        anchor="w",
        pady=1,
    )
    ui.success(content, "Success status (Success.TLabel)").pack(anchor="w", pady=1)
    ui.warning(content, "Warning status (Warning.TLabel)").pack(anchor="w", pady=1)
    ui.error(content, "Error status (Error.TLabel)").pack(anchor="w", pady=1)

    ui.divider(content).pack(fill="x", pady=(10, 10))

    # ================================================================================================
    # SECONDARY / CARD SURFACE DEMO
    # ================================================================================================
    # Note: Secondary headings should be placed ON secondary surfaces (inside cards/panels)
    # First, show the heading on primary surface explaining what comes next
    ui.label_primary(
        content,
        "Below: Secondary surface styles (headings and labels with Secondary background):",
    ).pack(anchor="w", pady=(0, 4))

    # Create a secondary surface frame to demonstrate secondary styles
    secondary_panel = ui.frame(content, style="SectionBody.TFrame")
    secondary_panel.pack(fill="x", pady=(4, 8), padx=4)

    ui.heading_secondary(secondary_panel, "Secondary / Card Surface").pack(
        anchor="w",
        padx=8,
        pady=(8, 4),
    )

    ui.section_heading_secondary(secondary_panel, "Section Heading on Card Surface").pack(
        anchor="w",
        padx=8,
        pady=(0, 6),
    )

    card = ui.frame(secondary_panel, style="Card.TFrame")
    card.pack(fill="x", pady=(4, 8), padx=8)

    ui.label_card(
        card,
        "Card label — Card.TLabel inside Card.TFrame.",
    ).pack(anchor="w", padx=8, pady=(6, 2))

    ui.label_secondary(
        card,
        "Secondary label — normal body text on card surface.",
    ).pack(anchor="w", padx=8, pady=2)

    ui.label_secondary_bold(
        card,
        "Secondary label — bold body text on card surface.",
    ).pack(anchor="w", padx=8, pady=(0, 6))

    ui.divider(content).pack(fill="x", pady=(10, 10))

    # ================================================================================================
    # INPUT WIDGETS DEMO
    # ================================================================================================
    ui.heading_primary(content, "Input Widgets").pack(anchor="w", pady=(0, 4))
    ui.section_heading_primary(content, "Entry, Combobox, Textarea, Buttons").pack(
        anchor="w",
        pady=(0, 6),
    )

    # Entry
    ui.label_primary(content, "Entry:").pack(anchor="w")
    ui.entry(content, width=32).pack(anchor="w", pady=(0, 6))

    # Combobox
    ui.label_primary(content, "Combobox:").pack(anchor="w")
    ui.combobox(
        content,
        values=["Option A", "Option B", "Option C"],
        state="readonly",
        width=30,
    ).pack(anchor="w", pady=(0, 6))

    # Textarea
    ui.label_primary(content, "Textarea (ScrolledText):").pack(anchor="w")
    ui.textarea(content, height=5).pack(fill="both", expand=True, pady=(0, 8))

    # Buttons
    button_row = ui.frame(content)
    button_row.pack(anchor="w", pady=(4, 8))

    ui.button(button_row, text="Primary Button").pack(side="left", padx=(0, 8))
    ui.button(
        button_row,
        text="Secondary Button",
        style="Secondary.TButton",
    ).pack(side="left")

    ui.divider(content).pack(fill="x", pady=(10, 10))

    # ================================================================================================
    # CHOICE CONTROLS DEMO
    # ================================================================================================
    ui.heading_primary(content, "Choice Controls").pack(anchor="w", pady=(0, 4))
    ui.section_heading_primary(content, "Checkbox, Radio Group, Switch").pack(
        anchor="w",
        pady=(0, 6),
    )

    # Checkbox
    chk_var = tk.BooleanVar(value=True)  # type: ignore[name-defined]
    ui.checkbox(content, "Enable feature X", variable=chk_var).pack(
        anchor="w",
        pady=(2, 4),
    )

    # Radio group
    radio_var = tk.StringVar(value="A")  # type: ignore[name-defined]
    ui.label_primary(content, "Radio group (A/B):").pack(
        anchor="w",
        pady=(8, 2),
    )
    ui.radio(content, "Option A", variable=radio_var, value="A").pack(anchor="w")
    ui.radio(content, "Option B", variable=radio_var, value="B").pack(anchor="w")

    # Switch
    switch_var = tk.BooleanVar(value=False)  # type: ignore[name-defined]
    ui.label_primary(content, "Switch control:").pack(
        anchor="w",
        pady=(8, 2),
    )
    ui.switch(content, "Use experimental mode", variable=switch_var).pack(
        anchor="w",
        pady=(0, 4),
    )

    ui.divider(content).pack(fill="x", pady=(10, 10))

    # ================================================================================================
    # STRUCTURAL PRIMITIVES DEMO
    # ================================================================================================
    ui.heading_primary(content, "Structural Primitives").pack(anchor="w", pady=(0, 4))
    ui.section_heading_primary(content, "Frame + Spacer + Divider").pack(
        anchor="w",
        pady=(0, 6),
    )

    structural = ui.frame(content)
    structural.pack(fill="x", pady=(4, 0))

    ui.label_primary(
        structural,
        "This block is inside a TFrame created via ui.frame(...).",
    ).pack(anchor="w", pady=(0, 4))

    ui.spacer(structural, height=12).pack(fill="x")

    ui.label_primary(
        structural,
        "Spacer above created vertical breathing room.",
    ).pack(anchor="w", pady=(0, 4))

    ui.divider(structural).pack(fill="x", pady=(6, 0))

    logger.info("=== G01c_widget_primitives.py — Sandbox Ready (entering mainloop) ===")
    root.mainloop()
    logger.info("=== G01c_widget_primitives.py — Sandbox End ===")


# ====================================================================================================
# 9. MAIN GUARD
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Minimal logging initialisation for sandbox runs
    init_logging()
    sandbox()