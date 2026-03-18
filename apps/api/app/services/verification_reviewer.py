"""
WRHITW AI Verification Reviewer
Assists admin by pre-screening stakeholder verification applications
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.personas import EventStakeholderVerification, UserPersona
from app.models.stakeholders import Stakeholder
from app.models import Event

logger = logging.getLogger(__name__)


REVIEW_PROMPT_TEMPLATE = """You are reviewing a stakeholder verification application for WRHITW, a multi-perspective news platform where affected people can get verified badges to comment on events.

## Application Details

**Applicant persona name:** {persona_name}
**Claiming to be:** {stakeholder_name} ({stakeholder_description})
**Related event:** {event_title}
**Proof type:** {proof_type}
**Application text:**
{application_text}

## Your Task

Evaluate this application's legitimacy. Consider:

1. **Relevance**: Does the application text explain a credible connection to the event as the claimed stakeholder type?
2. **Specificity**: Does it contain specific details (location, experience, timeline) rather than vague claims?
3. **Consistency**: Does the persona name align with the claimed stakeholder role?
4. **Red flags**: Look for copy-paste text, generic statements, contradictions, or attempts to game the system.

## Output

Return ONLY valid JSON:

```json
{{
  "score": 75,
  "recommendation": "approve|reject|needs_review",
  "reasoning": "Brief explanation of the score",
  "flags": ["flag1", "flag2"],
  "suggested_questions": ["question for admin to ask if unsure"]
}}
```

Score guide:
- 80-100: Strong application, likely legitimate → recommend approve
- 50-79: Unclear, needs human judgment → recommend needs_review
- 0-49: Likely illegitimate or insufficient → recommend reject

Flag types: "too_short", "generic_text", "no_specifics", "persona_mismatch", "copy_paste_suspected", "contradictory", "high_quality", "detailed_evidence"
"""


def _get_ai_client():
    """Create OpenAI-compatible client for DashScope."""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        return None

    from openai import AsyncOpenAI
    return AsyncOpenAI(
        base_url=os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        api_key=api_key,
    )


async def ai_review_application(
    db: Session,
    verification_id: str,
) -> Dict[str, Any]:
    """
    Run AI review on a verification application.
    Stores results in the verification record.

    Returns:
        Dict with score, recommendation, reasoning, flags
    """
    verification = db.query(EventStakeholderVerification).filter(
        EventStakeholderVerification.id == verification_id
    ).first()

    if not verification:
        raise ValueError(f"Verification {verification_id} not found")

    # Gather context
    persona = db.query(UserPersona).filter(
        UserPersona.id == verification.user_persona_id
    ).first()

    stakeholder = db.query(Stakeholder).filter(
        Stakeholder.id == verification.stakeholder_id
    ).first()

    event = db.query(Event).filter(
        Event.id == verification.event_id
    ).first()

    # Build prompt
    prompt = REVIEW_PROMPT_TEMPLATE.format(
        persona_name=persona.persona_name if persona else "Unknown",
        stakeholder_name=stakeholder.name if stakeholder else "Unknown",
        stakeholder_description=stakeholder.description if stakeholder else "",
        event_title=event.title if event else "Unknown",
        proof_type=verification.proof_type or "self_declaration",
        application_text=verification.application_text or "(empty)",
    )

    client = _get_ai_client()
    if not client:
        # Fallback: rule-based scoring when AI is not available
        result = _rule_based_review(verification, persona, stakeholder)
    else:
        try:
            response = await client.chat.completions.create(
                model="qwen3.5-plus",
                messages=[
                    {"role": "system", "content": "You are a verification reviewer. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            result = json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"AI review failed for {verification_id}: {e}")
            result = _rule_based_review(verification, persona, stakeholder)

    # Store results
    verification.ai_review_score = result.get("score", 50)
    verification.ai_review_notes = result.get("reasoning", "")
    verification.ai_flags = json.dumps(result.get("flags", []))
    db.commit()

    return result


def _rule_based_review(
    verification: EventStakeholderVerification,
    persona: Optional[UserPersona],
    stakeholder: Optional[Stakeholder],
) -> Dict[str, Any]:
    """
    Simple rule-based fallback when AI is not available.
    """
    score = 50
    flags = []
    reasoning_parts = []

    text = verification.application_text or ""

    # Check text length
    if len(text) < 20:
        score -= 30
        flags.append("too_short")
        reasoning_parts.append("Application text is very short")
    elif len(text) < 50:
        score -= 10
        flags.append("too_short")
        reasoning_parts.append("Application text is brief")
    elif len(text) > 200:
        score += 15
        flags.append("detailed_evidence")
        reasoning_parts.append("Application provides detailed explanation")

    # Check if proof type is more than self-declaration
    if verification.proof_type and verification.proof_type != "self_declaration":
        score += 10
        flags.append("high_quality")
        reasoning_parts.append(f"Provided {verification.proof_type} as proof")

    # Check persona name vs stakeholder alignment (basic)
    if persona and stakeholder:
        persona_lower = persona.persona_name.lower()
        stakeholder_lower = stakeholder.name.lower()
        # Simple word overlap check
        persona_words = set(persona_lower.split())
        stakeholder_words = set(stakeholder_lower.split())
        if persona_words & stakeholder_words:
            score += 10
            reasoning_parts.append("Persona name aligns with stakeholder role")

    # Check for generic text patterns
    generic_phrases = ["i am", "i want to", "please verify", "i need"]
    generic_count = sum(1 for p in generic_phrases if p in text.lower())
    if generic_count >= 2 and len(text) < 100:
        score -= 10
        flags.append("generic_text")
        reasoning_parts.append("Text appears generic")

    # Clamp score
    score = max(0, min(100, score))

    # Determine recommendation
    if score >= 80:
        recommendation = "approve"
    elif score >= 50:
        recommendation = "needs_review"
    else:
        recommendation = "reject"

    return {
        "score": score,
        "recommendation": recommendation,
        "reasoning": ". ".join(reasoning_parts) if reasoning_parts else "Rule-based review (AI unavailable)",
        "flags": flags,
        "suggested_questions": [],
    }


async def review_pending_applications(db: Session) -> int:
    """
    Batch-review all pending applications that haven't been AI-reviewed yet.
    Returns count of reviewed applications.
    """
    pending = db.query(EventStakeholderVerification).filter(
        EventStakeholderVerification.status == "pending",
        EventStakeholderVerification.ai_review_score.is_(None),
    ).all()

    count = 0
    for v in pending:
        try:
            await ai_review_application(db, str(v.id))
            count += 1
        except Exception as e:
            logger.error(f"Failed to review {v.id}: {e}")

    return count
