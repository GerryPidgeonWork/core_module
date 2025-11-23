# ====================================================================================================
# C13_gui_helpers.py
# ----------------------------------------------------------------------------------------------------
# Provides reusable GUI utilities and visual standards for all CustomPythonCoreFunctions v1.0 projects.
#
# Purpose:
#   - Centralise common Tkinter operations (popups, progress bars, threaded tasks, helpers).
#   - Provide consistent fonts, colours, and behaviour across GUI modules.
#   - Offer safe wrappers using the core logging framework.
#
# Usage:
#   from core.C13_gui_helpers import show_info, ProgressPopup, run_in_thread
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
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
from gui.G00a_gui_packages import tk, ttk, messagebox
from gui.G00a_gui_packages import tkFont


# ====================================================================================================
# 3. GUI STYLE CONSTANTS
# ----------------------------------------------------------------------------------------------------
GUI_THEME = {
    "bg": "#F8F9FA",
    "fg": "#212529",
    "accent": "#0D6EFD",
    "success": "#198754",
    "warning": "#FFC107",
    "error": "#DC3545",
    "font": ("Segoe UI", 10),
    "font_bold": ("Segoe UI", 10, "bold"),
}


# ====================================================================================================
# 4. MESSAGE POPUPS
# ----------------------------------------------------------------------------------------------------
def show_info(message: str, title: str = "Information") -> None:
    """
    Description:
        Display an informational Tkinter message box and log the message.

    Args:
        message (str): Informational text to show in the popup body.
        title (str): Caption for the popup window. Defaults to "Information".

    Returns:
        None.

    Raises:
        None.

    Notes:
        - A temporary, hidden Tk root window is created solely for the
          message box and destroyed immediately afterwards.
        - Any unexpected exception is logged using log_exception() and
          suppressed (no exception is propagated to the caller).
    """
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(title, message)
        root.destroy()
        logger.info("💬 Info: %s", message)
    except Exception as error:
        log_exception(error, context="show_info")


def show_warning(message: str, title: str = "Warning") -> None:
    """
    Description:
        Display a warning Tkinter message box and log the message.

    Args:
        message (str): Warning text to show in the popup body.
        title (str): Caption for the popup window. Defaults to "Warning".

    Returns:
        None.

    Raises:
        None.

    Notes:
        - A temporary, hidden Tk root window is created solely for the
          message box and destroyed immediately afterwards.
        - Any unexpected exception is logged using log_exception() and
          suppressed (no exception is propagated to the caller).
    """
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(title, message)
        root.destroy()
        logger.warning("⚠️ Warning: %s", message)
    except Exception as error:
        log_exception(error, context="show_warning")


def show_error(message: str, title: str = "Error") -> None:
    """
    Description:
        Display an error Tkinter message box and log the message.

    Args:
        message (str): Error text to show in the popup body.
        title (str): Caption for the popup window. Defaults to "Error".

    Returns:
        None.

    Raises:
        None.

    Notes:
        - A temporary, hidden Tk root window is created solely for the
          message box and destroyed immediately afterwards.
        - Any unexpected exception is logged using log_exception() and
          suppressed (no exception is propagated to the caller).
    """
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
        logger.error("❌ Error: %s", message)
    except Exception as error:
        log_exception(error, context="show_error")


# ====================================================================================================
# 5. PROGRESS POPUP CLASS
# ----------------------------------------------------------------------------------------------------
class ProgressPopup:
    """
    Description:
        A reusable modal popup window providing a progress bar and status
        label for long-running tasks in Tkinter-based GUIs.

    Args:
        parent (tk.Tk): The parent Tk root or Toplevel window that owns
            this popup.
        message (str): Initial status message displayed above the progress
            bar. Defaults to "Processing...".

    Returns:
        None.

    Raises:
        None.

    Notes:
        - The popup grabs focus using grab_set() to behave modally relative
          to its parent.
        - Use as a context manager to ensure that the window is reliably
          destroyed when processing completes.
        - Progress is updated using update_progress(), which also triggers
          idle-task processing to keep the UI responsive.
    """

    def __init__(self, parent: tk.Tk, message: str = "Processing...") -> None:
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Please wait")
        self.window.configure(bg=GUI_THEME["bg"])
        self.window.geometry("350x120")
        self.window.resizable(False, False)
        self.window.grab_set()

        # -- Message label --
        self.label = ttk.Label(self.window, text=message, font=GUI_THEME["font_bold"])
        self.label.pack(pady=10)

        # -- Progress bar --
        self.progress = ttk.Progressbar(self.window, length=300, mode="determinate")
        self.progress.pack(pady=10)

        # -- Status text --
        self.status_label = ttk.Label(self.window, text="", font=GUI_THEME["font"])
        self.status_label.pack()

        logger.info("🪄 ProgressPopup initialised.")

    def update_progress(self, current: int, total: int) -> None:
        """
        Description:
            Update the progress bar and status label with the current
            progress percentage.

        Args:
            current (int): Current units of work completed.
            total (int): Total units of work expected.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - The percentage is computed as int((current / total) * 100).
            - Any unexpected errors are logged via log_exception() and
              suppressed.
        """
        try:
            percent = int((current / total) * 100) if total else 0
            self.progress["value"] = percent
            self.status_label.config(text=f"{percent}% complete")
            self.window.update_idletasks()
        except Exception as error:
            log_exception(error, context="ProgressPopup.update_progress")

    def __enter__(self) -> "ProgressPopup":
        """
        Description:
            Enter the context manager for ProgressPopup.

        Args:
            None.

        Returns:
            ProgressPopup: The ProgressPopup instance itself.

        Raises:
            None.

        Notes:
            - Allows usage with the "with" statement for automatic cleanup
              in __exit__().
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Description:
            Exit the context manager, destroying the popup window and
            logging its closure.

        Args:
            exc_type (type | None): Exception type if an error occurred.
            exc_val (BaseException | None): Exception instance if raised.
            exc_tb (TracebackType | None): Traceback object if available.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - The popup is destroyed regardless of whether an exception
              occurred inside the context block.
        """
        self.window.destroy()
        logger.info("✅ ProgressPopup closed.")


# ====================================================================================================
# 6. THREAD-SAFE TASK WRAPPER
# ----------------------------------------------------------------------------------------------------
def run_in_thread(target: Callable[..., Any], *args: Any, **kwargs: Any) -> threading.Thread:
    """
    Description:
        Run a blocking callable in a background daemon thread and log
        thread start and any uncaught exceptions.

    Args:
        target (Callable[..., Any]): Function or callable object to run
            in the background.
        *args (Any): Positional arguments forwarded to target.
        **kwargs (Any): Keyword arguments forwarded to target.

    Returns:
        threading.Thread: The started daemon thread instance.

    Raises:
        None.

    Notes:
        - Any exception raised by target is caught inside the thread and
          logged via log_exception() with the callable name as context.
        - The thread is created with daemon=True so it will not block
          interpreter shutdown.
    """

    def wrapper() -> None:
        try:
            target(*args, **kwargs)
        except Exception as error:
            log_exception(error, context=f"Thread: {getattr(target, '__name__', str(target))}")

    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()

    logger.info("🚀 Started thread for: %s", getattr(target, "__name__", str(target)))
    return thread


# ====================================================================================================
# 7. MAIN EXECUTION (SANDBOXED TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Description:
        Standalone sandboxed test for GUI helpers. Demonstrates info,
        warning, and error popups, followed by a simulated progress
        sequence using ProgressPopup.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Uses init_logging(enable_console=True) so that diagnostics are
          written to both the log file and the console.
        - No print() statements are used in accordance with core testing
          rules for self-tests.
    """
    init_logging(enable_console=True)
    logger.info("🔍 Running C13_gui_helpers self-test...")

    import time

    root = tk.Tk()
    root.withdraw()

    show_info("This is an info message.")
    show_warning("This is a warning message.")
    show_error("This is an error message.")

    with ProgressPopup(root, "Simulating progress...") as popup:
        for i in range(0, 101, 10):
            popup.update_progress(i, 100)
            time.sleep(0.1)

    root.destroy()
    logger.info("✅ GUI helpers sandboxed test complete.")
