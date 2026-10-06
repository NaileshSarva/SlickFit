# SlickFit

**SlickFit is an India-first, running-first event-preparation coach.** It helps an athlete prepare for an event through a practical loop:

**Plan → Train → Track → Evaluate → Adapt → Repeat**

The current repository is a local development prototype. It includes a React/Vite frontend, a FastAPI backend, SQLite persistence, deterministic planning/adaptation logic, and a separate archived PeakForge prototype. It is not a medical product and does not replace a qualified coach or clinician.

## Current scope

The SlickFit app is intended to support:

- Local account registration and demo profiles.
- Event setup and athlete onboarding.
- A running-first preparation plan, with custom-event setup.
- Daily training, activity logging, and recovery check-ins.
- Plan adaptation and revision history.
- General nutrition guidance and progress views.
- User-scoped records and corrections with an audit trail.

Plans are recommendations. The user remains in control. Missed workouts should not be blindly stacked onto later days. Sparse inputs and estimates must be treated as uncertain. SlickFit does not diagnose or treat medical conditions.

## Repository layout

```text
.
├── frontend/                 # React + Vite web app
├── src/slickfit/             # FastAPI app, domain logic, auth and database models
├── src/peakforge/            # Retained PeakForge compatibility API/code
├── alembic/                  # Database migrations
├── tests/                    # Backend unit and integration tests
├── PeakForge/                # Original PeakForge project snapshot
└── SlickFit_Antigravity_Build_Spec.md
```

## Requirements

- Python 3.11 or newer (the local project virtual environment may use a newer Python version).
- Node.js and npm.

## Run locally

From the repository root, create and activate a virtual environment if one is not already present, then install the Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Apply the database schema:

```bash
./.venv/bin/alembic upgrade head
```

Start the backend in one terminal:

```bash
cd /Users/nico/Developer/SlickFit
./.venv/bin/uvicorn src.slickfit.api.app:app --host 127.0.0.1 --port 8001
```

Start the frontend in a second terminal:

```bash
cd /Users/nico/Developer/SlickFit/frontend
npm install
VITE_API_URL=http://127.0.0.1:8001/api/v1 npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Open <http://127.0.0.1:5173>. Keep both terminal processes running while using the app. Stop each server with `Ctrl+C`.

If a port is already in use, an earlier server may still be running. Check the existing app before starting another copy. The default local database is `slickfit.db` in the repository root; back it up before manually changing or deleting it.

## API health and docs

- Health: <http://127.0.0.1:8001/health>
- OpenAPI docs: <http://127.0.0.1:8001/docs>

## Tests and frontend build

From the repository root:

```bash
./.venv/bin/pytest
```

For the frontend production build:

```bash
cd frontend
npm run build
```

Run these checks locally before treating a change as verified. A successful build or test suite does not establish sports-science validity or production readiness.

## Prototype limitations

- SQLite and the local demo flow are for local development and demonstration. Do not expose them as a production multi-user service without a security, deployment, and data-retention review.
- No wearable integration, payment processing, medical diagnosis, or validated race-time prediction is claimed.
- Training recommendations are deterministic MVP guidance and need appropriate domain review before use as high-stakes coaching advice.
- Keep secrets out of source control. Production requires deployment-specific secrets, HTTPS, secure authentication/session settings, migrations, backups, and monitoring.

## License and project status

See the repository for current licensing and project status. Do not infer production readiness from the presence of tests or demo screens.
