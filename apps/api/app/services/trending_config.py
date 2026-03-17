"""
Trending 配置 - 热度算法参数、RSS 数据源列表
"""
from typing import List, Dict
import os

# 热度算法配置
HEAT_TIME_DECAY_LAMBDA: float = float(os.getenv("HEAT_TIME_DECAY_LAMBDA", "0.1"))
HEAT_COMMENT_WEIGHT: float = float(os.getenv("HEAT_COMMENT_WEIGHT", "5.0"))
HEAT_SHARE_WEIGHT: float = float(os.getenv("HEAT_SHARE_WEIGHT", "3.0"))

# 聚类配置
CLUSTER_SIMILARITY_THRESHOLD: float = float(os.getenv("CLUSTER_SIMILARITY_THRESHOLD", "0.75"))
CLUSTER_TOP_KEYWORDS: int = int(os.getenv("CLUSTER_TOP_KEYWORDS", "20"))

# RSS 抓取配置
RSS_FETCH_TIMEOUT: int = int(os.getenv("RSS_FETCH_TIMEOUT", "30"))
RSS_MAX_ARTICLES_PER_FEED: int = int(os.getenv("RSS_MAX_ARTICLES_PER_FEED", "50"))

# RSS 数据源配置列表
RSS_SOURCES: List[Dict] = [
    # P0 优先级 - 权威媒体
    {"id": 1, "name": "Reuters", "stance": "center", "region": "international",
     "url": "https://www.reutersagency.com/feed/", "priority": "P0", "enabled": True},
    {"id": 2, "name": "Associated Press", "stance": "center", "region": "international",
     "url": "https://apnews.com/apf-topnews", "priority": "P0", "enabled": True},
    {"id": 3, "name": "BBC News", "stance": "center-left", "region": "uk",
     "url": "https://feeds.bbci.co.uk/news/rss.xml", "priority": "P0", "enabled": True},
    {"id": 4, "name": "The Guardian", "stance": "left", "region": "uk",
     "url": "https://www.theguardian.com/uk/rss", "priority": "P0", "enabled": True},
    {"id": 5, "name": "Financial Times", "stance": "center", "region": "uk",
     "url": "https://www.ft.com/?format=rss", "priority": "P0", "enabled": True},
    {"id": 6, "name": "Bloomberg", "stance": "center", "region": "us",
     "url": "https://www.bloomberg.com/feed/podcast/businessweek.xml", "priority": "P0", "enabled": True},
    # P1 优先级 - 主流媒体
    {"id": 7, "name": "CNN", "stance": "left", "region": "us",
     "url": "http://rss.cnn.com/rss/edition.rss", "priority": "P1", "enabled": True},
    {"id": 8, "name": "Fox News", "stance": "right", "region": "us",
     "url": "https://moxie.foxnews.com/google-publisher/top_stories.xml", "priority": "P1", "enabled": True},
    {"id": 9, "name": "The New York Times", "stance": "left", "region": "us",
     "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", "priority": "P1", "enabled": True},
    {"id": 10, "name": "The Wall Street Journal", "stance": "right", "region": "us",
     "url": "https://feeds.a.dj.com/rss/RSSOpinion.xml", "priority": "P1", "enabled": True},
    {"id": 11, "name": "The Economist", "stance": "center-right", "region": "uk",
     "url": "https://www.economist.com/the-world-this-week/rss.xml", "priority": "P1", "enabled": True},
    {"id": 12, "name": "Al Jazeera", "stance": "center", "region": "international",
     "url": "https://www.aljazeera.com/xml/rss/all.xml", "priority": "P1", "enabled": True},
    # P2 优先级 - 其他媒体
    {"id": 13, "name": "Politico", "stance": "center-left", "region": "us",
     "url": "https://www.politico.com/rss/politics08.xml", "priority": "P2", "enabled": True},
    {"id": 14, "name": "The Hill", "stance": "center", "region": "us",
     "url": "https://thehill.com/feed/", "priority": "P2", "enabled": True},
    {"id": 15, "name": "NPR", "stance": "left", "region": "us",
     "url": "https://feeds.npr.org/1001/rss.xml", "priority": "P2", "enabled": True},
]

# Reddit 源（source_id 101-104）
REDDIT_SOURCES = [
    {"id": 101, "name": "Reddit r/all", "stance": "center", "region": "international",
     "subreddit": "all", "priority": "P1", "enabled": True},
    {"id": 102, "name": "Reddit r/worldnews", "stance": "center", "region": "international",
     "subreddit": "worldnews", "priority": "P1", "enabled": True},
    {"id": 103, "name": "Reddit r/news", "stance": "center", "region": "us",
     "subreddit": "news", "priority": "P1", "enabled": True},
    {"id": 104, "name": "Reddit r/technology", "stance": "center", "region": "international",
     "subreddit": "technology", "priority": "P1", "enabled": True},
]

# Hacker News 源（source_id 105）
HN_SOURCE = {"id": 105, "name": "Hacker News", "stance": "center", "region": "international",
             "priority": "P1", "enabled": True}

ALL_SOURCES = RSS_SOURCES + REDDIT_SOURCES + [HN_SOURCE]


def get_sources_by_priority(priority: str = "P0") -> List[Dict]:
    return [s for s in RSS_SOURCES if s["priority"] == priority and s["enabled"]]


def get_all_enabled_sources() -> List[Dict]:
    return [s for s in RSS_SOURCES if s["enabled"]]
