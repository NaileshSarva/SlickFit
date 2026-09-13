import numpy as np
import pytest

from src.peakforge.simulation import simulate, simulate_forward, _decay_factor


def test_decay_factor_bounds():
    d = _decay_factor(42)
    assert 0 < d < 1


def test_decay_factor_invalid_tau():
    with pytest.raises(ValueError):
        _decay_factor(0)


def test_zero_load_gives_zero_everything():
    result = simulate([0, 0, 0, 0], k1=1.0, k2=1.0, tau1=42, tau2=7, p0=5.0)
    assert np.allclose(result["fitness"], 0)
    assert np.allclose(result["fatigue"], 0)
    assert np.allclose(result["performance"], 5.0)


def test_single_impulse_decays_over_time():
    loads = [100] + [0] * 20
    result = simulate(loads, k1=1.0, k2=1.0, tau1=42, tau2=7, p0=0.0)
    # fatigue decays faster than fitness (shorter tau)
    assert result["fatigue"][-1] < result["fitness"][-1]
    # both should be strictly decreasing after the impulse
    assert np.all(np.diff(result["fitness"][1:]) < 0)
    assert np.all(np.diff(result["fatigue"][1:]) < 0)


def test_fatigue_decays_faster_than_fitness_short_term():
    loads = [50] * 5 + [0] * 5
    result = simulate(loads, k1=1.0, k2=1.0, tau1=42, tau2=7, p0=0.0)
    # right after training stops, fatigue should drop below fitness within a few days
    # (fast tau=7 vs slow tau=42) -- performance should be rising as fatigue clears
    perf = result["performance"]
    assert perf[-1] > perf[5]


def test_simulate_forward_matches_continuous_simulation():
    history = [40, 50, 60]
    future = [30, 20]
    forward_result = simulate_forward(history, future, k1=1.0, k2=1.0, tau1=42, tau2=7, p0=0.0)

    full_result = simulate(history + future, k1=1.0, k2=1.0, tau1=42, tau2=7, p0=0.0)

    assert np.allclose(forward_result["fitness"], full_result["fitness"][len(history):])
    assert np.allclose(forward_result["performance"], full_result["performance"][len(history):])
