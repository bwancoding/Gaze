"""
Trending API 路由 - 热榜相关端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from app.core.database import get_db
from app.models.trending import TrendingEvent, TrendingArticle, TrendingSource
from app.models import Event
from app.services.heat_calculator import HeatCalculator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/trending")
def get_trending(
    limit: int = Query(20, ge=1, le=50),
    category: Optional[str] = Query(None),
    time_window: Optional[int] = Query(None, description="Time window in hours"),
    published_only: bool = Query(False, description="Only return trending events that have been published"),
    db: Session = Depends(get_db)
):
    """获取 Top N 热榜事件"""
    if published_only:
        # 直接查询有 published event 关联的 trending events
        query = (
            db.query(TrendingEvent, Event.id.label("pub_event_id"))
            .join(Event, Event.trending_origin_id == TrendingEvent.id)
            .filter(Event.status.in_(['active', 'published']))
        )
        if category:
            query = query.filter(TrendingEvent.category == category)
        query = query.order_by(TrendingEvent.heat_score.desc()).limit(limit)
        results = query.all()

        return {
            "count": len(results),
            "events": [
                {
                    "rank": idx + 1,
                    **trending_event.to_dict(),
                    "published_event_id": str(pub_event_id),
                }
                for idx, (trending_event, pub_event_id) in enumerate(results)
            ]
        }

    # 默认：返回所有 trending events（admin 视图等）
    calculator = HeatCalculator(db)
    events = calculator.get_top_events(
        limit=limit,
        time_window_hours=time_window,
        category=category
    )

    # 查找已关联的 published events
    trending_ids = [e.id for e in events]
    published_map = {}
    if trending_ids:
        published_events = db.query(Event.trending_origin_id, Event.id).filter(
            Event.trending_origin_id.in_(trending_ids)
        ).all()
        published_map = {row[0]: str(row[1]) for row in published_events}

    return {
        "count": len(events),
        "events": [
            {
                "rank": idx + 1,
                **event.to_dict(),
                "published_event_id": published_map.get(event.id),
            }
            for idx, event in enumerate(events)
        ]
    }


@router.get("/trending/{event_id}")
def get_trending_event(event_id: int, db: Session = Depends(get_db)):
    """获取热榜事件详情（包含关联文章）"""
    event = db.query(TrendingEvent).filter(TrendingEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    articles = db.query(TrendingArticle).filter(
        TrendingArticle.event_id == event_id
    ).order_by(TrendingArticle.heat_score.desc()).all()

    return {
        **event.to_dict(),
        "articles": [a.to_dict() for a in articles],
    }


@router.get("/trending/{event_id}/articles")
def get_trending_event_articles(
    event_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取热榜事件的所有相关文章"""
    event = db.query(TrendingEvent).filter(TrendingEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    articles = db.query(TrendingArticle).filter(
        TrendingArticle.event_id == event_id
    ).order_by(TrendingArticle.heat_score.desc()).limit(limit).all()

    return {
        "event_id": event_id,
        "count": len(articles),
        "articles": [a.to_dict() for a in articles],
    }


@router.get("/trending/sources/list")
def get_trending_sources(db: Session = Depends(get_db)):
    """获取所有数据源列表"""
    sources = db.query(TrendingSource).filter(TrendingSource.enabled == True).all()
    return {
        "count": len(sources),
        "sources": [s.to_dict() for s in sources],
    }


@router.post("/trending/refresh")
def refresh_trending(db: Session = Depends(get_db)):
    """
    手动触发热榜刷新（完整管线：抓取 → 去重 → 聚类 → 热度计算）
    注意：此端点会执行网络请求，可能需要较长时间
    """
    from app.services.news_aggregator import run_full_pipeline
    try:
        result = run_full_pipeline(db)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Refresh failed: {e}")
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")


@router.post("/trending/heat/recalculate")
def recalculate_heat(db: Session = Depends(get_db)):
    """手动触发热度重新计算"""
    from app.services.heat_calculator import calculate_all_heat_scores
    result = calculate_all_heat_scores(db)
    return {"status": "success", "result": result}
