"""Main app — 3-profile fullscreen (720p/1080p/4K) with letterbox."""

import pygame
from src.config.roles import ROLES
from src.config.ideologies import IDEOLOGIES
from src.simulation.state import create_initial_state
from src.simulation.engine import simulate
from src.narrative.reports import generate_history_reports, generate_final_report
from src.ui.theme import UI_PROFILES, get_nearest_profile, set_profile, get_profile
from src.ui.assets import discover_backgrounds, load_background_surface, shuffle_portraits
from src.ui.screens.start import StartScreen
from src.ui.screens.init import InitScreen
from src.ui.screens.setup import SetupScreen
from src.ui.screens.observation import ObservationScreen
from src.ui.screens.final_report import FinalReportScreen

STATE_START = "start"
STATE_SETUP = "setup"
STATE_INIT = "init"
STATE_OBSERVATION = "observation"
STATE_FINAL = "final"

ERA_TITLES = {10: "THE FIRST CONSEQUENCES", 25: "A GENERATION", 50: "INSTITUTIONS HARDEN", 100: "THE CENTURY"}
ERA_SUBTITLES = {10: "Ten years have passed", 25: "Fifteen years have passed", 50: "Twenty-five years have passed", 100: "Fifty years have passed"}

class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("The World Machine — An Ideological Experiment")
        # Detect actual display
        try:
            info = pygame.display.Info()
            sw, sh = info.current_w, info.current_h
            if sw == 0 or sh == 0:
                sw, sh = 1920, 1080
        except Exception:
            sw, sh = 1920, 1080
        # Nearest profile
        profile_name = get_nearest_profile(sw, sh)
        set_profile(profile_name)
        prof = get_profile()
        pw, ph = prof["w"], prof["h"]
        # Try fullscreen at actual size, fallback to profile windowed for headless
        try:
            self.window = pygame.display.set_mode((sw, sh), pygame.FULLSCREEN)
            self.actual_w, self.actual_h = self.window.get_size()
        except Exception:
            self.window = pygame.display.set_mode((pw, ph))
            self.actual_w, self.actual_h = pw, ph
            sw, sh = pw, ph
        # Logical is profile size
        self.W, self.H = pw, ph
        self.logical = pygame.Surface((self.W, self.H))
        # Letterbox scale to fit actual
        scale = min(self.actual_w / self.W, self.actual_h / self.H)
        self.letterbox_scale = scale
        self.letterbox_w = int(self.W * scale)
        self.letterbox_h = int(self.H * scale)
        self.letterbox_x = (self.actual_w - self.letterbox_w)//2
        self.letterbox_y = (self.actual_h - self.letterbox_h)//2

        self.clock = pygame.time.Clock()
        self.running = True

        self.bg_map_paths = discover_backgrounds()
        self.bg_surfs = {}
        for year, path in self.bg_map_paths.items():
            try:
                surf = pygame.image.load(str(path)).convert()
                self.bg_surfs[year] = surf
            except Exception as e:
                print(f"Failed bg {path}: {e}")
                fallback = pygame.Surface((self.W, self.H))
                fallback.fill((20, 25, 40))
                self.bg_surfs[year] = fallback

        self.state = STATE_START
        self.start_screen = StartScreen((self.W, self.H), self.bg_surfs[0])
        self.init_screen = None
        self.setup_screen = None
        self.observation_screen = None
        self.final_screen = None
        self.history = None
        self.reports = None
        self.final = None
        self.portraits = None
        self.choices = None
        self.era_transition_timer = 0
        self.era_transition_year = None

    def _new_experiment_init(self):
        self.portraits = shuffle_portraits()
        self.choices = {role: IDEOLOGIES[role][0] for role in ROLES}
        self.setup_screen = SetupScreen((self.W, self.H), self.bg_surfs[0], self.portraits, self.choices)
        self.observation_screen = None
        self.final_screen = None
        self.era_transition_timer = 0

    def _start_setup(self):
        self._new_experiment_init()
        self.state = STATE_SETUP

    def _start_init(self):
        self.choices = dict(self.setup_screen.choices)
        self.init_screen = InitScreen((self.W, self.H), self.bg_surfs[0])
        self.state = STATE_INIT

    def _start_simulation(self):
        initial = create_initial_state(self.choices)
        self.history = simulate(initial, self.choices)
        self.reports = generate_history_reports(self.history)
        self.final = generate_final_report(self.history)
        self.observation_screen = ObservationScreen((self.W, self.H), self.bg_surfs, self.history, self.portraits, self.reports)
        self.observation_screen.set_unlocked(1)
        self.observation_screen.set_current(1)
        self.state = STATE_OBSERVATION

    def _trigger_era_transition(self, to_year):
        self.era_transition_year = to_year
        self.era_transition_timer = 60

    def _window_to_logical(self, pos):
        wx, wy = pos
        # map window coords to logical via letterbox
        # first subtract letterbox offset, then divide by scale
        lx = (wx - self.letterbox_x) / self.letterbox_scale if self.letterbox_scale else wx
        ly = (wy - self.letterbox_y) / self.letterbox_scale if self.letterbox_scale else wy
        return (int(lx), int(ly))

    def _blit_logical_to_window(self):
        # scale logical to letterbox and center with black bars
        if self.letterbox_scale == 1.0 and self.letterbox_w == self.W and self.letterbox_h == self.H and self.letterbox_x==0 and self.letterbox_y==0:
            self.window.blit(self.logical, (0,0))
        else:
            scaled = pygame.transform.scale(self.logical, (self.letterbox_w, self.letterbox_h))
            self.window.fill((0,0,0))
            self.window.blit(scaled, (self.letterbox_x, self.letterbox_y))

    def run(self):
        while self.running:
            mouse_window = pygame.mouse.get_pos()
            mouse_logical = self._window_to_logical(mouse_window)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state == STATE_FINAL:
                        self.state = STATE_OBSERVATION
                        if self.observation_screen:
                            self.observation_screen.set_current(len(self.history.all_states)-1)
                    elif self.state == STATE_OBSERVATION and self.observation_screen and self.observation_screen.observe_open:
                        self.observation_screen.observe_open = False
                    elif self.state == STATE_START and self.start_screen.show_how:
                        self.start_screen.show_how = False
                    elif self.state == STATE_SETUP:
                        self.state = STATE_START
                    continue
                if self.era_transition_timer > 0:
                    if event.type == pygame.MOUSEBUTTONDOWN and self.era_transition_timer < 45:
                        self.era_transition_timer = 0
                    continue
                if self.state == STATE_START:
                    res = self.start_screen.handle_event(event, mouse_logical)
                    if res == "BEGIN_EXPERIMENT":
                        self._start_setup()
                elif self.state == STATE_SETUP:
                    res = self.setup_screen.handle_event(event, mouse_logical)
                    if res == "BEGIN":
                        self._start_init()
                elif self.state == STATE_INIT:
                    self.init_screen.handle_event(event, mouse_logical)
                elif self.state == STATE_OBSERVATION:
                    res = self.observation_screen.handle_event(event, mouse_logical)
                    if res == "ADVANCED":
                        cur_year = self.observation_screen.current_state().year
                        self._trigger_era_transition(cur_year)
                        continue
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.observation_screen and self.observation_screen.advance_rect.collidepoint(mouse_logical):
                            years = [s.year for s in self.history.all_states]
                            if self.observation_screen.max_unlocked == len(years)-1 and self.observation_screen.current_year_idx == len(years)-1:
                                self.final_screen = FinalReportScreen((self.W, self.H), self.bg_surfs[100], self.history, self.final)
                                self.state = STATE_FINAL
                elif self.state == STATE_FINAL:
                    res = self.final_screen.handle_event(event, mouse_logical)
                    if res == "NEW_EXPERIMENT":
                        self.state = STATE_START
                        self.start_screen = StartScreen((self.W, self.H), self.bg_surfs[0])
                    elif res == "BACK":
                        self.state = STATE_OBSERVATION
                        if self.observation_screen:
                            self.observation_screen.set_current(len(self.history.all_states)-1)

            if self.state == STATE_INIT and self.init_screen:
                self.init_screen.update()
                if self.init_screen.done:
                    self._start_simulation()
                    self._trigger_era_transition(10)
            if self.era_transition_timer > 0:
                self.era_transition_timer -= 1

            self.logical.fill((14, 14, 22))
            if self.state == STATE_START:
                self.start_screen.draw(self.logical)
            elif self.state == STATE_SETUP:
                self.setup_screen.draw(self.logical)
            elif self.state == STATE_INIT:
                self.init_screen.draw(self.logical)
            elif self.state == STATE_OBSERVATION:
                self.observation_screen.draw(self.logical)
            elif self.state == STATE_FINAL:
                self.final_screen.draw(self.logical)

            if self.era_transition_timer > 0:
                if self.era_transition_timer > 40:
                    a = int(220 * (1 - (self.era_transition_timer - 40)/20))
                elif self.era_transition_timer > 20:
                    a = 220
                else:
                    a = int(220 * (self.era_transition_timer / 20))
                over = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
                over.fill((10, 10, 16, a))
                self.logical.blit(over, (0, 0))
                if 20 < self.era_transition_timer <= 40:
                    yr = self.era_transition_year
                    title = ERA_TITLES.get(yr, f"YEAR {yr}")
                    subtitle = ERA_SUBTITLES.get(yr, "")
                    from src.ui.theme import get_heading_font, get_body_font, COLOR_TEXT, COLOR_ACCENT
                    yf = get_heading_font(72, bold=True).render(f"YEAR {yr}", True, COLOR_TEXT)
                    tf = get_heading_font(26, bold=True).render(title, True, COLOR_ACCENT)
                    sf = get_body_font(20).render(subtitle, True, (218,212,190))
                    self.logical.blit(yf, yf.get_rect(center=(self.W//2, self.H//2 - 40)))
                    self.logical.blit(tf, tf.get_rect(center=(self.W//2, self.H//2 + 18)))
                    self.logical.blit(sf, sf.get_rect(center=(self.W//2, self.H//2 + 48)))

            self._blit_logical_to_window()
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
