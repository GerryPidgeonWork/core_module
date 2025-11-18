# ====================================================================================================
# C12_data_audit.py
# ----------------------------------------------------------------------------------------------------
# Description:
# Provides reusable DataFrame comparison and reconciliation tools.
#
# Purpose:
#   - Identify mismatches, missing rows, and column-level discrepancies between datasets.
#   - Support structured auditing for reconciliation and validation workflows.
#   - Ensure all audits are logged using the central logging framework.
#
# Usage:
#   from core.C12_data_audit import (
#       get_missing_rows,
#       compare_dataframes,
#       reconcile_column_sums,
#       summarise_differences,
#       log_audit_summary,
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

# --- Additional project-level imports (append below this line only) ---------------------------------
from core.C06_validation_utils import validate_required_columns, validate_non_empty


# ====================================================================================================
# 3. ROW & COLUMN COMPARISON UTILITIES
# ----------------------------------------------------------------------------------------------------
def get_missing_rows(df_a: pd.DataFrame, df_b: pd.DataFrame, on: str) -> pd.DataFrame:
    """
    Description:
        Identify rows that exist in df_a but are missing in df_b based on a
        shared key column.

    Args:
        df_a (pd.DataFrame): Source DataFrame used as the baseline set of
            rows to check.
        df_b (pd.DataFrame): Reference DataFrame expected to contain all
            key values present in df_a.
        on (str): Column name used as the join key in both DataFrames.

    Returns:
        pd.DataFrame: Subset of df_a containing only those rows whose key
        values are not present in df_b[on].

    Raises:
        Exception: Any unexpected error raised during validation or
            comparison. The error is logged via log_exception() and then
            re-raised.

    Notes:
        - Both df_a and df_b must contain the key column and be non-empty;
          these conditions are enforced using validate_required_columns()
          and validate_non_empty().
        - A summary of missing row count is logged at INFO level.
    """
    try:
        validate_required_columns(df_a, [on])
        validate_required_columns(df_b, [on])
        validate_non_empty(df_a, label="df_a")
        validate_non_empty(df_b, label="df_b")

        missing = df_a[~df_a[on].isin(df_b[on])]
        logger.info("🚫 Missing rows in df_b (key=%s): %s", on, len(missing))
        return missing

    except Exception as exc:
        log_exception(exc, context="get_missing_rows")
        raise


def compare_dataframes(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    on: str,
    cols: List[str],
) -> pd.DataFrame:
    """
    Description:
        Compare selected columns between two DataFrames and return the rows
        where values differ. The comparison is performed after an inner
        join on a shared key column.

    Args:
        df_a (pd.DataFrame): First DataFrame (for example, a source system).
        df_b (pd.DataFrame): Second DataFrame (for example, a reference system).
        on (str): Join key column used to align rows between df_a and df_b.
        cols (List[str]): List of column names to compare across the two
            DataFrames.

    Returns:
        pd.DataFrame: DataFrame containing rows with mismatched values.
        Columns include:
            - The key column specified by on.
            - "<col>_a" for each compared column (values from df_a).
            - "<col>_b" for each compared column (values from df_b).
        If no mismatches are found, an empty DataFrame with the expected
        columns is returned.

    Raises:
        Exception: Any unexpected error encountered during validation,
            merge, or comparison is logged via log_exception() with
            context="compare_dataframes" and then re-raised.

    Notes:
        - Performs an inner join using pandas.merge(..., how="inner",
          suffixes=("_a", "_b")).
        - Columns that do not survive the merge (missing col_a or col_b)
          are skipped with a warning.
        - Strict inequality (!=) is used; NaN values are treated as
          mismatches because NaN != NaN.
    """
    try:
        validate_required_columns(df_a, [on] + cols)
        validate_required_columns(df_b, [on] + cols)
        validate_non_empty(df_a, label="df_a")
        validate_non_empty(df_b, label="df_b")

        merged = pd.merge(df_a, df_b, on=on, how="inner", suffixes=("_a", "_b"))
        diffs: List[pd.DataFrame] = []

        for col in cols:
            col_a = f"{col}_a"
            col_b = f"{col}_b"

            if col_a not in merged.columns or col_b not in merged.columns:
                logger.warning("⚠️ Skipping '%s' – merged columns not found.", col)
                continue

            mismatched = merged[merged[col_a] != merged[col_b]]

            if len(mismatched) > 0:
                logger.warning("⚠️ %s mismatches found in '%s'.", len(mismatched), col)
                diffs.append(mismatched[[on, col_a, col_b]])

        if diffs:
            result = pd.concat(diffs, axis=0).reset_index(drop=True)
            logger.info("🧾 Total mismatched rows: %s", len(result))
            return result

        logger.info("✅ No mismatches found for columns: %s", cols)
        return pd.DataFrame(
            columns=[on] + [f"{c}_a" for c in cols] + [f"{c}_b" for c in cols]
        )

    except Exception as exc:
        log_exception(exc, context="compare_dataframes")
        raise


def reconcile_column_sums(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    column: str,
    label_a: str = "A",
    label_b: str = "B",
) -> pd.DataFrame:
    """
    Description:
        Compare total sums for a numeric column across two DataFrames and
        return a small summary table showing the sums and the variance.

    Args:
        df_a (pd.DataFrame): First DataFrame, typically the primary or
            source dataset.
        df_b (pd.DataFrame): Second DataFrame, typically the reference or
            target dataset.
        column (str): Name of the numeric column whose totals should be
            compared.
        label_a (str): Label used to identify df_a in the summary output.
        label_b (str): Label used to identify df_b in the summary output.

    Returns:
        pd.DataFrame: Summary with three rows:
            - Row 1: df_a total.
            - Row 2: df_b total.
            - Row 3: Variance (Δ) and percentage difference, where
              "% Difference" is populated only on the variance row.

    Raises:
        Exception: Any unexpected exception during validation, summation,
            or DataFrame creation is logged and re-raised.

    Notes:
        - If the reference sum (sum_b) is zero, the percentage difference
          is reported as NaN to avoid division by zero.
        - A detailed summary line is logged at INFO level, including both
          sums, the variance, and the percentage difference.
    """
    try:
        validate_required_columns(df_a, [column])
        validate_required_columns(df_b, [column])
        validate_non_empty(df_a, label="df_a")
        validate_non_empty(df_b, label="df_b")

        sum_a = df_a[column].sum()
        sum_b = df_b[column].sum()

        variance = sum_a - sum_b
        pct_diff = (variance / sum_b * 100) if sum_b != 0 else np.nan

        summary = pd.DataFrame(
            {
                "DataFrame": [label_a, label_b, "Δ Variance"],
                "Sum": [sum_a, sum_b, variance],
                "% Difference": [np.nan, np.nan, pct_diff],
            }
        )

        logger.info(
            "💰 Column '%s': %s=%.2f, %s=%.2f, Δ=%.2f (%.2f%%)",
            column,
            label_a,
            sum_a,
            label_b,
            sum_b,
            variance,
            pct_diff if not np.isnan(pct_diff) else float("nan"),
        )
        return summary

    except Exception as exc:
        log_exception(exc, context="reconcile_column_sums")
        raise


# ====================================================================================================
# 4. AUDIT SUMMARY UTILITIES
# ----------------------------------------------------------------------------------------------------
def summarise_differences(df_diffs: pd.DataFrame, key_col: str) -> Dict[str, int]:
    """
    Description:
        Summarise the number of mismatched rows and unique keys in a
        differences DataFrame for audit reporting.

    Args:
        df_diffs (pd.DataFrame): DataFrame containing mismatched rows, as
            returned by compare_dataframes().
        key_col (str): Name of the key column used to group mismatches.

    Returns:
        Dict[str, int]: A dictionary with at least:
            - "mismatches": Total number of mismatched rows.
            - "unique_keys": Number of distinct key values with mismatches
              (only present when mismatches > 0).

    Raises:
        KeyError: If key_col is not present in df_diffs and the DataFrame
            is non-empty.
        Exception: Any other unexpected exception is propagated.

    Notes:
        - When df_diffs is empty, the function returns
          {"mismatches": 0} and logs the summary.
        - A structured summary is logged at INFO level.
    """
    if df_diffs.empty:
        summary = {"mismatches": 0}
        logger.info("🧮 Summary: %s", summary)
        return summary

    summary = {
        "mismatches": len(df_diffs),
        "unique_keys": df_diffs[key_col].nunique(),
    }
    logger.info("🧮 Summary: %s", summary)
    return summary


def log_audit_summary(
    source_name: str,
    target_name: str,
    missing_count: int,
    mismatch_count: int,
) -> None:
    """
    Description:
        Log a structured, human-readable audit summary comparing two data
        sources, including missing row counts and value-mismatch counts.

    Args:
        source_name (str): Name or label of the source dataset (for example,
            "A" or "Source System").
        target_name (str): Name or label of the target dataset (for example,
            "B" or "GL Extract").
        missing_count (int): Number of rows missing in the target compared
            to the source.
        mismatch_count (int): Number of rows with mismatched values between
            the two datasets.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Writes a multi-line block at INFO level with separators and
          emoji markers suitable for log scanning.
        - This function does not perform any calculations; it only logs
          the supplied metrics.
    """
    logger.info("------------------------------------------------------------")
    logger.info("🔍 Audit Summary: %s → %s", source_name, target_name)
    logger.info("   Missing in %s: %s", target_name, missing_count)
    logger.info("   Value mismatches: %s", mismatch_count)
    logger.info("------------------------------------------------------------")


# ====================================================================================================
# 5. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Description:
        Standalone self-test for C12_data_audit. Constructs small in-memory
        DataFrames, runs the audit utilities (missing rows, value
        mismatches, and sum reconciliation), and logs a compact summary.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Intended as a smoke test for development and CI environments.
        - Uses init_logging() so that all output is routed via the central
          logging system, with no print() calls.
    """
    init_logging()
    logger.info("🔍 Running C12_data_audit self-test...")

    df_a = pd.DataFrame({"order_id": [1, 2, 3, 4], "amount": [100, 200, 300, 400]})
    df_b = pd.DataFrame({"order_id": [2, 3, 4, 5], "amount": [200, 350, 400, 500]})

    missing = get_missing_rows(df_a, df_b, on="order_id")
    diffs = compare_dataframes(df_a, df_b, on="order_id", cols=["amount"])
    summary = reconcile_column_sums(df_a, df_b, "amount", label_a="A", label_b="B")

    log_audit_summary("A", "B", len(missing), len(diffs))
    logger.info("🧾 Summary table:\n%s", summary)
    logger.info("✅ C12_data_audit self-test complete.")
