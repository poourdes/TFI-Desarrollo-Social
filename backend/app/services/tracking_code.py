import hashlib
import hmac
import re
import secrets

from app.core.config import settings

_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
TRACKING_CODE_PATTERN = (
    rf"CUID-[{_ALPHABET}]{{4}}-[{_ALPHABET}]{{4}}-[{_ALPHABET}]{{4}}"
)
TRACKING_CODE_RE = re.compile(rf"^{TRACKING_CODE_PATTERN}$")
_HASH_DOMAIN = b"tracking-code:v1:"


def normalize_tracking_code(code: str) -> str:
    return code.strip().upper()


def is_valid_tracking_code(code: str) -> bool:
    return TRACKING_CODE_RE.fullmatch(normalize_tracking_code(code)) is not None


def generate_tracking_code() -> str:
    groups = ["".join(secrets.choice(_ALPHABET) for _ in range(4)) for _ in range(3)]
    return f"CUID-{'-'.join(groups)}"


def hash_tracking_code(code: str) -> str:
    normalized = normalize_tracking_code(code)
    key = settings.tracking_code_pepper.encode("utf-8")
    message = _HASH_DOMAIN + normalized.encode("utf-8")
    return hmac.new(key, message, hashlib.sha256).hexdigest()
