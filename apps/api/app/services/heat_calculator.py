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
        Engagement-aware event heat (Phase B — demand dominates, supply dampened).

        Phase A introduced `topic_engagement_score` and sqrt-dampened supply,
        but prod data showed that term was still too weak: a 22k-upvote
        Canadians/boycott story landed at heat 252 while a 150-article wire
        story with 0 Reddit attention sat at 6272. Three causes:

        1. `total_article_heat` accumulated LINEARLY across 150+ articles.
           Even though most RSS feeds contribute 0 interaction, the 20-30
           Reddit/HN crossovers in a hard-news wire story each add ~15
           heat — summing to 2000+, which dwarfed any engagement term.
        2. `engagement_score` multiplier was 20, giving a 25k-upvote story
           only ~88 heat from demand. Supply's raw AIH sum ate it 20:1.
        3. Four bonuses (media_div × stance × region × category) compounded
           to 2.6x uncapped, amplifying whichever side already dominated.

        Phase B fixes (tuned via /tmp/heat_regression.py):
        - Wrap `total_article_heat` in `log10(sum+1) * 60` — dampens a
          20-article Reddit crossover from ~300 raw to ~150, while a
          quiet 3-article story with same per-article heat stays ~120.
        - `engagement_score` multiplier 20 → 70. A 25k-upvote story now
          contributes ~308 (was 88), finally competitive with supply.
        - Compound bonus product capped at 1.5. Editorial diversity is
          still rewarded but can't multiply a dominant signal into orbit.
        """
        # Per-article interaction — accumulate the raw sum here, then
        # log-dampen below before adding to base_score. The dampening is
        # what kills the linear-with-article-count bias that used to
        # make 150-article wholesale stories structurally dominate.
        total_article_heat_raw = 0.0
        if event.articles:
            for article in event.articles:
                interaction = self.calculate_interaction_score(
                    article.comment_count or 0,
                    article.share_count or 0,
                )
                if interaction > 0:
                    src_weight = self.get_source_weight(article.source_id)
                    td = self.calculate_time_decay(article.published_at, reference_time)
                    total_article_heat_raw += td * interaction * src_weight

        total_article_heat = math.log10(total_article_heat_raw + 1) * 60.0

        # Time decay for the event itself — use last_updated so long-running
        # stories that keep getting merged with new articles don't decay.
        reference_at = event.last_updated or event.created_at
        event_time_decay = self.calculate_time_decay(reference_at, reference_time)

        article_count = max(event.article_count or 0, len(event.articles) if event.articles else 0)
        media_count = max(
            event.media_count or 0,
            event.unique_media_count if event.articles else 0
        )

        # Supply-side: sqrt-dampened so a 10-outlet story is ~3.2x the
        # base of a 1-outlet story (not 10x).
        supply_score = (
            math.sqrt(article_count) * 5.0
            + math.sqrt(media_count) * 8.0
        )

        # Demand-side: persisted topic engagement (Reddit upvotes + HN
        # points + Bluesky likes + comments). multiplier 70 (was 20) —
        # see class docstring for the Phase B rebalance rationale.
        engagement = event.topic_engagement_score or 0.0
        engagement_score = math.log10(engagement + 1) * 70.0

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

        category_weight = self.get_category_weight(event.category)
        region_bonus = self.get_region_diversity_bonus(event)

        # Compound bonus cap: the four multipliers used to multiply
        # uncapped to ~2.6x, which amplified whichever side (supply or
        # demand) was already dominant. Capping at 1.5 means editorial
        # diversity is still rewarded but can't push a story into orbit.
        compound_bonus = min(
            media_diversity_bonus * stance_bonus * category_weight * region_bonus,
            1.5,
        )

        event_heat = (base_score + total_article_heat) * compound_bonus
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

    def update_event_heat_scores(self, batch_size: Optional[int] = None) -> int:
        # Recalculate all active (non-archived) events. The previous
        # batch_size=50 only touched the most recently created events,
        # which meant older still-active stories kept stale heat after
        # formula changes and silently dominated the leaderboard. Bound
        # with an optional limit for tests; in prod we recalc everything.
        query = self.db.query(TrendingEvent).filter(
            TrendingEvent.status.in_(['raw', 'promoted'])
        ).order_by(desc(TrendingEvent.created_at))
        if batch_size is not None:
            query = query.limit(batch_size)
        events = query.all()

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
