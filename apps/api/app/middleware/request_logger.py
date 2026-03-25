"""
Request Logger Middleware
Logs all API requests to the database for monitoring and analytics
"""

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

# Paths to skip logging (noise reduction)
SKIP_PATHS = {"/health", "/", "/docs", "/openapi.json", "/redoc", "/favicon.ico"}
SKIP_PREFIXES = ("/uploads/", "/_next/", "/static/")

SLOW_THRESHOLD_MS = 2000


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip noisy paths
        if path in SKIP_PATHS or any(path.startswith(p) for p in SKIP_PREFIXES):
            return await call_next(request)

        start = time.perf_counter()
        status_code = 500
        error_detail = None

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as e:
            error_detail = str(e)
            raise
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)
            is_slow = duration_ms > SLOW_THRESHOLD_MS

            # Extract user_id from JWT (best-effort, no validation)
            user_id = self._extract_user_id(request)

            # Extract client IP
            client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            if not client_ip and request.client:
                client_ip = request.client.host

            # Log slow requests
            if is_slow:
                logger.warning(f"SLOW REQUEST: {request.method} {path} took {duration_ms}ms")

            # Write to database (fire-and-forget)
            try:
                self._save_log(
                    method=request.method,
                    path=path,
                    status_code=status_code,
                    duration_ms=duration_ms,
                    client_ip=client_ip,
                    user_agent=(request.headers.get("user-agent") or "")[:500],
                    is_slow=is_slow,
                    user_id=user_id,
                    error_detail=error_detail,
                )
            except Exception as log_err:
                logger.debug(f"Failed to save request log: {log_err}")

    def _extract_user_id(self, request: Request) -> str | None:
        """Best-effort JWT user_id extraction without validation."""
        try:
            auth = request.headers.get("authorization", "")
            if not auth.startswith("Bearer "):
                return None
            import json
            import base64
            token = auth[7:]
            payload = token.split(".")[1]
            # Add padding
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += "=" * padding
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            return decoded.get("sub") or decoded.get("user_id")
        except Exception:
            return None

    def _save_log(self, **kwargs):
        """Save request log to database."""
        from app.models.request_log import RequestLog
        db = SessionLocal()
        try:
            log = RequestLog(**kwargs)
            db.add(log)
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
