"""
News Aggregator - Orchestrates RSS/Reddit/HN fetching, dedup, clustering, heat scoring, and top-N trimming
"""
import asyncio
import logging
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.trending import TrendingArticle, TrendingEvent, TrendingSource
from app.services.trending_config import RSS_SOURCES, REDDIT_SOURCES, HN_SOURCE, ALL_SOURCES
from app.services.fetchers.rss_fetcher import RSSFetcher
from app.services.fetchers.reddit_fetcher import RedditFetcher
from app.services.fetchers.hackernews_fetcher import HackerNewsFetcher
from app.services.event_clusterer import cluster_new_articles
from app.services.heat_calculator import calculate_all_heat_scores

logger = logging.getLogger(__name__)


def ensure_sources_exist(db: Session):
    """Ensure all data sources exist in the database"""
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
    """Deduplicate by URL, only keep articles not already in the database"""
    if not articles:
        return []

    existing_urls = set()
    urls = [a.url for a in articles]
    # Query in batches to avoid overly long SQL statements
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
    """Fetch articles from all data sources"""
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


def trim_to_top_n(db: Session, top_n: int = 20) -> Dict:
    """
    Keep only the top N trending events as 'raw' (available for admin review).
    Events ranked below top N that are still 'raw' get archived automatically.
    Events already 'promoted' or 'rejected' are left untouched.

    Args:
        db: Database session
        top_n: Number of top events to keep (default 20)

    Returns:
        Stats about the trim operation
    """
    # Get top N event IDs by heat_score (only from raw status)
    top_events = (
        db.query(TrendingEvent.id)
        .filter(TrendingEvent.status == 'raw')
        .order_by(desc(TrendingEvent.heat_score))
        .limit(top_n)
        .all()
    )
    top_ids = {e.id for e in top_events}

    # Archive all raw events NOT in top N
    archived_count = (
        db.query(TrendingEvent)
        .filter(
            TrendingEvent.status == 'raw',
            ~TrendingEvent.id.in_(top_ids) if top_ids else True
        )
        .update({"status": "archived"}, synchronize_session="fetch")
    )

    db.commit()

    logger.info(f"Trim: kept top {len(top_ids)} raw events, archived {archived_count}")
    return {
        "kept": len(top_ids),
        "archived": archived_count,
    }


def run_full_pipeline(db: Session, top_n: int = 20) -> Dict:
    """
    Run the complete news aggregation pipeline:
    1. Ensure data sources exist
    2. Fetch from all sources
    3. Deduplicate and store
    4. Cluster articles into events
    5. Calculate heat scores
    6. Trim to top N events (archive the rest)

    Args:
        db: Database session
        top_n: Number of top trending events to keep for admin review (default 20)
    """
    result = {"fetch": 0, "new": 0, "cluster": {}, "heat": {}, "trim": {}}

    # 1. Ensure sources
    ensure_sources_exist(db)

    # 2. Fetch
    articles = asyncio.run(fetch_all_sources())
    result["fetch"] = len(articles)

    # 3. Deduplicate and store
    new_articles = deduplicate_articles(db, articles)
    for article in new_articles:
        db.add(article)
    db.commit()
    result["new"] = len(new_articles)

    # 4. Cluster
    cluster_result = cluster_new_articles(db)
    result["cluster"] = cluster_result

    # 5. Calculate heat
    heat_result = calculate_all_heat_scores(db)
    result["heat"] = heat_result

    # 6. Trim to top N (archive low-ranking events)
    trim_result = trim_to_top_n(db, top_n=top_n)
    result["trim"] = trim_result

    logger.info(f"Pipeline complete: {result}")
    return result


def run_heat_update(db: Session, top_n: int = 20) -> Dict:
    """Recalculate heat scores and re-trim to top N (for scheduled tasks)"""
    heat = calculate_all_heat_scores(db)
    trim = trim_to_top_n(db, top_n=top_n)
    return {"heat": heat, "trim": trim}


def run_clustering(db: Session, top_n: int = 20) -> Dict:
    """Run clustering and trim (for scheduled tasks)"""
    cluster = cluster_new_articles(db)
    trim = trim_to_top_n(db, top_n=top_n)
    return {"cluster": cluster, "trim": trim}
