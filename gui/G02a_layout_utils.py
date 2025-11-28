# ====================================================================================================
# G02a_layout_utils.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Comprehensive layout utilities for all GUI modules.
#
#   This module provides THREE categories of layout functionality:
#
#   1. GEOMETRY HELPERS (low-level grid/pack wrappers):
#       • safe_grid(widget, **kwargs)       – Grid with geometry_kwargs merge
#       • safe_pack(widget, **kwargs)       – Pack with geometry_kwargs merge
#       • auto_pack(widget, **kwargs)       – Pack using G01d default padding
#       • place_centered(widget, **kwargs)  – Center widget in parent
#
#   2. GRID CONFIGURATION (row/column weight management):
#       • configure_grid(container, rows, cols, weights)
#       • ensure_row_weights(container, rows, weights)
#       • ensure_column_weights(container, cols, weights)
#       • equal_columns(container, count)   – Quick equal-width columns
#       • weighted_columns(container, weights)  – Percentage-based columns
#
#   3. LAYOUT PATTERNS (multi-frame composition):
#       • grid_form_row(...)                – Label + Field form row
#       • grid_form(parent, fields)         – Build entire form from list
#       • centered_content(parent, widget)  – Centered single widget
#       • header_body_footer(parent)        – 3-part vertical layout (returns dataclass)
#       • sidebar_content(parent, sidebar_width)  – Sidebar + main area (returns dataclass)
#
#   4. SPACING PRESETS (from G01a design tokens):
#       • SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL
#       • PAD_NONE, PAD_TIGHT, PAD_NORMAL, PAD_LOOSE
#       • get_default_padding(widget)       – Read G01d metadata
#
#   NOTE: Container widget factories (make_button_bar, make_horizontal_group, etc.)
#   have been moved to G01c_widget_primitives where they belong.
#
# Architectural Role:
#   - Sits in G02 layer (patterns built on G01 primitives)
#   - Pure layout logic – NO widget creation (use G01c for that)
#   - Consumes spacing tokens from G01a_style_config
#   - Can read G01d metadata for smart defaults
#
# Integration:
#   from gui.G02a_layout_utils import (
#       safe_grid, safe_pack, auto_pack,
#       configure_grid, equal_columns, weighted_columns,
#       grid_form_row, grid_form, header_body_footer, sidebar_content,
#       SPACING_MD, PAD_NORMAL,
#   )
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-23
# Updated:      2025-11-28 (v2 - Comprehensive layout system)
# Project:      Core Boilerplate v1.0
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ====================================================================================================
from __future__ import annotations

import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

if "" in sys.path:
    sys.path.remove("")

sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ====================================================================================================
from core.C00_set_packages import *

from core.C03_logging_handler import get_logger, init_logging
logger = get_logger(__name__)

from gui.G00a_gui_packages import tk, ttk
from gui.G01a_style_config import (
    FRAME_PADDING,
    SECTION_SPACING,
    SECTION_TITLE_SPACING,
    LABEL_ENTRY_SPACING,
    BUTTON_SPACING,
    LAYOUT_COLUMN_GAP,
    LAYOUT_ROW_GAP,
)


# ====================================================================================================
# 3. MODULE CONFIGURATION
# ====================================================================================================
DEBUG_LAYOUT: bool = False
VERBOSE_LAYOUT: bool = False


def debug(message: str, *, verbose: bool = False) -> None:
    """Controlled debug output."""
    if not DEBUG_LAYOUT:
        return
    if verbose and not VERBOSE_LAYOUT:
        return
    logger.debug("[G02a] %s", message)


# ====================================================================================================
# 4. SPACING PRESETS (derived from G01a design tokens)
# ----------------------------------------------------------------------------------------------------
# Standardised spacing values for consistent layouts.
# ====================================================================================================

# Absolute spacing values (pixels)
SPACING_XS: int = 2
SPACING_SM: int = 4
SPACING_MD: int = 8
SPACING_LG: int = 12
SPACING_XL: int = 16
SPACING_XXL: int = 24

# Padding presets as (x, y) tuples
PAD_NONE: tuple[int, int] = (0, 0)
PAD_TIGHT: tuple[int, int] = (SPACING_SM, SPACING_SM)
PAD_NORMAL: tuple[int, int] = (SPACING_MD, SPACING_MD)
PAD_LOOSE: tuple[int, int] = (SPACING_LG, SPACING_LG)
PAD_SPACIOUS: tuple[int, int] = (SPACING_XL, SPACING_XL)

# Common padding patterns
PAD_FORM_LABEL: tuple[int, int] = (0, LABEL_ENTRY_SPACING)
PAD_FORM_FIELD: tuple[int, int] = (0, 0)
PAD_BUTTON_ROW: tuple[int, int] = (BUTTON_SPACING, SPACING_MD)
PAD_SECTION: tuple[int, int] = (0, SECTION_SPACING)
PAD_TITLE: tuple[int, int] = (0, SECTION_TITLE_SPACING)


# ====================================================================================================
# 5. GEOMETRY HELPERS (low-level grid/pack wrappers)
# ====================================================================================================

def merge_geometry_kwargs(widget: Any, overrides: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge widget's geometry_kwargs with explicit overrides.

    Priority: overrides > geometry_kwargs

    Args:
        widget: Widget possibly having .geometry_kwargs attribute.
        overrides: Explicit kwargs to merge in.

    Returns:
        Merged dictionary ready for grid/pack.
    """
    base: Dict[str, Any] = {}

    # Get geometry_kwargs from G01c primitives
    geom = getattr(widget, "geometry_kwargs", None)
    if isinstance(geom, dict):
        base.update(geom)

    base.update(overrides)
    return base


def safe_grid(widget: Any, **kwargs: Any) -> None:
    """
    Call widget.grid() with merged geometry_kwargs.

    Args:
        widget: Widget to grid.
        **kwargs: Grid options (row, column, sticky, padx, pady, etc.)

    Example:
        safe_grid(label, row=0, column=0, sticky="e")
    """
    final = merge_geometry_kwargs(widget, kwargs)
    debug(f"safe_grid: {widget}, {final}", verbose=True)
    widget.grid(**final)


def safe_pack(widget: Any, **kwargs: Any) -> None:
    """
    Call widget.pack() with merged geometry_kwargs.

    Args:
        widget: Widget to pack.
        **kwargs: Pack options (side, fill, expand, padx, pady, etc.)

    Example:
        safe_pack(button, side="right", padx=PAD_TIGHT)
    """
    final = merge_geometry_kwargs(widget, kwargs)
    debug(f"safe_pack: {widget}, {final}", verbose=True)
    widget.pack(**final)


def auto_pack(widget: Any, **kwargs: Any) -> None:
    """
    Pack widget using G01d default padding if available.

    If the widget has .g01d_default_pady metadata (from G01d primitives),
    it will be used as the default pady unless explicitly overridden.

    Args:
        widget: Widget to pack (preferably created by G01d).
        **kwargs: Pack options (overrides defaults).

    Example:
        title = page_title(frame, "Settings")
        auto_pack(title, anchor="w")  # Uses g01d_default_pady automatically
    """
    # Check for G01d default padding
    default_pady = getattr(widget, "g01d_default_pady", None)
    if default_pady is not None and "pady" not in kwargs:
        kwargs["pady"] = default_pady
        debug(f"auto_pack: Using g01d_default_pady={default_pady}")

    safe_pack(widget, **kwargs)


def place_centered(
    widget: Any,
    parent: tk.Widget | None = None,
    **kwargs: Any,
) -> None:
    """
    Center a widget in its parent using place geometry.

    Args:
        widget: Widget to center.
        parent: Parent widget (uses widget's parent if None).
        **kwargs: Additional place options.

    Example:
        place_centered(loading_spinner)
    """
    kwargs.setdefault("relx", 0.5)
    kwargs.setdefault("rely", 0.5)
    kwargs.setdefault("anchor", "center")

    debug(f"place_centered: {widget}, {kwargs}", verbose=True)
    widget.place(**kwargs)


# ====================================================================================================
# 6. GRID CONFIGURATION (row/column weight management)
# ====================================================================================================

def configure_grid(
    container: tk.Widget,
    rows: int,
    cols: int,
    *,
    row_weights: Sequence[int] | int | None = None,
    col_weights: Sequence[int] | int | None = None,
    row_minsize: int | None = None,
    col_minsize: int | None = None,
) -> None:
    """
    Configure grid rows and columns in one call.

    Args:
        container: Widget to configure.
        rows: Number of rows.
        cols: Number of columns.
        row_weights: Single weight for all rows, or sequence per row.
        col_weights: Single weight for all cols, or sequence per col.
        row_minsize: Minimum row height.
        col_minsize: Minimum column width.

    Examples:
        configure_grid(frame, 3, 2)  # 3 rows, 2 cols, all weight=1
        configure_grid(frame, 3, 2, row_weights=[0, 1, 0], col_weights=[1, 2])
    """
    debug(f"configure_grid: rows={rows}, cols={cols}")

    # Process row weights
    if row_weights is None:
        rw = [1] * rows
    elif isinstance(row_weights, int):
        rw = [row_weights] * rows
    else:
        rw = list(row_weights)
        if len(rw) != rows:
            raise ValueError(f"row_weights length ({len(rw)}) != rows ({rows})")

    # Process column weights
    if col_weights is None:
        cw = [1] * cols
    elif isinstance(col_weights, int):
        cw = [col_weights] * cols
    else:
        cw = list(col_weights)
        if len(cw) != cols:
            raise ValueError(f"col_weights length ({len(cw)}) != cols ({cols})")

    # Apply row configuration
    for i, w in enumerate(rw):
        cfg: Dict[str, Any] = {"weight": w}
        if row_minsize is not None:
            cfg["minsize"] = row_minsize
        container.rowconfigure(i, **cfg)

    # Apply column configuration
    for i, w in enumerate(cw):
        cfg = {"weight": w}
        if col_minsize is not None:
            cfg["minsize"] = col_minsize
        container.columnconfigure(i, **cfg)


def ensure_row_weights(
    container: tk.Widget,
    rows: Iterable[int],
    *,
    weights: Sequence[int] | None = None,
    minsize: int | None = None,
) -> None:
    """
    Configure weights for specific rows.

    Args:
        container: Widget to configure.
        rows: Row indices to configure.
        weights: Weight per row (default all 1).
        minsize: Minimum row height.

    Example:
        ensure_row_weights(frame, [0, 1, 2], weights=[0, 1, 0])
    """
    rows_list = list(rows)
    if not rows_list:
        return

    if weights is None:
        weights = [1] * len(rows_list)
    elif len(weights) != len(rows_list):
        raise ValueError("weights length must match rows length")

    for idx, r in enumerate(rows_list):
        cfg: Dict[str, Any] = {"weight": weights[idx]}
        if minsize is not None:
            cfg["minsize"] = minsize
        container.rowconfigure(r, **cfg)


def ensure_column_weights(
    container: tk.Widget,
    columns: Iterable[int],
    *,
    weights: Sequence[int] | None = None,
    minsize: int | None = None,
) -> None:
    """
    Configure weights for specific columns.

    Args:
        container: Widget to configure.
        columns: Column indices to configure.
        weights: Weight per column (default all 1).
        minsize: Minimum column width.

    Example:
        ensure_column_weights(frame, [0, 1], weights=[1, 3])
    """
    cols_list = list(columns)
    if not cols_list:
        return

    if weights is None:
        weights = [1] * len(cols_list)
    elif len(weights) != len(cols_list):
        raise ValueError("weights length must match columns length")

    for idx, c in enumerate(cols_list):
        cfg: Dict[str, Any] = {"weight": weights[idx]}
        if minsize is not None:
            cfg["minsize"] = minsize
        container.columnconfigure(c, **cfg)


def equal_columns(container: tk.Widget, count: int, *, minsize: int | None = None) -> None:
    """
    Configure N equal-width columns.

    Args:
        container: Widget to configure.
        count: Number of columns.
        minsize: Minimum column width.

    Example:
        equal_columns(frame, 4)  # 4 equal columns
    """
    ensure_column_weights(container, range(count), minsize=minsize)


def weighted_columns(
    container: tk.Widget,
    weights: Sequence[int],
    *,
    minsize: int | None = None,
) -> None:
    """
    Configure columns with percentage-like weights.

    Args:
        container: Widget to configure.
        weights: Weight for each column (e.g., [30, 70] for 30%/70%).
        minsize: Minimum column width.

    Example:
        weighted_columns(frame, [30, 70])  # Left 30%, right 70%
        weighted_columns(frame, [1, 2, 1])  # 25%, 50%, 25%
    """
    ensure_column_weights(container, range(len(weights)), weights=weights, minsize=minsize)


def equal_rows(container: tk.Widget, count: int, *, minsize: int | None = None) -> None:
    """
    Configure N equal-height rows.

    Args:
        container: Widget to configure.
        count: Number of rows.
        minsize: Minimum row height.

    Example:
        equal_rows(frame, 3)  # 3 equal rows
    """
    ensure_row_weights(container, range(count), minsize=minsize)


# ====================================================================================================
# 7. LAYOUT PATTERNS (common arrangement recipes)
# ====================================================================================================

def grid_form_row(
    parent: tk.Widget,
    row: int,
    label_widget: Any,
    field_widget: Any,
    *,
    label_column: int = 0,
    field_column: int = 1,
    label_sticky: str = "e",
    field_sticky: str = "we",
    label_padx: tuple[int, int] = (0, LABEL_ENTRY_SPACING),
    pady: tuple[int, int] = (SPACING_XS, SPACING_XS),
) -> None:
    """
    Standard 2-column form row: [Label] [Field]

    Args:
        parent: Container using grid.
        row: Grid row index.
        label_widget: Pre-created label.
        field_widget: Pre-created input widget.
        label_column: Column for label (default 0).
        field_column: Column for field (default 1).
        label_sticky: Label alignment (default "e" = right).
        field_sticky: Field alignment (default "we" = expand).
        label_padx: Label horizontal padding.
        pady: Vertical padding for both.

    Example:
        grid_form_row(form, 0, name_label, name_entry)
        grid_form_row(form, 1, email_label, email_entry)
    """
    debug(f"grid_form_row: row={row}")

    # Ensure field column stretches
    ensure_column_weights(parent, [field_column])

    safe_grid(label_widget, row=row, column=label_column, sticky=label_sticky, padx=label_padx, pady=pady)
    safe_grid(field_widget, row=row, column=field_column, sticky=field_sticky, pady=pady)


def grid_form(
    parent: tk.Widget,
    fields: list[tuple[Any, Any]],
    *,
    start_row: int = 0,
    **kwargs: Any,
) -> int:
    """
    Build multiple form rows from a list of (label, field) tuples.

    Args:
        parent: Container using grid.
        fields: List of (label_widget, field_widget) tuples.
        start_row: Starting row index.
        **kwargs: Passed to grid_form_row.

    Returns:
        Next available row index.

    Example:
        next_row = grid_form(form, [
            (name_label, name_entry),
            (email_label, email_entry),
            (phone_label, phone_entry),
        ])
    """
    for i, (label, field) in enumerate(fields):
        grid_form_row(parent, start_row + i, label, field, **kwargs)

    return start_row + len(fields)


def horizontal_group(
    parent: tk.Widget,
    widgets: list[Any] | None = None,
    *,
    gap: int = SPACING_MD,
    anchor: str = "w",
    expand_last: bool = False,
) -> ttk.Frame:
    """
    DEPRECATED: Use make_horizontal_group() from G01c_widget_primitives instead.

    This function is retained for backwards compatibility but simply returns
    an empty frame. Create widgets as children of the container manually.

    Example (new pattern):
        from gui.G01c_widget_primitives import make_horizontal_group, make_label

        row = make_horizontal_group(parent)
        make_label(row, "Status:", category="Body", weight="Bold").pack(side="left")
        make_label(row, "Connected", category="Body").pack(side="left", padx=(4, 0))
        row.pack(anchor="w")
    """
    import warnings
    warnings.warn(
        "horizontal_group() is deprecated. Use make_horizontal_group() from G01c_widget_primitives.",
        DeprecationWarning,
        stacklevel=2,
    )
    container = ttk.Frame(parent, style="TFrame")
    container.g02a_role = "horizontal_group"  # type: ignore[attr-defined]
    return container


def vertical_group(
    parent: tk.Widget,
    widgets: list[Any] | None = None,
    *,
    gap: int = SPACING_SM,
    anchor: str = "w",
    expand_last: bool = False,
) -> ttk.Frame:
    """
    DEPRECATED: Use make_vertical_group() from G01c_widget_primitives instead.

    This function is retained for backwards compatibility but simply returns
    an empty frame. Create widgets as children of the container manually.

    Example (new pattern):
        from gui.G01c_widget_primitives import make_vertical_group, make_label

        col = make_vertical_group(parent)
        make_label(col, "Item 1", category="Body").pack(anchor="w")
        make_label(col, "Item 2", category="Body").pack(anchor="w", pady=(4, 0))
        col.pack(fill="y")
    """
    import warnings
    warnings.warn(
        "vertical_group() is deprecated. Use make_vertical_group() from G01c_widget_primitives.",
        DeprecationWarning,
        stacklevel=2,
    )
    container = ttk.Frame(parent, style="TFrame")
    container.g02a_role = "vertical_group"  # type: ignore[attr-defined]
    return container


def button_bar(
    parent: tk.Widget,
    buttons: list[Any] | None = None,
    *,
    gap: int = BUTTON_SPACING,
    align: str = "right",
    pady: tuple[int, int] = PAD_BUTTON_ROW,
) -> ttk.Frame:
    """
    DEPRECATED: Use make_button_bar() from G01c_widget_primitives instead.

    This function is retained for backwards compatibility but simply returns
    an empty frame. Create buttons as children of the container manually.

    Example (new pattern):
        from gui.G01c_widget_primitives import make_button_bar, make_button

        bar = make_button_bar(parent)
        make_button(bar, "Cancel", style="Secondary.TButton").pack(side="right")
        make_button(bar, "Save").pack(side="right", padx=(8, 0))
        bar.pack(fill="x", side="bottom")
    """
    import warnings
    warnings.warn(
        "button_bar() is deprecated. Use make_button_bar() from G01c_widget_primitives.",
        DeprecationWarning,
        stacklevel=2,
    )
    container = ttk.Frame(parent, style="TFrame")
    container.g02a_role = "button_bar"  # type: ignore[attr-defined]
    return container


def centered_content(parent: tk.Widget, widget: Any) -> ttk.Frame:
    """
    Center a widget both horizontally and vertically.

    Args:
        parent: Parent widget.
        widget: Widget to center.

    Returns:
        Frame containing the centered widget.

    Example:
        centered = centered_content(frame, loading_label)
        centered.pack(fill="both", expand=True)
    """
    container = ttk.Frame(parent, style="TFrame")

    # Use grid for true centering
    container.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)

    widget.grid(in_=container, row=0, column=0)

    container.g02a_role = "centered_content"  # type: ignore[attr-defined]
    return container


@dataclass
class HeaderBodyFooter:
    """Container for header-body-footer layout parts."""
    container: ttk.Frame
    header: ttk.Frame
    body: ttk.Frame
    footer: ttk.Frame


def header_body_footer(
    parent: tk.Widget,
    *,
    header_height: int | None = None,
    footer_height: int | None = None,
) -> HeaderBodyFooter:
    """
    Create a 3-part vertical layout: header, body (expanding), footer.

    Args:
        parent: Parent widget.
        header_height: Fixed header height (None = auto).
        footer_height: Fixed footer height (None = auto).

    Returns:
        HeaderBodyFooter dataclass with container, header, body, footer frames.

    Example:
        layout = header_body_footer(frame)
        page_title(layout.header, "Settings").pack()
        # ... add content to layout.body ...
        button_bar(layout.footer, [save_btn]).pack(fill="x")
    """
    container = ttk.Frame(parent, style="TFrame")

    # Configure rows: header (0), body (1, expanding), footer (2)
    container.rowconfigure(0, weight=0)
    container.rowconfigure(1, weight=1)
    container.rowconfigure(2, weight=0)
    container.columnconfigure(0, weight=1)

    header = ttk.Frame(container, style="TFrame")
    if header_height:
        header.configure(height=header_height)
    header.grid(row=0, column=0, sticky="ew")

    body = ttk.Frame(container, style="TFrame")
    body.grid(row=1, column=0, sticky="nsew")

    footer = ttk.Frame(container, style="TFrame")
    if footer_height:
        footer.configure(height=footer_height)
    footer.grid(row=2, column=0, sticky="ew")

    container.g02a_role = "header_body_footer"  # type: ignore[attr-defined]

    return HeaderBodyFooter(container=container, header=header, body=body, footer=footer)


@dataclass
class SidebarContent:
    """Container for sidebar-content layout parts."""
    container: ttk.Frame
    sidebar: ttk.Frame
    content: ttk.Frame


def sidebar_content(
    parent: tk.Widget,
    *,
    sidebar_width: int = 200,
    sidebar_side: str = "left",
) -> SidebarContent:
    """
    Create a 2-part horizontal layout: sidebar + main content.

    Args:
        parent: Parent widget.
        sidebar_width: Fixed sidebar width in pixels.
        sidebar_side: "left" or "right".

    Returns:
        SidebarContent dataclass with container, sidebar, content frames.

    Example:
        layout = sidebar_content(frame, sidebar_width=250)
        # Add navigation to layout.sidebar
        # Add main content to layout.content
    """
    container = ttk.Frame(parent, style="TFrame")

    sidebar = ttk.Frame(container, style="SectionBody.TFrame", width=sidebar_width)
    sidebar.pack_propagate(False)  # Maintain fixed width

    content = ttk.Frame(container, style="TFrame")

    if sidebar_side == "left":
        sidebar.pack(side="left", fill="y")
        content.pack(side="left", fill="both", expand=True)
    else:
        content.pack(side="left", fill="both", expand=True)
        sidebar.pack(side="right", fill="y")

    container.g02a_role = "sidebar_content"  # type: ignore[attr-defined]

    return SidebarContent(container=container, sidebar=sidebar, content=content)


# ====================================================================================================
# 8. UTILITY HELPERS
# ====================================================================================================

def get_default_padding(widget: Any) -> tuple[int, int] | None:
    """
    Get default vertical padding from G01d widget metadata.

    Args:
        widget: Widget to check.

    Returns:
        (top, bottom) padding tuple or None.
    """
    return getattr(widget, "g01d_default_pady", None)


def clear_children(container: tk.Widget) -> None:
    """
    Destroy all child widgets of a container.

    Args:
        container: Widget to clear.
    """
    for child in container.winfo_children():
        child.destroy()


def get_layout_role(widget: Any) -> str | None:
    """
    Get the layout role from a G02a-created container.

    Args:
        widget: Widget to check.

    Returns:
        Role string or None.
    """
    return getattr(widget, "g02a_role", None)


# ====================================================================================================
# 9. ATTACH HELPERS TO UI CLASS (OPTIONAL)
# ====================================================================================================

def attach_layout_helpers(ui_class: Type[Any]) -> None:
    """
    Monkey-patch layout methods onto a UI class.

    After calling this, instances of ui_class will have:
        - ui.safe_grid(widget, **kwargs)
        - ui.safe_pack(widget, **kwargs)
        - ui.auto_pack(widget, **kwargs)
        - ui.grid_form_row(...)
        - ui.button_bar(...)
        - etc.

    Args:
        ui_class: Class to patch.
    """
    debug(f"attach_layout_helpers: Patching {ui_class.__name__}")

    # Grid/pack helpers
    ui_class.safe_grid = lambda self, w, **kw: safe_grid(w, **kw)
    ui_class.safe_pack = lambda self, w, **kw: safe_pack(w, **kw)
    ui_class.auto_pack = lambda self, w, **kw: auto_pack(w, **kw)

    # Grid configuration
    ui_class.configure_grid = lambda self, c, r, cols, **kw: configure_grid(c, r, cols, **kw)
    ui_class.equal_columns = lambda self, c, n, **kw: equal_columns(c, n, **kw)
    ui_class.weighted_columns = lambda self, c, w, **kw: weighted_columns(c, w, **kw)

    # Layout patterns
    ui_class.grid_form_row = lambda self, p, r, l, f, **kw: grid_form_row(p, r, l, f, **kw)
    ui_class.grid_form = lambda self, p, fields, **kw: grid_form(p, fields, **kw)
    ui_class.horizontal_group = lambda self, p, w, **kw: horizontal_group(p, w, **kw)
    ui_class.vertical_group = lambda self, p, w, **kw: vertical_group(p, w, **kw)
    ui_class.button_bar = lambda self, p, b, **kw: button_bar(p, b, **kw)

    debug("attach_layout_helpers: Complete")


# ====================================================================================================
# 10. SELF-TEST
# ====================================================================================================
def run_self_test() -> None:
    """Visual demo of G02a layout utilities."""
    init_logging()
    logger.info("=== G02a_layout_utils v2 — Self-Test Start ===")

    from gui.G01a_style_config import GUI_COLOUR_BG_PRIMARY
    from gui.G01b_style_engine import configure_ttk_styles
    from gui.G01c_widget_primitives import (
        make_label,
        make_entry,
        make_button,
        make_button_bar,
        make_horizontal_group,
    )
    from gui.G01d_layout_primitives import page_title, section_title, body_text

    root = tk.Tk()
    root.title("G02a Layout Utils v2 — Demo")
    root.geometry("900x600")
    root.configure(bg=GUI_COLOUR_BG_PRIMARY)

    style = ttk.Style(root)
    configure_ttk_styles(style)

    # Use header-body-footer layout
    layout = header_body_footer(root)
    layout.container.pack(fill="both", expand=True, padx=SPACING_LG, pady=SPACING_LG)

    # Header
    title = page_title(layout.header, "G02a Layout Utils v2 — Demo")
    auto_pack(title, anchor="w")

    # Body with sidebar
    body_layout = sidebar_content(layout.body, sidebar_width=200)
    body_layout.container.pack(fill="both", expand=True, pady=(SPACING_MD, 0))

    # Sidebar
    section_title(body_layout.sidebar, "Navigation", surface="Secondary").pack(anchor="w", padx=SPACING_MD, pady=SPACING_MD)
    for item in ["Dashboard", "Settings", "Users", "Reports"]:
        make_label(body_layout.sidebar, f"  {item}", category="Body", surface="Secondary").pack(anchor="w", padx=SPACING_MD, pady=SPACING_XS)

    # Main content
    content_frame = ttk.Frame(body_layout.content, padding=SPACING_MD, style="TFrame")
    content_frame.pack(fill="both", expand=True)

    section_title(content_frame, "Form Layout Demo").pack(anchor="w", pady=(0, SPACING_SM))

    form = ttk.Frame(content_frame, style="TFrame")
    form.pack(fill="x", pady=(0, SPACING_MD))

    # Build form
    fields = [
        (make_label(form, "Name:", category="Body"), make_entry(form, width=30)),
        (make_label(form, "Email:", category="Body"), make_entry(form, width=30)),
        (make_label(form, "Department:", category="Body"), make_entry(form, width=30)),
    ]
    grid_form(form, fields)

    # Button bar demo - using G01c make_button_bar
    section_title(content_frame, "Button Bar Demo").pack(anchor="w", pady=(SPACING_MD, SPACING_SM))

    # NEW PATTERN: Create container first, then create children inside it
    bar = make_button_bar(content_frame)
    make_button(bar, "Cancel", style="Secondary.TButton").pack(side="right")
    make_button(bar, "Save").pack(side="right", padx=(SPACING_MD, 0))
    bar.pack(fill="x")

    # Horizontal group demo - using G01c make_horizontal_group
    section_title(content_frame, "Group Demos").pack(anchor="w", pady=(SPACING_MD, SPACING_SM))

    # NEW PATTERN: Create container first, then create children inside it
    h_group = make_horizontal_group(content_frame)
    make_label(h_group, "Status:", category="Body", weight="Bold").pack(side="left")
    make_label(h_group, "Connected", category="Body").pack(side="left", padx=(SPACING_SM, 0))
    h_group.pack(anchor="w", pady=SPACING_XS)

    # Footer
    body_text(layout.footer, "G02a Layout Utils v2 — Spacing presets, layout patterns, and smart defaults.").pack(anchor="w", pady=SPACING_SM)

    logger.info("=== G02a_layout_utils v2 — Self-Test Ready ===")
    root.mainloop()
    logger.info("=== G02a_layout_utils v2 — Self-Test End ===")


if __name__ == "__main__":
    run_self_test()