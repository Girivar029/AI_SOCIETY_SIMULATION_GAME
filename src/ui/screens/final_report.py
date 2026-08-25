"""Final report — simplified pages: title → numbers → graph → new experiment."""

import pygame
from src.simulation.state import History
from src.narrative.reports import FinalReport
from src.ui.theme import (
    get_profile, get_heading_font, get_body_font,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_TEXT_FAINT, COLOR_ACCENT, COLOR_BORDER,
    COLOR_BORDER_DIM, COLOR_HIGH, COLOR_LOW
)
from src.ui.widgets import draw_panel, draw_pixel_border, background_cover


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
    if cur:
        lines.append(cur)
    return lines


class FinalReportScreen:
    def __init__(self, logical_size, bg_surface, history: History, final_report: FinalReport):
        self.w, self.h = logical_size
        self.bg = bg_surface
        self.history = history
        self.final = final_report
        self.scroll = 0
        self.max_scroll = 0
        self.pro = get_profile()
        self.page = 0  # 0=century, 1=numbers, 2=graph
        self.hover_prev = False
        self.hover_next = False
        self.hover_new = False
        self.hover_graph = False
        self.graph_surf = None
        self.show_graph_fullscreen = False
        self.prev_rect = pygame.Rect(0, 0, 0, 0)
        self.next_rect = pygame.Rect(0, 0, 0, 0)
        self.new_rect = pygame.Rect(0, 0, 0, 0)
        self.graph_rect = pygame.Rect(0, 0, 0, 0)
        self.close_graph_rect = pygame.Rect(0, 0, 0, 0)
        self.scroll_y = 0
        self.scroll_max = 0
        self.scroll_content = None
        self.scroll_content_used = 0
        self._generate_graph()

    def _generate_graph(self):
        try:
            from src.ui.graphs import generate_graph_surface
            surf, _ = generate_graph_surface(self.history, width=1500, height=700, dpi=100)
            if surf is not None:
                gw = int(self.w * 0.78)
                gh = int(self.h * 0.60)
                self.graph_surf = pygame.transform.scale(surf, (gw, gh))
        except Exception:
            self.graph_surf = None

    def handle_event(self, event, mouse_logical):
        mx, my = mouse_logical
        pro = self.pro
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.show_graph_fullscreen:
                close = pygame.Rect(self.w // 2 - 180, self.h // 2 - 260, 360, 360)
                if not close.collidepoint(mx, my):
                    self.show_graph_fullscreen = False
                elif self.close_graph_rect.collidepoint(mx, my):
                    self.show_graph_fullscreen = False
                return None
            if self.page == 2 and self.graph_rect.collidepoint(mx, my) and self.graph_surf is not None:
                self.show_graph_fullscreen = True
                return None
            if self.prev_rect.collidepoint(mx, my) and self.page > 0:
                self.page -= 1
                return None
            if self.next_rect.collidepoint(mx, my) and self.page < 2:
                self.page += 1
                return None
            if self.new_rect.collidepoint(mx, my):
                return "NEW_EXPERIMENT"
        if event.type == pygame.MOUSEWHEEL:
            if self.page == 1:
                self.scroll_y -= event.y * 30
                self.scroll_y = max(0, min(self.scroll_y, self.scroll_max))
        if event.type == pygame.MOUSEMOTION:
            self.hover_prev = self.prev_rect.collidepoint(mx, my)
            self.hover_next = self.next_rect.collidepoint(mx, my)
            self.hover_new = self.new_rect.collidepoint(mx, my)
            self.hover_graph = self.graph_rect.collidepoint(mx, my)
        return None

    def draw(self, surf):
        pro = self.pro
        bg_cover = background_cover(self.bg, (self.w, self.h))
        surf.blit(bg_cover, (0, 0))
        dim = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        dim.fill((10, 10, 18, 60))
        surf.blit(dim, (0, 0))

        if self.page == 0:
            self._draw_century(surf, pro)
        elif self.page == 1:
            self._draw_numbers(surf, pro)
        elif self.page == 2:
            self._draw_graph_page(surf, pro)

        # Navigation buttons
        bw, bh = 180, 50
        btn_y = int(self.h * 0.92)
        self.prev_rect = pygame.Rect(self.w // 2 - bw * 2 - 16, btn_y, bw, bh)
        self.next_rect = pygame.Rect(self.w // 2 + 16, btn_y, bw, bh)
        self.new_rect = pygame.Rect(self.w // 2 + bw + 48, btn_y, bw, bh)
        self._draw_btn(surf, self.prev_rect, "<  PREV", self.hover_prev, self.page > 0, pro)
        if self.page < 2:
            self._draw_btn(surf, self.next_rect, "NEXT  >", self.hover_next, True, pro)
        else:
            self._draw_btn(surf, self.next_rect, "VIEW GRAPHS", self.hover_next, True, pro)
        self._draw_btn(surf, self.new_rect, "NEW EXPERIMENT", self.hover_new, True, pro)

        # Fullscreen graph overlay
        if self.show_graph_fullscreen and self.graph_surf is not None:
            over = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            over.fill((10, 10, 16, 200))
            surf.blit(over, (0, 0))
            gw, gh = self.graph_surf.get_size()
            modal = pygame.Rect(self.w // 2 - gw // 2 - 10, self.h // 2 - gh // 2 - 30, gw + 20, gh + 60)
            draw_panel(surf, modal, (28, 26, 34, 240), COLOR_BORDER)
            title = get_heading_font(pro["section_sz"], bold=True).render("HISTORY  /  100 YEARS", True, COLOR_ACCENT)
            surf.blit(title, (modal.x + 16, modal.y + 10))
            surf.blit(self.graph_surf, (modal.x + 10, modal.y + 40))
            self.close_graph_rect = pygame.Rect(modal.right - 22, modal.y + 8, 18, 18)
            pygame.draw.rect(surf, (52, 44, 34), self.close_graph_rect, border_radius=2)
            draw_pixel_border(surf, self.close_graph_rect, COLOR_BORDER_DIM, 1)
            xt = get_body_font(12, bold=True).render("X", True, COLOR_TEXT)
            surf.blit(xt, xt.get_rect(center=self.close_graph_rect.center))

    def _draw_century(self, surf, pro):
        # Big title
        cy = int(self.h * 0.20)
        title = get_heading_font(pro["year_sz"], bold=True).render("A CENTURY HAS PASSED", True, COLOR_TEXT)
        surf.blit(title, title.get_rect(center=(self.w // 2, cy)))
        archetype = self.final.final_archetype
        arch_t = get_heading_font(pro["screen_heading_sz"], bold=True).render(archetype.title.upper(), True, COLOR_ACCENT)
        surf.blit(arch_t, arch_t.get_rect(center=(self.w // 2, cy + pro["year_sz"] + 24)))
        desc_t = get_body_font(pro["body_sz"]).render(archetype.description, True, COLOR_TEXT)
        surf.blit(desc_t, desc_t.get_rect(center=(self.w // 2, cy + pro["year_sz"] + pro["screen_heading_sz"] + 48)))
        # Reasons
        ry = cy + pro["year_sz"] + pro["screen_heading_sz"] + 80
        for reason in archetype.reasons[:3]:
            rt = get_body_font(pro["micro_sz"]).render("• " + reason, True, COLOR_TEXT_FAINT)
            surf.blit(rt, rt.get_rect(center=(self.w // 2, ry)))
            ry += pro["micro_sz"] + 6

    def _draw_numbers(self, surf, pro):
        # Scrollable content
        content_w = self.w - 80
        content_h = int(self.h * 0.75)
        content = pygame.Surface((content_w, content_h), pygame.SRCALPHA)
        cy = 10

        title = get_heading_font(pro["section_sz"], bold=True).render("THE FINAL PORTRAIT", True, COLOR_ACCENT)
        content.blit(title, title.get_rect(center=(content_w // 2, cy)))
        cy += pro["section_sz"] + 20

        # Table header
        hdr = pygame.Rect(0, cy, content_w, 32)
        pygame.draw.rect(content, (44, 38, 32), hdr, border_radius=3)
        draw_pixel_border(content, hdr, COLOR_BORDER, 1)
        for i, lbl in enumerate(["VARIABLE", "VALUE", "STATUS"]):
            x = (content_w // 3) * i + 16
            t = get_body_font(pro["micro_sz"], bold=True).render(lbl, True, COLOR_TEXT)
            content.blit(t, (x, cy + 6))
        cy += 40

        # Rows — compact
        row_h = 22
        for idx, (var, val) in enumerate(sorted(self.final.final_state.items())):
            y = cy + idx * (row_h + 2)
            row_bg = (44, 38, 32) if idx % 2 == 0 else (36, 32, 28)
            pygame.draw.rect(content, row_bg, pygame.Rect(0, y, content_w, row_h), border_radius=2)
            draw_pixel_border(content, pygame.Rect(0, y, content_w, row_h), COLOR_BORDER_DIM, 1)
            t = get_body_font(pro["micro_sz"]).render(var.replace("_", " ").upper(), True, COLOR_TEXT)
            content.blit(t, (16, y + 4))
            col_text = COLOR_HIGH if val >= 60 and var != "inequality" else COLOR_LOW if val <= 40 or (var == "inequality" and val >= 60) else COLOR_TEXT
            vt = get_body_font(pro["micro_sz"], bold=True).render(f"{val:.0f}", True, col_text)
            content.blit(vt, (content_w // 3 + 40, y + 3))
            status = "HIGH" if val >= 68 else "LOW" if val <= 38 else "MID"
            st = get_body_font(pro["micro_sz"]).render(status, True, COLOR_TEXT_FAINT)
            content.blit(st, (content_w * 2 // 3 + 16, y + 4))
        cy += len(self.final.final_state) * (row_h + 2) + 16

        # Summary — wrapped text
        sum_font = get_body_font(pro["body_sz"])
        for line in wrap(self.final.century_summary, sum_font, content_w - 40):
            t = sum_font.render(line, True, COLOR_TEXT)
            content.blit(t, (20, cy))
            cy += pro["body_sz"] + 6
        cy += 8

        # History fault lines (if any)
        if self.final.major_fault_lines:
            ft = get_body_font(pro["micro_sz"], bold=True).render("MAJOR FAULT LINES", True, COLOR_ACCENT)
            content.blit(ft, (0, cy))
            cy += pro["micro_sz"] + 8
            for fl in self.final.major_fault_lines:
                flt = get_body_font(pro["micro_sz"]).render(f"- {fl}", True, COLOR_TEXT_DIM)
                content.blit(flt, (10, cy))
                cy += pro["micro_sz"] + 4

        self.scroll_content = content
        self.scroll_content_used = cy
        self.scroll_max = max(0, cy - content_h + 20)

        # Draw with clipping
        clip = pygame.Rect(40, int(self.h * 0.12), content_w, content_h)
        self.scroll_y = max(0, min(self.scroll_y, self.scroll_max))
        surf.set_clip(clip)
        surf.blit(content, (40, clip.y - self.scroll_y))
        surf.set_clip(None)
        # Scrollbar
        if self.scroll_max > 0:
            track = pygame.Rect(self.w - 40, clip.y, 6, clip.height)
            pygame.draw.rect(surf, (40, 40, 50), track)
            th = max(12, int(track.height * (track.height / (cy + 20))))
            ty = track.y + int((self.scroll_y / self.scroll_max) * (track.height - th))
            pygame.draw.rect(surf, COLOR_ACCENT, pygame.Rect(track.x, ty, track.width, th), border_radius=2)

    def _draw_graph_page(self, surf, pro):
        cy = int(self.h * 0.12)
        title = get_heading_font(pro["screen_heading_sz"], bold=True).render("CENTURY TRAJECTORY", True, COLOR_ACCENT)
        surf.blit(title, title.get_rect(center=(self.w // 2, cy)))
        if self.graph_surf is not None:
            gw, gh = self.graph_surf.get_size()
            self.graph_rect = pygame.Rect(self.w // 2 - gw // 2, cy + pro["screen_heading_sz"] + 30, gw, gh)
            surf.blit(self.graph_surf, self.graph_rect.topleft)
            draw_pixel_border(surf, self.graph_rect, COLOR_BORDER, 1)
        else:
            hint = get_body_font(pro["body_sz"]).render("Graph not available.", True, COLOR_TEXT_FAINT)
            surf.blit(hint, hint.get_rect(center=(self.w // 2, cy + 120)))

    def _draw_btn(self, surf, rect, label, hovered, enabled, pro):
        bg = (52, 44, 34) if hovered and enabled else (28, 26, 32)
        pygame.draw.rect(surf, bg, rect, border_radius=4)
        draw_pixel_border(surf, rect, COLOR_ACCENT if hovered and enabled else COLOR_BORDER_DIM, 1)
        col = COLOR_TEXT if enabled else COLOR_TEXT_FAINT
        t = get_body_font(pro["button_sz"] - 4, bold=True).render(label, True, col)
        surf.blit(t, t.get_rect(center=rect.center))
