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
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm.attributes import flag_modified

from app.models.trending import TrendingArticle, TrendingEvent, TrendingSource
from app.services.trending_config import (
    RSS_SOURCES, REDDIT_SOURCES, HN_SOURCE, ALL_SOURCES,
    CATEGORY_KEYWORDS, CLUSTER_TOP_KEYWORDS,
)
from app.services.fetchers.rss_fetcher import RSSFetcher
from app.services.fetchers.trending_topics_fetcher import TrendingTopicsFetcher
from app.services.fetchers.google_news_fetcher import GoogleNewsFetcher
from app.services.heat_calculator import calculate_all_heat_scores
from app.services.timeline_summarizer import summarize_batch

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


def compute_topic_engagement(topic: Dict) -> float:
    """
    Demand-side engagement signal from a merged topic seed.

    Combines Reddit/HN/Bluesky upvotes/points and comment counts into one
    scalar. Comments are weighted 3x because they're harder to produce than
    a quick upvote — a 200-comment post reflects deeper engagement than a
    200-upvote post. The raw value is stored on TrendingEvent; the final
    log-scale weighting happens in HeatCalculator.calculate_event_heat so
    the engagement term doesn't dominate the formula for viral outliers.
    """
    score = topic.get('total_score', topic.get('score', 0)) or 0
    comments = topic.get('total_comments', topic.get('comments', 0)) or 0
    return float(score) + float(comments) * 3.0


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

        # Persist the demand-side signal on the event so the later heat
        # recalculation step can read it. Initial heat_score is a rough
        # placeholder — calculate_all_heat_scores will overwrite it using
        # the full engagement-aware formula.
        engagement = compute_topic_engagement(topic)

        event = TrendingEvent(
            title=topic['title'],
            summary=topic.get('selftext', '')[:2000] or (matched[0].summary if matched else ''),
            keywords=keywords,
            category=category,
            source_id=topic.get('source_id', 102),
            article_count=len(matched) + 1,  # +1 for the topic itself
            media_count=len(all_sources),
            topic_engagement_score=engagement,
            heat_score=0.0,  # placeholder; overwritten by heat recalc
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


def trim_to_top_n(
    db: Session,
    top_n: int = 40,
    min_per_category: int = 3,
    inactive_days: int = 2,
) -> Dict:
    """Keep top N raw events with per-category minimum retention.

    Events that fall outside top_n are only archived if they also haven't been
    updated in `inactive_days` days. This protects actively-merged long-running
    stories that temporarily drop out of top_n but are still getting new
    articles.

    Per-category floor ensures under-represented categories
    (Entertainment, Sports, Gaming, Culture, Lifestyle, Science) always have
    a minimum seat count in the raw pool so they aren't structurally crushed
    by multi-outlet hard-news stories.
    """
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

    # Step 3: archive only events that are BOTH outside keep set AND inactive
    inactive_cutoff = datetime.utcnow() - timedelta(days=inactive_days)
    to_archive_ids = [
        e.id for e in all_raw
        if e.id not in keep_ids
        and (e.last_updated or e.created_at or datetime.utcnow()) < inactive_cutoff
    ]
    archived_count = 0
    if to_archive_ids:
        archived_count = (
            db.query(TrendingEvent)
            .filter(TrendingEvent.id.in_(to_archive_ids))
            .update({"status": "archived"}, synchronize_session="fetch")
        )
    db.commit()

    # Build full-pool category distribution for visibility into supply balance
    pool_distribution: Dict[str, int] = {}
    for e in all_raw:
        if e.id in keep_ids:
            k = e.category or 'Uncategorized'
            pool_distribution[k] = pool_distribution.get(k, 0) + 1

    protected_active = len(all_raw) - len(keep_ids) - archived_count
    logger.info(
        f"Trim: kept {len(keep_ids)} ({len(category_counts)} cats), "
        f"archived {archived_count}, protected {protected_active} active-out-of-topN"
    )
    logger.info(f"Trim category distribution: {pool_distribution}")
    return {
        "kept": len(keep_ids),
        "archived": archived_count,
        "protected_active": protected_active,
        "category_distribution": pool_distribution,
    }


def find_matching_event(
    db: Session,
    topic: Dict,
    recency_days: int = 7,
) -> Optional[TrendingEvent]:
    """
    Find an existing raw/promoted event that this topic is a continuation of.

    Uses shared curated entities (from TrendingTopicsFetcher._extract_entities)
    and keyword overlap. Returns the best-scoring match or None.
    """
    cutoff = datetime.utcnow() - timedelta(days=recency_days)
    candidates = db.query(TrendingEvent).filter(
        TrendingEvent.status.in_(['raw', 'promoted']),
        TrendingEvent.last_updated >= cutoff,
    ).all()
    if not candidates:
        return None

    # Use the fetcher's curated-entity extractor so detection rules match
    # exactly what the topic clustering step uses.
    fetcher = TrendingTopicsFetcher()

    # Build the topic's entity set from all its titles (cluster_entities is
    # already computed in the fetcher, prefer it when available).
    topic_entities = set(topic.get('cluster_entities') or [])
    if not topic_entities:
        for t in topic.get('all_titles', [topic.get('title', '')]):
            topic_entities |= fetcher._extract_entities(t)

    topic_titles = topic.get('all_titles', [topic.get('title', '')])
    topic_text = ' '.join(topic_titles)

    best_event = None
    best_score = 0.0
    for event in candidates:
        # Build the event's entity + word set from its title, keywords, and
        # a sample of linked article titles.
        event_texts = [event.title or '']
        if event.keywords:
            event_texts.append(' '.join(event.keywords))
        if event.articles:
            event_texts.extend([a.title or '' for a in event.articles[:15]])
        event_text = ' '.join(event_texts)

        event_entities = fetcher._extract_entities(event_text)
        shared = topic_entities & event_entities
        word_sim = title_similarity(topic_text, event_text)

        # For the entity-poor fallback we need TITLE-only entity sets
        # (not the aggregated event corpus, which picks up Google News
        # article entities and is rarely empty). A topic with title
        # "GitHub Stacked PRs" has no curated entities; an existing
        # event for the same story has articles like "GitHub rolls out
        # stacked PR review, CEO says..." which leaks entities into
        # the aggregated set. Compare title-only to avoid that skew.
        topic_title_entities = fetcher._extract_entities(topic.get('title', '') or '')
        event_title_entities = fetcher._extract_entities(event.title or '')
        title_only_sim = title_similarity(
            topic.get('title', '') or '',
            event.title or '',
        )

        # Matching tiers (in order of confidence):
        #   strong  — ≥2 shared curated entities
        #   moderate — 1 shared entity + real word overlap
        #   entity-poor — BOTH titles have 0 curated entities but the
        #                 titles are near-identical. Catches tech/HN
        #                 stories like "GitHub Stacked PRs", "Backblaze
        #                 has stopped backing up your data", "DaVinci
        #                 Resolve – Photo" where the curated entity list
        #                 has no relevant terms but the SAME story shows
        #                 up run after run. Requires title_only_sim ≥ 0.7
        #                 (70%+ of stopword-stripped tokens coincide) to
        #                 avoid false positives like the old 0.35 text-only
        #                 tier.
        match_score = 0.0
        if len(shared) >= 2:
            match_score = 1.0 + len(shared) * 0.1 + word_sim  # strong
        elif len(shared) >= 1 and word_sim >= 0.25:
            match_score = 0.6 + word_sim  # moderate: shared entity + real overlap
        elif (
            len(topic_title_entities) == 0
            and len(event_title_entities) == 0
            and title_only_sim >= 0.7
        ):
            match_score = 0.3 + title_only_sim  # entity-poor, nearly identical titles
        else:
            continue

        if match_score > best_score:
            best_score = match_score
            best_event = event

    return best_event


async def merge_topic_into_event(
    db: Session,
    event: TrendingEvent,
    topic: Dict,
    new_articles: List[TrendingArticle],
) -> None:
    """
    Merge a new topic cluster + its articles into an existing event.

    - Links ACTUALLY new articles to event.id (skipping ones already attached)
    - Appends one LLM-summarized timeline entry covering the new batch —
      only if there actually are new articles. If the topic brought nothing
      new (every article was already on this event from a prior run), we
      skip the LLM call and do not append a duplicate timeline entry.
    - Always accumulates demand-side engagement from the topic seed, since
      fresh Reddit/HN attention is valid signal even without new articles.
    - Refreshes last_updated only when new articles or fresh engagement
      show up (otherwise the event's clock freezes, matching reality).
    - Revives archived events back to 'raw' (rare given recency filter).
    """
    # Split incoming articles into "genuinely new to this event" vs
    # "already linked from a prior pipeline run". The timeline summary
    # and article_count should only reflect the genuinely new batch —
    # otherwise every run re-summarizes the same 30 Google News articles
    # and the timeline fills with near-duplicate entries.
    net_new = [a for a in new_articles if a.event_id != event.id]

    for article in net_new:
        article.event_id = event.id
        article.is_processed = True

    # Revive if somehow archived
    if event.status == 'archived':
        event.status = 'raw'

    # Accumulate the demand-side engagement signal from the new topic seed.
    # This happens even when net_new is empty: a long-running story that
    # gets fresh Reddit attention each pipeline run should rise in heat,
    # not fall, even if no new RSS articles arrived.
    new_engagement = compute_topic_engagement(topic)
    had_fresh_engagement = new_engagement > 0
    event.topic_engagement_score = (event.topic_engagement_score or 0.0) + new_engagement

    if net_new:
        # Real new batch — summarize and append a timeline entry.
        try:
            entry = await summarize_batch(
                event.title or topic.get('title', ''),
                net_new,
                is_initial=False,
            )
        except Exception as e:
            logger.warning(
                f"merge_topic_into_event: summarize failed for event {event.id}: {e}"
            )
            from app.services.timeline_summarizer import _fallback_entry
            entry = _fallback_entry(event.title or '', net_new)

        existing_timeline = list(event.timeline_data or [])
        existing_timeline.append(entry)
        event.timeline_data = existing_timeline
        flag_modified(event, 'timeline_data')
        event.last_updated = datetime.utcnow()
    elif had_fresh_engagement:
        # No new articles but the topic is still getting fresh engagement —
        # bump last_updated so the trim step treats the event as alive,
        # but don't append a noise entry to the timeline.
        event.last_updated = datetime.utcnow()
    else:
        logger.debug(
            f"merge_topic_into_event: event {event.id} got no new articles "
            f"and no fresh engagement — skipping timeline update"
        )

    # Refresh counts (based on actual linked articles in DB)
    db.flush()
    db.refresh(event)
    if event.articles:
        event.article_count = len(event.articles)
        event.media_count = len(set(a.source_id for a in event.articles))
    db.commit()


def _title_token_set(title: str) -> Set[str]:
    """Stopword-filtered token set from a single title (for Jaccard)."""
    return set(clean_words(title or ''))


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def consolidate_existing_events(db: Session) -> Dict:
    """
    Pairwise merge already-persisted raw/promoted events that should be the
    same story.

    Matching is done purely on event.title (not article titles) to keep
    signals stable: previously, absorbing a loser into a winner grew the
    winner's text+entity set from its articles, which snowballed into
    cross-topic pollution (one HN "C++ ocamlc" event absorbed 50 unrelated
    stories). Here the winner's title-based meta is FROZEN for the whole
    pass so no cascading.

    Three match tiers:
    - Strong: 2+ shared curated entities in titles
    - Moderate: 1+ shared curated entity AND title jaccard >= 0.25
    - Near-duplicate: title jaccard >= 0.6 (catches "Ketamine Queen Jasveen
      Sangha jailed..." appearing twice even when no curated entity hits)
    """
    candidates = db.query(TrendingEvent).filter(
        TrendingEvent.status.in_(['raw', 'promoted']),
    ).order_by(desc(TrendingEvent.heat_score)).all()

    if len(candidates) < 2:
        return {"checked": len(candidates), "merged": 0}

    fetcher = TrendingTopicsFetcher()
    # Precompute title-based entities + token sets for each event ONCE.
    # These are intentionally not mutated during the merge loop.
    meta = {
        e.id: (
            fetcher._extract_entities(e.title or ''),
            _title_token_set(e.title or ''),
        )
        for e in candidates
    }

    absorbed: Set[int] = set()
    merge_count = 0

    for i, winner in enumerate(candidates):
        if winner.id in absorbed:
            continue
        w_ents, w_tokens = meta[winner.id]

        for j in range(i + 1, len(candidates)):
            loser = candidates[j]
            if loser.id in absorbed:
                continue
            l_ents, l_tokens = meta[loser.id]

            shared = w_ents & l_ents
            title_jac = _jaccard(w_tokens, l_tokens)

            tier = None
            if len(shared) >= 2:
                tier = 'strong'
            elif len(shared) >= 1 and title_jac >= 0.25:
                tier = 'moderate'
            elif title_jac >= 0.6:
                tier = 'near-dup'
            else:
                continue

            logger.info(
                f"Consolidate[{tier}]: merging event {loser.id} "
                f"'{(loser.title or '')[:50]}' into {winner.id} "
                f"'{(winner.title or '')[:50]}' "
                f"(shared={len(shared)}, jac={title_jac:.2f})"
            )

            # Re-point loser's articles to winner
            for art in loser.articles:
                art.event_id = winner.id

            # Concatenate and sort timelines by timestamp
            winner_tl = list(winner.timeline_data or [])
            loser_tl = list(loser.timeline_data or [])
            combined_tl = winner_tl + loser_tl

            def _ts(entry):
                return entry.get('timestamp', '') if isinstance(entry, dict) else ''
            combined_tl.sort(key=_ts)
            winner.timeline_data = combined_tl
            flag_modified(winner, 'timeline_data')

            # Archive loser
            loser.status = 'archived'
            absorbed.add(loser.id)
            merge_count += 1

            db.flush()
            db.refresh(winner)
            winner.article_count = len(winner.articles)
            winner.media_count = len(set(a.source_id for a in winner.articles))
            winner.last_updated = datetime.utcnow()
            # NOTE: deliberately do NOT update meta[winner.id] — keep match
            # signal frozen to title to prevent cross-topic cascading.

    db.commit()
    return {"checked": len(candidates), "merged": merge_count}


def consolidate_published_events(db: Session) -> Dict:
    """
    Pairwise-merge duplicate published events (Stories page).

    Published events use the separate `Event` model (UUID pk, backed by
    `event_sources` for articles + its own AI analysis tables). They are
    created when admins promote a trending event, and currently nothing
    prevents the same real-world story from being promoted twice.

    Same 3-tier title matching as consolidate_existing_events. When a
    pair matches the loser's EventSource rows are re-pointed to the
    winner (dedup'd against the uq_event_source unique constraint) and
    the loser is archived. Winner's AI analysis (timeline, cause chain,
    etc.) is kept as-is; no re-generation.
    """
    # Local imports to avoid touching the main module-level import block
    from app.models import Event, EventSource
    from sqlalchemy import update as sql_update

    candidates = db.query(Event).filter(
        Event.status == 'active',
    ).order_by(desc(Event.hot_score)).all()
    if len(candidates) < 2:
        return {"checked": len(candidates), "merged": 0}

    fetcher = TrendingTopicsFetcher()
    meta = {
        str(e.id): (
            fetcher._extract_entities(e.title or ''),
            _title_token_set(e.title or ''),
        )
        for e in candidates
    }

    absorbed: Set[str] = set()
    merge_count = 0

    for i, winner in enumerate(candidates):
        w_key = str(winner.id)
        if w_key in absorbed:
            continue
        w_ents, w_tokens = meta[w_key]

        for j in range(i + 1, len(candidates)):
            loser = candidates[j]
            l_key = str(loser.id)
            if l_key in absorbed:
                continue
            l_ents, l_tokens = meta[l_key]

            shared = w_ents & l_ents
            title_jac = _jaccard(w_tokens, l_tokens)

            tier = None
            if len(shared) >= 2:
                tier = 'strong'
            elif len(shared) >= 1 and title_jac >= 0.25:
                tier = 'moderate'
            elif title_jac >= 0.6:
                tier = 'near-dup'
            else:
                continue

            logger.info(
                f"Consolidate-published[{tier}]: merging event {l_key[:8]} "
                f"'{(loser.title or '')[:50]}' into {w_key[:8]} "
                f"'{(winner.title or '')[:50]}' "
                f"(shared={len(shared)}, jac={title_jac:.2f})"
            )

            # Move loser's EventSource rows to winner, skipping rows whose
            # source_id already exists on winner (uq_event_source).
            winner_source_ids = {
                row[0] for row in db.query(EventSource.source_id)
                .filter(EventSource.event_id == winner.id).all()
            }
            loser_rows = db.query(EventSource).filter(
                EventSource.event_id == loser.id
            ).all()
            for row in loser_rows:
                if row.source_id in winner_source_ids:
                    db.delete(row)
                else:
                    row.event_id = winner.id
                    winner_source_ids.add(row.source_id)

            # Archive loser (cascades leave AiSummary etc. intact on loser;
            # those tables are user-facing only for active events).
            loser.status = 'archived'
            loser.archived_at = datetime.utcnow()

            absorbed.add(l_key)
            merge_count += 1

            # Refresh winner source count
            db.flush()
            winner.source_count = db.query(EventSource).filter(
                EventSource.event_id == winner.id
            ).count()
            winner.last_activity_at = datetime.utcnow()
            # Freeze winner meta (no cascading)

    db.commit()
    return {"checked": len(candidates), "merged": merge_count}


def cleanup_bad_merges(db: Session, event_ids: List[int]) -> Dict:
    """
    Archive a list of event ids that were wrongly merged into (e.g. spammy
    container events that absorbed unrelated stories via the removed
    text-only matching tier). Orphaned articles stay linked to the archived
    event; next pipeline run will re-fetch fresh ones on their real topics.
    """
    if not event_ids:
        return {"archived": 0}
    events = db.query(TrendingEvent).filter(TrendingEvent.id.in_(event_ids)).all()
    archived = 0
    for e in events:
        logger.info(f"cleanup_bad_merges: archiving event {e.id} '{(e.title or '')[:60]}'")
        e.status = 'archived'
        archived += 1
    db.commit()
    return {"archived": archived, "event_ids": [e.id for e in events]}


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
    # Resilient insert: use per-row SAVEPOINTs so a duplicate URL slipping
    # past dedup (race conditions, URL normalization edge cases) only drops
    # that one row instead of crashing the whole pipeline run.
    inserted_articles = []
    for article in new_articles:
        try:
            with db.begin_nested():
                db.add(article)
        except IntegrityError:
            logger.warning(f"Skipping duplicate article url={article.url[:80]}")
        else:
            inserted_articles.append(article)
    db.commit()
    new_articles = inserted_articles
    result["new_articles"] = len(new_articles)

    # 5. For each topic: merge into an existing event if it's a continuation,
    #    otherwise create a new event.
    async def build_events():
        events: List[TrendingEvent] = []
        merged_count = 0
        created_count = 0
        for i, topic in enumerate(top_topics):
            gn_arts = topic_gn_articles.get(i, [])
            gn_urls = {a.url for a in gn_arts}
            stored_articles = []
            if gn_urls:
                stored_articles = db.query(TrendingArticle).filter(
                    TrendingArticle.url.in_(gn_urls)
                ).all()

            # Continuation detection: is this topic an extension of an
            # existing event we saw recently?
            existing = find_matching_event(db, topic)
            if existing is not None:
                await merge_topic_into_event(db, existing, topic, stored_articles)
                events.append(existing)
                merged_count += 1
                logger.info(
                    f"Merged topic '{topic['title'][:50]}' into event {existing.id} "
                    f"'{(existing.title or '')[:50]}' (+{len(stored_articles)} articles)"
                )
                continue

            # New event path
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

            # Persist demand-side engagement so the heat recalc step can read
            # it as a first-class term. Without this, every newly-created event
            # this run would lose its Reddit/HN/Bluesky signal and fall back
            # to supply-side ranking. (This write used to live in the unused
            # create_events_from_topics helper — the real pipeline inlines
            # event construction here, so the write has to live here too.)
            engagement = compute_topic_engagement(topic)

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
                topic_engagement_score=engagement,
                heat_score=topic_heat,
                status='raw',
                timeline_data=[],
            )
            db.add(event)
            db.flush()

            for article in stored_articles:
                article.event_id = event.id
                article.is_processed = True

            # Seed initial timeline entry for new events
            try:
                entry = await summarize_batch(
                    event.title or '', stored_articles, is_initial=True,
                )
            except Exception as e:
                logger.warning(f"initial timeline summarize failed: {e}")
                from app.services.timeline_summarizer import _fallback_entry
                entry = _fallback_entry(event.title or '', stored_articles)
            event.timeline_data = [entry]
            flag_modified(event, 'timeline_data')

            events.append(event)
            created_count += 1

        db.commit()
        return events, merged_count, created_count

    _loop3 = asyncio.new_event_loop()
    try:
        events, merged_count, created_count = _loop3.run_until_complete(build_events())
    finally:
        _loop3.close()

    result["events_created"] = created_count
    result["events_merged"] = merged_count

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


def dedupe_existing_events(db: Session) -> Dict:
    """Retroactively merge active events whose titles collide.

    Pre-fix, `find_matching_event` silently refused to merge entity-poor
    stories (GitHub Stacked PRs, Backblaze, DaVinci Resolve, etc.) because
    `_extract_entities` returned empty sets for those titles. Every ~4h
    pipeline run created a fresh event instead of merging, so the same
    story accumulated 3-6 duplicate rows. This function groups active
    events by a normalized title key, keeps the winner (highest heat,
    then most engagement, then most articles), re-parents all articles
    from losers onto the winner, sums engagement, and archives losers.
    """
    fetcher = TrendingTopicsFetcher()

    def title_key(title: str) -> str:
        # Normalize: lowercase, strip punctuation, drop stopwords, sort
        # remaining tokens. Near-identical titles (curly vs straight quotes,
        # trailing ellipsis) collapse to the same key.
        words = fetcher._clean_words(title or '')
        return ' '.join(sorted(words))

    active = db.query(TrendingEvent).filter(
        TrendingEvent.status.in_(['raw', 'promoted'])
    ).all()

    groups: Dict[str, List[TrendingEvent]] = {}
    for e in active:
        k = title_key(e.title)
        if not k:
            continue
        groups.setdefault(k, []).append(e)

    merged_groups = 0
    archived_losers = 0
    reparented_articles = 0
    for key, group in groups.items():
        if len(group) < 2:
            continue
        # Winner: highest heat, tiebreak on engagement, then article count
        group.sort(
            key=lambda e: (
                e.heat_score or 0.0,
                e.topic_engagement_score or 0.0,
                e.article_count or 0,
            ),
            reverse=True,
        )
        winner = group[0]
        losers = group[1:]

        for loser in losers:
            # Re-parent articles
            updated = (
                db.query(TrendingArticle)
                .filter(TrendingArticle.event_id == loser.id)
                .update({"event_id": winner.id}, synchronize_session=False)
            )
            reparented_articles += updated

            # Sum engagement onto winner
            winner.topic_engagement_score = (
                (winner.topic_engagement_score or 0.0)
                + (loser.topic_engagement_score or 0.0)
            )

            # Merge timeline entries (winner first, then loser chronologically)
            winner_tl = winner.timeline_data or []
            loser_tl = loser.timeline_data or []
            winner.timeline_data = winner_tl + loser_tl
            flag_modified(winner, 'timeline_data')

            loser.status = 'archived'
            archived_losers += 1

        # Refresh counts on winner
        db.flush()
        winner_articles = db.query(TrendingArticle).filter(
            TrendingArticle.event_id == winner.id
        ).all()
        winner.article_count = len(winner_articles)
        winner.media_count = len(set(a.source_id for a in winner_articles if a.source_id))
        winner.last_updated = datetime.utcnow()
        merged_groups += 1
        logger.info(
            f"Deduped '{(winner.title or '')[:50]}': "
            f"kept event {winner.id}, archived {[l.id for l in losers]}"
        )

    db.commit()
    logger.info(
        f"Dedupe: merged {merged_groups} groups, archived {archived_losers} "
        f"losers, re-parented {reparented_articles} articles"
    )
    return {
        "merged_groups": merged_groups,
        "archived_losers": archived_losers,
        "reparented_articles": reparented_articles,
    }


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
