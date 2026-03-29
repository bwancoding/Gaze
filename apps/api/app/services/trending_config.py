"""
Trending configuration - heat algorithm parameters, RSS source list
"""
from typing import List, Dict
import os

# Heat algorithm configuration
HEAT_TIME_DECAY_LAMBDA: float = float(os.getenv("HEAT_TIME_DECAY_LAMBDA", "0.1"))
HEAT_COMMENT_WEIGHT: float = float(os.getenv("HEAT_COMMENT_WEIGHT", "5.0"))
HEAT_SHARE_WEIGHT: float = float(os.getenv("HEAT_SHARE_WEIGHT", "3.0"))

# Category weights: boost global-impact topics, reduce niche/entertainment
CATEGORY_WEIGHTS: Dict[str, float] = {
    "Geopolitics": 1.4,
    "Politics": 1.3,
    "Environment": 1.3,
    "Economy": 1.2,
    "Health": 1.2,
    "Science": 1.1,
    "Technology": 1.0,
    "Society": 1.0,
    "Culture": 0.8,
    "Entertainment": 0.7,
    "Sports": 0.7,
}
CATEGORY_DEFAULT_WEIGHT: float = 0.9  # uncategorized events get a slight penalty

# Region diversity: events covered by sources from multiple regions get a bonus
REGION_DIVERSITY_BONUS: Dict[int, float] = {
    1: 1.0,    # single region
    2: 1.15,   # 2 regions
    3: 1.3,    # 3 regions (truly global)
}
REGION_DIVERSITY_MAX: float = 1.4  # 4+ regions

# Cap article count influence to prevent niche topics with bot-amplified article counts
ARTICLE_COUNT_BONUS_CAP: float = 1.5  # max multiplier from article count

# Auto-categorization keyword rules
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Geopolitics": ["war", "sanctions", "treaty", "nato", "military", "invasion", "diplomacy", "nuclear", "missile", "ceasefire", "troops", "geopolitical"],
    "Politics": ["election", "vote", "president", "congress", "parliament", "legislation", "senator", "democrat", "republican", "policy", "campaign", "impeach"],
    "Environment": ["climate", "carbon", "emissions", "wildfire", "drought", "flood", "hurricane", "earthquake", "tsunami", "pollution", "deforestation", "renewable", "rainforest"],
    "Economy": ["gdp", "inflation", "recession", "trade", "tariff", "stock", "market", "unemployment", "fed", "interest rate", "cryptocurrency", "bitcoin", "semiconductor", "supply chain"],
    "Technology": ["ai", "artificial intelligence", "quantum", "spacex", "starship", "robot", "chip", "software", "cyber", "hack", "data breach", "startup"],
    "Health": ["vaccine", "pandemic", "virus", "malaria", "cancer", "drug", "fda", "who", "disease", "outbreak", "hospital", "medical"],
    "Science": ["nasa", "research", "discovery", "species", "genome", "physics", "cern", "space", "telescope", "mars", "moon"],
    "Society": ["protest", "rights", "inequality", "migration", "refugee", "poverty", "education", "housing"],
    "Entertainment": ["movie", "film", "oscar", "grammy", "celebrity", "album", "concert", "netflix", "streaming", "box office"],
    "Sports": ["olympic", "world cup", "championship", "tournament", "league", "soccer", "football", "basketball", "tennis"],
}

# Clustering configuration
CLUSTER_SIMILARITY_THRESHOLD: float = float(os.getenv("CLUSTER_SIMILARITY_THRESHOLD", "0.75"))
CLUSTER_TOP_KEYWORDS: int = int(os.getenv("CLUSTER_TOP_KEYWORDS", "20"))

# RSS fetch configuration
RSS_FETCH_TIMEOUT: int = int(os.getenv("RSS_FETCH_TIMEOUT", "30"))
RSS_MAX_ARTICLES_PER_FEED: int = int(os.getenv("RSS_MAX_ARTICLES_PER_FEED", "100"))

# RSS source configuration list
RSS_SOURCES: List[Dict] = [
    # P0 priority - authoritative media
    {"id": 1, "name": "Reuters", "stance": "center", "region": "international",
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:reuters.com&ceid=US:en&hl=en-US&gl=US", "priority": "P0", "enabled": True},
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
    # P1 priority - mainstream media
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
    # P2 priority - other media
    {"id": 13, "name": "Politico", "stance": "center-left", "region": "us",
     "url": "https://www.politico.com/rss/politics08.xml", "priority": "P2", "enabled": True},
    {"id": 14, "name": "The Hill", "stance": "center", "region": "us",
     "url": "https://thehill.com/feed/", "priority": "P2", "enabled": True},
    {"id": 15, "name": "NPR", "stance": "left", "region": "us",
     "url": "https://feeds.npr.org/1001/rss.xml", "priority": "P2", "enabled": True},
    # Additional sources for broader coverage
    {"id": 16, "name": "BBC World", "stance": "center-left", "region": "uk",
     "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "priority": "P0", "enabled": True},
    {"id": 17, "name": "Reuters World", "stance": "center", "region": "international",
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:reuters.com+world&ceid=US:en&hl=en-US&gl=US", "priority": "P0", "enabled": True},
    {"id": 18, "name": "Guardian World", "stance": "left", "region": "uk",
     "url": "https://www.theguardian.com/world/rss", "priority": "P1", "enabled": True},
    {"id": 19, "name": "CNN World", "stance": "left", "region": "us",
     "url": "http://rss.cnn.com/rss/edition_world.rss", "priority": "P1", "enabled": True},
    {"id": 20, "name": "ABC News", "stance": "center-left", "region": "us",
     "url": "https://abcnews.go.com/abcnews/topstories", "priority": "P1", "enabled": True},
    {"id": 21, "name": "CBS News", "stance": "center-left", "region": "us",
     "url": "https://www.cbsnews.com/latest/rss/main", "priority": "P1", "enabled": True},
    {"id": 22, "name": "Sky News", "stance": "center", "region": "uk",
     "url": "https://feeds.skynews.com/feeds/rss/world.xml", "priority": "P2", "enabled": True},
    {"id": 23, "name": "France24", "stance": "center", "region": "europe",
     "url": "https://www.france24.com/en/rss", "priority": "P2", "enabled": True},
    {"id": 24, "name": "DW News", "stance": "center", "region": "europe",
     "url": "https://rss.dw.com/rdf/rss-en-all", "priority": "P2", "enabled": True},
    {"id": 25, "name": "The Independent", "stance": "center-left", "region": "uk",
     "url": "https://www.independent.co.uk/news/world/rss", "priority": "P2", "enabled": True},
    {"id": 26, "name": "South China Morning Post", "stance": "center", "region": "asia",
     "url": "https://www.scmp.com/rss/91/feed", "priority": "P2", "enabled": True},
    {"id": 27, "name": "Times of India", "stance": "center", "region": "asia",
     "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "priority": "P2", "enabled": True},
    {"id": 28, "name": "NHK World", "stance": "center", "region": "asia",
     "url": "https://www3.nhk.or.jp/rss/news/cat0.xml", "priority": "P2", "enabled": True},
]

# Reddit sources (source_id 101-104)
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

# Hacker News source (source_id 105)
HN_SOURCE = {"id": 105, "name": "Hacker News", "stance": "center", "region": "international",
             "priority": "P1", "enabled": True}

ALL_SOURCES = RSS_SOURCES + REDDIT_SOURCES + [HN_SOURCE]


def get_sources_by_priority(priority: str = "P0") -> List[Dict]:
    return [s for s in RSS_SOURCES if s["priority"] == priority and s["enabled"]]


def get_all_enabled_sources() -> List[Dict]:
    return [s for s in RSS_SOURCES if s["enabled"]]
