"""
Analytics Routes - Page view tracking endpoint
"""

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.limiter import limiter

router = APIRouter()


class PageViewEvent(BaseModel):
    path: str
    referrer: Optional[str] = None
    screen_width: Optional[int] = None


@router.post("/analytics/pageview", status_code=204)
@limiter.limit("60/minute")
async def track_page_view(
    request: Request,
    event: PageViewEvent,
    db: Session = Depends(get_db),
):
    """Track a frontend page view. Public endpoint, rate-limited."""
    from app.models.page_view import PageView

    # Extract real IP from headers
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if not client_ip and request.client:
        client_ip = request.client.host

    # Extract user_id from JWT if present (best-effort)
    user_id = None
    try:
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            import json, base64
            payload = auth[7:].split(".")[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += "=" * padding
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            user_id = decoded.get("sub") or decoded.get("user_id")
    except Exception:
        pass

    pv = PageView(
        path=event.path[:500],
        referrer=(event.referrer or "")[:1000] or None,
        user_agent=(request.headers.get("user-agent") or "")[:500],
        client_ip=client_ip,
        screen_width=event.screen_width,
        user_id=user_id,
    )
    db.add(pv)
    db.commit()

    return None
