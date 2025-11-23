# ====================================================================================================
# C11_data_processing.py
# ----------------------------------------------------------------------------------------------------
# Provides generic data transformation and cleaning utilities for Pandas DataFrames.
#
# Purpose:
#   - Standardise DataFrame cleaning and merging across projects.
#   - Ensure consistent preprocessing steps (column names, nulls, dtypes, etc.).
#   - Provide safe wrappers around common Pandas operations with full logging.
#
# Usage:
#   from core.C11_data_processing import *
#
# Example:
#   df = standardise_columns(df)
#   df = remove_duplicates(df, subset=["order_id"])
#   merged = merge_dataframes(df1, df2, on="id", how="left")
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
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
from core.C06_validation_utils import validate_non_empty, validate_required_columns
# No additional imports required.


# ====================================================================================================
# 3. STANDARDISATION UTILITIES
# ----------------------------------------------------------------------------------------------------
def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Description:
        Standardises DataFrame column names to a normalised format by
        stripping whitespace, converting to lowercase, and replacing spaces
        with underscores.

    Args:
        df (pd.DataFrame): Input DataFrame whose column labels are to be
            normalised.

    Returns:
        pd.DataFrame: DataFrame with standardised column names. A new
        DataFrame is returned; the original reference is not modified in
        place.

    Raises:
        None.

    Notes:
        - This helper promotes consistent naming across merge, audit, and
          export workflows.
        - Original and transformed column lists are logged at INFO level.
    """
    original = df.columns.tolist()
    df = df.rename(columns=lambda c: str(c).strip().lower().replace(" ", "_"))
    logger.info("🧹 Standardised columns: %s → %s", original, df.columns.tolist())
    return df


def convert_to_datetime(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """
    Description:
        Converts selected DataFrame columns to datetime dtype using
        pandas.to_datetime() with errors coerced to NaT. Missing columns
        are skipped with a warning.

    Args:
        df (pd.DataFrame): Input DataFrame containing the columns to
            convert.
        cols (List[str]): Column names to cast to datetime.

    Returns:
        pd.DataFrame: Updated DataFrame with datetime conversion applied
        to the specified columns when present.

    Raises:
        None.

    Notes:
        - Uses pandas.to_datetime(..., errors="coerce"), so invalid values
          become NaT instead of raising.
        - Emits a warning if a requested column is not found in df.columns.
    """
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            logger.info("🕒 Converted column '%s' to datetime", col)
        else:
            logger.warning("⚠️ Column '%s' not found for datetime conversion", col)
    return df


def fill_missing(df: pd.DataFrame, fill_map: Dict[str, Any]) -> pd.DataFrame:
    """
    Description:
        Fills missing values in the DataFrame based on a column-wise
        mapping using DataFrame.fillna().

    Args:
        df (pd.DataFrame): DataFrame to process.
        fill_map (Dict[str, Any]): Mapping of column name → value used to
            fill NaNs in that column.

    Returns:
        pd.DataFrame: DataFrame with missing values replaced according to
        the provided mapping.

    Raises:
        None.

    Notes:
        - Only the columns specified in fill_map are affected.
        - Existing non-null values remain unchanged.
    """
    df = df.fillna(fill_map)
    logger.info("🩹 Filled missing values for columns: %s", list(fill_map.keys()))
    return df


# ====================================================================================================
# 4. CLEANING AND FILTERING
# ----------------------------------------------------------------------------------------------------
def remove_duplicates(df: pd.DataFrame, subset: List[str] | None = None) -> pd.DataFrame:
    """
    Description:
        Removes duplicate rows from a DataFrame, optionally based on a
        subset of columns. The index is reset after deduplication.

    Args:
        df (pd.DataFrame): Target DataFrame from which duplicates should
            be removed.
        subset (List[str] | None): Optional list of column names used to
            identify duplicates. If None, all columns are considered.

    Returns:
        pd.DataFrame: Deduplicated DataFrame with a reset integer index.

    Raises:
        None.

    Notes:
        - Logs the number of rows removed at INFO level.
        - Uses DataFrame.drop_duplicates(subset=subset).
    """
    before = len(df)
    df = df.drop_duplicates(subset=subset).reset_index(drop=True)
    after = len(df)
    logger.info("🧩 Removed %s duplicate rows (subset=%s)", before - after, subset)
    return df


def filter_rows(df: pd.DataFrame, condition: Any) -> pd.DataFrame:
    """
    Description:
        Filters DataFrame rows using a boolean mask or a callable that
        produces a boolean mask. The resulting filtered DataFrame is
        returned without modifying the original.

    Args:
        df (pd.DataFrame): Input DataFrame to be filtered.
        condition (Any): Filter condition, which may be:
            - A callable taking df and returning a mask (Series, ndarray,
              or list of booleans).
            - A mask-like object directly (Series, ndarray, or list).

    Returns:
        pd.DataFrame: Filtered DataFrame containing only rows where the
        mask evaluates to True.

    Raises:
        ValueError: If the condition is neither callable nor a mask-like
            object (Series, ndarray, list).
        Exception: Any other unexpected exception raised during filtering
            is logged and re-raised.

    Notes:
        - Logs the number of rows remaining after filtering at INFO level.
        - Errors are passed to log_exception() with context="filter_rows".
    """
    try:
        mask = condition(df) if callable(condition) else condition

        if isinstance(mask, (pd.Series, np.ndarray, list)):
            filtered = df.loc[mask]
        else:
            raise ValueError("Condition must be callable or a boolean mask-like object.")

        logger.info("🔍 Filtered DataFrame: %s rows remaining", len(filtered))
        return filtered

    except Exception as exc:
        log_exception(exc, context="filter_rows")
        raise


# ====================================================================================================
# 5. DATA MERGING AND SUMMARY
# ----------------------------------------------------------------------------------------------------
def merge_dataframes(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    on: str,
    how: Literal["left", "right", "outer", "inner", "cross"] = "inner",
) -> pd.DataFrame:
    """
    Description:
        Merges two DataFrames using pandas.merge() and logs basic
        information about the resulting row count and join type.

    Args:
        df1 (pd.DataFrame): Left-hand DataFrame in the merge operation.
        df2 (pd.DataFrame): Right-hand DataFrame in the merge operation.
        on (str): Column name used as the join key.
        how (Literal["left", "right", "outer", "inner", "cross"]):
            Type of join to perform. Defaults to "inner".

    Returns:
        pd.DataFrame: The merged DataFrame produced by pandas.merge().

    Raises:
        Exception: Any exception raised by pandas.merge() is logged via
            log_exception() with context="merge_dataframes" and then
            re-raised.

    Notes:
        - Logs the join type and resulting row count at INFO level.
        - The join key column must exist in both input DataFrames.
    """
    try:
        merged = pd.merge(df1, df2, on=on, how=how)
        logger.info("🔗 Merged DataFrames using %s join: %s rows", how.upper(), len(merged))
        return merged
    except Exception as exc:
        log_exception(exc, context="merge_dataframes")
        raise


def summarise_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Description:
        Produces summary statistics for numeric columns in a DataFrame
        using pandas.DataFrame.describe(), returning the result as a
        transposed table (one row per column).

    Args:
        df (pd.DataFrame): Input DataFrame containing numeric columns.

    Returns:
        pd.DataFrame: Summary statistics for numeric columns, with one
        row per column.

    Raises:
        Exception: Any exception raised by DataFrame.describe() is
            propagated to the caller.

    Notes:
        - Non-numeric columns are automatically excluded by using
          include=[np.number].
        - Logs the number of numeric columns summarised at INFO level.
    """
    summary = df.describe(include=[np.number]).T
    logger.info("📊 Generated summary for %s numeric columns", len(summary))
    return summary


# ====================================================================================================
# 6. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Description:
        Executes a fully logged, no-print self-test for the data
        processing utilities. A small in-memory DataFrame is created,
        cleaned, deduplicated, filled, type-cast, and summarised.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Intended for quick smoke-testing of C11_data_processing
          behaviour.
        - Output is logged via the central logging system; no print()
          calls are used.
    """
    init_logging(enable_console=True)
    logger.info("🔍 Running C11_data_processing self-test...")

    df = pd.DataFrame(
        {
            "Order ID": [1, 2, 2, 3],
            "Amount": [10.0, 20.0, 20.0, None],
            "Date": ["2025-11-01", "2025-11-02", "2025-11-02", "2025-11-03"],
        }
    )

    df = standardise_columns(df)
    df = remove_duplicates(df, subset=["order_id"])
    df = fill_missing(df, {"amount": 0})
    df = convert_to_datetime(df, ["date"])
    summary = summarise_numeric(df)

    logger.info("📊 Summary output:\n%s", summary)
    logger.info("✅ C11_data_processing self-test complete.")
