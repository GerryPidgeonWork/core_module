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
# Core Imports
from gui.G00a_gui_packages import tk, ttk
from gui.G01a_style_config import *
from gui.G02c_gui_base import BaseWindow
from gui.G02a_widget_primitives import *
from gui.G02b_layout_utils import *

# Pattern Imports
from gui.G03a_layout_patterns import *
from gui.G03b_container_patterns import *
from gui.G03c_form_patterns import *
from gui.G03d_table_patterns import *
from gui.G03e_widget_components import *


class VisualTestWindow(BaseWindow):
    def build_widgets(self) -> None:
        # 1. Setup Main Page Layout
        # ----------------------------------------------------------------
        page = page_layout(self.main_frame, padding=SPACING_LG)
        page.pack(fill="both", expand=True)

        header, actions = action_header(
            page,
            title="SP1 — Framework Visual Test",
            actions=[("Run Tests", None), ("Export Report", None)],
        )
        header.pack(fill="x", pady=(0, SPACING_LG))

        # 2. Typography & Primitives
        # ----------------------------------------------------------------
        self.add_section_header(page, "1. Typography & Primitives")

        typo_card = card(page, role="SECONDARY")
        typo_card.pack(fill="x", pady=(0, SPACING_MD))

        stack_vertical(
            typo_card,
            [
                page_title(typo_card, text="Display Text (Page Title)"),
                section_title(
                    typo_card, text="Heading Text (Section Title)"
                ),
                body_text(
                    typo_card,
                    text=(
                        "Body text: The quick brown fox jumps over the lazy dog."
                    ),
                ),
                small_text(
                    typo_card,
                    text=(
                        "Small text: Used for captions and secondary information."
                    ),
                ),
                meta_text(
                    typo_card,
                    text="Meta text: ID #12345 • Updated 2m ago",
                ),
            ],
            spacing=SPACING_SM,
        )

        # 3. Interactive Controls
        # ----------------------------------------------------------------
        self.add_section_header(page, "2. Interactive Controls")

        control_panel = panel(page, role="SECONDARY")
        control_panel.pack(fill="x", pady=(0, SPACING_MD))

        # Button Variants
        section_title(control_panel, text="Button Variants").pack(
            anchor="w", pady=(0, SPACING_SM)
        )

        btn_row = button_row(control_panel, alignment="left", padding=0)
        btn_row.pack(fill="x", pady=(0, SPACING_MD))

        variants = ["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "DANGER"]
        for variant in variants:
            make_button(
                btn_row,
                text=variant,
                variant=variant,
            ).pack(side="left", padx=(0, SPACING_SM))

        divider(control_panel).pack(fill="x", pady=SPACING_MD)

        # Toggles (Checkboxes / Radios / Switches)
        toggle_row = layout_row(control_panel, weights=(1, 1, 1))
        toggle_row.pack(fill="x")

        # Col 1: Checkboxes
        col1 = ttk.Frame(toggle_row)
        col1.grid(row=0, column=0, sticky="w")
        make_label(col1, text="Checkboxes", bold=True).pack(anchor="w")
        make_checkbox(col1, text="Primary Option", variant="PRIMARY").pack(anchor="w")
        make_checkbox(col1, text="Success Option", variant="SUCCESS").pack(anchor="w")

        # Col 2: Radios
        col2 = ttk.Frame(toggle_row)
        col2.grid(row=0, column=1, sticky="w")
        make_label(col2, text="Radio Buttons", bold=True).pack(anchor="w")
        make_radio(col2, text="Option A", value="A", variant="PRIMARY").pack(anchor="w")
        make_radio(col2, text="Option B", value="B", variant="WARNING").pack(anchor="w")

        # Col 3: Switches
        col3 = ttk.Frame(toggle_row)
        col3.grid(row=0, column=2, sticky="w")
        make_label(col3, text="Switches", bold=True).pack(anchor="w")
        make_checkbox(col3, text="Toggle Feature", variant="PRIMARY").pack(anchor="w")

        # 4. Containers & Alerts
        # ----------------------------------------------------------------
        self.add_section_header(page, "3. Containers & Alerts")

        alert_row = layout_row(page, weights=(1, 1))
        alert_row.pack(fill="x", pady=(0, SPACING_MD))

        # Alerts
        c_left = ttk.Frame(alert_row)
        c_left.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING_MD))

        stack_vertical(
            c_left,
            [
                alert_box(c_left, "Information note.", role="SECONDARY"),
                alert_box(c_left, "Operation successful!", role="SUCCESS"),
                alert_box(c_left, "Warning: Disk space low.", role="WARNING"),
                alert_box(c_left, "Critical System Failure.", role="ERROR"),
            ],
            spacing=SPACING_XS,
        )

        # Surfaces
        c_right = ttk.Frame(alert_row)
        c_right.grid(row=0, column=1, sticky="nsew")

        surf = surface(c_right, role="SECONDARY", shade="MID")
        surf.pack(fill="both", expand=True)
        make_label(
            surf,
            text="Surface Container (No Border)",
        ).pack()
        make_label(
            surf,
            text="Used for backgrounds.",
        ).pack()

        # 5. Form Patterns
        # ----------------------------------------------------------------
        self.add_section_header(page, "4. Form Patterns")

        form_frame, form_content = titled_section(
            page,
            title="User Registration",
        )
        form_frame.pack(fill="x", pady=(0, SPACING_MD))

        fields = [
            FormField(
                name="username",
                label="Username",
                required=True,
            ),
            FormField(
                name="role",
                label="Role",
                field_type="combobox",
                options=["Admin", "User", "Guest"],
            ),
            FormField(
                name="age",
                label="Age",
                field_type="spinbox",
                options={"from_": 18, "to": 99},
            ),
            FormField(
                name="newsletter",
                label="Subscribe",
                field_type="checkbox",
                default=True,
            ),
        ]

        form_result = form_group(form_content, fields=fields)
        form_result.frame.pack(fill="x")

        form_btn_row, _ = form_button_row(
            form_content,
            [("Save", None), ("Cancel", None)],
        )
        form_btn_row.pack(fill="x", pady=(SPACING_MD, 0))

        # 6. Metrics & Components
        # ----------------------------------------------------------------
        self.add_section_header(page, "5. Composite Components")

        # Metric Row
        metrics = [
            {"title": "Active Users", "value": "14.2k", "role": "PRIMARY"},
            {"title": "Revenue", "value": "$1.2M", "role": "SUCCESS"},
            {"title": "Server Load", "value": "98%", "role": "ERROR"},
        ]
        metric_row_frame, _ = metric_row(page, metrics)
        metric_row_frame.pack(fill="x", pady=(0, SPACING_MD))

        # Filter Bar
        filters = [
            {"name": "search", "label": "Search", "width": 25},
            {
                "name": "status",
                "label": "Status",
                "type": "combobox",
                "options": ["All", "Active"],
            },
        ]
        filter_bar_result = filter_bar(page, filters=filters)
        filter_bar_result.frame.pack(fill="x", pady=(0, SPACING_MD))

        # Empty State
        empty_frame = section(page, role="SECONDARY")
        empty_frame.pack(fill="x")
        empty_state(
            empty_frame,
            title="No Results Found",
            message="Try adjusting filters.",
        ).pack()

        # 7. Tables
        # ----------------------------------------------------------------
        self.add_section_header(page, "6. Data Tables")

        cols = [
            TableColumn("id", "ID", width=50, anchor="center"),
            TableColumn("name", "Name", width=150),
            TableColumn("role", "Role", width=100),
            TableColumn("status", "Status", width=100, anchor="center"),
        ]

        table_outer, table_toolbar, table_result = create_table_with_toolbar(
            page,
            columns=cols,
            height=6,
        )
        table_outer.pack(fill="x", pady=(0, SPACING_XXL))  # Extra padding at bottom

        # Populate Toolbar
        make_button(
            table_toolbar,
            text="Export CSV",
            variant="SECONDARY",
        ).pack(side="right")
        make_label(
            table_toolbar,
            text="System Users",
        ).pack(side="left")

        # Populate Table
        data = [
            (101, "Alice Johnson", "Admin", "Active"),
            (102, "Bob Smith", "Editor", "Inactive"),
            (103, "Charlie Davis", "Viewer", "Active"),
            (104, "Dana Lee", "Admin", "Active"),
            (105, "Evan Wright", "Editor", "Pending"),
        ]
        insert_rows_zebra(table_result.treeview, data)

    def add_section_header(self, parent: ttk.Widget, text: str) -> None:
        """Helper to create consistent section dividers."""
        container = ttk.Frame(parent)
        container.pack(fill="x", pady=(SPACING_LG, SPACING_SM))
        section_title(container, text).pack(anchor="w")
        divider(container).pack(fill="x", pady=(SPACING_XS, 0))


if __name__ == "__main__":
    init_logging()
    logger.info("Launching SP1 VisualTestWindow (G00–G03 harness)")
    app = VisualTestWindow(width=900, height=900)
    app.center_window()
    app.run()
