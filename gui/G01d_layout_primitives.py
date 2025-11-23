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
#       e.g., SectionHeading.TLabel, Heading2.TLabel, Body.TLabel
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
#   - Metadata (_g01d_padding / _g01d_anchor) is attached for G02 layout helpers.
#   - No creation of windows or geometry usage inside primitives.
#
# Notes:
#   - Highly stable primitives used in all G03 page construction.
#   - Debugging is available via DEBUG_LAYOUT_PRIMITIVES flag.
#   - Self-test demo (_demo) is developer-only and isolated under __main__.
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
from gui.G00a_gui_packages import tk, ttk, tkFont, scrolledtext
from gui.G01a_style_config import *

DEBUG_LAYOUT_PRIMITIVES = True


# ====================================================================================================
# 3. CORE PRIMITIVES
# ----------------------------------------------------------------------------------------------------
def heading(
    parent: ttk.Widget | tk.Widget,
    text: str,
    *,
    style: str = "SectionHeading.TLabel",
    padding: tuple[int, int, int, int] | None = None,
    anchor: str = "w",
) -> ttk.Label:
    """
    Create a primary heading label for section titles.

    This is typically used at the top of a logical section or panel, and is expected
    to use a dedicated heading style (e.g. SectionHeading.TLabel) provided by
    G01a_style_engine.configure_ttk_styles(...).

    Args:
        parent:
            Parent widget (Frame, TFrame, etc.) that will contain the heading.
        text:
            Heading text to display.
        style:
            ttk style name (default: 'SectionHeading.TLabel').
        padding:
            Optional (left, top, right, bottom) padding metadata to inform layout code.
            This function does NOT call pack/grid/place — the caller is responsible.
        anchor:
            Logical alignment metadata ('w', 'center', 'e', etc.). Not used directly
            by this function but stored on the widget for layout helpers.

    Returns:
        ttk.Label:
            Unpacked label instance with metadata attributes:
                • _g01d_padding
                • _g01d_anchor
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01c] Creating heading: %r (style=%s)", text, style)

    lbl = ttk.Label(parent, text=text, style=style)
    # Padding & anchor are for the caller's chosen geometry manager
    lbl._g01d_padding = padding  # type: ignore[attr-defined]
    lbl._g01d_anchor = anchor    # type: ignore[attr-defined]
    return lbl


def subheading(
    parent: ttk.Widget | tk.Widget,
    text: str,
    *,
    style: str = "Heading2.TLabel",
    padding: tuple[int, int, int, int] | None = None,
    anchor: str = "w",
) -> ttk.Label:
    """
    Create a secondary heading label (e.g., subsection title).

    Subheadings are intended for use within a section to group related controls or
    smaller logical blocks, typically using a slightly smaller or lighter style than
    the main section heading.

    Args:
        parent:
            Parent widget that will contain the subheading.
        text:
            Sub-heading text.
        style:
            ttk style name (default: 'Heading2.TLabel').
        padding:
            Optional padding metadata stored on the widget for external layout helpers.
        anchor:
            Logical alignment metadata (for layout helpers).

    Returns:
        ttk.Label:
            Unpacked label instance with _g01d_padding and _g01d_anchor metadata.
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01c] Creating subheading: %r (style=%s)", text, style)

    lbl = ttk.Label(parent, text=text, style=style)
    lbl._g01d_padding = padding  # type: ignore[attr-defined]
    lbl._g01d_anchor = anchor    # type: ignore[attr-defined]
    return lbl


def body_text(
    parent: ttk.Widget | tk.Widget,
    text: str,
    *,
    style: str = "Body.TLabel",
    wraplength: int | None = None,
    justify: str = "left",
) -> ttk.Label:
    """
    Create a standard body text label.

    Body text is used for descriptive copy, helper text, and instructions. The style
    is expected to be a neutral text style (e.g. Body.TLabel) provided by the theme.

    Args:
        parent:
            Parent widget.
        text:
            Body text content.
        style:
            ttk style name (default: 'Body.TLabel').
        wraplength:
            Optional wrap length in pixels. When set, long lines will wrap instead
            of overflowing horizontally.
        justify:
            Text justification for multi-line text ('left', 'center', or 'right').

    Returns:
        ttk.Label:
            Unpacked label instance with the specified style and wrapping behaviour.
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01c] Creating body_text: %r (style=%s)", text, style)

    kwargs: dict[str, Any] = {
        "text": text,
        "style": style,
        "justify": justify,
    }
    if wraplength is not None:
        kwargs["wraplength"] = wraplength

    lbl = ttk.Label(parent, **kwargs)
    return lbl


def divider(
    parent: ttk.Widget | tk.Widget,
    *,
    orient: Literal["horizontal", "vertical"] = "horizontal",
    padding: tuple[int, int] | None = None,
) -> ttk.Separator:
    """
    Create a simple divider line using ttk.Separator.

    Dividers are useful for visually separating groups of controls or sections within
    a layout without introducing extra frames or complex styling.

    Args:
        parent:
            Parent widget.
        orient:
            Separator orientation: 'horizontal' or 'vertical'.
        padding:
            Optional (padx, pady) metadata. The divider itself does not apply padding;
            layout helpers can use this metadata to decide how to pack/grid the widget.

    Returns:
        ttk.Separator:
            Unpacked separator instance with _g01d_padding metadata.
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01c] Creating divider (orient=%s)", orient)

    sep = ttk.Separator(parent, orient=orient)
    sep._g01d_padding = padding  # type: ignore[attr-defined]
    return sep


def spacer(
    parent: ttk.Widget | tk.Widget,
    *,
    height: int = 8,
) -> tk.Frame:
    """
    Create a fixed-height vertical spacer using a plain tk.Frame.

    A spacer introduces breathing room between stacked widgets without requiring
    magic numbers inside pack/grid calls. Because a plain tk.Frame is used, we can
    safely set a background colour without impacting ttk theme behaviour.

    Args:
        parent:
            Parent widget.
        height:
            Height in pixels for the spacer.

    Returns:
        tk.Frame:
            Unpacked Frame instance with the specified fixed height.
    """
    if DEBUG_LAYOUT_PRIMITIVES:
        logger.debug("[G01c] Creating spacer (height=%d)", height)

    frame = tk.Frame(
        parent,
        height=height,
        bd=0,
        highlightthickness=0,
        bg=GUI_COLOUR_BG_PRIMARY,
    )
    # Prevent the frame from shrinking to fit children (there are none)
    frame.pack_propagate(False)
    return frame


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
    """
    logger.info("[G01c] attach_primitives: Attaching layout primitives to %s", ui_cls.__name__)

    def _ui_heading(self, parent, text: str, **kwargs):
        return heading(parent, text, **kwargs)

    def _ui_subheading(self, parent, text: str, **kwargs):
        return subheading(parent, text, **kwargs)

    def _ui_body_text(self, parent, text: str, **kwargs):
        return body_text(parent, text, **kwargs)

    def _ui_divider(self, parent, **kwargs):
        return divider(parent, **kwargs)

    def _ui_spacer(self, parent, **kwargs):
        return spacer(parent, **kwargs)

    setattr(ui_cls, "heading", _ui_heading)
    setattr(ui_cls, "subheading", _ui_subheading)
    setattr(ui_cls, "body_text", _ui_body_text)
    setattr(ui_cls, "divider", _ui_divider)
    setattr(ui_cls, "spacer", _ui_spacer)

    logger.info("[G01c] attach_primitives: Layout primitives attached successfully.")


# ====================================================================================================
# 5. SELF-TEST / ENHANCED DEMO
# ----------------------------------------------------------------------------------------------------
def _demo() -> None:
    """
    Enhanced standalone demo to visualise the layout primitives in isolation.

    Behaviour:
        - Attempts to use G01a_style_engine.configure_ttk_styles(...) to apply
          the full project theme.
        - If G01a is not available, falls back to minimal local styles so the
          demo remains usable.
        - Demonstrates:
            • heading / subheading / body_text
            • divider / spacer
            • Basic grid and pack layouts
    """
    logger.info("=== G01d_layout_primitives demo start ===")

    root = tk.Tk()
    root.title("G01c Layout Primitives Demo")
    root.geometry("780x520")
    root.configure(bg=GUI_COLOUR_BG_PRIMARY)

    # -----------------------------------------------------------------------------------------------
    # 5.1 Style initialisation
    # -----------------------------------------------------------------------------------------------
    style = ttk.Style(root)

    # Try to use the main style engine if available
    try:
        from gui.G01a_style_engine import configure_ttk_styles  # type: ignore[import]

        logger.info("[G01c] Demo: Applying styles via G01a_style_engine.configure_ttk_styles.")
        configure_ttk_styles(style)  # type: ignore[arg-type]
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "[G01c] Demo: Failed to import/apply G01a_style_engine; "
            "falling back to lightweight local styles. Error: %s",
            exc,
        )
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Determine a safe base font from your project config
        try:
            base_family = GUI_FONT_FAMILY[0]  # type: ignore[index]
        except Exception:
            base_family = "Segoe UI"

        # Minimal styles to keep the demo legible
        style.configure("SectionHeading.TLabel", font=(base_family, 14, "bold"))
        style.configure("Heading2.TLabel", font=(base_family, 12, "bold"))
        style.configure("Body.TLabel", font=(base_family, 10))

    # -----------------------------------------------------------------------------------------------
    # 5.2 Layout: top-level container with two columns
    # -----------------------------------------------------------------------------------------------
    outer = ttk.Frame(root, padding=20)
    outer.pack(fill="both", expand=True)

    outer.columnconfigure(0, weight=1)
    outer.columnconfigure(1, weight=1)
    outer.rowconfigure(0, weight=1)

    # Left column: primitive showcase
    left = ttk.Frame(outer)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    # Right column: usage notes / examples
    right = ttk.Frame(outer)
    right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    # -----------------------------------------------------------------------------------------------
    # 5.3 Left column – visual primitives
    # -----------------------------------------------------------------------------------------------
    heading(left, "Layout Primitives — Visual Example").pack(anchor="w", pady=(0, 8))

    subheading(left, "Headings & Text").pack(anchor="w", pady=(0, 4))

    body_text(
        left,
        "Use heading(...) for primary section titles and subheading(...) for "
        "subsections within a block. body_text(...) is ideal for explanatory "
        "copy that may need wrapping.",
        wraplength=340,
    ).pack(anchor="w", pady=(0, 8))

    divider(left).pack(fill="x", pady=(4, 8))

    subheading(left, "Stacked Content With Spacers").pack(anchor="w", pady=(0, 4))

    body_text(
        left,
        "Spacers are simple fixed-height frames that introduce breathing room "
        "between groups of widgets without embedding magic numbers into pack/grid "
        "calls.",
        wraplength=340,
    ).pack(anchor="w", pady=(0, 6))

    spacer(left, height=12).pack(fill="x")

    body_text(
        left,
        "Below is another block of text separated by a spacer and a divider:",
        wraplength=340,
    ).pack(anchor="w", pady=(6, 4))

    divider(left).pack(fill="x", pady=(4, 8))

    body_text(
        left,
        "End of left column demo.",
        wraplength=340,
    ).pack(anchor="w", pady=(0, 0))

    # -----------------------------------------------------------------------------------------------
    # 5.4 Right column – usage examples (code-style text)
    # -----------------------------------------------------------------------------------------------
    heading(right, "How to Use These Primitives").pack(anchor="w", pady=(0, 8))

    body_text(
        right,
        "The primitives are intentionally thin wrappers around tk/ttk widgets. "
        "They do not perform any layout — you still choose pack/grid/place. "
        "They only standardise styling and attach light metadata.",
        wraplength=340,
    ).pack(anchor="w", pady=(0, 8))

    subheading(right, "Example: Section Block").pack(anchor="w", pady=(0, 4))

    body_text(
        right,
        "Typical usage pattern for a section might look like:",
        wraplength=340,
    ).pack(anchor="w", pady=(0, 4))

    # Use a plain tk.Text as a code-style box (keeps demo simple)
    code_box = tk.Text(
        right,
        height=8,
        wrap="word",
        bd=0,
        relief="solid",
        padx=8,
        pady=6,
        background=GUI_COLOUR_BG_SECONDARY,
    )
    code_box.pack(fill="both", expand=False, pady=(0, 8))

    code_example = (
        "from gui.G01d_layout_primitives import heading, subheading, body_text, divider, spacer\n\n"
        "section = ttk.Frame(parent)\n"
        "section.pack(fill='x', padx=8, pady=8)\n\n"
        "heading(section, 'Connection Settings').pack(anchor='w')\n"
        "subheading(section, 'Account details').pack(anchor='w', pady=(4, 2))\n"
        "body_text(section, 'Enter your credentials and connection parameters.', "
        "wraplength=320).pack(anchor='w', pady=(0, 6))\n"
        "divider(section).pack(fill='x', pady=(4, 8))\n"
        "spacer(section, height=12).pack(fill='x')\n"
    )
    code_box.insert("1.0", code_example)
    code_box.configure(state="disabled")

    subheading(right, "Metadata for Layout Helpers").pack(anchor="w", pady=(4, 4))

    body_text(
        right,
        "heading(...) and subheading(...) attach _g01d_padding and _g01d_anchor "
        "metadata to their label instances. Future layout helpers can use this "
        "metadata to apply consistent spacing rules.",
        wraplength=340,
    ).pack(anchor="w", pady=(0, 8))

    body_text(
        right,
        "Try resizing the window to see how both columns grow. This module "
        "focuses only on primitive building blocks; higher-level patterns live "
        "in other G01x/G02x/G03x modules.",
        wraplength=340,
    ).pack(anchor="w", pady=(0, 0))

    logger.info("=== G01d_layout_primitives demo end ===")
    root.mainloop()


# ====================================================================================================
# 6. MAIN GUARD
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    _demo()
