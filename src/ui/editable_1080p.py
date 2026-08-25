"""
Shim — this file re-exports the root editable_1080p.py so editing either works.
Edit the root file at project root: editable_1080p.py
"""

try:
    # Prefer root file (user-facing, easy to find)
    from editable_1080p import GLOBAL, START, INIT, SETUP, OBSERVATION, FINAL, GRAPH, PROFILE_1080P  # type: ignore
except ImportError:
    # Fallback: define defaults here if root not found (e.g., when src is run as package without root on path)
    GLOBAL = {
        "w": 1920, "h": 1080, "outer_margin": 60, "panel_padding": 24, "title_sz": 64, "year_sz": 80, "screen_heading_sz": 40, "section_sz": 30, "body_sz": 24, "body2_sz": 20, "label_sz": 16, "button_sz": 22, "micro_sz": 14, "large_value_sz": 48, "portrait_sz": 160, "button_h": 68, "button_w_primary": 380, "button_w_secondary": 240, "panel_gap": 24, "section_gap": 32, "timeline_h": 48, "card_w": 340, "card_h": 150,
        "color_bg_dim": (10, 12, 24, 155), "color_panel": (32, 28, 38, 210), "color_panel_light": (44, 38, 48, 225), "color_panel_parchment": (38, 32, 26, 215), "color_border": (168, 144, 98), "color_border_dim": (84, 72, 60), "color_border_light": (195, 175, 130), "color_text": (252, 248, 232), "color_text_dim": (210, 200, 174), "color_text_faint": (158, 152, 132), "color_accent": (198, 168, 88), "color_accent_hover": (225, 200, 130), "color_high": (110, 190, 110), "color_low": (210, 85, 85), "color_conflict": (180, 130, 85), "color_timeline_active": (198, 168, 88), "color_timeline_done": (110, 190, 110), "color_timeline_todo": (72, 68, 64),
    }
    START = {"title_y_offset": 100, "title_sz": 64, "subtitle_sz": 32, "tagline_sz": 20, "button_w": 380, "button_h": 68, "button_y_offset": 88, "how_link_y_offset": 160, "info_y": -28, "vignette_alpha": 85}
    INIT = {"card_w": 700, "card_h": 320, "title_sz": 64, "subtitle_sz": 30, "bar_w_factor": 0.86, "bar_h": 14, "step_font_sz": 14, "step_gap": 14}
    SETUP = {"card_w": 860, "card_h": 560, "card_y": 0.16, "portrait_sz": 160, "portrait_border": 2, "ideology_card_w": 300, "ideology_card_h": 150, "ideology_gap": 12, "ideology_title_sz": 16, "ideology_preview_sz": 14, "nav_button_w": 120, "nav_button_h": 34, "dot_w": 28, "dot_h": 6, "dot_gap": 8, "begin_w": 380, "begin_h": 68, "begin_y_offset": 72}
    OBSERVATION = {"panel_w_factor": 0.56, "panel_h_factor": 0.70, "panel_x_factor": 0.06, "panel_y_factor": 0.12, "inner_padding": 16, "timeline_h": 48, "timeline_marker_sz": 14, "year_title_sz": 44, "year_subtitle_sz": 14, "domain_card_w": 340, "domain_card_h": 150, "domain_gap": 16, "domain_title_sz": 14, "domain_value_sz": 16, "detail_title_sz": 22, "detail_body_sz": 20, "var_name_sz": 12, "var_value_sz": 22, "why_button_w": 80, "why_button_h": 22, "sparkline_w": 90, "sparkline_h": 14, "bottom_h": 36, "observe_w": 100, "advance_w": 380, "advance_h": 36, "strip_w_factor": 0.16, "strip_h_factor": 0.22}
    FINAL = {"reveal_title_sz": 64, "reveal_subtitle_sz": 32, "reveal_card_w": 900, "reveal_card_h": 500, "section_title_sz": 28, "body_sz": 20, "value_sz": 36, "panel_w_factor": 0.88, "panel_h_factor": 0.72}
    GRAPH = {"w_factor": 0.78, "h_factor": 0.62, "title_sz": 28, "axis_label_sz": 16, "legend_sz": 14, "line_width": 2.5}
    PROFILE_1080P = GLOBAL
