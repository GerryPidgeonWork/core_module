# ====================================================================================================
# C19_api_manager.py
# ----------------------------------------------------------------------------------------------------
# Provides reusable REST API utilities for authenticated and unauthenticated requests.
#
# Purpose:
#   - Standardise GET/POST/PUT/DELETE requests using the requests library.
#   - Handle JSON parsing, retries, timeouts, and structured error logging.
#   - Provide consistent wrappers for REST API integrations across all projects.
#
# Usage:
#   from core.C19_api_manager import (
#       api_request,
#       get_json,
#       post_json,
#       get_auth_header,
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


# ====================================================================================================
# 3. API REQUEST WRAPPER
# ----------------------------------------------------------------------------------------------------
def api_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    retries: int = 3,
    timeout: int = 15,
) -> Optional[requests.Response]:
    """
    Description:
        Execute a REST API request with retry logic, timeout handling, structured logging,
        and safe JSON/form payload support.

    Args:
        method (str):
            HTTP method ('GET', 'POST', 'PUT', 'DELETE').
        url (str):
            Request URL.
        headers (dict | None):
            Optional headers for authentication or metadata.
        params (dict | None):
            Optional query parameters for GET requests.
        data (dict | None):
            Optional form-data dictionary for POST/PUT.
        json_data (dict | None):
            Optional JSON body for POST/PUT.
        retries (int):
            Number of retry attempts on failure.
        timeout (int):
            Maximum number of seconds to wait for a response.

    Returns:
        requests.Response | None:
            Response object on success, otherwise None.

    Raises:
        None.

    Notes:
        - Implements simple backoff (2 seconds between retries).
        - Logs truncated response bodies (first 200 characters).
        - All unexpected exceptions logged via log_exception().
    """
    method = method.upper().strip()

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"🌐 [{method}] Attempt {attempt}/{retries} → {url}")

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=timeout,
            )

            if response.ok:
                logger.info(f"✅ [{response.status_code}] Success → {url}")
                return response

            logger.warning(
                f"⚠️  [{response.status_code}] API request failed "
                f"(attempt {attempt}/{retries}): {response.text[:200]}"
            )

        except requests.Timeout:
            logger.warning(f"⏰ Timeout on attempt {attempt}/{retries} for URL: {url}")

        except requests.ConnectionError as e:
            logger.error(f"🔌 Connection error: {e}")

        except Exception as e:
            log_exception(e, context=f"API request to {url}")

        if attempt < retries:
            time.sleep(2)

    logger.error(f"❌ Failed after {retries} attempts → {url}")
    return None
# ====================================================================================================


# ====================================================================================================
# 4. HELPER FUNCTIONS
# ----------------------------------------------------------------------------------------------------
def get_json(
    url: str,
    headers: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Description:
        Perform a safe GET request and return parsed JSON.

    Args:
        url (str):
            API endpoint.
        headers (dict | None):
            Optional headers.
        params (dict | None):
            Optional GET parameters.

    Returns:
        dict | None:
            Parsed JSON object, or None if request or parsing fails.

    Raises:
        None.

    Notes:
        - Structured logging for JSON decoding failures.
    """
    response = api_request("GET", url, headers=headers, params=params)
    if response is None:
        return None

    try:
        return response.json()
    except Exception as e:
        log_exception(e, context=f"Parsing JSON from GET {url}")
        return None


def post_json(
    url: str,
    json_data: Dict[str, Any],
    headers: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Description:
        Performs a POST request with JSON payload and returns parsed JSON response.

    Args:
        url (str):
            API endpoint.
        json_data (dict):
            JSON payload body.
        headers (dict | None):
            Optional headers.

    Returns:
        dict | None:
            Response JSON or None if request/parsing fails.

    Raises:
        None.

    Notes:
        - Structured error logging on JSON parse failure.
    """
    response = api_request("POST", url, headers=headers, json_data=json_data)
    if response is None:
        return None

    try:
        return response.json()
    except Exception as e:
        log_exception(e, context=f"Parsing JSON from POST {url}")
        return None


def get_auth_header(token: str, bearer: bool = True) -> Dict[str, str]:
    """
    Description:
        Build a standardised Authorization header for REST API calls.

    Args:
        token (str):
            Raw API token or credential.
        bearer (bool):
            If True, prefix with 'Bearer '. If False, use token as-is.

    Returns:
        dict:
            Header dictionary with properly formatted Authorization entry.

    Raises:
        None.

    Notes:
        - Used widely across API integrations in multiple services.
    """
    if bearer:
        return {"Authorization": f"Bearer {token}"}
    return {"Authorization": token}
# ====================================================================================================


# ====================================================================================================
# 5. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Description:
        Basic connectivity + JSON parsing test using GitHub's public API.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Safe to run in any environment.
        - Validates GET + JSON decode pipeline.
    """
    init_logging(enable_console=True)
    logger.info("🔍 Running C19_api_manager self-test...")

    response_json = get_json("https://api.github.com")

    if response_json:
        logger.info(f"🧪 Self-test JSON keys: {list(response_json.keys())[:5]}")
    else:
        logger.error("❌ API self-test failed.")

    logger.info("✅ C19_api_manager self-test complete.")
