"""
Cross-domain propagation edges.

Each edge: source -> target with coefficient (small, < 0.35).
Executed as one controlled pass per era, not iteratively.

These are documented theory links, not hidden modifiers.

Coefficients are intentionally small so cross-domain is second-order vs direct institutional pressure.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    coeff: float
    note: str = ""


# Exactly the minimum set requested plus documentation
EDGES: list[Edge] = [
    Edge("practical_skill", "productivity", 0.22, "skilled workforce boosts output"),
    Edge("creativity", "research_capacity", 0.20, "creative capacity feeds research"),
    Edge("research_capacity", "technological_progress", 0.28, "research yields tech"),
    Edge("public_health", "productivity", 0.18, "healthy workforce more productive"),
    Edge("healthcare_access", "life_expectancy", 0.20, "access extends lives"),
    Edge("inequality", "social_stability", -0.28, "inequality destabilizes (high inequality -> low stability)"),
    Edge("tax_revenue", "state_capacity", 0.25, "revenue enables state capability"),
    Edge("state_capacity", "military_strength", 0.20, "capable state can fund military"),
    Edge("state_capacity", "research_capacity", 0.15, "state funds research infra"),
    Edge("social_stability", "productivity", 0.14, "stable environment enables output"),
    Edge("freedom", "trust", 0.16, "freedom can build trust (or tension)"),
    Edge("trust", "social_stability", 0.18, "trust underpins stability"),
    Edge("industrial_strength", "productivity", 0.22, "industry drives output"),
    Edge("technological_progress", "industrial_strength", 0.20, "tech upgrades industry"),
    # Additional small edges that enrich dynamics without explosion
    Edge("technological_progress", "productivity", 0.12, "tech directly aids productivity"),
    Edge("public_health", "life_expectancy", 0.18, "population health extends lives"),
]

# Validate on import
for e in EDGES:
    assert 0.05 <= abs(e.coeff) <= 0.35, f"Coeff out of intended second-order range: {e}"
    assert e.source != e.target, f"Self-loop not allowed: {e}"

# Helper: edges grouped by source (not needed for single-pass but useful)
EDGES_BY_SOURCE: dict[str, list[Edge]] = {}
for e in EDGES:
    EDGES_BY_SOURCE.setdefault(e.source, []).append(e)
