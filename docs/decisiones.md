# Decisiones de diseño

## Fase 0
- **Monorepo** con `/backend`, `/frontend`, `/docs` para facilitar evolución y entrega académica.
- **FastAPI + Pydantic v2** y **React + Vite + TypeScript** según stack definido.
- **Docker Compose** con `db`, `api`, `web` y variables en `.env`.
- Interfaz y textos en español; código, identificadores y commits en inglés.
- Captcha en modo `mock` para desarrollo (integración real en Fase 3).
- CI básico con linters, typecheck y smoke tests sobre el esqueleto.

## Fase 2
- **Auth interna**: contraseñas con argon2 y JWT en cookie `httpOnly`, `SameSite=lax`, `Secure` solo en producción, `Path=/api`. Nunca en `localStorage`. No hay registro público: el admin se crea con `python -m app.seed_admin` (o variables `ADMIN_*`).
- **Panel**: endpoints bajo `/api/panel` con `Depends(get_current_user)`. `visible_cases()` y `can_access_area()` siguen siendo la única fuente de permisos por área; las transiciones salen de `workflow.transitions` del área.
- **Escalamiento**: la sugerencia existente no se aplica sola. La confirmación humana explícita agrega el evento `escalation_confirmed` y una entrada de auditoría; nunca notifica a la policía automáticamente.
- **Auditoría**: visitas, cambios de estado, confirmación de escalamiento, denegaciones de acceso y lectura de contacto usan `AuditAction`. El contacto cifrado solo se descifra en `GET /api/panel/reports/{report_id}/contact`, para roles permitidos por el área, y esa lectura también se audita.
- **Patrón**: Strategy para reglas por área (`AreaConfig` inyectado en `workflow.py`, `escalation.py`, `access.py` y `cases.py`). No se usa State por estado porque las transiciones ya son datos de configuración.

## Fase 1
- **Tres entidades**: `cases`, `reports` y `case_events`. El caso concentra denuncias; el evento es el único historial expuesto públicamente.
- **Código de seguimiento de un solo uso visible**: se muestra en claro solo en la respuesta de creación; en DB se guarda únicamente HMAC-SHA256 con `TRACKING_CODE_PEPPER` y dominio `tracking-code:v1:`.
- **Alfabeto sin ambigüedades** (`2-9`, `A-Z` sin `I`/`O`) y 12 caracteres para el código.
- **Consulta por POST con el código en el body**, nunca en query string, para evitar que quede en logs de accesos. Respuesta 404 genérica para códigos inexistentes y 422 para formatos inválidos.
- **Contacto voluntario cifrado con Fernet** desde esta fase; si `FERNET_KEY` está vacía en `development` se deriva una clave estable desde `JWT_SECRET_KEY` (en `production` es obligatoria). El cifrado de campos adicionales y la limpieza de metadatos se completan en Fase 3.
- **Agrupación conservadora** por nombre + localidad + dirección normalizados, hasheados con el mismo pepper; sin dirección o sin nombre no se agrupa. Solo se reutilizan casos abiertos/en revisión. El ajuste manual se hará en el panel interno.
- **Numeración de casos** `CASO-AAAAMM-0001` secuencial por mes; en una fase posterior puede reemplazarse por una secuencia atómica de PostgreSQL si aparece concurrencia real.
- **Sin adjuntos, auth ni auditoría de personal** en esta fase (Fases 2 y 3).
