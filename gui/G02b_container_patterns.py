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
#       create_card_grid(...)        # Compact card-style container
#       create_two_column_body(...)  # 50/50 or weighted split inside a section/card
#
#   These building blocks ensure all views adhere to the same spacing, padding, heading style, and
#   grid structure defined by the GUI Boilerplate 00/01 layer.
#
# ----------------------------------------------------------------------------------------------------
# Key Patterns:
#   • create_section_grid(...)       → Heading label (optional) + bordered outer frame + content area
#   • create_card_grid(...)          → Compact version of a section, ideal for nested UI blocks
#   • create_two_column_body(...)    → Split an existing container body into left/right frames
#
# Visual Structure:
#       Parent
#         ├── [Heading Label]   (optional)
#         └── [Outer Frame]     (border, background, padding)
#               └── [Body Frame] (place all widgets here)
#
# Usage Example:
#       from gui.G02b_container_patterns import create_section_grid
#
#       section = create_section_grid(
#           parent=self.main_frame,
#           row=0,
#           column=0,
#           title="Connection Settings",
#       )
#
#       ttk.Label(section.body, text="Host:").grid(row=0, column=0, sticky="w")
#
# Integration Notes:
#   • Pattern frames use style names defined in:
#         - G01a_style_engine      (ttk style definitions)
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
from gui.G01a_style_config import *  # noqa: F401,F403 - colours / layout constants (if needed)

# ====================================================================================================
# 3. DATA CLASSES
# ----------------------------------------------------------------------------------------------------
@dataclass
class Container:
    """
    Simple bundle of the widgets that make up a container pattern.

    Attributes:
        outer:  The outer frame providing border / background.
        body:   The inner content frame where widgets should be placed.
        heading: Optional heading label (may be None).
    """
    outer: ttk.Frame
    body: ttk.Frame
    heading: Optional[ttk.Label] = None


# ====================================================================================================
# 4. LOCAL LAYOUT CONSTANTS
# ----------------------------------------------------------------------------------------------------
# Note:
#   These are intentionally conservative defaults. If you later add equivalents to
#   G00_style_config.py (e.g. LAYOUT_SECTION_PADX), you can swap these out easily.

SECTION_HEADING_PADX: Tuple[int, int] = (4, 4)
SECTION_HEADING_PADY: Tuple[int, int] = (8, 2)

SECTION_OUTER_PADX: Tuple[int, int] = (0, 0)
SECTION_OUTER_PADY: Tuple[int, int] = (0, 12)

SECTION_BODY_PADX: Tuple[int, int] = (12, 12)
SECTION_BODY_PADY: Tuple[int, int] = (8, 12)

CARD_OUTER_PADX: Tuple[int, int] = (8, 8)
CARD_OUTER_PADY: Tuple[int, int] = (8, 8)

CARD_BODY_PADX: Tuple[int, int] = (8, 8)
CARD_BODY_PADY: Tuple[int, int] = (8, 8)


# ====================================================================================================
# 5. INTERNAL HELPER
# ----------------------------------------------------------------------------------------------------
def create_bordered_container_grid(
    parent: ttk.Widget,
    *,
    row: int,
    column: int = 0,
    columnspan: int = 1,
    title: Optional[str] = None,
    sticky: str = "nsew",
    heading_style: str = "SectionHeading.TLabel",
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
    Core implementation shared by section/card helpers.

    Creates:
        [ heading label ]     (optional, on parent)
        [ outer frame ]       (on parent)
          └─ [ body frame ]   (inside outer)

    Returns:
        Container(outer, body, heading)
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
# 6. PUBLIC HELPERS
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
    Create a standard "section" container:

        ┌────────────────────────────────────────────┐
        │  Heading Label                            │
        └────────────────────────────────────────────┘
        ┌────────────────────────────────────────────┐
        │  Bordered content area (body frame)       │
        └────────────────────────────────────────────┘

    Args:
        parent:     Widget to attach the section to (typically a Frame).
        row:        Grid row on the parent where the heading will be placed.
        column:     Grid column on the parent.
        columnspan: Column span on the parent grid.
        title:      Optional heading text. If omitted, no heading label is created.
        sticky:     Sticky setting for the outer frame on the parent grid.

    Returns:
        Container dataclass with (outer, body, heading).
    """
    return create_bordered_container_grid(
        parent=parent,
        row=row,
        column=column,
        columnspan=columnspan,
        title=title,
        sticky=sticky,
        heading_style="SectionHeading.TLabel",
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
    Create a compact "card" container.

    Visually similar to create_section_grid but with tighter padding, intended for
    secondary information or nested content inside a larger section.

    Args:
        parent:     Widget to attach the card to.
        row:        Grid row on the parent where the heading (if any) will be placed.
        column:     Grid column on the parent.
        columnspan: Column span on the parent grid.
        title:      Optional heading text.
        sticky:     Sticky setting for the outer frame on the parent grid.
        outer_style:
                    ttk style for the outer frame. Defaults to SectionOuter.TFrame to
                    reuse the main section border visual.
        body_style: ttk style for the body frame. Defaults to SectionBody.TFrame.

    Returns:
        Container dataclass with (outer, body, heading).
    """
    return create_bordered_container_grid(
        parent=parent,
        row=row,
        column=column,
        columnspan=columnspan,
        title=title,
        sticky=sticky,
        heading_style="SectionHeading.TLabel",
        outer_style=outer_style,
        body_style=body_style,
        heading_padx=(CARD_OUTER_PADX[0], CARD_OUTER_PADX[1]),
        heading_pady=(4, 2),
        outer_padx=CARD_OUTER_PADX,
        outer_pady=CARD_OUTER_PADY,
        body_padx=CARD_BODY_PADX,
        body_pady=CARD_BODY_PADY,
    )


def create_two_column_body(
    container: Container,
    *,
    left_weight: int = 1,
    right_weight: int = 1,
    left_min_width: int = 200,
    right_min_width: int = 200,
) -> Tuple[ttk.Frame, ttk.Frame]:
    """
    Split an existing container body into a simple two-column layout:

        [ body (existing) ]
           ├─ left_frame  (column 0)
           └─ right_frame (column 1)

    This is handy when you want a quick 2-column grid inside a section/card without
    repeating boilerplate.

    Args:
        container:      Container instance returned from create_section_grid / create_card_grid.
        left_weight:    Grid weight for the left column (controls horizontal stretch).
        right_weight:   Grid weight for the right column.
        left_min_width: Minimum pixel width for left column.
        right_min_width:Minimum pixel width for right column.

    Returns:
        (left_frame, right_frame)
    """
    body = container.body

    body.columnconfigure(0, weight=left_weight, minsize=left_min_width)
    body.columnconfigure(1, weight=right_weight, minsize=right_min_width)
    body.rowconfigure(0, weight=1)

    left = ttk.Frame(body)
    right = ttk.Frame(body)

    left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

    return left, right


# ====================================================================================================
# 7. SELF-TEST / DEMO
# ----------------------------------------------------------------------------------------------------
def _demo() -> None:
    """
    Lightweight visual demo to verify the container patterns.

    Opens a standard Tk window (no BaseGUI dependency) and shows a couple of
    sections and cards so you can see padding/borders in context.
    """
    logger.info("=== G01e_container_patterns demo start ===")

    root = tk.Tk()
    root.title("G01e_container_patterns — Demo")
    root.geometry("900x600")

    # Try to apply project styles if available
    try:
        from gui.G01b_style_engine import configure_ttk_styles

        style = ttk.Style(root)
        configure_ttk_styles(style)
        logger.info("[G01e] Project styles applied successfully.")
    except Exception as exc:  # noqa: BLE001
        logger.warning("[G01e] Could not apply project styles: %s", exc)

    # Layout root
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    main = ttk.Frame(root, padding=20)
    main.grid(row=0, column=0, sticky="nsew")

    # Example 1: Full-width section with 2-column body
    section = create_section_grid(
        parent=main,
        row=0,
        column=0,
        columnspan=2,
        title="Primary Section (Two Column)",
    )
    left, right = create_two_column_body(section)

    ttk.Label(left, text="Left column content").grid(row=0, column=0, sticky="w", pady=(0, 4))
    ttk.Label(right, text="Right column content").grid(row=0, column=0, sticky="w", pady=(0, 4))

    # Example 2: Two cards beneath the section
    card1 = create_card_grid(parent=main, row=2, column=0, title="Card A")
    card2 = create_card_grid(parent=main, row=2, column=1, title="Card B")

    ttk.Label(card1.body, text="Card A body content.").grid(row=0, column=0, sticky="w")
    ttk.Label(card2.body, text="Card B body content.").grid(row=0, column=0, sticky="w")

    root.mainloop()
    logger.info("=== G01e_container_patterns demo end ===")


# ====================================================================================================
# 8. MAIN GUARD
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    _demo()
