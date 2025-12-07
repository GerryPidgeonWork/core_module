# Project: GUI Framework v1.0
# Module: G04b_navigation
# ----------------------------------------------------------------------------------------------------
# Navigation Engine (Routing Controller)
#
# Purpose:
#   - Manage route registry (Route ID -> Page Class mapping).
#   - Resolve a route ID into a page controller and delegate rendering to G03Renderer.
#   - Maintain history for 'back' functionality.
#   - Orchestrate page lifecycle hooks (on_mount, on_unmount).
#
# Relationships:
#   - G04a AppController: Provides services (state, events, tasks).
#   - G04e Controllers: Provides controller base and injection contract.
#   - G03 Renderer: Builds and mounts all UI.
#
# Design principles:
#   - Must contain zero UI code or styling.
#   - Navigation failure must trigger the G04a error boundary.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-03
# Project:      GUI Framework v1.0
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# CRITICAL FIX: sys.path manipulation block is permanently removed.
# ----------------------------------------------------------------------------------------------------

# --- Future behaviour & type system enhancements -----------------------------------------------------
from __future__ import annotations # Future-proof type hinting (PEP 563 / PEP 649)

# --- Required dependencies ---------------------------------------------------------------------------
import sys                                # Python interpreter access (Allowed system import)
from collections import deque             # Required for History Stack (Allowed stdlib import)
# FIX 1: Removed unused 'from pathlib import Path'

# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
if TYPE_CHECKING:
    from G04a_app_controller import AppController
    from G04e_controllers import BasePageController 


# ====================================================================================================
# G04b Implementation: Navigator
# ====================================================================================================

class Navigator:
    """
    The Navigation Engine for the application.

    Manages route definitions, resolves route IDs to Page classes, handles 
    page lifecycle, and history management for 'back' navigation.
    """
    def __init__(self, app_controller: 'AppController'):
        """
        Initializes the Navigator with a reference to the main AppController.

        Args:
            app_controller: Reference to the main AppController (G04a).
        """
        self.app = app_controller
        self.registry: Dict[str, Type] = {}
        self.history: deque[str] = deque(maxlen=20) 
        self.current_route_id: str | None = None
        self.error_page_class: Type | None = None
        logger.info("[G04b] Navigator initialized.")

    # --- Properties ---

    @property
    def current_route(self) -> str | None:
        """Returns the route ID of the currently active page."""
        return self.current_route_id

    # --- Registration and Setup ---

    def register_routes(self, routes: Dict[str, Type]) -> None:
        """
        Registers a dictionary of routes (ID -> Page Class) with validation.

        Args:
            routes: Dictionary of route IDs mapped to page classes.

        Raises:
            ValueError: If a route ID is not unique or page class is missing required attributes.
        """
        for route_id, page_cls in routes.items():
            if not isinstance(route_id, str):
                raise TypeError(f"Route ID must be a string, got {type(route_id)}.")
            if route_id in self.registry:
                raise ValueError(f"Route ID '{route_id}' is not unique.")
            
            # Validate Page Contract (Required: route, title, build)
            required_attrs = ['route', 'title', 'build']
            if not all(hasattr(page_cls, attr) for attr in required_attrs):
                raise ValueError(f"Page class {page_cls.__name__} must define {required_attrs}.")

            self.registry[route_id] = page_cls
            logger.info(f"[G04b] Registered route: {route_id}")

    def set_error_page(self, ErrorPage: Type) -> None:
        """Sets the error page class for fallback use (required for G04a)."""
        self.error_page_class = ErrorPage
        
    def create_controller(self) -> 'BasePageController':
        """
        Instantiates a Page Controller instance using the full service injection (G04e contract).
        
        Delegates controller creation to the AppController. The AppController then 
        injects all required G04 services (navigation, state, events, tasks) 
        into the controller class.
        """
        return self.app.create_full_service_controller()

    # --- Navigation Core ---

    def to(self, route_id: str, params: Dict[str, Any] | None = None) -> None:
        """
        Navigates to the specified route, managing page lifecycle and delegation.
        """
        if route_id not in self.registry:
            raise ValueError(f"Navigation failed: Route ID '{route_id}' is undefined.")
        if params is not None and not isinstance(params, dict):
            raise TypeError(f"Navigation parameters must be a dictionary or None, got {type(params)}.")

        # 1. Page Unmount (Lifecycle Hook)
        self.unmount_current_page()
        
        # 2. History Management
        if self.current_route_id:
            self.history.append(self.current_route_id)
        self.current_route_id = route_id

        # 3. Route Resolution and Controller Instantiation
        PageClass = self.registry[route_id]
        
        try:
            # G04 creates the controller
            page_controller = self.create_controller()
            
            # 4. Delegate Build and Mount to G03 Renderer (G03 ownership)
            self.app.renderer.render_page(PageClass, page_controller, params)
            
            # 5. Notify BaseWindow of navigation change
            self.app.window.on_navigate(route_id, params or {})

            logger.info(f"[G04b] Navigated to: {route_id} ({PageClass.__name__})")

        except Exception as e:
            # Error Boundary: Hand off to AppController for fail-safe rendering of ErrorPage
            self.app.handle_navigation_error(e)

    def back(self) -> None:
        """Navigates to the previous page in the history stack and publishes an event."""
        if not self.history:
            logger.info("[G04b] Back navigation: History stack is empty (No-op).")
            return

        previous_route = self.history.pop()
        
        self.unmount_current_page()
        self.current_route_id = None 
        
        # Perform the navigation
        self.to(previous_route)
        
        # Publish 'navigation_back' event
        self.app.events.publish("navigation_back", {"route": previous_route})


    # --- Internal Lifecycle Management ---
    
    def unmount_current_page(self) -> None:
        """
        Calls the on_unmount lifecycle hook on the current page if it exists.
        
        Note: This is a conceptual hook for future extension.
        """
        pass