"""
Stakeholder Public API
相关方公开查询接口（只读）
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.stakeholders import Stakeholder

router = APIRouter(prefix="/stakeholders", tags=["Stakeholders"])


# ==================== Public Endpoints ====================

@router.get("/list")
async def list_stakeholders_public(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List all active stakeholders (public endpoint)
    
    公开端点，无需认证。用于前端申请表单显示相关方选项。
    
    - **category**: Optional filter by category (geopolitics, technology, etc.)
    """
    query = db.query(Stakeholder).filter(Stakeholder.is_active == True)
    
    if category:
        query = query.filter(Stakeholder.category == category)
    
    stakeholders = query.order_by(Stakeholder.name).all()
    
    return {
        "items": [
            {
                "id": str(s.id),
                "name": s.name,
                "description": s.description,
                "category": s.category,
                "verification_required": s.verification_required,
            }
            for s in stakeholders
        ]
    }
