# AGENTS.md

## Sources of truth
- Trust config, scripts, tests and `docs/modelo-datos.md` over prose; `README.md` and `docs/arquitectura.md` were updated for Fase 2 but docs still lag code between phases.
- `docs/decisiones.md` records design decisions. UI/docs are Spanish; identifiers and commits are English.

## Commands (run from each package directory)
- Backend, in CI order (Python 3.11): `ruff check .` → `black --check .` → `mypy app` → `pytest -q`.
- One backend test: `python -m pytest tests/test_reports_api.py::test_third_report_suggests_escalation_and_audits_it -q` (panel: `tests/test_panel_cases_api.py`).
- After changing models/migrations: `alembic upgrade head && alembic check` on a fresh DB. `alembic check` has caught real model/migration drift; CI does not run it.
- Create internal users with `python -m app.seed_admin --email ... --password ... --areas adultos-mayores`; no public registration exists.
- Frontend (Node 20): `npm run lint` → `npm run format:check` → `npm run typecheck` → `npm run test` → `npm run build`.
- Copy `.env.example` to root `.env` (and `frontend/.env`). Backend loads `Settings(env_file=(".env", "../.env"))`, so run backend commands from `backend/`.

## Wiring
- FastAPI entrypoint: `backend/app/main.py`; public routers (`public_areas`, `public_reports`) and internal routers (`auth`, `panel_cases`) live in `backend/app/api/routes/`. Auth is a JWT cookie read by `app/api/deps.py`; area scoping still comes from `can_access_area`/`visible_cases`.
- Alembic takes its URL from `settings.database_url`, not `alembic.ini`; SQLite migrations must use batch DDL (`render_as_batch` is enabled in `backend/alembic/env.py`).
- Tests use in-memory SQLite with `StaticPool` and call `seed_areas()` in the `db_session` fixture; no Postgres needed. Migration tests use subprocesses because `settings` is read at import time.
- `frontend/src/api.ts` is the only API client (native `fetch`, `credentials: "include"`); `App.tsx` has a minimal public form and panel view, no router or state library.

## Invariants
- Area config is the source of forms, workflow, escalation and privacy: `backend/app/schemas/area_config.py` plus seeds in `backend/app/data/areas.py`. Do not hardcode per-area rules in services. The 1-complaint = visit / 3-complaints = alert rule exists only in `adultos-mayores` config, and escalation is always a suggested event plus audit requiring human confirmation.
- Privacy: report endpoints take no `Request`, IP or fingerprint; schemas use `extra="forbid"`; the tracking code is shown once and stored hashed; voluntary contact data lives encrypted in `report_contacts`, never on `reports`. Decryption happens only in the panel contact endpoint and is audited.
- Escalation confirmation requires `{"confirm": true}`; `false` is rejected. Visits, status changes, confirmations, contact reveals and denied access all write `AuditLog`.
- Route order matters: `POST /reports/track` is declared before `POST /reports/{area_slug}` so `track` is not captured as an area slug.
- `StaffRole` persists Spanish values via `values_callable`; removing it silently writes English enum member names (`coordinator`, `social_worker`) instead of `coordinador`, `trabajador_social`.
