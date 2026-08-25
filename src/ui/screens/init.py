"""Init sequence — cosmetic 1-2s society initializing."""

import pygame
from src.ui.theme import *
from src.ui.widgets import draw_panel, draw_pixel_border, background_cover

STEPS = [
    "EDUCATIONAL STRUCTURES",
    "HEALTH SYSTEMS",
    "FISCAL INSTITUTIONS",
    "INDUSTRIAL CAPACITY",
    "SOCIAL ORDER",
    "SCIENTIFIC INSTITUTIONS",
]

class InitScreen:
    def __init__(self, logical_size, bg_surface):
        self.w, self.h = logical_size
        self.bg = bg_surface
        self.t = 0  # 0..120 frames (~2s at 60fps, we run 30fps so 60 frames =2s)
        self.done = False

    def update(self):
        self.t += 1
        if self.t >= 70:  # ~2.3s at 30fps
            self.done = True

    def handle_event(self, event, mouse_logical):
        # allow click to skip
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.t > 15:
            self.done = True
        return None

    def draw(self, surf):
        bg_cover = background_cover(self.bg, (self.w, self.h))
        surf.blit(bg_cover, (0, 0))
        dim = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        dim.fill((14, 12, 16, 120))
        surf.blit(dim, (0, 0))
        # center card — larger length per request, equally spaced elements
        card_w = int(self.w * 0.42)
        card_h = int(self.h * 0.42)
        card = pygame.Rect(self.w//2 - card_w//2, self.h//2 - card_h//2, card_w, card_h)
        draw_panel(surf, card, (38, 32, 26, 220), COLOR_BORDER)
        from src.ui.theme import get_profile, get_heading_font, get_body_font
        prof = get_profile()
        title = get_heading_font(prof["title_sz"]-6, bold=True).render("THE WORLD MACHINE", True, COLOR_TEXT)
        surf.blit(title, title.get_rect(center=(card.centerx, card.y + 32)))
        # Everything except title brought down 5% (0.05*h ≈ 54px at 1080p)
        down = int(self.h * 0.05)
        sub = get_heading_font(prof["section_sz"], bold=True).render("INITIALIZING SOCIETY..." if not self.done else "SOCIETY READY", True, COLOR_ACCENT)
        surf.blit(sub, sub.get_rect(center=(card.centerx, card.y + 58 + down)))
        # progress bar — also down 5% and larger
        bar = pygame.Rect(card.x + 32, card.y + 90 + down, card.width - 64, 14)
        pygame.draw.rect(surf, (24, 20, 18), bar)
        draw_pixel_border(surf, bar, COLOR_BORDER_DIM, 1)
        prog = min(1.0, self.t / 60.0)
        fill_w = int(bar.width * prog)
        fill = pygame.Rect(bar.x, bar.y, fill_w, bar.height)
        pygame.draw.rect(surf, COLOR_ACCENT, fill)
        # steps — equally spaced inside remaining card height
        available_h = card.bottom - bar.bottom - 40
        step_gap = available_h // (len(STEPS) + 1)
        y0 = bar.bottom + step_gap
        for i, step in enumerate(STEPS):
            reveal_idx = int(prog * len(STEPS))
            is_on = i < reveal_idx
            is_current = i == reveal_idx
            col = COLOR_TEXT if is_on else COLOR_ACCENT if is_current else COLOR_TEXT
            prefix = "[#]" if is_on else "[ ]" if not is_current else "[~]"
            txt = get_body_font(prof["micro_sz"]+1, bold=is_on).render(f"{prefix} {step}", True, col)
            y = y0 + i * step_gap
            surf.blit(txt, (card.x + 40, y))
        if self.done:
            hint = get_body_font(prof["micro_sz"]).render("Click to continue", True, COLOR_TEXT_FAINT)
            surf.blit(hint, hint.get_rect(center=(card.centerx, card.bottom - 16)))
