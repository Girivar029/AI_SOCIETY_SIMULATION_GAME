"""
Role definitions — stable identifiers for the 10 institutional roles.
"""
from enum import Enum


class Role(str, Enum):
    head_of_state = "head_of_state"
    education_minister = "education_minister"
    teacher = "teacher"
    doctor = "doctor"
    health_food_minister = "health_food_minister"
    tax_minister = "tax_minister"
    justice_minister = "justice_minister"
    industry_minister = "industry_minister"
    science_minister = "science_minister"
    defense_minister = "defense_minister"

    def __str__(self) -> str:
        return self.value


# Deterministic iteration order — sorted by enum value string, but explicit list is clearer
ROLES: list[Role] = [
    Role.head_of_state,
    Role.education_minister,
    Role.teacher,
    Role.doctor,
    Role.health_food_minister,
    Role.tax_minister,
    Role.justice_minister,
    Role.industry_minister,
    Role.science_minister,
    Role.defense_minister,
]

ROLE_NAMES: list[str] = [r.value for r in ROLES]
