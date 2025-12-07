# T06 — GUI Framework Cheat Sheet v1.0

## 1. At a Glance

| Layer    | Responsibility       | Key Rule                                                              |
| :------- | :------------------- | :-------------------------------------------------------------------- |
| **G00**  | **Package Hub**      | Import `tk`, `ttk` from here. **Never** import `tkinter` directly.    |
| **G01**  | **Design System**    | Defines tokens & styles. **Never** creates widgets.                   |
| **G02a** | **Widget Factories** | **Sole creator** of widgets. Automatically resolves styles via G01.   |
| **G02b** | **Layout Utils**     | Manages geometry. **Never** use raw pixel padding in app code.        |
| **G02c** | **BaseWindow**       | Manages Root & Scroll Engine. **Always** subclass this.               |
| **G03**  | **Patterns**         | Composes G02 widgets. Returns **Result Dataclasses**, not raw frames. |

**Golden Rule:** Never instantiate `ttk.Widget` directly. Always use `make_*` factories.

---

## 2. Tokens & Naming (G01)

### Visual Tokens

| Category        | Tokens                                                                  | Context                            |
| :-------------- | :---------------------------------------------------------------------- | :--------------------------------- |
| **Colours**     | `PRIMARY`, `SECONDARY`, `SUCCESS`, `WARNING`, `ERROR`, `TEXT`           | Passed via `role=` or `variant=`   |
| **Shades**      | `LIGHT`, `MID`, `DARK`, `XDARK`                                         | Used via `fg_shade=` / `bg_shade=` |
| **Text Shades** | `BLACK`, `WHITE`, `GREY`                                                | Foreground text shading            |
| **Type Scale**  | `DISPLAY` (20), `HEADING` (16), `TITLE` (14), `BODY` (11), `SMALL` (10) | Typography scale                   |
| **Spacing**     | `XS`, `SM`, `MD`, `LG`, `XL`, `XXL`                                     | Used for padding & gaps            |
| **Borders**     | `NONE`, `THIN`, `MEDIUM`, `THICK`                                       | Border thickness                   |

### Semantic Kinds

| Kind        | Use Case                         |
| :---------- | :------------------------------- |
| **SURFACE** | Neutral background, no border    |
| **CARD**    | Grouped content with relief      |
| **PANEL**   | Tools/sidebars with solid border |
| **SECTION** | Logical grouped content, flat    |

---

## 3. Widget Factories (G02a)

**Import:** `from gui.G02a_widget_primitives import ...`

* `make_label(parent, text="", size="BODY", fg_shade="BLACK", bg_colour=None, bg_shade=None, bold=False, ...)`
* `make_button(parent, text="", command=None, widget_type="BUTTON", variant="PRIMARY", fg_colour=None, fg_shade="BLACK", ...)`
* `make_entry(parent, textvariable=None, control_type="ENTRY", role="SECONDARY", shade="LIGHT", border="THIN", padding="SM")`
* `make_frame(parent, kind="SURFACE", role="SECONDARY", shade="LIGHT", padding="MD", border="THIN", relief="flat", ...)`
* `make_combobox(parent, values=[], role="SECONDARY", shade="LIGHT", border="THIN", padding="SM")`
* `make_spinbox(parent, from_=0, to=100, role="SECONDARY", shade="LIGHT", border="THIN", padding="SM")`
* `make_checkbox(parent, text="", variable=None, command=None, variant="PRIMARY")`
* `make_radio(parent, text="", value="", command=None, variant="PRIMARY")`
* `make_textarea(parent, width=40, height=10, wrap="word")` *(Returns `tk.Text`)*
* `make_separator(parent, orient="horizontal")`
* `make_spacer(parent, width=0, height=0)`

---

## 4. Style Wrappers (G02a)

Return **style name strings** only.

* `label_style(fg_colour, fg_shade, bg_colour, bg_shade, size, bold, ...)`
* `frame_style(role, shade, kind, border, padding, relief, ...)`
* `button_style(widget_type, variant, fg_colour, fg_shade, ...)`
* `entry_style(control_type, role, shade, border, padding)`

### Shortcuts

* `button_primary()`, `button_success()`, `button_error()`
* `frame_style_card()`, `frame_style_panel()`, `frame_style_surface()`
* `entry_style_default()`, `entry_style_error()`, `entry_style_success()`
* `label_style_heading()`, `label_style_body()`, `label_style_small()`

---

## 5. Typography Helpers (G02a)

* `page_title(parent, text, fg_colour=None, fg_shade="BLACK")` — DISPLAY/Bold
* `section_title(parent, text, fg_colour=None, fg_shade="BLACK")` — HEADING/Bold
* `page_subtitle(parent, text, fg_colour=None, fg_shade="GREY")` — TITLE/Normal
* `body_text(parent, text, fg_colour=None, fg_shade="BLACK")` — BODY/Normal
* `small_text(parent, text, fg_colour=None, fg_shade="BLACK")` — SMALL/Normal
* `meta_text(parent, text, fg_colour=None, fg_shade="GREY")` — SMALL/Grey
* `divider(parent, orient="horizontal")` — Separator

### Treeview and Table Factories (G02a Exclusive Ownership)

* **`make_treeview(parent, columns, ...)`**  
  Creates a styled `ttk.Treeview`.  
  G02a exclusively configures:
  - `rowheight`
  - `background` & `fieldbackground`
  - structural layout (`Treeview.treearea`)
  - state maps (selected row colours)

* **`make_zebra_treeview(parent, columns, odd_bg=..., even_bg=...)`**  
  Creates a Treeview with **predefined `"odd"` and `"even"` tags**.  
  These tags use G01 tokens but are applied **only in G02a**.  
  **G03d must use this factory for all striped tables.**


---

## 6. Layout Utilities (G02b)

**Import:** `from gui.G02b_layout_utils import ...`

* `layout_row(parent, weights=(1,), min_height=0)`
* `layout_col(parent, weights=(1,), min_width=0)`
* `stack_vertical(parent, widgets, spacing=0, anchor="w", fill="x", expand=False)`
* `stack_horizontal(parent, widgets, spacing=0, side="left", anchor="w", fill="x", expand=False)`
* `grid_configure(container, column_weights, row_weights)`
* `fill_remaining(container, row, column, weight=1)`
* `center_in_parent(widget, parent, row=0, column=0)`
* `apply_padding(widget, padx, pady, method="pack")`

---

## 7. Base Window API (G02c)

**Import:** `from gui.G02c_gui_base import BaseWindow`

```python
class MyApp(BaseWindow):
    def build_widgets(self):
        # Parent everything to self.main_frame
        pass
```

### Methods

* `__init__(title="App", width=800, height=600, min_width=400, resizable=(True, True))`
* `init_gui_theme()` — Called automatically
* `center_window()`
* `toggle_fullscreen(event=None)`
* `bind_scroll_widget(widget)`
* `safe_close()`
* `run()`

---

## 8. Pattern Library (G03)

### G03a — Layout Patterns

* `page_layout(parent, padding=SPACING_MD)` → Frame
* `header_content_footer_layout(parent, ...)` → (outer, header, content, footer)
* `two_column_layout(parent, left_weight=1, right_weight=1, gap=SPACING_MD)` → (outer, left, right)
* `three_column_layout(parent, weights=(1,2,1), gap=SPACING_MD)` → (outer, left, center, right)
* `sidebar_content_layout(parent, sidebar_width=200, side="left", gap=SPACING_MD)` → (outer, sidebar, content)
* `section_with_header(parent, header_padding=SPACING_SM, content_padding=SPACING_MD)` → (outer, header, content)
* `toolbar_content_layout(parent, toolbar_height=40, ...)` → (outer, toolbar, content)
* `button_row(parent, align="right", spacing=SPACING_SM)` → Frame
* `form_row(parent, label_w, gap=SPACING_SM)` → (row, label, input)
* `split_row(parent, weights, gap=SPACING_MD)` → (row, list_of_cols)

### G03b — Container Patterns

* `card(parent, role, shade)`, `panel(...)`, `section(...)`, `surface(...)` → Frame
* `titled_card(parent, title, ...)` → (frame, content)
* `titled_section(parent, title, ...)` → (frame, content)
* `page_header(parent, title, subtitle, ...)` → Frame
* `page_header_with_actions(parent, title, subtitle, ...)` → (header_frame, actions_frame)
* `section_header(parent, title)` → Frame
* `alert_box(parent, msg, role="WARNING")` → Frame
* `status_banner(parent, msg, role="PRIMARY")` → Frame

### G03c — Forms

* `form_group(parent, fields=[FormField...])` → **FormResult**
* `form_section(parent, title, fields=[...])` → **FormResult**
* `form_field_entry(parent, label)` → (row, entry, var)
* `form_field_combobox`, `form_field_spinbox`, `form_field_checkbox`
* `form_button_row(parent, buttons)` → (row, buttons_dict)
* `validation_message(parent)` → (label, show_fn, hide_fn)

### G03d — Tables

* `create_table(parent, columns=[TableColumn...])` → **TableResult**
* `create_table_with_horizontal_scroll(...)` → **TableResult**
* `create_table_with_toolbar(...)` → (outer, toolbar, result)
* `create_zebra_table(parent, cols, odd_bg=..., even_bg=...)` → **TableResult**
* `insert_rows(tree, rows)` / `insert_rows_zebra(tree, rows)`
* `apply_zebra_striping(tree)`
* `get_selected_values(tree)` / `clear_table(tree)`

### G03 Treeview Constraints

* G03 **must not style Treeviews**.  
  No direct tag configuration, no direct calls to `style.map`, etc.

* G03d **must only**:
  - call `make_treeview()` or `make_zebra_treeview()`
  - call `insert_rows_zebra()` or `apply_zebra_striping()`
  - never reference `GUI_PRIMARY`, `GUI_SECONDARY`, or any G01 token

* All Treeview runtime behaviour (striping, rowheight, colours) is owned by **G02a**, not G03.

### G03e — Components

* `filter_bar(parent, filters)` → **FilterBarResult**
* `search_box(parent, placeholder)` → (frame, entry, var)
* `metric_card(parent, title, value)` → **MetricCardResult**
* `metric_row(parent, metrics)` → (frame, list[MetricCardResult])
* `dismissible_alert(parent, msg, role)` → (frame, dismiss_fn)
* `toast_notification(parent, msg)` → Frame
* `empty_state(parent, title, msg)` → Frame
* `action_header(parent, title, actions)` → (header, buttons)

---

## 9. Structured Result Types

Always capture these objects to access internal widgets/variables.

```python
@dataclass
class FormResult:
    frame: ttk.Frame
    fields: dict[str, tk.Widget]
    variables: dict[str, tk.Variable]

@dataclass
class TableResult:
    frame: ttk.Frame
    treeview: ttk.Treeview
    scrollbar_y: ttk.Scrollbar | None
    scrollbar_x: ttk.Scrollbar | None

@dataclass
class FilterBarResult:
    frame: ttk.Frame
    filters: dict[str, tk.Widget]
    variables: dict[str, tk.Variable]
    search_button: ttk.Button
    clear_button: ttk.Button | None

@dataclass
class MetricCardResult:
    frame: ttk.Frame
    value_label: ttk.Label
    title_label: ttk.Label
    subtitle_label: ttk.Label | None
```

---

## 10. Quick Examples

### 1. Labelled Entry (Manual)

```python
# Returns: Row Frame, Entry Widget, StringVar
row, entry, var = form_field_entry(parent, "Username", required=True)
row.pack(fill="x")
```

### 2. Two-Column Page

```python
outer, left, right = two_column_layout(self.main_frame, left_weight=1, right_weight=3)
outer.pack(fill="both", expand=True)
card(left, padding="MD").pack(fill="x")
create_table(right, columns=cols).frame.pack(fill="both", expand=True)
```

### 3. Metric Row

```python
metrics = [
    {"title": "Users", "value": "1.2k", "role": "PRIMARY"},
    {"title": "Errors", "value": "0", "role": "SUCCESS"}
]
row, cards = metric_row(parent, metrics)
row.pack(fill="x")
```

---

## 11. Forbidden Patterns ❌

* ❌ `ttk.Button(root, ...)` — **Use `make_button`**
* ❌ `widget.pack(padx=10)` — **Use `stack_vertical` or `SPACING_MD`**
* ❌ `style.configure("MyStyle")` — **Use G01 tokens / G02 wrappers**
* ❌ `import tkinter` — **Use `from gui.G00a_gui_packages import tk`**
* ❌ Logic inside `build_widgets` — **Use Controllers / G04**
* ❌ Creating widgets inside G03 using `ttk.Label` — **G03 must call `make_*` only**
* ❌ `result.treeview.tag_configure("odd", background="#EEE")`  
  → Violates the **G02a Treeview Ownership Rule**.  
  Use `insert_rows_zebra` or `make_zebra_treeview` instead.

## 12. Changelog

### v1.1 — 2025-12-06
* Added the **Treeview Ownership Rule**:  
  G02a now exclusively controls Treeview layout, tag styling, zebra striping, and rowheight.
* Updated G03d constraints:  
  G03d may no longer configure any Treeview colours or tags.
* Updated Factory Reference to include `make_zebra_treeview`.
* Updated Forbidden Patterns to include Treeview styling blocks.
