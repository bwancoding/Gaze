"""
Event Analysis Service
Generates stakeholder-based deep analysis for events using AI.
Replaces the old left/center/right summary system.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models import Event, EventSource, Source
from app.models.event_analysis import EventAnalysis
from app.models.stakeholders import Stakeholder, StakeholderType, EventStakeholder
from app.services.ai_prompts import AISummaryGenerator

logger = logging.getLogger(__name__)

ANALYSIS_TTL_HOURS = int(os.getenv("ANALYSIS_TTL_HOURS", "24"))


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


def get_cached_analysis(db: Session, event_id: str) -> Optional[Dict[str, Any]]:
    """Get cached analysis if exists and not expired."""
    analysis = db.query(EventAnalysis).filter(EventAnalysis.event_id == event_id).first()
    if not analysis:
        return None
    if analysis.expires_at and datetime.utcnow() > analysis.expires_at:
        return None
    return analysis.to_dict()


def _gather_articles_for_event(db: Session, event_id: str) -> List[Dict]:
    """Collect articles with source info for an event.

    First checks event_sources table, then falls back to trending_articles
    via the event's trending_origin_id link.
    """
    results = (
        db.query(EventSource, Source)
        .join(Source, EventSource.source_id == Source.id)
        .filter(EventSource.event_id == event_id)
        .all()
    )

    articles = []
    for es, source in results:
        articles.append({
            "source_name": source.name,
            "title": es.article_title,
            "content": es.article_content or es.article_summary or "",
            "published_at": es.published_at.isoformat() if es.published_at else "",
        })

    # Fallback: get articles from trending_articles via trending_origin_id
    if not articles:
        event = db.query(Event).filter(Event.id == event_id).first()
        if event and event.trending_origin_id:
            from app.models.trending import TrendingArticle, TrendingSource
            trending_results = (
                db.query(TrendingArticle, TrendingSource)
                .outerjoin(TrendingSource, TrendingArticle.source_id == TrendingSource.id)
                .filter(TrendingArticle.event_id == event.trending_origin_id)
                .limit(30)  # Cap to avoid overly long prompts
                .all()
            )
            for ta, ts in trending_results:
                articles.append({
                    "source_name": ts.name if ts else "Unknown",
                    "title": ta.title or "",
                    "content": ta.content or ta.summary or "",
                    "published_at": ta.published_at.isoformat() if ta.published_at else "",
                })
            if articles:
                logger.info(f"Using {len(articles)} trending articles for event {event_id} (origin={event.trending_origin_id})")

    return articles


def _get_or_create_stakeholder(db: Session, name: str) -> Stakeholder:
    """Find or create a stakeholder by name."""
    existing = db.query(Stakeholder).filter(Stakeholder.name == name).first()
    if existing:
        return existing

    # Get or create a default "Group" type
    group_type = db.query(StakeholderType).filter(StakeholderType.name == "Group").first()
    if not group_type:
        group_type = StakeholderType(name="Group", description="General stakeholder group")
        db.add(group_type)
        db.flush()

    stakeholder = Stakeholder(
        name=name,
        type_id=group_type.id,
        verification_required=False,
        is_active=True,
    )
    db.add(stakeholder)
    db.flush()
    return stakeholder


async def generate_event_analysis(
    db: Session,
    event_id: str,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Generate full stakeholder-based deep analysis for an event.

    Returns cached analysis if available and not expired.
    Creates EventStakeholder records for AI-identified stakeholders.
    """
    if not force:
        cached = get_cached_analysis(db, event_id)
        if cached:
            return cached

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise ValueError(f"Event {event_id} not found")

    client = _get_ai_client()
    if not client:
        raise ValueError("DASHSCOPE_API_KEY not configured")

    articles = _gather_articles_for_event(db, event_id)
    if not articles:
        raise ValueError(f"No articles found for event {event_id}")

    logger.info(f"Generating stakeholder analysis for event {event_id} with {len(articles)} articles")

    generator = AISummaryGenerator(client)
    result = await generator.generate_stakeholder_analysis(articles)

    now = datetime.utcnow()
    expires = now + timedelta(hours=ANALYSIS_TTL_HOURS)

    # Build stakeholder perspectives with IDs
    stakeholder_perspectives = []
    for sp in result.get("stakeholders", []):
        stakeholder = _get_or_create_stakeholder(db, sp["stakeholder_name"])
        stakeholder_perspectives.append({
            "stakeholder_id": str(stakeholder.id),
            "stakeholder_name": sp["stakeholder_name"],
            "perspective_text": sp.get("perspective_text", ""),
            "key_arguments": sp.get("key_arguments", []),
            "sources_cited": sp.get("sources_cited", []),
        })

        # Create or update EventStakeholder record
        es = db.query(EventStakeholder).filter(
            EventStakeholder.event_id == event_id,
            EventStakeholder.stakeholder_id == stakeholder.id,
        ).first()
        if not es:
            es = EventStakeholder(
                event_id=event_id,
                stakeholder_id=stakeholder.id,
                is_ai_generated=True,
                status='approved',
            )
            db.add(es)
        es.perspective_summary = sp.get("perspective_text", "")
        es.key_concerns = sp.get("key_arguments", [])

    # Upsert EventAnalysis
    existing = db.query(EventAnalysis).filter(EventAnalysis.event_id == event_id).first()
    if existing:
        existing.background = result.get("background", "")
        existing.cause_chain = result.get("cause_chain", [])
        existing.impact_analysis = result.get("impact_analysis", [])
        existing.timeline = result.get("timeline", [])
        existing.stakeholder_perspectives = stakeholder_perspectives
        existing.disputed_claims = result.get("disputed_claims", [])
        existing.model_name = "qwen3.5-plus"
        existing.quality_score = result.get("confidence_score")
        existing.generated_at = now
        existing.expires_at = expires
        analysis = existing
    else:
        analysis = EventAnalysis(
            event_id=event_id,
            background=result.get("background", ""),
            cause_chain=result.get("cause_chain", []),
            impact_analysis=result.get("impact_analysis", []),
            timeline=result.get("timeline", []),
            stakeholder_perspectives=stakeholder_perspectives,
            disputed_claims=result.get("disputed_claims", []),
            model_name="qwen3.5-plus",
            quality_score=result.get("confidence_score"),
            generated_at=now,
            expires_at=expires,
        )
        db.add(analysis)

    # Also update the Event's inline fields for quick access
    event.background = result.get("background", "")
    event.cause_chain = result.get("cause_chain", [])
    event.impact_analysis = result.get("impact_analysis", [])
    event.timeline_data = result.get("timeline", [])
    event.stakeholder_perspectives = stakeholder_perspectives
    event.source_article_count = len(articles)

    try:
        db.commit()
        db.refresh(analysis)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to commit analysis for event {event_id}: {e}")
        raise

    logger.info(f"Stakeholder analysis cached for event {event_id}, {len(stakeholder_perspectives)} stakeholders identified")

    return analysis.to_dict()
