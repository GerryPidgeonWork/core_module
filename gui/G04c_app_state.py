# Project: GUI Framework v1.0
# Module: G04c_app_state
# ----------------------------------------------------------------------------------------------------
# Application State Engine (Global Reactive Store)
#
# Purpose:
#   - Store session-wide application state (filters, user prefs, session data).
#   - Provide typed getters/setters with validation against the initial type.
#   - Support subscription for reactive updates via on_change callbacks.
#   - Maintain an immutable update pattern (data mutation is internal).
#
# Relationships:
#   - G04a AppController: Owns the instance and provides global state access methods.
#   - G04e Controllers: Accesses state via self.state.get() and self.state.set().
#
# Design principles:
#   - Must be 100% UI-free (NO tkinter, NO G00a/G01/G02 imports).
#   - Must enforce strict type checking on mutations.
#   - Subscriber errors must not break the state engine.
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-07
# Project:      GUI Framework v1.0
# ====================================================================================================

from __future__ import annotations

# Allowed system imports
import sys

# Project imports
from core.C00_set_packages import *
from core.C03_logging_handler import get_logger, log_exception, init_logging

logger = get_logger(__name__)

class AppState:
    """
    Global reactive state engine (Central Store).

    Supports typed state slices, subscription model, and enforces strict type 
    checking on mutation to maintain data integrity across the application session.
    """

    def __init__(self):
        self.state: Dict[str, Any] = {}
        self.type_registry: Dict[str, Type] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        logger.info("[G04c] AppState initialized.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def define(self, key: str, initial_value: Any) -> None:
        """Defines a new state slice with an initial value and enforced type."""
        if not isinstance(key, str):
            raise TypeError(f"State key must be a string, got {type(key)}.")
        if key in self.state:
            raise ValueError(f"State key '{key}' is already defined.")

        self.state[key] = initial_value
        self.type_registry[key] = type(initial_value)
        self.subscribers[key] = []

        logger.info(f"Defined state slice: '{key}' (Initial type: {self.type_registry[key].__name__})")

    def get(self, key: str) -> Any:
        """Retrieves the current value of a state slice."""
        if key not in self.state:
            raise KeyError(f"State key '{key}' is undefined. Must call define() first.")
        return self.state[key]

    def set(self, key: str, value: Any) -> None:
        """Updates the value of a state slice, enforcing type checks and notifying subscribers."""
        if key not in self.state:
            raise KeyError(f"State key '{key}' is undefined. Must call define() first.")

        original_type = self.type_registry[key]
        incoming_type = type(value)

        # Type rules:
        # - initial type NoneType => allow any new type
        # - new value None => always allowed
        # - otherwise: types must match
        if original_type is not type(None) and incoming_type not in (original_type, type(None)):
            raise TypeError(
                f"State '{key}' type mismatch. Expected {original_type.__name__}, got {incoming_type.__name__}."
            )

        if self.state[key] == value:
            return  # No change, no notification

        self.state[key] = value
        logger.info(f"State '{key}' updated. Notifying {len(self.subscribers[key])} subscribers.")
        self.notify_subscribers(key, value)

    def subscribe(self, key: str, callback: Callable) -> None:
        """Registers a callback for reactive state updates."""
        if key not in self.subscribers:
            raise KeyError(f"State key '{key}' is undefined. Must call define() first.")
        if not callable(callback):
            raise TypeError("Subscription callback must be callable.")

        if callback not in self.subscribers[key]:
            self.subscribers[key].append(callback)
            logger.info(f"Subscribed '{callback.__name__}' to state key '{key}'.")

    def unsubscribe(self, key: str, callback: Callable) -> None:
        """Removes a previously registered callback."""
        if key in self.subscribers:
            self.subscribers[key] = [
                fn for fn in self.subscribers[key] if fn != callback
            ]

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def notify_subscribers(self, key: str, new_value: Any) -> None:
        """Executes all subscribers with error isolation."""
        for callback in self.subscribers.get(key, []):
            try:
                callback(new_value)
            except Exception as e:
                log_exception(
                    e,
                    logger=logger,
                    context=f"State Subscriber Error in '{callback.__name__}' for key '{key}'"
                )
