"""Determinism + portrait-independence + history tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config.roles import Role
from src.simulation.state import create_initial_state
from src.simulation.engine import simulate


def choices_a():
    return {
        Role.head_of_state: "authoritarian",
        Role.education_minister: "standardization",
        Role.teacher: "discipline",
        Role.doctor: "treatment_first",
        Role.health_food_minister: "clinical_access",
        Role.tax_minister: "low_tax",
        Role.justice_minister: "punitive",
        Role.industry_minister: "state_directed",
        Role.science_minister: "mission_driven",
        Role.defense_minister: "standing_force",
    }


def choices_b():
    return {
        Role.head_of_state: "laissez_faire",
        Role.education_minister: "educational_freedom",
        Role.teacher: "holistic",
        Role.doctor: "preventive",
        Role.health_food_minister: "nutrition_first",
        Role.tax_minister: "redistribution",
        Role.justice_minister: "restorative",
        Role.industry_minister: "cooperative",
        Role.science_minister: "open_science",
        Role.defense_minister: "minimal_defense",
    }


def history_to_tuple(history):
    """Deterministic serialization for comparison."""
    out = []
    for s in history.all_states:
        out.append((s.year, tuple(sorted(s.values.items()))))
    return tuple(out)


def test_determinism_same_choices_same_history():
    s0 = create_initial_state(choices_a())
    h1 = simulate(s0, choices_a())
    h2 = simulate(s0, choices_a())
    assert history_to_tuple(h1) == history_to_tuple(h2), "Same config produced different history"
    # Also per-value floating exact
    for a, b in zip(h1.all_states, h2.all_states):
        for var in a.values:
            assert a.values[var] == b.values[var], f"Float mismatch {var} {a.values[var]} vs {b.values[var]}"


def test_determinism_repeated_calls():
    for _ in range(3):
        s0 = create_initial_state(choices_a())
        h = simulate(s0, choices_a())
        t = history_to_tuple(h)
        s0b = create_initial_state(choices_a())
        hb = simulate(s0b, choices_a())
        assert history_to_tuple(hb) == t


def test_portrait_independence():
    # Simulation API must NOT have a portrait argument
    import inspect

    sig = inspect.signature(simulate)
    assert "portrait" not in sig.parameters, "simulate should not accept portrait argument"
    # Verify that shuffling portraits elsewhere does not affect simulation
    # (We simulate that by just calling twice; portraits are not in engine)
    s0 = create_initial_state(choices_a())
    h1 = simulate(s0, choices_a())
    h2 = simulate(s0, choices_a())
    assert history_to_tuple(h1) == history_to_tuple(h2)


def test_history_years():
    s0 = create_initial_state(choices_a())
    h = simulate(s0, choices_a())
    assert h.years == [0, 10, 25, 50, 100], f"Got {h.years}"
    assert len(h.all_states) == 5
    assert h.initial.year == 0
    assert h.steps[0].year == 10
    assert h.steps[-1].year == 100


def test_different_configs_diverge():
    h_a = simulate(create_initial_state(choices_a()), choices_a())
    h_b = simulate(create_initial_state(choices_b()), choices_b())
    # At Year 100, at least several variables differ meaningfully
    a_vals = h_a.state_at(100).values
    b_vals = h_b.state_at(100).values
    diffs = {v: abs(a_vals[v] - b_vals[v]) for v in a_vals}
    significant = sum(1 for d in diffs.values() if d > 2.0)
    assert significant >= 5, f"Configs should diverge, only {significant} vars differ >2.0: {diffs}"
    # They must not be identical histories
    assert history_to_tuple(h_a) != history_to_tuple(h_b)


def test_all_variables_bounded_across_history():
    for choices in [choices_a(), choices_b()]:
        h = simulate(create_initial_state(choices), choices)
        for s in h.all_states:
            for var, val in s.values.items():
                assert 0.0 <= val <= 100.0, f"{var}={val} out of bounds at year {s.year}"
                assert val == val, "NaN"
                assert abs(val) != float("inf"), "inf"


def test_extreme_config_stays_bounded():
    # Deliberately extreme: pick ideologies that push same direction where possible
    extreme = {
        Role.head_of_state: "authoritarian",
        Role.education_minister: "standardization",
        Role.teacher: "marks",
        Role.doctor: "experimental",
        Role.health_food_minister: "minimal_intervention",
        Role.tax_minister: "low_tax",
        Role.justice_minister: "punitive",
        Role.industry_minister: "deregulated",
        Role.science_minister: "mission_driven",
        Role.defense_minister: "standing_force",
    }
    h = simulate(create_initial_state(extreme), extreme)
    for s in h.all_states:
        for var, val in s.values.items():
            assert 0.0 <= val <= 100.0


if __name__ == "__main__":
    test_determinism_same_choices_same_history()
    print("PASS test_determinism_same_choices_same_history")
    test_determinism_repeated_calls()
    print("PASS test_determinism_repeated_calls")
    test_portrait_independence()
    print("PASS test_portrait_independence")
    test_history_years()
    print("PASS test_history_years")
    test_different_configs_diverge()
    print("PASS test_different_configs_diverge")
    test_all_variables_bounded_across_history()
    print("PASS test_all_variables_bounded_across_history")
    test_extreme_config_stays_bounded()
    print("PASS test_extreme_config_stays_bounded")
    print("ALL test_determinism PASSED")
