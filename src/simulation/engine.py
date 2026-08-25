"""
Deterministic simulation engine.

Public API:
    state = create_initial_state(choices)
    result = simulate(initial_state, choices)
    next_state = step(current_state, choices, era_index)

No random, no I/O, no Pygame, no filesystem.
"""

from src.config.variables import VAR_NAMES
from src.config.cross_domain import EDGES
from src.simulation.state import State, History, create_initial_state, clamp, EraExplainability, VariablePressure
from src.simulation.conflicts import aggregate_pressures, extract_conflicts
from src.simulation.momentum import era_for_index, contextual_modifier, apply_momentum, BASE_SCALE, ERA_YEARS

__all__ = ["create_initial_state", "step", "simulate", "ERA_YEARS"]


def step(
    current: State,
    choices: dict,
    era_index: int,
) -> State:
    """
    Advance one era deterministically.
    era_index 0..3 corresponds to intervals 10,15,25,50 years.
    Choices are re-validated but expected unchanged across history (Year-0 config).
    """
    years, inertia = era_for_index(era_index)
    time_scale = years / 10.0

    # 1) Aggregate pressures + conflict resolution (pure function of choices)
    pressures: dict[str, VariablePressure] = aggregate_pressures(choices)
    conflicts = extract_conflicts(pressures)

    # 2) Compute raw deltas per variable (before cross-domain, before contextual)
    #    raw_delta = effective_pressure * BASE_SCALE * time_scale
    raw_deltas: dict[str, float] = {}
    for var in VAR_NAMES:
        vp = pressures[var]
        raw = vp.effective_pressure * BASE_SCALE * time_scale
        # Store for explainability
        vp.raw_delta = raw
        raw_deltas[var] = raw

    # 3) Cross-domain propagation — one pass, deterministic edge order (list order)
    #    cross contribution added to raw_deltas
    cross_applied: dict[str, float] = {var: 0.0 for var in VAR_NAMES}
    # Use copy so edges read pre-cross values? We read from raw_deltas pre-cross for source,
    # so edge order does not compound within pass (second-order remains second-order).
    pre_cross = dict(raw_deltas)
    for edge in EDGES:
        src_delta = pre_cross[edge.source]
        # Cross effect magnitude proportional to source raw delta
        contribution = src_delta * edge.coeff
        # Diminishing near caps is handled in contextual modifier, but cross also tapers
        # if target near opposite extreme? Keep simple: no extra taper here (contextual covers it)
        raw_deltas[edge.target] += contribution
        cross_applied[edge.target] += contribution
        # Record per-variable cross for explainability
        pressures[edge.target].cross_domain_delta += contribution

    # 4) Contextual modifier + momentum + clamp per variable
    new_values: dict[str, float] = {}
    ordered_choices = {r: choices[r] for r in sorted(choices, key=lambda x: x.value)}
    for var in VAR_NAMES:
        prev = current.values[var]
        raw = raw_deltas[var]
        # Contextual: variable-specific diminishing returns
        adjusted = contextual_modifier(prev, raw, var)
        # Momentum
        new_val = apply_momentum(prev, adjusted, inertia)
        new_val = clamp(new_val)
        new_values[var] = new_val
        # For explainability, store final adjusted raw before momentum? We keep raw_delta + cross.

    # 5) Build explainability
    explain = EraExplainability(
        era_index=era_index,
        years=years,
        inertia=inertia,
        pressures=pressures,
        conflicts=conflicts,
        cross_domain_applied=cross_applied,
    )

    # 6) Build next state
    end_year = current.year + years
    next_state = State(
        year=end_year,
        values=new_values,
        choices=ordered_choices,
        explain=explain,
    )
    next_state.validate()
    return next_state


def simulate(
    initial_state: State,
    choices: dict,
) -> History:
    """
    Run full 0->10->25->50->100 simulation.
    initial_state must be Year 0. Choices must contain all 10 roles.
    Returns History with 5 snapshots (Year 0 + 4 steps).
    """
    # Validate choices completeness
    from src.config.roles import ROLES

    for r in ROLES:
        if r not in choices:
            raise ValueError(f"Missing choice for role {r}")
    # Also validate ideologies are valid
    from src.config.ideologies import IDEOLOGIES

    for r, ideology in choices.items():
        if ideology not in IDEOLOGIES[r]:
            raise ValueError(f"Invalid ideology '{ideology}' for role {r}")

    assert initial_state.year == 0, f"initial_state must be Year 0, got {initial_state.year}"
    initial_state.validate()

    # Deterministic ordered choices copy
    ordered_choices = {r: choices[r] for r in sorted(choices, key=lambda x: x.value)}

    current = initial_state
    # Ensure initial choices match passed choices (if caller used create_initial_state they do)
    # We override state's choices to ordered_choices to keep history consistent
    # But keep initial as-is for Year 0 snapshot (re-create to ensure sorted)
    initial = State(year=0, values=dict(initial_state.values), choices=ordered_choices, explain=None)

    steps: list[State] = []
    current = initial
    for era_index in range(len(ERA_YEARS)):
        nxt = step(current, ordered_choices, era_index)
        steps.append(nxt)
        current = nxt

    return History(initial=initial, steps=steps)
