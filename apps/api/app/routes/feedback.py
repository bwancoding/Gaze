"""
Feedback API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.models.feedback import Feedback

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackCreate(BaseModel):
    type: str = "general"
    message: str
    email: Optional[str] = None


@router.post("")
def submit_feedback(data: FeedbackCreate, db: Session = Depends(get_db)):
    if not data.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")
    if data.type not in ("bug", "feature", "content", "general"):
        raise HTTPException(status_code=400, detail="Invalid feedback type")

    fb = Feedback(
        type=data.type,
        message=data.message.strip(),
        email=data.email.strip() if data.email else None,
    )
    db.add(fb)
    db.commit()
    return {"status": "ok", "message": "Feedback received. Thank you!"}


@router.get("")
def list_feedback(
    type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all feedback submissions (for admin panel)."""
    query = db.query(Feedback)
    if type:
        query = query.filter(Feedback.type == type)

    total = query.count()
    items = query.order_by(desc(Feedback.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": fb.id,
                "type": fb.type,
                "message": fb.message,
                "email": fb.email,
                "created_at": fb.created_at.isoformat() if fb.created_at else None,
            }
            for fb in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
