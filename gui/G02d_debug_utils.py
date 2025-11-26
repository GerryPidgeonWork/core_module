# ====================================================================================================
# G02d_debug_utils.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Developer Debug Console for GUI Boilerplate (G00 + G01x + G02x)
#
#   Provides a single entry point to visually and programmatically verify:
#       • G01a_style_config       (design tokens)
#       • G01b_style_engine       (ttk style definitions)
#       • G01c_widget_primitives  (widget factories)
#       • G01d_layout_primitives  (layout wrappers)
#       • G02a_layout_utils       (grid/pack helpers)
#       • G02b_container_patterns (sections/cards)
#       • G02c_form_patterns      (schema-driven forms)
#
#   The console opens a Tk/ttk (or ttkbootstrap) window with a ttk.Notebook containing tabs:
#       1. Imports & Styles
#       2. Widget Primitives
#       3. Layout Helpers
#       4. Container Patterns
#       5. Form Patterns
#
#   All tests are run automatically on startup (no buttons required). Each tab exercises the
#   relevant module(s) using the same style + layout system as production GUIs.
#
# Usage:
#   python gui/G02d_debug_utils.py
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
from gui.G01a_style_config import *  # FRAME_SIZE_H, FRAME_SIZE_V, FRAME_PADDING, GUI_COLOUR_BG_PRIMARY, etc.
from gui.G01b_style_engine import (
    configure_ttk_styles,
    FONT_NAME_BASE,
    FONT_NAME_HEADING,
    FONT_NAME_SECTION_HEADING,
)
from gui.G01c_widget_primitives import (
    make_label,
    make_button,
    make_entry,
    make_textarea,
    make_combobox,
    make_checkbox,
    make_radio,
    make_switch,
    make_divider,
    make_spacer,
)
from gui.G01d_layout_primitives import *  # imported for coverage; typically attaches to UIComponents
from gui.G02a_layout_utils import (
    safe_grid,
    safe_pack,
    ensure_row_weights,
    ensure_column_weights,
    grid_form_row,
)
from gui.G02b_container_patterns import (
    create_section_grid,
    create_card_grid,
    create_two_column_body,
)
from gui.G02c_form_patterns import FormBuilder

# Prefer ttkbootstrap's ttk-compatible widgets when available, otherwise fall back to standard ttk.
try:
    bttk = tb  # type: ignore[name-defined]
except Exception:
    bttk = ttk  # type: ignore[assignment]


# ====================================================================================================
# 3. IMPORT & STYLE DIAGNOSTICS
# ----------------------------------------------------------------------------------------------------
def gather_import_diagnostics() -> List[Tuple[str, str]]:
    """
    Attempt to import all key GUI modules again (safe even if already imported)
    and return a list of (module_label, status_text).
    """
    checks: List[Tuple[str, str]] = []
    modules = [
        ("gui.G01a_style_config", "G01a_style_config"),
        ("gui.G01b_style_engine", "G01b_style_engine"),
        ("gui.G01c_widget_primitives", "G01c_widget_primitives"),
        ("gui.G01d_layout_primitives", "G01d_layout_primitives"),
        ("gui.G02a_layout_utils", "G02a_layout_utils"),
        ("gui.G02b_container_patterns", "G02b_container_patterns"),
        ("gui.G02c_form_patterns", "G02c_form_patterns"),
    ]

    for import_path, label in modules:
        try:
            __import__(import_path, fromlist=["*"])
            checks.append((label, "OK"))
        except Exception as exc:  # noqa: BLE001
            logger.exception("[G02d] Import failed for %s: %s", import_path, exc)
            checks.append((label, f"FAIL – {exc}"))

    return checks


def gather_style_diagnostics(style_obj: ttk.Style) -> Dict[str, Any]:
    """
    Collect simple diagnostics about the active ttk/ttkbootstrap Style instance.
    """
    diag: Dict[str, Any] = {}

    # Theme info
    try:
        diag["theme"] = style_obj.theme_use()
    except Exception:
        diag["theme"] = "(unavailable)"

    # Named fonts (from G01a_style_engine)
    def _font_exists(name: str | None) -> bool:
        if not name:
            return False
        try:
            tkFont.nametofont(name)
            return True
        except Exception:
            return False

    diag["FONT_NAME_BASE_exists"] = _font_exists(FONT_NAME_BASE)
    diag["FONT_NAME_HEADING_exists"] = _font_exists(FONT_NAME_HEADING)
    diag["FONT_NAME_SECTION_HEADING_exists"] = _font_exists(FONT_NAME_SECTION_HEADING)

    # Key styles – presence check only (no assertion)
    style_names = [
        "TLabel",
        "TButton",
        "Primary.SectionHeading.Bold.TLabel",
        "Primary.Normal.TLabel",
        "Secondary.Normal.TLabel",
        "SectionOuter.TFrame",
        "SectionBody.TFrame",
        "ToolbarDivider.TFrame",
        "Vertical.TScrollbar",
    ]

    present: Dict[str, bool] = {}
    for name in style_names:
        try:
            _ = style_obj.lookup(name, "font")
            present[name] = True
        except Exception:
            present[name] = False
    diag["styles_present"] = present

    return diag


# ====================================================================================================
# 4. TAB BUILDERS
# ----------------------------------------------------------------------------------------------------
def build_tab_imports_and_styles(parent: tk.Misc, style_obj: ttk.Style) -> None:  # type: ignore[name-defined]
    """Build the 'Imports & Styles' tab content."""
    container = ttk.Frame(parent, style="SectionOuter.TFrame")
    container.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)

    make_label(
        container,
        "G01x + G02x Imports & Styles",
        category="WindowHeading",
        surface="Primary",
        weight="Bold",
    ).pack(anchor="w", pady=(0, 8))
    make_label(
        container,
        "Overview of module import status and key style / font diagnostics.",
        category="Body",
        surface="Primary",
        weight="Normal",
    ).pack(anchor="w", pady=(0, 12))

    # Import results
    import_results = gather_import_diagnostics()

    imports_frame = ttk.Frame(container, style="SectionOuter.TFrame")
    imports_frame.pack(fill="x", pady=(0, 12))

    make_label(
        imports_frame,
        "Module Import Status",
        category="SectionHeading",
        surface="Primary",
        weight="Bold",
    ).pack(anchor="w", pady=(0, 4))

    for label, status in import_results:
        text = f"{label:<30} : {status}"
        if status == "OK":
            make_label(imports_frame, text, category="Success", surface="Primary", weight="Normal").pack(anchor="w")
        else:
            make_label(imports_frame, text, category="Error", surface="Primary", weight="Normal").pack(anchor="w")

    make_divider(container).pack(fill="x", pady=(8, 12))

    # Style diagnostics
    style_diag = gather_style_diagnostics(style_obj)

    style_frame = ttk.Frame(container, style="SectionOuter.TFrame")
    style_frame.pack(fill="both", expand=True)

    make_label(
        style_frame,
        "Style Engine Diagnostics",
        category="SectionHeading",
        surface="Primary",
        weight="Bold",
    ).pack(anchor="w", pady=(0, 4))

    make_label(
        style_frame,
        f"Active theme: {style_diag.get('theme')}",
        category="Body",
        surface="Primary",
        weight="Normal",
    ).pack(anchor="w", pady=(0, 4))

    font_info = (
        f"Named fonts: BASE={FONT_NAME_BASE!r} "
        f"(exists={style_diag['FONT_NAME_BASE_exists']}), "
        f"HEADING={FONT_NAME_HEADING!r} "
        f"(exists={style_diag['FONT_NAME_HEADING_exists']}), "
        f"SECTION={FONT_NAME_SECTION_HEADING!r} "
        f"(exists={style_diag['FONT_NAME_SECTION_HEADING_exists']})"
    )
    make_label(
        style_frame,
        font_info,
        category="Body",
        surface="Primary",
        weight="Normal",
    ).pack(anchor="w", pady=(0, 8))

    make_label(
        style_frame,
        "Key Style Presence",
        category="SectionHeading",
        surface="Primary",
        weight="Bold",
    ).pack(anchor="w", pady=(4, 4))
    for style_name, present in style_diag["styles_present"].items():
        if present:
            make_label(
                style_frame,
                f"{style_name:<40} : present",
                category="Success",
                surface="Primary",
                weight="Normal",
            ).pack(anchor="w")
        else:
            make_label(
                style_frame,
                f"{style_name:<40} : missing",
                category="Warning",
                surface="Primary",
                weight="Normal",
            ).pack(anchor="w")


def build_tab_widget_primitives(parent: tk.Misc) -> None:  # type: ignore[name-defined]
    """Build the 'Widget Primitives' tab content."""
    outer = ttk.Frame(parent, style="SectionOuter.TFrame")
    outer.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)

    make_label(
        outer,
        "G01c Widget Primitives",
        category="WindowHeading",
        surface="Primary",
        weight="Bold",
    ).pack(anchor="w", pady=(0, 8))
    make_label(
        outer,
        "Core text, input, and choice widgets constructed via make_* helpers.",
        category="Body",
        surface="Primary",
        weight="Normal",
    ).pack(anchor="w", pady=(0, 12))

    # Textual widgets
    text_frame = ttk.Frame(outer, style="SectionOuter.TFrame")
    text_frame.pack(fill="x", pady=(0, 10))

    make_label(
        text_frame,
        "Textual Widgets",
        category="SectionHeading",
        surface="Primary",
        weight="Bold",
    ).pack(anchor="w", pady=(0, 4))
    make_label(text_frame, "Standard label text.", category="Body", surface="Primary", weight="Normal").pack(anchor="w", pady=2)
    make_label(text_frame, "Success status", category="Success", surface="Primary", weight="Normal").pack(anchor="w", pady=1)
    make_label(text_frame, "Warning status", category="Warning", surface="Primary", weight="Normal").pack(anchor="w", pady=1)
    make_label(text_frame, "Error status", category="Error", surface="Primary", weight="Normal").pack(anchor="w", pady=1)

    make_divider(outer).pack(fill="x", pady=(8, 8))

    # Inputs
    input_frame = ttk.Frame(outer, style="SectionOuter.TFrame")
    input_frame.pack(fill="x", pady=(0, 10))

    make_label(
        input_frame,
        "Input Widgets",
        category="SectionHeading",
        surface="Primary",
        weight="Bold",
    ).pack(anchor="w", pady=(0, 4))

    make_label(input_frame, "Entry:", category="Body", surface="Primary", weight="Normal").pack(anchor="w")
    make_entry(input_frame, width=30).pack(anchor="w", pady=(0, 6))

    make_label(input_frame, "Combobox:", category="Body", surface="Primary", weight="Normal").pack(anchor="w")
    make_combobox(
        input_frame,
        values=["Option A", "Option B", "Option C"],
        state="readonly",
        width=28,
    ).pack(anchor="w", pady=(0, 6))

    make_label(input_frame, "Textarea:", category="Body", surface="Primary", weight="Normal").pack(anchor="w")
    make_textarea(input_frame, height=4).pack(fill="both", expand=True, pady=(0, 6))

    make_divider(outer).pack(fill="x", pady=(8, 8))

    # Choice widgets
    choice_frame = ttk.Frame(outer, style="SectionOuter.TFrame")
    choice_frame.pack(fill="x", pady=(0, 10))

    make_label(
        choice_frame,
        "Choice Widgets",
        category="SectionHeading",
        surface="Primary",
        weight="Bold",
    ).pack(anchor="w", pady=(0, 4))

    chk_var = tk.BooleanVar(value=True)
    make_checkbox(choice_frame, "Enable feature X", variable=chk_var).pack(anchor="w", pady=2)

    radio_var = tk.StringVar(value="A")
    make_radio(choice_frame, "Radio A", variable=radio_var, value="A").pack(anchor="w")
    make_radio(choice_frame, "Radio B", variable=radio_var, value="B").pack(anchor="w")

    switch_var = tk.BooleanVar(value=False)
    make_switch(choice_frame, "Use experimental mode", variable=switch_var).pack(anchor="w", pady=(6, 0))

    make_divider(outer).pack(fill="x", pady=(8, 8))

    # Structural widgets
    struct_frame = ttk.Frame(outer, style="SectionOuter.TFrame")
    struct_frame.pack(fill="x")

    make_label(
        struct_frame,
        "Structural Helpers",
        category="SectionHeading",
        surface="Primary",
        weight="Bold",
    ).pack(anchor="w", pady=(0, 4))
    make_label(struct_frame, "Divider below:", category="Body", surface="Primary", weight="Normal").pack(anchor="w")
    make_divider(struct_frame).pack(fill="x", pady=(4, 4))
    make_label(struct_frame, "Spacer below (16px):", category="Body", surface="Primary", weight="Normal").pack(anchor="w")
    make_spacer(struct_frame, height=16).pack(fill="x")


def build_tab_layout_helpers(parent: tk.Misc) -> None:  # type: ignore[name-defined]
    """Build the 'Layout Helpers' tab content (G02a)."""
    outer = ttk.Frame(parent, style="SectionOuter.TFrame")
    outer.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)

    make_label(
        outer,
        "G02a Layout Helpers",
        category="WindowHeading",
        surface="Primary",
        weight="Bold",
    ).pack(anchor="w", pady=(0, 8))
    make_label(
        outer,
        "Demonstrates safe_grid, safe_pack, ensure_row_weights / ensure_column_weights, "
        "and grid_form_row.",
        category="Body",
        surface="Primary",
        weight="Normal",
    ).pack(anchor="w", pady=(0, 12))

    frame = ttk.Frame(outer, style="SectionOuter.TFrame")
    frame.pack(fill="x")

    # Configure column weights using helpers
    ensure_column_weights(frame, [0, 1], weights=[0, 1])

    # Row 0: Name
    lbl_name = make_label(frame, "Name:", category="Body", surface="Primary", weight="Normal")
    ent_name = make_entry(frame, width=30)
    grid_form_row(
        frame,
        row=0,
        label_widget=lbl_name,
        field_widget=ent_name,
    )

    # Row 1: Category
    lbl_cat = make_label(frame, "Category:", category="Body", surface="Primary", weight="Normal")
    cmb_cat = make_combobox(
        frame,
        values=["A", "B", "C"],
        state="readonly",
        width=28,
    )
    grid_form_row(
        frame,
        row=1,
        label_widget=lbl_cat,
        field_widget=cmb_cat,
    )

    # Demonstrate safe_pack for a bottom status label
    status = make_label(
        outer,
        "This status label was positioned with safe_pack.",
        category="Success",
        surface="Primary",
        weight="Normal",
    )
    safe_pack(status, anchor="w", pady=(12, 0))


def build_tab_container_patterns(parent: tk.Misc) -> None:  # type: ignore[name-defined]
    """Build the 'Container Patterns' tab content (G02b)."""
    outer = ttk.Frame(parent, style="SectionOuter.TFrame")
    outer.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)

    make_label(
        outer,
        "G02b Container Patterns",
        category="WindowHeading",
        surface="Primary",
        weight="Bold",
    ).pack(anchor="w", pady=(0, 8))
    make_label(
        outer,
        "Standardised sections and cards created with create_section_grid() "
        "and create_card_grid().",
        category="Body",
        surface="Primary",
        weight="Normal",
    ).pack(anchor="w", pady=(0, 12))

    # Use a dedicated body frame for all grid-managed content to avoid mixing
    # pack and grid on the same parent.
    body = ttk.Frame(outer, style="SectionOuter.TFrame")
    body.pack(fill="both", expand=True)

    # Main section
    section = create_section_grid(
        parent=body,
        row=0,
        column=0,
        columnspan=2,
        title="Primary Section (Two-Column Body)",
    )

    left, right = create_two_column_body(section)

    make_label(left, "Left column label 1", category="Body", surface="Secondary", weight="Normal").grid(row=0, column=0, sticky="w", pady=2)
    make_label(left, "Left column label 2", category="Body", surface="Secondary", weight="Normal").grid(row=1, column=0, sticky="w", pady=2)
    make_label(right, "Right column label 1", category="Body", surface="Secondary", weight="Normal").grid(row=0, column=0, sticky="w", pady=2)
    make_label(right, "Right column label 2", category="Body", surface="Secondary", weight="Normal").grid(row=1, column=0, sticky="w", pady=2)

    # Cards under the section
    card_row = 2
    card_a = create_card_grid(
        parent=body,
        row=card_row,
        column=0,
        title="Card A",
    )
    card_b = create_card_grid(
        parent=body,
        row=card_row,
        column=1,
        title="Card B",
    )

    make_label(card_a.body, "Card A body content.", category="Body", surface="Secondary", weight="Normal").grid(row=0, column=0, sticky="w", pady=2)
    make_label(card_b.body, "Card B body content.", category="Body", surface="Secondary", weight="Normal").grid(row=0, column=0, sticky="w", pady=2)

    # Ensure the grid in the body frame stretches
    body.columnconfigure(0, weight=1)
    body.columnconfigure(1, weight=1)


def build_tab_form_patterns(parent: tk.Misc) -> None:  # type: ignore[name-defined]
    """Build the 'Form Patterns' tab content (G02c)."""
    outer = ttk.Frame(parent, style="SectionOuter.TFrame")
    outer.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)

    make_label(
        outer,
        "G02c Form Patterns",
        category="WindowHeading",
        surface="Primary",
        weight="Bold",
    ).pack(anchor="w", pady=(0, 8))
    make_label(
        outer,
        "Schema-driven forms using FormBuilder, with validation and value model.",
        category="Body",
        surface="Primary",
        weight="Normal",
    ).pack(anchor="w", pady=(0, 12))

    form_frame = ttk.Frame(outer, style="SectionOuter.TFrame")
    form_frame.pack(fill="x")

    schema = [
        {"type": "entry", "label": "Host", "key": "host", "required": True, "default": "localhost"},
        {"type": "entry", "label": "Port", "key": "port", "numeric": True, "default": "1521"},
        {
            "type": "combo",
            "label": "Environment",
            "key": "env",
            "values": ["Dev", "UAT", "Prod"],
            "required": True,
            "default": "Dev",
        },
        {"type": "checkbox", "label": "Use SSL", "key": "ssl", "default": True},
        {"type": "text", "label": "Description", "key": "desc"},
    ]

    form = FormBuilder(form_frame, schema=schema)

    # Buttons row
    buttons = ttk.Frame(outer, style="SectionOuter.TFrame")
    buttons.pack(fill="x", pady=(12, 0))

    def on_print() -> None:
        values = form.get_values()
        errors = form.validate_all()
        logger.info("[G02d] Form values: %s", values)
        logger.info("[G02d] Form errors: %s", errors)

    def on_clear() -> None:
        form.clear()

    ttk.Button(buttons, text="Print Values / Errors (to log)", command=on_print).pack(side="left")
    ttk.Button(buttons, text="Clear", command=on_clear).pack(side="left", padx=(8, 0))


# ====================================================================================================
# 5. MAIN DEBUG CONSOLE
# ----------------------------------------------------------------------------------------------------
def run_debug_console() -> None:
    """Entry point: build and run the G01x + G02x debug console."""
    init_logging()
    logger.info("=== G02d_debug_utils – Debug Console Start ===")

    # -----------------------------------------------------------------------------------------------
    # Window & style initialisation
    # -----------------------------------------------------------------------------------------------
    try:
        root = Window(themename="flatly")  # type: ignore[name-defined]
        style_obj = Style()                # type: ignore[name-defined]
        logger.info("[G02d] Using ttkbootstrap Window/Style.")
    except Exception:
        root = tk.Tk()
        style_obj = ttk.Style()
        logger.info("[G02d] Falling back to standard Tk/ttk.")

    root.title("G02d – Debug Console")
    root.geometry(f"{FRAME_SIZE_H}x{FRAME_SIZE_V}")
    root.configure(bg=GUI_COLOUR_BG_PRIMARY)

    # Apply global ttk styles
    configure_ttk_styles(style_obj)  # type: ignore[arg-type]
    logger.info("[G02d] configure_ttk_styles applied successfully.")

    # -----------------------------------------------------------------------------------------------
    # Notebook + tabs
    # -----------------------------------------------------------------------------------------------
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)

    tab_imports = ttk.Frame(notebook, style="SectionOuter.TFrame")
    tab_widgets = ttk.Frame(notebook, style="SectionOuter.TFrame")
    tab_layout_helpers = ttk.Frame(notebook, style="SectionOuter.TFrame")
    tab_containers = ttk.Frame(notebook, style="SectionOuter.TFrame")
    tab_forms = ttk.Frame(notebook, style="SectionOuter.TFrame")

    notebook.add(tab_imports, text="Imports & Styles")
    notebook.add(tab_widgets, text="Widget Primitives")
    notebook.add(tab_layout_helpers, text="Layout Helpers")
    notebook.add(tab_containers, text="Container Patterns")
    notebook.add(tab_forms, text="Form Patterns")

    # Build each tab (auto-run tests)
    build_tab_imports_and_styles(tab_imports, style_obj)
    build_tab_widget_primitives(tab_widgets)
    build_tab_layout_helpers(tab_layout_helpers)
    build_tab_container_patterns(tab_containers)
    build_tab_form_patterns(tab_forms)

    logger.info("=== G02d_debug_utils – Debug Console Ready ===")
    root.mainloop()
    logger.info("=== G02d_debug_utils – Debug Console End ===")


# ====================================================================================================
# 6. MAIN GUARD
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    run_debug_console()