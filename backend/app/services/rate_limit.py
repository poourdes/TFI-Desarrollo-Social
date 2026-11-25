import base64
import hashlib
import hmac
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from app.core.config import settings


class RateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            bucket = self._hits[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Demasiadas solicitudes. Intente nuevamente más tarde.",
                )
            bucket.append(now)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


rate_limiter = RateLimiter()


def _client_fingerprint(request: Request) -> str:
    host = request.client.host if request.client else "unknown"
    pepper = settings.tracking_code_pepper.encode("utf-8")
    digest = hmac.new(pepper, host.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest[:18]).decode("ascii")


def enforce_rate_limit(
    request: Request, scope: str, limit: int, window_seconds: int
) -> None:
    rate_limiter.check(f"{scope}:{_client_fingerprint(request)}", limit, window_seconds)
