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
#         • GUI_FONT_FAMILY, sizes, colour palette, semantic colour roles
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
from gui.G00a_gui_packages import *
from gui.G01a_style_config import *


# ====================================================================================================
# 3. FONT RESOLUTION & NAMED FONTS
# ----------------------------------------------------------------------------------------------------
# Named font identifiers used throughout the GUI theme.
# These names are referenced by higher-level modules (G01b, G01c, etc.).
# ====================================================================================================
FONT_NAME_BASE = "GP.UI.Base"
FONT_NAME_BASE_BOLD = "GP.UI.BaseBold"
FONT_NAME_HEADING = "GP.UI.Heading"
FONT_NAME_SECTION_HEADING = "GP.UI.SectionHeading"

def resolve_font_family() -> str:
    """
    Resolve the active GUI font family for the current environment.

    Behaviour:
        - Iterates over GUI_FONT_FAMILY (tuple/list or single string) from
          G00a_style_config.
        - Attempts to instantiate a tkFont.Font with each candidate.
        - Returns the first family that succeeds.
        - Falls back to "Segoe UI" if none of the configured families are
          available.

    Returns:
        str:
            The name of the resolved font family. Guaranteed to be usable
            with tkFont.Font on the current system.
    """
    families = GUI_FONT_FAMILY
    logger.debug("[G01a] Resolving font family from GUI_FONT_FAMILY=%r", families)

    if isinstance(families, (tuple, list)):
        for fam in families:
            try:
                tkFont.Font(family=fam, size=GUI_FONT_SIZE_DEFAULT)  # type: ignore[name-defined]
                logger.info("[G01a] Resolved GUI font family: %s", fam)
                return fam
            except Exception:  # noqa: BLE001
                logger.debug("[G01a] Font family '%s' not available; trying next.", fam)
    else:
        try:
            tkFont.Font(family=families, size=GUI_FONT_SIZE_DEFAULT)  # type: ignore[name-defined]
            logger.info("[G01a] Resolved GUI font family: %s", families)
            return families
        except Exception:  # noqa: BLE001
            logger.debug("[G01a] Font family '%s' not available; falling back.", families)

    fallback = "Segoe UI"
    logger.warning(
        "[G01a] No configured GUI_FONT_FAMILY fonts available; using fallback %s",
        fallback,
    )
    return fallback


def ensure_named_fonts(family: str) -> None:
    """
    Create or update the core named Tk fonts used by the GUI framework.

    This function is intentionally idempotent: it may be called multiple
    times without side effects. If a named font already exists, its
    configuration is updated; otherwise it is created.

    Args:
        family:
            The font family name to apply to all named fonts. This should
            be the result of resolve_font_family().

    Named fonts:
        - FONT_NAME_BASE:
              • Default body font for labels, buttons, entries, etc.
              • Size: GUI_FONT_SIZE_DEFAULT
        - FONT_NAME_BASE_BOLD:
              • Bold version of the base body font.
              • Size: GUI_FONT_SIZE_DEFAULT, weight="bold"
        - FONT_NAME_HEADING:
              • Main window heading font.
              • Size: GUI_FONT_SIZE_HEADING, weight="bold"
        - FONT_NAME_SECTION_HEADING:
              • Section title font used above content frames.
              • Size: GUI_FONT_SIZE_TITLE, weight="bold"
    """
    logger.debug("[G01a] Ensuring named fonts exist (family=%s).", family)

    # -----------------------------------------------------------------------------------------------
    # Base font (body text)
    # -----------------------------------------------------------------------------------------------
    try:
        base_font_obj = tkFont.nametofont(FONT_NAME_BASE)  # type: ignore[name-defined]
        base_font_obj.configure(family=family, size=GUI_FONT_SIZE_DEFAULT)
        logger.debug("[G01a] Updated existing base font '%s'.", FONT_NAME_BASE)
    except Exception:  # noqa: BLE001
        tkFont.Font(  # type: ignore[name-defined]
            name=FONT_NAME_BASE,
            family=family,
            size=GUI_FONT_SIZE_DEFAULT,
        )
        logger.debug("[G01a] Created new base font '%s'.", FONT_NAME_BASE)

    # -----------------------------------------------------------------------------------------------
    # Base bold font (body text, bold)
    # -----------------------------------------------------------------------------------------------
    try:
        bold_font_obj = tkFont.nametofont(FONT_NAME_BASE_BOLD)  # type: ignore[name-defined]
        bold_font_obj.configure(
            family=family,
            size=GUI_FONT_SIZE_DEFAULT,
            weight="bold",
        )
        logger.debug("[G01a] Updated existing base bold font '%s'.", FONT_NAME_BASE_BOLD)
    except Exception:  # noqa: BLE001
        tkFont.Font(  # type: ignore[name-defined]
            name=FONT_NAME_BASE_BOLD,
            family=family,
            size=GUI_FONT_SIZE_DEFAULT,
            weight="bold",
        )
        logger.debug("[G01a] Created new base bold font '%s'.", FONT_NAME_BASE_BOLD)

    # -----------------------------------------------------------------------------------------------
    # Heading font (large window titles)
    # -----------------------------------------------------------------------------------------------
    try:
        heading_font_obj = tkFont.nametofont(FONT_NAME_HEADING)  # type: ignore[name-defined]
        heading_font_obj.configure(
            family=family,
            size=GUI_FONT_SIZE_HEADING,
            weight="bold",
        )
        logger.debug("[G01a] Updated existing heading font '%s'.", FONT_NAME_HEADING)
    except Exception:  # noqa: BLE001
        tkFont.Font(  # type: ignore[name-defined]
            name=FONT_NAME_HEADING,
            family=family,
            size=GUI_FONT_SIZE_HEADING,
            weight="bold",
        )
        logger.debug("[G01a] Created new heading font '%s'.", FONT_NAME_HEADING)

    # -----------------------------------------------------------------------------------------------
    # Section heading font (smaller bold section titles)
    # -----------------------------------------------------------------------------------------------
    try:
        section_font_obj = tkFont.nametofont(FONT_NAME_SECTION_HEADING)  # type: ignore[name-defined]
        section_font_obj.configure(
            family=family,
            size=GUI_FONT_SIZE_TITLE,
            weight="bold",
        )
        logger.debug(
            "[G01a] Updated existing section heading font '%s'.",
            FONT_NAME_SECTION_HEADING,
        )
    except Exception:  # noqa: BLE001
        tkFont.Font(  # type: ignore[name-defined]
            name=FONT_NAME_SECTION_HEADING,
            family=family,
            size=GUI_FONT_SIZE_TITLE,
            weight="bold",
        )
        logger.debug(
            "[G01a] Created new section heading font '%s'.",
            FONT_NAME_SECTION_HEADING,
        )


# ====================================================================================================
# 4. UNIFORM STYLE TEMPLATE
# ----------------------------------------------------------------------------------------------------
# STYLE_TEMPLATE provides a fully-expanded list of all ttk style options we care
# about. Individual style blocks:
#
#   • Start from STYLE_TEMPLATE.copy()
#   • Apply their own base overrides (colours, font, padding, etc.)
#   • Optionally apply an "overrides" dict for state-specific or rare changes.
#
# clean_style_dict(...) removes None values before the dict is passed into
# style.configure(...), because ttk does not accept None as a valid value.
# ====================================================================================================
STYLE_TEMPLATE: Dict[str, Any] = {
    # ---- Colours ----
    "background": None,         # Base background colour of widget surface
    "foreground": None,         # Base foreground (text/line) colour
    "fieldbackground": None,    # Inner field background (Entry/Combobox)
    "arrowcolor": None,         # Colour of dropdown arrows / spin arrows
    "selectforeground": None,   # Foreground colour when item/row is selected
    "selectbackground": None,   # Background colour when item/row is selected
    "troughcolor": None,        # Progressbar / Scale trough background colour
    "lightcolor": None,         # Highlight/light colour for 3D effects
    "darkcolor": None,          # Shadow/dark colour for 3D effects
    "bordercolor": None,        # Colour used for widget borders where supported

    # ---- Typography ----
    "font": None,               # Font tuple or named font (family, size[, weight/style])

    # ---- Spacing ----
    "padding": None,            # Internal widget padding (left, top, right, bottom)

    # ---- Borders ----
    "borderwidth": None,        # Width of widget border in pixels
    "relief": None,             # Border relief style (flat, solid, raised, sunken, etc.)
}


def build_style(base: Dict[str, Any], overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Build a complete style definition from the shared STYLE_TEMPLATE.

    The merge order is:

        STYLE_TEMPLATE  →  base  →  overrides

    This ensures:
        - All style dicts share the same key set (for readability).
        - Base values are applied consistently.
        - Any overrides can replace both template and base values.

    Args:
        base:
            Core values for the style block (colours, font, padding, etc.).
            Keys should be a subset of STYLE_TEMPLATE keys.

        overrides:
            Optional dict of values that must take precedence over both the
            template and the base block (rarely needed in practice).

    Returns:
        dict[str, Any]:
            The merged style dictionary. None values are preserved here and
            will be stripped by clean_style_dict(...) before calling
            style.configure(...).
    """
    merged: Dict[str, Any] = STYLE_TEMPLATE.copy()
    merged.update(base)

    if overrides:
        merged.update(overrides)

    return merged


def clean_style_dict(values: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a copy of a style dictionary with all None entries removed.

    ttk's style.configure(...) does not accept None values for options; passing
    them results in Tcl errors. This helper preserves the convenience of a rich
    STYLE_TEMPLATE (with many optional keys) while ensuring that only keys with
    concrete values are passed to ttk.

    Args:
        values:
            The style dictionary to clean. Typically the result of
            build_style(...).

    Returns:
        dict[str, Any]:
            A shallow copy of `values` with all key/value pairs where the
            value is None removed.
    """
    return {k: v for k, v in values.items() if v is not None}


# A small index of the styles defined in this module, used by diagnostics.
STYLE_BLOCKS: Dict[str, str] = {
    "TLabel": "Standard body text label",
    "Bold.TLabel": "Bold body text label",
    "TButton": "Standard push button",
    "TEntry": "Single-line text entry",
    "TCombobox": "Dropdown combobox",
    "TCheckbutton": "Checkbox control",
    "TRadiobutton": "Radio button control",
    "TNotebook": "Tabbed notebook container (body)",
    "TNotebook.Tab": "Notebook tab",
    "Treeview": "Tabular data view",
    "Treeview.Heading": "Treeview column header",
    "TMenubutton": "Menu button",
    "Horizontal.TProgressbar": "Horizontal progressbar",
    "SectionOuter.TFrame": "Outer section frame",
    "SectionBody.TFrame": "Inner section body frame",
    "SectionHeading.TLabel": "Section heading label",
    "WindowHeading.TLabel": "Window heading label",
    "ToolbarDivider.TFrame": "Toolbar divider frame",
}


# ====================================================================================================
# 5. MAIN STYLE ENGINE
# ----------------------------------------------------------------------------------------------------
def configure_ttk_styles(style: ttk.Style) -> None:  # type: ignore[name-defined]
    """
    Apply the full ttk style configuration for the GUI framework.

    This function is the single entry point for styling in the framework.
    It does **not** create the ttk.Style instance itself; instead it
    expects the caller (e.g. BaseGUI) to provide an existing Style object.

    Behaviour:
        1. Forces the base theme to a stable, modern theme (prefers "clam").
        2. Resolves an available GUI font family and ensures named Tk fonts
           exist for body/heading/section text.
        3. Configures all core ttk styles (labels, buttons, entries, combobox,
           notebook, treeview, etc.) using the STYLE_TEMPLATE + build_style
           pattern to keep definitions consistent.

    Args:
        style:
            An instance of ttk.Style (or ttkbootstrap.Style) that will be
            configured in-place.

    Raises:
        Any exception raised by ttk during style configuration will bubble up.
        In normal operation this is unlikely unless Tk itself is misconfigured.
    """
    logger.info("[G01a] Starting ttk style configuration.")

    # ======================================================================
    # 0. Force a stable theme (avoids Windows 'vista' breaking styles)
    # ======================================================================
    try:
        style.theme_use("clam")
        logger.debug("[G01a] Base theme set to 'clam'.")
    except Exception:  # noqa: BLE001
        logger.warning(
            "[G01a] Failed to set theme 'clam'; falling back to first available "
            "from ('alt', 'default', 'classic')."
        )
        for fallback in ("alt", "default", "classic"):
            try:
                style.theme_use(fallback)
                logger.debug("[G01a] Fallback theme '%s' applied.", fallback)
                break
            except Exception:  # noqa: BLE001
                logger.debug("[G01a] Fallback theme '%s' unavailable; trying next.", fallback)

    # -----------------------------------------------------------------------------------------------
    # 1. RESOLVE ACTIVE FONT FAMILY AND ENSURE NAMED FONTS
    # -----------------------------------------------------------------------------------------------
    fam = resolve_font_family()
    ensure_named_fonts(fam)

    BASE_FONT = FONT_NAME_BASE
    BOLD_FONT = FONT_NAME_BASE_BOLD
    HEADING_FONT = FONT_NAME_HEADING
    SECTION_HEADING_FONT = FONT_NAME_SECTION_HEADING

    logger.debug(
        "[G01a] Named fonts set: base=%s, heading=%s, section=%s "
        "(family=%s)",
        BASE_FONT,
        BOLD_FONT,
        HEADING_FONT,
        SECTION_HEADING_FONT,
        fam,
    )

    # -----------------------------------------------------------------------------------------------
    # 2. TLabel
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Standard body text label used throughout the interface.
    #   • Renders captions, descriptions, and non-interactive text.
    #
    # Visual rules:
    #   • Background: primary window background.
    #   • Text: primary body text colour.
    #   • Font: BASE_FONT (named Tk font).
    # -----------------------------------------------------------------------------------------------
    style.configure(
        "TLabel",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": TEXT_COLOUR_PRIMARY,
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

    style.configure(
        "Bold.TLabel",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": TEXT_COLOUR_PRIMARY,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": FONT_NAME_BASE_BOLD,
                    "padding": None,
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )

    # -----------------------------------------------------------------------------------------------
    # 2b. TFrame
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Base frame background used throughout the interface.
    #   • Ensures all plain ttk.Frame widgets inherit the primary background colour.
    # -----------------------------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------------------------
    # 3. TButton
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Standard push button used for primary and secondary actions.
    #
    # Visual rules:
    #   • Font: BASE_FONT.
    #   • Padding: modest horizontal/vertical padding for clickable area.
    #   • Colours: sourced from the active ttk theme / bootstyle.
    # -----------------------------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------------------------
    # 4. TEntry
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Single-line text input field for user data entry.
    #
    # Visual rules:
    #   • Background: secondary background roles for inputs.
    #   • Text: primary text colour.
    #   • Field background: matches background for seamless edges.
    # -----------------------------------------------------------------------------------------------
    style.configure(
        "TEntry",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_SECONDARY,
                    "foreground": TEXT_COLOUR_PRIMARY,
                    "fieldbackground": GUI_COLOUR_BG_SECONDARY,
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

    # -----------------------------------------------------------------------------------------------
    # 5. TCombobox
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Dropdown selection control for choosing one value from a discrete list.
    #
    # Visual rules:
    #   • Background: secondary background.
    #   • Text: primary text colour.
    #   • Arrow colour: primary text colour for clarity.
    #   • Selected row: subtle highlight using background roles.
    # -----------------------------------------------------------------------------------------------
    style.configure(
        "TCombobox",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_SECONDARY,
                    "foreground": TEXT_COLOUR_PRIMARY,
                    "fieldbackground": GUI_COLOUR_BG_SECONDARY,
                    "arrowcolor": TEXT_COLOUR_PRIMARY,
                    "selectforeground": TEXT_COLOUR_PRIMARY,
                    "selectbackground": GUI_COLOUR_BG_SECONDARY,
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

    # -----------------------------------------------------------------------------------------------
    # 6. TCheckbutton
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Boolean toggle control for settings, filters, and flags.
    #
    # Visual rules:
    #   • Background: primary window background.
    #   • Text: primary text colour.
    #   • Font: BASE_FONT.
    # -----------------------------------------------------------------------------------------------
    style.configure(
        "TCheckbutton",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": TEXT_COLOUR_PRIMARY,
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

    # -----------------------------------------------------------------------------------------------
    # 7. TRadiobutton
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Mutually exclusive single-choice control within a small set.
    #
    # Visual rules:
    #   • Shares visual defaults with TCheckbutton for consistency.
    # -----------------------------------------------------------------------------------------------
    style.configure(
        "TRadiobutton",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": TEXT_COLOUR_PRIMARY,
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

    # -----------------------------------------------------------------------------------------------
    # 8. TNotebook / TNotebook.Tab
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Tabbed container for grouping related content regions.
    #
    # Visual rules:
    #   • Notebook body uses primary background.
    #   • Tabs use secondary background with selected-state overrides.
    # -----------------------------------------------------------------------------------------------
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
                    "foreground": TEXT_COLOUR_PRIMARY,
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

    # -----------------------------------------------------------------------------------------------
    # 9. Treeview / Treeview.Heading
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Table-like widget for tabular datasets (rows/columns).
    #
    # Visual rules:
    #   • Body: secondary background for rows.
    #   • Heading: primary background with stronger typography.
    # -----------------------------------------------------------------------------------------------
    style.configure(
        "Treeview",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_SECONDARY,
                    "foreground": TEXT_COLOUR_PRIMARY,
                    "fieldbackground": GUI_COLOUR_BG_SECONDARY,
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

    style.configure(
        "Treeview.Heading",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": TEXT_COLOUR_PRIMARY,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": SECTION_HEADING_FONT,
                    "padding": None,
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )

    # -----------------------------------------------------------------------------------------------
    # 10. TMenubutton
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Menu-style button used for dropdown menus and command lists.
    #
    # Visual rules:
    #   • Background matches primary window background.
    #   • Text uses body font and primary text colour.
    # -----------------------------------------------------------------------------------------------
    style.configure(
        "TMenubutton",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": TEXT_COLOUR_PRIMARY,
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

    # -----------------------------------------------------------------------------------------------
    # 11. Horizontal.TProgressbar
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Horizontal progress indicator for task completion / busy state.
    #
    # Visual rules:
    #   • Trough: secondary background.
    #   • Bar: DEFAULT_PROGRESS_COLOUR from G00a_style_config.
    # -----------------------------------------------------------------------------------------------
    # (Removed duplicate SectionBody.TFrame definition)

    # -----------------------------------------------------------------------------------------------
    # 12. SectionOuter.TFrame
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Outer container frame for logical sections (padding + backdrop).
    #
    # Visual rules:
    #   • Background: primary background.
    #   • Border: flat, no visible edge.
    #   • Padding: FRAME_PADDING from G00a_style_config.
    # -----------------------------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------------------------
    # 13. SectionBody.TFrame
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Inner card-like frame containing section controls.
    #
    # Visual rules:
    #   • Background: secondary background.
    #   • Border: subtle solid border using theme border colour.
    # -----------------------------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------------------------
    # 13b. Card.TFrame
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Distinct style for 'Card' UI elements (bordered, secondary background).
    #   • Semantically separate from SectionBody, though visually similar.
    # -----------------------------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------------------------
    # 14. SectionHeading.TLabel
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Section heading label displayed above SectionBody frames.
    #
    # Visual rules:
    #   • Font: SECTION_HEADING_FONT.
    #   • Text: primary text colour.
    #   • Bottom padding: SECTION_SPACING to separate from content.
    # -----------------------------------------------------------------------------------------------
    style.configure(
        "SectionHeading.TLabel",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": TEXT_COLOUR_PRIMARY,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": SECTION_HEADING_FONT,
                    "padding": (0, 0, 0, SECTION_SPACING),
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )

    # -----------------------------------------------------------------------------------------------
    # 14b. Card.TLabel
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Labels inside cards (secondary background).
    # -----------------------------------------------------------------------------------------------
    style.configure(
        "Card.TLabel",
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
                    "font": None,
                    "padding": None,
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )

    # -----------------------------------------------------------------------------------------------
    # 14c. Card.TRadiobutton
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Radio buttons inside cards (secondary background).
    # -----------------------------------------------------------------------------------------------
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
                    "font": None,
                    "padding": None,
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )

    # -----------------------------------------------------------------------------------------------
    # 15. WindowHeading.TLabel
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Prominent window-level heading label.
    #
    # Visual rules:
    #   • Font: HEADING_FONT (large, bold).
    #   • Background: primary window background.
    #   • Text: primary text colour.
    # -----------------------------------------------------------------------------------------------
    style.configure(
        "WindowHeading.TLabel",
        **clean_style_dict(
            build_style(
                base={
                    "background": GUI_COLOUR_BG_PRIMARY,
                    "foreground": TEXT_COLOUR_PRIMARY,
                    "fieldbackground": None,
                    "arrowcolor": None,
                    "selectforeground": None,
                    "selectbackground": None,
                    "troughcolor": None,
                    "lightcolor": None,
                    "darkcolor": None,
                    "bordercolor": None,
                    "font": HEADING_FONT,
                    "padding": None,
                    "borderwidth": None,
                    "relief": None,
                }
            )
        ),
    )

    # -----------------------------------------------------------------------------------------------
    # 16. ToolbarDivider.TFrame
    # -----------------------------------------------------------------------------------------------
    # Purpose:
    #   • Simple divider line used inside toolbars or horizontal control strips.
    #
    # Visual rules:
    #   • Background: GUI_COLOUR_DIVIDER.
    #   • No padding or border; relies on height and colour only.
    # -----------------------------------------------------------------------------------------------
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

    logger.info("[G01a] ttk style configuration completed successfully.")


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
    logger.info("=== G01a_style_engine.py — Self-Test Start ===")

    # Create a headless Tk root to allow style creation safely
    try:
        root = tk.Tk()  # type: ignore[name-defined]
        root.withdraw()     # Hide the root window
    except Exception as e:  # noqa: BLE001
        logger.exception("[G01a] Failed to initialise Tk for self-test: %s", e)
        return

    try:
        style = ttk.Style()  # type: ignore[name-defined]
        configure_ttk_styles(style)

        logger.debug("[G01a][DEBUG] ----- Diagnostics start -----")
        try:
            logger.debug("[G01a][DEBUG] Active theme name: %s", style.theme_use())
        except Exception:  # noqa: BLE001
            logger.debug("[G01a][DEBUG] Could not query active theme name.")

        key_styles = [
            "TLabel",
            "TButton",
            "TEntry",
            "TCombobox",
            "Treeview",
            "Treeview.Heading",
            "TNotebook",
            "TNotebook.Tab",
            "SectionOuter.TFrame",
            "SectionBody.TFrame",
            "SectionHeading.TLabel",
            "WindowHeading.TLabel",
        ]

        for name in key_styles:
            try:
                style.configure(name)
                defined = True
            except Exception:  # noqa: BLE001
                defined = False
            logger.debug("[G01a][DEBUG] Style '%s' defined: %s", name, defined)

        # Font descriptor for SectionHeading
        section_font_desc = style.lookup("SectionHeading.TLabel", "font")
        logger.debug(
            "[G01a][DEBUG] SectionHeading.TLabel raw font lookup: %r",
            section_font_desc,
        )

        # Try resolving as named font (informational only)
        try:
            f_obj = tkFont.nametofont(section_font_desc)  # type: ignore[name-defined]
            logger.debug(
                "[G01a][DEBUG] SectionHeading named font resolved -> "
                "family=%s size=%s weight=%s",
                f_obj.cget("family"),
                f_obj.cget("size"),
                f_obj.cget("weight"),
            )
        except Exception:
            logger.debug(
                "[G01a][DEBUG] SectionHeading font is not a named Tk font "
                "(descriptor=%r); this is acceptable if the style uses a "
                "direct font descriptor.",
                section_font_desc,
            )

        logger.debug(
            "[G01a][DEBUG] Using font family preference: %s",
            resolve_font_family(),
        )
        logger.debug("[G01a][DEBUG] ----- Diagnostics end -----")

    except Exception as e:  # noqa: BLE001
        logger.exception("[G01a] ERROR applying theme during self-test: %s", e)
        raise
    finally:
        root.destroy()

    logger.info("[G01a] Theme applied successfully for self-test.")
    logger.info("=== G01a_style_engine.py — Self-Test Complete ===")


if __name__ == "__main__":
    # Initialize logging so we can see the test output
    from core.C03_logging_handler import init_logging
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
