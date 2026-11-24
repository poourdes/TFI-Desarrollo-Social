from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Area, Case, StaffUser
from app.schemas.area_config import PanelAccess
from app.services.areas import parse_area_config


class AreaAccessDenied(PermissionError):
    pass


def can_access_area(user: StaffUser, area: Area) -> bool:
    if not user.active or not area.activa:
        return False
    if area.id not in {assigned.id for assigned in user.areas}:
        return False
    config = parse_area_config(area)
    if config.privacy.panel_access is PanelAccess.restricted:
        return user.role in config.privacy.allowed_roles
    return True


def assert_area_access(user: StaffUser, area: Area) -> None:
    if not can_access_area(user, area):
        raise AreaAccessDenied(f"Acceso denegado al área {area.slug}")


def visible_cases(db: Session, user: StaffUser) -> list[Case]:
    if not user.active:
        return []
    areas = {area.id: area for area in user.areas if area.activa}
    if not areas:
        return []
    cases = db.scalars(
        select(Case).where(Case.area_id.in_(areas)).order_by(Case.created_at.asc())
    ).all()
    return [case for case in cases if can_access_area(user, areas[case.area_id])]
