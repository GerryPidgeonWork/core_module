# T05 — Dependency & Integration Rules (GUI Framework v1.0)

## 1. Purpose

This document establishes the authoritative rules governing module interactions and dependencies within the GUI Framework (G00–G04). The purpose is to enforce **strict architectural boundaries**, ensure **visual consistency**, and prevent **circular dependencies** or **stylistic contamination**. Compliance with these rules guarantees the framework remains modular, testable, and maintainable.

---

## 2. Layer-to-Layer Integration Rules

The framework operates on a **Strict Unidirectional Flow** model where dependencies move only from higher layers (G03, G04) to lower layers (G00, G01).

### 2.1. G00 (Package Hub)

| Rule                 | May Import                                                                  | May Not Import                  | Interaction                                                                                   |
| :------------------- | :-------------------------------------------------------------------------- | :------------------------------ | :-------------------------------------------------------------------------------------------- |
| **G00a Gatekeeping** | Standard Library, `tkinter`, `ttk`, Optional GUI Libs (e.g., `tkcalendar`). | Any Framework Module (G01–G04). | The **sole source** for core GUI libraries. Manages the Windows Theme Fix (`init_gui_theme`). |

---

### 2.2. G01 (Design System)

| Rule                | May Import                                         | May Not Import | Interaction                                                                                                                    |
| :------------------ | :------------------------------------------------- | :------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| **Pure Definition** | G00 (for `ttk.Style` access), Sibling G01 modules. | G02, G03, G04. | Provides design tokens, implements style resolvers, and manages the **Font/Style Cache**. **Forbidden from creating widgets**. |

---

### 2.3. G02 (Primitives & Shell)

| Rule                              | May Import                                                       | May Not Import                 | Interaction                                                                                                                                                                             |
| :-------------------------------- | :--------------------------------------------------------------- | :----------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **G02 Explicit Responsibilities** | G00 (via `G00a`), G01 (Resolvers & Tokens), Sibling G02 modules. | G03, G04, raw `tkinter`/`ttk`. | Acts as the **Runtime Visual Engine**. Performs **all widget creation**, style application, theme validation, and **Treeview structural fixes** (e.g., `Treeview.treearea`, rowheight). |
| **Treeview Ownership Rule**       | (N/A)                                                            | G03, G04.                      | Handles **all Treeview creation, styling, layout configuration, and zebra row colour defaults** exclusively.                                                                            |

---

### 2.4. G03 (Patterns)

| Rule                         | May Import                                                       | May Not Import                     | Interaction                                                                                                                                                       |
| :--------------------------- | :--------------------------------------------------------------- | :--------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **G03 → G02 Factories Rule** | G00 (via `G00a`), G02 (Factories & Utils), Sibling G03 patterns. | **G01** (Forbidden direct access). | **Must rely entirely on G02a factories** (`make_*`) for widget creation. Returns **Structured Result Types** (`TableResult`, `FormResult`, etc.), not raw frames. |
| **Treeview Usage**           | (N/A)                                                            | **G01** (Directly).                | **Must not configure Treeview style maps, tags, or backgrounds**; must use `make_zebra_treeview()` or `insert_rows_zebra()`.                                      |

---

### 2.5. G04 (Infrastructure)

| Rule                       | May Import                                                          | May Not Import      | Interaction                                                                                                              |
| :------------------------- | :------------------------------------------------------------------ | :------------------ | :----------------------------------------------------------------------------------------------------------------------- |
| **Integration Boundaries** | Standard Library (Non-GUI), Application Page Classes (for routing). | G00, G01, G02, G03. | **Non-Visual.** Orchestrates state and navigation. Instantiates Page classes, which then render the UI via G03 patterns. |

---

## 3. Cross-Layer Dependency Matrix (Updated)

This matrix defines the strict import permissions. **(Y)es** indicates permission to import from the column's layer.

| From Layer           | G00 | G01         | G02         | G03         | G04         |
| :------------------- | :-- | :---------- | :---------- | :---------- | :---------- |
| **G04 (Infra)**      | N   | N           | N           | N           | Y (Sibling) |
| **G03 (Patterns)**   | Y   | N           | Y           | Y (Sibling) | N           |
| **G02 (Primitives)** | Y   | Y           | Y (Sibling) | N           | N           |
| **G01 (Design)**     | Y   | Y (Sibling) | N           | N           | N           |
| **G00 (Hub)**        | N   | N           | N           | N           | N           |

---

## 4. Runtime Ownership Rules

| Component                         | Owner (The only module/class permitted to perform this action)                       | Note                                                                               |
| :-------------------------------- | :----------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------- |
| **Root Window Lifecycle**         | `G02c_gui_base.BaseWindow`.                                                          | The sole owner of the `tk.Tk()` instance.                                          |
| **Widget Creation**               | **G02a_widget_primitives.py** (`make_*` factories).                                  | Must consume G01 style strings before creation.                                    |
| **Styling & Theme Validation**    | G01 (Definition) and G02 (Application).                                              | G02c calls `init_gui_theme()` immediately after root creation.                     |
| **Layout Management**             | **G02b_layout_utils.py**.                                                            | G03 must use `layout_row`, `stack_vertical`, etc..                                 |
| **Treeview Structure & Fixes**    | **G02a_widget_primitives.py**.                                                       | Handles the `Treeview.treearea` fix, `rowheight`, and default tags.                |
| **Zebra Tagging**                 | **G02a_widget_primitives.py** (Via `make_zebra_treeview` or tags configured within). | `G03d` calls `insert_rows_zebra()`, which relies on pre-configured tags from G02a. |
| **Result Object Standardisation** | **G03 Layer**.                                                                       | Patterns must return structured dataclasses (`TableResult`, `FormResult`, etc.).   |

---

## 5. Integration Patterns (Best Practices)

The recommended workflow is a single, continuous, unidirectional delegation stream:

1. **Application Layer:** A G03 Page Class (Application Layer) calls a G03 Pattern.
2. **G03 Patterns:** Receives parameters and delegates widget creation to G02 factories.
3. **G02 Primitives:** Consumes semantic parameters, delegates style resolution to G01, creates the widget, and returns the instance to G03.
4. **G01 Design System:** Provides deterministic style string/token lookups, ensuring consistency.

*G04 orchestration interacts only with Page Classes (Application Layer), which are non-visual. G04 never imports or touches a G02 or G03 GUI module directly.*

---

## 6. Anti-patterns (Forbidden Actions)

Any implementation exhibiting the following behaviours constitutes an architectural violation:

* ❌ **Creating Widgets Directly in G03:** `ttk.Treeview(parent, ...)`. (Must use `G02a.make_*` factories)
* ❌ **Styling in G03:** `tree.tag_configure("odd", background="#FF0000")` or defining `ttk.Style` in G03. (Must use `G02a.make_zebra_treeview()`)
* ❌ **Importing G01 in G03:** `from gui.G01a_style_config import GUI_PRIMARY`. (Styling must be delegated to G02)
* ❌ **Raw Imports:** `import tkinter` or `from tkinter import ttk`. (Must use `G00a_gui_packages` exports)
* ❌ **G04 Importing GUI:** `from gui.G03d_table_patterns import create_table`. (G04 must remain GUI-agnostic)
* ❌ **Raw Geometry:** `widget.grid(row=0, padx=10)`. (Must use G02b layout utilities)

---

## 7. Dependency Diagram

```text
[ G04 Infrastructure ]  (Behavioural Control Plane)
        │
        ├──> Instantiates Page Classes (Logic/Routing)
        │
        ▼
[ Application / Page Layer ] (User Code)
        │
        ▼
[ G03 Patterns ]        (Composition Layer)
        │
        ├──> Calls Factories
        │
        ▼
[ G02 Primitives ]      (Runtime Implementation)
        │
        ├──> Resolves Styles
        │
        ▼
[ G01 Design System ]   (Visual Definitions)
        │
        ├──> Configures Theme
        │
        ▼
[ G00 Package Hub ]     (External Interface)
        │
        ▼
[ Python / Tkinter ]    (Standard Library)
```

## 8. Unit-Test Scope Rules

| Layer   | Allowed Scope of Smoke/Unit Tests                                                                         | Note                                                          |
| :------ | :-------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------ |
| **G01** | Test output predictability (cache hits, style name generation) and token immutability.                    | Tests should validate G01 resolvers without creating widgets. |
| **G02** | Test factory output (widget creation) and layout utilities. `G02c_gui_base` owns the window smoke test.   | Must ensure G02a factories apply styles correctly.            |
| **G03** | Test composition (Pattern A assembles Primitives B, C, D correctly) and Structured Return Type integrity. | Tests confirm correct widget assembly and delegation flow.    |
| **G04** | Test state engine, navigation flow, and service connectivity.                                             | Tests must not import or initialize any GUI component.        |

## 9. Changelog for this revision

| Version  | Date           | Changes Introduced                                                                                                                                                                                                                                                                                                                 |
| :------- | :------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **v1.0** | **2025-12-06** | Finalised **Treeview Ownership Rule**: All styling, layout, and tag configuration (including zebra striping) are strictly moved from `G02a_widget_primitives`. `G03d` now relies entirely on G02a factory functions (`make_zebra_treeview`) for Treeview construction. Reinforced the **G03 ↛ G01** forbidden dependency boundary. |
