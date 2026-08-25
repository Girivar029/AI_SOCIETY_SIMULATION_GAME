"""
Trend detection — deterministic classification of variable trajectories.

Trend is computed from actual historical values, not pressures.
Categories are deliberately coarse to keep narrative stable.
"""

from dataclasses import dataclass
from typing import Literal

from src.config.variables import VAR_NAMES
from src.simulation.state import History, State

TrendLabel = Literal["strongly_increasing", "increasing", "stable", "decreasing", "strongly_decreasing"]

# Thresholds (points of delta) — tuned for 0-100 scale per era.
# Per-era raw changes after momentum are typically 1-8 points.
STRONG_THRESHOLD: float = 5.0
WEAK_THRESHOLD: float = 1.2
# For multi-era streaks we look at total movement over 2-3 eras


@dataclass(frozen=True)
class Trend:
    variable: str
    delta_prev: float  # current - previous
    label: TrendLabel
    previous_value: float
    current_value: float
    # Streak info across full history up to current index (inclusive)
    consecutive_direction: int  # signed count of consecutive same-sign moves ending now (+3 means 3 rising eras)
    total_delta_from_start: float  # current - Year0


def classify_delta(delta: float) -> TrendLabel:
    if delta >= STRONG_THRESHOLD:
        return "strongly_increasing"
    if delta >= WEAK_THRESHOLD:
        return "increasing"
    if delta <= -STRONG_THRESHOLD:
        return "strongly_decreasing"
    if delta <= -WEAK_THRESHOLD:
        return "decreasing"
    return "stable"


def describe_trend(label: TrendLabel, var_name: str) -> str:
    """Human phrase for trend, deterministic."""
    # Keep neutral: describe movement, not judgment
    m = {
        "strongly_increasing": "has risen sharply",
        "increasing": "has risen",
        "stable": "has remained broadly stable",
        "decreasing": "has declined",
        "strongly_decreasing": "has declined sharply",
    }
    return m[label]


def compute_trends(history: History, state_index: int) -> dict[str, Trend]:
    """
    Compute trends for the state at history.all_states[state_index] (0=Year0, 1=Year10 etc).
    For Year0, all deltas are 0/stable.
    """
    states = history.all_states
    if not (0 <= state_index < len(states)):
        raise IndexError(state_index)
    if state_index == 0:
        # Year 0: no movement
        out: dict[str, Trend] = {}
        for var in VAR_NAMES:
            cur = states[0].values[var]
            out[var] = Trend(
                variable=var,
                delta_prev=0.0,
                label="stable",
                previous_value=cur,
                current_value=cur,
                consecutive_direction=0,
                total_delta_from_start=0.0,
            )
        return out

    prev = states[state_index - 1]
    cur = states[state_index]
    start = states[0]
    out = {}
    for var in VAR_NAMES:
        delta = cur.values[var] - prev.values[var]
        label = classify_delta(delta)
        # compute consecutive direction streak ending at state_index
        streak = 0
        # Walk backwards from state_index
        for k in range(state_index, 0, -1):
            d = states[k].values[var] - states[k - 1].values[var]
            lbl = classify_delta(d)
            # Determine sign of this step (1, -1, 0)
            if lbl in ("increasing", "strongly_increasing"):
                sign = 1
            elif lbl in ("decreasing", "strongly_decreasing"):
                sign = -1
            else:
                break  # stable breaks streak
            if streak == 0:
                streak = sign
            elif streak > 0 and sign == 1:
                streak += 1
            elif streak < 0 and sign == -1:
                streak -= 1
            else:
                break
        total = cur.values[var] - start.values[var]
        out[var] = Trend(
            variable=var,
            delta_prev=delta,
            label=label,
            previous_value=prev.values[var],
            current_value=cur.values[var],
            consecutive_direction=streak,
            total_delta_from_start=total,
        )
    return out


def is_persistent_decliner(history: History, var: str, up_to_index: int, min_steps: int = 3) -> bool:
    """Check if var has declined for >=min_steps consecutive eras up to state_index."""
    states = history.all_states
    count = 0
    for k in range(up_to_index, 0, -1):
        d = states[k].values[var] - states[k - 1].values[var]
        if d <= -WEAK_THRESHOLD:
            count += 1
        else:
            break
    return count >= min_steps
