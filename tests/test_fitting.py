import numpy as np
import pytest

from src.peakforge.fitting import fit_parameters
from src.peakforge.simulation import simulate


def test_fit_recovers_known_parameters_on_synthetic_data():
    rng = np.random.default_rng(42)
    n_days = 60
    loads = list(rng.uniform(20, 80, size=n_days))

    true_k1, true_k2 = 0.9, 1.6
    true_tau1, true_tau2 = 40.0, 8.0
    true_p0 = 10.0

    sim = simulate(loads, true_k1, true_k2, true_tau1, true_tau2, true_p0)

    # sample a handful of "test days" with the true (noiseless) performance
    obs_days = [10, 20, 30, 40, 50, 59]
    obs_scores = [sim["performance"][d] for d in obs_days]

    fitted = fit_parameters(
        loads, obs_days, obs_scores,
        tau1_grid=[30, 35, 40, 45, 50],
        tau2_grid=[5, 7, 8, 10, 12],
    )

    # with noiseless data on the grid, the fit should recover the true taus
    # exactly (they're on the grid) and the residual error should be ~0
    assert fitted.tau1 == pytest.approx(true_tau1)
    assert fitted.tau2 == pytest.approx(true_tau2)
    assert fitted.residual_error == pytest.approx(0.0, abs=1e-6)


def test_fit_requires_minimum_observations():
    loads = [10] * 10
    with pytest.raises(ValueError):
        fit_parameters(loads, [1, 2], [5.0, 6.0])


def test_fit_rejects_mismatched_lengths():
    loads = [10] * 10
    with pytest.raises(ValueError):
        fit_parameters(loads, [1, 2, 3], [5.0, 6.0])
