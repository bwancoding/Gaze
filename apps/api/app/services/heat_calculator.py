"""
Heat score algorithm service - calculates heat scores for articles and events

Features:
- Time decay function (newer events get higher heat scores)
- Interaction weight calculation (comment count, share count, etc.)
- Source priority weighting (authoritative media get higher weights)
- Top 20 selection logic
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
import math

from app.models.trending import TrendingArticle, TrendingEvent, TrendingSource
from app.services.trending_config import (
    HEAT_TIME_DECAY_LAMBDA, HEAT_COMMENT_WEIGHT, HEAT_SHARE_WEIGHT,
    CATEGORY_WEIGHTS, CATEGORY_DEFAULT_WEIGHT,
    REGION_DIVERSITY_BONUS, REGION_DIVERSITY_MAX,
    ARTICLE_COUNT_BONUS_CAP,
)


class HeatCalculator:
    """Heat score calculator"""

    SOURCE_PRIORITY_WEIGHTS = {
        "P0": 1.5,
        "P1": 1.2,
        "P2": 1.0,
    }

    STANCE_DIVERSITY_BONUS = {
        1: 1.0,
        2: 1.1,
        3: 1.2,
        4: 1.25,
        5: 1.3,
    }

    def __init__(self, db: Session):
        self.db = db
        self.time_decay_lambda = HEAT_TIME_DECAY_LAMBDA
        self.comment_weight = HEAT_COMMENT_WEIGHT
        self.share_weight = HEAT_SHARE_WEIGHT

    def calculate_time_decay(self, published_at: datetime, reference_time: Optional[datetime] = None) -> float:
        if reference_time is None:
            reference_time = datetime.utcnow()
        time_diff = reference_time - published_at
        hours = max(0, time_diff.total_seconds() / 3600)
        return math.exp(-self.time_decay_lambda * hours)

    def calculate_interaction_score(self, comment_count: int = 0, share_count: int = 0) -> float:
        comment_score = math.log10(comment_count + 1) * self.comment_weight
        share_score = math.log10(share_count + 1) * self.share_weight
        return comment_score + share_score

    def get_source_weight(self, source_id: int) -> float:
        source = self.db.query(TrendingSource).filter(TrendingSource.id == source_id).first()
        if not source:
            return 1.0
        return self.SOURCE_PRIORITY_WEIGHTS.get(source.priority, 1.0)

    def calculate_article_heat(self, article: TrendingArticle, reference_time: Optional[datetime] = None) -> float:
        time_decay = self.calculate_time_decay(article.published_at, reference_time)
        interaction_score = self.calculate_interaction_score(
            article.comment_count, article.share_count
        )
        source_weight = self.get_source_weight(article.source_id)
        base_score = 10.0
        heat_score = time_decay * (base_score + interaction_score) * source_weight
        return round(heat_score, 2)

    def get_category_weight(self, category: Optional[str]) -> float:
        if not category:
            return CATEGORY_DEFAULT_WEIGHT
        return CATEGORY_WEIGHTS.get(category, CATEGORY_DEFAULT_WEIGHT)

    def get_region_diversity_bonus(self, event: TrendingEvent) -> float:
        regions = set()
        for article in event.articles:
            if article.source and hasattr(article.source, 'region'):
                regions.add(article.source.region)
        n = len(regions)
        if n >= 4:
            return REGION_DIVERSITY_MAX
        return REGION_DIVERSITY_BONUS.get(n, 1.0)

    def calculate_event_heat(self, event: TrendingEvent, reference_time: Optional[datetime] = None) -> float:
        """
        Engagement-aware event heat.

        Prior to Phase A, base_score was dominated by `media_count * 10`,
        which rewarded supply-side behavior (how many newsrooms covered a
        story) rather than demand-side behavior (how many humans engaged
        with it). That structurally crushed Entertainment/Gaming/Sports,
        because hard news gets wholesale 8+ outlet coverage by default.

        New formula:
        - `sqrt` dampening on article_count / media_count so a 10-outlet
          hard news story is ~3.2x bigger than a 1-outlet story, not 10x
        - `log10(engagement+1) * 20` as a FIRST-CLASS term, reading the
          persisted topic_engagement_score (Reddit upvotes + HN points +
          Bluesky likes/reposts + comments, weighted in news_aggregator)
        - Time decay anchored to last_updated so long-running stories
          that keep getting merged don't decay
        """
        # Per-article interaction heat ONLY — we deliberately skip the
        # "base 10 per article" term from calculate_article_heat, because
        # that would re-introduce the supply-side bias we just removed
        # (every RSS article would add +10 regardless of demand). What we
        # keep is the interaction score (comment_count / share_count),
        # which is non-zero for articles fetched via Reddit/HN fetchers
        # that carry real engagement data, and zero for pure RSS feeds.
        total_article_heat = 0.0
        if event.articles:
            for article in event.articles:
                interaction = self.calculate_interaction_score(
                    article.comment_count or 0,
                    article.share_count or 0,
                )
                if interaction > 0:
                    src_weight = self.get_source_weight(article.source_id)
                    td = self.calculate_time_decay(article.published_at, reference_time)
                    total_article_heat += td * interaction * src_weight

        # Time decay for the event itself — use last_updated so long-running
        # stories that keep getting merged with new articles don't decay.
        reference_at = event.last_updated or event.created_at
        event_time_decay = self.calculate_time_decay(reference_at, reference_time)

        article_count = max(event.article_count or 0, len(event.articles) if event.articles else 0)
        media_count = max(
            event.media_count or 0,
            event.unique_media_count if event.articles else 0
        )

        # Supply-side: dampened with sqrt so a 10-outlet story is ~3.2x the
        # base of a 1-outlet story (not 10x). This prevents wholesale
        # coverage from structurally dominating demand signals.
        supply_score = (
            math.sqrt(article_count) * 5.0
            + math.sqrt(media_count) * 8.0
        )

        # Demand-side: persisted topic engagement (Reddit upvotes + HN
        # points + Bluesky likes + comments, from topic seeds at event
        # creation and every merge). Log-scale so a 50k-upvote post is
        # ~1.5x the contribution of a 2k-upvote post, not 25x — we want
        # the signal to matter without letting outliers dominate.
        engagement = event.topic_engagement_score or 0.0
        engagement_score = math.log10(engagement + 1) * 20.0

        base_score = (supply_score + engagement_score) * event_time_decay

        # Diversity bonuses (kept — these reward multi-perspective
        # coverage, which is still a product goal independent of raw heat)
        media_diversity_bonus = min(1.0 + (media_count - 1) * 0.08, 1.6)

        stances = set()
        if event.articles:
            for article in event.articles:
                if article.source:
                    stances.add(article.source.stance)
        stance_bonus = self.STANCE_DIVERSITY_BONUS.get(len(stances), 1.0)

        # Category weight — Phase A reverted to 1.0 across the board.
        # The engagement term above is now doing the work that 1.4x
        # multipliers were trying to do, but in a data-driven way.
        category_weight = self.get_category_weight(event.category)

        # Region diversity
        region_bonus = self.get_region_diversity_bonus(event)

        event_heat = (
            (base_score + total_article_heat)
            * media_diversity_bonus
            * stance_bonus
            * category_weight
            * region_bonus
        )
        return round(event_heat, 2)

    def update_article_heat_scores(self, batch_size: int = 100) -> int:
        articles = self.db.query(TrendingArticle).order_by(
            desc(TrendingArticle.published_at)
        ).limit(batch_size).all()

        updated_count = 0
        for article in articles:
            new_heat = self.calculate_article_heat(article)
            if abs(new_heat - (article.heat_score or 0)) > 0.01:
                article.heat_score = new_heat
                updated_count += 1

        self.db.commit()
        return updated_count

    def update_event_heat_scores(self, batch_size: int = 50) -> int:
        events = self.db.query(TrendingEvent).order_by(
            desc(TrendingEvent.created_at)
        ).limit(batch_size).all()

        updated_count = 0
        for event in events:
            self.db.refresh(event)
            new_heat = self.calculate_event_heat(event)
            if abs(new_heat - (event.heat_score or 0)) > 0.01:
                event.heat_score = new_heat
                updated_count += 1

        self.db.commit()
        return updated_count

    def get_top_events(self, limit: int = 20, time_window_hours: Optional[int] = None,
                       category: Optional[str] = None) -> List[TrendingEvent]:
        # Only show raw (pending review) and promoted events, not archived
        query = self.db.query(TrendingEvent).filter(
            TrendingEvent.heat_score > 0,
            TrendingEvent.status.in_(['raw', 'promoted']),
        )

        if time_window_hours:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            query = query.filter(TrendingEvent.created_at >= cutoff_time)

        if category:
            query = query.filter(TrendingEvent.category == category)

        return query.order_by(desc(TrendingEvent.heat_score)).limit(limit).all()

    def get_trending_events(self, limit: int = 20, time_window_hours: int = 24) -> List[Tuple[TrendingEvent, float]]:
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        events = self.db.query(TrendingEvent).filter(
            and_(
                TrendingEvent.created_at >= cutoff_time,
                TrendingEvent.heat_score > 0
            )
        ).all()

        trending = []
        for event in events:
            time_decay = self.calculate_time_decay(event.created_at)
            expected_heat = event.heat_score / max(time_decay, 0.01)
            growth_rate = event.heat_score / max(expected_heat, 0.01)
            trending.append((event, growth_rate))

        trending.sort(key=lambda x: x[1], reverse=True)
        return trending[:limit]


def calculate_all_heat_scores(db: Session) -> Dict:
    """Convenience function: calculate heat scores for all articles and events"""
    calculator = HeatCalculator(db)
    articles_updated = calculator.update_article_heat_scores()
    events_updated = calculator.update_event_heat_scores()
    return {
        "articles_updated": articles_updated,
        "events_updated": events_updated,
    }
