import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

CONTACT_DOMAIN = b"contact:v1:"


def _derive_key(source: str) -> str:
    digest = hashlib.sha256(source.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii")


def get_fernet(configured_key: str | None = None) -> Fernet:
    key = (
        configured_key if configured_key is not None else settings.fernet_key
    ).strip()
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


def encrypt_contact(value: str, domain: bytes = CONTACT_DOMAIN) -> bytes:
    fernet = get_fernet()
    return fernet.encrypt(domain + value.encode("utf-8"))


def decrypt_contact(token: bytes, domain: bytes = CONTACT_DOMAIN) -> str:
    fernet = get_fernet()
    try:
        plaintext = fernet.decrypt(token)
    except InvalidToken as exc:
        raise ValueError("Invalid encrypted token") from exc
    if not plaintext.startswith(domain):
        raise ValueError("Invalid encrypted payload")
    return plaintext[len(domain) :].decode("utf-8")
