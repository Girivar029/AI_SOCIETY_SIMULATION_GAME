"""
Variable registry for the deterministic simulation.

All 18 variables are 0.0–100.0 with default start 50.0.
No moral polarity is encoded in the engine; 0/100 meanings are descriptive.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class VariableDef:
    name: str
    min_value: float = 0.0
    max_value: float = 100.0
    start_value: float = 50.0
    zero_means: str = ""
    hundred_means: str = ""
    group: str = ""
    # polarity is purely documentary: whether high is intuitively "good"
    # but engine treats it neutrally. Kept for narrative hints later.
    polarity_note: str = ""


# ---------------------------------------------------------------------------
# 18-variable MVP set (order is deterministic iteration order — do not use sets)
# ---------------------------------------------------------------------------
VARIABLES: list[VariableDef] = [
    # Education
    VariableDef(
        name="academic_performance",
        zero_means="widespread educational failure; negligible test/knowledge outcomes",
        hundred_means="peak standardized academic achievement across population",
        group="education",
        polarity_note="high = strong test/academic outcomes, not necessarily holistic quality",
    ),
    VariableDef(
        name="practical_skill",
        zero_means="population lacks usable vocational/practical competencies",
        hundred_means="population highly skilled in applied, hands-on domains",
        group="education",
        polarity_note="high = strong applied capability",
    ),
    VariableDef(
        name="creativity",
        zero_means="conformist, rote output; negligible original thought",
        hundred_means="highly inventive, divergent thinking across population",
        group="education",
        polarity_note="high = strong creative/divergent capacity",
    ),
    # Health
    VariableDef(
        name="life_expectancy",
        zero_means="extremely short average lifespan",
        hundred_means="extremely long average lifespan",
        group="health",
        polarity_note="high = longer lives (generally desired)",
    ),
    VariableDef(
        name="public_health",
        zero_means="endemic illness, poor sanitation/prevention",
        hundred_means="excellent population-level preventive health",
        group="health",
        polarity_note="high = healthier population stock",
    ),
    VariableDef(
        name="healthcare_access",
        zero_means="care is scarce or unreachable for most",
        hundred_means="care is widely accessible and timely",
        group="health",
        polarity_note="high = broad access",
    ),
    # Economy
    VariableDef(
        name="productivity",
        zero_means="economy produces very little per capita",
        hundred_means="very high output per capita",
        group="economy",
        polarity_note="high = more output",
    ),
    VariableDef(
        name="wealth",
        zero_means="extreme material poverty (aggregate)",
        hundred_means="great aggregate material wealth",
        group="economy",
        polarity_note="high = richer in aggregate (distribution separate)",
    ),
    VariableDef(
        name="inequality",
        zero_means="extremely equal distribution of wealth/income",
        hundred_means="extreme concentration of wealth in few hands",
        group="economy",
        polarity_note="high = MORE unequal (inverted desirability; neutral in engine)",
    ),
    VariableDef(
        name="industrial_strength",
        zero_means="negligible industrial capacity",
        hundred_means="formidable industrial capacity",
        group="economy",
        polarity_note="high = strong industry",
    ),
    VariableDef(
        name="tax_revenue",
        zero_means="state collects almost no revenue",
        hundred_means="state collects very high revenue (capacity, not rate)",
        group="economy",
        polarity_note="high = high fiscal intake",
    ),
    # Society
    VariableDef(
        name="social_stability",
        zero_means="chronic unrest, frequent disruptions",
        hundred_means="highly stable, predictable social order",
        group="society",
        polarity_note="high = more stable (can trade off with freedom)",
    ),
    VariableDef(
        name="freedom",
        zero_means="extremely restricted liberties",
        hundred_means="extremely broad individual freedoms",
        group="society",
        polarity_note="high = more liberty",
    ),
    VariableDef(
        name="trust",
        zero_means="pervasive distrust (interpersonal + institutional)",
        hundred_means="high generalized and institutional trust",
        group="society",
        polarity_note="high = higher trust",
    ),
    # Science / Government
    VariableDef(
        name="research_capacity",
        zero_means="negligible ability to conduct research",
        hundred_means="world-leading research infrastructure and talent",
        group="science",
        polarity_note="high = stronger research base",
    ),
    VariableDef(
        name="technological_progress",
        zero_means="technological stagnation",
        hundred_means="rapid, broad technological advancement",
        group="science",
        polarity_note="high = more tech progress",
    ),
    VariableDef(
        name="state_capacity",
        zero_means="state cannot implement policy or deliver services",
        hundred_means="state highly capable of execution and delivery",
        group="government",
        polarity_note="high = capable state (can coexist with low freedom)",
    ),
    VariableDef(
        name="military_strength",
        zero_means="negligible defense capability",
        hundred_means="formidable military capability",
        group="government",
        polarity_note="high = stronger military",
    ),
]

# Derived helpers — deterministic order preserved
VAR_NAMES: list[str] = [v.name for v in VARIABLES]
VAR_MAP: dict[str, VariableDef] = {v.name: v for v in VARIABLES}
START_VALUES: dict[str, float] = {v.name: v.start_value for v in VARIABLES}

# Validation that MVP is exactly 18
assert len(VARIABLES) == 18, f"expected 18 variables, got {len(VARIABLES)}"
assert len(VAR_NAMES) == len(set(VAR_NAMES)), "duplicate variable names"

# Grouping helper
GROUPS: dict[str, list[str]] = {}
for v in VARIABLES:
    GROUPS.setdefault(v.group, []).append(v.name)
