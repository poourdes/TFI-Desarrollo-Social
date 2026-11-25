from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditAction, AuditLog

TEST_PASSWORD = "TestPass123!"


def login(client: TestClient, email: str) -> None:
    response = client.post(
        "/api/auth/login", json={"email": email, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200


def test_admin_can_create_user_and_worker_cannot(
    client: TestClient, admin_user, worker_user, db_session: Session
) -> None:
    login(client, "admin@example.com")
    payload = {
        "email": "nuevo@example.com",
        "password": "StrongPass123!",
        "full_name": "Nuevo Usuario",
        "role": "trabajador_social",
        "area_slugs": ["adultos-mayores"],
        "active": True,
    }
    response = client.post("/api/panel/admin/users", json=payload)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["email"] == "nuevo@example.com"
    assert body["role"] == "trabajador_social"
    assert [area["slug"] for area in body["areas"]] == ["adultos-mayores"]

    audits = db_session.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.staff_user_created)
    ).all()
    assert len(audits) == 1

    client.post("/api/auth/logout")
    login(client, "worker@example.com")
    forbidden = client.post(
        "/api/panel/admin/users", json=payload | {"email": "otro@example.com"}
    )
    assert forbidden.status_code == 403
