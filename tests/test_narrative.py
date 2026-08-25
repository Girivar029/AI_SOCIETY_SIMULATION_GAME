"""Narrative determinism, sensitivity, trend, conflict, archetype, no-mutation tests."""
import sys
from pathlib import Path
import copy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config.roles import Role
from src.simulation.state import create_initial_state
from src.simulation.engine import simulate
from src.narrative.reports import generate_history_reports, generate_final_report, generate_era_report
from src.narrative.trends import compute_trends, classify_delta


def config_a():
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

def config_b():
    return {
        Role.head_of_state: "laissez_faire",
        Role.education_minister: "educational_freedom",
        Role.teacher: "holistic",
        Role.doctor: "preventive",
        Role.health_food_minister: "nutrition_first",
        Role.tax_minister: "progressive_tax",
        Role.justice_minister: "restorative",
        Role.industry_minister: "cooperative",
        Role.science_minister: "open_science",
        Role.defense_minister: "minimal_defense",
    }

def config_c():
    return {
        Role.head_of_state: "technocratic",
        Role.education_minister: "meritocracy",
        Role.teacher: "skills",
        Role.doctor: "preventive",
        Role.health_food_minister: "public_prevention",
        Role.tax_minister: "progressive_tax",
        Role.justice_minister: "rehabilitative",
        Role.industry_minister: "deregulated",
        Role.science_minister: "applied_research",
        Role.defense_minister: "technological_defense",
    }

def serialize_reports(reports):
    # Deterministic tuple for comparison (exclude object identity)
    out = []
    for r in reports:
        out.append((
            r.year,
            r.opening,
            tuple((s.title, s.text) for s in r.domain_sections),
            r.dominant_conflict.variable if r.dominant_conflict else None,
            tuple((km.variable, round(km.delta, 6)) for km in r.key_movements),
            tuple(sorted(r.persistent_conflicts)),
            r.ideology_sentence,
        ))
    return tuple(out)

def test_determinism_same_history_same_report():
    h1 = simulate(create_initial_state(config_a()), config_a())
    h2 = simulate(create_initial_state(config_a()), config_a())
    r1 = generate_history_reports(h1)
    r2 = generate_history_reports(h2)
    assert serialize_reports(r1) == serialize_reports(r2), "Same history produced different narrative"
    f1 = generate_final_report(h1)
    f2 = generate_final_report(h2)
    assert f1.final_archetype.key == f2.final_archetype.key
    assert f1.century_summary == f2.century_summary
    assert f1.major_fault_lines == f2.major_fault_lines

def test_state_sensitivity_changes_narrative():
    ha = simulate(create_initial_state(config_a()), config_a())
    hb = simulate(create_initial_state(config_b()), config_b())
    ra = generate_history_reports(ha)
    rb = generate_history_reports(hb)
    # At Year 10, education texts should differ (A low creativity vs B high creativity)
    assert ra[0].education.text != rb[0].education.text
    assert ra[0].society.text != rb[0].society.text
    # Economy also
    assert ra[0].economy.text != rb[0].economy.text

def test_trend_sensitivity():
    # Create two histories where a variable trend direction differs
    ha = simulate(create_initial_state(config_a()), config_a())
    # Config A creativity declines over time; config B rises. Check trend labels differ at Year 25
    hb = simulate(create_initial_state(config_b()), config_b())
    tra = compute_trends(ha, 2)  # state_index 2 = Year25
    trb = compute_trends(hb, 2)
    assert tra["creativity"].label != trb["creativity"].label or tra["creativity"].delta_prev != trb["creativity"].delta_prev
    # Classify delta boundaries
    assert classify_delta(6.0) == "strongly_increasing"
    assert classify_delta(-6.0) == "strongly_decreasing"
    assert classify_delta(0.5) == "stable"
    # Verify persistent detection: Config A creativity should be persistent declining 3 eras
    from src.narrative.reports import generate_final_report
    fa = generate_final_report(ha)
    # At Year100, persistent_conflicts for A should include at least one variable
    assert len(fa.eras[-1].persistent_conflicts) >= 1
    # Year25 trends: creativity for A should be decreasing at least
    assert tra["creativity"].label in ("decreasing", "strongly_decreasing")

def test_conflict_sensitivity():
    # Config A top conflict at Year10 should differ from Config B due to ideology divergence
    ha = simulate(create_initial_state(config_a()), config_a())
    hb = simulate(create_initial_state(config_b()), config_b())
    ra = generate_history_reports(ha)
    rb = generate_history_reports(hb)
    # Dominant conflict variable may differ or pressures differ
    ca = ra[0].dominant_conflict
    cb = rb[0].dominant_conflict
    # At minimum tensions should differ
    assert ca is not None and cb is not None
    # They involve different role sets
    # Check that at least one of variable/tension/roles differs
    differs = (ca.variable != cb.variable) or (abs(ca.tension - cb.tension) > 1e-9) or (ca.positive_roles != cb.positive_roles)
    assert differs, f"Expected conflict difference but got same: {ca} vs {cb}"
    # All conflicts list lengths may differ
    # Ensure conflict report outcome text exists
    assert len(ca.outcome_text) > 10

def test_causal_chain_sensitivity():
    ha = simulate(create_initial_state(config_a()), config_a())
    hc = simulate(create_initial_state(config_c()), config_c())
    ra = generate_history_reports(ha)
    rc = generate_history_reports(hc)
    # Chains are based on actual deltas; they should differ between divergent configs
    # At Year25, collections should not be identical
    chains_a = [(c.path[0], c.path[1]) for c in ra[1].causal_chains]
    chains_c = [(c.path[0], c.path[1]) for c in rc[1].causal_chains]
    # It's okay if they share some edges, but overall report texts should not be byte-identical
    # Stronger: at least one chain differs or count differs
    if chains_a == chains_c and len(chains_a) > 0:
        # Check descriptions differ due to delta magnitudes
        descs_a = [c.description for c in ra[1].causal_chains]
        descs_c = [c.description for c in rc[1].causal_chains]
        assert descs_a != descs_c

def test_final_archetype_different_configs_different():
    ha = simulate(create_initial_state(config_a()), config_a())
    hb = simulate(create_initial_state(config_b()), config_b())
    fa = generate_final_report(ha)
    fb = generate_final_report(hb)
    # They should get different archetypes
    assert fa.final_archetype.key != fb.final_archetype.key, f"Both got {fa.final_archetype.key} — archetype failed to discriminate"
    assert fa.final_archetype.title != fb.final_archetype.title
    assert len(fa.final_archetype.description) > 20
    # Check deterministic classification
    fa2 = generate_final_report(simulate(create_initial_state(config_a()), config_a()))
    assert fa.final_archetype.key == fa2.final_archetype.key

def test_no_simulation_mutation():
    h = simulate(create_initial_state(config_a()), config_a())
    # Snapshot values before narrative
    before = copy.deepcopy([(s.year, dict(s.values)) for s in h.all_states])
    before_choices = copy.deepcopy(h.initial.choices)
    reports = generate_history_reports(h)
    final = generate_final_report(h)
    after = [(s.year, dict(s.values)) for s in h.all_states]
    assert before == after, "Narrative mutated simulation values"
    assert before_choices == h.initial.choices
    # Ensure reports didn't inject explain changes
    for s in h.all_states:
        for var in s.values:
            assert 0.0 <= s.values[var] <= 100.0

def test_structured_observation_api():
    h = simulate(create_initial_state(config_a()), config_a())
    reports = generate_history_reports(h)
    for r in reports:
        # EraReport must expose structured fields
        assert r.year in (10, 25, 50, 100)
        assert isinstance(r.opening, str) and len(r.opening) > 10
        assert hasattr(r, "education") and hasattr(r, "health")
        assert hasattr(r, "dominant_conflict") and hasattr(r, "key_movements")
        assert hasattr(r, "causal_chains") and hasattr(r, "trends")
        assert hasattr(r, "persistent_conflicts") and hasattr(r, "domain_sections")
        assert len(r.domain_sections) == 6
        for s in r.domain_sections:
            assert len(s.text) > 20
        for km in r.key_movements:
            assert hasattr(km, "variable") and hasattr(km, "interpretation")
        for cc in r.causal_chains:
            assert hasattr(cc, "path") and hasattr(cc, "supported")
        # trends dict has all 18 vars
        assert len(r.trends) == 18


if __name__ == "__main__":
    test_determinism_same_history_same_report()
    print("PASS determinism")
    test_state_sensitivity_changes_narrative()
    print("PASS state sensitivity")
    test_trend_sensitivity()
    print("PASS trend sensitivity")
    test_conflict_sensitivity()
    print("PASS conflict sensitivity")
    test_causal_chain_sensitivity()
    print("PASS causal chain sensitivity")
    test_final_archetype_different_configs_different()
    print("PASS archetype")
    test_no_simulation_mutation()
    print("PASS no mutation")
    test_structured_observation_api()
    print("PASS structured API")
    print("ALL test_narrative PASSED")
