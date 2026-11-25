from fastapi.testclient import TestClient

from app.services.rate_limit import rate_limiter


def test_rate_limit_on_track_endpoint(client: TestClient) -> None:
    rate_limiter.reset()
    for _ in range(15):
        response = client.post(
            "/api/reports/track", json={"tracking_code": "CUID-AAAA-BBBB-CCCC"}
        )
        assert response.status_code in {404, 422}
    blocked = client.post(
        "/api/reports/track", json={"tracking_code": "CUID-AAAA-BBBB-CCCC"}
    )
    assert blocked.status_code == 429
    rate_limiter.reset()
