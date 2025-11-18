# ====================================================================================================
# <File Name>
# ----------------------------------------------------------------------------------------------------
# High-level description of module functionality.
#
# Purpose:
#   - xxx
#   - xxx
#   - xxx
#
# Usage:
#   Example showing how this module is typically used.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      <DD-MMM-YYYY>
# Project:      <Project Name>
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
# Import anything required from the core library or other project modules.
#
# Notes:
#   - ALWAYS use ABSOLUTE imports.
#       Example: from core.C03_logging_handler import get_logger
#   - DO NOT use relative imports ("from .x import y").
#
#   - IMPORTANT: Core modules MUST import shared packages from:
#         from core.C00_set_packages import *
#
#   - CRITICAL WARNING:
#       No GUI libraries (tkinter, ttk, ttkbootstrap, PIL, etc.) may be imported
#       directly inside the core library. All GUI-related imports belong in:
#           gui/G00b_gui_packages.py
#       This prevents early bootstrap execution and circular-initialisation issues.
# ----------------------------------------------------------------------------------------------------