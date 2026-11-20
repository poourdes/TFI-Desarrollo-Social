# Decisiones de diseño

## Fase 0
- **Monorepo** con `/backend`, `/frontend`, `/docs` para facilitar evolución y entrega académica.
- **FastAPI + Pydantic v2** y **React + Vite + TypeScript** según stack definido.
- **Docker Compose** con `db`, `api`, `web` y variables en `.env`.
- Interfaz y textos en español; código, identificadores y commits en inglés.
- Captcha en modo `mock` para desarrollo (integración real en Fase 3).
- CI básico con linters, typecheck y smoke tests sobre el esqueleto.

Decisiones adicionales (reglas de negocio, privacidad, modelo) se registrarán en fases siguientes.
