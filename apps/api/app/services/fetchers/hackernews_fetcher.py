"""
Hacker News API fetch service - uses the Firebase public API (free)
"""
import aiohttp
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timezone
from app.models.trending import TrendingArticle
import logging
import time

logger = logging.getLogger(__name__)


class HackerNewsFetcher:
    """Hacker News fetcher"""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    RATE_LIMIT_DELAY = 0.5
    SOURCE_ID = 105

    def __init__(self, timeout: int = 30, max_stories: int = 50):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0
        self.max_stories = max_stories

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(ssl=False)
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={'User-Agent': 'Gaze-HN-Fetcher/1.0 (+https://gaze.app)'},
                connector=connector
            )
        return self.session

    async def _respect_rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()

    async def get_top_stories_ids(self, limit: int = None) -> List[int]:
        await self._respect_rate_limit()
        session = await self._get_session()

        try:
            logger.info("Fetching Hacker News top stories")
            async with session.get(f"{self.BASE_URL}/topstories.json") as response:
                if response.status != 200:
                    return []
                story_ids = await response.json()
                return story_ids[:limit] if limit else story_ids
        except Exception as e:
            logger.error(f"Error fetching HN top stories: {e}")
            return []

    async def get_story(self, story_id: int) -> Optional[Dict]:
        await self._respect_rate_limit()
        session = await self._get_session()

        try:
            async with session.get(f"{self.BASE_URL}/item/{story_id}.json") as response:
                if response.status != 200:
                    return None
                return await response.json()
        except Exception as e:
            logger.warning(f"Error fetching HN story {story_id}: {e}")
            return None

    async def fetch_stories(self, story_ids: List[int]) -> List[TrendingArticle]:
        articles = []
        semaphore = asyncio.Semaphore(10)

        async def fetch_with_semaphore(sid):
            async with semaphore:
                return await self.get_story(sid)

        tasks = [fetch_with_semaphore(sid) for sid in story_ids]
        stories = await asyncio.gather(*tasks, return_exceptions=True)

        for story_id, story in zip(story_ids, stories):
            if isinstance(story, Exception) or story is None:
                continue
            article = self._parse_story(story, story_id)
            if article:
                articles.append(article)

        logger.info(f"Parsed {len(articles)} Hacker News stories")
        return articles

    def _parse_story(self, story: Dict, story_id: int) -> Optional[TrendingArticle]:
        try:
            title = story.get('title', '').strip()
            if not title:
                return None

            url = story.get('url', '') or f"https://news.ycombinator.com/item?id={story_id}"
            text = story.get('text', '')
            summary = text[:2000] if text else ''

            time_utc = story.get('time', 0)
            published_at = (datetime.fromtimestamp(time_utc, tz=timezone.utc)
                            if time_utc else datetime.utcnow())

            return TrendingArticle(
                title=title,
                summary=summary,
                url=url,
                published_at=published_at,
                source_id=self.SOURCE_ID,
                source_priority="P1",
                fetched_at=datetime.utcnow(),
                heat_score=float(story.get('score', 0)),
                comment_count=story.get('descendants', 0),
                is_processed=False
            )
        except Exception as e:
            logger.warning(f"Failed to parse HN story: {e}")
            return None

    async def fetch_top_stories(self, limit: int = None) -> List[TrendingArticle]:
        limit = limit or self.max_stories
        story_ids = await self.get_top_stories_ids(limit=limit)
        if not story_ids:
            return []
        return await self.fetch_stories(story_ids)

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
