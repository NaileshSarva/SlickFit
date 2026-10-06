"""Genetic Algorithm search for the optimal future training-load sequence.

Given an athlete's current accumulated Fitness/Fatigue state (derived from
their real training history) and a target event N days away, this module
searches the space of possible daily training loads for the remaining days
and returns the sequence that maximizes predicted performance on the event
day, subject to simple realism constraints (max load, max day-to-day jump).

Implemented from scratch: chromosome encoding, fitness evaluation,
tournament selection, crossover, mutation, and elitism.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .simulation import simulate_forward


@dataclass
class TaperConstraints:
    max_daily_load: float = 100.0
    min_daily_load: float = 0.0
    max_daily_increase: float = 25.0  # largest jump allowed vs previous day
    increase_penalty_weight: float = 5.0


@dataclass
class GAConfig:
    population_size: int = 60
    generations: int = 150
    elite_count: int = 4
    tournament_size: int = 4
    crossover_rate: float = 0.8
    mutation_rate: float = 0.15
    mutation_sigma: float = 12.0
    seed: int | None = None


@dataclass
class TaperResult:
    best_loads: list[float]
    predicted_peak_performance: float
    fitness_history: list[float] = field(default_factory=list)


def _random_chromosome(days: int, constraints: TaperConstraints, rng: random.Random) -> list[float]:
    return [rng.uniform(constraints.min_daily_load, constraints.max_daily_load) for _ in range(days)]


def _clamp(value: float, constraints: TaperConstraints) -> float:
    return max(constraints.min_daily_load, min(constraints.max_daily_load, value))


def _evaluate(
    chromosome: list[float],
    loads_history: list[float],
    k1: float,
    k2: float,
    tau1: float,
    tau2: float,
    p0: float,
    constraints: TaperConstraints,
) -> float:
    """Fitness = predicted performance on the final (event) day, minus
    a penalty for any day-to-day jump exceeding max_daily_increase."""
    sim = simulate_forward(loads_history, chromosome, k1, k2, tau1, tau2, p0)
    peak_performance = float(sim["performance"][-1])

    penalty = 0.0
    prev = loads_history[-1] if loads_history else chromosome[0]
    for load in chromosome:
        jump = abs(load - prev)
        if jump > constraints.max_daily_increase:
            penalty += (jump - constraints.max_daily_increase) * constraints.increase_penalty_weight
        prev = load

    return peak_performance - penalty


def _tournament_select(
    population: list[list[float]],
    fitnesses: list[float],
    tournament_size: int,
    rng: random.Random,
) -> list[float]:
    contenders = rng.sample(range(len(population)), tournament_size)
    best_idx = max(contenders, key=lambda i: fitnesses[i])
    return population[best_idx]


def _crossover(parent_a: list[float], parent_b: list[float], rng: random.Random) -> tuple[list[float], list[float]]:
    n = len(parent_a)
    if n < 2:
        return parent_a[:], parent_b[:]
    point = rng.randint(1, n - 1)
    child_a = parent_a[:point] + parent_b[point:]
    child_b = parent_b[:point] + parent_a[point:]
    return child_a, child_b


def _mutate(chromosome: list[float], config: GAConfig, constraints: TaperConstraints, rng: random.Random) -> list[float]:
    mutated = chromosome[:]
    for i in range(len(mutated)):
        if rng.random() < config.mutation_rate:
            mutated[i] = _clamp(mutated[i] + rng.gauss(0, config.mutation_sigma), constraints)
    return mutated


def find_optimal_taper(
    loads_history: list[float],
    days_until_event: int,
    k1: float,
    k2: float,
    tau1: float,
    tau2: float,
    p0: float,
    constraints: TaperConstraints | None = None,
    config: GAConfig | None = None,
) -> TaperResult:
    """Search for the future training-load sequence that maximizes
    predicted performance on the event day.
    """
    if days_until_event < 1:
        raise ValueError("days_until_event must be at least 1")

    constraints = constraints or TaperConstraints()
    config = config or GAConfig()
    rng = random.Random(config.seed)

    population = [
        _random_chromosome(days_until_event, constraints, rng)
        for _ in range(config.population_size)
    ]

    fitness_history: list[float] = []
    best_chromosome = population[0]
    best_fitness = float("-inf")

    for _generation in range(config.generations):
        fitnesses = [
            _evaluate(chrom, loads_history, k1, k2, tau1, tau2, p0, constraints)
            for chrom in population
        ]

        gen_best_idx = max(range(len(population)), key=lambda i: fitnesses[i])
        if fitnesses[gen_best_idx] > best_fitness:
            best_fitness = fitnesses[gen_best_idx]
            best_chromosome = population[gen_best_idx][:]
        fitness_history.append(best_fitness)

        ranked = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
        next_population = [population[i][:] for i in ranked[: config.elite_count]]

        while len(next_population) < config.population_size:
            parent_a = _tournament_select(population, fitnesses, config.tournament_size, rng)
            parent_b = _tournament_select(population, fitnesses, config.tournament_size, rng)

            if rng.random() < config.crossover_rate:
                child_a, child_b = _crossover(parent_a, parent_b, rng)
            else:
                child_a, child_b = parent_a[:], parent_b[:]

            child_a = _mutate(child_a, config, constraints, rng)
            child_b = _mutate(child_b, config, constraints, rng)

            next_population.append(child_a)
            if len(next_population) < config.population_size:
                next_population.append(child_b)

        population = next_population

    return TaperResult(
        best_loads=best_chromosome,
        predicted_peak_performance=best_fitness,
        fitness_history=fitness_history,
    )
