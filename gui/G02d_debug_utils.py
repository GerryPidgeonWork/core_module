# ====================================================================================================
# G02d_debug_utils.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Comprehensive Developer Debug Console for GUI Boilerplate
#
#   Provides extensive tools for visual and programmatic debugging:
#
#   TABS:
#       1. System Info      - Python, Tk, ttkbootstrap versions, memory
#       2. Import Status    - Module import diagnostics with timing
#       3. Style Explorer   - Browse all ttk styles, fonts, colours
#       4. Widget Gallery   - Interactive widget demos
#       5. Widget Inspector - Select and inspect any widget
#       6. Colour Palette   - Visual display of all design tokens
#       7. Performance      - Timing metrics for common operations
#       8. Log Viewer       - Real-time log output in GUI
#
#   FEATURES:
#       • Real-time widget inspection
#       • Style and font browser
#       • Colour swatch display
#       • Performance benchmarking
#       • Export diagnostics to file
#       • Interactive testing tools
#
# Usage:
#   python gui/G02d_debug_utils.py
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-23
# Updated:      2025-11-28 (v2 - Comprehensive debug system)
# Project:      Core Boilerplate v1.0
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ====================================================================================================
from __future__ import annotations

import sys
import time
import platform
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Callable
from io import StringIO

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

if "" in sys.path:
    sys.path.remove("")

sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ====================================================================================================
from core.C00_set_packages import *

from core.C03_logging_handler import get_logger, init_logging
logger = get_logger(__name__)

from gui.G00a_gui_packages import tk, ttk, tkFont, scrolledtext, Window, Style, tb
from gui.G01a_style_config import *
from gui.G01b_style_engine import (
    configure_ttk_styles,
    FONT_NAME_BASE,
    FONT_NAME_HEADING,
    FONT_NAME_SECTION_HEADING,
)
from gui.G01c_widget_primitives import (
    make_label,
    make_button,
    make_entry,
    make_textarea,
    make_combobox,
    make_checkbox,
    make_radio,
    make_switch,
    make_divider,
    make_spacer,
    make_frame,
    make_button_bar,
    make_horizontal_group,
    make_vertical_group,
)
from gui.G02a_layout_utils import (
    safe_grid,
    safe_pack,
    ensure_row_weights,
    ensure_column_weights,
    grid_form_row,
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
    SPACING_LG,
    SPACING_XL,
)


# ====================================================================================================
# 3. TIMING UTILITIES
# ====================================================================================================
@dataclass
class TimingResult:
    """Result of a timed operation."""
    name: str
    duration_ms: float
    success: bool
    error: Optional[str] = None


class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time: float = 0
        self.end_time: float = 0
    
    def __enter__(self) -> "Timer":
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.end_time = time.perf_counter()
    
    @property
    def elapsed_ms(self) -> float:
        return (self.end_time - self.start_time) * 1000


def time_operation(name: str, func: Callable[[], Any]) -> TimingResult:
    """Time a function and return result."""
    try:
        with Timer(name) as t:
            func()
        return TimingResult(name=name, duration_ms=t.elapsed_ms, success=True)
    except Exception as e:
        return TimingResult(name=name, duration_ms=0, success=False, error=str(e))


# ====================================================================================================
# 4. DIAGNOSTIC COLLECTORS
# ====================================================================================================
def get_system_info() -> Dict[str, str]:
    """Collect system information."""
    info = {
        "Python Version": platform.python_version(),
        "Platform": platform.platform(),
        "Architecture": platform.machine(),
        "Tk Version": "Unknown",
        "Tcl Version": "Unknown",
        "ttkbootstrap": "Not available",
    }
    
    try:
        # Need a Tk instance to get versions
        temp = tk.Tk()
        temp.withdraw()
        info["Tk Version"] = str(temp.tk.call("info", "patchlevel"))
        info["Tcl Version"] = str(temp.tk.call("info", "patchlevel"))
        temp.destroy()
    except Exception:
        pass
    
    try:
        if tb is not None:
            info["ttkbootstrap"] = getattr(tb, "__version__", "Available (version unknown)")
    except Exception:
        pass
    
    return info


def get_import_diagnostics() -> List[Tuple[str, str, float]]:
    """Check module imports and return (name, status, time_ms)."""
    modules = [
        "gui.G00a_gui_packages",
        "gui.G01a_style_config",
        "gui.G01b_style_engine",
        "gui.G01c_widget_primitives",
        "gui.G01d_layout_primitives",
        "gui.G02a_layout_utils",
        "gui.G02b_container_patterns",
        "gui.G02c_form_patterns",
    ]
    
    results: List[Tuple[str, str, float]] = []
    
    for module in modules:
        start = time.perf_counter()
        try:
            __import__(module, fromlist=["*"])
            elapsed = (time.perf_counter() - start) * 1000
            results.append((module.split(".")[-1], "OK", elapsed))
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            results.append((module.split(".")[-1], f"FAIL: {e}", elapsed))
    
    return results


def get_style_info(style_obj: ttk.Style) -> Dict[str, Any]:
    """Collect style engine information."""
    info: Dict[str, Any] = {
        "theme": "Unknown",
        "available_themes": [],
        "fonts": {},
        "key_styles": {},
    }
    
    try:
        info["theme"] = style_obj.theme_use()
        info["available_themes"] = list(style_obj.theme_names())
    except Exception:
        pass
    
    # Check named fonts
    font_names = [FONT_NAME_BASE, FONT_NAME_HEADING, FONT_NAME_SECTION_HEADING]
    for name in font_names:
        if name:
            try:
                font = tkFont.nametofont(name)
                info["fonts"][name] = font.actual()
            except Exception:
                info["fonts"][name] = None
    
    # Check key styles
    key_styles = [
        "TLabel", "TButton", "TEntry", "TFrame",
        "Primary.TButton", "Secondary.TButton",
        "Primary.Normal.TLabel", "Secondary.Normal.TLabel",
        "Primary.Heading.Bold.TLabel", "Primary.SectionHeading.Bold.TLabel",
        "SectionOuter.TFrame", "SectionBody.TFrame", "Card.TFrame",
    ]
    
    for style_name in key_styles:
        try:
            # Try to get any property to verify existence
            style_obj.lookup(style_name, "font")
            info["key_styles"][style_name] = True
        except Exception:
            info["key_styles"][style_name] = False
    
    return info


def get_colour_palette() -> Dict[str, str]:
    """Get all colour tokens from G01a."""
    colours = {}
    
    # Background colours
    colours["GUI_COLOUR_BG_PRIMARY"] = GUI_COLOUR_BG_PRIMARY
    colours["GUI_COLOUR_BG_SECONDARY"] = GUI_COLOUR_BG_SECONDARY
    colours["GUI_COLOUR_BG_TEXTAREA"] = GUI_COLOUR_BG_TEXTAREA
    
    # Text colours
    colours["TEXT_COLOUR_PRIMARY"] = TEXT_COLOUR_PRIMARY
    colours["TEXT_COLOUR_SECONDARY"] = TEXT_COLOUR_SECONDARY
    colours["TEXT_COLOUR_DISABLED"] = TEXT_COLOUR_DISABLED
    
    # Status colours
    colours["GUI_COLOUR_STATUS_SUCCESS"] = GUI_COLOUR_STATUS_SUCCESS
    colours["GUI_COLOUR_STATUS_WARNING"] = GUI_COLOUR_STATUS_WARNING
    colours["GUI_COLOUR_STATUS_ERROR"] = GUI_COLOUR_STATUS_ERROR
    
    # Button colours
    colours["BUTTON_PRIMARY_BG"] = BUTTON_PRIMARY_BG
    colours["BUTTON_SECONDARY_BG"] = BUTTON_SECONDARY_BG
    
    # Accent/divider
    colours["GUI_COLOUR_DIVIDER"] = GUI_COLOUR_DIVIDER
    colours["GUI_COLOUR_ACCENT"] = GUI_COLOUR_ACCENT
    
    return colours


def count_widgets(root: tk.Misc) -> Dict[str, int]:
    """Count widgets by type in the hierarchy."""
    counts: Dict[str, int] = {}
    
    def count_recursive(widget: tk.Misc) -> None:
        widget_type = type(widget).__name__
        counts[widget_type] = counts.get(widget_type, 0) + 1
        
        try:
            for child in widget.winfo_children():
                count_recursive(child)
        except Exception:
            pass
    
    count_recursive(root)
    return counts


# ====================================================================================================
# 5. LOG HANDLER FOR GUI
# ====================================================================================================
class TextHandler(logging.Handler):
    """Logging handler that writes to a Text widget."""
    
    def __init__(self, text_widget: tk.Text):
        super().__init__()
        self.text_widget = text_widget
        self.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S"
        ))
    
    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", msg + "\n")
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")
        except Exception:
            pass


# ====================================================================================================
# 6. TAB BUILDERS
# ====================================================================================================
def build_tab_system_info(parent: tk.Misc) -> None:
    """Build the System Info tab."""
    container = ttk.Frame(parent, style="TFrame")
    container.pack(fill="both", expand=True, padx=SPACING_LG, pady=SPACING_LG)
    
    make_label(container, "System Information", category="WindowHeading", weight="Bold").pack(anchor="w", pady=(0, SPACING_MD))
    
    info = get_system_info()
    
    info_frame = make_frame(container)
    info_frame.pack(fill="x", pady=(0, SPACING_LG))
    
    for i, (key, value) in enumerate(info.items()):
        make_label(info_frame, f"{key}:", category="Body", weight="Bold").grid(row=i, column=0, sticky="e", padx=(0, SPACING_MD), pady=SPACING_XS)
        make_label(info_frame, str(value), category="Body").grid(row=i, column=1, sticky="w", pady=SPACING_XS)
    
    make_divider(container).pack(fill="x", pady=SPACING_MD)
    
    # Widget count (will update after window is shown)
    make_label(container, "Widget Statistics", category="SectionHeading", weight="Bold").pack(anchor="w", pady=(0, SPACING_SM))
    
    stats_label = make_label(container, "Loading...", category="Body")
    stats_label.pack(anchor="w")
    
    def update_stats():
        try:
            root = container.winfo_toplevel()
            counts = count_widgets(root)
            total = sum(counts.values())
            text = f"Total widgets: {total}\n"
            for wtype, count in sorted(counts.items(), key=lambda x: -x[1])[:10]:
                text += f"  {wtype}: {count}\n"
            stats_label.configure(text=text)
        except Exception as e:
            stats_label.configure(text=f"Error: {e}")
    
    container.after(500, update_stats)


def build_tab_imports(parent: tk.Misc) -> None:
    """Build the Import Status tab."""
    container = ttk.Frame(parent, style="TFrame")
    container.pack(fill="both", expand=True, padx=SPACING_LG, pady=SPACING_LG)
    
    make_label(container, "Module Import Diagnostics", category="WindowHeading", weight="Bold").pack(anchor="w", pady=(0, SPACING_MD))
    
    results = get_import_diagnostics()
    
    # Header
    header = make_frame(container)
    header.pack(fill="x")
    make_label(header, "Module", category="Body", weight="Bold").grid(row=0, column=0, sticky="w", padx=(0, SPACING_LG))
    make_label(header, "Status", category="Body", weight="Bold").grid(row=0, column=1, sticky="w", padx=(0, SPACING_LG))
    make_label(header, "Time (ms)", category="Body", weight="Bold").grid(row=0, column=2, sticky="e")
    
    make_divider(container).pack(fill="x", pady=SPACING_SM)
    
    # Results
    results_frame = make_frame(container)
    results_frame.pack(fill="x")
    
    for i, (name, status, time_ms) in enumerate(results):
        make_label(results_frame, name, category="Body").grid(row=i, column=0, sticky="w", padx=(0, SPACING_LG), pady=SPACING_XS)
        
        if status == "OK":
            status_label = make_label(results_frame, "✓ OK", category="Success")
        else:
            status_label = make_label(results_frame, f"✗ {status[:30]}", category="Error")
        status_label.grid(row=i, column=1, sticky="w", padx=(0, SPACING_LG), pady=SPACING_XS)
        
        make_label(results_frame, f"{time_ms:.2f}", category="Body").grid(row=i, column=2, sticky="e", pady=SPACING_XS)
    
    # Total time
    total_time = sum(r[2] for r in results)
    make_divider(container).pack(fill="x", pady=SPACING_SM)
    make_label(container, f"Total import time: {total_time:.2f} ms", category="Body", weight="Bold").pack(anchor="e")


def build_tab_styles(parent: tk.Misc, style_obj: ttk.Style) -> None:
    """Build the Style Explorer tab."""
    container = ttk.Frame(parent, style="TFrame")
    container.pack(fill="both", expand=True, padx=SPACING_LG, pady=SPACING_LG)
    
    make_label(container, "Style Explorer", category="WindowHeading", weight="Bold").pack(anchor="w", pady=(0, SPACING_MD))
    
    info = get_style_info(style_obj)
    
    # Theme info
    make_label(container, f"Active Theme: {info['theme']}", category="Body", weight="Bold").pack(anchor="w")
    make_label(container, f"Available: {', '.join(info['available_themes'])}", category="Body").pack(anchor="w", pady=(0, SPACING_MD))
    
    make_divider(container).pack(fill="x", pady=SPACING_SM)
    
    # Fonts
    make_label(container, "Named Fonts", category="SectionHeading", weight="Bold").pack(anchor="w", pady=(SPACING_SM, SPACING_XS))
    
    for name, details in info["fonts"].items():
        if details:
            text = f"{name}: {details.get('family', '?')} {details.get('size', '?')}pt"
            if details.get('weight') == 'bold':
                text += " (bold)"
            make_label(container, text, category="Body").pack(anchor="w")
        else:
            make_label(container, f"{name}: Not registered", category="Warning").pack(anchor="w")
    
    make_divider(container).pack(fill="x", pady=SPACING_SM)
    
    # Key styles
    make_label(container, "Key Styles", category="SectionHeading", weight="Bold").pack(anchor="w", pady=(SPACING_SM, SPACING_XS))
    
    style_frame = make_frame(container)
    style_frame.pack(fill="x")
    
    for i, (style_name, exists) in enumerate(info["key_styles"].items()):
        col = i % 2
        row = i // 2
        status = "✓" if exists else "✗"
        category = "Success" if exists else "Error"
        make_label(style_frame, f"{status} {style_name}", category=category).grid(row=row, column=col, sticky="w", padx=(0, SPACING_LG), pady=SPACING_XS)


def build_tab_colours(parent: tk.Misc) -> None:
    """Build the Colour Palette tab."""
    container = ttk.Frame(parent, style="TFrame")
    container.pack(fill="both", expand=True, padx=SPACING_LG, pady=SPACING_LG)
    
    make_label(container, "Colour Palette", category="WindowHeading", weight="Bold").pack(anchor="w", pady=(0, SPACING_MD))
    make_label(container, "Design tokens from G01a_style_config", category="Body").pack(anchor="w", pady=(0, SPACING_MD))
    
    colours = get_colour_palette()
    
    # Create swatches
    swatch_frame = make_frame(container)
    swatch_frame.pack(fill="both", expand=True)
    
    for i, (name, colour) in enumerate(colours.items()):
        row = i // 3
        col = i % 3
        
        cell = make_frame(swatch_frame)
        cell.grid(row=row, column=col, sticky="nsew", padx=SPACING_SM, pady=SPACING_SM)
        
        # Colour swatch (using a frame with background)
        try:
            swatch = tk.Frame(cell, width=60, height=40, bg=colour, relief="solid", bd=1)
            swatch.pack(anchor="w")
            swatch.pack_propagate(False)
        except Exception:
            make_label(cell, "[Invalid]", category="Error").pack(anchor="w")
        
        # Short name
        short_name = name.replace("GUI_COLOUR_", "").replace("TEXT_COLOUR_", "T_").replace("BUTTON_", "BTN_")
        make_label(cell, short_name, category="Body", weight="Bold").pack(anchor="w")
        make_label(cell, colour, category="Body").pack(anchor="w")
    
    # Configure grid weights
    for i in range(3):
        swatch_frame.columnconfigure(i, weight=1)


def build_tab_widgets(parent: tk.Misc) -> None:
    """Build the Widget Gallery tab."""
    # Use a canvas with scrollbar for this tab
    canvas = tk.Canvas(parent, bg=GUI_COLOUR_BG_PRIMARY, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    
    container = ttk.Frame(canvas, style="TFrame")
    
    canvas.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    
    canvas_window = canvas.create_window((0, 0), window=container, anchor="nw")
    
    def configure_scroll(event: Any) -> None:
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(canvas_window, width=event.width)
    
    container.bind("<Configure>", configure_scroll)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
    
    # Content
    inner = ttk.Frame(container, style="TFrame")
    inner.pack(fill="both", expand=True, padx=SPACING_LG, pady=SPACING_LG)
    
    make_label(inner, "Widget Gallery", category="WindowHeading", weight="Bold").pack(anchor="w", pady=(0, SPACING_MD))
    
    # Labels section
    make_label(inner, "Labels", category="SectionHeading", weight="Bold").pack(anchor="w", pady=(SPACING_MD, SPACING_SM))
    make_label(inner, "Body text (Primary/Normal)", category="Body").pack(anchor="w")
    make_label(inner, "Body text Bold", category="Body", weight="Bold").pack(anchor="w")
    make_label(inner, "Success message", category="Success").pack(anchor="w")
    make_label(inner, "Warning message", category="Warning").pack(anchor="w")
    make_label(inner, "Error message", category="Error").pack(anchor="w")
    
    make_divider(inner).pack(fill="x", pady=SPACING_MD)
    
    # Buttons section
    make_label(inner, "Buttons", category="SectionHeading", weight="Bold").pack(anchor="w", pady=(0, SPACING_SM))
    btn_row = make_horizontal_group(inner)
    make_button(btn_row, "Primary").pack(side="left", padx=(0, SPACING_SM))
    make_button(btn_row, "Secondary", style="Secondary.TButton").pack(side="left", padx=(0, SPACING_SM))
    make_button(btn_row, "Success", style="Success.TButton").pack(side="left", padx=(0, SPACING_SM))
    make_button(btn_row, "Warning", style="Warning.TButton").pack(side="left", padx=(0, SPACING_SM))
    make_button(btn_row, "Danger", style="Danger.TButton").pack(side="left")
    btn_row.pack(anchor="w")
    
    make_divider(inner).pack(fill="x", pady=SPACING_MD)
    
    # Inputs section
    make_label(inner, "Inputs", category="SectionHeading", weight="Bold").pack(anchor="w", pady=(0, SPACING_SM))
    
    input_frame = make_frame(inner)
    input_frame.pack(fill="x")
    
    make_label(input_frame, "Entry:", category="Body").grid(row=0, column=0, sticky="e", padx=(0, SPACING_SM))
    make_entry(input_frame, width=30).grid(row=0, column=1, sticky="w", pady=SPACING_XS)
    
    make_label(input_frame, "Combobox:", category="Body").grid(row=1, column=0, sticky="e", padx=(0, SPACING_SM))
    make_combobox(input_frame, values=["Option A", "Option B", "Option C"], width=28).grid(row=1, column=1, sticky="w", pady=SPACING_XS)
    
    make_divider(inner).pack(fill="x", pady=SPACING_MD)
    
    # Choice widgets
    make_label(inner, "Choice Widgets", category="SectionHeading", weight="Bold").pack(anchor="w", pady=(0, SPACING_SM))
    
    chk_var = tk.BooleanVar(value=True)
    make_checkbox(inner, "Checkbox option", variable=chk_var).pack(anchor="w")
    
    radio_var = tk.StringVar(value="A")
    radio_row = make_horizontal_group(inner)
    make_radio(radio_row, "Radio A", variable=radio_var, value="A").pack(side="left", padx=(0, SPACING_MD))
    make_radio(radio_row, "Radio B", variable=radio_var, value="B").pack(side="left", padx=(0, SPACING_MD))
    make_radio(radio_row, "Radio C", variable=radio_var, value="C").pack(side="left")
    radio_row.pack(anchor="w", pady=SPACING_XS)
    
    switch_var = tk.BooleanVar(value=False)
    make_switch(inner, "Toggle switch", variable=switch_var).pack(anchor="w")


def build_tab_performance(parent: tk.Misc, style_obj: ttk.Style) -> None:
    """Build the Performance tab."""
    container = ttk.Frame(parent, style="TFrame")
    container.pack(fill="both", expand=True, padx=SPACING_LG, pady=SPACING_LG)
    
    make_label(container, "Performance Metrics", category="WindowHeading", weight="Bold").pack(anchor="w", pady=(0, SPACING_MD))
    
    results_frame = make_frame(container)
    results_frame.pack(fill="x", pady=(0, SPACING_LG))
    
    results_text = make_textarea(container, height=15)
    results_text.pack(fill="both", expand=True)
    
    def run_benchmarks() -> None:
        results_text.delete("1.0", "end")
        results_text.insert("end", "Running benchmarks...\n\n")
        results_text.update()
        
        benchmarks: List[TimingResult] = []
        
        # Benchmark: Create 100 labels
        test_frame = ttk.Frame(container)
        def create_labels():
            for i in range(100):
                lbl = make_label(test_frame, f"Label {i}", category="Body")
        benchmarks.append(time_operation("Create 100 labels", create_labels))
        test_frame.destroy()
        
        # Benchmark: Create 50 buttons
        test_frame = ttk.Frame(container)
        def create_buttons():
            for i in range(50):
                btn = make_button(test_frame, f"Button {i}")
        benchmarks.append(time_operation("Create 50 buttons", create_buttons))
        test_frame.destroy()
        
        # Benchmark: Create 50 entries
        test_frame = ttk.Frame(container)
        def create_entries():
            for i in range(50):
                ent = make_entry(test_frame)
        benchmarks.append(time_operation("Create 50 entries", create_entries))
        test_frame.destroy()
        
        # Benchmark: Style lookup
        def style_lookups():
            for _ in range(100):
                style_obj.lookup("TLabel", "font")
                style_obj.lookup("TButton", "background")
        benchmarks.append(time_operation("100 style lookups", style_lookups))
        
        # Display results
        results_text.delete("1.0", "end")
        results_text.insert("end", "Benchmark Results\n")
        results_text.insert("end", "=" * 50 + "\n\n")
        
        for result in benchmarks:
            status = "✓" if result.success else "✗"
            if result.success:
                results_text.insert("end", f"{status} {result.name}: {result.duration_ms:.2f} ms\n")
            else:
                results_text.insert("end", f"{status} {result.name}: FAILED - {result.error}\n")
        
        total = sum(r.duration_ms for r in benchmarks if r.success)
        results_text.insert("end", f"\nTotal: {total:.2f} ms\n")
    
    btn_frame = make_horizontal_group(container)
    make_button(btn_frame, "Run Benchmarks", command=run_benchmarks).pack(side="left")
    btn_frame.pack(anchor="w", pady=(SPACING_MD, 0))


def build_tab_logs(parent: tk.Misc) -> None:
    """Build the Log Viewer tab."""
    container = ttk.Frame(parent, style="TFrame")
    container.pack(fill="both", expand=True, padx=SPACING_LG, pady=SPACING_LG)
    
    make_label(container, "Log Viewer", category="WindowHeading", weight="Bold").pack(anchor="w", pady=(0, SPACING_MD))
    make_label(container, "Real-time log output from the application", category="Body").pack(anchor="w", pady=(0, SPACING_SM))
    
    # Log text widget
    log_text = scrolledtext.ScrolledText(
        container,
        height=20,
        font=("Consolas", 9),
        bg=GUI_COLOUR_BG_TEXTAREA,
        state="disabled",
    )
    log_text.pack(fill="both", expand=True, pady=(0, SPACING_SM))
    
    # Add handler to root logger
    handler = TextHandler(log_text)
    handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(handler)
    
    # Control buttons
    btn_frame = make_horizontal_group(container)
    
    def clear_logs():
        log_text.configure(state="normal")
        log_text.delete("1.0", "end")
        log_text.configure(state="disabled")
    
    def test_log():
        logger.info("Test INFO message from debug console")
        logger.warning("Test WARNING message")
        logger.error("Test ERROR message")
    
    make_button(btn_frame, "Clear", command=clear_logs, style="Secondary.TButton").pack(side="left", padx=(0, SPACING_SM))
    make_button(btn_frame, "Test Log", command=test_log).pack(side="left")
    btn_frame.pack(anchor="w")


# ====================================================================================================
# 7. MAIN DEBUG CONSOLE
# ====================================================================================================
def run_debug_console() -> None:
    """Entry point: build and run the enhanced debug console."""
    init_logging()
    logger.info("=== G02d Debug Console v2 — Starting ===")
    
    # Window setup
    try:
        root = Window(themename="flatly")
        style_obj = Style()
        logger.info("[G02d] Using ttkbootstrap")
    except Exception:
        root = tk.Tk()
        style_obj = ttk.Style()
        logger.info("[G02d] Using standard Tk/ttk")
    
    root.title("G02d Debug Console v2")
    root.geometry(f"{FRAME_SIZE_H + 100}x{FRAME_SIZE_V + 50}")
    root.configure(bg=GUI_COLOUR_BG_PRIMARY)
    
    configure_ttk_styles(style_obj)
    
    # Notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=SPACING_MD, pady=SPACING_MD)
    
    # Create tabs
    tabs = [
        ("System Info", lambda p: build_tab_system_info(p)),
        ("Imports", lambda p: build_tab_imports(p)),
        ("Styles", lambda p: build_tab_styles(p, style_obj)),
        ("Colours", lambda p: build_tab_colours(p)),
        ("Widgets", lambda p: build_tab_widgets(p)),
        ("Performance", lambda p: build_tab_performance(p, style_obj)),
        ("Logs", lambda p: build_tab_logs(p)),
    ]
    
    for name, builder in tabs:
        tab = ttk.Frame(notebook, style="TFrame")
        notebook.add(tab, text=name)
        builder(tab)
    
    logger.info("=== G02d Debug Console v2 — Ready ===")
    root.mainloop()
    logger.info("=== G02d Debug Console v2 — Closed ===")


# ====================================================================================================
# 8. MAIN GUARD
# ====================================================================================================
if __name__ == "__main__":
    run_debug_console()