# SlickFit — Antigravity Repository Audit & End-to-End Build Brief

## Purpose and execution instruction

Use this brief to turn the existing PeakForge repository into a demonstrable SlickFit MVP. First inspect the repository and its history, then make a short inventory of what is sound, what is unsafe or misleading, and what must change. Reuse good implementation where it fits; refactor or replace weak foundations without preserving code merely because it exists. Implement the end-to-end MVP described below in the repository. Do not stop after generating a plan, mockup, or architecture document. Do not ask the user to make routine product or engineering choices; use the decisions in this brief and reasonable engineering judgment. If a required external credential or service is unavailable, deliver a complete local/demo path, make the limitation clear, and do not claim the missing capability works.

The attached SlickFit Product Specification v0.1 is the product source of truth. This document resolves its open implementation choices for a realistic first build. Product rules marked **LOCKED** must be preserved. Technology choices are **GUIDANCE** and may change when repository evidence justifies a simpler or safer alternative, but explain material changes in the final handoff.

## Executive product definition

SlickFit is a personalized event-preparation coach. Its central loop is:

**Plan → Train → Track → Evaluate → Adapt → Repeat**

It gives the user a clear recommendation for today, records what actually happened, and safely adjusts the upcoming plan with understandable reasons. It is a recommendation tool; the user remains in control. It is not a medical product, an autonomous clinical decision system, or an AI-generated workout chatbot.

### Locked product requirements

- **India-first**, with Asia/Kolkata and Indian date/time conventions by default; kg, cm, km, °C, kcal, and INR where relevant. Support vegetarian, eggetarian, non-vegetarian, and vegan preferences and regional variation without treating Indian food as one cuisine.
- Support structured events eventually, but do not pretend to have specialized models for every sport. The MVP is **running-first**, with **custom event setup** available through explicit measurable requirements and conservative, transparent recommendations.
- Account, event, profile, baseline with “I don’t know,” availability/equipment, plan, daily Home, guided Train flow, actual-workout logging, recovery check-in, safe missed-workout handling, nutrition guidance, progress/history, explanation of meaningful adaptations, correction of important data, always-visible event countdown, and responsive web UX are MVP scope.
- User can review and correct important data. Keep the original value and correction history; never silently overwrite the audit trail. Label source, timestamp, confidence, and derived status where meaningful.
- Estimates and model outputs must not be presented as ground truth. Do not fabricate reasoning, measurements, evidence, validation, or capabilities.
- Never stack missed training blindly. Preserve recovery and event priorities; intentionally dropping a session is acceptable.
- Pain, illness, and severe fatigue should make recommendations conservative. No diagnosis, treatment, or “ignore warning and continue” bypass.
- Separate training calculations, planning/adaptation, storage/API, and explanatory language. AI is optional and is not the underlying training algorithm.
- Core success is a demonstrable closed loop: goal → baseline → feasible plan → today → activity → evaluation → reasoned adaptation → updated plan and history.

## 1. Repository inspection and evidence-based gap analysis

Repository supplied: `PeakForge.zip`. Its relevant contents include `src/peakforge/{models,simulation,fitting,optimizer,storage,api,app}.py`, a React/Vite frontend, SQLite persistence, pytest tests, and `data/sample_training_log.csv`. It also contains archived `.git`, virtual-environment, `node_modules`, build/cache and temporary-file content; treat those as baggage, not application source. `design-reference` contains no useful design files in the supplied archive. Inspect the actual checkout before changing it, including the current branch/diff and any additional files present at execution time.

### Keep or adapt

- **FastAPI + Python** is a reasonable MVP service base. Keep the API framework if it remains maintainable; build explicit domain/service boundaries around it.
- **React + Vite** and the existing responsive-capable frontend are a reasonable shell. Reuse components/styles only after checking accessibility and interaction quality; the current dashboard layout is not the target product UX.
- **SQLite storage** and repository tests show a useful prototype baseline. SQLite is suitable for local demos and one-user development, not an unexamined multi-user production deployment. Use migrations and a repository/service abstraction. For hosted multi-user deployment, choose a managed relational database such as PostgreSQL unless a strong reason supports another option.
- **Recharts** may be reused for accessible progress charts when the chart helps a user answer a question. Avoid the current arbitrary-unit curve as a user-facing performance claim.
- Existing numerical modules may be retained behind isolated interfaces as experimental analysis utilities only if code review and tests justify them.

### Refactor or replace

- Replace the current home page workflow (“log training/test → fit model → optimize taper”) with SlickFit’s onboarding, Home, Plan, Train, Nutrition, Progress, Profile and unified history experience.
- Replace the global single-athlete data access pattern with user-scoped services and persistence. Every query and mutation must be scoped to the authenticated principal.
- Replace the underspecified `TrainingSession(date, load, notes)` as the canonical activity record with typed planned-session, actual-session, metric, source/confidence, and amendment records. Preserve legacy import only as an explicit mapping path.
- Replace unversioned SQLite schema creation with migrations, constraints, transaction handling and documented backup/development setup.
- Replace string dates and direct date-index assumptions with validated timezone-aware event dates, local-day boundaries, and real calendar-day series including zero-training days where a calculation needs a daily series.
- Replace blanket API error strings with consistent structured validation and domain errors; never return internal exception details or sensitive data.
- Remove or isolate the unused Flet UI if it creates duplicate product surfaces and maintenance burden. Keep only if the repo proves it is intentionally required and it can share the same domain behavior.
- Remove bundled `.venv`, `node_modules`, `dist`, cache, `.DS_Store`, `tempCodeRunnerFile*`, and nested `.git` material from the deliverable/tracked source as appropriate. Do not delete user work blindly; inspect git status/history first.

### Critical findings from supplied source

These are code-grounded risks, not claims that the app has been run:

1. `simulation.py` assumes each array element is one consecutive day. API `/fit` passes only logged sessions, so skipped calendar days vanish and irregular sessions are treated as adjacent days. The performance trajectory is therefore not time-correct for sparse logs.
2. `/fit` requires five sessions and three performance tests, while fitting itself only checks three observations. The current sample CSV has 30 days, but its persistence/API path is not an importer and has no explicit zero-load daily records.
3. `fitting.py` estimates five parameters using only a small number of observations. Three observations cannot identify baseline plus two coefficients robustly, and even the route’s three-test minimum is underdetermined/fragile. It fits arbitrary user score scales without sport, protocol, noise, or measurement-quality metadata. A low residual is not proof of physiological validity.
4. `optimizer.py` maximizes a single model output on event day across arbitrary daily load values. It does not model workout type, running mileage/intensity distribution, availability, recovery/safety, event goal, missed sessions, or the quality/uncertainty of fitted parameters. Absolute jump penalties and load bounds are not a validated training prescription. Calling it “optimal” overstates what the code establishes.
5. `/taper` accepts an unbounded `days_until_event`, and GA configuration values are not comprehensively constrained. Synchronous optimization can consume server time. Apply strict bounds/time budgets to any retained compute endpoint.
6. `storage.py` stores one global athlete, opens a default home-directory database, creates tables at runtime, has no user ownership, IDs in returned session/test records, update/correction history, migrations, or explicit transaction workflow. Connection lifecycle and concurrency are not a deployable multi-user design.
7. API date strings and measurement ranges are not validated; CORS is hard-coded for localhost; there is no authentication, authorization, rate limit, CSRF strategy, privacy lifecycle, or secrets/configuration system. Current API exposes health, global session/test CRUD-create/list, parameter fitting, and taper only.
8. Existing React frontend is a single technical dashboard with hard-coded `http://localhost:8000`, no account/onboarding/planning loop, no edit/correct path, no explicit loading/empty/offline coverage beyond partial form errors, and mixed date handling (`toISOString()` may show a day different from local date near timezone boundaries).
9. Tests cover numerical smoke behavior, basic storage round trips, and API flows. They do not establish sports-science validity, safe plans, auth/privacy, date gaps, amendments, data isolation, race handling, accessibility, responsive behavior, or production readiness. No test command was run for this audit; make no claims that these tests pass.
10. README describes the app as offline and says the core is unit-tested, but those descriptions are not evidence of SlickFit readiness. The included synthetic-looking sample log and prototype score curves cannot be represented as real athlete evidence.

### Banister and genetic algorithm decision

Do **not** preserve Banister or the genetic algorithm as SlickFit’s primary plan engine. They solve a narrower taper-optimization problem and need longitudinal, standardized performance observations plus independent validation. They can remain in a quarantined experimental module, disabled from user-facing prescriptions, with clear “research prototype” labeling and bounded input if valuable for exploration. Prefer a transparent, rule-based running MVP planner with explicit safety/feasibility constraints, stable tests, and reason codes. Add a model only after a defensible validation dataset, calibration strategy, uncertainty handling, and out-of-sample evaluation exist. Never label a score “fitness”, “readiness”, “projection”, or “optimal” unless its definition and limitations are exposed and supported.

## 2. MVP architecture and implementation decisions

### Architecture

Build a modular monolith, not microservices:

1. **Web client:** React/Vite (or a clearly justified evolution of the existing stack), responsive and keyboard-accessible. Typed API client, route-level loading/error/empty states, forms with inline validation, and optimistic UI only for operations that can safely be reconciled.
2. **HTTP API:** FastAPI with versioned `/api/v1` endpoints, authentication middleware, schema validation, explicit DTOs, rate limits on auth and expensive operations, and user-scoped access checks.
3. **Domain/services:** onboarding/profile, event, baseline, plan generation, planned-session lifecycle, actual activity, recovery, nutrition guidance, progress, data correction/audit, and explanation services. Pure deterministic functions for calculations; API controllers do not contain planning policy.
4. **Persistence:** SQLAlchemy/SQLModel or another maintainable ORM plus Alembic migrations. SQLite local; PostgreSQL for hosted multi-user use. Transactions for logging/adaptation and amendment audit. Store canonical units and timezone. Add indexes for owner/date and foreign keys. Use UTC timestamps plus user timezone for local event/calendar semantics.
5. **Planner:** running-focused, deterministic, versioned planner producing a rolling near-term plan plus phase/milestone overview. Planner inputs/outputs and reason codes are persisted so the user can inspect “what changed.” Planning should be deterministic for the same version and inputs.
6. **Explanation:** generate coach copy from structured recommendation/reason data using templates initially. Do not call a language model necessary for MVP. If later added, constrain it to supplied structured facts; validate output and preserve deterministic recommendation ownership in the planning service.
7. **Deployment:** local setup through documented environment configuration and seeded demo; hosted option with managed app/database, HTTPS, secure secret injection, migrations, health checks, backups and error logging that excludes health data. Keep dev/test/prod configs separate. Do not ship secrets in frontend or repository.

Antigravity may use a different library or hosting provider if the repo or environment makes the guidance unsuitable. Preserve the boundaries, invariants, and acceptance criteria.

### Core data model (minimum)

Design concrete normalized tables/entities; names may vary, semantics may not:

- `User`: auth subject, created/updated timestamps, timezone, locale, units; do not store raw passwords if delegated auth is available.
- `AthleteProfile`: age or age band only if necessary, optional sex, height, weight, region; sensitive fields optional and explained. Avoid collecting birthdate if age band suffices. Profile edits create auditable revisions for recommendation-relevant values.
- `Event`: owner, structured/custom kind, sport/category, title, date/time/timezone, location optional, goal type, target value/unit optional, event format/duration/distance/demands, status (active/completed/cancelled), notes. At most one active event in MVP unless switching is deliberately supported cleanly.
- `Availability`: training days, daily time cap, preferred times, environment/equipment, unavailable dates, revision timestamp.
- `BaselineObservation`: discipline, value/unit/protocol/date/source, confidence, provenance and amendment link; allow unknown. For running: optional recent race/time, distance, recent weekly running volume, experience. Never infer an exact pace from absent evidence.
- `Plan` + `PlanRevision`: owner/event, algorithm/version, created time, input snapshot/hash, start/end, phase/milestones, status, explanation. Plan revisions immutable; a new revision supersedes the previous one.
- `PlannedSession`: plan revision, local date, type, purpose, duration or distance range, effort target (plain-language/RPE), warmup/main/cooldown blocks where relevant, optional pace only when evidence supports it, priority, flexibility window, status, reason codes.
- `Activity` / `ActivityRevision`: date/time/timezone, type, planned-session link optional, planned-vs-actual fields, duration/distance, perceived effort, completion state (complete/partial/skipped), notes, source, confidence, imported/manual marker. Corrections append revisions; retain original.
- `DailyCheckIn` / `CheckInRevision`: date, sleep duration/quality optional, energy, soreness, stress, fatigue and pain flags/body area/severity as appropriate, source and timestamps. Use simple scales with labels. Make check-in skippable.
- `NutritionProfile`: dietary pattern, allergies/intolerances, foods avoided, goal preference, optional existing intake, locale. Allergies must be distinct from preferences.
- `NutritionGuidance`: date, broad estimated energy/macronutrient ranges where defensible, hydration/general meal guidance, training-day rationale, algorithm/version, confidence and explicit limitations. Do not present calorie/macronutrient estimates as prescriptions or clinical advice.
- `DataAmendment` / audit record: entity/field, prior and replacement value (securely scoped), actor, reason optional, source, timestamp, affected recommendation revisions. Do not expose unrelated users’ data.
- `AdaptationEvent`: plan revision before/after, trigger inputs, deterministic reason codes and readable explanation, timestamp, algorithm version, user-visible impact.

Use constraints and validation to prevent impossible values, orphaned records, duplicate idempotent activity ingestion and cross-user reads. Never trust a user ID supplied by the client; derive owner from authenticated identity.

### Event abstraction and support boundary

Use a common event contract: date, goal, target (optional), preparation horizon, constraints, baseline observations, required capabilities, and event-specific demands. Add an event strategy/discipline adapter behind an interface, not `if` statements spread through UI/API.

- **Running is the only specialized training engine in MVP.** Support common goals: complete an event, build consistency/fitness, or pursue a stated time target only when baseline evidence and time horizon are adequate. Allow 5K/10K and generic distance/custom running event entries without claiming every distance has a validated algorithm.
- **Custom events are supported as event records and bounded manual planning.** Ask the user for format, dates, number/duration of bouts or key demands, goal, and constraints. Provide a general preparation checklist, schedule, recovery/nutrition guidance, activity logging and user-editable session blocks. Clearly label it “general/custom guidance,” avoid sport-specific prescriptions and unsupported performance predictions. If the user selects running as the measurable demand, route to the running planner. Do not imply trained support for football, cricket, powerlifting, or any other category without a corresponding tested adapter.
- Unsupported structured event types must not silently receive a running plan. Offer custom setup or a clear unsupported-specialization explanation.

### Adaptive planner: realistic first algorithm

The engine should be deterministic and conservative, not an optimizer searching arbitrary loads.

1. Validate event date, baseline quality, age/eligibility assumptions, availability, weekly time/days, recent training and recovery inputs. Ask only for data required by chosen plan path. If key inputs are missing, offer a low-confidence, introductory plan or a short baseline-building period; do not force fabricated numbers.
2. Build a weekly running structure from experience, recent volume and constraints: mostly easy running, at most a conservative quality-session pattern when the user has an adequate base and horizon, rest/recovery, and gradual volume changes. Use explicit caps and safe fallback rules; avoid aggressive one-size-fits-all percentage rules. Treat chosen values as prototype heuristics, document that they are not clinical or sports-science validation, and do not imply proven injury prevention.
3. Use user availability and time caps as hard feasibility constraints. If target and horizon are implausible for available evidence, explain the limitation and offer a completion/participation goal or baseline period without promising the target.
4. Generate a detailed rolling 7-day plan and a lighter phase/milestone outline beyond that horizon. The future stays flexible. Show what is planned versus tentative.
5. On each daily check-in and activity completion/skip, evaluate only relevant new inputs. Adapt the next 7 days, preserve completed history and record an immutable plan revision. Avoid oscillations: apply thresholds, only adapt on meaningful signals, and explain trigger and consequences.
6. Missing session: ask whether skipped, moved, or completed elsewhere when ambiguity matters. Never move missed work by default. Re-plan remaining weekly priority/recovery; safely drop low-priority work and never compress load into adjacent days to catch up.
7. Partial/harder-than-planned/extra workout: use actual values and user RPE as input, but reject impossible values and flag uncertainty. If actual workout substantially differs, reduce/replace subsequent session only when rules say so; explain why.
8. Low recovery, illness, pain, or conflicting signals: conservative fallback; allow rest or low-intensity alternatives. For severe/new/worsening pain, chest pain, fainting, breathing difficulty, fever, or other red flags, stop training recommendation and show appropriate urgent/professional-care guidance with no override button. Do not diagnose.
9. Every adjustment has structured reason codes such as `MISSED_PRIORITY_SESSION`, `HIGHER_THAN_PLANNED_EFFORT`, `LOW_RECOVERY`, `PAIN_REPORTED`, `AVAILABILITY_CHANGED`, `EVENT_CHANGED`, `DATA_CORRECTED`, `INSUFFICIENT_BASELINE`. The explanation must refer only to actual input. Show “No plan change” where thresholds were not crossed.
10. Do not compute or display Banister-derived fitness/fatigue/readiness or event performance projections as authoritative MVP metrics. Progress can show measured run distance/duration/pace, consistency and plan completion with source/confidence labels. Any simple aggregation must identify its definition.

### Nutrition and recovery

- Make check-in skippable; capture sleep, energy, soreness, stress and pain in brief labeled controls. Support manual correction and history.
- Provide general training-day nutrition guidance with Indian foods, substitutions, dietary preferences, and allergy exclusions. Prioritize regular meals, adequate fueling, hydration to conditions, and practical protein/carbohydrate sources; use ranges and confidence labels only where a defensible estimation method exists.
- MVP can produce general meal ideas and a transparent estimate, not a precision meal prescription. Avoid weight-loss prescriptions for minors or users with disclosed eating-disorder/medical concerns; route to professional guidance and omit unsafe calorie targets. Do not diagnose, treat, or recommend supplements as necessary.
- Hydration guidance should be broad and context-aware; no exact sweat replacement claims without measurement. Weather integration is not required. If unavailable, do not pretend it was considered.

## 3. Exact screens and flows

Create a coherent polished product UI; choose a calm, athletic visual system with strong contrast, readable type, clear hierarchy and restrained charts. Antigravity may choose exact colors/components, but not the information architecture or interaction requirements below. Use responsive desktop and mobile layouts, semantic HTML, labels, keyboard navigation, visible focus, screen-reader status/error announcements, and touch targets.

### Public landing and account

- Landing: concise value proposition “Prepare smarter for the event that matters to you,” explain plan/adaptation/user control, describe running-first and custom-event boundaries, CTA to create account/sign in, and a short non-clinical disclaimer.
- Account: secure sign-up/sign-in/sign-out and password recovery through a maintained auth solution. If cloud auth is unavailable in the environment, implement a secure local demo auth mode clearly limited to local use; never store plaintext passwords. Keep all data isolated by user.
- First-run empty state resumes onboarding after refresh without losing completed answers.

### Onboarding wizard

Use a short, save-as-you-go, multi-step wizard with progress, back/continue, validation, and “skip/unknown” where allowed. Explain why sensitive/recommendation-relevant fields are requested.

1. **Event:** choose Running or Custom Event; event name/type; date/time/timezone; location optional; event structure/demands; goal (finish/participate, build capacity, target); optional target with units. Past date, missing date, multi-day event, cancelled event, and short horizon must be handled explicitly.
2. **Current ability/baseline:** running experience, recent weekly volume/frequency, optional recent race/test and date, optional easy pace only if known. Offer “I don’t know” for each optional measure. Never require a maximal test.
3. **Availability:** days/week, time/day, preferred days/time, indoor/outdoor, equipment, blackout dates. Hard-check that plan can fit.
4. **Profile and safety:** minimal necessary age/age band, optional height/weight/sex, timezone/region; short safety prompt for current pain/illness/restrictions with skip where appropriate. Explain this is not diagnosis.
5. **Nutrition preferences:** dietary pattern, allergies, foods avoided, goal preference; optional. Allergy choices must be unambiguous.
6. **Review:** summary of collected facts, unknowns and their impact, editable answers, privacy summary, CTA “Create my plan.” No fabricated precision.
7. **Plan created:** show event countdown, confidence/limitations, first week overview, today’s action and why; user can edit availability/event before starting.

### Persistent app shell

Primary navigation: **Home, Plan, Train, Nutrition, Progress, Profile**. On mobile use an accessible compact nav. Event title/countdown remains visible on core pages. Recovery is prominent in Home and history/Profile, not a separate tab. Provide unified activity/check-in/nutrition history accessible from Progress.

### Home — daily command center

- Header: greeting, local day/date, event title/countdown, current phase; empty/loading/error states.
- Today card: one clear recommended action, duration/distance, effort, priority and purpose; if rest, say so. Distinguish planned from completed.
- Coach explanation: concise reason based only on the current plan and actual recent data; show low/limited confidence when inputs are sparse. Show significant “What changed?” with before/after summary and reason; do not invent rationale.
- Actions: Start workout, Log/edit activity, Mark skipped (with reason/option to replan), Check in, View plan. Prevent duplicate submissions and indicate saved status.
- Recovery mini check-in: optional sleep, energy, soreness, stress, pain flag; sensible labels and skip. If risk flag, surface the safe action clearly.
- Nutrition summary: daily general guidance and meal idea based on preferences; clearly estimated/non-clinical.
- Progress preview: one or two measured trends and data provenance; no arbitrary model readiness score.

### Plan

- Event overview, date/countdown, preparation phase, goal, baseline confidence, milestone list.
- Weekly calendar/list with planned sessions, rest days, priority, tentative/fixed marker, duration/distance range and purpose. Mobile list is primary; desktop may add calendar.
- Show current 7 days concretely and later plan as phases/milestones, not fake precise months of sessions.
- Each plan revision accessible in “Changes,” with timestamp, trigger, reason, affected sessions and old/new values. User can edit reasonable availability/session preference, but cannot override safety stop.
- Change event/goal flow previews consequences and requires explicit save; regenerate as a new plan revision. Past sessions remain intact.

### Train — execution

- Session overview and equipment/environment; warm-up, main set and cooldown in readable steps; effort target in plain language. Show pace only if supported by reliable baseline; never force it.
- Controls: Start, pause/resume timer, skip step, modify within allowed bounds, stop/finish. Timer survives accidental navigation where feasible. Do not require always-on screen.
- On finish or stop: capture actual duration/distance where relevant, perceived effort, complete/partial/stopped status, notes and pain flag; allow user to say session happened elsewhere. Planned values prefilled but visibly distinct from actual. Save once with idempotency protection.
- Stopping early is valid; ask whether due to time, fatigue, pain, other, or prefer not to say. Pain invokes safety rules.

### Nutrition

- Today’s training demand, estimated ranges if supported, meal ideas/food substitutions matching diet and allergies, hydration reminder, simple log/edit entries if logging is included.
- Provide common Indian foods across relevant regional patterns; users can set food availability/preferences. Clearly label estimates and data source. No database claim or precise nutrient composition unless food data is actually bundled/licensed and traceable.
- Nutrition profile edit, history and correction. Allergy exclusion must be applied to suggestions. Empty/offline fallback gives general guidance without inventing analysis.

### Progress and unified history

- Answer “Am I improving?” with measured trends: running frequency, distance/time/pace when present, consistency, planned-vs-completed count and user-entered benchmarks. Include period filters and empty/insufficient-data states.
- Every chart has units, time range, accessible text summary, source/confidence and correction route. Do not extrapolate projected race time in MVP.
- Unified history filters activities, performance observations, check-ins, nutrition entries and adaptation events; each entry opens detail and correction flow.

### Profile and data correction

- Profile, active event, availability, dietary/allergy preferences, privacy/settings, integrations placeholder only if clearly labeled “not connected,” export/delete account/data, and data corrections.
- Each editable record shows current value, source, captured time and confidence where relevant. Edit flow shows old/new values, reason optional, confirm, and success. Persist original plus amendment; recalculate affected future recommendations and create a plan revision when necessary. Explain historical training is not rewritten.
- Never display a wearable as connected unless actual integration and sync status exist.

## 4. API boundary guidance

Design request/response schemas and endpoint names as suitable; at minimum provide authenticated, user-scoped equivalents for:

- `GET/PATCH /api/v1/me`; profile, availability, nutrition settings.
- `GET/POST/PATCH /api/v1/events` and activate/cancel/complete actions.
- Onboarding status/save and plan generation.
- `GET /api/v1/plans/current`, plan revisions, dated session list, and plan-change history.
- `POST /api/v1/activities`; `GET/PATCH` activity and append-only correction/amendment endpoint.
- Daily check-in create/read/correct.
- Nutrition guidance and optional logged meal/hydration records.
- Progress summaries and paginated history.
- `POST /api/v1/plans/recalculate` with idempotency key and reason inputs controlled by server.
- Data export and deletion request/action.
- Health/readiness endpoint that returns no private data.

Use UUIDs, pagination, stable sorting, ISO-8601 timestamps, canonical units, explicit null/unknown semantics, server-side owner derivation, and consistent `{code, message, field_errors, request_id}` error shape. Never expose model internals or arbitrary stack traces. Add optimistic concurrency/version checks for edits and idempotency keys for retries. The API must make plan revision, adaptation explanation and provenance retrievable; frontend must not invent these.

## 5. Safety, security, privacy, data integrity

- HTTPS in deployment; secure, HTTP-only, same-site cookies or a reputable hosted auth flow; CSRF protection appropriate to chosen auth; short-lived sessions; sign-out/revocation; rate-limit login and sensitive routes. Never put secrets in the browser bundle.
- Enforce authorization in the service/database query layer, not just UI. Add automated tests proving user A cannot list, read, edit, export or delete user B data, including guessed IDs.
- Validate dates, enums, units and numeric bounds server-side; reject NaN/infinity, negative durations/distances, impossible check-in values, malformed timezone, unknown enum, excessive text, and out-of-range API payloads. Use parameterized ORM queries.
- Avoid logging access tokens, raw health notes, allergy details or unnecessary personal data. Minimize collection, document retention, provide export/delete, and ensure deletion includes dependent records/backups according to documented policy.
- Use migrations; transactionally persist an activity/check-in and related audit/revision/adaptation state. Failed adaptation must not leave a half-written plan. Preserve immutable prior plan revisions and original corrected observations.
- Avoid duplicate activity entries on network retry and conflicting edits with version checks. Handle concurrent check-in/plan recalculation deterministically.
- Safety policy is deterministic and testable. Red-flag symptoms stop exercise recommendations and show appropriate professional/urgent care language. General soreness/fatigue can result in conservative modification; no diagnosis.
- Do not claim HIPAA/GDPR/other certification or regulatory compliance. Implement good privacy hygiene without invented certification.

## 6. Failure and edge cases that must be handled

- Empty account, interrupted onboarding, refresh mid-flow, session expiration, offline/API unavailable, retry, duplicate request, malformed response.
- Unknown baseline; inconsistent units; implausible or corrected value; wrong source/confidence; sparse or nonconsecutive dates; no actual activity for several days.
- Miss one session, several sessions, or a key session; do not stack missed work. Partially complete, stop early, train outside app, add unplanned activity, or submit duplicate finish.
- Poor sleep, high stress/fatigue, soreness, illness, pain; contradictory check-ins; severe red flag; user corrects accidental pain flag.
- Event date past/near, event moved/cancelled, target changed, timezone/daylight-saving boundary, multiple events, short preparation window.
- Availability changes, travel, no equipment, heat/weather unavailable, user cannot fit generated session into time cap.
- Nutrition allergy conflict, unsupported dietary preference, unknown foods/food data, missing nutrition inputs, unsafe weight-loss request or minor.
- Empty charts/history, pagination, daylight saving, locale formatting, mobile keyboard, reduced-motion and screen-reader interaction.
- Database migration failure, disk full, transaction rollback, stale plan, concurrent correction/recalculation, dependency/provider outage.

## 7. Acceptance criteria

The MVP is complete only when the following can be demonstrated from a clean setup (local demo mode allowed if documented):

1. A new user can create/sign into an account, complete onboarding with unknown baseline answers, and see a running-first or custom-event plan without fabricated baseline values.
2. Account data is isolated. Another account cannot access it, and tests exercise guessed IDs and list endpoints.
3. Plan respects event date, weekly days and time caps; near-term sessions are detailed, distant plan is phase-based; every session has purpose, effort/intensity description and priority. Unsupported sports do not receive a running prescription silently.
4. Home says what to do today and why using actual stored inputs. Event countdown is correct in user timezone and available across core pages.
5. User can execute, pause/stop/modify within allowed bounds, record complete/partial/skipped actual activity, and see it in history/progress.
6. A meaningful difference or check-in produces an updated plan revision with a deterministic reason and visible before/after. Insignificant changes do not churn the plan. Recommendation and audit record commit atomically.
7. A missed workout is not blindly moved or stacked; demonstrate missed-one and missed-multiple cases, including intentionally dropped work and recovery preservation.
8. Unknown/missing/conflicting data yields limited confidence and a safe fallback; key numeric calculations are traceable. No unsupported readiness score or race projection appears.
9. User corrects a measurement/activity/check-in; old and new values are retained, source/time are visible, future recommendations are recalculated as appropriate, and historical plan revisions remain available.
10. Custom event setup captures explicit demands and produces clearly bounded general/manual preparation guidance; it avoids claiming a specialized algorithm. Running custom-distance goal routes to running support when appropriate.
11. Nutrition suggestions respect allergy exclusions and dietary preferences, show limitations, and do not claim clinical precision. Recovery and nutrition are not medical advice.
12. Red-flag safety input suppresses exercise recommendation, shows clear stop/professional-care guidance, and offers no safety bypass.
13. All main screens have designed loading, empty, validation, success, offline/error, and retry states. Layout works at narrow mobile and desktop widths; essential flows work with keyboard and screen reader semantics.
14. Data migration/setup, local demo seed, environment config, backup/deletion/export behavior and deployment assumptions are documented. Seed data is explicitly synthetic.
15. Automated tests cover planner invariants, edge cases, date gaps/time zones, data correction/audit, adaptation revisions, missed sessions, nutrition allergy filtering, red-flag handling, auth isolation, API validation/idempotency/transactions, and frontend critical flows/accessibility where practical.
16. Run the relevant test suites, lint/type checks and production frontend build; report exact commands and actual outcomes. Do not report tests as passing if not run. No benchmark, user-study, sports-science validation, real wearable integration, clinical review or production security certification may be claimed unless truly completed and evidenced.

## 8. Testing strategy

- **Unit:** date normalization/DST; weekly plan feasibility and caps; schedule generation; adaptation thresholds; deterministic reason codes; missed-workout non-stacking; confidence derivation; measurement validation; allergy filtering; safety stop; corrections and plan revision invariants.
- **Property/invariant:** no generated session outside availability/time cap; no negative or non-finite prescription; safety stop never yields a workout; same version+inputs yields same plan; no missed-session auto-stacking; edits retain prior values.
- **Integration/API:** migration from empty/current schema, auth and owner filtering, CRUD/correction, transaction rollback, idempotent retries, concurrent/stale update, event changes, data export/delete, pagination and timezone handling.
- **Frontend:** onboarding including unknowns, event setup, start/stop/partial logging, check-in, skipped session, correction, adaptation explanation, allergy filter, offline/error/retry and responsive/accessibility smoke checks.
- **Manual demo script:** create demo account → onboard 10K runner without baseline → inspect cautious introductory plan → log an easy run harder than expected → check in low energy → verify reasoned revision → mark next quality session missed and verify it is dropped/replanned rather than stacked → correct distance → inspect amendment and resulting plan history → review nutrition/allergy behavior → demonstrate red-flag safety stop.
- Use deterministic fixed clock and seeded synthetic data. Separate synthetic fixtures from real user data. Keep any retained Banister/GA exploratory tests isolated and do not let them imply validation.

## 9. Performance and deployment

- Keep planner synchronous if it completes quickly under bounded input. If expensive work is introduced, use a bounded background job with status; do not run unconstrained search in a request. Paginate history and index user/date queries. Avoid loading a user’s entire history for dashboard summaries.
- Provide structured logs with request IDs and privacy-safe event metadata; health/liveness checks; actionable error reporting; DB backup/restore steps; migration procedure; rollback notes.
- Local quickstart must not need paid services. Hosted deployment must clearly identify required credentials/resources and use managed secrets/database where available. Do not add paid wearable, weather, nutrition data or LLM dependencies to make core loop work.
- Avoid microservices, payments/subscriptions, elaborate recommendation ML, and third-party integrations in MVP.

## 10. Explicit non-goals

- Full production-grade support for every sport or validated sport-science prescriptions.
- Claiming medical diagnosis/treatment, injury prevention, dietitian replacement, or clinical nutrition.
- Wearable/device imports (Apple Health, Health Connect, Garmin, Fitbit, Strava), weather-aware decisions, or automatic syncing; UI placeholders must say unavailable.
- Payments, subscriptions, marketplace, social feed, coaching marketplace, or corporate teams.
- Banister/GA-based user-facing daily plan generation, exact peak timing, “optimal” taper claims, fabricated readiness/fitness/fatigue scores, or unsupported performance prediction.
- Computer vision, exercise video library, AI as authority, or open-ended chat that can override deterministic rules.
- Native iOS/Android apps; responsive web is the target.
- Claiming production readiness, validated efficacy, certified security, accuracy or user outcomes without evidence.

## 11. Implementation sequence and final handoff

Work in increments while keeping the app runnable:

1. Inspect repo/status/history/dependencies; write a brief audit decision record. Remove packaged artifacts only after confirming they are not user data or required inputs.
2. Define schema/migrations, auth/user ownership and local demo mode; prove tenant isolation.
3. Build event/profile/availability/baseline onboarding and persistence.
4. Implement deterministic running-first/custom-event plan service with unit/property tests and reason codes.
5. Implement Plan/Home, training execution and actual logging, then atomic adaptation/version history.
6. Add recovery check-in, safety rules, nutrition profile/guidance/allergy filtering, progress/history and corrections.
7. Complete responsive/accessibility/error states, security/privacy/export/delete, synthetic seed and deployment docs.
8. Run all appropriate tests, lint/type checks and build; fix failures. Inspect final diff for accidental data or secrets.

Final response must report: what was implemented; architecture and major decisions; what from PeakForge was reused/isolated/removed; exact test/build commands and results; prototype limitations and external prerequisites; how to run/demo. Link important files. Be candid if any acceptance criterion remains incomplete. Never claim the product is production-ready merely because it builds.
