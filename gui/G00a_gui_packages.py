# ====================================================================================================
# G00a_gui_packages.py
# ----------------------------------------------------------------------------------------------------
# Centralised GUI import hub for Tkinter, ttk, and optional ttkbootstrap.
#
# Purpose:
#   - Provide a single, safe import location for all GUI-related libraries.
#   - Prevent GUI imports from appearing in the core library (critical architecture rule).
#   - Avoid premature Tk/ttkbootstrap initialisation during core/module loading.
#   - Keep GUI modules lightweight by importing from this shared hub.
#
# Usage:
#   from gui.G00a_gui_packages import tk, ttk, tkFont, ...
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      17-Nov-2025
# Project:      CustomPythonCoreFunctions v1.0
# ====================================================================================================


# ====================================================================================================
# OVERVIEW
# ----------------------------------------------------------------------------------------------------
# Exports:
#   - tk, ttk, tkFont, scrolledtext
#   - messagebox, filedialog
#
# Optional (when enable_ttkbootstrap() is called):
#   - Window, Style, ThemedLabel, ThemedButton, ThemedFrame
#
# Architecture Rules:
#   • No sys.path manipulation
#   • No project imports
#   • No core imports
#   • No side effects
#   • Safe to import anywhere in the GUI layer
#   • Tkinter must ONLY be imported from this module
# ----------------------------------------------------------------------------------------------------


# ====================================================================================================
# 1. BASE TKINTER IMPORTS
# ----------------------------------------------------------------------------------------------------
# Tkinter imports must be isolated in this module to avoid:
#   - accidental root-window creation
#   - early theme/ttkbootstrap initialisation
#   - circular dependencies with core
#   - environment crashes on machines without a GUI subsystem
# ----------------------------------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkFont
from tkinter import scrolledtext



# ====================================================================================================
# 2. OPTIONAL ttkbootstrap SUPPORT (OPT-IN ONLY)
# ----------------------------------------------------------------------------------------------------
# ttkbootstrap must be opt-in because:
#   - Not all environments include it.
#   - Importing ttkbootstrap too early overrides themes and breaks style setup.
#   - BaseGUI must initialise FIRST to apply project-wide styles.
#
# Usage:
#       from gui.G00a_gui_packages import enable_ttkbootstrap
#       enable_ttkbootstrap()
#
# NOTE:
#       Must be called BEFORE creating BaseGUI() or applying styles.
# ----------------------------------------------------------------------------------------------------

tb = None
Window = None
Style = None
ThemedLabel = ttk.Label
ThemedButton = ttk.Button
ThemedFrame = ttk.Frame


def enable_ttkbootstrap():
    """Opt-in, safe activation of ttkbootstrap. Silent fallback to pure ttk if unavailable."""
    global tb, Window, Style, ThemedLabel, ThemedButton, ThemedFrame

    try:
        import ttkbootstrap as _tb
        tb = _tb
        Window = tb.Window
        Style = tb.Style
        ThemedLabel = tb.Label
        ThemedButton = tb.Button
        ThemedFrame = tb.Frame

    except Exception as exc:
        # Silent fallback to standard ttk widgets
        print("DEBUG: ttkbootstrap failed →", repr(exc))
        tb = None
        Window = None
        Style = None
        ThemedLabel = ttk.Label
        ThemedButton = ttk.Button
        ThemedFrame = ttk.Frame

# ====================================================================================================
# 3. OPTIONAL GUI WIDGET PACKAGES
# ----------------------------------------------------------------------------------------------------
# Additional GUI widget libraries should be imported here.
# tkcalendar provides Calendar and DateEntry widgets for date selection.
# These imports are optional and only needed for modules that use date-based UI components.
# ----------------------------------------------------------------------------------------------------
try:
    from tkcalendar import Calendar, DateEntry
except Exception:
    # Graceful fallback: tkcalendar is optional
    Calendar = None
    DateEntry = None
