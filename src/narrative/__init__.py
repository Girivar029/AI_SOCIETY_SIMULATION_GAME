"""Narrative package — deterministic historical interpretation layer."""

from src.narrative.trends import describe_trend, compute_trends, Trend
from src.narrative.archetypes import classify_archetype
from src.narrative.reports import generate_history_reports, generate_era_report, EraReport

__all__ = ["describe_trend", "compute_trends", "Trend", "classify_archetype", "generate_history_reports", "generate_era_report", "EraReport"]
