from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CaseEventType, Report
from app.services.areas import get_active_area


def test_public_areas_expose_form_emergency_lines_and_notice(
    client: TestClient,
) -> None:
    response = client.get("/api/areas")
    assert response.status_code == 200, response.text
    body = response.json()

    assert len(body["areas"]) == 5
    assert {line["numero"] for line in body["emergency_lines"]} == {"911", "144", "102"}
    assert "no es para emergencias" in body["notice"]

    ninez = next(area for area in body["areas"] if area["slug"] == "ninez-adolescencia")
    fields = {field["key"] for field in ninez["form"]["fields"]}
    assert "affected_name" not in fields
    assert "affected_initials" in fields
    assert "escalation" not in ninez


def test_base_form_works_for_every_area(
    client: TestClient, report_payload: dict[str, object]
) -> None:
    payloads = {
        "adultos-mayores": report_payload,
        "violencia-de-genero": {
            "situation_type": "physical",
            "locality": "Aguilares",
            "description": (
                "Se informa una situación de violencia física en el domicilio."
            ),
        },
        "ninez-adolescencia": {
            "situation_type": "mistreatment",
            "locality": "Aguilares",
            "description": "Se informa una situación de maltrato con datos mínimos.",
        },
        "diversidad-genero": {
            "situation_type": "discrimination",
            "locality": "Aguilares",
            "description": "Se informa una situación de discriminación en el barrio.",
        },
        "abuso-laboral": {
            "situation_type": "harassment",
            "locality": "Aguilares",
            "description": "Se informa una situación de acoso en el lugar de trabajo.",
        },
    }
    for slug, payload in payloads.items():
        response = client.post(f"/api/reports/{slug}", json=payload)
        assert response.status_code == 201, (slug, response.text)
        assert response.json()["area_slug"] == slug


def test_reinforced_areas_reject_unnecessary_data(
    client: TestClient, report_payload: dict[str, object]
) -> None:
    ninez_payload = {
        "situation_type": "mistreatment",
        "locality": "Aguilares",
        "description": "Se informa una situación de maltrato con datos mínimos.",
        "affected_name": "María Pérez",
    }
    response = client.post("/api/reports/ninez-adolescencia", json=ninez_payload)
    assert response.status_code == 422

    diversity_payload = dict(report_payload)
    diversity_payload["gender_identity_of_third_party"] = "no_binario"
    response = client.post("/api/reports/diversidad-genero", json=diversity_payload)
    assert response.status_code == 422


def test_areas_without_escalation_do_not_emit_suggestions(
    client: TestClient, db_session: Session
) -> None:
    response = client.post(
        "/api/reports/abuso-laboral",
        json={
            "situation_type": "harassment",
            "locality": "Aguilares",
            "description": "Se informa una situación de acoso en el lugar de trabajo.",
        },
    )
    assert response.status_code == 201, response.text
    report = db_session.scalar(select(Report))
    assert report is not None
    assert {event.event_type for event in report.case.events} == {
        CaseEventType.report_received
    }


def test_inactive_area_is_not_available(
    client: TestClient, db_session: Session, report_payload: dict[str, object]
) -> None:
    area = get_active_area(db_session, "abuso-laboral")
    area.activa = False
    db_session.commit()
    response = client.post("/api/reports/abuso-laboral", json=report_payload)
    assert response.status_code == 404
