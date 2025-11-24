# ====================================================================================================
# G03c_dynamic_layout_engine.py
# ----------------------------------------------------------------------------------------------------
# Dynamic Layout Engine for GUIBoilerplatePython
#
# Purpose:
#   Provide a unified, zero-widget, styling-agnostic layout system used by all GUI modules.
#   This file contains ONLY layout behaviour — no widgets, no styling, no business logic.
#
# Features:
#   • Spacing constants (padding, gutters, column gaps)
#   • Low-level grid utilities (configure_grid, clear_frame)
#   • Reusable page-level layout helpers (make_page_frame, single_column_layout)
#   • Two-column responsive layout pattern
#   • High-level page templates (dashboard_page, form_page)
#   • Optional debugging utilities for grid/pack inspection
#
# Design Principles:
#   • 100% deterministic: no side effects at import time.
#   • Works with tk.Frame, ttk.Frame, BasePage, or any container widget.
#   • Designed for G03 “Reusable Widgets & UI Patterns” layer.
#   • Imports:
#         - ALL external packages → core.C00_set_packages
#         - ALL Tk/ttk UI packages → gui.G00a_gui_packages
#
# Integration:
#       from gui.G03c_dynamic_layout_engine import (
#           make_page_frame, two_column_layout,
#           PAD_X, PAD_Y, GUTTER, configure_grid
#       )
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
from core.C03_logging_handler import get_logger, log_divider


# ====================================================================================================
# 3. LAYOUT CONSTANTS
# ----------------------------------------------------------------------------------------------------

# Standard padding for widgets inside sections/frames
PAD_X = 12
PAD_Y = 8

# Larger spacing between grouped components
GUTTER = 16

# Column spacing used in multi-column layouts
COL_GAP = 20


# ====================================================================================================
# 4. LOW-LEVEL GRID UTILITIES
# ----------------------------------------------------------------------------------------------------
def configure_grid(frame: tk.Widget, rows: int, cols: int, *, row_weight=1, col_weight=1):
    """
    Configure row/column weights for a frame.

    Example:
        configure_grid(my_frame, rows=3, cols=2)
    """
    for r in range(rows):
        frame.grid_rowconfigure(r, weight=row_weight)
    for c in range(cols):
        frame.grid_columnconfigure(c, weight=col_weight)


def clear_frame(frame: tk.Widget):
    """Remove all child widgets from a frame."""
    for child in frame.winfo_children():
        child.destroy()


# ====================================================================================================
# 5. PAGE LAYOUT HELPERS
# ----------------------------------------------------------------------------------------------------
def make_page_frame(parent: tk.Widget) -> ttk.Frame:
    """
    Create a clean page frame with standard padding + expansion.

    Usage in any PageClass.build_page():
        page = make_page_frame(self)
        ttk.Label(page, text="Some content").grid(...)
    """
    frame = ttk.Frame(parent, padding=(PAD_X, PAD_Y))
    frame.grid_columnconfigure(0, weight=1)
    return frame


def single_column_layout(parent: tk.Widget) -> ttk.Frame:
    """
    Create a vertically-stacked single-column layout.

    Useful for form-based pages, settings pages, or long content sections.
    """
    frame = ttk.Frame(parent, padding=(PAD_X, PAD_Y))
    frame.grid_columnconfigure(0, weight=1)
    return frame


def two_column_layout(parent: tk.Widget) -> tuple[ttk.Frame, ttk.Frame]:
    """
    Create a responsive two-column layout.

    Returns (left_frame, right_frame)
    """
    container = ttk.Frame(parent, padding=(PAD_X, PAD_Y))
    container.grid_columnconfigure(0, weight=1)
    container.grid_columnconfigure(1, weight=1)

    left = ttk.Frame(container, padding=(0, 0))
    right = ttk.Frame(container, padding=(0, 0))

    left.grid(row=0, column=0, sticky="nsew", padx=(0, COL_GAP))
    right.grid(row=0, column=1, sticky="nsew")

    return left, right


def form_row(parent: tk.Widget, label_text: str, widget: tk.Widget, *, pady=4):
    """
    Add a labelled input row to a form.

    Example:
        entry = ttk.Entry(...)
        form_row(form_frame, "Username:", entry)
    """
    row_frame = ttk.Frame(parent)
    row_frame.pack(fill="x", pady=pady)

    lbl = ttk.Label(row_frame, text=label_text)
    lbl.pack(side="left")

    widget.pack(side="right", fill="x", expand=True)

    return row_frame


# ====================================================================================================
# 6. HIGH-LEVEL PAGE TEMPLATES
# ----------------------------------------------------------------------------------------------------
def dashboard_page(parent: tk.Widget):
    """
    Quick template for dashboard-style pages:
        • Flexible grid
        • Expanding rows/columns
        • Suitable for cards, summary boxes, metrics

    Example:
        grid = dashboard_page(self)
        Card(grid, ...).grid(row=0, column=0)
    """
    frame = ttk.Frame(parent, padding=(PAD_X, PAD_Y))
    configure_grid(frame, rows=4, cols=4, row_weight=1, col_weight=1)
    return frame


def form_page(parent: tk.Widget):
    """
    Template for input-heavy pages.
    """
    frame = ttk.Frame(parent, padding=(PAD_X, PAD_Y))
    frame.grid_columnconfigure(0, weight=1)
    return frame


# ====================================================================================================
# 7. SANDBOX TEST
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Quick layout test window
    root = tk.Tk()
    root.title("G04 Layout Engine – Sandbox")
    root.geometry("800x600")

    page = make_page_frame(root)
    page.pack(fill="both", expand=True)

    ttk.Label(page, text="Layout Engine Sandbox").grid(row=0, column=0, sticky="w", pady=(0, GUTTER))

    left, right = two_column_layout(page)
    left.grid(row=1, column=0, sticky="nsew")
    right.grid(row=2, column=0, sticky="nsew")

    ttk.Label(left, text="Left Column").pack(pady=10)
    ttk.Label(right, text="Right Column").pack(pady=10)

    root.mainloop()

# ====================================================================================================
# 8. OPTIONAL DEBUGGING SUPPORT
# ----------------------------------------------------------------------------------------------------
# These helpers provide structure inspection and grid/pack diagnostics.
# They remain silent unless LAYOUT_DEBUG is set to True.
# ====================================================================================================

LAYOUT_DEBUG = True
_layout_logger = get_logger("G04_layout_engine")

def debug(msg: str) -> None:
    """Internal conditional logger."""
    if LAYOUT_DEBUG:
        _layout_logger.info(f"[G04] {msg}")


def debug_grid(frame: tk.Widget) -> None:
    """
    Log grid configuration for a frame and its children.
    """
    if not LAYOUT_DEBUG:
        return

    log_divider(label="G04 Grid Debug")
    debug(f"Frame: {frame.winfo_pathname(frame.winfo_id())}")

    # Row/column weights
    debug("Row Weights:")
    for r in range(10):  # limit to 10 rows
        try:
            weight = frame.grid_rowconfigure(r)["weight"]
            debug(f"  Row {r}: weight={weight}")
        except Exception:
            break

    debug("Column Weights:")
    for c in range(10):
        try:
            weight = frame.grid_columnconfigure(c)["weight"]
            debug(f"  Col {c}: weight={weight}")
        except Exception:
            break

    # Children
    debug("Children (grid info):")
    for child in frame.winfo_children():
        info = child.grid_info()
        if info:
            debug(f"  {child}: {info}")


def debug_pack(frame: tk.Widget) -> None:
    """
    Log pack configuration for a frame and its children.
    """
    if not LAYOUT_DEBUG:
        return

    log_divider(label="G04 Pack Debug")
    debug(f"Frame: {frame.winfo_pathname(frame.winfo_id())}")

    for child in frame.winfo_children():
        info = child.pack_info() if child.pack_info() else {}
        debug(f"  {child}: {info}")


def debug_summary(frame: tk.Widget) -> None:
    """
    Summary of layout configuration (grid + pack).
    """
    if not LAYOUT_DEBUG:
        return

    log_divider(label="G04 Layout Summary")
    debug(f"Frame: {frame.winfo_pathname(frame.winfo_id())}")
    debug(f"Children count: {len(frame.winfo_children())}")

    for child in frame.winfo_children():
        child_path = child.winfo_pathname(child.winfo_id())
        debug(f"  Child: {child_path}")

        if child.grid_info():
            debug(f"    grid: {child.grid_info()}")
        if child.pack_info():
            debug(f"    pack: {child.pack_info()}")
