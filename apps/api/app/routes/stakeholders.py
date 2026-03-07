"""
Stakeholder Management API
相关方认证系统 API 接口
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.stakeholders import (
    StakeholderType, Stakeholder, EventStakeholder,
    StakeholderVerification, UserStakeholderRole
)
from app.models import Event, User
from app.routes.admin import verify_admin_credentials

router = APIRouter(prefix="/admin/stakeholders", tags=["Stakeholder Management"])


# ==================== Stakeholder Types ====================

@router.get("/types")
async def list_stakeholder_types(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """List all stakeholder types"""
    query = db.query(StakeholderType)
    
    if category:
        query = query.filter(StakeholderType.category == category)
    
    types = query.order_by(StakeholderType.name).all()
    
    return {
        "items": [
            {
                "id": str(t.id),
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "verification_required": t.verification_required,
                "verification_method": t.verification_method,
            }
            for t in types
        ]
    }


@router.post("/types")
async def create_stakeholder_type(
    name: str,
    description: str,
    category: str,
    verification_required: bool = True,
    verification_method: str = "",
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Create new stakeholder type"""
    # Check if exists
    existing = db.query(StakeholderType).filter(StakeholderType.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Type already exists")
    
    type_obj = StakeholderType(
        id=uuid.uuid4(),
        name=name,
        description=description,
        category=category,
        verification_required=verification_required,
        verification_method=verification_method,
    )
    
    db.add(type_obj)
    db.commit()
    db.refresh(type_obj)
    
    return {"message": "Type created", "id": str(type_obj.id)}


# ==================== Stakeholders ====================

@router.get("")
async def list_stakeholders(
    category: Optional[str] = None,
    type_id: Optional[str] = None,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """List all stakeholders"""
    query = db.query(Stakeholder)
    
    if category:
        query = query.filter(Stakeholder.category == category)
    if type_id:
        query = query.filter(Stakeholder.type_id == type_id)
    
    stakeholders = query.order_by(Stakeholder.name).all()
    
    return {
        "items": [
            {
                "id": str(s.id),
                "name": s.name,
                "type_id": str(s.type_id),
                "description": s.description,
                "category": s.category,
                "verification_required": s.verification_required,
                "is_active": s.is_active,
            }
            for s in stakeholders
        ]
    }


@router.post("")
async def create_stakeholder(
    name: str,
    type_id: str,
    description: str,
    category: str,
    verification_required: bool = True,
    verification_method: str = "",
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Create new stakeholder"""
    # Check if exists
    existing = db.query(Stakeholder).filter(Stakeholder.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Stakeholder already exists")
    
    stakeholder = Stakeholder(
        id=uuid.uuid4(),
        name=name,
        type_id=type_id,
        description=description,
        category=category,
        verification_required=verification_required,
        verification_method=verification_method,
        is_active=True,
    )
    
    db.add(stakeholder)
    db.commit()
    db.refresh(stakeholder)
    
    return {"message": "Stakeholder created", "id": str(stakeholder.id)}


@router.post("/{stakeholder_id}/deactivate")
async def deactivate_stakeholder(
    stakeholder_id: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Deactivate stakeholder"""
    stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
    if not stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    
    stakeholder.is_active = False
    db.commit()
    
    return {"message": "Stakeholder deactivated"}


# ==================== Event-Stakeholder Links ====================

@router.get("/events/{event_id}")
async def get_event_stakeholders(
    event_id: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Get stakeholders for an event"""
    links = db.query(EventStakeholder).filter(EventStakeholder.event_id == event_id).all()
    
    return {
        "items": [
            {
                "id": str(link.id),
                "event_id": str(link.event_id),
                "stakeholder_id": str(link.stakeholder_id),
                "relevance_score": float(link.relevance_score) if link.relevance_score else 0,
                "status": link.status,
            }
            for link in links
        ]
    }


@router.post("/events/{event_id}/link")
async def link_event_stakeholder(
    event_id: str,
    stakeholder_id: str,
    relevance_score: float = 0.5,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Link stakeholder to event"""
    # Check if exists
    existing = db.query(EventStakeholder).filter(
        EventStakeholder.event_id == event_id,
        EventStakeholder.stakeholder_id == stakeholder_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Link already exists")
    
    link = EventStakeholder(
        id=uuid.uuid4(),
        event_id=event_id,
        stakeholder_id=stakeholder_id,
        relevance_score=relevance_score,
        status='approved',  # Auto-approve admin-created links
        approved_at=datetime.utcnow(),
    )
    
    db.add(link)
    db.commit()
    
    return {"message": "Stakeholder linked to event"}


# ==================== Verifications ====================

@router.get("/verifications")
async def list_verifications(
    status_filter: Optional[str] = "pending",
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """List verification requests"""
    query = db.query(StakeholderVerification)
    
    if status_filter and status_filter != "all":
        query = query.filter(StakeholderVerification.status == status_filter)
    
    verifications = query.order_by(StakeholderVerification.created_at.desc()).all()
    
    return {
        "items": [
            {
                "id": str(v.id),
                "user_id": str(v.user_id),
                "stakeholder_id": str(v.stakeholder_id),
                "event_id": str(v.event_id) if v.event_id else None,
                "application_text": v.application_text,
                "proof_type": v.proof_type,
                "status": v.status,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
            for v in verifications
        ]
    }


@router.post("/verifications/{verification_id}/approve")
async def approve_verification(
    verification_id: str,
    review_notes: str = "",
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Approve verification request"""
    verification = db.query(StakeholderVerification).filter(
        StakeholderVerification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    verification.status = 'approved'
    verification.reviewed_at = datetime.utcnow()
    verification.review_notes = review_notes
    
    # Create user-stakeholder role
    role = UserStakeholderRole(
        id=uuid.uuid4(),
        user_id=verification.user_id,
        stakeholder_id=verification.stakeholder_id,
        is_verified=True,
        verified_at=datetime.utcnow(),
    )
    
    db.add(role)
    db.commit()
    
    return {"message": "Verification approved"}


@router.post("/verifications/{verification_id}/reject")
async def reject_verification(
    verification_id: str,
    review_notes: str = "",
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Reject verification request"""
    verification = db.query(StakeholderVerification).filter(
        StakeholderVerification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    verification.status = 'rejected'
    verification.reviewed_at = datetime.utcnow()
    verification.review_notes = review_notes
    
    db.commit()
    
    return {"message": "Verification rejected"}
