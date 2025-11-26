# ====================================================================================================
# G03d_app_state.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Centralised, strongly-typed application-state manager for the GUI layer.
#
#   This module provides a SINGLE source of truth for all runtime GUI variables, including:
#       • user selections (MFC, theme, folders, parameters)
#       • global flags (debug_mode, theme mode)
#       • session-level caches and shared values between pages
#
# Responsibilities:
#   • Maintain a strict schema of allowed state keys (with type hints + defaults).
#   • Provide safe get() / set() / update() operations with validation.
#   • Support full reset-to-defaults capability.
#   • Provide JSON serialisation helpers for saving/loading session state.
#   • Never allow arbitrary keys or incorrect types into state.
#
# Architectural Role:
#   • Lives in G03 (“Reusable Widgets & UI Patterns”) namespace.
#   • Does NOT import or depend on GUI widgets, layout primitives, or BaseGUI.
#   • Can be safely used by any page, controller, or background process.
#   • Enforces strict typing for all UI-shared state across the system.
#
# Integration:
#       from gui.G03d_app_state import AppState
#       state = AppState()
#       state.set("selected_mfc", "MFC001")
#
# Rules:
#   • No Tkinter/ttk imports (must remain pure logic).
#   • No side effects at import time.
#   • All valid state keys must be declared in AppState.KEYS.
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


# ====================================================================================================
# 3. APPLICATION STATE MANAGER (REWRITTEN + FULLY STANDARDS-COMPLIANT)
# ----------------------------------------------------------------------------------------------------
class AppState:
    """
    Description:
        Strongly-typed centralised state manager for all GUI runtime variables.
        This class stores only validated keys defined in the KEYS catalogue, each
        with explicit allowed types and default values.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - State keys must be declared in the KEYS dictionary.
        - No GUI imports should ever be added here.
        - Defaults for mutable types (e.g., dict) are deep-copied to prevent
          instance-level contamination.
    """

    # Allowed keys + (allowed types, default value template)
    KEYS: Dict[str, Tuple[Tuple[type, ...], Any]] = {
        "last_opened_folder": ((str, type(None)), None),
        "theme": ((str,), "default"),
        "debug_mode": ((bool,), False),
        "session_data": ((dict,), {}),     # default is deep-copied at init/reset
        "selected_mfc": ((str, type(None)), None),
        "google_drive_letter": ((str,), "G"),
    }

    def __init__(self) -> None:
        """
        Description:
            Initialise state to clean default values by deep-copying any mutable
            default values to ensure state isolation across instances.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        self.state_map: Dict[str, Any] = {}
        for key, (_, default) in AppState.KEYS.items():
            # Safe copy for mutable types (dict, list, set)
            self.state_map[key] = deepcopy(default) if isinstance(default, (dict, list, set)) else default

    # ------------------------------------------------------------------------------------------------
    # INTERNAL VALIDATION HELPERS — PUBLIC NAME (NO UNDERSCORES)
    # ------------------------------------------------------------------------------------------------
    def validate_state_key(self, key: str) -> None:
        """
        Description:
            Validate that the supplied key exists in the AppState schema.

        Args:
            key (str): The key to validate.

        Returns:
            None.

        Raises:
            KeyError: If the key is not allowed.

        Notes:
            - This function ensures all state access is schema-safe.
        """
        if key not in AppState.KEYS:
            raise KeyError(
                f"Invalid state key '{key}'. Allowed keys: {list(AppState.KEYS.keys())}"
            )

    def validate_state_type(self, key: str, value: Any) -> None:
        """
        Description:
            Validate that the supplied value matches the allowed types for a given key.

        Args:
            key (str): The state key.
            value (Any): The value to validate.

        Returns:
            None.

        Raises:
            TypeError: If the value type is not among the allowed types.

        Notes:
            - Allowed types are defined in AppState.KEYS.
        """
        expected_types = AppState.KEYS[key][0]
        if not isinstance(value, expected_types):
            raise TypeError(
                f"Invalid type for '{key}': expected {expected_types}, got {type(value)} (value={value!r})"
            )

    # ------------------------------------------------------------------------------------------------
    # PUBLIC API METHODS
    # ------------------------------------------------------------------------------------------------
    def get_state(self, key: str) -> Any:
        """
        Description:
            Retrieve a state value after validating the key.

        Args:
            key (str): The state key to retrieve.

        Returns:
            Any: The current value for this key.

        Raises:
            KeyError: If the key is invalid.

        Notes:
            - Values are returned exactly as stored.
        """
        self.validate_state_key(key)
        return self.state_map[key]

    def set_state(self, key: str, value: Any) -> None:
        """
        Description:
            Assign a value to a state key after validating both the key and the value type.

        Args:
            key (str): State key.
            value (Any): New value to assign.

        Returns:
            None.

        Raises:
            KeyError: Invalid key.
            TypeError: Invalid value type.

        Notes:
            - Mutable values are assigned directly (caller manages lifecycle).
        """
        self.validate_state_key(key)
        self.validate_state_type(key, value)
        self.state_map[key] = value

    def update_state(self, **kwargs: Any) -> None:
        """
        Description:
            Convenience method to update multiple state fields at once.

        Args:
            **kwargs: Key/value pairs to update.

        Returns:
            None.

        Raises:
            KeyError: For any invalid key.
            TypeError: For any invalid value.

        Notes:
            - Equivalent to multiple calls to set_state().
        """
        for key, value in kwargs.items():
            self.set_state(key, value)

    def reset_state(self) -> None:
        """
        Description:
            Reset all state keys to their default values.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Mutable defaults are deep-copied to avoid shared state.
        """
        for key, (_, default) in AppState.KEYS.items():
            self.state_map[key] = deepcopy(default) if isinstance(default, (dict, list, set)) else default

    # ------------------------------------------------------------------------------------------------
    # SERIALISATION HELPERS
    # ------------------------------------------------------------------------------------------------
    def save_to_json(self, filepath: str) -> bool:
        """
        Description:
            Save the current application state to a JSON file.

        Args:
            filepath (str): Path to the JSON file.

        Returns:
            bool: True on success, False on failure.

        Raises:
            None.

        Notes:
            - File is written in UTF-8 with indentation.
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.state_map, f, indent=4)
            return True
        except Exception as e:
            logger.error("Failed to save AppState to '%s': %s", filepath, e)
            return False

    def load_from_json(self, filepath: str) -> bool:
        """
        Description:
            Load application state from a JSON file.

        Args:
            filepath (str): Path to the JSON file.

        Returns:
            bool: True if data was loaded successfully, False otherwise.

        Raises:
            None.

        Notes:
            - Invalid keys are ignored.
            - Invalid value types are skipped safely.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            for key, value in data.items():
                if key not in AppState.KEYS:
                    continue
                try:
                    self.set_state(key, value)
                except Exception:
                    continue

            return True

        except Exception as e:
            logger.error("Failed to load AppState from '%s': %s", filepath, e)
            return False

    # ------------------------------------------------------------------------------------------------
    # UTILITY METHODS
    # ------------------------------------------------------------------------------------------------
    def snapshot(self) -> dict:
        """
        Description:
            Return a shallow copy of the current state dictionary.

        Args:
            None.

        Returns:
            dict: A copy of the state_map.

        Raises:
            None.
        """
        return dict(self.state_map)

    def as_dict(self) -> dict:
        """
        Description:
            Alias for snapshot().

        Args:
            None.

        Returns:
            dict.
        """
        return self.snapshot()

    def diff_state(self, other: dict) -> dict:
        """
        Description:
            Compare this state against another dictionary and return only keys that differ.

        Args:
            other (dict): Dictionary to compare against.

        Returns:
            dict: Mapping of differing keys → current values.

        Raises:
            None.

        Notes:
            - Useful for debugging and change detection.
        """
        return {k: v for k, v in self.state_map.items() if k not in other or other[k] != v}

    def __contains__(self, key: str) -> bool:
        """Allow usage of: 'if key in state:' """
        return key in self.state_map

    def __repr__(self) -> str:
        """Friendly debug representation."""
        return f"AppState({self.state_map})"


# ====================================================================================================
# 4. SANDBOX TEST
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging()
    logger.info("=== G03d_app_state.py — Sandbox Test Start ===")

    state = AppState()

    logger.info("Initial state: %s", state.snapshot())

    logger.info("Setting selected_mfc = 'MFC001'")
    state.set_state("selected_mfc", "MFC001")
    logger.info("State: %s", state.snapshot())

    logger.info("Bulk update: debug_mode=True, theme='dark'")
    state.update_state(debug_mode=True, theme="dark")
    logger.info("State: %s", state.snapshot())

    logger.info("Saving state to 'test_app_state.json'")
    state.save_to_json("test_app_state.json")

    logger.info("Resetting state to defaults")
    state.reset_state()
    logger.info("State: %s", state.snapshot())

    logger.info("Loading state back from JSON")
    state.load_from_json("test_app_state.json")
    logger.info("State: %s", state.snapshot())

    logger.info("State diff vs defaults: %s", state.diff_state(AppState().snapshot()))

    logger.info("=== G03d_app_state.py — Sandbox Test End ===")
