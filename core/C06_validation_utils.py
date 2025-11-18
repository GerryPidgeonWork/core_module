# ====================================================================================================
# C06_validation_utils.py
# ----------------------------------------------------------------------------------------------------
# Provides shared validation and sanity-check utilities for CustomPythonCoreFunctions v1.0.
#
# Purpose:
#   - Centralise reusable validation logic for files, directories, data frames, and configuration.
#   - Provide consistent, logged validation across CLI, GUI, and automation contexts.
#   - Ensure early detection of missing inputs, invalid structures, and configuration issues.
#
# Usage:
#   from core.C06_validation_utils import *
#
#   validate_file_exists("data/orders.csv")
#   validate_required_columns(df, ["order_id", "amount", "date"])
#   validate_config_keys("snowflake", ["user", "account"])
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
from core.C01_set_file_paths import PROJECT_ROOT, LOGS_DIR, CONFIG_DIR
from core.C04_config_loader import get_config


# ====================================================================================================
# 3. FILE & DIRECTORY VALIDATION
# ----------------------------------------------------------------------------------------------------
def validate_file_exists(file_path: str | Path) -> bool:
    """
    Description:
        Validates that the specified file exists and is accessible.

    Args:
        file_path (str | Path): Path to the required file.

    Returns:
        bool: True if the file exists.

    Raises:
        FileNotFoundError: If the file does not exist or is not a file.

    Notes:
        - Logs both success and failure scenarios.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        logger.error("❌ File not found: %s", path)
        raise FileNotFoundError(f"Required file not found: {path}")

    logger.info("✅ File exists: %s", path)
    return True


def validate_directory_exists(dir_path: str | Path, create_if_missing: bool = False) -> bool:
    """
    Description:
        Validates that a directory exists, with optional creation.

    Args:
        dir_path (str | Path): Path to the directory.
        create_if_missing (bool): If True, the directory will be created automatically.

    Returns:
        bool: True if validation succeeds.

    Raises:
        FileNotFoundError: If the directory does not exist and creation is disabled.

    Notes:
        - Supports recursive folder creation.
    """
    path = Path(dir_path)

    if not path.exists():
        if create_if_missing:
            path.mkdir(parents=True, exist_ok=True)
            logger.warning("📁 Directory created: %s", path)
        else:
            logger.error("❌ Directory not found: %s", path)
            raise FileNotFoundError(f"Directory not found: {path}")
    else:
        logger.info("✅ Directory exists: %s", path)

    return True


# ====================================================================================================
# 4. DATA VALIDATION (PANDAS)
# ----------------------------------------------------------------------------------------------------
def validate_required_columns(df: pd.DataFrame, required_cols: List[str]) -> bool:
    """
    Description:
        Ensures that all required columns exist in a DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.
        required_cols (List[str]): Columns that must be present.

    Returns:
        bool: True if all required columns exist.

    Raises:
        ValueError: If any required columns are missing.

    Notes:
        - Logs the list of missing columns before failing.
    """
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        logger.error("❌ Missing required columns: %s", missing)
        raise ValueError(f"Missing required columns: {missing}")

    logger.info("✅ All required columns present.")
    return True


def validate_non_empty(data: Any, label: str = "Data") -> bool:
    """
    Description:
        Validates that the provided dataset is not empty or None.

    Args:
        data (Any): Any object supporting __len__(), such as DataFrame, list, dict.
        label (str): Friendly label for logging.

    Returns:
        bool: True if the dataset is non-empty.

    Raises:
        ValueError: If the data is None or empty.

    Notes:
        - Commonly used in ETL pipelines.
    """
    if data is None or (hasattr(data, "__len__") and len(data) == 0):
        logger.error("❌ %s is empty or None.", label)
        raise ValueError(f"{label} cannot be empty.")

    logger.info("✅ %s contains data.", label)
    return True


def validate_numeric(df: pd.DataFrame, column: str) -> bool:
    """
    Description:
        Validates that a DataFrame column contains numeric values.

    Args:
        df (pd.DataFrame): Input DataFrame.
        column (str): Name of the column to validate.

    Returns:
        bool: True if the column is numeric.

    Raises:
        ValueError: If the column is missing or contains non-numeric data.

    Notes:
        - Uses pandas dtype inference for numeric detection.
    """
    if column not in df.columns:
        logger.error("❌ Column '%s' not found in DataFrame.", column)
        raise ValueError(f"Column '{column}' not found in DataFrame.")

    if not pd.api.types.is_numeric_dtype(df[column]):
        logger.error("❌ Column '%s' contains non-numeric data.", column)
        raise ValueError(f"Column '{column}' must contain numeric values.")

    logger.info("✅ Column '%s' is numeric.", column)
    return True


# ====================================================================================================
# 5. CONFIGURATION VALIDATION
# ----------------------------------------------------------------------------------------------------
def validate_config_keys(section: str, keys: List[str]) -> bool:
    """
    Description:
        Validates that all required configuration keys exist in the specified
        configuration section.

    Args:
        section (str): Name of the configuration section.
        keys (List[str]): Required keys within the section.

    Returns:
        bool: True if all keys are present.

    Raises:
        KeyError: If any required keys are missing.

    Notes:
        - Uses get_config() with a sentinel to detect missing keys.
    """
    missing: List[str] = []
    sentinel = object()

    for key in keys:
        value = get_config(section, key, default=sentinel)
        if value is sentinel:
            missing.append(key)

    if missing:
        logger.error("❌ Missing configuration keys in section '%s': %s", section, missing)
        raise KeyError(f"Missing configuration keys in section '{section}': {missing}")

    logger.info("✅ All required config keys found in section '%s'.", section)
    return True


# ====================================================================================================
# 6. AGGREGATED VALIDATION REPORT
# ----------------------------------------------------------------------------------------------------
def validation_report(results: Dict[str, bool]) -> None:
    """
    Description:
        Logs a structured validation report mapping validation names to statuses.

    Args:
        results (Dict[str, bool]): Mapping of validation name → success flag.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Intended for diagnostics in ETL pipelines or batch processes.
    """
    logger.info("🧾 Validation Summary Report:")
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(" - %-30s : %s", name, status)


# ====================================================================================================
# 7. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging()
    logger.info("C06_validation_utils self-test started.")

    # File & directory validation
    try:
        validate_directory_exists("test_dir", create_if_missing=True)
        temp_file = Path("test_dir") / "test.csv"
        temp_file.write_text("col1,col2\n1,2")
        validate_file_exists(temp_file)
    except Exception as error:
        log_exception(error, context="File/Directory validation")

    # DataFrame validation
    try:
        df = pd.DataFrame({"order_id": [1, 2], "amount": [10.5, 20.0]})
        validate_required_columns(df, ["order_id", "amount"])
        validate_non_empty(df, label="Orders DataFrame")
        validate_numeric(df, "amount")
    except Exception as error:
        log_exception(error, context="Data validation")

    # Configuration validation
    try:
        if get_config("snowflake", "user", default=None) is not None:
            validate_config_keys("snowflake", ["user", "account"])
        else:
            logger.info("ℹ️ Skipping config validation: 'snowflake' not present.")
    except Exception as error:
        log_exception(error, context="Config validation")

    logger.info("C06_validation_utils self-test complete.")
