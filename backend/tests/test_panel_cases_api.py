from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import AuditAction, AuditLog, Case, StaffRole, StaffUser
from app.schemas.report import ReportCreate
from app.services.areas import get_active_area, parse_area_config
from app.services.reports import create_report

TEST_PASSWORD = "TestPass123!"


def login(client: TestClient, email: str) -> None:
    response = client.post(
        "/api/auth/login", json={"email": email, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200


def create_reports(
    db: Session, slug: str, *, count: int = 1, contact: str | None = None
) -> Case:
    area = get_active_area(db, slug)
    config = parse_area_config(area)
    case: Case | None = None
    for index in range(count):
        data: dict[str, object] = {
            "situation_type": config.form.situation_types[0].value,
            "locality": "Aguilares",
            "address": "Calle Sarmiento 123",
            "description": f"Denuncia número {index + 1} con suficiente detalle.",
        }
        if slug == "adultos-mayores":
            data["affected_name"] = "María José Pérez"
            data["age_range"] = "range_70_79"
        if index == 0 and contact is not None:
            data["contact"] = contact
        case = create_report(db, area, config, ReportCreate(**data)).report.case
    assert case is not None
    return case


def audit_actions(db: Session, action: AuditAction) -> list[AuditLog]:
    return list(db.scalars(select(AuditLog).where(AuditLog.action == action)).all())


def test_panel_lists_only_assigned_areas_and_filters_by_status(
    client: TestClient,
    db_session: Session,
    admin_user: StaffUser,
    worker_user: StaffUser,
) -> None:
    adultos_case = create_reports(db_session, "adultos-mayores")
    ninez_case = create_reports(db_session, "ninez-adolescencia")

    login(client, "admin@example.com")
    response = client.get("/api/panel/cases")
    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == {
        str(adultos_case.id),
        str(ninez_case.id),
    }

    filtered = client.get("/api/panel/cases", params={"status": "open"})
    assert filtered.status_code == 200
    assert len(filtered.json()) == len(response.json())

    client.post("/api/auth/logout")
    login(client, "worker@example.com")
    worker_response = client.get("/api/panel/cases")
    assert [item["area_slug"] for item in worker_response.json()] == ["adultos-mayores"]


def test_denied_case_access_is_audited(
    client: TestClient, db_session: Session, worker_user: StaffUser
) -> None:
    case = create_reports(db_session, "ninez-adolescencia")
    login(client, "worker@example.com")

    response = client.get(f"/api/panel/cases/{case.id}")
    assert response.status_code == 403
    denials = audit_actions(db_session, AuditAction.area_access_denied)
    assert len(denials) == 1
    assert denials[0].details["area_slug"] == "ninez-adolescencia"


def test_transition_uses_area_workflow_and_is_audited(
    client: TestClient, db_session: Session, admin_user: StaffUser
) -> None:
    case = create_reports(db_session, "adultos-mayores")
    login(client, "admin@example.com")

    detail = client.get(f"/api/panel/cases/{case.id}")
    assert detail.json()["allowed_transitions"] == ["in_review", "closed"]

    response = client.post(
        f"/api/panel/cases/{case.id}/transition", json={"target": "in_review"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_review"

    invalid = client.post(
        f"/api/panel/cases/{case.id}/transition", json={"target": "in_review"}
    )
    assert invalid.status_code == 409
    assert len(audit_actions(db_session, AuditAction.case_status_changed)) == 1


def test_visit_and_escalation_confirmation_require_human_action(
    client: TestClient, db_session: Session, admin_user: StaffUser
) -> None:
    case = create_reports(db_session, "adultos-mayores", count=3)
    login(client, "admin@example.com")

    detail = client.get(f"/api/panel/cases/{case.id}").json()
    assert detail["pending_escalation"] is True
    assert any(
        event["event_type"] == "escalation_suggested" for event in detail["timeline"]
    )

    visit = client.post(
        f"/api/panel/cases/{case.id}/visit", json={"notes": "Visita acordada."}
    )
    assert visit.status_code == 200
    assert len(audit_actions(db_session, AuditAction.visit_recorded)) == 1

    unconfirmed = client.post(
        f"/api/panel/cases/{case.id}/escalation/confirm", json={"confirm": False}
    )
    assert unconfirmed.status_code == 422

    confirmed = client.post(
        f"/api/panel/cases/{case.id}/escalation/confirm", json={"confirm": True}
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["pending_escalation"] is False
    assert any(
        event["event_type"] == "escalation_confirmed"
        for event in confirmed.json()["timeline"]
    )
    assert len(audit_actions(db_session, AuditAction.escalation_confirmed)) == 1


def test_contact_decryption_is_authorized_and_audited(
    client: TestClient, db_session: Session, admin_user: StaffUser
) -> None:
    case = create_reports(db_session, "adultos-mayores", contact="contacto@example.com")
    report_id = case.reports[0].id
    login(client, "admin@example.com")

    response = client.get(f"/api/panel/reports/{report_id}/contact")
    assert response.status_code == 200
    assert response.json()["contact"] == "contacto@example.com"
    revealed = audit_actions(db_session, AuditAction.contact_revealed)
    assert len(revealed) == 1
    assert str(revealed[0].entity_id) == str(report_id)

    restricted_case = create_reports(
        db_session, "ninez-adolescencia", contact="reservado@example.com"
    )
    restricted_report = restricted_case.reports[0]
    restricted_worker = StaffUser(
        email="restricted@example.com",
        full_name="Trabajador restringido",
        role=StaffRole.social_worker,
        password_hash=hash_password(TEST_PASSWORD),
    )
    restricted_worker.areas = [get_active_area(db_session, "ninez-adolescencia")]
    db_session.add(restricted_worker)
    db_session.commit()

    client.post("/api/auth/logout")
    login(client, "restricted@example.com")
    denied = client.get(f"/api/panel/reports/{restricted_report.id}/contact")
    assert denied.status_code == 403
    assert len(audit_actions(db_session, AuditAction.area_access_denied)) == 1
