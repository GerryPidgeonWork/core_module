# ====================================================================================================
# G99_demo_script.py
# ----------------------------------------------------------------------------------------------------
# Comprehensive visual test harness for the GUI Framework.
#
# Purpose:
#   - Provide a single window that exercises ALL layers from G00 to G03.
#   - Demonstrate typography, primitives, controls, containers, forms,
#     composite components, and data tables.
#   - Serve as a developer-facing "Design System Explorer" to validate
#     spacing, style resolution, layout behaviour, and interactive states.
#   - Act as a regression-testing tool during framework evolution.
#
# IMPORTANT:
#   This module is a *demo and diagnostic script only*. It must not:
#       - contain production logic,
#       - create new styles,
#       - define widget factories,
#       - define layout utilities,
#       - or be imported by application pages (G30+).
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-03
# Updated:      2025-12-07 - Added comprehensive demo sections
# Project:      GUI Framework v1.0 - G99 Developer Tools
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
from __future__ import annotations
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
if "" in sys.path:
    sys.path.remove("")
sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *
from core.C03_logging_handler import get_logger, log_exception, init_logging

logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------

# Foundation (G00)
from gui.G00a_gui_packages import tk, ttk

# Base window (G02c)
from gui.G02c_gui_base import BaseWindow

# Widget primitives, spacing tokens, and type aliases from G02a (the facade)
from gui.G02a_widget_primitives import (
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL, SPACING_XXL,
    ControlVariantType, ShadeType, ContainerRoleType,
    CONTROL_VARIANTS,
    entry_style, entry_style_default, entry_style_error, entry_style_success,
    label_style,
    make_label, make_button, make_checkbox, make_radio, make_frame,
    make_entry, make_combobox, make_spinbox, make_separator, make_spacer,
    page_title, section_title, body_text, small_text, meta_text, divider,
)

# Layout utilities from G02b
from gui.G02b_layout_utils import (
    layout_row, layout_col, grid_configure,
    stack_vertical, stack_horizontal, fill_remaining,
)

# Layout patterns from G03a
from gui.G03a_layout_patterns import page_layout

# Container patterns from G03b
from gui.G03b_container_patterns import (
    card, panel, section, surface, titled_section, alert_box,
)

# Form patterns from G03c
from gui.G03c_form_patterns import FormField, form_group, form_button_row

# Table patterns from G03d
from gui.G03d_table_patterns import TableColumn, create_table_with_toolbar, insert_rows_zebra

# Composite components from G03e
from gui.G03e_widget_components import filter_bar, metric_row, action_header, empty_state

# Cache info functions (for diagnostics panel)
from gui.G01c_text_styles import get_text_style_cache_info
from gui.G01d_container_styles import get_container_style_cache_info
from gui.G01e_input_styles import get_input_style_cache_info
from gui.G01f_control_styles import get_control_style_cache_info
from gui.G01b_style_base import get_font_cache_info

# Color families for palette display (direct G01a import for demo purposes only)
from gui.G01a_style_config import (
    GUI_PRIMARY, GUI_SECONDARY, GUI_SUCCESS, GUI_WARNING, GUI_ERROR, GUI_TEXT,
)


# ====================================================================================================
# 3. VISUAL TEST WINDOW
# ----------------------------------------------------------------------------------------------------
class VisualTestWindow(BaseWindow):
    """Comprehensive visual test harness demonstrating all GUI Framework capabilities."""

    def build_widgets(self) -> None:
        """Build all demo sections."""
        page = page_layout(self.main_frame, padding=SPACING_LG)
        page.pack(fill="both", expand=True)

        header, actions = action_header(
            page,
            title="GUI Framework - Design System Explorer",
            actions=[("Refresh Cache Info", self.refresh_cache_info)],
        )
        header.pack(fill="x", pady=(0, SPACING_LG))

        self.build_color_palette_section(page)
        self.build_typography_section(page)
        self.build_interactive_controls_section(page)
        self.build_disabled_states_section(page)
        self.build_input_validation_section(page)
        self.build_containers_alerts_section(page)
        self.build_form_patterns_section(page)
        self.build_metrics_components_section(page)
        self.build_tables_section(page)
        self.build_cache_diagnostics_section(page)

        make_spacer(page, height=SPACING_XXL).pack()

    def build_color_palette_section(self, page: ttk.Frame) -> None:
        """Display all color families with their shades."""
        self.add_section_header(page, "1. Color Palette")
        palette_card = card(page, role="SECONDARY")
        palette_card.pack(fill="x", pady=(0, SPACING_MD))

        body_text(palette_card, text="All color families with LIGHT to XDARK shades:").pack(
            anchor="w", pady=(0, SPACING_SM)
        )

        color_families = [
            ("PRIMARY", GUI_PRIMARY), ("SECONDARY", GUI_SECONDARY),
            ("SUCCESS", GUI_SUCCESS), ("WARNING", GUI_WARNING), ("ERROR", GUI_ERROR),
        ]
        shades = ["LIGHT", "MID", "DARK", "XDARK"]

        for family_name, family_dict in color_families:
            row = ttk.Frame(palette_card)
            row.pack(fill="x", pady=SPACING_XS)
            make_label(row, text=f"{family_name}:", bold=True, size="BODY").pack(side="left", padx=(0, SPACING_SM))

            for shade in shades:
                hex_color = family_dict.get(shade, "#CCCCCC")
                swatch = tk.Frame(row, bg=hex_color, width=60, height=24)
                swatch.pack(side="left", padx=2)
                swatch.pack_propagate(False)
                fg = "#000000" if shade in ["LIGHT", "MID"] else "#FFFFFF"
                tk.Label(swatch, text=shade[:1], bg=hex_color, fg=fg, font=("Arial", 8)).place(relx=0.5, rely=0.5, anchor="center")

        divider(palette_card).pack(fill="x", pady=SPACING_SM)
        small_text(palette_card, text="TEXT family:").pack(anchor="w")
        text_row = ttk.Frame(palette_card)
        text_row.pack(fill="x", pady=SPACING_XS)

        for shade_name, hex_color in GUI_TEXT.items():
            swatch = tk.Frame(text_row, bg=hex_color, width=60, height=24)
            swatch.pack(side="left", padx=2)
            swatch.pack_propagate(False)
            contrast = "#FFFFFF" if shade_name in ["BLACK", "GREY"] else "#000000"
            tk.Label(swatch, text=shade_name[:3], bg=hex_color, fg=contrast, font=("Arial", 7)).place(relx=0.5, rely=0.5, anchor="center")

    def build_typography_section(self, page: ttk.Frame) -> None:
        """Display typography scale and styles."""
        self.add_section_header(page, "2. Typography and Text Styles")
        typo_card = card(page, role="SECONDARY")
        typo_card.pack(fill="x", pady=(0, SPACING_MD))

        stack_vertical(typo_card, [
            page_title(typo_card, text="Display Text (Page Title) - 20px Bold"),
            section_title(typo_card, text="Heading Text (Section Title) - 16px Bold"),
            body_text(typo_card, text="Body text: The quick brown fox jumps over the lazy dog. - 11px"),
            small_text(typo_card, text="Small text: Used for captions and secondary information. - 10px"),
            meta_text(typo_card, text="Meta text: ID #12345 - Updated 2m ago - 10px Grey"),
        ], spacing=SPACING_SM)

        divider(typo_card).pack(fill="x", pady=SPACING_SM)
        small_text(typo_card, text="Semantic text colors:").pack(anchor="w", pady=(0, SPACING_XS))
        styled_row = ttk.Frame(typo_card)
        styled_row.pack(fill="x")

        make_label(styled_row, text="Success Text", fg_colour=GUI_SUCCESS, fg_shade="DARK").pack(side="left", padx=SPACING_SM)
        make_label(styled_row, text="Warning Text", fg_colour=GUI_WARNING, fg_shade="DARK").pack(side="left", padx=SPACING_SM)
        make_label(styled_row, text="Error Text", fg_colour=GUI_ERROR, fg_shade="DARK").pack(side="left", padx=SPACING_SM)
        make_label(styled_row, text="Primary Text", fg_colour=GUI_PRIMARY, fg_shade="DARK").pack(side="left", padx=SPACING_SM)

    def build_interactive_controls_section(self, page: ttk.Frame) -> None:
        """Display buttons, checkboxes, radios in all variants."""
        self.add_section_header(page, "3. Interactive Controls")
        control_panel = panel(page, role="SECONDARY")
        control_panel.pack(fill="x", pady=(0, SPACING_MD))

        section_title(control_panel, text="Button Variants").pack(anchor="w", pady=(0, SPACING_SM))
        btn_row = ttk.Frame(control_panel)
        btn_row.pack(fill="x", pady=(0, SPACING_MD))

        for variant in CONTROL_VARIANTS:
            make_button(btn_row, text=variant, variant=variant).pack(side="left", padx=(0, SPACING_SM))

        divider(control_panel).pack(fill="x", pady=SPACING_MD)

        toggle_row = layout_row(control_panel, weights=(1, 1, 1))
        toggle_row.pack(fill="x")

        col1 = ttk.Frame(toggle_row)
        col1.grid(row=0, column=0, sticky="nw")
        make_label(col1, text="Checkboxes", bold=True).pack(anchor="w")
        chk1_var, chk2_var = tk.BooleanVar(value=True), tk.BooleanVar(value=False)
        make_checkbox(col1, text="Primary (checked)", variant="PRIMARY", variable=chk1_var).pack(anchor="w")
        make_checkbox(col1, text="Success (unchecked)", variant="SUCCESS", variable=chk2_var).pack(anchor="w")

        col2 = ttk.Frame(toggle_row)
        col2.grid(row=0, column=1, sticky="nw")
        make_label(col2, text="Radio Buttons", bold=True).pack(anchor="w")
        radio_var = tk.StringVar(value="A")
        make_radio(col2, text="Option A", value="A", variant="PRIMARY", variable=radio_var).pack(anchor="w")
        make_radio(col2, text="Option B", value="B", variant="WARNING", variable=radio_var).pack(anchor="w")

        col3 = ttk.Frame(toggle_row)
        col3.grid(row=0, column=2, sticky="nw")
        make_label(col3, text="More Controls", bold=True).pack(anchor="w")
        chk3_var = tk.BooleanVar(value=True)
        make_checkbox(col3, text="Toggle Feature", variant="PRIMARY", variable=chk3_var).pack(anchor="w")

    def build_disabled_states_section(self, page: ttk.Frame) -> None:
        """Demonstrate disabled widget states."""
        self.add_section_header(page, "4. Disabled States")
        disabled_card = card(page, role="SECONDARY")
        disabled_card.pack(fill="x", pady=(0, SPACING_MD))

        body_text(disabled_card, text="All controls support disabled state:").pack(anchor="w", pady=(0, SPACING_SM))

        btn_row = ttk.Frame(disabled_card)
        btn_row.pack(fill="x", pady=(0, SPACING_SM))
        for variant in CONTROL_VARIANTS[:3]:  # PRIMARY, SECONDARY, SUCCESS
            btn = make_button(btn_row, text=f"{variant} (disabled)", variant=variant)
            btn.configure(state="disabled")
            btn.pack(side="left", padx=(0, SPACING_SM))

        input_row = ttk.Frame(disabled_card)
        input_row.pack(fill="x", pady=(0, SPACING_SM))
        make_label(input_row, text="Entry:").pack(side="left", padx=(0, SPACING_XS))
        disabled_entry = make_entry(input_row, width=20)
        disabled_entry.insert(0, "Disabled entry")
        disabled_entry.configure(state="disabled")
        disabled_entry.pack(side="left", padx=(0, SPACING_MD))

        make_label(input_row, text="Combobox:").pack(side="left", padx=(0, SPACING_XS))
        disabled_combo = make_combobox(input_row, values=["Option 1", "Option 2"], width=15)
        disabled_combo.set("Disabled")
        disabled_combo.configure(state="disabled")
        disabled_combo.pack(side="left")

        toggle_row = ttk.Frame(disabled_card)
        toggle_row.pack(fill="x")
        chk_dis = make_checkbox(toggle_row, text="Disabled checkbox", variant="PRIMARY")
        chk_dis.configure(state="disabled")
        chk_dis.pack(side="left", padx=(0, SPACING_MD))
        radio_dis = make_radio(toggle_row, text="Disabled radio", value="X", variant="PRIMARY")
        radio_dis.configure(state="disabled")
        radio_dis.pack(side="left")

    def build_input_validation_section(self, page: ttk.Frame) -> None:
        """Demonstrate input validation visual states."""
        self.add_section_header(page, "5. Input Validation States")
        validation_card = card(page, role="SECONDARY")
        validation_card.pack(fill="x", pady=(0, SPACING_MD))

        body_text(validation_card, text="Entry fields with validation styling:").pack(anchor="w", pady=(0, SPACING_SM))

        input_row = layout_row(validation_card, weights=(1, 1, 1))
        input_row.pack(fill="x")

        col1 = ttk.Frame(input_row)
        col1.grid(row=0, column=0, sticky="nw", padx=(0, SPACING_MD))
        make_label(col1, text="Default:", bold=True).pack(anchor="w")
        default_entry = make_entry(col1, width=20)
        default_entry.insert(0, "Normal input")
        default_entry.pack(anchor="w", pady=SPACING_XS)

        col2 = ttk.Frame(input_row)
        col2.grid(row=0, column=1, sticky="nw", padx=(0, SPACING_MD))
        make_label(col2, text="Success:", bold=True, fg_colour=GUI_SUCCESS, fg_shade="DARK").pack(anchor="w")
        success_entry = ttk.Entry(col2, width=20, style=entry_style_success())
        success_entry.insert(0, "Valid input")
        success_entry.pack(anchor="w", pady=SPACING_XS)

        col3 = ttk.Frame(input_row)
        col3.grid(row=0, column=2, sticky="nw")
        make_label(col3, text="Error:", bold=True, fg_colour=GUI_ERROR, fg_shade="DARK").pack(anchor="w")
        error_entry = ttk.Entry(col3, width=20, style=entry_style_error())
        error_entry.insert(0, "Invalid input")
        error_entry.pack(anchor="w", pady=SPACING_XS)

    def build_containers_alerts_section(self, page: ttk.Frame) -> None:
        """Display container types and alert boxes."""
        self.add_section_header(page, "6. Containers and Alerts")
        container_row = layout_row(page, weights=(1, 1))
        container_row.pack(fill="x", pady=(0, SPACING_MD))

        c_left = ttk.Frame(container_row)
        c_left.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING_MD))
        small_text(c_left, text="Alert boxes by role:").pack(anchor="w", pady=(0, SPACING_XS))
        stack_vertical(c_left, [
            alert_box(c_left, "Information: Neutral message.", role="SECONDARY"),
            alert_box(c_left, "Success: Operation completed!", role="SUCCESS"),
            alert_box(c_left, "Warning: Disk space running low.", role="WARNING"),
            alert_box(c_left, "Error: Critical system failure!", role="ERROR"),
        ], spacing=SPACING_XS)

        c_right = ttk.Frame(container_row)
        c_right.grid(row=0, column=1, sticky="nsew")
        small_text(c_right, text="Container types:").pack(anchor="w", pady=(0, SPACING_XS))

        surf = surface(c_right, role="SECONDARY", shade="MID")
        surf.pack(fill="x", pady=SPACING_XS)
        make_label(surf, text="Surface (no border)", size="SMALL").pack(padx=SPACING_SM, pady=SPACING_XS)

        crd = card(c_right, role="SECONDARY", shade="LIGHT")
        crd.pack(fill="x", pady=SPACING_XS)
        make_label(crd, text="Card (raised)", size="SMALL").pack(padx=SPACING_SM, pady=SPACING_XS)

        pnl = panel(c_right, role="PRIMARY", shade="LIGHT")
        pnl.pack(fill="x", pady=SPACING_XS)
        make_label(pnl, text="Panel (bordered)", size="SMALL").pack(padx=SPACING_SM, pady=SPACING_XS)

    def build_form_patterns_section(self, page: ttk.Frame) -> None:
        """Demonstrate form building patterns."""
        self.add_section_header(page, "7. Form Patterns")
        form_frame, form_content = titled_section(page, title="User Registration Form")
        form_frame.pack(fill="x", pady=(0, SPACING_MD))

        fields = [
            FormField(name="username", label="Username", required=True),
            FormField(name="email", label="Email Address", required=True),
            FormField(name="role", label="Role", field_type="combobox", options=["Admin", "Editor", "Viewer", "Guest"]),
            FormField(name="age", label="Age", field_type="spinbox", options={"from_": 18, "to": 99}),
            FormField(name="newsletter", label="Subscribe to newsletter", field_type="checkbox", default=True),
        ]
        form_result = form_group(form_content, fields=fields)
        form_result.frame.pack(fill="x")

        form_btn_row, _ = form_button_row(form_content, [("Submit", None), ("Reset", None), ("Cancel", None)])
        form_btn_row.pack(fill="x", pady=(SPACING_MD, 0))

    def build_metrics_components_section(self, page: ttk.Frame) -> None:
        """Display composite metric cards and filter bar."""
        self.add_section_header(page, "8. Composite Components")

        metrics = [
            {"title": "Active Users", "value": "14,256", "role": "PRIMARY"},
            {"title": "Revenue (MTD)", "value": "$1.2M", "role": "SUCCESS"},
            {"title": "Server Load", "value": "98%", "role": "ERROR"},
            {"title": "Open Tickets", "value": "47", "role": "WARNING"},
        ]
        metric_row_frame, _ = metric_row(page, metrics)
        metric_row_frame.pack(fill="x", pady=(0, SPACING_MD))

        filters = [
            {"name": "search", "label": "Search", "width": 25},
            {"name": "status", "label": "Status", "type": "combobox", "options": ["All", "Active", "Inactive"]},
            {"name": "role", "label": "Role", "type": "combobox", "options": ["All", "Admin", "User"]},
        ]
        filter_bar_result = filter_bar(page, filters=filters)
        filter_bar_result.frame.pack(fill="x", pady=(0, SPACING_MD))

        empty_frame = section(page, role="SECONDARY")
        empty_frame.pack(fill="x", pady=(0, SPACING_MD))
        empty_state(empty_frame, title="No Results Found", message="Try adjusting your search criteria or filters.").pack()

    def build_tables_section(self, page: ttk.Frame) -> None:
        """Display zebra-striped data table with toolbar."""
        self.add_section_header(page, "9. Data Tables")

        cols = [
            TableColumn("id", "ID", width=60, anchor="center"),
            TableColumn("name", "Full Name", width=180),
            TableColumn("email", "Email Address", width=200),
            TableColumn("role", "Role", width=100),
            TableColumn("status", "Status", width=80, anchor="center"),
        ]

        table_outer, table_toolbar, table_result = create_table_with_toolbar(page, columns=cols, height=8)
        table_outer.pack(fill="x", pady=(0, SPACING_MD))

        make_label(table_toolbar, text="System Users", bold=True).pack(side="left")
        make_button(table_toolbar, text="Add User", variant="PRIMARY").pack(side="right", padx=(SPACING_SM, 0))
        make_button(table_toolbar, text="Export CSV", variant="SECONDARY").pack(side="right")

        data = [
            (1001, "Alice Johnson", "alice@example.com", "Admin", "Active"),
            (1002, "Bob Smith", "bob@example.com", "Editor", "Active"),
            (1003, "Charlie Davis", "charlie@example.com", "Viewer", "Inactive"),
            (1004, "Dana Lee", "dana@example.com", "Admin", "Active"),
            (1005, "Evan Wright", "evan@example.com", "Editor", "Pending"),
            (1006, "Fiona Green", "fiona@example.com", "Viewer", "Active"),
            (1007, "George Hall", "george@example.com", "Editor", "Active"),
            (1008, "Hannah King", "hannah@example.com", "Viewer", "Inactive"),
        ]
        insert_rows_zebra(table_result.treeview, data)

    def build_cache_diagnostics_section(self, page: ttk.Frame) -> None:
        """Display style cache statistics."""
        self.add_section_header(page, "10. Style Cache Diagnostics")

        self.cache_card = card(page, role="SECONDARY")
        self.cache_card.pack(fill="x", pady=(0, SPACING_MD))

        body_text(self.cache_card, text="Live cache statistics (click 'Refresh Cache Info' to update):").pack(
            anchor="w", pady=(0, SPACING_SM)
        )

        self.cache_stats_frame = ttk.Frame(self.cache_card)
        self.cache_stats_frame.pack(fill="x")
        self.refresh_cache_info()

    def refresh_cache_info(self) -> None:
        """Update cache statistics display."""
        for widget in self.cache_stats_frame.winfo_children():
            widget.destroy()

        caches = [
            ("Font Cache", get_font_cache_info()),
            ("Text Styles", get_text_style_cache_info()),
            ("Container Styles", get_container_style_cache_info()),
            ("Input Styles", get_input_style_cache_info()),
            ("Control Styles", get_control_style_cache_info()),
        ]

        stats_row = layout_row(self.cache_stats_frame, weights=(1, 1, 1, 1, 1))
        stats_row.pack(fill="x")

        for idx, (name, info) in enumerate(caches):
            col = ttk.Frame(stats_row)
            col.grid(row=0, column=idx, sticky="nw", padx=SPACING_XS)
            count = info.get("count", len(info.get("keys", [])))
            make_label(col, text=name, bold=True, size="SMALL").pack(anchor="w")
            make_label(col, text=f"{count} styles", size="SMALL").pack(anchor="w")

        total = sum(info.get("count", len(info.get("keys", []))) for _, info in caches)
        divider(self.cache_stats_frame).pack(fill="x", pady=SPACING_XS)
        make_label(self.cache_stats_frame, text=f"Total cached styles: {total}", bold=True).pack(anchor="w")
        logger.info("[G99] Cache info refreshed. Total styles: %d", total)

    def add_section_header(self, parent: ttk.Frame, text: str) -> None:
        """Create consistent section dividers."""
        container = ttk.Frame(parent)
        container.pack(fill="x", pady=(SPACING_LG, SPACING_SM))
        section_title(container, text).pack(anchor="w")
        divider(container).pack(fill="x", pady=(SPACING_XS, 0))


# ====================================================================================================
# 4. MAIN ENTRY POINT
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging()
    logger.info("=" * 60)
    logger.info("GUI Framework - Design System Explorer")
    logger.info("=" * 60)
    logger.info("Launching comprehensive visual test harness...")

    app = VisualTestWindow(
        title="GUI Framework - Design System Explorer",
        width=1000,
        height=900,
    )
    app.center_window()
    app.run()