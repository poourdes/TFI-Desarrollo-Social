import hashlib
import hmac
import re
import unicodedata
from uuid import UUID

from app.core.config import settings

_DOMAIN = b"grouping:v2:"


def normalize_grouping_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.strip().lower())
    without_accents = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", " ", without_accents).strip()


def build_grouping_key(
    area_id: UUID,
    locality: str,
    address: str | None,
    affected_name: str | None = None,
) -> str | None:
    if not address:
        return None
    parts = [
        str(area_id),
        normalize_grouping_text(locality),
        normalize_grouping_text(address),
    ]
    if affected_name:
        parts.append(normalize_grouping_text(affected_name))
    if not all(parts):
        return None
    key = settings.tracking_code_pepper.encode("utf-8")
    message = _DOMAIN + "|".join(parts).encode("utf-8")
    return hmac.new(key, message, hashlib.sha256).hexdigest()
