"""
User Persona Management API
User identity management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, UploadFile, File
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import uuid
import json
import os

from pydantic import BaseModel

from app.core.database import get_db
from app.core.limiter import limiter
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

class ReviewNotes(BaseModel):
    review_notes: str = ""

class VerificationApply(BaseModel):
    event_id: str
    stakeholder_id: str
    application_text: str = ""
    proof_type: str = "self_declaration"
    proof_data: str = ""
    proof_files: List[str] = []  # List of uploaded file URLs

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
@limiter.limit("10/minute")
async def create_persona(
    request: Request,
    persona_data: PersonaCreate,
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
        UserPersona.persona_name == persona_data.persona_name
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
        persona_name=persona_data.persona_name,
        avatar_color=persona_data.avatar_color or random.choice(colors),
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
                "proof_files": json.loads(v.proof_files) if v.proof_files else [],
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
    body: ReviewNotes = ReviewNotes(),
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
    verification.review_notes = body.review_notes

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
    body: ReviewNotes = ReviewNotes(),
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
    verification.review_notes = body.review_notes

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
    body: ReviewNotes = ReviewNotes(),
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
    verification.review_notes = body.review_notes if body.review_notes else "Revoked by admin"
    
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


# ==================== Quick Self-Declaration ====================

class QuickDeclareRequest(BaseModel):
    event_id: str
    stakeholder_id: str = ""  # Existing stakeholder ID (optional if custom_name provided)
    custom_name: str = ""  # Custom stakeholder name (e.g. "Local Journalist")
    reason: str = ""  # Optional: why you are this stakeholder


@router.post("/quick-declare")
@limiter.limit("10/minute")
async def quick_declare_stakeholder(
    request: Request,
    data: QuickDeclareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """
    Quick self-declaration as a stakeholder for an event.

    Instantly grants 'declared' status (no admin review needed).
    User can later upgrade to 'verified' by submitting proof.
    """
    # Get or create default persona
    persona = db.query(UserPersona).filter(
        UserPersona.user_id == current_user.id,
        UserPersona.is_deleted == False,
    ).first()

    if not persona:
        import random
        persona = UserPersona(
            id=uuid.uuid4(),
            user_id=current_user.id,
            persona_name=random.choice(["Anonymous Observer", "Curious Reader", "Global Citizen"]),
            avatar_color=random.choice(['blue', 'green', 'purple', 'orange', 'teal']),
            is_verified=False,
        )
        db.add(persona)
        db.flush()

    # Check event exists
    event = db.query(Event).filter(Event.id == data.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Resolve stakeholder: use existing ID or create from custom name
    if data.stakeholder_id:
        stakeholder = db.query(Stakeholder).filter(Stakeholder.id == data.stakeholder_id).first()
        if not stakeholder:
            raise HTTPException(status_code=404, detail="Stakeholder not found")
    elif data.custom_name and data.custom_name.strip():
        custom_name = data.custom_name.strip()
        if len(custom_name) > 100:
            raise HTTPException(status_code=400, detail="Stakeholder name too long (max 100 characters)")
        # Find or create stakeholder with this name
        from app.models.stakeholders import StakeholderType, EventStakeholder
        stakeholder = db.query(Stakeholder).filter(Stakeholder.name == custom_name).first()
        if not stakeholder:
            # Get or create a generic "Group" type
            group_type = db.query(StakeholderType).filter(StakeholderType.name == "Group").first()
            if not group_type:
                group_type = StakeholderType(id=uuid.uuid4(), name="Group", description="General group")
                db.add(group_type)
                db.flush()
            stakeholder = Stakeholder(
                id=uuid.uuid4(),
                name=custom_name,
                type_id=group_type.id,
                description=f"User-declared stakeholder: {custom_name}",
                is_active=True,
            )
            db.add(stakeholder)
            db.flush()
        # Link stakeholder to event if not already linked
        existing_link = db.query(EventStakeholder).filter(
            EventStakeholder.event_id == data.event_id,
            EventStakeholder.stakeholder_id == stakeholder.id,
        ).first()
        if not existing_link:
            db.add(EventStakeholder(
                id=uuid.uuid4(),
                event_id=data.event_id,
                stakeholder_id=stakeholder.id,
                is_ai_generated=False,
                status='approved',
            ))
            db.flush()
    else:
        raise HTTPException(status_code=400, detail="Either stakeholder_id or custom_name is required")

    # Check existing verification
    existing = db.query(EventStakeholderVerification).filter(
        EventStakeholderVerification.user_persona_id == persona.id,
        EventStakeholderVerification.event_id == data.event_id,
    ).first()

    if existing:
        if existing.status in ('approved', 'declared'):
            return {
                "message": "Already declared",
                "verification_id": str(existing.id),
                "status": existing.status,
                "stakeholder_name": stakeholder.name,
                "persona_id": str(persona.id),
                "persona_name": persona.persona_name,
            }
        elif existing.status == 'pending':
            # Upgrade pending to declared
            existing.status = 'declared'
            existing.proof_type = 'self_declaration'
            db.commit()
            return {
                "message": "Declaration confirmed",
                "verification_id": str(existing.id),
                "status": "declared",
                "stakeholder_name": stakeholder.name,
                "persona_id": str(persona.id),
                "persona_name": persona.persona_name,
            }
        elif existing.status == 'rejected':
            # Allow re-declaration
            existing.status = 'declared'
            existing.proof_type = 'self_declaration'
            existing.application_text = data.reason or existing.application_text
            existing.stakeholder_id = data.stakeholder_id
            db.commit()
            return {
                "message": "Re-declared",
                "verification_id": str(existing.id),
                "status": "declared",
                "stakeholder_name": stakeholder.name,
                "persona_id": str(persona.id),
                "persona_name": persona.persona_name,
            }

    # Create new declaration
    verification = EventStakeholderVerification(
        id=uuid.uuid4(),
        user_persona_id=persona.id,
        event_id=data.event_id,
        stakeholder_id=data.stakeholder_id,
        application_text=data.reason,
        proof_type='self_declaration',
        status='declared',
    )
    db.add(verification)
    db.commit()

    return {
        "message": "Declared as stakeholder",
        "verification_id": str(verification.id),
        "status": "declared",
        "stakeholder_name": stakeholder.name,
        "persona_id": str(persona.id),
        "persona_name": persona.persona_name,
    }


class QuickUndeclareRequest(BaseModel):
    event_id: str
    stakeholder_id: str


@router.post("/quick-undeclare")
@limiter.limit("10/minute")
async def quick_undeclare_stakeholder(
    request: Request,
    data: QuickUndeclareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """
    Cancel a self-declaration for an event.

    Only 'declared' status can be cancelled by the user.
    Admin-approved verifications cannot be undone here.
    """
    # Find user's persona
    persona = db.query(UserPersona).filter(
        UserPersona.user_id == current_user.id,
        UserPersona.is_deleted == False,
    ).first()

    if not persona:
        raise HTTPException(status_code=404, detail="No persona found")

    verification = db.query(EventStakeholderVerification).filter(
        EventStakeholderVerification.user_persona_id == persona.id,
        EventStakeholderVerification.event_id == data.event_id,
        EventStakeholderVerification.stakeholder_id == data.stakeholder_id,
    ).first()

    if not verification:
        raise HTTPException(status_code=404, detail="Declaration not found")

    if verification.status == 'approved':
        raise HTTPException(status_code=400, detail="Verified status can only be revoked by an admin")

    if verification.status != 'declared':
        raise HTTPException(status_code=400, detail=f"Cannot cancel {verification.status} declaration")

    db.delete(verification)
    db.commit()

    return {"message": "Declaration cancelled"}


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
@limiter.limit("5/minute")
async def apply_for_verification(
    request: Request,
    persona_id: str,
    verify_data: VerificationApply,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """
    Apply for stakeholder verification in a specific event

    - **persona_id**: ID of persona to use
    - **verify_data.event_id**: Event to apply for
    - **verify_data.stakeholder_id**: Stakeholder type to apply as
    - **verify_data.application_text**: Why you qualify
    """
    event_id = verify_data.event_id
    stakeholder_id = verify_data.stakeholder_id
    application_text = verify_data.application_text
    proof_type = verify_data.proof_type or 'self_declaration'
    proof_data = verify_data.proof_data or ''
    proof_files_json = json.dumps(verify_data.proof_files) if verify_data.proof_files else None
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
            # Allow re-application: update existing record
            # Check stakeholder exists
            stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
            if not stakeholder:
                raise HTTPException(status_code=404, detail="Stakeholder not found")

            existing.stakeholder_id = stakeholder_id
            existing.application_text = application_text
            existing.proof_type = proof_type
            existing.proof_data = proof_data
            existing.proof_files = proof_files_json
            existing.status = 'pending'
            existing.admin_notes = None
            existing.ai_review_score = None
            existing.ai_flags = None
            db.commit()

            # AI review disabled for now — manual admin review only

            return {
                "message": "Re-application submitted",
                "application_id": str(existing.id),
                "status": "pending",
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Already have an application for this event"
            )

    # Check stakeholder exists
    stakeholder = db.query(Stakeholder).filter(Stakeholder.id == stakeholder_id).first()
    if not stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")

    # Create new application
    try:
        application = EventStakeholderVerification(
            id=uuid.uuid4(),
            user_persona_id=persona_id,
            event_id=event_id,
            stakeholder_id=stakeholder_id,
            application_text=application_text,
            proof_type=proof_type,
            proof_data=proof_data,
            proof_files=proof_files_json,
            status='pending',
        )

        db.add(application)
        db.commit()

        # AI review disabled for now — manual admin review only

        return {
            "message": "Application submitted",
            "application_id": str(application.id),
            "status": "pending",
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


# ==================== File Upload for Verification ====================

ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "verification")


@router.post("/verify/upload")
@limiter.limit("10/minute")
async def upload_verification_files(
    request: Request,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Upload proof files for a verification application (max 5 files, 10MB each)"""

    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 files allowed")

    saved_files = []
    for file in files:
        # Validate extension
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{ext}' not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Read and validate size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' exceeds 10MB limit"
            )

        # Save file
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(content)

        saved_files.append({
            "filename": filename,
            "original_name": file.filename,
            "url": f"/uploads/verification/{filename}",
        })

    return {
        "message": f"{len(saved_files)} file(s) uploaded",
        "files": saved_files,
    }
