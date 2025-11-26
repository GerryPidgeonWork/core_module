# ====================================================================================================
# G01d_layout_primitives.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Provide LOW-LEVEL, STYLE-AWARE LAYOUT BUILDING BLOCKS used across all GUI pages.
#
#   These primitives build *structure*, not widgets:
#       • heading(...)      – Section-level heading label (style-driven)
#       • subheading(...)   – Subsection label
#       • body_text(...)    – Standard body/description text
#       • divider(...)      – Horizontal/vertical separators
#       • spacer(...)       – Fixed-height empty space for vertical rhythm
#
# Architectural Role:
#   - Sits BELOW widget primitives (G01c) and ABOVE the layout framework (G02).
#   - Does NOT create GUI structure (frames/pages) and does NOT apply geometry.
#   - Produces consistent, theme-bound building blocks for any page layout.
#
# Integration:
#   - Styles come from G01b_style_engine.configure_ttk_styles(...)
#       e.g., SectionHeading.TLabel, Secondary.Bold.TLabel, Secondary.Normal.TLabel
#   - Can optionally attach to a UI-factory class via:
#         attach_primitives(UIComponents)
#     allowing clean usage:
#         ui.heading(parent, "Title")
#         ui.subheading(parent, "Block")
#         ui.body_text(parent, "Explain…")
#         ui.divider(parent)
#         ui.spacer(parent)
#
# Rules:
#   - NO direct ttkbootstrap widget subclasses.
#   - NO unsupported ttk options (e.g., background= on ttk widgets).
#   - ZERO side effects at import time.
#   - Metadata (g01d_padding / g01d_anchor) is attached for G02 layout helpers.
#   - No creation of windows or geometry usage inside primitives.
#
# Notes:
#   - Highly stable primitives used in all G03 page construction.
#   - Debugging is available via DEBUG_LAYOUT_PRIMITIVES flag.
#   - Self-test demo (demo) is developer-only and isolated under __main__.
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
from gui.G01a_style_config import *
from gui.G01c_widget_primitives import (
    make_label,
    make_divider as g01c_make_divider,
    make_spacer as g01c_make_spacer,
)


DEBUG_LAYOUT_PRIMITIVES = False


# ====================================================================================================
# 3. CORE PRIMITIVES
# ----------------------------------------------------------------------------------------------------
# These primitives wrap G01c widget functions and add layout-specific metadata.
# They provide a semantic layer for building page structure.
# ----------------------------------------------------------------------------------------------------

def heading(
    parent: ttk.Widget | tk.Widget,
    text: str,
    *,
    surface: str = "Primary",
    weight: str = "Bold",
    padding: tuple[int, int, int, int] | None = None,
    anchor: str = "w",
    **kwargs: Any,
) -> ttk.Label:
    """
    Create a section heading label for page/panel titles.

    Description:
        Wraps G01c.make_label() with category="SectionHeading" and attaches
        layout metadata (g01d_padding, g01d_anchor) for G02 layout helpers.

    Args:
        parent (ttk.Widget | tk.Widget):
            Parent widget (Frame, TFrame, etc.) that will contain the heading.
        text (str):
            Heading text to display.
        surface (str):
            Background surface context. "Primary" or "Secondary". Default: "Primary".
        weight (str):
            Font weight. "Normal" or "Bold". Default: "Bold".
        padding (tuple[int, int, int, int] | None):
            Optional (left, top, right, bottom) padding metadata for G02 helpers.
        anchor (str):
            Logical alignment metadata ('w', 'center', 'e', etc.). Stored but not applied.
        **kwargs (Any):
            Additional options passed to make_label().

    Returns:
        ttk.Label:
            Label instance with metadata:
                • g01d_padding
                • g01d_anchor

    Raises:
        None.

    Notes:
        - The caller must still apply pack/grid/place.
        - Layout helpers may inspect g01d_padding / g01d_anchor for spacing rules.
        - Style generated: "{surface}.SectionHeading.{weight}.TLabel"
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] Creating heading: %r (surface=%s, weight=%s)", text, surface, weight)

    lbl = make_label(parent, text, category="SectionHeading", surface=surface, weight=weight, **kwargs)
    lbl.g01d_padding = padding  # type: ignore[attr-defined]
    lbl.g01d_anchor = anchor    # type: ignore[attr-defined]
    return lbl


def subheading(
    parent: ttk.Widget | tk.Widget,
    text: str,
    *,
    surface: str = "Primary",
    weight: str = "Bold",
    padding: tuple[int, int, int, int] | None = None,
    anchor: str = "w",
    **kwargs: Any,
) -> ttk.Label:
    """
    Create a subsection heading (bold label).

    Description:
        Wraps G01c.make_label() with category="Body" and bold weight.
        Used for smaller headings within sections.

    Args:
        parent (ttk.Widget | tk.Widget):
            Parent widget that will contain the subheading.
        text (str):
            Subheading text.
        surface (str):
            Background surface context. "Primary" or "Secondary". Default: "Primary".
        weight (str):
            Font weight. "Normal" or "Bold". Default: "Bold".
        padding (tuple[int, int, int, int] | None):
            Optional padding metadata for layout helpers.
        anchor (str):
            Logical alignment metadata for layout helpers.
        **kwargs (Any):
            Additional options passed to make_label().

    Returns:
        ttk.Label:
            Label instance with metadata.

    Raises:
        None.

    Notes:
        - g01d_padding / g01d_anchor are stored but not applied.
        - Caller chooses pack/grid.
        - Style generated: "{surface}.{weight}.TLabel"
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] Creating subheading: %r (surface=%s, weight=%s)", text, surface, weight)

    lbl = make_label(parent, text, category="Body", surface=surface, weight=weight, **kwargs)
    lbl.g01d_padding = padding  # type: ignore[attr-defined]
    lbl.g01d_anchor = anchor    # type: ignore[attr-defined]
    return lbl


def body_text(
    parent: ttk.Widget | tk.Widget,
    text: str,
    *,
    surface: str = "Primary",
    weight: str = "Normal",
    wraplength: int | None = None,
    justify: str = "left",
    **kwargs: Any,
) -> ttk.Label:
    """
    Create standard body text for general descriptive content.

    Description:
        Wraps G01c.make_label() with category="Body" for paragraph/descriptive text.

    Args:
        parent (ttk.Widget | tk.Widget):
            Parent widget.
        text (str):
            Text content.
        surface (str):
            Background surface context. "Primary" or "Secondary". Default: "Primary".
        weight (str):
            Font weight. "Normal" or "Bold". Default: "Normal".
        wraplength (int | None):
            Optional wrap length in pixels.
        justify (str):
            Text justification: 'left', 'center', or 'right'. Default: "left".
        **kwargs (Any):
            Additional options passed to make_label().

    Returns:
        ttk.Label:
            Label instance.

    Raises:
        None.

    Notes:
        - No g01d_* metadata attached; layout is explicit via pack/grid.
        - Style generated: "{surface}.{weight}.TLabel"
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] Creating body_text: %r (surface=%s, weight=%s)", text, surface, weight)

    # Build extra kwargs for make_label
    if wraplength is not None:
        kwargs["wraplength"] = wraplength
    kwargs["justify"] = justify

    return make_label(parent, text, category="Body", surface=surface, weight=weight, **kwargs)


def divider(
    parent: ttk.Widget | tk.Widget,
    *,
    orient: Literal["horizontal", "vertical"] = "horizontal",
    height: int = 1,
    padding: tuple[int, int] | None = None,
) -> ttk.Frame:
    """
    Create a simple divider line (thin separator).

    Description:
        Wraps G01c.make_divider() and attaches layout metadata.
        For vertical dividers, uses width instead of height.

    Args:
        parent (ttk.Widget | tk.Widget):
            Parent widget.
        orient (Literal["horizontal", "vertical"]):
            Orientation: 'horizontal' or 'vertical'. Default: "horizontal".
        height (int):
            Thickness in pixels. Default: 1.
        padding (tuple[int, int] | None):
            Optional (padx, pady) metadata for G02 helpers.

    Returns:
        ttk.Frame:
            Divider frame with g01d_padding metadata.

    Raises:
        None.

    Notes:
        - Uses ToolbarDivider.TFrame style from G01b.
        - Horizontal dividers use height; vertical dividers use width.
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] Creating divider (orient=%s, height=%d)", orient, height)

    if orient == "vertical":
        # For vertical dividers, create a frame with width instead of height
        div = ttk.Frame(parent, width=height, style="ToolbarDivider.TFrame")
    else:
        div = g01c_make_divider(parent, height=height)
    
    div.g01d_padding = padding  # type: ignore[attr-defined]
    return div


def spacer(
    parent: ttk.Widget | tk.Widget,
    *,
    height: int = 8,
) -> ttk.Frame:
    """
    Create a fixed-height vertical spacer.

    Description:
        Wraps G01c.make_spacer() for vertical rhythm between content blocks.

    Args:
        parent (ttk.Widget | tk.Widget):
            Parent widget.
        height (int):
            Spacer height in pixels. Default: 8.

    Returns:
        ttk.Frame:
            Fixed-height spacer frame.

    Raises:
        None.

    Notes:
        - Uses TFrame style from G01b for consistent theming.
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01d] Creating spacer (height=%d)", height)

    return g01c_make_spacer(parent, height=height)


# ====================================================================================================
# 4. OPTIONAL: ATTACH TO A UI FACTORY CLASS
# ----------------------------------------------------------------------------------------------------
def attach_primitives(ui_cls: Type[Any]) -> None:
    """
    Monkey-patch layout primitives onto a UIComponents-like class.

    This is purely optional, but useful if you maintain a central UI factory:

        class UIComponents:
            def __init__(self, root: tk.Tk | tk.Toplevel):
                self.root = root
                self.style = ttk.Style(root)

        from gui.G01d_layout_primitives import attach_primitives
        attach_primitives(UIComponents)

    After which you can use:

        ui.heading(parent, "Title")
        ui.subheading(parent, "Subtitle")
        ui.body_text(parent, "Some text...")
        ui.divider(parent)
        ui.spacer(parent, height=12)

    The attached methods are thin wrappers over the standalone functions above.

    Args:
        ui_cls:
            Class object to which the primitives should be attached. Typically a
            UI factory or helper class (e.g., UIComponents).

    Returns:
        None.

    Notes:
        - This function mutates ui_cls by adding methods at runtime.
    """
    logger.info("[G01d] attach_primitives: Attaching layout primitives to %s", ui_cls.__name__)

    def ui_heading(self, parent, text: str, **kwargs):
        return heading(parent, text, **kwargs)

    def ui_subheading(self, parent, text: str, **kwargs):
        return subheading(parent, text, **kwargs)

    def ui_body_text(self, parent, text: str, **kwargs):
        return body_text(parent, text, **kwargs)

    def ui_divider(self, parent, **kwargs):
        return divider(parent, **kwargs)

    def ui_spacer(self, parent, **kwargs):
        return spacer(parent, **kwargs)

    setattr(ui_cls, "heading", ui_heading)
    setattr(ui_cls, "subheading", ui_subheading)
    setattr(ui_cls, "body_text", ui_body_text)
    setattr(ui_cls, "divider", ui_divider)
    setattr(ui_cls, "spacer", ui_spacer)

    logger.info("[G01d] attach_primitives: Layout primitives attached successfully.")


# ====================================================================================================
# 5. SELF-TEST / ENHANCED DEMO
# ----------------------------------------------------------------------------------------------------
def demo() -> None:
    """
    Standalone demo to visualise the layout primitives.

    Description:
        Creates a two-column layout demonstrating all layout primitives
        with proper styling from G01b.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Intended for developer diagnostics and visual inspection only.
        - Uses G01b_style_engine.configure_ttk_styles() for full theme support.
    """
    logger.info("=== G01d_layout_primitives demo start ===")

    root = tk.Tk()
    root.title("G01d Layout Primitives Demo")
    root.geometry("800x600")
    root.configure(bg=GUI_COLOUR_BG_PRIMARY)

    # -----------------------------------------------------------------------------------------------
    # Style initialisation
    # -----------------------------------------------------------------------------------------------
    style = ttk.Style(root)

    try:
        from gui.G01b_style_engine import configure_ttk_styles
        logger.info("[G01d] Demo: Applying styles via G01b_style_engine.")
        configure_ttk_styles(style)
    except Exception as exc:
        logger.warning("[G01d] Demo: Failed to apply G01b styles: %s", exc)
        style.theme_use("clam")

    # -----------------------------------------------------------------------------------------------
    # Main container with two columns
    # -----------------------------------------------------------------------------------------------
    outer = ttk.Frame(root, padding=10, style="SectionOuter.TFrame")
    outer.pack(fill="both", expand=True)

    outer.columnconfigure(0, weight=1)
    outer.columnconfigure(1, weight=0)
    outer.columnconfigure(2, weight=1)
    outer.rowconfigure(0, weight=1)

    # -----------------------------------------------------------------------------------------------
    # Left column — Secondary surface demo
    # -----------------------------------------------------------------------------------------------
    left = ttk.Frame(outer, style="SectionBody.TFrame", padding=10)
    left.grid(row=0, column=0, sticky="nsew")

    heading(left, "Layout Primitives — Secondary Surface", surface="Secondary").pack(
        anchor="w", pady=(0, 8)
    )

    subheading(left, "Headings & Text", surface="Secondary").pack(anchor="w", pady=(0, 4))

    body_text(
        left,
        "Use heading(...) for section titles and subheading(...) for "
        "subsections. body_text(...) is for explanatory content.",
        surface="Secondary",
        wraplength=340,
    ).pack(anchor="w", pady=(0, 8))

    divider(left).pack(fill="x", pady=(4, 8))

    subheading(left, "Spacers & Dividers", surface="Secondary").pack(anchor="w", pady=(0, 4))

    body_text(
        left,
        "Spacers create vertical breathing room. Dividers separate content blocks visually.",
        surface="Secondary",
        wraplength=340,
    ).pack(anchor="w", pady=(0, 6))

    spacer(left, height=12).pack(fill="x")

    body_text(
        left,
        "This text follows a 12px spacer.",
        surface="Secondary",
        wraplength=340,
    ).pack(anchor="w", pady=(6, 4))

    divider(left).pack(fill="x", pady=(4, 8))

    body_text(left, "End of left column.", surface="Secondary").pack(anchor="w")

    # -----------------------------------------------------------------------------------------------
    # Vertical divider between columns
    # -----------------------------------------------------------------------------------------------
    divider_col = tk.Frame(outer, width=1, bg=GUI_COLOUR_DIVIDER)
    divider_col.grid(row=0, column=1, sticky="ns", padx=4)

    # -----------------------------------------------------------------------------------------------
    # Right column — Primary surface demo
    # -----------------------------------------------------------------------------------------------
    right = ttk.Frame(outer, style="TFrame", padding=10)
    right.grid(row=0, column=2, sticky="nsew")

    heading(right, "How to Use These Primitives", surface="Primary").pack(
        anchor="w", pady=(0, 8)
    )

    body_text(
        right,
        "The primitives wrap G01c widgets and add layout metadata. "
        "They standardise styling while you choose pack/grid/place.",
        surface="Primary",
        wraplength=340,
    ).pack(anchor="w", pady=(0, 8))

    subheading(right, "Example Usage", surface="Primary").pack(anchor="w", pady=(0, 4))

    body_text(
        right,
        "Typical usage pattern:",
        surface="Primary",
        wraplength=340,
    ).pack(anchor="w", pady=(0, 4))

    # Code example box
    code_box = tk.Text(
        right,
        height=10,
        wrap="word",
        bd=0,
        padx=8,
        pady=6,
        font=(GUI_FONT_FAMILY[0], GUI_FONT_SIZE_DEFAULT),
        foreground=TEXT_COLOUR_SECONDARY,
        background=GUI_COLOUR_BG_SECONDARY,
        highlightthickness=1,
        highlightbackground=GUI_COLOUR_DIVIDER,
    )
    code_box.pack(fill="x", pady=(0, 8))

    code_example = """\
from gui.G01d_layout_primitives import (
    heading, subheading, body_text, divider, spacer
)

section = ttk.Frame(parent, style='SectionBody.TFrame')
section.pack(fill='x', padx=8, pady=8)

heading(section, 'Settings', surface='Secondary').pack(anchor='w')
subheading(section, 'Account', surface='Secondary').pack(anchor='w')
body_text(section, 'Enter credentials.', surface='Secondary').pack(anchor='w')
divider(section).pack(fill='x', pady=8)
spacer(section, height=12).pack(fill='x')
"""
    code_box.insert("1.0", code_example)
    code_box.configure(state="disabled")

    subheading(right, "Metadata for Layout Helpers", surface="Primary").pack(
        anchor="w", pady=(4, 4)
    )

    body_text(
        right,
        "heading() and subheading() attach g01d_padding and g01d_anchor "
        "metadata. Layout helpers (G02) can use this for consistent spacing.",
        surface="Primary",
        wraplength=340,
    ).pack(anchor="w", pady=(0, 8))

    body_text(
        right,
        "Try resizing the window to see responsive behaviour.",
        surface="Primary",
        wraplength=340,
    ).pack(anchor="w")

    logger.info("=== G01d_layout_primitives demo ready ===")
    root.mainloop()
    logger.info("=== G01d_layout_primitives demo end ===")


# ====================================================================================================
# 6. MAIN GUARD
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging()
    demo()