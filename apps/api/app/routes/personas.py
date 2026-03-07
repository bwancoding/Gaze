"""
User Persona Management API
用户身份管理接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import secrets

from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.models.personas import UserPersona, EventStakeholderVerification
from app.models.stakeholders import Stakeholder
from app.models import User, Event
from app.routes.admin import verify_admin_credentials

# Request schemas
class PersonaCreate(BaseModel):
    persona_name: str
    avatar_color: Optional[str] = None

class PersonaUpdate(BaseModel):
    persona_name: Optional[str] = None
    avatar_color: Optional[str] = None

class VerificationApply(BaseModel):
    event_id: str
    stakeholder_id: str
    application_text: str = ""
    proof_type: str = "self_declaration"
    proof_data: str = ""

router = APIRouter(prefix="/personas", tags=["User Personas"])

# User authentication
security = HTTPBasic()


def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from credentials"""
    # Try to find user by email
    user = db.query(User).filter(User.email == credentials.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Simple password check (in production, use proper hashing)
    if user.password_hash and not secrets.compare_digest(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return user


# ==================== Persona Management ====================

@router.get("")
async def get_my_personas(
    include_deleted: bool = False,
    auto_create: bool = True,  # Auto-create if user has no personas
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's personas
    
    - **include_deleted**: Optionally include deleted personas (default: false)
    - **auto_create**: Auto-create a persona if user has none (default: true)
    """
    from datetime import datetime, timezone
    
    query = db.query(UserPersona).filter(
        UserPersona.user_id == current_user.id
    )
    
    # By default, filter out deleted personas
    if not include_deleted:
        query = query.filter(UserPersona.is_deleted == False)
    
    personas = query.order_by(UserPersona.created_at.desc()).all()
    
    # Auto-create a persona if user has none
    if auto_create and len(personas) == 0:
        import random
        
        # Generate recommended name
        recommended_names = [
            "在互联网冲浪的普通人",
            "吃瓜群众",
            "匿名观察者",
            "路过的网友",
            "普通市民",
        ]
        persona_name = random.choice(recommended_names)
        avatar_color = random.choice(['blue', 'green', 'purple', 'orange', 'teal'])
        
        persona = UserPersona(
            id=uuid.uuid4(),
            user_id=current_user.id,
            persona_name=persona_name,
            avatar_color=avatar_color,
            is_verified=False,
        )
        
        db.add(persona)
        db.commit()
        db.refresh(persona)
        
        personas = [persona]
    
    return {
        "items": [
            {
                "id": str(p.id),
                "persona_name": p.persona_name,
                "avatar_color": p.avatar_color,
                "is_verified": p.is_verified,
                "is_deleted": p.is_deleted,
                "deleted_at": p.deleted_at.isoformat() if p.deleted_at else None,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in personas
        ],
        "auto_created": auto_create and len(personas) == 1 and personas[0].created_at and \
                        (datetime.now(timezone.utc) - (personas[0].created_at.replace(tzinfo=timezone.utc) if personas[0].created_at.tzinfo is None else personas[0].created_at)).total_seconds() < 5
    }


@router.post("")
async def create_persona(
    request: PersonaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create new persona
    
    - **persona_name**: Name for the persona (e.g., "Iranian Civilian")
    - **avatar_color**: Optional color identifier
    """
    # Check persona limit (max 5)
    existing_count = db.query(UserPersona).filter(
        UserPersona.user_id == current_user.id
    ).count()
    
    if existing_count >= 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 personas allowed per user"
        )
    
    # Check if name already exists for this user
    existing = db.query(UserPersona).filter(
        UserPersona.user_id == current_user.id,
        UserPersona.persona_name == request.persona_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Persona name already exists"
        )
    
    # Create persona
    import random
    colors = ['blue', 'green', 'purple', 'orange', 'red', 'teal', 'indigo', 'pink']
    
    persona = UserPersona(
        id=uuid.uuid4(),
        user_id=current_user.id,
        persona_name=request.persona_name,
        avatar_color=request.avatar_color or random.choice(colors),
        is_verified=False,
    )
    
    db.add(persona)
    db.commit()
    db.refresh(persona)
    
    return {
        "message": "Persona created",
        "id": str(persona.id),
        "persona_name": persona.persona_name,
        "avatar_color": persona.avatar_color,
    }


@router.put("/{persona_id}")
async def update_persona(
    persona_id: str,
    persona_name: Optional[str] = None,
    avatar_color: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update persona details"""
    persona = db.query(UserPersona).filter(
        UserPersona.id == persona_id,
        UserPersona.user_id == current_user.id
    ).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    if persona_name:
        # Check if name already exists
        existing = db.query(UserPersona).filter(
            UserPersona.user_id == current_user.id,
            UserPersona.persona_name == persona_name,
            UserPersona.id != persona_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Persona name already exists"
            )
        
        persona.persona_name = persona_name
    
    if avatar_color:
        persona.avatar_color = avatar_color
    
    db.commit()
    
    return {"message": "Persona updated"}


@router.delete("/{persona_id}")
async def delete_persona(
    persona_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete persona (marks as deleted, keeps comments intact)"""
    from datetime import datetime
    
    persona = db.query(UserPersona).filter(
        UserPersona.id == persona_id,
        UserPersona.user_id == current_user.id,
        UserPersona.is_deleted == False  # Can't delete already deleted persona
    ).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    # Soft delete: mark as deleted instead of removing
    persona.is_deleted = True
    persona.deleted_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Persona deleted",
        "note": "Comments and verifications are preserved"
    }


# ==================== Admin Review ====================
# Note: Admin routes MUST be before dynamic routes like /{persona_id}/...
# to avoid "admin" being matched as a persona_id

@router.get("/admin/verifications")
async def list_all_verifications(
    status_filter: str = "pending",
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """List all verification applications (admin)"""
    from sqlalchemy.orm import joinedload
    
    query = db.query(EventStakeholderVerification).options(
        joinedload(EventStakeholderVerification.persona).joinedload(UserPersona.user),
        joinedload(EventStakeholderVerification.event),
        joinedload(EventStakeholderVerification.stakeholder)
    )
    
    if status_filter and status_filter != "all":
        query = query.filter(EventStakeholderVerification.status == status_filter)
    
    verifications = query.order_by(EventStakeholderVerification.created_at.desc()).all()
    
    return {
        "items": [
            {
                "id": str(v.id),
                "user_persona_id": str(v.user_persona_id),
                "persona_name": v.persona.persona_name if v.persona else "Unknown",
                "user_email": v.persona.user.email if v.persona and v.persona.user else None,
                "event_id": str(v.event_id),
                "event_title": v.event.title if v.event else "Unknown",
                "stakeholder_id": str(v.stakeholder_id),
                "stakeholder_name": v.stakeholder.name if v.stakeholder else "Unknown",
                "application_text": v.application_text,
                "proof_type": v.proof_type,
                "status": v.status,
                "review_notes": v.review_notes,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
            for v in verifications
        ]
    }


@router.post("/admin/verifications/{verification_id}/approve")
async def approve_verification(
    verification_id: str,
    review_notes: str = "",
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Approve verification application (admin)"""
    verification = db.query(EventStakeholderVerification).filter(
        EventStakeholderVerification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Application not found")
    
    verification.status = 'approved'
    verification.reviewed_at = datetime.utcnow()
    verification.review_notes = review_notes
    
    # Update persona is_verified flag
    if verification.persona:
        verification.persona.is_verified = True
    
    db.commit()
    
    return {"message": "Application approved"}


@router.post("/admin/verifications/{verification_id}/reject")
async def reject_verification(
    verification_id: str,
    review_notes: str = "",
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Reject verification application (admin)"""
    verification = db.query(EventStakeholderVerification).filter(
        EventStakeholderVerification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Application not found")
    
    verification.status = 'rejected'
    verification.reviewed_at = datetime.utcnow()
    verification.review_notes = review_notes
    
    db.commit()
    
    return {"message": "Application rejected"}


@router.post("/admin/verifications/{verification_id}/revoke")
async def revoke_verification(
    verification_id: str,
    review_notes: str = "",
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Revoke an approved verification (admin)"""
    from sqlalchemy.orm import joinedload
    
    verification = db.query(EventStakeholderVerification).options(
        joinedload(EventStakeholderVerification.persona)
    ).filter(
        EventStakeholderVerification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if verification.status != 'approved':
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot revoke {verification.status} verification. Only approved verifications can be revoked."
        )
    
    verification.status = 'revoked'
    verification.reviewed_at = datetime.utcnow()
    verification.review_notes = review_notes if review_notes else "Revoked by admin"
    
    # Update persona is_verified flag
    if verification.persona:
        # Check if there are any other approved verifications for this persona
        other_approved = db.query(EventStakeholderVerification).filter(
            EventStakeholderVerification.user_persona_id == verification.user_persona_id,
            EventStakeholderVerification.status == 'approved',
            EventStakeholderVerification.id != verification_id
        ).first()
        
        # If no other approved verifications, set is_verified to False
        if not other_approved:
            verification.persona.is_verified = False
    
    db.commit()
    
    return {"message": "Verification revoked successfully"}


@router.post("/admin/verifications/{verification_id}/revoke")
async def revoke_verification(
    verification_id: str,
    review_notes: str = "",
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Revoke an approved verification (admin)"""
    verification = db.query(EventStakeholderVerification).filter(
        EventStakeholderVerification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if verification.status != 'approved':
        raise HTTPException(status_code=400, detail="Can only revoke approved verifications")
    
    # Change status back to pending
    verification.status = 'pending'
    verification.reviewed_at = None
    verification.review_notes = review_notes
    
    # Unset persona is_verified flag
    if verification.persona:
        # Check if persona has any other approved verifications
        other_approved = db.query(EventStakeholderVerification).filter(
            EventStakeholderVerification.user_persona_id == verification.user_persona_id,
            EventStakeholderVerification.id != verification.id,
            EventStakeholderVerification.status == 'approved'
        ).count()
        
        if other_approved == 0:
            verification.persona.is_verified = False
    
    db.commit()
    
    return {"message": "Verification revoked"}


@router.post("/verifications/{verification_id}/cancel")
async def cancel_verification(
    verification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel/revoke a verification application (user)
    
    - For pending applications: cancels (deletes) the application
    - For approved applications: revokes the verification (sets status to 'revoked')
    """
    from sqlalchemy.orm import joinedload
    
    verification = db.query(EventStakeholderVerification).options(
        joinedload(EventStakeholderVerification.persona)
    ).filter(
        EventStakeholderVerification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check ownership
    if not verification.persona or verification.persona.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this application")
    
    # Handle based on status
    if verification.status == 'pending':
        # Delete pending applications
        db.delete(verification)
        db.commit()
        return {"message": "Application cancelled successfully"}
    elif verification.status == 'approved':
        # Revoke approved verifications (set to 'revoked' status)
        verification.status = 'revoked'
        verification.reviewed_at = datetime.utcnow()
        verification.review_notes = "Revoked by user"
        
        # Update persona is_verified flag if this was the only verified verification
        if verification.persona:
            # Check if there are any other approved verifications for this persona
            other_approved = db.query(EventStakeholderVerification).filter(
                EventStakeholderVerification.user_persona_id == verification.user_persona_id,
                EventStakeholderVerification.status == 'approved',
                EventStakeholderVerification.id != verification_id
            ).first()
            
            # If no other approved verifications, set is_verified to False
            if not other_approved:
                verification.persona.is_verified = False
        
        db.commit()
        return {"message": "Verification revoked successfully"}
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel {verification.status} application. Only pending or approved verifications can be cancelled."
        )


# ==================== Event-Level Verification ====================

@router.get("/{persona_id}/verifications")
async def get_persona_verifications(
    persona_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get verification applications for a persona"""
    persona = db.query(UserPersona).filter(
        UserPersona.id == persona_id,
        UserPersona.user_id == current_user.id
    ).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    verifications = db.query(EventStakeholderVerification).filter(
        EventStakeholderVerification.user_persona_id == persona_id
    ).order_by(EventStakeholderVerification.created_at.desc()).all()
    
    return {
        "items": [
            {
                "id": str(v.id),
                "event_id": str(v.event_id),
                "event_title": v.event.title if v.event else "Unknown",
                "stakeholder_id": str(v.stakeholder_id),
                "stakeholder_name": v.stakeholder.name if v.stakeholder else "Unknown",
                "application_text": v.application_text,
                "status": v.status,
                "review_notes": v.review_notes,
                "created_at": v.created_at.isoformat() if v.created_at else None,
                "reviewed_at": v.reviewed_at.isoformat() if v.reviewed_at else None,
            }
            for v in verifications
        ]
    }


@router.post("/{persona_id}/verify")
async def apply_for_verification(
    persona_id: str,
    request: VerificationApply,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Apply for stakeholder verification in a specific event
    
    - **persona_id**: ID of persona to use
    - **request.event_id**: Event to apply for
    - **request.stakeholder_id**: Stakeholder type to apply as
    - **request.application_text**: Why you qualify
    """
    # Extract from request body
    event_id = request.event_id
    stakeholder_id = request.stakeholder_id
    application_text = request.application_text
    proof_type = request.proof_type or 'self_declaration'
    proof_data = request.proof_data or ''
    # Check persona ownership
    persona = db.query(UserPersona).filter(
        UserPersona.id == persona_id,
        UserPersona.user_id == current_user.id
    ).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    # Check if already verified in this event
    existing = db.query(EventStakeholderVerification).filter(
        EventStakeholderVerification.user_persona_id == persona_id,
        EventStakeholderVerification.event_id == event_id
    ).first()
    
    if existing:
        if existing.status == 'approved':
            raise HTTPException(
                status_code=400,
                detail="Already verified for this event"
            )
        elif existing.status == 'pending':
            raise HTTPException(
                status_code=400,
                detail="Application already pending review"
            )
        elif existing.status == 'rejected':
            # Allow re-application after rejection
            pass
        else:
            raise HTTPException(
                status_code=400,
                detail="Already have an application for this event"
            )
    
    # Check stakeholder exists
    stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
    if not stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    
    # Create application
    try:
        application = EventStakeholderVerification(
            id=uuid.uuid4(),
            user_persona_id=persona_id,
            event_id=event_id,
            stakeholder_id=stakeholder_id,
            application_text=application_text,
            proof_type=proof_type,
            proof_data=proof_data,
            status='pending',
        )
        
        db.add(application)
        db.commit()
        
        return {
            "message": "Application submitted",
            "application_id": str(application.id),
            "status": "pending"
        }
    except Exception as e:
        db.rollback()
        # Check for unique constraint violation
        if 'UNIQUE constraint failed' in str(e):
            raise HTTPException(
                status_code=400,
                detail="You already have an application for this event"
            )
        raise
