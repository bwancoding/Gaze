"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import List, Dict, Optional
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "WRHITW Trending API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API 配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    WORKERS: int = 4
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://wrhitw:password@localhost:5432/wrhitw"
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 缓存配置
    CACHE_TTL_SECONDS: int = 300  # 5 分钟
    
    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # 热度算法配置
    HEAT_TIME_DECAY_LAMBDA: float = 0.1  # 时间衰减系数（每小时）
    HEAT_COMMENT_WEIGHT: float = 5.0  # 评论权重
    HEAT_SHARE_WEIGHT: float = 3.0  # 分享权重
    
    # 聚类配置
    CLUSTER_SIMILARITY_THRESHOLD: float = 0.6  # 相似度阈值
    CLUSTER_TOP_KEYWORDS: int = 20  # 关键词数量
    
    # 抓取配置
    RSS_FETCH_TIMEOUT: int = 30  # 秒
    RSS_MAX_ARTICLES_PER_FEED: int = 50  # 每个源最多抓取文章数
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()


# RSS 数据源配置列表
RSS_SOURCES: List[Dict] = [
    # P0 优先级 - 每 15-30 分钟抓取
    {
        "id": 1,
        "name": "Reuters",
        "stance": "center",
        "region": "international",
        "url": "https://www.reutersagency.com/feed/",
        "update_interval_minutes": 15,
        "priority": "P0",
        "enabled": True
    },
    {
        "id": 2,
        "name": "Associated Press",
        "stance": "center",
        "region": "international",
        "url": "https://apnews.com/apf-topnews",
        "update_interval_minutes": 15,
        "priority": "P0",
        "enabled": True
    },
    {
        "id": 3,
        "name": "BBC News",
        "stance": "center-left",
        "region": "uk",
        "url": "https://feeds.bbci.co.uk/news/rss.xml",
        "update_interval_minutes": 15,
        "priority": "P0",
        "enabled": True
    },
    {
        "id": 4,
        "name": "The Guardian",
        "stance": "left",
        "region": "uk",
        "url": "https://www.theguardian.com/uk/rss",
        "update_interval_minutes": 15,
        "priority": "P0",
        "enabled": True
    },
    {
        "id": 5,
        "name": "Financial Times",
        "stance": "center",
        "region": "uk",
        "url": "https://www.ft.com/?format=rss",
        "update_interval_minutes": 30,
        "priority": "P0",
        "enabled": True
    },
    {
        "id": 6,
        "name": "Bloomberg",
        "stance": "center",
        "region": "us",
        "url": "https://www.bloomberg.com/feed/podcast/businessweek.xml",
        "update_interval_minutes": 30,
        "priority": "P0",
        "enabled": True
    },
    # P1 优先级 - 每 30-60 分钟抓取
    {
        "id": 7,
        "name": "CNN",
        "stance": "left",
        "region": "us",
        "url": "http://rss.cnn.com/rss/edition.rss",
        "update_interval_minutes": 15,
        "priority": "P1",
        "enabled": True
    },
    {
        "id": 8,
        "name": "Fox News",
        "stance": "right",
        "region": "us",
        "url": "https://moxie.foxnews.com/google-publisher/top_stories.xml",
        "update_interval_minutes": 15,
        "priority": "P1",
        "enabled": True
    },
    {
        "id": 9,
        "name": "The New York Times",
        "stance": "left",
        "region": "us",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "update_interval_minutes": 30,
        "priority": "P1",
        "enabled": True
    },
    {
        "id": 10,
        "name": "The Wall Street Journal",
        "stance": "right",
        "region": "us",
        "url": "https://feeds.a.dj.com/rss/RSSOpinion.xml",
        "update_interval_minutes": 30,
        "priority": "P1",
        "enabled": True
    },
    {
        "id": 11,
        "name": "The Economist",
        "stance": "center-right",
        "region": "uk",
        "url": "https://www.economist.com/the-world-this-week/rss.xml",
        "update_interval_minutes": 60,
        "priority": "P1",
        "enabled": True
    },
    {
        "id": 12,
        "name": "Al Jazeera",
        "stance": "center",
        "region": "international",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "update_interval_minutes": 30,
        "priority": "P1",
        "enabled": True
    },
    # P2 优先级 - 每小时抓取
    {
        "id": 13,
        "name": "Politico",
        "stance": "center-left",
        "region": "us",
        "url": "https://www.politico.com/rss/politics08.xml",
        "update_interval_minutes": 30,
        "priority": "P2",
        "enabled": True
    },
    {
        "id": 14,
        "name": "The Hill",
        "stance": "center",
        "region": "us",
        "url": "https://thehill.com/feed/",
        "update_interval_minutes": 30,
        "priority": "P2",
        "enabled": True
    },
    {
        "id": 15,
        "name": "NPR",
        "stance": "left",
        "region": "us",
        "url": "https://feeds.npr.org/1001/rss.xml",
        "update_interval_minutes": 60,
        "priority": "P2",
        "enabled": True
    },
]


def get_sources_by_priority(priority: str = "P0") -> List[Dict]:
    """根据优先级获取数据源"""
    return [s for s in RSS_SOURCES if s["priority"] == priority and s["enabled"]]


def get_sources_by_stance(stance: str) -> List[Dict]:
    """根据政治立场获取数据源"""
    return [s for s in RSS_SOURCES if s["stance"] == stance and s["enabled"]]


def get_all_enabled_sources() -> List[Dict]:
    """获取所有启用的数据源"""
    return [s for s in RSS_SOURCES if s["enabled"]]
