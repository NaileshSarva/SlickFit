"""Core data structures used across the PeakForge engine."""

from dataclasses import dataclass


@dataclass
class TrainingSession:
    """A single logged training session.

    load is the training impulse for the day, typically computed as
    duration_minutes * intensity (RPE 1-10), often called TRIMP.
    """
    date: str  # ISO format YYYY-MM-DD
    load: float
    notes: str = ""


@dataclass
class PerformanceTest:
    """A recorded performance benchmark (time trial, test score, etc.)."""
    date: str  # ISO format YYYY-MM-DD
    score: float  # higher = better performance, normalize before logging if needed


@dataclass
class AthleteParams:
    """Fitted Banister Impulse-Response model parameters for one athlete."""
    k1: float          # fitness weighting coefficient
    k2: float          # fatigue weighting coefficient
    tau1: float         # fitness (CTL) time constant, days
    tau2: float         # fatigue (ATL) time constant, days
    p0: float           # baseline performance
    residual_error: float = 0.0
