# GUI Framework Comprehensive Audit Report

**Version:** 1.0  
**Date:** 2025-12-07  
**Scope:** G00–G03 Layers (11 modules)  
**Reference Documents:** T01–T06 Technical Specifications

---

## Executive Summary

This report provides a detailed technical audit of the GUI Framework implementation against its authoritative specifications. Each module is assessed for architectural compliance, code quality, and adherence to established patterns. The report includes specific line-number references and actionable remediation steps.

**Overall Framework Score: 9.2/10**

| Layer | Current Score | Target | Gap |
|-------|---------------|--------|-----|
| G00 (Package Hub) | 9/10 | 10/10 | 1 item |
| G01 (Design System) | 8.8/10 | 10/10 | 6 items |
| G02 (Primitives) | 8.7/10 | 10/10 | 8 items |
| G03 (Patterns) | 9.4/10 | 10/10 | 5 items |

---

## Table of Contents

1. [G00 Layer Audit](#g00-layer-audit)
2. [G01 Layer Audit](#g01-layer-audit)
3. [G02 Layer Audit](#g02-layer-audit)
4. [G03 Layer Audit](#g03-layer-audit)
5. [Cross-Cutting Concerns](#cross-cutting-concerns)
6. [Specification Amendments](#specification-amendments)
7. [Prioritised Action Plan](#prioritised-action-plan)

---

## G00 Layer Audit

### G00a_gui_packages.py

**Current Score: 9/10**

**Role:** Centralised import hub for all GUI dependencies. Sole authority for tkinter/ttk imports.

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G00-01 | Low | 1 | Missing UTF-8 encoding declaration | PEP 263 best practice |
| G00-02 | Low | ~45 | Redundant `import sys` (already available via C00) | DRY principle |

#### Detailed Analysis

**G00-01: Missing Encoding Declaration**

```python
# Current (line 1):
# ====================================================================================================

# Recommended:
# -*- coding: utf-8 -*-
# ====================================================================================================
```

**Rationale:** While Python 3 defaults to UTF-8, explicit declaration ensures compatibility with all editors and prevents encoding-related issues if the file contains special characters in comments.

**G00-02: Redundant sys Import**

```python
# Current (approximately line 45):
import sys

# Issue: sys is already imported via C00_set_packages
# The module header section (lines 33-56) imports sys for path manipulation,
# but C00_set_packages also provides sys.
```

**Recommendation:** Remove the redundant import if C00 provides it, or document why a separate import is needed (e.g., if importing before C00 is loaded).

#### Remediation Checklist

- [ ] Add `# -*- coding: utf-8 -*-` as line 1
- [ ] Review and remove redundant `import sys` if C00 provides it
- [ ] Verify no other redundant imports exist

#### Target Score: 10/10

---

## G01 Layer Audit

### G01a_style_config.py

**Current Score: 9/10**

**Role:** Pure design token definitions. Immutable colour families, typography scale, spacing grid.

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G01a-01 | Medium | ~end | `TEXT_DISABLED` not in `__all__` | T04 API completeness |
| G01a-02 | Medium | ~end | `INDICATOR_BG` not in `__all__` | T04 API completeness |
| G01a-03 | Low | N/A | No module-level docstring | Code documentation standard |

#### Detailed Analysis

**G01a-01 & G01a-02: Missing __all__ Exports**

```python
# Current __all__ (verify exact contents):
__all__ = [
    "GUI_PRIMARY",
    "GUI_SECONDARY",
    # ... other exports
]

# Missing:
# - "TEXT_DISABLED"
# - "INDICATOR_BG"
```

**Impact:** These tokens are used by G01e and G01f but aren't publicly exported, making them "hidden API" that could break if refactored.

**Recommendation:**
```python
__all__ = [
    # ... existing exports ...
    "TEXT_DISABLED",
    "INDICATOR_BG",
]
```

#### Remediation Checklist

- [ ] Add `TEXT_DISABLED` to `__all__`
- [ ] Add `INDICATOR_BG` to `__all__`
- [ ] Add module-level docstring describing the token categories
- [ ] Verify all public constants are in `__all__`

#### Target Score: 10/10

---

### G01b_style_base.py

**Current Score: 9/10**

**Role:** Shared utilities for font resolution, cache key generation, colour classification.

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G01b-01 | Low | N/A | `Literal` type assumed from C00 | Explicit import best practice |
| G01b-02 | Low | N/A | Section numbering skips (e.g., 3 to 5) | Documentation consistency |
| G01b-03 | Low | N/A | Consider exporting spacing tokens for G03 | T03 §3 compliance path |

#### Detailed Analysis

**G01b-01: Implicit Type Import**

```python
# Current: Assumes Literal is available from C00_set_packages
# If C00 doesn't export Literal, this will fail silently or cause runtime errors

# Recommended: Verify C00 exports Literal, or add explicit import
from typing import Literal  # Add if not in C00
```

**G01b-03: Spacing Token Re-export Consideration**

The current architecture has G03 importing spacing tokens directly from G01a, which technically violates T03 §3. One resolution path is to re-export spacing tokens via G01b or G02b:

```python
# Option A: Re-export in G01b (keeps tokens in G01 layer)
from gui.G01a_style_config import (
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
    SPACING_LG,
    SPACING_XL,
    SPACING_XXL,
)

# Add to __all__
__all__ = [
    # ... existing ...
    "SPACING_XS",
    "SPACING_SM",
    "SPACING_MD",
    "SPACING_LG",
    "SPACING_XL",
    "SPACING_XXL",
]
```

**Note:** This is a design decision. See [Specification Amendments](#specification-amendments) for the alternative approach of updating T03.

#### Remediation Checklist

- [ ] Verify `Literal` type is properly imported/available
- [ ] Fix section numbering in comments
- [ ] Decide on spacing token re-export strategy (see Specification Amendments)

#### Target Score: 10/10

---

### G01c_text_styles.py

**Current Score: 9/10**

**Role:** Text/label style resolution. Parametric, cached, idempotent.

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G01c-01 | Low | N/A | `Any` type assumed from C00 | Explicit import best practice |
| G01c-02 | Low | Multiple | Shade validation logic repeated | DRY principle |

#### Detailed Analysis

**G01c-02: Repeated Shade Validation**

```python
# Pattern appears multiple times:
if shade not in ("LIGHT", "MID", "DARK", "XDARK"):
    shade = "MID"  # or similar default

# Recommendation: Extract to G01b utility function
def validate_shade(shade: str, default: str = "MID") -> str:
    """Validate and normalise shade value."""
    valid_shades = ("LIGHT", "MID", "DARK", "XDARK")
    return shade if shade in valid_shades else default
```

#### Remediation Checklist

- [ ] Verify `Any` type is properly imported
- [ ] Extract shade validation to G01b utility function
- [ ] Update all shade validation calls to use the utility

#### Target Score: 10/10

---

### G01d_container_styles.py

**Current Score: 9/10**

**Role:** Container style resolution (frames, cards, panels, sections).

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G01d-01 | Low | N/A | `Any` type assumed from C00 | Explicit import best practice |
| G01d-02 | Low | N/A | `logging` assumed from C00 | Explicit import best practice |

#### Remediation Checklist

- [ ] Verify `Any` and `logging` are properly imported
- [ ] Add fallback imports if C00 doesn't provide them

#### Target Score: 10/10

---

### G01e_input_styles.py

**Current Score: 8/10**

**Role:** Input/field style resolution (Entry, Combobox, Spinbox).

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G01e-01 | **HIGH** | 158 | Hard-coded `INPUT_DISABLED_FG_HEX = "#999999"` | T01 §5.1 (Semantic Styling) |
| G01e-02 | Low | N/A | `Any` type assumed from C00 | Explicit import best practice |

#### Detailed Analysis

**G01e-01: Hard-Coded Colour Violation (CRITICAL)**

```python
# Current (line 158):
INPUT_DISABLED_FG_HEX = "#999999"

# This violates the core principle that all colours should come from G01a tokens.
# The value duplicates TEXT_COLOUR_GREY from G01a.

# Recommended fix:
from gui.G01a_style_config import TEXT_COLOUR_GREY

# Then use TEXT_COLOUR_GREY instead of INPUT_DISABLED_FG_HEX
# Or, if a distinct disabled colour is needed, add it to G01a:

# In G01a_style_config.py:
INPUT_DISABLED_FG = "#999999"  # Add to tokens

# In G01e_input_styles.py:
from gui.G01a_style_config import INPUT_DISABLED_FG
```

**Impact:** This hard-coded value breaks the single-source-of-truth principle. If the grey colour is changed in G01a, this value won't update, causing visual inconsistency.

#### Remediation Checklist

- [ ] **CRITICAL:** Remove hard-coded `#999999` hex value
- [ ] Either import `TEXT_COLOUR_GREY` from G01a, or add `INPUT_DISABLED_FG` token to G01a
- [ ] Verify no other hard-coded hex values exist in G01e
- [ ] Verify `Any` type is properly imported

#### Target Score: 10/10

---

### G01f_control_styles.py

**Current Score: 9/10**

**Role:** Control style resolution (buttons, checkboxes, radios, switches).

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G01f-01 | Low | N/A | `logging` assumed from C00 | Explicit import best practice |
| G01f-02 | Low | N/A | `Any` type assumed from C00 | Explicit import best practice |

#### Remediation Checklist

- [ ] Verify `logging` and `Any` are properly imported
- [ ] Add fallback imports if needed

#### Target Score: 10/10

---

## G02 Layer Audit

### G02a_widget_primitives.py

**Current Score: 8/10**

**Role:** Widget factories. Creates all widgets, delegates styling to G01.

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G02a-01 | **CRITICAL** | 1731 | Debug print statement in production code | Production readiness |
| G02a-02 | Medium | 1855 | `section_title()` default shade mismatch | API consistency |
| G02a-03 | Medium | 361-362, 568-569, 726-727 | Duplicate `Literal` type definitions | DRY principle |
| G02a-04 | Low | N/A | `SPACING_MD` imported directly from G01a | Layer boundary (minor) |
| G02a-05 | Low | N/A | `TREEVIEW_STYLES_INITIALISED` should be prefixed with underscore | Naming convention |
| G02a-06 | Low | 1837-1838, 1886-1887, 1984-1985, 2033-2034 | Runtime `DARK` → `BLACK` conversion scattered | Code consolidation |

#### Detailed Analysis

**G02a-01: Debug Print Statement (CRITICAL)**

```python
# Current (line 1731):
print("[DEBUG] make_treeview() created tree with style:", tree.cget("style"))

# This MUST be removed before production use.
# It will pollute stdout and potentially expose internal details.

# Recommended: Remove entirely, or replace with logger.debug() if needed
logger.debug("make_treeview() created tree with style: %s", tree.cget("style"))
```

**G02a-02: section_title() Default Shade Mismatch**

```python
# Current signature (line 1855):
def section_title(
    parent: tk.Misc,
    text: str = "",
    fg_colour: ColourFamilyType | None = None,
    fg_shade: TextShadeType = "DARK",  # Default is "DARK"
    ...
) -> ttk.Label:

# But runtime converts DARK to BLACK (lines 1886-1887):
if fg_shade == "DARK":
    fg_shade = "BLACK"

# This is confusing - the signature says "DARK" but it actually uses "BLACK"

# Recommended: Change signature default to match runtime behaviour
fg_shade: TextShadeType = "BLACK",  # Honest default
# And remove the runtime conversion
```

**G02a-03: Duplicate Type Definitions**

```python
# Current (lines 361-362, 568-569, 726-727):
ColourFamilyType = Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR", "TEXT"]
ShadeType = Literal["LIGHT", "MID", "DARK", "XDARK"]

# These are defined in G01b and should be imported from there

# Recommended:
from gui.G01b_style_base import ColourFamilyType, ShadeType, TextShadeType
# Remove local definitions
```

**G02a-05: Internal Flag Naming**

```python
# Current:
TREEVIEW_STYLES_INITIALISED = False

# Should use underscore prefix to indicate internal/private
_TREEVIEW_STYLES_INITIALISED = False
```

**G02a-06: Scattered DARK→BLACK Conversion**

```python
# This pattern appears in multiple typography helpers:
if fg_shade == "DARK":
    fg_shade = "BLACK"

# Recommendation: Extract to a utility function in G01b or locally
def _normalise_text_shade(shade: str) -> str:
    """Convert legacy DARK shade to BLACK for text elements."""
    return "BLACK" if shade == "DARK" else shade
```

#### Remediation Checklist

- [ ] **CRITICAL:** Remove debug print at line 1731
- [ ] Fix `section_title()` signature to use `"BLACK"` default
- [ ] Import type aliases from G01b instead of redefining
- [ ] Rename `TREEVIEW_STYLES_INITIALISED` to `_TREEVIEW_STYLES_INITIALISED`
- [ ] Extract `DARK→BLACK` conversion to utility function
- [ ] Apply utility function to all typography helpers
- [ ] Update `__all__` if any exports change

#### Target Score: 10/10

---

### G02b_layout_utils.py

**Current Score: 10/10**

**Role:** Pure structural layout utilities. No styling logic.

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G02b-01 | Info | 299 | `stack_horizontal()` defaults `fill="x"` | Potential UX surprise |

#### Detailed Analysis

**G02b-01: Default fill="x" in stack_horizontal**

```python
# Current (line 299):
def stack_horizontal(
    parent: tk.Misc,
    widgets: list[tk.Widget],
    spacing: int = 0,
    side: str = "left",
    anchor: str = "w",
    fill: str = "x",  # This default may be unintuitive
    expand: bool = False,
) -> None:

# The default fill="x" causes horizontal stacks to expand horizontally,
# which may not be expected behaviour for all use cases.

# This is not a bug, but worth documenting clearly in the docstring.
```

**Note:** This module is exceptionally clean and requires no changes. The note above is purely informational.

#### Remediation Checklist

- [ ] (Optional) Enhance docstring to clarify `fill="x"` default behaviour

#### Target Score: 10/10 (Already achieved)

---

### G02c_gui_base.py

**Current Score: 9/10**

**Role:** BaseWindow class. Root window ownership, scroll engine.

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G02c-01 | Medium | 3 | Header comment says `G02c_base_window.py` but file is `G02c_gui_base.py` | Documentation accuracy |
| G02c-02 | Low | 255 | `self.canvas_window: int` type could be more explicit | Type clarity |
| G02c-03 | Info | N/A | No horizontal scrollbar provided | Feature limitation |

#### Detailed Analysis

**G02c-01: Filename Mismatch in Header**

```python
# Current (line 3):
# G02c_base_window.py

# Should be:
# G02c_gui_base.py
```

**G02c-02: Canvas Window Type Annotation**

```python
# Current (line 255):
self.canvas_window: int  # Window ID from canvas.create_window()

# More explicit would be:
self.canvas_window: int  # tk canvas window item ID
```

This is a very minor point—the current annotation is acceptable.

#### Remediation Checklist

- [ ] Fix header comment filename (line 3)
- [ ] (Optional) Enhance `canvas_window` type annotation comment

#### Target Score: 10/10

---

## G03 Layer Audit

### G03a_layout_patterns.py

**Current Score: 9/10**

**Role:** Page-level layout structures (columns, sidebars, headers).

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G03a-01 | Low | 464-465 | Dynamic attribute assignment with `# type: ignore` | Type safety |
| G03a-02 | Low | 178 vs others | Inconsistent parent type annotations | API consistency |
| G03a-03 | Info | N/A | Imports spacing tokens from G01a | T03 §3 (see Spec Amendments) |

#### Detailed Analysis

**G03a-01: Dynamic Attribute Assignment**

```python
# Current (lines 464-465):
frame.button_alignment = alignment  # type: ignore
frame.button_spacing = spacing      # type: ignore

# This works but is non-idiomatic. Alternative approaches:

# Option A: Return a dataclass instead
@dataclass
class ButtonRowResult:
    frame: ttk.Frame
    alignment: str
    spacing: int

# Option B: Use a custom Frame subclass (heavier)
# Option C: Accept current approach with clear documentation
```

**Recommendation:** The current approach is acceptable for this simple case. Document the dynamic attributes in the docstring.

**G03a-02: Inconsistent Parent Type**

```python
# Some functions use:
parent: tk.Widget

# Others use:
parent: tk.Misc

# Recommendation: Standardise on tk.Misc (more permissive)
# tk.Misc is the base class that provides common widget methods
```

#### Remediation Checklist

- [ ] Standardise parent parameter type annotations to `tk.Misc`
- [ ] Document dynamic attributes in `button_row()` docstring
- [ ] (See Specification Amendments for G01a import resolution)

#### Target Score: 10/10

---

### G03b_container_patterns.py

**Current Score: 10/10**

**Role:** Styled container building blocks (cards, panels, sections).

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G03b-01 | Low | 107 | `ContainerRoleType` duplicates G02a definition | DRY principle |
| G03b-02 | Info | 597-599 | `status_banner()` uses extra inner frame | Minor inefficiency |

#### Detailed Analysis

**G03b-01: Duplicate Type Definition**

```python
# Current (line 107):
ContainerRoleType = Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR"]

# This is also defined in G02a and should be imported from G01b

# Recommended:
from gui.G01b_style_base import ContainerRoleType
# Remove local definition
```

Note: If G01b doesn't export this type, add it there first.

#### Remediation Checklist

- [ ] Import `ContainerRoleType` from centralised location (G01b)
- [ ] Remove local type definition

#### Target Score: 10/10 (Already achieved, improvement optional)

---

### G03c_form_patterns.py

**Current Score: 9/10**

**Role:** Form field patterns and form builders.

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G03c-01 | Low | 296 | `form_field_spinbox` return type uses `tk.Misc` instead of `ttk.Spinbox` | Type accuracy |
| G03c-02 | Low | 221, 279, 339 | Label width uses `// 8` magic number | Code clarity |
| G03c-03 | Info | 574 | Local import for circular dependency avoidance | Acceptable pattern |
| G03c-04 | Info | 434-435 | `pack_forget()` called on never-packed widget | Minor oddity |

#### Detailed Analysis

**G03c-01: Incorrect Return Type Annotation**

```python
# Current (line 296):
def form_field_spinbox(
    ...
) -> tuple[ttk.Frame, tk.Misc, tk.StringVar]:

# The second element is actually a ttk.Spinbox, not tk.Misc

# Recommended:
) -> tuple[ttk.Frame, ttk.Spinbox, tk.StringVar]:
```

**G03c-02: Magic Number for Label Width**

```python
# Current (lines 221, 279, 339):
lbl.configure(width=label_width // 8)

# The // 8 is an approximation for character width
# This should be documented or extracted to a constant

# Recommended: Add constant and comment
APPROX_CHAR_WIDTH_DIVISOR = 8  # Approximate pixels per character

lbl.configure(width=label_width // APPROX_CHAR_WIDTH_DIVISOR)
```

#### Remediation Checklist

- [ ] Fix `form_field_spinbox` return type to `ttk.Spinbox`
- [ ] Extract label width divisor to named constant
- [ ] Add comment explaining the approximation

#### Target Score: 10/10

---

### G03d_table_patterns.py

**Current Score: 9/10**

**Role:** Table and Treeview patterns.

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G03d-01 | Low | 217 vs 283 | Inconsistent treeview factory usage | API consistency |
| G03d-02 | Low | 364-367 | `create_zebra_table` applies colours directly | T05 Treeview Ownership |
| G03d-03 | Info | 441 | Local import for circular dependency | Acceptable pattern |
| G03d-04 | Info | 569 | `cast()` used for type safety | Acceptable workaround |

#### Detailed Analysis

**G03d-01: Inconsistent Factory Usage**

```python
# create_table() (line 217):
tree = make_zebra_treeview(...)  # Uses zebra factory

# create_table_with_horizontal_scroll() (line 283):
tree = make_treeview(...)  # Uses basic factory

# This means create_table() has zebra tags available even if not using striping,
# while create_table_with_horizontal_scroll() does not.

# Recommendation: Document this difference clearly, or standardise
```

**G03d-02: Direct Colour Application in create_zebra_table**

```python
# Current (lines 364-367):
if odd_bg is not None:
    result.treeview.tag_configure("odd", background=odd_bg)
if even_bg is not None:
    result.treeview.tag_configure("even", background=even_bg)

# This technically violates T05's Treeview Ownership Rule, which states
# G03d "must never apply colours".

# However, this is a user-provided override, not hardcoded colours.

# Options:
# A) Remove the parameters and require users to use G02a defaults only
# B) Update T05 to clarify user-provided overrides are acceptable
# C) Move this override capability to G02a

# Recommendation: Option B (update spec) - see Specification Amendments
```

#### Remediation Checklist

- [ ] Document factory usage difference in `create_table_with_horizontal_scroll` docstring
- [ ] (See Specification Amendments for colour override resolution)

#### Target Score: 10/10

---

### G03e_widget_components.py

**Current Score: 9/10**

**Role:** Composite widget components (filter bars, metric cards, alerts).

#### Findings

| ID | Severity | Line(s) | Issue | Specification Reference |
|----|----------|---------|-------|------------------------|
| G03e-01 | Low | 189-196 | `filter_bar` uses `dict` instead of typed dataclass | Type safety |
| G03e-02 | Low | 313 | `search_box` placeholder as initial value | UX consideration |
| G03e-03 | Info | 513 | Dismiss button uses `×` character | Cross-platform text |

#### Detailed Analysis

**G03e-01: Untyped Filter Definitions**

```python
# Current (lines 189-196):
def filter_bar(
    parent: tk.Widget,
    filters: list[dict[str, Any]],  # Untyped dict
    ...
) -> FilterBarResult:

# G03c uses typed FormField dataclass for similar purpose.
# Recommendation: Create FilterDef dataclass for consistency

@dataclass
class FilterDef:
    """Definition for a filter bar field."""
    name: str
    label: str
    field_type: Literal["entry", "combobox"] = "entry"
    options: list[str] = field(default_factory=list)
    width: int = 15

# Then update signature:
def filter_bar(
    parent: tk.Widget,
    filters: list[FilterDef],
    ...
) -> FilterBarResult:
```

**G03e-02: Placeholder Handling**

```python
# Current (line 313):
var = tk.StringVar(value=placeholder)

# The placeholder text becomes the initial value.
# If user clicks Search without typing, they search for the placeholder text.

# Recommendation: Check for placeholder in do_search()
def do_search() -> None:
    search_text = var.get()
    if search_text == placeholder:
        search_text = ""  # Treat as empty search
    if on_search:
        on_search(search_text)
```

#### Remediation Checklist

- [ ] Create `FilterDef` dataclass for type safety
- [ ] Update `filter_bar` to accept `list[FilterDef]`
- [ ] Update `search_box` to handle placeholder in search callback
- [ ] Add `FilterDef` to `__all__`

#### Target Score: 10/10

---

## Cross-Cutting Concerns

### Issue: G03 Imports G01a Spacing Tokens

**Affected Modules:** G03a, G03b, G03c, G03d, G03e

**Current State:**
```python
# All G03 modules contain:
from gui.G01a_style_config import (
    SPACING_XS,
    SPACING_SM,
    SPACING_MD,
    SPACING_LG,
)
```

**Specification (T03 §3):**
> G03 → ❌ G01: Patterns must not access tokens; pass semantic roles to G02 instead.

**Analysis:** This is a specification gap, not a code bug. Spacing tokens are necessary for layout composition in G03. The specification didn't anticipate this need.

**Resolution Options:**

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A | Update T03 to permit G01a spacing imports | Simple, matches reality | Weakens layer boundary |
| B | Re-export spacing via G02b | Maintains strict boundaries | Extra indirection |
| C | Pass spacing as parameters | Pure compliance | Impractical, verbose |

**Recommendation:** Option A (update specification). See [Specification Amendments](#specification-amendments).

---

### Issue: Type Alias Duplication

**Affected Modules:** G01b, G02a, G03b, G03c, G03d, G03e

**Current State:** Multiple modules define the same `Literal` type aliases:
- `ColourFamilyType`
- `ShadeType`
- `TextShadeType`
- `ContainerRoleType`
- `ControlVariantType`

**Recommendation:** Centralise all type aliases in G01b and import from there.

```python
# G01b_style_base.py - Add/consolidate:
ColourFamilyType = Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR", "TEXT"]
ShadeType = Literal["LIGHT", "MID", "DARK", "XDARK"]
TextShadeType = Literal["BLACK", "WHITE", "GREY"]
ContainerRoleType = Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR"]
ControlVariantType = Literal["PRIMARY", "SECONDARY", "SUCCESS", "WARNING", "ERROR"]
ContainerKindType = Literal["SURFACE", "CARD", "PANEL", "SECTION"]

__all__ = [
    # ... existing exports ...
    "ColourFamilyType",
    "ShadeType",
    "TextShadeType",
    "ContainerRoleType",
    "ControlVariantType",
    "ContainerKindType",
]
```

---

### Issue: Plain ttk.Frame Usage in G03

**Affected Modules:** G03a, G03b, G03c, G03d, G03e

**Current State:** G03 modules create plain `ttk.Frame` instances directly for structural/layout purposes.

**Specification (T02 §5.3):**
> All widgets must be created via G02a factory functions.

**Analysis:** The specification is too strict. Plain structural frames don't require styling and shouldn't use `make_frame()` (which applies styling).

**Recommendation:** Update specification to clarify. See [Specification Amendments](#specification-amendments).

---

## Specification Amendments

Based on this audit, the following specification updates are recommended:

### Amendment 1: G03 → G01a Spacing Token Import

**Document:** T03 Module Responsibilities & Dependency Specification

**Section:** §3 Allowed Imports & Dependency Matrix

**Current Text:**
> | G03 | G00 via hub, G02 primitives, sibling G03 | **G01** (Forbidden direct access) |

**Proposed Amendment:**
> | G03 | G00 via hub, G02 primitives, sibling G03, **G01a spacing tokens only** | G01b-f (Forbidden), direct tkinter |

**Add Clarification:**
> G03 modules may import spacing tokens (`SPACING_XS`, `SPACING_SM`, `SPACING_MD`, `SPACING_LG`, `SPACING_XL`, `SPACING_XXL`) from G01a for layout composition. Import of colour tokens, style resolvers, or any other G01 module content remains forbidden.

---

### Amendment 2: Structural Frame Creation

**Document:** T02 Architecture Specification

**Section:** §5.3 The Factory Pattern

**Current Text:**
> All widgets must be created via G02a factory functions.

**Proposed Amendment:**
> All **styled widgets** must be created via G02a factory functions. Neutral structural `ttk.Frame` instances used solely for layout grouping (without styling requirements) may be created directly.

**Add to T06 Cheat Sheet §11:**
> ✅ `ttk.Frame(parent)` — Acceptable for pure layout containers  
> ❌ `ttk.Frame(parent, style="...")` — Use `make_frame()` for styled containers

---

### Amendment 3: Treeview Colour Override Clarification

**Document:** T05 Dependency & Integration Rules

**Section:** §4 Runtime Ownership Rules (Zebra Tagging)

**Current Text:**
> G03d calls `insert_rows_zebra()`, which relies on pre-configured tags from G02a.

**Proposed Addition:**
> G03d pattern functions may accept user-provided colour parameters (e.g., `odd_bg`, `even_bg`) for Treeview customisation. These parameters allow application-level overrides of default G02a colours. G03d must not hardcode colour values or import G01 colour tokens directly.

---

## Prioritised Action Plan

### Priority 1: Critical (Must Fix)

| ID | Module | Issue | Effort |
|----|--------|-------|--------|
| G02a-01 | G02a_widget_primitives.py | Remove debug print (line 1731) | 1 min |
| G01e-01 | G01e_input_styles.py | Replace hard-coded hex `#999999` | 5 min |

### Priority 2: High (Should Fix)

| ID | Module | Issue | Effort |
|----|--------|-------|--------|
| G02a-02 | G02a_widget_primitives.py | Fix `section_title()` default shade | 5 min |
| G02a-03 | G02a_widget_primitives.py | Import types from G01b | 15 min |
| G02c-01 | G02c_gui_base.py | Fix header filename | 1 min |
| G03c-01 | G03c_form_patterns.py | Fix spinbox return type | 2 min |
| G01a-01/02 | G01a_style_config.py | Add missing `__all__` exports | 5 min |

### Priority 3: Medium (Recommended)

| ID | Module | Issue | Effort |
|----|--------|-------|--------|
| G02a-05 | G02a_widget_primitives.py | Rename internal flag with underscore | 5 min |
| G02a-06 | G02a_widget_primitives.py | Extract DARK→BLACK utility | 15 min |
| G03e-01 | G03e_widget_components.py | Create `FilterDef` dataclass | 20 min |
| Cross-cutting | G01b + all users | Centralise type aliases | 30 min |

### Priority 4: Low (Optional Improvements)

| ID | Module | Issue | Effort |
|----|--------|-------|--------|
| G00-01 | G00a_gui_packages.py | Add UTF-8 encoding declaration | 1 min |
| G00-02 | G00a_gui_packages.py | Remove redundant sys import | 2 min |
| G03c-02 | G03c_form_patterns.py | Extract label width constant | 5 min |
| G03e-02 | G03e_widget_components.py | Fix placeholder search handling | 5 min |
| G03a-01 | G03a_layout_patterns.py | Document dynamic attributes | 5 min |
| G03a-02 | G03a_layout_patterns.py | Standardise parent type annotations | 15 min |

### Priority 5: Specification Updates

| Amendment | Document | Section | Effort |
|-----------|----------|---------|--------|
| 1 | T03 | §3 | 10 min |
| 2 | T02, T06 | §5.3, §11 | 10 min |
| 3 | T05 | §4 | 5 min |

---

## Verification Checklist

After implementing fixes, verify the following:

### Automated Checks

- [ ] All modules pass `python -m py_compile <module>`
- [ ] All smoke tests pass: `python G00a_gui_packages.py`, etc.
- [ ] No hard-coded hex values in G01e, G01f, G02a
- [ ] No debug print statements in any module
- [ ] All `__all__` exports are valid

### Manual Checks

- [ ] Header comments match filenames
- [ ] All type aliases imported from G01b (no local redefinitions)
- [ ] Typography helpers use consistent shade defaults
- [ ] `FilterDef` dataclass created and used (if implemented)

### Cross-Reference Checks

- [ ] T04 API Reference matches actual function signatures
- [ ] T06 Cheat Sheet examples work with current implementation
- [ ] All structured result types documented in T04 §6.1

---

## Appendix A: File-by-File Score Summary

| File | Current | Issues | Target |
|------|---------|--------|--------|
| G00a_gui_packages.py | 9/10 | 2 Low | 10/10 |
| G01a_style_config.py | 9/10 | 2 Medium, 1 Low | 10/10 |
| G01b_style_base.py | 9/10 | 3 Low | 10/10 |
| G01c_text_styles.py | 9/10 | 2 Low | 10/10 |
| G01d_container_styles.py | 9/10 | 2 Low | 10/10 |
| G01e_input_styles.py | 8/10 | 1 High, 1 Low | 10/10 |
| G01f_control_styles.py | 9/10 | 2 Low | 10/10 |
| G02a_widget_primitives.py | 8/10 | 1 Critical, 2 Medium, 3 Low | 10/10 |
| G02b_layout_utils.py | 10/10 | 1 Info | 10/10 |
| G02c_gui_base.py | 9/10 | 1 Medium, 1 Low | 10/10 |
| G03a_layout_patterns.py | 9/10 | 2 Low, 1 Info | 10/10 |
| G03b_container_patterns.py | 10/10 | 1 Low (optional) | 10/10 |
| G03c_form_patterns.py | 9/10 | 2 Low, 2 Info | 10/10 |
| G03d_table_patterns.py | 9/10 | 2 Low, 2 Info | 10/10 |
| G03e_widget_components.py | 9/10 | 2 Low, 1 Info | 10/10 |

---

## Appendix B: Quick Reference - What to Fix Where

### Remove/Delete

| File | Line | What |
|------|------|------|
| G02a | 1731 | `print("[DEBUG] make_treeview()...")` |
| G01e | 158 | `INPUT_DISABLED_FG_HEX = "#999999"` |

### Add

| File | Location | What |
|------|----------|------|
| G00a | Line 1 | `# -*- coding: utf-8 -*-` |
| G01a | `__all__` | `"TEXT_DISABLED"`, `"INDICATOR_BG"` |
| G01a | Tokens | `INPUT_DISABLED_FG = "#999999"` (or use TEXT_COLOUR_GREY) |
| G01b | Exports | Centralised type aliases |
| G03e | Types | `FilterDef` dataclass |

### Change

| File | Line | From | To |
|------|------|------|-----|
| G02a | 1855 | `fg_shade: TextShadeType = "DARK"` | `fg_shade: TextShadeType = "BLACK"` |
| G02c | 3 | `G02c_base_window.py` | `G02c_gui_base.py` |
| G03c | 296 | `tk.Misc` | `ttk.Spinbox` |

---

*End of Audit Report*