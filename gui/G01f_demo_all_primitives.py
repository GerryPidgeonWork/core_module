# ====================================================================================================
# G01f_demo_all_primitives.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Developer-facing "component explorer" for the GUI Boilerplate framework.
#   Demonstrates and documents the core G01 layer:
#       • G01a_style_config       — Theme tokens (fonts/colours/spacing)
#       • G01b_style_engine       — ttk style engine
#       • G01c_widget_primitives  — Low-level widget factories
#       • G01d_layout_primitives  — Layout/typography helpers
#       • G01e_gui_base           — BaseGUI scrollable window shell
#
#   The window is structured as a tabbed, two-column documentation view:
#       Left  column → Developer documentation (what/when/how, usage, notes).
#       Right column → Live examples using the real framework primitives.
#
# Usage:
#   python gui/G01f_demo_all_primitives.py
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
    make_label,
    make_entry,
    make_textarea,
    make_combobox,
    make_checkbox,
    make_radio,
    make_switch,
    make_divider,
    make_spacer,
    make_button,
)
from gui.G01d_layout_primitives import (
    heading as lp_heading,
    subheading as lp_subheading,
    body_text as lp_body_text,
    divider as lp_divider,
    spacer as lp_spacer,
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
    make_label(parent, text, category="Body", surface="Primary", weight="Bold").pack(
        anchor="w", pady=(SECTION_TITLE_SPACING, 4)
    )


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
    bullet_text = "".join(f"• {line}\n" for line in lines)
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
        height=max(3, code.count("\n") + 1),
        wrap="none",
        padx=2,
        pady=2,
        bd=0,
        bg="#F3F3F5",
        fg="#222222",
        font=code_font,
    )
    txt.insert("1.0", dedent(code).strip() + "\n")  # type: ignore[name-defined]
    txt.configure(state="disabled")
    txt.pack(fill="both", expand=True)


def doc_kv(parent: ttk.Frame, items: list[tuple[str, str]]) -> None:  # type: ignore[name-defined]
    """Small key/value grid for things like Module, Function, Category."""
    grid = ttk.Frame(parent)
    grid.pack(anchor="w", pady=(0, 6))

    for row, (key, value) in enumerate(items):
        ttk.Label(grid, text=f"{key}:", font=FONT_NAME_BASE_BOLD).grid(  # type: ignore[arg-type]
            row=row,
            column=0,
            sticky="nw",
            padx=(0, 6),
        )
        ttk.Label(grid, text=value, wraplength=420, justify="left").grid(
            row=row,
            column=1,
            sticky="nw",
        )


# ====================================================================================================
# 4. MAIN DEMO WINDOW (TABBED COMPONENT EXPLORER)
# ----------------------------------------------------------------------------------------------------
class DemoAllPrimitives(BaseGUI):
    """Tabbed explorer for the 00/01 GUI framework primitives.

    Tabs:
        • Styles (G01b)
        • Widget Primitives (G01c)
        • Layout Primitives (G01d)
        • BaseGUI Features (G01e)
        • Dashboard Showcase (connection-launcher style demo)
    """

    def __init__(self, *args, **kwargs):
        # Force a larger default size for documentation-heavy layout
        kwargs.setdefault("width", 1100)
        kwargs.setdefault("height", 750)
        super().__init__(*args, **kwargs)

    # ------------------------------------------------------------------------------------------------
    def build_widgets(self) -> None:
        # Top-level window heading
        make_label(
            self.main_frame,
            "GUI Boilerplate – G01 Component Explorer",
            category="WindowHeading",
            surface="Primary",
            weight="Bold",
        ).pack(anchor="w", pady=(0, 6))

        make_label(
            self.main_frame,
            "This window documents and demonstrates the core design + base GUI layer.",
            category="Body",
            surface="Primary",
            weight="Normal",
        ).pack(anchor="w", pady=(0, 10))

        make_divider(self.main_frame).pack(fill="x", pady=(0, 10))

        nb = ttk.Notebook(self.main_frame)
        nb.pack(fill="both", expand=True)

        tab_styles = ttk.Frame(nb)
        tab_widgets = ttk.Frame(nb)
        tab_layout = ttk.Frame(nb)
        tab_basegui = ttk.Frame(nb)
        tab_dashboard = ttk.Frame(nb)

        nb.add(tab_styles, text="Styles (G01b)")
        nb.add(tab_widgets, text="Widget Primitives (G01c)")
        nb.add(tab_layout, text="Layout Primitives (G01d)")
        nb.add(tab_basegui, text="BaseGUI (G01e)")
        nb.add(tab_dashboard, text="Dashboard Demo")

        self.build_tab_styles(tab_styles)
        self.build_tab_widgets(tab_widgets)
        self.build_tab_layout(tab_layout)
        self.build_tab_basegui(tab_basegui)
        self.build_tab_dashboard(tab_dashboard)

    # =================================================================================================
    # 4.1 TAB: STYLES (G01b)
    # =================================================================================================
    def build_tab_styles(self, parent: ttk.Frame) -> None:  # type: ignore[name-defined]
        left, right = create_two_column_panel(parent)

        # --- Docs column ---------------------------------------------------------------------------
        make_label(
            left,
            "Style Engine Overview (G01b_style_engine)",
            category="SectionHeading",
            surface="Primary",
            weight="Bold",
        ).pack(anchor="w", pady=(0, 4))

        doc_text(
            left,
            "G01b_style_engine centralises all ttk style definitions. It ensures every ttk widget "
            "uses a consistent palette, typography, and spacing, driven entirely by G01a_style_config.",
        )

        doc_kv(
            left,
            [
                ("Module", "gui.G01b_style_engine"),
                ("Entry point", "configure_ttk_styles(style: ttk.Style)"),
                ("Depends on", "gui.G01a_style_config (fonts, colours, spacing)"),
            ],
        )

        doc_title(left, "How the style engine integrates")
        doc_bullets(
            left,
            [
                "BaseGUI creates a ttk or ttkbootstrap Style instance.",
                "Immediately calls configure_ttk_styles(style).",
                "All G01 primitives use the theme automatically.",
            ],
        )

        code_block(
            left,
            """
            from gui.G01b_style_engine import configure_ttk_styles

            style = ttk.Style(root)
            configure_ttk_styles(style)
            """,
        )

        doc_title(left, "Key styles (using surface/category/weight naming)")
        doc_bullets(
            left,
            [
                "Primary.WindowHeading.Bold.TLabel",
                "Primary.SectionHeading.Bold.TLabel / Secondary.SectionHeading.Bold.TLabel",
                "Primary.Normal.TLabel / Primary.Bold.TLabel",
                "Secondary.Normal.TLabel / Secondary.Bold.TLabel",
                "TButton / Primary.TButton / Secondary.TButton / Success.TButton / Warning.TButton / Danger.TButton",
                "TEntry / TCombobox / Vertical.TScrollbar",
                "TFrame / SectionOuter.TFrame / SectionBody.TFrame / Card.TFrame",
            ],
        )

        # ----------------------------------------------------------------------
        # Typography Examples — Shows all four named font levels
        # ----------------------------------------------------------------------
        make_label(right, "Typography Samples", category="Body", surface="Primary", weight="Bold").pack(
            anchor="w", pady=(0, 6)
        )

        ttk.Label(
            right,
            text="Window Heading (Primary.WindowHeading.Bold.TLabel)",
            style="Primary.WindowHeading.Bold.TLabel",
        ).pack(anchor="w", pady=2)

        ttk.Label(
            right,
            text="Section Heading (Primary.SectionHeading.Bold.TLabel)",
            style="Primary.SectionHeading.Bold.TLabel",
        ).pack(anchor="w", pady=2)

        ttk.Label(
            right,
            text="Bold Text (Primary.Bold.TLabel)",
            style="Primary.Bold.TLabel",
        ).pack(anchor="w", pady=2)

        ttk.Label(
            right,
            text="Normal Text (Primary.Normal.TLabel)",
            style="Primary.Normal.TLabel",
        ).pack(anchor="w", pady=2)

        make_divider(right).pack(fill="x", pady=10)

        # ------------------------------
        # Inputs & Controls (aligned grid)
        # ------------------------------
        make_label(right, "Inputs & Controls", category="Body", surface="Primary", weight="Bold").pack(
            anchor="w", pady=(0, 6)
        )

        controls = ttk.Frame(right)
        controls.pack(fill="x", expand=False)

        # Two columns: label / widget
        controls.columnconfigure(0, weight=0)
        controls.columnconfigure(1, weight=1)

        current_row = 0

        def add_control_row(label_text: str, widget: ttk.Widget) -> None:
            """Add a single aligned row to the Inputs & Controls grid."""
            nonlocal current_row
            ttk.Label(
                controls,
                text=label_text,
                style="TLabel",
            ).grid(
                row=current_row,
                column=0,
                sticky="w",
                padx=(0, 12),
                pady=3,
            )
            widget.grid(
                row=current_row,
                column=1,
                sticky="w",
                pady=3,
            )
            current_row += 1


        # Neutral button
        add_control_row("TButton (neutral base):", ttk.Button(controls, text="TButton"))

        # Semantic buttons
        add_control_row("Primary.TButton:", ttk.Button(controls, text="Primary", style="Primary.TButton"))
        add_control_row("Secondary.TButton:", ttk.Button(controls, text="Secondary", style="Secondary.TButton"))
        add_control_row("Success.TButton:", ttk.Button(controls, text="Success", style="Success.TButton"))
        add_control_row("Warning.TButton:", ttk.Button(controls, text="Warning", style="Warning.TButton"))
        add_control_row("Danger.TButton:", ttk.Button(controls, text="Danger", style="Danger.TButton"))

        # Entry
        add_control_row("Entry:", ttk.Entry(controls, width=24))

        # Combobox
        combo = ttk.Combobox(controls, state="readonly", values=["Alpha", "Beta", "Gamma"])
        combo.current(0)
        add_control_row("Combobox:", combo)

        # Progressbar
        progress = ttk.Progressbar(controls, mode="determinate", length=180)
        progress["value"] = 55
        add_control_row("Progressbar:", progress)

        # Notebook example
        notebook_example = ttk.Notebook(controls)
        for name in ("Tab One", "Tab Two"):
            frame = ttk.Frame(notebook_example)
            notebook_example.add(frame, text=name)
            ttk.Label(frame, text=f"Content for {name}").pack(anchor="w", padx=6, pady=6)

        add_control_row("Notebook Example:", notebook_example)


    # =================================================================================================
    # 4.2 TAB: WIDGET PRIMITIVES (G01c)
    # =================================================================================================
    def build_tab_widgets(self, parent: ttk.Frame) -> None:  # type: ignore[name-defined]
        left, right = create_two_column_panel(parent)

        # --- Docs column: overview -----------------------------------------------------------------
        make_label(
            left,
            "Widget Primitives Overview (G01c)",
            category="SectionHeading",
            surface="Primary",
            weight="Bold",
        ).pack(anchor="w", pady=(0, 4))

        doc_text(
            left,
            "G01c_widget_primitives provides a unified make_label() function and specialized widget "
            "factories (buttons, entries, comboboxes, etc.) with consistent defaults and attached "
            "geometry metadata.",
        )

        doc_kv(
            left,
            [
                ("Module", "gui.G01c_widget_primitives"),
                ("Pattern", "make_label(parent, text, category, surface, weight) → widget"),
                ("Geometry", "Each widget gets widget.geometry_kwargs with padx/pady/ipadx/ipady."),
            ],
        )

        doc_title(left, "Unified make_label() signature")
        doc_text(
            left,
            "All labels are created via make_label() with category, surface, and weight parameters. "
            "This ensures style names always match G01b's matrix.",
        )
        code_block(
            left,
            """
            from gui.G01c_widget_primitives import make_label

            # Window heading
            make_label(parent, "Title", category="WindowHeading", surface="Primary", weight="Bold")

            # Section heading
            make_label(parent, "Section", category="SectionHeading", surface="Primary", weight="Bold")

            # Body text
            make_label(parent, "Hello", category="Body", surface="Primary", weight="Normal")

            # Status labels
            make_label(parent, "OK", category="Success", surface="Primary", weight="Normal")
            make_label(parent, "Warning", category="Warning", surface="Primary", weight="Normal")
            make_label(parent, "Error", category="Error", surface="Primary", weight="Normal")
            """,
        )

        doc_title(left, "Categories available")
        doc_bullets(
            left,
            [
                "Body — standard text (Normal or Bold)",
                "Heading — page-level headings",
                "SectionHeading — section titles",
                "WindowHeading — top-of-window titles",
                "Card — text inside Card.TFrame",
                "Success / Warning / Error — status labels",
            ],
        )

        # --- Live examples column ------------------------------------------------------------------
        make_label(right, "Text primitives", category="Body", surface="Primary", weight="Bold").pack(
            anchor="w", pady=(0, 6)
        )

        make_label(right, "WindowHeading", category="WindowHeading", surface="Primary", weight="Bold").pack(
            anchor="w", pady=2
        )
        make_label(right, "SectionHeading", category="SectionHeading", surface="Primary", weight="Bold").pack(
            anchor="w", pady=2
        )
        make_label(right, "Body Normal", category="Body", surface="Primary", weight="Normal").pack(
            anchor="w", pady=2
        )
        make_label(right, "Body Bold", category="Body", surface="Primary", weight="Bold").pack(
            anchor="w", pady=2
        )
        make_label(right, "Success status", category="Success", surface="Primary", weight="Normal").pack(
            anchor="w", pady=2
        )
        make_label(right, "Warning status", category="Warning", surface="Primary", weight="Normal").pack(
            anchor="w", pady=2
        )
        make_label(right, "Error status", category="Error", surface="Primary", weight="Normal").pack(
            anchor="w", pady=2
        )

        make_divider(right).pack(fill="x", pady=10)

        make_label(right, "Inputs", category="Body", surface="Primary", weight="Bold").pack(
            anchor="w", pady=(0, 6)
        )
        make_label(right, "Entry:", category="Body", surface="Primary", weight="Normal").pack(anchor="w")
        make_entry(right, width=30).pack(anchor="w", pady=(0, 4))

        make_label(right, "Combobox:", category="Body", surface="Primary", weight="Normal").pack(anchor="w")
        make_combobox(
            right,
            values=["Option A", "Option B", "Option C"],
            state="readonly",
            width=28,
        ).pack(anchor="w", pady=(0, 4))

        make_label(right, "Textarea (with per-widget scroll bound):", category="Body", surface="Primary", weight="Normal").pack(
            anchor="w", pady=(6, 2)
        )
        txt = make_textarea(right, height=6)
        txt.pack(fill="both", expand=True)
        for i in range(15):
            txt.insert("end", f"Log line {i + 1}\n")
        self.bind_scroll_widget(txt)

        make_divider(right).pack(fill="x", pady=10)

        make_label(right, "Choice controls", category="Body", surface="Primary", weight="Bold").pack(
            anchor="w", pady=(0, 6)
        )
        chk_var = tk.BooleanVar(value=True)  # type: ignore[name-defined]
        make_checkbox(right, "Enable feature X", variable=chk_var).pack(anchor="w", pady=2)

        radio_var = tk.StringVar(value="A")  # type: ignore[name-defined]
        make_radio(right, "Radio A", variable=radio_var, value="A").pack(anchor="w", pady=1)
        make_radio(right, "Radio B", variable=radio_var, value="B").pack(anchor="w", pady=1)

        switch_var = tk.BooleanVar(value=False)  # type: ignore[name-defined]
        make_switch(right, "Use experimental mode", variable=switch_var).pack(anchor="w", pady=(6, 2))

    # =================================================================================================
    # 4.3 TAB: LAYOUT PRIMITIVES (G01d)
    # =================================================================================================
    def build_tab_layout(self, parent: ttk.Frame) -> None:  # type: ignore[name-defined]
        left, right = create_two_column_panel(parent)

        # --- Docs column ---------------------------------------------------------------------------
        make_label(
            left,
            "Layout Primitives Overview (G01d)",
            category="SectionHeading",
            surface="Primary",
            weight="Bold",
        ).pack(anchor="w", pady=(0, 4))

        doc_text(
            left,
            "G01d_layout_primitives wraps G01c functions and adds layout-specific metadata "
            "(g01d_padding, g01d_anchor). These are thin wrappers for headings, body text, "
            "dividers, and spacers used in page layout.",
        )

        doc_kv(
            left,
            [
                ("Module", "gui.G01d_layout_primitives"),
                ("Key functions", "heading, subheading, body_text, divider, spacer"),
                ("Wraps", "G01c.make_label, G01c.make_divider, G01c.make_spacer"),
            ],
        )

        doc_title(left, "heading(parent, text, surface='Primary', weight='Bold')")
        doc_text(
            left,
            "Creates a section heading label. Wraps make_label() with category='SectionHeading' "
            "and attaches g01d_padding/g01d_anchor metadata for layout helpers.",
        )
        code_block(
            left,
            """
            from gui.G01d_layout_primitives import heading

            heading(container, "Data Source Settings", surface="Primary").pack(anchor="w")
            heading(container, "Card Title", surface="Secondary").pack(anchor="w")
            """,
        )

        doc_title(left, "divider(parent) and spacer(parent, height=...)")
        doc_text(
            left,
            "divider() wraps G01c.make_divider() and spacer() wraps G01c.make_spacer(). Both are "
            "used to introduce breathing room and visual separation.",
        )
        code_block(
            left,
            """
            from gui.G01d_layout_primitives import divider, spacer

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
    # 4.4 TAB: BASE GUI (G01e)
    # =================================================================================================
    def build_tab_basegui(self, parent: ttk.Frame) -> None:  # type: ignore[name-defined]
        left, right = create_two_column_panel(parent)

        # --- Docs column ---------------------------------------------------------------------------
        make_label(
            left,
            "BaseGUI Overview (G01e_gui_base)",
            category="SectionHeading",
            surface="Primary",
            weight="Bold",
        ).pack(anchor="w", pady=(0, 4))

        doc_text(
            left,
            "BaseGUI is the standard root window class for all GUIs in this framework. It sets up "
            "the Tk window, applies the style engine, and exposes a scrollable main_frame for "
            "content. It also provides helpers for fullscreen, centering, and scroll binding.",
        )

        doc_kv(
            left,
            [
                ("Module", "gui.G01e_gui_base"),
                ("Class", "BaseGUI(tk.Tk)"),
                ("Key attribute", "self.main_frame → scrollable content area"),
            ],
        )

        doc_title(left, "Typical usage pattern")
        code_block(
            left,
            """
            from gui.G01e_gui_base import BaseGUI
            from gui.G01c_widget_primitives import make_label

            class MyWindow(BaseGUI):

                def build_widgets(self):
                    make_label(
                        self.main_frame,
                        "My first window",
                        category="WindowHeading",
                        surface="Primary",
                        weight="Bold",
                    ).pack(anchor="w", pady=(0, 10))

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
        make_label(right, "Scrollable content demo", category="Body", surface="Primary", weight="Bold").pack(
            anchor="w", pady=(0, 6)
        )
        make_label(right, "Scroll this tab using the mouse wheel or trackpad.", category="Body", surface="Primary", weight="Normal").pack(
            anchor="w", pady=(0, 4)
        )

        make_divider(right).pack(fill="x", pady=(4, 8))

        for i in range(25):
            make_label(right, f"Main-frame content line {i + 1}", category="Body", surface="Primary", weight="Normal").pack(
                anchor="w", pady=1
            )

        make_divider(right).pack(fill="x", pady=(8, 8))

        make_label(right, "Text console with its own scroll binding:", category="Body", surface="Primary", weight="Normal").pack(
            anchor="w", pady=(0, 4)
        )
        console = make_textarea(right, height=8)
        console.pack(fill="both", expand=True, pady=(0, 6))
        for i in range(40):
            console.insert("end", f"Console log line {i + 1}\n")
        self.bind_scroll_widget(console)

        make_label(
            right,
            "Hover over the console and scroll → only the console moves. Hover above it → the whole tab scrolls.",
            category="Body",
            surface="Primary",
            weight="Normal",
        ).pack(anchor="w", pady=(4, 0))

    # =================================================================================================
    # 4.5 TAB: DASHBOARD SHOWCASE (CONNECTION LAUNCHER STYLE)
    # =================================================================================================
    def build_tab_dashboard(self, parent: ttk.Frame) -> None:  # type: ignore[name-defined]
        """
        Full-page demo that looks like a small "Connection Launcher" dashboard.

        This tab intentionally combines:
            • BaseGUI main_frame + scroll behaviour.
            • G01b section/card styles (SectionOuter/SectionBody/Card).
            • G01c widget primitives (make_label, inputs, switches).
            • G01d layout helpers (divider/spacer) where appropriate.
        """
        left, right = create_two_column_panel(parent)

        # --------------------------------------------------------------------------------------------
        # Docs column – explain the layout and how it maps to primitives
        # --------------------------------------------------------------------------------------------
        make_label(
            left,
            "Dashboard Demo – Connection Launcher",
            category="SectionHeading",
            surface="Primary",
            weight="Bold",
        ).pack(anchor="w", pady=(0, 4))

        doc_text(
            left,
            "This tab shows how the G01 primitives can be composed into a realistic 'Connection "
            "Launcher' style dashboard. It is not tied to any specific project; it simply "
            "demonstrates a production-like layout.",
        )

        doc_kv(
            left,
            [
                ("Pattern", "Header + toolbar + 2-column responsive cards"),
                ("Key styles", "SectionOuter.TFrame, SectionBody.TFrame, Card.TFrame"),
                ("Key primitives", "make_label with various categories, make_entry, make_combobox, make_switch"),
            ],
        )

        doc_title(left, "Layout structure")
        doc_bullets(
            left,
            [
                "Top window heading + short description.",
                "Toolbar row with primary / secondary actions.",
                "Outer section frame containing a grid of cards (Overview, Configuration, Accounting, Data).",
                "Bottom status strip with a semantic status label.",
            ],
        )

        code_block(
            left,
            """
            # High level pattern

            make_heading(main_frame, "Connection Launcher").pack(anchor="w")
            toolbar = ttk.Frame(main_frame); toolbar.pack(fill="x")

            # Cards area
            outer = ttk.Frame(main_frame, style="SectionOuter.TFrame")
            body = ttk.Frame(outer, style="SectionBody.TFrame")
            body.grid_columnconfigure((0, 1), weight=1)

            overview_card  = ttk.Frame(body, style="Card.TFrame")
            config_card    = ttk.Frame(body, style="Card.TFrame")
            period_card    = ttk.Frame(body, style="Card.TFrame")
            warehouse_card = ttk.Frame(body, style="Card.TFrame")
            """,
        )

        # --------------------------------------------------------------------------------------------
        # Live dashboard column – visual connection launcher demo
        # --------------------------------------------------------------------------------------------
        # Header
        make_label(
            right,
            "Connection Launcher",
            category="WindowHeading",
            surface="Primary",
            weight="Bold",
        ).pack(anchor="w", pady=(0, 4))

        make_label(
            right,
            "Configure your data source, accounting period, and warehouse destination, then launch "
            "a connection run using the toolbar actions.",
            category="Body",
            surface="Primary",
            weight="Normal",
        ).pack(anchor="w", pady=(0, 8))

        lp_divider(right).pack(fill="x", pady=(4, 8))

        # Toolbar row
        toolbar = ttk.Frame(right)
        toolbar.pack(fill="x", pady=(0, 8))

        ttk.Button(toolbar, text="Run connection", style="Primary.TButton").pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Open logs", style="Secondary.TButton").pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Dry-run", style="Secondary.TButton").pack(side="left", padx=(0, 6))

        toolbar_spacer = ttk.Frame(toolbar)
        toolbar_spacer.pack(side="left", expand=True, fill="x")

        make_label(toolbar, "Ready to run", category="Success", surface="Primary", weight="Normal").pack(side="right")

        lp_divider(right).pack(fill="x", pady=(8, 8))

        # Outer section + body (uses SectionOuter / SectionBody styles)
        outer = ttk.Frame(right, style="SectionOuter.TFrame")
        outer.pack(fill="both", expand=True)

        body = ttk.Frame(outer, style="SectionBody.TFrame")
        body.pack(fill="both", expand=True)

        # Card grid configuration
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        # Helper to build a card with title + body text
        def make_card(parent_frame: ttk.Frame, title: str) -> ttk.Frame:  # type: ignore[name-defined]
            card = ttk.Frame(parent_frame, style="Card.TFrame")
            card.grid_propagate(True)

            make_label(
                card,
                title,
                category="SectionHeading",
                surface="Secondary",
                weight="Bold",
            ).pack(anchor="w", padx=8, pady=(8, 4))

            return card

        # --- Row 1: Overview + Configuration ------------------------------------------------------
        overview_card = make_card(body, "Overview")
        overview_card.grid(row=0, column=0, sticky="nsew", padx=(0, FRAME_PADDING), pady=(0, FRAME_PADDING))

        make_label(
            overview_card,
            "Quick snapshot of the current connection preset. This is static demo content; "
            "in a real app you would bind actual values here.",
            category="Body",
            surface="Secondary",
            weight="Normal",
        ).pack(anchor="w", padx=8, pady=(0, 6))

        lp_spacer(overview_card, height=6).pack(fill="x")

        make_label(overview_card, "Last run: 2025-11-22 14:32", category="Body", surface="Secondary", weight="Normal").pack(
            anchor="w", padx=8
        )
        make_label(overview_card, "Status:", category="Body", surface="Secondary", weight="Normal").pack(
            anchor="w", padx=8, pady=(4, 0)
        )
        make_label(overview_card, "All systems operational", category="Success", surface="Secondary", weight="Normal").pack(
            anchor="w", padx=8, pady=(0, 8)
        )

        config_card = make_card(body, "Configuration")
        config_card.grid(row=0, column=1, sticky="nsew", padx=(FRAME_PADDING, 0), pady=(0, FRAME_PADDING))

        make_label(config_card, "Connection name:", category="Body", surface="Secondary", weight="Normal").pack(
            anchor="w", padx=8
        )
        make_entry(config_card, width=28).pack(anchor="w", padx=8, pady=(0, 4))

        make_label(config_card, "Source system:", category="Body", surface="Secondary", weight="Normal").pack(
            anchor="w", padx=8
        )
        make_combobox(
            config_card,
            values=["Braintree", "Stripe", "Revolut", "Custom CSV"],
            state="readonly",
            width=26,
        ).pack(anchor="w", padx=8, pady=(0, 4))

        make_label(config_card, "Environment:", category="Body", surface="Secondary", weight="Normal").pack(
            anchor="w", padx=8
        )
        make_combobox(
            config_card,
            values=["DEV", "UAT", "PROD"],
            state="readonly",
            width=18,
        ).pack(anchor="w", padx=8, pady=(0, 4))

        lp_spacer(config_card, height=4).pack(fill="x")
        switch_var = tk.BooleanVar(value=True)  # type: ignore[name-defined]
        make_switch(config_card, "Auto-open logs after run", variable=switch_var).pack(anchor="w", padx=8, pady=(4, 8))

        # --- Row 2: Accounting Period + Warehouse / Providers -------------------------------------
        period_card = make_card(body, "Accounting Period")
        period_card.grid(row=1, column=0, sticky="nsew", padx=(0, FRAME_PADDING), pady=(0, 0))

        make_label(period_card, "Period start (YYYY-MM):", category="Body", surface="Secondary", weight="Normal").pack(
            anchor="w", padx=8
        )
        make_entry(period_card, width=12).pack(anchor="w", padx=8, pady=(0, 4))

        make_label(period_card, "Period end (YYYY-MM):", category="Body", surface="Secondary", weight="Normal").pack(
            anchor="w", padx=8
        )
        make_entry(period_card, width=12).pack(anchor="w", padx=8, pady=(0, 4))

        lp_spacer(period_card, height=4).pack(fill="x")
        chk_lock = tk.BooleanVar(value=True)  # type: ignore[name-defined]
        make_checkbox(period_card, "Lock period after successful run", variable=chk_lock).pack(
            anchor="w", padx=8, pady=(4, 8)
        )

        warehouse_card = make_card(body, "Data Warehouse & Providers")
        warehouse_card.grid(row=1, column=1, sticky="nsew", padx=(FRAME_PADDING, 0), pady=(0, 0))

        make_label(warehouse_card, "Warehouse destination:", category="Body", surface="Secondary", weight="Normal").pack(
            anchor="w", padx=8
        )
        make_combobox(
            warehouse_card,
            values=["Snowflake – PROD", "Snowflake – UAT", "Local CSV export"],
            state="readonly",
            width=30,
        ).pack(anchor="w", padx=8, pady=(0, 4))

        make_label(warehouse_card, "Providers in this preset:", category="Body", surface="Secondary", weight="Normal").pack(
            anchor="w", padx=8, pady=(6, 2)
        )
        make_label(warehouse_card, "• Braintree\n• Uber Eats\n• Deliveroo", category="Body", surface="Secondary", weight="Normal").pack(
            anchor="w", padx=8
        )

        lp_spacer(warehouse_card, height=4).pack(fill="x")
        make_label(
            warehouse_card,
            "3 providers configured",
            category="Body",
            surface="Secondary",
            weight="Normal",
        ).pack(anchor="w", padx=8, pady=(2, 8))

        # --- Bottom status strip -------------------------------------------------------------------
        lp_divider(right).pack(fill="x", pady=(8, 4))
        status_bar = ttk.Frame(right)
        status_bar.pack(fill="x", pady=(0, 2))

        make_label(status_bar, "Status:", category="Body", surface="Primary", weight="Normal").pack(side="left", padx=(0, 4))
        make_label(status_bar, "Idle – no run in progress", category="Body", surface="Primary", weight="Normal").pack(side="left")

        make_label(
            status_bar,
            "Tip: use this as a starting point for real connection dashboards.",
            category="Body",
            surface="Primary",
            weight="Normal",
        ).pack(side="right")


# ====================================================================================================
# 5. MAIN ENTRY POINT
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging()
    app = DemoAllPrimitives(title="GUI Boilerplate – G01 Component Explorer")
    app.mainloop()