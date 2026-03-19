"""
Feedback API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
