# ====================================================================================================
# C00_set_packages.py
# ----------------------------------------------------------------------------------------------------
# Central import hub for all reusable project dependencies.
#
# Purpose:
#   - Provide a single controlled location for all third-party and standard library imports.
#   - Allow other modules to simplify their imports using:  from core.C00_set_packages import *
#   - Guarantee consistent dependency availability across any project using the core library.
#
# Usage:
#   from core.C00_set_packages import *
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
# Import anything required from the core library or other project modules.
#
# Notes:
#   - ALWAYS use ABSOLUTE imports.
#       Example: from core.C03_logging_handler import get_logger
#   - DO NOT use relative imports ("from .x import y").
#
#   - IMPORTANT:
#       Core modules MUST import shared packages from:
#           from core.C00_set_packages import *
#
#   - CRITICAL WARNING:
#       No GUI libraries (tkinter, ttk, ttkbootstrap, PIL, etc.) may be imported
#       directly inside the core library. All GUI-related imports belong in:
#           gui/G00b_gui_packages.py
#       This prevents early bootstrap execution and circular-initialisation issues.
#
#   - C00 itself must NEVER import from other core modules to avoid circular dependencies.
# ----------------------------------------------------------------------------------------------------


# ====================================================================================================
# 3. STANDARD LIBRARY IMPORTS
# ----------------------------------------------------------------------------------------------------
# Common Python standard-library modules likely to be used across many scripts.
# These are guaranteed to exist in all Python environments.
# ----------------------------------------------------------------------------------------------------
import os                                               # OS operations (paths, environment variables)
import io                                               # Streams and in-memory buffers
import re                                               # Regular expressions
import csv                                              # CSV reader/writer
import time                                             # Timing utilities, sleep()
import json                                             # JSON encoding/decoding
import glob                                             # Wildcard file matching
import shutil                                           # File/folder operations
import logging                                          # Logging API (configured separately in C03)
import queue                                            # Thread-safe FIFO queue
import platform                                         # OS/platform detection
import subprocess                                       # Run system commands / processes
import calendar                                         # Calendar utilities
import tempfile                                         # Temporary file/directory utilities
import threading                                        # Lightweight threading
import zipfile                                          # ZIP archive utilities
import getpass                                          # Get current username (useful for WSL/paths)
import pickle                                           # Object serialisation
import hashlib                                          # Standard library hashing (MD5/SHA families)
import contextlib                                       # Context manager utilities

import datetime as dt                                   # Primary datetime module (aliased)
from datetime import date, timedelta, datetime          # Common date utilities

from typing import (
    Any,                # Generic placeholder type
    Callable,           # Callable[..., T] — function/method signatures
    Dict,               # Dictionary type annotation
    List,               # List[T] — ordered, mutable sequences
    Literal,            # Literal["A", "B"] — fixed allowed values
    MutableMapping,     # Dict-like mutable mappings (e.g., config objects)
    Optional,           # Optional[T] shorthand (T | None)
    Tuple,              # Fixed-length tuple structures
    Union,              # Union[A, B] — multiple allowed types
    overload,           # Function overload declarations for typing
)

from concurrent.futures import (
    ThreadPoolExecutor,             # Thread-based parallel task execution
    ProcessPoolExecutor,            # Process-based (CPU-bound) task parallelism
    as_completed,                   # Iterate futures as they complete (progress-friendly)
)


# ====================================================================================================
# 4. THIRD-PARTY LIBRARIES
# ----------------------------------------------------------------------------------------------------
# Widely-used external libraries that support data handling, PDF processing, APIs, and DWH access.
# These imports are global because they are used across multiple modules and projects.
# ----------------------------------------------------------------------------------------------------
import numpy as np                        # (pip install numpy) Numerical computing
import pandas as pd                       # (pip install pandas) Tabular data analysis
import requests                           # (pip install requests) HTTP requests / APIs

import openpyxl                           # (pip install openpyxl) Excel .xlsx reader/writer
import PyPDF2                             # (pip install PyPDF2) PDF merging/splitting
import pdfplumber                         # (pip install pdfplumber) High-accuracy PDF extraction
from pdfminer.high_level import extract_text   # Fallback PDF text extractor

import yaml                               # (pip install pyyaml) YAML configuration parsing
import snowflake.connector                # (pip install snowflake-connector-python) Snowflake DWH

from tqdm import tqdm                     # (pip install tqdm) Progress bars for loops/tasks


# ====================================================================================================
# 5. WEB AUTOMATION LIBRARIES (SELENIUM)
# ----------------------------------------------------------------------------------------------------
# Selenium provides full browser automation capabilities. These imports enable:
#   - launching controlled Chrome browser instances
#   - interacting with web elements using XPATH/CSS/ID selectors
#   - simulating keypresses
#   - using explicit waits for complex page interactions
# Web automation is centralised here for consistency across:
#   - scraping workflows
#   - online platform integrations (e.g., JustEat, PayPal, UberEats)
#   - automated download tasks
# ----------------------------------------------------------------------------------------------------
from selenium import webdriver                               # Base driver interface
from selenium.webdriver.common.by import By                  # Element locator strategies
from selenium.webdriver.common.keys import Keys              # Keyboard control constants
from selenium.webdriver.chrome.options import Options        # Chrome configuration (headless, flags)
from selenium.webdriver.support.ui import WebDriverWait      # Explicit waiting for conditions
from selenium.webdriver.support import expected_conditions as EC   # Element state conditions
from webdriver_manager.chrome import ChromeDriverManager     # Auto-download & manage ChromeDriver


# ====================================================================================================
# 6. GOOGLE API & OAUTH CLIENT LIBRARIES
# ----------------------------------------------------------------------------------------------------
# Google API client suite for authentication and accessing Google services.
#
# These imports support:
#   - OAuth 2.0 credential storage and refresh
#   - launching local login flows for the first-time authentication
#   - building service clients for APIs such as:
#         • Google Drive
#         • Google Sheets
#         • Google Docs
#         • Gmail API
#   - file upload/download operations
# Consolidation here ensures that all Google integrations use consistent authentication logic.
# ----------------------------------------------------------------------------------------------------
from google.auth.transport.requests import Request                    # Token refresh transport
from google.oauth2.credentials import Credentials                     # OAuth2 credential wrapper
from google_auth_oauthlib.flow import InstalledAppFlow                # Local OAuth login flow
from googleapiclient.discovery import build                           # Google API service builder
from googleapiclient.errors import HttpError                          # Common API error handler
from googleapiclient.http import (
    MediaFileUpload,              # Upload local files (Drive/Sheets/etc.)
    MediaIoBaseUpload,            # Upload from file-like objects
    MediaIoBaseDownload,          # Stream-download files (Google Drive)
)


# ====================================================================================================
# END OF CENTRAL IMPORT HUB
# ----------------------------------------------------------------------------------------------------
# All downstream modules access these via:
#     from core.C00_set_packages import *
#
# This guarantees a consistent environment across all projects using the core library.
# ====================================================================================================
