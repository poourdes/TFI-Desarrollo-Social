from fastapi.testclient import TestClient

TEST_PASSWORD = "TestPass123!"


def login(client: TestClient, email: str = "admin@example.com") -> None:
    response = client.post(
        "/api/auth/login", json={"email": email, "password": TEST_PASSWORD}
    )
    assert response.status_code == 200


def test_login_sets_httponly_cookie_and_me_returns_user(
    client: TestClient, admin_user: object
) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"
    assert response.json()["role"] == "admin"

    set_cookie = response.headers["set-cookie"]
    assert "cuidar_access=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie
    assert "Path=/api" in set_cookie
    assert "Secure" not in set_cookie

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["full_name"] == "Admin de prueba"


def test_login_rejects_bad_password_and_me_requires_cookie(
    client: TestClient, admin_user: object
) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "incorrecta"},
    )
    assert response.status_code == 401
    assert client.get("/api/auth/me").status_code == 401

    login(client)
    assert client.get("/api/auth/me").status_code == 200
    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_there_is_no_public_registration(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={"email": "nuevo@example.com", "password": TEST_PASSWORD},
    )
    assert response.status_code == 404
