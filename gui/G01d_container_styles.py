# ====================================================================================================
# G01d_container_styles.py
# ----------------------------------------------------------------------------------------------------
# Container style resolver for frames, cards, panels, and sections.
#
# Purpose:
#   - Provide a parametric, cached container-style engine for the GUI framework.
#   - Turn high-level semantic parameters (role, shade, kind, border, padding)
#     into concrete ttk styles for container widgets (typically ttk.Frame).
#   - Keep ALL container (background/border/padding) styling logic in one place.
#
# Relationships:
#   - G01a_style_config       → pure design tokens (colours, spacing, borders).
#   - G01b_style_base         → shared utilities (colour families, spacing, cache keys).
#   - G01c_text_styles        → text/label styles (separate from containers).
#   - G01d_container_styles   → container style resolution (THIS MODULE).
#
# Design principles:
#   - Single responsibility: only container appearance lives here.
#   - Parametric generation: one resolver, many styles.
#   - Idempotent caching: repeated calls with the same parameters return
#     the same style name.
#   - No raw hex values: ALL colours come from G01a tokens / colour families.
#
# Style naming pattern (via build_style_cache_key in G01b):
#   Container_<KIND>_bg_<FAMILY>_<SHADE>_border_<WEIGHT>_pad_<TOKEN|NONE>
#
#   KIND values (semantic):
#       SURFACE, CARD, PANEL, SECTION
#   FAMILY values:
#       PRIMARY, SECONDARY, SUCCESS, WARNING, ERROR (or any registered family)
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-12-02
# Project:      GUI Framework v1.0
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
from gui.G00a_gui_packages import tk, ttk

# Shared utilities, type aliases, and design tokens from G01b (single source of truth)
from gui.G01b_style_base import (
    # Type aliases
    ShadeType,
    ColourFamily,
    BorderWeightType,
    SpacingType,
    ContainerRoleType,
    ContainerKindType,
    # Utilities
    SPACING_SCALE,
    BORDER_WEIGHTS,
    build_style_cache_key,
    detect_colour_family_name,
    # Design tokens (re-exported from G01a)
    GUI_PRIMARY,
    GUI_SECONDARY,
    GUI_SUCCESS,
    GUI_WARNING,
    GUI_ERROR,
)


# ====================================================================================================
# 4. CONTAINER STYLE CACHE
# ----------------------------------------------------------------------------------------------------
# A dedicated cache for storing all resolved ttk container style names.
#
# Purpose:
#   - Ensure idempotent behaviour: repeated calls with the same parameters
#     return the same style name.
#   - Prevent duplicate ttk.Style registrations.
#   - Act as the single source of truth for created container styles.
# ====================================================================================================
CONTAINER_STYLE_CACHE: dict[str, str] = {}


# ====================================================================================================
# 5. INTERNAL HELPERS
# ----------------------------------------------------------------------------------------------------
# Pure internal utilities supporting container-style resolution.
#
# Purpose:
#   - Construct canonical style names (build_container_style_name).
#   - Resolve border widths and padding tokens into pixel values.
#   - Resolve semantic roles into colour families.
#   - DO NOT create ttk styles or modify global state.
#
# Notes:
#   - detect_colour_family_name() is imported from G01b (single source of truth).
# ====================================================================================================

# Semantic mapping of roles → colour families
CONTAINER_ROLE_FAMILIES: dict[str, ColourFamily] = {
    "PRIMARY": GUI_PRIMARY,
    "SECONDARY": GUI_SECONDARY,
    "SUCCESS": GUI_SUCCESS,
    "WARNING": GUI_WARNING,
    "ERROR": GUI_ERROR,
}


def build_container_style_name(
    kind: str,
    bg_family_name: str,
    bg_shade: str,
    border_weight: str,
    padding_token: str,
) -> str:
    """
    Description:
        Construct the canonical style name for a container widget using the
        shared build_style_cache_key helper from G01b.

    Args:
        kind:
            Container kind token ("SURFACE", "CARD", "PANEL", "SECTION").
        bg_family_name:
            Background colour family name (e.g., "PRIMARY", "SECONDARY").
        bg_shade:
            Background shade token (e.g., "LIGHT", "MID").
        border_weight:
            Border weight token ("NONE", "THIN", "MEDIUM", "THICK").
        padding_token:
            Padding token ("NONE", "XS", "SM", "MD", "LG", "XL", "XXL").

    Returns:
        str:
            Deterministic, human-readable style name.

    Raises:
        None.

    Notes:
        - Uses build_style_cache_key from G01b for consistency.
        - The name encodes semantic intent, not raw hex values.
    """
    return build_style_cache_key(
        "Container",
        kind.upper(),
        f"bg_{bg_family_name}",
        bg_shade.upper(),
        f"border_{border_weight.upper()}",
        f"pad_{padding_token.upper()}",
    )


def resolve_border_width_internal(border: BorderWeightType | None) -> int:
    """
    Description:
        Convert a BorderWeightType token into a numeric pixel border width.

    Args:
        border:
            Border weight token or None.

    Returns:
        int:
            Pixel width (0 for NONE or None).

    Raises:
        KeyError:
            If border is not a valid BORDER_WEIGHTS key.

    Notes:
        - Returns 0 for None or "NONE".
    """
    if border is None or str(border).upper() == "NONE":
        return 0

    token = str(border).upper()
    if token not in BORDER_WEIGHTS:
        raise KeyError(
            f"[G01d] Invalid border token '{token}'. "
            f"Available: {list(BORDER_WEIGHTS.keys())}"
        )

    return BORDER_WEIGHTS[token]


def resolve_padding_internal(padding: SpacingType | None) -> tuple[int, int, str]:
    """
    Description:
        Resolve a spacing token into symmetric (pad_x, pad_y) pixel values and
        a semantic padding label for cache keys.

    Args:
        padding:
            Spacing token ("XS", "SM", "MD", "LG", "XL", "XXL") or None.
            Passing None disables padding entirely.

    Returns:
        tuple[int, int, str]:
            Symmetric padding values (pad_x, pad_y) and a padding label.
            The label will be "NONE" when padding is None.

    Raises:
        KeyError:
            If padding is not a valid SPACING_SCALE key.

    Notes:
        - Passing None returns (0, 0, "NONE").
        - "NONE" is an internal style-token label and is not accepted
          as an input value; use padding=None instead.
    """
    if padding is None:
        return (0, 0, "NONE")

    token = str(padding).upper()
    if token not in SPACING_SCALE:
        raise KeyError(
            f"[G01d] Invalid padding token '{token}'. "
            f"Available: {list(SPACING_SCALE.keys())}"
        )

    px = SPACING_SCALE[token]
    return (px, px, token)


# ====================================================================================================
# 6. CONTAINER STYLE RESOLUTION (PUBLIC API – CORE ENGINE)
# ----------------------------------------------------------------------------------------------------
# The main container-style resolver: resolve_container_style().
#
# Purpose:
#   - Convert high-level semantic parameters (role, shade, kind, border, padding)
#     into concrete ttk container styles.
#   - Apply deterministic naming and idempotent caching.
#   - Register styles with ttk.Style(), including background, border, and padding.
#
# Notes:
#   - This is the ONLY place that creates ttk styles for container widgets.
#   - New in this version: optional bg_colour/bg_shade override, mirroring
#     the flexibility of G01c_text_styles.
# ====================================================================================================
def resolve_container_style(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    kind: ContainerKindType = "SURFACE",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "MD",
    relief: str = "flat",
    *,
    bg_colour: ColourFamily | None = None,
    bg_shade: ShadeType | None = None,
) -> str:
    """
    Description:
        Resolve a complete ttk container style with background, border, padding,
        and relief. Styles are created lazily and cached by a deterministic key.

        This function supports **two modes** of background selection:

        1) Semantic mode (existing behaviour, backwards-compatible):
               role + shade  → background family + shade

        2) Direct family override (new flexible mode):
               bg_colour + bg_shade → background family + shade

        In both cases, style names are built from semantic family names rather
        than raw hex values.

    Args:
        role:
            Semantic colour role. One of: "PRIMARY", "SECONDARY", "SUCCESS",
            "WARNING", "ERROR". Defaults to "SECONDARY".
            Ignored if bg_colour/bg_shade are provided.
        shade:
            Shade within the role's colour family. One of: "LIGHT", "MID",
            "DARK", "XDARK". Defaults to "LIGHT".
            Ignored if bg_colour/bg_shade are provided.
        kind:
            Container kind for semantic naming. One of: "SURFACE", "CARD",
            "PANEL", "SECTION". Defaults to "SURFACE".
        border:
            Border weight token. One of: "NONE", "THIN", "MEDIUM", "THICK",
            or None. Defaults to "THIN".
        padding:
            Internal padding token. One of: "XS", "SM", "MD", "LG", "XL",
            "XXL", or None. Defaults to "MD".
        relief:
            Tkinter relief style. Common values: "flat", "raised", "sunken",
            "solid", "ridge", "groove". Defaults to "flat".
        bg_colour:
            Optional explicit background colour family dictionary. If provided,
            bg_shade must also be provided and role/shade are ignored.
        bg_shade:
            Optional background shade token within bg_colour. Must be provided
            when bg_colour is provided.

    Returns:
        str:
            The registered ttk style name. Use directly on ttk.Frame:
                ttk.Frame(parent, style=style_name)

    Raises:
        KeyError:
            If role is invalid, or shade/bg_shade are not valid keys for their
            respective colour families.
        ValueError:
            If bg_colour is provided without bg_shade, or bg_shade without
            bg_colour.

    Notes:
        - SECONDARY/LIGHT is the default for neutral backgrounds.
        - Border width 0 effectively hides borders regardless of relief.
        - bg_colour/bg_shade provide full surface control using design tokens,
          mirroring G01c_text_styles behaviour.
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("———[G01d DEBUG START]———————————————————————————")
        logger.debug(
            "INPUT → role=%s, shade=%s, kind=%s, border=%s, padding=%s, relief=%s",
            role, shade, kind, border, padding, relief
        )
        logger.debug(
            "INPUT → bg_colour=%s, bg_shade=%s",
            detect_colour_family_name(bg_colour), bg_shade
        )

    # ------------------------------------------------------------------------------------------------
    # Step 1: Resolve background colour family + shade
    # ------------------------------------------------------------------------------------------------
    if (bg_colour is not None and bg_shade is None) or (
        bg_colour is None and bg_shade is not None
    ):
        raise ValueError(
            "[G01d] bg_colour and bg_shade must either both be provided or both be None."
        )

    # Normalise shade tokens to uppercase before validation
    shade_normalised: str = shade.upper()
    bg_shade_normalised: str | None = bg_shade.upper() if bg_shade is not None else None

    if bg_colour is not None and bg_shade_normalised is not None:
        # Direct family override mode
        if bg_shade_normalised not in bg_colour:
            raise KeyError(
                f"[G01d] Invalid bg_shade '{bg_shade_normalised}' for this colour family. "
                f"Available shades: {list(bg_colour.keys())}"
            )
        bg_family: ColourFamily = bg_colour
        bg_shade_token: str = bg_shade_normalised
    else:
        # Semantic role/shade mode (existing behaviour)
        role_key = role.upper()
        if role_key not in CONTAINER_ROLE_FAMILIES:
            raise KeyError(
                f"[G01d] Invalid role '{role_key}'. "
                f"Expected: {list(CONTAINER_ROLE_FAMILIES.keys())}"
            )

        colour_family = CONTAINER_ROLE_FAMILIES[role_key]

        if shade_normalised not in colour_family:
            raise KeyError(
                f"[G01d] Invalid shade '{shade_normalised}' for role '{role_key}'. "
                f"Available: {list(colour_family.keys())}"
            )

        bg_family = colour_family
        bg_shade_token = shade_normalised

    bg_hex = bg_family[bg_shade_token]
    bg_family_name = detect_colour_family_name(bg_family)
    bg_shade_label = bg_shade_token

    # ------------------------------------------------------------------------------------------------
    # Step 2: Border width resolution
    # ------------------------------------------------------------------------------------------------
    border_width = resolve_border_width_internal(border)
    border_token = "NONE" if border_width == 0 else str(border).upper()

    # ------------------------------------------------------------------------------------------------
    # Step 3: Padding resolution
    # ------------------------------------------------------------------------------------------------
    pad_x, pad_y, padding_label = resolve_padding_internal(padding)

    # ------------------------------------------------------------------------------------------------
    # Step 4: Style name + cache
    # ------------------------------------------------------------------------------------------------
    style_name = build_container_style_name(
        kind=kind,
        bg_family_name=bg_family_name,
        bg_shade=bg_shade_label,
        border_weight=border_token,
        padding_token=padding_label,
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("STYLE NAME BUILT → %s", style_name)

    if style_name in CONTAINER_STYLE_CACHE:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01d] Cache hit for %s", style_name)
            logger.debug("———[G01d DEBUG END]—————————————————————————————")
        return CONTAINER_STYLE_CACHE[style_name]

    # ------------------------------------------------------------------------------------------------
    # Step 5: ttk.Style creation
    # ------------------------------------------------------------------------------------------------
    style = ttk.Style()

    # Try to base layout on TFrame so ttk knows how to render it
    try:
        base_layout = style.layout("TFrame")
        style.layout(style_name, base_layout)
    except Exception as exc:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[G01d] WARNING — could not apply layout: %s", exc)

    configure_kwargs: dict[str, Any] = {
        "background": bg_hex,
        "borderwidth": border_width,
        "relief": relief,
        "padding": (pad_x, pad_y),
    }

    style.configure(style_name, **configure_kwargs)
    CONTAINER_STYLE_CACHE[style_name] = style_name

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("CONFIGURE → %s", configure_kwargs)
        logger.debug("[G01d] Created container style: %s", style_name)
        logger.debug("———[G01d DEBUG END]—————————————————————————————")

    return style_name


# ====================================================================================================
# 7. CONVENIENCE HELPERS
# ----------------------------------------------------------------------------------------------------
# Simple wrappers around resolve_container_style() that provide commonly used
# semantic presets (cards, panels, sections, surfaces).
#
# Purpose:
#   - Reduce boilerplate when creating frequently-used container styles.
#   - Keep component construction clean.
#
# Notes:
#   - All helpers must defer to resolve_container_style() internally.
#   - No caching or style creation logic belongs here.
# ====================================================================================================
def container_style_card(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "MD",
) -> str:
    """
    Description:
        Create a card-style container with raised relief.

    Args:
        role:
            Semantic colour role. Defaults to "SECONDARY".
        shade:
            Shade within the role. Defaults to "LIGHT".
        border:
            Border weight token. Defaults to "THIN".
        padding:
            Internal padding token. Defaults to "MD".

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If role or shade is invalid.

    Notes:
        - Uses "raised" relief for card elevation effect.
        - Background family/shade can still be overridden via bg_colour/bg_shade
          by calling resolve_container_style directly.
    """
    return resolve_container_style(
        role=role,
        shade=shade,
        kind="CARD",
        border=border,
        padding=padding,
        relief="raised",
    )


def container_style_panel(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
) -> str:
    """
    Description:
        Create a panel-style container with solid relief.

    Args:
        role:
            Semantic colour role. Defaults to "SECONDARY".
        shade:
            Shade within the role. Defaults to "LIGHT".
        border:
            Border weight token. Defaults to "THIN".
        padding:
            Internal padding token. Defaults to "SM".

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If role or shade is invalid.

    Notes:
        - Uses "solid" relief for clear boundary.
    """
    return resolve_container_style(
        role=role,
        shade=shade,
        kind="PANEL",
        border=border,
        padding=padding,
        relief="solid",
    )


def container_style_section(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    border: BorderWeightType | None = "THIN",
    padding: SpacingType | None = "SM",
) -> str:
    """
    Description:
        Create a section-style container with flat relief.

    Args:
        role:
            Semantic colour role. Defaults to "SECONDARY".
        shade:
            Shade within the role. Defaults to "LIGHT".
        border:
            Border weight token. Defaults to "THIN".
        padding:
            Internal padding token. Defaults to "SM".

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If role or shade is invalid.

    Notes:
        - Uses "flat" relief for subtle grouping.
    """
    return resolve_container_style(
        role=role,
        shade=shade,
        kind="SECTION",
        border=border,
        padding=padding,
        relief="flat",
    )


def container_style_surface(
    role: ContainerRoleType = "SECONDARY",
    shade: ShadeType = "LIGHT",
    padding: SpacingType | None = "MD",
) -> str:
    """
    Description:
        Create a surface-style container with no border.

    Args:
        role:
            Semantic colour role. Defaults to "SECONDARY".
        shade:
            Shade within the role. Defaults to "LIGHT".
        padding:
            Internal padding token. Defaults to "MD".

    Returns:
        str:
            Registered ttk style name.

    Raises:
        KeyError:
            If role or shade is invalid.

    Notes:
        - Uses no border and flat relief for background surfaces.
    """
    return resolve_container_style(
        role=role,
        shade=shade,
        kind="SURFACE",
        border="NONE",
        padding=padding,
        relief="flat",
    )


# ====================================================================================================
# 8. CACHE INTROSPECTION
# ----------------------------------------------------------------------------------------------------
# Diagnostic functions for inspecting and managing the container style cache.
#
# Purpose:
#   - Enable runtime cache inspection for debugging.
#   - Support cache clearing for theme switching or testing.
# ====================================================================================================
def get_container_style_cache_info() -> dict[str, int | list[str]]:
    """
    Description:
        Return diagnostic information about the container style cache.

    Args:
        None.

    Returns:
        dict[str, int | list[str]]:
            Dictionary containing:
            - "count": Number of cached styles
            - "keys": List of all cached style names

    Raises:
        None.

    Notes:
        - Useful for debugging and verifying cache behaviour.
    """
    return {
        "count": len(CONTAINER_STYLE_CACHE),
        "keys": list(CONTAINER_STYLE_CACHE.keys()),
    }


def clear_container_style_cache() -> None:
    """
    Description:
        Clear all entries from the container style cache.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Use for theme switching or testing.
        - Does NOT unregister styles from ttk.Style().
    """
    CONTAINER_STYLE_CACHE.clear()
    logger.info("[G01d] Cleared container style cache")


# ====================================================================================================
# 9. PUBLIC API
# ----------------------------------------------------------------------------------------------------
__all__ = [
    # Main engine
    "resolve_container_style",
    # Convenience helpers
    "container_style_card",
    "container_style_panel",
    "container_style_section",
    "container_style_surface",
    # Cache introspection
    "get_container_style_cache_info",
    "clear_container_style_cache",
]


# ====================================================================================================
# 10. SELF-TEST
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init_logging()
    logger.info("[G01d] Running G01d_container_styles self-test...")

    root = tk.Tk()
    root.title("G01d Container Styles — Self-test")

    try:
        root.geometry("600x500")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        main = ttk.Frame(root)
        main.grid(row=0, column=0, sticky="nsew")

        # Primary Surface
        style_surface = container_style_surface(role="PRIMARY", shade="LIGHT")
        frame1 = ttk.Frame(main, style=style_surface)
        frame1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ttk.Label(frame1, text="Primary Surface (no border)").pack(padx=10, pady=10)

        # Secondary Card
        style_card = container_style_card(role="SECONDARY", shade="MID")
        frame2 = ttk.Frame(main, style=style_card)
        frame2.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        ttk.Label(frame2, text="Secondary Card (raised)").pack(padx=10, pady=10)

        # Warning Panel
        style_panel = container_style_panel(role="WARNING", shade="LIGHT")
        frame3 = ttk.Frame(main, style=style_panel)
        frame3.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        ttk.Label(frame3, text="Warning Panel (solid border)").pack(padx=10, pady=10)

        # Success Section
        style_section = container_style_section(role="SUCCESS", shade="LIGHT")
        frame4 = ttk.Frame(main, style=style_section)
        frame4.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        ttk.Label(frame4, text="Success Section (flat)").pack(padx=10, pady=10)

        # Direct bg override example (uses bg_colour/bg_shade)
        direct_style = resolve_container_style(
            kind="CARD",
            border="THIN",
            padding="MD",
            relief="raised",
            bg_colour=GUI_PRIMARY,
            bg_shade="MID",
        )
        frame5 = ttk.Frame(main, style=direct_style)
        frame5.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)
        ttk.Label(frame5, text="Direct bg override (GUI_PRIMARY[MID])").pack(
            padx=10, pady=10
        )

        # Cache info
        logger.info("Cache info: %s", get_container_style_cache_info())

        root.mainloop()

    except Exception as exc:
        log_exception(exc, logger, "G01d self-test")

    finally:
        try:
            root.destroy()
        except Exception:
            pass
        logger.info("[G01d] Self-test complete.")