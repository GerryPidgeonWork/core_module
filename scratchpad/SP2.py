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
from gui.G00a_gui_packages import tk, ttk
from gui.G01a_style_config import (
    FRAME_PADDING,
    FRAME_SIZE_H,
    FRAME_SIZE_V,
)
from gui.G01b_style_engine import configure_ttk_styles
from gui.G01c_widget_primitives import (
    UIPrimitives,
    make_label,
    make_button,
    make_spacer,
    make_divider,
)
from gui.G01d_layout_primitives import (
    heading,
    subheading,
    body_text,
    spacer,
    divider,
)
from gui.G01e_gui_base import BaseGUI
from gui.G02b_container_patterns import (
    create_section_grid,
    create_card_grid,
    create_two_column_body,
)
from gui.G02e_widget_components import ButtonRow


# ====================================================================================================
# 3. CONSTANTS
# ----------------------------------------------------------------------------------------------------
PAGE_HEADING = "Connection Launcher — Sandbox"
PAGE_SUBHEADING = "Developer-only layout sandbox for the Connection Launcher window."


# ====================================================================================================
# 4. MAIN SANDBOX WINDOW
# ----------------------------------------------------------------------------------------------------
class ConnectionLauncherSandbox(BaseGUI):
    """
    Description:
        Single-page sandbox window that exercises the full Connection Launcher layout:
        top overview/console, middle configuration row, bottom provider row.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Uses production G01/G02 primitives and patterns, but contains no real logic.
        - Cards include inline debug hints describing grid positions and intentions.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        logger.info("[SP2] Initialising ConnectionLauncherSandbox window.")
        super().__init__(*args, **kwargs)
        self.ui = UIPrimitives(self.main_frame)
        self.build_widgets()

    # ------------------------------------------------------------------------------------------------
    # WIDGET TREE
    # ------------------------------------------------------------------------------------------------
    def build_widgets(self) -> None:
        """
        Description:
            Build the full layout for the sandbox window.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            - Top row: overview + console cards
            - Middle row: 4 configuration cards
            - Bottom row: 4 provider cards
        """
        logger.info("[SP2] Building widget tree.")

        # --------------------------------------------------------------------------------------------
        # 4.1 WINDOW HEADING
        # --------------------------------------------------------------------------------------------
        heading(self.main_frame, PAGE_HEADING, surface="Primary").pack(
            anchor="n",
            pady=(0, 4),
        )
        body_text(self.main_frame, PAGE_SUBHEADING, surface="Primary").pack(
            anchor="n",
            pady=(0, 12),
        )

        # --------------------------------------------------------------------------------------------
        # 4.2 TOP ROW — OVERVIEW (30%) + CONSOLE (70%)
        # --------------------------------------------------------------------------------------------
        logger.debug("[SP2] Building top row (overview + console).")
        top_row = ttk.Frame(self.main_frame, style="SectionOuter.TFrame")
        top_row.pack(fill="x", padx=FRAME_PADDING, pady=(0, FRAME_PADDING))

        # 30% / 70% weighting across two columns
        top_row.columnconfigure(0, weight=3, minsize=int(FRAME_SIZE_H * 0.25))
        top_row.columnconfigure(1, weight=7, minsize=int(FRAME_SIZE_H * 0.45))

        overview = create_card_grid(
            parent=top_row,
            row=0,
            column=0,
            title="Overview",
        )
        console = create_card_grid(
            parent=top_row,
            row=0,
            column=1,
            title="Console",
        )

        self.build_overview_card(overview.body)
        self.build_console_card(console.body)

        # --------------------------------------------------------------------------------------------
        # 4.3 MIDDLE ROW — 4 × CONFIGURATION CARDS
        # --------------------------------------------------------------------------------------------
        logger.debug("[SP2] Building middle row (4 configuration cards).")
        mid_row = ttk.Frame(self.main_frame, style="SectionOuter.TFrame")
        mid_row.pack(fill="x", padx=FRAME_PADDING, pady=(0, FRAME_PADDING))

        for col in range(4):
            mid_row.columnconfigure(col, weight=1, minsize=int(FRAME_SIZE_H * 0.20))

        self.build_google_drive_card(mid_row, column=0)
        self.build_snowflake_card(mid_row, column=1)
        self.build_accounting_period_card(mid_row, column=2)
        self.build_dwh_period_card(mid_row, column=3)

        # --------------------------------------------------------------------------------------------
        # 4.4 BOTTOM ROW — 4 × PROVIDER CARDS
        # --------------------------------------------------------------------------------------------
        logger.debug("[SP2] Building bottom row (4 provider cards).")
        bottom_row = ttk.Frame(self.main_frame, style="SectionOuter.TFrame")
        bottom_row.pack(fill="x", padx=FRAME_PADDING, pady=(0, FRAME_PADDING))

        for col in range(4):
            bottom_row.columnconfigure(col, weight=1, minsize=int(FRAME_SIZE_H * 0.20))

        self.build_provider_card(bottom_row, column=0, provider_name="Braintree")
        self.build_provider_card(bottom_row, column=1, provider_name="Uber Eats")
        self.build_provider_card(bottom_row, column=2, provider_name="Deliveroo")
        self.build_provider_card(bottom_row, column=3, provider_name="Just Eat")

        # --------------------------------------------------------------------------------------------
        # 4.5 BOTTOM BUTTON ROW (DEV CONTROLS)
        # --------------------------------------------------------------------------------------------
        logger.debug("[SP2] Building bottom button row.")
        button_row = ButtonRow(
            self.main_frame,
            buttons=[
                ("Run Layout Sanity Check", self.on_run_layout_check),
                ("Close Sandbox", self.close),
            ],
        )
        button_row.pack(fill="x", padx=FRAME_PADDING, pady=(4, 12))

    # =================================================================================================
    # 5. CARD BUILDERS
    # =================================================================================================
    def build_overview_card(self, parent: ttk.Frame) -> None:
        """
        Description:
            Populate the Overview card with explanatory text and debug hints.

        Args:
            parent (ttk.Frame): Card body frame from create_card_grid.

        Returns:
            None.

        Raises:
            None.
        """
        logger.debug("[SP2] Building Overview card contents.")
        parent.columnconfigure(0, weight=1)

        make_label(
            parent,
            "Overview",
            category="SectionHeading",
            surface="Secondary",
            weight="Bold",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        body_text(
            parent,
            "Review and confirm high-level settings before running any jobs. "
            "Use the configuration cards in the middle row to adjust periods, "
            "credentials, and provider selection. The console on the right "
            "shows mock log output.",
            surface="Secondary",
            wraplength=360,
        ).grid(row=1, column=0, sticky="w")

        make_label(
            parent,
            "[DEBUG] Top row: Overview card (approx. 30% width).",
            category="Body",
            surface="Secondary",
            weight="Normal",
        ).grid(row=2, column=0, sticky="w", pady=(8, 0))

    # ------------------------------------------------------------------------------------------------
    def build_console_card(self, parent: ttk.Frame) -> None:
        """
        Description:
            Populate the Console card with a simple read-only text area.

        Args:
            parent (ttk.Frame): Card body frame from create_card_grid.

        Returns:
            None.

        Raises:
            None.
        """
        logger.debug("[SP2] Building Console card contents.")
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

        make_label(
            parent,
            "Console Output",
            category="SectionHeading",
            surface="Secondary",
            weight="Bold",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        console_frame = ttk.Frame(parent)
        console_frame.grid(row=1, column=0, sticky="nsew")

        text_widget = tk.Text(
            console_frame,
            height=10,
            wrap="word",
        )
        scrollbar = ttk.Scrollbar(
            console_frame,
            orient="vertical",
            command=text_widget.yview,
        )
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        console_frame.rowconfigure(0, weight=1)
        console_frame.columnconfigure(0, weight=1)

        sample_log = (
            "[INFO] Connection Launcher Sandbox initialised.\n"
            "[INFO] Top row: Overview + Console ready.\n"
            "[INFO] Middle row: configuration cards created.\n"
            "[INFO] Bottom row: provider cards created.\n"
            "[DEBUG] Use this area for mock status/log output.\n"
        )
        text_widget.insert("1.0", sample_log)
        text_widget.configure(state="disabled")

        make_label(
            parent,
            "[DEBUG] Top row: Console card (approx. 70% width).",
            category="Body",
            surface="Secondary",
            weight="Normal",
        ).grid(row=2, column=0, sticky="w", pady=(8, 0))

    # ------------------------------------------------------------------------------------------------
    def build_google_drive_card(self, parent: ttk.Frame, *, column: int) -> None:
        """
        Description:
            Build the Google Drive configuration card in the middle row.

        Args:
            parent (ttk.Frame): Middle-row container frame.
            column (int): Grid column (0–3).

        Returns:
            None.

        Raises:
            None.
        """
        logger.debug("[SP2] Building Google Drive card at column %s.", column)
        container = create_card_grid(
            parent=parent,
            row=0,
            column=column,
            title="Google Drive Mapping",
        )
        body = container.body
        body.columnconfigure(0, weight=1)

        make_label(
            body,
            "Configuration",
            category="Body",
            surface="Secondary",
            weight="Bold",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        drive_mode_var = tk.StringVar(value="api")

        ttk.Radiobutton(
            body,
            text="Use Google Drive API",
            variable=drive_mode_var,
            value="api",
        ).grid(row=1, column=0, sticky="w", pady=(0, 2))

        ttk.Radiobutton(
            body,
            text="Use Local Mapped Drive",
            variable=drive_mode_var,
            value="local",
        ).grid(row=2, column=0, sticky="w", pady=(0, 6))

        ttk.Button(
            body,
            text="Browse Local Folder",
            command=lambda: self.on_browse_local_folder(drive_mode_var.get()),
        ).grid(row=3, column=0, sticky="w", pady=(0, 4))

        self.google_drive_path_var = tk.StringVar(value="Local Path: (not selected)")
        tk.Label(body, textvariable=self.google_drive_path_var, anchor="w").grid(
            row=4,
            column=0,
            sticky="w",
            pady=(2, 0),
        )

        self.google_drive_status_var = tk.StringVar(value="Status: Not mapped")
        tk.Label(body, textvariable=self.google_drive_status_var, anchor="w").grid(
            row=5,
            column=0,
            sticky="w",
            pady=(2, 0),
        )

        make_label(
            body,
            "[DEBUG] Middle row col 0: Google Drive card.",
            category="Body",
            surface="Secondary",
            weight="Normal",
        ).grid(row=6, column=0, sticky="w", pady=(6, 0))

    # ------------------------------------------------------------------------------------------------
    def build_snowflake_card(self, parent: ttk.Frame, *, column: int) -> None:
        """
        Description:
            Build the Snowflake configuration card.

        Args:
            parent (ttk.Frame): Middle-row container frame.
            column (int): Grid column (0–3).

        Returns:
            None.

        Raises:
            None.
        """
        logger.debug("[SP2] Building Snowflake card at column %s.", column)
        container = create_card_grid(
            parent=parent,
            row=0,
            column=column,
            title="Snowflake Connector",
        )
        body = container.body
        body.columnconfigure(0, weight=1)

        user_mode_var = tk.StringVar(value="user1")

        make_label(
            body,
            "User Selection",
            category="Body",
            surface="Secondary",
            weight="Bold",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        ttk.Radiobutton(
            body,
            text="User 1 (default)",
            variable=user_mode_var,
            value="user1",
        ).grid(row=1, column=0, sticky="w")

        ttk.Radiobutton(
            body,
            text="User 2",
            variable=user_mode_var,
            value="user2",
        ).grid(row=2, column=0, sticky="w")

        ttk.Radiobutton(
            body,
            text="Custom Email",
            variable=user_mode_var,
            value="custom",
        ).grid(row=3, column=0, sticky="w", pady=(0, 4))

        self.snowflake_email_var = tk.StringVar(value="")
        email_entry = ttk.Entry(body, textvariable=self.snowflake_email_var, width=28)
        email_entry.grid(row=4, column=0, sticky="we")

        ttk.Button(
            body,
            text="Connect to Snowflake",
            command=lambda: self.on_connect_snowflake(user_mode_var.get()),
        ).grid(row=5, column=0, sticky="w", pady=(6, 2))

        self.snowflake_status_var = tk.StringVar(value="Status: Not connected")
        tk.Label(body, textvariable=self.snowflake_status_var, anchor="w").grid(
            row=6,
            column=0,
            sticky="w",
            pady=(2, 0),
        )

        make_label(
            body,
            "[DEBUG] Middle row col 1: Snowflake card.",
            category="Body",
            surface="Secondary",
            weight="Normal",
        ).grid(row=7, column=0, sticky="w", pady=(6, 0))

    # ------------------------------------------------------------------------------------------------
    def build_accounting_period_card(self, parent: ttk.Frame, *, column: int) -> None:
        """
        Description:
            Build the Accounting Period configuration card.

        Args:
            parent (ttk.Frame): Middle-row container frame.
            column (int): Grid column (0–3).

        Returns:
            None.

        Raises:
            None.
        """
        logger.debug("[SP2] Building Accounting Period card at column %s.", column)
        container = create_card_grid(
            parent=parent,
            row=0,
            column=column,
            title="Accounting Period",
        )
        body = container.body
        body.columnconfigure(0, weight=1)

        make_label(
            body,
            "Current Accounting Period",
            category="Body",
            surface="Secondary",
            weight="Bold",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        make_label(
            body,
            "Default: November 2025",
            category="Body",
            surface="Secondary",
            weight="Normal",
        ).grid(row=1, column=0, sticky="w")

        body_text(
            body,
            "Use the default period for most runs. Override only when backfilling or "
            "running historical reconciliations.",
            surface="Secondary",
            wraplength=220,
        ).grid(row=2, column=0, sticky="w", pady=(4, 4))

        mode_var = tk.StringVar(value="default")

        ttk.Radiobutton(
            body,
            text="Use Default Accounting Period",
            variable=mode_var,
            value="default",
        ).grid(row=3, column=0, sticky="w")

        ttk.Radiobutton(
            body,
            text="Override Accounting Period",
            variable=mode_var,
            value="override",
        ).grid(row=4, column=0, sticky="w", pady=(0, 4))

        self.accounting_override_var = tk.StringVar(value="YYYY-MM")
        ttk.Entry(body, textvariable=self.accounting_override_var, width=12).grid(
            row=5,
            column=0,
            sticky="w",
        )

        make_label(
            body,
            "[DEBUG] Middle row col 2: Accounting Period card.",
            category="Body",
            surface="Secondary",
            weight="Normal",
        ).grid(row=6, column=0, sticky="w", pady=(6, 0))

    # ------------------------------------------------------------------------------------------------
    def build_dwh_period_card(self, parent: ttk.Frame, *, column: int) -> None:
        """
        Description:
            Build the Datawarehouse Period configuration card.

        Args:
            parent (ttk.Frame): Middle-row container frame.
            column (int): Grid column (0–3).

        Returns:
            None.

        Raises:
            None.
        """
        logger.debug("[SP2] Building DWH Period card at column %s.", column)
        container = create_card_grid(
            parent=parent,
            row=0,
            column=column,
            title="Datawarehouse Period",
        )
        body = container.body
        body.columnconfigure(0, weight=1)

        make_label(
            body,
            "Current DWH Period",
            category="Body",
            surface="Secondary",
            weight="Bold",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        make_label(
            body,
            "Default: November 2025",
            category="Body",
            surface="Secondary",
            weight="Normal",
        ).grid(row=1, column=0, sticky="w")

        body_text(
            body,
            "The DWH period should normally match the accounting period. Override only "
            "when the warehouse lags or leads the accounting close.",
            surface="Secondary",
            wraplength=220,
        ).grid(row=2, column=0, sticky="w", pady=(4, 4))

        mode_var = tk.StringVar(value="default")

        ttk.Radiobutton(
            body,
            text="Use Default DWH Period",
            variable=mode_var,
            value="default",
        ).grid(row=3, column=0, sticky="w")

        ttk.Radiobutton(
            body,
            text="Override DWH Period",
            variable=mode_var,
            value="override",
        ).grid(row=4, column=0, sticky="w", pady=(0, 4))

        self.dwh_override_var = tk.StringVar(value="YYYY-MM")
        ttk.Entry(body, textvariable=self.dwh_override_var, width=12).grid(
            row=5,
            column=0,
            sticky="w",
        )

        make_label(
            body,
            "[DEBUG] Middle row col 3: DWH Period card.",
            category="Body",
            surface="Secondary",
            weight="Normal",
        ).grid(row=6, column=0, sticky="w", pady=(6, 0))

    # ------------------------------------------------------------------------------------------------
    def build_provider_card(self, parent: ttk.Frame, *, column: int, provider_name: str) -> None:
        """
        Description:
            Build a provider selection card in the bottom row.

        Args:
            parent (ttk.Frame): Bottom-row container frame.
            column (int): Grid column (0–3).
            provider_name (str): Provider display name.

        Returns:
            None.

        Raises:
            None.
        """
        logger.debug("[SP2] Building Provider card '%s' at column %s.", provider_name, column)
        container = create_card_grid(
            parent=parent,
            row=0,
            column=column,
            title=provider_name,
        )
        body = container.body
        body.columnconfigure(0, weight=1)

        make_label(
            body,
            f"{provider_name} Provider",
            category="Body",
            surface="Secondary",
            weight="Bold",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        body_text(
            body,
            "Toggle this provider on/off for the current run. "
            "In production this card would show recent stats and health.",
            surface="Secondary",
            wraplength=220,
        ).grid(row=1, column=0, sticky="w", pady=(0, 6))

        var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            body,
            text="Include in run",
            variable=var,
        ).grid(row=2, column=0, sticky="w")

        make_label(
            body,
            f"[DEBUG] Bottom row col {column}: {provider_name} card.",
            category="Body",
            surface="Secondary",
            weight="Normal",
        ).grid(row=3, column=0, sticky="w", pady=(6, 0))

    # =================================================================================================
    # 6. CALLBACKS (DEV-ONLY)
    # =================================================================================================
    def on_browse_local_folder(self, mode: str) -> None:
        """
        Description:
            Dev callback for the 'Browse Local Folder' button.

        Args:
            mode (str): Current drive mode ("api" or "local").

        Returns:
            None.

        Raises:
            None.
        """
        logger.info("[SP2] Browse Local Folder clicked (mode=%s).", mode)
        # Dev stub – in production you would open a filedialog here.
        self.google_drive_path_var.set("Local Path: H:\\SharedDrive\\Example")
        self.google_drive_status_var.set("Status: Mapped (DEV MOCK)")

    # ------------------------------------------------------------------------------------------------
    def on_connect_snowflake(self, user_mode: str) -> None:
        """
        Description:
            Dev callback for the 'Connect to Snowflake' button.

        Args:
            user_mode (str): Selected user mode ("user1", "user2", "custom").

        Returns:
            None.

        Raises:
            None.
        """
        logger.info("[SP2] Connect to Snowflake clicked (user_mode=%s).", user_mode)
        email = self.snowflake_email_var.get().strip()
        if user_mode == "custom" and not email:
            self.snowflake_status_var.set("Status: Custom email required (DEV MOCK)")
        else:
            self.snowflake_status_var.set("Status: Connected (DEV MOCK)")

    # ------------------------------------------------------------------------------------------------
    def on_run_layout_check(self) -> None:
        """
        Description:
            Simple dev callback that logs a layout sanity check.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """
        logger.info("[SP2] Running layout sanity check (DEV ONLY).")
        # This is where you could add assertions / layout diagnostics later.


# ====================================================================================================
# 7. MAIN GUARD
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging()
    logger.info("=== SP2 Connection Launcher Sandbox — Start ===")

    app = ConnectionLauncherSandbox(title=PAGE_HEADING)

    # For sandbox work you can comment/uncomment fullscreen as needed:
    # app.open_fullscreen()
    app.mainloop()

    logger.info("=== SP2 Connection Launcher Sandbox — End ===")