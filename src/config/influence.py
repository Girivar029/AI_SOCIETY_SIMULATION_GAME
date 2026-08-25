"""
Institutional influence matrix.

Influence[role][variable] in 0.0–1.5
  0.0 = no influence
  1.0 = normal influence
  1.5 = very strong
Plus a global role weight (broad vs specialized).
Weighted pressure = vector * influence * global_weight
"""

from src.config.roles import Role
from src.config.variables import VAR_NAMES

# Global role weights — broad vs niche. Head of State broad but not dominant per-variable.
GLOBAL_WEIGHT: dict[Role, float] = {
    Role.head_of_state: 0.85,
    Role.education_minister: 1.10,
    Role.teacher: 0.95,
    Role.doctor: 0.95,
    Role.health_food_minister: 1.05,
    Role.tax_minister: 1.10,
    Role.justice_minister: 1.00,
    Role.industry_minister: 1.10,
    Role.science_minister: 1.00,
    Role.defense_minister: 0.90,
}

# Domain-specific influence matrix. Sparse storage: missing == 0.30 (weak generic) for Head of State,
# 0.05 for others (essentially no influence on irrelevant domain). Explicit entries override.
# Values chosen to create real conflicts (multiple roles influence same variable) while preserving specialization.

# Base helper to build full matrix from explicit overrides
_EXPLICIT: dict[Role, dict[str, float]] = {
    Role.head_of_state: {
        # Broad — moderate on many, not maximal anywhere
        "social_stability": 0.90,
        "freedom": 0.90,
        "trust": 0.75,
        "state_capacity": 0.85,
        "military_strength": 0.55,
        "wealth": 0.45,
        "productivity": 0.40,
        "inequality": 0.45,
        "research_capacity": 0.35,
        "academic_performance": 0.30,
        "public_health": 0.30,
        "tax_revenue": 0.40,
    },
    Role.education_minister: {
        "academic_performance": 1.50,
        "practical_skill": 1.10,
        "creativity": 1.00,
        "research_capacity": 0.60,
        "trust": 0.35,
        "social_stability": 0.30,
        "inequality": 0.45,
    },
    Role.teacher: {
        "academic_performance": 1.20,
        "practical_skill": 1.40,
        "creativity": 1.35,
        "research_capacity": 0.45,
        "trust": 0.40,
        "social_stability": 0.30,
    },
    Role.doctor: {
        "public_health": 1.50,
        "life_expectancy": 1.30,
        "healthcare_access": 1.00,
        "research_capacity": 0.35,
        "trust": 0.30,
        "productivity": 0.25,
    },
    Role.health_food_minister: {
        "public_health": 1.40,
        "life_expectancy": 1.20,
        "healthcare_access": 1.20,
        "productivity": 0.40,
        "state_capacity": 0.40,
        "wealth": 0.25,
        "freedom": 0.30,
    },
    Role.tax_minister: {
        "tax_revenue": 1.50,
        "wealth": 1.00,
        "inequality": 1.40,
        "productivity": 0.70,
        "state_capacity": 0.80,
        "social_stability": 0.50,
        "trust": 0.35,
        "industrial_strength": 0.40,
    },
    Role.justice_minister: {
        "social_stability": 1.30,
        "freedom": 1.40,
        "trust": 1.20,
        "state_capacity": 0.60,
        "military_strength": 0.30,
        "research_capacity": 0.25,
    },
    Role.industry_minister: {
        "industrial_strength": 1.50,
        "productivity": 1.40,
        "wealth": 1.10,
        "technological_progress": 0.50,
        "state_capacity": 0.35,
        "inequality": 0.50,
        "trust": 0.30,
    },
    Role.science_minister: {
        "research_capacity": 1.50,
        "technological_progress": 1.45,
        "creativity": 0.70,
        "productivity": 0.45,
        "industrial_strength": 0.55,
        "academic_performance": 0.40,
        "trust": 0.30,
    },
    Role.defense_minister: {
        "military_strength": 1.50,
        "state_capacity": 0.80,
        "technological_progress": 0.45,
        "research_capacity": 0.35,
        "wealth": 0.30,
        "social_stability": 0.40,
        "freedom": 0.35,
    },
}

# Default influence for unspecified variables per role
_DEFAULT_BY_ROLE: dict[Role, float] = {
    Role.head_of_state: 0.30,
    Role.education_minister: 0.05,
    Role.teacher: 0.05,
    Role.doctor: 0.05,
    Role.health_food_minister: 0.05,
    Role.tax_minister: 0.05,
    Role.justice_minister: 0.05,
    Role.industry_minister: 0.05,
    Role.science_minister: 0.05,
    Role.defense_minister: 0.05,
}


def build_influence_matrix() -> dict[Role, dict[str, float]]:
    matrix: dict[Role, dict[str, float]] = {}
    for role in Role:
        role_map: dict[str, float] = {}
        explicit = _EXPLICIT.get(role, {})
        default = _DEFAULT_BY_ROLE[role]
        for var in VAR_NAMES:
            role_map[var] = explicit.get(var, default)
            assert 0.0 <= role_map[var] <= 1.5, f"Influence out of range {role} {var} {role_map[var]}"
        matrix[role] = role_map
    return matrix


INFLUENCE: dict[Role, dict[str, float]] = build_influence_matrix()


def get_influence(role: Role, variable: str) -> float:
    return INFLUENCE[role][variable]


def get_global_weight(role: Role) -> float:
    return GLOBAL_WEIGHT[role]
