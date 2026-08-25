"""Start screen — simple title + subtitle + button. Clean, minimal."""

import pygame
from src.ui.theme import (
    get_heading_font, get_body_font, get_profile,
    COLOR_TEXT, COLOR_ACCENT, COLOR_BORDER, COLOR_BORDER_DIM,
    COLOR_TEXT_FAINT, COLOR_ACCENT_HOVER, FONT_BODY, FONT_TINY, FONT_SECTION, FONT_TITLE
)
from src.ui.widgets import draw_panel, draw_pixel_border, background_cover


class StartScreen:
    def __init__(self, logical_size, bg_surface):
        self.w, self.h = logical_size
        self.bg = bg_surface
        self.hover_begin = False
        self.hover_how = False
        self.show_how = False
        self.begin_rect = pygame.Rect(0, 0, 0, 0)
        self.how_rect = pygame.Rect(0, 0, 0, 0)
        self.how_close_rect = pygame.Rect(0, 0, 0, 0)
        self.pro = get_profile()

    def handle_event(self, event, mouse_logical):
        mx, my = mouse_logical
        if self.show_how:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                modal = pygame.Rect(self.w // 2 - 220, self.h // 2 - 140, 440, 280)
                close = pygame.Rect(modal.right - 20, modal.y + 6, 18, 16)
                if close.collidepoint(mx, my) or not modal.collidepoint(mx, my):
                    self.show_how = False
                    return None
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.begin_rect.collidepoint(mx, my):
                return "BEGIN_EXPERIMENT"
            if self.how_rect.collidepoint(mx, my):
                self.show_how = True
                return None
        if event.type == pygame.MOUSEMOTION:
            self.hover_begin = self.begin_rect.collidepoint(mx, my)
            self.hover_how = self.how_rect.collidepoint(mx, my)
        return None

    def draw(self, surf):
        pro = self.pro
        bg_cover = background_cover(self.bg, (self.w, self.h))
        surf.blit(bg_cover, (0, 0))
        dim = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        dim.fill((10, 10, 18, 70))
        surf.blit(dim, (0, 0))

        # Centre block — title 25% from top, button below, rest of page open
        cx = self.w // 2
        ty = int(self.h * 0.25)

        title = get_heading_font(pro["title_sz"], bold=True).render(
            "THE WORLD MACHINE", True, COLOR_TEXT
        )
        sub = get_heading_font(pro["section_sz"], bold=True).render(
            "AN IDEOLOGICAL EXPERIMENT", True, COLOR_ACCENT
        )
        tagline = get_body_font(pro["body_sz"] - 2).render(
            "Choose the doctrines that will govern a century.", True, COLOR_TEXT
        )

        surf.blit(title, title.get_rect(center=(cx, ty)))
        surf.blit(sub, sub.get_rect(center=(cx, ty + pro["title_sz"] + 18)))
        surf.blit(tagline, tagline.get_rect(center=(cx, ty + pro["title_sz"] + pro["section_sz"] + 30)))

        # Divider
        div_y = ty + pro["title_sz"] + pro["section_sz"] + 18
        pygame.draw.line(surf, COLOR_BORDER, (cx - 60, div_y), (cx + 60, div_y), 2)

        # Button — large, centered
        bw = pro["button_w_primary"]
        bh = pro["button_h"]
        by = ty + pro["title_sz"] + pro["section_sz"] + pro["body_sz"] + 70
        self.begin_rect = pygame.Rect(cx - bw // 2, by, bw, bh)

        if self.hover_begin:
            glow = pygame.Surface((bw + 16, bh + 16), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*COLOR_ACCENT, 25), glow.get_rect(), border_radius=6)
            surf.blit(glow, (self.begin_rect.x - 8, self.begin_rect.y - 8))
        pygame.draw.rect(
            surf,
            COLOR_ACCENT if self.hover_begin else (42, 36, 30),
            self.begin_rect,
            border_radius=5,
        )
        draw_pixel_border(surf, self.begin_rect, COLOR_BORDER, 2)
        lbl = get_heading_font(pro["button_sz"], bold=True).render(
            "BEGIN EXPERIMENT", True, (16, 12, 10) if self.hover_begin else COLOR_TEXT
        )
        surf.blit(lbl, lbl.get_rect(center=self.begin_rect.center))

        # HOW IT WORKS link
        self.how_rect = pygame.Rect(cx - 60, self.begin_rect.bottom + 30, 120, 20)
        how_col = COLOR_ACCENT_HOVER if self.hover_how else COLOR_TEXT_FAINT
        how_txt = get_body_font(pro["micro_sz"], bold=True).render("HOW IT WORKS", True, how_col)
        surf.blit(how_txt, how_txt.get_rect(center=self.how_rect.center))
        if self.hover_how:
            pygame.draw.line(surf, how_col, (self.how_rect.x, self.how_rect.bottom), (self.how_rect.right, self.how_rect.bottom), 1)

        # HOW overlay
        if self.show_how:
            over = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            over.fill((10, 10, 16, 180))
            surf.blit(over, (0, 0))
            modal = pygame.Rect(self.w // 2 - 240, self.h // 2 - 150, 480, 300)
            draw_panel(surf, modal, (38, 32, 26, 240), COLOR_BORDER)
            t2 = get_heading_font(pro["section_sz"], bold=True).render("HOW IT WORKS", True, COLOR_ACCENT)
            surf.blit(t2, (modal.x + 20, modal.y + 16))
            close = pygame.Rect(modal.right - 22, modal.y + 8, 18, 18)
            pygame.draw.rect(surf, (52, 44, 34), close, border_radius=2)
            draw_pixel_border(surf, close, COLOR_BORDER_DIM, 1)
            self.how_close_rect = close
            xt = get_body_font(pro["label_sz"], bold=True).render("X", True, COLOR_TEXT)
            surf.blit(xt, xt.get_rect(center=close.center))
            body_lines = [
                "You configure 10 institutions, each with a doctrine.",
                "The simulation is deterministic — same choices produce the same century.",
                "After Year 0 you observe: click WHY?, follow consequences.",
                "No winning ideology — only trade-offs that compound over 100 years.",
            ]
            y = modal.y + 50
            for line in body_lines:
                for l in self._wrap(line, get_body_font(pro["body_sz"] - 2), modal.width - 40):
                    surf.blit(
                        get_body_font(pro["body_sz"] - 2).render(l, True, COLOR_TEXT),
                        (modal.x + 20, y),
                    )
                    y += pro["body_sz"] + 4
                y += 6
            hint = get_body_font(pro["micro_sz"]).render(
                "Click outside or X to close", True, COLOR_TEXT_FAINT
            )
            surf.blit(hint, (modal.x + 20, modal.bottom - 22))

    def _wrap(self, text, font, max_w):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            test = cur + (" " if cur else "") + w
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines
