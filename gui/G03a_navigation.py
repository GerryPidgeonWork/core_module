# ====================================================================================================
# G03a_navigation.py
# ----------------------------------------------------------------------------------------------------
# Centralised Page Navigation System for GUIBoilerplatePython
#
# Purpose:
#   Provides a lightweight, dependable page-navigation layer for all GUI
#   applications built on the GUIBoilerplatePython framework.
#
#   Components:
#       • NavigationController
#           - Registers page classes
#           - Instantiates + switches active pages
#           - Manages destruction of previous pages
#
#       • BasePage
#           - Minimal, clean superclass for all logical “pages”
#           - Enforces a consistent build_page() pattern
#           - Every page is parented inside BaseGUI.main_frame
#
# Architecture Rules:
#   • ALL Tkinter/ttk imports must come ONLY from gui.G00a_gui_packages.
#   • No external imports other than: core.C00_set_packages, C03_logging_handler.
#   • No GUI logic may appear in core modules.
#   • Pages must never modify window layout directly — only populate their frame.
#
# Integration:
#   from gui.G03a_navigation import NavigationController, BasePage
#
#   controller = NavigationController(app)
#   controller.register_page("home", HomePage)
#   controller.show_page("home")
#
# Notes:
#   - This module contains NO side effects.
#   - Self-test block provides a minimal GUI to verify navigation.
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
from gui.G00a_gui_packages import tk, ttk  # Explicit imports for classes


# ====================================================================================================
# BasePage
# ----------------------------------------------------------------------------------------------------
class BasePage(ttk.Frame):
    """
    Minimal page superclass (Option A).

    Pages implement build_page(), and are always parented to BaseGUI.main_frame.
    """

    def __init__(self, parent):
        logger.debug(f"[BasePage] Initialising {self.__class__.__name__}")
        super().__init__(parent, style="TFrame")
        self.build_page()

    def build_page(self):
        """Subclasses override this."""
        pass


# ====================================================================================================
# NavigationController
# ----------------------------------------------------------------------------------------------------
class NavigationController:
    """
    Lightweight page switcher for BaseGUI.

    - register_page(name, class)
    - show_page(name)
    """

    def __init__(self, root):
        logger.info("[NavigationController] Initialising")
        self.root = root
        self.pages: Dict[str, type[BasePage]] = {}
        self.current_page: BasePage | None = None

    def register_page(self, name: str, page_class: type[BasePage]):
        logger.info(f"[NavigationController] Registering page: {name} -> {page_class.__name__}")
        self.pages[name] = page_class

    def show_page(self, name: str):
        if name not in self.pages:
            logger.error(f"[NavigationController] Attempt to show unknown page '{name}'")
            raise KeyError(f"Page '{name}' not registered.")

        # Destroy old page
        if self.current_page is not None:
            logger.debug(
                f"[NavigationController] Destroying old page {self.current_page.__class__.__name__}"
            )
            self.current_page.destroy()

        # Instantiate new page
        page_class = self.pages[name]
        logger.info(f"[NavigationController] Showing page '{name}' ({page_class.__name__})")

        page_instance = page_class(self.root.main_frame)
        page_instance.pack(fill="both", expand=True)

        self.current_page = page_instance


# ====================================================================================================
# 4. SELF-TEST
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Simple test window to verify NavigationController + BasePage.
    """
    init_logging()
    logger.info("=== G03a_navigation.py — Self Test Start ===")

    from gui.G01e_gui_base import BaseGUI
    from gui.G01c_widget_primitives import make_label

    class TestPage(BasePage):
        def build_page(self):
            make_label(
                self,
                "G03a Navigation Test Page",
                category="WindowHeading",
                surface="Primary",
                weight="Bold",
            ).pack(pady=(10, 5))
            make_label(
                self,
                "If you see this page, navigation is working.",
                category="Body",
                surface="Primary",
                weight="Normal",
            ).pack()

    app = BaseGUI(title="G03a Navigation — Self Test")
    nav = NavigationController(app)

    nav.register_page("test", TestPage)
    nav.show_page("test")

    logger.info("=== G03a_navigation.py — Entering mainloop ===")
    app.mainloop()
    logger.info("=== G03a_navigation.py — Self Test End ===")
