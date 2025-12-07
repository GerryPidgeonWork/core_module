# Project: GUI Framework v1.0
# Module: G03f_renderer
# ----------------------------------------------------------------------------------------------------
# Renderer (UI Factory and Mounting Delegate)
#
# Purpose:
#   - Implement the G03Renderer contract required by G04a/G04b.
#   - Act as the sole point of instantiation for Page classes in the framework.
#   - Call page lifecycle methods (build) and mount the resulting UI frame into the BaseWindow.
#   - Maintain the architectural boundary: G03 handles construction, G04 handles orchestration.
#
# Relationships:
#   - G04: Calls render_page/render_error_page to delegate UI creation.
#   - G02c: BaseWindow provides the set_content() method for mounting.
#   - Pages (G03): Provides the __init__ and build() methods.
#
# Design principles:
#   - Must be the ONLY part of the framework that calls PageClass() or page.build().
#   - Must NOT contain business logic or import G04 components.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-07
# Project:      GUI Framework v1.0
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

# --- Remove '' (current working directory) which can shadow installed packages ----------------------
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
from gui.G00a_gui_packages import tk 
# BaseWindow contract imported via the correct module path
from gui.G02c_gui_base import BaseWindow 


# ====================================================================================================
# 3. PROTOCOL FOR WINDOW INJECTION
# ----------------------------------------------------------------------------------------------------
# G03Renderer must accept:
#   - real BaseWindow implementations (G02c)
#   - mock window objects in self-tests
#
# Structural typing avoids forcing inheritance.
# ====================================================================================================

class WindowProtocol(Protocol):
    content_frame: Any
    def set_content(self, frame: Any) -> None:
        ...


# ====================================================================================================
# 4. G03f IMPLEMENTATION: G03Renderer
# ====================================================================================================

class G03Renderer:
    """
    The UI Factory for the GUI Framework.

    G04 delegates all UI construction to this class.
    G03Renderer instantiates pages, calls build(), and mounts the resulting Frame.
    """

    def __init__(self):
        self.window: WindowProtocol | None = None
        logger.info("[G03f] Renderer initialised.")

    def set_window(self, window: WindowProtocol) -> None:
        """Inject the BaseWindow (or mock) into the renderer."""
        self.window = window
        logger.info("[G03f] BaseWindow reference injected.")

    # ------------------------------------------------------------------------------------------------

    def render_page(self, PageClass: Type, controller: Any, params: Dict[str, Any] | None = None) -> None:
        """
        Instantiate and mount a Page.

        G04b Navigator calls this as part of the routing flow.
        """
        if self.window is None:
            raise RuntimeError("Renderer must receive BaseWindow via set_window() before rendering.")

        try:
            logger.info(f"[G03f] Rendering page: {PageClass.__name__}")

            # 1. Instantiate page (G03 owns lifecycle)
            page_instance = PageClass(controller)

            # 2. Parent frame for building UI
            parent_frame = self.window.content_frame

            # 3. Build the page
            content_frame = page_instance.build(parent_frame, params or {})

            # 4. Mount result
            self.window.set_content(content_frame)

            logger.info(f"[G03f] Successfully mounted: {PageClass.__name__}")

        except Exception as e:
            log_exception(e, logger, f"G03 Page Render Failure in {PageClass.__name__}")
            raise

    # ------------------------------------------------------------------------------------------------

    def render_error_page(self, ErrorPageClass: Type, controller: Any, message: str) -> None:
        """
        Render the fallback UI when G04a catches an exception.
        """
        if self.window is None:
            raise RuntimeError("Renderer must receive BaseWindow via set_window() before rendering.")

        try:
            logger.error(f"[G03f] Mounting ErrorPage: {message[:100]}")

            # 1. Instantiate error page
            error_page_instance = ErrorPageClass(controller)

            # 2. Build with message injected through params
            parent_frame = self.window.content_frame
            error_frame = error_page_instance.build(parent_frame, {"message": message})

            # 3. Mount fallback
            self.window.set_content(error_frame)

            logger.error("[G03f] ErrorPage mounted successfully.")

        except Exception as e:
            log_exception(e, logger, "G03 FATAL: ErrorPage Rendering Failed.")
            pass   # Final line of defence — cannot re-raise here


# ====================================================================================================
# 5. PUBLIC API
# ----------------------------------------------------------------------------------------------------

__all__ = [
    "G03Renderer",
]


# ====================================================================================================
# 6. SELF-TEST (Non-Tk Safe)
# ----------------------------------------------------------------------------------------------------
# G03 must not create real windows during smoke tests.
# We use mock objects to verify:
#   - set_window()
#   - render_page() lifecycle
#   - build() → content_frame → set_content()
# ====================================================================================================

if __name__ == "__main__":
    init_logging()
    logger.info("[G03f] Running Renderer smoke test...")

    class MockFrame:
        pass

    class MockBaseWindow:
        def __init__(self):
            self.content_frame = MockFrame()
            self.last_frame_set = None

        def set_content(self, frame):
            self.last_frame_set = frame
            logger.info("[MockBaseWindow] set_content called.")

    class MockPage:
        def __init__(self, controller):
            self.controller = controller

        def build(self, parent_frame, params=None):
            logger.info(f"[MockPage] build called with params={params}")
            return MockFrame()

    try:
        renderer = G03Renderer()
        mock_window = MockBaseWindow()
        renderer.set_window(mock_window)

        # Test page rendering
        renderer.render_page(MockPage, controller=None, params={"ok": True})

        assert mock_window.last_frame_set is not None, \
            "Smoke test failed: set_content() was not called."

        logger.info("[G03f] Smoke test PASSED.")

    except Exception as exc:
        log_exception(exc, logger, "G03f Renderer Smoke Test Failure")
