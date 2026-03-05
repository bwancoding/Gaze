"""
WRHITW Event API Routes
事件相关 API 接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models import Event, EventSource, Source, AiSummary
from app.schemas import EventResponse, EventListResponse, EventCreate, EventUpdate

router = APIRouter()


@router.get("", response_model=EventListResponse)
async def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    sort_by: str = Query("hot_score", regex="^(hot_score|created_at|view_count)$"),
    db: Session = Depends(get_db),
):
    """
    获取事件列表
    
    - **page**: 页码
    - **page_size**: 每页数量
    - **category**: 分类筛选
    - **sort_by**: 排序字段 (hot_score, created_at, view_count)
    """
    # 基础查询
    query = db.query(Event).filter(Event.status == 'active')
    
    # 分类筛选
    if category:
        query = query.filter(Event.category == category)
    
    # 总数
    total = query.count()
    
    # 排序
    if sort_by == "hot_score":
        query = query.order_by(Event.hot_score.desc())
    elif sort_by == "created_at":
        query = query.order_by(Event.created_at.desc())
    elif sort_by == "view_count":
        query = query.order_by(Event.view_count.desc())
    
    # 分页
    offset = (page - 1) * page_size
    events = query.offset(offset).limit(page_size).all()
    
    return EventListResponse(
        items=events,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    db: Session = Depends(get_db),
):
    """
    获取事件详情
    
    - **event_id**: 事件 ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    # 增加浏览次数
    event.view_count += 1
    db.commit()
    
    return event


@router.post("", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
):
    """
    创建新事件
    
    - **title**: 事件标题
    - **summary**: 事件摘要
    - **category**: 分类
    - **tags**: 标签
    """
    import json
    data = event_data.model_dump()
    
    # SQLite 需要将 tags 序列化为 JSON 字符串
    if 'tags' in data and isinstance(data['tags'], list):
        data['tags'] = json.dumps(data['tags'])
    
    event = Event(**data)
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
):
    """
    更新事件
    
    - **event_id**: 事件 ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    # 更新字段
    update_data = event_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    return event


@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    db: Session = Depends(get_db),
):
    """
    删除事件（软删除）
    
    - **event_id**: 事件 ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    # 软删除
    event.status = 'archived'
    db.commit()
    
    return {"message": "事件已删除"}


@router.get("/{event_id}/sources")
async def get_event_sources(
    event_id: str,
    db: Session = Depends(get_db),
):
    """
    获取事件的所有来源
    
    - **event_id**: 事件 ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    sources = db.query(EventSource, Source).join(
        Source, EventSource.source_id == Source.id
    ).filter(EventSource.event_id == event_id).all()
    
    return [
        {
            "id": es.id,
            "source": {
                "id": s.id,
                "name": s.name,
                "bias_label": s.bias_label,
                "bias_score": float(s.bias_score) if s.bias_score else None,
            },
            "article_title": es.article_title,
            "article_url": es.article_url,
            "published_at": es.published_at,
        }
        for es, s in sources
    ]


@router.get("/{event_id}/summary")
async def get_event_summary(
    event_id: str,
    db: Session = Depends(get_db),
):
    """
    获取事件的 AI 多视角摘要
    
    - **event_id**: 事件 ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    summary = db.query(AiSummary).filter(AiSummary.event_id == event_id).first()
    
    if not summary:
        raise HTTPException(status_code=404, detail="摘要尚未生成")
    
    return {
        "event_id": str(summary.event_id),
        "left_perspective": {
            "summary": summary.left_perspective,
            "sources": summary.left_sources or []
        },
        "center_perspective": {
            "summary": summary.center_perspective,
            "sources": summary.center_sources or []
        },
        "right_perspective": {
            "summary": summary.right_perspective,
            "sources": summary.right_sources or []
        },
        "generated_at": summary.generated_at,
    }
