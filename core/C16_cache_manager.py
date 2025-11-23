# ====================================================================================================
# C16_cache_manager.py
# ----------------------------------------------------------------------------------------------------
# Provides a lightweight caching framework for temporary or reusable data.
#
# Purpose:
#   - Store and retrieve frequently used data (e.g., API responses, DataFrames, query results).
#   - Improve performance by avoiding repeated expensive operations.
#   - Ensure consistent cache directory handling across all projects.
#
# Supported Formats:
#   - JSON for dictionary-like data.
#   - CSV for Pandas DataFrames.
#   - Pickle for arbitrary Python objects.
#
# Usage:
#   from core.C16_cache_manager import (
#       save_cache,
#       load_cache,
#       clear_cache,
#       list_cache_files,
#       get_cache_path,
#   )
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
from core.C01_set_file_paths import PROJECT_ROOT
from core.C07_datetime_utils import as_str, get_today
from core.C06_validation_utils import validate_directory_exists


# ====================================================================================================
# 3. GLOBAL SETTINGS
# ----------------------------------------------------------------------------------------------------
# NOTE:
#   - CACHE_DIR is defined as a Path but the directory is NOT created at import time.
#   - Use ensure_cache_dir() to create/validate the cache directory when needed.
# ----------------------------------------------------------------------------------------------------
CACHE_DIR: Path = PROJECT_ROOT / "cache"


def ensure_cache_dir() -> Path:
    """
    Summary:
        Ensure that the cache directory exists and return its path.

    Extended Description:
        This helper validates the cache directory using validate_directory_exists()
        with create_if_missing=True. It centralises cache-directory creation logic
        so that no directory is created at import time, only at runtime when
        caching is actually required.

    Args:
        None.

    Returns:
        Path:
            The validated cache directory path as a Path instance.

    Raises:
        FileNotFoundError:
            Propagated from validate_directory_exists() if directory creation fails
            and the underlying function raises.

    Notes:
        This function may be called multiple times safely; the underlying directory
        creation uses exist_ok=True semantics via validate_directory_exists().
    """
    validate_directory_exists(CACHE_DIR, create_if_missing=True)
    return CACHE_DIR


# ====================================================================================================
# 4. CORE CACHE FUNCTIONS
# ----------------------------------------------------------------------------------------------------
def get_cache_path(name: str, fmt: str = "json") -> Path:
    """
    Summary:
        Build the full path to a cache file in the cache directory.

    Extended Description:
        This function converts a logical cache name (for example, "orders_today")
        into a concrete filesystem path under the cache directory. It normalises
        the requested format and applies an appropriate filename extension.

    Args:
        name (str):
            Logical name for the cache file (for example, "orders_today").
        fmt (str, optional):
            File format for the cache. Supported options are:
                - "json": JSON object.
                - "csv":  Pandas DataFrame.
                - "pkl":  Pickled Python object.
            Defaults to "json".

    Returns:
        Path:
            Fully resolved filesystem path of the cache file in CACHE_DIR.

    Raises:
        None.

    Notes:
        If an unrecognised format is supplied, the extension defaults to ".json"
        but no validation is performed here. Validation is enforced in save_cache()
        and load_cache().
    """
    base_dir = ensure_cache_dir()
    extension_map = {"json": ".json", "csv": ".csv", "pkl": ".pkl"}
    ext = extension_map.get(fmt.lower(), ".json")
    return base_dir / f"{name}{ext}"


def save_cache(name: str, data: Any, fmt: str = "json") -> Path | None:
    """
    Summary:
        Save data to a cache file in the specified format.

    Extended Description:
        This function writes cache data in one of three supported formats:
        JSON, CSV (for pandas DataFrames), or pickle (for arbitrary objects).
        It ensures that the cache directory exists, validates the requested
        cache format, and logs the outcome of the save operation.

    Args:
        name (str):
            Name of the cache file without extension.
        data (Any):
            The data or object to be cached. For CSV format, this must be a
            pandas DataFrame instance.
        fmt (str, optional):
            Cache format, one of:
                - "json"
                - "csv"
                - "pkl"
            Defaults to "json".

    Returns:
        Path | None:
            The Path where the cache was saved on success; otherwise None if an
            error occurs during serialisation or I/O.

    Raises:
        ValueError:
            If an unsupported cache format is requested or if CSV format is used
            with a non-DataFrame object.

    Notes:
        - All unexpected exceptions are logged via log_exception() and result in
          a None return value.
        - JSON caches are written with UTF-8 encoding and indent=2.
    """
    fmt = fmt.lower()
    if fmt not in {"json", "csv", "pkl"}:
        raise ValueError("Unsupported cache format '"
                         f"{fmt}'. Use 'json', 'csv', or 'pkl'.")

    path = get_cache_path(name, fmt)

    try:
        if fmt == "json":
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        elif fmt == "csv":
            if not isinstance(data, pd.DataFrame):
                raise ValueError("CSV cache format requires a pandas DataFrame.")
            data.to_csv(path, index=False)
        else:  # "pkl"
            with open(path, "wb") as file:
                pickle.dump(data, file)

        logger.info("💾 Cache saved: %s", path.name)
        return path

    except Exception as error:
        log_exception(error, context=f"saving cache '{name}' ({fmt})")
        return None


def load_cache(name: str, fmt: str = "json") -> Any:
    """
    Summary:
        Load cached data from disk if it exists.

    Extended Description:
        This function reconstructs the appropriate cache path based on the cache
        name and format, checks for existence, and loads the cached data using
        the matching deserialisation method (JSON, CSV, or pickle).

    Args:
        name (str):
            Name of the cache file without extension.
        fmt (str, optional):
            Cache file format. Supported values:
                - "json"
                - "csv"
                - "pkl"
            Defaults to "json".

    Returns:
        Any:
            The loaded cached data (for example, dict, DataFrame, or arbitrary
            Python object), or None if the cache file does not exist or an
            unexpected error occurs.

    Raises:
        ValueError:
            If an unsupported cache format is requested.

    Notes:
        - Missing cache files are treated as a non-error condition; the function
          logs a warning and returns None.
        - Unexpected exceptions are logged via log_exception() and result in
          a None return value.
    """
    fmt = fmt.lower()
    if fmt not in {"json", "csv", "pkl"}:
        raise ValueError("Unsupported cache format '"
                         f"{fmt}'. Use 'json', 'csv', or 'pkl'.")

    path = get_cache_path(name, fmt)

    if not path.exists():
        logger.warning("⚠️  Cache not found: %s", path.name)
        return None

    try:
        if fmt == "json":
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
        elif fmt == "csv":
            data = pd.read_csv(path)
        else:
            with open(path, "rb") as file:
                data = pickle.load(file)

        logger.info("✅ Cache loaded: %s", path.name)
        return data

    except Exception as error:
        log_exception(error, context=f"loading cache '{name}' ({fmt})")
        return None


def clear_cache(name: str | None = None) -> None:
    """
    Summary:
        Delete one specific cache or clear all cache files.

    Extended Description:
        This function supports two modes:
        - When a cache name is provided, it attempts to delete all file variants
          (JSON, CSV, PKL) corresponding to that name.
        - When name is None, it deletes all files currently present in the cache
          directory.

    Args:
        name (str | None):
            Identifier of a specific cache to remove. If None, all cache files
            in CACHE_DIR are deleted.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Any file-system errors encountered during deletion are logged via
          log_exception() and do not stop processing of other files.
        - If a specific named cache is not found, a warning is logged.
    """
    base_dir = ensure_cache_dir()

    if name:
        deleted = False
        for fmt in ("json", "csv", "pkl"):
            path = get_cache_path(name, fmt)
            if path.exists():
                try:
                    path.unlink()
                    logger.info("🗑️  Deleted cache: %s", path.name)
                    deleted = True
                except Exception as error:
                    log_exception(error, context=f"deleting cache file '{path}'")
        if not deleted:
            logger.warning("⚠️  No cache found for '%s'.", name)
    else:
        files = list(base_dir.glob("*"))
        for file_path in files:
            try:
                file_path.unlink()
            except Exception as error:
                log_exception(error, context=f"clearing cache file '{file_path}'")
        logger.info("🧹 Cleared %d cache file(s) from %s.", len(files), base_dir)


def list_cache_files() -> list[Path]:
    """
    Summary:
        List all cache files currently present in the cache directory.

    Extended Description:
        This helper ensures that the cache directory exists and then enumerates
        all files within it. It provides a simple overview of the current cache
        footprint for diagnostics and housekeeping.

    Args:
        None.

    Returns:
        list[Path]:
            List of Path objects representing cache files found in CACHE_DIR.

    Raises:
        None.

    Notes:
        The result includes all files in the cache directory, irrespective of
        extension or format.
    """
    base_dir = ensure_cache_dir()
    files = list(base_dir.glob("*"))
    logger.info("📦 Found %d cached file(s).", len(files))
    return files


# ====================================================================================================
# 5. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Summary:
        Run a standalone self-test of the cache manager.

    Extended Description:
        This self-test exercises the core cache operations by:
            - Creating sample JSON, CSV, and pickle caches.
            - Loading them back from disk.
            - Listing all cache files.
            - Clearing the test caches and confirming the directory contents.
        All feedback is written via the logging system; no print() calls are used,
        in line with core module self-test rules.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        Run from the core directory, for example:
            python C16_cache_manager.py
    """
    init_logging(enable_console=True)
    logger.info("🔍 C16_cache_manager self-test started.")

    cache_dir = ensure_cache_dir()
    logger.info("📁 Cache directory in use: %s", cache_dir)

    # Example data for test caches
    sample_data = {
        "user": "gerry",
        "date": as_str(get_today()),
        "value": 123,
    }
    df = pd.DataFrame(
        [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    )

    # --- Save test caches ---------------------------------------------------------------------------
    save_cache("test_json", sample_data, "json")
    save_cache("test_csv", df, "csv")
    save_cache("test_pickle", df, "pkl")

    # --- Load test caches ---------------------------------------------------------------------------
    json_cache = load_cache("test_json", "json")
    csv_cache = load_cache("test_csv", "csv")
    pkl_cache = load_cache("test_pickle", "pkl")

    logger.info("📥 Loaded JSON cache: %s", json_cache)
    logger.info(
        "📥 Loaded CSV cache shape: %s",
        csv_cache.shape if isinstance(csv_cache, pd.DataFrame) else "N/A",
    )
    logger.info("📥 Loaded PKL cache type: %s", type(pkl_cache).__name__)

    # --- List all cache files -----------------------------------------------------------------------
    files = list_cache_files()
    logger.info("📃 Cache files after save: %s", [file.name for file in files])

    # --- Clear test caches --------------------------------------------------------------------------
    clear_cache("test_json")
    clear_cache("test_csv")
    clear_cache("test_pickle")

    remaining_files = list_cache_files()
    logger.info("📃 Cache files after clear: %s", [file.name for file in remaining_files])

    logger.info("✅ C16_cache_manager self-test complete.")
