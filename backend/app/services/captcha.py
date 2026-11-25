from dataclasses import dataclass

import httpx

from app.core.config import Settings, settings


class CaptchaVerificationError(ValueError):
    pass


@dataclass(frozen=True)
class CaptchaProvider:
    def verify(self, token: str | None) -> None:
        raise NotImplementedError


class MockCaptchaProvider(CaptchaProvider):
    def verify(self, token: str | None) -> None:
        if token is None or not token.strip():
            return


class TurnstileCaptchaProvider(CaptchaProvider):
    verify_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

    def __init__(self, secret_key: str) -> None:
        self.secret_key = secret_key

    def verify(self, token: str | None) -> None:
        if not self.secret_key.strip():
            raise CaptchaVerificationError("Captcha no configurado")
        if token is None or not token.strip():
            raise CaptchaVerificationError("Captcha requerido")
        try:
            response = httpx.post(
                self.verify_url,
                data={"secret": self.secret_key, "response": token},
                timeout=5.0,
            )
            response.raise_for_status()
            body = response.json()
        except Exception as exc:  # noqa: BLE001
            raise CaptchaVerificationError("No se pudo verificar el captcha") from exc
        if not bool(body.get("success")):
            raise CaptchaVerificationError("Captcha inválido")


def get_captcha_provider(config: Settings | None = None) -> CaptchaProvider:
    current = config or settings
    provider = current.captcha_provider.strip().lower()
    if provider == "turnstile":
        return TurnstileCaptchaProvider(current.turnstile_secret_key)
    return MockCaptchaProvider()
