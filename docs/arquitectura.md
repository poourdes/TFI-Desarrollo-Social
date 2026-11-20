# Arquitectura (borrador) — Cuidar

## Visión general

Sistema web para denuncias anónimas de maltrato/abandono de adultos mayores, con:
- **Frontend público e interno** (React + TypeScript + Vite).
- **API** (FastAPI) con lógica de negocio, seguridad y auditoría.
- **Base de datos** PostgreSQL.

## Componentes (Fase 0)

- `web`: SPA React servida en desarrollo por Vite.
- `api`: servicio FastAPI, expone `/health` y (en fases siguientes) `/api/...`.
- `db`: PostgreSQL con persistencia en volumen Docker.

## Estructura de monorepo

- `/backend`: aplicación FastAPI, migraciones Alembic, tests pytest.
- `/frontend`: aplicación React, tests Vitest.
- `/docs`: documentación técnica y funcional.

## Decisiones iniciales

- Configuración por variables de entorno (`.env`, ver `.env.example`).
- Separación estricta entre endpoints públicos (denuncias/seguimiento) e internos (panel autenticado) desde fases posteriores.
- Privacidad por diseño: se profundiza en Fase 3 (sin IPs en endpoints públicos, hash de códigos, cifrado de contacto, limpieza EXIF, etc.).

## Próximos pasos

- Fase 1: modelo de datos, migraciones y endpoints públicos núcleo.
- Fase 2: máquina de estados, umbrales, visitas y auditoría.
- Fase 3: endurecimiento de seguridad y privacidad.
