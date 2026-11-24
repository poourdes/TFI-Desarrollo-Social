from uuid import UUID

from sqlalchemy.orm import Session

from app.models import AuditAction, AuditLog


def record_audit(
    db: Session,
    action: AuditAction,
    entity_type: str,
    entity_id: UUID | None = None,
    actor_id: UUID | None = None,
    details: dict | None = None,
) -> AuditLog:
    entry = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor_id,
        details=details or {},
    )
    db.add(entry)
    db.flush()
    return entry
