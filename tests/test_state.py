"""State validity + variable semantics tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config.variables import VAR_NAMES, VARIABLES
from src.config.roles import Role, ROLES
from src.simulation.state import create_initial_state


def default_choices():
    return {
        Role.head_of_state: "technocratic",
        Role.education_minister: "standardization",
        Role.teacher: "skills",
        Role.doctor: "preventive",
        Role.health_food_minister: "public_prevention",
        Role.tax_minister: "progressive_tax",
        Role.justice_minister: "rehabilitative",
        Role.industry_minister: "cooperative",
        Role.science_minister: "basic_research",
        Role.defense_minister: "minimal_defense",
    }


def test_variable_count():
    assert len(VAR_NAMES) == 18


def test_variable_semantics_documented():
    for v in VARIABLES:
        assert v.zero_means, f"{v.name} missing zero_means"
        assert v.hundred_means, f"{v.name} missing hundred_means"
        assert v.group in ("education", "health", "economy", "society", "science", "government")
        assert v.min_value == 0.0 and v.max_value == 100.0
        assert v.start_value == 50.0


def test_initial_state_validity():
    s = create_initial_state(default_choices())
    assert s.year == 0
    assert len(s.values) == 18
    for var in VAR_NAMES:
        assert var in s.values
        v = s.values[var]
        assert 0.0 <= v <= 100.0
        assert v == 50.0


def test_initial_state_bounds_with_overrides():
    s = create_initial_state(default_choices(), overrides={"inequality": 0.0, "freedom": 100.0})
    assert s.values["inequality"] == 0.0
    assert s.values["freedom"] == 100.0
    s.validate()


def test_choices_stored_sorted():
    choices = default_choices()
    s = create_initial_state(choices)
    # Keys sorted by value string
    assert list(s.choices.keys()) == sorted(s.choices.keys(), key=lambda x: x.value)


if __name__ == "__main__":
    test_variable_count()
    print("PASS test_variable_count")
    test_variable_semantics_documented()
    print("PASS test_variable_semantics_documented")
    test_initial_state_validity()
    print("PASS test_initial_state_validity")
    test_initial_state_bounds_with_overrides()
    print("PASS test_initial_state_bounds_with_overrides")
    test_choices_stored_sorted()
    print("PASS test_choices_stored_sorted")
    print("ALL test_state PASSED")
