# ====================================================================================================
# C14_snowflake_connector.py
# ----------------------------------------------------------------------------------------------------
# Provides a unified Snowflake connection interface for core projects.
#
# Purpose:
#   - Establish secure Okta SSO connections to Snowflake.
#   - Auto-select an appropriate Role/Warehouse context.
#   - Support both interactive (CLI/GUI) and automated (config-based) connections.
#
# Features:
#   • Supports Okta-based SSO authentication for Snowflake.
#   • Validates user email address against an allowed domain.
#   • Auto-applies the best matching context from a priority list.
#   • Logs all steps and exceptions centrally via C03_logging_handler.
#   • Includes run_query() helper for convenient SQL execution.
#
# Usage:
#   from core.C14_snowflake_connector import (
#       get_snowflake_credentials,
#       connect_to_snowflake,
#       run_query,
#   )
#
#   init_logging()  # from C03, recommended before connecting
#   conn = connect_to_snowflake("user@example.com")
#   if conn:
#       rows = run_query(conn, "SELECT CURRENT_DATE();")
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
#
# NOTE (EXCEPTION TO PRINT RULE):
#   This module is explicitly allowed to use print() for interactive Snowflake / Okta SSO flows.
#   All other feedback should still use the logging framework.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
from core.C04_config_loader import get_config


# ====================================================================================================
# 3. DEFAULT SNOWFLAKE CONFIGURATION
# ----------------------------------------------------------------------------------------------------
SNOWFLAKE_ACCOUNT: str = "HC77929-GOPUFF"
SNOWFLAKE_EMAIL_DOMAIN: str = "gopuff.com"

CONTEXT_PRIORITY: List[Dict[str, str]] = [
    {"role": "OKTA_ANALYTICS_ROLE", "warehouse": "ANALYTICS"},
    {"role": "OKTA_READER_ROLE", "warehouse": "READER_WH"},
]

DEFAULT_DATABASE: str = "DBT_PROD"
DEFAULT_SCHEMA: str = "CORE"
AUTHENTICATOR: str = "externalbrowser"
TIMEOUT_SECONDS: int = 20


# ====================================================================================================
# 4. SNOWFLAKE CREDENTIAL BUILDER
# ----------------------------------------------------------------------------------------------------
def get_snowflake_credentials(email_address: str) -> Dict[str, Any] | None:
    """
    Description:
        Validate a user email address and build a Snowflake Okta SSO credential
        dictionary suitable for snowflake.connector.connect().

    Args:
        email_address (str):
            User's email address to be used for Snowflake authentication.

    Returns:
        Dict[str, Any] | None:
            A credential mapping containing keys such as 'user', 'account', and
            'authenticator' if the email is valid; otherwise None.

    Raises:
        None.

    Notes:
        - The email must contain an '@' symbol and match the allowed domain
          defined in SNOWFLAKE_EMAIL_DOMAIN.
        - On success, the SNOWFLAKE_USER environment variable is set and all
          validation steps are logged.
    """
    if not email_address or "@" not in email_address:
        logger.error("❌ Invalid email provided: %s", email_address)
        return None

    required_suffix = f"@{SNOWFLAKE_EMAIL_DOMAIN}"
    if not email_address.endswith(required_suffix):
        logger.error(
            "❌ Email '%s' does not match required domain '%s'.",
            email_address,
            SNOWFLAKE_EMAIL_DOMAIN,
        )
        return None

    os.environ["SNOWFLAKE_USER"] = email_address
    logger.info("📧 Using Snowflake email: %s", email_address)

    return {
        "user": email_address,
        "account": SNOWFLAKE_ACCOUNT,
        "authenticator": AUTHENTICATOR,
    }


# ====================================================================================================
# 5. SNOWFLAKE CONTEXT SETTER
# ----------------------------------------------------------------------------------------------------
def set_snowflake_context(
    conn: Any,
    role: str,
    warehouse: str,
    database: str = DEFAULT_DATABASE,
    schema: str = DEFAULT_SCHEMA,
) -> bool:
    """
    Description:
        Apply role, warehouse, database, and schema context to an active
        Snowflake connection.

    Args:
        conn (Any):
            Active Snowflake connection object.
        role (str):
            Target Snowflake role (for example, 'OKTA_ANALYTICS_ROLE').
        warehouse (str):
            Target warehouse name.
        database (str):
            Database name to select. Defaults to DEFAULT_DATABASE.
        schema (str):
            Schema name to select. Defaults to DEFAULT_SCHEMA.

    Returns:
        bool:
            True if all context settings are applied successfully; otherwise
            False.

    Raises:
        None.

    Notes:
        - Any failure is logged via log_exception and results in False.
        - A short summary of the final active context is logged on success.
    """
    cur = conn.cursor()
    try:
        cur.execute(f"USE ROLE {role}")
        cur.execute(f"USE WAREHOUSE {warehouse}")
        cur.execute(f"USE DATABASE {database}")
        cur.execute(f"USE SCHEMA {schema}")

        cur.execute(
            """
            SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE(),
                   CURRENT_DATABASE(), CURRENT_SCHEMA()
            """
        )
        role_now, wh_now, db_now, sc_now = cur.fetchone()

        logger.info(
            "📂 Active Context → Role=%s, Warehouse=%s, DB=%s, Schema=%s",
            role_now,
            wh_now,
            db_now,
            sc_now,
        )
        cur.close()
        return True

    except Exception as exc:
        log_exception(exc, context=f"set_snowflake_context({role}/{warehouse})")
        cur.close()
        return False


# ====================================================================================================
# 6. SNOWFLAKE CONNECTION HANDLER
# ----------------------------------------------------------------------------------------------------
def connect_to_snowflake(email_address: str) -> Any | None:
    """
    Description:
        Establish an Okta-based Snowflake SSO connection with automatic context
        selection based on a priority list of role/warehouse combinations.

    Args:
        email_address (str):
            Email address used for Snowflake authentication.

    Returns:
        Any | None:
            An active Snowflake connection object if login and context
            selection succeed; otherwise None.

    Raises:
        None.

    Notes:
        - This function uses |print()| for interactive Okta prompts as a
          deliberate exception to the usual "no print in core modules" rule.
        - All non-interactive feedback, including failures, is written to the
          central logging system.
        - If the login fails due to a user mismatch, SNOWFLAKE_USER is cleared
          from the environment as a safety measure.
    """
    creds = get_snowflake_credentials(email_address)
    if not creds:
        return None

    logger.info("🔄 Initiating Snowflake SSO session via Okta...")
    print("Please complete the Okta authentication in the browser window.\n")

    conn_container: Dict[str, Any] = {}

    def connector() -> None:
        """
        Description:
            Worker function that performs the actual Snowflake connection in a
            background thread so that a timeout can be enforced.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Redirects stdout/stderr into in-memory buffers to avoid noisy
              console output from the Snowflake driver.
            - Stores either 'conn' or 'error' in conn_container.
        """
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                io.StringIO()
            ):
                conn_obj = snowflake.connector.connect(**creds)
                conn_container["conn"] = conn_obj
        except Exception as exc:
            conn_container["error"] = exc

    thread = threading.Thread(target=connector, daemon=True)
    thread.start()
    thread.join(timeout=TIMEOUT_SECONDS)

    # --- Timeout handling ---------------------------------------------------------------------------
    if thread.is_alive():
        logger.error(
            "⏰ Timeout after %s seconds waiting for Okta login.",
            TIMEOUT_SECONDS,
        )
        return None

    if "error" in conn_container:
        err = str(conn_container["error"])
        logger.error("❌ Connection failed: %s", err)

        if "differs from the user currently logged in" in err:
            logger.warning(
                "User mismatch detected — clearing SNOWFLAKE_USER environment variable."
            )
            os.environ.pop("SNOWFLAKE_USER", None)

        return None

    if "conn" not in conn_container:
        logger.error("❌ Unexpected failure — no connection object returned.")
        return None

    conn = conn_container["conn"]
    logger.info("✅ Authentication successful for %s", creds["user"])
    print("Retrieving available roles and warehouses...\n")

    # --- Discover available roles and warehouses ----------------------------------------------------
    try:
        cur = conn.cursor()
        available_roles = {row[1] for row in cur.execute("SHOW ROLES")}
        available_whs = {row[0] for row in cur.execute("SHOW WAREHOUSES")}
        cur.close()
    except Exception as exc:
        log_exception(exc, context="Retrieving Snowflake roles/warehouses")
        conn.close()
        return None

    # --- Attempt context selection ------------------------------------------------------------------
    for context_item in CONTEXT_PRIORITY:
        role = context_item["role"]
        wh = context_item["warehouse"]

        if role in available_roles and wh in available_whs:
            logger.info("🔧 Matching context available → %s/%s", role, wh)
            if set_snowflake_context(conn, role, wh):
                return conn
            logger.warning(
                "⚠️ Failed to apply context %s/%s; trying next option.",
                role,
                wh,
            )

    # --- No valid context found ----------------------------------------------------------------------
    logger.error("❌ No valid role/warehouse combination found for this user.")
    print("\nRequired contexts (role / warehouse):")
    for ctx in CONTEXT_PRIORITY:
        print(f"  • {ctx['role']}  /  {ctx['warehouse']}")
    conn.close()
    return None


# ====================================================================================================
# 7. SQL EXECUTION HELPER
# ----------------------------------------------------------------------------------------------------
def run_query(conn: Any, sql: str, fetch: bool = True) -> Any | None:
    """
    Description:
        Execute a SQL query safely against an open Snowflake connection with
        full logging and optional result fetching.

    Args:
        conn (Any):
            Active Snowflake connection object.
        sql (str):
            SQL statement to execute.
        fetch (bool):
            When True, fetch all result rows and return them; when False,
            execute without returning data.

    Returns:
        Any | None:
            A sequence of result rows if fetch=True and the query returns
            data; otherwise None.

    Raises:
        None.

    Notes:
        - Any exceptions during execution are logged via log_exception and
          result in a None return value.
        - Only a short preview of the SQL (first 100 characters) is logged to
          avoid excessive log size.
    """
    try:
        cur = conn.cursor()
        cur.execute(sql)

        preview_raw = sql.replace("\n", " ")
        preview = preview_raw[:100]
        if len(preview_raw) > 100:
            preview = f"{preview}..."

        logger.info("🧠 Executed SQL (preview): %s", preview)

        if fetch:
            data = cur.fetchall()
            cur.close()
            logger.info("📦 Rows fetched: %s", len(data))
            return data

        cur.close()
        logger.info("✅ Query executed successfully (no fetch).")
        return None

    except Exception as exc:
        log_exception(exc, context="run_query")
        return None


# ====================================================================================================
# 8. MAIN EXECUTION (SANDBOXED TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Description:
        Manual test runner for validating Snowflake authentication and context
        setup using Okta SSO.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Uses print() for interactive prompts as an explicit exception to the
          usual "no print in core modules" rule.
        - Attempts to read a default email from configuration under:
              section = "snowflake", key = "email"
          and prompts the user if not present.
    """
    init_logging(enable_console=True)
    logger.info("🔍 Running C14_snowflake_connector self-test...")

    print("🔍 Running C14_snowflake_connector self-test...\n")

    test_email: str = get_config("snowflake", "email", default="")  # type: ignore[assignment]
    if not test_email:
        test_email = input("Enter your Snowflake/Okta email address: ").strip()

    connection = connect_to_snowflake(test_email)

    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT CURRENT_USER(), CURRENT_ACCOUNT(), CURRENT_ROLE(),
                       CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();
                """
            )
            user, acct, role, wh, db, sc = cursor.fetchone()

            print(
                f"\n👤 {user} | 🏢 {acct} | 🧩 {role} | 🏭 {wh} | "
                f"📚 {db} | 📁 {sc}\n"
            )

            sample_sql = "SELECT CURRENT_DATE(), CURRENT_TIMESTAMP();"
            result = run_query(connection, sample_sql)

            if result:
                print(f"🧾 Sample query result: {result}")

            cursor.close()
            connection.close()
            logger.info("✅ Snowflake connection closed cleanly.")

        except Exception as exc:
            log_exception(exc, context="C14 self-test main block")
    else:
        logger.error("❌ Snowflake connection test failed.")
        print("❌ Snowflake connection test failed. Check logs for details.")
