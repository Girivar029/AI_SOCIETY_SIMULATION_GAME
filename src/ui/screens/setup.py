"""Setup — dropdown per role, large portrait, details after choosing. No overflow."""

import pygame
from src.config.roles import Role, ROLES
from src.config.ideologies import IDEOLOGIES, VECTORS
from src.config.influence import INFLUENCE
from src.ui.theme import (
    get_profile, get_heading_font, get_body_font,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_TEXT_FAINT, COLOR_ACCENT, COLOR_BORDER,
    COLOR_BORDER_DIM, COLOR_HIGH, COLOR_LOW
)
from src.ui.widgets import draw_panel, draw_pixel_border, background_cover
from src.ui.assets import load_face_surface

ROLE_TITLES = {
    Role.head_of_state: "HEAD OF STATE",
    Role.education_minister: "EDUCATION MINISTER",
    Role.teacher: "TEACHER",
    Role.doctor: "DOCTOR",
    Role.health_food_minister: "FOOD & HEALTH MINISTER",
    Role.tax_minister: "TAX MINISTER",
    Role.justice_minister: "JUSTICE MINISTER",
    Role.industry_minister: "INDUSTRY MINISTER",
    Role.science_minister: "SCIENCE MINISTER",
    Role.defense_minister: "DEFENSE MINISTER",
}
ROLE_DESCS = {
    Role.head_of_state: "Broad legitimacy and national direction.",
    Role.education_minister: "Designs the national curriculum and examinations.",
    Role.teacher: "Shapes the classroom lived experience.",
    Role.doctor: "Front-line care and clinical philosophy.",
    Role.health_food_minister: "Population health and nutrition strategy.",
    Role.tax_minister: "Fiscal structure and redistribution.",
    Role.justice_minister: "Order, freedom and social trust.",
    Role.industry_minister: "Productivity and industrial capacity.",
    Role.science_minister: "Research and technological trajectory.",
    Role.defense_minister: "Security and state coercion.",
}


class SetupScreen:
    def __init__(self, logical_size, bg_surface, portrait_assignment, initial_choices):
        self.w, self.h = logical_size
        self.bg = bg_surface
        self.portraits = portrait_assignment
        self.choices = dict(initial_choices)
        self.page_idx = 0
        self.hover_prev = False
        self.hover_next = False
        self.hover_begin = False
        self.hover_option = None
        self.dropdown_open = None
        self.face_cache = {}
        pro = get_profile()
        psize = pro["portrait_sz"]
        for role, path in self.portraits.items():
            small = load_face_surface(path)
            self.face_cache[role] = pygame.transform.scale(small, (psize, psize))
        self.prev_rect = pygame.Rect(0, 0, 0, 0)
        self.next_rect = pygame.Rect(0, 0, 0, 0)
        self.begin_rect = pygame.Rect(0, 0, 0, 0)
        self.dropdown_rect = pygame.Rect(0, 0, 0, 0)
        self.option_rects: list[tuple[str, pygame.Rect]] = []

    @property
    def current_role(self):
        return ROLES[self.page_idx]

    def handle_event(self, event, mouse_pos):
        mx, my = mouse_pos
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.dropdown_open is not None:
                for ide, rect in self.option_rects:
                    if rect.collidepoint(mx, my):
                        self.choices[self.dropdown_open] = ide
                        self.dropdown_open = None
                        self.option_rects = []
                        return None
                self.dropdown_open = None
                self.option_rects = []
                return None
            if self.prev_rect.collidepoint(mx, my) and self.page_idx > 0:
                self.page_idx -= 1
                return None
            if self.next_rect.collidepoint(mx, my) and self.page_idx < len(ROLES) - 1:
                self.page_idx += 1
                return None
            dot_w, dot_h, gap = 28, 10, 10
            total = len(ROLES) * (dot_w + gap)
            start_x = (self.w - total) // 2
            dot_y = int(self.h * 0.13) + int(self.h * 0.07) + 14
            for i in range(len(ROLES)):
                r = pygame.Rect(start_x + i * (dot_w + gap), dot_y, dot_w, dot_h)
                if r.collidepoint(mx, my):
                    self.page_idx = i
                    return None
            if self.dropdown_rect.collidepoint(mx, my):
                self.dropdown_open = self.current_role if self.dropdown_open is None else None
                return None
            if self.begin_rect.collidepoint(mx, my) or self.begin_rect.inflate(16, 16).collidepoint(mx, my):
                if len(self.choices) == len(ROLES):
                    return "BEGIN"
        if event.type == pygame.MOUSEMOTION:
            self.hover_prev = self.prev_rect.collidepoint(mx, my)
            self.hover_next = self.next_rect.collidepoint(mx, my)
            self.hover_begin = self.begin_rect.collidepoint(mx, my)
            self.hover_option = None
            for ide, rect in self.option_rects:
                if rect.collidepoint(mx, my):
                    self.hover_option = ide
                    break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and self.page_idx > 0:
                self.page_idx -= 1
            elif event.key == pygame.K_RIGHT and self.page_idx < len(ROLES) - 1:
                self.page_idx += 1
        return None

    def draw(self, surf):
        pro = get_profile()
        bg_cover = background_cover(self.bg, (self.w, self.h))
        surf.blit(bg_cover, (0, 0))
        dim = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        dim.fill((10, 10, 18, 60))
        surf.blit(dim, (0, 0))

        # Header
        header_h = int(self.h * 0.07)
        header = pygame.Rect(pro["outer_margin"], int(self.h * 0.02), self.w - 2 * pro["outer_margin"], header_h)
        draw_panel(surf, header, (28, 24, 34, 170), COLOR_BORDER_DIM)
        title = get_heading_font(pro["title_sz"] - 4, bold=True).render("THE WORLD MACHINE", True, COLOR_TEXT)
        surf.blit(title, title.get_rect(center=(self.w // 2, header.centery - 10)))
        sub = get_body_font(pro["label_sz"]).render(
            "AN IDEOLOGICAL EXPERIMENT  \u2022  ONE ROLE AT A TIME", True, COLOR_TEXT
        )
        surf.blit(sub, sub.get_rect(center=(self.w // 2, header.centery + 16)))

        # Progress dots
        dot_y = header.bottom + 14
        dot_w, dot_h, gap = 28, 10, 10
        total = len(ROLES) * (dot_w + gap)
        start_x = (self.w - total) // 2
        for i in range(len(ROLES)):
            r = pygame.Rect(start_x + i * (dot_w + gap), dot_y, dot_w, dot_h)
            active = i == self.page_idx
            filled = ROLES[i] in self.choices
            col = COLOR_ACCENT if active else (120, 180, 130) if filled else (50, 48, 52)
            pygame.draw.rect(surf, col, r, border_radius=2)
            if active:
                draw_pixel_border(surf, r, COLOR_ACCENT, 1)
        label = get_body_font(pro["micro_sz"], bold=True).render("BUILDING THE SOCIETY", True, COLOR_TEXT_FAINT)
        surf.blit(label, label.get_rect(center=(self.w // 2, dot_y - 18)))
        counter = get_body_font(pro["micro_sz"], bold=True).render(
            f"{self.page_idx + 1} / {len(ROLES)}  INSTITUTIONS", True, COLOR_TEXT_FAINT
        )
        surf.blit(counter, counter.get_rect(center=(self.w // 2, dot_y + dot_h + 12)))

        role = self.current_role

        # Main card — tall enough to fit everything without overflow
        card_w = 1060
        card_h = int(self.h * 0.72)  # 778 at 1080p — plenty of room
        card_x = (self.w - card_w) // 2
        card_y = int(self.h * 0.18)
        card = pygame.Rect(card_x, card_y, card_w, card_h)
        draw_panel(surf, card, (38, 32, 26, 210), COLOR_BORDER)
        draw_pixel_border(surf, card.inflate(-4, -4), COLOR_BORDER_DIM, 1)

        # Portrait — left third
        psize = pro["portrait_sz"]
        pf = pygame.Rect(card.x + 30, card.y + 30, psize, psize)
        pygame.draw.rect(surf, (10, 8, 12), pf)
        surf.blit(self.face_cache[role], pf.topleft)
        draw_pixel_border(surf, pf, COLOR_BORDER, 2)
        pygame.draw.rect(surf, COLOR_ACCENT, pf.inflate(4, 4), 1)

        # Role title below portrait — never overflow card, shrink for long names
        role_name = ROLE_TITLES[role]
        avail_w = psize + 40  # max width for name (portrait width + margins)
        role_font_size = pro["section_sz"]
        name = get_heading_font(role_font_size, bold=True).render(role_name, True, COLOR_TEXT)
        # shrink if wider than portrait area
        while name.get_width() > avail_w and role_font_size > 14:
            role_font_size -= 1
            name = get_heading_font(role_font_size, bold=True).render(role_name, True, COLOR_TEXT)
        surf.blit(name, (pf.centerx - name.get_width() // 2, pf.bottom + 12))

        # Description below role title
        desc_y = pf.bottom + 34
        for line in self._wrap(ROLE_DESCS[role], get_body_font(pro["body_sz"] - 4), psize + 40):
            t = get_body_font(pro["body_sz"] - 4).render(line, True, COLOR_TEXT)
            surf.blit(t, (pf.centerx - t.get_width() // 2, desc_y))
            desc_y += 18

        # Influence — below description, not cramped
        inf_y = desc_y + 16
        inf_title = get_body_font(pro["micro_sz"], bold=True).render("INSTITUTIONAL INFLUENCE", True, COLOR_TEXT_FAINT)
        surf.blit(inf_title, (card.x + 30, inf_y))
        inf_y += 16
        for var, inf in sorted(INFLUENCE[role].items(), key=lambda x: -x[1])[:3]:
            lvl = "HIGH" if inf >= 1.2 else "MED" if inf >= 0.6 else "LOW"
            label = get_body_font(pro["micro_sz"]).render(var.replace("_", " ")[:18], True, COLOR_TEXT)
            surf.blit(label, (card.x + 30, inf_y))
            bar_w = int(80 * (inf / 1.5))
            bar = pygame.Rect(card.x + 30, inf_y + 14, 80, 6)
            pygame.draw.rect(surf, (38, 38, 48), bar, border_radius=1)
            pygame.draw.rect(surf, COLOR_ACCENT, pygame.Rect(bar.x, bar.y, bar_w, bar.h), border_radius=1)
            lvl_t = get_body_font(pro["micro_sz"]).render(lvl, True, COLOR_TEXT_FAINT)
            surf.blit(lvl_t, (bar.right + 8, inf_y + 12))
            inf_y += 26

        # Right side — dropdown + details: use card height, not overflowing
        right_x = pf.right + 50
        right_w = card.right - right_x - 30

        dd_label = get_body_font(pro["micro_sz"], bold=True).render("CHOOSE DOCTRINE", True, COLOR_TEXT_FAINT)
        surf.blit(dd_label, (right_x, card.y + 30))

        # Dropdown — compact height, options OVERLAY on top, not push content down
        dd_h = 44
        self.dropdown_rect = pygame.Rect(right_x, card.y + 52, right_w, dd_h)
        is_open = self.dropdown_open == role
        dd_bg = (52, 44, 34) if is_open else (36, 34, 44)
        pygame.draw.rect(surf, dd_bg, self.dropdown_rect, border_radius=4)
        draw_pixel_border(surf, self.dropdown_rect, COLOR_ACCENT if is_open else COLOR_BORDER_DIM, 1)
        sel = self.choices[role]
        sel_txt = get_heading_font(pro["label_sz"], bold=True).render(sel.replace("_", " ").upper(), True, COLOR_TEXT)
        surf.blit(sel_txt, (self.dropdown_rect.x + 16, self.dropdown_rect.y + 10))
        arrow = get_body_font(pro["label_sz"]).render("\u25BC" if not is_open else "\u25B2", True, COLOR_TEXT_FAINT)
        surf.blit(arrow, (self.dropdown_rect.right - 28, self.dropdown_rect.y + 10))

        # Details panel — fixed position below dropdown (drawn FIRST so dropdown options overlay on top)
        details_y = card.y + 120  # fixed, regardless of dropdown state
        details_h = card.bottom - details_y - 70  # fill rest of card
        details_rect = pygame.Rect(right_x, details_y, right_w, details_h)
        pygame.draw.rect(surf, (28, 26, 34, 180), details_rect, border_radius=3)
        draw_pixel_border(surf, details_rect, COLOR_BORDER_DIM, 1)
        dt = get_body_font(pro["micro_sz"], bold=True).render(
            f"SELECTED: {sel.replace('_', ' ').upper()}", True, COLOR_ACCENT
        )
        surf.blit(dt, (details_rect.x + 16, details_rect.y + 12))
        conf = get_body_font(pro["micro_sz"], bold=True).render("DOCTRINE INSTALLED", True, COLOR_HIGH)
        surf.blit(conf, (details_rect.x + 16, details_rect.y + 30))
        vec = VECTORS[role][sel]
        dy = details_rect.y + 52
        for k, v in sorted(vec.items(), key=lambda x: -abs(x[1]))[:4]:
            eff = ("+ " if v > 0 else "- ") + k.replace("_", " ")
            col = COLOR_HIGH if v > 0 else COLOR_LOW
            t = get_body_font(pro["micro_sz"]).render(eff[:26], True, col)
            surf.blit(t, (details_rect.x + 16, dy))
            dy += 18

        # Dropdown options — draw AFTER details so they appear on top
        self.option_rects.clear()
        if is_open:
            opts = IDEOLOGIES[role]
            opt_h = 40
            opt_gap = 4
            for idx, ideology in enumerate(opts):
                or_y = self.dropdown_rect.bottom + 6 + idx * (opt_h + opt_gap)
                opt_rect = pygame.Rect(right_x, or_y, right_w, opt_h)
                is_hov = self.hover_option == ideology
                opt_bg = (62, 56, 44) if is_hov else (32, 28, 36)
                pygame.draw.rect(surf, opt_bg, opt_rect, border_radius=3)
                draw_pixel_border(surf, opt_rect, COLOR_ACCENT if is_hov else COLOR_BORDER_DIM, 1)
                opt_txt = get_body_font(pro["label_sz"]).render(ideology.replace("_", " ").upper(), True, (16, 12, 10) if is_hov else COLOR_TEXT)
                surf.blit(opt_txt, (opt_rect.x + 16, opt_rect.y + 8))
                self.option_rects.append((ideology, opt_rect))

        # Navigation — bottom of card
        nav_y = card.bottom - 50
        nav_h = 36
        self.prev_rect = pygame.Rect(card.x + 30, nav_y, 140, nav_h)
        self.next_rect = pygame.Rect(card.right - 170, nav_y, 140, nav_h)
        for rect, enabled, hover, label in [
            (self.prev_rect, self.page_idx > 0, self.hover_prev, "<  PREV"),
            (self.next_rect, self.page_idx < len(ROLES) - 1, self.hover_next, "NEXT  >"),
        ]:
            bg = (52, 44, 34) if hover and enabled else (32, 28, 30)
            pygame.draw.rect(surf, bg, rect, border_radius=4)
            draw_pixel_border(surf, rect, COLOR_ACCENT if hover and enabled else COLOR_BORDER_DIM, 1)
            col = COLOR_TEXT if enabled else COLOR_TEXT_FAINT
            txt = get_body_font(pro["button_sz"] - 2, bold=True).render(label, True, col)
            surf.blit(txt, txt.get_rect(center=rect.center))

        # BEGIN button — below card
        complete = len(self.choices) == len(ROLES)
        status = get_body_font(pro["micro_sz"], bold=True).render(
            f"SOCIETY CONFIGURATION  {len(self.choices)}/10  {'COMPLETE' if complete else 'IN PROGRESS'}",
            True, COLOR_TEXT_FAINT
        )
        surf.blit(status, (self.w // 2 - status.get_width() // 2, card.bottom + 20))
        if complete:
            bw, bh = pro["button_w_primary"], pro["button_h"]
            self.begin_rect = pygame.Rect(self.w // 2 - bw // 2, card.bottom + 40, bw, bh)
            if self.hover_begin:
                glow = pygame.Surface((bw + 16, bh + 16), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*COLOR_ACCENT, 30), glow.get_rect(), border_radius=6)
                surf.blit(glow, (self.begin_rect.x - 8, self.begin_rect.y - 8))
            pygame.draw.rect(surf, COLOR_ACCENT if self.hover_begin else (48, 40, 32), self.begin_rect, border_radius=5)
            draw_pixel_border(surf, self.begin_rect, COLOR_BORDER, 2)
            lbl = get_heading_font(pro["button_sz"], bold=True).render(
                "BEGIN THE CENTURY", True, (16, 12, 10) if self.hover_begin else COLOR_TEXT
            )
            surf.blit(lbl, lbl.get_rect(center=(self.begin_rect.centerx, self.begin_rect.centery - 8)))
            sub = get_body_font(pro["micro_sz"]).render(
                "Commit these doctrines and observe their consequences",
                True, (16, 12, 10) if self.hover_begin else COLOR_TEXT_FAINT,
            )
            surf.blit(sub, sub.get_rect(center=(self.begin_rect.centerx, self.begin_rect.centery + 14)))

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
