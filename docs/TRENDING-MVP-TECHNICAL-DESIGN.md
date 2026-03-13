# WRHITW 热榜话题 MVP 技术方案文档

**版本**: v1.0  
**创建日期**: 2026-03-13  
**MVP 时间线**: 2 周  
**状态**: 技术方案完成

---

## 目录

1. [系统架构设计](#1-系统架构设计)
2. [数据源详细列表](#2-数据源详细列表)
3. [热度算法详细实现](#3-热度算法详细实现)
4. [事件去重与聚类算法](#4-事件去重与聚类算法)
5. [数据库表结构设计](#5-数据库表结构设计)
6. [API 设计](#6-api 设计)
7. [定时任务设计](#7-定时任务设计)
8. [性能优化策略](#8-性能优化策略)
9. [部署方案](#9-部署方案)
10. [风险评估 + 应对方案](#10-风险评估 - 应对方案)

---

## 1. 系统架构设计

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层                                 │
│                    (Web / 移动端 / API)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API 网关                                  │
│                   (FastAPI + 限流)                               │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  热榜服务     │ │   事件服务    │ │   健康检查    │
    │   Service    │ │   Service    │ │   Check      │
    └──────────────┘ └──────────────┘ └──────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      数据访问层                                  │
│                   (SQLAlchemy + Redis 缓存)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  PostgreSQL  │ │    Redis     │ │   SQLite     │
    │  (主数据库)   │ │   (缓存)     │ │  (降级方案)   │
    └──────────────┘ └──────────────┘ └──────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     后台任务                                     │
│              (APScheduler + RSS 抓取器)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RSS 源层                                     │
│         (10-15 家媒体，覆盖政治光谱)                              │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈选型

| 层级 | 技术 | 选型理由 |
|-------|------------|-----------|
| **后端框架** | FastAPI | 异步支持、自动文档、高性能 |
| **数据库** | PostgreSQL 15+ | JSONB 支持、全文搜索、可靠性高 |
| **缓存** | Redis 7+ | 高性能、丰富数据结构 |
| **任务调度** | APScheduler 3.10+ | 轻量级、灵活、支持分布式 |
| **RSS 解析** | feedparser 6.0+ | 成熟稳定、支持多格式 |
| **NLP 处理** | jieba + scikit-learn | 中文分词、TF-IDF、关键词提取 |
| **部署** | Docker + Docker Compose | 快速部署、环境隔离 |
| **监控** | Prometheus + Grafana | 开源、生态完善 |

### 1.3 核心模块拆分

```python
# 项目结构
wrhitw/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── article.py       # 文章模型
│   │   ├── event.py         # 事件聚类模型
│   │   └── source.py        # 数据源模型
│   ├── schemas/             # Pydantic 模式
│   │   ├── __init__.py
│   │   ├── article.py
│   │   ├── event.py
│   │   └── trending.py
│   ├── services/            # 业务逻辑
│   │   ├── __init__.py
│   │   ├── rss_fetcher.py   # RSS 抓取服务
│   │   ├── heat_calculator.py # 热度计算
│   │   ├── cluster.py       # 事件聚类
│   │   └── trending.py      # 热榜生成
│   ├── api/                 # API 路由
│   │   ├── __init__.py
│   │   ├── trending.py      # 热榜接口
│   │   ├── events.py        # 事件接口
│   │   └── health.py        # 健康检查
│   ├── scheduler/           # 定时任务
│   │   ├── __init__.py
│   │   └── jobs.py          # 任务定义
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── nlp.py           # NLP 工具
│       └── cache.py         # 缓存工具
├── tests/                   # 测试
├── scripts/                 # 部署脚本
├── docker-compose.yml       # Docker 配置
├── Dockerfile               # 容器镜像
└── requirements.txt         # 依赖
```

---

## 2. 数据源详细列表

### 2.1 RSS 新闻源选择原则

- **政治光谱覆盖**: 左派 (进步/自由派)、中间 (中立/平衡)、右派 (保守/传统派)
- **地理覆盖**: 国际媒体，聚焦美国、英国、欧洲及全球视角
- **语言**: 仅英文媒体
- **更新频率**: 至少每小时更新
- **RSS 质量**: 完整的标题、摘要、发布日期、链接

### 2.2 媒体源详细列表

| ID | 媒体名称 | 立场标签 | 地区 | RSS URL | 更新频率 | 优先级 |
|----|------------|--------------|--------|---------|------------------|----------|
| 1 | Reuters | 中间 | 国际 | https://www.reutersagency.com/feed/ | 15 分钟 | P0 |
| 2 | Associated Press | 中间 | 国际 | https://apnews.com/apf-topnews | 15 分钟 | P0 |
| 3 | BBC News | 中间偏左 | 英国 | https://feeds.bbci.co.uk/news/rss.xml | 15 分钟 | P0 |
| 4 | The Guardian | 左派 | 英国 | https://www.theguardian.com/uk/rss | 15 分钟 | P0 |
| 5 | Financial Times | 中间 | 英国 | https://www.ft.com/?format=rss | 30 分钟 | P0 |
| 6 | Bloomberg | 中间 | 美国 | https://www.bloomberg.com/feed/podcast/businessweek.xml | 30 分钟 | P0 |
| 7 | CNN | 左派 | 美国 | http://rss.cnn.com/rss/edition.rss | 15 分钟 | P1 |
| 8 | Fox News | 右派 | 美国 | https://moxie.foxnews.com/google-publisher/top_stories.xml | 15 分钟 | P1 |
| 9 | The New York Times | 左派 | 美国 | https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml | 30 分钟 | P1 |
| 10 | The Wall Street Journal | 右派 | 美国 | https://feeds.a.dj.com/rss/RSSOpinion.xml | 30 分钟 | P1 |
| 11 | The Economist | 中间偏右 | 英国 | https://www.economist.com/the-world-this-week/rss.xml | 1 小时 | P1 |
| 12 | Al Jazeera | 中间 | 卡塔尔 | https://www.aljazeera.com/xml/rss/all.xml | 30 分钟 | P1 |
| 13 | Politico | 中间偏左 | 美国 | https://www.politico.com/rss/politics08.xml | 30 分钟 | P2 |
| 14 | The Hill | 中间 | 美国 | https://thehill.com/feed/ | 30 分钟 | P2 |
| 15 | NPR | 左派 | 美国 | https://feeds.npr.org/1001/rss.xml | 1 小时 | P2 |

### 2.3 数据源配置代码

```python
# app/config/sources.py
from typing import List, Dict
from enum import Enum

class PoliticalStance(Enum):
    LEFT = "left"              # 左派
    CENTER_LEFT = "center-left"   # 中间偏左
    CENTER = "center"           # 中间/中立
    CENTER_RIGHT = "center-right" # 中间偏右
    RIGHT = "right"             # 右派

class Region(Enum):
    US = "us"
    UK = "uk"
    EUROPE = "europe"
    ASIA = "asia"
    INTERNATIONAL = "international"

# RSS 数据源配置列表
RSS_SOURCES: List[Dict] = [
    {
        "id": 1,
        "name": "Reuters",
        "stance": PoliticalStance.CENTER.value,
        "region": Region.INTERNATIONAL.value,
        "url": "https://www.reutersagency.com/feed/",
        "update_interval_minutes": 15,
        "priority": "P0",
        "enabled": True
    },
    {
        "id": 2,
        "name": "Associated Press",
        "stance": PoliticalStance.CENTER.value,
        "region": Region.INTERNATIONAL.value,
        "url": "https://apnews.com/apf-topnews",
        "update_interval_minutes": 15,
        "priority": "P0",
        "enabled": True
    },
    # ... 更多数据源
]

def get_sources_by_priority(priority: str = "P0") -> List[Dict]:
    """根据优先级获取数据源"""
    return [s for s in RSS_SOURCES if s["priority"] == priority and s["enabled"]]

def get_sources_by_stance(stance: str) -> List[Dict]:
    """根据政治立场获取数据源"""
    return [s for s in RSS_SOURCES if s["stance"] == stance and s["enabled"]]
```

---

## 3. 热度算法详细实现

### 3.1 热度分数公式

```
热度分数 = (基础分数 × 时间衰减 + 互动权重) × 源权重 + 传播 bonus

其中:
- 基础分数 = 100 (每篇文章初始分数)
- 时间衰减 = e^(-λ × Δt)  (λ=0.1, Δt=经过的小时数)
- 互动权重 = log(评论数 + 1) × 5 + log(分享数 + 1) × 3
- 源权重 = 源权重系数 (P0=1.5, P1=1.2, P2=1.0)
- 传播 bonus = 报道同一事件的独特媒体数量 × 10
```

### 3.2 热度计算实现代码

```python
# app/services/heat_calculator.py
import math
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.article import Article
from app.models.event import Event

class HeatCalculator:
    # 时间衰减系数 (每小时)
    TIME_DECAY_LAMBDA = 0.1
    
    # 源权重
    SOURCE_WEIGHTS = {
        "P0": 1.5,
        "P1": 1.2,
        "P2": 1.0
    }
    
    # 互动权重
    COMMENT_WEIGHT = 5.0
    SHARE_WEIGHT = 3.0
    
    @classmethod
    def calculate_article_heat(cls, article: Article, now: datetime = None) -> float:
        """计算单篇文章的热度分数"""
        if now is None:
            now = datetime.utcnow()
        
        # 1. 基础分数
        base_score = 100.0
        
        # 2. 时间衰减
        hours_elapsed = (now - article.published_at).total_seconds() / 3600
        time_decay = math.exp(-cls.TIME_DECAY_LAMBDA * hours_elapsed)
        
        # 3. 互动权重 (来自外部 API 或估算)
        interaction_bonus = (
            math.log(article.comment_count + 1) * cls.COMMENT_WEIGHT +
            math.log(article.share_count + 1) * cls.SHARE_WEIGHT
        )
        
        # 4. 源权重
        source_weight = cls.SOURCE_WEIGHTS.get(article.source_priority, 1.0)
        
        # 5. 传播 bonus (报道同一事件的媒体数量)
        spread_bonus = article.event_media_count * 10 if article.event_id else 0
        
        # 综合计算
        heat_score = (base_score * time_decay + interaction_bonus) * source_weight + spread_bonus
        
        return round(heat_score, 2)
    
    @classmethod
    def calculate_event_heat(cls, event: Event, articles: List[Article], now: datetime = None) -> float:
        """计算事件热度分数 (所有相关文章热度之和)"""
        if not articles:
            return 0.0
        
        article_heats = [cls.calculate_article_heat(a, now) for a in articles]
        
        # 事件热度 = 文章热度之和 × 媒体多样性系数
        media_diversity = len(set(a.source_id for a in articles))
        diversity_multiplier = 1 + (media_diversity - 1) * 0.1  # 每增加一家媒体 +10%
        
        total_heat = sum(article_heats) * diversity_multiplier
        
        return round(total_heat, 2)
    
    @classmethod
    def get_trending_events(cls, db: Session, limit: int = 50) -> List[Dict]:
        """获取热榜事件"""
        now = datetime.utcnow()
        
        # 获取过去 24 小时内的事件
        cutoff_time = now - timedelta(hours=24)
        events = db.query(Event).filter(
            Event.created_at >= cutoff_time
        ).all()
        
        event_heats = []
        for event in events:
            articles = event.articles
            if not articles:
                continue
            
            heat = cls.calculate_event_heat(event, articles, now)
            event_heats.append({
                "event": event,
                "heat": heat,
                "article_count": len(articles),
                "media_count": len(set(a.source_id for a in articles))
            })
        
        # 按热度分数排序
        event_heats.sort(key=lambda x: x["heat"], reverse=True)
        
        return event_heats[:limit]
```

### 3.3 热度更新策略

```python
# app/scheduler/jobs.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.heat_calculator import HeatCalculator
from app.database import get_db

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job(CronTrigger(minute='*/10'))  # 每 10 分钟更新一次
async def update_heat_scores():
    """更新所有事件的热度分数"""
    db = next(get_db())
    try:
        trending = HeatCalculator.get_trending_events(db, limit=500)
        # 缓存到 Redis
        await cache_trending_results(trending)
    finally:
        db.close()
```

---

## 4. 事件去重与聚类算法

### 4.1 算法流程

```
1. 文本预处理
   ├─ 分词 (jieba)
   ├─ 去除停用词 (英文)
   ├─ 提取关键词 (Top 20)
   └─ 生成文本向量

2. TF-IDF 向量化
   ├─ 构建语料库 (过去 24 小时所有文章)
   ├─ 计算 TF-IDF 矩阵
   └─ 降维 (可选：LSA/PCA)

3. 余弦相似度计算
   ├─ 新文章 vs 现有事件中心向量
   ├─ 相似度阈值检查 (>0.6 视为同一事件)
   └─ 归类到相似度最高的事件

4. 事件更新
   ├─ 更新事件中心向量 (增量平均)
   ├─ 添加文章到事件
   └─ 更新时间戳
```

### 4.2 聚类实现代码

```python
# app/services/cluster.py
import numpy as np
from typing import List, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba
from datetime import datetime, timedelta

class EventClusterer:
    # 相似度阈值
    SIMILARITY_THRESHOLD = 0.6
    
    # 关键词数量
    TOP_KEYWORDS = 20
    
    # 英文停用词 (因为新闻源是英文)
    STOPWORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'this', 'that', 'these', 'those', 'it', 'its', 'as', 'if', 'when',
        'than', 'because', 'while', 'although', 'though', 'after', 'before',
        'until', 'since', 'unless', 'where', 'what', 'which', 'who', 'whom',
        'whose', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
        'same', 'so', 'then', 'too', 'very', 'just', 'also', 'now'
    }
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            min_df=2
        )
        self.event_centroids = {}  # event_id -> 中心向量
        self.corpus = []  # 语料库
    
    @staticmethod
    def preprocess_text(text: str) -> str:
        """文本预处理"""
        # 由于新闻源是英文，使用简单的空格分词
        tokens = text.lower().split()
        # 去除停用词和单字符
        filtered = [w for w in tokens if w not in EventClusterer.STOPWORDS and len(w) > 1 and w.isalpha()]
        return ' '.join(filtered)
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        tokens = text.lower().split()
        filtered = [w for w in tokens if w not in self.STOPWORDS and len(w) > 1 and w.isalpha()]
        return filtered[:self.TOP_KEYWORDS]
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两篇文章的余弦相似度"""
        texts = [self.preprocess_text(text1), self.preprocess_text(text2)]
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    def find_best_cluster(
        self, 
        article_text: str, 
        events: List[dict]
    ) -> Tuple[Optional[int], float]:
        """
        查找最佳匹配的事件聚类
        
        返回:
            (event_id, similarity_score) 或 (None, 0.0) 如果没有匹配
        """
        if not events:
            return None, 0.0
        
        processed_text = self.preprocess_text(article_text)
        
        # 构建当前语料库
        event_texts = [self.preprocess_text(e['title'] + ' ' + e['summary']) for e in events]
        all_texts = event_texts + [processed_text]
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            article_vector = tfidf_matrix[-1:]
            event_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(article_vector, event_vectors)[0]
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]
            
            if best_score >= self.SIMILARITY_THRESHOLD:
                return events[best_idx]['id'], float(best_score)
            else:
                return None, float(best_score)
        except Exception as e:
            print(f"聚类错误：{e}")
            return None, 0.0
    
    def update_event_centroid(self, event_id: int, new_article_text: str, existing_vectors=None):
        """
        更新事件中心向量 (增量平均)
        
        参数:
            event_id: 事件标识符
            new_article_text: 预处理后的文章文本
            existing_vectors: 可选的现有 TF-IDF 向量用于正确转换
        """
        processed = self.preprocess_text(new_article_text)
        
        if event_id not in self.event_centroids:
            # 该事件的第一个向量 - 如果尚未完成则需要拟合向量化器
            if existing_vectors:
                self.event_centroids[event_id] = self.vectorizer.transform([processed])
            else:
                # 在单个文档上拟合 (不理想但适用于初始化)
                self.event_centroids[event_id] = self.vectorizer.fit_transform([processed])
        else:
            new_vector = self.vectorizer.transform([processed])
            # 增量平均
            old_centroid = self.event_centroids[event_id]
            self.event_centroids[event_id] = (old_centroid + new_vector) / 2
```

### 4.3 聚类服务集成

```python
# app/services/cluster_service.py
from sqlalchemy.orm import Session
from app.models.article import Article
from app.models.event import Event
from app.services.cluster import EventClusterer

class ClusterService:
    def __init__(self):
        self.clusterer = EventClusterer()
    
    def process_article(self, db: Session, article: Article) -> Event:
        """处理新文章，归类到事件或创建新事件"""
        
        # 获取过去 24 小时的活跃事件
        cutoff = datetime.utcnow() - timedelta(hours=24)
        active_events = db.query(Event).filter(
            Event.last_updated >= cutoff
        ).all()
        
        events_data = [
            {'id': e.id, 'title': e.title, 'summary': e.summary}
            for e in active_events
        ]
        
        # 查找最佳匹配事件
        article_text = article.title + ' ' + (article.summary or '')
        matched_event_id, similarity = self.clusterer.find_best_cluster(
            article_text, 
            events_data
        )
        
        if matched_event_id:
            # 添加到现有事件
            event = db.query(Event).get(matched_event_id)
            event.articles.append(article)
            event.last_updated = datetime.utcnow()
            event.article_count += 1
        else:
            # 创建新事件
            event = Event(
                title=article.title,
                summary=article.summary,
                keywords=self.clusterer.extract_keywords(article_text),
                article_count=1
            )
            event.articles.append(article)
            db.add(event)
        
        db.commit()
        return event
```

---

## 5. 数据库表结构设计

### 5.1 ER 图

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     sources     │       │     events      │       │    articles     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ name            │◄──────│ source_id (FK)  │       │ event_id (FK)   │──────►
│ url             │       │ title           │       │ source_id (FK)  │
│ stance          │       │ summary         │       │ title           │
│ region          │       │ keywords        │       │ summary         │
│ priority        │       │ heat_score      │       │ content         │
│ update_interval │       │ article_count   │       │ url             │
│ enabled         │       │ created_at      │       │ published_at    │
└─────────────────┘       │ last_updated    │       │ heat_score      │
                          └─────────────────┘       │ comment_count   │
                                    ▲               │ share_count     │
                                    │               │ created_at      │
                          ┌─────────┴────────┐      └─────────────────┘
                          │ event_articles   │
                          ├──────────────────┤
                          │ event_id (FK)    │
                          │ article_id (FK)  │
                          │ added_at         │
                          └──────────────────┘
```

### 5.2 SQLAlchemy 模型定义

```python
# app/models/source.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False, unique=True)
    stance = Column(String(20), nullable=False)  # left, center, right 等
    region = Column(String(50), nullable=False)
    priority = Column(String(10), default="P2")  # P0, P1, P2
    update_interval_minutes = Column(Integer, default=60)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    articles = relationship("Article", back_populates="source")
    events = relationship("Event", back_populates="source")
```

```python
# app/models/event.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    keywords = Column(JSONB)  # 关键词列表
    heat_score = Column(Float, default=0.0, index=True)
    article_count = Column(Integer, default=0)
    media_count = Column(Integer, default=0)  # 媒体数量
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    source = relationship("Source", back_populates="events")
    articles = relationship("Article", back_populates="event", cascade="all, delete-orphan")
    
    # 辅助属性：获取独特媒体数量
    @property
    def unique_media_count(self) -> int:
        return len(set(a.source_id for a in self.articles))
    
    # 索引
    __table_args__ = (
        Index('idx_event_heat_created', 'heat_score', 'created_at'),
    )
```

```python
# app/models/article.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    content = Column(Text)
    url = Column(String(1000), nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    heat_score = Column(Float, default=0.0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    is_processed = Column(Boolean, default=False)  # 是否已聚类/处理
    source_priority = Column(String(10), default="P2")  # P0, P1, P2 - 从源缓存以提升性能
    
    # 关系
    event = relationship("Event", back_populates="articles")
    source = relationship("Source", back_populates="articles")
    
    # 索引
    __table_args__ = (
        Index('idx_article_published_source', 'published_at', 'source_id'),
        Index('idx_article_heat', 'heat_score', 'published_at'),
    )
```

### 5.3 数据库迁移脚本

```sql
-- migrations/001_initial_schema.sql

-- 启用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 数据源表
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(500) NOT NULL UNIQUE,
    stance VARCHAR(20) NOT NULL,
    region VARCHAR(50) NOT NULL,
    priority VARCHAR(10) DEFAULT 'P2',
    update_interval_minutes INTEGER DEFAULT 60,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 事件表
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    keywords JSONB,
    heat_score FLOAT DEFAULT 0.0,
    article_count INTEGER DEFAULT 0,
    media_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_event_heat_created ON events(heat_score, created_at);
CREATE INDEX idx_event_created ON events(created_at);

-- 文章表
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id) ON DELETE SET NULL,
    source_id INTEGER REFERENCES sources(id),
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content TEXT,
    url VARCHAR(1000) NOT NULL UNIQUE,
    published_at TIMESTAMP NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    heat_score FLOAT DEFAULT 0.0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    is_processed BOOLEAN DEFAULT FALSE,
    source_priority VARCHAR(10) DEFAULT 'P2'
);

CREATE INDEX idx_article_event ON articles(event_id);
CREATE INDEX idx_article_published_source ON articles(published_at, source_id);
CREATE INDEX idx_article_heat ON articles(heat_score, published_at);
CREATE INDEX idx_article_url ON articles(url);

-- 初始化数据源
INSERT INTO sources (name, url, stance, region, priority, update_interval_minutes) VALUES
('Reuters', 'https://www.reutersagency.com/feed/', 'center', 'international', 'P0', 15),
('Associated Press', 'https://apnews.com/apf-topnews', 'center', 'international', 'P0', 15),
('BBC News', 'https://feeds.bbci.co.uk/news/rss.xml', 'center-left', 'uk', 'P0', 15),
('The Guardian', 'https://www.theguardian.com/uk/rss', 'left', 'uk', 'P0', 15),
('Financial Times', 'https://www.ft.com/?format=rss', 'center', 'uk', 'P0', 30),
('Bloomberg', 'https://www.bloomberg.com/feed/podcast/businessweek.xml', 'center', 'us', 'P0', 30),
('CNN', 'http://rss.cnn.com/rss/edition.rss', 'left', 'us', 'P1', 15),
('Fox News', 'https://moxie.foxnews.com/google-publisher/top_stories.xml', 'right', 'us', 'P1', 15),
('The New York Times', 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml', 'left', 'us', 'P1', 30),
('The Wall Street Journal', 'https://feeds.a.dj.com/rss/RSSOpinion.xml', 'right', 'us', 'P1', 30),
('The Economist', 'https://www.economist.com/the-world-this-week/rss.xml', 'center-right', 'uk', 'P1', 60),
('Al Jazeera', 'https://www.aljazeera.com/xml/rss/all.xml', 'center', 'international', 'P1', 30),
('Politico', 'https://www.politico.com/rss/politics08.xml', 'center-left', 'us', 'P2', 30),
('The Hill', 'https://thehill.com/feed/', 'center', 'us', 'P2', 30),
('NPR', 'https://feeds.npr.org/1001/rss.xml', 'left', 'us', 'P2', 60);
```

---

## 6. API 设计

### 6.1 API 概览

| 端点 | 方法 | 描述 | 认证 |
|----------|--------|-------------|------|
| `/trending/now` | GET | 获取当前热榜 | 否 |
| `/trending/:id` | GET | 获取事件详情 | 否 |
| `/trending/:id/history` | GET | 获取事件热度历史 | 否 |
| `/events` | GET | 搜索/过滤事件 | 否 |
| `/articles` | GET | 搜索文章 | 否 |
| `/sources` | GET | 获取数据源列表 | 否 |
| `/health` | GET | 健康检查 | 否 |

### 6.2 API 详细实现

```python
# app/api/trending.py
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.event import Event
from app.models.article import Article
from app.models.source import Source
from app.schemas.trending import TrendingEventResponse, EventDetailResponse
from app.services.heat_calculator import HeatCalculator
from typing import Dict

router = APIRouter(prefix="/trending", tags=["trending"])

def get_stance_distribution(articles) -> Dict[str, int]:
    """从文章源获取政治立场分布"""
    distribution = {"left": 0, "center": 0, "right": 0}
    for article in articles:
        stance = article.source.stance
        if stance in ["left", "center-left"]:
            distribution["left"] += 1
        elif stance in ["right", "center-right"]:
            distribution["right"] += 1
        else:
            distribution["center"] += 1
    return distribution

@router.get("/now", response_model=List[TrendingEventResponse])
async def get_trending_now(
    limit: int = Query(50, ge=1, le=200, description="结果数量"),
    stance: Optional[str] = Query(None, description="按政治立场过滤"),
    region: Optional[str] = Query(None, description="按地区过滤"),
    hours: int = Query(24, ge=1, le=168, description="时间范围 (小时)")
):
    """
    获取当前热榜话题
    
    - **limit**: 返回事件数量 (1-200)
    - **stance**: 按政治立场过滤 (left, center, right)
    - **region**: 按地区过滤 (us, uk, europe, asia, international)
    - **hours**: 时间范围 (1-168 小时)
    """
    db = next(get_db())
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(Event).filter(Event.created_at >= cutoff)
        
        if stance:
            # 通过相关文章和源过滤
            query = query.join(Event.articles).join(Article.source).filter(
                Source.stance == stance
            )
        
        if region:
            query = query.join(Event.articles).join(Article.source).filter(
                Source.region == region
            )
        
        events = query.order_by(Event.heat_score.desc()).limit(limit).all()
        
        # 计算实时热度
        now = datetime.utcnow()
        results = []
        for event in events:
            heat = HeatCalculator.calculate_event_heat(event, event.articles, now)
            results.append(TrendingEventResponse(
                id=event.id,
                title=event.title,
                summary=event.summary,
                keywords=event.keywords,
                heat_score=heat,
                article_count=event.article_count,
                media_count=event.media_count,
                created_at=event.created_at,
                last_updated=event.last_updated,
                stance_distribution=get_stance_distribution(event.articles)
            ))
        
        return results
    finally:
        db.close()


@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event_detail(event_id: int):
    """获取详细事件信息"""
    db = next(get_db())
    try:
        event = db.query(Event).get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="事件未找到")
        
        # 获取相关文章
        articles = sorted(
            event.articles,
            key=lambda a: a.published_at,
            reverse=True
        )[:50]  # 最多返回 50 篇文章
        
        return EventDetailResponse(
            id=event.id,
            title=event.title,
            summary=event.summary,
            keywords=event.keywords,
            heat_score=event.heat_score,
            article_count=event.article_count,
            media_count=event.media_count,
            created_at=event.created_at,
            last_updated=event.last_updated,
            articles=[
                {
                    "id": a.id,
                    "title": a.title,
                    "summary": a.summary,
                    "url": a.url,
                    "source_name": a.source.name,
                    "source_stance": a.source.stance,
                    "published_at": a.published_at,
                    "heat_score": a.heat_score
                }
                for a in articles
            ]
        )
    finally:
        db.close()


@router.get("/{event_id}/history")
async def get_event_history(
    event_id: int,
    hours: int = Query(24, ge=1, le=168)
):
    """
    获取事件热度历史
    
    返回指定小时内的热度分数变化
    """
    db = next(get_db())
    try:
        event = db.query(Event).get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="事件未找到")
        
        # 从缓存或数据库获取历史
        history = get_heat_history_from_cache(event_id, hours)
        
        return {
            "event_id": event_id,
            "title": event.title,
            "history": history
        }
    finally:
        db.close()
```

### 6.3 Pydantic 模式定义

```python
# app/schemas/trending.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ArticleBrief(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    url: str
    source_name: str
    source_stance: str
    published_at: datetime
    heat_score: float

class TrendingEventResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    keywords: Optional[List[str]]
    heat_score: float
    article_count: int
    media_count: int
    created_at: datetime
    last_updated: datetime
    stance_distribution: Dict[str, int]  # {"left": 5, "center": 3, "right": 2}
    
    class Config:
        from_attributes = True

class EventDetailResponse(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    keywords: Optional[List[str]]
    heat_score: float
    article_count: int
    media_count: int
    created_at: datetime
    last_updated: datetime
    articles: List[ArticleBrief]
    
    class Config:
        from_attributes = True

class HeatHistoryPoint(BaseModel):
    timestamp: datetime
    heat_score: float
    article_count: int

class EventHistoryResponse(BaseModel):
    event_id: int
    title: str
    history: List[HeatHistoryPoint]
```

### 6.4 API 响应示例

```json
// GET /trending/now?limit=3
{
  "data": [
    {
      "id": 1234,
      "title": "Major Policy Announcement Sparks Debate",
      "summary": "This morning, relevant authorities released new policy...",
      "keywords": ["policy", "announcement", "economy"],
      "heat_score": 2847.56,
      "article_count": 23,
      "media_count": 12,
      "created_at": "2026-03-13T08:30:00Z",
      "last_updated": "2026-03-13T16:00:00Z",
      "stance_distribution": {
        "left": 8,
        "center": 10,
        "right": 5
      }
    }
  ]
}
```

---

## 7. 定时任务设计

### 7.1 任务调度架构

```
┌─────────────────────────────────────────────────────────────┐
│                    APScheduler (异步)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   RSS 抓取器     │  │  热度更新器      │  │   清理器      │ │
│  │   (每 10-30 分钟)  │  │  (每 10 分钟)    │  │   (每日)     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   聚类服务       │  │   缓存更新       │                   │
│  │   (实时)        │  │  (每 5 分钟)      │                   │
│  └─────────────────┘  └─────────────────┘                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 任务调度实现

```python
# app/scheduler/jobs.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import asyncio
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.rss_fetcher import RSSFetcher
from app.services.cluster_service import ClusterService
from app.services.heat_calculator import HeatCalculator
from app.config.sources import RSS_SOURCES

scheduler = AsyncIOScheduler()

async def fetch_rss_feed(source: dict):
    """抓取单个 RSS 源"""
    db = next(get_db())
    try:
        fetcher = RSSFetcher()
        articles = await fetcher.fetch(source)
        
        # 处理新文章
        cluster_service = ClusterService()
        for article in articles:
            if not article.is_processed:
                cluster_service.process_article(db, article)
                article.is_processed = True
        
        db.commit()
        print(f"[{datetime.utcnow()}] 从 {source['name']} 抓取 {len(articles)} 篇文章")
    except Exception as e:
        db.rollback()
        print(f"[{datetime.utcnow()}] 抓取 {source['name']} 错误：{e}")
    finally:
        db.close()

async def fetch_all_sources():
    """抓取所有启用的数据源"""
    tasks = []
    for source in RSS_SOURCES:
        if source["enabled"]:
            tasks.append(fetch_rss_feed(source))
    
    await asyncio.gather(*tasks, return_exceptions=True)

@scheduler.scheduled_job(IntervalTrigger(minutes=10))
async def scheduled_fetch_p0():
    """抓取 P0 优先级数据源 (每 10 分钟)"""
    sources = [s for s in RSS_SOURCES if s["priority"] == "P0" and s["enabled"]]
    for source in sources:
        await fetch_rss_feed(source)

@scheduler.scheduled_job(IntervalTrigger(minutes=30))
async def scheduled_fetch_p1():
    """抓取 P1 优先级数据源 (每 30 分钟)"""
    sources = [s for s in RSS_SOURCES if s["priority"] == "P1" and s["enabled"]]
    for source in sources:
        await fetch_rss_feed(source)

@scheduler.scheduled_job(IntervalTrigger(hours=1))
async def scheduled_fetch_p2():
    """抓取 P2 优先级数据源 (每小时)"""
    sources = [s for s in RSS_SOURCES if s["priority"] == "P2" and s["enabled"]]
    for source in sources:
        await fetch_rss_feed(source)

@scheduler.scheduled_job(IntervalTrigger(minutes=10))
async def update_heat_scores():
    """更新热度分数"""
    db = next(get_db())
    try:
        trending = HeatCalculator.get_trending_events(db, limit=500)
        # 更新数据库
        for item in trending:
            event = item["event"]
            event.heat_score = item["heat"]
            event.media_count = item["media_count"]
        db.commit()
        
        # 缓存到 Redis
        await cache_trending_results(trending)
    except Exception as e:
        db.rollback()
        print(f"[{datetime.utcnow()}] 更新热度分数错误：{e}")
    finally:
        db.close()

@scheduler.scheduled_job(CronTrigger(hour=3, minute=0))  # 每日 UTC 3 AM
async def cleanup_old_data():
    """清理旧数据"""
    db = next(get_db())
    try:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=7)
        
        # 删除 7 天前的文章
        deleted = db.query(Article).filter(Article.published_at < cutoff).delete()
        
        # 删除没有文章的事件
        empty_events = db.query(Event).filter(
            Event.id.notin_(
                db.query(Article.event_id).filter(Article.event_id != None)
            )
        ).delete()
        
        db.commit()
        print(f"[{datetime.utcnow()}] 清理 {deleted} 篇文章和 {empty_events} 个事件")
    except Exception as e:
        db.rollback()
        print(f"[{datetime.utcnow()}] 清理错误：{e}")
    finally:
        db.close()

def start_scheduler():
    """启动调度器"""
    scheduler.start()
    print(f"[{datetime.utcnow()}] 调度器已启动")

def stop_scheduler():
    """停止调度器"""
    scheduler.shutdown()
    print(f"[{datetime.utcnow()}] 调度器已停止")
```

### 7.3 任务监控

```python
# app/api/health.py
from fastapi import APIRouter
from datetime import datetime
from app.scheduler.jobs import scheduler

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """健康检查"""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "scheduler_running": scheduler.running,
        "scheduled_jobs": jobs
    }
```

---

## 8. 性能优化策略

### 8.1 缓存策略

```python
# app/utils/cache.py
import redis
import json
from typing import Any, Optional
from datetime import timedelta
import asyncio

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 300  # 5 分钟
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = None
    ):
        """设置缓存"""
        ttl = ttl or self.default_ttl
        serialized = json.dumps(value, default=str)
        self.redis.setex(key, ttl, serialized)
    
    async def delete(self, key: str):
        """删除缓存"""
        self.redis.delete(key)
    
    async def cache_trending(self, limit: int, data: list):
        """缓存热榜数据"""
        key = f"trending:now:{limit}"
        await self.set(key, data, ttl=300)  # 5 分钟
    
    async def get_trending(self, limit: int) -> Optional[list]:
        """获取缓存的热榜数据"""
        key = f"trending:now:{limit}"
        return await self.get(key)
    
    async def cache_event(self, event_id: int, data: dict):
        """缓存事件详情"""
        key = f"event:{event_id}"
        await self.set(key, data, ttl=600)  # 10 分钟
    
    async def cache_heat_history(self, event_id: int, hours: int, data: list):
        """缓存热度历史"""
        key = f"event:{event_id}:history:{hours}"
        await self.set(key, data, ttl=1800)  # 30 分钟

# 全局缓存实例
cache = CacheManager()
```

### 8.2 数据库优化

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# 连接池配置
DATABASE_URL = "postgresql://user:pass@localhost/wrhitw"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # 连接池大小
    max_overflow=40,        # 最大溢出连接数
    pool_timeout=30,        # 连接获取超时
    pool_recycle=3600,      # 连接回收时间
    pool_pre_ping=True      # 使用前检查连接
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 慢查询日志
from sqlalchemy import event
import time

@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 1.0:  # 超过 1 秒的查询
        print(f"慢查询：{total:.2f}s - {statement}")
```

### 8.3 限流

```python
# app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseMiddleware
import time
from collections import defaultdict

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_history = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # 清理超过 1 分钟的记录
        self.request_history[client_ip] = [
            t for t in self.request_history[client_ip]
            if current_time - t < 60
        ]
        
        # 检查限流
        if len(self.request_history[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "请求过多",
                    "message": f"超过速率限制。最多每分钟{self.requests_per_minute}个请求。",
                    "retry_after": 60
                }
            )
        
        # 记录请求
        self.request_history[client_ip].append(current_time)
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.request_history[client_ip])
        )
        
        return response
```

### 8.4 异步并发优化

```python
# app/services/rss_fetcher.py
import aiohttp
import feedparser
from typing import List
from datetime import datetime
import asyncio

class RSSFetcher:
    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = None
    
    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def fetch(self, source: dict) -> List[dict]:
        """抓取单个 RSS 源"""
        session = await self._get_session()
        
        try:
            async with session.get(source["url"]) as response:
                if response.status != 200:
                    print(f"抓取 {source['name']} 失败：{response.status}")
                    return []
                
                content = await response.text()
                feed = feedparser.parse(content)
                
                articles = []
                for entry in feed.entries[:50]:  # 最多 50 篇文章
                    article = {
                        "title": entry.title,
                        "summary": entry.get("summary", ""),
                        "url": entry.link,
                        "published_at": self._parse_date(entry.published),
                        "source_id": source["id"],
                        "source_priority": source["priority"]
                    }
                    articles.append(article)
                
                return articles
        except Exception as e:
            print(f"抓取 {source['name']} 错误：{e}")
            return []
    
    async def fetch_all(self, sources: List[dict]) -> dict:
        """并发抓取多个源"""
        session = await self._get_session()
        tasks = [self.fetch(source) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            source["name"]: result if not isinstance(result, Exception) else []
            for source, result in zip(sources, results)
        }
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        # 实现日期解析逻辑
        pass
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
```

---

## 9. 部署方案

### 9.1 Docker 配置

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 创建非 root 用户
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://wrhitw:password@db:5432/wrhitw
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=wrhitw
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=wrhitw
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U wrhitw"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # 可选：监控
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### 9.2 环境变量配置

```bash
# .env.example
# 数据库
DATABASE_URL=postgresql://wrhitw:password@localhost:5432/wrhitw

# Redis
REDIS_URL=redis://localhost:6379/0

# 应用
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=4

# 限流
RATE_LIMIT_PER_MINUTE=60

# 缓存
CACHE_TTL_SECONDS=300

# 监控
PROMETHEUS_ENABLED=True
```

### 9.3 部署脚本

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 开始部署..."

# 1. 拉取最新代码
git pull origin main

# 2. 构建 Docker 镜像
docker-compose build

# 3. 数据库迁移
docker-compose run --rm api alembic upgrade head

# 4. 重启服务
docker-compose up -d

# 5. 健康检查
echo "等待服务健康..."
sleep 10

health_status=$(curl -s http://localhost:8000/health | jq -r '.status')
if [ "$health_status" = "healthy" ]; then
    echo "✅ 部署成功!"
else
    echo "❌ 部署失败 - 健康检查未通过"
    exit 1
fi

# 6. 查看日志
docker-compose logs -f api
```

### 9.4 Nginx 反向代理配置

```nginx
# /etc/nginx/sites-available/wrhitw
upstream wrhitw_api {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name api.wrhitw.com;
    
    location / {
        proxy_pass http://wrhitw_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 60s;
    }
    
    # 限流
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=60r/m;
    limit_req zone=api_limit burst=20 nodelay;
    
    # 日志
    access_log /var/log/nginx/wrhitw_access.log;
    error_log /var/log/nginx/wrhitw_error.log;
}
```

---

## 10. 风险评估 + 应对方案

### 10.1 技术风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|------------|--------|------------|
| **RSS 源故障** | 高 | 高 | 1. 实现源健康监控，自动禁用故障源<br>2. 准备备用 RSS URL<br>3. 支持手动添加源 |
| **聚类算法不准确** | 中 | 中 | 1. 提供人工审核界面<br>2. 支持手动合并/拆分事件<br>3. 持续优化 TF-IDF 参数 |
| **数据库性能瓶颈** | 中 | 高 | 1. 实现读写分离<br>2. 添加数据库索引<br>3. 定期归档旧数据<br>4. 考虑分库分表 |
| **Redis 缓存穿透** | 低 | 中 | 1. 实现布隆过滤器<br>2. 缓存空值 (短 TTL)<br>3. 限流保护 |
| **并发抓取导致 IP 被封** | 中 | 高 | 1. 实现请求间隔控制<br>2. 使用代理池<br>3. 遵守 robots.txt |

### 10.2 运营风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|------------|--------|------------|
| **政治敏感内容** | 高 | 非常高 | 1. 建立关键词过滤机制<br>2. 热榜事件人工审核<br>3. 准备应急响应流程<br>4. 合规审查 |
| **数据源偏见** | 中 | 中 | 1. 明确标注媒体立场<br>2. 确保光谱平衡 (左/中/右比例)<br>3. 用户可调整权重 |
| **热度算法被操纵** | 低 | 高 | 1. 限制单一源权重<br>2. 检测异常流量模式<br>3. 多因素验证 |

### 10.3 法律与合规风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|------------|--------|------------|
| **版权侵权** | 中 | 高 | 1. 仅抓取标题 + 摘要<br>2. 链接到原文<br>3. 遵循合理使用原则<br>4. 准备 DMCA 响应流程 |
| **数据隐私** | 低 | 高 | 1. 不收集个人用户信息<br>2. 遵守 GDPR/隐私法<br>3. 发布隐私政策 |
| **内容审核责任** | 中 | 非常高 | 1. 明确平台定位 (信息聚合器)<br>2. 建立举报机制<br>3. 快速响应删除请求 |

### 10.4 应急响应方案

```python
# app/emergency.py
from typing import List
from datetime import datetime

class EmergencyResponse:
    """应急响应处理"""
    
    @staticmethod
    async def disable_source(source_id: int, reason: str):
        """紧急禁用数据源"""
        # 实现逻辑
        pass
    
    @staticmethod
    async def purge_event(event_id: int, reason: str):
        """紧急删除事件"""
        # 实现逻辑
        pass
    
    @staticmethod
    async def enable_maintenance_mode():
        """启用维护模式"""
        # 返回固定响应，停止所有后台任务
        pass
    
    @staticmethod
    async def notify_admins(message: str):
        """通知管理员"""
        # 发送邮件/短信/钉钉通知
        pass

# 紧急联系人
EMERGENCY_CONTACTS = [
    {"name": "技术负责人", "phone": "+1-xxx", "email": "tech@wrhitw.com"},
    {"name": "运营负责人", "phone": "+1-xxx", "email": "ops@wrhitw.com"},
    {"name": "法律顾问", "phone": "+1-xxx", "email": "legal@wrhitw.com"}
]
```

### 10.5 监控与告警

```yaml
# monitoring/alerts.yml
groups:
  - name: wrhitw_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "高错误率"
          description: "API 错误率超过 10%"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "高响应时间"
          description: "P95 响应时间超过 2 秒"
      
      - alert: RSSFetchFailure
        expr: rate(rss_fetch_failures_total[5m]) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "RSS 抓取失败"
          description: "RSS 抓取失败率过高"
      
      - alert: DatabaseConnectionsHigh
        expr: pg_stat_activity_count > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "数据库连接数过高"
      
      - alert: CacheHitRateLow
        expr: redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total) < 0.8
        for: 10m
        labels:
          severity: warning
          description: "缓存命中率低于 80%"
```

---

## 附录

### A. 依赖列表

```txt
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
redis==5.0.1
apscheduler==3.10.4
feedparser==6.0.10
scikit-learn==1.4.0
jieba==0.42.1
numpy==1.26.3
pandas==2.1.4
aiohttp==3.9.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6
prometheus-client==0.19.0
```

### B. 开发时间线 (2 周 MVP)

| 阶段 | 时间 | 任务 | 交付物 |
|-------|------|-------|--------------|
| **阶段 1** | 第 1-2 天 | 项目初始化、数据库设计、基础设施 | 项目骨架、DB Schema |
| **阶段 2** | 第 3-5 天 | RSS 抓取、文章存储、基础 API | 可运行的抓取系统 |
| **阶段 3** | 第 6-8 天 | 事件聚类算法、热度计算 | 聚类 + 热度功能 |
| **阶段 4** | 第 9-10 天 | 热榜 API、缓存优化 | 完整 API |
| **阶段 5** | 第 11-12 天 | 定时任务、监控、部署 | 生产就绪 |
| **阶段 6** | 第 13-14 天 | 测试、文档、调优 | MVP 发布 |

### C. 测试策略

```python
# tests/test_trending.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_trending_now():
    """测试获取当前热榜"""
    response = client.get("/trending/now?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10

def test_get_event_detail():
    """测试获取事件详情"""
    response = client.get("/trending/1")
    assert response.status_code in [200, 404]

def test_rate_limiting():
    """测试限流"""
    # 快速发送 100 个请求
    for i in range(100):
        response = client.get("/trending/now")
        if response.status_code == 429:
            break
    assert response.status_code == 429
```

---

**文档结束**

*最后更新：2026-03-13*  
*作者：小狗 (AI 项目经理)*  
*状态：技术方案完成，等待开发实施*
