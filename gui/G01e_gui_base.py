# ====================================================================================================
# G01e_gui_base.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Defines the standardised BaseGUI root-window class used by ALL GUI windows
#   in the framework. This module provides the *window shell*, scroll engine,
#   and visual bootstrap layer — leaving actual content/layout to subclasses.
#
#   Core responsibilities:
#       • Initialise Tk root window (title, geometry, background, minsize).
#       • Construct the global ttk/ttkbootstrap Style and delegate all widget
#         styling to G01b_style_engine.configure_ttk_styles(...).
#       • Provide a scrollable main content area using:
#             Canvas  → vertical Scrollbar → inner ttk.Frame
#         All pages attach widgets ONLY to self.main_frame.
#       • Implement cross-platform scrolling:
#             - Global scroll → window-wide Canvas scroll
#             - Per-widget scroll overrides via bind_scroll_widget(...) for
#               widgets with their own yview (Text, ScrolledText, Listbox, etc.)
#       • Provide utility helpers:
#             - center_window(...)
#             - open_fullscreen() / exit_fullscreen()
#             - close() / safe_close()
#
# Usage:
#   from gui.G01e_gui_base import BaseGUI
#
#   class MyWindow(BaseGUI):
#       def build_widgets(self):
#           ttk.Label(self.main_frame, text="Hello World").pack(pady=10)
#
#   if __name__ == "__main__":
#       MyWindow(title="Demo").mainloop()
#
# Architecture:
#   - G00a_style_config:
#         Colours, fonts, spacing, frame sizes (design tokens).
#   - G01a_style_engine:
#         Named fonts + ttk style definitions based on tokens.
#   - G01b/G01c/G01d:
#         Widget primitives, layout primitives, layout frameworks.
#   - G01e_gui_base (THIS MODULE):
#         The window shell + scroll engine + style initialisation.
#
# Rules:
#   - No business logic here.
#   - No creation of child widgets — subclasses override build_widgets().
#   - No geometry management inside primitives; only the shell is defined here.
#   - No direct external imports — everything goes through C00_set_packages.
#
# Debugging:
#   - Uses C03_logging_handler.get_logger for structured diagnostics.
#   - DEBUG_BASE_GUI toggles detailed scroll/style/environment logging.
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
from core.C02_system_processes import detect_os
from gui.G00a_gui_packages import tk, ttk, tkFont
from gui.G01a_style_config import *
from gui.G01b_style_engine import configure_ttk_styles

DEBUG_BASE_GUI: bool = True


# ====================================================================================================
# 3. BASE GUI CLASS
# ----------------------------------------------------------------------------------------------------
class BaseGUI(tk.Tk):  # type: ignore[name-defined]
    """
    Standardised Tkinter root window for all GUIs in the framework.

    Responsibilities:
        - Configure geometry, title, and base background.
        - Create ttk/ttkbootstrap Style and delegate all visual styling to
          configure_ttk_styles(...) in G01a_style_engine.
        - Provide a scrollable main content area (self.main_frame) embedded
          in a Canvas + vertical ttk Scrollbar.
        - Bind global mouse-wheel / trackpad scrolling for the main content.
        - Provide optional per-widget scroll override for .yview-capable widgets
          via bind_scroll_widget(...).
        - Offer overridable build_widgets() hook for child classes.

    Usage pattern:

        class MyWindow(BaseGUI):
            def build_widgets(self):
                ttk.Label(self.main_frame, text="Hello World").pack(pady=10)

        app = MyWindow(title="Demo")
        app.mainloop()
    """

    # ------------------------------------------------------------------------------------------------
    def __init__(
        self,
        title: str = FRAME_HEADING,
        width: int = FRAME_SIZE_H,
        height: int = FRAME_SIZE_V,
        resizable: bool = True,
    ):
        """
        Initialise the base window and apply visual standards.

        Args:
            title:
                Window title text (default: FRAME_HEADING from G00a_style_config).

            width:
                Initial window width in pixels (default: FRAME_SIZE_H).

            height:
                Initial window height in pixels (default: FRAME_SIZE_V).

            resizable:
                Whether the window can be resized by the user (both directions).
        """
        logger.info("=== BaseGUI.__init__ start ===")
        logger.debug(
            "[G01d] Requested window: title=%r width=%d height=%d resizable=%s",
            title,
            width,
            height,
            resizable,
        )

        super().__init__()

        # Allow the root window to resize fully
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Window configuration -------------------------------------------------------------------
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(bg=GUI_COLOUR_BG_PRIMARY)
        self.resizable(resizable, resizable)
        self.minsize(400, 300)

        logger.debug("[G01d] Base window configured (geometry, bg, resizable, minsize).")

        # --- Style configuration (ttk / ttkbootstrap) -----------------------------------------------
        self.style = self.configure_styles()

        # --- Scrollable root layout (Canvas + Scrollbar + main_frame) -------------------------------
        self.build_root_layout()
        logger.debug("[G01d] Root scrollable layout built (canvas + scrollbar + main_frame).")

        # --- Build actual window content ------------------------------------------------------------
        self.build_widgets()
        logger.debug("[G01d] build_widgets() hook executed.")

        # --- Center window on screen ----------------------------------------------------------------
        self.center_window(width, height)
        logger.debug("[G01d] Window centered on screen.")

        # --- Bind global mouse-wheel / trackpad scroll for main window ------------------------------
        self.bind_global_scroll()
        logger.debug("[G01d] Global scroll bindings applied.")

        # --- Optional debug diagnostics -------------------------------------------------------------
        if DEBUG_BASE_GUI:
            self.log_debug_diagnostics()

        logger.info("=== BaseGUI.__init__ complete ===")

    # =================================================================================================
    # 3.1 STYLE CONFIGURATION (DELEGATED TO G01a)
    # =================================================================================================
    def configure_styles(self) -> ttk.Style:  # type: ignore[name-defined]
        """
        Create and configure the ttk/ttkbootstrap Style instance for this window.

        Behaviour:
            - Attempts to resolve a working font from GUI_FONT_FAMILY (G00a_style_config).
            - Prefers ttkbootstrap.Style when available; otherwise falls back to ttk.Style.
            - Delegates all widget styling rules to configure_ttk_styles(style)
              in G01a_style_engine.
            - Ensures the window background colour aligns with GUI_COLOUR_BG_PRIMARY.

        Returns:
            The active ttk.Style instance for this window.
        """
        logger.info("[G01d] Configuring ttk/ttkbootstrap styles...")

        # --- Detect an installed font from the configured family sequence ---------------------------
        active_font_family: str | None = None
        font_candidates = (
            GUI_FONT_FAMILY
            if isinstance(GUI_FONT_FAMILY, (tuple, list))
            else [GUI_FONT_FAMILY]
        )
        logger.debug("[G01d] Font candidate sequence: %r", font_candidates)

        for fam in font_candidates:
            try:
                _ = tkFont.Font(family=fam, size=GUI_FONT_SIZE_DEFAULT)  # type: ignore[name-defined]
                active_font_family = fam
                logger.info("[G01d] Active GUI font family: %s", fam)
                break
            except Exception as exc:  # noqa: BLE001
                logger.debug("[G01d] Font '%s' not available: %s", fam, exc)

        if not active_font_family:
            # Fallback to a safe system default
            active_font_family = "Segoe UI"
            logger.warning(
                "[G01d] No configured fonts available; falling back to %s",
                active_font_family,
            )

        # Cache for downstream use if needed by subclasses
        self.active_font_family = active_font_family  # type: ignore[attr-defined]

        # --- Create Style (prefer ttkbootstrap.Style if available) ----------------------------------
        try:
            style = Style(theme="flatly")  # type: ignore[name-defined]
            logger.info("[G01d] Using ttkbootstrap.Style with theme 'flatly'.")
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "[G01d] ttkbootstrap Style not available (%s); falling back to ttk.Style",
                exc,
            )
            style = ttk.Style(self)  # type: ignore[call-arg]

        # --- Log and potentially normalise base theme ----------------------------------------------
        try:
            current_theme = style.theme_use()
            logger.info("[G01d] Initial style theme: %s", current_theme)
        except Exception as exc:  # noqa: BLE001
            logger.debug("[G01d] Could not query current theme: %s", exc)

        # For plain ttk, prefer a neutral theme where possible.
        try:
            style.theme_use("clam")
            logger.info("[G01d] Theme set to 'clam' for consistency.")
        except Exception as exc:  # noqa: BLE001
            logger.warning("[G01d] Failed to set theme 'clam': %s", exc)

        # --- Delegate all widget styling to G01a_style_engine --------------------------------------
        try:
            configure_ttk_styles(style)
            logger.info("[G01d] configure_ttk_styles(...) completed successfully.")
        except Exception as exc:  # noqa: BLE001
            logger.exception("[G01d] Error during configure_ttk_styles: %s", exc)

        # Align root background with theme
        self.configure(bg=GUI_COLOUR_BG_PRIMARY)

        return style

    # =================================================================================================
    # 3.2 ROOT LAYOUT (SCROLLABLE CONTENT AREA)
    # =================================================================================================
    def build_root_layout(self) -> None:
        """
        Build the scrollable root layout used by all GUIs.

        Structure:

            self (BaseGUI / Tk)
              └─ self.container (TFrame)
                   ├─ self.canvas (Canvas)
                   │    └─ window -> self.main_frame (TFrame)
                   └─ self.v_scrollbar (Vertical.TScrollbar)

        Notes:
            - All child GUIs must attach their widgets to self.main_frame.
            - The Canvas + Scrollbar combination provides vertical scrolling for
              content that exceeds the visible window height.
        """
        logger.debug("[G01d] Building root scrollable layout...")

        # Container holds both canvas and scrollbar
        self.container = ttk.Frame(self, padding=0)  # type: ignore[attr-defined]
        self.container.pack(fill=tk.BOTH, expand=True)

        # Ensure container expands horizontally
        self.container.columnconfigure(0, weight=1)

        # Canvas provides the scrollable area
        self.canvas = tk.Canvas(  # type: ignore[attr-defined]
            self.container,
            background=GUI_COLOUR_BG_PRIMARY,
            highlightthickness=0,
            bd=0,
        )

        # Vertical scrollbar (styled via G01a_style_engine)
        self.v_scrollbar = ttk.Scrollbar(  # type: ignore[attr-defined]
            self.container,
            orient="vertical",
            command=self.canvas.yview,
            style="Vertical.TScrollbar",
        )
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Main content frame inside the canvas
        self.main_frame = ttk.Frame(self.canvas, padding=FRAME_PADDING)  # type: ignore[attr-defined]

        # Allow main content frame to expand horizontally
        self.main_frame.columnconfigure(0, weight=1)

        self._canvas_window_id = self.canvas.create_window(  # type: ignore[attr-defined]
            (0, 0),
            window=self.main_frame,
            anchor="nw",
        )

        # Ensure scrollregion and width adjust automatically
        self.main_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    # ------------------------------------------------------------------------------------------------
    def on_frame_configure(self, event) -> None:
        """
        Update the scrollregion whenever the main_frame size changes.

        Behaviour:
            - The Canvas scrollregion is adjusted to the bounding box of all content.
            - This keeps the scrollbar in sync with the full scrollable height.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))  # type: ignore[attr-defined]

    # ------------------------------------------------------------------------------------------------
    def on_canvas_configure(self, event) -> None:
        """
        Keep the inner frame width in sync with the canvas width.

        Behaviour:
            - When the Canvas is resized horizontally (e.g. user resizes window),
              the embedded self.main_frame is stretched to match the new width.
            - This avoids horizontal scrollbars and supports responsive layouts.
        """
        canvas_width = event.width
        self.canvas.itemconfig(self._canvas_window_id, width=canvas_width)  # type: ignore[attr-defined]

        # Ensure main_frame stretches to full available width
        self.main_frame.configure(width=canvas_width)

    # =================================================================================================
    # 3.3 GLOBAL SCROLL BINDINGS (MAIN WINDOW)
    # =================================================================================================
    def bind_global_scroll(self) -> None:
        """
        Bind cross-platform mouse-wheel / trackpad scrolling for the main window.

        Behaviour:
            - When the user scrolls and the event is not intercepted by a child widget,
              the main Canvas (and therefore the whole window content) is scrolled.
            - Platform-specific event sequences:
                * Windows / macOS: <MouseWheel>
                * Linux / X11:     <Button-4> (up) / <Button-5> (down)
        """
        os_type = detect_os()
        logger.info("[G01d] Binding global scroll handlers for OS: %s", os_type)

        if os_type in ("Windows", "MacOS"):
            self.bind_all("<MouseWheel>", self.on_global_mousewheel)
        else:
            self.bind_all("<Button-4>", self.on_global_mousewheel_linux)
            self.bind_all("<Button-5>", self.on_global_mousewheel_linux)

    # ------------------------------------------------------------------------------------------------
    def on_global_mousewheel(self, event):
        """
        Handle mouse wheel scrolling for Windows and macOS at the window level.

        Behaviour:
            - Scrolls the main Canvas vertically.
            - Only used when no child widget intercepts the event
              (see bind_scroll_widget for per-widget overrides).
        """
        delta_raw = getattr(event, "delta", 0)
        delta = int(delta_raw / 120) if delta_raw else 0
        if delta != 0:
            self.canvas.yview_scroll(-delta, "units")  # type: ignore[attr-defined]

    # ------------------------------------------------------------------------------------------------
    def on_global_mousewheel_linux(self, event):
        """
        Handle mouse wheel scrolling on Linux using Button-4 / Button-5 events.

        Behaviour:
            - Button-4 → scroll up
            - Button-5 → scroll down
        """
        if event.num == 4:
            self.canvas.yview_scroll(-3, "units")  # type: ignore[attr-defined]
        elif event.num == 5:
            self.canvas.yview_scroll(3, "units")  # type: ignore[attr-defined]

    # =================================================================================================
    # 3.4 PER-WIDGET SCROLL OVERRIDE
    # =================================================================================================
    def bind_scroll_widget(self, widget) -> None:
        """
        Attach mouse-wheel / trackpad scrolling to a specific widget.

        When the cursor is over the widget:
            - Scroll events move that widget's content only
              (e.g., Text, ScrolledText, Listbox, Treeview).
            - The main window Canvas does NOT scroll while the event is handled.

        When the cursor is not over such a widget:
            - Global scroll bindings move the main window content.

        Requirements:
            - The widget must implement a .yview(...) method.

        Usage:
            console = make_textarea(self.main_frame, height=10)
            console.pack(fill="both", expand=True)
            self.bind_scroll_widget(console)
        """
        if not hasattr(widget, "yview"):
            logger.warning("[G01d] bind_scroll_widget called on non-scrollable widget: %r", widget)
            return

        os_type = detect_os()
        logger.info("[G01d] Binding per-widget scroll for %r (OS=%s)", widget, os_type)

        # Inner handlers use closure over widget
        def _on_widget_mousewheel(event, w=widget):
            delta_raw = getattr(event, "delta", 0)
            delta = int(delta_raw / 120) if delta_raw else 0
            if delta:
                w.yview_scroll(-delta, "units")
            return "break"  # prevent global handler

        def _on_widget_mousewheel_linux(event, w=widget):
            if event.num == 4:
                w.yview_scroll(-3, "units")
            elif event.num == 5:
                w.yview_scroll(3, "units")
            return "break"

        if os_type in ("Windows", "MacOS"):
            widget.bind("<MouseWheel>", _on_widget_mousewheel, add="+")
        else:
            widget.bind("<Button-4>", _on_widget_mousewheel_linux, add="+")
            widget.bind("<Button-5>", _on_widget_mousewheel_linux, add="+")

    # =================================================================================================
    # 3.5 OVERRIDABLE CONTENT HOOK
    # =================================================================================================
    def build_widgets(self) -> None:
        """
        Placeholder method for constructing window widgets.

        Notes:
            - Subclasses must override this method to define their GUI layout.
            - All child widgets should be attached to self.main_frame (not directly to
              the root window) so they benefit from the scrollable layout.
        """
        logger.debug("[G01d] BaseGUI.build_widgets() — override in subclass.")
        # Intentionally left blank.

    # =================================================================================================
    # 3.6 WINDOW UTILITY METHODS
    # =================================================================================================
    def center_window(self, width: int, height: int) -> None:
        """
        Center the window on the screen based on its width and height.
        """
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_pos = (screen_width // 2) - (width // 2)
        y_pos = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x_pos}+{y_pos}")
        logger.debug(
            "[G01d] Window centered at %dx%d+%d+%d",
            width,
            height,
            x_pos,
            y_pos,
        )

    # ------------------------------------------------------------------------------------------------
    def open_fullscreen(self) -> None:
        """
        Open the GUI in fullscreen/maximised mode in an OS-agnostic way.

        Behaviour:
            - Windows: uses the 'zoomed' state.
            - macOS / Linux: uses the '-fullscreen' window attribute.
        """
        os_type = detect_os()
        logger.info("[G01d] Request to enter fullscreen (OS=%s)", os_type)

        try:
            if os_type == "Windows":
                self.state("zoomed")
            elif os_type in ("MacOS", "Linux"):
                self.attributes("-fullscreen", True)
                self.update_idletasks()
            else:
                self.state("zoomed")
        except Exception as exc:  # noqa: BLE001
            logger.exception("[G01d] Failed to open fullscreen mode: %s", exc)
            try:
                self.state("zoomed")
            except Exception:  # noqa: BLE001
                pass

    # ------------------------------------------------------------------------------------------------
    def exit_fullscreen(self) -> None:
        """
        Exit fullscreen mode and restore normal windowed size.
        """
        os_type = detect_os()
        logger.info("[G01d] Request to exit fullscreen (OS=%s)", os_type)

        try:
            if os_type in ("MacOS", "Linux"):
                self.attributes("-fullscreen", False)
            else:
                self.state("normal")
            self.update_idletasks()
        except Exception as exc:  # noqa: BLE001
            logger.exception("[G01d] Failed to exit fullscreen mode: %s", exc)

    # ------------------------------------------------------------------------------------------------
    def safe_close(self) -> None:
        """
        Close the window safely, ensuring all resources are released.

        Subclasses can override this method if additional cleanup is required
        (threads, temporary files, background tasks, etc.).
        """
        logger.info("[G01d] safe_close() called; destroying window.")
        self.destroy()

    # ------------------------------------------------------------------------------------------------
    def close(self) -> None:
        """
        Convenience alias for safe_close(), so all GUIs can use self.close().
        """
        self.safe_close()

    # =================================================================================================
    # 3.7 DEBUG DIAGNOSTICS
    # =================================================================================================
    def log_debug_diagnostics(self) -> None:
        """
        Emit detailed diagnostics about the GUI environment to the logger.

        Includes:
            - Tk version
            - Active ttk theme
            - Available themes
            - Active font family
            - Presence checks for key styles
        """
        try:
            tk_version = self.tk.call("info", "patchlevel")
        except Exception:  # noqa: BLE001
            tk_version = "unknown"

        try:
            active_theme = self.style.theme_use()
            available_themes = self.style.theme_names()
        except Exception:  # noqa: BLE001
            active_theme = "unknown"
            available_themes = []

        logger.debug("=== G01d Debug Diagnostics =====================================")
        logger.debug("[G01d][DEBUG] Tk Version: %s", tk_version)
        logger.debug("[G01d][DEBUG] Active ttk theme: %s", active_theme)
        logger.debug("[G01d][DEBUG] Available themes: %r", available_themes)
        logger.debug(
            "[G01d][DEBUG] Active font family: %s",
            getattr(self, "active_font_family", None),
        )

        critical_styles = [
            "TLabel",
            "TButton",
            "TEntry",
            "TCombobox",
            "Vertical.TScrollbar",
            "SectionBody.TFrame",
            "SectionOuter.TFrame",
            "SectionHeading.TLabel",
        ]

        for style_name in critical_styles:
            exists = True
            try:
                _ = self.style.layout(style_name)
            except Exception:  # noqa: BLE001
                exists = False
            logger.debug("[G01d][DEBUG] Style '%s' defined: %s", style_name, exists)

        logger.debug("================================================================")


# ====================================================================================================
# 4. SANDBOX TEST (OPTION A – New Architecture)
# ----------------------------------------------------------------------------------------------------
#   Standalone test of the BaseGUI class and scroll behaviour, using ONLY the new
#   G01x primitives (no legacy helpers, no UIComponents dependency).
#
#   Demonstrates:
#       • Main window scroll with several labels.
#       • Textarea that captures its own scroll events when hovered.
#       • All styling coming from G00a + G01a.
# ====================================================================================================
if __name__ == "__main__":
    # Import primitives locally to avoid circular dependencies in normal use.
    from gui.G01c_widget_primitives import (  # type: ignore[import]
        make_heading,
        make_label,
        make_textarea,
        make_divider,
    )

    class G01dTestGUI(BaseGUI):
        """
        Simple sandbox window to exercise BaseGUI behaviour:
            - Global scroll of the main content.
            - Per-widget scroll override for a text console.
        """

        def build_widgets(self) -> None:
            # Heading
            make_heading(
                self.main_frame,
                "G01d BaseGUI Scroll Sandbox",
                pady=(0, 10),
            ).pack(anchor="w", pady=(0, 10))

            # Add enough labels to require main-window scrolling
            for i in range(15):
                make_label(
                    self.main_frame,
                    f"Main window content line {i + 1}",
                ).pack(anchor="w", pady=2)

            # Divider
            make_divider(self.main_frame).pack(fill="x", pady=10)

            # Text console with its own scrollbar
            make_label(
                self.main_frame,
                "Scrollable console (captures mouse wheel when hovered):",
            ).pack(anchor="w", pady=(0, 4))

            console = make_textarea(self.main_frame, height=8)
            console.pack(fill="both", expand=True, pady=(0, 10))

            for i in range(40):
                console.insert("end", f"Console log line {i + 1}\n")

            # Register console as a scroll widget so it handles its own mouse wheel
            self.bind_scroll_widget(console)

            # Footer label
            make_label(
                self.main_frame,
                "Try scrolling with the mouse/trackpad over the main area vs over the console.",
            ).pack(anchor="w", pady=(10, 0))

    logger.info("=== G01d_gui_base sandbox test start ===")
    app = G01dTestGUI(title="G01d BaseGUI Sandbox (Option A – New Architecture)")
    app.mainloop()
    logger.info("=== G01d_gui_base sandbox test end ===")
