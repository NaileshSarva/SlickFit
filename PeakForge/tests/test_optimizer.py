from src.peakforge.optimizer import GAConfig, TaperConstraints, find_optimal_taper


def test_optimizer_improves_fitness_over_generations():
    loads_history = [60, 65, 70, 55, 60, 62, 58]
    config = GAConfig(population_size=30, generations=40, seed=1)
    constraints = TaperConstraints(max_daily_load=100, max_daily_increase=30)

    result = find_optimal_taper(
        loads_history, days_until_event=10,
        k1=1.0, k2=1.5, tau1=42, tau2=7, p0=0.0,
        constraints=constraints, config=config,
    )

    # fitness history should be non-decreasing (elitism preserves the best)
    history = result.fitness_history
    assert all(b >= a - 1e-9 for a, b in zip(history, history[1:]))
    # the final best should be at least as good as the first generation's best
    assert history[-1] >= history[0]


def test_optimizer_returns_correct_length_sequence():
    loads_history = [50, 50, 50]
    config = GAConfig(population_size=20, generations=10, seed=2)
    result = find_optimal_taper(
        loads_history, days_until_event=14,
        k1=1.0, k2=1.5, tau1=42, tau2=7, p0=0.0,
        config=config,
    )
    assert len(result.best_loads) == 14


def test_optimizer_rejects_invalid_days():
    import pytest
    with pytest.raises(ValueError):
        find_optimal_taper([10, 10], days_until_event=0, k1=1, k2=1, tau1=42, tau2=7, p0=0)


def test_optimizer_respects_load_bounds():
    loads_history = [40, 40, 40]
    constraints = TaperConstraints(max_daily_load=70, min_daily_load=10, max_daily_increase=50)
    config = GAConfig(population_size=25, generations=25, seed=3)
    result = find_optimal_taper(
        loads_history, days_until_event=7,
        k1=1.0, k2=1.5, tau1=42, tau2=7, p0=0.0,
        constraints=constraints, config=config,
    )
    assert all(constraints.min_daily_load <= v <= constraints.max_daily_load for v in result.best_loads)
