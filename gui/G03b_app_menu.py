# ====================================================================================================
# G03b_app_menu.py
# ----------------------------------------------------------------------------------------------------
# Standardised Application Menu Bar for GUIBoilerplatePython
#
# Purpose:
#   Provides a consistent, reusable top-level application menu for all GUI windows.
#   The menu integrates cleanly with NavigationController (G03a) and supports:
#
#       • File menu (Exit)
#       • View menu (Home, Reload Current Page)
#       • Help menu (About)
#       • Global keyboard accelerators (Ctrl+H, Ctrl+R, Ctrl+Q)
#
# Design Principles:
#   • Pure UI behaviour — no business logic and no layout logic.
#   • No dependency on UIComponents, layout primitives, or BaseGUI internals.
#   • Full architectural isolation in the G03 “Reusable Widgets & Patterns” layer.
#   • Safe import rules:
#       - ALL Tkinter/ttk imports come ONLY from gui.G00a_gui_packages.
#       - ALL third-party/stdlib imports come ONLY from core.C00_set_packages.
#
# Integration:
#       from gui.G03b_app_menu import AppMenuBar
#
#       menu = AppMenuBar(root, navigation=controller)
#
# Notes:
#   - Menu attaches via root.config(menu=...).
#   - Keyboard shortcuts use root.bind_all().
#   - Self-test block provides a minimal working demo.
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
from gui.G00a_gui_packages import tk, ttk  # Explicit for type hints
from gui.G03a_navigation import NavigationController


# ====================================================================================================
# 3. CLASS — AppMenuBar
# ----------------------------------------------------------------------------------------------------
class AppMenuBar:
    """
    Standard application menu bar with built-in navigation support.

    Menu structure:
        File
            • Exit                  (Ctrl+Q)
        View
            • Home Page             (Ctrl+H)
            • Reload Current Page   (Ctrl+R)
        Help
            • About

    Behaviour:
        • Menu attaches to a BaseGUI root via root.config(menu=...)
        • Shortcuts bind globally using root.bind_all()
        • Integrates with AppController for page switching
    """

    # -----------------------------------------------------------------------------------------------
    def __init__(self, root: tk.Tk, navigation: NavigationController):
        """
        Initialise the menu bar.

        Args:
            root (tk.Tk | BaseGUI):
                Main window, must support .config(menu=...)
            navigation (NavigationController):
                App-wide controller handling page navigation.
        """
        self.root = root
        self.navigation: NavigationController = navigation

        # Build top-level menu container
        self.menubar = tk.Menu(self.root)

        # Build each menu group
        self._build_file_menu()
        self._build_view_menu()
        self._build_help_menu()

        # Attach to window
        self.root.config(menu=self.menubar)

        # Bind global shortcuts
        self._bind_shortcuts()

    # =================================================================================================
    # 4. FILE MENU
    # =================================================================================================
    def _build_file_menu(self) -> None:
        file_menu = tk.Menu(self.menubar, tearoff=False)

        file_menu.add_command(
            label="Exit\tCtrl+Q",
            accelerator="Ctrl+Q",
            command=self.root.quit,
        )

        self.menubar.add_cascade(label="File", menu=file_menu)

    # =================================================================================================
    # 5. VIEW MENU
    # =================================================================================================
    def _build_view_menu(self) -> None:
        view_menu = tk.Menu(self.menubar, tearoff=False)

        # Home page -------------------------------------------------------------------------------
        def go_home():
            try:
                self.navigation.show_page("home")
            except KeyError:
                pass  # home not registered — silently ignore

        view_menu.add_command(
            label="Home Page\tCtrl+H",
            accelerator="Ctrl+H",
            command=go_home,
        )

        # Reload current page ---------------------------------------------------------------------
        def reload_page():
            current = self.navigation.current_page
            if current:
                self.navigation.show_page(current)

        view_menu.add_command(
            label="Reload Current Page\tCtrl+R",
            accelerator="Ctrl+R",
            command=reload_page,
        )

        self.menubar.add_cascade(label="View", menu=view_menu)

    # =================================================================================================
    # 6. HELP MENU
    # =================================================================================================
    def _build_help_menu(self) -> None:
        help_menu = tk.Menu(self.menubar, tearoff=False)

        help_menu.add_command(
            label="About",
            command=lambda: messagebox.showinfo(
                "About",
                "GUI Boilerplate Framework\n© 2025 Gerry Pidgeon",
                parent=self.root,
            ),
        )

        self.menubar.add_cascade(label="Help", menu=help_menu)

    # =================================================================================================
    # 7. KEYBOARD SHORTCUTS
    # =================================================================================================
    def _bind_shortcuts(self) -> None:
        """
        Register global keyboard accelerators.

        Tkinter menus do not automatically bind accelerators.
        We manually attach them using bind_all().
        """

        # Home Page
        self.root.bind_all("<Control-h>", lambda e: self.navigation.show_page("home"))

        # Reload current
        def reload_event(_):
            current = self.navigation.current_page
            if current:
                self.navigation.show_page(current)

        self.root.bind_all("<Control-r>", reload_event)

        # Quit
        self.root.bind_all("<Control-q>", lambda e: self.root.quit())


# ====================================================================================================
# 8. SANDBOX TEST
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    from gui.G01e_gui_base import BaseGUI
    from gui.G03a_navigation import BasePage, NavigationController

    class DemoHome(BasePage):
        def build_page(self):
            ttk.Label(self, text="🏠 Home Page").pack(pady=20)

    class DemoSettings(BasePage):
        def build_page(self):
            ttk.Label(self, text="⚙ Settings Page").pack(pady=20)

    # Create window
    app = BaseGUI(title="G03b Menu Sandbox", width=900, height=650)

    # Navigation controller
    controller = NavigationController(app)
    controller.register_page("home", DemoHome)
    controller.register_page("settings", DemoSettings)
    controller.show_page("home")

    # Attach menu bar
    AppMenuBar(app, navigation=controller)

    app.mainloop()
