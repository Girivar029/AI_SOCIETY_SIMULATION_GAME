"""Engine-specific: conflict, cross-domain, momentum tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config.roles import Role
from src.simulation.state import create_initial_state
from src.simulation.engine import simulate, step
from src.simulation.conflicts import aggregate_pressures, CONFLICT_EPSILON
from src.config.cross_domain import EDGES


def choices_conflict_creativity():
    """Teacher skills (+creativity) vs Education Minister standardization (-creativity) => conflict on creativity."""
    return {
        Role.head_of_state: "technocratic",
        Role.education_minister: "standardization",  # creativity -0.55
        Role.teacher: "skills",  # creativity +0.55
        Role.doctor: "preventive",
        Role.health_food_minister: "public_prevention",
        Role.tax_minister: "flat_tax",
        Role.justice_minister: "strict_procedure",
        Role.industry_minister: "cooperative",
        Role.science_minister: "basic_research",
        Role.defense_minister: "minimal_defense",
    }


def choices_no_conflict():
    """Align education ideologies to avoid creativity conflict."""
    return {
        Role.head_of_state: "technocratic",
        Role.education_minister: "educational_freedom",  # creativity +0.75
        Role.teacher: "skills",  # creativity +0.55 (same sign)
        Role.doctor: "preventive",
        Role.health_food_minister: "public_prevention",
        Role.tax_minister: "flat_tax",
        Role.justice_minister: "strict_procedure",
        Role.industry_minister: "cooperative",
        Role.science_minister: "basic_research",
        Role.defense_minister: "minimal_defense",
    }


def test_conflict_detection():
    pressures = aggregate_pressures(choices_conflict_creativity())
    vp = pressures["creativity"]
    # Should be conflict: both sides exceed epsilon
    assert vp.is_conflict, f"Expected conflict on creativity, pos={vp.positive_sum} neg={vp.negative_sum}"
    assert vp.tension > 0.1, f"Tension too low {vp.tension}"
    # Attenuation should be <1.0 when conflict
    assert 0.40 <= vp.attenuation < 1.0, f"Attenuation {vp.attenuation}"

    # No-conflict case: both positive => no conflict
    pressures2 = aggregate_pressures(choices_no_conflict())
    vp2 = pressures2["creativity"]
    assert not vp2.is_conflict, f"Should not be conflict when aligned: pos={vp2.positive_sum} neg={vp2.negative_sum}"
    assert vp2.attenuation == 1.0


def test_conflict_small_noise_not_flagged():
    # Use a config where only tiny pressures exist on a variable -> no conflict
    # e.g., pick roles that don't touch 'military_strength' except defense + head_of_state
    # Both push same direction in our choices => no conflict expected on military_strength if magnitudes small
    # Instead test epsilon boundary directly via synthetic: create pressures with small pos/neg < epsilon
    # We do it via aggregate: find a variable with no ideology vector covering it strongly for both sides
    pressures = aggregate_pressures(choices_no_conflict())
    # Find a variable with small both sides (if any) should not be conflict
    for var, vp in pressures.items():
        if abs(vp.positive_sum) < CONFLICT_EPSILON or abs(vp.negative_sum) < CONFLICT_EPSILON:
            assert not vp.is_conflict or (vp.positive_sum > CONFLICT_EPSILON and vp.negative_sum < -CONFLICT_EPSILON)


def test_cross_domain_propagation():
    """Changing source pressure should affect documented downstream variable beyond direct institutional effect."""
    # We test: practical_skill -> productivity edge exists
    assert any(e.source == "practical_skill" and e.target == "productivity" for e in EDGES)

    # Create two configs differing mainly in Teacher ideology (skills vs marks)
    base = {
        Role.head_of_state: "laissez_faire",
        Role.education_minister: "equal_access",
        Role.teacher: "marks",  # practical_skill -0.25
        Role.doctor: "preventive",
        Role.health_food_minister: "public_prevention",
        Role.tax_minister: "flat_tax",
        Role.justice_minister: "strict_procedure",
        Role.industry_minister: "cooperative",
        Role.science_minister: "basic_research",
        Role.defense_minister: "minimal_defense",
    }
    variant = dict(base)
    variant[Role.teacher] = "skills"  # practical_skill +0.90 (higher)

    h_base = simulate(create_initial_state(base), base)
    h_variant = simulate(create_initial_state(variant), variant)

    # productivity at Year 10 should differ due to practical_skill difference + cross propagation
    prod_base = h_base.state_at(10).values["productivity"]
    prod_variant = h_variant.state_at(10).values["productivity"]
    # Also practical_skill itself should differ
    skill_base = h_base.state_at(10).values["practical_skill"]
    skill_variant = h_variant.state_at(10).values["practical_skill"]
    assert skill_variant > skill_base, f"skills teacher should give higher practical_skill: {skill_variant} vs {skill_base}"
    assert prod_variant > prod_base, f"Cross-domain: higher skill should yield higher productivity: {prod_variant} vs {prod_base}"

    # Verify Year 0 cross didn't affect Year 0 values (pre-simulation)
    assert h_base.state_at(0).values["productivity"] == 50.0


def test_cross_domain_coefficients_small():
    for e in EDGES:
        assert 0.05 <= abs(e.coeff) <= 0.35, f"Coeff out of expected range {e}"


def test_momentum_damping():
    """Same pressure under later era (higher inertia) should move less than early era."""
    # Use same choices and compare delta magnitudes era 0 (inertia 0.35) vs era 3 (0.70)
    choices = {
        Role.head_of_state: "technocratic",
        Role.education_minister: "standardization",
        Role.teacher: "marks",
        Role.doctor: "preventive",
        Role.health_food_minister: "public_prevention",
        Role.tax_minister: "progressive_tax",
        Role.justice_minister: "rehabilitative",
        Role.industry_minister: "state_directed",
        Role.science_minister: "applied_research",
        Role.defense_minister: "standing_force",
    }
    # First step vs later step: we need to isolate raw movement
    # Simulate and measure per-era deltas for a variable that moves consistently (e.g., tax_revenue)
    h = simulate(create_initial_state(choices), choices)
    # Deltas: 0->10, 10->25, 25->50, 50->100
    deltas = []
    states = h.all_states
    for i in range(1, len(states)):
        delta = states[i].values["tax_revenue"] - states[i - 1].values["tax_revenue"]
        deltas.append(delta)
    # Not asserting strict monotonic decrease because contextual modifiers and cross-domain interact,
    # but verify that effective dampening exists: later era inertia is higher, so if raw pressures were constant,
    # movement per year decreases. We check (delta / years) declines after era 0 for a stable-direction variable.
    # Pick a variable with consistent direction; tax_revenue with progressive_tax should trend up
    # Let's check per-year rate
    years = [10, 15, 25, 50]
    rates = [abs(deltas[i]) / years[i] for i in range(4)]
    # Rate in era 3 should be <= rate in era 0 (higher inertia dominates despite longer interval)
    # Allow some tolerance due to contextual but expect dampening
    assert rates[3] <= rates[0] + 0.05, f"Later era per-year rate should be dampened: {rates}"


def test_step_api():
    choices = {
        Role.head_of_state: "populist",
        Role.education_minister: "meritocracy",
        Role.teacher: "holistic",
        Role.doctor: "traditional",
        Role.health_food_minister: "nutrition_first",
        Role.tax_minister: "redistribution",
        Role.justice_minister: "restorative",
        Role.industry_minister: "protectionist",
        Role.science_minister: "open_science",
        Role.defense_minister: "mass_mobilization",
    }
    s0 = create_initial_state(choices)
    s10 = step(s0, choices, 0)
    assert s10.year == 10
    s25 = step(s10, choices, 1)
    assert s25.year == 25
    # Step should produce explainability
    assert s10.explain is not None
    assert s25.explain is not None
    assert len(s10.explain.conflicts) >= 0
    # History via simulate should equal sequential steps
    h = simulate(s0, choices)
    assert h.state_at(10).values == s10.values
    assert h.steps[1].values == s25.values


def test_explainability_retained():
    choices = choices_conflict_creativity()
    h = simulate(create_initial_state(choices), choices)
    for s in h.steps:
        assert s.explain is not None
        assert s.explain.era_index in (0, 1, 2, 3)
        # Pressures for all 18 vars should be present
        assert len(s.explain.pressures) == 18
        # Each pressure should have at least net/effective computed
        for var, vp in s.explain.pressures.items():
            assert isinstance(vp.net, float)
            assert isinstance(vp.effective_pressure, float)


if __name__ == "__main__":
    test_conflict_detection()
    print("PASS test_conflict_detection")
    test_conflict_small_noise_not_flagged()
    print("PASS test_conflict_small_noise_not_flagged")
    test_cross_domain_propagation()
    print("PASS test_cross_domain_propagation")
    test_cross_domain_coefficients_small()
    print("PASS test_cross_domain_coefficients_small")
    test_momentum_damping()
    print("PASS test_momentum_damping")
    test_step_api()
    print("PASS test_step_api")
    test_explainability_retained()
    print("PASS test_explainability_retained")
    print("ALL test_engine PASSED")
