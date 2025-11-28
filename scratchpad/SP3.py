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
# SP3.py — Visual Demonstration of G02a Layout Helpers
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Provide a simple, visual, developer-friendly demonstration of the key G02a layout helpers:
#       • safe_grid
#       • safe_pack
#       • ensure_row_weights / ensure_column_weights
#       • grid_form_row
#
#   This is NOT a production script — it is purely a training / demonstration tool.
# ====================================================================================================

from gui.G00a_gui_packages import tk, ttk
from gui.G01a_style_config import FRAME_PADDING, GUI_COLOUR_BG_PRIMARY
from gui.G01b_style_engine import configure_ttk_styles
from gui.G01c_widget_primitives import (
    make_label,
    make_button,
    make_entry,
    make_combobox,
    make_spacer,
)
from gui.G02a_layout_utils import (
    safe_grid,
    safe_pack,
    ensure_row_weights,
    ensure_column_weights,
    grid_form_row,
)


def demo_header(parent, text: str) -> None:
    """Simple section heading."""
    lbl = make_label(
        parent,
        text,
        category="SectionHeading",
        surface="Primary",
        weight="Bold",
    )
    safe_pack(lbl, anchor="w", pady=(12, 6))


def run_demo() -> None:
    root = tk.Tk()
    root.title("SP3 — G02a Layout Utils Visual Demo")
    root.geometry("880x650")
    root.configure(bg=GUI_COLOUR_BG_PRIMARY)

    style = ttk.Style(root)
    configure_ttk_styles(style)

    outer = ttk.Frame(root, padding=FRAME_PADDING, style="TFrame")
    outer.pack(fill="both", expand=True)

    # =================================================================================================
    # 1. safe_grid Demo
    # =================================================================================================
    demo_header(outer, "1. safe_grid Demonstration")

    grid_demo = ttk.Frame(outer, style="TFrame")
    safe_pack(grid_demo, fill="x", pady=(0, 10))

    # 3 columns: 33% / 33% / 33%
    ensure_column_weights(grid_demo, [0, 1, 2])

    lbl1 = make_label(grid_demo, "Left column", category="Body", surface="Primary")
    lbl2 = make_label(grid_demo, "Middle column", category="Body", surface="Primary")
    lbl3 = make_label(grid_demo, "Right column", category="Body", surface="Primary")

    safe_grid(lbl1, row=0, column=0, sticky="n")
    safe_grid(lbl2, row=0, column=1, sticky="n")
    safe_grid(lbl3, row=0, column=2, sticky="n")

    # =================================================================================================
    # 2. safe_pack Demo
    # =================================================================================================
    demo_header(outer, "2. safe_pack Demonstration")

    pack_demo = ttk.Frame(outer, style="TFrame", padding=8)
    safe_pack(pack_demo, fill="x")

    b1 = make_button(pack_demo, "Left Button")
    b2 = make_button(pack_demo, "Center Button")
    b3 = make_button(pack_demo, "Right Button")

    safe_pack(b1, side="left", padx=4)
    safe_pack(b2, side="top", pady=4, anchor="center")
    safe_pack(b3, side="right", padx=4)

    # =================================================================================================
    # 3. ensure_row_weights / ensure_column_weights Demo
    # =================================================================================================
    demo_header(outer, "3. ensure_row_weights / ensure_column_weights Demonstration")

    weight_demo = ttk.Frame(outer, style="TFrame")
    safe_pack(weight_demo, fill="both", expand=True)

    # Make a 2×2 grid that stretches perfectly when the window resizes
    ensure_row_weights(weight_demo, [0, 1])
    ensure_column_weights(weight_demo, [0, 1])

    box_style = {"width": 18, "height": 3}

    top_left = ttk.Label(weight_demo, text="(0,0)", anchor="center")
    top_right = ttk.Label(weight_demo, text="(0,1)", anchor="center")
    bot_left = ttk.Label(weight_demo, text="(1,0)", anchor="center")
    bot_right = ttk.Label(weight_demo, text="(1,1)", anchor="center")

    safe_grid(top_left, **{"row": 0, "column": 0, "sticky": "nsew", "padx": 4, "pady": 4})
    safe_grid(top_right, **{"row": 0, "column": 1, "sticky": "nsew", "padx": 4, "pady": 4})
    safe_grid(bot_left, **{"row": 1, "column": 0, "sticky": "nsew", "padx": 4, "pady": 4})
    safe_grid(bot_right, **{"row": 1, "column": 1, "sticky": "nsew", "padx": 4, "pady": 4})

    # =================================================================================================
    # 4. grid_form_row Demo
    # =================================================================================================
    demo_header(outer, "4. grid_form_row Demonstration")

    form_demo = ttk.Frame(outer, style="TFrame")
    safe_pack(form_demo, fill="x")

    # Make the form column stretch
    ensure_column_weights(form_demo, [1])

    # Row 0
    lbl_name = make_label(form_demo, "Your Name:", category="Body", surface="Primary")
    ent_name = make_entry(form_demo, width=30)

    grid_form_row(form_demo, 0, lbl_name, ent_name)

    # Row 1
    lbl_type = make_label(form_demo, "User Type:", category="Body", surface="Primary")
    cmb_type = make_combobox(
        form_demo, values=["Admin", "Editor", "Viewer"], state="readonly", width=28
    )

    grid_form_row(form_demo, 1, lbl_type, cmb_type)

    make_spacer(outer, height=16).pack()

    root.mainloop()


if __name__ == "__main__":
    run_demo()
