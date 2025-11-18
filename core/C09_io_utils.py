# ====================================================================================================
# C09_io_utils.py
# ----------------------------------------------------------------------------------------------------
# Provides reusable file input/output utilities for CustomPythonCoreFunctions v1.0.
#
# Purpose:
#   - Read and write CSV, JSON, and Excel files with consistent logging and validation.
#   - Ensure directories exist before writing.
#   - Provide timestamped backups when overwriting existing files.
#   - Integrate with core logging, validation, and datetime utilities.
#
# Usage:
#   from core.C09_io_utils import (
#       read_csv_file,
#       save_dataframe,
#       read_json,
#       save_json,
#       save_excel,
#       get_latest_file,
#       append_to_file,
#   )
#
#   df = read_csv_file("data/input/orders.csv")
#   save_dataframe(df, "outputs/orders_cleaned.csv")
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
from core.C06_validation_utils import validate_directory_exists, validate_file_exists
from core.C07_datetime_utils import timestamp_now


# ====================================================================================================
# 3. CSV UTILITIES
# ----------------------------------------------------------------------------------------------------
def read_csv_file(file_path: str | Path, **kwargs) -> pd.DataFrame:
    """
    Description:
        Reads a CSV file into a pandas DataFrame with validation and logging.
        The target file is validated for existence before reading, and the
        resulting row and column counts are logged on success.

    Args:
        file_path (str | Path): Path to the CSV file to read.
        **kwargs: Additional keyword arguments passed directly to
            pandas.read_csv().

    Returns:
        pd.DataFrame: DataFrame containing the loaded CSV data.

    Raises:
        FileNotFoundError: If the file does not exist or is not accessible.
        Exception: Any other error raised by pandas.read_csv() or file I/O
            operations.

    Notes:
        - Uses validate_file_exists() to ensure the file exists prior to
          attempting to read.
        - All exceptions are logged via log_exception() before being
          re-raised.
    """
    path = Path(file_path)

    try:
        validate_file_exists(path)
        df = pd.read_csv(path, **kwargs)
        logger.info("📄 Loaded CSV: %s (%s rows, %s columns)", path, len(df), len(df.columns))
        return df
    except Exception as exc:
        log_exception(exc, context=f"Reading CSV file: {path}")
        raise


def save_dataframe(
    df: pd.DataFrame,
    file_path: str | Path,
    overwrite: bool = True,
    backup_existing: bool = True,
    index: bool = False,
    **kwargs,
) -> Path:
    """
    Description:
        Saves a pandas DataFrame to a CSV file with optional backup
        protection and overwrite control. The destination directory is
        created if necessary, and existing files can be backed up or
        versioned using a timestamp.

    Args:
        df (pd.DataFrame): DataFrame to save.
        file_path (str | Path): Path to the target CSV file.
        overwrite (bool, optional): If False and the file exists, a new
            timestamped filename is generated instead of overwriting.
            Defaults to True.
        backup_existing (bool, optional): If True and the file exists,
            creates a backup file with a "_backup_<timestamp>" suffix
            before overwriting. Defaults to True.
        index (bool, optional): Whether to include the DataFrame index in
            the CSV output. Defaults to False.
        **kwargs: Additional keyword arguments passed to DataFrame.to_csv().

    Returns:
        Path: The final path where the CSV file was saved.

    Raises:
        Exception: Any exception raised during directory creation, backup,
            or CSV write operations.

    Notes:
        - Backup files follow the naming pattern:
          "<stem>_backup_<timestamp><suffix>".
        - When overwrite is False, the final filename is suffixed with
          "_<timestamp>" prior to the extension.
    """
    path = Path(file_path)
    validate_directory_exists(path.parent, create_if_missing=True)

    # Backup existing file first, if requested
    if path.exists() and backup_existing:
        backup_path = path.with_name(f"{path.stem}_backup_{timestamp_now()}{path.suffix}")
        try:
            shutil.copy2(path, backup_path)
            logger.warning("🗂️  Backup created: %s", backup_path)
        except Exception as exc:
            log_exception(exc, context=f"Backing up {path}")

    # Respect overwrite policy by generating a new timestamped name
    if not overwrite and path.exists():
        path = path.with_name(f"{path.stem}_{timestamp_now()}{path.suffix}")

    try:
        df.to_csv(path, index=index, **kwargs)
        logger.info("💾 DataFrame saved to: %s (%s rows)", path, len(df))
        return path
    except Exception as exc:
        log_exception(exc, context=f"Saving DataFrame to {path}")
        raise


# ====================================================================================================
# 4. JSON UTILITIES
# ----------------------------------------------------------------------------------------------------
def read_json(file_path: str | Path, encoding: str = "utf-8") -> Dict[str, Any]:
    """
    Description:
        Reads and parses a JSON file from disk into a Python dictionary.
        The file is validated for existence before being opened and parsed
        via json.load().

    Args:
        file_path (str | Path): Path to the JSON file.
        encoding (str, optional): Text encoding used when opening the file.
            Defaults to "utf-8".

    Returns:
        Dict[str, Any]: Parsed JSON data as a dictionary.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        json.JSONDecodeError: If the file content is not valid JSON.
        Exception: Any other I/O-related error.

    Notes:
        - Uses validate_file_exists() to ensure the file exists.
        - All exceptions are logged with log_exception() before being
          re-raised.
    """
    path = Path(file_path)

    try:
        validate_file_exists(path)
        with open(path, "r", encoding=encoding) as fh:
            data = json.load(fh)
        logger.info("📖 Loaded JSON: %s", path)
        return data
    except Exception as exc:
        log_exception(exc, context=f"Reading JSON: {path}")
        raise


def save_json(
    data: Dict[str, Any] | List[Any],
    file_path: str | Path,
    indent: int = 4,
    overwrite: bool = True,
    encoding: str = "utf-8",
) -> Path:
    """
    Description:
        Serialises JSON-compatible data to disk with optional overwrite
        protection. The output directory is created if necessary, and
        existing files can be versioned using a timestamp.

    Args:
        data (Dict[str, Any] | List[Any]): JSON-serialisable dictionary
            or list.
        file_path (str | Path): Target JSON file path.
        indent (int, optional): Number of spaces used for indentation in
            the output file. Defaults to 4.
        overwrite (bool, optional): If False and the target file exists,
            a timestamp is appended to the filename to avoid overwriting.
            Defaults to True.
        encoding (str, optional): Output file encoding. Defaults to
            "utf-8".

    Returns:
        Path: Final file path where the JSON content was written.

    Raises:
        Exception: Any exception raised by directory creation, file I/O,
            or json.dump().

    Notes:
        - Uses ensure_ascii=False to preserve Unicode characters in the
          output file.
    """
    path = Path(file_path)
    validate_directory_exists(path.parent, create_if_missing=True)

    if not overwrite and path.exists():
        path = path.with_name(f"{path.stem}_{timestamp_now()}{path.suffix}")

    try:
        with open(path, "w", encoding=encoding) as fh:
            json.dump(data, fh, indent=indent, ensure_ascii=False)
        logger.info("💾 JSON saved: %s", path)
        return path
    except Exception as exc:
        log_exception(exc, context=f"Saving JSON to {path}")
        raise


# ====================================================================================================
# 5. EXCEL UTILITIES
# ----------------------------------------------------------------------------------------------------
def save_excel(
    df: pd.DataFrame,
    file_path: str | Path,
    sheet_name: str = "Sheet1",
    index: bool = False,
    **kwargs,
) -> Path:
    """
    Description:
        Saves a pandas DataFrame to an Excel file, ensuring that the
        destination directory exists. The DataFrame is written using
        DataFrame.to_excel().

    Args:
        df (pd.DataFrame): DataFrame to save.
        file_path (str | Path): Destination Excel file path.
        sheet_name (str, optional): Worksheet name to use. Defaults
            to "Sheet1".
        index (bool, optional): Whether to include the DataFrame index
            in the sheet. Defaults to False.
        **kwargs: Additional keyword arguments forwarded to
            DataFrame.to_excel().

    Returns:
        Path: Path to the saved Excel file.

    Raises:
        Exception: Any exception encountered during file creation or
            write operations.

    Notes:
        - Requires an appropriate Excel engine (such as openpyxl) made
          available via the shared package hub.
    """
    path = Path(file_path)
    validate_directory_exists(path.parent, create_if_missing=True)

    try:
        df.to_excel(path, index=index, sheet_name=sheet_name, **kwargs)
        logger.info("📘 Excel saved: %s", path)
        return path
    except Exception as exc:
        log_exception(exc, context=f"Saving Excel to {path}")
        raise


# ====================================================================================================
# 6. FILE SEARCH & TEXT APPEND UTILITIES
# ----------------------------------------------------------------------------------------------------
def get_latest_file(directory: str | Path, pattern: str = "*") -> Path | None:
    """
    Description:
        Finds the most recently modified file in a directory that matches
        a given glob pattern.

    Args:
        directory (str | Path): Directory to search.
        pattern (str, optional): Glob pattern (for example, "*.csv").
            Defaults to "*".

    Returns:
        Path | None: Path to the newest matching file, or None if no
        files match or an error occurs.

    Raises:
        None.

    Notes:
        - Logs a warning if the directory is invalid or no files match.
        - Any unexpected exceptions are logged via log_exception() and
          result in a None return value.
    """
    path = Path(directory)

    try:
        if not path.exists() or not path.is_dir():
            logger.warning("⚠️  Invalid directory: %s", path)
            return None

        files = list(path.glob(pattern))
        if not files:
            logger.warning("⚠️  No files matching '%s' in %s", pattern, path)
            return None

        latest = max(files, key=lambda f: f.stat().st_mtime)
        logger.info("🕒 Latest file: %s", latest)
        return latest
    except Exception as exc:
        log_exception(exc, context=f"Searching latest file in {path}")
        return None


def append_to_file(file_path: str | Path, text: str, newline: bool = True) -> Path:
    """
    Description:
        Appends text to a file, creating it if necessary. The target
        directory is created on demand, and the append operation is
        logged.

    Args:
        file_path (str | Path): Path of the file to append to.
        text (str): Text to write to the file.
        newline (bool, optional): Whether to append a newline character
            after the text. Defaults to True.

    Returns:
        Path: Path to the file that was written to.

    Raises:
        Exception: Any I/O error encountered while writing to the file.

    Notes:
        - The file is opened in append mode using UTF-8 encoding.
        - This helper is suitable for simple logging or audit trails
          outside the central logging system.
    """
    path = Path(file_path)
    validate_directory_exists(path.parent, create_if_missing=True)

    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(text + ("\n" if newline else ""))
        logger.info("✏️  Appended text to: %s", path)
        return path
    except Exception as exc:
        log_exception(exc, context=f"Appending to file: {path}")
        raise


# ====================================================================================================
# 7. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Sandboxed I/O self-test using a temporary directory.
    #
    # Description:
    #   Runs a set of sample operations (CSV, JSON, Excel, append, latest-file)
    #   within a TemporaryDirectory to verify behaviour without touching
    #   project data.
    #
    # Notes:
    #   - All feedback is written via the logging system.
    #   - No print() statements are used in accordance with core testing rules.
    init_logging(enable_console=True)
    logger.info("🔍 C09_io_utils self-test started.")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        logger.info("🧪 Temporary directory: %s", tmp)

        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})

        # CSV round-trip
        csv_path = save_dataframe(df, tmp / "sample.csv")
        _ = read_csv_file(csv_path)

        # JSON round-trip
        json_path = save_json({"example": True, "rows": len(df)}, tmp / "sample.json")
        _ = read_json(json_path)

        # Excel write
        _ = save_excel(df, tmp / "sample.xlsx")

        # Text append + latest file lookup
        log_path = append_to_file(tmp / "log.txt", "First entry")
        append_to_file(log_path, "Second entry")
        _ = get_latest_file(tmp, "*.csv")

    logger.info("✅ C09_io_utils self-test complete.")
