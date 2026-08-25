"""
Domain narrative templates — deterministic, threshold-based, causal where traceable.

Each function is pure: (state, previous_state, trends, pressures, history) -> string.
No random, no I/O, no mutation.
"""

from src.simulation.state import State
from src.narrative.trends import Trend

# Threshold helpers
HIGH = 68.0
LOW = 38.0
MID_HIGH = 60.0
MID_LOW = 42.0


def _level(v: float) -> str:
    if v >= HIGH:
        return "high"
    if v <= LOW:
        return "low"
    if v >= MID_HIGH:
        return "mid_high"
    if v <= MID_LOW:
        return "mid_low"
    return "mid"


def _trend_phrase(trend: Trend) -> str:
    if trend.label == "strongly_increasing":
        return "a sharp rise"
    if trend.label == "increasing":
        return "a steady rise"
    if trend.label == "strongly_decreasing":
        return "a sharp decline"
    if trend.label == "decreasing":
        return "a gradual decline"
    return "broad stability"


def _streak_phrase(trend: Trend) -> str:
    if abs(trend.consecutive_direction) >= 3:
        if trend.consecutive_direction > 0:
            return " for three consecutive eras"
        return " for three consecutive eras"
    if abs(trend.consecutive_direction) == 2:
        if trend.consecutive_direction > 0:
            return " for two consecutive eras"
        return " for two consecutive eras"
    return ""


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------
def education_narrative(state: State, trends: dict[str, Trend], state_explain=None) -> str:
    acad = state.values["academic_performance"]
    skill = state.values["practical_skill"]
    creat = state.values["creativity"]
    ta = trends["academic_performance"]
    ts = trends["practical_skill"]
    tc = trends["creativity"]

    # Conflict hint: if creativity or academic appears in top conflicts, tag it
    conflict_hint = ""
    if state_explain and state_explain.conflicts:
        top_vars = [c.variable for c in state_explain.top_conflicts(3)]
        if "creativity" in top_vars or "academic_performance" in top_vars:
            conflict_hint = " This tension reflects an active institutional disagreement between classroom practice and system-level curriculum."

    # High academic + low creativity
    if acad >= HIGH and creat <= LOW:
        base = (
            f"Formal academic performance has become a defining strength (academic {acad:.0f}), "
            f"with examination results and standardized attainment among the highest in the century. "
            f"Yet the same system increasingly rewards predictable answers over divergent thinking "
            f"(creativity {creat:.0f}).{conflict_hint}"
        )
        if tc.label in ("decreasing", "strongly_decreasing"):
            base += f" Creativity {_trend_phrase(tc)}{_streak_phrase(tc)}, reinforcing the pattern."
        return base

    if skill >= HIGH and acad <= MID_LOW:
        return (
            f"Workshops, apprenticeships and practical instruction have thrived (practical skill {skill:.0f}), "
            f"producing a generation confident with tools and applied problems. "
            f"Formal academic attainment is more modest (academic {acad:.0f}), reflecting a curriculum that "
            f"privileges hands-on competence over standardized testing.{conflict_hint}"
        )

    if creat >= HIGH and acad >= MID_HIGH:
        return (
            f"Education balances strong academic foundations (academic {acad:.0f}) with a vibrant creative "
            f"culture (creativity {creat:.0f}). Students display both test proficiency and willingness to "
            f"pursue unconventional approaches, a combination sustained across recent eras.{conflict_hint}"
        )

    if creat >= HIGH and acad <= MID_LOW:
        return (
            f"Creative and practical capacities have flourished (creativity {creat:.0f}, practical {skill:.0f}), "
            f"fostering inventive classrooms. Standardized academic scores remain moderate (academic {acad:.0f}), "
            f"as the system values exploration over uniform outcomes.{conflict_hint}"
        )

    if acad >= MID_HIGH and skill >= MID_HIGH and creat >= MID_LOW:
        return (
            f"The education system is broadly balanced — competent in examinations (academic {acad:.0f}), "
            f"capable in applied work (practical {skill:.0f}) and reasonably open to original thought "
            f"(creativity {creat:.0f}). No single doctrine dominates the classroom.{conflict_hint}"
        )

    if acad <= LOW and creat <= LOW and skill <= MID_LOW:
        return (
            f"Educational outcomes are weak across the board (academic {acad:.0f}, practical {skill:.0f}, "
            f"creativity {creat:.0f}). {ta.label.replace('_',' ')} academic performance and "
            f"{tc.label.replace('_',' ')} creative capacity suggest a system caught between competing prescriptions.{conflict_hint}"
        )

    # Improving / declining wrappers
    if ta.label in ("strongly_increasing", "increasing") and tc.label == "stable":
        return (
            f"Academic performance { _trend_phrase(ta)}{_streak_phrase(ta)} to {acad:.0f}, while creative life "
            f"has held steady around {creat:.0f}. Practical competence sits at {skill:.0f}.{conflict_hint}"
        )
    if tc.label in ("decreasing", "strongly_decreasing"):
        return (
            f"Creative capacity { _trend_phrase(tc)}{_streak_phrase(tc)} to {creat:.0f}, even as academic results "
            f"stand at {acad:.0f}. Practical skill measures {skill:.0f}.{conflict_hint}"
        )

    # Default balanced description
    return (
        f"Education stands at academic {acad:.0f}, practical skill {skill:.0f} and creativity {creat:.0f}. "
        f"Academic trends show { _trend_phrase(ta)}, creativity { _trend_phrase(tc)}.{conflict_hint}"
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
def health_narrative(state: State, trends: dict[str, Trend], state_explain=None) -> str:
    life = state.values["life_expectancy"]
    pub = state.values["public_health"]
    access = state.values["healthcare_access"]
    tp = trends["public_health"]
    tl = trends["life_expectancy"]
    ta = trends["healthcare_access"]
    # Cross hint: if productivity trend aligns with health improvement, allow causal hint only if supported
    prod_phrase = ""
    if state.values["productivity"] >= MID_HIGH and pub >= HIGH and tp.label in ("increasing", "strongly_increasing"):
        prod_phrase = " The resulting improvement in population health is beginning to strengthen the productive workforce."
    # Preventive vs treatment distinction based on levels
    if pub >= HIGH and access >= MID_HIGH:
        return (
            f"Preventive medicine has become deeply embedded in public life (public health {pub:.0f}), with care "
            f"widely reachable (access {access:.0f}) and lifespans extending to {life:.0f}.{prod_phrase}"
        )
    if pub >= HIGH and access <= MID_LOW:
        return (
            f"Population-level prevention is strong (public health {pub:.0f}) and lifespans have risen to {life:.0f}, "
            f"yet clinical access remains uneven (access {access:.0f}). Community health outpaces individual care delivery."
            + prod_phrase
        )
    if pub <= LOW and access >= HIGH:
        return (
            f"Clinical capacity is extensive (access {access:.0f}) and patients receive timely treatment, but preventive "
            f"health remains fragile (public health {pub:.0f}). Life expectancy {life:.0f} reflects a treatment-heavy system."
            + prod_phrase
        )
    if pub <= LOW and access <= LOW:
        return (
            f"Public health remains fragile (public health {pub:.0f}, access {access:.0f}) and life expectancy {life:.0f} "
            f"has { _trend_phrase(tl)}{_streak_phrase(tl)}. Both prevention and care delivery show strain."
        )
    if pub >= MID_HIGH and access <= LOW:
        return (
            f"Preventive efforts have lifted population health to {pub:.0f}, but access bottlenecks (access {access:.0f}) "
            f"mean that when illness strikes, care is not always at hand. Life expectancy {life:.0f} reflects that mix."
            + prod_phrase
        )
    # General
    return (
        f"Health stands at public health {pub:.0f}, access {access:.0f} and life expectancy {life:.0f}. "
        f"Public health has shown { _trend_phrase(tp)}{_streak_phrase(tp)}, access { _trend_phrase(ta)}."
        + prod_phrase
    )


# ---------------------------------------------------------------------------
# Economy
# ---------------------------------------------------------------------------
def economy_narrative(state: State, trends: dict[str, Trend], state_explain=None) -> str:
    prod = state.values["productivity"]
    wealth = state.values["wealth"]
    ineq = state.values["inequality"]
    ind = state.values["industrial_strength"]
    tax = state.values["tax_revenue"]
    tp = trends["productivity"]
    ti = trends["inequality"]

    # Build wealth/inequality combo
    ineq_desc = "concentrated" if ineq >= HIGH else "moderate" if ineq >= MID_LOW else "broadly shared"
    tax_desc = f"fiscal intake {tax:.0f} ({'strong' if tax >= HIGH else 'moderate' if tax >= MID_LOW else 'strained'})"
    if prod >= HIGH and wealth >= MID_HIGH and ineq >= HIGH:
        return (
            f"Output is high (productivity {prod:.0f}) and aggregate wealth is substantial ({wealth:.0f}), "
            f"yet distribution is {ineq_desc} (inequality {ineq:.0f}). Industrial strength {ind:.0f} supports that output, "
            f"while {tax_desc} funds the state. Inequality {_trend_phrase(ti)}{_streak_phrase(ti)}."
        )
    if prod >= HIGH and wealth <= MID_LOW:
        return (
            f"The economy produces efficiently (productivity {prod:.0f}, industry {ind:.0f}) but aggregate wealth remains "
            f"modest ({wealth:.0f}), suggesting output is not translating into widespread accumulation. {tax_desc}."
        )
    if wealth >= HIGH and ineq <= LOW:
        return (
            f"Material wealth is abundant ({wealth:.0f}) and unusually evenly spread (inequality {ineq:.0f}). "
            f"Productivity {prod:.0f} and industry {ind:.0f} support that distribution, with {tax_desc}."
        )
    if tax >= HIGH and wealth <= MID_LOW:
        return (
            f"Fiscal capacity is strong ({tax_desc}) but private accumulation is restrained (wealth {wealth:.0f}). "
            f"Productivity {prod:.0f} and industry {ind:.0f} reflect an economy where the state captures a larger share."
        )
    if ind >= HIGH and tax <= LOW:
        return (
            f"Industrial capacity is formidable ({ind:.0f}) and productivity {prod:.0f} remains high, yet {tax_desc} — "
            f"a low-revenue state presiding over a strong industrial base. Inequality {ineq:.0f} { _trend_phrase(ti)}."
        )
    if prod <= LOW and wealth <= LOW:
        return (
            f"The economy is strained: productivity {prod:.0f} and wealth {wealth:.0f} remain low, with industry {ind:.0f}. "
            f"{tax_desc.capitalize()}. Productivity has shown { _trend_phrase(tp)}."
        )
    # Divergence
    return (
        f"Economy: productivity {prod:.0f} ({ _trend_phrase(tp)}{_streak_phrase(tp)}), wealth {wealth:.0f}, "
        f"inequality {ineq_desc} ({ineq:.0f}, { _trend_phrase(ti)}{_streak_phrase(ti)}), "
        f"industry {ind:.0f}, {tax_desc}."
    )


# ---------------------------------------------------------------------------
# Society
# ---------------------------------------------------------------------------
def society_narrative(state: State, trends: dict[str, Trend], state_explain=None) -> str:
    stab = state.values["social_stability"]
    free = state.values["freedom"]
    trust = state.values["trust"]
    ineq = state.values["inequality"]
    ts = trends["social_stability"]
    tf = trends["freedom"]
    tt = trends["trust"]

    if stab >= HIGH and free <= LOW:
        return (
            f"Public order remains unusually strong (stability {stab:.0f}), but political and personal freedoms have "
            f"narrowed considerably (freedom {free:.0f}). Trust {trust:.0f} reflects life under tight institutional control. "
            f"Freedom has shown { _trend_phrase(tf)}{_streak_phrase(tf)}."
        )
    if free >= HIGH and trust >= HIGH:
        return (
            f"Institutions retain broad legitimacy, and citizens appear increasingly willing to rely on voluntary cooperation "
            f"(freedom {free:.0f}, trust {trust:.0f}, stability {stab:.0f}). Freedom { _trend_phrase(tf)}, "
            f"trust { _trend_phrase(tt)}."
        )
    if free >= HIGH and stab <= LOW:
        return (
            f"Personal freedoms remain extensive (freedom {free:.0f}), but institutional disagreements have begun to "
            f"weaken social cohesion (stability {stab:.0f}, trust {trust:.0f})."
        )
    if stab <= LOW and trust <= LOW:
        return (
            f"Social cohesion is fragile (stability {stab:.0f}, trust {trust:.0f}). Freedom {free:.0f} sits alongside "
            f"pervasive uncertainty. Trust { _trend_phrase(tt)}{_streak_phrase(tt)}."
        )
    if ineq >= HIGH and stab <= MID_LOW:
        return (
            f"High inequality (inequality {ineq:.0f}) weighs on cohesion. Stability {stab:.0f} { _trend_phrase(ts)}, "
            f"while freedom {free:.0f} and trust {trust:.0f} mirror that distributional strain."
        )
    # General
    return (
        f"Society: stability {stab:.0f} ({ _trend_phrase(ts)}{_streak_phrase(ts)}), "
        f"freedom {free:.0f} ({ _trend_phrase(tf)}), trust {trust:.0f} ({ _trend_phrase(tt)})."
    )


# ---------------------------------------------------------------------------
# Science & Tech
# ---------------------------------------------------------------------------
def science_narrative(state: State, trends: dict[str, Trend], state_explain=None) -> str:
    rc = state.values["research_capacity"]
    tp = state.values["technological_progress"]
    creat = state.values["creativity"]
    ind = state.values["industrial_strength"]
    tr = trends["research_capacity"]
    tt = trends["technological_progress"]

    if rc >= HIGH and tp >= HIGH:
        return (
            f"Research infrastructure is world-leading (research {rc:.0f}) and technological advancement is rapid "
            f"(technology {tp:.0f}). Industrial capacity {ind:.0f} and creative culture {creat:.0f} underpin that momentum."
        )
    if rc >= HIGH and tp <= MID_LOW:
        return (
            f"Research capacity is strong ({rc:.0f}) but technological translation remains sluggish (technology {tp:.0f}). "
            f"Knowledge accumulates faster than it is applied. Creativity {creat:.0f}, industry {ind:.0f}."
        )
    if rc <= LOW and tp <= LOW:
        return (
            f"Scientific investment and creative culture have both atrophied (research {rc:.0f}, creativity {creat:.0f}), "
            f"producing technological stagnation (technology {tp:.0f}). Research { _trend_phrase(tr)}{_streak_phrase(tr)}."
        )
    if creat <= LOW and rc <= MID_LOW:
        return (
            f"Constrained creative life (creativity {creat:.0f}) has begun to erode research capacity ({rc:.0f}), "
            f"with consequences for technology ({tp:.0f}). Cross-domain trace: creativity → research_capacity → technological_progress."
        )
    if tp >= HIGH and rc <= MID_LOW:
        return (
            f"Technological progress is impressive ({tp:.0f}), outpacing the formal research base ({rc:.0f}). "
            f"Applied and industrial adoption (industry {ind:.0f}) drives advance more than basic science."
        )
    return (
        f"Science: research {rc:.0f} ({ _trend_phrase(tr)}{_streak_phrase(tr)}), technology {tp:.0f} "
        f"({ _trend_phrase(tt)}{_streak_phrase(tt)}), creativity {creat:.0f}, industry {ind:.0f}."
    )


# ---------------------------------------------------------------------------
# Government
# ---------------------------------------------------------------------------
def government_narrative(state: State, trends: dict[str, Trend], state_explain=None) -> str:
    cap = state.values["state_capacity"]
    mil = state.values["military_strength"]
    free = state.values["freedom"]
    trust = state.values["trust"]
    stab = state.values["social_stability"]
    tc = trends["state_capacity"]
    tm = trends["military_strength"]

    if cap >= HIGH and free <= LOW:
        return (
            f"The state is highly capable of execution and delivery (capacity {cap:.0f}) yet governs with "
            f"tight constraints on personal liberty (freedom {free:.0f}). Trust {trust:.0f}, military {mil:.0f}, "
            f"stability {stab:.0f}. State capacity { _trend_phrase(tc)}{_streak_phrase(tc)}."
        )
    if cap <= LOW:
        return (
            f"State capacity remains weak ({cap:.0f}). Policies are announced more often than they are implemented. "
            f"Freedom {free:.0f}, trust {trust:.0f}, military {mil:.0f}. Stability {stab:.0f} reflects that gap."
        )
    if mil >= HIGH and cap <= MID_HIGH:
        return (
            f"Military power is pronounced ({mil:.0f}) relative to civilian state capacity ({cap:.0f}). "
            f"Security institutions outpace the broader administrative state. Freedom {free:.0f}, trust {trust:.0f}."
        )
    if cap >= HIGH and mil >= HIGH and stab >= HIGH:
        return (
            f"A capable state ({cap:.0f}) fields a formidable military ({mil:.0f}) while maintaining social stability "
            f"({stab:.0f}). Freedom {free:.0f}, trust {trust:.0f}. Military { _trend_phrase(tm)}."
        )
    if cap >= HIGH and free >= MID_HIGH:
        return (
            f"A capable yet comparatively open state: capacity {cap:.0f}, freedom {free:.0f}, trust {trust:.0f}, "
            f"military {mil:.0f}. Capacity { _trend_phrase(tc)}, trust reflects voluntary cooperation."
        )
    return (
        f"Government: capacity {cap:.0f} ({ _trend_phrase(tc)}{_streak_phrase(tc)}), "
        f"military {mil:.0f} ({ _trend_phrase(tm)}), freedom {free:.0f}, trust {trust:.0f}, stability {stab:.0f}."
    )
