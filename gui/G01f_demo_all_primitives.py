# ====================================================================================================
# G01f_demo_all_primitives.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Developer-facing "component explorer" for the GUI Boilerplate framework.
#   Demonstrates and documents the core 00/01 layer:
#       • G00a_style_config       — Theme tokens (fonts/colours/spacing)
#       • G01a_style_engine       — ttk style engine
#       • G01b_widget_primitives  — Low-level widget factories
#       • G01c_layout_primitives  — Layout/typography helpers
#       • G01d_gui_base           — BaseGUI scrollable window shell
#
#   The window is structured as a tabbed, two-column documentation view:
#       Left  column → Developer documentation (what/when/how, usage, notes).
#       Right column → Live examples using the real framework primitives.
#
# Usage:
#   python gui/G01_demo_all_primitives.py
#
#   This file is for learning + QA. It should not be imported by production
#   code, but it is safe to run at any time while developing the framework.
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
from gui.G01a_style_config import *
from gui.G01b_style_engine import FONT_NAME_BASE_BOLD
from gui.G01c_widget_primitives import (
    make_heading,
    make_subheading,
    make_label,
    make_status_label,
    make_entry,
    make_textarea,
    make_combobox,
    make_checkbox,
    make_radio,
    make_switch,
    make_divider,
    make_spacer
)
from gui.G01d_layout_primitives import (
    heading as lp_heading,
    subheading as lp_subheading,
    body_text as lp_body_text,
    divider as lp_divider,
    spacer as lp_spacer
)
from gui.G01e_gui_base import BaseGUI


# ====================================================================================================
# 3. SHARED DOC/EXAMPLE HELPERS
# ----------------------------------------------------------------------------------------------------
def create_two_column_panel(parent: ttk.Frame) -> tuple[ttk.Frame, ttk.Frame]:  # type: ignore[name-defined]
    """Create a 50/50 two-column layout inside *parent*.

    Returns (left_frame, right_frame).
    """
    container = ttk.Frame(parent)
    container.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)

    container.columnconfigure(0, weight=1)
    container.columnconfigure(1, weight=1)

    left = ttk.Frame(container)
    right = ttk.Frame(container)

    left.grid(row=0, column=0, sticky="nsew", padx=(0, FRAME_PADDING))
    right.grid(row=0, column=1, sticky="nsew", padx=(FRAME_PADDING, 0))

    return left, right


def doc_title(parent: ttk.Frame, text: str) -> None:  # type: ignore[name-defined]
    """Section title for the documentation column."""
    make_subheading(parent, text, pady=(SECTION_TITLE_SPACING, 4)).pack(anchor="w")


def doc_text(parent: ttk.Frame, text: str) -> None:  # type: ignore[name-defined]
    """Body text for documentation, wrapped for readability."""
    lbl = ttk.Label(
        parent,
        text=text,
        wraplength=480,
        justify="left",
    )
    lbl.pack(anchor="w", pady=(0, 6))


def doc_bullets(parent: ttk.Frame, lines: list[str]) -> None:  # type: ignore[name-defined]
    """Render a simple bullet list in the docs column."""
    if not lines:
        return
    bullet_text = "".join(f"• {line}" for line in lines)
    lbl = ttk.Label(parent, text=bullet_text, justify="left", wraplength=480)
    lbl.pack(anchor="w", pady=(0, 6))


def code_block(parent: ttk.Frame, code: str) -> None:  # type: ignore[name-defined]
    """Render a grey rounded-style code block using a read-only Text widget."""
    outer = tk.Frame(  # type: ignore[name-defined]
        parent,
        bg="#F3F3F5",
        bd=0,
        highlightthickness=1,
        highlightbackground="#D0D0D5",
        padx=6,
        pady=4,
    )
    outer.pack(fill="x", expand=False, pady=(0, 10))

    try:
        code_font = tkFont.Font(family="Consolas", size=9)  # type: ignore[name-defined]
    except Exception:
        code_font = tkFont.nametofont("TkFixedFont")  # type: ignore[name-defined]

    txt = tk.Text(  # type: ignore[name-defined]
        outer,
        height= max(3, code.count("") + 1),
        wrap="none",
        padx=2,
        pady=2,
        bd=0,
        bg="#F3F3F5",
        fg="#222222",
        font=code_font,
    )
    txt.insert("1.0", dedent(code).strip("") + "")
    txt.configure(state="disabled")
    txt.pack(fill="both", expand=True)


def doc_kv(parent: ttk.Frame, items: list[tuple[str, str]]) -> None:  # type: ignore[name-defined]
    """Small key/value grid for things like Module, Function, Category."""
    grid = ttk.Frame(parent)
    grid.pack(anchor="w", pady=(0, 6))

    for row, (key, value) in enumerate(items):
        ttk.Label(grid, text=f"{key}:", font=FONT_NAME_BASE_BOLD).grid(row=row, column=0, sticky="nw", padx=(0, 6))
        ttk.Label(grid, text=value, wraplength=420, justify="left").grid(row=row, column=1, sticky="nw")


# ====================================================================================================
# 4. MAIN DEMO WINDOW (TABBED COMPONENT EXPLORER)
# ----------------------------------------------------------------------------------------------------
class DemoAllPrimitives(BaseGUI):
    """Tabbed explorer for the 00/01 GUI framework primitives.

    Tabs:
        • Styles (G01a)
        • Widget Primitives (G01b)
        • Layout Primitives (G01c)
        • BaseGUI Features (G01d)
    """

    def __init__(self, *args, **kwargs):
        # Force a larger default size for documentation-heavy layout
        kwargs.setdefault("width", 1100)
        kwargs.setdefault("height", 750)
        super().__init__(*args, **kwargs)

    # ------------------------------------------------------------------------------------------------
    def build_widgets(self) -> None:
        # Top-level window heading
        make_heading(self.main_frame, "GUI Boilerplate – 00/01 Component Explorer").pack(
            anchor="w",
            pady=(0, 6),
        )
        make_label(
            self.main_frame,
            "This window documents and demonstrates the core design + base GUI layer.",
        ).pack(anchor="w", pady=(0, 10))

        make_divider(self.main_frame).pack(fill="x", pady=(0, 10))

        nb = ttk.Notebook(self.main_frame)
        nb.pack(fill="both", expand=True)

        tab_styles = ttk.Frame(nb)
        tab_widgets = ttk.Frame(nb)
        tab_layout = ttk.Frame(nb)
        tab_basegui = ttk.Frame(nb)

        nb.add(tab_styles, text="Styles (G01a)")
        nb.add(tab_widgets, text="Widget Primitives (G01b)")
        nb.add(tab_layout, text="Layout Primitives (G01c)")
        nb.add(tab_basegui, text="BaseGUI (G01d)")

        self.build_tab_styles(tab_styles)
        self.build_tab_widgets(tab_widgets)
        self.build_tab_layout(tab_layout)
        self.build_tab_basegui(tab_basegui)

    # =================================================================================================
    # 4.1 TAB: STYLES (G01a)
    # =================================================================================================
    def build_tab_styles(self, parent: ttk.Frame) -> None:  # type: ignore[name-defined]
        left, right = create_two_column_panel(parent)

        # --- Docs column ---------------------------------------------------------------------------
        make_heading(left, "Style Engine Overview (G01a_style_engine)").pack(anchor="w", pady=(0, 4))

        doc_text(
            left,
            "G01a_style_engine centralises all ttk style definitions. It ensures every ttk widget "
            "uses a consistent palette, typography, and padding, driven entirely by G00a_style_config.",
        )

        doc_kv(
            left,
            [
                ("Module", "gui.G01a_style_engine"),
                ("Entry point", "configure_ttk_styles(style: ttk.Style)"),
                ("Depends on", "gui.G00a_style_config (fonts, colours, spacing)"),
            ],
        )

        doc_title(left, "How it is used in the framework")
        doc_bullets(
            left,
            [
                "BaseGUI (G01d) creates a ttk.Style or ttkbootstrap.Style instance.",
                "BaseGUI immediately calls configure_ttk_styles(style).",
                "All widgets (ttk + primitives) then rely on these styles for their visuals.",
            ],
        )

        code_block(
            left,
            """
            from gui.G01a_style_engine import configure_ttk_styles

            style = ttk.Style(root)
            configure_ttk_styles(style)
            """,
        )

        doc_title(left, "Key styles defined")
        doc_bullets(
            left,
            [
                "TLabel / TButton / TEntry / TCombobox",
                "TNotebook / TNotebook.Tab",
                "Treeview / Treeview.Heading",
                "SectionOuter.TFrame / SectionBody.TFrame / SectionHeading.TLabel",
                "WindowHeading.TLabel, ToolbarDivider.TFrame",
            ],
        )

        # ----------------------------------------------------------------------
        # Typography Examples — Shows all four named font levels
        # ----------------------------------------------------------------------
        make_subheading(right, "Typography & Font Levels").pack(anchor="w", pady=(0, 6))

        # 1) Window Heading (largest)
        ttk.Label(
            right,
            text="FONT_NAME_HEADING → WindowHeading.TLabel",
            style="WindowHeading.TLabel",
        ).pack(anchor="w", pady=3)

        # 2) Section Heading (medium-large, bold)
        ttk.Label(
            right,
            text="FONT_NAME_SECTION_HEADING → SectionHeading.TLabel",
            style="SectionHeading.TLabel",
        ).pack(anchor="w", pady=3)

        # 3) Base Bold text (body size, weight=bold)
        ttk.Label(
            right,
            text="FONT_NAME_BASE_BOLD → Bold.TLabel",
            style="Bold.TLabel",
        ).pack(anchor="w", pady=3)

        # 4) Base text (standard body text)
        ttk.Label(
            right,
            text="FONT_NAME_BASE → TLabel",
            style="TLabel",
        ).pack(anchor="w", pady=3)

        make_divider(right).pack(fill="x", pady=10)

        make_subheading(right, "Buttons, Entry, Combobox, Progressbar").pack(anchor="w", pady=(0, 6))
        ttk.Button(right, text="TButton sample").pack(anchor="w", pady=2)
        ttk.Entry(right).pack(anchor="w", pady=2)
        cb = ttk.Combobox(right, state="readonly", values=["Alpha", "Beta", "Gamma"])
        cb.current(0)
        cb.pack(anchor="w", pady=2)

        pb = ttk.Progressbar(right, mode="determinate", length=220)
        pb["value"] = 55
        pb.pack(anchor="w", pady=6)

        make_divider(right).pack(fill="x", pady=10)

        make_subheading(right, "Notebook + Tabs").pack(anchor="w", pady=(0, 6))
        small_nb = ttk.Notebook(right)
        small_nb.pack(fill="both", expand=True)
        for name in ("Tab One", "Tab Two"):
            frame = ttk.Frame(small_nb)
            small_nb.add(frame, text=name)
            ttk.Label(frame, text=f"Content for {name}").pack(anchor="w", padx=8, pady=8)

    # =================================================================================================
    # 4.2 TAB: WIDGET PRIMITIVES (G01b)
    # =================================================================================================
    def build_tab_widgets(self, parent: ttk.Frame) -> None:  # type: ignore[name-defined]
        left, right = create_two_column_panel(parent)

        # --- Docs column: overview -----------------------------------------------------------------
        make_heading(left, "Widget Primitives Overview (G01b)").pack(anchor="w", pady=(0, 4))
        doc_text(
            left,
            "G01b_widget_primitives provides small, focused factory functions that create individual "
            "widgets (labels, buttons, entries, comboboxes, status labels, etc.) with consistent "
            "defaults and attached geometry metadata.",
        )

        doc_kv(
            left,
            [
                ("Module", "gui.G01b_widget_primitives"),
                ("Pattern", "make_foo(parent, **kwargs) → widget"),
                ("Geometry", "Each widget gets widget.geometry_kwargs with padx/pady/ipadx/ipady."),
            ],
        )

        doc_title(left, "Example: make_heading")
        doc_text(
            left,
            "Creates a primary heading label using the theme heading font and colours. Use this for "
            "window titles and major section headings.",
        )
        code_block(
            left,
            """
            from gui.G01b_widget_primitives import make_heading

            make_heading(self.main_frame, "Connection Settings").pack(anchor="w", pady=(0, 8))
            """,
        )

        doc_title(left, "Example: make_entry + make_combobox")
        doc_text(
            left,
            "Entry widgets deliberately avoid unsupported fg/bg keyword args and rely purely on the "
            "ttk style engine for their appearance.",
        )
        code_block(
            left,
            """
            from gui.G01b_widget_primitives import make_label, make_entry, make_combobox

            make_label(parent, "Username:").pack(anchor="w")
            make_entry(parent, width=32).pack(anchor="w", pady=(0, 6))

            make_label(parent, "Environment:").pack(anchor="w")
            make_combobox(
                parent,
                values=["DEV", "UAT", "PROD"],
                state="readonly",
                width=30,
            ).pack(anchor="w", pady=(0, 6))
            """,
        )

        doc_title(left, "Status labels, checkboxes, radios, switches")
        doc_bullets(
            left,
            [
                "make_status_label(parent, text, status='info'|'success'|'warning'|'error')",
                "make_checkbox(parent, text, variable, command=None, bootstyle='primary')",
                "make_radio(parent, text, variable, value, command=None)",
                "make_switch(parent, text, variable, command=None) — modern on/off toggle.",
            ],
        )

        # --- Live examples column ------------------------------------------------------------------
        make_subheading(right, "Text primitives").pack(anchor="w", pady=(0, 6))
        make_heading(right, "make_heading – Primary heading").pack(anchor="w", pady=2)
        make_subheading(right, "make_subheading – Subheading").pack(anchor="w", pady=2)
        make_label(right, "make_label – Standard body label").pack(anchor="w", pady=2)
        make_status_label(right, "Status: info (make_status_label)", status="info").pack(anchor="w", pady=2)
        make_status_label(right, "Status: success", status="success").pack(anchor="w", pady=2)
        make_status_label(right, "Status: warning", status="warning").pack(anchor="w", pady=2)
        make_status_label(right, "Status: error", status="error").pack(anchor="w", pady=2)

        make_divider(right).pack(fill="x", pady=10)

        make_subheading(right, "Inputs").pack(anchor="w", pady=(0, 6))
        make_label(right, "Entry:").pack(anchor="w")
        make_entry(right, width=30).pack(anchor="w", pady=(0, 4))

        make_label(right, "Combobox:").pack(anchor="w")
        make_combobox(right, values=["Option A", "Option B", "Option C"], state="readonly", width=28).pack(
            anchor="w", pady=(0, 4)
        )

        make_label(right, "Textarea (with per-widget scroll bound):").pack(anchor="w", pady=(6, 2))
        txt = make_textarea(right, height=6)
        txt.pack(fill="both", expand=True)
        for i in range(15):
            txt.insert("end", f"Log line {i+1}")
        self.bind_scroll_widget(txt)

        make_divider(right).pack(fill="x", pady=10)

        make_subheading(right, "Choice controls").pack(anchor="w", pady=(0, 6))
        chk_var = tk.BooleanVar(value=True)  # type: ignore[name-defined]
        make_checkbox(right, "Enable feature X", variable=chk_var).pack(anchor="w", pady=2)

        radio_var = tk.StringVar(value="A")  # type: ignore[name-defined]
        make_radio(right, "Radio A", variable=radio_var, value="A").pack(anchor="w", pady=1)
        make_radio(right, "Radio B", variable=radio_var, value="B").pack(anchor="w", pady=1)

        switch_var = tk.BooleanVar(value=False)  # type: ignore[name-defined]
        make_switch(right, "Use experimental mode", variable=switch_var).pack(anchor="w", pady=(6, 2))

    # =================================================================================================
    # 4.3 TAB: LAYOUT PRIMITIVES (G01c)
    # =================================================================================================
    def build_tab_layout(self, parent: ttk.Frame) -> None:  # type: ignore[name-defined]
        left, right = create_two_column_panel(parent)

        # --- Docs column ---------------------------------------------------------------------------
        make_heading(left, "Layout Primitives Overview (G01c)").pack(anchor="w", pady=(0, 4))
        doc_text(
            left,
            "G01c_layout_primitives provides lightweight helpers for headings, body text, dividers, "
            "and spacers that sit directly on ttk widgets. They do not depend on ttkbootstrap and "
            "are safe to use in any ttk-only context.",
        )

        doc_kv(
            left,
            [
                ("Module", "gui.G01c_layout_primitives"),
                ("Key functions", "heading, subheading, body_text, divider, spacer"),
                ("Intended use", "Quick layout/typography in simple windows without full primitives"),
            ],
        )

        doc_title(left, "heading(parent, text, style='SectionHeading.TLabel')")
        doc_text(
            left,
            "Creates a primary section heading label. Unlike make_heading, this works directly with "
            "ttk.Label and assumes styles provided by G01a.",
        )
        code_block(
            left,
            """
            from gui.G01c_layout_primitives import heading

            heading(container, "Data Source Settings").pack(anchor="w", pady=(0, 8))
            """,
        )

        doc_title(left, "divider(parent) and spacer(parent, height=...) ")
        doc_text(
            left,
            "divider() wraps ttk.Separator and spacer() creates a fixed-height empty frame. Both are "
            "used to introduce breathing room and visual separation without magic numbers inside "
            "pack/grid calls.",
        )
        code_block(
            left,
            """
            from gui.G01c_layout_primitives import divider, spacer

            divider(container).pack(fill="x", pady=(8, 8))
            spacer(container, height=16).pack(fill="x")
            """,
        )

        # --- Live examples column ------------------------------------------------------------------
        lp_heading(right, "heading() example").pack(anchor="w", pady=(0, 4))
        lp_subheading(right, "subheading() example").pack(anchor="w", pady=(0, 6))

        lp_body_text(
            right,
            "This is lp_body_text() – a simple helper around ttk.Label with optional wrapping. "
            "Use it for explanatory text blocks and inline documentation.",
            wraplength=520,
        ).pack(anchor="w", pady=(0, 10))

        lp_divider(right).pack(fill="x", pady=(4, 8))
        lp_body_text(right, "Spacer below (height=16)...").pack(anchor="w", pady=(0, 4))
        lp_spacer(right, height=16).pack(fill="x")
        lp_body_text(right, "End of layout primitive demo.").pack(anchor="w", pady=(8, 0))

    # =================================================================================================
    # 4.4 TAB: BASE GUI (G01d)
    # =================================================================================================
    def build_tab_basegui(self, parent: ttk.Frame) -> None:  # type: ignore[name-defined]
        left, right = create_two_column_panel(parent)

        # --- Docs column ---------------------------------------------------------------------------
        make_heading(left, "BaseGUI Overview (G01d_gui_base)").pack(anchor="w", pady=(0, 4))
        doc_text(
            left,
            "BaseGUI is the standard root window class for all GUIs in this framework. It sets up "
            "the Tk window, applies the style engine, and exposes a scrollable main_frame for "
            "content. It also provides helpers for fullscreen, centering, and scroll binding.",
        )

        doc_kv(
            left,
            [
                ("Module", "gui.G01d_gui_base"),
                ("Class", "BaseGUI(tk.Tk)"),
                ("Key attribute", "self.main_frame → scrollable content area"),
            ],
        )

        doc_title(left, "Typical usage pattern")
        code_block(
            left,
            """
            from gui.G01d_gui_base import BaseGUI
            from gui.G01b_widget_primitives import make_heading

            class MyWindow(BaseGUI):

                def build_widgets(self):
                    make_heading(self.main_frame, "My first window").pack(anchor="w", pady=(0, 10))

            if __name__ == "__main__":
                app = MyWindow(title="Demo")
                app.mainloop()
            """,
        )

        doc_title(left, "Scroll behaviour")
        doc_bullets(
            left,
            [
                "The whole window scrolls vertically when content exceeds the viewport.",
                "Use BaseGUI.bind_scroll_widget(widget) for widgets with their own yview (Text, Listbox, Treeview).",
                "When the cursor is over such a widget, its own content scrolls instead of the main window.",
            ],
        )

        # --- Live examples column ------------------------------------------------------------------
        make_subheading(right, "Scrollable content demo").pack(anchor="w", pady=(0, 6))
        make_label(right, "Scroll this tab using the mouse wheel or trackpad.").pack(anchor="w", pady=(0, 4))

        make_divider(right).pack(fill="x", pady=(4, 8))

        for i in range(25):
            make_label(right, f"Main-frame content line {i+1}").pack(anchor="w", pady=1)

        make_divider(right).pack(fill="x", pady=(8, 8))

        make_label(right, "Text console with its own scroll binding:").pack(anchor="w", pady=(0, 4))
        console = make_textarea(right, height=8)
        console.pack(fill="both", expand=True, pady=(0, 6))
        for i in range(40):
            console.insert("end", f"Console log line {i+1}")
        self.bind_scroll_widget(console)

        make_label(
            right,
            "Hover over the console and scroll → only the console moves. Hover above it → the whole tab scrolls.",
        ).pack(anchor="w", pady=(4, 0))


# ====================================================================================================
# 5. MAIN ENTRY POINT
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure ttk styles are fully configured (BaseGUI will also do this in its init flow).
    app = DemoAllPrimitives(title="GUI Boilerplate – 00/01 Component Explorer")
    app.mainloop()

