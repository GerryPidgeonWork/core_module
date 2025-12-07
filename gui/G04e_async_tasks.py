# Project: GUI Framework v1.0
# Module: G04e_async_tasks
# ----------------------------------------------------------------------------------------------------
# Async Task Manager (Background Execution Engine)
#
# Purpose:
#   - Execute long-running functions in background worker threads (non-blocking UI).
#   - Guarantee thread-safe UI handoff for on_done/on_error callbacks.
#   - Prevent background exceptions from ever crashing the main UI thread.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-07
# Project:      GUI Framework v1.0
# ====================================================================================================

from __future__ import annotations

# Allowed system imports
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

# Project imports
from core.C00_set_packages import Any, Callable, Type
from core.C03_logging_handler import get_logger, log_exception, init_logging

if TYPE_CHECKING:
    from gui.G00a_gui_packages import tk  # For type hints only

logger = get_logger(__name__)

# ====================================================================================================
# G04e Implementation: TaskManager
# ====================================================================================================

class TaskManager:
    """
    Manages background worker execution using a ThreadPoolExecutor.

    Ensures thread-safe callback execution on the Tkinter main thread
    by routing all completion and error handling through root.after().
    """

    DEFAULT_MAX_WORKERS = 5

    def __init__(self, max_workers: int = DEFAULT_MAX_WORKERS):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.root: 'tk.Tk' | None = None
        logger.info(f"[G04e] TaskManager initialized with {max_workers} workers.")

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def set_root(self, root: 'tk.Tk') -> None:
        """Called by G04a to provide Tk root for main-thread scheduling."""
        self.root = root
        logger.info("[G04e] Tk root reference set for UI handoff.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        fn: Callable,
        *args,
        on_done: Callable | None = None,
        on_error: Callable | None = None
    ):
        """
        Schedules a function to run in the background.

        Args:
            fn: Background function to run.
            *args: Arguments to pass to fn.
            on_done: UI-thread callback executed with fn(result).
            on_error: UI-thread callback executed with fn(exception).

        Returns:
            A Future representing the background computation.
        """

        if not callable(fn):
            raise TypeError("Background function 'fn' must be callable.")
        if on_done is not None and not callable(on_done):
            raise TypeError("'on_done' must be callable or None.")
        if on_error is not None and not callable(on_error):
            raise TypeError("'on_error' must be callable or None.")
        if self.root is None:
            raise RuntimeError("TaskManager not initialized. Call set_root() first.")

        future = self.executor.submit(fn, *args)
        future.add_done_callback(lambda f: self._handle_completion(f, on_done, on_error))
        return future

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _handle_completion(
        self,
        future,
        on_done: Callable | None,
        on_error: Callable | None
    ) -> None:
        """
        Background-thread callback triggered when Future completes.
        Schedules UI-thread handlers via root.after().
        """
        if self.root is None:
            logger.error("FATAL: TaskManager root lost; cannot perform UI handoff.")
            return

        try:
            result = future.result()
            if on_done:
                self.root.after(0, lambda: self._execute_safe_handler(on_done, result))
        except Exception as e:
            if on_error:
                self.root.after(0, lambda: self._execute_safe_handler(on_error, e))
            else:
                # If no user error handler is provided, log the exception via C03
                self.root.after(
                    0,
                    lambda: log_exception(
                        e,
                        logger=logger,
                        context="Async Task Unhandled Error"
                    )
                )

    def _execute_safe_handler(self, handler: Callable, *args) -> None:
        """Executes a UI-thread handler inside an error boundary."""
        try:
            handler(*args)
        except Exception as e:
            log_exception(
                e,
                logger=logger,
                context=f"Async Handler Error in '{handler.__name__}'"
            )
