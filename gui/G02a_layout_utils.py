# ====================================================================================================
# G02a_layout_utils.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Provide reusable, theme-aware layout helpers for all GUI modules.
#
#   This module focuses on geometry and grid/pack behaviour only:
#       • merge_geometry_kwargs(widget, overrides)
#       • safe_grid(widget, **kwargs)      – merge geometry_kwargs then call grid(...)
#       • safe_pack(widget, **kwargs)      – merge geometry_kwargs then call pack(...)
#       • ensure_row_weights(container, ...)    – configure row weights in a DRY way
#       • ensure_column_weights(container, ...) – configure column weights in a DRY way
#       • grid_form_row(...)               – standard 2-column label + field layout
#
#   It also provides:
#       • attach_layout_helpers(UIClass)
#           - Monkey-patches these helpers as methods on a UI factory class:
#               ui.safe_grid(widget, **kwargs)
#               ui.safe_pack(widget, **kwargs)
#               ui.ensure_row_weights(container, rows, ...)
#               ui.ensure_column_weights(container, columns, ...)
#               ui.grid_form_row(parent, row_index, label_widget, field_widget, ...)
#
# Design:
#   - Layout-only: no widget creation happens here (that lives in G01b_widget_primitives).
#   - Styling is delegated to G01a_style_engine + G00a_style_config.
#   - Safe to import in any GUI module; no side-effects except when attach_layout_helpers is called.
#
# Debugging:
#   - Uses core.C03_logging_handler.get_logger for structured logging.
#   - DEBUG_LAYOUT_HELPERS toggles extra diagnostics.
#
# Integration:
#   from gui.G01d_layout_helpers import (
#       safe_grid, safe_pack,
#       ensure_row_weights, ensure_column_weights,
#       grid_form_row,
#       attach_layout_helpers,
#   )
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
from gui.G00a_gui_packages import tk, ttk  # dedicated Tk/ttk import hub
from gui.G01a_style_config import FRAME_PADDING

DEBUG_LAYOUT_HELPERS: bool = True   # Master debug toggle for this module
VERBOSE_LAYOUT_HELPERS: bool = False

def _debug(message: str, *, verbose: bool = False) -> None:
    """
    Controlled debug output for G01d_layout_helpers.

    Args:
        message: Debug message to log.
        verbose: If True, only logs when VERBOSE_LAYOUT_HELPERS is also True.
    """
    if not DEBUG_LAYOUT_HELPERS:
        return
    if verbose and not VERBOSE_LAYOUT_HELPERS:
        return
    logger.debug("[G01d] %s", message)


# ====================================================================================================
# 3. CORE LAYOUT HELPERS (FREE FUNCTIONS)
# ----------------------------------------------------------------------------------------------------
# These functions operate purely on Tk/ttk widgets and containers. They are layout-only and
# do not create widgets themselves. G01b_widget_primitives is responsible for widget creation.
# ====================================================================================================

def merge_geometry_kwargs(widget: Any, overrides: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge a widget's geometry_kwargs (if present) with explicit overrides.

    Priority:
        1. geometry_kwargs from the widget (created by widget primitives)
        2. overrides passed into this function

    Explicit overrides always win. The merged dictionary is returned and NOT stored back on
    the widget, so geometry_kwargs remain available for reuse if the caller wants.
    """
    base_geom: Dict[str, Any] = {}

    geom = getattr(widget, "geometry_kwargs", None)
    if isinstance(geom, dict):
        base_geom.update(geom)

    base_geom.update(overrides)
    return base_geom


def safe_grid(widget: Any, **grid_kwargs: Any) -> None:
    """
    Safely call widget.grid(...), merging any geometry_kwargs first.

    Typical usage:
        label = make_label(parent, text="Name", padx=(0, 8))
        entry = make_entry(parent)
        safe_grid(label, row=0, column=0, sticky="e")
        safe_grid(entry, row=0, column=1, sticky="we")

    This keeps layout explicit while still respecting geometry hints attached at creation time.
    """
    final_kwargs = merge_geometry_kwargs(widget, grid_kwargs)
    _debug(f"safe_grid: widget={widget!r}, final_kwargs={final_kwargs}", verbose=True)
    widget.grid(**final_kwargs)


def safe_pack(widget: Any, **pack_kwargs: Any) -> None:
    """
    Safely call widget.pack(...), merging any geometry_kwargs first.

    Typical usage:
        button = make_button(parent, text=\"Run\", pady=(8, 4))
        safe_pack(button, side=\"right\")

    This mirrors safe_grid but for pack geometry.
    """
    final_kwargs = merge_geometry_kwargs(widget, pack_kwargs)
    _debug(f"safe_pack: widget={widget!r}, final_kwargs={final_kwargs}", verbose=True)
    widget.pack(**final_kwargs)


def ensure_row_weights(
    container: tk.Misc,  # type: ignore[name-defined]
    rows: Iterable[int],
    *,
    weights: Optional[Sequence[int]] = None,
    minsize: Optional[int] = None,
) -> None:
    """
    Ensure that one or more rows on a container have grid weights configured.

    Args:
        container: Any widget supporting grid rowconfigure.
        rows: Iterable of row indices to configure.
        weights: Optional sequence of weights; if None, all rows get weight=1.
        minsize: Optional minimum row height applied to all rows.

    Examples:
        ensure_row_weights(frame, [0, 1, 2])                       # all weight=1
        ensure_row_weights(frame, [0, 1], weights=[2, 1])          # row 0 > row 1
    """
    rows_list = list(rows)
    if not rows_list:
        return

    if weights is None:
        weights = [1] * len(rows_list)
    elif len(weights) != len(rows_list):
        raise ValueError("Length of weights must match number of rows.")

    for idx, r in enumerate(rows_list):
        kw: Dict[str, Any] = {"weight": int(weights[idx])}
        if minsize is not None:
            kw["minsize"] = int(minsize)
        _debug(f"ensure_row_weights: row={r}, cfg={kw}", verbose=True)
        container.rowconfigure(r, **kw)


def ensure_column_weights(
    container: tk.Misc,  # type: ignore[name-defined]
    columns: Iterable[int],
    *,
    weights: Optional[Sequence[int]] = None,
    minsize: Optional[int] = None,
) -> None:
    """
    Ensure that one or more columns on a container have grid weights configured.

    Args:
        container: Any widget supporting grid columnconfigure.
        columns: Iterable of column indices to configure.
        weights: Optional sequence of weights; if None, all columns get weight=1.
        minsize: Optional minimum column width applied to all columns.

    Examples:
        ensure_column_weights(frame, [0, 1])                   # equal stretch
        ensure_column_weights(frame, [0, 1], weights=[1, 3])   # col 1 stretches more
    """
    cols_list = list(columns)
    if not cols_list:
        return

    if weights is None:
        weights = [1] * len(cols_list)
    elif len(weights) != len(cols_list):
        raise ValueError("Length of weights must match number of columns.")

    for idx, c in enumerate(cols_list):
        kw: Dict[str, Any] = {"weight": int(weights[idx])}
        if minsize is not None:
            kw["minsize"] = int(minsize)
        _debug(f"ensure_column_weights: column={c}, cfg={kw}", verbose=True)
        container.columnconfigure(c, **kw)


def grid_form_row(
    parent: tk.Misc,  # type: ignore[name-defined]
    row: int,
    label_widget: Any,
    field_widget: Any,
    *,
    label_column: int = 0,
    field_column: int = 1,
    label_sticky: str = "e",
    field_sticky: str = "we",
    label_padx: tuple[int, int] = (0, FRAME_PADDING),
    common_pady: tuple[int, int] = (2, 2),
) -> None:
    """
    Standardised 2-column form row:

        [ Label        ] [ Field......................... ]

    Assumes that label_widget and field_widget have already been created and that the
    parent will be grid-managed. Geometry hints attached via geometry_kwargs are merged
    with the parameters here before calling grid on each widget.

    Args:
        parent: Container using grid geometry.
        row: Grid row index for this form row.
        label_widget: Pre-created label widget.
        field_widget: Pre-created input widget (Entry, Combobox, etc.).
        label_column: Column index for the label (default 0).
        field_column: Column index for the field (default 1).
        label_sticky: Sticky for label (default "e" – east/right-align).
        field_sticky: Sticky for field (default "we" – expand horizontally).
        label_padx: Horizontal padding for the label.
        common_pady: Vertical padding applied to both widgets.
    """
    _debug(
        f"grid_form_row: row={row}, label_col={label_column}, field_col={field_column}",
        verbose=True,
    )

    # Ensure the field column stretches by default.
    ensure_column_weights(parent, [field_column])

    safe_grid(
        label_widget,
        row=row,
        column=label_column,
        sticky=label_sticky,
        padx=label_padx,
        pady=common_pady,
    )

    safe_grid(
        field_widget,
        row=row,
        column=field_column,
        sticky=field_sticky,
        pady=common_pady,
    )


# ====================================================================================================
# 4. ATTACH HELPERS TO A UI FACTORY CLASS (OPTIONAL)
# ----------------------------------------------------------------------------------------------------
# This function monkey-patches methods onto a UI factory / helper class WITHOUT importing it here.
# Call this once from your UI module after the class is defined:
#
#   from gui.G01d_layout_helpers import attach_layout_helpers
#   attach_layout_helpers(UIPrimitives)   # or whatever your factory class is called
#
# After that, any instance gains:
#   ui.safe_grid(widget, **kwargs)
#   ui.safe_pack(widget, **kwargs)
#   ui.ensure_row_weights(container, rows, ...)
#   ui.ensure_column_weights(container, columns, ...)
#   ui.grid_form_row(parent, row, label_widget, field_widget, ...)
# ====================================================================================================


def attach_layout_helpers(ui_class: Type[Any]) -> None:
    """
    Attach layout helper methods to ui_class (monkey-patching).

    This DOES NOT create instances. It only adds methods to the class so that
    its instances can call these helpers as instance methods.
    """
    _debug(f"attach_layout_helpers: Attaching layout helpers to {ui_class.__name__}.")

    # -----------------------------------------------------------------------------------------------
    def ui_safe_grid(self, widget: Any, **grid_kwargs: Any) -> None:
        _debug(f"{ui_class.__name__}.safe_grid: widget={widget!r}, kwargs={grid_kwargs}", verbose=True)
        safe_grid(widget, **grid_kwargs)

    def ui_safe_pack(self, widget: Any, **pack_kwargs: Any) -> None:
        _debug(f"{ui_class.__name__}.safe_pack: widget={widget!r}, kwargs={pack_kwargs}", verbose=True)
        safe_pack(widget, **pack_kwargs)

    def ui_ensure_row_weights(
        self,
        container: tk.Misc,  # type: ignore[name-defined]
        rows: Iterable[int],
        *,
        weights: Optional[Sequence[int]] = None,
        minsize: Optional[int] = None,
    ) -> None:
        _debug(
            f"{ui_class.__name__}.ensure_row_weights: rows={list(rows)}, "
            f"weights={weights}, minsize={minsize}",
            verbose=True,
        )
        ensure_row_weights(container, rows, weights=weights, minsize=minsize)

    def ui_ensure_column_weights(
        self,
        container: tk.Misc,  # type: ignore[name-defined]
        columns: Iterable[int],
        *,
        weights: Optional[Sequence[int]] = None,
        minsize: Optional[int] = None,
    ) -> None:
        _debug(
            f"{ui_class.__name__}.ensure_column_weights: cols={list(columns)}, "
            f"weights={weights}, minsize={minsize}",
            verbose=True,
        )
        ensure_column_weights(container, columns, weights=weights, minsize=minsize)

    def ui_grid_form_row(
        self,
        parent: tk.Misc,  # type: ignore[name-defined]
        row: int,
        label_widget: Any,
        field_widget: Any,
        *,
        label_column: int = 0,
        field_column: int = 1,
        label_sticky: str = "e",
        field_sticky: str = "we",
        label_padx: tuple[int, int] = (0, FRAME_PADDING),
        common_pady: tuple[int, int] = (2, 2),
    ) -> None:
        _debug(
            f"{ui_class.__name__}.grid_form_row: row={row}, label_col={label_column}, "
            f"field_col={field_column}",
            verbose=True,
        )
        grid_form_row(
            parent,
            row,
            label_widget,
            field_widget,
            label_column=label_column,
            field_column=field_column,
            label_sticky=label_sticky,
            field_sticky=field_sticky,
            label_padx=label_padx,
            common_pady=common_pady,
        )

    # Attach methods to the class
    ui_class.safe_grid = ui_safe_grid                    # type: ignore[attr-defined]
    ui_class.safe_pack = ui_safe_pack                    # type: ignore[attr-defined]
    ui_class.ensure_row_weights = ui_ensure_row_weights  # type: ignore[attr-defined]
    ui_class.ensure_column_weights = ui_ensure_column_weights  # type: ignore[attr-defined]
    ui_class.grid_form_row = ui_grid_form_row            # type: ignore[attr-defined]

    _debug("attach_layout_helpers: Layout helpers attached successfully.")


# ====================================================================================================
# 5. SELF-TEST / SANDBOX (RUN ONLY WHEN EXECUTING THIS FILE DIRECTLY)
# ----------------------------------------------------------------------------------------------------
def run_self_test() -> None:
    """
    Run a small visual sandbox to verify the layout helpers.

    This is developer-only and is never called by production code.
    """
    logger.info("=== G01d_layout_helpers.py — Self-Test Start ===")

    # Local imports to avoid hard dependencies for normal use
    from gui.G01a_style_config import GUI_COLOUR_BG_PRIMARY  # type: ignore
    from gui.G01b_style_engine import configure_ttk_styles   # type: ignore
    from gui.G01c_widget_primitives import (                 # type: ignore
        make_heading,
        make_label,
        make_entry,
        make_combobox,
        make_spacer,
    )

    root = tk.Tk()
    root.title("G01d Layout Helpers Sandbox")
    root.geometry("800x480")
    root.configure(bg=GUI_COLOUR_BG_PRIMARY)

    style = ttk.Style(root)
    configure_ttk_styles(style)  # apply project theme

    outer = ttk.Frame(root, style="TFrame", padding=FRAME_PADDING)
    outer.pack(fill="both", expand=True)

    heading = make_heading(outer, "G01d Layout Helpers Demo")
    safe_pack(heading, anchor="w", pady=(0, 10))

    form_frame = ttk.Frame(outer, style="TFrame")
    form_frame.pack(fill="x")

    # Two rows, standard label + field layout
    name_label = make_label(form_frame, "Name:")
    name_entry = make_entry(form_frame, width=30)
    grid_form_row(form_frame, 0, name_label, name_entry)

    cat_label = make_label(form_frame, "Category:")
    cat_combo = make_combobox(form_frame, values=["A", "B", "C"], state="readonly", width=28)
    grid_form_row(form_frame, 1, cat_label, cat_combo)

    make_spacer(outer, height=16).pack(fill="x")

    info = make_label(
        outer,
        "Helpers: safe_grid, safe_pack, ensure_row_weights, "
        "ensure_column_weights, grid_form_row.",
    )
    safe_pack(info, anchor="w", pady=(8, 0))

    logger.info("=== G01d_layout_helpers.py — Self-Test Ready ===")
    root.mainloop()
    logger.info("=== G01d_layout_helpers.py — Self-Test End ===")


if __name__ == "__main__":
    run_self_test()
