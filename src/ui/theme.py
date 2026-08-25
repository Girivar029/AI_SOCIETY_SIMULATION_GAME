"""Theme — 3-profile hand-calibrated fullscreen (720p / 1080p / 4K), warm historical."""

import pygame

# ----------------------------------------------------------------------
# 1. THREE PROFILES — hand-calibrated, not proportionally scaled
#    1080p is loaded from src/ui/editable_1080p.py so you can edit it manually
# ----------------------------------------------------------------------
try:
    # Prefer root editable file (user-facing) for easy manual editing
    import editable_1080p as _editable_root
    _EDITABLE_1080P_GLOBAL = getattr(_editable_root, "GLOBAL", None)
    # also cache per-page dicts for screens that import directly
    _EDITABLE_START = getattr(_editable_root, "START", None)
    _EDITABLE_INIT = getattr(_editable_root, "INIT", None)
    _EDITABLE_SETUP = getattr(_editable_root, "SETUP", None)
    _EDITABLE_OBSERVATION = getattr(_editable_root, "OBSERVATION", None)
    _EDITABLE_FINAL = getattr(_editable_root, "FINAL", None)
    _EDITABLE_GRAPH = getattr(_editable_root, "GRAPH", None)
except Exception:
    try:
        from src.ui.editable_1080p import GLOBAL as _EDITABLE_1080P_GLOBAL
        from src.ui.editable_1080p import START as _EDITABLE_START, INIT as _EDITABLE_INIT, SETUP as _EDITABLE_SETUP, OBSERVATION as _EDITABLE_OBSERVATION, FINAL as _EDITABLE_FINAL, GRAPH as _EDITABLE_GRAPH
    except Exception:
        _EDITABLE_1080P_GLOBAL = None
        _EDITABLE_START = _EDITABLE_INIT = _EDITABLE_SETUP = _EDITABLE_OBSERVATION = _EDITABLE_FINAL = _EDITABLE_GRAPH = None

def _get_1080p_profile():
    if _EDITABLE_1080P_GLOBAL is not None:
        # ensure required keys exist, fallback to defaults if missing
        d = dict(_EDITABLE_1080P_GLOBAL)
        d.setdefault("name", "1080p")
        d.setdefault("w", 1920); d.setdefault("h", 1080)
        return d
    return {
        "name": "1080p",
        "w": 1920, "h": 1080,
        "outer_margin": 60,
        "panel_padding": 24,
        "title_sz": 64,
        "year_sz": 80,
        "screen_heading_sz": 40,
        "section_sz": 30,
        "body_sz": 24,
        "body2_sz": 20,
        "label_sz": 16,
        "button_sz": 22,
        "micro_sz": 14,
        "large_value_sz": 48,
        "portrait_sz": 160,
        "button_h": 68,
        "button_w_primary": 380,
        "button_w_secondary": 240,
        "panel_gap": 24,
        "section_gap": 32,
        "timeline_h": 48,
        "card_w": 340,
        "card_h": 150,
    }

UI_PROFILES = {
    "720p": {
        "name": "720p",
        "w": 1280, "h": 720,
        "outer_margin": 36,
        "panel_padding": 18,
        "title_sz": 52,
        "year_sz": 64,
        "screen_heading_sz": 32,
        "section_sz": 24,
        "body_sz": 18,
        "body2_sz": 16,
        "label_sz": 14,
        "button_sz": 18,
        "micro_sz": 12,
        "large_value_sz": 36,
        "portrait_sz": 120,
        "button_h": 56,
        "button_w_primary": 320,
        "button_w_secondary": 200,
        "panel_gap": 16,
        "section_gap": 20,
        "timeline_h": 36,
        "card_w": 260,
        "card_h": 120,
    },
    "1080p": _get_1080p_profile(),
    "4K": {
        "name": "4K",
        "w": 3840, "h": 2160,
        "outer_margin": 120,
        "panel_padding": 40,
        "title_sz": 96,
        "year_sz": 120,
        "screen_heading_sz": 56,
        "section_sz": 44,
        "body_sz": 30,
        "body2_sz": 26,
        "label_sz": 22,
        "button_sz": 28,
        "micro_sz": 18,
        "large_value_sz": 72,
        "portrait_sz": 280,
        "button_h": 110,
        "button_w_primary": 560,
        "button_w_secondary": 360,
        "panel_gap": 40,
        "section_gap": 48,
        "timeline_h": 72,
        "card_w": 520,
        "card_h": 220,
    },
}

# Current profile (set at startup)
CURRENT_PROFILE_NAME = "1080p"
CURRENT = UI_PROFILES[CURRENT_PROFILE_NAME]

def set_profile(name: str):
    global CURRENT_PROFILE_NAME, CURRENT
    if name not in UI_PROFILES:
        raise ValueError(name)
    CURRENT_PROFILE_NAME = name
    CURRENT = UI_PROFILES[name]
    # also update legacy globals for code that still uses LOGICAL_W etc
    global LOGICAL_W, LOGICAL_H, WINDOW_W, WINDOW_H, SCALE, ACTUAL_W, ACTUAL_H
    global FONT_TINY, FONT_SMALL, FONT_MED, FONT_LARGE, FONT_TITLE, FONT_YEAR, FONT_BODY, FONT_BODY_LG, FONT_SECTION, FONT_LARGE_VAL, FONT_SECTION_SZ
    LOGICAL_W = CURRENT["w"]
    LOGICAL_H = CURRENT["h"]
    WINDOW_W = CURRENT["w"]
    WINDOW_H = CURRENT["h"]
    SCALE = 1.0
    ACTUAL_W = CURRENT["w"]
    ACTUAL_H = CURRENT["h"]
    FONT_TINY = CURRENT["micro_sz"]
    FONT_SMALL = CURRENT["label_sz"]
    FONT_MED = CURRENT["body_sz"]
    FONT_LARGE = CURRENT["section_sz"]
    FONT_TITLE = CURRENT["title_sz"]
    FONT_YEAR = CURRENT["year_sz"]
    FONT_BODY = CURRENT["body_sz"]
    FONT_BODY_LG = CURRENT["body2_sz"]
    FONT_SECTION = CURRENT["section_sz"]
    FONT_LARGE_VAL = CURRENT["large_value_sz"]
    FONT_SECTION_SZ = CURRENT["section_sz"]
    _cached.clear()

def get_nearest_profile(w, h):
    # distance to each profile size
    best = None
    best_dist = float("inf")
    for name, prof in UI_PROFILES.items():
        # use area + aspect diff
        dist = abs(prof["w"] - w) + abs(prof["h"] - h) * 1.5
        if dist < best_dist:
            best_dist = dist
            best = name
    return best

# Palette — warm historical, all grey text turned to white per user request
COLOR_BG_DIM = (10, 12, 24, 155)
COLOR_PANEL = (32, 28, 38, 210)
COLOR_PANEL_LIGHT = (44, 38, 48, 225)
COLOR_PANEL_PARCHMENT = (38, 32, 26, 215)
COLOR_BORDER = (168, 144, 98)
COLOR_BORDER_DIM = (84, 72, 60)
COLOR_BORDER_LIGHT = (195, 175, 130)
COLOR_TEXT = (252, 248, 232)        # warm ivory — primary white
COLOR_TEXT_DIM = (252, 248, 232)    # was 210,200,174 — now white per request (all grey → white)
COLOR_TEXT_FAINT = (252, 248, 232)  # was 158,152,132 — now white per request
COLOR_ACCENT = (198, 168, 88)       # antique gold
COLOR_ACCENT_HOVER = (225, 200, 130)
# Strong RED/GREEN — per spec 5, warm palette but immediately readable
COLOR_HIGH = (110, 190, 110)        # strong muted green
COLOR_LOW = (210, 85, 85)           # strong muted red
COLOR_CONFLICT = (180, 130, 85)
COLOR_TIMELINE_ACTIVE = (198, 168, 88)
COLOR_TIMELINE_DONE = (110, 190, 110)
COLOR_TIMELINE_TODO = (72, 68, 64)

# Legacy globals (for app that still reads LOGICAL_W etc)
LOGICAL_W = CURRENT["w"]
LOGICAL_H = CURRENT["h"]
WINDOW_W = CURRENT["w"]
WINDOW_H = CURRENT["h"]
SCALE = 1.0
SCALE_INT = 1
REF_W = 1920
REF_H = 1080
ACTUAL_W = LOGICAL_W
ACTUAL_H = LOGICAL_H

def set_actual_size(w, h):
    # for compat with previous dynamic code — now delegates to profile
    name = get_nearest_profile(w, h)
    set_profile(name)

# Legacy font size aliases (keep for old screens, now map to profile)
FONT_TINY = CURRENT["micro_sz"]
FONT_SMALL = CURRENT["label_sz"]
FONT_MED = CURRENT["body_sz"]
FONT_LARGE = CURRENT["section_sz"]
FONT_TITLE = CURRENT["title_sz"]
FONT_YEAR = CURRENT["year_sz"]
FONT_BODY = CURRENT["body_sz"]
FONT_BODY_LG = CURRENT["body2_sz"]
FONT_SECTION = CURRENT["section_sz"]
FONT_LARGE_VAL = CURRENT["large_value_sz"]
FONT_SECTION_SZ = CURRENT["section_sz"]

# Two-font system — DISPLAY for titles/years/buttons, BODY for paragraphs
_DISPLAY_FAMILIES = ["garamond", "georgia", "times new roman", "cambria"]
_BODY_FAMILIES = ["georgia", "cambria", "times new roman", "segoe ui"]
_cached = {}

def _try_sysfont(families, size, bold=False, italic=False):
    for fam in families:
        try:
            f = pygame.font.SysFont(fam, size, bold=bold, italic=italic)
            return f
        except Exception:
            continue
    return pygame.font.SysFont(None, size)

def get_font(size: int, bold=False):
    key = ("body", size, bold)
    if key not in _cached:
        _cached[key] = _try_sysfont(_BODY_FAMILIES, size, bold=bold)
    return _cached[key]

def get_heading_font(size: int, bold=False):
    # DISPLAY_FONT
    key = ("heading", size, bold)
    if key not in _cached:
        _cached[key] = _try_sysfont(_DISPLAY_FAMILIES, size, bold=bold)
    return _cached[key]

def get_body_font(size: int, bold=False, italic=False):
    key = ("body2", size, bold, italic)
    if key not in _cached:
        _cached[key] = _try_sysfont(_BODY_FAMILIES, size, bold=bold, italic=italic)
    return _cached[key]

def get_pixel_font(size: int, bold=False):
    key = ("pixel", size, bold)
    if key not in _cached:
        _cached[key] = _try_sysfont(["impact", "bahnschrift", "anton"], size, bold=bold)
        if _cached[key] is None:
            _cached[key] = get_heading_font(size, bold=bold)
    return _cached[key]

def get_profile():
    return CURRENT

def init_fonts():
    for s in [14, 16, 18, 20, 22, 24, 28, 32, 48, 52, 64]:
        get_font(s)
        get_heading_font(s)
        get_body_font(s)
