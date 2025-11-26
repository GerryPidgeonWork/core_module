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
#   - G01a_style_config:
#         Colours, fonts, spacing, frame sizes (design tokens).
#   - G01b_style_engine:
#         Named fonts + ttk style definitions based on tokens.
#   - G01c_widget_primitives:
#         Widget factory functions (labels, buttons, entries, etc.).
#   - G01d_layout_primitives:
#         Layout building blocks (headings, body text, dividers, spacers).
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
from gui.G00a_gui_packages import tk, ttk, tkFont, Style
from gui.G01a_style_config import *
from gui.G01b_style_engine import configure_ttk_styles

DEBUG_BASE_GUI: bool = True


# ====================================================================================================
# 3. BASE GUI CLASS
# ----------------------------------------------------------------------------------------------------
# The BaseGUI class defines the *window shell* for all GUI pages in the framework.
#
# Responsibilities:
#     • Construct the Tk root window (title, geometry, background, minsize).
#     • Initialise ttk/ttkbootstrap Style (delegating styling to G01a_style_engine).
#     • Provide a scrollable main content area (Canvas → Scrollbar → inner frame).
#     • Implement global mouse/trackpad scroll handling across platforms.
#     • Provide per-widget scroll overrides for widgets with native yview support.
#     • Expose clean utility methods (fullscreen, center_window, safe_close, etc.).
#
# Architectural Rules:
#     • NO widgets created here — subclasses override build_widgets().
#     • NO business logic.
#     • All widgets must attach to self.main_frame (scrollable container).
#     • All styling is delegated to configure_ttk_styles().
#
# Usage:
#     from gui.G01e_gui_base import BaseGUI
#
#     class MyWindow(BaseGUI):
#         def build_widgets(self):
#             ttk.Label(self.main_frame, text="Hello World").pack()
#
#     if __name__ == "__main__":
#         MyWindow(title="Demo").mainloop()
# ====================================================================================================
class BaseGUI(tk.Tk):  # type: ignore[name-defined]
    """
    Standardised Tkinter root window for all GUI windows in the framework.

    This class creates:
        • A fully styled Tk window (title, geometry, fonts, ttk styles).
        • A vertical scrollable content region (Canvas + Scrollbar).
        • An overridable build_widgets() hook for concrete pages.
        • Cross-platform mouse-wheel / trackpad scrolling.
        • Optional per-widget scroll override for Text/Listbox/etc.

    Subclasses should:
        • Override build_widgets().
        • Attach all widgets to self.main_frame.
        • Never manipulate the underlying Canvas/Scrollbar directly.
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
        Initialise the window shell and scroll engine.

        Args:
            title (str):
                Initial window title (default: FRAME_HEADING).

            width (int):
                Initial window width in pixels.

            height (int):
                Initial window height in pixels.

            resizable (bool):
                Whether the user may resize the window horizontally/vertically.
        """
        logger.info("[G01e] === BaseGUI.__init__ start ===")
        logger.debug(
            "[G01e] Window request — title=%r width=%d height=%d resizable=%s",
            title,
            width,
            height,
            resizable,
        )

        super().__init__()

        # Root-level geometry + structure ------------------------------------------------------------
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(bg=GUI_COLOUR_BG_PRIMARY)
        self.resizable(resizable, resizable)
        self.minsize(400, 300)

        logger.debug("[G01e] Base window configured (geometry, colours, resizable, minsize).")

        # Style initialisation -----------------------------------------------------------------------
        self.style = self.configure_styles()

        # Scrollable layout --------------------------------------------------------------------------
        self.build_root_layout()
        logger.debug("[G01e] Scrollable container built (canvas + scrollbar + main_frame).")

        # Subclass widget construction ---------------------------------------------------------------
        self.build_widgets()
        logger.debug("[G01e] build_widgets() executed (subclass hook).")

        # Window centring ---------------------------------------------------------------------------
        self.center_window(width, height)
        logger.debug("[G01e] Window centred on screen.")

        # Global scroll handling ---------------------------------------------------------------------
        self.bind_global_scroll()
        logger.debug("[G01e] Global scroll bindings applied.")

        # Optional diagnostics -----------------------------------------------------------------------
        if DEBUG_BASE_GUI:
            self.log_debug_diagnostics()

        logger.info("[G01e] === BaseGUI.__init__ complete ===")

    # =================================================================================================
    # 3.1 STYLE CONFIGURATION (delegated to G01a_style_engine)
    # =================================================================================================
    def configure_styles(self) -> ttk.Style:  # type: ignore[name-defined]
        """
        Create the ttk/ttkbootstrap Style instance for the window.

        Behaviour:
            • Identify a working font from GUI_FONT_FAMILY.
            • If gui.G00a_gui_packages.Style is available, try to construct it
              (this may be a ttkbootstrap.Style if enable_ttkbootstrap() was
              called earlier).
            • Fall back to ttk.Style(self) if Style is None or cannot be
              constructed.
            • For plain ttk.Style, normalise the theme to 'clam'.
            • For ttkbootstrap.Style, preserve the bootstrap theme and do NOT
              call theme_use().
            • Delegate all ttk style configuration to configure_ttk_styles().
        """
        logger.info("[G01e] Configuring ttk styles...")

        # --- Font family resolution -----------------------------------------------------------------
        active_font_family: str | None = None
        font_candidates = (
            GUI_FONT_FAMILY
            if isinstance(GUI_FONT_FAMILY, (list, tuple))
            else [GUI_FONT_FAMILY]
        )
        logger.debug("[G01e] Font candidate list: %r", font_candidates)

        for fam in font_candidates:
            try:
                _ = tkFont.Font(family=fam, size=GUI_FONT_SIZE_DEFAULT)
                active_font_family = fam
                logger.info("[G01e] Using GUI font family: %s", fam)
                break
            except Exception as exc:  # noqa: BLE001
                logger.debug("[G01e] Font '%s' unavailable (%s); trying next…", fam, exc)

        if not active_font_family:
            active_font_family = "Segoe UI"
            logger.warning(
                "[G01e] No preferred fonts available; falling back to %s",
                active_font_family,
            )

        self.active_font_family = active_font_family  # cached for subclasses

        # --- Create Style instance ------------------------------------------------------------------
        style_obj: ttk.Style | Any
        is_bootstrap_style = False

        # If G00a has provided a Style symbol (potentially ttkbootstrap.Style),
        # try to use it; otherwise fall back to plain ttk.Style.
        if Style is not None:
            try:
                style_obj = Style(theme="flatly")  # type: ignore[name-defined]
                style_module = type(style_obj).__module__
                is_bootstrap_style = style_module.startswith("ttkbootstrap")
                if is_bootstrap_style:
                    logger.info("[G01e] Using ttkbootstrap.Style with theme 'flatly'.")
                else:
                    logger.info("[G01e] Using non-bootstrap Style from G00a_gui_packages.")
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "[G01e] Failed to construct Style(...) from G00a_gui_packages (%s); "
                    "falling back to ttk.Style.",
                    exc,
                )
                style_obj = ttk.Style(self)  # type: ignore[call-arg]
        else:
            logger.info("[G01e] gui.G00a_gui_packages.Style is None; using ttk.Style.")
            style_obj = ttk.Style(self)  # type: ignore[call-arg]

        if not is_bootstrap_style:
            # Plain ttk.Style: normalise to 'clam' or a safe fallback theme.
            try:
                style_obj.theme_use("clam")
                logger.info("[G01e] Theme set to 'clam' for plain ttk.Style.")
            except Exception as exc:  # noqa: BLE001
                logger.warning("[G01e] Failed to set theme 'clam': %s", exc)
        else:
            # ttkbootstrap.Style: leave theme exactly as configured (e.g. 'flatly').
            try:
                current_theme = getattr(getattr(style_obj, "theme", None), "name", None)
            except Exception:  # noqa: BLE001
                current_theme = None
            logger.info(
                "[G01e] Detected ttkbootstrap.Style; preserving bootstrap theme %r.",
                current_theme,
            )

        # Delegate visual styles ----------------------------------------------------------------------
        try:
            configure_ttk_styles(style_obj)
            logger.info("[G01e] configure_ttk_styles() applied successfully.")
        except Exception as exc:  # noqa: BLE001
            logger.exception("[G01e] Error applying configure_ttk_styles(): %s", exc)

        # Ensure background colour consistency -------------------------------------------------------
        self.configure(bg=GUI_COLOUR_BG_PRIMARY)

        return style_obj

    # =================================================================================================
    # 3.2 ROOT LAYOUT (SCROLL ENGINE)
    # =================================================================================================
    def build_root_layout(self) -> None:
        """
        Create the scrollable GUI container.

        Structure:
            self (Tk)
              └─ self.container (TFrame)
                   ├─ self.canvas (Canvas)
                   │      └─ window → self.main_frame (TFrame)
                   └─ self.v_scrollbar (Vertical.TScrollbar)

        Notes:
            • All widgets must attach to self.main_frame (not directly to root).
            • Scrollregion auto-expands as widgets are added.
        """
        logger.debug("[G01e] Building scrollable root layout...")

        # Outer frame --------------------------------------------------------------------------------
        self.container = ttk.Frame(self, padding=0)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container.columnconfigure(0, weight=1)

        # Canvas (scroll area) -----------------------------------------------------------------------
        self.canvas = tk.Canvas(
            self.container,
            background=GUI_COLOUR_BG_PRIMARY,
            highlightthickness=0,
            bd=0,
        )

        # Vertical scrollbar -------------------------------------------------------------------------
        self.v_scrollbar = ttk.Scrollbar(
            self.container,
            orient="vertical",
            command=self.canvas.yview,
            style="Vertical.TScrollbar",
        )
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Inner content frame ------------------------------------------------------------------------
        self.main_frame = ttk.Frame(self.canvas, padding=FRAME_PADDING)
        self.main_frame.columnconfigure(0, weight=1)

        self._canvas_window_id = self.canvas.create_window(
            (0, 0),
            window=self.main_frame,
            anchor="nw",
        )

        # Auto-sizing callbacks ----------------------------------------------------------------------
        self.main_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    # ------------------------------------------------------------------------------------------------
    def on_frame_configure(self, event) -> None:
        """
        Update scrollregion whenever the main_frame changes size.

        Description:
            Called automatically when main_frame is resized. Updates the canvas
            scrollregion to encompass all content.

        Args:
            event: Tkinter Configure event (unused but required by binding).

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Bound to main_frame's <Configure> event in build_root_layout().
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # ------------------------------------------------------------------------------------------------
    def on_canvas_configure(self, event) -> None:
        """
        Synchronise main_frame width with canvas width.

        Description:
            Called automatically when canvas is resized. Ensures the main_frame
            expands horizontally to fill the available canvas width.

        Args:
            event: Tkinter Configure event containing new width.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Bound to canvas's <Configure> event in build_root_layout().
        """
        canvas_width = event.width
        self.canvas.itemconfig(self._canvas_window_id, width=canvas_width)
        self.main_frame.configure(width=canvas_width)

    # =================================================================================================
    # 3.3 GLOBAL SCROLL BINDINGS
    # =================================================================================================
    def bind_global_scroll(self) -> None:
        """
        Bind mouse-wheel / trackpad scrolling across platforms.

        Windows & macOS:
            <MouseWheel>

        Linux:
            <Button-4> = Scroll up
            <Button-5> = Scroll down
        """
        os_type = detect_os()
        logger.info("[G01e] Setting up global scroll bindings (OS=%s)", os_type)

        if os_type in ("Windows", "MacOS"):
            self.bind_all("<MouseWheel>", self.on_global_mousewheel)
        else:
            self.bind_all("<Button-4>", self.on_global_mousewheel_linux)
            self.bind_all("<Button-5>", self.on_global_mousewheel_linux)

    # ------------------------------------------------------------------------------------------------
    def on_global_mousewheel(self, event):
        """Scroll canvas on Windows/macOS."""
        delta_raw = getattr(event, "delta", 0)
        delta = int(delta_raw / 120) if delta_raw else 0
        if delta:
            self.canvas.yview_scroll(-delta, "units")

    # ------------------------------------------------------------------------------------------------
    def on_global_mousewheel_linux(self, event):
        """Scroll canvas on Linux using Button-4/5 events."""
        if event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(3, "units")

    # =================================================================================================
    # 3.4 PER-WIDGET SCROLL OVERRIDE
    # =================================================================================================
    def bind_scroll_widget(self, widget) -> None:
        """
        Assign mouse-wheel handling to a specific widget (Text, Listbox, etc.).

        When hovered:
            • Scroll only the widget.
            • Prevent scroll events from propagating to the main canvas.

        Requirement:
            The widget must implement .yview().
        """
        if not hasattr(widget, "yview"):
            logger.warning("[G01e] bind_scroll_widget called on non-scrollable widget: %r", widget)
            return

        os_type = detect_os()
        logger.info("[G01e] Binding per-widget scroll for %r (OS=%s)", widget, os_type)

        def _on_widget_mousewheel(event, w=widget):
            delta_raw = getattr(event, "delta", 0)
            delta = int(delta_raw / 120) if delta_raw else 0
            if delta:
                w.yview_scroll(-delta, "units")
            return "break"

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
        Subclasses override this to populate the GUI.

        Description:
            Hook method called during __init__ after the scroll engine is built.
            Subclasses must override this to create their UI content.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - All widgets must be created as children of self.main_frame.
            - Do NOT attach widgets directly to self (the root window).
            - The base implementation does nothing; override in subclass.
        """
        logger.debug("[G01e] BaseGUI.build_widgets() — override in subclass.")

    # =================================================================================================
    # 3.6 WINDOW UTILITY METHODS
    # =================================================================================================
    def center_window(self, width: int, height: int) -> None:
        """Center the window on the user’s screen."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_pos = (screen_width // 2) - (width // 2)
        y_pos = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x_pos}+{y_pos}")
        logger.debug("[G01e] Window centered at %dx%d+%d+%d", width, height, x_pos, y_pos)

    # ------------------------------------------------------------------------------------------------
    def open_fullscreen(self) -> None:
        """
        Enter fullscreen/maximised mode in a cross-platform way.
        """
        os_type = detect_os()
        logger.info("[G01e] Entering fullscreen (OS=%s)", os_type)

        try:
            if os_type == "Windows":
                self.state("zoomed")
            elif os_type in ("MacOS", "Linux"):
                self.attributes("-fullscreen", True)
                self.update_idletasks()
            else:
                self.state("zoomed")
        except Exception as exc:  # noqa: BLE001
            logger.exception("[G01e] Failed to enter fullscreen: %s", exc)

    # ------------------------------------------------------------------------------------------------
    def exit_fullscreen(self) -> None:
        """Exit fullscreen and return to normal size."""
        os_type = detect_os()
        logger.info("[G01e] Exiting fullscreen (OS=%s)", os_type)

        try:
            if os_type in ("MacOS", "Linux"):
                self.attributes("-fullscreen", False)
            else:
                self.state("normal")
            self.update_idletasks()
        except Exception as exc:  # noqa: BLE001
            logger.exception("[G01e] Failed to exit fullscreen: %s", exc)

    # ------------------------------------------------------------------------------------------------
    def safe_close(self) -> None:
        """Close the window safely (override for cleanup if needed)."""
        logger.info("[G01e] safe_close() called; destroying window.")
        self.destroy()

    # ------------------------------------------------------------------------------------------------
    def close(self) -> None:
        """Convenience wrapper for safe_close()."""
        self.safe_close()

    # =================================================================================================
    # 3.7 DEBUG DIAGNOSTICS
    # =================================================================================================
    def log_debug_diagnostics(self) -> None:
        """
        Emit diagnostics for debugging style/theme/font configuration.

        Logged:
            • Tk version
            • Active ttk theme
            • Theme availability list
            • Active font family
            • Presence of critical ttk styles
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

        logger.debug("=== [G01e] Debug Diagnostics =====================================")
        logger.debug("[G01e] Tk Version: %s", tk_version)
        logger.debug("[G01e] Active ttk theme: %s", active_theme)
        logger.debug("[G01e] Available themes: %r", available_themes)
        logger.debug("[G01e] Active font family: %s", getattr(self, "active_font_family", None))

        critical_styles = [
            "TLabel",
            "TButton",
            "TEntry",
            "TCombobox",
            "Vertical.TScrollbar",
            "TFrame",
            "SectionBody.TFrame",
            "SectionOuter.TFrame",
            "Primary.Normal.TLabel",
            "Primary.Bold.TLabel",
            "Primary.SectionHeading.Bold.TLabel",
            "Secondary.Normal.TLabel",
        ]

        for style_name in critical_styles:
            exists = True
            try:
                _ = self.style.layout(style_name)
            except Exception:  # noqa: BLE001
                exists = False
            logger.debug("[G01e] Style '%s' defined: %s", style_name, exists)

        logger.debug("================================================================")

# ====================================================================================================
# 4. SANDBOX TEST
# ----------------------------------------------------------------------------------------------------
# A simple frame demonstrating BaseGUI behaviour using G01c/G01d primitives.
# ====================================================================================================
if __name__ == "__main__":
    init_logging()

    # Local imports avoid circular dependencies in production
    from gui.G01c_widget_primitives import make_label, make_textarea, make_divider

    class G01eTestGUI(BaseGUI):
        """Simple sandbox window to test scroll behaviour and styling."""

        def build_widgets(self) -> None:
            # Window heading
            make_label(
                self.main_frame,
                "G01e BaseGUI Scroll Sandbox",
                category="WindowHeading",
                surface="Primary",
                weight="Bold",
            ).pack(anchor="w", pady=(0, 10))

            # Section heading
            make_label(
                self.main_frame,
                "Main Content Area",
                category="SectionHeading",
                surface="Primary",
                weight="Bold",
            ).pack(anchor="w", pady=(0, 6))

            # Fill with lines to force scrolling
            for i in range(15):
                make_label(
                    self.main_frame,
                    f"Main content line {i + 1}",
                    category="Body",
                    surface="Primary",
                    weight="Normal",
                ).pack(anchor="w", pady=2)

            make_divider(self.main_frame).pack(fill="x", pady=10)

            make_label(
                self.main_frame,
                "Scrollable console (hover to capture scroll):",
                category="Body",
                surface="Primary",
                weight="Bold",
            ).pack(anchor="w", pady=(0, 4))

            # Text console
            console = make_textarea(self.main_frame, height=8)
            console.pack(fill="both", expand=True, pady=(0, 10))

            for i in range(40):
                console.insert("end", f"Console log line {i + 1}\n")

            # Console scroll override
            self.bind_scroll_widget(console)

            make_label(
                self.main_frame,
                "Scroll over main area vs scroll over the console to test per-widget scroll override.",
                category="Body",
                surface="Primary",
                weight="Normal",
            ).pack(anchor="w", pady=(10, 0))

    logger.info("[G01e] === BaseGUI sandbox start ===")
    app = G01eTestGUI(title="G01e BaseGUI Sandbox")
    app.mainloop()
    logger.info("[G01e] === BaseGUI sandbox end ===")