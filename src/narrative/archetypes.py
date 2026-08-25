"""
Final archetype classification — deterministic mapping from final state to descriptive label.

No moral ranking; purely descriptive.
"""

from dataclasses import dataclass
from src.simulation.state import State


@dataclass(frozen=True)
class Archetype:
    key: str
    title: str
    description: str
    # Which scoring logic triggered it (for explainability)
    reasons: list[str]


# Helper thresholds
HIGH = 68.0
LOW = 38.0
MID_HIGH = 60.0

# We use a small rule set: each archetype has a predicate over final values.
# Classification picks the best-matching archetype deterministically;
# if no predicate matches, returns Mixed / Transitional.

def _reasons(state: State, checks: list[tuple[bool, str]]) -> list[str]:
    return [msg for ok, msg in checks if ok]


def classify_archetype(final: State) -> Archetype:
    v = final.values  # alias

    # Precompute booleans deterministically (no set iteration)
    high_stability = v["social_stability"] >= HIGH
    high_freedom = v["freedom"] >= HIGH
    low_freedom = v["freedom"] <= LOW
    high_trust = v["trust"] >= HIGH
    low_trust = v["trust"] <= LOW
    high_capacity = v["state_capacity"] >= HIGH
    low_capacity = v["state_capacity"] <= LOW
    high_military = v["military_strength"] >= HIGH
    high_tech = v["technological_progress"] >= HIGH
    high_research = v["research_capacity"] >= HIGH
    low_research = v["research_capacity"] <= LOW
    high_inequality = v["inequality"] >= HIGH
    low_inequality = v["inequality"] <= LOW
    high_wealth = v["wealth"] >= MID_HIGH
    high_productivity = v["productivity"] >= HIGH
    low_productivity = v["productivity"] <= LOW
    high_health = v["public_health"] >= HIGH and v["life_expectancy"] >= MID_HIGH
    low_health = v["public_health"] <= LOW

    # Order matters: first match wins deterministically.
    # We test from most distinctive to least.

    # 1. Militarized state — strong military + high capacity + low freedom
    if high_military and high_capacity and low_freedom:
        rs = _reasons(final, [
            (high_military, f"formidable military ({v['military_strength']:.0f})"),
            (high_capacity, f"high state capacity ({v['state_capacity']:.0f})"),
            (low_freedom, f"restricted freedom ({v['freedom']:.0f})"),
        ])
        return Archetype(
            key="militarized_state",
            title="Militarized State",
            description="A highly capable coercive state whose military power exceeds its civilian institutions. Order is maintained through institutional control, at the cost of personal liberty.",
            reasons=rs,
        )

    # 2. High-control industrial society — high stability, high industry, low freedom, moderate/ high tech
    if high_stability and low_freedom and v["industrial_strength"] >= HIGH:
        rs = _reasons(final, [
            (high_stability, f"strong social stability ({v['social_stability']:.0f})"),
            (low_freedom, f"narrowed freedom ({v['freedom']:.0f})"),
            (v["industrial_strength"] >= HIGH, f"formidable industry ({v['industrial_strength']:.0f})"),
        ])
        return Archetype(
            key="high_control_industrial",
            title="High-Control Industrial Society",
            description="A tightly managed industrial order with strong output and stability, sustained by institutional discipline rather than voluntary cooperation.",
            reasons=rs,
        )

    # 3. Open innovation society — high freedom, high trust, high research/tech, creativity high
    if high_freedom and high_trust and high_tech and v["creativity"] >= MID_HIGH and high_research:
        rs = _reasons(final, [
            (high_freedom, f"broad freedom ({v['freedom']:.0f})"),
            (high_trust, f"high trust ({v['trust']:.0f})"),
            (high_research, f"strong research capacity ({v['research_capacity']:.0f})"),
        ])
        return Archetype(
            key="open_innovation",
            title="Open Innovation Society",
            description="An open, scientifically creative society where broad freedoms and generalized trust sustain a vibrant research culture and rapid technological exchange.",
            reasons=rs,
        )

    # 4. Egalitarian cooperative — low inequality, high trust, moderate productivity/stability
    if low_inequality and high_trust and v["trust"] >= MID_HIGH:
        rs = _reasons(final, [
            (low_inequality, f"low inequality ({v['inequality']:.0f})"),
            (high_trust, f"high trust ({v['trust']:.0f})"),
            (high_health, f"broad population health ({v['public_health']:.0f})"),
        ])
        return Archetype(
            key="egalitarian_cooperative",
            title="Egalitarian Cooperative Society",
            description="A comparatively equal society held together by cooperative institutions and generalized trust, with broadly shared health and educational outcomes.",
            reasons=rs,
        )

    # 5. Technocratic society — high capacity + high research/tech + moderate stability, not militarized
    if high_capacity and high_tech and high_research and not high_military:
        rs = _reasons(final, [
            (high_capacity, f"capable state ({v['state_capacity']:.0f})"),
            (high_research, f"strong research ({v['research_capacity']:.0f})"),
            (high_tech, f"advanced technology ({v['technological_progress']:.0f})"),
        ])
        return Archetype(
            key="technocratic",
            title="Technocratic Society",
            description="A capable administrative state that has invested heavily in research infrastructure and technological advancement, governed more by expertise than coercion.",
            reasons=rs,
        )

    # 6. Fragmented liberal — high freedom, low stability, low trust
    if high_freedom and v["social_stability"] <= LOW and low_trust:
        rs = _reasons(final, [
            (high_freedom, f"broad freedom ({v['freedom']:.0f})"),
            (v["social_stability"] <= LOW, f"low stability ({v['social_stability']:.0f})"),
            (low_trust, f"low trust ({v['trust']:.0f})"),
        ])
        return Archetype(
            key="fragmented_liberal",
            title="Fragmented Liberal Society",
            description="A society where personal liberties remain extensive but institutional fragmentation has eroded social cohesion and generalized trust.",
            reasons=rs,
        )

    # 7. Stable bureaucratic — high stability, high capacity, moderate freedom/trust, not industrial/military extreme
    if high_stability and high_capacity and v["freedom"] >= 42 and v["freedom"] <= 66:
        rs = _reasons(final, [
            (high_stability, f"strong stability ({v['social_stability']:.0f})"),
            (high_capacity, f"high capacity ({v['state_capacity']:.0f})"),
        ])
        return Archetype(
            key="stable_bureaucratic",
            title="Stable Bureaucratic Society",
            description="A well-administered, socially stable society whose state effectively delivers policy without relying on extreme control or coercion.",
            reasons=rs,
        )

    # 8. Stagnant traditional — low research, low tech, low creativity, low productivity
    if low_research and v["technological_progress"] <= LOW and v["creativity"] <= LOW:
        rs = _reasons(final, [
            (low_research, f"weak research ({v['research_capacity']:.0f})"),
            (v["technological_progress"] <= LOW, f"stagnant technology ({v['technological_progress']:.0f})"),
            (v["creativity"] <= LOW, f"constrained creativity ({v['creativity']:.0f})"),
        ])
        return Archetype(
            key="stagnant_traditional",
            title="Stagnant Traditional Society",
            description="A society where scientific investment and creative culture have atrophied, producing technological stagnation despite institutional continuity.",
            reasons=rs,
        )

    # 9. Productive but unequal — high productivity/wealth, high inequality
    if high_productivity and high_inequality and high_wealth:
        rs = _reasons(final, [
            (high_productivity, f"high productivity ({v['productivity']:.0f})"),
            (high_inequality, f"high inequality ({v['inequality']:.0f})"),
            (high_wealth, f"material wealth ({v['wealth']:.0f})"),
        ])
        return Archetype(
            key="productive_unequal",
            title="Productive but Unequal Society",
            description="A highly productive, materially wealthy order whose gains are concentrated, sustaining output alongside pronounced distributional tension.",
            reasons=rs,
        )

    # Fallback — Mixed / Transitional
    # Describe broad drift rather than forcing a label
    if high_health and high_productivity:
        return Archetype(
            key="mixed_prosperous",
            title="Mixed Prosperous Society",
            description="A broadly healthy and productive society that does not fit a single archetype cleanly, blending elements of openness, capability, and economic strength.",
            reasons=[f"public_health {v['public_health']:.0f}, productivity {v['productivity']:.0f}"],
        )
    if low_productivity and low_health:
        return Archetype(
            key="mixed_strained",
            title="Strained Society",
            description="A society facing concurrent strain in health and productivity, yet retaining institutional continuity across the century.",
            reasons=[f"productivity {v['productivity']:.0f}, public_health {v['public_health']:.0f}"],
        )
    return Archetype(
        key="mixed_transitional",
        title="Mixed / Transitional Society",
        description="A hybrid order whose century-long trajectory has blended competing institutional logics without settling into a single dominant pattern.",
        reasons=[f"stability {v['social_stability']:.0f}, freedom {v['freedom']:.0f}, trust {v['trust']:.0f}"],
    )
