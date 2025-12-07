# ====================================================================================================
# SP2.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Developer sandbox for the "Connection Launcher" layout.
#
#   Validates the new 3-row / 4-column layout concept using the production GUI framework:
#
#       • Top Row    → 30% Overview  + 70% Console Log (2 cards)
#       • Middle Row → 4 × 25% configuration cards
#            - Google Drive
#            - Snowflake
#            - Accounting Period
#            - Datawarehouse Period
#       • Bottom Row → 4 × 25% provider tiles
#            - Braintree
#            - Uber Eats
#            - Deliveroo
#            - Just Eat
#
#   This file is a DEVELOPER SANDBOX ONLY:
#       - Extra logging
#       - Inline debug hints in cards
#       - No business logic, no real connections
#
# ----------------------------------------------------------------------------------------------------
# Author:  Gerry Pidgeon
# Created: 2025-11-26
# Project: Core Boilerplate v1.0 (GUI Scratchpad)
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

# --- Remove '' (current working directory) which can shadow installed packages ----------------------
if "" in sys.path:
    sys.path.remove("")

# --- Prevent creation of __pycache__ folders --------------------------------------------------------
sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Bring in shared external packages from the central import hub.
#
# CRITICAL ARCHITECTURE RULE:
#   ALL external + stdlib packages MUST be imported exclusively via:
#       from core.C00_set_packages import *
#   No other script may import external libraries directly.
#
# C01_set_file_paths is a pure core module and must not import GUI packages.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
import gui.G02b_layout_utils as m
print("Loaded from:", m.__file__)
print("Public API:", getattr(m, "__all__", None))
