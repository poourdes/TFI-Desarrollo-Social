from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import StaffRole, StaffUser
from app.services.areas import get_active_area


def seed_admin_user(
    db: Session,
    *,
    email: str,
    password: str,
    full_name: str,
    area_slugs: list[str],
) -> StaffUser:
    normalized = email.strip().lower()
    user = db.scalar(select(StaffUser).where(StaffUser.email == normalized))
    if user is None:
        user = StaffUser(
            email=normalized,
            full_name=full_name,
            role=StaffRole.admin,
            active=True,
            password_hash=hash_password(password),
        )
        db.add(user)
    else:
        user.full_name = full_name
        user.role = StaffRole.admin
        user.active = True
        if user.password_hash is None:
            user.password_hash = hash_password(password)

    user.areas = [get_active_area(db, slug) for slug in area_slugs]
    db.commit()
    db.refresh(user)
    return user
