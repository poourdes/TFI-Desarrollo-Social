# Cuidar (nombre provisorio)

Plataforma web para **denuncias anónimas** de situaciones de negligencia, abuso o abandono de **adultos mayores**, destinada a una oficina municipal (contexto: Municipalidad de Aguilares, Tucumán, Argentina).

> Trabajo Final Integrador (TFI). Estado: **Fase 2 — Panel interno, auth y auditoría**.

## Principios

- **Anonimato real**: sin datos identificatorios del denunciante salvo aporte voluntario.
- **Verificación humana**: ninguna acción grave se ejecuta automáticamente.
- **Sobriedad y claridad**: interfaz accesible para un tema sensible.
- **Trazabilidad interna**: acciones del personal auditadas.

## Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2
- **Base de datos:** PostgreSQL (SQLite solo en tests)
- **Frontend:** React + TypeScript + Vite, React Router, TanStack Query, React Hook Form + Zod, Tailwind CSS
- **Auth:** JWT (access + refresh), contraseñas con argon2
- **Tests:** pytest (backend), Vitest + Testing Library (frontend)
- **Infra:** Docker Compose (`api`, `db`, `web`)

## Estructura

```text
/backend   (app/, tests/, alembic/)
/frontend  (src/)
/docs      (arquitectura, modelo de datos, privacidad, manual, decisiones)
docker-compose.yml
README.md
```

## Requisitos

- Docker y Docker Compose
- (Opcional, desarrollo local) Python 3.11+ y Node.js 20+

## Inicio rápido (Docker)

1. Copiar variables de entorno:
   ```bash
   cp .env.example .env
   ```
   En Windows PowerShell: `Copy-Item .env.example .env`
2. Levantar servicios:
   ```bash
   docker compose up --build
   ```
   El servicio `api` aplica las migraciones Alembic antes de arrancar.
3. Servicios:
   - API: http://localhost:8000 (health: `GET /health`)
   - Web: http://localhost:5173
   - DB: PostgreSQL en `localhost:5432`

## Desarrollo local (sin Docker, Windows)

1. Crear archivos de entorno (SQLite por defecto):
   ```powershell
   Copy-Item .env.example .env
   Copy-Item .env.example frontend\.env
   ```
   En `.env` (raíz, usado por backend) dejar `DATABASE_URL=sqlite:///./cuidar.db`.
   En `frontend\.env` asegurar `VITE_API_BASE_URL=http://localhost:8000`. Para crear el admin: `python -m app.seed_admin --email admin@example.com --password <clave> --areas adultos-mayores` (o usar `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_AREAS`).

2. Backend (PowerShell):
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt -r requirements-dev.txt
   alembic upgrade head
   python -m app.seed
   uvicorn app.main:app --reload
   ```
   API: http://localhost:8000 (health: `GET /health`)

3. Frontend (otra terminal PowerShell):
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
   Web: http://localhost:5173

> `alembic upgrade head` crea todas las tablas, incluidas `areas`, `staff_users` y `audit_logs`. `python -m app.seed` carga las cinco áreas; `python -m app.seed_admin` crea el usuario interno.

## Comandos útiles

- Backend lint/formato/tipos/tests:
  ```bash
  cd backend
  ruff check .
  black --check .
  mypy app
  pytest -q
  ```
- Frontend lint/formato/tipos/tests:
  ```bash
  cd frontend
  npm run lint
  npm run format:check
  npm run typecheck
  npm run test
  ```

## Endpoints

Públicos:
- `GET /api/areas`: áreas activas, campos del formulario y líneas de emergencia.
- `POST /api/reports/{area_slug}`: crea una denuncia para un área y devuelve `tracking_code`, `case_number`, `status` y `created_at`. Guardar el código: se muestra una sola vez.
- `POST /api/reports/track`: con `{"tracking_code": "CUID-XXXX-XXXX-XXXX"}` en el body, devuelve el número de caso, su estado y un timeline público sin datos personales.

Internos (requieren cookie de sesión):
- `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout`.
- `GET /api/panel/cases`, `GET /api/panel/cases/{id}`, `POST /api/panel/cases/{id}/transition`, `POST /api/panel/cases/{id}/visit`, `POST /api/panel/cases/{id}/escalation/confirm`, `GET /api/panel/reports/{id}/contact`.

```bash
curl -X POST http://localhost:8000/api/reports/adultos-mayores \
  -H "Content-Type: application/json" \
  -d '{"situation_type":"neglect","affected_name":"María Pérez","age_range":"range_70_79","locality":"Aguilares","address":"Calle 1","description":"Relato de la situación observada."}'
```

Detalles del modelo, reglas de agrupación y panel: `/docs/modelo-datos.md`.

## Usuarios de prueba

No hay registro público. Crear uno con `python -m app.seed_admin --email admin@example.com --password <clave> --areas adultos-mayores`.

## Documentación

- `/docs/arquitectura.md`
- `/docs/modelo-datos.md` (Fase 1 multi-área + Fase 2 panel)
- `/docs/privacidad-y-seguridad.md` (Fase 3)
- `/docs/manual-usuario.md` (Fase 7)
- `/docs/decisiones.md`
