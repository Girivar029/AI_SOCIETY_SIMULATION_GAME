"""
Editable 1080p UI Layout — EDIT THIS FILE AND RESTART THE GAME (python main.py)

This is the ONLY file you need to edit for 1080p (1920×1080).
Every position (x,y), size (w,h), font size, color, gap, and shadow is here.
All values are in logical pixels for 1920×1080.
720p and 4K use their own hand-tuned profiles in theme.py and are not affected.

HOW TO MOVE THINGS:
  - Increase x → move right, increase y → move down
  - Increase w/h → bigger, increase font_sz → bigger text
  - Increase gap → more space between elements (fixes border collisions)
  - If text doesn't fit: increase card_w/card_h or decrease font_sz or increase panel_h

Restart the game after saving.
"""

# ==============================================================================
# GLOBAL — margins, fonts, colors (affects all pages)
# ==============================================================================
GLOBAL = {
    "w": 1920, "h": 1080,
    "outer_margin": 60,
    "panel_padding": 24,
    "panel_gap": 24,
    "section_gap": 32,
    # Fonts
    "title_sz": 64,        # THE WORLD MACHINE
    "year_sz": 80,         # YEAR 10
    "screen_heading_sz": 40,
    "section_sz": 30,
    "body_sz": 24,         # body prose — NEVER below 22 at 1080p
    "body2_sz": 20,
    "label_sz": 16,
    "button_sz": 22,
    "micro_sz": 14,
    "large_value_sz": 48,
    # Portraits & Buttons
    "portrait_sz": 160,
    "button_h": 68,
    "button_w_primary": 380,
    "button_w_secondary": 240,
    "timeline_h": 48,
    # Cards
    "card_w": 340,
    "card_h": 150,
    # Colors — warm historical laboratory
    "color_bg_dim": (10, 12, 24, 155),
    "color_panel": (32, 28, 38, 210),
    "color_panel_light": (44, 38, 48, 225),
    "color_panel_parchment": (38, 32, 26, 215),
    "color_border": (168, 144, 98),
    "color_border_dim": (84, 72, 60),
    "color_border_light": (195, 175, 130),
    "color_text": (252, 248, 232),       # white — all grey → white per request
    "color_text_dim": (252, 248, 232),   # was grey, now white
    "color_text_faint": (252, 248, 232), # was grey, now white
    "color_accent": (198, 168, 88),
    "color_accent_hover": (225, 200, 130),
    "color_high": (110, 190, 110),       # GREEN ↑
    "color_low": (210, 85, 85),          # RED ↓
    "color_conflict": (180, 130, 85),
    "color_timeline_active": (198, 168, 88),
    "color_timeline_done": (110, 190, 110),
    "color_timeline_todo": (72, 68, 64),
}

# ==============================================================================
# START PAGE — title screen
# To move title: change title_x/title_y. To fix overlap: increase title_gap.
# ==============================================================================
START = {
    # Title block — was centered at h//2 -70, now movable
    "title_text": "THE WORLD MACHINE",
    "title_x": 960,              # center x (was w//2)
    "title_y": 270,              # Y at top 25% (was h//2 -70 = 470, now 270 per request)
    "title_sz": 64,
    "title_color": "color_text", # use GLOBAL color name or RGB tuple

    "subtitle_text": "AN IDEOLOGICAL EXPERIMENT",
    "subtitle_x": 960,
    "subtitle_y_offset": 42,     # distance below title (increase if overlapping)
    "subtitle_sz": 32,
    "subtitle_color": "color_text", # was color_accent, now white per request to be same level

    "tagline_text": "Choose the doctrines that will govern a century.",
    "tagline_x": 960,
    "tagline_y_offset": 78,
    "tagline_sz": 20,

    "divider_x": 960,
    "divider_y_offset": 58,
    "divider_w": 100,
    "divider_h": 1,

    # BEGIN button — moved slightly below, changed colours to white/gold
    "button_w": 420,             # was 380, slightly larger
    "button_h": 72,              # was 68
    "button_y_offset": 125,      # was 88, pushed slightly below per request
    "button_font_sz": 22,
    "button_subtext": "Commit doctrines and observe consequences",
    "button_subtext_sz": 12,
    "button_shadow_size": 16,    # was 8-12, larger per request
    "button_color_idle": "color_text", # was (48,40,32) dark, now white
    "button_color_hover": "color_accent",
    "button_text_color": (32, 28, 38), # dark text on white/gold button

    # Bottom info — now white
    "info_text": "10 institutions  •  4 ideological choices each  •  100 years of consequences",
    "info_x": 960,
    "info_y": 1300,
    "info_sz": 14,
    "how_link_x": 960,
    "how_link_y": 13700,
    "how_link_sz": 14,

    "vignette_alpha": 85,
    "framing_inset": 6,
}

# ==============================================================================
# INIT PAGE — initializing society
# ==============================================================================
INIT = {
    "card_w": 760,               # was 700, larger length per request
    "card_h": 380,               # was 320, larger
    "card_center_y": 540,        # center Y
    "title_sz": 64,
    "subtitle_sz": 30,
    "subtitle_y": 58,            # subtitle Y inside card (was 52, now down 5% ≈ +6)
    "bar_x": 32,                 # bar X inside card
    "bar_y": 110,                # bar Y inside card (was 72+down, now 110)
    "bar_w_factor": 0.86,
    "bar_h": 14,
    "step_font_sz": 14,
    "step_start_y": 150,         # first step Y inside card (was bar.bottom+16, now fixed)
    "step_gap": 18,              # was 13-14, now equally spaced larger
    "hint_y_offset": -24,        # hint Y from card bottom
}

# ==============================================================================
# SETUP PAGE — one institution per page (10 pages)
# All elements inside card except title can be moved down via y offsets
# ==============================================================================
SETUP = {
    # Card — larger length per request
    "card_w": 900,               # was 860, larger per request
    "card_h": 600,               # was 560, larger for equal spacing
    "card_x": 510,               # centered (1920-900)//2=510
    "card_y": 172,               # was 0.16*h =172
    "card_bg_alpha": 200,

    # Portrait
    "portrait_x": 24,            # X offset inside card
    "portrait_y": 24,            # Y offset inside card
    "portrait_sz": 160,
    "portrait_border": 2,
    "portrait_glow": 4,

    # Role title (stays, everything else down)
    "role_title_y_offset": 194,  # Y offset from card top (was 194)
    "role_title_sz": 22,
    "role_desc_y": 218,          # Y offset for description (was 218)
    "role_desc_sz": 13,
    "role_desc_line_gap": 9,

    # Influence — moved down little
    "influence_y": 300,          # was ~280, now +20 down
    "influence_title_sz": 12,
    "influence_bar_w": 90,
    "influence_bar_h": 6,
    "influence_gap": 24,

    # Ideology grid — moved down little
    "ideology_grid_x": 200,      # X offset from card left
    "ideology_grid_y": 240,      # Y offset from card top (was 210, now +30 down)
    "ideology_card_w": 320,      # was 300, larger to fix text not fitting
    "ideology_card_h": 160,      # was 150, larger to fix text not fitting
    "ideology_gap": 14,          # was 12
    "ideology_title_sz": 16,
    "ideology_preview_sz": 13,   # was 14
    "ideology_shadow": 16,       # was 12, larger per request
    "ideology_padding": 10,

    # Current doctrine
    "current_y": 460,            # was 420, down little
    "current_title_sz": 12,
    "current_preview_sz": 12,

    # Navigation
    "nav_y": 522,                # Y offset for PREV/NEXT inside card
    "nav_button_w": 120,
    "nav_button_h": 34,
    "dot_y": 58,                 # dot Y below header
    "dot_w": 28,
    "dot_h": 6,
    "dot_gap": 8,

    # BEGIN button
    "begin_w": 380,
    "begin_h": 68,
    "begin_y": 980,
    "begin_font_sz": 22,
    "status_y": 574,             # status text Y
}

# ==============================================================================
# OBSERVATION — book view (YEAR 10/25/50/100)
# Main card + subpages (education etc)
# ==============================================================================
OBSERVATION = {
    # Main book panel — moved down 5% except year
    "panel_x": 115,
    "panel_y": 155,              # was 129, +26 (5% of 540≈27) down per request
    "panel_w": 1075,             # was 0.56*w
    "panel_h": 756,
    "inner_padding": 16,

    # Header timeline
    "timeline_h": 48,
    "timeline_marker_sz": 14,
    "timeline_y": 21,

    # Year title — stays (exception per request)
    "year_title_x": 24,
    "year_title_y": 14,
    "year_title_sz": 44,
    "year_subtitle_sz": 14,
    "year_subtitle_x_offset": 180,

    # Domain cards in OVERVIEW (6 cards) — already 5% down via panel_y, ensure no border collision
    "domain_card_w": 360,        # was 340, slightly larger to fix text
    "domain_card_h": 160,        # was 150
    "domain_gap": 18,            # was 16, more gap to fix border collisions
    "domain_grid_x": 24,
    "domain_grid_y": 210,        # was 180, down 30
    "domain_title_sz": 14,
    "domain_value_sz": 16,

    # Detail page (when domain clicked) — also down 5%
    "detail_back_x": 16,
    "detail_back_y": 68,         # was 68, will add 5% offset in code
    "detail_back_w": 100,
    "detail_back_h": 30,
    "detail_close_x": -32,       # offset from panel right
    "detail_close_y": 12,
    "detail_title_x_offset": 116,
    "detail_title_y": 72,
    "detail_title_sz": 22,
    "detail_body_sz": 20,
    "detail_body_line_gap": 7,   # 10% more already, keep

    # Variables — big numbers moved to right
    "var_name_sz": 12,
    "var_value_sz": 22,
    "var_value_x": -120,         # X offset from panel right (was 160 from left, now right)
    "var_row_h": 42,
    "var_gap": 8,
    "why_button_w": 80,
    "why_button_h": 22,
    "why_button_x": -90,         # X offset from panel right
    "sparkline_w": 90,
    "sparkline_h": 14,

    # Bottom bar
    "bottom_h": 36,
    "bottom_y": 1040,
    "observe_w": 100,
    "advance_w": 380,
    "advance_h": 36,

    # Right institution strip — more vertical, larger font, white, opaque
    "strip_x": 1420,
    "strip_y": 155,              # was 129, down 5% per request
    "strip_w": 300,              # was 268, larger
    "strip_h": 480,              # was 237, more vertical per request (one per line needs more height)
    "strip_font_sz": 13,         # was 11, larger per request
    "strip_line_h": 26,          # was 20, more vertical
    "strip_bg_alpha": 235,       # was 110 translucent, now 235 opaque per request
    "strip_text_color": "color_text", # was grey, now white
}

# ==============================================================================
# FINAL REPORT — century reveal (5 pages)
# Larger text, +10% line spacing, table for final state
# ==============================================================================
FINAL = {
    "reveal_title_sz": 72,       # was 64, larger per request
    "reveal_subtitle_sz": 36,    # was 32, larger
    "reveal_card_w": 960,        # was 900, larger
    "reveal_card_h": 540,        # was 500, larger
    "reveal_center_y": 540,
    "section_title_sz": 32,      # was 28, larger
    "body_sz": 22,               # was 20, larger
    "body_line_gap_factor": 1.10, # +10% line spacing per request
    "value_sz": 40,              # was 36, larger
    "panel_x": 96,               # was 115, slightly more left
    "panel_y": 160,              # was 140, down a bit
    "panel_w": 1728,             # was 1690, larger (0.90*w)
    "panel_h": 800,              # was 777, larger and scrollable
    "table_header_h": 28,        # was 24, larger
    "table_row_h": 24,           # was 20, larger
    "table_col1_w": 400,         # VARIABLE column width
    "table_col2_w": 200,         # VALUE column width
    "graph_w": 1100,             # was 900, larger
    "graph_h": 500,              # was 420, larger
}

# ==============================================================================
# GRAPH — historical trajectory (fullscreen)
# ==============================================================================
GRAPH = {
    "w_factor": 0.78,
    "h_factor": 0.62,
    "title_sz": 28,
    "axis_label_sz": 16,
    "legend_sz": 14,
    "line_width": 2.5,
}

PROFILE_1080P = GLOBAL
