# GUI Framework Architecture Specification v1.0

## 1. Purpose and Authority

This document defines the authoritative architectural specification for the GUI Framework. It establishes the structural rules, layer boundaries, dependency constraints, and runtime invariants that govern the system.

This specification serves as the primary reference for maintaining architectural integrity. Any code implementation or extension that contradicts the rules defined herein is considered an architectural violation.

---

## 2. High-Level Overview

The GUI Framework implements a **Strictly Layered Architecture** designed to decouple visual design from runtime behaviour and application logic. The system is composed of four implementation layers (G00–G03) and a behavioural infrastructure layer (G04).

### Core Architectural Principles

1. **Unidirectional Flow:** Dependencies strictly flow downwards. Higher-level layers consume lower-level primitives; lower levels never reference higher levels.
2. **Code is Truth:** The codebase is the single source of truth. Documentation describes the intent, but the implementation defines the reality.
3. **Idempotent Styling:** Style resolution is deterministic and cached. Requesting the same semantic parameters twice yields the exact same underlying `ttk.Style`.
4. **Separation of Design and Runtime:** The Design System (G01) defines *what* the interface looks like but is strictly forbidden from creating widgets. The Primitives layer (G02) creates widgets but must not define styles locally.
5. **Separation of Behaviour and UI:** The Application Infrastructure (G04) defines *how* the application behaves (state, navigation, events) but contains **zero** widget creation, layout code, or style definitions.

---

## 3. Architectural Layers

The framework is organised into distinct layers, each with specific responsibilities and restricted boundaries.

### 3.1. G00 — Package Hub

**Role:** The system's boundary interface for external GUI libraries.

**Modules:** `G00a_gui_packages.py`

**Responsibilities:**

* Centralises all imports for `tkinter` and `ttk`.
* Implements the critical `init_gui_theme()` fix to ensure consistent rendering on Windows platforms.
* Provides optional hooks for third-party libraries (e.g., `tkcalendar`).

**Invariants:**

* Must never create a root window as a side effect of importing.
* Must be the only module in the system that imports `tkinter` directly.

---

### 3.2. G01 — Design System

**Role:** The single source of truth for visual definitions.

**Modules:** `G01a` (Tokens), `G01b` (Utilities), `G01c`–`G01f` (Resolvers).

**Responsibilities:**

* Defines immutable design tokens (Colours, Typography, Spacing).
* Implements Style Resolvers that transform semantic parameters into registered `ttk.Style` names.
* Manages the **Style Cache** and **Font Cache**.

**Caching Boundaries:**

* All caching of visual assets (fonts, style names) must occur within G01.
* G02 and G03 must not implement their own visual caches.

**Invariants:**

* Must never instantiate a widget.
* Must never import G02 or G03.
* Must never contain layout logic.

---

### 3.3. G02 — Primitives & Shell

**Role:** The runtime implementation layer that creates concrete UI objects.

**Modules:** `G02a` (Factories), `G02b` (Layouts), `G02c` (Window Shell).

**Responsibilities:**

* **Factories (G02a):** Functions that consume G01 style strings to create and configure `ttk` widgets.
* **Layouts (G02b):** Pure geometric helpers that wrap `pack` and `grid` to enforce consistent spacing and alignment.
* **Window Shell (G02c):** The `BaseWindow` class responsible for the application lifecycle.

**Invariants:**

* **Subclassing Rule:** `BaseWindow` is an abstract shell; applications must subclass it to define `build_widgets()`.
* The only layer allowed to instantiate `tk.Tk()`.
* Must resolve styles via G01 before creating widgets.

---

### 3.4. G03 — Patterns & Components

**Role:** The composition layer that assembles primitives into high-level UI structures.

**Modules:** `G03a` (Layouts), `G03b` (Containers), `G03c` (Forms), `G03d` (Tables), `G03e` (Components).

**Responsibilities:**

* Combines G02 widgets into reusable patterns (e.g., Cards, Form Groups, Filter Bars).
* Returns **Structured Result Objects** (Dataclasses) containing the root frame and internal interactive elements.

**Scroll Engine Constraints:**

* G03 patterns must **not** create their own scrollable frames or canvases. Scrolling is handled by `G02c`.

**Invariants:**

* Must rely exclusively on G02 primitives; never instantiate raw `ttk` widgets directly.
* Must not define or configure `ttk` styles.

---

### 3.5. G04 — Application Infrastructure

**Role:** The behavioural control plane. Orchestrates application lifecycle, data, and flow.

**Modules:**

* `G04a_navigation`
* `G04b_app_state`
* `G04c_event_bus`
* `G04d_services`
* `G04e_lifecycle`
* `G04f_context`

**Responsibilities:**

* Managing non-visual state.
* Determining which G03 Page to show.
* Handling business logic and backend services.

**Invariants:**

* **Non-Visual:** Must never import `tkinter`, `ttk`, or GUI classes.
* **No Widgets:** Must never instantiate widgets or define layouts.
* **No Styling:** Must not reference G01 tokens or style resolvers.
* **Page Objects:** Navigation instantiates Page classes, not widgets.

---

## 4. Dependency Rules

The system enforces a strict acyclic graph for dependencies.

### 4.1. Canonical Dependency Graph

```
G04 (Infrastructure)
↓
G03 (Patterns & Pages)
↓
G02 (Primitives & Layouts)
↓
G01 (Design System)
↓
G00 (Package Hub)
↓
Standard Library (tkinter)
```

---

### 4.2. Forbidden Dependencies

1. **Upward Imports:** G01 must never import G02; G02 must never import G03.
2. **Visual Contamination:** G04 must never import GUI libraries.
3. **Circular Siblings:** Modules within the same layer should avoid cycles.
4. **External Leakage:** Application code must not import `tkinter` directly.

---

### 4.3. Permitted Imports Matrix

| From Layer | May Import        | May NOT Import               |
| ---------- | ----------------- | ---------------------------- |
| **G04**    | G03, Standard Lib | G00a, G01, G02, tkinter/ttk  |
| **G03**    | G02, G00, G03     | G01 (directly), G04, tkinter |
| **G02**    | G01, G00          | G03, G04, raw tkinter        |
| **G01**    | G00, G01          | G02, G03, G04                |
| **G00**    | Standard Library  | Any Framework Module         |

---

### 4.4. Rationale

Skipping architectural layers creates visual inconsistency, logic duplication, and tight coupling, which makes testing and maintenance significantly harder.

---

## 5. System Invariants

### 5.1. Single Root Window

Only one `tk.Tk()` instance may exist at runtime, created exclusively by `BaseWindow` in G02c.

### 5.2. Mandatory Theme Initialisation

`init_gui_theme()` must be called immediately after root creation. G02c is responsible for this.

### 5.3. The Factory Pattern

All widgets must be created via G02a factory functions.

### 5.4. Structured Return Types

G03 patterns must return structured objects exposing both the container and child elements.

### 5.5. Allowed Side Effects

| Module   | Allowed          | Forbidden                    |
| -------- | ---------------- | ---------------------------- |
| **G00**  | import stdlib    | create root window           |
| **G01**  | define constants | create widgets               |
| **G02c** | create root      | global-scope creation        |
| **G03**  | none             | raw `ttk` calls              |
| **G04**  | define state     | widget creation, GUI imports |

---

## 6. Runtime Lifecycles

### 6.1. Application Startup

1. Boot via `G04e_lifecycle.boot()`.
2. Initialise Event Bus, State Engine, and Services.
3. Create `BaseWindow`.
4. Assemble Context.
5. Resolve initial route via G04a.
6. Instantiate G03 page class.
7. `build_widgets()` renders the UI.
8. Event loop begins.

---

### 6.2. Style Resolution Pipeline

1. G02 factory receives parameters.
2. Delegates to G01 resolver.
3. Resolver fetches Tokens and Utilities.
4. Deterministic cache key is generated.
5. Cache is checked.
6. Style is registered if needed.
7. Returned style name applied to widget.

---

### 6.3. Widget Construction Flow

* **Semantic Mode:** `make_frame(role="PRIMARY")` → G01d → Style
* **Direct Mode:** `make_frame(bg_colour=X)` → G01d → Style

All flows MUST pass through G01.

---

### 6.4. Runtime Pipeline Diagram

```
[ Application Entry (G04e) ]
      │
      ▼
[ G04a Navigation ] → inject context → [ G03 Page Class ]
      │                                     │
      ▼                                     ▼
[ G02c BaseWindow ] ← mount frame ← [ G03 Pattern ]
      │                                     │
 init theme                                 request widget
      ▼                                     ▼
[ G00a Package Hub ] → [ G02a Factory ] → [ G01 Resolver ] → [ G01a Tokens ]
```

---

## 7. Layout Philosophy

All layout operations must use G02b utilities.

* **Explicit Spacing:** Uses spacing tokens.
* **Grid Consistency:** Prevents unstable layouts.
* **Pack Discipline:** Prevents inconsistent spacing.

Patterns must never call `.grid()` or `.pack()` directly.

---

## 8. Naming Conventions

| Object Type    | Naming Pattern                     | Layer |
| -------------- | ---------------------------------- | ----- |
| **Resolvers**  | `resolve_[widget_type]_style`      | G01   |
| **Style Keys** | `[Category]_[Variant]_[Params...]` | G01   |
| **Factories**  | `make_[widget_type]`               | G02   |
| **Layouts**    | `layout_[type]`, `stack_[dir]`     | G02b  |
| **Patterns**   | `[noun]`, `[noun]_[type]`          | G03   |
| **Services**   | `[Domain]Service`                  | G04d  |
| **Context**    | `AppContext`                       | G04f  |
| **Results**    | `[Component]Result`                | G03   |
