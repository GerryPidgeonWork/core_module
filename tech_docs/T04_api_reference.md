# GUI Framework API Reference v1.0

## 1. Overview

This document provides the authoritative public API reference for the GUI Framework (Layers G00–G03). It describes the classes, functions, and structured data types available for application development.

### 1.1. Usage Principles
* **Widget Instantiation:** Application code must strictly use **G02a factories** (`make_*`). Direct instantiation of `tk` or `ttk` widgets is prohibited to ensure style compliance.
* **Layout Management:** Geometry management must be performed via **G02b utilities** (`stack_vertical`, `layout_row`). Ad-hoc grid/pack configuration is restricted.
* **Window Management:** Applications must subclass `BaseWindow` (G02c) to ensure correct root initialisation and theme handling.
* **Composition:** Complex UI structures should be built using **G03 patterns**, which return structured result objects providing access to internal state.

---

## 2. G00 — Package Hub

**Module:** `gui.G00a_gui_packages`

Provides the foundational imports and platform-specific initialisation logic. This is the **sole source** for all Tkinter-related imports.

### 2.1. Theme & Initialisation

#### `init_gui_theme()`
Initialises the `ttk` theme engine to ensure consistent cross-platform rendering, specifically forcing the 'clam' theme on Windows to support custom button backgrounds.
* **Usage:** Automatically called by `BaseWindow`. Must be called manually immediately after `tk.Tk()` if `BaseWindow` is not used.
* **Scrollbars:** The framework uses the standard OS-native scrollbar styling provided by the underlying theme. No custom scrollbar styles are applied to ensure native look-and-feel.

#### `enable_ttkbootstrap()`
Optional helper to enable `ttkbootstrap` theming if the package is installed.
* **Usage:** Call before creating the root window if third-party theming is required.

#### `is_gui_theme_initialised() -> bool`
Returns `True` if the theme system has been successfully configured.

#### `reset_gui_theme_flag()`
Resets the internal tracking flag used to prevent double-initialisation.
* **Usage:** Used only in automated tests and debugging to force a re-run of theme logic.

### 2.2. Exported Namespaces & Classes
Use these exports instead of importing directly from `tkinter`.

* **Core Namespaces:** `tk` (Tkinter), `ttk` (Themed Tkinter), `tkFont` (Font module).
* **Dialogs:** `messagebox`, `filedialog`.
* **Utilities:** `scrolledtext`, `Misc`, `Pack`.
* **Optional Widgets:**
    * `Calendar`: From `tkcalendar`.
    * `DateEntry`: From `tkcalendar`.
    * **Note:** If `tkcalendar` is not installed, these will be exported as `None`. Code should check for `None` before use.

---

## 3. G02a — Widget Primitives

**Module:** `gui.G02a_widget_primitives`

This module provides three categories of tools: **Widget Factories** (create widgets), **Style Wrappers** (create style strings), and **Typography Primitives** (create text widgets).

### 3.1. Widget Factories
These functions create fully configured `ttk` widgets with styles applied.

#### `make_label(parent, text="", size="BODY", bold=False, fg_shade="BLACK", ...)`
Creates a styled `ttk.Label`.
* **Parameters:** `size` (Typography Token), `fg_shade` (Colour Shade).
* **Returns:** `ttk.Label`

#### `make_button(parent, text="", command=None, variant="PRIMARY", ...)`
Creates a styled `ttk.Button`.
* **Parameters:** `variant` (Semantic Role: PRIMARY, SUCCESS, ERROR...).
* **Returns:** `ttk.Button`

#### `make_entry(parent, textvariable=None, role="SECONDARY", shade="LIGHT", ...)`
Creates a styled `ttk.Entry`.
* **Returns:** `ttk.Entry`

#### `make_frame(parent, role="SECONDARY", kind="SURFACE", padding="MD", ...)`
Creates a styled `ttk.Frame`.
* **Parameters:** `kind` (SURFACE, CARD, PANEL, SECTION).
* **Returns:** `ttk.Frame`

#### Other Factories
* `make_combobox(..., values=[], ...)`
* `make_spinbox(..., from_=0, to=100, ...)`
* `make_checkbox(..., variable=None, ...)`
* `make_radio(..., variable=None, value="", ...)`
* `make_textarea(..., width=40, height=10)` (Returns `tk.Text`)
* `make_separator(..., orient="horizontal")`
* `make_spacer(..., width=0, height=0)`

### 3.2. Style Wrappers
These functions return a **registered style name string** (e.g., `"Text_fg_TEXT_BLACK..."`) without creating a widget. Use these when you need to apply framework styling to existing or custom widgets.

#### Text Styles
* `label_style(size, bold, fg_colour, ...)`: Generic text style resolver.
* `label_style_heading(bold=True)`: Shortcut for HEADING size.
* `label_style_body()`: Shortcut for BODY size.
* `label_style_small()`: Shortcut for SMALL size.
* `label_style_error()`: Shortcut for ERROR colour.
* `label_style_success()`: Shortcut for SUCCESS colour.
* `label_style_warning()`: Shortcut for WARNING colour.

#### Container Styles
* `frame_style(role, shade, kind, border, padding)`: Generic container style resolver.
* `frame_style_card(role, shade)`: Raised relief, standard padding.
* `frame_style_panel(role, shade)`: Solid border, medium padding.
* `frame_style_section(role, shade)`: Flat, small padding.
* `frame_style_surface(role, shade)`: Flat, no border.

#### Input Styles
* `entry_style(control_type, role, shade)`: Generic input style.
* `entry_style_default()`: Secondary/Light.
* `entry_style_error()`: Error/Light with thicker border.
* `entry_style_success()`: Success/Light.
* `combobox_style_default()`: Standard Combobox style.
* `spinbox_style_default()`: Standard Spinbox style.

#### Control Styles
* `button_style(variant, ...)`: Generic button style.
* `button_primary()`: Primary variant.
* `button_secondary()`: Secondary variant.
* `button_success()`: Success variant.
* `button_warning()`: Warning variant.
* `button_error()`: Error variant.
* `checkbox_primary()`, `checkbox_success()`: Checkbox variants.
* `radio_primary()`, `radio_warning()`: Radio button variants.
* `switch_primary()`, `switch_error()`: Switch variants.

### 3.3. Typography Primitives
Convenience factories for semantic text elements.

**Font Sizing Tokens:**
| Token | Size (px) | Usage |
| :--- | :--- | :--- |
| **DISPLAY** | 20 | Hero titles, major page headers. |
| **HEADING** | 16 | Section headers, card titles. |
| **TITLE** | 14 | Sub-sections, grouping labels. |
| **BODY** | 11 | Standard interface text. |
| **SMALL** | 10 | Metadata, captions, hints. |

* `page_title(parent, text)`: DISPLAY size, Bold.
* `page_subtitle(parent, text)`: TITLE size, Normal, Grey.
* `section_title(parent, text)`: HEADING size, Bold.
* `body_text(parent, text)`: BODY size, Normal.
* `small_text(parent, text)`: SMALL size, Normal.
* `meta_text(parent, text)`: SMALL size, Grey.
* `divider(parent, orient="horizontal")`: Alias for `make_separator`.

### 3.4. Debug Utilities
* `debug_dump_button_styles()`: Prints all registered button styles and their configuration to stdout. Useful for verifying theme application.

### 3.5. Style Key Naming Guarantees
The framework's G01b generator produces stable, deterministic naming patterns for all styles to ensure robust caching.
* **Pattern:** `[Category]_[Variant]_[Params...]`
* **Example:** `Control_BUTTON_PRIMARY_fg_TEXT_WHITE_bg_PRIMARY_norm_MID...`
* **Guarantee:** Calling a resolver with the exact same parameters will always return the exact same style name string, preserving Tkinter resource limits.

---

## 4. G02b — Layout Utilities

**Module:** `gui.G02b_layout_utils`

These utilities replace raw geometry calls, enforcing the design system's spacing grid.

### `layout_row(parent, weights=(1,), min_height=0)`
Creates a container frame pre-configured as a grid row.
* **Returns:** `ttk.Frame` (configured parent)

### `layout_col(parent, weights=(1,), min_width=0)`
Creates a container frame pre-configured as a grid column.
* **Returns:** `ttk.Frame`

### `stack_vertical(parent, widgets, spacing=0, anchor="w", fill="x")`
Packs a list of widgets vertically with consistent spacing.
* **Returns:** `None`

### `stack_horizontal(parent, widgets, spacing=0, side="left", ...)`
Packs a list of widgets horizontally.
* **Returns:** `None`

### `grid_configure(container, column_weights=None, row_weights=None)`
Applies weight configuration to an existing container.
* **Returns:** `None`

### `fill_remaining(container, row=None, column=None, weight=1)`
Configures a specific row or column to expand and fill available space.
* **Returns:** `None`

### `center_in_parent(widget, parent, row=0, column=0)`
Centers a widget within its parent using grid geometry.
* **Returns:** `None`

### `apply_padding(widget, padx=None, pady=None, method="pack")`
Updates the padding of an already-placed widget.
* **Returns:** `None`

---

## 5. G02c — Base Window

**Module:** `gui.G02c_gui_base`

The mandatory base class for all applications.

### Class: `BaseWindow`

#### `__init__(title="App", width=800, height=600, ...)`
Initialises the Tk root, configures the theme, and establishes the scrollable content/canvas system.

#### `build_widgets()`
**Abstract Method.** Must be overridden by subclasses.
* **Note:** Widgets must be parented to `self.main_frame`, not `self.root`.

#### `center_window()`: Centers window on screen.
#### `toggle_fullscreen()`: Toggles fullscreen mode.
#### `bind_scroll_widget(widget)`: Links a widget's scroll events to the main window.
#### `safe_close()`: Destroys window safely.
#### `run()`: Starts the main event loop.

#### Attributes
* `self.root`: The `tk.Tk` instance.
* `self.main_frame`: The scrollable `ttk.Frame`.

---

## 6. G03 — Patterns & Components

G03 modules compose primitives into higher-order structures. These functions return **Structured Result Types** (Dataclasses) to provide access to internal elements.

### 6.1. Structured Result Types

#### `FormResult`
Returned by form builders.
    @dataclass
    class FormResult:
        frame: ttk.Frame              # The container widget
        fields: dict[str, tk.Widget]  # Access to widget instances
        variables: dict[str, tk.Variable] # Access to bound variables

#### `TableResult`
Returned by table builders.
    @dataclass
    class TableResult:
        frame: ttk.Frame
        treeview: ttk.Treeview
        scrollbar_y: ttk.Scrollbar | None
        scrollbar_x: ttk.Scrollbar | None

#### `FilterBarResult`
Returned by the filter bar component.
    @dataclass
    class FilterBarResult:
        frame: ttk.Frame
        filters: dict[str, tk.Widget]
        variables: dict[str, tk.Variable]
        search_button: ttk.Button
        clear_button: ttk.Button | None

#### `MetricCardResult`
Returned by metric components.
    @dataclass
    class MetricCardResult:
        frame: ttk.Frame
        value_label: ttk.Label
        title_label: ttk.Label
        subtitle_label: ttk.Label | None

### 6.2. G03a — Layout Patterns

**Module:** `gui.G03a_layout_patterns`

* `page_layout(parent, padding=SPACING_MD)`: Returns a standard page container.
* `header_content_footer_layout(...)`: Returns `(outer, header, content, footer)`.
* `two_column_layout(parent, left_weight=1, right_weight=1)`: Returns `(outer, left_frame, right_frame)`.
* `three_column_layout(parent, weights=(1,2,1))`: Returns `(outer, left, center, right)`.
* `sidebar_content_layout(...)`: Returns `(outer, sidebar, content)`.
* `section_with_header(...)`: Returns `(outer, header, content)`.
* `toolbar_content_layout(...)`: Returns `(outer, toolbar, content)`.
* `button_row(parent, alignment="right")`: Returns a frame configured for button placement.
* `form_row(parent, label_width=120)`: Returns `(row, label, input)`.
* `split_row(parent, weights=(1,1))`: Returns `(row, list_of_cols)`.

### 6.3. G03b — Container Patterns

**Module:** `gui.G03b_container_patterns`

* `card(parent, role, ...)`: Returns a `ttk.Frame` with card styling.
* `panel(parent, role, ...)`: Returns a `ttk.Frame` with panel styling.
* `section(parent, role, ...)`: Returns a `ttk.Frame` with section styling.
* `surface(parent, role, ...)`: Returns a `ttk.Frame` with surface styling.
* `titled_card(parent, title, ...)`: Returns `(card_frame, content_frame)`.
* `titled_section(parent, title, ...)`: Returns `(section_frame, content_frame)`.
* `page_header(parent, title, subtitle)`: Returns a header frame.
* `page_header_with_actions(...)`: Returns `(header, actions_frame)`.
* `section_header(parent, title)`: Returns a header frame.
* `alert_box(parent, message, role)`: Returns a pre-populated alert frame.
* `status_banner(parent, message, role)`: Returns a full-width banner frame.

### 6.4. G03c — Form Patterns

**Module:** `gui.G03c_form_patterns`

* `form_group(parent, fields: list[FormField])`: Creates a set of labelled inputs.
    * **Returns:** `FormResult`
* `form_section(parent, title, fields)`: Creates a titled section containing a form group.
    * **Returns:** `FormResult`
* `form_field_entry(parent, label, ...)`: Returns `(row_frame, entry, variable)`.
* `form_field_combobox(...)`: Returns `(row, combobox, variable)`.
* `form_field_spinbox(...)`: Returns `(row, spinbox, variable)`.
* `form_field_checkbox(...)`: Returns `(row, checkbox, variable)`.
* `form_button_row(parent, buttons, alignment)`: Returns `(row, dict_of_buttons)`.
* `validation_message(parent)`: Returns `(label, show_func, hide_func)`.

### 6.5. G03d — Table Patterns

**Module:** `gui.G03d_table_patterns`

* `create_table(parent, columns: list[TableColumn], ...)`: Creates a Treeview with scrollbar.
    * **Returns:** `TableResult`
* `create_table_with_horizontal_scroll(...)`: Creates table with X and Y scrollbars.
    * **Returns:** `TableResult`
* `create_table_with_toolbar(...)`: Returns `(outer, toolbar, TableResult)`.
* `create_zebra_table(...)`: Returns `TableResult` (configured for striping).
* `insert_rows(treeview, rows)`: Returns list of item IDs.
* `insert_rows_zebra(treeview, rows)`: Inserts and stripes rows.
* `apply_zebra_striping(treeview)`: Re-applies zebra striping tags to all current rows (useful after sorting).
* `get_selected_values(treeview)`: Returns list of values.
* `clear_table(treeview)`: Clears all rows.

### 6.6. G03e — Widget Components

**Module:** `gui.G03e_widget_components`

* `filter_bar(parent, filters: list[dict])`: Generates a search/filter row.
    * **Returns:** `FilterBarResult`
* `search_box(parent, placeholder, on_search)`: Returns `(frame, entry, variable)`.
* `metric_card(parent, title, value, ...)`: Displays a KPI with visual emphasis.
    * **Returns:** `MetricCardResult`
* `metric_row(parent, metrics: list)`: Returns `(row_frame, list_of_results)`.
* `dismissible_alert(parent, message, role)`: Returns `(alert_frame, dismiss_func)`.
* `toast_notification(parent, message, duration)`: Shows a transient message.
* `empty_state(parent, title, message)`: Returns a centered placeholder frame.
* `action_header(parent, title, actions)`: Returns `(header_frame, buttons_dict)`.