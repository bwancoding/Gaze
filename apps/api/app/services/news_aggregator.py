"""
新闻聚合器 - 统一调度 RSS/Reddit/HN 抓取、去重入库、聚类、热度计算
"""
import asyncio
import logging
from typing import Dict, List
from sqlalchemy.orm import Session

from app.models.trending import TrendingArticle, TrendingSource
from app.services.trending_config import RSS_SOURCES, REDDIT_SOURCES, HN_SOURCE, ALL_SOURCES
from app.services.fetchers.rss_fetcher import RSSFetcher
from app.services.fetchers.reddit_fetcher import RedditFetcher
from app.services.fetchers.hackernews_fetcher import HackerNewsFetcher
from app.services.event_clusterer import cluster_new_articles
from app.services.heat_calculator import calculate_all_heat_scores

logger = logging.getLogger(__name__)


def ensure_sources_exist(db: Session):
    """确保所有数据源在数据库中存在"""
    for src in ALL_SOURCES:
        existing = db.query(TrendingSource).filter(TrendingSource.id == src["id"]).first()
        if not existing:
            db.add(TrendingSource(
                id=src["id"],
                name=src["name"],
                url=src.get("url", src.get("subreddit", "")),
                stance=src.get("stance", "center"),
                region=src.get("region", "international"),
                priority=src.get("priority", "P2"),
                enabled=src.get("enabled", True),
            ))
    db.commit()


def deduplicate_articles(db: Session, articles: List[TrendingArticle]) -> List[TrendingArticle]:
    """根据 URL 去重，只保留数据库中不存在的文章"""
    if not articles:
        return []

    existing_urls = set()
    urls = [a.url for a in articles]
    # 分批查询避免 SQL 过长
    batch_size = 100
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        rows = db.query(TrendingArticle.url).filter(TrendingArticle.url.in_(batch)).all()
        existing_urls.update(row[0] for row in rows)

    # Filter out DB duplicates AND within-batch duplicates (keep first occurrence)
    seen_urls = set(existing_urls)
    new_articles = []
    for a in articles:
        if a.url not in seen_urls:
            seen_urls.add(a.url)
            new_articles.append(a)
    logger.info(f"Deduplication: {len(articles)} total, {len(existing_urls)} in DB, {len(new_articles)} new")
    return new_articles


async def fetch_all_sources() -> List[TrendingArticle]:
    """从所有数据源抓取文章"""
    all_articles = []

    # RSS
    rss_fetcher = RSSFetcher()
    try:
        rss_articles = await rss_fetcher.fetch_all(
            [s for s in RSS_SOURCES if s["enabled"]]
        )
        all_articles.extend(rss_articles)
        logger.info(f"RSS: fetched {len(rss_articles)} articles")
    finally:
        await rss_fetcher.close()

    # Reddit
    reddit_fetcher = RedditFetcher()
    try:
        reddit_articles = await reddit_fetcher.fetch_all(limit=25)
        all_articles.extend(reddit_articles)
        logger.info(f"Reddit: fetched {len(reddit_articles)} articles")
    finally:
        await reddit_fetcher.close()

    # Hacker News
    hn_fetcher = HackerNewsFetcher()
    try:
        hn_articles = await hn_fetcher.fetch_top_stories(limit=30)
        all_articles.extend(hn_articles)
        logger.info(f"HN: fetched {len(hn_articles)} articles")
    finally:
        await hn_fetcher.close()

    logger.info(f"Total fetched: {len(all_articles)} articles from all sources")
    return all_articles


def run_full_pipeline(db: Session) -> Dict:
    """
    运行完整的新闻聚合管线：
    1. 确保数据源存在
    2. 抓取所有来源
    3. 去重入库
    4. 聚类
    5. 计算热度
    """
    result = {"fetch": 0, "new": 0, "cluster": {}, "heat": {}}

    # 1. 确保数据源
    ensure_sources_exist(db)

    # 2. 抓取
    articles = asyncio.run(fetch_all_sources())
    result["fetch"] = len(articles)

    # 3. 去重入库
    new_articles = deduplicate_articles(db, articles)
    for article in new_articles:
        db.add(article)
    db.commit()
    result["new"] = len(new_articles)

    # 4. 聚类
    cluster_result = cluster_new_articles(db)
    result["cluster"] = cluster_result

    # 5. 计算热度
    heat_result = calculate_all_heat_scores(db)
    result["heat"] = heat_result

    logger.info(f"Pipeline complete: {result}")
    return result


def run_heat_update(db: Session) -> Dict:
    """仅重新计算热度分数（定时任务用）"""
    return calculate_all_heat_scores(db)


def run_clustering(db: Session) -> Dict:
    """仅运行聚类（定时任务用）"""
    return cluster_new_articles(db)
