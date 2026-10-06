# PeakForge

**A Physiological Performance-Simulation & Optimal Taper Engine**

PeakForge is an offline, single-language (Python) application that models
an athlete's fitness and fatigue as a dynamical system from their own
training history, and computes the optimal training-load sequence leading
up to a target event date so that predicted performance peaks exactly
when it matters.

Unlike conventional fitness apps, which either passively record completed
workouts or issue generic templated training plans, PeakForge simulates
how an individual's performance evolves under different training
scenarios and solves for the scenario that maximizes performance on a
chosen date.

## How it works

1. **Simulation engine** — implements the Banister Impulse-Response
   (Fitness-Fatigue) model as a discrete-time simulation: each day's
   training load feeds two exponentially decaying accumulators, Fitness
   (slow decay) and Fatigue (fast decay). Predicted performance is the
   difference between the two, scaled by fitted weights.
2. **Personalized parameter fitting** — fits the model's parameters to
   an individual athlete's own logged training and performance-test
   history via least-squares regression over a grid of physiologically
   plausible time constants — no black-box ML library.
3. **Optimal taper search** — given a target event date, a
   from-scratch Genetic Algorithm searches the space of possible future
   daily training loads to find the sequence that maximizes predicted
   performance on that date, subject to realistic constraints (maximum
   load, maximum day-to-day increase).
4. **Local storage & UIs** — training sessions, performance tests, and
   fitted parameters are stored in a local SQLite database; the Flet
   desktop UI and FastAPI-backed React dashboard both let the user log
   sessions, fit their model, and run the optimizer.

Everything runs fully offline — no external API, wearable device, or
cloud service is required.

## Project structure

```
PeakForge/
├── main.py                     # application entry point
├── requirements.txt
├── data/
│   └── sample_training_log.csv # synthetic demo data
├── src/peakforge/
│   ├── models.py                # TrainingSession, PerformanceTest, AthleteParams
│   ├── simulation.py            # Banister Fitness-Fatigue simulation engine
│   ├── fitting.py                # least-squares personalized parameter fitting
│   ├── optimizer.py              # Genetic Algorithm optimal taper search
│   ├── storage.py                # SQLite persistence layer
│   ├── app.py                    # Flet UI
│   └── api.py                    # FastAPI HTTP layer
├── frontend/                     # Vite + React dashboard
└── tests/
    ├── test_simulation.py
    ├── test_fitting.py
    ├── test_optimizer.py
    ├── test_storage.py
    └── test_api.py
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the app

```bash
python main.py
```

## Running the API

```bash
uvicorn src.peakforge.api:app --reload
```

## Running the React frontend

Run both halves together from separate terminals:

```bash
# Terminal 1
uvicorn src.peakforge.api:app --reload

# Terminal 2
cd frontend
npm install
npm run dev
```

## Running the tests

```bash
pytest -v
```

## Tech stack

| Layer                | Technology                                             |
|-----------------------|---------------------------------------------------------|
| Language              | Python 3.11+                                            |
| Numerical computing   | NumPy                                                    |
| Core algorithms       | Hand-implemented Banister simulation, least-squares fitting, Genetic Algorithm |
| Data storage          | SQLite (`sqlite3`)                                        |
| API                   | FastAPI, Uvicorn                                        |
| UI                    | Flet, React, Vite                                       |
| Visualization         | Matplotlib, Recharts                                    |
| Testing               | pytest                                                   |

## Status

Zeroth-review stage — core simulation, fitting, optimization, storage,
and UI scaffolding are implemented and unit-tested. See the project
report for the full methodology, timeline, and references.
