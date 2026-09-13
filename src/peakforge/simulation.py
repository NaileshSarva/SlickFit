"""Banister Impulse-Response (Fitness-Fatigue) simulation engine.

Each day's training load is treated as an impulse that feeds two
exponentially decaying accumulators:

    Fitness (CTL) - slow decay,  long time constant (tau1, default 42 days)
    Fatigue (ATL) - fast decay, short time constant (tau2, default 7 days)

Predicted performance on day t is:

    Performance(t) = p0 + k1 * Fitness(t) - k2 * Fatigue(t)

This module implements the discrete-time recurrence relations directly —
no external simulation/ODE library is used.
"""

from __future__ import annotations

import numpy as np


def _decay_factor(tau: float) -> float:
    """Single-day exponential decay factor for a given time constant."""
    if tau <= 0:
        raise ValueError("time constant tau must be positive")
    return float(np.exp(-1.0 / tau))


def simulate(
    loads: list[float] | np.ndarray,
    k1: float,
    k2: float,
    tau1: float = 42.0,
    tau2: float = 7.0,
    p0: float = 0.0,
) -> dict[str, np.ndarray]:
    """Run the discrete-time Fitness-Fatigue simulation over a load series.

    Parameters
    ----------
    loads : sequence of daily training loads, index 0 = first day.
    k1, k2 : fitness / fatigue weighting coefficients.
    tau1, tau2 : fitness / fatigue decay time constants, in days.
    p0 : baseline performance level.

    Returns
    -------
    dict with numpy arrays "fitness", "fatigue", "performance", each of
    the same length as `loads`.
    """
    loads = np.asarray(loads, dtype=float)
    n = len(loads)

    decay1 = _decay_factor(tau1)
    decay2 = _decay_factor(tau2)

    fitness = np.zeros(n)
    fatigue = np.zeros(n)

    prev_fitness = 0.0
    prev_fatigue = 0.0
    for t in range(n):
        curr_fitness = prev_fitness * decay1 + loads[t]
        curr_fatigue = prev_fatigue * decay2 + loads[t]
        fitness[t] = curr_fitness
        fatigue[t] = curr_fatigue
        prev_fitness = curr_fitness
        prev_fatigue = curr_fatigue

    performance = p0 + k1 * fitness - k2 * fatigue

    return {"fitness": fitness, "fatigue": fatigue, "performance": performance}


def simulate_forward(
    loads_history: list[float],
    future_loads: list[float],
    k1: float,
    k2: float,
    tau1: float = 42.0,
    tau2: float = 7.0,
    p0: float = 0.0,
) -> dict[str, np.ndarray]:
    """Simulate history + a proposed future load sequence in one continuous run.

    Useful for the optimizer: it needs performance predictions on future
    days given the athlete's real accumulated state up to today.
    """
    combined = list(loads_history) + list(future_loads)
    result = simulate(combined, k1, k2, tau1, tau2, p0)
    split = len(loads_history)
    return {
        "fitness": result["fitness"][split:],
        "fatigue": result["fatigue"][split:],
        "performance": result["performance"][split:],
    }
