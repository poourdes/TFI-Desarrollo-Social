from fastapi.testclient import TestClient

from app.services.rate_limit import rate_limiter


def test_login_rate_limited(client: TestClient, admin_user) -> None:
    rate_limiter.reset()
    for _ in range(10):
        response = client.post(
            "/api/auth/login", json={"email": "admin@example.com", "password": "bad"}
        )
        assert response.status_code == 401
    blocked = client.post(
        "/api/auth/login", json={"email": "admin@example.com", "password": "bad"}
    )
    assert blocked.status_code == 429
    rate_limiter.reset()
