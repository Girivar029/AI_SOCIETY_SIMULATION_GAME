"""Observation — year pages with domain detail + existing WHY specimen modal."""

import pygame
from src.config.roles import ROLES
from src.config.variables import VAR_NAMES
from src.simulation.state import History
from src.narrative.reports import EraReport
from src.ui.theme import (
    get_profile, get_heading_font, get_body_font,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_TEXT_FAINT, COLOR_ACCENT,
    COLOR_BORDER, COLOR_BORDER_DIM, COLOR_HIGH, COLOR_LOW, COLOR_TIMELINE_DONE
)
from src.ui.widgets import draw_panel, draw_pixel_border, background_cover
from src.ui.assets import load_face_surface

ROLE_TITLES = {
    "head_of_state": "HEAD OF STATE", "education_minister": "EDUCATION MIN",
    "teacher": "TEACHER", "doctor": "DOCTOR",
    "health_food_minister": "HEALTH MIN", "tax_minister": "TAX MIN",
    "justice_minister": "JUSTICE MIN", "industry_minister": "INDUSTRY MIN",
    "science_minister": "SCIENCE MIN", "defense_minister": "DEFENSE MIN",
}
DOMAIN_VARS = {
    "EDUCATION": ["academic_performance", "practical_skill", "creativity"],
    "HEALTH": ["life_expectancy", "public_health", "healthcare_access"],
    "ECONOMY": ["productivity", "wealth", "inequality", "industrial_strength", "tax_revenue"],
    "SOCIETY": ["social_stability", "freedom", "trust"],
    "SCIENCE": ["research_capacity", "technological_progress", "creativity"],
    "GOVERNMENT": ["state_capacity", "military_strength", "freedom", "trust"],
}
DOMAIN_KEYS = list(DOMAIN_VARS.keys())


def wrap(text, font, max_w):
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
            while font.size(cur)[0] > max_w and len(cur) > 1:
                for i in range(len(cur) - 1, 0, -1):
                    if font.size(cur[:i])[0] <= max_w:
                        lines.append(cur[:i])
                        cur = cur[i:]
                        break
                else:
                    break
    if cur:
        lines.append(cur)
    return lines


class ObservationScreen:
    def __init__(self, logical_size, bg_map, history: History, portraits, reports):
        self.w, self.h = logical_size
        self.bg_map = bg_map
        self.history = history
        self.portraits = portraits
        self.reports = reports
        self.current_year_idx = 0
        self.max_unlocked = 1
        self.observe_open = False
        self.observe_tab = "roles"
        self.inspect_var = None
        self.inspect_conflict = None
        self.inspect_role = None
        # Year page state
        self.domain_page = None  # None = story page, else domain name
        self.domain_scroll = 0
        self.domain_max_scroll = 0
        # Navigation rects
        self.prev_rect = pygame.Rect(0, 0, 0, 0)
        self.next_rect = pygame.Rect(0, 0, 0, 0)
        self.begin_rect = pygame.Rect(0, 0, 0, 0)
        self.advance_rect = pygame.Rect(0, 0, 0, 0)
        self.observe_rect = pygame.Rect(0, 0, 0, 0)
        self.back_rect = pygame.Rect(0, 0, 0, 0)
        self.domain_cards: list[tuple[str, pygame.Rect]] = []
        self.why_rects: list[tuple[str, pygame.Rect]] = []
        # Modal rects
        self.timeline_rects: list[tuple[int, pygame.Rect]] = []
        self.var_rects: list[tuple[str, pygame.Rect]] = []
        self.conflict_rects: list[pygame.Rect] = []
        self.role_strip_rects: list[tuple[object, pygame.Rect]] = []
        self.chain_rects: list[tuple[list[str], pygame.Rect]] = []
        self.hover_advance = False
        self.hover_observe = False
        self.hover_next = False
        self.hover_prev = False
        self.hover_timeline = None
        self.t = 0
        self.pro = get_profile()
        self.small_faces = {}
        for r, p in self.portraits.items():
            surf = load_face_surface(p)
            self.small_faces[r] = pygame.transform.scale(surf, (32, 32))

    def set_unlocked(self, idx):
        self.max_unlocked = idx

    def set_current(self, idx):
        if 0 <= idx <= self.max_unlocked and idx < len(self.history.all_states):
            self.current_year_idx = idx
            self.domain_page = None
            self.domain_scroll = 0
            self.observe_open = False
            self.inspect_var = None

    def current_state(self):
        return self.history.all_states[self.current_year_idx]

    def current_report(self):
        if self.current_year_idx == 0:
            return None
        return self.reports[self.current_year_idx - 1]

    def handle_event(self, event, mouse_pos):
        mx, my = mouse_pos
        pro = self.pro
        # WHY modal (exactly as before)
        if self.observe_open:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                modal = pygame.Rect(self.w // 2 - 380, self.h // 2 - 260, 760, 520)
                close = pygame.Rect(modal.right - 28, modal.y + 8, 22, 22)
                if close.inflate(12, 12).collidepoint(mx, my):
                    self.observe_open = False
                    return None
                tabs = ["roles", "variables", "conflicts", "chains"]
                for i, tab in enumerate(tabs):
                    r = pygame.Rect(modal.x + 20 + i * 180, modal.y + 50, 170, 28)
                    if r.collidepoint(mx, my):
                        self.observe_tab = tab
                        self.inspect_var = None
                        self.inspect_role = None
                        self.inspect_conflict = None
                        return None
                if self.observe_tab == "roles":
                    for role, rect in self.role_strip_rects:
                        if rect.collidepoint(mx, my):
                            self.inspect_role = role
                            return None
                    if self.inspect_role is not None:
                        back = pygame.Rect(modal.x + 20, modal.bottom - 40, 100, 28)
                        if back.collidepoint(mx, my):
                            self.inspect_role = None
                            return None
                elif self.observe_tab == "variables":
                    for var, rect in self.var_rects:
                        if rect.collidepoint(mx, my):
                            self.inspect_var = var if self.inspect_var != var else None
                            return None
                elif self.observe_tab == "conflicts":
                    for idx, rect in enumerate(self.conflict_rects):
                        if rect.collidepoint(mx, my):
                            self.inspect_conflict = idx if self.inspect_conflict != idx else None
                            return None
                elif self.observe_tab == "chains":
                    for path, rect in self.chain_rects:
                        if rect.collidepoint(mx, my):
                            self.observe_tab = "variables"
                            self.inspect_var = path[0]
                            return None
                if not modal.collidepoint(mx, my):
                    self.observe_open = False
                    return None
            return None
        # Domain detail page: WHY button → modal
        if self.domain_page is not None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_rect.collidepoint(mx, my):
                    self.domain_page = None
                    self.domain_scroll = 0
                    return None
                for var, rect in self.why_rects:
                    if rect.inflate(10, 10).collidepoint(mx, my):
                        self.observe_open = True
                        self.observe_tab = "variables"
                        self.inspect_var = var
                        return None
            if event.type == pygame.MOUSEWHEEL:
                self.domain_scroll -= event.y * 30
                self.domain_scroll = max(0, min(self.domain_scroll, self.domain_max_scroll))
            return None
        # Story page: domain cards → domain detail
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for dom, rect in self.domain_cards:
                if rect.collidepoint(mx, my):
                    self.domain_page = dom
                    self.domain_scroll = 0
                    return None
            for year, rect in self.timeline_rects:
                if rect.collidepoint(mx, my):
                    idx = [s.year for s in self.history.all_states].index(year)
                    if idx <= self.max_unlocked:
                        self.current_year_idx = idx
                        self.domain_page = None
                    return None
            if self.observe_rect.collidepoint(mx, my):
                self.observe_open = True
                self.observe_tab = "variables"
                return None
            if self.advance_rect.collidepoint(mx, my):
                if self.max_unlocked < len(self.history.all_states) - 1 and self.current_year_idx == self.max_unlocked:
                    self.max_unlocked += 1
                    self.current_year_idx = self.max_unlocked
                    self.domain_page = None
                    return "ADVANCED"
                return None
            if self.next_rect.collidepoint(mx, my) and self.current_year_idx < self.max_unlocked:
                self.current_year_idx += 1
                self.domain_page = None
                return None
            if self.prev_rect.collidepoint(mx, my) and self.current_year_idx > 0:
                self.current_year_idx -= 1
                self.domain_page = None
                return None
        if event.type == pygame.MOUSEMOTION:
            self.hover_advance = self.advance_rect.collidepoint(mx, my)
            self.hover_observe = self.observe_rect.collidepoint(mx, my)
            self.hover_next = self.next_rect.collidepoint(mx, my)
            self.hover_prev = self.prev_rect.collidepoint(mx, my)
            self.hover_timeline = None
            for year, rect in self.timeline_rects:
                if rect.collidepoint(mx, my):
                    self.hover_timeline = year
                    break
        self.t += 1

    def _panel_rect(self):
        pro = self.pro
        # Full width panel (no strip), generous height
        return pygame.Rect(pro["outer_margin"], int(self.h * 0.10), self.w - 2 * pro["outer_margin"], int(self.h * 0.72))

    def draw(self, surf):
        cur = self.current_state()
        year = cur.year
        pro = self.pro
        bg_raw = self.bg_map.get(year, list(self.bg_map.values())[0])
        surf.blit(background_cover(bg_raw, (self.w, self.h)), (0, 0))
        dim = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        dim.fill((10, 10, 18, 60))
        surf.blit(dim, (0, 0))

        # Timeline
        self._draw_timeline(surf, pro, year)

        # Main panel
        panel = self._panel_rect()
        draw_panel(surf, panel, (28, 26, 34, 200), COLOR_BORDER)
        report = self.current_report()

        if self.domain_page is not None:
            self._draw_domain_detail(surf, panel, report, cur, pro, year)
        elif year == 0:
            self._draw_year0(surf, panel, cur, pro)
        else:
            self._draw_story_page(surf, panel, report, cur, pro, year)

        # Bottom navigation
        self._draw_bottom(surf, pro, year)

        # Observe modal
        if self.observe_open:
            self._draw_observe_modal(surf, pro, cur, year)

    def _draw_timeline(self, surf, pro, year):
        header = pygame.Rect(pro["outer_margin"], int(self.h * 0.02), self.w - 2 * pro["outer_margin"], pro["timeline_h"])
        draw_panel(surf, header, (18, 18, 26, 175), COLOR_BORDER_DIM)
        years = [s.year for s in self.history.all_states]
        self.timeline_rects.clear()
        left = header.x + 20
        right = header.right - 20
        step = (right - left) // (len(years) - 1) if len(years) > 1 else 0
        line_y = header.centery + 6
        pygame.draw.line(surf, (55, 55, 68), (left, line_y), (right, line_y), 3)
        if self.max_unlocked > 0:
            pygame.draw.line(surf, COLOR_HIGH, (left, line_y), (left + self.max_unlocked * step, line_y), 3)
        for i, y in enumerate(years):
            x = left + i * step
            rect = pygame.Rect(x - 50, header.y + 4, 100, header.height - 8)
            self.timeline_rects.append((y, rect))
            active = y == year
            done = i <= self.max_unlocked
            bg = COLOR_ACCENT if active else (42, 62, 48) if done else (34, 34, 42)
            marker = pygame.Rect(x - 8, line_y - 8, 16, 16)
            pygame.draw.rect(surf, bg, marker, border_radius=2)
            draw_pixel_border(surf, marker, COLOR_ACCENT if active else (COLOR_TIMELINE_DONE if done else COLOR_TEXT_FAINT), 2)
            if active:
                pulse = int(70 + 30 * abs((self.t % 40) - 20) / 20)
                halo = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.rect(halo, (*COLOR_ACCENT, pulse), halo.get_rect(), 1)
                surf.blit(halo, (x - 10, line_y - 10))
            lbl = get_heading_font(pro["label_sz"], bold=active).render(
                str(y), True, COLOR_TEXT if active else COLOR_TEXT_DIM if done else COLOR_TEXT_FAINT
            )
            surf.blit(lbl, lbl.get_rect(center=(x, header.y + 14)))

    def _draw_story_page(self, surf, panel, report, cur, pro, year):
        # Year title — compact, not huge
        yr = get_heading_font(pro["screen_heading_sz"], bold=True).render(f"YEAR {year}", True, COLOR_TEXT)
        surf.blit(yr, (panel.x + 30, panel.y + 20))
        subtitle = {10: "THE FIRST CONSEQUENCES", 25: "A GENERATION", 50: "INSTITUTIONS HARDEN", 100: "THE CENTURY"}.get(year, "")
        if subtitle:
            sub = get_body_font(pro["micro_sz"], bold=True).render(subtitle, True, COLOR_ACCENT)
            surf.blit(sub, (panel.x + 30 + yr.get_width() + 20, panel.y + 26))
        pygame.draw.line(surf, COLOR_BORDER_DIM, (panel.x + 20, panel.y + 60), (panel.right - 20, panel.y + 60), 1)

        # Story — fills middle
        y = panel.y + 72
        for line in wrap(report.opening, get_body_font(pro["body_sz"]), panel.width - 60):
            t = get_body_font(pro["body_sz"]).render(line, True, COLOR_TEXT)
            surf.blit(t, (panel.x + 30, y))
            y += pro["body_sz"] + 8
        y += 20

        # Key movements — large values
        if report.key_movements:
            km_title = get_heading_font(pro["section_sz"], bold=True).render("KEY MOVEMENTS", True, COLOR_ACCENT)
            surf.blit(km_title, (panel.x + 30, y))
            y += pro["section_sz"] + 12
            for km in report.key_movements[:3]:
                sign = "+" if km.delta >= 0 else ""
                col = COLOR_HIGH if km.delta > 0 else COLOR_LOW
                arrow = "\u25B2" if km.delta > 0 else "\u25BC" if km.delta < 0 else "\u2014"
                name_t = get_body_font(pro["label_sz"], bold=True).render(km.variable.replace("_", " ").upper(), True, COLOR_TEXT)
                num_t = get_heading_font(pro["large_value_sz"], bold=True).render(f"{km.current:.0f}", True, col)
                arr_t = get_body_font(pro["label_sz"], bold=True).render(f" {arrow} ({sign}{km.delta:+.1f})", True, col)
                surf.blit(name_t, (panel.x + 30, y))
                surf.blit(num_t, (panel.right - 140, y - 4))
                surf.blit(arr_t, (panel.right - 140 + num_t.get_width() + 8, y + 12))
                y += pro["large_value_sz"] + 12

        # Domain cards — click to explore each field
        y += 10
        domain_title = get_heading_font(pro["label_sz"], bold=True).render("EXPLORE DOMAINS", True, COLOR_ACCENT)
        surf.blit(domain_title, (panel.x + 30, y))
        y += pro["label_sz"] + 10
        self.domain_cards.clear()
        card_w = (panel.width - 80) // 3
        card_h = 50
        for idx, dom in enumerate(DOMAIN_KEYS):
            col = idx % 3
            row = idx // 3
            rx = panel.x + 30 + col * (card_w + 10)
            ry = y + row * (card_h + 8)
            rect = pygame.Rect(rx, ry, card_w, card_h)
            pygame.draw.rect(surf, (36, 34, 44), rect, border_radius=3)
            draw_pixel_border(surf, rect, COLOR_BORDER_DIM, 1)
            title_t = get_body_font(pro["label_sz"], bold=True).render(dom, True, COLOR_ACCENT)
            surf.blit(title_t, (rect.x + 10, rect.y + 8))
            # preview: first 2 variable values
            vars_in = DOMAIN_VARS[dom][:2]
            preview = "  ".join(f"{cur.values[v]:.0f}" for v in vars_in)
            pv_t = get_body_font(pro["micro_sz"]).render(preview, True, COLOR_TEXT_FAINT)
            surf.blit(pv_t, (rect.x + 10, rect.y + 28))
            arrow_t = get_body_font(pro["label_sz"], bold=True).render(">", True, COLOR_TEXT_FAINT)
            surf.blit(arrow_t, (rect.right - 16, rect.centery - 8))
            self.domain_cards.append((dom, rect))

        # Ideology sentence
        y = self.domain_cards[-1][1].bottom + 16
        ide = get_body_font(pro["micro_sz"]).render(report.ideology_sentence, True, COLOR_TEXT_FAINT)
        surf.blit(ide, (panel.x + 30, y))

    def _draw_domain_detail(self, surf, panel, report, cur, pro, year):
        # Back button — top left
        self.back_rect = pygame.Rect(panel.x + 16, panel.y + 16, 110, 32)
        pygame.draw.rect(surf, (44, 38, 36), self.back_rect, border_radius=3)
        draw_pixel_border(surf, self.back_rect, COLOR_BORDER_DIM, 1)
        bt = get_body_font(pro["label_sz"], bold=True).render("< BACK", True, COLOR_TEXT)
        surf.blit(bt, bt.get_rect(center=self.back_rect.center))
        # Domain title — to the right of back button, no overlap
        wanted = self.domain_page
        detail_title = get_heading_font(pro["screen_heading_sz"], bold=True).render(wanted, True, COLOR_TEXT)
        surf.blit(detail_title, (self.back_rect.right + 20, panel.y + 18))
        # Divider below both back + title
        div_y = panel.y + 56
        pygame.draw.line(surf, COLOR_BORDER_DIM, (panel.x + 20, div_y), (panel.right - 20, div_y), 1)
        # Scrollable content — starts below divider
        content_top = div_y + 12
        content_h = panel.height - 85
        clip = pygame.Rect(panel.x + 20, content_top, panel.width - 40, content_h)
        content = pygame.Surface((clip.width, 800), pygame.SRCALPHA)
        cy = 0
        # Narrative
        chosen = None
        title_map = {"EDUCATION": "EDUCATION", "HEALTH": "HEALTH", "ECONOMY": "ECONOMY", "SOCIETY": "SOCIETY", "SCIENCE": "SCIENCE & TECHNOLOGY", "GOVERNMENT": "GOVERNMENT & SECURITY"}
        wanted_title = title_map.get(self.domain_page, self.domain_page)
        for sec in report.domain_sections:
            if sec.title == wanted_title or sec.title.startswith(self.domain_page):
                chosen = sec
                break
        if chosen:
            for line in wrap(chosen.text, get_body_font(pro["body_sz"]), clip.width):
                t = get_body_font(pro["body_sz"]).render(line, True, COLOR_TEXT)
                content.blit(t, (0, cy))
                cy += pro["body_sz"] + 8
            cy += 12
        # Variables in domain — clean row layout, no overlap
        vars_in = DOMAIN_VARS[self.domain_page]
        self.why_rects.clear()
        for var in vars_in:
            val = cur.values[var]
            arrow = "\u25B2" if val > 55 else "\u25BC" if val < 45 else "\u2014"
            col = COLOR_HIGH if val > 55 else COLOR_LOW if val < 45 else COLOR_TEXT
            # Row: variable name | value | arrow | WHY button — all in one clean line
            var_name = get_body_font(pro["label_sz"], bold=True).render(var.replace("_", " ").upper(), True, COLOR_TEXT_FAINT)
            content.blit(var_name, (0, cy + 4))
            val_t = get_heading_font(pro["large_value_sz"], bold=True).render(f"{val:.0f}", True, col)
            arr_t = get_body_font(pro["label_sz"], bold=True).render(f" {arrow}", True, col)
            content.blit(val_t, (240, cy))
            content.blit(arr_t, (240 + val_t.get_width() + 8, cy + 8))
            # WHY button — at far right
            why_r = pygame.Rect(clip.width - 100, cy, 90, 26)
            pygame.draw.rect(content, (42, 38, 36), why_r, border_radius=3)
            draw_pixel_border(content, why_r, COLOR_BORDER_DIM, 1)
            why_lbl = get_body_font(pro["micro_sz"], bold=True).render("WHY?", True, COLOR_ACCENT)
            content.blit(why_lbl, why_lbl.get_rect(center=why_r.center))
            self.why_rects.append((var, pygame.Rect(clip.x + why_r.x, clip.y + cy - self.domain_scroll, why_r.width, why_r.height)))
            # Trend — below the row
            cy += pro["large_value_sz"] + 6
            tr = report.trends[var]
            tr_txt = get_body_font(pro["micro_sz"]).render(
                f"{tr.label} {tr.delta_prev:+.0f}  \u2022  {abs(tr.consecutive_direction)} eras",
                True, COLOR_TEXT_FAINT
            )
            content.blit(tr_txt, (0, cy))
            cy += 18
        # Conflict for this domain
        relevant = [c for c in report.all_conflicts if c.variable in vars_in]
        if relevant:
            dc = relevant[0]
            box = pygame.Rect(0, cy, clip.width, 44)
            pygame.draw.rect(content, (30, 28, 34), box, border_radius=3)
            draw_pixel_border(content, box, COLOR_BORDER_DIM, 1)
            hdr = get_body_font(pro["micro_sz"], bold=True).render(
                f"CONFLICT: {dc.variable.upper()}  tension {dc.tension:.2f}", True, COLOR_LOW
            )
            content.blit(hdr, (10, cy + 4))
            vs = get_body_font(pro["micro_sz"]).render(
                f"{','.join(dc.positive_roles[:2])}  <->  {','.join(dc.negative_roles[:2])}",
                True, COLOR_TEXT_FAINT
            )
            content.blit(vs, (10, cy + 20))
            cy += 52
        self.domain_max_scroll = max(0, cy - content_h + 20)
        self.domain_scroll = max(0, min(self.domain_scroll, self.domain_max_scroll))
        surf.set_clip(clip)
        surf.blit(content, (clip.x, clip.y - self.domain_scroll))
        surf.set_clip(None)
        if self.domain_max_scroll > 0:
            track = pygame.Rect(panel.right - 8, clip.y, 4, clip.height)
            pygame.draw.rect(surf, (40, 40, 50), track)
            th = max(16, int(track.height * (track.height / (cy + 20))))
            ty = track.y + int((self.domain_scroll / self.domain_max_scroll) * (track.height - th)) if self.domain_max_scroll else track.y
            pygame.draw.rect(surf, COLOR_ACCENT, pygame.Rect(track.x, ty, track.width, th), border_radius=2)

    def _draw_year0(self, surf, panel, cur, pro):
        yr = get_heading_font(pro["screen_heading_sz"], bold=True).render("YEAR 0", True, COLOR_TEXT)
        surf.blit(yr, (panel.x + 30, panel.y + 20))
        pygame.draw.line(surf, COLOR_BORDER_DIM, (panel.x + 20, panel.y + 55), (panel.right - 20, panel.y + 55), 1)
        txt = "The century has not yet begun. Your ideological configuration remains in force. Advance to Year 10 to see the first consequences."
        y = panel.y + 72
        for line in wrap(txt, get_body_font(pro["body_sz"]), panel.width - 60):
            t = get_body_font(pro["body_sz"]).render(line, True, COLOR_TEXT)
            surf.blit(t, (panel.x + 30, y))
            y += pro["body_sz"] + 8
        y += 12
        # Show all roles chosen
        font_tiny = get_body_font(pro["micro_sz"])
        t = font_tiny.render("YOUR CHOICES:", True, COLOR_TEXT_FAINT)
        surf.blit(t, (panel.x + 30, y))
        y += 14
        from src.config.roles import ROLES as R
        for role in R:
            ide = cur.choices[role]
            line = f"  {ROLE_TITLES.get(role.value, role.value):24s}  {ide.replace('_', ' ').title()}"
            tt = font_tiny.render(line, True, COLOR_TEXT)
            surf.blit(tt, (panel.x + 30, y))
            y += 14

    def _draw_bottom(self, surf, pro, year):
        bottom_y = int(self.h * 0.88)
        bw, bh = 160, 50
        self.prev_rect = pygame.Rect(int(self.w * 0.08), bottom_y, bw, bh)
        self.next_rect = pygame.Rect(int(self.w * 0.08) + bw + 16, bottom_y, bw, bh)
        self.observe_rect = pygame.Rect(self.w // 2 - 100, bottom_y, 200, bh)
        adv_w = 300
        self.advance_rect = pygame.Rect(self.w // 2 - adv_w // 2 + 220, bottom_y, adv_w, bh)
        years = [s.year for s in self.history.all_states]
        can_advance = self.max_unlocked < len(years) - 1 and self.current_year_idx == self.max_unlocked
        next_yr = years[self.max_unlocked + 1] if can_advance else None
        self._draw_btn(surf, self.prev_rect, "<  BACK", self.hover_prev, self.current_year_idx > 0, pro)
        self._draw_btn(surf, self.next_rect, "NEXT  > ", self.hover_next, self.current_year_idx < self.max_unlocked, pro)
        self._draw_btn(surf, self.observe_rect, "OBSERVE", self.hover_observe, True, pro)
        adv_lbl = f"ADVANCE TO {next_yr}" if can_advance else "VIEW FINAL REPORT" if self.max_unlocked == len(years) - 1 and self.current_year_idx == len(years) - 1 else "ADVANCE"
        adv_enabled = can_advance or (self.max_unlocked == len(years) - 1 and self.current_year_idx == len(years) - 1)
        if adv_enabled:
            pygame.draw.rect(surf, COLOR_ACCENT if self.hover_advance else (48, 40, 32), self.advance_rect, border_radius=5)
            draw_pixel_border(surf, self.advance_rect, COLOR_BORDER, 2)
        else:
            pygame.draw.rect(surf, (32, 28, 30), self.advance_rect, border_radius=5)
            draw_pixel_border(surf, self.advance_rect, COLOR_BORDER_DIM, 1)
        lbl = get_heading_font(pro["button_sz"] - 4, bold=True).render(adv_lbl, True, COLOR_TEXT if adv_enabled else COLOR_TEXT_FAINT)
        surf.blit(lbl, lbl.get_rect(center=self.advance_rect.center))
        mid = get_body_font(pro["micro_sz"], bold=True).render(f"YEAR {year}", True, COLOR_TEXT_FAINT)
        surf.blit(mid, mid.get_rect(center=(self.w // 2, self.h - 18)))

    def _draw_btn(self, surf, rect, label, hovered, enabled, pro):
        bg = (52, 44, 34) if hovered and enabled else (28, 26, 32)
        pygame.draw.rect(surf, bg, rect, border_radius=4)
        draw_pixel_border(surf, rect, COLOR_ACCENT if hovered and enabled else COLOR_BORDER_DIM, 1)
        col = COLOR_TEXT if enabled else COLOR_TEXT_FAINT
        t = get_body_font(pro["button_sz"] - 4, bold=True).render(label, True, col)
        surf.blit(t, t.get_rect(center=rect.center))

    # ── Observe modal (WHY specimen — preserved exactly) ───────────────────
    def _draw_observe_modal(self, surf, pro, cur, year):
        modal = pygame.Rect(self.w // 2 - 380, self.h // 2 - 260, 760, 520)
        draw_panel(surf, modal, (24, 24, 34, 248), COLOR_BORDER)
        title = get_heading_font(pro["section_sz"], bold=True).render(f"OBSERVATION  —  Year {year}", True, COLOR_ACCENT)
        surf.blit(title, (modal.x + 20, modal.y + 14))
        close = pygame.Rect(modal.right - 28, modal.y + 8, 22, 22)
        pygame.draw.rect(surf, (48, 42, 38), close, border_radius=2)
        draw_pixel_border(surf, close, COLOR_BORDER_DIM, 1)
        xt = get_heading_font(14, bold=True).render("X", True, COLOR_TEXT)
        surf.blit(xt, xt.get_rect(center=close.center))
        tabs = ["roles", "variables", "conflicts", "chains"]
        tab_labels = ["ROLES", "VARIABLES", "CONFLICTS", "CHAINS"]
        for i, (tab, lbl) in enumerate(zip(tabs, tab_labels)):
            r = pygame.Rect(modal.x + 20 + i * 180, modal.y + 50, 170, 28)
            is_active = self.observe_tab == tab
            pygame.draw.rect(surf, COLOR_ACCENT if is_active else (40, 40, 52), r, border_radius=2)
            draw_pixel_border(surf, r, COLOR_ACCENT if is_active else COLOR_BORDER_DIM, 1)
            tf = get_body_font(pro["label_sz"], bold=is_active).render(lbl, True, (16, 12, 10) if is_active else COLOR_TEXT)
            surf.blit(tf, tf.get_rect(center=r.center))
        cr = pygame.Rect(modal.x + 20, modal.y + 84, modal.width - 40, modal.height - 100)
        # Roles tab
        if self.observe_tab == "roles":
            self.role_strip_rects.clear()
            self.var_rects.clear()
            self.conflict_rects.clear()
            self.chain_rects.clear()
            if self.inspect_role is None:
                for idx, role in enumerate(ROLES):
                    col = idx % 2
                    row = idx // 2
                    rr = pygame.Rect(cr.x + col * (cr.width // 2 + 10), cr.y + row * 62, cr.width // 2 - 10, 56)
                    pygame.draw.rect(surf, (36, 34, 44), rr, border_radius=2)
                    draw_pixel_border(surf, rr, COLOR_BORDER_DIM, 1)
                    face = self.small_faces[role]
                    surf.blit(pygame.transform.scale(face, (40, 40)), (rr.x + 8, rr.y + 8))
                    rf = get_body_font(pro["label_sz"], bold=True).render(ROLE_TITLES[role.value], True, COLOR_TEXT)
                    surf.blit(rf, (rr.x + 58, rr.y + 10))
                    ide = cur.choices[role]
                    t2 = get_body_font(pro["micro_sz"]).render(ide.replace("_", " ")[:18], True, COLOR_ACCENT)
                    surf.blit(t2, (rr.x + 58, rr.y + 28))
                    self.role_strip_rects.append((role, rr))
            else:
                role = self.inspect_role
                back = pygame.Rect(cr.x, cr.bottom - 32, 110, 28)
                pygame.draw.rect(surf, (44, 38, 36), back, border_radius=2)
                draw_pixel_border(surf, back, COLOR_BORDER_DIM, 1)
                bt = get_body_font(12).render("< BACK", True, COLOR_TEXT)
                surf.blit(bt, bt.get_rect(center=back.center))
                y = cr.y
                t = get_heading_font(16, bold=True).render(ROLE_TITLES.get(role.value, role.value), True, COLOR_TEXT)
                surf.blit(t, (cr.x, y)); y += 24
                ide = cur.choices[role]
                t = get_body_font(13).render(f"Ideology: {ide}", True, COLOR_TEXT)
                surf.blit(t, (cr.x, y)); y += 18
                from src.config.influence import INFLUENCE
                t = get_body_font(11, bold=True).render("INSTITUTIONAL INFLUENCE \u2014 top 3", True, COLOR_TEXT_FAINT)
                surf.blit(t, (cr.x, y)); y += 16
                for var, inf in sorted(INFLUENCE[role].items(), key=lambda x: -x[1])[:3]:
                    lvl = "HIGH" if inf >= 1.2 else "MED" if inf >= 0.6 else "LOW"
                    tt = get_body_font(12).render(f"{var:22s} {lvl} {inf:.2f}", True, COLOR_TEXT_DIM)
                    surf.blit(tt, (cr.x, y)); y += 16
                big = pygame.transform.scale(load_face_surface(self.portraits[role]), (90, 90))
                frame = pygame.Rect(cr.right - 100, cr.y, 90, 90)
                pygame.draw.rect(surf, (12, 10, 14), frame)
                surf.blit(big, frame.topleft)
                draw_pixel_border(surf, frame, COLOR_BORDER, 2)
        # Variables tab
        elif self.observe_tab == "variables":
            self.var_rects.clear()
            self.role_strip_rects.clear()
            self.conflict_rects.clear()
            self.chain_rects.clear()
            if self.inspect_var is None:
                cols = 3
                chip_w = (cr.width - (cols - 1) * 12) // cols
                for idx, var in enumerate(VAR_NAMES):
                    row = idx // cols
                    col = idx % cols
                    rr = pygame.Rect(cr.x + col * (chip_w + 12), cr.y + row * 38, chip_w, 32)
                    val = cur.values[var]
                    col_bar = COLOR_HIGH if val >= 60 and var != "inequality" else COLOR_LOW if val <= 40 or (var == "inequality" and val >= 60) else COLOR_TEXT_DIM
                    pygame.draw.rect(surf, (36, 34, 44), rr, border_radius=2)
                    draw_pixel_border(surf, rr, COLOR_BORDER_DIM, 1)
                    tf = get_body_font(11, bold=True).render(var[:14].upper(), True, COLOR_TEXT)
                    surf.blit(tf, (rr.x + 8, rr.y + 6))
                    vf = get_heading_font(14, bold=True).render(f"{val:.0f}", True, col_bar)
                    surf.blit(vf, (rr.right - vf.get_width() - 8, rr.y + 6))
                    self.var_rects.append((var, rr))
            else:
                var = self.inspect_var
                y = cr.y
                hdr = get_heading_font(20, bold=True).render(var.upper(), True, COLOR_TEXT)
                surf.blit(hdr, (cr.x, y))
                val = cur.values[var]
                vbig = get_heading_font(28, bold=True).render(f"{val:.0f}", True, COLOR_HIGH if val >= 60 and var != "inequality" else COLOR_LOW if val <= 40 or (var == "inequality" and val >= 60) else COLOR_TEXT)
                surf.blit(vbig, (cr.right - vbig.get_width(), y - 4))
                y += 32
                traj = [s.values[var] for s in self.history.all_states[:self.max_unlocked + 1]]
                yrs = [s.year for s in self.history.all_states[:self.max_unlocked + 1]]
                spark = pygame.Rect(cr.x, y, cr.width, 70)
                pygame.draw.rect(surf, (18, 18, 26), spark, border_radius=2)
                draw_pixel_border(surf, spark, COLOR_BORDER_DIM, 1)
                if len(traj) > 1:
                    for i in range(len(traj) - 1):
                        x1 = spark.x + int(i * spark.width / (len(traj) - 1))
                        x2 = spark.x + int((i + 1) * spark.width / (len(traj) - 1))
                        y1 = spark.y + spark.height - int(traj[i] / 100 * spark.height)
                        y2 = spark.y + spark.height - int(traj[i + 1] / 100 * spark.height)
                        pygame.draw.line(surf, COLOR_ACCENT, (x1, y1), (x2, y2), 2)
                        pygame.draw.circle(surf, COLOR_TEXT, (x1, y1), 3)
                    pygame.draw.circle(surf, COLOR_TEXT, (x2, y2), 4)
                y = spark.bottom + 16
                for i, yy in enumerate(yrs):
                    xv = spark.x + int(i * spark.width / max(1, len(yrs) - 1))
                    lbl = get_body_font(10).render(str(yy), True, COLOR_TEXT_FAINT)
                    surf.blit(lbl, (xv - lbl.get_width() // 2, spark.bottom + 2))
                hist = "  ".join(f"{yy}:{v:.0f}" for yy, v in zip(yrs, traj))
                for line in wrap(hist, get_body_font(12), cr.width)[:1]:
                    t = get_body_font(12).render(line, True, COLOR_TEXT_DIM)
                    surf.blit(t, (cr.x, y)); y += 16
                y += 6
                rep = self.current_report()
                if rep:
                    tr = rep.trends[var]
                    trend_col = COLOR_HIGH if "increasing" in tr.label else COLOR_LOW if "decreasing" in tr.label else COLOR_TEXT_FAINT
                    txt = f"{tr.label.upper()}  \u2022  {abs(tr.consecutive_direction)} eras  \u2022  total {tr.total_delta_from_start:+.1f}"
                    t = get_body_font(12, bold=True).render(txt, True, trend_col)
                    surf.blit(t, (cr.x, y)); y += 18
                if self.history.all_states[self.current_year_idx].explain:
                    expl = self.history.all_states[self.current_year_idx].explain
                    vp = expl.pressures[var]
                    t = get_body_font(12, bold=True).render("WHY?", True, COLOR_ACCENT)
                    surf.blit(t, (cr.x, y)); y += 16
                    for c in sorted(vp.contributions, key=lambda c: -abs(c.weighted_pressure))[:4]:
                        line = f"{c.role.value[:14]:14s} {c.ideology[:14]:14s} {c.weighted_pressure:+.2f}"
                        tt = get_body_font(11).render(line, True, COLOR_TEXT_DIM if abs(c.weighted_pressure) < 0.25 else COLOR_TEXT)
                        if y < cr.bottom - 40:
                            surf.blit(tt, (cr.x, y)); y += 14
                    if abs(vp.cross_domain_delta) > 0.07:
                        tt = get_body_font(11, bold=True).render(f"cross-domain {vp.cross_domain_delta:+.2f}", True, COLOR_TEXT_FAINT)
                        surf.blit(tt, (cr.x, y)); y += 14
                back = pygame.Rect(cr.x, cr.bottom - 28, 90, 22)
                pygame.draw.rect(surf, (44, 38, 36), back, border_radius=2)
                draw_pixel_border(surf, back, COLOR_BORDER_DIM, 1)
                bt = get_body_font(11).render("< BACK", True, COLOR_TEXT)
                surf.blit(bt, bt.get_rect(center=back.center))
        # Conflicts tab
        elif self.observe_tab == "conflicts":
            self.conflict_rects.clear()
            self.var_rects.clear()
            self.chain_rects.clear()
            rep = self.current_report()
            if rep is None or not rep.all_conflicts:
                t = get_body_font(14).render("No significant conflict this era.", True, COLOR_TEXT_DIM)
                surf.blit(t, (cr.x, cr.y))
            else:
                y = cr.y
                for idx, cc in enumerate(rep.all_conflicts):
                    is_sel = self.inspect_conflict == idx
                    rr = pygame.Rect(cr.x, y, cr.width, 72 if is_sel else 36)
                    pygame.draw.rect(surf, (36, 34, 44) if is_sel else (32, 32, 44), rr, border_radius=2)
                    draw_pixel_border(surf, rr, COLOR_ACCENT if is_sel else COLOR_BORDER_DIM, 1)
                    hdr = get_body_font(12, bold=True).render(f"{cc.variable.upper()}  \u2022  TENSION {cc.tension:.2f}", True, COLOR_ACCENT if is_sel else COLOR_TEXT)
                    surf.blit(hdr, (rr.x + 12, rr.y + 8))
                    vs = get_body_font(11).render(f"{','.join(cc.positive_roles[:2])}  <->  {','.join(cc.negative_roles[:2])}", True, COLOR_TEXT_FAINT)
                    surf.blit(vs, (rr.x + 12, rr.y + 22))
                    if is_sel:
                        net = get_body_font(11).render(f"net {cc.net_pressure:+.2f} -> eff {cc.effective_pressure:+.2f}  atten {cc.attenuation:.2f}  dominant {cc.dominant_side}", True, COLOR_TEXT_DIM)
                        surf.blit(net, (rr.x + 12, rr.y + 36))
                        out = get_body_font(11).render(cc.outcome_text[:70], True, COLOR_TEXT_FAINT)
                        surf.blit(out, (rr.x + 12, rr.y + 50))
                    self.conflict_rects.append(rr)
                    y += rr.height + 10
                    if y > cr.bottom - 10:
                        break
        # Chains tab
        elif self.observe_tab == "chains":
            self.chain_rects.clear()
            rep = self.current_report()
            if rep is None or not rep.causal_chains:
                t = get_body_font(14).render("No strong cross-domain chain this era.", True, COLOR_TEXT_DIM)
                surf.blit(t, (cr.x, cr.y))
            else:
                y = cr.y
                for cc in rep.causal_chains:
                    rr = pygame.Rect(cr.x, y, cr.width, 48)
                    pygame.draw.rect(surf, (36, 34, 44), rr, border_radius=2)
                    draw_pixel_border(surf, rr, COLOR_BORDER_DIM, 1)
                    tf = get_body_font(13, bold=True).render(" -> ".join(cc.path), True, COLOR_ACCENT)
                    surf.blit(tf, (rr.x + 12, rr.y + 8))
                    desc = get_body_font(11).render(cc.description[:64], True, COLOR_TEXT_DIM)
                    surf.blit(desc, (rr.x + 12, rr.y + 26))
                    sup = get_body_font(10).render("supported" if cc.supported else "weak", True, COLOR_HIGH if cc.supported else COLOR_TEXT_FAINT)
                    surf.blit(sup, (rr.right - sup.get_width() - 12, rr.y + 8))
                    self.chain_rects.append((cc.path, rr))
                    y += 56
