"""
State representation — headless, no Pygame/Matplotlib/portrait data.

State holds the 18 variables at a given year plus explainability logs.
History holds the full 0→10→25→50→100 sequence.
"""

from dataclasses import dataclass, field
from typing import Optional

from src.config.roles import Role
from src.config.variables import VAR_NAMES, START_VALUES


# ---------------------------------------------------------------------------
# Explainability structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Contribution:
    role: Role
    ideology: str
    vector_pressure: float  # raw vector value [-1,1]
    influence: float
    global_weight: float
    weighted_pressure: float  # vector * influence * global


@dataclass
class VariablePressure:
    """Aggregated pressures for a single variable in one era."""
    variable: str
    contributions: list[Contribution] = field(default_factory=list)
    positive_sum: float = 0.0
    negative_sum: float = 0.0  # negative value (sum of negative weighted)
    net: float = 0.0
    tension: float = 0.0
    is_conflict: bool = False
    # After resolution:
    attenuation: float = 1.0
    effective_pressure: float = 0.0
    # After cross-domain & momentum:
    cross_domain_delta: float = 0.0
    raw_delta: float = 0.0  # effective_pressure scaled to delta units


@dataclass
class ConflictInfo:
    variable: str
    positive_roles: list[Role]
    negative_roles: list[Role]
    positive_pressure: float
    negative_pressure: float
    net_pressure: float
    tension: float
    effective_pressure: float
    attenuation: float


@dataclass
class EraExplainability:
    era_index: int  # 0..3 for the 4 transitions
    years: int  # interval length (10,15,25,50)
    inertia: float
    pressures: dict[str, VariablePressure] = field(default_factory=dict)
    conflicts: list[ConflictInfo] = field(default_factory=list)
    cross_domain_applied: dict[str, float] = field(default_factory=dict)  # var -> cross delta added

    def top_conflicts(self, n: int = 3) -> list[ConflictInfo]:
        return sorted(self.conflicts, key=lambda c: c.tension, reverse=True)[:n]


# ---------------------------------------------------------------------------
# State Snapshot
# ---------------------------------------------------------------------------

@dataclass
class State:
    year: int
    values: dict[str, float]  # var -> 0..100
    choices: dict[Role, str]  # role -> ideology (frozen across history but stored per snapshot)
    explain: Optional[EraExplainability] = None  # None for Year 0, populated for Year 10+

    def get(self, var: str) -> float:
        return self.values[var]

    def copy_values(self) -> dict[str, float]:
        return dict(self.values)

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "values": dict(self.values),
            "choices": {r.value: v for r, v in self.choices.items()},
        }

    def validate(self) -> None:
        for var in VAR_NAMES:
            assert var in self.values, f"Missing variable {var}"
            v = self.values[var]
            assert isinstance(v, float), f"Variable {var} not float: {type(v)}"
            assert 0.0 <= v <= 100.0, f"Variable {var} out of bounds {v}"
            assert v == v, f"Variable {var} is NaN"  # NaN != NaN
            assert v != float("inf") and v != float("-inf"), f"Variable {var} is infinite"


@dataclass
class History:
    initial: State  # Year 0
    steps: list[State]  # Year 10,25,50,100 in order

    @property
    def all_states(self) -> list[State]:
        return [self.initial] + self.steps

    @property
    def years(self) -> list[int]:
        return [s.year for s in self.all_states]

    def state_at(self, year: int) -> State:
        for s in self.all_states:
            if s.year == year:
                return s
        raise KeyError(f"No state at year {year}")


# ---------------------------------------------------------------------------
# Constructors
# ---------------------------------------------------------------------------

def create_initial_state(
    choices: dict[Role, str],
    overrides: Optional[dict[str, float]] = None,
) -> State:
    """
    Create Year 0 state. Choices are stored but no explainability yet.
    Optionally override starting values (for testing).
    """
    values: dict[str, float] = dict(START_VALUES)
    if overrides:
        for k, v in overrides.items():
            assert k in VAR_NAMES, f"Unknown variable {k}"
            assert 0.0 <= v <= 100.0, f"Override out of bounds {k}={v}"
            values[k] = float(v)
    # Ensure floats
    values = {k: float(v) for k, v in values.items()}
    # Deterministic ordering of choices (sort by role value string)
    ordered_choices = {r: choices[r] for r in sorted(choices, key=lambda x: x.value)}
    s = State(year=0, values=values, choices=ordered_choices, explain=None)
    s.validate()
    return s


def clamp(value: float) -> float:
    if value != value:  # NaN
        raise ValueError("NaN encountered in clamp")
    if value < 0.0:
        return 0.0
    if value > 100.0:
        return 100.0
    return float(value)
