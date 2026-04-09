"""
Google News RSS Search Fetcher

Uses Google News RSS endpoint to search for articles related to specific topics.
No API key required. Returns articles from various media outlets.

Endpoint: https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en
"""
import aiohttp
import asyncio
import feedparser
import logging
import time
import re
import html
from typing import List, Dict, Optional
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from app.models.trending import TrendingArticle

logger = logging.getLogger(__name__)


class GoogleNewsFetcher:
    """Fetch articles from Google News RSS search by keyword"""

    BASE_URL = "https://news.google.com/rss/search"
    RATE_LIMIT_DELAY = 1.5  # Be polite to Google

    # Map known publisher domains to source IDs (matching existing sources)
    PUBLISHER_SOURCE_MAP = {
        'bbc': 3, 'guardian': 4, 'ft.com': 5, 'bloomberg': 6,
        'cnn': 7, 'foxnews': 8, 'nytimes': 9, 'wsj': 10,
        'economist': 11, 'aljazeera': 12, 'politico': 13,
        'thehill': 14, 'npr': 15, 'abcnews': 20, 'cbsnews': 21,
        'skynews': 22, 'france24': 23, 'dw.com': 24,
        'independent': 25, 'scmp': 26, 'reuters': 1, 'apnews': 2,
    }

    # Default source ID for Google News articles from unknown publishers
    GOOGLE_NEWS_SOURCE_ID = 200

    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(ssl=False)
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; Gaze-Bot/1.0)',
                    'Accept': 'application/rss+xml, application/xml, text/xml',
                },
                connector=connector,
            )
        return self.session

    async def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()

    def _extract_publisher(self, entry: dict) -> str:
        """Extract publisher name from Google News RSS entry"""
        # Google News includes source in the title as "Title - Publisher"
        title = entry.get('title', '')
        if ' - ' in title:
            return title.rsplit(' - ', 1)[-1].strip()
        # Try source tag
        source = entry.get('source', {})
        if isinstance(source, dict):
            return source.get('title', '') or source.get('value', '')
        return ''

    def _clean_title(self, title: str) -> str:
        """Remove publisher suffix from Google News title"""
        if ' - ' in title:
            return title.rsplit(' - ', 1)[0].strip()
        return title.strip()

    def _get_source_id(self, publisher: str, url: str) -> int:
        """Map publisher/URL to a source ID"""
        publisher_lower = publisher.lower()
        url_lower = url.lower()

        for key, source_id in self.PUBLISHER_SOURCE_MAP.items():
            if key in publisher_lower or key in url_lower:
                return source_id

        return self.GOOGLE_NEWS_SOURCE_ID

    def _clean_summary(self, summary: str) -> str:
        """Clean HTML from summary"""
        if not summary:
            return ''
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', ' ', summary)
        # Decode HTML entities
        clean = html.unescape(clean)
        # Normalize whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean[:2000]

    async def search_topic(self, query: str, max_results: int = 30) -> List[TrendingArticle]:
        """
        Search Google News for articles related to a query.
        Returns list of TrendingArticle objects.
        """
        await self._rate_limit()
        session = await self._get_session()

        # Build search URL
        # Use quotes for multi-word key phrases, limit to recent news
        params = {
            'q': query,
            'hl': 'en',
            'gl': 'US',
            'ceid': 'US:en',
        }

        articles = []
        try:
            url = f"{self.BASE_URL}?q={aiohttp.helpers.quote(query, safe='')}&hl=en&gl=US&ceid=US:en"
            logger.info(f"Google News search: '{query[:50]}'")

            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.warning(f"Google News HTTP {resp.status} for '{query[:30]}'")
                    return []

                content = await resp.text()
                feed = feedparser.parse(content)

                for entry in feed.entries[:max_results]:
                    try:
                        title = self._clean_title(entry.get('title', ''))
                        if not title:
                            continue

                        publisher = self._extract_publisher(entry)
                        link = entry.get('link', '')

                        # Parse published date
                        published_at = datetime.utcnow()
                        if entry.get('published'):
                            try:
                                published_at = parsedate_to_datetime(entry['published'])
                                if published_at.tzinfo:
                                    published_at = published_at.replace(tzinfo=None)
                            except Exception:
                                pass

                        summary = self._clean_summary(
                            entry.get('summary', '') or entry.get('description', '')
                        )

                        source_id = self._get_source_id(publisher, link)

                        articles.append(TrendingArticle(
                            title=title,
                            summary=summary,
                            url=link,
                            published_at=published_at,
                            source_id=source_id,
                            source_priority="P1",
                            fetched_at=datetime.utcnow(),
                            heat_score=0.0,
                            comment_count=0,
                            is_processed=False,
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to parse Google News entry: {e}")

                logger.info(f"Google News: {len(articles)} articles for '{query[:30]}'")

        except asyncio.TimeoutError:
            logger.error(f"Google News timeout for '{query[:30]}'")
        except Exception as e:
            logger.error(f"Google News error for '{query[:30]}': {e}")

        return articles

    def build_search_query(self, topic: Dict) -> str:
        """
        Build an effective search query from a topic.

        For merged super-topics (cluster_size > 1), use shared entities +
        the most common distinctive words across all titles — this yields
        broader coverage than any single title.

        For single-post topics, extract key terms from the title.
        """
        stop = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'has', 'have',
                'its', 'it', 'this', 'that', 'as', 'be', 'will', 'would', 'says', 'said',
                'not', 'can', 'could', 'how', 'what', 'who', 'which', 'new', 'after',
                'been', 'being', 'into', 'over', 'than', 'about', 'just', 'also'}

        cluster_size = topic.get('cluster_size', 1)
        cluster_entities = topic.get('cluster_entities', [])

        if cluster_size > 1 and cluster_entities:
            # Super-topic: use shared entities as primary query
            # Plus the top distinctive word from the best title
            from collections import Counter
            all_titles = topic.get('all_titles', [topic.get('title', '')])
            word_counter: Counter = Counter()
            for t in all_titles:
                words = re.sub(r'[^a-zA-Z0-9\s]', ' ', t).split()
                word_counter.update(
                    w.lower() for w in words
                    if w.lower() not in stop and len(w) > 3
                )
            # Take most common words that aren't entities (already included)
            entity_set = set(cluster_entities)
            extra_words = [w for w, _ in word_counter.most_common(10) if w not in entity_set][:2]
            # Cap entities to 3 most salient to avoid overly specific query
            query_terms = cluster_entities[:3] + extra_words
            return ' '.join(query_terms)

        # Single-post topic: extract key terms from title
        title = topic.get('title', '')
        words = re.sub(r'[^a-zA-Z0-9\s]', ' ', title).split()
        key_words = [w for w in words if w.lower() not in stop and len(w) > 2]
        return ' '.join(key_words[:5])

    async def search_topics(self, topics: List[Dict], max_per_topic: int = 30) -> Dict[int, List[TrendingArticle]]:
        """
        Search Google News for each topic, return {topic_index: [articles]}
        """
        result: Dict[int, List[TrendingArticle]] = {}

        for i, topic in enumerate(topics):
            query = self.build_search_query(topic)
            if not query:
                result[i] = []
                continue

            articles = await self.search_topic(query, max_results=max_per_topic)
            result[i] = articles
            logger.info(f"Topic {i+1}/{len(topics)}: '{topic['title'][:40]}' → {len(articles)} articles")

        return result

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
