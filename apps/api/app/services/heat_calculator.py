"""
热度算法服务 - 计算文章和事件的热度分数

功能：
- 时间衰减函数（越新的事件热度越高）
- 互动权重计算（讨论量、转发量等）
- 源优先级加权（权威媒体权重更高）
- Top20 筛选逻辑
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
import math

from app.models.trending import TrendingArticle, TrendingEvent, TrendingSource
from app.services.trending_config import (
    HEAT_TIME_DECAY_LAMBDA, HEAT_COMMENT_WEIGHT, HEAT_SHARE_WEIGHT
)


class HeatCalculator:
    """热度计算器"""

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

    def calculate_event_heat(self, event: TrendingEvent, reference_time: Optional[datetime] = None) -> float:
        if not event.articles:
            return 0.0

        total_article_heat = sum(
            self.calculate_article_heat(article, reference_time)
            for article in event.articles
        )

        media_count = event.unique_media_count
        media_diversity_bonus = min(1.0 + (media_count - 1) * 0.1, 2.0)

        stances = set()
        for article in event.articles:
            if article.source:
                stances.add(article.source.stance)
        stance_bonus = self.STANCE_DIVERSITY_BONUS.get(len(stances), 1.3)

        article_count_bonus = math.log10(event.article_count + 1) * 0.5

        event_heat = total_article_heat * media_diversity_bonus * stance_bonus * (1 + article_count_bonus)
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
    """便捷函数：计算所有文章和事件的热度分数"""
    calculator = HeatCalculator(db)
    articles_updated = calculator.update_article_heat_scores()
    events_updated = calculator.update_event_heat_scores()
    return {
        "articles_updated": articles_updated,
        "events_updated": events_updated,
    }
