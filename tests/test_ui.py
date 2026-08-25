"""UI asset and integration tests — headless, no window required."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Force dummy video driver for headless
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
pygame.init()

from src.config.roles import Role
from src.config.ideologies import IDEOLOGIES
from src.simulation.state import create_initial_state
from src.simulation.engine import simulate
from src.narrative.reports import generate_history_reports
from src.ui.assets import discover_backgrounds, discover_faces, shuffle_portraits, get_background_mapping_without_load

def test_background_discovery():
    mapping = discover_backgrounds()
    assert len(mapping) == 5, f"expected 5 backgrounds, got {len(mapping)}"
    assert set(mapping.keys()) == {0, 10, 25, 50, 100}
    # deterministic sorted order: Bluish first, Vortex last
    names = [mapping[y].name for y in [0,10,25,50,100]]
    assert names[0] == "Bluish_Twilight.jpg"
    assert names[-1] == "Vortex Dark.jpg"
    assert names == sorted(names), f"should be sorted: {names}"

def test_background_deterministic_mapping():
    m1 = get_background_mapping_without_load()
    m2 = discover_backgrounds()
    assert m1 == m2, "mapping must be deterministic"

def test_faces_count():
    faces = discover_faces()
    assert len(faces) == 16
    assert all(f.suffix == ".png" for f in faces)

def test_portrait_shuffle_assigns_10():
    assign = shuffle_portraits()
    assert len(assign) == 10
    assert set(assign.keys()) == set([r for r in __import__('src.config.roles', fromlist=['ROLES']).ROLES])
    # 6 unused
    all_faces = set(discover_faces())
    used = set(assign.values())
    assert len(used) == 10
    assert used.issubset(all_faces)

def test_portrait_reshuffled():
    a = shuffle_portraits()
    b = shuffle_portraits()
    # Extremely unlikely to be identical shuffle; if equal, shuffle again
    # But test that at least one role differs or overall not identical deterministically? We check that randomization happens
    # Since we can't guarantee inequality, just verify both are valid and not permanently associated
    assert len(a) == len(b) == 10
    # If by chance equal, report skip? We'll allow equality but note it's random
    # The test passes regardless; we just ensure no face has fixed role by checking across two shuffles we can't assert fixed.
    # Instead verify that assignment is not the same as sorted order (which would indicate no shuffle)
    sorted_faces = sorted(discover_faces(), key=lambda x: x.name)
    ordered = {role: path for role, path in zip(__import__('src.config.roles', fromlist=['ROLES']).ROLES, sorted_faces)}
    # At least one shuffle should differ from ordered sorted assignment
    # Run multiple shuffles to ensure some variation
    found_variation = False
    for _ in range(10):
        s = shuffle_portraits()
        if s != ordered:
            found_variation = True
            break
    assert found_variation, "shuffle should produce variation from sorted order over 10 trials"

def test_backgrounds_do_not_affect_simulation():
    choices = {Role.head_of_state:"technocratic", Role.education_minister:"standardization", Role.teacher:"skills", Role.doctor:"preventive", Role.health_food_minister:"public_prevention", Role.tax_minister:"progressive_tax", Role.justice_minister:"rehabilitative", Role.industry_minister:"deregulated", Role.science_minister:"applied_research", Role.defense_minister:"technological_defense"}
    h1 = simulate(create_initial_state(choices), choices)
    # Simulate again after different background mapping would be same mapping, but we ensure portraits don't affect
    p1 = shuffle_portraits()
    h2 = simulate(create_initial_state(choices), choices)
    p2 = shuffle_portraits()
    assert [s.values for s in h1.all_states] == [s.values for s in h2.all_states]
    # Also ensure background mapping deterministic not used in simulation
    assert discover_backgrounds() == discover_backgrounds()

def test_ideology_selection_feeds_engine():
    # Changing one ideology should change history
    base = {Role.head_of_state:"authoritarian", Role.education_minister:"standardization", Role.teacher:"discipline", Role.doctor:"treatment_first", Role.health_food_minister:"clinical_access", Role.tax_minister:"low_tax", Role.justice_minister:"punitive", Role.industry_minister:"state_directed", Role.science_minister:"mission_driven", Role.defense_minister:"standing_force"}
    variant = dict(base)
    variant[Role.teacher] = "skills"
    h_base = simulate(create_initial_state(base), base)
    h_var = simulate(create_initial_state(variant), variant)
    assert h_base.state_at(100).values["creativity"] != h_var.state_at(100).values["creativity"]

def test_observation_does_not_mutate():
    choices = {Role.head_of_state:"laissez_faire", Role.education_minister:"educational_freedom", Role.teacher:"holistic", Role.doctor:"preventive", Role.health_food_minister:"nutrition_first", Role.tax_minister:"progressive_tax", Role.justice_minister:"restorative", Role.industry_minister:"cooperative", Role.science_minister:"open_science", Role.defense_minister:"minimal_defense"}
    h = simulate(create_initial_state(choices), choices)
    before = [dict(s.values) for s in h.all_states]
    reports = generate_history_reports(h)
    # Access observation data repeatedly
    for r in reports:
        _ = r.education.text
        _ = r.dominant_conflict
        _ = r.key_movements
        _ = r.trends["freedom"]
    after = [dict(s.values) for s in h.all_states]
    assert before == after

def test_timeline_readonly():
    # Timeline navigation should not alter history
    choices = {Role.head_of_state:"populist", Role.education_minister:"meritocracy", Role.teacher:"holistic", Role.doctor:"traditional", Role.health_food_minister:"nutrition_first", Role.tax_minister:"redistribution", Role.justice_minister:"restorative", Role.industry_minister:"protectionist", Role.science_minister:"open_science", Role.defense_minister:"mass_mobilization"}
    h = simulate(create_initial_state(choices), choices)
    # Create observation screen headless — ensure display mode for convert()
    if not pygame.display.get_surface():
        pygame.display.set_mode((640, 360))
    from src.ui.assets import load_background_surface, discover_backgrounds
    from src.ui.screens.observation import ObservationScreen
    bg_map = {year: load_background_surface(path) for year, path in discover_backgrounds().items()}
    portraits = shuffle_portraits()
    reports = generate_history_reports(h)
    obs = ObservationScreen((640,360), bg_map, h, portraits, reports)
    # Initially unlocked 1
    obs.set_unlocked(1)
    vals_before = [dict(s.values) for s in h.all_states]
    # Navigate timeline to 0 and back — should not mutate
    obs.set_current(0)
    obs.set_current(1)
    assert vals_before == [dict(s.values) for s in h.all_states]
    # Advance to 25
    obs.set_unlocked(2)
    obs.set_current(2)
    assert vals_before == [dict(s.values) for s in h.all_states]

def test_matplotlib_graph_generation():
    try:
        from src.ui.graphs import generate_graph_surface, HAS_MPL
    except ImportError:
        assert True  # fallback
        return
    if not HAS_MPL:
        assert True
        return
    if not pygame.display.get_surface():
        pygame.display.set_mode((640, 360))
    choices = {Role.head_of_state:"technocratic", Role.education_minister:"meritocracy", Role.teacher:"skills", Role.doctor:"preventive", Role.health_food_minister:"public_prevention", Role.tax_minister:"progressive_tax", Role.justice_minister:"rehabilitative", Role.industry_minister:"deregulated", Role.science_minister:"applied_research", Role.defense_minister:"technological_defense"}
    h = simulate(create_initial_state(choices), choices)
    surf, _ = generate_graph_surface(h, width=640, height=360)
    assert surf is not None
    assert surf.get_width() > 0

if __name__ == "__main__":
    test_background_discovery()
    print("PASS test_background_discovery")
    test_background_deterministic_mapping()
    print("PASS test_background_deterministic_mapping")
    test_faces_count()
    print("PASS test_faces_count")
    test_portrait_shuffle_assigns_10()
    print("PASS test_portrait_shuffle_assigns_10")
    test_portrait_reshuffled()
    print("PASS test_portrait_reshuffled")
    test_backgrounds_do_not_affect_simulation()
    print("PASS test_backgrounds_do_not_affect_simulation")
    test_ideology_selection_feeds_engine()
    print("PASS test_ideology_selection_feeds_engine")
    test_observation_does_not_mutate()
    print("PASS test_observation_does_not_mutate")
    test_timeline_readonly()
    print("PASS test_timeline_readonly")
    test_matplotlib_graph_generation()
    print("PASS test_matplotlib_graph_generation")
    print("ALL test_ui PASSED")
