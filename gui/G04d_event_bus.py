# Project: GUI Framework v1.0
# Module: G04d_event_bus
# ----------------------------------------------------------------------------------------------------
# Event Bus (Decoupled Messaging Channel)
#
# Purpose:
#   - Implement a publish/subscribe system for cross-page and application-wide communication.
#   - Decouple components: publishers don't need to know about subscribers.
#   - Ensure all subscriber callbacks are executed safely on the UI thread via G04a executor.
#   - Provide robust error boundaries for subscriber failures.
#
# Relationships:
#   - G04a AppController: Injects the required UI-safe executor method.
#   - G04e Controllers/Pages: Uses subscribe/publish for decoupled events.
#
# Design principles:
#   - Must be 100% UI-free (NO tkinter, NO G00a imports).
#   - Publishing with no subscribers must never raise errors.
#   - One subscriber failing must not block others.
# ----------------------------------------------------------------------------------------------------

from __future__ import annotations

# Allowed system import
import sys

# Project imports
from core.C00_set_packages import Any, Dict, Callable, List
from core.C03_logging_handler import get_logger, log_exception, init_logging

logger = get_logger(__name__)

# ====================================================================================================
# G04d Implementation: EventBus
# ====================================================================================================

class EventBus:
    """
    A decoupled Publish/Subscribe messaging system for cross-component communication.

    It relies on a UI-safe executor (from G04a) to dispatch all callbacks,
    guaranteeing correct execution on the Tkinter main thread.
    """

    def __init__(self, ui_safe_executor: Callable[[Callable, Any], None]):
        """
        Args:
            ui_safe_executor:
                A function injected by G04a that schedules a callback for safe UI-thread execution.
        """
        self.subscribers: Dict[str, List[Callable]] = {}
        self.ui_safe_executor = ui_safe_executor

        logger.info("[G04d] EventBus initialized.")

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------

    def subscribe(self, event: str, callback: Callable) -> None:
        """Registers a callback for an event."""
        if not isinstance(event, str):
            raise TypeError("Event name must be a string.")
        if not callable(callback):
            raise TypeError("Subscription callback must be callable.")

        if event not in self.subscribers:
            self.subscribers[event] = []

        if callback not in self.subscribers[event]:
            self.subscribers[event].append(callback)
            logger.info(f"Subscribed '{callback.__name__}' to event '{event}'.")

    def publish(self, event: str, payload: Dict[str, Any] | None = None) -> None:
        """
        Publishes an event and dispatches to all registered subscribers.
        """
        if not isinstance(event, str):
            raise TypeError("Event name must be a string.")

        subscribers_list = self.subscribers.get(event, [])
        if not subscribers_list:
            return  # Silent no-op

        logger.info(f"Publishing event '{event}' to {len(subscribers_list)} subscribers.")

        for callback in subscribers_list:
            # UI-safe executor will catch errors inside callback
            try:
                self.ui_safe_executor(callback, payload or {})
            except Exception as e:
                # Executor errors are extremely rare, but still logged
                log_exception(
                    e,
                    logger=logger,
                    context=f"EventBus executor error for event '{event}'"
                )

    def unsubscribe(self, event: str, callback: Callable) -> None:
        """
        Removes a previously registered callback.

        Silent no-op if callback is missing.
        """
        if event in self.subscribers:
            try:
                self.subscribers[event].remove(callback)
                logger.info(f"Unsubscribed '{callback.__name__}' from event '{event}'.")
            except ValueError:
                pass  # Silent no-op
