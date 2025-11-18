# ====================================================================================================
# C17_web_automation.py
# ----------------------------------------------------------------------------------------------------
# Provides standardised Selenium utilities for browser automation across projects.
#
# Purpose:
#   - Simplify Selenium setup using Chrome WebDriver and shared configuration.
#   - Handle OS-specific Chrome profile locations and optional headless mode.
#   - Provide utility helpers for waiting, scrolling, clicking, and clean shutdown.
#
# Notes:
#   - All Selenium-related imports (webdriver, By, WebDriverWait, EC, etc.) come
#     exclusively from core.C00_set_packages in line with architecture rules.
#   - Designed for reuse across CLI, service, and GUI-style projects.
#
# Usage:
#   from core.C17_selenium_utils import (
#       get_chrome_driver,
#       wait_for_element,
#       scroll_to_bottom,
#       click_element,
#       close_driver,
#   )
#
#   driver = get_chrome_driver(headless=True)
#   if driver:
#       driver.get("https://www.google.com")
#       search_box = wait_for_element(driver, by="name", selector="q", timeout=10)
#       close_driver(driver)
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
from core.C02_system_processes import detect_os


# ====================================================================================================
# 3. SELENIUM DRIVER SETUP
# ----------------------------------------------------------------------------------------------------
def get_chrome_driver(profile_name: str | None = None, headless: bool = False) -> Any:
    """
    Summary:
        Create and return a configured Selenium Chrome WebDriver instance.

    Extended Description:
        This helper builds a ChromeOptions configuration, applies sensible
        defaults for stability (no sandbox, disable GPU, etc.), and optionally
        enables headless mode. It also attempts to attach to a user profile
        directory based on the detected operating system so that existing
        browser sessions (cookies, saved logins) can be reused when desired.

    Args:
        profile_name (str | None):
            Name of the Chrome profile to use (for example, "Default",
            "Profile 1"). When None, Chrome is started with a temporary,
            anonymous profile.
        headless (bool):
            When True, Chrome is started in headless mode (no visible UI).
            Defaults to False.

    Returns:
        Any:
            An active WebDriver instance if initialisation succeeds;
            otherwise None when an error occurs.

    Raises:
        None.

    Notes:
        - All exceptions encountered while creating the driver are logged via
          log_exception and result in a None return.
        - WebDriver binaries and Selenium packages are provided centrally by
          core.C00_set_packages.
    """
    try:
        # You can also use Options() imported via C00_set_packages, but
        # webdriver.ChromeOptions() keeps the dependency surface explicit.
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")

        if headless:
            # New-style headless flag for modern Chrome
            options.add_argument("--headless=new")

        os_label = detect_os().lower()
        if "windows" in os_label:
            base_path = Path.home() / "AppData/Local/Google/Chrome/User Data"
        elif "mac" in os_label or "darwin" in os_label:
            base_path = Path.home() / "Library/Application Support/Google/Chrome"
        else:
            # Linux and other Unix-like environments
            base_path = Path.home() / ".config/google-chrome"

        if profile_name:
            options.add_argument(f"--user-data-dir={base_path}")
            options.add_argument(f"--profile-directory={profile_name}")
            logger.info("🧠 Using Chrome profile '%s' at '%s'", profile_name, base_path)

        driver = webdriver.Chrome(options=options)
        logger.info("✅ Chrome WebDriver initialised successfully (headless=%s).", headless)
        return driver

    except Exception as exc:
        log_exception(exc, context="get_chrome_driver")
        return None


# ====================================================================================================
# 4. SELENIUM HELPER FUNCTIONS
# ----------------------------------------------------------------------------------------------------
def wait_for_element(driver: Any, by: str, selector: str, timeout: int = 10) -> Any:
    """
    Summary:
        Wait for an element to be present in the DOM and return it.

    Extended Description:
        This function uses Selenium's WebDriverWait and expected conditions to
        poll the page until a matching element is found or the timeout is
        reached. The locator strategy is derived from selenium.webdriver.common.by.By.

    Args:
        driver (Any):
            Active Selenium WebDriver instance.
        by (str):
            Locator strategy name that maps to a member of By
            (for example, "id", "xpath", "css_selector", "name").
        selector (str):
            Selector string used with the chosen strategy.
        timeout (int):
            Maximum time, in seconds, to wait for the element to appear.
            Defaults to 10.

    Returns:
        Any:
            The located WebElement when found successfully; otherwise None
            if the wait times out or an error occurs.

    Raises:
        None.

    Notes:
        - If an invalid locator strategy is supplied, an AttributeError is
          logged and None is returned.
        - Presence in the DOM is checked (not necessarily visibility).
    """
    try:
        try:
            by_attr = getattr(By, by.upper())
        except AttributeError as attr_err:
            log_exception(attr_err, context=f"wait_for_element (invalid locator '{by}')")
            return None

        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by_attr, selector))
        )
        logger.info("✅ Element located by %s: %s", by, selector)
        return element

    except Exception as exc:
        log_exception(exc, context=f"wait_for_element({by!r}, {selector!r})")
        return None


def scroll_to_bottom(driver: Any, pause_time: float = 1.0) -> None:
    """
    Summary:
        Scroll the active page gradually to the bottom.

    Extended Description:
        This helper repeatedly scrolls to the bottom of the document body,
        pausing between scrolls, until no further height changes are detected.
        It is particularly useful for pages that implement lazy-loading of
        content as the user scrolls down.

    Args:
        driver (Any):
            Active Selenium WebDriver instance.
        pause_time (float):
            Delay in seconds between scroll operations. Defaults to 1.0.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Any unexpected exception during scrolling is logged and swallowed.
        - The function returns when no additional content is loaded.
    """
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        logger.info("📜 Finished scrolling to the bottom of the page.")
    except Exception as exc:
        log_exception(exc, context="scroll_to_bottom")


def click_element(driver: Any, by: str, selector: str) -> bool:
    """
    Summary:
        Safely locate and click a specific web element.

    Extended Description:
        This helper first reuses wait_for_element() to locate the desired
        element and then attempts to click it, logging both success and
        failure outcomes. It is intended as a robust wrapper for simple
        click operations.

    Args:
        driver (Any):
            Active Selenium WebDriver instance.
        by (str):
            Locator strategy name (for example, "xpath", "css_selector", "id").
        selector (str):
            Selector string matching the desired element.

    Returns:
        bool:
            True when the click succeeds, False if the element cannot be
            found or if the click operation raises an exception.

    Raises:
        None.

    Notes:
        - Uses wait_for_element() internally, so locator issues are logged
          there first.
        - Any click-related errors are logged with full context.
    """
    element = wait_for_element(driver, by=by, selector=selector)
    if not element:
        logger.warning("⚠️  Element not clickable (not found): %s", selector)
        return False

    try:
        element.click()
        logger.info("🖱️  Clicked element located by %s: %s", by, selector)
        return True
    except Exception as exc:
        log_exception(exc, context=f"click_element({by!r}, {selector!r})")
        return False


def close_driver(driver: Any) -> None:
    """
    Summary:
        Cleanly close a Selenium WebDriver session.

    Extended Description:
        Attempts to quit the WebDriver instance, releasing any associated
        browser processes and resources. Errors during shutdown are logged
        but otherwise ignored so that caller code can continue gracefully.

    Args:
        driver (Any):
            Active WebDriver instance to close.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - This function is safe to call even if the driver is already closed
          or partially initialised; errors are simply logged.
    """
    try:
        driver.quit()
        logger.info("🧹 Selenium driver session closed cleanly.")
    except Exception as exc:
        log_exception(exc, context="close_driver")


# ====================================================================================================
# 5. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Summary:
        Run a minimal self-test of Selenium utilities.

    Extended Description:
        This self-test initialises logging, starts a headless Chrome session,
        navigates to Google's homepage, waits for the search box, scrolls to
        the bottom of the page, and then closes the driver. All progress and
        any errors are logged via the central logging framework.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Requires network connectivity and a functioning Chrome installation.
        - Designed to be safe to run from the /core/ directory:
              python C17_selenium_utils.py
    """
    init_logging(enable_console=True)
    logger.info("🔍 Running C17_selenium_utils self-test...")

    driver_instance = get_chrome_driver(profile_name=None, headless=True)
    if not driver_instance:
        logger.error("❌ Selenium self-test failed: WebDriver could not be created.")
    else:
        try:
            driver_instance.get("https://www.google.com")
            _ = wait_for_element(driver_instance, by="name", selector="q", timeout=10)
            scroll_to_bottom(driver_instance, pause_time=0.5)
            logger.info("✅ Selenium self-test completed successfully.")
        except Exception as exc:
            log_exception(exc, context="C17_selenium_utils self-test")
        finally:
            close_driver(driver_instance)
