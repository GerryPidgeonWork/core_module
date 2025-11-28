# ====================================================================================================
# G01d_layout_primitives.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Provide SEMANTIC, LAYOUT-AWARE TYPOGRAPHY & STRUCTURE PRIMITIVES for GUI pages.
#
#   This module bridges the gap between raw widget factories (G01c) and container
#   patterns (G02b). It provides:
#
#       TYPOGRAPHY PRIMITIVES (semantic text elements):
#           • page_title(...)       – Top-level page/window title
#           • section_title(...)    – Section heading within a page
#           • card_title(...)       – Card/panel heading
#           • body_text(...)        – Paragraph/descriptive text
#           • caption(...)          – Small helper/hint text
#           • code_text(...)        – Monospace code snippets
#
#       STRUCTURAL PRIMITIVES (visual separators & spacing):
#           • divider(...)          – Horizontal/vertical separator line
#           • spacer(...)           – Fixed-height vertical spacing
#           • indent_block(...)     – Indented content wrapper
#
#       LAYOUT HELPERS (convenience for common patterns):
#           • label_value_pair(...) – "Label: Value" inline display
#           • bullet_list(...)      – Simple bullet point list
#           • icon_text(...)        – Icon + text combination
#
#   KEY DIFFERENCE FROM G01c:
#       G01c = atomic widget factories (make_label, make_button, etc.)
#       G01d = semantic primitives with built-in spacing defaults
#
#   Every G01d primitive returns a widget with:
#       • Sensible default padding/margins
#       • Consistent typography hierarchy
#       • Metadata for programmatic layout queries
#
# Architectural Role:
#   - Sits BETWEEN G01c (widget primitives) and G02 (container patterns)
#   - Consumes styles from G01b_style_engine
#   - Produces ready-to-use elements with semantic meaning
#
# Integration:
#   from gui.G01d_layout_primitives import (
#       page_title, section_title, card_title,
#       body_text, caption, code_text,
#       divider, spacer, indent_block,
#       label_value_pair, bullet_list
#   )
#
# Rules:
#   - NO geometry management (pack/grid/place) — caller decides
#   - NO container creation (use G02b for sections/cards)
#   - ZERO side effects at import time
#   - All styling via ttk styles from G01b
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-23
# Updated:      2025-11-28 (v2 - Enhanced with clear semantic hierarchy)
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
    GUI_COLOUR_BG_PRIMARY,
    GUI_COLOUR_BG_SECONDARY,
    GUI_COLOUR_DIVIDER,
    TEXT_COLOUR_SECONDARY,
    TEXT_COLOUR_MONO,
    GUI_FONT_FAMILY,
    GUI_FONT_SIZE_DEFAULT,
    GUI_FONT_SIZE_SMALL,
    SECTION_SPACING,
    SECTION_TITLE_SPACING,
    LABEL_ENTRY_SPACING,
)
from gui.G01c_widget_primitives import (
    make_label,
    make_divider as g01c_make_divider,
    make_spacer as g01c_make_spacer,
    make_frame,
)


# ====================================================================================================
# 3. MODULE CONFIGURATION
# ====================================================================================================
DEBUG_LAYOUT_PRIMITIVES: bool = False

# Default spacing values (can be overridden per-call)
DEFAULT_TITLE_BOTTOM_PADDING = 8
DEFAULT_SECTION_BOTTOM_PADDING = 4
DEFAULT_BODY_BOTTOM_PADDING = 6
DEFAULT_CAPTION_TOP_PADDING = 2


# ====================================================================================================
# 4. TYPOGRAPHY PRIMITIVES
# ----------------------------------------------------------------------------------------------------
# Semantic text elements with built-in hierarchy and spacing defaults.
# ====================================================================================================

def page_title(
    parent: tk.Widget,
    text: str,
    *,
    surface: str = "Primary",
    weight: str = "Bold",
    anchor: str = "w",
    **kwargs: Any,
) -> ttk.Label:
    """
    Create a top-level page/window title.

    Description:
        The largest, most prominent text element. Use once per page at the top.
        Maps to category="WindowHeading" in G01c.

    Args:
        parent: Parent widget.
        text: Title text.
        surface: "Primary" or "Secondary" background context.
        weight: "Normal" or "Bold" (default Bold).
        anchor: Text anchor ('w', 'center', 'e').
        **kwargs: Additional options passed to make_label().

    Returns:
        ttk.Label with metadata:
            • .g01d_role = "page_title"
            • .g01d_default_pady = (0, DEFAULT_TITLE_BOTTOM_PADDING)

    Example:
        page_title(frame, "Settings").pack(anchor="w", pady=(0, 8))
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] page_title: %r", text)

    lbl = make_label(
        parent,
        text,
        category="WindowHeading",
        surface=surface,
        weight=weight,
        anchor=anchor,
        **kwargs,
    )
    
    # Attach semantic metadata
    lbl.g01d_role = "page_title"  # type: ignore[attr-defined]
    lbl.g01d_default_pady = (0, DEFAULT_TITLE_BOTTOM_PADDING)  # type: ignore[attr-defined]
    
    return lbl


def section_title(
    parent: tk.Widget,
    text: str,
    *,
    surface: str = "Primary",
    weight: str = "Bold",
    anchor: str = "w",
    **kwargs: Any,
) -> ttk.Label:
    """
    Create a section-level heading.

    Description:
        Used to introduce a logical section of the page. Smaller than page_title,
        larger than card_title. Maps to category="Heading" in G01c.

    Args:
        parent: Parent widget.
        text: Section title text.
        surface: "Primary" or "Secondary" background context.
        weight: "Normal" or "Bold" (default Bold).
        anchor: Text anchor.
        **kwargs: Additional options passed to make_label().

    Returns:
        ttk.Label with metadata:
            • .g01d_role = "section_title"
            • .g01d_default_pady = (SECTION_SPACING, SECTION_TITLE_SPACING)

    Example:
        section_title(frame, "Connection Settings").pack(anchor="w")
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] section_title: %r", text)

    lbl = make_label(
        parent,
        text,
        category="Heading",
        surface=surface,
        weight=weight,
        anchor=anchor,
        **kwargs,
    )
    
    lbl.g01d_role = "section_title"  # type: ignore[attr-defined]
    lbl.g01d_default_pady = (SECTION_SPACING, SECTION_TITLE_SPACING)  # type: ignore[attr-defined]
    
    return lbl


def card_title(
    parent: tk.Widget,
    text: str,
    *,
    surface: str = "Secondary",
    weight: str = "Bold",
    anchor: str = "w",
    **kwargs: Any,
) -> ttk.Label:
    """
    Create a card/panel heading.

    Description:
        Used inside cards or small panels. Smaller than section_title.
        Maps to category="SectionHeading" in G01c.

    Args:
        parent: Parent widget (typically a card body frame).
        text: Card title text.
        surface: "Primary" or "Secondary" (default Secondary for cards).
        weight: "Normal" or "Bold" (default Bold).
        anchor: Text anchor.
        **kwargs: Additional options.

    Returns:
        ttk.Label with metadata:
            • .g01d_role = "card_title"
            • .g01d_default_pady = (0, DEFAULT_SECTION_BOTTOM_PADDING)

    Example:
        card_title(card.body, "Google Drive").pack(anchor="w")
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] card_title: %r", text)

    lbl = make_label(
        parent,
        text,
        category="SectionHeading",
        surface=surface,
        weight=weight,
        anchor=anchor,
        **kwargs,
    )
    
    lbl.g01d_role = "card_title"  # type: ignore[attr-defined]
    lbl.g01d_default_pady = (0, DEFAULT_SECTION_BOTTOM_PADDING)  # type: ignore[attr-defined]
    
    return lbl


def body_text(
    parent: tk.Widget,
    text: str,
    *,
    surface: str = "Primary",
    weight: str = "Normal",
    wraplength: int | None = None,
    justify: str = "left",
    **kwargs: Any,
) -> ttk.Label:
    """
    Create standard body/paragraph text.

    Description:
        For descriptive content, instructions, and general text.
        Maps to category="Body" in G01c.

    Args:
        parent: Parent widget.
        text: Body text content.
        surface: "Primary" or "Secondary" background context.
        weight: "Normal" or "Bold" (default Normal).
        wraplength: Optional wrap width in pixels.
        justify: Text justification ('left', 'center', 'right').
        **kwargs: Additional options.

    Returns:
        ttk.Label with metadata:
            • .g01d_role = "body_text"
            • .g01d_default_pady = (0, DEFAULT_BODY_BOTTOM_PADDING)

    Example:
        body_text(frame, "Enter your credentials below.", wraplength=300).pack()
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] body_text: %r", text[:50] if len(text) > 50 else text)

    if wraplength is not None:
        kwargs["wraplength"] = wraplength
    kwargs["justify"] = justify

    lbl = make_label(
        parent,
        text,
        category="Body",
        surface=surface,
        weight=weight,
        **kwargs,
    )
    
    lbl.g01d_role = "body_text"  # type: ignore[attr-defined]
    lbl.g01d_default_pady = (0, DEFAULT_BODY_BOTTOM_PADDING)  # type: ignore[attr-defined]
    
    return lbl


def caption(
    parent: tk.Widget,
    text: str,
    *,
    surface: str = "Primary",
    **kwargs: Any,
) -> ttk.Label:
    """
    Create small caption/hint text.

    Description:
        For helper text, hints, footnotes. Smaller and lighter than body_text.

    Args:
        parent: Parent widget.
        text: Caption text.
        surface: "Primary" or "Secondary" background context.
        **kwargs: Additional options.

    Returns:
        ttk.Label with metadata:
            • .g01d_role = "caption"

    Example:
        caption(frame, "* Required field").pack(anchor="w")
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] caption: %r", text)

    # Use small font size - we need to create a custom style or use configure
    lbl = make_label(
        parent,
        text,
        category="Body",
        surface=surface,
        weight="Normal",
        **kwargs,
    )
    
    # Apply smaller font
    try:
        current_font = lbl.cget("font")
        if current_font:
            lbl.configure(font=(GUI_FONT_FAMILY[0], GUI_FONT_SIZE_SMALL))
    except Exception:
        pass
    
    lbl.g01d_role = "caption"  # type: ignore[attr-defined]
    lbl.g01d_default_pady = (DEFAULT_CAPTION_TOP_PADDING, 0)  # type: ignore[attr-defined]
    
    return lbl


def code_text(
    parent: tk.Widget,
    text: str,
    *,
    surface: str = "Secondary",
    **kwargs: Any,
) -> ttk.Label:
    """
    Create monospace code/technical text.

    Description:
        For code snippets, file paths, technical identifiers.
        Uses monospace font.

    Args:
        parent: Parent widget.
        text: Code/technical text.
        surface: Background context (default Secondary for contrast).
        **kwargs: Additional options.

    Returns:
        ttk.Label with metadata:
            • .g01d_role = "code_text"

    Example:
        code_text(frame, "/path/to/file.py").pack(anchor="w")
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] code_text: %r", text)

    lbl = make_label(
        parent,
        text,
        category="Body",
        surface=surface,
        weight="Normal",
        **kwargs,
    )
    
    # Apply monospace font
    try:
        lbl.configure(font=("Consolas", GUI_FONT_SIZE_DEFAULT))
    except Exception:
        try:
            lbl.configure(font=("Courier New", GUI_FONT_SIZE_DEFAULT))
        except Exception:
            pass
    
    lbl.g01d_role = "code_text"  # type: ignore[attr-defined]
    
    return lbl


# ====================================================================================================
# 5. STRUCTURAL PRIMITIVES
# ----------------------------------------------------------------------------------------------------
# Visual separators and spacing elements.
# ====================================================================================================

def divider(
    parent: tk.Widget,
    *,
    orient: Literal["horizontal", "vertical"] = "horizontal",
    thickness: int = 1,
) -> ttk.Frame:
    """
    Create a visual separator line.

    Description:
        A thin line to visually separate content blocks.

    Args:
        parent: Parent widget.
        orient: "horizontal" or "vertical".
        thickness: Line thickness in pixels (default 1).

    Returns:
        ttk.Frame with metadata:
            • .g01d_role = "divider"
            • .g01d_orient = orient

    Example:
        divider(frame).pack(fill="x", pady=8)
        divider(frame, orient="vertical").pack(side="left", fill="y", padx=4)
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] divider: orient=%s, thickness=%d", orient, thickness)

    if orient == "vertical":
        div = ttk.Frame(parent, width=thickness, style="ToolbarDivider.TFrame")
    else:
        div = g01c_make_divider(parent, height=thickness)

    div.g01d_role = "divider"  # type: ignore[attr-defined]
    div.g01d_orient = orient  # type: ignore[attr-defined]
    
    return div


def spacer(
    parent: tk.Widget,
    *,
    height: int = 8,
    width: int | None = None,
) -> ttk.Frame:
    """
    Create fixed-dimension spacing.

    Description:
        Empty space for visual rhythm between content blocks.

    Args:
        parent: Parent widget.
        height: Vertical space in pixels (default 8).
        width: Optional horizontal space (for horizontal layouts).

    Returns:
        ttk.Frame with metadata:
            • .g01d_role = "spacer"
            • .g01d_height = height
            • .g01d_width = width

    Example:
        spacer(frame, height=16).pack(fill="x")
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] spacer: height=%d, width=%s", height, width)

    if width is not None:
        sp = ttk.Frame(parent, height=height, width=width, style="TFrame")
    else:
        sp = g01c_make_spacer(parent, height=height)

    sp.g01d_role = "spacer"  # type: ignore[attr-defined]
    sp.g01d_height = height  # type: ignore[attr-defined]
    sp.g01d_width = width  # type: ignore[attr-defined]
    
    return sp


def indent_block(
    parent: tk.Widget,
    *,
    indent: int = 20,
    surface: str = "Primary",
) -> ttk.Frame:
    """
    Create an indented content wrapper.

    Description:
        A frame with left padding to indent child content. Useful for
        hierarchical displays or nested options.

    Args:
        parent: Parent widget.
        indent: Left padding in pixels (default 20).
        surface: "Primary" or "Secondary" for background matching.

    Returns:
        ttk.Frame with metadata:
            • .g01d_role = "indent_block"
            • .g01d_indent = indent

    Example:
        block = indent_block(frame, indent=24)
        block.pack(fill="x")
        body_text(block, "Indented content here").pack()
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] indent_block: indent=%d", indent)

    style = "TFrame" if surface == "Primary" else "SectionBody.TFrame"
    block = ttk.Frame(parent, padding=(indent, 0, 0, 0), style=style)
    
    block.g01d_role = "indent_block"  # type: ignore[attr-defined]
    block.g01d_indent = indent  # type: ignore[attr-defined]
    
    return block


# ====================================================================================================
# 6. LAYOUT HELPERS
# ----------------------------------------------------------------------------------------------------
# Convenience functions for common patterns.
# ====================================================================================================

def label_value_pair(
    parent: tk.Widget,
    label: str,
    value: str,
    *,
    surface: str = "Primary",
    label_width: int | None = None,
    separator: str = ":",
) -> ttk.Frame:
    """
    Create a "Label: Value" inline display.

    Description:
        Common pattern for displaying key-value information.
        Returns a frame containing both labels.

    Args:
        parent: Parent widget.
        label: Label text (e.g., "Status").
        value: Value text (e.g., "Connected").
        surface: Background context.
        label_width: Optional fixed width for label alignment.
        separator: Separator between label and value (default ":").

    Returns:
        ttk.Frame containing the label-value pair with metadata:
            • .g01d_role = "label_value_pair"
            • .label_widget = the label ttk.Label
            • .value_widget = the value ttk.Label

    Example:
        pair = label_value_pair(frame, "Status", "Connected")
        pair.pack(anchor="w")
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] label_value_pair: %s = %s", label, value)

    container = ttk.Frame(parent, style="TFrame" if surface == "Primary" else "SectionBody.TFrame")
    
    # Label (bold)
    lbl_text = f"{label}{separator}" if separator else label
    lbl = make_label(
        container,
        lbl_text,
        category="Body",
        surface=surface,
        weight="Bold",
    )
    if label_width:
        lbl.configure(width=label_width)
    lbl.pack(side="left")
    
    # Spacer
    ttk.Label(container, text=" ", style=f"{surface}.Normal.TLabel").pack(side="left")
    
    # Value (normal)
    val = make_label(
        container,
        value,
        category="Body",
        surface=surface,
        weight="Normal",
    )
    val.pack(side="left")
    
    container.g01d_role = "label_value_pair"  # type: ignore[attr-defined]
    container.label_widget = lbl  # type: ignore[attr-defined]
    container.value_widget = val  # type: ignore[attr-defined]
    
    return container


def bullet_list(
    parent: tk.Widget,
    items: list[str],
    *,
    surface: str = "Primary",
    bullet: str = "•",
    indent: int = 16,
) -> ttk.Frame:
    """
    Create a simple bullet point list.

    Description:
        Renders a list of items with bullet points.

    Args:
        parent: Parent widget.
        items: List of text items.
        surface: Background context.
        bullet: Bullet character (default "•").
        indent: Indentation for text after bullet.

    Returns:
        ttk.Frame containing all bullet items with metadata:
            • .g01d_role = "bullet_list"
            • .item_widgets = list of item label widgets

    Example:
        bullet_list(frame, ["Item 1", "Item 2", "Item 3"]).pack(anchor="w")
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] bullet_list: %d items", len(items))

    container = ttk.Frame(parent, style="TFrame" if surface == "Primary" else "SectionBody.TFrame")
    item_widgets = []
    
    for item in items:
        row = ttk.Frame(container, style="TFrame" if surface == "Primary" else "SectionBody.TFrame")
        row.pack(fill="x", pady=1)
        
        # Bullet
        make_label(
            row,
            bullet,
            category="Body",
            surface=surface,
            weight="Normal",
        ).pack(side="left")
        
        # Text with indent
        item_lbl = make_label(
            row,
            f" {item}",
            category="Body",
            surface=surface,
            weight="Normal",
        )
        item_lbl.pack(side="left", padx=(indent - 8, 0))
        item_widgets.append(item_lbl)
    
    container.g01d_role = "bullet_list"  # type: ignore[attr-defined]
    container.item_widgets = item_widgets  # type: ignore[attr-defined]
    
    return container


def icon_text(
    parent: tk.Widget,
    icon: str,
    text: str,
    *,
    surface: str = "Primary",
    weight: str = "Normal",
    gap: int = 6,
) -> ttk.Frame:
    """
    Create an icon + text combination.

    Description:
        Common pattern for status indicators, menu items, etc.
        Uses Unicode icons (emoji or symbols).

    Args:
        parent: Parent widget.
        icon: Icon character (e.g., "✓", "⚠", "ℹ").
        text: Text content.
        surface: Background context.
        weight: Text weight ("Normal" or "Bold").
        gap: Space between icon and text.

    Returns:
        ttk.Frame containing icon and text with metadata:
            • .g01d_role = "icon_text"
            • .icon_widget = the icon label
            • .text_widget = the text label

    Example:
        icon_text(frame, "✓", "Connected", surface="Secondary").pack()
        icon_text(frame, "⚠", "Warning", weight="Bold").pack()
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] icon_text: %s %s", icon, text)

    container = ttk.Frame(parent, style="TFrame" if surface == "Primary" else "SectionBody.TFrame")
    
    icon_lbl = make_label(
        container,
        icon,
        category="Body",
        surface=surface,
        weight="Normal",
    )
    icon_lbl.pack(side="left")
    
    text_lbl = make_label(
        container,
        text,
        category="Body",
        surface=surface,
        weight=weight,
    )
    text_lbl.pack(side="left", padx=(gap, 0))
    
    container.g01d_role = "icon_text"  # type: ignore[attr-defined]
    container.icon_widget = icon_lbl  # type: ignore[attr-defined]
    container.text_widget = text_lbl  # type: ignore[attr-defined]
    
    return container


# ====================================================================================================
# 7. LEGACY ALIASES (for backwards compatibility)
# ----------------------------------------------------------------------------------------------------
# These map old names to new semantic names.
# ====================================================================================================

def heading(parent: tk.Widget, text: str, **kwargs: Any) -> ttk.Label:
    """Legacy alias for section_title(). Use section_title() in new code."""
    return section_title(parent, text, **kwargs)


def subheading(parent: tk.Widget, text: str, **kwargs: Any) -> ttk.Label:
    """Legacy alias for card_title(). Use card_title() in new code."""
    return card_title(parent, text, **kwargs)


# ====================================================================================================
# 8. METADATA QUERY HELPERS
# ----------------------------------------------------------------------------------------------------
# Utilities to query G01d metadata on widgets.
# ====================================================================================================

def get_g01d_role(widget: tk.Widget) -> str | None:
    """
    Get the semantic role of a G01d-created widget.

    Returns:
        Role string (e.g., "page_title", "body_text") or None if not a G01d widget.
    """
    return getattr(widget, "g01d_role", None)


def get_default_pady(widget: tk.Widget) -> tuple[int, int] | None:
    """
    Get the default vertical padding for a G01d widget.

    Returns:
        (top_padding, bottom_padding) tuple or None.
    """
    return getattr(widget, "g01d_default_pady", None)


def is_g01d_widget(widget: tk.Widget) -> bool:
    """Check if a widget was created by G01d."""
    return hasattr(widget, "g01d_role")


# ====================================================================================================
# 9. SELF-TEST / DEMO
# ====================================================================================================
def demo() -> None:
    """
    Visual demonstration of all G01d layout primitives.
    """
    logger.info("=== G01d_layout_primitives v2 demo start ===")

    from gui.G01b_style_engine import configure_ttk_styles

    root = tk.Tk()
    root.title("G01d Layout Primitives v2 — Demo")
    root.geometry("900x700")
    root.configure(bg=GUI_COLOUR_BG_PRIMARY)

    style = ttk.Style(root)
    configure_ttk_styles(style)

    # Main container
    main = ttk.Frame(root, padding=16, style="TFrame")
    main.pack(fill="both", expand=True)

    # -------------------------------------------------------------------------
    # Typography Section
    # -------------------------------------------------------------------------
    page_title(main, "G01d Layout Primitives — Typography Hierarchy").pack(anchor="w", pady=(0, 12))
    
    body_text(
        main,
        "This demo shows all typography primitives in the semantic hierarchy.",
        wraplength=600,
    ).pack(anchor="w", pady=(0, 16))

    # Section with card inside
    section_title(main, "Typography Examples").pack(anchor="w", pady=(8, 4))
    
    card_frame = ttk.Frame(main, padding=12, style="SectionBody.TFrame")
    card_frame.pack(fill="x", pady=(0, 12))
    
    card_title(card_frame, "Card Title Example", surface="Secondary").pack(anchor="w", pady=(0, 4))
    body_text(card_frame, "This is body text inside a card.", surface="Secondary").pack(anchor="w")
    caption(card_frame, "This is caption text — smaller and lighter.", surface="Secondary").pack(anchor="w", pady=(4, 0))
    code_text(card_frame, "/usr/local/bin/python3", surface="Secondary").pack(anchor="w", pady=(8, 0))

    divider(main).pack(fill="x", pady=12)

    # -------------------------------------------------------------------------
    # Layout Helpers Section
    # -------------------------------------------------------------------------
    section_title(main, "Layout Helpers").pack(anchor="w", pady=(0, 4))

    # Label-value pairs
    label_value_pair(main, "Status", "Connected").pack(anchor="w", pady=2)
    label_value_pair(main, "Version", "1.0.0").pack(anchor="w", pady=2)
    label_value_pair(main, "Last Updated", "2025-11-28").pack(anchor="w", pady=2)

    spacer(main, height=12).pack(fill="x")

    # Bullet list
    body_text(main, "Feature highlights:").pack(anchor="w", pady=(0, 4))
    bullet_list(main, [
        "Semantic typography hierarchy",
        "Built-in spacing defaults",
        "Metadata for programmatic queries",
        "Legacy compatibility aliases",
    ]).pack(anchor="w", pady=(0, 8))

    spacer(main, height=8).pack(fill="x")

    # Icon text examples
    body_text(main, "Status indicators:").pack(anchor="w", pady=(0, 4))
    icon_text(main, "✓", "All systems operational").pack(anchor="w", pady=2)
    icon_text(main, "⚠", "Minor issues detected", weight="Bold").pack(anchor="w", pady=2)
    icon_text(main, "ℹ", "For more info, see documentation").pack(anchor="w", pady=2)

    divider(main).pack(fill="x", pady=12)

    # -------------------------------------------------------------------------
    # Indentation Example
    # -------------------------------------------------------------------------
    section_title(main, "Indentation & Structure").pack(anchor="w", pady=(0, 4))
    body_text(main, "Parent content here.").pack(anchor="w")
    
    indented = indent_block(main, indent=24)
    indented.pack(fill="x", pady=(4, 0))
    body_text(indented, "This content is indented.").pack(anchor="w")
    caption(indented, "Nested caption text.").pack(anchor="w")

    logger.info("=== G01d_layout_primitives v2 demo ready ===")
    root.mainloop()
    logger.info("=== G01d_layout_primitives v2 demo end ===")


# ====================================================================================================
# 10. MAIN GUARD
# ====================================================================================================
if __name__ == "__main__":
    init_logging()
    demo()