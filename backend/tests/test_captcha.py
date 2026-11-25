def test_captcha_rejected_with_turnstile_provider(
    client, monkeypatch, report_payload
) -> None:
    from app.core.config import settings
    from app.services import captcha as captcha_module

    class Rejecting:
        def verify(self, token):
            raise captcha_module.CaptchaVerificationError("Captcha inválido")

    monkeypatch.setattr(settings, "captcha_provider", "turnstile")
    monkeypatch.setattr(
        captcha_module, "get_captcha_provider", lambda config=None: Rejecting()
    )
    response = client.post("/api/reports/adultos-mayores", json=report_payload)
    assert response.status_code == 400
    assert "Captcha" in response.json()["detail"]
