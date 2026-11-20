# Cuidar (nombre provisorio)

Plataforma web para **denuncias anónimas** de situaciones de negligencia, abuso o abandono de **adultos mayores**, destinada a una oficina municipal (contexto: Municipalidad de Aguilares, Tucumán, Argentina).

> Trabajo Final Integrador (TFI). Estado: **Fase 0 — Fundamentos**.

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
   En `frontend\.env` asegurar `VITE_API_BASE_URL=http://localhost:8000`.

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

> Nota: en esta fase no hay migraciones de dominio ni datos de seed; los comandos `alembic upgrade head` y `python -m app.seed` se ejecutan correctamente y quedarán operativos al agregarse modelos/datos en fases siguientes.

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

## Usuarios de prueba

Se definirán en fases posteriores (seed).

## Documentación

- `/docs/arquitectura.md`
- `/docs/modelo-datos.md` (Fase 1)
- `/docs/privacidad-y-seguridad.md` (Fase 3)
- `/docs/manual-usuario.md` (Fase 7)
- `/docs/decisiones.md`
