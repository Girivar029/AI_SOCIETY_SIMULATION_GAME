"""
Report engine — deterministic assembly of era and century reports from simulation History.

No random, no Pygame, no mutation of History.
"""

from dataclasses import dataclass, field
from typing import Optional

from src.config.roles import Role
from src.config.cross_domain import EDGES
from src.simulation.state import History, State
from src.narrative.trends import compute_trends, Trend, describe_trend, classify_delta
from src.narrative.templates import (
    education_narrative,
    health_narrative,
    economy_narrative,
    society_narrative,
    science_narrative,
    government_narrative,
)
from src.narrative.archetypes import classify_archetype, Archetype

# Fixed era openings (deterministic)
ERA_OPENINGS: dict[int, str] = {
    10: "A decade has passed since the new ideological order was established. Its first institutional effects are beginning to become visible.",
    25: "A quarter-century has now passed. Policies that once existed only as administrative preferences have begun to shape an entire generation.",
    50: "Half a century has passed. The original ideological choices are no longer merely policies; they have become institutional habits.",
    100: "A century has passed. The society that now exists bears the accumulated marks of decisions made generations ago.",
}

# Thresholds for key movements / causal chains
SIGNIFICANT_MOVE: float = 2.2  # per-era delta considered meaningful


@dataclass(frozen=True)
class DomainSection:
    title: str
    text: str


@dataclass(frozen=True)
class KeyMovement:
    variable: str
    delta: float
    previous: float
    current: float
    trend_label: str  # from trends
    interpretation: str  # why (pressure-based hint)


@dataclass(frozen=True)
class ConflictReport:
    variable: str
    positive_roles: list[str]  # ideology labels included in text
    negative_roles: list[str]
    positive_pressure: float
    negative_pressure: float
    net_pressure: float
    tension: float
    effective_pressure: float
    attenuation: float
    dominant_side: str  # "positive" / "negative" / "balanced"
    outcome_text: str


@dataclass(frozen=True)
class CausalChain:
    path: list[str]  # e.g., ["practical_skill","productivity","industrial_strength"]
    description: str
    supported: bool  # whether cross-domain magnitudes justify it
    details: list[str]  # per-edge delta notes


@dataclass(frozen=True)
class EraReport:
    era: int  # 10,25,50,100
    year: int
    opening: str
    # Domain sections — structured for UI inspection
    education: DomainSection
    health: DomainSection
    economy: DomainSection
    society: DomainSection
    science: DomainSection
    government: DomainSection
    # Convenience accessor for iteration in renderer
    domain_sections: list[DomainSection]
    # Conflicts & movements
    dominant_conflict: Optional[ConflictReport]
    all_conflicts: list[ConflictReport]
    key_movements: list[KeyMovement]
    causal_chains: list[CausalChain]
    trends: dict[str, Trend]
    # Persistent fault lines up to this era (for Year25+)
    persistent_conflicts: list[str]  # variable names that have recurred
    # Snapshot of ideology visibility snippet
    ideology_sentence: str
    # Raw state for reference (no mutation)
    state_values: dict[str, float]


@dataclass(frozen=True)
class FinalReport:
    # Includes all era reports plus century synthesis
    eras: list[EraReport]
    century_summary: str
    final_archetype: Archetype
    major_fault_lines: list[str]
    long_term_consequences: list[str]
    final_state: dict[str, float]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _conflict_report(c) -> ConflictReport:
    # Resolve human-readable role+ideology strings elsewhere; here store role names
    # Determine dominant side
    abs_pos = abs(c.positive_pressure)
    abs_neg = abs(c.negative_pressure)
    if abs(abs_pos - abs_neg) < 0.12:
        dominant = "balanced"
    elif abs_pos > abs_neg:
        dominant = "positive"
    else:
        dominant = "negative"
    # Outcome text: compromise vs dominance
    if c.attenuation < 0.64 and abs(c.tension) > 0.45:
        outcome = "The opposing pressures substantially cancelled each other, producing a persistent structural tension rather than a clear victory."
        if dominant != "balanced":
            outcome += " The dominant coalition retained more of its influence, but the minority view left a durable institutional residue."
    elif c.attenuation < 0.85:
        outcome = "Neither side prevailed outright; the result is a managed compromise with residual friction visible in day-to-day administration."
    else:
        outcome = "One coalition's influence was strong enough to largely set direction, though the counter-pressure remains traceable in policy debates."
    return ConflictReport(
        variable=c.variable,
        positive_roles=[r.value for r in c.positive_roles],
        negative_roles=[r.value for r in c.negative_roles],
        positive_pressure=c.positive_pressure,
        negative_pressure=c.negative_pressure,
        net_pressure=c.net_pressure,
        tension=c.tension,
        effective_pressure=c.effective_pressure,
        attenuation=c.attenuation,
        dominant_side=dominant,
        outcome_text=outcome,
    )


def _key_movement_interpretation(var: str, delta: float, state, history, state_index: int) -> str:
    # Use current era's pressures to hint at cause, if available
    st = history.all_states[state_index]
    if st.explain and var in st.explain.pressures:
        vp = st.explain.pressures[var]
        # Find strongest contributor
        if vp.contributions:
            # Sort by absolute weighted pressure descending deterministically
            contribs = sorted(vp.contributions, key=lambda c: (-abs(c.weighted_pressure), c.role.value))
            top = contribs[0]
            direction = "upward" if delta > 0 else "downward"
            return f"{var} moved {direction} under notable {direction} pressure from {top.role.value} ({top.ideology}, weighted {top.weighted_pressure:+.2f})."
        if abs(vp.cross_domain_delta) > 0.10 and abs(delta) > 1.0:
            return f"{var} shifted partly through cross-domain effects (cross contribution {vp.cross_domain_delta:+.2f})."
    # Fallback without pressure detail
    return f"{var} {'rose' if delta>0 else 'declined'} reflecting the cumulative institutional balance of the era."


def _ideology_sentence(choices: dict[Role, str]) -> str:
    # Deterministically pick 2-3 representative roles to name (those with most distinctive vectors)
    # We always include Head of State + Education Minister + Teacher for education, but generalize
    parts = []
    # Education line
    parts.append(f"education reflects a {choices[Role.teacher]}-oriented classroom under a {choices[Role.education_minister]} system")
    parts.append(f"fiscal posture is {choices[Role.tax_minister].replace('_',' ')}")
    parts.append(f"science follows a {choices[Role.science_minister].replace('_',' ')} approach")
    # Join deterministically
    return "The society " + ", ".join(parts) + "."
    

def _detect_persistent(history: History, up_to_index: int) -> list[str]:
    # Variables that have been among top 3 conflicts in at least 2 of the last 3 eras (or all if <3)
    from collections import Counter
    counter: Counter = Counter()
    start = max(1, up_to_index - 2)  # look back up to 3 eras
    for idx in range(start, up_to_index + 1):
        st = history.all_states[idx]
        if st.explain:
            tops = [c.variable for c in st.explain.top_conflicts(3)]
            for v in tops:
                counter[v] += 1
    # Persistent if count >=2
    persistent = [var for var, cnt in counter.items() if cnt >= 2]
    return sorted(persistent)


def _causal_chains(history: History, state_index: int, trends: dict[str, Trend]) -> list[CausalChain]:
    # Use EDGES to find chains where source and target both moved in expected direction
    # Only report chains where source delta and target delta are both > SIGNIFICANT_MOVE and share sign with edge coeff
    chains: list[CausalChain] = []
    if state_index == 0:
        return chains
    # We consider all edges individually as length-1 chains, plus a few known 2-step paths
    cur_state = history.all_states[state_index]
    prev_state = history.all_states[state_index - 1]
    # Single-edge chains
    for edge in EDGES:
        src = edge.source
        dst = edge.target
        src_delta = cur_state.values[src] - prev_state.values[src]
        dst_delta = cur_state.values[dst] - prev_state.values[dst]
        # Edge expects: dst moves same sign as src*coeff
        expected_sign = 1 if edge.coeff > 0 else -1
        src_sign = 1 if src_delta > SIGNIFICANT_MOVE else -1 if src_delta < -SIGNIFICANT_MOVE else 0
        dst_sign = 1 if dst_delta > SIGNIFICANT_MOVE else -1 if dst_delta < -SIGNIFICANT_MOVE else 0
        if src_sign != 0 and dst_sign != 0 and dst_sign == src_sign * expected_sign:
            # Check that cross-domain applied magnitude is non-trivial
            cross = 0.0
            if cur_state.explain:
                cross = cur_state.explain.cross_domain_applied.get(dst, 0.0)
            supported = abs(cross) > 0.08 or abs(dst_delta) > 2.5
            desc = f"{src} ({src_delta:+.1f}) → {dst} ({dst_delta:+.1f}) via {edge.note}"
            details = [f"{src} {src_delta:+.1f} → {dst} {dst_delta:+.1f} (coeff {edge.coeff:+.2f}, cross {cross:+.2f})"]
            chains.append(CausalChain(path=[src, dst], description=desc, supported=supported, details=details))
    # Add deterministic 2-step chain detections for the canonical path creativity→research→tech
    for mid in ["research_capacity", "technological_progress"]:
        # Find edges forming 2-step via this mid
        pass
    # Sort deterministically and limit to strongest 4
    chains.sort(key=lambda c: (not c.supported, c.path))
    return chains[:4]


def _build_era_report(history: History, state_index: int) -> EraReport:
    states = history.all_states
    cur = states[state_index]
    year = cur.year
    opening = ERA_OPENINGS.get(year, "")
    trends = compute_trends(history, state_index)

    # Domain sections
    # For Year0 there is no explain, but reports are only generated for 10/25/50/100; still handle.
    edu_text = education_narrative(cur, trends, cur.explain)
    health_text = health_narrative(cur, trends, cur.explain)
    econ_text = economy_narrative(cur, trends, cur.explain)
    soc_text = society_narrative(cur, trends, cur.explain)
    sci_text = science_narrative(cur, trends, cur.explain)
    gov_text = government_narrative(cur, trends, cur.explain)

    # Add ideology visibility to health/science where relevant (append short sentence)
    ideology_snippet = _ideology_sentence(cur.choices)

    # Only append to education narrative to avoid repetition everywhere; but store snippet separately
    # Conflicts
    all_conflicts: list[ConflictReport] = []
    dominant: Optional[ConflictReport] = None
    if cur.explain and cur.explain.conflicts:
        all_conflicts = [_conflict_report(c) for c in cur.explain.conflicts]
        # Dominant already sorted by tension in engine
        dominant = all_conflicts[0] if all_conflicts else None

    # Key movements: largest absolute deltas this era
    key_movements: list[KeyMovement] = []
    if state_index > 0:
        prev = states[state_index - 1]
        deltas = []
        for var in cur.values:
            d = cur.values[var] - prev.values[var]
            deltas.append((var, d))
        # Sort by abs(delta) descending, then var name for ties
        deltas.sort(key=lambda x: (-abs(x[1]), x[0]))
        # Keep only significant moves
        for var, d in deltas:
            if abs(d) >= 1.8 and len(key_movements) < 4:
                tr = trends[var]
                interp = _key_movement_interpretation(var, d, cur, history, state_index)
                km = KeyMovement(variable=var, delta=d, previous=prev.values[var], current=cur.values[var], trend_label=tr.label, interpretation=interp)
                key_movements.append(km)

    causal_chains = _causal_chains(history, state_index, trends)
    persistent = _detect_persistent(history, state_index)

    domain_sections = [
        DomainSection("EDUCATION", edu_text),
        DomainSection("HEALTH", health_text),
        DomainSection("ECONOMY", econ_text),
        DomainSection("SOCIETY", soc_text),
        DomainSection("SCIENCE & TECHNOLOGY", sci_text),
        DomainSection("GOVERNMENT & SECURITY", gov_text),
    ]

    return EraReport(
        era=year,
        year=year,
        opening=opening,
        education=domain_sections[0],
        health=domain_sections[1],
        economy=domain_sections[2],
        society=domain_sections[3],
        science=domain_sections[4],
        government=domain_sections[5],
        domain_sections=domain_sections,
        dominant_conflict=dominant,
        all_conflicts=all_conflicts,
        key_movements=key_movements,
        causal_chains=causal_chains,
        trends=trends,
        persistent_conflicts=persistent,
        ideology_sentence=ideology_snippet,
        state_values=dict(cur.values),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_era_report(history: History, year: int) -> EraReport:
    """Generate report for a specific year (10,25,50,100)."""
    idx = {s.year: i for i, s in enumerate(history.all_states)}[year]
    return _build_era_report(history, idx)


def generate_history_reports(history: History) -> list[EraReport]:
    """Generate reports for all eras 10,25,50,100 (excludes Year 0)."""
    out: list[EraReport] = []
    for st in history.steps:
        idx = history.all_states.index(st)
        out.append(_build_era_report(history, idx))
    return out


def generate_final_report(history: History) -> FinalReport:
    eras = generate_history_reports(history)
    final_state = history.state_at(100)
    archetype = classify_archetype(final_state)

    # Fault lines: persistent conflicts at Year 100
    fault_lines = eras[-1].persistent_conflicts if eras else []

    # Long-term consequences: combine trends that have persisted and archetype reasons
    consequences: list[str] = []
    trends100 = eras[-1].trends if eras else {}
    for var, tr in trends100.items():
        if abs(tr.consecutive_direction) >= 3 and abs(tr.total_delta_from_start) >= 8.0:
            direction = "risen" if tr.consecutive_direction > 0 else "declined"
            consequences.append(f"{var} has {direction} for three consecutive eras (total {tr.total_delta_from_start:+.1f} since Year 0).")
    if not consequences:
        # Fallback: top 2 total movers
        sorted_totals = sorted(trends100.items(), key=lambda kv: -abs(kv[1].total_delta_from_start))
        for var, tr in sorted_totals[:2]:
            consequences.append(f"{var} stands at {tr.current_value:.0f} after a century-long shift of {tr.total_delta_from_start:+.1f}.")

    # Century summary (2-3 paragraphs synthesis)
    v = final_state.values
    summary = (
        f"By the close of the century the society bears the imprint of its founding doctrines. "
        f"{archetype.title} — {archetype.description} "
        f"Productivity {v['productivity']:.0f}, inequality {v['inequality']:.0f}, "
        f"stability {v['social_stability']:.0f}, freedom {v['freedom']:.0f} and trust {v['trust']:.0f} "
        f"chart the trade-offs that accumulated era by era."
    )
    return FinalReport(
        eras=eras,
        century_summary=summary,
        final_archetype=archetype,
        major_fault_lines=fault_lines,
        long_term_consequences=consequences,
        final_state=dict(final_state.values),
    )
