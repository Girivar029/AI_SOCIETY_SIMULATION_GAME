"""
Pressure aggregation, conflict detection and resolution.

Deterministic: iterates roles and variables in sorted order, no random, no set iteration.
"""

from src.config.roles import ROLES, Role
from src.config.variables import VAR_NAMES
from src.config.ideologies import VECTORS
from src.config.influence import INFLUENCE, GLOBAL_WEIGHT
from src.simulation.state import VariablePressure, Contribution, ConflictInfo

# Epsilon below which pressure is considered noise, not conflict
CONFLICT_EPSILON: float = 0.05

# Tension normalization divisor — keeps tension in interpretable [0, ~1.5] range
# Max possible positive + negative approx ~2.0 each side, net small -> tension up to ~4.
# We don't normalize aggressively; raw tension is fine, but we clamp effective attenuation.


def aggregate_pressures(
    choices: dict[Role, str],
) -> dict[str, VariablePressure]:
    """
    For each variable, aggregate weighted pressures from all roles.
    Returns dict var -> VariablePressure with contributions, sums, net, tension, conflict flag.
    """
    result: dict[str, VariablePressure] = {}

    for var in VAR_NAMES:  # deterministic order
        vp = VariablePressure(variable=var)
        pos = 0.0
        neg = 0.0
        pos_roles: list[Role] = []
        neg_roles: list[Role] = []

        # Deterministic role iteration
        for role in ROLES:
            ideology = choices[role]
            vector = VECTORS[role][ideology]
            raw_pressure = vector.get(var, 0.0)
            if raw_pressure == 0.0:
                continue
            influence = INFLUENCE[role][var]
            gw = GLOBAL_WEIGHT[role]
            weighted = raw_pressure * influence * gw

            contrib = Contribution(
                role=role,
                ideology=ideology,
                vector_pressure=raw_pressure,
                influence=influence,
                global_weight=gw,
                weighted_pressure=weighted,
            )
            vp.contributions.append(contrib)

            if weighted > 0:
                pos += weighted
                pos_roles.append(role)
            elif weighted < 0:
                neg += weighted  # stays negative
                neg_roles.append(role)

        vp.positive_sum = pos
        vp.negative_sum = neg
        vp.net = pos + neg

        # Tension: amount of cancelled-out opposing pressure
        # tension = |pos| + |neg| - |net|
        # If only one side, tension = 0
        raw_tension = abs(pos) + abs(neg) - abs(vp.net)
        # Clamp small floating noise
        if raw_tension < 1e-12:
            raw_tension = 0.0
        vp.tension = raw_tension

        # Conflict if both sides exceed epsilon
        vp.is_conflict = (pos > CONFLICT_EPSILON) and (neg < -CONFLICT_EPSILON)

        # Resolution: attenuate net when tension is high, but preserve dominant side partly
        vp.attenuation, vp.effective_pressure = _resolve(
            net=vp.net,
            pos=pos,
            neg=neg,
            tension=raw_tension,
            is_conflict=vp.is_conflict,
        )

        result[var] = vp

    return result


def _resolve(
    net: float,
    pos: float,
    neg: float,
    tension: float,
    is_conflict: bool,
) -> tuple[float, float]:
    """
    Conflict resolution: weighted compromise with attenuation.

    - No conflict: effective = net
    - Conflict: effective = net * attenuation
      attenuation in [0.40, 1.0] depending on tension magnitude and dominance ratio.

    If one side overwhelmingly dominates (dominance_ratio > 1.8), attenuation is relaxed
    (compromise retains more of dominant side).
    """
    if not is_conflict or tension == 0.0:
        return 1.0, net

    # Base attenuation: stronger tension -> lower attenuation (more suppression)
    # tension 0 -> 1.0, tension 1.0 -> ~0.60, tension 2.0 -> ~0.45
    # Formula: atten = 1 / (1 + tension * 0.65)
    atten = 1.0 / (1.0 + tension * 0.65)

    # Dominance check
    abs_pos = abs(pos)
    abs_neg = abs(neg)
    # Determine dominant side magnitude and minority side magnitude
    dominant = max(abs_pos, abs_neg)
    minority = min(abs_pos, abs_neg)
    if minority > 1e-12:
        ratio = dominant / minority
        if ratio > 1.8:
            # Relax attenuation: weighted blend toward 1.0
            # e.g., ratio 2 -> attenuation moves 30% toward 1.0; ratio 5 -> 60% toward 1.0
            dominance_boost = min(0.60, (ratio - 1.8) * 0.18)
            atten = atten + (1.0 - atten) * dominance_boost
    else:
        # Should not happen in conflict case, but guard
        pass

    # Clamp attenuation to sensible bounds
    if atten < 0.40:
        atten = 0.40
    if atten > 1.0:
        atten = 1.0

    effective = net * atten
    return atten, effective


def extract_conflicts(
    pressures: dict[str, VariablePressure],
) -> list[ConflictInfo]:
    """Build ConflictInfo list from pressures where is_conflict True."""
    conflicts: list[ConflictInfo] = []
    for var in VAR_NAMES:
        vp = pressures[var]
        if not vp.is_conflict:
            continue
        pos_roles: list[Role] = []
        neg_roles: list[Role] = []
        for c in vp.contributions:
            if c.weighted_pressure > 0:
                pos_roles.append(c.role)
            elif c.weighted_pressure < 0:
                neg_roles.append(c.role)
        # Deterministic sort
        pos_roles = sorted(pos_roles, key=lambda r: r.value)
        neg_roles = sorted(neg_roles, key=lambda r: r.value)
        ci = ConflictInfo(
            variable=var,
            positive_roles=pos_roles,
            negative_roles=neg_roles,
            positive_pressure=vp.positive_sum,
            negative_pressure=vp.negative_sum,
            net_pressure=vp.net,
            tension=vp.tension,
            effective_pressure=vp.effective_pressure,
            attenuation=vp.attenuation,
        )
        conflicts.append(ci)
    # Sort by tension descending, then variable name for stability
    conflicts.sort(key=lambda c: (-c.tension, c.variable))
    return conflicts
