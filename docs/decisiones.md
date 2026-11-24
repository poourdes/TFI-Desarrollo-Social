# Decisiones de diseño

## Fase 0
- **Monorepo** con `/backend`, `/frontend`, `/docs` para facilitar evolución y entrega académica.
- **FastAPI + Pydantic v2** y **React + Vite + TypeScript** según stack definido.
- **Docker Compose** con `db`, `api`, `web` y variables en `.env`.
- Interfaz y textos en español; código, identificadores y commits en inglés.
- Captcha en modo `mock` para desarrollo (integración real en Fase 3).
- CI básico con linters, typecheck y smoke tests sobre el esqueleto.

## Fase 1
- **Tres entidades**: `cases`, `reports` y `case_events`. El caso concentra denuncias; el evento es el único historial expuesto públicamente.
- **Código de seguimiento de un solo uso visible**: se muestra en claro solo en la respuesta de creación; en DB se guarda únicamente HMAC-SHA256 con `TRACKING_CODE_PEPPER` y dominio `tracking-code:v1:`.
- **Alfabeto sin ambigüedades** (`2-9`, `A-Z` sin `I`/`O`) y 12 caracteres para el código.
- **Consulta por POST con el código en el body**, nunca en query string, para evitar que quede en logs de accesos. Respuesta 404 genérica para códigos inexistentes y 422 para formatos inválidos.
- **Contacto voluntario cifrado con Fernet** desde esta fase; si `FERNET_KEY` está vacía en `development` se deriva una clave estable desde `JWT_SECRET_KEY` (en `production` es obligatoria). El cifrado de campos adicionales y la limpieza de metadatos se completan en Fase 3.
- **Agrupación conservadora** por nombre + localidad + dirección normalizados, hasheados con el mismo pepper; sin dirección o sin nombre no se agrupa. Solo se reutilizan casos abiertos/en revisión. El ajuste manual se hará en el panel interno.
- **Numeración de casos** `CASO-AAAAMM-0001` secuencial por mes; en una fase posterior puede reemplazarse por una secuencia atómica de PostgreSQL si aparece concurrencia real.
- **Sin adjuntos, auth ni auditoría de personal** en esta fase (Fases 2 y 3).
