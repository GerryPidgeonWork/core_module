# ====================================================================================================
# C05_error_handler.py
# ----------------------------------------------------------------------------------------------------
# Centralised error handling for all CustomPythonCoreFunctions v1.0 projects.
#
# Purpose:
#   - Provide a unified error-handling interface for CLI and service-style applications.
#   - Capture and log all uncaught exceptions via sys.excepthook.
#   - Support manual error capture with contextual logging.
#   - Honour configuration flags for fatal-exit behaviour.
#
# Usage:
#   from core.C05_error_handler import (
#       install_global_exception_hook,
#       handle_error,
#   )
#
#   install_global_exception_hook()
#
#   try:
#       risky_operation()
#   except Exception as e:
#       handle_error(e, context="During import process")
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
from core.C04_config_loader import get_config


# ====================================================================================================
# 3. GLOBAL ERROR HANDLING FUNCTIONS
# ----------------------------------------------------------------------------------------------------
def handle_error(exception: Exception, context: str = "", fatal: bool = False) -> None:
    """
    Description:
        Handles an exception by logging it and optionally triggering a fatal exit
        depending on configuration settings.

    Args:
        exception (Exception): The exception object to be handled.
        context (str, optional): Additional information describing where the error
            occurred. Defaults to an empty string.
        fatal (bool, optional): Whether the error should be treated as fatal. If True,
            behaviour depends on CONFIG["error_handling"]["exit_on_fatal"]. Defaults to False.

    Returns:
        None.

    Raises:
        SystemExit: If fatal=True and configuration enables fatal exiting.

    Notes:
        - All exceptions are logged with full traceback via log_exception().
        - Safe for use in CLI tools, services, and background workers.
    """
    log_exception(exception, context=context)

    exit_on_fatal = get_config("error_handling", "exit_on_fatal", default=False)
    if fatal and exit_on_fatal:
        logger.error("💀 Fatal error encountered. Exiting application.")
        sys.exit(1)


def global_exception_hook(exc_type, exc_value, exc_traceback) -> None:
    """
    Description:
        Global fallback handler for uncaught exceptions. Installed via
        install_global_exception_hook().

    Args:
        exc_type (type): The exception class.
        exc_value (Exception): The exception instance.
        exc_traceback (TracebackType): The associated traceback.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - KeyboardInterrupt is passed through cleanly to avoid noisy logs.
        - All other exceptions are logged and routed to handle_error() with fatal=True.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        logger.info("🛑 Application interrupted by user (Ctrl+C).")
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("❌ Unhandled Exception", exc_info=(exc_type, exc_value, exc_traceback))
    handle_error(exc_value, context="Unhandled Exception", fatal=True)


def install_global_exception_hook() -> None:
    """
    Description:
        Installs the custom global exception hook to ensure all uncaught exceptions
        are processed by this module’s logic.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Replaces sys.excepthook.
        - Future uncaught exceptions will be logged and handled consistently.
    """
    sys.excepthook = global_exception_hook
    logger.info("🛡️ Global exception hook installed.")


# ====================================================================================================
# 4. MANUAL TEST FUNCTION
# ----------------------------------------------------------------------------------------------------
def simulate_error() -> None:
    """
    Description:
        Raises a controlled ValueError for manual testing of error handlers.

    Args:
        None.

    Returns:
        None.

    Raises:
        ValueError: Always raised to simulate an error condition.

    Notes:
        - Used only for standalone testing.
    """
    raise ValueError("This is a simulated test exception.")


# ====================================================================================================
# 5. MAIN EXECUTION (STANDALONE TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging()
    logger.info("C05_error_handler self-test started.")
    logger.info("Testing C05_error_handler logic...")
    install_global_exception_hook()

    try:
        simulate_error()
    except Exception as error:
        handle_error(error, context="During standalone test")

    logger.info("Testing fatal error behaviour (if enabled in config)...")

    try:
        handle_error(
            Exception("This is a simulated fatal error."),
            context="Fatal test",
            fatal=True,
        )
    except SystemExit:
        logger.info("💥 Fatal exit triggered successfully (SystemExit caught for test).")

    logger.info("C05_error_handler self-test complete.")
