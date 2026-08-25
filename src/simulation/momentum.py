"""
Historical momentum and contextual modifiers.

Inertia schedule is fixed per era index:
  0: 0->10   inertia 0.35
  1: 10->25  inertia 0.50
  2: 25->50  inertia 0.60
  3: 50->100 inertia 0.70

Contextual modifiers:
 - Near-cap diminishing returns (variable near 0 or 100 resists further movement in that direction)
 - Extreme inequality saturation (documented)

All functions pure and deterministic.
"""

from src.config.variables import VAR_NAMES

# Era schedule
ERA_YEARS: list[int] = [10, 15, 25, 50]  # intervals covering 0->10,10->25,25->50,50->100
ERA_START_YEARS: list[int] = [0, 10, 25, 50]
ERA_END_YEARS: list[int] = [10, 25, 50, 100]
INERTIA: list[float] = [0.35, 0.50, 0.60, 0.70]

# Raw delta scaling: maps effective_pressure (~ -1.5..+1.5) to points on 0-100 scale.
# BASE_SCALE * pressure * (years/10) then moderated by (1-inertia).
# With BASE_SCALE 7.0, max ~ 7*1.5*5*0.3 ~ 15.75 per era for longest era with high inertia.
BASE_SCALE: float = 7.0


def era_for_index(index: int) -> tuple[int, float]:
    """Return (years, inertia) for era_index 0..3."""
    if not 0 <= index < len(ERA_YEARS):
        raise IndexError(f"era_index {index} out of range 0..3")
    return ERA_YEARS[index], INERTIA[index]


def contextual_modifier(
    current_value: float,
    proposed_delta: float,
    variable: str,
) -> float:
    """
    Apply explicit contextual modifiers to proposed_delta before momentum.

    Rules:
    1) Near-cap resistance: if value near 100 and delta positive, scale down.
       Similarly near 0 and delta negative.
       Uses smooth taper: factor = 1 - ((value/100) ^2) style? Simple linear taper.

    2) Inequality special: high inequality (>75) makes further inequality increase slightly harder
       (social friction) but also makes reduction harder if state capacity low — we keep it simple:
       if inequality > 75 and delta >0: multiply 0.85 ; if inequality <25 and delta <0: multiply 0.85
       This prevents ping-pong at extremes.

    All modifiers are explicit and documented; no hidden per-variable curves.
    """
    delta = proposed_delta

    # Near-cap resistance
    if delta > 0:
        # Remaining headroom = 100 - value
        headroom = 100.0 - current_value
        # At value 90+, headroom 10 -> factor ~0.55 ; at 50 -> factor 1.0
        # Formula: factor = 0.5 + 0.5 * (headroom / 50) clamped, with smooth floor 0.30
        # Simpler: factor = 1.0 - 0.5 * ((value - 50)/50) for value>50
        if current_value > 50.0:
            # Excess above 50
            excess = (current_value - 50.0) / 50.0  # 0..1
            factor = 1.0 - excess * 0.55  # at 100 -> 0.45
            if factor < 0.30:
                factor = 0.30
            delta *= factor
    elif delta < 0:
        # Near floor
        if current_value < 50.0:
            deficit = (50.0 - current_value) / 50.0  # 0..1
            factor = 1.0 - deficit * 0.55
            if factor < 0.30:
                factor = 0.30
            delta *= factor

    # Inequality saturation
    if variable == "inequality":
        if current_value > 75.0 and delta > 0:
            delta *= 0.85
        elif current_value < 25.0 and delta < 0:
            delta *= 0.85

    return delta


def apply_momentum(
    previous: float,
    raw_delta: float,
    inertia: float,
) -> float:
    """
    Momentum: new = previous + raw_delta * (1 - inertia)
    """
    return previous + raw_delta * (1.0 - inertia)
