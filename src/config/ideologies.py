"""
Ideology inventory + ideology vectors.

Each role has exactly 4 ideological choices.
Each ideology maps to a sparse vector: variable -> pressure in [-1.0, +1.0].
Pressure is directional preference strength, NOT final state delta.

Design principles (documented trade-offs):
- 4-8 non-zero entries per ideology.
- Every ideology has at least one negative pressure (cost/trade-off).
- No ideology is universally positive/negative.
- Magnitudes comparable across ideologies (L1 roughly 2.5-4.5) so no ideology is accidentally stronger.
- Direct-domain effects stronger (0.6-0.95) than distant effects (0.15-0.35).
"""

from src.config.roles import Role

# ---------------------------------------------------------------------------
# Ideology names per role (stable strings)
# ---------------------------------------------------------------------------
IDEOLOGIES: dict[Role, list[str]] = {
    Role.head_of_state: ["authoritarian", "technocratic", "populist", "laissez_faire"],
    Role.education_minister: ["standardization", "meritocracy", "equal_access", "educational_freedom"],
    Role.teacher: ["discipline", "marks", "skills", "holistic"],
    Role.doctor: ["preventive", "treatment_first", "experimental", "traditional"],
    Role.health_food_minister: ["public_prevention", "clinical_access", "nutrition_first", "minimal_intervention"],
    Role.tax_minister: ["low_tax", "flat_tax", "progressive_tax", "redistribution"],
    Role.justice_minister: ["punitive", "rehabilitative", "restorative", "strict_procedure"],
    Role.industry_minister: ["protectionist", "deregulated", "state_directed", "cooperative"],
    Role.science_minister: ["basic_research", "applied_research", "open_science", "mission_driven"],
    Role.defense_minister: ["standing_force", "minimal_defense", "technological_defense", "mass_mobilization"],
}

# Reverse map ideology -> role for validation
IDEOLOGY_TO_ROLE: dict[str, Role] = {}
for role, names in IDEOLOGIES.items():
    for n in names:
        # ideology names are unique across roles in this design (intentional)
        IDEOLOGY_TO_ROLE[n] = role

# ---------------------------------------------------------------------------
# Vectors: Role -> Ideology -> {variable: pressure}
# ---------------------------------------------------------------------------
# We keep vectors sparse and documented. Values are pressure coefficients.

VECTORS: dict[Role, dict[str, dict[str, float]]] = {
    Role.head_of_state: {
        # Broad influence, moderate magnitude. Each has distinct society/government trade-off.
        "authoritarian": {
            # Order/control at cost of freedom/trust/creativity.
            "social_stability": 0.75,
            "state_capacity": 0.65,
            "military_strength": 0.35,
            "freedom": -0.70,
            "trust": -0.40,
            "creativity": -0.30,
            "research_capacity": -0.15,
        },
        "technocratic": {
            "state_capacity": 0.60,
            "research_capacity": 0.40,
            "technological_progress": 0.30,
            "productivity": 0.35,
            "public_health": 0.20,
            "trust": 0.25,
            "freedom": -0.20,
            "inequality": 0.25,  # technocracy can concentrate gains
        },
        "populist": {
            "trust": 0.30,  # short-term mobilization
            "social_stability": -0.30,
            "wealth": 0.20,
            "inequality": -0.30,  # rhetorical redistribution
            "freedom": 0.25,
            "state_capacity": -0.35,
            "research_capacity": -0.25,
            "productivity": -0.15,
        },
        "laissez_faire": {
            "freedom": 0.55,
            "productivity": 0.30,
            "wealth": 0.35,
            "trust": 0.15,
            "state_capacity": -0.55,
            "social_stability": -0.25,
            "tax_revenue": -0.40,
            "inequality": 0.45,
        },
    },
    Role.education_minister: {
        "standardization": {
            # High academic, discipline, at creativity/equality cost.
            "academic_performance": 0.85,
            "practical_skill": -0.15,
            "creativity": -0.55,
            "social_stability": 0.15,
            "trust": -0.15,
            "research_capacity": -0.10,
        },
        "meritocracy": {
            "academic_performance": 0.65,
            "research_capacity": 0.35,
            "creativity": 0.20,
            "productivity": 0.20,
            "inequality": 0.50,  # sorting creates divergence
            "trust": -0.20,
            "wealth": 0.15,
        },
        "equal_access": {
            "academic_performance": 0.25,
            "creativity": 0.35,
            "practical_skill": 0.20,
            "trust": 0.30,
            "social_stability": 0.25,
            "inequality": -0.55,
            "tax_revenue": -0.20,  # costs
        },
        "educational_freedom": {
            "creativity": 0.75,
            "practical_skill": 0.40,
            "academic_performance": -0.30,
            "freedom": 0.40,
            "research_capacity": 0.20,
            "social_stability": -0.15,
            "trust": 0.15,
        },
    },
    Role.teacher: {
        "discipline": {
            "academic_performance": 0.45,
            "creativity": -0.50,
            "practical_skill": 0.20,
            "social_stability": 0.25,
            "freedom": -0.25,
            "trust": -0.15,
        },
        "marks": {
            "academic_performance": 0.90,
            "creativity": -0.40,
            "practical_skill": -0.25,
            "research_capacity": 0.15,
            "trust": -0.10,
            "social_stability": 0.10,
        },
        "skills": {
            # Strong practical/creativity at academic cost — the canonical trade-off example.
            "practical_skill": 0.90,
            "creativity": 0.55,
            "academic_performance": -0.30,
            "productivity": 0.30,
            "research_capacity": 0.20,
            "industrial_strength": 0.20,
            "freedom": 0.10,
        },
        "holistic": {
            "creativity": 0.60,
            "practical_skill": 0.30,
            "academic_performance": 0.15,
            "trust": 0.30,
            "social_stability": 0.20,
            "freedom": 0.20,
            "productivity": -0.10,  # slower, reflective
        },
    },
    Role.doctor: {
        "preventive": {
            "public_health": 0.85,
            "life_expectancy": 0.50,
            "healthcare_access": 0.15,
            "productivity": 0.20,
            "research_capacity": 0.10,
            "wealth": -0.10,  # upfront prevention costs
        },
        "treatment_first": {
            "healthcare_access": 0.80,
            "life_expectancy": 0.40,
            "public_health": -0.15,
            "wealth": -0.20,
            "trust": 0.20,
            "technological_progress": 0.10,
        },
        "experimental": {
            "research_capacity": 0.50,
            "technological_progress": 0.45,
            "life_expectancy": 0.20,
            "public_health": -0.25,
            "trust": -0.30,
            "healthcare_access": -0.10,
        },
        "traditional": {
            "trust": 0.35,
            "public_health": 0.25,
            "life_expectancy": 0.15,
            "research_capacity": -0.40,
            "technological_progress": -0.35,
            "healthcare_access": 0.10,
        },
    },
    Role.health_food_minister: {
        "public_prevention": {
            "public_health": 0.80,
            "life_expectancy": 0.45,
            "productivity": 0.25,
            "state_capacity": 0.20,
            "wealth": -0.15,
            "freedom": -0.20,
        },
        "clinical_access": {
            "healthcare_access": 0.85,
            "life_expectancy": 0.40,
            "public_health": 0.15,
            "tax_revenue": -0.25,
            "trust": 0.25,
            "state_capacity": 0.15,
        },
        "nutrition_first": {
            "public_health": 0.55,
            "life_expectancy": 0.45,
            "productivity": 0.20,
            "wealth": -0.10,
            "trust": 0.15,
            "creativity": 0.10,
        },
        "minimal_intervention": {
            "freedom": 0.40,
            "wealth": 0.20,
            "tax_revenue": 0.15,
            "public_health": -0.55,
            "life_expectancy": -0.35,
            "healthcare_access": -0.30,
            "state_capacity": -0.25,
        },
    },
    Role.tax_minister: {
        "low_tax": {
            "wealth": 0.45,
            "productivity": 0.35,
            "freedom": 0.30,
            "industrial_strength": 0.25,
            "tax_revenue": -0.85,
            "state_capacity": -0.40,
            "inequality": 0.50,
            "public_health": -0.15,
        },
        "flat_tax": {
            "wealth": 0.25,
            "productivity": 0.20,
            "tax_revenue": 0.15,
            "trust": 0.10,
            "inequality": 0.15,
            "state_capacity": 0.10,
            "social_stability": -0.10,
        },
        "progressive_tax": {
            "inequality": -0.65,
            "tax_revenue": 0.50,
            "social_stability": 0.30,
            "trust": 0.20,
            "state_capacity": 0.30,
            "productivity": -0.20,
            "wealth": -0.10,
        },
        "redistribution": {
            "inequality": -0.90,
            "wealth": -0.15,
            "social_stability": 0.35,
            "trust": 0.25,
            "tax_revenue": 0.40,
            "state_capacity": 0.25,
            "productivity": -0.35,
            "freedom": -0.20,
        },
    },
    Role.justice_minister: {
        "punitive": {
            "social_stability": 0.50,  # short-term order
            "freedom": -0.55,
            "trust": -0.40,
            "state_capacity": 0.25,
            "military_strength": 0.15,
            "research_capacity": -0.10,
        },
        "rehabilitative": {
            "trust": 0.40,
            "social_stability": 0.25,
            "freedom": 0.20,
            "productivity": 0.15,
            "state_capacity": -0.15,
            "military_strength": -0.10,
        },
        "restorative": {
            "trust": 0.55,
            "social_stability": 0.20,
            "freedom": 0.25,
            "creativity": 0.15,
            "state_capacity": -0.10,
            "productivity": 0.10,
        },
        "strict_procedure": {
            "trust": 0.30,
            "freedom": 0.15,
            "social_stability": 0.20,
            "state_capacity": 0.20,
            "productivity": -0.15,
            "military_strength": -0.05,
        },
    },
    Role.industry_minister: {
        "protectionist": {
            "industrial_strength": 0.65,
            "productivity": 0.15,
            "social_stability": 0.15,
            "wealth": -0.15,
            "technological_progress": -0.30,
            "trust": -0.15,
            "inequality": -0.10,
        },
        "deregulated": {
            "industrial_strength": 0.55,
            "productivity": 0.50,
            "wealth": 0.40,
            "freedom": 0.25,
            "inequality": 0.50,
            "public_health": -0.20,
            "social_stability": -0.20,
        },
        "state_directed": {
            "industrial_strength": 0.70,
            "state_capacity": 0.50,
            "productivity": 0.20,
            "military_strength": 0.25,
            "freedom": -0.35,
            "creativity": -0.20,
            "tax_revenue": -0.20,
        },
        "cooperative": {
            "industrial_strength": 0.35,
            "trust": 0.45,
            "social_stability": 0.30,
            "productivity": 0.20,
            "inequality": -0.35,
            "wealth": 0.10,
            "creativity": 0.15,
        },
    },
    Role.science_minister: {
        "basic_research": {
            "research_capacity": 0.85,
            "technological_progress": 0.35,
            "creativity": 0.25,
            "wealth": -0.20,
            "productivity": -0.10,
            "state_capacity": -0.10,
        },
        "applied_research": {
            "technological_progress": 0.75,
            "productivity": 0.40,
            "industrial_strength": 0.35,
            "research_capacity": 0.30,
            "wealth": 0.15,
            "creativity": -0.10,
        },
        "open_science": {
            "research_capacity": 0.55,
            "trust": 0.35,
            "creativity": 0.35,
            "technological_progress": 0.30,
            "freedom": 0.20,
            "state_capacity": -0.15,
        },
        "mission_driven": {
            "technological_progress": 0.60,
            "military_strength": 0.40,
            "research_capacity": 0.40,
            "state_capacity": 0.25,
            "freedom": -0.25,
            "creativity": -0.20,
        },
    },
    Role.defense_minister: {
        "standing_force": {
            "military_strength": 0.85,
            "state_capacity": 0.35,
            "social_stability": 0.20,
            "tax_revenue": -0.35,
            "wealth": -0.25,
            "freedom": -0.15,
            "technological_progress": 0.10,
        },
        "minimal_defense": {
            "wealth": 0.30,
            "freedom": 0.25,
            "trust": 0.20,
            "tax_revenue": 0.20,
            "military_strength": -0.75,
            "state_capacity": -0.20,
            "social_stability": -0.15,
        },
        "technological_defense": {
            "military_strength": 0.60,
            "technological_progress": 0.45,
            "research_capacity": 0.30,
            "wealth": -0.20,
            "tax_revenue": -0.25,
            "industrial_strength": 0.20,
        },
        "mass_mobilization": {
            "military_strength": 0.55,
            "social_stability": -0.20,
            "freedom": -0.40,
            "trust": -0.20,
            "state_capacity": 0.30,
            "industrial_strength": 0.15,
            "productivity": -0.15,
        },
    },
}


def get_vector(role: Role, ideology: str) -> dict[str, float]:
    """Retrieve vector for role+ideology. Raises if unknown."""
    try:
        return VECTORS[role][ideology]
    except KeyError as e:
        raise ValueError(f"Unknown role/ideology: {role}/{ideology}") from e


def validate_vectors() -> None:
    for role, id_map in VECTORS.items():
        expected = set(IDEOLOGIES[role])
        actual = set(id_map.keys())
        assert expected == actual, f"Vector ideology mismatch for {role}: {expected} vs {actual}"
        for ideology, vec in id_map.items():
            for var, pressure in vec.items():
                assert -1.0 <= pressure <= 1.0, f"Pressure out of range {role}/{ideology}/{var}={pressure}"
                # variable must exist
                from src.config.variables import VAR_MAP

                assert var in VAR_MAP, f"Unknown variable {var} in {role}/{ideology}"
            # trade-off check: at least one negative
            assert any(v < 0 for v in vec.values()), f"No trade-off (no negative) in {role}/{ideology}"
            assert 2 <= len(vec) <= 10, f"Vector size unexpected {role}/{ideology}: {len(vec)}"


# Validate on import (deterministic, no I/O)
validate_vectors()
