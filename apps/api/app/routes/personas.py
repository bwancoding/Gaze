"""
User Persona Management API
User identity management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import uuid
import json

from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user_from_header as get_current_user_from_token
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


# ==================== Persona Management ====================

@router.get("")
async def get_my_personas(
    include_deleted: bool = False,
    auto_create: bool = True,  # Auto-create if user has no personas
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
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
            "Anonymous Observer",
            "Curious Reader",
            "Global Citizen",
            "News Follower",
            "Concerned Individual",
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
    current_user: User = Depends(get_current_user_from_token),
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
    current_user: User = Depends(get_current_user_from_token),
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
    current_user: User = Depends(get_current_user_from_token),
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

    # Check if this is the last active persona
    active_count = db.query(UserPersona).filter(
        UserPersona.user_id == current_user.id,
        UserPersona.is_deleted == False
    ).count()

    if active_count <= 1:
        raise HTTPException(
            status_code=400,
            detail="You must keep at least one persona. Create a new one before deleting this."
        )

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
                "ai_review_score": v.ai_review_score,
                "ai_review_notes": v.ai_review_notes,
                "ai_flags": json.loads(v.ai_flags) if v.ai_flags else [],
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

        # Notify persona owner
        from app.models.notifications import create_notification
        stakeholder_name = verification.stakeholder.name if verification.stakeholder else "stakeholder"
        create_notification(
            db, verification.persona.user_id, "verification_approved",
            f'Your verification as "{stakeholder_name}" has been approved',
            f'/events/{verification.event_id}',
        )

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

    # Notify persona owner
    if verification.persona:
        from app.models.notifications import create_notification
        stakeholder_name = verification.stakeholder.name if verification.stakeholder else "stakeholder"
        create_notification(
            db, verification.persona.user_id, "verification_rejected",
            f'Your verification as "{stakeholder_name}" has been rejected',
            f'/profile',
        )

    db.commit()

    return {"message": "Application rejected"}


@router.post("/admin/verifications/ai-review-all")
async def batch_ai_review(
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Batch AI review all pending applications that haven't been reviewed (admin)"""
    from app.services.verification_reviewer import review_pending_applications
    count = await review_pending_applications(db)
    return {"message": f"AI reviewed {count} applications"}


@router.post("/admin/verifications/{verification_id}/ai-review")
async def ai_review_single(
    verification_id: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin_credentials),
):
    """Run or re-run AI review on a specific verification application (admin)"""
    from app.services.verification_reviewer import ai_review_application
    try:
        result = await ai_review_application(db, verification_id)
        return {"message": "AI review completed", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


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

        # Notify persona owner
        from app.models.notifications import create_notification
        stakeholder_name = verification.stakeholder.name if verification.stakeholder else "stakeholder"
        create_notification(
            db, verification.persona.user_id, "verification_revoked",
            f'Your verification as "{stakeholder_name}" has been revoked',
            f'/profile',
        )

    db.commit()
    
    return {"message": "Verification revoked successfully"}


@router.post("/verifications/{verification_id}/cancel")
async def cancel_verification(
    verification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Cancel a pending verification application (user only)
    
    Users can only cancel their own PENDING applications.
    Approved verifications can only be revoked by admins.
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
    
    # Users can ONLY cancel pending applications
    if verification.status != 'pending':
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel {verification.status} application. Users can only cancel pending applications. Approved verifications can only be revoked by admins."
        )
    
    # Delete the pending application
    db.delete(verification)
    db.commit()
    
    return {"message": "Application cancelled successfully"}


# ==================== Event-Level Verification ====================

@router.get("/{persona_id}/verifications")
async def get_persona_verifications(
    persona_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Get verification applications for a persona"""
    persona = db.query(UserPersona).filter(
        UserPersona.id == persona_id,
        UserPersona.user_id == current_user.id
    ).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    verifications = db.query(EventStakeholderVerification).options(
        joinedload(EventStakeholderVerification.event),
        joinedload(EventStakeholderVerification.stakeholder),
    ).filter(
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
    current_user: User = Depends(get_current_user_from_token),
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

        # Trigger AI review in background (non-blocking, best-effort)
        ai_result = None
        try:
            from app.services.verification_reviewer import ai_review_application
            ai_result = await ai_review_application(db, str(application.id))
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"AI review failed: {e}")

        return {
            "message": "Application submitted",
            "application_id": str(application.id),
            "status": "pending",
            "ai_review": ai_result,
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
