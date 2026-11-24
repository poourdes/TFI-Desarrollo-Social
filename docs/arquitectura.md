# Arquitectura (borrador) — Cuidar

## Visión general

Sistema web para denuncias anónimas de maltrato/abandono de adultos mayores, con:
- **Frontend público e interno** (React + TypeScript + Vite).
- **API** (FastAPI) con lógica de negocio, seguridad y auditoría.
- **Base de datos** PostgreSQL.

## Componentes (Fase 0)

- `web`: SPA React servida en desarrollo por Vite.
- `api`: servicio FastAPI, expone `/health`, los endpoints públicos `/api/areas`, `/api/reports/{area_slug}` y `/api/reports/track`, y los internos `/api/auth/*` y `/api/panel/*`.
- `db`: PostgreSQL con persistencia en volumen Docker.

## Estructura de monorepo

- `/backend`: aplicación FastAPI, migraciones Alembic, tests pytest.
- `/frontend`: aplicación React, tests Vitest.
- `/docs`: documentación técnica y funcional.

## Decisiones iniciales

- Configuración por variables de entorno (`.env`, ver `.env.example`).
- Separación estricta entre endpoints públicos (denuncias/seguimiento) e internos (panel autenticado) desde fases posteriores.
- Privacidad por diseño: sin IPs en endpoints públicos, hash de códigos y cifrado de contacto ya implementados; limpieza EXIF y endurecimiento quedan para Fase 3.

## Próximos pasos

- Fase 1 (implementada): modelo `cases`/`reports`/`case_events`, migración inicial, código de seguimiento hasheado, agrupación en casos y endpoints públicos.
- Fase 2 (implementada): auth con cookie httpOnly, panel por área, transiciones, visitas, confirmación humana de escalamientos y auditoría ampliada.
- Fase 3: endurecimiento de seguridad y privacidad (adjuntos/EXIF, RBAC fino, documentación detallada).
