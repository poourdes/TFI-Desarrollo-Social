import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

_DOMAIN = b"contact:v1:"


def _derive_key(source: str) -> str:
    digest = hashlib.sha256(source.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii")


def _fernet() -> Fernet:
    key = settings.fernet_key.strip()
    if not key:
        if settings.env == "production":
            raise RuntimeError("FERNET_KEY must be configured in production")
        key = _derive_key(settings.jwt_secret_key)
    else:
        try:
            Fernet(key.encode("ascii"))
        except (ValueError, UnicodeEncodeError):
            key = _derive_key(key)
    return Fernet(key.encode("ascii"))


def encrypt_contact(value: str) -> bytes:
    fernet = _fernet()
    return fernet.encrypt(_DOMAIN + value.encode("utf-8"))


def decrypt_contact(token: bytes) -> str:
    fernet = _fernet()
    try:
        plaintext = fernet.decrypt(token)
    except InvalidToken as exc:
        raise ValueError("Invalid encrypted contact token") from exc
    if not plaintext.startswith(_DOMAIN):
        raise ValueError("Invalid encrypted contact payload")
    return plaintext[len(_DOMAIN) :].decode("utf-8")
