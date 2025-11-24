# ====================================================================================================
# G02e_widget_components.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Provides reusable, app-level Tkinter/ttk widgets for all GUI modules.
#
#   Hybrid approach:
#       • Atomic widgets:
#             - AppTitle         → Large page/window titles
#             - SectionHeader    → Section headings within a window
#             - InfoBanner       → Soft information banner (ℹ)
#             - WarningBanner    → Warning/attention banner (⚠)
#             - DangerBanner     → Error/critical banner (⛔)
#             - ButtonRow        → Right-aligned row of action buttons
#
#       • Structured containers:
#             - SectionContainer → Title + (optional) subtitle + bordered body area
#             - Card             → Lightweight card with optional title and body
#             - SummaryBox       → Compact two-column key/value summary list
#
# Usage (example):
#   from gui.G02e_widget_components import (
#       AppTitle,
#       SectionHeader,
#       InfoBanner,
#       WarningBanner,
#       DangerBanner,
#       ButtonRow,
#       SectionContainer,
#       Card,
#       SummaryBox,
#   )
#
#   class MyWindow(BaseGUI):
#       def build_widgets(self):
#           title = AppTitle(self.main_frame, text="Demo Window")
#           title.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
#
#           section = SectionContainer(self.main_frame, title="Example Section")
#           section.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
#
#           ttk.Label(section.body, text="Inside the section").grid(row=0, column=0, sticky="w")
#
# Integration:
#   - Respects global fonts/colours from G01a_style_config (with safe fallbacks).
#   - Intended to be used from BaseGUI subclasses (G01e_gui_base).
#   - Plays nicely with layout primitives and style engine, but has no hard dependency.
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

from gui.G00a_gui_packages import tk, ttk  # Explicit imports for classes
from gui.G01e_gui_base import BaseGUI

# Import style configuration in a SAFE way (no hard dependency on specific constant names)
try:
    import gui.G01a_style_config as style
except Exception:  # pragma: no cover - extremely defensive
    style = None


# ====================================================================================================
# 3. STYLE ACCESS HELPERS — SAFE ACCESS TO STYLE CONSTANTS
# ----------------------------------------------------------------------------------------------------
def get_first_font_family(candidate):
    """
    Description:
        Normalise a font family configuration to a single Tk-compatible family name.

    Args:
        candidate:
            Either:
                • A single family string (e.g. "Segoe UI")
                • A list/tuple of family names (preference order)
                • None (no configured family)

    Returns:
        str:
            A single font family string. Falls back to "Segoe UI" if no valid
            candidate is provided.

    Raises:
        None.

    Notes:
        - This function is defensive: it never raises on bad input.
        - Intended for internal use by build_font_tuple.
    """
    if candidate is None:
        return "Segoe UI"
    if isinstance(candidate, (list, tuple)):
        return candidate[0]
    return candidate


def build_font_tuple(size_key: str, default_size: int, weight: str | None = None):
    """
    Description:
        Build a Tk font tuple using values from gui.G01a_style_config where possible,
        with safe fallbacks when the style module or attributes are missing.

    Args:
        size_key:
            Name of the size attribute on the style module
            (e.g. "GUI_FONT_SIZE_HEADING").
        default_size:
            Fallback font size used when style is missing or incomplete.
        weight:
            Optional font weight ("bold", etc.). If None, the returned tuple is
            (family, size). If provided, returns (family, size, weight).

    Returns:
        tuple:
            A Tk-compatible font tuple suitable for use as the 'font' option on
            Tk/ttk widgets.

    Raises:
        None.

    Notes:
        - Prefers style.GUI_FONT_DISPLAY, then style.GUI_FONT_PRIMARY_FAMILY.
        - Falls back to "Segoe UI" and default_size if style is unavailable.
    """
    family = None
    size = default_size

    if style is not None:
        family = getattr(style, "GUI_FONT_DISPLAY", None)
        if family is None:
            family = getattr(style, "GUI_FONT_PRIMARY_FAMILY", None)
        size = getattr(style, size_key, getattr(style, "GUI_FONT_SIZE_DEFAULT", default_size))

    family = get_first_font_family(family)
    if weight:
        return (family, size, weight)
    return (family, size)


def get_style_colour(colour_attribute_name: str, fallback: str):
    """
    Description:
        Safely retrieve a colour value from gui.G01a_style_config, falling back
        to the supplied default when the style module or attribute is missing.

    Args:
        colour_attribute_name:
            Attribute name on the style module (e.g. "COLOUR_TEXT_DEFAULT").
        fallback:
            Hex colour string to use when the style attribute is unavailable.

    Returns:
        str:
            A hex colour string suitable for Tk/ttk foreground/background values.

    Raises:
        None.

    Notes:
        - This function never raises on missing style modules or attributes.
        - Keeps widget components resilient when the theme evolves.
    """
    if style is not None and hasattr(style, colour_attribute_name):
        return getattr(style, colour_attribute_name)
    return fallback


# Common colour lookups (names chosen to be descriptive but safe)
COLOUR_BG_SECTION = get_style_colour("COLOUR_BRAND_WHITE", "#FFFFFF")
COLOUR_BG_CARD = get_style_colour("COLOUR_CARD_BG", "#FFFFFF")
COLOUR_BORDER_LIGHT = get_style_colour("COLOUR_BORDER_LIGHT", "#D0D4DA")
COLOUR_TEXT_DEFAULT = get_style_colour("COLOUR_TEXT_DEFAULT", "#1F2933")
COLOUR_TEXT_MUTED = get_style_colour("COLOUR_TEXT_MUTED", "#6B7280")

COLOUR_INFO_BG = get_style_colour("COLOUR_INFO_BG", "#E5F3FF")
COLOUR_INFO_BORDER = get_style_colour("COLOUR_INFO_BORDER", "#60A5FA")

COLOUR_WARNING_BG = get_style_colour("COLOUR_WARNING_BG", "#FEF3C7")
COLOUR_WARNING_BORDER = get_style_colour("COLOUR_WARNING_BORDER", "#FBBF24")

COLOUR_DANGER_BG = get_style_colour("COLOUR_DANGER_BG", "#FEE2E2")
COLOUR_DANGER_BORDER = get_style_colour("COLOUR_DANGER_BORDER", "#F87171")


# ====================================================================================================
# 4. ATOMIC WIDGETS
# ----------------------------------------------------------------------------------------------------
class AppTitle(ttk.Label):
    """
    Description:
        Large page-level title label for the current window.

    Args:
        parent:
            Parent widget (typically BaseGUI.main_frame or a section body).
        text:
            Title text to display.
        **kwargs:
            Additional ttk.Label keyword arguments.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Uses the display/heading font from gui.G01a_style_config where available.
        - Callers can override the font by passing font=... in **kwargs.
    """

    def __init__(self, parent, text: str, **kwargs):
        font = kwargs.pop("font", build_font_tuple("GUI_FONT_SIZE_HEADING", 14, weight="bold"))
        super().__init__(parent, text=text, font=font, **kwargs)


class SectionHeader(ttk.Label):
    """
    Description:
        Section header text within a window or container.

    Args:
        parent:
            Parent widget for the header.
        text:
            Header text to display.
        **kwargs:
            Additional ttk.Label keyword arguments. Supports:
                - style: explicit ttk style name
                - font:  explicit font override

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Defaults to style "SectionHeading.TLabel" if no explicit style is provided.
        - If style is "SectionHeading.TLabel" and no font is specified, uses the
          heading font from gui.G01a_style_config.
    """

    def __init__(self, parent, text: str, **kwargs):
        # Prefer existing style if present; otherwise specify font directly.
        style_name = kwargs.pop("style", None)
        if style_name is None:
            style_name = "SectionHeading.TLabel"

        # Only set font explicitly if caller did not override style.
        font = kwargs.pop("font", None)
        if font is None and style_name == "SectionHeading.TLabel":
            font = build_font_tuple("GUI_FONT_SIZE_HEADING", 14, weight="bold")

        super().__init__(parent, text=text, style=style_name, font=font, **kwargs)


class InfoBanner(ttk.Frame):
    """
    Description:
        Soft information banner used to convey non-critical information.

    Layout:
        [ ICON ]  Message text (wrapped)

    Args:
        parent:
            Parent widget for the banner.
        text:
            Message text to display.
        icon:
            Symbol to display on the left (default: "ℹ").
        **kwargs:
            Additional ttk.Frame keyword arguments.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Uses plain Tk frames internally for precise control over background
          and border colours.
        - Colours are theme-aware via get_style_colour.
    """

    def __init__(self, parent, text: str, icon: str = "ℹ", **kwargs):
        super().__init__(parent, **kwargs)

        # Use a plain Tk frame inside to control background colour precisely
        self.outer_frame = tk.Frame(
            self,
            bg=COLOUR_INFO_BG,
            highlightbackground=COLOUR_INFO_BORDER,
            highlightcolor=COLOUR_INFO_BORDER,
            highlightthickness=1,
            bd=0,
        )
        self.outer_frame.pack(fill="x", expand=True)

        inner_frame = tk.Frame(self.outer_frame, bg=COLOUR_INFO_BG)
        inner_frame.pack(fill="x", expand=True, padx=8, pady=6)

        icon_label = tk.Label(
            inner_frame,
            text=icon,
            bg=COLOUR_INFO_BG,
            fg=COLOUR_TEXT_DEFAULT,
        )
        icon_label.pack(side="left", anchor="n", padx=(0, 6))

        text_label = tk.Label(
            inner_frame,
            text=text,
            bg=COLOUR_INFO_BG,
            fg=COLOUR_TEXT_DEFAULT,
            justify="left",
            wraplength=600,
        )
        text_label.pack(side="left", anchor="w", fill="x", expand=True)


class WarningBanner(InfoBanner):
    """
    Description:
        Warning banner used for cautions / attention messages.

    Args:
        parent:
            Parent widget for the banner.
        text:
            Warning message text.
        icon:
            Icon symbol to display (default: "⚠").
        **kwargs:
            Additional ttk.Frame keyword arguments.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Reuses InfoBanner layout but applies the warning colour palette.
    """

    def __init__(self, parent, text: str, icon: str = "⚠", **kwargs):
        # Initialise base banner then overwrite colours
        super().__init__(parent, text=text, icon=icon, **kwargs)

        # Re-skin the outer frame to warning palette
        self.outer_frame.configure(
            bg=COLOUR_WARNING_BG,
            highlightbackground=COLOUR_WARNING_BORDER,
            highlightcolor=COLOUR_WARNING_BORDER,
        )
        for child in self.outer_frame.winfo_children():
            child.configure(bg=COLOUR_WARNING_BG)
            for grandchild in child.winfo_children():
                grandchild.configure(bg=COLOUR_WARNING_BG, fg=COLOUR_TEXT_DEFAULT)


class DangerBanner(InfoBanner):
    """
    Description:
        Danger banner used for error / critical alerts.

    Args:
        parent:
            Parent widget for the banner.
        text:
            Error/critical message text.
        icon:
            Icon symbol to display (default: "⛔").
        **kwargs:
            Additional ttk.Frame keyword arguments.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Reuses InfoBanner layout but applies the danger colour palette.
    """

    def __init__(self, parent, text: str, icon: str = "⛔", **kwargs):
        super().__init__(parent, text=text, icon=icon, **kwargs)

        self.outer_frame.configure(
            bg=COLOUR_DANGER_BG,
            highlightbackground=COLOUR_DANGER_BORDER,
            highlightcolor=COLOUR_DANGER_BORDER,
        )
        for child in self.outer_frame.winfo_children():
            child.configure(bg=COLOUR_DANGER_BG)
            for grandchild in child.winfo_children():
                grandchild.configure(bg=COLOUR_DANGER_BG, fg=COLOUR_TEXT_DEFAULT)


class ButtonRow(ttk.Frame):
    """
    Description:
        Simple horizontal row of buttons, right-aligned by default.

    Usage:
        row = ButtonRow(parent, buttons=[
            ("Run", self.on_run),
            ("Close", self.on_close),
        ])
        row.grid(row=99, column=0, sticky="e", padx=10, pady=(10, 5))

    Args:
        parent:
            Parent widget for the button row.
        buttons:
            Optional list of (text, command) tuples to initialise the row.
        **kwargs:
            Additional ttk.Frame keyword arguments.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Buttons are created as ttk.Button instances inside an internal container
          frame to simplify right-alignment.
    """

    def __init__(self, parent, buttons: list[tuple[str, callable]] | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.columnconfigure(0, weight=1)

        self.button_container = ttk.Frame(self)
        self.button_container.grid(row=0, column=0, sticky="e")

        self.button_widgets: list[ttk.Button] = []
        if buttons:
            for text, cmd in buttons:
                self.add_button(text=text, command=cmd)

    def add_button(self, text: str, command=None, style_name: str | None = None) -> ttk.Button:
        """
        Description:
            Add a button to the row and return the created ttk.Button instance.

        Args:
            text:
                Button label text.
            command:
                Callable to invoke when the button is pressed.
            style_name:
                Optional ttk style name for the button.

        Returns:
            ttk.Button:
                The created button instance.

        Raises:
            None.

        Notes:
            - New buttons are appended to the right of existing ones.
        """
        style_kw = {}
        if style_name:
            style_kw["style"] = style_name

        button = ttk.Button(self.button_container, text=text, command=command, **style_kw)
        if self.button_widgets:
            button.grid(row=0, column=len(self.button_widgets), padx=(6, 0))
        else:
            button.grid(row=0, column=0)
        self.button_widgets.append(button)
        return button


# ====================================================================================================
# 5. STRUCTURED CONTAINERS
# ----------------------------------------------------------------------------------------------------
class SectionContainer(ttk.Frame):
    """
    Description:
        Section container with a title above and a bordered content area.

    Layout:
        Title (SectionHeader)
        [ Bordered body frame ]

    Args:
        parent:
            Parent widget.
        title:
            Section title text (required).
        subtitle:
            Optional subtitle/explanatory text.
        body_padding:
            Tuple (left, top, right, bottom) padding for the inner body frame.
        **kwargs:
            Additional ttk.Frame keyword arguments.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Widgets should be added to section.body, not directly to SectionContainer.
        - The container configures its own grid to make the body stretch with the window.
    """

    def __init__(
        self,
        parent,
        title: str,
        subtitle: str | None = None,
        body_padding: tuple[int, int, int, int] = (10, 10, 10, 10),
        **kwargs,
    ):
        super().__init__(parent, **kwargs)

        self.columnconfigure(0, weight=1)

        # Title row
        self.title_label = SectionHeader(self, text=title)
        self.title_label.grid(row=0, column=0, sticky="w", padx=(0, 0), pady=(0, 2))

        if subtitle:
            self.subtitle_label = ttk.Label(
                self,
                text=subtitle,
                foreground=COLOUR_TEXT_MUTED,
                wraplength=800,
                justify="left",
            )
            self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(0, 6))
            body_row = 2
        else:
            self.subtitle_label = None
            body_row = 1

        # Outer "card" / section border (Tk frame for fine control)
        self.outer_frame = tk.Frame(
            self,
            bg=COLOUR_BG_SECTION,
            highlightbackground=COLOUR_BORDER_LIGHT,
            highlightcolor=COLOUR_BORDER_LIGHT,
            highlightthickness=1,
            bd=0,
        )
        self.outer_frame.grid(row=body_row, column=0, sticky="nsew", pady=(2, 0))
        self.rowconfigure(body_row, weight=1)

        # Inner body container; user will add widgets to .body
        left, top, right, bottom = body_padding
        self.body = tk.Frame(self.outer_frame, bg=COLOUR_BG_SECTION)
        self.body.pack(
            fill="both",
            expand=True,
            padx=(left, right),
            pady=(top, bottom),
        )

        # Make grid usage inside .body convenient
        self.body.grid_rowconfigure(99, weight=1)
        self.body.grid_columnconfigure(0, weight=1)


class Card(ttk.Frame):
    """
    Description:
        Lightweight card container used for dashboards or summary tiles.

    Layout:
        Optional title
        Body frame (for arbitrary content)

    Args:
        parent:
            Parent widget.
        title:
            Optional card title text.
        **kwargs:
            Additional ttk.Frame keyword arguments.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Widgets should be added to card.body.
    """

    def __init__(self, parent, title: str | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.columnconfigure(0, weight=1)

        self.outer_frame = tk.Frame(
            self,
            bg=COLOUR_BG_CARD,
            highlightbackground=COLOUR_BORDER_LIGHT,
            highlightcolor=COLOUR_BORDER_LIGHT,
            highlightthickness=1,
            bd=0,
        )
        self.outer_frame.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)

        inner_frame = tk.Frame(self.outer_frame, bg=COLOUR_BG_CARD)
        inner_frame.pack(fill="both", expand=True, padx=10, pady=8)

        row_index = 0
        self.title_label = None
        if title:
            self.title_label = tk.Label(
                inner_frame,
                text=title,
                bg=COLOUR_BG_CARD,
                fg=COLOUR_TEXT_DEFAULT,
                font=build_font_tuple("GUI_FONT_SIZE_HEADING", 12, weight="bold"),
                anchor="w",
            )
            self.title_label.grid(row=row_index, column=0, sticky="w", pady=(0, 4))
            row_index += 1

        # Body frame for user widgets
        self.body = tk.Frame(inner_frame, bg=COLOUR_BG_CARD)
        self.body.grid(row=row_index, column=0, sticky="nsew")
        inner_frame.grid_rowconfigure(row_index, weight=1)
        inner_frame.grid_columnconfigure(0, weight=1)


class SummaryBox(ttk.Frame):
    """
    Description:
        Simple two-column key/value summary area.

    Usage:
        summary = SummaryBox(parent, items=[
            ("Orders (Last 4w)", "12,345"),
            ("DTC%", "64.2%"),
        ])

    Args:
        parent:
            Parent widget.
        items:
            Optional initial list of (label, value) pairs.
        **kwargs:
            Additional ttk.Frame keyword arguments.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - New rows can be appended via add_item(label, value).
    """

    def __init__(self, parent, items: list[tuple[str, str]] | None = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.summary_container = ttk.Frame(self)
        self.summary_container.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.summary_container.columnconfigure(0, weight=1)
        self.summary_container.columnconfigure(1, weight=0)

        self.current_row_index = 0
        if items:
            for label, value in items:
                self.add_item(label, value)

    def add_item(self, label: str, value: str):
        """
        Description:
            Add a new key/value row to the summary box.

        Args:
            label:
                Left-hand label text.
            value:
                Right-hand value text.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Rows are appended from top to bottom.
        """
        lbl = ttk.Label(self.summary_container, text=label, foreground=COLOUR_TEXT_MUTED)
        val = ttk.Label(self.summary_container, text=value, foreground=COLOUR_TEXT_DEFAULT)

        lbl.grid(row=self.current_row_index, column=0, sticky="w", padx=(0, 8), pady=1)
        val.grid(row=self.current_row_index, column=1, sticky="e", pady=1)

        self.current_row_index += 1


# ====================================================================================================
# 6. DEMO WINDOW (MAIN TEST)
# ----------------------------------------------------------------------------------------------------
class WidgetComponentsDemoWindow(BaseGUI):
    """
    Description:
        Simple self-test window to preview G02e widget components in isolation.

    Args:
        None (constructed via BaseGUI standard pattern).

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Intended for manual QA during development only.
        - Should not be imported or used by production GUI modules.
    """

    def __init__(self):
        self.demo_built_flag = False
        super().__init__(title="G02e_widget_components — Demo")
        self.build_demo_content()

    def build_widgets(self):
        """
        Description:
            Required BaseGUI override. Ensures the demo content exists and
            avoids duplicate construction if BaseGUI calls this more than once.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Uses demo_built_flag to keep the demo idempotent.
        """
        if not self.demo_built_flag:
            self.build_demo_content()

    def build_demo_content(self):
        """
        Description:
            Construct the full demo layout showcasing banners, sections,
            cards, and summaries.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Content is rendered into self.main_frame (scrollable BaseGUI area).
        """
        self.demo_built_flag = True

        # Make sure main_frame stretches
        self.main_frame.columnconfigure(0, weight=1)

        # Title
        title = AppTitle(self.main_frame, text="G02e Widget Components — Demo")
        title.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))

        subtitle = ttk.Label(
            self.main_frame,
            text=(
                "Demonstrates atomic widgets (titles, banners, button rows) "
                "and structured containers (sections, cards, summary boxes)."
            ),
            wraplength=900,
            foreground=COLOUR_TEXT_MUTED,
        )
        subtitle.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))

        # Info banner
        info_banner = InfoBanner(
            self.main_frame,
            text=(
                "This is an informational banner. Use it to communicate important, "
                "non-critical information to the user."
            ),
        )
        info_banner.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))

        # Warning banner
        warning_banner = WarningBanner(
            self.main_frame,
            text="This is a warning banner. Use it for things that need attention.",
        )
        warning_banner.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 10))

        # Danger banner
        danger_banner = DangerBanner(
            self.main_frame,
            text="This is a danger banner. Use it for critical errors or blocking issues.",
        )
        danger_banner.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 10))

        # Main section
        section = SectionContainer(
            self.main_frame,
            title="Main Section Container",
            subtitle="SectionContainer wraps a title, optional subtitle, and a bordered body area.",
        )
        section.grid(row=5, column=0, sticky="nsew", padx=16, pady=(10, 10))
        self.main_frame.rowconfigure(5, weight=1)

        # Inside section.body, add a card + summary box
        section.body.grid_columnconfigure(0, weight=1)
        section.body.grid_columnconfigure(1, weight=1)

        card = Card(section.body, title="Example Card")
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))
        section.body.rowconfigure(0, weight=1)

        ttk.Label(
            card.body,
            text="Use cards for grouped information or dashboard tiles.",
            wraplength=350,
        ).grid(row=0, column=0, sticky="w")

        summary = SummaryBox(
            section.body,
            items=[
                ("Orders (Last 4 weeks)", "12,345"),
                ("DTC %", "64.2%"),
                ("YOY vs LY", "+5.1%"),
            ],
        )
        summary.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 6))

        # Button row at the bottom
        button_row = ButtonRow(
            self.main_frame,
            buttons=[
                ("Primary Action", self.on_primary_clicked),
                ("Close", self.close),
            ],
        )
        button_row.grid(row=99, column=0, sticky="ew", padx=16, pady=(10, 16))

    # ------------------------------------------------------------------------------------------------
    # Demo callbacks
    # ------------------------------------------------------------------------------------------------
    def on_primary_clicked(self):
        """
        Description:
            Demo callback for the primary action button.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - For now, prints to stdout; you can later wire this to logging
              or real actions as needed.
        """
        print("Primary action triggered from G02e widget components demo window.")
        # logger.info("Primary action triggered from G02e widget components demo window.")
        # (Uncomment logging line above and remove print when ready to standardise.)
        

# ====================================================================================================
# 7. MAIN
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app = WidgetComponentsDemoWindow()
    app.mainloop()
