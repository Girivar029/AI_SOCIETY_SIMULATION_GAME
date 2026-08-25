"""Low-level UI primitives — pixel borders, panels, buttons, text wrap."""

import pygame
from src.ui.theme import *

# ---------- helpers ----------

def draw_pixel_border(surf: pygame.Surface, rect: pygame.Rect, color=COLOR_BORDER, width=1):
    pygame.draw.rect(surf, color, rect, width)

def draw_panel(surf: pygame.Surface, rect: pygame.Rect, fill=COLOR_PANEL, border=COLOR_BORDER_DIM):
    # Fill with alpha — need SRCALPHA surface
    # If surf has no alpha, we fake with solid plus dim overlay
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill(fill)
    surf.blit(panel, rect.topleft)
    draw_pixel_border(surf, rect, border, 1)

def draw_button(surf: pygame.Surface, rect: pygame.Rect, label: str, hovered=False, enabled=True, font_size=FONT_SMALL):
    bg = COLOR_PANEL_LIGHT if hovered else COLOR_PANEL
    if not enabled:
        bg = (30, 30, 36, 180)
    draw_panel(surf, rect, bg, COLOR_ACCENT if hovered and enabled else COLOR_BORDER_DIM)
    if hovered and enabled:
        # inset highlight
        inner = rect.inflate(-2, -2)
        pygame.draw.rect(surf, COLOR_ACCENT, inner, 1)
    font = get_font(font_size, bold=True)
    col = COLOR_ACCENT_HOVER if hovered and enabled else COLOR_TEXT_DIM if not enabled else COLOR_TEXT
    txt = font.render(label, True, col)
    surf.blit(txt, txt.get_rect(center=rect.center))

    return rect

def wrap_text(text: str, font: pygame.font.Font, max_width: int):
    """Return list of lines wrapped."""
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = cur + (" " if cur else "") + w
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            # handle overlong word
            cur = w
            # if single word too long, split char
            while font.size(cur)[0] > max_width and len(cur) > 1:
                # find split point
                for i in range(len(cur)-1, 0, -1):
                    if font.size(cur[:i])[0] <= max_width:
                        lines.append(cur[:i])
                        cur = cur[i:]
                        break
                else:
                    break
    if cur:
        lines.append(cur)
    return lines

def render_wrapped(surf: pygame.Surface, text: str, font: pygame.font.Font, color, rect: pygame.Rect, line_h=0):
    if line_h == 0:
        line_h = font.get_height() + 1
    lines = wrap_text(text, font, rect.width)
    y = rect.y
    for line in lines:
        if y + line_h > rect.y + rect.height:
            break
        txt = font.render(line, True, color)
        surf.blit(txt, (rect.x, y))
        y += line_h
    return y - rect.y  # height used

def background_cover(bg: pygame.Surface, target_size: tuple[int,int]) -> pygame.Surface:
    """Scale bg to fill target preserving aspect ratio, crop center. Uses scale (nearest)."""
    tw, th = target_size
    bw, bh = bg.get_size()
    scale = max(tw / bw, th / bh)
    new_w = int(bw * scale)
    new_h = int(bh * scale)
    # pygame.transform.scale is nearest (scale, not smoothscale)
    scaled = pygame.transform.scale(bg, (new_w, new_h))
    # crop center
    x = (new_w - tw) // 2
    y = (new_h - th) // 2
    out = pygame.Surface(target_size)
    out.blit(scaled, (0, 0), area=pygame.Rect(x, y, tw, th))
    return out
