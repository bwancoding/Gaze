"""
WRHITW AI Summary Service
Handles summary generation, caching, and DB persistence
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models import AiSummary, Event, EventSource, Source
from app.services.ai_prompts import AISummaryGenerator

logger = logging.getLogger(__name__)

# Summary cache TTL: regenerate if older than this
SUMMARY_TTL_HOURS = int(os.getenv("SUMMARY_TTL_HOURS", "24"))


def _get_ai_client():
    """Create OpenAI-compatible client for DashScope."""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        return None

    from openai import AsyncOpenAI
    return AsyncOpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=api_key,
    )


def get_cached_summary(db: Session, event_id: str) -> Optional[Dict[str, Any]]:
    """
    Get cached summary if it exists and is not expired.

    Returns None if no summary exists or if it's expired.
    """
    summary = db.query(AiSummary).filter(AiSummary.event_id == event_id).first()

    if not summary:
        return None

    # Check if expired
    if summary.expires_at and datetime.utcnow() > summary.expires_at:
        return None

    return _format_summary(summary)


def _format_summary(summary: AiSummary) -> Dict[str, Any]:
    """Format DB summary to API response."""
    return {
        "event_id": str(summary.event_id),
        "left_perspective": {
            "summary": summary.left_perspective,
            "sources": summary.left_sources or [],
        },
        "center_perspective": {
            "summary": summary.center_perspective,
            "sources": summary.center_sources or [],
        },
        "right_perspective": {
            "summary": summary.right_perspective,
            "sources": summary.right_sources or [],
        },
        "model_name": summary.model_name,
        "quality_score": float(summary.quality_score) if summary.quality_score else None,
        "generated_at": summary.generated_at.isoformat() if summary.generated_at else None,
    }


def _gather_articles_for_event(db: Session, event_id: str) -> List[Dict]:
    """Collect articles with source bias info for an event."""
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
            "bias_label": source.bias_label or "center",
            "published_at": es.published_at.isoformat() if es.published_at else "",
        })

    return articles


async def generate_and_cache_summary(
    db: Session,
    event_id: str,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Generate AI summary for an event and cache it in DB.

    Args:
        db: Database session
        event_id: Event UUID
        force: Force regeneration even if cached

    Returns:
        Formatted summary dict

    Raises:
        ValueError: If AI client is not configured or no articles found
    """
    # Check cache first (unless forced)
    if not force:
        cached = get_cached_summary(db, event_id)
        if cached:
            return cached

    # Verify event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise ValueError(f"Event {event_id} not found")

    # Get AI client
    client = _get_ai_client()
    if not client:
        raise ValueError("DASHSCOPE_API_KEY not configured. Cannot generate AI summary.")

    # Gather articles
    articles = _gather_articles_for_event(db, event_id)
    if not articles:
        raise ValueError(f"No articles found for event {event_id}")

    logger.info(f"Generating AI summary for event {event_id} with {len(articles)} articles")

    # Generate
    generator = AISummaryGenerator(client)
    result = await generator.generate_summary(articles)

    # Extract source names for each perspective
    left_sources = result.get("left_perspective", {}).get("sources_cited", [])
    center_sources = result.get("center_perspective", {}).get("sources_cited", [])
    right_sources = result.get("right_perspective", {}).get("sources_cited", [])

    # Upsert into DB
    existing = db.query(AiSummary).filter(AiSummary.event_id == event_id).first()

    now = datetime.utcnow()
    expires = now + timedelta(hours=SUMMARY_TTL_HOURS)

    if existing:
        existing.left_perspective = result.get("left_perspective", {}).get("summary", "")
        existing.center_perspective = result.get("center_perspective", {}).get("summary", "")
        existing.right_perspective = result.get("right_perspective", {}).get("summary", "")
        existing.left_sources = json.dumps(left_sources) if left_sources else None
        existing.center_sources = json.dumps(center_sources) if center_sources else None
        existing.right_sources = json.dumps(right_sources) if right_sources else None
        existing.model_name = "qwen3.5-plus"
        existing.quality_score = result.get("confidence_score")
        existing.generated_at = now
        existing.expires_at = expires
        summary = existing
    else:
        summary = AiSummary(
            event_id=event_id,
            left_perspective=result.get("left_perspective", {}).get("summary", ""),
            center_perspective=result.get("center_perspective", {}).get("summary", ""),
            right_perspective=result.get("right_perspective", {}).get("summary", ""),
            left_sources=json.dumps(left_sources) if left_sources else None,
            center_sources=json.dumps(center_sources) if center_sources else None,
            right_sources=json.dumps(right_sources) if right_sources else None,
            model_name="qwen3.5-plus",
            quality_score=result.get("confidence_score"),
            generated_at=now,
            expires_at=expires,
        )
        db.add(summary)

    db.commit()
    db.refresh(summary)

    logger.info(f"AI summary cached for event {event_id}, expires at {expires}")

    return _format_summary(summary)
