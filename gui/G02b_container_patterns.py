# ====================================================================================================
# G02b_container_patterns.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Provide a unified set of reusable *container layout patterns* built entirely from ttk.Frame
#   widgets. These patterns serve as foundational building blocks for all GUI view modules, allowing
#   developers to assemble clean, consistent, visually aligned interfaces without re-implementing
#   boilerplate “frame + heading + padding + border” logic.
#
#   This module abstracts layout composition, NOT business logic. A view module should simply call:
#
#       create_section_grid(...)     # Full-width, bordered section with optional heading
#       create_card_grid(...)        # Compact card-style container (single card)
#       create_card_row(...)         # Horizontal row of N cards (multi-card convenience)
#       create_two_column_body(...)  # 50/50 or weighted split inside a section/card
#
#   These building blocks ensure all views adhere to the same spacing, padding, heading style, and
#   grid structure defined by the GUI Boilerplate 00/01 layer.
#
# ----------------------------------------------------------------------------------------------------
# Key Patterns:
#   • create_section_grid(...)       → Heading label (optional) + bordered outer frame + content area
#   • create_card_grid(...)          → Compact version of a section, ideal for nested UI blocks
#   • create_card_row(...)           → Row of N cards (returns list[Container])
#   • create_two_column_body(...)    → Split an existing container body into left/right frames
#
# Visual Structure:
#       Parent
#         ├── [Heading Label]   (optional)
#         └── [Outer Frame]     (border, background, padding)
#               └── [Body Frame] (place all widgets here)
#
# Usage Example:
#       from gui.G02b_container_patterns import create_section_grid, create_card_row
#
#       section = create_section_grid(
#           parent=self.main_frame,
#           row=0,
#           column=0,
#           title="Connection Settings",
#       )
#
#       cards = create_card_row(
#           parent=self.main_frame,
#           row=2,
#           columns=4,
#           titles=["Card A", "Card B", "Card C", "Card D"],
#       )
#
#       ttk.Label(cards[0].body, text="Card A body").grid(row=0, column=0)
#
# Integration Notes:
#   • Pattern frames use style names defined in:
#         - G01b_style_engine      (ttk style definitions)
#         - G01a_style_config      (colour/spacing theme tokens)
#   • If those styles are not active, ttk simply falls back to default themes.
#   • Guaranteed safe: no BaseGUI dependency, no tkinter root creation, no side effects.
#   • 100% ttk-only — no ttkbootstrap assumptions.
#
# Architectural Rules:
#   • GUI container patterns MUST contain no business logic.
#   • No core imports except via core.C00_set_packages.
#   • No sys.path mutation beyond the standard Section 1 template.
#   • ZERO GUI side effects at import time.
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
from gui.G00a_gui_packages import tk, ttk, tkFont
from gui.G01a_style_config import *
from gui.G01c_widget_primitives import make_label, make_radio
from gui.G01d_layout_primitives import body_text


# ====================================================================================================
# 3. DATA CLASSES
# ----------------------------------------------------------------------------------------------------
@dataclass
class Container:
    """
    Description:
        Simple bundle of the widgets that make up a container pattern.

    Attributes:
        outer:   The outer frame providing border / background.
        body:    The inner content frame where widgets should be placed.
        heading: Optional heading label (may be None).
    """
    outer: ttk.Frame
    body: ttk.Frame
    heading: Optional[ttk.Label] = None


# ====================================================================================================
# 4. LOCAL LAYOUT CONSTANTS (derived from G01a where possible)
# ----------------------------------------------------------------------------------------------------
SECTION_HEADING_PADX: Tuple[int, int] = (4, 4)
SECTION_HEADING_PADY: Tuple[int, int] = (8, 2)

SECTION_OUTER_PADX: Tuple[int, int] = (0, 0)
SECTION_OUTER_PADY: Tuple[int, int] = (0, LAYOUT_ROW_GAP)

SECTION_BODY_PADX: Tuple[int, int] = (12, 12)
SECTION_BODY_PADY: Tuple[int, int] = (8, 12)

CARD_OUTER_PADX: Tuple[int, int] = (LAYOUT_CARD_GAP, LAYOUT_CARD_GAP)
CARD_OUTER_PADY: Tuple[int, int] = (LAYOUT_CARD_GAP, LAYOUT_CARD_GAP)

CARD_BODY_PADX: Tuple[int, int] = (LAYOUT_CARD_GAP, LAYOUT_CARD_GAP)
CARD_BODY_PADY: Tuple[int, int] = (LAYOUT_CARD_GAP, LAYOUT_CARD_GAP)

PAGE_HEADER_PADY: Tuple[int, int] = (0, LAYOUT_ROW_GAP)


# ====================================================================================================
# 5. INTERNAL HELPER — BORDERED CONTAINER
# ----------------------------------------------------------------------------------------------------
def create_bordered_container_grid(
    parent: ttk.Widget,
    *,
    row: int,
    column: int = 0,
    columnspan: int = 1,
    title: Optional[str] = None,
    sticky: str = "nsew",
    heading_style: str = "Primary.SectionHeading.Bold.TLabel",
    outer_style: str = "SectionOuter.TFrame",
    body_style: str = "SectionBody.TFrame",
    heading_padx: Tuple[int, int] = SECTION_HEADING_PADX,
    heading_pady: Tuple[int, int] = SECTION_HEADING_PADY,
    outer_padx: Tuple[int, int] = SECTION_OUTER_PADX,
    outer_pady: Tuple[int, int] = SECTION_OUTER_PADY,
    body_padx: Tuple[int, int] = SECTION_BODY_PADX,
    body_pady: Tuple[int, int] = SECTION_BODY_PADY,
) -> Container:
    """
    Description:
        Core implementation shared by section/card helpers. Creates on the parent grid:
            [ heading label ]     (optional, on parent)
            [ outer frame ]       (on parent)
              └─ [ body frame ]   (inside outer)

    Args:
        parent (ttk.Widget): Parent widget that owns the grid.
        row (int): Grid row to start at (heading uses this; outer uses row or row+1).
        column (int): Grid column on the parent.
        columnspan (int): Column span for both heading and outer.
        title (str | None): Optional heading text; if None, no heading is added.
        sticky (str): Sticky configuration for the outer frame.
        heading_style (str): ttk style name for the heading label.
        outer_style (str): ttk style name for the outer frame.
        body_style (str): ttk style name for the body frame.
        heading_padx (Tuple[int, int]): Horizontal padding for heading.
        heading_pady (Tuple[int, int]): Vertical padding for heading.
        outer_padx (Tuple[int, int]): Horizontal padding for outer frame.
        outer_pady (Tuple[int, int]): Vertical padding for outer frame.
        body_padx (Tuple[int, int]): Horizontal padding for body frame.
        body_pady (Tuple[int, int]): Vertical padding for body frame.

    Returns:
        Container: Dataclass containing outer, body, and optional heading.

    Raises:
        None.

    Notes:
        - This function performs the actual grid placement.
        - Public helpers (sections, cards, rows) are thin wrappers around this.
    """
    heading_label: Optional[ttk.Label] = None

    current_row = row
    if title:
        heading_label = ttk.Label(parent, text=title, style=heading_style)
        heading_label.grid(
            row=current_row,
            column=column,
            columnspan=columnspan,
            sticky="w",
            padx=heading_padx,
            pady=heading_pady,
        )
        current_row += 1

    outer = ttk.Frame(parent, style=outer_style)
    outer.grid(
        row=current_row,
        column=column,
        columnspan=columnspan,
        sticky=sticky,
        padx=outer_padx,
        pady=outer_pady,
    )

    # Allow contents to stretch
    outer.rowconfigure(0, weight=1)
    outer.columnconfigure(0, weight=1)

    body = ttk.Frame(outer, style=body_style)
    body.grid(row=0, column=0, sticky="nsew", padx=body_padx, pady=body_pady)

    return Container(outer=outer, body=body, heading=heading_label)


# ====================================================================================================
# 6. PUBLIC HELPERS — PAGE HEADER
# ----------------------------------------------------------------------------------------------------
def create_page_header(
    parent: ttk.Widget,
    *,
    row: int,
    column: int = 0,
    columnspan: int = 1,
    title: str,
    subtitle: Optional[str] = None,
) -> int:
    """
    Description:
        Create a standard page header with title and optional subtitle.
        This is the first element on most pages.

    Args:
        parent (ttk.Widget): Parent widget (typically main_frame).
        row (int): Starting grid row for the header.
        column (int): Grid column on the parent.
        columnspan (int): Column span for the header elements.
        title (str): Main page title text.
        subtitle (str | None): Optional explanatory subtitle text.

    Returns:
        int: The next available row number after the header.

    Raises:
        None.

    Notes:
        - Title uses WindowHeading style (large, bold, primary colour).
        - Subtitle uses Body style (normal weight, secondary text).
        - Returns next row so caller can continue layout easily.
    """
    current_row = row

    # Title
    title_label = make_label(
        parent,
        title,
        category="WindowHeading",
        surface="Primary",
        weight="Bold",
    )
    title_label.grid(
        row=current_row,
        column=column,
        columnspan=columnspan,
        sticky="n",
        padx=(4, 4),
        pady=(0, 4),
    )
    current_row += 1

    # Subtitle (optional)
    if subtitle:
        subtitle_label = make_label(
            parent,
            subtitle,
            category="Body",
            surface="Primary",
            weight="Normal",
        )
        subtitle_label.grid(
            row=current_row,
            column=column,
            columnspan=columnspan,
            sticky="n",
            padx=(4, 4),
            pady=PAGE_HEADER_PADY,
        )
        current_row += 1

    return current_row


# ====================================================================================================
# 7. PUBLIC HELPERS — SECTIONS AND CARDS
# ----------------------------------------------------------------------------------------------------
def create_section_grid(
    parent: ttk.Widget,
    *,
    row: int,
    column: int = 0,
    columnspan: int = 1,
    title: Optional[str] = None,
    sticky: str = "nsew",
) -> Container:
    """
    Description:
        Create a standard "section" container: a full-width bordered area with optional heading.

    Args:
        parent (ttk.Widget): Widget to attach the section to (typically a Frame).
        row (int): Grid row on the parent where the heading will be placed.
        column (int): Grid column on the parent.
        columnspan (int): Column span on the parent grid.
        title (str | None): Optional heading text. If omitted, no heading label is created.
        sticky (str): Sticky setting for the outer frame on the parent grid.

    Returns:
        Container: Dataclass with (outer, body, heading).

    Raises:
        None.

    Notes:
        - Uses primary section heading style and standard section paddings.
        - Place widgets inside container.body, not directly in the Container.
    """
    return create_bordered_container_grid(
        parent=parent,
        row=row,
        column=column,
        columnspan=columnspan,
        title=title,
        sticky=sticky,
        heading_style="Primary.SectionHeading.Bold.TLabel",
        outer_style="SectionOuter.TFrame",
        body_style="SectionBody.TFrame",
        heading_padx=SECTION_HEADING_PADX,
        heading_pady=SECTION_HEADING_PADY,
        outer_padx=SECTION_OUTER_PADX,
        outer_pady=SECTION_OUTER_PADY,
        body_padx=SECTION_BODY_PADX,
        body_pady=SECTION_BODY_PADY,
    )


def create_card_grid(
    parent: ttk.Widget,
    *,
    row: int,
    column: int = 0,
    columnspan: int = 1,
    title: Optional[str] = None,
    sticky: str = "nsew",
    outer_style: str = "SectionOuter.TFrame",
    body_style: str = "SectionBody.TFrame",
) -> Container:
    """
    Description:
        Create a compact "card" container, placed on the parent's grid.

    Args:
        parent (ttk.Widget): Widget to attach the card to.
        row (int): Grid row on the parent where the heading (if any) will be placed.
        column (int): Grid column on the parent.
        columnspan (int): Column span on the parent grid.
        title (str | None): Optional heading text.
        sticky (str): Sticky setting for the outer frame on the parent grid.
        outer_style (str): ttk style for the outer frame.
        body_style (str): ttk style for the body frame.

    Returns:
        Container: Dataclass with (outer, body, heading).

    Raises:
        None.

    Notes:
        - Uses a secondary heading style by default.
        - Padding is slightly tighter than full-width sections.
        - Place widgets inside container.body.
    """
    return create_bordered_container_grid(
        parent=parent,
        row=row,
        column=column,
        columnspan=columnspan,
        title=title,
        sticky=sticky,
        heading_style="Secondary.SectionHeading.Bold.TLabel",
        outer_style=outer_style,
        body_style=body_style,
        heading_padx=(CARD_OUTER_PADX[0], CARD_OUTER_PADX[1]),
        heading_pady=(4, 2),
        outer_padx=CARD_OUTER_PADX,
        outer_pady=CARD_OUTER_PADY,
        body_padx=CARD_BODY_PADX,
        body_pady=CARD_BODY_PADY,
    )


# ====================================================================================================
# 8. PUBLIC HELPERS — ROW LAYOUTS
# ----------------------------------------------------------------------------------------------------
def create_weighted_row(
    parent: ttk.Widget,
    *,
    row: int,
    weights: List[int],
    titles: Optional[List[Optional[str]]] = None,
    sticky: str = "nsew",
    outer_style: str = "SectionOuter.TFrame",
    body_style: str = "SectionBody.TFrame",
) -> List[Container]:
    """
    Description:
        Create a horizontal row of card containers with custom column weights.
        This is the primary pattern for layouts like 30/70 or 25/25/25/25.

        IMPORTANT: This function creates its own row container frame to isolate
        column configurations. Each row's column weights won't affect other rows.

    Args:
        parent (ttk.Widget): Parent frame that owns the grid.
        row (int): Grid row on the parent where the row container will be placed.
        weights (List[int]): List of relative column weights (e.g., [30, 70] or [1, 1, 1, 1]).
            The values are used directly as grid column weights — they don't need to sum to 100.
        titles (List[Optional[str]] | None): Optional list of card titles. May be shorter
            than weights; missing titles default to None (no heading).
        sticky (str): Sticky configuration for each card's outer frame.
        outer_style (str): ttk style for each card outer frame.
        body_style (str): ttk style for each card body frame.

    Returns:
        List[Container]: List of Container instances, one per column.

    Raises:
        None.

    Notes:
        - Each card spans exactly 1 column within the row container.
        - Column weights control relative sizing (e.g., [30, 70] gives 30% / 70%).
        - Use container.body to add widgets inside each card.
        - The row container spans all columns of the parent.

    Example:
        # 30% / 70% split
        top_row = create_weighted_row(parent, row=1, weights=[30, 70], titles=["Left", "Right"])

        # 4 equal columns
        middle_row = create_weighted_row(parent, row=2, weights=[1, 1, 1, 1])

        # 20% / 60% / 20% (sidebar-content-sidebar)
        layout = create_weighted_row(parent, row=3, weights=[20, 60, 20])
    """
    containers: List[Container] = []
    num_columns = len(weights)

    # Create a row container frame that spans the full width
    # This isolates this row's column configuration from other rows
    row_container = ttk.Frame(parent, style="Primary.TFrame")
    row_container.grid(row=row, column=0, sticky="nsew", columnspan=99)

    # Configure parent to allow this row to expand horizontally
    parent.columnconfigure(0, weight=1)

    # Configure column weights within the row container
    for col_idx, weight in enumerate(weights):
        row_container.columnconfigure(col_idx, weight=weight)

    # Calculate half gap for spacing between cards
    half_gap = LAYOUT_COLUMN_GAP // 2

    for index in range(num_columns):
        # Get title if available
        title = None
        if titles and index < len(titles):
            title = titles[index]

        # Calculate padx based on position
        # First column: no left padding, half gap on right
        # Middle columns: half gap on both sides
        # Last column: half gap on left, no right padding
        if num_columns == 1:
            padx = (0, 0)
        elif index == 0:
            padx = (0, half_gap)
        elif index == num_columns - 1:
            padx = (half_gap, 0)
        else:
            padx = (half_gap, half_gap)

        # Create the card container inside row_container
        container = create_bordered_container_grid(
            parent=row_container,
            row=0,  # Always row 0 within the row_container (or row 1 if title)
            column=index,
            columnspan=1,
            title=title,
            sticky=sticky,
            heading_style="Secondary.SectionHeading.Bold.TLabel",
            outer_style=outer_style,
            body_style=body_style,
            heading_padx=(padx[0] + 4, padx[1] + 4),
            heading_pady=(4, 2),
            outer_padx=padx,
            outer_pady=(0, 0),  # No vertical padding within row container
            body_padx=CARD_BODY_PADX,
            body_pady=CARD_BODY_PADY,
        )

        containers.append(container)

    return containers


def create_card_row(
    parent: ttk.Widget,
    *,
    row: int,
    columns: int,
    titles: Optional[List[Optional[str]]] = None,
    sticky: str = "nsew",
    outer_style: str = "SectionOuter.TFrame",
    body_style: str = "SectionBody.TFrame",
) -> List[Container]:
    """
    Description:
        Create a horizontal row of N equal-width card containers.
        This is a convenience wrapper around create_weighted_row with equal weights.

    Args:
        parent (ttk.Widget): Parent frame that owns the grid.
        row (int): Grid row on the parent where cards will be placed.
        columns (int): Number of cards in the row.
        titles (List[Optional[str]] | None): Optional list of card titles.
        sticky (str): Sticky configuration for each card's outer frame.
        outer_style (str): ttk style for each card outer frame.
        body_style (str): ttk style for each card body frame.

    Returns:
        List[Container]: List of Container instances, one per card.

    Raises:
        None.

    Notes:
        - All columns have equal weight (1).
        - For custom weights, use create_weighted_row() instead.
    """
    # Equal weights for all columns
    weights = [1] * columns
    return create_weighted_row(
        parent=parent,
        row=row,
        weights=weights,
        titles=titles,
        sticky=sticky,
        outer_style=outer_style,
        body_style=body_style,
    )


# ====================================================================================================
# 9. PUBLIC HELPERS — BODY SPLITS
# ----------------------------------------------------------------------------------------------------
def create_two_column_body(
    container: Container,
    *,
    left_weight: int = 1,
    right_weight: int = 1,
    left_min_width: int = 200,
    right_min_width: int = 200,
) -> Tuple[ttk.Frame, ttk.Frame]:
    """
    Description:
        Split an existing container body into a simple two-column layout.

    Args:
        container (Container): Container returned from create_section_grid / create_card_grid.
        left_weight (int): Grid weight for the left column (controls horizontal stretch).
        right_weight (int): Grid weight for the right column.
        left_min_width (int): Minimum pixel width for left column.
        right_min_width (int): Minimum pixel width for right column.

    Returns:
        Tuple[ttk.Frame, ttk.Frame]: (left_frame, right_frame).

    Raises:
        None.

    Notes:
        - Frames are created inside container.body.
        - Caller is responsible for placing widgets inside the returned frames.
        - Gap between columns uses LAYOUT_COLUMN_GAP from G01a.
    """
    body = container.body
    half_gap = LAYOUT_COLUMN_GAP // 2

    body.columnconfigure(0, weight=left_weight, minsize=left_min_width)
    body.columnconfigure(1, weight=right_weight, minsize=right_min_width)
    body.rowconfigure(0, weight=1)

    left = ttk.Frame(body, style="SectionBody.TFrame")
    right = ttk.Frame(body, style="SectionBody.TFrame")

    left.grid(row=0, column=0, sticky="nsew", padx=(0, half_gap))
    right.grid(row=0, column=1, sticky="nsew", padx=(half_gap, 0))

    return left, right


def create_multi_column_body(
    container: Container,
    *,
    weights: List[int],
    min_widths: Optional[List[int]] = None,
) -> List[ttk.Frame]:
    """
    Description:
        Split an existing container body into N columns with custom weights.

    Args:
        container (Container): Container returned from create_section_grid / create_card_grid.
        weights (List[int]): List of grid weights for each column.
        min_widths (List[int] | None): Optional minimum widths for each column.
            If shorter than weights, remaining columns get no minsize.

    Returns:
        List[ttk.Frame]: List of frames, one per column.

    Raises:
        None.

    Notes:
        - Frames are created inside container.body.
        - Gap between columns uses LAYOUT_COLUMN_GAP from G01a.
    """
    body = container.body
    num_columns = len(weights)
    half_gap = LAYOUT_COLUMN_GAP // 2
    frames: List[ttk.Frame] = []

    # Configure columns
    for index, weight in enumerate(weights):
        min_width = 0
        if min_widths and index < len(min_widths):
            min_width = min_widths[index]
        body.columnconfigure(index, weight=weight, minsize=min_width)

    body.rowconfigure(0, weight=1)

    # Create frames
    for index in range(num_columns):
        # Calculate padding
        if num_columns == 1:
            padx = (0, 0)
        elif index == 0:
            padx = (0, half_gap)
        elif index == num_columns - 1:
            padx = (half_gap, 0)
        else:
            padx = (half_gap, half_gap)

        frame = ttk.Frame(body, style="SectionBody.TFrame")
        frame.grid(row=0, column=index, sticky="nsew", padx=padx)
        frames.append(frame)

    return frames


# ====================================================================================================
# 10. COMPOSITE WIDGET PATTERNS
# ----------------------------------------------------------------------------------------------------
def make_radio_group(
    parent: tk.Misc,
    options: List[Tuple[str, Any]],
    variable: tk.Variable,
    *,
    orientation: str = "vertical",
    command: Optional[Callable[[], Any]] = None,
    **kwargs: Any,
) -> ttk.Frame:
    """
    Description:
        Create a group of radio buttons inside a frame. This is a composite pattern
        that wraps multiple make_radio() calls for convenience.

    Args:
        parent (tk.Misc): Parent container widget.
        options (List[Tuple[str, Any]]): List of (label_text, value) tuples.
            Each tuple creates one radio button with the given label and value.
        variable (tk.Variable): Shared Tk variable (StringVar, IntVar) for the group.
            All radio buttons in the group share this variable.
        orientation (str): Layout direction. One of "vertical" (default) or "horizontal".
        command (Optional[Callable]): Optional callback when selection changes.
            Applied to all radio buttons in the group.
        **kwargs: Additional options passed to each make_radio() call.

    Returns:
        ttk.Frame: Frame containing all radio buttons.

    Raises:
        None.

    Notes:
        - The frame uses "Primary.TFrame" style by default.
        - Radio buttons are packed with consistent spacing.
        - For custom layouts, use make_radio() directly instead.

    Example:
        drive_mode = tk.StringVar(value="api")
        radio_group = make_radio_group(
            card.body,
            options=[
                ("Use Google Drive API", "api"),
                ("Use Local Mapped Drive", "local"),
            ],
            variable=drive_mode,
            command=on_drive_mode_change,
        )
        radio_group.pack(anchor="w", pady=4)
    """
    # Create container frame
    frame_style = kwargs.pop("frame_style", "Primary.TFrame")
    frame = ttk.Frame(parent, style=frame_style)

    # Determine pack direction and padding
    if orientation == "horizontal":
        side = "left"
        padx = (0, LAYOUT_COLUMN_GAP)
        pady = 0
    else:  # vertical
        side = "top"
        padx = 0
        pady = (0, 4)

    # Create radio buttons
    for index, (label_text, value) in enumerate(options):
        radio = make_radio(
            frame,
            text=label_text,
            variable=variable,
            value=value,
            command=command,
            **kwargs,
        )

        # Last item doesn't need trailing padding
        if index == len(options) - 1:
            if orientation == "horizontal":
                padx = 0
            else:
                pady = 0

        radio.pack(side=side, anchor="w", padx=padx, pady=pady)

    return frame


# ====================================================================================================
# 11. SELF-TEST / DEMO
# ----------------------------------------------------------------------------------------------------
def demo() -> None:
    """
    Description:
        Lightweight visual demo to verify the container patterns.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Developer-only; never called by production code.
        - Demonstrates page header, weighted rows, and standard sections.
    """
    init_logging()
    logger.info("=== G02b_container_patterns demo start ===")

    root = tk.Tk()
    root.title("G02b_container_patterns — Demo")
    root.geometry("1100x800")
    root.configure(bg=GUI_COLOUR_BG_PRIMARY)

    # Try to apply project styles if available
    try:
        from gui.G01b_style_engine import configure_ttk_styles
        style = ttk.Style(root)
        configure_ttk_styles(style)
        logger.info("[G02b] Project styles applied successfully.")
    except Exception as exc:
        logger.warning("[G02b] Could not apply project styles: %s", exc)

    # Main container with padding
    main = ttk.Frame(root, padding=20, style="SectionOuter.TFrame")
    main.pack(fill="both", expand=True)

    # Configure main to expand column 0 (all row containers go here)
    main.columnconfigure(0, weight=1)

    # -------------------------------------------------------------------------
    # Page Header
    # -------------------------------------------------------------------------
    next_row = create_page_header(
        main,
        row=0,
        columnspan=1,
        title="G02b Container Patterns Demo",
        subtitle="Demonstrates page headers, weighted rows, sections, and cards.",
    )

    # -------------------------------------------------------------------------
    # Example 1: Weighted row (30/70 split)
    # -------------------------------------------------------------------------
    top_row = create_weighted_row(
        main,
        row=next_row,
        weights=[30, 70],
        titles=["Overview (30%)", "Console (70%)"],
    )
    next_row += 1  # Each weighted row is a single row in the parent

    make_label(top_row[0].body, "Left panel content", category="Body", surface="Secondary").grid(
        row=0, column=0, sticky="w", pady=4
    )
    make_label(top_row[1].body, "Right panel content", category="Body", surface="Secondary").grid(
        row=0, column=0, sticky="w", pady=4
    )

    # -------------------------------------------------------------------------
    # Example 2: Four equal columns (25/25/25/25)
    # -------------------------------------------------------------------------
    middle_row = create_card_row(
        main,
        row=next_row,
        columns=4,
        titles=["Google Drive", "Snowflake", "Accounting Period", "DWH Period"],
    )
    next_row += 1

    for idx, container in enumerate(middle_row):
        make_label(
            container.body,
            f"Card {idx + 1} content",
            category="Body",
            surface="Secondary",
        ).grid(row=0, column=0, sticky="w", pady=4)

    # -------------------------------------------------------------------------
    # Example 3: Three columns (20/60/20)
    # -------------------------------------------------------------------------
    bottom_row = create_weighted_row(
        main,
        row=next_row,
        weights=[20, 60, 20],
        titles=["Sidebar Left", "Main Content", "Sidebar Right"],
    )
    next_row += 1

    for idx, container in enumerate(bottom_row):
        make_label(
            container.body,
            f"Panel {idx + 1}",
            category="Body",
            surface="Secondary",
        ).grid(row=0, column=0, sticky="w", pady=4)

    # -------------------------------------------------------------------------
    # Example 4: Full-width section with two-column body
    # -------------------------------------------------------------------------
    section = create_section_grid(
        main,
        row=next_row,
        column=0,
        columnspan=1,
        title="Full-Width Section",
    )
    next_row += 2

    left, right = create_two_column_body(section)
    make_label(left, "Left column inside section", category="Body", surface="Secondary").grid(
        row=0, column=0, sticky="w", pady=4
    )
    make_label(right, "Right column inside section", category="Body", surface="Secondary").grid(
        row=0, column=0, sticky="w", pady=4
    )

    logger.info("=== G02b_container_patterns demo ready ===")
    root.mainloop()
    logger.info("=== G02b_container_patterns demo end ===")


# ====================================================================================================
# 12. MAIN GUARD
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    demo()
