"""
News Aggregator v2 - Topics First approach

Pipeline:
1. Fetch trending topics from Reddit/HN (these become event seeds)
2. Fetch articles from RSS feeds
3. Match articles to topic-events by title similarity
4. Unmatched articles with high engagement become standalone events
5. Calculate heat scores
6. Trim to top N
"""
import asyncio
import logging
import re
import math
from typing import Dict, List, Set, Optional
from collections import Counter
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.models.trending import TrendingArticle, TrendingEvent, TrendingSource
from app.services.trending_config import (
    RSS_SOURCES, REDDIT_SOURCES, HN_SOURCE, ALL_SOURCES,
    CATEGORY_KEYWORDS, CLUSTER_TOP_KEYWORDS,
)
from app.services.fetchers.rss_fetcher import RSSFetcher
from app.services.fetchers.trending_topics_fetcher import TrendingTopicsFetcher
from app.services.fetchers.google_news_fetcher import GoogleNewsFetcher
from app.services.heat_calculator import calculate_all_heat_scores

logger = logging.getLogger(__name__)

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
    'this', 'that', 'these', 'those', 'it', 'its', 'as', 'if', 'when',
    'than', 'because', 'while', 'although', 'though', 'after', 'before',
    'about', 'into', 'through', 'during', 'without', 'against', 'between',
    'not', 'only', 'own', 'same', 'so', 'just', 'also', 'now', 'very',
    'how', 'what', 'who', 'which', 'new', 'says', 'said', 'his', 'her',
}


def clean_words(text: str) -> List[str]:
    words = re.sub(r'[^a-z0-9\s]', ' ', text.lower()).split()
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def extract_keywords(text: str, top_n: int = 20) -> List[str]:
    words = clean_words(text)
    if not words:
        return []
    return [w for w, _ in Counter(words).most_common(top_n)]


def title_similarity(t1: str, t2: str) -> float:
    """Word overlap similarity between two titles"""
    words1 = set(clean_words(t1))
    words2 = set(clean_words(t2))
    if not words1 or not words2:
        return 0.0
    overlap = words1 & words2
    # Use Jaccard index for balanced comparison; min-based scoring
    # inflates scores when one title is very short (e.g. 3 words)
    min_len = min(len(words1), len(words2))
    if min_len <= 3:
        # For short titles, use Jaccard to avoid inflation
        return len(overlap) / len(words1 | words2)
    return len(overlap) / min_len


def classify_category(text: str) -> Optional[str]:
    text_lower = text.lower()
    # Use word-boundary matching for single words to avoid substring false positives
    # e.g. "ai" matching "said", "git" matching "digital"
    words = set(re.findall(r'\b[a-z0-9+#/.]+\b', text_lower))
    scores: Dict[str, float] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        matches = 0
        for kw in keywords:
            if ' ' in kw:
                # Multi-word phrases: substring match is fine
                if kw in text_lower:
                    matches += 1
            else:
                # Single words: require word boundary match
                if kw in words:
                    matches += 1
        if matches > 0:
            # Normalize by keyword count to prevent categories with more keywords
            # (e.g. Technology: 80+) from dominating over smaller categories
            scores[category] = matches / len(keywords)
    if not scores:
        return None
    return max(scores, key=scores.get)


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
    """Deduplicate by URL"""
    if not articles:
        return []

    existing_urls = set()
    urls = [a.url for a in articles]
    batch_size = 100
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        rows = db.query(TrendingArticle.url).filter(TrendingArticle.url.in_(batch)).all()
        existing_urls.update(row[0] for row in rows)

    seen_urls = set(existing_urls)
    new_articles = []
    for a in articles:
        if a.url not in seen_urls:
            seen_urls.add(a.url)
            new_articles.append(a)

    logger.info(f"Dedup: {len(articles)} total → {len(new_articles)} new")
    return new_articles


async def fetch_rss_articles() -> List[TrendingArticle]:
    """Fetch articles from RSS feeds"""
    rss_fetcher = RSSFetcher()
    try:
        articles = await rss_fetcher.fetch_all(
            [s for s in RSS_SOURCES if s["enabled"]]
        )
        logger.info(f"RSS: {len(articles)} articles")
        return articles
    finally:
        await rss_fetcher.close()


async def fetch_trending_topics() -> List[Dict]:
    """Fetch trending topics from Reddit + HN"""
    fetcher = TrendingTopicsFetcher()
    try:
        topics = await fetcher.fetch_all_trending()
        logger.info(f"Topics: {len(topics)} trending topics")
        return topics
    finally:
        await fetcher.close()


def topic_article_relevance(topic: Dict, article: TrendingArticle) -> float:
    """
    Calculate relevance between a topic and an article using multiple signals:
    1. Title word overlap (against all merged topic titles)
    2. Keyword overlap (topic keywords vs article title+summary)
    """
    article_title = article.title or ''
    article_text = f"{article_title} {article.summary or ''}"

    # Check against all titles in the merged topic group
    all_titles = topic.get('all_titles', [topic['title']])
    best_title_sim = 0.0
    for t_title in all_titles:
        sim = title_similarity(t_title, article_title)
        best_title_sim = max(best_title_sim, sim)

    # Keyword overlap: all topic words appearing in article text
    topic_text = ' '.join(all_titles)
    topic_words = set(clean_words(topic_text))
    article_words = set(clean_words(article_text))

    if not topic_words or not article_words:
        return best_title_sim

    keyword_overlap = len(topic_words & article_words) / len(topic_words)

    # Combined score: weighted average
    return best_title_sim * 0.4 + keyword_overlap * 0.6


def _get_article_category(article: TrendingArticle) -> Optional[str]:
    """Classify an article's category from its title + summary"""
    text = f"{article.title or ''} {article.summary or ''}"
    return classify_category(text)


def match_articles_to_topics(
    topics: List[Dict],
    articles: List[TrendingArticle],
    threshold: float = 0.40,
) -> Dict[int, List[TrendingArticle]]:
    """
    Match articles to topic-events by relevance scoring.
    Applies a cross-category penalty to prevent misclassification.
    Returns: {topic_index: [matched_articles]}
    """
    matches: Dict[int, List[TrendingArticle]] = {i: [] for i in range(len(topics))}
    unmatched: List[TrendingArticle] = []

    # Pre-classify topic categories
    topic_categories = []
    for topic in topics:
        all_titles = topic.get('all_titles', [topic['title']])
        combined = ' '.join(all_titles + [topic.get('selftext', '')])
        topic_categories.append(classify_category(combined))

    for article in articles:
        best_idx = -1
        best_score = 0.0
        article_cat = _get_article_category(article)

        for i, topic in enumerate(topics):
            score = topic_article_relevance(topic, article)

            # Cross-category penalty: halve score when categories don't match
            topic_cat = topic_categories[i]
            if topic_cat and article_cat and topic_cat != article_cat:
                score *= 0.5

            if score > best_score:
                best_score = score
                best_idx = i

        if best_score >= threshold and best_idx >= 0:
            matches[best_idx].append(article)
        else:
            unmatched.append(article)

    matched_count = sum(len(arts) for arts in matches.values())
    logger.info(f"Article matching: {matched_count} matched, {len(unmatched)} unmatched")

    return matches


def create_events_from_topics(
    db: Session,
    topics: List[Dict],
    topic_articles: Dict[int, List[TrendingArticle]],
    max_events: int = 20,
) -> List[TrendingEvent]:
    """Create TrendingEvent records from topics + matched articles"""
    events = []

    for i, topic in enumerate(topics):
        if len(events) >= max_events:
            break

        matched = topic_articles.get(i, [])
        all_sources = list(set(
            [topic.get('source', '')] +
            topic.get('sources', []) +
            [get_source_name(a.source_id) for a in matched]
        ))
        all_sources = [s for s in all_sources if s]

        # Build combined text for keywords and category
        texts = [topic['title'], topic.get('selftext', '')]
        texts.extend([a.title or '' for a in matched])
        texts.extend([a.summary or '' for a in matched[:5]])
        combined_text = ' '.join(texts)

        keywords = extract_keywords(combined_text, CLUSTER_TOP_KEYWORDS)
        category = classify_category(combined_text)

        # Calculate initial heat from topic engagement
        topic_heat = (
            topic.get('total_score', topic.get('score', 0)) * 0.1 +
            topic.get('total_comments', topic.get('comments', 0)) * 0.5 +
            len(matched) * 10 +
            len(all_sources) * 5
        )

        event = TrendingEvent(
            title=topic['title'],
            summary=topic.get('selftext', '')[:2000] or (matched[0].summary if matched else ''),
            keywords=keywords,
            category=category,
            source_id=topic.get('source_id', 102),
            article_count=len(matched) + 1,  # +1 for the topic itself
            media_count=len(all_sources),
            heat_score=topic_heat,
            status='raw',
        )
        db.add(event)
        db.flush()

        # Link matched articles to this event
        for article in matched:
            article.event_id = event.id
            article.is_processed = True

        events.append(event)
        logger.info(f"Event #{event.id}: '{topic['title'][:60]}' "
                     f"({len(matched)} articles, {len(all_sources)} sources, "
                     f"heat={topic_heat:.0f}, cat={category})")

    db.commit()
    return events


# Source ID → name lookup
_SOURCE_NAMES = {s['id']: s['name'] for s in ALL_SOURCES}


def get_source_name(source_id: int) -> str:
    return _SOURCE_NAMES.get(source_id, f"Source #{source_id}")


def event_article_relevance(event: TrendingEvent, article: TrendingArticle) -> float:
    """
    Calculate relevance between an existing event and an unlinked article.
    Uses event keywords + title + linked article titles for broad matching.
    """
    article_title = article.title or ''
    article_text = f"{article_title} {article.summary or ''}"
    article_words = set(clean_words(article_text))

    if not article_words:
        return 0.0

    # Build event word set from: title + keywords + linked article titles
    event_texts = [event.title or '']
    if event.keywords:
        event_texts.append(' '.join(event.keywords))
    if event.articles:
        event_texts.extend([a.title or '' for a in event.articles[:10]])
    event_words = set(clean_words(' '.join(event_texts)))

    if not event_words:
        return 0.0

    # How much of the event's vocabulary appears in the article
    overlap = event_words & article_words
    coverage = len(overlap) / len(event_words)

    # Also check title-to-title similarity
    t_sim = title_similarity(event.title or '', article_title)

    return t_sim * 0.3 + coverage * 0.7


def second_pass_matching(db: Session, events: List[TrendingEvent], threshold: float = 0.35) -> int:
    """
    Second pass: sweep all unlinked articles and try to match them to existing events
    using broader keyword matching (event keywords + linked article context).
    Applies cross-category penalty and large-cluster penalty.
    """
    unlinked = db.query(TrendingArticle).filter(
        and_(
            TrendingArticle.event_id.is_(None),
        )
    ).all()

    if not unlinked or not events:
        return 0

    matched_count = 0
    for article in unlinked:
        best_event = None
        best_score = 0.0
        article_cat = _get_article_category(article)

        for event in events:
            score = event_article_relevance(event, article)

            # Cross-category penalty
            if event.category and article_cat and event.category != article_cat:
                score *= 0.5

            # Large cluster penalty: raise bar for events with 100+ articles
            effective_threshold = threshold
            if event.article_count and event.article_count >= 100:
                effective_threshold += 0.10

            if score > best_score and score >= effective_threshold:
                best_score = score
                best_event = event

        if best_event is not None:
            article.event_id = best_event.id
            article.is_processed = True
            best_event.article_count += 1
            matched_count += 1

    # Update media counts
    for event in events:
        db.refresh(event)
        if event.articles:
            event.media_count = len(set(a.source_id for a in event.articles))
            event.article_count = len(event.articles)

    db.commit()
    logger.info(f"Second pass: {matched_count} additional articles matched from {len(unlinked)} unlinked")
    return matched_count


def trim_to_top_n(db: Session, top_n: int = 40, min_per_category: int = 2) -> Dict:
    """Keep top N raw events with per-category minimum retention"""
    all_raw = (
        db.query(TrendingEvent)
        .filter(TrendingEvent.status == 'raw')
        .order_by(desc(TrendingEvent.heat_score))
        .all()
    )
    if not all_raw:
        return {"kept": 0, "archived": 0}

    # Step 1: guarantee min_per_category per category
    keep_ids = set()
    category_counts: Dict[str, int] = {}
    for event in all_raw:
        cat = event.category or 'Uncategorized'
        count = category_counts.get(cat, 0)
        if count < min_per_category:
            keep_ids.add(event.id)
            category_counts[cat] = count + 1

    # Step 2: fill remaining slots by global heat rank
    for event in all_raw:
        if len(keep_ids) >= top_n:
            break
        keep_ids.add(event.id)

    # Step 3: archive the rest
    archived_count = 0
    if keep_ids:
        archived_count = (
            db.query(TrendingEvent)
            .filter(
                TrendingEvent.status == 'raw',
                ~TrendingEvent.id.in_(keep_ids)
            )
            .update({"status": "archived"}, synchronize_session="fetch")
        )
    db.commit()

    logger.info(f"Trim: kept {len(keep_ids)} ({len(category_counts)} categories), archived {archived_count}")
    return {"kept": len(keep_ids), "archived": archived_count}


def _select_diverse_topics(topics: List[Dict], top_n: int, min_per_source: int = 2) -> List[Dict]:
    """
    Select top_n topics ensuring each source (subreddit/HN) contributes
    at least min_per_source topics, then fill remaining by global score.
    """
    if len(topics) <= top_n:
        return topics

    selected = []
    selected_set = set()
    source_counts: Dict[str, int] = {}

    # Step 1: guarantee min_per_source from each source
    # Topics are already sorted by score desc, so first ones per source are the best
    for i, topic in enumerate(topics):
        source = topic.get('source', 'Unknown')
        count = source_counts.get(source, 0)
        if count < min_per_source:
            selected.append(topic)
            selected_set.add(i)
            source_counts[source] = count + 1

    # Step 2: fill remaining slots by global score rank
    for i, topic in enumerate(topics):
        if len(selected) >= top_n:
            break
        if i not in selected_set:
            selected.append(topic)

    return selected


def run_full_pipeline(db: Session, top_n: int = 40) -> Dict:
    """
    Topics-First Pipeline v3:
    1. Fetch trending topics from Reddit/HN
    2. For each topic, search Google News for related articles (targeted)
    3. Also fetch RSS as supplement
    4. Deduplicate, create events, link articles
    5. Second-pass match remaining RSS articles
    6. Calculate heat, trim
    """
    result = {
        "topics": 0, "google_news_articles": 0, "rss_articles": 0,
        "new_articles": 0, "events_created": 0, "heat": {}, "trim": {},
    }

    # 1. Ensure sources
    ensure_sources_exist(db)
    from app.models.trending import TrendingSource
    if not db.query(TrendingSource).filter(TrendingSource.id == 200).first():
        db.add(TrendingSource(
            id=200, name="Google News", url="https://news.google.com",
            stance="center", region="international", priority="P1", enabled=True,
        ))
        db.commit()

    # 2. Fetch trending topics
    # Use new_event_loop() so this works even when called from a thread
    # spawned by an existing event loop (e.g. FastAPI's run_in_executor)
    _loop = asyncio.new_event_loop()
    try:
        topics = _loop.run_until_complete(fetch_trending_topics())
    finally:
        _loop.close()
    result["topics"] = len(topics)
    top_topics = _select_diverse_topics(topics, top_n)
    logger.info(f"Selected {len(top_topics)} topics from {len(set(t.get('source','?') for t in top_topics))} sources")

    # 3. For each topic, search Google News + fetch RSS
    async def fetch_articles():
        gn_fetcher = GoogleNewsFetcher()
        rss_fetcher = RSSFetcher()
        try:
            topic_gn_articles = await gn_fetcher.search_topics(top_topics, max_per_topic=30)
            rss_articles = await rss_fetcher.fetch_all(
                [s for s in RSS_SOURCES if s["enabled"]]
            )
            return topic_gn_articles, rss_articles
        finally:
            await gn_fetcher.close()
            await rss_fetcher.close()

    _loop2 = asyncio.new_event_loop()
    try:
        topic_gn_articles, rss_articles = _loop2.run_until_complete(fetch_articles())
    finally:
        _loop2.close()

    total_gn = sum(len(arts) for arts in topic_gn_articles.values())
    result["google_news_articles"] = total_gn
    result["rss_articles"] = len(rss_articles)

    # 4. Deduplicate and store all articles
    all_new_articles = []
    for arts in topic_gn_articles.values():
        all_new_articles.extend(arts)
    all_new_articles.extend(rss_articles)

    new_articles = deduplicate_articles(db, all_new_articles)
    for article in new_articles:
        db.add(article)
    db.commit()
    result["new_articles"] = len(new_articles)

    # 5. Create events: link Google News articles directly to their topics
    events = []
    for i, topic in enumerate(top_topics):
        gn_arts = topic_gn_articles.get(i, [])
        gn_urls = {a.url for a in gn_arts}

        # Find stored versions by URL
        stored_articles = []
        if gn_urls:
            stored_articles = db.query(TrendingArticle).filter(
                TrendingArticle.url.in_(gn_urls)
            ).all()

        all_sources_names = list(set(
            [topic.get('source', '')] +
            topic.get('sources', []) +
            [get_source_name(a.source_id) for a in stored_articles]
        ))
        all_sources_names = [s for s in all_sources_names if s]

        texts = [topic['title'], topic.get('selftext', '')]
        for t in topic.get('all_titles', []):
            texts.append(t)
        texts.extend([a.title or '' for a in stored_articles])
        combined_text = ' '.join(texts)

        keywords = extract_keywords(combined_text, CLUSTER_TOP_KEYWORDS)
        category = classify_category(combined_text)

        topic_heat = (
            topic.get('total_score', topic.get('score', 0)) * 0.1 +
            topic.get('total_comments', topic.get('comments', 0)) * 0.5 +
            len(stored_articles) * 10 +
            len(all_sources_names) * 5
        )

        event = TrendingEvent(
            title=topic['title'],
            summary=topic.get('selftext', '')[:2000] or (
                stored_articles[0].summary if stored_articles else ''
            ),
            keywords=keywords,
            category=category,
            source_id=topic.get('source_id', 102),
            article_count=len(stored_articles) + 1,
            media_count=len(all_sources_names),
            heat_score=topic_heat,
            status='raw',
        )
        db.add(event)
        db.flush()

        for article in stored_articles:
            article.event_id = event.id
            article.is_processed = True

        events.append(event)

    db.commit()
    result["events_created"] = len(events)

    # 6. Second pass: match remaining RSS articles to events
    second_pass_count = second_pass_matching(db, events)
    result["second_pass_matched"] = second_pass_count

    # Mark remaining
    still_unprocessed = db.query(TrendingArticle).filter(
        and_(
            TrendingArticle.is_processed == False,
            TrendingArticle.event_id.is_(None),
        )
    ).all()
    for a in still_unprocessed:
        a.is_processed = True
    db.commit()

    # 7. Update final counts
    for event in events:
        db.refresh(event)
        if event.articles:
            event.article_count = len(event.articles)
            event.media_count = len(set(a.source_id for a in event.articles))
    db.commit()

    # 8. Calculate heat
    heat_result = calculate_all_heat_scores(db)
    result["heat"] = heat_result

    # 9. Trim
    trim_result = trim_to_top_n(db, top_n=top_n)
    result["trim"] = trim_result

    logger.info(f"Pipeline complete: {result}")
    return result


def reclassify_events(db: Session) -> Dict:
    """Reclassify all active events using the current classification logic"""
    events = db.query(TrendingEvent).filter(
        TrendingEvent.status.in_(['raw', 'promoted'])
    ).all()
    updated = 0
    for event in events:
        # Build text from title + keywords + article titles
        texts = [event.title or '']
        if event.keywords:
            texts.extend(event.keywords)
        articles = db.query(TrendingArticle.title).filter(
            TrendingArticle.event_id == event.id
        ).all()
        texts.extend([a.title for a in articles if a.title])
        combined = ' '.join(texts)
        new_cat = classify_category(combined)
        if new_cat != event.category:
            old_cat = event.category
            event.category = new_cat
            updated += 1
            logger.info(f"Reclassified event {event.id}: {old_cat} -> {new_cat} | {event.title[:60]}")
    db.commit()
    logger.info(f"Reclassified {updated}/{len(events)} events")
    return {"total": len(events), "updated": updated}


def run_heat_update(db: Session, top_n: int = 40) -> Dict:
    """Recalculate heat scores, reclassify, and re-trim"""
    reclass = reclassify_events(db)
    heat = calculate_all_heat_scores(db)
    trim = trim_to_top_n(db, top_n=top_n)
    return {"heat": heat, "trim": trim, "reclassified": reclass}
