"""
热度算法服务 - 计算文章和事件的热度分数

功能：
- 时间衰减函数（越新的事件热度越高）
- 互动权重计算（讨论量、转发量等）
- 源优先级加权（权威媒体权重更高）
- Top20 筛选逻辑
- 排序算法
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
import math

from app.models.article import Article
from app.models.event import Event
from app.models.source import Source
from app.config import settings


class HeatCalculator:
    """热度计算器"""
    
    # 源优先级权重（P0 权威媒体权重最高）
    SOURCE_PRIORITY_WEIGHTS = {
        "P0": 1.5,  # 权威媒体：Reuters, AP, BBC 等
        "P1": 1.2,  # 主流媒体：CNN, NYT, WSJ 等
        "P2": 1.0,  # 其他媒体
    }
    
    # 政治立场多样性系数（用于事件热度）
    STANCE_DIVERSITY_BONUS = {
        1: 1.0,   # 仅 1 种立场
        2: 1.1,   # 2 种立场
        3: 1.2,   # 3 种立场
        4: 1.25,  # 4 种立场
        5: 1.3,   # 5 种立场（全覆盖）
    }
    
    def __init__(self, db: Session):
        """
        初始化热度计算器
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.time_decay_lambda = settings.HEAT_TIME_DECAY_LAMBDA
        self.comment_weight = settings.HEAT_COMMENT_WEIGHT
        self.share_weight = settings.HEAT_SHARE_WEIGHT
    
    def calculate_time_decay(self, published_at: datetime, reference_time: Optional[datetime] = None) -> float:
        """
        计算时间衰减因子
        
        使用指数衰减函数：decay = e^(-λ * hours)
        越新的文章衰减少，热度越高
        
        Args:
            published_at: 文章发布时间
            reference_time: 参考时间（默认为当前时间）
            
        Returns:
            时间衰减因子（0-1 之间）
        """
        if reference_time is None:
            reference_time = datetime.utcnow()
        
        # 计算时间差（小时）
        time_diff = reference_time - published_at
        hours = max(0, time_diff.total_seconds() / 3600)
        
        # 指数衰减
        decay = math.exp(-self.time_decay_lambda * hours)
        
        return decay
    
    def calculate_interaction_score(self, comment_count: int = 0, share_count: int = 0) -> float:
        """
        计算互动分数
        
        互动分数 = 评论数 * 评论权重 + 分享数 * 分享权重
        使用对数缩放避免极端值
        
        Args:
            comment_count: 评论数
            share_count: 分享数
            
        Returns:
            互动分数
        """
        # 使用对数缩放，避免极端值主导
        # log10(x+1) 确保 0 互动时得分为 0
        comment_score = math.log10(comment_count + 1) * self.comment_weight
        share_score = math.log10(share_count + 1) * self.share_weight
        
        return comment_score + share_score
    
    def get_source_weight(self, source_id: int) -> float:
        """
        获取源权重
        
        根据源优先级返回权重系数
        
        Args:
            source_id: 源 ID
            
        Returns:
            权重系数
        """
        source = self.db.query(Source).filter(Source.id == source_id).first()
        if not source:
            return 1.0
        
        priority = source.priority
        return self.SOURCE_PRIORITY_WEIGHTS.get(priority, 1.0)
    
    def calculate_article_heat(self, article: Article, reference_time: Optional[datetime] = None) -> float:
        """
        计算单篇文章的热度分数
        
        热度 = 时间衰减 * (基础分 + 互动分) * 源权重
        
        Args:
            article: 文章对象
            reference_time: 参考时间
            
        Returns:
            热度分数
        """
        # 时间衰减
        time_decay = self.calculate_time_decay(article.published_at, reference_time)
        
        # 互动分数
        interaction_score = self.calculate_interaction_score(
            article.comment_count,
            article.share_count
        )
        
        # 源权重
        source_weight = self.get_source_weight(article.source_id)
        
        # 基础分（固定值，确保新文章有基础热度）
        base_score = 10.0
        
        # 计算最终热度
        heat_score = time_decay * (base_score + interaction_score) * source_weight
        
        return round(heat_score, 2)
    
    def calculate_event_heat(self, event: Event, reference_time: Optional[datetime] = None) -> float:
        """
        计算事件的热度分数
        
        事件热度 = 文章热度总和 * 媒体多样性系数 * 时间衰减
        
        Args:
            event: 事件对象
            reference_time: 参考时间
            
        Returns:
            事件热度分数
        """
        if not event.articles:
            return 0.0
        
        # 计算所有文章的热度总和
        total_article_heat = sum(
            self.calculate_article_heat(article, reference_time)
            for article in event.articles
        )
        
        # 媒体多样性系数（报道媒体越多，事件越重要）
        media_count = event.unique_media_count
        media_diversity_bonus = 1.0 + (media_count - 1) * 0.1  # 每多一家媒体 +10%
        media_diversity_bonus = min(media_diversity_bonus, 2.0)  # 上限 2 倍
        
        # 政治立场多样性
        stances = set()
        for article in event.articles:
            if article.source:
                stances.add(article.source.stance)
        
        stance_bonus = self.STANCE_DIVERSITY_BONUS.get(len(stances), 1.3)
        
        # 文章数量系数（报道文章越多越重要）
        article_count_bonus = math.log10(event.article_count + 1) * 0.5
        
        # 计算最终事件热度
        event_heat = total_article_heat * media_diversity_bonus * stance_bonus * (1 + article_count_bonus)
        
        return round(event_heat, 2)
    
    def update_article_heat_scores(self, batch_size: int = 100) -> int:
        """
        批量更新所有文章的热度分数
        
        Args:
            batch_size: 批量处理大小
            
        Returns:
            更新的文章数量
        """
        # 获取未处理或需要更新的文章
        articles = self.db.query(Article).order_by(desc(Article.published_at)).limit(batch_size).all()
        
        updated_count = 0
        for article in articles:
            new_heat = self.calculate_article_heat(article)
            
            # 只有当热度变化超过 1% 时才更新
            if abs(new_heat - (article.heat_score or 0)) > 0.01:
                article.heat_score = new_heat
                updated_count += 1
        
        self.db.commit()
        return updated_count
    
    def update_event_heat_scores(self, batch_size: int = 50) -> int:
        """
        批量更新所有事件的热度分数
        
        Args:
            batch_size: 批量处理大小
            
        Returns:
            更新的事件数量
        """
        events = self.db.query(Event).order_by(desc(Event.created_at)).limit(batch_size).all()
        
        updated_count = 0
        for event in events:
            # 刷新会话以获取最新的文章数据
            self.db.refresh(event)
            
            new_heat = self.calculate_event_heat(event)
            
            # 只有当热度变化超过 1% 时才更新
            if abs(new_heat - (event.heat_score or 0)) > 0.01:
                event.heat_score = new_heat
                updated_count += 1
        
        self.db.commit()
        return updated_count
    
    def get_top_events(self, limit: int = 20, time_window_hours: Optional[int] = None) -> List[Event]:
        """
        获取 Top N 热门事件
        
        Args:
            limit: 返回数量（默认 20）
            time_window_hours: 时间窗口（小时），None 表示不限制
            
        Returns:
            热门事件列表
        """
        query = self.db.query(Event).filter(Event.heat_score > 0)
        
        # 时间窗口过滤
        if time_window_hours:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            query = query.filter(Event.created_at >= cutoff_time)
        
        # 按热度排序，取 Top N
        events = query.order_by(desc(Event.heat_score)).limit(limit).all()
        
        return events
    
    def get_top_articles(self, limit: int = 50, time_window_hours: Optional[int] = None) -> List[Article]:
        """
        获取 Top N 热门文章
        
        Args:
            limit: 返回数量（默认 50）
            time_window_hours: 时间窗口（小时），None 表示不限制
            
        Returns:
            热门文章列表
        """
        query = self.db.query(Article).filter(Article.heat_score > 0)
        
        # 时间窗口过滤
        if time_window_hours:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            query = query.filter(Article.published_at >= cutoff_time)
        
        # 按热度排序，取 Top N
        articles = query.order_by(desc(Article.heat_score)).limit(limit).all()
        
        return articles
    
    def get_trending_events(self, limit: int = 20, time_window_hours: int = 24) -> List[Tuple[Event, float]]:
        """
        获取 trending 事件（热度增长最快的）
        
        计算最近 time_window_hours 内的热度增长率
        
        Args:
            limit: 返回数量
            time_window_hours: 时间窗口
            
        Returns:
            (事件，热度增长率) 列表
        """
        # 获取时间窗口内的事件
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        events = self.db.query(Event).filter(
            and_(
                Event.created_at >= cutoff_time,
                Event.heat_score > 0
            )
        ).all()
        
        trending = []
        for event in events:
            # 计算时间衰减后的"预期热度"
            time_decay = self.calculate_time_decay(event.created_at)
            expected_heat = event.heat_score / max(time_decay, 0.01)
            
            # 热度增长率 = 实际热度 / 预期热度
            growth_rate = event.heat_score / max(expected_heat, 0.01)
            
            trending.append((event, growth_rate))
        
        # 按增长率排序
        trending.sort(key=lambda x: x[1], reverse=True)
        
        return trending[:limit]
    
    def calculate_heat_distribution(self) -> Dict:
        """
        计算热度分布统计
        
        Returns:
            热度分布统计信息
        """
        from sqlalchemy import func
        
        # 文章热度统计
        article_stats = self.db.query(
            func.min(Article.heat_score),
            func.max(Article.heat_score),
            func.avg(Article.heat_score),
            func.count(Article.id)
        ).filter(Article.heat_score > 0).first()
        
        # 事件热度统计
        event_stats = self.db.query(
            func.min(Event.heat_score),
            func.max(Event.heat_score),
            func.avg(Event.heat_score),
            func.count(Event.id)
        ).filter(Event.heat_score > 0).first()
        
        return {
            "articles": {
                "min": article_stats[0] or 0,
                "max": article_stats[1] or 0,
                "avg": article_stats[2] or 0,
                "count": article_stats[3] or 0,
            },
            "events": {
                "min": event_stats[0] or 0,
                "max": event_stats[1] or 0,
                "avg": event_stats[2] or 0,
                "count": event_stats[3] or 0,
            },
        }


def calculate_all_heat_scores(db: Session) -> Dict:
    """
    计算所有文章和事件的热度分数（便捷函数）
    
    Args:
        db: 数据库会话
        
    Returns:
        计算结果统计
    """
    calculator = HeatCalculator(db)
    
    # 更新文章热度
    articles_updated = calculator.update_article_heat_scores()
    
    # 更新事件热度
    events_updated = calculator.update_event_heat_scores()
    
    # 获取热度分布
    distribution = calculator.calculate_heat_distribution()
    
    return {
        "articles_updated": articles_updated,
        "events_updated": events_updated,
        "distribution": distribution,
    }
