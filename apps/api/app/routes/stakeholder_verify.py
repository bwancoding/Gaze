"""
Stakeholder Verification API (User-facing)
用户申请相关方认证接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import secrets

from app.core.database import get_db
from app.models.stakeholders import StakeholderVerification, UserStakeholderRole, Stakeholder
from app.models import User, Event
from app.routes.admin import verify_admin_credentials

router = APIRouter(prefix="/stakeholders", tags=["Stakeholder Verification"])

# User authentication (simplified for MVP)
security = HTTPBasic()


# ==================== Public Endpoints ====================

@router.get("/list")
async def list_stakeholders_public(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List all active stakeholders (public endpoint for application form)
    No authentication required
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


# User authentication (simplified for MVP)
security = HTTPBasic()


def get_current_user(
    credentials: Optional[HTTPBasicCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from credentials (optional)"""
    if not credentials:
        return None
    
    # Try to find user by email
    user = db.query(User).filter(User.email == credentials.username).first()
    
    if not user:
        return None
    
    # Simple password check (in production, use proper hashing)
    if not secrets.compare_digest(credentials.password, user.password_hash or ""):
        return None
    
    return user


# ==================== User Application ====================

@router.post("/apply")
async def apply_for_verification(
    stakeholder_id: str,
    event_id: Optional[str] = None,
    application_text: str = "",
    proof_type: str = "self_declaration",  # self_declaration, ip_address, email, document
    proof_data: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    User applies for stakeholder verification
    
    - **stakeholder_id**: ID of stakeholder to apply for
    - **event_id**: Optional event context
    - **application_text**: User's explanation why they qualify
    - **proof_type**: Type of proof provided
    - **proof_data**: Proof data (encrypted in production)
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Check if stakeholder exists
    stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
    if not stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    
    # Check if already verified
    existing_role = db.query(UserStakeholderRole).filter(
        UserStakeholderRole.user_id == current_user.id,
        UserStakeholderRole.stakeholder_id == stakeholder_id
    ).first()
    
    if existing_role and existing_role.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Already verified for this stakeholder"
        )
    
    # Check if already applied
    existing_app = db.query(StakeholderVerification).filter(
        StakeholderVerification.user_id == current_user.id,
        StakeholderVerification.stakeholder_id == stakeholder_id,
        StakeholderVerification.status == "pending"
    ).first()
    
    if existing_app:
        raise HTTPException(
            status_code=400,
            detail="Application already pending review"
        )
    
    # Create application
    application = StakeholderVerification(
        id=uuid.uuid4(),
        user_id=current_user.id,
        stakeholder_id=stakeholder_id,
        event_id=event_id,
        application_text=application_text,
        proof_type=proof_type,
        proof_data=proof_data,
        status="pending",
    )
    
    db.add(application)
    db.commit()
    
    return {
        "message": "Application submitted",
        "application_id": str(application.id),
        "status": "pending"
    }


@router.get("/my-applications")
async def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's verification applications"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    applications = db.query(StakeholderVerification).filter(
        StakeholderVerification.user_id == current_user.id
    ).order_by(StakeholderVerification.created_at.desc()).all()
    
    return {
        "items": [
            {
                "id": str(app.id),
                "stakeholder_id": str(app.stakeholder_id),
                "stakeholder_name": app.stakeholder.name if app.stakeholder else "Unknown",
                "event_id": str(app.event_id) if app.event_id else None,
                "application_text": app.application_text,
                "proof_type": app.proof_type,
                "status": app.status,
                "review_notes": app.review_notes,
                "created_at": app.created_at.isoformat() if app.created_at else None,
                "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None,
            }
            for app in applications
        ]
    }


@router.get("/my-roles")
async def get_my_stakeholder_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's verified stakeholder roles"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    roles = db.query(UserStakeholderRole).filter(
        UserStakeholderRole.user_id == current_user.id,
        UserStakeholderRole.is_verified == True
    ).all()
    
    return {
        "items": [
            {
                "id": str(role.id),
                "stakeholder_id": str(role.stakeholder_id),
                "stakeholder_name": role.stakeholder.name if role.stakeholder else "Unknown",
                "display_name": role.display_name,
                "badge_color": role.badge_color,
                "verified_at": role.verified_at.isoformat() if role.verified_at else None,
            }
            for role in roles
        ]
    }


# ==================== Admin Review ====================

@router.get("/admin/applications")
async def list_pending_applications(
    status_filter: str = "pending",
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """List verification applications (admin)"""
    query = db.query(StakeholderVerification)
    
    if status_filter and status_filter != "all":
        query = query.filter(StakeholderVerification.status == status_filter)
    
    applications = query.order_by(StakeholderVerification.created_at.desc()).all()
    
    return {
        "items": [
            {
                "id": str(app.id),
                "user_id": str(app.user_id),
                "user_email": app.user.email if app.user else None,
                "stakeholder_id": str(app.stakeholder_id),
                "stakeholder_name": app.stakeholder.name if app.stakeholder else "Unknown",
                "event_id": str(app.event_id) if app.event_id else None,
                "application_text": app.application_text,
                "proof_type": app.proof_type,
                "proof_data": app.proof_data,
                "status": app.status,
                "review_notes": app.review_notes,
                "created_at": app.created_at.isoformat() if app.created_at else None,
            }
            for app in applications
        ]
    }


@router.post("/admin/applications/{application_id}/approve")
async def approve_application(
    application_id: str,
    review_notes: str = "",
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Approve verification application (admin)"""
    application = db.query(StakeholderVerification).filter(
        StakeholderVerification.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application.status = "approved"
    application.reviewed_at = datetime.utcnow()
    application.review_notes = review_notes
    
    # Create user-stakeholder role
    role = UserStakeholderRole(
        id=uuid.uuid4(),
        user_id=application.user_id,
        stakeholder_id=application.stakeholder_id,
        is_verified=True,
        verified_at=datetime.utcnow(),
        display_name=application.stakeholder.name if application.stakeholder else None,
    )
    
    db.add(role)
    db.commit()
    
    return {"message": "Application approved"}


@router.post("/admin/applications/{application_id}/reject")
async def reject_application(
    application_id: str,
    review_notes: str = "",
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Reject verification application (admin)"""
    application = db.query(StakeholderVerification).filter(
        StakeholderVerification.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application.status = "rejected"
    application.reviewed_at = datetime.utcnow()
    application.review_notes = review_notes
    
    db.commit()
    
    return {"message": "Application rejected"}
