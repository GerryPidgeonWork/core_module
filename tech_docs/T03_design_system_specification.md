# T03 — Module Responsibilities & Dependency Specification v1.0

## 1. Purpose and Authority

This document defines the strict module-level responsibilities and the dependency graph for the GUI Framework. It governs how modules interact, what they may import, and how responsibilities are divided across layers.

While **T02 Architecture** defines the high-level conceptual layers, **T03** defines *per-module* rules used by linters, reviewers, and automated audit tools.

---

## 2. Module Responsibilities

The framework is composed of five tightly scoped layers: **G00**, **G01**, **G02**, **G03**, and **G04**.

---

### 2.1. G00 — Package Hub

**Scope:** Centralisation of all external GUI dependencies.

| Module                   | Responsibilities                                                                                                                                                           | Output                                                                            |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **G00a_gui_packages.py** | • Sole importer of `tkinter` and `ttk`<br>• Windows theme init (`init_gui_theme`)<br>• Manages optional libs (`ttkbootstrap`, `tkcalendar`)<br>• Provides system utilities | • `tk`, `ttk` namespaces<br>• Initialisation helpers<br>• Optional widget classes |

---

### 2.2. G01 — Design System

**Scope:** Defines the *visual language* of the framework. **Non-visual layer**: does **not** create widgets.

| Module                       | Responsibilities                                                                       | Output                       |
| ---------------------------- | -------------------------------------------------------------------------------------- | ---------------------------- |
| **G01a_style_config.py**     | • Defines immutable design tokens<br>• Colours, fonts, spacing                         | • Token dictionaries         |
| **G01b_style_base.py**       | • Font creation + caching<br>• Style cache key generation<br>• Colour family utilities | • Font names<br>• Cache keys |
| **G01c_text_styles.py**      | • Resolves text styles                                                                 | • `ttk.Style` names          |
| **G01d_container_styles.py** | • Styles for frames, cards, panels                                                     | • `ttk.Style` names          |
| **G01e_input_styles.py**     | • Styles for Entry, Combobox, Spinbox                                                  | • `ttk.Style` names          |
| **G01f_control_styles.py**   | • Styles for Buttons, Checkboxes, Toggles<br>• Stateful variants (hover, focus)        | • `ttk.Style` names          |

---

### 2.3. G02 — Primitives & BaseWindow

**Scope:** Runtime implementation. **Only layer allowed to instantiate widgets.**

| Module                        | Responsibilities                                                                                                                                            | Output                 |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| **G02a_widget_primitives.py** | • Widget factories (`make_*`)<br>• Consumes G01 styles<br>• Implements **Treeview defaults, zebra tags, layout fixes**<br>• Applies default widget bindings | • Configured widgets   |
| **G02b_layout_utils.py**      | • Layout helpers (`layout_row`, `stack_vertical`)<br>• Enforces spacing tokens                                                                              | • Layout configuration |
| **G02c_gui_base.py**          | • `BaseWindow` shell<br>• Root window ownership<br>• Scroll engine                                                                                          | • `BaseWindow` class   |

---

### 2.4. G03 — Patterns

**Scope:** UI Composition. Builds reusable structures out of G02 primitives.

| Module                         | Responsibilities                                                                                                                                                                     | Output              |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- |
| **G03a_layout_patterns.py**    | • Page layouts (sidebar, toolbar, header/footer)                                                                                                                                     | • Layout frames     |
| **G03b_container_patterns.py** | • Semantic containers (Card, Panel, Section, Alert)                                                                                                                                  | • Styled containers |
| **G03c_form_patterns.py**      | • Field groups, form sections, validation labels                                                                                                                                     | • `FormResult`      |
| **G03d_table_patterns.py**     | • Table & Treeview composition<br>• Toolbars<br>• Zebra striping logic<br>**• Must use G02a factories exclusively for Treeviews**<br>**• Must never apply colours using G01 tokens** | • `TableResult`     |
| **G03e_widget_components.py**  | • Composite components (Filter Bar, Metric Cards, Alerts)                                                                                                                            | • Component results |

> **Important:** Application Pages belong in `app/` or `G05`, not in G03.

---

### 2.5. G04 — Application Infrastructure

**Scope:** Behavioural Control Plane. No GUI imports or widgets.

| Module                 | Responsibilities                                               | Output            |
| ---------------------- | -------------------------------------------------------------- | ----------------- |
| **G04a_navigation.py** | • Route registry<br>• Navigation stack<br>• Page instantiation | • Routing logic   |
| **G04b_app_state.py**  | • Immutable state store<br>• Subscriptions                     | • App state       |
| **G04c_event_bus.py**  | • Publish–Subscribe messaging                                  | • Event bus       |
| **G04d_services.py**   | • Backend service registry<br>• Async operations               | • Services        |
| **G04e_lifecycle.py**  | • Boot sequence<br>• Shutdown<br>• Global exception handling   | • Lifecycle hooks |
| **G04f_context.py**    | • Dependency Injection<br>• Bundles Nav, State, Events         | • `AppContext`    |

---

## 3. Allowed Imports & Dependency Matrix

| Layer   | Allowed Imports                                             | Forbidden Imports                 |
| ------- | ----------------------------------------------------------- | --------------------------------- |
| **G00** | Stdlib GUI imports (`tkinter`, `ttk`, `sys`), optional libs | G01–G04                           |
| **G01** | G00, sibling G01 modules                                    | G02, G03, G04, widget creation    |
| **G02** | G00 via hub, G01 tokens/resolvers, sibling G02              | G03, G04, raw `import tkinter`    |
| **G03** | G00 via hub, G02 primitives, sibling G03                    | **G01**, G04, raw ttk/tk calls    |
| **G04** | Stdlib (non-GUI), Page classes                              | G00, G01, G02, G03, GUI libraries |

### Clarifications

1. **G03 →❌ G01:** Patterns must not access tokens; pass semantic roles to G02 instead.
2. **G02 imports GUI only via G00a.** Direct tkinter imports are forbidden.
3. **G04 may reference Page classes** but never GUI layers.

---

## 4. Module Invariants

### G01 — Design System

1. No widget creation.
2. Pure functions only.
3. Immutable tokens.
4. **Treeview colours, zebra striping, and layout adjustments belong in G02a only.**

### G02 — Primitives

1. Only layer allowed to instantiate widgets.
2. Must resolve styles using G01 before widget creation.
3. `BaseWindow` owns the root window.

### G03 — Patterns

1. No raw geometry — must call layout utilities.
2. Must return dataclasses.
3. Never configure `ttk.Style`.
4. **Must use `make_treeview` / `make_zebra_treeview` for all Treeviews.**

### G04 — Infrastructure

1. Cannot import GUI libraries.
2. No widgets or styles.
3. No geometry logic.
4. Behavioural flow only.

---

## 5. Cross-Layer Dependency Diagram

```
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

---

## 6. Deprecated Modules (Prohibited)

The following modules from previous iterations are **forbidden**:

* `G04b_app_menu`
* `G04c_app_state` (old)
* `G04d_app_controller`

---

## 7. Layout Philosophy

All layout must use **G02b** utilities.

* Explicit spacing using tokens.
* Consistent grid structure.
* No direct `.grid()` / `.pack()` calls inside patterns.

---

## 8. Naming Conventions

| Object Type | Pattern                            | Layer |
| ----------- | ---------------------------------- | ----- |
| Resolvers   | `resolve_[widget]_style`           | G01   |
| Style Keys  | `[Category]_[Variant]_[Params...]` | G01   |
| Factories   | `make_[widget]`                    | G02   |
| Layouts     | `layout_[type]` / `stack_[dir]`    | G02b  |
| Patterns    | `[noun]` / `[noun]_[type]`         | G03   |
| Services    | `[Domain]Service`                  | G04d  |
| Context     | `AppContext`                       | G04f  |
| Results     | `[Component]Result`                | G03   |
