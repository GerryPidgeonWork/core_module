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
# 2. CLASS — APPLICATION STATE MANAGER
# ----------------------------------------------------------------------------------------------------
class AppState:
    """
    Centralised, strongly-typed state manager for all GUI modules.
    """

    # -----------------------------------------------------------------------------------------------
    # Allowed keys + type definitions + default values
    # -----------------------------------------------------------------------------------------------
    KEYS: Dict[str, Tuple[Tuple[type, ...], Any]] = {
        "last_opened_folder": ((str, type(None)), None),
        "theme": ((str,), "default"),
        "debug_mode": ((bool,), False),
        "session_data": ((dict,), {}),
        "selected_mfc": ((str, type(None)), None),
        "google_drive_letter": ((str,), "G"),
    }

    # -----------------------------------------------------------------------------------------------
    def __init__(self):
        """Initialise state to default values."""
        self._state: Dict[str, Any] = {
            key: default for key, (_, default) in AppState.KEYS.items()
        }

    # =================================================================================================
    # 2.1 VALIDATION UTILITIES
    # =================================================================================================
    def _validate_key(self, key: str) -> None:
        """Ensure the key exists in the schema."""
        if key not in AppState.KEYS:
            raise KeyError(
                f"State key '{key}' is not defined in AppState.KEYS. "
                f"Allowed keys: {list(AppState.KEYS.keys())}"
            )

    def _validate_type(self, key: str, value: Any) -> None:
        """Validate type of assigned value."""
        expected_types = AppState.KEYS[key][0]

        if not isinstance(value, expected_types):
            raise TypeError(
                f"Invalid type for key '{key}': expected {expected_types}, "
                f"got {type(value)} (value: {value!r})"
            )

    # =================================================================================================
    # 2.2 PUBLIC API — GET / SET / UPDATE / RESET
    # =================================================================================================
    def get(self, key: str) -> Any:
        self._validate_key(key)
        return self._state[key]

    def set(self, key: str, value: Any) -> None:
        self._validate_key(key)
        self._validate_type(key, value)
        self._state[key] = value

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            self.set(key, value)

    def reset(self) -> None:
        for key, (_, default) in AppState.KEYS.items():
            self._state[key] = default

    # =================================================================================================
    # 2.3 SERIALISATION — SAVE / LOAD
    # =================================================================================================
    def save_to_json(self, filepath: str) -> bool:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=4)
            return True
        except Exception as e:
            print(f"❌ Failed to save AppState to {filepath}: {e}")
            return False

    def load_from_json(self, filepath: str) -> bool:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            for key, value in data.items():
                if key not in AppState.KEYS:
                    continue
                try:
                    self.set(key, value)
                except Exception:
                    continue

            return True

        except Exception as e:
            print(f"❌ Failed to load AppState from {filepath}: {e}")
            return False

    # =================================================================================================
    # 2.4 UTILITIES
    # =================================================================================================
    def snapshot(self) -> dict:
        return dict(self._state)

    def as_dict(self) -> dict:
        return self.snapshot()

    def diff(self, other_state: dict) -> dict:
        changes = {}
        for key, value in self._state.items():
            if key not in other_state or other_state[key] != value:
                changes[key] = value
        return changes

    def __contains__(self, key: str) -> bool:
        return key in self._state

    def __repr__(self) -> str:
        return f"AppState({self._state})"


# ====================================================================================================
# 3. SANDBOX TEST
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== G05 AppState Sandbox Test ===")
    state = AppState()

    print("\nInitial state:")
    print(state.snapshot())

    print("\nSetting selected_mfc = 'MFC001'")
    state.set("selected_mfc", "MFC001")
    print(state.snapshot())

    print("\nBulk update: debug_mode=True, theme='dark'")
    state.update(debug_mode=True, theme="dark")
    print(state.snapshot())

    print("\nSaving state to 'test_app_state.json'")
    state.save_to_json("test_app_state.json")

    print("\nResetting state to defaults:")
    state.reset()
    print(state.snapshot())

    print("\nLoading state back:")
    state.load_from_json("test_app_state.json")
    print(state.snapshot())

    print("\nState diff vs defaults:")
    print(state.diff(AppState().snapshot()))

    print("\nSandbox test complete.")

