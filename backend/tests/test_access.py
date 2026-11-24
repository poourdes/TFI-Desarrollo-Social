import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import Case, StaffRole, StaffUser
from app.schemas.report import ReportCreate
from app.services.access import (
    AreaAccessDenied,
    assert_area_access,
    can_access_area,
    visible_cases,
)
from app.services.areas import get_active_area, parse_area_config
from app.services.reports import create_report


def _create_user(
    db: Session, email: str, role: StaffRole, area_slugs: list[str], active: bool = True
) -> StaffUser:
    user = StaffUser(
        email=email, full_name="Usuario de prueba", role=role, active=active
    )
    user.areas = [get_active_area(db, slug) for slug in area_slugs]
    db.add(user)
    db.commit()
    return user


def _create_case(db: Session, slug: str, description: str) -> Case:
    area = get_active_area(db, slug)
    data: dict[str, str] = {
        "situation_type": parse_area_config(area).form.situation_types[0].value,
        "locality": "Aguilares",
        "description": description,
    }
    if slug == "adultos-mayores":
        data["affected_name"] = "María José Pérez"
        data["age_range"] = "range_70_79"
    payload = ReportCreate(**data)
    return create_report(db, area, parse_area_config(area), payload).report.case


def test_worker_only_sees_cases_from_assigned_areas(db_session: Session) -> None:
    adultos_case = _create_case(
        db_session, "adultos-mayores", "Denuncia de adultos mayores."
    )
    _create_case(db_session, "abuso-laboral", "Denuncia de abuso laboral.")
    worker = _create_user(
        db_session, "worker@example.com", StaffRole.social_worker, ["adultos-mayores"]
    )

    visible = visible_cases(db_session, worker)
    assert [case.id for case in visible] == [adultos_case.id]


def test_admin_sees_all_assigned_areas(db_session: Session) -> None:
    _create_case(db_session, "adultos-mayores", "Denuncia de adultos mayores.")
    _create_case(
        db_session, "ninez-adolescencia", "Denuncia sobre niñez y adolescencia."
    )
    admin = _create_user(
        db_session,
        "admin@example.com",
        StaffRole.admin,
        ["adultos-mayores", "ninez-adolescencia"],
    )
    assert len(visible_cases(db_session, admin)) == 2


def test_restricted_areas_exclude_social_worker(db_session: Session) -> None:
    _create_case(
        db_session, "ninez-adolescencia", "Denuncia sobre niñez y adolescencia."
    )
    ninez = get_active_area(db_session, "ninez-adolescencia")
    worker = _create_user(
        db_session,
        "worker@example.com",
        StaffRole.social_worker,
        ["ninez-adolescencia"],
    )
    coordinator = _create_user(
        db_session,
        "coordinator@example.com",
        StaffRole.coordinator,
        ["ninez-adolescencia"],
    )

    assert not can_access_area(worker, ninez)
    assert visible_cases(db_session, worker) == []
    with pytest.raises(AreaAccessDenied):
        assert_area_access(worker, ninez)
    assert can_access_area(coordinator, ninez)
    assert len(visible_cases(db_session, coordinator)) == 1


def test_role_values_match_the_spanish_configuration(db_session: Session) -> None:
    _create_user(
        db_session,
        "coordinator@example.com",
        StaffRole.coordinator,
        ["adultos-mayores"],
    )
    stored_role = db_session.execute(
        text("SELECT role FROM staff_users WHERE email = 'coordinator@example.com'")
    ).scalar_one()
    assert stored_role == "coordinador"


def test_inactive_user_has_no_visibility(db_session: Session) -> None:
    _create_case(db_session, "adultos-mayores", "Denuncia de adultos mayores.")
    inactive = _create_user(
        db_session,
        "inactive@example.com",
        StaffRole.admin,
        ["adultos-mayores"],
        active=False,
    )
    assert visible_cases(db_session, inactive) == []
