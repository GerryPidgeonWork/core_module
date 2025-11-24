# ====================================================================================================
# G03e_app_controller.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Centralised application-level controller for multi-page Tkinter GUIs.
#
#   This module provides the glue layer between:
#       • BaseGUI (G01e)                – window shell, scroll region, main_frame
#       • Navigation (this module)      – page registration, lazy loading, switching
#       • UIPrimitives (G01c)           – atomic widget + layout primitives
#       • AppState (G03d)               – strongly-typed application state
#
# Responsibilities:
#       • Register logical page names → page classes
#       • Instantiate pages lazily and cache them
#       • Switch visible pages inside BaseGUI.main_frame
#       • Destroy pages safely when required
#       • Provide shared access to:
#             - UIPrimitives (ui)
#             - AppState (app_state)
#
# Architectural Role:
#   • Lives in the G03 (“Reusable Widgets & UI Patterns”) namespace.
#   • Contains NO business logic.
#   • Does NOT create widgets other than page containers.
#   • All pages must subclass BasePage (below) and implement build_page().
#
# Usage:
#       nav = NavigationController(app)
#       nav.register_page("home", HomePage)
#       nav.show_page("home")
#
# Notes:
#   • Pages are normal ttk.Frame subclasses with four injected parameters:
#         parent, controller, ui, app_state
#   • NavigationController owns the shared UI + AppState instances.
#   • BasePage provides consistent padding, styling, and page lifecycle.
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
from gui.G01a_style_config import FRAME_PADDING
from gui.G01c_widget_primitives import UIPrimitives
from gui.G01e_gui_base import BaseGUI
from gui.G03d_app_state import AppState


# ====================================================================================================
# 3. NAVIGATION CONTROLLER
# ----------------------------------------------------------------------------------------------------
class NavigationController:
    """
    Central navigation + state controller for Tkinter multi-page GUIs.

    Features:
        • register_page(name, PageClass)
        • show_page(name)
        • destroy_page(name)
        • Shared AppState + UIPrimitives instances

    Pages must subclass BasePage or ttk.Frame, and accept:
        parent, controller, ui, app_state
    """

    def __init__(self, root_window: BaseGUI):
        """
        Initialise a NavigationController bound to a BaseGUI window.

        Args:
            root_window: The BaseGUI instance that owns the scrollable main_frame.
        """
        self.root: BaseGUI = root_window
        self.container: ttk.Frame = root_window.main_frame

        # Shared state & UI layer
        self.app_state: AppState = AppState()
        self.ui: UIPrimitives = UIPrimitives(root_window)

        # Registry of page classes
        self.page_classes: Dict[str, Type[Any]] = {}

        # Cache of instantiated page frames
        self.page_instances: Dict[str, ttk.Frame] = {}

        self.current_page: Optional[str] = None

    # ------------------------------------------------------------------------------------------------
    def register_page(self, name: str, page_class: Type[Any]) -> None:
        """
        Register a logical page name to a page class.

        Args:
            name:        Logical name for the page (e.g. "home", "settings").
            page_class:  Class implementing the page, usually a subclass of BasePage.
        """
        if not issubclass(page_class, ttk.Frame):
            raise TypeError(
                f"Page '{name}' must subclass ttk.Frame or BasePage. "
                f"Got {page_class!r}"
            )
        self.page_classes[name] = page_class

    # ------------------------------------------------------------------------------------------------
    def show_page(self, name: str) -> None:
        """
        Switch the visible page to the given name.

        If the page has not been instantiated yet, it is created lazily and cached.
        """
        if name not in self.page_classes:
            raise KeyError(f"Page '{name}' has not been registered.")

        # Hide current page if present
        if self.current_page is not None:
            current_frame = self.page_instances.get(self.current_page)
            if current_frame is not None:
                current_frame.pack_forget()

        # Lazily create the page instance
        if name not in self.page_instances:
            PageClass = self.page_classes[name]
            instance = PageClass(
                parent=self.container,
                controller=self,
                ui=self.ui,
                app_state=self.app_state,
            )
            self.page_instances[name] = instance

        new_frame = self.page_instances[name]
        new_frame.pack(fill="both", expand=True)

        self.current_page = name

    # ------------------------------------------------------------------------------------------------
    def destroy_page(self, name: str) -> None:
        """
        Destroy a cached page (if it exists) and forget it.

        If the destroyed page is the current page, it is first hidden.
        """
        frame = self.page_instances.get(name)
        if frame is None:
            return

        if self.current_page == name:
            frame.pack_forget()
            self.current_page = None

        try:
            frame.destroy()
        except Exception:
            # Fail silently; this is a best-effort cleanup.
            pass

        del self.page_instances[name]


# ====================================================================================================
# 4. BASE PAGE CLASS
# ----------------------------------------------------------------------------------------------------
class BasePage(ttk.Frame):
    """
    Base class for all application pages.

    Provides:
        • self.controller → NavigationController
        • self.ui         → UIPrimitives (wrapping widget/layout primitives)
        • self.app_state  → shared typed state
        • Default padding + style on the root frame
        • Required override: build_page()
    """

    def __init__(
        self,
        parent: tk.Widget,
        controller: NavigationController,
        ui: UIPrimitives,
        app_state: AppState,
        **kwargs: Any,
    ):
        """
        Initialise the page and immediately call build_page().

        Args:
            parent:     Parent container widget, usually NavigationController.container.
            controller: The NavigationController managing this page.
            ui:         Shared UIPrimitives instance.
            app_state:  Shared AppState instance.
        """
        super().__init__(parent, padding=FRAME_PADDING, style="TFrame", **kwargs)

        self.controller: NavigationController = controller
        self.ui: UIPrimitives = ui
        self.app_state: AppState = app_state

        self.build_page()

    # ------------------------------------------------------------------------------------------------
    def build_page(self) -> None:
        """
        Construct the page layout.

        Must be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement build_page().")


# ====================================================================================================
# 5. SANDBOX TEST PAGES
# ----------------------------------------------------------------------------------------------------
class HomePage(BasePage):
    """Simple demo home page to test NavigationController and BasePage."""

    def build_page(self) -> None:
        ui = self.ui

        ui.heading(self, "🏠 Home Page").pack(anchor="w", pady=(0, 20))

        ttk.Button(
            self,
            text="Go To Settings",
            command=lambda: self.controller.show_page("settings"),
        ).pack(anchor="w")


class SettingsPage(BasePage):
    """Simple demo settings page to test NavigationController and BasePage."""

    def build_page(self) -> None:
        ui = self.ui

        ui.heading(self, "⚙ Settings Page").pack(anchor="w", pady=(0, 20))

        ttk.Button(
            self,
            text="Back To Home",
            command=lambda: self.controller.show_page("home"),
        ).pack(anchor="w")


# ====================================================================================================
# 6. STANDALONE SANDBOX LAUNCHER
# ----------------------------------------------------------------------------------------------------
def main() -> None:
    """
    Standalone test window for G03d_app_controller.

    Creates a BaseGUI window, attaches a NavigationController,
    registers demo pages, and shows the home page.
    """
    app = BaseGUI(title="G03d NavigationController Sandbox")

    nav = NavigationController(app)
    nav.register_page("home", HomePage)
    nav.register_page("settings", SettingsPage)

    nav.show_page("home")

    app.mainloop()


if __name__ == "__main__":
    main()
