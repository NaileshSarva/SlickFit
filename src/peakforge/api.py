"""FastAPI HTTP layer for the PeakForge engine."""

from __future__ import annotations

import datetime as dt
from dataclasses import asdict
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .fitting import fit_parameters
from .models import AthleteParams, PerformanceTest, TrainingSession
from .optimizer import GAConfig, TaperConstraints, find_optimal_taper
from .simulation import simulate
from .storage import PeakForgeStore


app = FastAPI(title="PeakForge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SessionCreate(BaseModel):
    date: str
    duration_min: float = Field(gt=0)
    intensity: float = Field(gt=0)
    notes: str = ""


class SessionResponse(BaseModel):
    date: str
    load: float
    notes: str = ""


class PerformanceTestBody(BaseModel):
    date: str
    score: float


class AthleteParamsBody(BaseModel):
    k1: float
    k2: float
    tau1: float
    tau2: float
    p0: float
    residual_error: float = 0.0


class SimulationResponse(BaseModel):
    dates: list[str]
    fitness: list[float]
    fatigue: list[float]
    performance: list[float]


class FitResponse(BaseModel):
    params: AthleteParamsBody
    simulation: SimulationResponse


class TaperConstraintsBody(BaseModel):
    max_daily_load: float = 100.0
    min_daily_load: float = 0.0
    max_daily_increase: float = 25.0
    increase_penalty_weight: float = 5.0


class GAConfigBody(BaseModel):
    population_size: int = 60
    generations: int = 150
    elite_count: int = 4
    tournament_size: int = 4
    crossover_rate: float = 0.8
    mutation_rate: float = 0.15
    mutation_sigma: float = 12.0
    seed: int | None = None


class TaperRequest(BaseModel):
    days_until_event: int
    constraints: TaperConstraintsBody | None = None
    config: GAConfigBody | None = None


class TaperResponse(BaseModel):
    best_loads: list[float]
    predicted_peak_performance: float
    fitness_history: list[float]
    simulation: SimulationResponse


def get_store():
    store = PeakForgeStore()
    try:
        yield store
    finally:
        store.close()


StoreDep = Annotated[PeakForgeStore, Depends(get_store)]


def _session_response(session: TrainingSession) -> SessionResponse:
    return SessionResponse(date=session.date, load=session.load, notes=session.notes)


def _test_response(test: PerformanceTest) -> PerformanceTestBody:
    return PerformanceTestBody(date=test.date, score=test.score)


def _params_response(params: AthleteParams) -> AthleteParamsBody:
    return AthleteParamsBody(**asdict(params))


def _simulation_response(dates: list[str], sim: dict) -> SimulationResponse:
    return SimulationResponse(
        dates=dates,
        fitness=sim["fitness"].astype(float).tolist(),
        fatigue=sim["fatigue"].astype(float).tolist(),
        performance=sim["performance"].astype(float).tolist(),
    )


def _model_data(model: BaseModel) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _projected_dates(session_dates: list[str], future_count: int) -> list[str]:
    if not session_dates:
        return [str(i) for i in range(future_count)]

    try:
        last_date = dt.date.fromisoformat(session_dates[-1])
    except ValueError:
        return session_dates + [str(i) for i in range(len(session_dates), len(session_dates) + future_count)]

    future_dates = [
        (last_date + dt.timedelta(days=offset)).isoformat()
        for offset in range(1, future_count + 1)
    ]
    return session_dates + future_dates


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/sessions", response_model=SessionResponse)
def add_session(body: SessionCreate, store: StoreDep) -> SessionResponse:
    load = body.duration_min * body.intensity
    session = TrainingSession(date=body.date, load=load, notes=body.notes)
    store.add_session(session)
    return _session_response(session)


@app.get("/sessions", response_model=list[SessionResponse])
def list_sessions(store: StoreDep) -> list[SessionResponse]:
    return [_session_response(session) for session in store.list_sessions()]


@app.post("/performance-tests", response_model=PerformanceTestBody)
def add_performance_test(body: PerformanceTestBody, store: StoreDep) -> PerformanceTestBody:
    test = PerformanceTest(date=body.date, score=body.score)
    store.add_performance_test(test)
    return _test_response(test)


@app.get("/performance-tests", response_model=list[PerformanceTestBody])
def list_performance_tests(store: StoreDep) -> list[PerformanceTestBody]:
    return [_test_response(test) for test in store.list_performance_tests()]


@app.post("/fit", response_model=FitResponse)
def fit(store: StoreDep) -> FitResponse:
    sessions = store.list_sessions()
    tests = store.list_performance_tests()

    if len(sessions) < 5:
        raise HTTPException(status_code=400, detail="Log at least 5 training sessions before fitting.")
    if len(tests) < 3:
        raise HTTPException(status_code=400, detail="Log at least 3 performance tests before fitting.")

    session_dates = [session.date for session in sessions]
    loads = [session.load for session in sessions]
    date_index = {date: index for index, date in enumerate(session_dates)}

    observation_days: list[int] = []
    observation_scores: list[float] = []
    for test in tests:
        if test.date in date_index:
            observation_days.append(date_index[test.date])
            observation_scores.append(test.score)

    if len(observation_days) < 3:
        raise HTTPException(
            status_code=400,
            detail="Performance test dates must match logged session dates.",
        )

    try:
        params = fit_parameters(loads, observation_days, observation_scores)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    store.save_params(params)
    sim = simulate(loads, params.k1, params.k2, params.tau1, params.tau2, params.p0)
    return FitResponse(params=_params_response(params), simulation=_simulation_response(session_dates, sim))


@app.get("/params/latest", response_model=AthleteParamsBody)
def latest_params(store: StoreDep) -> AthleteParamsBody:
    params = store.latest_params()
    if params is None:
        raise HTTPException(status_code=404, detail="No fitted parameters exist yet.")
    return _params_response(params)


@app.post("/taper", response_model=TaperResponse)
def taper(body: TaperRequest, store: StoreDep) -> TaperResponse:
    params = store.latest_params()
    if params is None:
        raise HTTPException(status_code=400, detail="Fit parameters before running the taper optimizer.")

    sessions = store.list_sessions()
    session_dates = [session.date for session in sessions]
    loads_history = [session.load for session in sessions]

    constraints = TaperConstraints(**_model_data(body.constraints)) if body.constraints else TaperConstraints()
    config = GAConfig(**_model_data(body.config)) if body.config else GAConfig()

    try:
        result = find_optimal_taper(
            loads_history,
            body.days_until_event,
            params.k1,
            params.k2,
            params.tau1,
            params.tau2,
            params.p0,
            constraints=constraints,
            config=config,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    full_loads = loads_history + result.best_loads
    full_dates = _projected_dates(session_dates, len(result.best_loads))
    sim = simulate(full_loads, params.k1, params.k2, params.tau1, params.tau2, params.p0)

    return TaperResponse(
        best_loads=[float(load) for load in result.best_loads],
        predicted_peak_performance=float(result.predicted_peak_performance),
        fitness_history=[float(value) for value in result.fitness_history],
        simulation=_simulation_response(full_dates, sim),
    )
