# ====================================================================================================
# G02c_form_patterns.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Schema-driven, theme-aware form patterns for all GUI modules.
#
#   This module provides a single high-level abstraction:
#
#       • FormBuilder
#           - Builds a complete form from a declarative schema.
#           - Uses themed widget primitives (G01b_widget_primitives).
#           - Uses standardised layout helpers (G02a_layout_utils.grid_form_row).
#           - Exposes a simple value/validation API.
#
#   FormBuilder focuses on **form structure and behaviour**, not raw widget creation:
#       • Takes a schema describing fields, types, validation rules, and defaults.
#       • Renders a consistent two-column layout: [Label] [Field].
#       • Keeps an internal mapping of keys → widgets and tk.Variables.
#       • Provides methods to get/set/clear values and run validation.
#
#   Supported schema keys per field:
#       type:      "entry" | "combo" | "checkbox" | "text"     (default: "entry")
#       label:     User-facing label text (left column).
#       key:       Unique identifier used in the values dict.
#       values:    List of items for "combo" fields.
#       required:  bool — value must not be empty when True.
#       numeric:   bool — value must be castable to float when True.
#       allowed:   Iterable of permitted values (exact match).
#       default:   Default value applied on initial render (optional).
#       validate:  callable(value) -> (ok: bool, error_message: str)
#
# Design Principles:
#   • 100% form behaviour and layout – no business logic, no I/O.
#   • Styling and spacing tokens come from G01a_style_config.
#   • Widget creation comes from G01b_widget_primitives.
#   • Layout primitives (grid_form_row) come from G02a_layout_utils.
#   • Safe to import anywhere in the GUI layer; no side effects at import time.
#
# Debugging:
#   • Uses core.C03_logging_handler.get_logger for structured logging.
#   • Demo entry point (run_demo) is isolated under the __main__ guard.
#
# Integration:
#       from gui.G02c_form_patterns import FormBuilder
#
#       schema = [
#           {"type": "entry", "label": "Host", "key": "host", "required": True},
#           {"type": "entry", "label": "Port", "key": "port", "numeric": True},
#           {"type": "combo", "label": "Env",  "key": "env",  "values": ["Dev", "UAT", "Prod"]},
#       ]
#
#       form = FormBuilder(parent=section.body, schema=schema)
#       values = form.get_values()
#       errors = form.validate_all()
#
# Architectural Guarantees:
#   • No core imports outside core.C00_set_packages.
#   • No sys.path mutation beyond the standard Section 1 template.
#   • No Tk root creation or theme initialisation at import time.
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-23
# Project:      Core Boilerplate v1.0
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
from gui.G00a_gui_packages import tk, ttk, scrolledtext, Window, Style, tb  # GUI toolkit + helpers
from gui.G01a_style_config import *                         # FRAME_PADDING, FRAME_SIZE_H, FRAME_SIZE_V, colours, etc.
from gui.G01b_style_engine import configure_ttk_styles
from gui.G01c_widget_primitives import (
    make_label,
    make_entry,
    make_combobox,
    make_checkbox,
    make_textarea,
)
from gui.G02a_layout_utils import grid_form_row             # layout-only, no UIComponents dependency

# Prefer ttkbootstrap's ttk-compatible widgets when available, otherwise fall back to standard ttk.
try:
    bttk = tb  # type: ignore[name-defined]
    if bttk is None:
        bttk = ttk  # type: ignore[assignment]
except Exception:
    bttk = ttk  # type: ignore[assignment]


# ====================================================================================================
# 3. FORM BUILDER CLASS
# ----------------------------------------------------------------------------------------------------
class FormBuilder:
    """
    Description:
        Dynamic, schema-driven form builder that produces a clean, consistent layout using
        themed widgets and shared layout primitives.

        The form is always rendered as a simple two-column grid:

            [ Label (column 0) ]  [ Field widget (column 1, sticky="we") ]

        A caller provides a schema describing each field, and FormBuilder:
            - Creates the correct widget (entry/combobox/checkbox/text).
            - Wires up tk.Variable bindings where appropriate.
            - Applies default values.
            - Manages layout using grid_form_row from G02a_layout_utils.
            - Exposes a small API for get/set/clear/validate operations.

    Args:
        parent (tk.Misc):
            Container where the form rows will be created (typically a section body).
        schema (List[Dict[str, Any]]):
            Declarative description of each form field.

            Supported keys per field:
                type:      "entry" | "combo" | "checkbox" | "text"  (default: "entry")
                label:     Display label string (left column).
                key:       Unique identifier for this field's value (required).
                values:    List of allowed values for "combo".
                required:  bool; when True, value must not be empty.
                numeric:   bool; when True, value must be castable to float.
                allowed:   Iterable of allowed values; value must be in this collection.
                default:   Default value applied on initial render.
                validate:  callable(value) -> (ok: bool, error_message: str)

    Returns:
        None.

    Raises:
        ValueError:
            If any field in the schema is missing a required 'key' attribute, or if an
            unsupported field type is encountered.

    Notes:
        - This class is layout- and behaviour-focused only; there is no business logic.
        - It is safe to instantiate multiple FormBuilder instances on the same parent.
    """

    # Default row spacing
    ROW_PADY: Tuple[int, int] = (4, 4)
    LABEL_PADX: Tuple[int, int] = (0, FRAME_PADDING)

    def __init__(self, parent: tk.Misc, schema: List[Dict[str, Any]]) -> None:  # type: ignore[name-defined]
        self.parent = parent
        self.schema = schema

        # Maps field key -> widget instance
        self.widgets: Dict[str, Any] = {}
        # Maps field key -> associated tk.Variable (if used)
        self.variables: Dict[str, Any] = {}

        logger.debug("[G02c] Initialising FormBuilder with %d fields", len(schema))
        self.render_form_rows()

    # -----------------------------------------------------------------------------------------------
    # 3.1 FORM CONSTRUCTION
    # -----------------------------------------------------------------------------------------------
    def render_form_rows(self) -> None:
        """
        Description:
            Build all form rows using widget primitives and the shared grid_form_row helper.

            For each field in the schema:
                - Create a label using make_label().
                - Create an appropriate widget primitive based on 'type'.
                - Bind a tk.Variable when appropriate (entry/combo/checkbox).
                - Apply any default value.
                - Lay out using grid_form_row(...).

        Args:
            None.

        Returns:
            None.

        Raises:
            ValueError:
                If a field dictionary is missing the required 'key' attribute, or if
                the 'type' value is unsupported.

        Notes:
            This method is called automatically from __init__, but can also be called
            again if you ever decide to rebuild the form in-place.
        """
        for row_index, field in enumerate(self.schema):
            field_type = str(field.get("type", "entry")).lower()
            label_text = field.get("label", "")
            key = field.get("key")

            if not key:
                raise ValueError("Form field is missing required 'key' attribute")

            logger.debug(
                "[G02c] Building field '%s' (type=%s, row=%d)",
                key,
                field_type,
                row_index,
            )

            # ---------------------------------------------------------------------------------------
            # Label widget (left column)
            # ---------------------------------------------------------------------------------------
            label_widget = make_label(self.parent, label_text)

            # ---------------------------------------------------------------------------------------
            # Field widget (right column) + variable binding
            # ---------------------------------------------------------------------------------------
            widget: Any
            variable: Any = None

            if field_type == "entry":
                variable = tk.StringVar()
                widget = make_entry(self.parent)
                widget.configure(textvariable=variable)

            elif field_type == "combo":
                variable = tk.StringVar()
                values = field.get("values", [])
                widget = make_combobox(
                    self.parent,
                    values=values,
                    state=field.get("state", "readonly"),
                )
                widget.configure(textvariable=variable)

            elif field_type == "checkbox":
                variable = tk.BooleanVar()
                # Checkbox text is typically shown in the label column, so use empty button text.
                widget = make_checkbox(
                    self.parent,
                    text="",
                    variable=variable,
                )

            elif field_type == "text":
                # Use themed textarea; no direct StringVar binding (handled via widget.get()).
                widget = make_textarea(self.parent, height=4)

            else:
                raise ValueError(f"Unsupported form field type: {field_type!r}")

            # Apply default value if provided
            if "default" in field:
                default_value = field["default"]
                self.apply_default_value_for_field(
                    widget=widget,
                    variable=variable,
                    field_type=field_type,
                    default_value=default_value,
                )

            # ---------------------------------------------------------------------------------------
            # Layout via grid_form_row (from G02a_layout_utils)
            # ---------------------------------------------------------------------------------------
            grid_form_row(
                parent=self.parent,
                row=row_index,
                label_widget=label_widget,
                field_widget=widget,
                label_column=0,
                field_column=1,
                label_sticky="e",
                field_sticky="we",
                label_padx=self.LABEL_PADX,
                common_pady=self.ROW_PADY,
            )

            # Store references
            self.widgets[key] = widget
            self.variables[key] = variable

    # -----------------------------------------------------------------------------------------------
    def apply_default_value_for_field(
        self,
        widget: Any,
        variable: Any,
        field_type: str,
        default_value: Any,
    ) -> None:
        """
        Description:
            Apply a default value to a field during initial render.

            For variable-backed widgets, this prefers setting the tk.Variable so that
            widget and model stay in sync. For text widgets, it writes directly into
            the content area.

        Args:
            widget (Any):
                The widget instance created for this field.
            variable (Any):
                Associated tk.Variable instance (if any), such as StringVar/BooleanVar.
            field_type (str):
                The normalised form field type ("entry", "combo", "checkbox", "text").
            default_value (Any):
                Value to apply as the initial content.

        Returns:
            None.

        Raises:
            None.

        Notes:
            All exceptions are caught and logged as warnings; failure to apply a default
            never stops the form from rendering.
        """
        if field_type == "text":
            try:
                widget.delete("1.0", "end")
                if default_value is not None:
                    widget.insert("1.0", str(default_value))
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "[G02c] Failed to apply default value to text field: %s",
                    exc,
                )
            return

        # For entry/combo/checkbox, prefer the tk.Variable (if present)
        if variable is not None and hasattr(variable, "set"):
            try:
                variable.set(default_value)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "[G02c] Failed to set default via tk.Variable: %s",
                    exc,
                )

        # Fallback to direct widget set if supported
        if hasattr(widget, "insert") and hasattr(widget, "delete"):
            try:
                widget.delete(0, "end")
                if default_value is not None:
                    widget.insert(0, str(default_value))
            except Exception:
                # Swallow completely; defaults are not critical enough to fail rendering.
                pass

    # -----------------------------------------------------------------------------------------------
    # 3.2 DATA EXTRACTION & MANIPULATION
    # -----------------------------------------------------------------------------------------------
    def get_values(self) -> Dict[str, Any]:
        """
        Description:
            Return a dictionary of field values keyed by each field's 'key'.

            For each row:
                - If widget is a Text/ScrolledText, uses widget.get("1.0", "end").
                - Else if there is a tk.Variable, uses variable.get().
                - Else falls back to widget.get() when available.

        Args:
            None.

        Returns:
            Dict[str, Any]:
                Mapping of schema keys to the current widget values.

        Raises:
            None.

        Notes:
            Any widget that does not support the above access patterns will simply
            yield a value of None.
        """
        data: Dict[str, Any] = {}

        for field in self.schema:
            key = field["key"]
            widget = self.widgets.get(key)
            variable = self.variables.get(key)

            if widget is None:
                continue

            if isinstance(widget, scrolledtext.ScrolledText):  # type: ignore[name-defined]
                value = widget.get("1.0", "end").strip()
            elif isinstance(widget, tk.Text):
                value = widget.get("1.0", "end").strip()
            elif variable is not None and hasattr(variable, "get"):
                value = variable.get()
            elif hasattr(widget, "get"):
                try:
                    value = widget.get()
                except Exception:
                    value = None
            else:
                value = None

            data[key] = value

        return data

    # -----------------------------------------------------------------------------------------------
    def set_values(self, values: Dict[str, Any]) -> None:
        """
        Description:
            Update form values from a dict keyed by field 'key'.

            Behaviour:
                - For Text/ScrolledText: clear content and insert new text.
                - For var-backed widgets: uses variable.set(value).
                - For simple entry-like widgets: uses delete/insert if available.

        Args:
            values (Dict[str, Any]):
                Mapping of field key -> desired value.

        Returns:
            None.

        Raises:
            None.

        Notes:
            Any errors while updating a particular field are logged as warnings,
            and processing for other fields continues.
        """
        for key, value in values.items():
            widget = self.widgets.get(key)
            variable = self.variables.get(key)

            if widget is None:
                continue

            # Multi-line widgets
            if isinstance(widget, scrolledtext.ScrolledText) or isinstance(widget, tk.Text):  # type: ignore[name-defined]
                try:
                    widget.delete("1.0", "end")
                    if value is not None:
                        widget.insert("1.0", str(value))
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "[G02c] Failed to set value for text field %s: %s",
                        key,
                        exc,
                    )
                continue

            # tk.Variable-backed widgets
            if variable is not None and hasattr(variable, "set"):
                try:
                    variable.set(value)
                    continue
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "[G02c] Failed to set tk.Variable value for %s: %s",
                        key,
                        exc,
                    )

            # Fallback: direct widget manipulation
            if hasattr(widget, "delete") and hasattr(widget, "insert"):
                try:
                    widget.delete(0, "end")
                    if value is not None:
                        widget.insert(0, str(value))
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "[G02c] Failed to set value on widget for %s: %s",
                        key,
                        exc,
                    )

    # -----------------------------------------------------------------------------------------------
    def clear(self) -> None:
        """
        Description:
            Reset all fields to a sensible empty state.

            Behaviour:
                - For Text/ScrolledText: delete all content.
                - For StringVar: set to "".
                - For BooleanVar: set to False.
                - For others: widget.delete(0, "end") if available.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Notes:
            Any errors while clearing an individual field are swallowed, as this
            operation is best-effort and should never crash the UI.
        """
        for key, widget in self.widgets.items():
            variable = self.variables.get(key)

            if isinstance(widget, scrolledtext.ScrolledText) or isinstance(widget, tk.Text):  # type: ignore[name-defined]
                try:
                    widget.delete("1.0", "end")
                except Exception:
                    pass
                if variable is not None and hasattr(variable, "set"):
                    try:
                        variable.set("")
                    except Exception:
                        pass
                continue

            if isinstance(variable, tk.StringVar):
                variable.set("")
            elif isinstance(variable, tk.BooleanVar):
                variable.set(False)
            elif variable is not None and hasattr(variable, "set"):
                try:
                    variable.set("")
                except Exception:
                    pass
            else:
                if hasattr(widget, "delete"):
                    try:
                        widget.delete(0, "end")
                    except Exception:
                        pass

    # -----------------------------------------------------------------------------------------------
    # 3.3 VALIDATION ENGINE
    # -----------------------------------------------------------------------------------------------
    def validate_all(self) -> Dict[str, str]:
        """
        Description:
            Validate all fields according to the rules in their schema entries.

            Validation rules per field:
                required: True        → value must not be empty/None.
                numeric:  True        → value must be castable to float.
                allowed:  [list]      → value must be a member of the list.
                validate: callable    → custom validator; value -> (ok: bool, msg: str).

        Args:
            None.

        Returns:
            Dict[str, str]:
                Mapping from field key to error message (only for failing fields).
                An empty dict indicates that all fields passed validation.

        Raises:
            None.

        Notes:
            - Custom validators are fully user-defined; any exceptions are caught and
              logged, and the field is treated as failing validation.
        """
        errors: Dict[str, str] = {}
        values = self.get_values()

        for field in self.schema:
            key = field["key"]
            value = values.get(key)

            # Required
            if field.get("required") and (value is None or value == ""):
                errors[key] = "This field is required"
                continue

            # Numeric
            if field.get("numeric") and value not in (None, ""):
                try:
                    float(value)
                except Exception:
                    errors[key] = "Must be numeric"
                    continue

            # Allowed values (exact match)
            allowed_values = field.get("allowed")
            if allowed_values is not None and value not in allowed_values and value not in (None, ""):
                errors[key] = f"Invalid value (allowed: {allowed_values})"
                continue

            # Custom validator
            validator: Optional[Callable[[Any], Tuple[bool, str]]] = field.get("validate")  # type: ignore[assignment]
            if validator:
                try:
                    ok, message = validator(value)
                    if not ok:
                        errors[key] = message or "Invalid value"
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "[G02c] Validator for '%s' raised exception: %s",
                        key,
                        exc,
                    )
                    errors[key] = "Validation failed"

        return errors


# ====================================================================================================
# 4. SELF-TEST / SANDBOX
# ----------------------------------------------------------------------------------------------------
def run_demo() -> None:
    """
    Description:
        Lightweight visual demo to verify FormBuilder behaviour in isolation.

        Creates a simple Tk/ttk (or ttkbootstrap) window and renders a schema-driven form
        directly into a padded frame using the project-wide style engine.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - This function is intended for manual testing only.
        - It is only invoked when this module is run as a script.
    """
    logger.info("=== G02c_form_patterns demo start ===")

    # -------------------------------------------------------------------------------------------
    # Window & style initialisation
    # -------------------------------------------------------------------------------------------
    try:
        root = Window(themename="flatly")  # type: ignore[name-defined]
        style_obj = Style()                # type: ignore[name-defined]
        logger.info("[G02c] Using ttkbootstrap Window/Style.")
    except Exception:
        root = tk.Tk()
        style_obj = ttk.Style()
        logger.info("[G02c] Falling back to standard Tk/ttk.")

    root.title("G02c Form Patterns Demo")
    root.geometry(f"{FRAME_SIZE_H}x{FRAME_SIZE_V}")
    root.configure(bg=GUI_COLOUR_BG_PRIMARY)

    # Apply global ttk styles
    configure_ttk_styles(style_obj)  # type: ignore[arg-type]
    logger.info("[G02c] configure_ttk_styles applied successfully.")

    # -------------------------------------------------------------------------------------------
    # Build demo schema and container
    # -------------------------------------------------------------------------------------------
    schema = [
        {"type": "entry", "label": "Host", "key": "host", "required": True, "default": "localhost"},
        {"type": "entry", "label": "Port", "key": "port", "numeric": True, "default": "1521"},
        {
            "type": "combo",
            "label": "Environment",
            "key": "env",
            "values": ["Dev", "UAT", "Prod"],
            "required": True,
            "default": "Dev",
        },
        {"type": "checkbox", "label": "Use SSL", "key": "ssl", "default": True},
        {"type": "text", "label": "Description", "key": "desc"},
    ]

    # Simple padded container (no G02b dependency in the sandbox)
    outer = bttk.Frame(root)
    outer.pack(fill="both", expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)

    # Heading
    heading_label = make_label(outer, "G02c Form Patterns — Demo", fg=TEXT_COLOUR_PRIMARY)
    heading_label.geometry_kwargs.setdefault("pady", (0, 8))  # type: ignore[attr-defined]
    heading_label.pack(anchor="w", **heading_label.geometry_kwargs)  # type: ignore[arg-type]

    # Form container (grid-based)
    form_frame = bttk.Frame(outer)
    form_frame.pack(fill="x")

    form = FormBuilder(form_frame, schema=schema)

    # Buttons row
    buttons_row = bttk.Frame(outer)
    buttons_row.pack(fill="x", pady=(12, 0))

    def on_print() -> None:
        values = form.get_values()
        errors = form.validate_all()
        print("Values:", values)
        print("Errors:", errors)

    def on_clear() -> None:
        form.clear()

    print_btn = bttk.Button(buttons_row, text="Print Values / Errors", command=on_print)
    clear_btn = bttk.Button(buttons_row, text="Clear", command=on_clear)

    print_btn.pack(side="left")
    clear_btn.pack(side="left", padx=(8, 0))

    logger.info("=== G02c_form_patterns demo ready ===")
    root.mainloop()
    logger.info("=== G02c_form_patterns demo end ===")


# ====================================================================================================
# 5. MAIN GUARD
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    run_demo()
