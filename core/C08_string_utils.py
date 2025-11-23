# ====================================================================================================
# C08_string_utils.py
# ----------------------------------------------------------------------------------------------------
# Provides shared string and filename manipulation utilities for CustomPythonCoreFunctions v1.0.
#
# Purpose:
#   - Centralise reusable functions for text cleaning, normalization, and safe filename creation.
#   - Support consistent naming conventions across files, GUIs, and data transformations.
#   - Provide lightweight regex-based extraction helpers for IDs, dates, or custom tokens.
#   - Generate filenames prefixed with standardised date formats (daily, monthly, range).
#
# Usage:
#   from core.C08_string_utils import *
#
#   clean = normalize_text("Monthly Report - 25.09.01.pdf")
#   slug  = slugify_filename(clean)
#   dated = generate_dated_filename("Orders Report", ".csv")
#
#   # Or via class:
#   from core.C08_string_utils import StringUtils
#   clean = StringUtils.normalize_text("Some Text")
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
# (None required)


# ====================================================================================================
# 3. CLASS-BASED STRING & FILENAME UTILITIES
# ----------------------------------------------------------------------------------------------------
class StringUtils:
    """
    Description:
        Namespace-style container for shared string and filename manipulation
        helpers used throughout the core modules.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - All methods are implemented as @staticmethod, making this class a
          pure namespace with no instance state.
        - Methods are designed to be side-effect free apart from logging.
        - Methods rely only on imports provided via core.C00_set_packages or
          local, non-shared standard-library imports where appropriate.
    """

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Description:
            Normalises text by removing accents, converting to lowercase,
            trimming surrounding whitespace, and collapsing internal
            whitespace sequences into single spaces.

        Args:
            text (str): Input text to normalise. Non-string inputs are
                converted using str() before processing.

        Returns:
            str: Lowercase, accent-free, whitespace-collapsed representation
            of the input string.

        Raises:
            None.

        Notes:
            - Accents and diacritics are removed using NFKD Unicode
              normalisation.
            - Consecutive whitespace characters are collapsed to a single
              space.
            - A warning is logged if the input is not initially a str.
        """
        import unicodedata  # Local import; not a common/shared dependency.

        if not isinstance(text, str):
            logger.warning("Expected string, got %s. Converting to string.", type(text))
            text = str(text)

        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8", "ignore")
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        logger.debug("Normalized text: '%s'", text)
        return text

    # ------------------------------------------------------------------------------------------------

    @staticmethod
    def slugify_filename(filename: str, keep_extension: bool = True) -> str:
        """
        Description:
            Converts a filename into a filesystem-safe, slugified string with
            optional preservation of the original extension.

        Args:
            filename (str): Input filename (for example,
                "Monthly Report - 25.09.01.pdf").
            keep_extension (bool): If True, preserves and lowercases the
                original extension. If False, the returned value omits the
                extension. Defaults to True.

        Returns:
            str: Slugified, lowercase filename containing only characters
            [a-z0-9_] plus the original extension (if keep_extension is True).

        Raises:
            None.

        Notes:
            - All non-alphanumeric characters are replaced with underscores.
            - Multiple underscores are collapsed to a single underscore.
            - Leading and trailing underscores are stripped.
        """
        name, ext = os.path.splitext(filename)
        name = StringUtils.normalize_text(name)
        name = re.sub(r"[^a-z0-9]+", "_", name)
        name = re.sub(r"_+", "_", name).strip("_")
        ext = ext.lower()

        result = f"{name}{ext}" if keep_extension else name
        logger.debug("Slugified filename: '%s'", result)
        return result

    # ------------------------------------------------------------------------------------------------

    @staticmethod
    def make_safe_id(text: str, max_length: int = 50) -> str:
        """
        Description:
            Generates a clean, lowercase, alphanumeric identifier from
            arbitrary text, suitable for use as keys, IDs, or compact
            labels.

        Args:
            text (str): Input text to convert into an identifier.
            max_length (int): Maximum length of the returned identifier.
                Defaults to 50.

        Returns:
            str: Lowercase identifier using only letters, digits, and
            underscores, truncated to max_length characters.

        Raises:
            None.

        Notes:
            - All non-alphanumeric characters are converted to underscores.
            - Consecutive underscores are collapsed to a single underscore.
            - Leading and trailing underscores are removed.
        """
        text = StringUtils.normalize_text(text)
        text = re.sub(r"[^a-z0-9]+", "_", text)
        text = re.sub(r"_+", "_", text).strip("_")
        safe_id = text[:max_length]
        logger.debug("Generated safe ID: '%s'", safe_id)
        return safe_id

    # ------------------------------------------------------------------------------------------------

    @staticmethod
    def extract_pattern(text: str, pattern: str, group: int | None = None) -> str | None:
        """
        Description:
            Extracts a substring from text using a regular expression
            pattern, returning either the whole match or a specific
            capturing group.

        Args:
            text (str): Input text to search.
            pattern (str): Regular expression pattern to apply.
            group (int | None): Capturing group index to return. If None,
                the entire match (group 0) is returned. Defaults to None.

        Returns:
            str | None: Extracted substring if a match is found; otherwise
            None.

        Raises:
            None.

        Notes:
            - Logs a warning if no match is found.
            - Designed for safe extraction; no exception is raised when
              no match is present.
        """
        match = re.search(pattern, text)
        if not match:
            logger.warning("Pattern not found: %s", pattern)
            return None

        result = match.group(0 if group is None else group)
        logger.debug("Extracted '%s' -> '%s'", pattern, result)
        return result

    # ------------------------------------------------------------------------------------------------

    @staticmethod
    def parse_number(value: Any) -> float | None:
        """
        Description:
            Safely parses a numeric input into a float, handling common
            formats encountered in financial/banking data:
                - Commas (e.g. "1,234.56")
                - Currency symbols (e.g. "£1,234.56", "GBP 123.45")
                - Parentheses for negative values (e.g. "(123.45)")
                - Leading/trailing whitespace
                - Empty strings or invalid values (→ None)

        Args:
            value (Any):
                Raw input value. May be str, int, float, or None.

        Returns:
            float | None:
                Parsed float value, or None if the input cannot be parsed.

        Raises:
            None:
                All errors are caught internally and logged.

        Notes:
            - Use validate_numeric() (C06) after cleaning if strict type
              enforcement is required.
            - Designed for permissive ETL pipelines where invalid inputs
              should not crash the pipeline.
        """
        try:
            if value is None:
                return None

            # Already numeric?
            if isinstance(value, (int, float)):
                return float(value)

            text = str(value).strip()
            if text == "":
                return None

            # Remove currency symbols and commas
            cleaned = (
                text.replace(",", "")
                    .replace("GBP", "")
                    .replace("£", "")
                    .strip()
            )

            # Handle (123.45) → -123.45
            if cleaned.startswith("(") and cleaned.endswith(")"):
                cleaned = "-" + cleaned[1:-1]

            return float(cleaned)

        except Exception as exc:
            log_exception(exc, context=f"parse_number(value={value})")
            return None

    # ------------------------------------------------------------------------------------------------

    @staticmethod
    def clean_filename_generic(original_name: str) -> str:
        """
        Description:
            Cleans a filename using generic project rules to produce a
            filesystem-safe version.

        Args:
            original_name (str): Raw filename, including extension.

        Returns:
            str: Cleaned, slugified filename suitable for filesystem usage.

        Raises:
            None.

        Notes:
            - Applies text normalisation (lowercasing, accent removal).
            - Removes brackets and dashes prior to slugification.
            - Intended as a high-level "one call" cleaning helper.
        """
        cleaned = StringUtils.normalize_text(original_name)
        cleaned = re.sub(r"[\(\)\[\]\-]+", " ", cleaned)
        result = StringUtils.slugify_filename(cleaned)
        logger.info("🧹 Cleaned generic filename: %s", result)
        return result

    # ------------------------------------------------------------------------------------------------

    @staticmethod
    def generate_dated_filename(
        descriptor: str,
        extension: str = ".csv",
        start_date: date | None = None,
        end_date: date | None = None,
        frequency: str = "daily",
    ) -> str:
        """
        Description:
            Generates a dated filename using shorthand YY.MM or YY.MM.DD
            prefixes, optionally supporting date ranges.

        Args:
            descriptor (str): Human-readable descriptor (for example,
                "Daily Orders", "JE Reconciliation").
            extension (str): File extension, with or without leading dot
                (for example, ".csv" or "csv"). Defaults to ".csv".
            start_date (date | None): Start date for the file context.
                If None, today's date is used.
            end_date (date | None): End date for range filenames. Only
                considered when provided alongside start_date.
            frequency (str): Frequency label, one of "daily", "monthly",
                or "range" (case-insensitive). Defaults to "daily".

        Returns:
            str: Dated filename string such as:
                - "25.11.01 - daily_orders.csv"
                - "25.11 - monthly_summary.csv"
                - "25.11.01 - 25.11.07 - weekly_rec.csv"

        Raises:
            None.

        Notes:
            - If both start_date and end_date are provided, a range-style
              prefix is used.
            - For "monthly" frequency, only YY.MM is used as the prefix.
            - The descriptor portion is converted via make_safe_id().
        """
        today = date.today()
        start = start_date or today

        if not extension.startswith("."):
            extension = f".{extension}"
        extension = extension.lower()

        descriptor_clean = StringUtils.make_safe_id(descriptor)

        if start_date and end_date:
            prefix = f"{start_date:%y.%m.%d} - {end_date:%y.%m.%d}"
        elif frequency.lower() == "monthly":
            prefix = f"{start:%y.%m}"
        else:
            prefix = f"{start:%y.%m.%d}"

        filename = f"{prefix} - {descriptor_clean}{extension}"
        logger.info("🗂️ Generated dated filename: %s", filename)
        return filename


# ====================================================================================================
# 4. FUNCTION FACADE (BACKWARDS COMPATIBLE API)
# ----------------------------------------------------------------------------------------------------
def normalize_text(text: str) -> str:
    """
    Description:
        Facade function that delegates to StringUtils.normalize_text() to
        normalise textual content.

    Args:
        text (str): Input text to normalise.

    Returns:
        str: Normalised text string.

    Raises:
        None.

    Notes:
        - Provided for backwards compatibility with earlier function-based
          APIs that did not use the StringUtils class.
    """
    return StringUtils.normalize_text(text)


def slugify_filename(filename: str, keep_extension: bool = True) -> str:
    """
    Description:
        Facade function that delegates to StringUtils.slugify_filename()
        to create a filesystem-safe filename.

    Args:
        filename (str): Input filename to slugify.
        keep_extension (bool): Whether to preserve the original file
            extension. Defaults to True.

    Returns:
        str: Slugified filename string.

    Raises:
        None.

    Notes:
        - Maintains compatibility with legacy function-based callers.
    """
    return StringUtils.slugify_filename(filename, keep_extension=keep_extension)


def make_safe_id(text: str, max_length: int = 50) -> str:
    """
    Description:
        Facade function that delegates to StringUtils.make_safe_id() to
        produce a safe identifier.

    Args:
        text (str): Input text to convert to an identifier.
        max_length (int): Maximum length of the identifier. Defaults
            to 50.

    Returns:
        str: Generated safe identifier.

    Raises:
        None.

    Notes:
        - Maintains compatibility with legacy function-based callers.
    """
    return StringUtils.make_safe_id(text, max_length=max_length)


def extract_pattern(text: str, pattern: str, group: int | None = None) -> str | None:
    """
    Description:
        Facade function that delegates to StringUtils.extract_pattern()
        for regular expression-based extraction.

    Args:
        text (str): Input text to search.
        pattern (str): Regular expression pattern to apply.
        group (int | None): Capturing group index to return, or None
            for the full match.

    Returns:
        str | None: Extracted substring, or None if no match is found.

    Raises:
        None.

    Notes:
        - Simplifies usage for callers preferring a function-based API.
    """
    return StringUtils.extract_pattern(text, pattern=pattern, group=group)


def clean_filename_generic(original_name: str) -> str:
    """
    Description:
        Facade function that delegates to StringUtils.clean_filename_generic()
        to clean filenames using standard project rules.

    Args:
        original_name (str): Raw filename, typically including extension.

    Returns:
        str: Cleaned, slugified filename.

    Raises:
        None.

    Notes:
        - Provided for compatibility with function-oriented code paths.
    """
    return StringUtils.clean_filename_generic(original_name)


def generate_dated_filename(
    descriptor: str,
    extension: str = ".csv",
    start_date: date | None = None,
    end_date: date | None = None,
    frequency: str = "daily",
) -> str:
    """
    Description:
        Facade function that delegates to StringUtils.generate_dated_filename()
        to construct date-prefixed filenames for reports and exports.

    Args:
        descriptor (str): Descriptor text for the filename.
        extension (str): File extension, with or without a leading dot.
            Defaults to ".csv".
        start_date (date | None): Optional start date for the filename
            context.
        end_date (date | None): Optional end date for range filenames.
        frequency (str): Frequency label such as "daily", "monthly", or
            "range". Defaults to "daily".

    Returns:
        str: Generated dated filename string.

    Raises:
        None.

    Notes:
        - Maintains compatibility with earlier function-based usage patterns.
    """
    return StringUtils.generate_dated_filename(
        descriptor=descriptor,
        extension=extension,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
    )

def parse_number(value: Any) -> float | None:
    """
    Description:
        Facade function delegating to StringUtils.parse_number() for
        safely parsing numeric values from strings or mixed input types.

    Args:
        value (Any): Raw input to parse.

    Returns:
        float | None: Parsed numeric value or None if parsing fails.

    Raises:
        None.

    Notes:
        - Maintains consistency with function-style APIs.
    """
    return StringUtils.parse_number(value)


# ====================================================================================================
# 5. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Description:
        Standalone self-test for C08_string_utils. Executes a small set of
        examples and logs the results for verification.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Uses init_logging() to configure logging.
        - Writes all diagnostics to the log (and console if configured).
        - No print() statements are used in accordance with core testing
          rules.
    """
    init_logging()
    logger.info("C08_string_utils self-test started.")

    sample = "Monthly Report - 25.09.01.pdf"
    logger.info("Original: %s", sample)
    logger.info("Normalized: %s", normalize_text(sample))
    logger.info("Slugified: %s", slugify_filename(sample))
    logger.info("Safe ID: %s", make_safe_id(sample))
    logger.info("Extract numbers: %s", extract_pattern(sample, r"\\d+"))
    logger.info("Generic clean: %s", clean_filename_generic(sample))

    logger.info("Daily filename: %s", generate_dated_filename("Daily Report"))
    logger.info(
        "Monthly filename: %s",
        generate_dated_filename("Monthly Summary", frequency="monthly"),
    )
    logger.info(
        "Range filename: %s",
        generate_dated_filename(
            "Weekly Rec",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 7),
        ),
    )

    logger.info("🔢 Testing parse_number()...")

    tests = {
        "123": parse_number("123"),
        "1,234.56": parse_number("1,234.56"),
        "£1,234.56": parse_number("£1,234.56"),
        "GBP 789.10": parse_number("GBP 789.10"),
        "(123.45)": parse_number("(123.45)"),
        "": parse_number(""),
        None: parse_number(None),
        "abc": parse_number("abc"),
    }

    for raw, cleaned in tests.items():
        logger.info("parse_number(%r) -> %s", raw, cleaned)

    logger.info("✅ C08_string_utils self-test complete.")
