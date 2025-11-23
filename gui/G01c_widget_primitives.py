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
#         - fonts resolved by G01b
#         - colours from G01a_style_config
#         - ttk styles from G01b_style_engine
#   • Translate tk/ttk differences (e.g., fg/bg vs foreground/background).
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
#             • style rules from G01b
#             • colour/size/font tokens from G01a
#             • layout abstraction from G02a
#
# Rules:
#   - No hard-coded colours/sizes except where ttk demands them.
#   - No direct widget layout (grid/pack). Only construct widgets.
#   - No creation of windows or styles at import time — all configuration by callers.
#   - Geometry hints are stored as `widget.geometry_kwargs` and consumed later by G02a.
#
# Notes:
#   - All primitives follow the same pattern: extract geometry → normalise options →
#     apply defaults → create widget.
#   - UIPrimitives wraps every function for clean consumption by page classes.
#   - attach_layout_helpers(UIPrimitives) integrates the G02a layout DSL transparently.
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
from gui.G01a_style_config import *
from gui.G01b_style_engine import FONT_NAME_BASE, FONT_NAME_HEADING, FONT_NAME_SECTION_HEADING, configure_ttk_styles
from gui.G02a_layout_utils import attach_layout_helpers
FontSpec = Union[str, Tuple[str, int], Tuple[str, int, str]]


# ====================================================================================================
# 3. INTERNAL HELPER FUNCTIONS (FONT & GEOMETRY)
# ----------------------------------------------------------------------------------------------------
# These helpers are "internal" in intent but named without underscores to comply with
# Global Coding Standards (no functions starting with an underscore).
# ====================================================================================================
def resolve_font_family() -> str:
    """
    Choose a usable font family based on GUI_FONT_FAMILY from G00a_style_config.

    The first family that can be instantiated by tkFont.Font(...) is returned.
    If none of the preferred families are available, the function falls back to
    'Segoe UI' as a safe cross-platform default.

    Returns:
        str: Name of the resolved font family.
    """
    families = GUI_FONT_FAMILY
    logger.debug("[G01b] resolve_font_family: GUI_FONT_FAMILY=%r", families)

    if isinstance(families, (tuple, list)):
        for fam in families:
            try:
                tkFont.Font(family=fam, size=GUI_FONT_SIZE_DEFAULT)  # type: ignore[name-defined]
                logger.info("[G01b] Resolved GUI font family: %s", fam)
                return fam
            except Exception as exc:  # noqa: BLE001
                logger.debug("[G01b] Font '%s' not available: %s", fam, exc)
    else:
        try:
            tkFont.Font(family=families, size=GUI_FONT_SIZE_DEFAULT)  # type: ignore[name-defined]
            logger.info("[G01b] Resolved GUI font family (single): %s", families)
            return families
        except Exception as exc:  # noqa: BLE001
            logger.debug("[G01b] Font '%s' not available: %s", families, exc)

    fallback = "Segoe UI"
    logger.warning("[G01b] Falling back to default font family: %s", fallback)
    return fallback


def base_font() -> FontSpec:
    """
    Return the default body font spec for widgets.

    Prefers the named font from G01a_style_engine (FONT_NAME_BASE), falling back to a
    direct (family, size) tuple if named fonts are unavailable.

    Returns:
        FontSpec: Named font identifier or (family, size) tuple.
    """
    if FONT_NAME_BASE:
        logger.debug("[G01b] base_font: using named font %s", FONT_NAME_BASE)
        return FONT_NAME_BASE
    fam = resolve_font_family()
    logger.debug("[G01b] base_font: using tuple font (%s, %d)", fam, GUI_FONT_SIZE_DEFAULT)
    return (fam, GUI_FONT_SIZE_DEFAULT)


def heading_font() -> FontSpec:
    """
    Return the heading font spec for primary headings.

    Prefers the named heading font from G01a_style_engine (FONT_NAME_HEADING) and falls
    back to a (family, size, weight) tuple if necessary.

    Returns:
        FontSpec: Named font identifier or (family, size, weight) tuple.
    """
    if FONT_NAME_HEADING:
        logger.debug("[G01b] heading_font: using named font %s", FONT_NAME_HEADING)
        return FONT_NAME_HEADING
    fam = resolve_font_family()
    logger.debug(
        "[G01b] heading_font: using tuple font (%s, %d, 'bold')",
        fam,
        GUI_FONT_SIZE_HEADING,
    )
    return (fam, GUI_FONT_SIZE_HEADING, "bold")


def section_heading_font() -> FontSpec:
    """
    Return the font spec used for subheadings / section-like labels.

    Prefers the named section heading font from G01a_style_engine and falls back to a
    (family, size, weight) tuple if necessary.

    Returns:
        FontSpec: Named font identifier or (family, size, weight) tuple.
    """
    if FONT_NAME_SECTION_HEADING:
        logger.debug(
            "[G01b] section_heading_font: using named font %s",
            FONT_NAME_SECTION_HEADING,
        )
        return FONT_NAME_SECTION_HEADING
    fam = resolve_font_family()
    logger.debug(
        "[G01b] section_heading_font: using tuple font (%s, %d, 'bold')",
        fam,
        GUI_FONT_SIZE_TITLE,
    )
    return (fam, GUI_FONT_SIZE_TITLE, "bold")


def extract_geometry_kwargs(options: MutableMapping[str, Any]) -> Dict[str, Any]:
    """
    Pop geometry-related keyword arguments from a widget options dict.

    Geometry keys are not passed to widget constructors; instead they are stored on the
    created widget as `widget.geometry_kwargs` so layout code can apply them explicitly.

    Args:
        options: Mapping of options that will be passed to the widget constructor.
                 This mapping is modified in-place (geometry keys are removed).

    Returns:
        dict: A dictionary containing only geometry-related keys (padx, pady, ipadx, ipady).
    """
    geometry_keys = ("padx", "pady", "ipadx", "ipady")
    geometry: Dict[str, Any] = {}

    for key in geometry_keys:
        if key in options:
            geometry[key] = options.pop(key)

    logger.debug("[G01b] extract_geometry_kwargs: %r", geometry)
    return geometry


# ====================================================================================================
# 4. TEXTUAL WIDGET PRIMITIVES
# ----------------------------------------------------------------------------------------------------
# Core primitives for rendering text: labels, headings, subheadings, and status messages.
# These are the foundation for most static and dynamic text in the GUI.
# ====================================================================================================

def make_label(parent: tk.Misc, text: str = "", **kwargs: Any) -> ttk.Label:  # type: ignore[name-defined]
    """
    Create a basic themed ttk Label.

    Geometry-related kwargs (padx, pady, etc.) are removed and stored on the widget as
    `geometry_kwargs` for external layout helpers to consume. Supports both `fg`/`bg`
    and `foreground` / `background` aliases.

    Args:
        parent: Parent container widget.
        text:   Label text.
        **kwargs: Additional ttk.Label options (font, foreground, background, etc.).

    Returns:
        ttk.Label: The created label instance with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    # Map tk-style fg/bg aliases to ttk foreground/background
    if "fg" in kwargs and "foreground" not in kwargs:
        kwargs["foreground"] = kwargs.pop("fg")
    if "bg" in kwargs and "background" not in kwargs:
        kwargs["background"] = kwargs.pop("bg")

    options: Dict[str, Any] = {
        "text": text,
        "font": kwargs.pop("font", base_font()),
        "foreground": kwargs.pop("foreground", TEXT_COLOUR_SECONDARY),
        "background": kwargs.pop("background", GUI_COLOUR_BG_PRIMARY),
    }
    options.update(kwargs)

    logger.debug("[G01b] make_label: text=%r options=%r geometry=%r", text, options, geometry)
    widget: ttk.Label = ttk.Label(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


def make_heading(parent: tk.Misc, text: str, **kwargs: Any) -> ttk.Label:  # type: ignore[name-defined]
    """
    Create a primary heading label.

    Typically used for window titles or major section headings. Uses the heading font
    from the theme and the primary text colour by default.

    Args:
        parent: Parent container widget.
        text:   Heading text.
        **kwargs: Additional ttk.Label options.

    Returns:
        ttk.Label: The created heading label instance with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    if "fg" in kwargs and "foreground" not in kwargs:
        kwargs["foreground"] = kwargs.pop("fg")
    if "bg" in kwargs and "background" not in kwargs:
        kwargs["background"] = kwargs.pop("bg")

    options: Dict[str, Any] = {
        "text": text,
        "font": kwargs.pop("font", heading_font()),
        "foreground": kwargs.pop("foreground", TEXT_COLOUR_PRIMARY),
        "background": kwargs.pop("background", GUI_COLOUR_BG_PRIMARY),
    }
    options.update(kwargs)

    logger.debug("[G01b] make_heading: text=%r options=%r geometry=%r", text, options, geometry)
    widget: ttk.Label = ttk.Label(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


def make_subheading(parent: tk.Misc, text: str, **kwargs: Any) -> ttk.Label:  # type: ignore[name-defined]
    """
    Create a subheading label inside a section or panel.

    Uses the section heading font and primary text colour for in-section emphasis.

    Args:
        parent: Parent container widget.
        text:   Subheading text.
        **kwargs: Additional ttk.Label options.

    Returns:
        ttk.Label: The created subheading label instance with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    if "fg" in kwargs and "foreground" not in kwargs:
        kwargs["foreground"] = kwargs.pop("fg")
    if "bg" in kwargs and "background" not in kwargs:
        kwargs["background"] = kwargs.pop("bg")

    options: Dict[str, Any] = {
        "text": text,
        "font": kwargs.pop("font", section_heading_font()),
        "foreground": kwargs.pop("foreground", TEXT_COLOUR_PRIMARY),
        "background": kwargs.pop("background", GUI_COLOUR_BG_PRIMARY),
    }
    options.update(kwargs)

    logger.debug("[G01b] make_subheading: text=%r options=%r geometry=%r", text, options, geometry)
    widget: ttk.Label = ttk.Label(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


def make_status_label(
    parent: tk.Misc,
    text: str = "",
    status: str = "info",
    **kwargs: Any,
) -> ttk.Label:  # type: ignore[name-defined]
    """
    Create a label for dynamic status/feedback messages.

    The text colour is derived from the `status` argument (info, success, warning, error)
    but can be overridden via `foreground` or `fg`.

    Args:
        parent: Parent container widget.
        text:   Status text to display.
        status: One of "info", "success", "warning", or "error".
        **kwargs: Additional ttk.Label options.

    Returns:
        ttk.Label: The created status label instance with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    if status == "success":
        fg_default = GUI_COLOUR_SUCCESS
    elif status == "warning":
        fg_default = GUI_COLOUR_WARNING
    elif status == "error":
        fg_default = GUI_COLOUR_ERROR
    else:
        fg_default = TEXT_COLOUR_SECONDARY

    if "fg" in kwargs and "foreground" not in kwargs:
        kwargs["foreground"] = kwargs.pop("fg")
    if "bg" in kwargs and "background" not in kwargs:
        kwargs["background"] = kwargs.pop("bg")

    options: Dict[str, Any] = {
        "text": text,
        "font": kwargs.pop("font", base_font()),
        "foreground": kwargs.pop("foreground", fg_default),
        "background": kwargs.pop("background", GUI_COLOUR_BG_PRIMARY),
    }
    options.update(kwargs)

    logger.debug(
        "[G01b] make_status_label: text=%r status=%s options=%r geometry=%r",
        text,
        status,
        options,
        geometry,
    )
    widget: ttk.Label = ttk.Label(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


# ====================================================================================================
# 5. INPUT WIDGET PRIMITIVES
# ----------------------------------------------------------------------------------------------------
# Widgets that accept user input: single-line entries, multi-line text areas, and comboboxes.
# ====================================================================================================

def make_button(parent: tk.Misc, text: str = "", **kwargs: Any) -> ttk.Button:  # type: ignore[name-defined]
    """
    Create a themed push button.

    Relies on ttk/ttkbootstrap theming for colours and applies the global base font
    by default. Geometry kwargs (padx, pady, etc.) are stored in .geometry_kwargs.

    Args:
        parent: Parent container widget.
        text:   Button label text.
        **kwargs: Additional ttk.Button options (command, bootstyle, etc.).

    Returns:
        ttk.Button: The created button instance with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    options: Dict[str, Any] = {
        "text": text,
        "command": kwargs.pop("command", None),
        # "font": kwargs.pop("font", base_font()),  # Removed: ttk.Button does not support font
    }
    options.update(kwargs)

    logger.debug("[G01b] make_button: text=%r options=%r geometry=%r", text, options, geometry)
    widget: ttk.Button = ttk.Button(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


def make_entry(parent: tk.Misc, **kwargs: Any) -> ttk.Entry:  # type: ignore[name-defined]
    """
    Create a single-line text entry widget.

    ttk.Entry does not accept direct bg/fg arguments; these are controlled by the
    active ttk style, so any such keys are removed.

    Args:
        parent: Parent container widget.
        **kwargs: Additional ttk.Entry options (width, textvariable, etc.).

    Returns:
        ttk.Entry: The created entry instance with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    # ttk.Entry does not accept direct bg/fg; these are controlled by style.
    for bad in ("bg", "background", "fg", "foreground"):
        if bad in kwargs:
            logger.debug("[G01b] make_entry: dropping unsupported option %s", bad)
        kwargs.pop(bad, None)

    options: Dict[str, Any] = {
        "font": kwargs.pop("font", base_font()),
    }
    options.update(kwargs)

    logger.debug("[G01b] make_entry: options=%r geometry=%r", options, geometry)
    widget: ttk.Entry = ttk.Entry(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


def make_textarea(parent: tk.Misc, **kwargs: Any) -> "scrolledtext.ScrolledText":  # type: ignore[name-defined]
    """
    Create a scrolled multi-line text area.

    Uses tk.scrolledtext.ScrolledText directly (not ttk), and maps ttk-style
    `foreground`/`background` onto classic tk `fg`/`bg` if provided.

    Args:
        parent: Parent container widget.
        **kwargs: Additional ScrolledText options (height, width, wrap, etc.).

    Returns:
        ScrolledText: The created text area instance with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    # Defaults tuned for body text.
    default_font = kwargs.pop("font", base_font())
    default_wrap = kwargs.pop("wrap", "word")

    # Map ttk-style foreground/background to classic tk fg/bg if used.
    if "foreground" in kwargs and "fg" not in kwargs:
        kwargs["fg"] = kwargs.pop("foreground")
    if "background" in kwargs and "bg" not in kwargs:
        kwargs["bg"] = kwargs.pop("background")

    options: Dict[str, Any] = {
        "font": default_font,
        "wrap": default_wrap,
        "fg": kwargs.pop("fg", TEXT_COLOUR_SECONDARY),
        "bg": kwargs.pop("bg", GUI_COLOUR_BG_TEXTAREA),
    }
    options.update(kwargs)

    logger.debug("[G01b] make_textarea: options=%r geometry=%r", options, geometry)
    widget = scrolledtext.ScrolledText(parent, **options)  # type: ignore[name-defined]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


def make_combobox(
    parent: tk.Misc,
    values: Optional[list[Any]] = None,
    **kwargs: Any,
) -> ttk.Combobox:  # type: ignore[name-defined]
    """
    Create a themed Combobox (dropdown) widget.

    Args:
        parent: Parent container widget.
        values: Optional list of values for the combobox.
        **kwargs: Additional ttk.Combobox options (state, width, textvariable, etc.).

    Returns:
        ttk.Combobox: The created combobox instance with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    if values is not None and "values" not in kwargs:
        kwargs["values"] = values

    options: Dict[str, Any] = {
        "font": kwargs.pop("font", base_font()),
    }
    options.update(kwargs)

    logger.debug("[G01b] make_combobox: options=%r geometry=%r", options, geometry)
    widget: ttk.Combobox = ttk.Combobox(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


# ====================================================================================================
# 6. CHOICE CONTROL PRIMITIVES
# ----------------------------------------------------------------------------------------------------
# Boolean and single-choice controls: checkboxes, radio buttons, and switches.
# Overloads are used to allow `command` to be callable or None while keeping type hints strict.
# ====================================================================================================

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
    Create a themed Checkbutton for boolean state toggles.

    Applies a default ttkbootstrap bootstyle "primary" when no style/bootstyle
    is provided.

    Args:
        parent:   Parent container widget.
        text:     Label text next to the checkbox.
        variable: Tkinter variable instance (BooleanVar / IntVar, etc.).
        command:  Optional callback invoked when the value changes.
        **kwargs: Additional Checkbutton options.

    Returns:
        ttk.Checkbutton: The created checkbutton with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    options: Dict[str, Any] = {
        "text": text,
        "variable": variable,
    }

    if command is not None:
        options["command"] = command

    # Note: bootstyle can be added via **kwargs if ttkbootstrap is available
    
    # Remove font if present (not supported by ttk.Checkbutton)
    kwargs.pop("font", None)

    options.update(kwargs)

    logger.debug(
        "[G01b] make_checkbox: text=%r options=%r geometry=%r",
        text,
        options,
        geometry,
    )
    widget: ttk.Checkbutton = ttk.Checkbutton(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


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

    Multiple radios bound to the same Tk variable form a logical group where exactly
    one value is selected at a time.

    Args:
        parent:   Parent container widget.
        text:     Label text next to the radio button.
        variable: Shared Tk variable instance.
        value:    Value assigned when this radio is selected.
        command:  Optional callback invoked when selection changes.
        **kwargs: Additional Radiobutton options.

    Returns:
        ttk.Radiobutton: The created radio button with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    options: Dict[str, Any] = {
        "text": text,
        "variable": variable,
        "value": value,
    }

    if command is not None:
        options["command"] = command

    # Note: bootstyle can be added via **kwargs if ttkbootstrap is available

    # Remove font if present (not supported by ttk.Radiobutton)
    kwargs.pop("font", None)

    options.update(kwargs)

    logger.debug(
        "[G01b] make_radio: text=%r value=%r options=%r geometry=%r",
        text,
        value,
        options,
        geometry,
    )
    widget: ttk.Radiobutton = ttk.Radiobutton(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


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
    Create a switch-style boolean toggle control.

    Uses ttkbootstrap "round-toggle" bootstyle where available but degrades
    gracefully to a standard Checkbutton when running under plain ttk.

    Args:
        parent:   Parent container widget.
        text:     Label text next to the switch.
        variable: Tk variable instance (BooleanVar / IntVar, etc.).
        command:  Optional callback invoked when the value changes.
        **kwargs: Additional Checkbutton options.

    Returns:
        ttk.Checkbutton: The created switch control with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    options: Dict[str, Any] = {
        "text": text,
        "variable": variable,
    }

    if command is not None:
        options["command"] = command

    # Note: bootstyle can be added via **kwargs if ttkbootstrap is available

    # Remove font if present (not supported by ttk.Checkbutton)
    kwargs.pop("font", None)

    options.update(kwargs)

    logger.debug(
        "[G01b] make_switch: text=%r options=%r geometry=%r",
        text,
        options,
        geometry,
    )
    widget: ttk.Checkbutton = ttk.Checkbutton(parent, **options)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


# ====================================================================================================
# 7. STRUCTURAL WIDGET PRIMITIVES
# ----------------------------------------------------------------------------------------------------
# Low-level containers that support layout and visual separation: frames, dividers, and spacers.
# ====================================================================================================

def make_frame(parent: tk.Misc, **kwargs: Any) -> ttk.Frame:  # type: ignore[name-defined]
    """
    Create a generic frame container.

    Visual appearance is primarily driven by the active ttk style. Geometry
    kwargs are stored in .geometry_kwargs for layout helpers.

    Args:
        parent: Parent container widget.
        **kwargs: Additional Frame options.

    Returns:
        ttk.Frame: The created frame with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    logger.debug("[G01b] make_frame: options=%r geometry=%r", kwargs, geometry)
    widget: ttk.Frame = ttk.Frame(parent, **kwargs)  # type: ignore[assignment]
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
    Create a visual divider line.

    Implemented as a Frame that defaults to the ToolbarDivider.TFrame style
    defined in G01a_style_engine.

    Args:
        parent: Parent container widget.
        height: Divider height in pixels.
        style:  Optional ttk style name to override the default divider style.
        **kwargs: Additional Frame options (excluding bg/fg).

    Returns:
        ttk.Frame: The created divider frame with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    # Determine effective style; fall back to the global toolbar divider style.
    effective_style = style or "ToolbarDivider.TFrame"

    # Remove any direct colour arguments that ttk/ttkbootstrap.Frame does not support.
    for bad in ("background", "bg", "foreground", "fg"):
        if bad in kwargs:
            logger.debug("[G01b] make_divider: dropping unsupported option %s", bad)
        kwargs.pop(bad, None)

    base: Dict[str, Any] = {
        "height": height,
        "style": effective_style,
    }
    base.update(kwargs)

    logger.debug("[G01b] make_divider: options=%r geometry=%r", base, geometry)
    widget: ttk.Frame = ttk.Frame(parent, **base)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget


def make_spacer(
    parent: tk.Misc,
    height: int = 8,
    **kwargs: Any,
) -> ttk.Frame:  # type: ignore[name-defined]
    """
    Create an empty spacer frame with a configurable height.

    Spacers are used to introduce vertical breathing room between widgets and
    avoid magic numbers embedded directly in geometry manager calls.

    Args:
        parent: Parent container widget.
        height: Spacer height in pixels.
        **kwargs: Additional Frame options.

    Returns:
        ttk.Frame: The created spacer frame with .geometry_kwargs metadata.
    """
    geometry = extract_geometry_kwargs(kwargs)

    base: Dict[str, Any] = {
        "height": height,
    }
    base.update(kwargs)

    logger.debug("[G01b] make_spacer: options=%r geometry=%r", base, geometry)
    widget: ttk.Frame = ttk.Frame(parent, **base)  # type: ignore[assignment]
    widget.geometry_kwargs = geometry  # type: ignore[attr-defined]
    return widget

# ====================================================================================================
# 7B. PUBLIC UI WRAPPER CLASS (REQUIRED BY G03 FRAMEWORK)
# ----------------------------------------------------------------------------------------------------
# This provides an object-oriented interface over the functional primitives.
# The NavigationController will pass an instance of this class to each page.
# ====================================================================================================

class UIPrimitives:
    """
    Thin OO wrapper around the primitive widget functions.
    Pages use ui.heading(), ui.label(), ui.button() instead of calling
    make_heading() etc. directly.
    """

    def __init__(self, root):
        self.root = root

    # --- text primitives -------------------------------------------------------------------------
    def label(self, parent, text="", **kwargs):
        return make_label(parent, text=text, **kwargs)

    def heading(self, parent, text="", **kwargs):
        return make_heading(parent, text, **kwargs)

    def subheading(self, parent, text="", **kwargs):
        return make_subheading(parent, text, **kwargs)

    def status(self, parent, text="", status="info", **kwargs):
        return make_status_label(parent, text=text, status=status, **kwargs)

    # --- input primitives ------------------------------------------------------------------------
    def button(self, parent, text="", **kwargs):
        return make_button(parent, text=text, **kwargs)

    def entry(self, parent, **kwargs):
        return make_entry(parent, **kwargs)

    def textarea(self, parent, **kwargs):
        return make_textarea(parent, **kwargs)

    def combobox(self, parent, values=None, **kwargs):
        return make_combobox(parent, values=values, **kwargs)

    # --- choice controls -------------------------------------------------------------------------
    def checkbox(self, parent, text, variable, **kwargs):
        return make_checkbox(parent, text, variable, **kwargs)

    def radio(self, parent, text, variable, value, **kwargs):
        return make_radio(parent, text, variable, value, **kwargs)

    def switch(self, parent, text, variable, **kwargs):
        return make_switch(parent, text, variable, **kwargs)

    # --- structural ------------------------------------------------------------------------------
    def frame(self, parent, **kwargs):
        return make_frame(parent, **kwargs)

    def divider(self, parent, **kwargs):
        return make_divider(parent, **kwargs)

    def spacer(self, parent, height=8, **kwargs):
        return make_spacer(parent, height=height, **kwargs)

# ====================================================================================================
# 8. SANDBOX / MAIN TEST WINDOW
# ----------------------------------------------------------------------------------------------------
# Developer-only sandbox:
#   - Demonstrates each primitive in a simple test window.
#   - Not used by production code; runs only when this file is executed directly.
#   - Hybrid debugging (Option C): concise but informative diagnostics.
# ====================================================================================================

def sandbox() -> None:
    """
    Minimal sandbox window to exercise widget primitives.

    Demonstrates:
        - Textual primitives (label, heading, status labels).
        - Input widgets (entry, combobox, textarea).
        - Choice controls (checkbox, radio, switch).
        - Structural primitives (divider, spacer).
    """
    logger.info("=== G01b_widget_primitives.py — Sandbox Start ===")

    # -------------------------------------------------------------------------------------------
    # Window & style initialisation (ttkbootstrap if available, else classic Tk/ttk)
    # -------------------------------------------------------------------------------------------
    try:
        root = tk.Tk()
        style_obj = ttk.Style()
        logger.info("[G01b] Sandbox: using standard Tk/ttk.")
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "[G01b] Sandbox: ttkbootstrap not available (%s); using standard Tk/ttk.",
            exc,
        )
        root = tk.Tk()
        style_obj = ttk.Style()

    root.title("G01b Widget Primitives Sandbox")
    root.geometry(f"{FRAME_SIZE_H}x{FRAME_SIZE_V}")
    root.configure(bg=GUI_COLOUR_BG_PRIMARY)

    # Apply global ttk styles
    configure_ttk_styles(style_obj)  # type: ignore[arg-type]
    logger.info("[G01b] Sandbox: configure_ttk_styles applied successfully.")

    # Check that named fonts from G01a are available
    has_named_fonts = True
    for name in (FONT_NAME_BASE, FONT_NAME_HEADING, FONT_NAME_SECTION_HEADING):
        if not name:
            has_named_fonts = False
            break
        try:
            tkFont.nametofont(name)  # type: ignore[name-defined]
        except Exception:  # noqa: BLE001
            has_named_fonts = False
            break

    logger.info(
        "[G01b] Sandbox: named fonts available=%s "
        "(BASE=%r HEADING=%r SECTION=%r)",
        has_named_fonts,
        FONT_NAME_BASE,
        FONT_NAME_HEADING,
        FONT_NAME_SECTION_HEADING,
    )

    # -------------------------------------------------------------------------------------------
    # Build demo content
    # -------------------------------------------------------------------------------------------
    container = ttk.Frame(root)
    container.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)

    # Textual widgets
    make_heading(container, "Widget Primitives Demo").pack(anchor="w", pady=(0, 8))
    make_label(container, "This is a standard label.").pack(anchor="w", pady=2)
    make_subheading(container, "Subheading text").pack(anchor="w", pady=(8, 2))
    make_status_label(container, "Info status", status="info").pack(anchor="w", pady=1)
    make_status_label(container, "Success status", status="success").pack(anchor="w", pady=1)
    make_status_label(container, "Warning status", status="warning").pack(anchor="w", pady=1)
    make_status_label(container, "Error status", status="error").pack(anchor="w", pady=1)

    make_divider(container).pack(fill="x", pady=(10, 10))

    # Inputs
    make_label(container, "Entry:").pack(anchor="w")
    make_entry(container, width=30).pack(anchor="w", pady=(0, 6))

    make_label(container, "Combobox:").pack(anchor="w")
    make_combobox(
        container,
        values=["Option A", "Option B", "Option C"],
        state="readonly",
        width=28,
    ).pack(anchor="w", pady=(0, 6))

    make_label(container, "Textarea:").pack(anchor="w")
    make_textarea(container, height=5).pack(fill="both", expand=True, pady=(0, 6))

    # Choice controls
    chk_var = tk.BooleanVar(value=True)  # type: ignore[name-defined]
    make_checkbox(container, "Enable feature X", variable=chk_var).pack(anchor="w", pady=(8, 2))

    radio_var = tk.StringVar(value="A")  # type: ignore[name-defined]
    make_subheading(container, "Radio group").pack(anchor="w", pady=(8, 2))
    make_radio(container, "Option A", variable=radio_var, value="A").pack(anchor="w")
    make_radio(container, "Option B", variable=radio_var, value="B").pack(anchor="w")

    switch_var = tk.BooleanVar(value=False)  # type: ignore[name-defined]
    make_subheading(container, "Switch control").pack(anchor="w", pady=(8, 2))
    make_switch(container, "Use experimental mode", variable=switch_var).pack(anchor="w")

    logger.info("=== G01b_widget_primitives.py — Sandbox Ready (entering mainloop) ===")
    root.mainloop()
    logger.info("=== G01b_widget_primitives.py — Sandbox End ===")

# ====================================================================================================
# 8A. INTEGRATE LAYOUT UTILITIES (G02a_layout_utils)
# ----------------------------------------------------------------------------------------------------
# The layout utility module (G02a_layout_utils.py) provides:
#     • safe_grid / safe_pack
#     • ensure_row_weights / ensure_column_weights
#     • grid_form_row (standard 2-column form layout)
#
# These are *monkey-patched* onto the UIPrimitives class so every page can do:
#
#     ui.safe_grid(widget, row=0, column=0)
#     ui.ensure_column_weights(frame, [0, 1])
#     ui.grid_form_row(form_frame, 0, label, entry)
#
# This keeps layout code consistent, DRY, and theme-aware.
# Call attach_layout_helpers(UIPrimitives) exactly once (here).
# ====================================================================================================

attach_layout_helpers(UIPrimitives)

# ====================================================================================================
# 9. MAIN GUARD
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    sandbox()
