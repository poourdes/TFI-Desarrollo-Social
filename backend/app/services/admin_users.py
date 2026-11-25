from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import AuditAction, StaffRole, StaffUser
from app.services.areas import get_active_area
from app.services.audit import record_audit


class AdminUserError(ValueError):
    pass


def list_staff_users(db: Session) -> list[StaffUser]:
    return list(db.scalars(select(StaffUser).order_by(StaffUser.email.asc())).all())


def create_staff_user(
    db: Session,
    *,
    actor_id,
    email: str,
    password: str,
    full_name: str,
    role: StaffRole,
    area_slugs: list[str],
    active: bool,
) -> StaffUser:
    normalized = email.strip().lower()
    existing = db.scalar(select(StaffUser).where(StaffUser.email == normalized))
    if existing is not None:
        raise AdminUserError("Ya existe un usuario con ese email")
    areas = [get_active_area(db, slug) for slug in area_slugs]
    user = StaffUser(
        email=normalized,
        full_name=full_name.strip(),
        role=role,
        active=active,
        password_hash=hash_password(password),
    )
    user.areas = areas
    db.add(user)
    db.flush()
    record_audit(
        db,
        action=AuditAction.staff_user_created,
        entity_type="staff_user",
        entity_id=user.id,
        actor_id=actor_id,
        details={
            "role": role.value,
            "area_slugs": sorted([area.slug for area in areas]),
            "active": active,
        },
    )
    db.commit()
    db.refresh(user)
    return user
