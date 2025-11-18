# ====================================================================================================
# C04_config_loader.py
# ----------------------------------------------------------------------------------------------------
# Centralised configuration loader for CustomPythonCoreFunctions v1.0.
#
# Purpose:
#   - Detect and load configuration files from /config/ directory.
#   - Merge YAML and JSON configuration sources into a unified CONFIG dictionary.
#   - Provide safe lookup and reload utilities.
#   - Log all load operations via the central logging system.
#
# Usage:
#   from core.C04_config_loader import (
#       CONFIG,
#       initialise_config,
#       get_config,
#       reload_config,
#   )
#
#   init_logging()             # from C03, recommended before calling initialise_config()
#   initialise_config()        # explicitly load configuration
#   db_user = get_config("snowflake", "user")
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-18
# Project:      Core Modules (Audited)
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# These imports (sys, pathlib.Path) are required to correctly initialise the project environment,
# ensure the core library can be imported safely (including C00_set_packages.py),
# and prevent project-local paths from overriding installed site-packages.
# ----------------------------------------------------------------------------------------------------

# --- Required for dynamic path handling and safe importing of core modules ---------------------------
import sys
from pathlib import Path

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
# Bring in shared external and standard-library packages from the central import hub.
#
# CRITICAL ARCHITECTURE RULE:
#   ALL external (and commonly-used standard-library) packages must be imported exclusively via:
#       from core.C00_set_packages import *
#   No other script may import external libraries directly.
#
# This module must not import any GUI packages.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
from core.C01_set_file_paths import CONFIG_DIR


# ====================================================================================================
# 3. CONFIGURATION LOADING
# ----------------------------------------------------------------------------------------------------
# Loads configuration files from /config/:
#   - config.yaml / config.yml
#   - settings.json
#
# Values are merged into CONFIG only when explicitly initialised.
# ====================================================================================================

CONFIG: Dict[str, Any] = {}   # <-- IMPORTANT: No auto-loading at import time.

DEFAULT_FILES: Dict[str, List[str]] = {
    "yaml": ["config.yaml", "config.yml"],
    "json": ["settings.json"],
}


def load_yaml_config(path: Path) -> Dict[str, Any]:
    """
    Description:
        Loads a YAML configuration file safely and returns its contents as a
        dictionary.

    Args:
        path (Path): Path to the YAML configuration file.

    Returns:
        Dict[str, Any]: Parsed configuration data, or an empty dictionary if the
        file does not exist or cannot be read/parsed.

    Raises:
        None.

    Notes:
        - Any I/O or parsing errors are logged via log_exception().
        - On error, an empty dictionary is returned rather than raising.
    """
    try:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
        logger.info("Loaded YAML config: %s", path.name)
        return data
    except Exception as exc:
        log_exception(exc, context=f"Loading YAML config: {path}")
        return {}


def load_json_config(path: Path) -> Dict[str, Any]:
    """
    Description:
        Loads a JSON configuration file safely and returns its contents as a
        dictionary.

    Args:
        path (Path): Path to the JSON configuration file.

    Returns:
        Dict[str, Any]: Parsed configuration data, or an empty dictionary if the
        file does not exist or cannot be read/parsed.

    Raises:
        None.

    Notes:
        - Any I/O or parsing errors are logged via log_exception().
        - On error, an empty dictionary is returned rather than raising.
    """
    try:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        logger.info("Loaded JSON config: %s", path.name)
        return data
    except Exception as exc:
        log_exception(exc, context=f"Loading JSON config: {path}")
        return {}


def merge_dicts(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """
    Description:
        Recursively merges one dictionary into another, updating the base mapping
        in place.

    Args:
        base (Dict[str, Any]): Original dictionary to be updated in place.
        update (Dict[str, Any]): Dictionary whose values take precedence on key
            collisions.

    Returns:
        Dict[str, Any]: The merged dictionary (identical object to the base argument).

    Raises:
        None.

    Notes:
        - If both base[key] and update[key] are dictionaries, they are merged
          recursively.
        - Otherwise, the value from update overwrites the value in base.
    """
    for key, value in update.items():
        if isinstance(base.get(key), dict) and isinstance(value, dict):
            base[key] = merge_dicts(base[key], value)
        else:
            base[key] = value
    return base


def initialise_config() -> Dict[str, Any]:
    """
    Description:
        Initialises the global CONFIG mapping by loading all known configuration
        files from the CONFIG_DIR directory.

    Args:
        None.

    Returns:
        Dict[str, Any]: The merged configuration dictionary.

    Raises:
        None.

    Notes:
        - Must be called explicitly; configuration is not loaded at import time.
        - YAML files searched (in order): "config.yaml", "config.yml".
        - JSON files searched: "settings.json".
        - Logs a warning if CONFIG_DIR does not exist.
    """
    global CONFIG
    CONFIG = {}

    try:
        if not CONFIG_DIR.exists():
            logger.warning("Config directory does not exist: %s", CONFIG_DIR)
            return CONFIG

        # YAML files
        for file_name in DEFAULT_FILES["yaml"]:
            path = CONFIG_DIR / file_name
            if path.exists():
                CONFIG = merge_dicts(CONFIG, load_yaml_config(path))

        # JSON files
        for file_name in DEFAULT_FILES["json"]:
            path = CONFIG_DIR / file_name
            if path.exists():
                CONFIG = merge_dicts(CONFIG, load_json_config(path))

        logger.info("Configuration initialised. Sections: %s", list(CONFIG.keys()))
        return CONFIG

    except Exception as exc:
        log_exception(exc, context="initialising configuration")
        return CONFIG


def reload_config() -> Dict[str, Any]:
    """
    Description:
        Reloads all configuration sources into the global CONFIG mapping.

    Args:
        None.

    Returns:
        Dict[str, Any]: The refreshed configuration dictionary.

    Raises:
        None.

    Notes:
        - Thin wrapper around initialise_config() for readability at call sites.
    """
    logger.info("Reloading configuration...")
    return initialise_config()


def get_config(section: str, key: str, default: Any = None) -> Any:
    """
    Description:
        Safely retrieves a configuration value from the global CONFIG mapping.

    Args:
        section (str): Top-level section name within CONFIG (for example,
            "snowflake").
        key (str): Key within the section to look up (for example, "user").
        default (Any, optional): Fallback value if the section or key is missing
            or if an error occurs. Defaults to None.

    Returns:
        Any: The retrieved configuration value, or default if not found or an
        error occurs.

    Raises:
        None.

    Notes:
        - Any unexpected errors during lookup are caught and logged via
          log_exception(), and the default value is returned instead.
    """
    try:
        return CONFIG.get(section, {}).get(key, default)
    except Exception as exc:
        log_exception(
            exc,
            context=f"get_config(section={section!r}, key={key!r})",
        )
        return default


# ====================================================================================================
# 4. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging()
    logger.info("C04_config_loader self-test started.")
    logger.info("CONFIG TEST STARTED")
    logger.info("Config directory: %s", CONFIG_DIR)

    initialise_config()

    loaded_sections = list(CONFIG.keys()) if CONFIG else "No config found"
    logger.info("Loaded configuration sections: %s", loaded_sections)

    logger.info("Test complete.")
    logger.info("C04_config_loader self-test complete.")
