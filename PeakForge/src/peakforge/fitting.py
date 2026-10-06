"""Personalized parameter fitting for the Banister Fitness-Fatigue model.

Performance(t) = p0 + k1 * Fitness(t) - k2 * Fatigue(t)

is linear in (p0, k1, k2) once Fitness(t) and Fatigue(t) have been
computed for a fixed pair of time constants (tau1, tau2). This lets us
fit (p0, k1, k2) exactly via ordinary least squares for any candidate
(tau1, tau2), and then search over a small grid of physiologically
plausible time constants to find the combination with lowest residual
error — a simple, transparent profile-likelihood style approach that
does not depend on any black-box ML library.
"""

from __future__ import annotations

import numpy as np

from .models import AthleteParams
from .simulation import simulate

# Physiologically plausible search grid for the two time constants (days).
DEFAULT_TAU1_GRID = list(range(20, 55, 5))   # fitness: 20-50 days
DEFAULT_TAU2_GRID = list(range(3, 15, 2))    # fatigue: 3-13 days


def _linear_fit(fitness: np.ndarray, fatigue: np.ndarray, scores: np.ndarray) -> tuple[float, float, float, float]:
    """Solve Performance = p0 + k1*Fitness - k2*Fatigue via least squares.

    Returns (p0, k1, k2, residual_sum_of_squares).
    """
    design = np.column_stack([np.ones_like(fitness), fitness, -fatigue])
    coeffs, residuals, _rank, _sv = np.linalg.lstsq(design, scores, rcond=None)
    p0, k1, k2 = coeffs

    predicted = design @ coeffs
    rss = float(np.sum((predicted - scores) ** 2))
    return float(p0), float(k1), float(k2), rss


def fit_parameters(
    loads: list[float],
    observation_days: list[int],
    observation_scores: list[float],
    tau1_grid: list[int] | None = None,
    tau2_grid: list[int] | None = None,
) -> AthleteParams:
    """Fit personalized Banister model parameters from an athlete's history.

    Parameters
    ----------
    loads : daily training load series, index 0 = first logged day.
    observation_days : indices into `loads` where a performance test
        was recorded (0-based, same indexing as `loads`).
    observation_scores : the recorded performance score for each
        corresponding day in `observation_days`.
    tau1_grid, tau2_grid : candidate time constants to search over.

    Returns
    -------
    AthleteParams with the best-fitting (k1, k2, tau1, tau2, p0) and
    the residual sum of squared errors for that fit.

    Raises
    ------
    ValueError if fewer than 3 performance observations are supplied —
    (p0, k1, k2) cannot be reliably identified with fewer data points.
    """
    if len(observation_days) < 3:
        raise ValueError(
            "at least 3 performance observations are required to fit "
            "(p0, k1, k2) reliably"
        )
    if len(observation_days) != len(observation_scores):
        raise ValueError("observation_days and observation_scores must be the same length")

    tau1_grid = tau1_grid or DEFAULT_TAU1_GRID
    tau2_grid = tau2_grid or DEFAULT_TAU2_GRID

    scores = np.asarray(observation_scores, dtype=float)
    obs_idx = np.asarray(observation_days, dtype=int)

    best: AthleteParams | None = None
    best_rss = np.inf

    for tau1 in tau1_grid:
        for tau2 in tau2_grid:
            sim = simulate(loads, k1=1.0, k2=1.0, tau1=tau1, tau2=tau2, p0=0.0)
            fitness_obs = sim["fitness"][obs_idx]
            fatigue_obs = sim["fatigue"][obs_idx]

            p0, k1, k2, rss = _linear_fit(fitness_obs, fatigue_obs, scores)

            if rss < best_rss:
                best_rss = rss
                best = AthleteParams(
                    k1=k1, k2=k2, tau1=float(tau1), tau2=float(tau2),
                    p0=p0, residual_error=rss,
                )

    assert best is not None
    return best
