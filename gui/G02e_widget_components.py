# ====================================================================================================
# G02e_widget_components.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Provides reusable, app-level composite widgets for all GUI modules.
#
#   COMPOSITE widgets (unique to this module):
#       • InfoBanner       → Soft information banner with icon (ℹ)
#       • WarningBanner    → Warning/attention banner with icon (⚠)
#       • DangerBanner     → Error/critical banner with icon (⛔)
#       • ButtonRow        → Right-aligned row of action buttons
#       • SummaryBox       → Compact two-column key/value summary list
#
#   DEPRECATED (use these instead):
#       • AppTitle         → Use make_label(..., category="WindowHeading")
#       • SectionHeader    → Use make_label(..., category="SectionHeading")
#       • SectionContainer → Use G02b_container_patterns.create_section_grid()
#       • Card             → Use G02b_container_patterns.create_card_grid()
#
# Usage (example):
#   from gui.G02e_widget_components import (
#       InfoBanner,
#       WarningBanner,
#       DangerBanner,
#       ButtonRow,
#       SummaryBox,
#   )
#
#   class MyWindow(BaseGUI):
#       def build_widgets(self):
#           banner = InfoBanner(self.main_frame, "Important information here")
#           banner.pack(fill="x", pady=(0, 10))
#
#           buttons = ButtonRow(self.main_frame, buttons=[
#               ("Save", self.on_save),
#               ("Cancel", self.on_cancel),
#           ])
#           buttons.pack(fill="x")
#
# Integration:
#   - Colours from G01a_style_config.
#   - Intended to be used from BaseGUI subclasses (G01e_gui_base).
#   - Works with G01c widget primitives and G02b container patterns.
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

from gui.G00a_gui_packages import tk, ttk
from gui.G01e_gui_base import BaseGUI
from gui.G01a_style_config import (
    GUI_COLOUR_BG_PRIMARY,
    GUI_COLOUR_BG_SECONDARY,
    GUI_COLOUR_STATUS_SUCCESS,
    GUI_COLOUR_STATUS_WARNING,
    GUI_COLOUR_STATUS_ERROR,
    COLOUR_STATUS_GREEN,
    COLOUR_STATUS_AMBER,
    COLOUR_STATUS_RED,
    COLOUR_PRIMARY_LIGHT,
    COLOUR_SECONDARY_LIGHT,
    COLOUR_SECONDARY_DARK,
    TEXT_COLOUR_PRIMARY,
    TEXT_COLOUR_SECONDARY,
    GUI_FONT_FAMILY,
    GUI_FONT_SIZE_DEFAULT,
    FRAME_PADDING,
)
from gui.G01c_widget_primitives import make_label, make_button
from gui.G02b_container_patterns import create_section_grid, create_card_grid


# ====================================================================================================
# 3. COLOUR CONSTANTS FOR BANNERS (derived from G01a)
# ----------------------------------------------------------------------------------------------------
# Banner backgrounds use lighter tints of the status colours
# Banner borders use the status colours directly

COLOUR_INFO_BG = COLOUR_PRIMARY_LIGHT
COLOUR_INFO_BORDER = GUI_COLOUR_STATUS_SUCCESS  # Using success colour for info (teal-ish)

COLOUR_WARNING_BG = "#FEF3C7"  # Light amber tint
COLOUR_WARNING_BORDER = COLOUR_STATUS_AMBER

COLOUR_DANGER_BG = "#FEE2E2"  # Light red tint
COLOUR_DANGER_BORDER = COLOUR_STATUS_RED

COLOUR_BG_SECTION = GUI_COLOUR_BG_PRIMARY
COLOUR_BG_CARD = GUI_COLOUR_BG_PRIMARY
COLOUR_BORDER_LIGHT = COLOUR_SECONDARY_DARK
COLOUR_TEXT_DEFAULT = TEXT_COLOUR_SECONDARY
COLOUR_TEXT_MUTED = TEXT_COLOUR_SECONDARY


# ====================================================================================================
# 4. ATOMIC WIDGETS
# ----------------------------------------------------------------------------------------------------
# NOTE: AppTitle and SectionHeader are DEPRECATED. Use make_label() instead.
# They are kept for backwards compatibility only.

class AppTitle(ttk.Label):
    """
    DEPRECATED: Use make_label(parent, text, category="WindowHeading", surface="Primary", weight="Bold")

    Description:
        Large page-level title label for the current window.
    """

    def __init__(self, parent, text: str, **kwargs):
        logger.warning("[G02e] AppTitle is deprecated. Use make_label(..., category='WindowHeading') instead.")
        style_name = kwargs.pop("style", "Primary.WindowHeading.Bold.TLabel")
        super().__init__(parent, text=text, style=style_name, **kwargs)


class SectionHeader(ttk.Label):
    """
    DEPRECATED: Use make_label(parent, text, category="SectionHeading", surface="Primary", weight="Bold")

    Description:
        Section header text within a window or container.
    """

    def __init__(self, parent, text: str, **kwargs):
        logger.warning("[G02e] SectionHeader is deprecated. Use make_label(..., category='SectionHeading') instead.")
        style_name = kwargs.pop("style", "Primary.SectionHeading.Bold.TLabel")
        super().__init__(parent, text=text, style=style_name, **kwargs)


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
        - Colours are derived from G01a_style_config.
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
            font=(GUI_FONT_FAMILY, GUI_FONT_SIZE_DEFAULT),
        )
        icon_label.pack(side="left", anchor="n", padx=(0, 6))

        text_label = tk.Label(
            inner_frame,
            text=text,
            bg=COLOUR_INFO_BG,
            fg=COLOUR_TEXT_DEFAULT,
            justify="left",
            wraplength=600,
            font=(GUI_FONT_FAMILY, GUI_FONT_SIZE_DEFAULT),
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
# 5. STRUCTURED CONTAINERS (DEPRECATED - use G02b_container_patterns instead)
# ----------------------------------------------------------------------------------------------------
class SectionContainer(ttk.Frame):
    """
    DEPRECATED: Use G02b_container_patterns.create_section_grid() instead.

    Description:
        Section container with a title above and a bordered content area.
    """

    def __init__(
        self,
        parent,
        title: str,
        subtitle: str | None = None,
        body_padding: tuple[int, int, int, int] = (10, 10, 10, 10),
        **kwargs,
    ):
        logger.warning("[G02e] SectionContainer is deprecated. Use create_section_grid() from G02b instead.")
        super().__init__(parent, **kwargs)

        self.columnconfigure(0, weight=1)

        # Title row using make_label
        self.title_label = make_label(
            self,
            title,
            category="SectionHeading",
            surface="Primary",
            weight="Bold",
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=(0, 0), pady=(0, 2))

        if subtitle:
            self.subtitle_label = make_label(
                self,
                subtitle,
                category="Body",
                surface="Primary",
                weight="Normal",
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
    DEPRECATED: Use G02b_container_patterns.create_card_grid() instead.

    Description:
        Lightweight card container used for dashboards or summary tiles.
    """

    def __init__(self, parent, title: str | None = None, **kwargs):
        logger.warning("[G02e] Card is deprecated. Use create_card_grid() from G02b instead.")
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
            self.title_label = make_label(
                inner_frame,
                title,
                category="SectionHeading",
                surface="Secondary",
                weight="Bold",
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

        # Title - using make_label instead of deprecated AppTitle
        title = make_label(
            self.main_frame,
            "G02e Widget Components — Demo",
            category="WindowHeading",
            surface="Primary",
            weight="Bold",
        )
        title.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 4))

        subtitle = make_label(
            self.main_frame,
            "Demonstrates banners, button rows, and summary boxes. "
            "Note: AppTitle, SectionHeader, SectionContainer, Card are deprecated.",
            category="Body",
            surface="Primary",
            weight="Normal",
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

        # Section using G02b pattern instead of deprecated SectionContainer
        section = create_section_grid(
            self.main_frame,
            row=5,
            column=0,
            title="Section via G02b (Recommended)",
        )
        self.main_frame.rowconfigure(5, weight=0)

        # Inside section.body, add a summary box
        section.body.grid_columnconfigure(0, weight=1)

        make_label(
            section.body,
            "Use create_section_grid() from G02b for sections.",
            category="Body",
            surface="Secondary",
            weight="Normal",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        summary = SummaryBox(
            section.body,
            items=[
                ("Orders (Last 4 weeks)", "12,345"),
                ("DTC %", "64.2%"),
                ("YOY vs LY", "+5.1%"),
            ],
        )
        summary.grid(row=1, column=0, sticky="nsew", pady=(0, 6))

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
    init_logging()
    logger.info("=== G02e_widget_components demo start ===")
    app = WidgetComponentsDemoWindow()
    app.mainloop()
    logger.info("=== G02e_widget_components demo end ===")