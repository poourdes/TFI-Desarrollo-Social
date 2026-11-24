import re

from fastapi.testclient import TestClient
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.data.areas import area_id_for
from app.models import (
    AuditAction,
    AuditLog,
    Case,
    CaseEventType,
    Report,
    ReportContact,
    ReportStatus,
)
from app.services.contact import decrypt_contact
from app.services.tracking_code import (
    TRACKING_CODE_RE,
    generate_tracking_code,
    hash_tracking_code,
)

ADULTOS = "adultos-mayores"


def _create_report(
    client: TestClient, payload: dict[str, object], area_slug: str = ADULTOS
) -> dict[str, object]:
    response = client.post(f"/api/reports/{area_slug}", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_report_returns_code_and_stores_only_hash(
    client: TestClient, db_session: Session, report_payload: dict[str, object]
) -> None:
    body = _create_report(client, report_payload)
    tracking_code = str(body["tracking_code"])

    assert TRACKING_CODE_RE.fullmatch(tracking_code)
    assert re.fullmatch(r"CASO-\d{6}-\d{4}", str(body["case_number"]))
    assert body["status"] == ReportStatus.received.value
    assert body["area_slug"] == ADULTOS

    report = db_session.scalar(
        select(Report).where(
            Report.tracking_code_hash == hash_tracking_code(tracking_code)
        )
    )
    assert report is not None
    assert report.tracking_code_hash != tracking_code
    assert tracking_code not in report.description
    assert report.case.case_number == body["case_number"]
    assert report.case.area.id == area_id_for(ADULTOS)
    assert {event.event_type for event in report.case.events} == {
        CaseEventType.report_received,
        CaseEventType.visit_due,
    }


def test_create_report_validates_payload(
    client: TestClient, report_payload: dict[str, object]
) -> None:
    invalid_values = {
        "description": "muy corto",
        "affected_name": "",
        "situation_type": "desconocida",
        "incident_date": "2099-01-01",
        "age_range": "range_0_5",
    }
    for field, value in invalid_values.items():
        payload = dict(report_payload)
        payload[field] = value
        response = client.post(f"/api/reports/{ADULTOS}", json=payload)
        assert response.status_code == 422, field


def test_create_report_rejects_tracking_and_identification_fields(
    client: TestClient, report_payload: dict[str, object]
) -> None:
    for field, value in {
        "ip": "192.0.2.10",
        "fingerprint": "abc123",
        "user_agent": "Mozilla/5.0",
        "gender_identity": "no_binario",
    }.items():
        payload = dict(report_payload)
        payload[field] = value
        response = client.post(f"/api/reports/{ADULTOS}", json=payload)
        assert response.status_code == 422, field


def test_unknown_area_returns_404(
    client: TestClient, report_payload: dict[str, object]
) -> None:
    response = client.post("/api/reports/area-inexistente", json=report_payload)
    assert response.status_code == 404


def test_contact_is_encrypted_in_separate_table(
    client: TestClient, db_session: Session, report_payload: dict[str, object]
) -> None:
    payload = dict(report_payload)
    payload["contact"] = "381 555 1234"
    _create_report(client, payload)

    report = db_session.scalar(select(Report))
    assert report is not None
    assert report.contact is not None
    assert b"381 555 1234" not in report.contact.contact_encrypted
    assert decrypt_contact(bytes(report.contact.contact_encrypted)) == "381 555 1234"
    assert "contact_encrypted" not in {
        column["name"] for column in inspect(db_session.bind).get_columns("reports")
    }
    assert db_session.scalar(select(ReportContact)) is not None


def test_contact_is_optional(
    client: TestClient, db_session: Session, report_payload: dict[str, object]
) -> None:
    _create_report(client, report_payload)
    report = db_session.scalar(select(Report))
    assert report is not None
    assert report.contact is None


def test_reports_about_same_address_are_grouped_in_one_case(
    client: TestClient, db_session: Session, report_payload: dict[str, object]
) -> None:
    first = _create_report(client, report_payload)
    second_payload = dict(report_payload)
    second_payload["description"] = "Otra denuncia sobre la misma situación."
    second = _create_report(client, second_payload)

    assert first["case_number"] == second["case_number"]
    assert second["status"] == ReportStatus.linked.value

    reports = db_session.scalars(select(Report)).all()
    assert len(reports) == 2
    assert all(report.case.case_number == first["case_number"] for report in reports)
    assert reports[0].grouping_key_hash == reports[1].grouping_key_hash
    case = db_session.scalar(select(Case))
    assert case is not None
    assert CaseEventType.report_linked in {event.event_type for event in case.events}


def test_grouping_is_address_normalized_and_area_scoped(
    client: TestClient, db_session: Session, report_payload: dict[str, object]
) -> None:
    first_payload = dict(report_payload)
    first_payload["address"] = "  Calle SARMiento 123  "
    first_payload["description"] = " Primera denuncia sobre la misma situación."
    first = _create_report(client, first_payload)

    second_payload = dict(report_payload)
    second_payload["address"] = "calle sarmiento 123"
    second_payload["description"] = "Segunda denuncia sobre la misma situación."
    second = _create_report(client, second_payload)
    assert first["case_number"] == second["case_number"]

    other_area_payload = {
        "situation_type": "physical",
        "locality": report_payload["locality"],
        "address": "Calle Sarmiento 123",
        "description": (
            "Denuncia del área de violencia de género sobre el mismo domicilio."
        ),
    }
    other = _create_report(client, other_area_payload, "violencia-de-genero")
    assert other["case_number"] != first["case_number"]
    assert len(db_session.scalars(select(Case)).all()) == 2


def test_reports_about_different_people_create_different_cases(
    client: TestClient, report_payload: dict[str, object]
) -> None:
    first = _create_report(client, report_payload)
    second_payload = dict(report_payload)
    second_payload["affected_name"] = "Ana María González"
    second = _create_report(client, second_payload)
    assert first["case_number"] != second["case_number"]


def test_reports_without_address_are_not_grouped(
    client: TestClient, db_session: Session, report_payload: dict[str, object]
) -> None:
    payload = dict(report_payload)
    payload.pop("address")
    first = _create_report(client, payload)
    second = _create_report(client, payload)
    assert first["case_number"] != second["case_number"]
    reports = db_session.scalars(select(Report)).all()
    assert all(report.grouping_key_hash is None for report in reports)


def test_tracking_lookup_returns_public_status_only(
    client: TestClient, report_payload: dict[str, object]
) -> None:
    created = _create_report(client, report_payload)
    code = str(created["tracking_code"])

    response = client.post("/api/reports/track", json={"tracking_code": code.lower()})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["case_number"] == created["case_number"]
    assert body["case_status"] == "open"
    assert body["timeline"][0]["message"] == "Denuncia recibida."
    assert "affected_name" not in body
    assert "description" not in body
    assert "contact" not in body
    assert code not in response.text


def test_third_report_suggests_escalation_and_audits_it(
    client: TestClient, db_session: Session, report_payload: dict[str, object]
) -> None:
    first = _create_report(client, report_payload)
    for index in range(2):
        payload = dict(report_payload)
        payload["description"] = (
            f"Denuncia número {index + 2} sobre la misma situación."
        )
        _create_report(client, payload)

    case = db_session.scalar(select(Case))
    assert case is not None
    assert case.case_number == first["case_number"]
    assert case.status.value == "open"
    event_types = [event.event_type for event in case.events]
    assert event_types.count(CaseEventType.visit_due) == 1
    assert event_types.count(CaseEventType.escalation_suggested) == 1

    suggestions = db_session.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.escalation_suggested)
    ).all()
    assert len(suggestions) == 2
    assert {item.details["report_count"] for item in suggestions} == {1, 3}
    assert all(
        item.details["requires_human_confirmation"] is True for item in suggestions
    )


def test_tracking_lookup_with_unknown_code_returns_generic_404(
    client: TestClient,
) -> None:
    code = generate_tracking_code()
    response = client.post("/api/reports/track", json={"tracking_code": code})
    assert response.status_code == 404
    assert response.json()["detail"] == "No se encontró una denuncia con ese código."
    assert code not in response.text


def test_tracking_lookup_with_invalid_format_returns_422(client: TestClient) -> None:
    response = client.post("/api/reports/track", json={"tracking_code": "INVALIDO"})
    assert response.status_code == 422
