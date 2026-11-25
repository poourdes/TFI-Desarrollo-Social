import pytest

from app.core.config import Settings, validate_production_settings
from app.services.captcha import CaptchaVerificationError, TurnstileCaptchaProvider


def test_turnstile_rejects_missing_token() -> None:
    provider = TurnstileCaptchaProvider("secret")
    with pytest.raises(CaptchaVerificationError):
        provider.verify(None)


def test_production_guard_rejects_insecure_defaults() -> None:
    config = Settings(
        env="production",
        jwt_secret_key="change_me",
        tracking_code_pepper="change_me",
        fernet_key="",
        captcha_provider="mock",
    )
    with pytest.raises(RuntimeError) as exc:
        validate_production_settings(config)
    assert "JWT_SECRET_KEY" in str(exc.value)
    assert "TRACKING_CODE_PEPPER" in str(exc.value)
    assert "FERNET_KEY" in str(exc.value)
    assert "CAPTCHA_PROVIDER=mock" in str(exc.value)
