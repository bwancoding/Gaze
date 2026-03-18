"""
Reddit API fetch service - uses the public JSON API (free, no authentication required)
"""
import aiohttp
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timezone
from app.models.trending import TrendingArticle
import logging
import time

logger = logging.getLogger(__name__)


class RedditFetcher:
    """Reddit fetcher"""

    TARGET_SUBREDDITS = ["all", "worldnews", "news", "technology"]
    BASE_URL = "https://www.reddit.com"
    RATE_LIMIT_DELAY = 1.0

    SUBREDDIT_SOURCE_MAP = {
        "all": 101,
        "worldnews": 102,
        "news": 103,
        "technology": 104,
    }

    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(ssl=False)
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={'User-Agent': 'WRHITW-Reddit-Fetcher/1.0 (by /u/wrhitw_bot)'},
                connector=connector
            )
        return self.session

    async def _respect_rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()

    async def fetch_subreddit(self, subreddit: str, limit: int = 25) -> List[TrendingArticle]:
        await self._respect_rate_limit()
        session = await self._get_session()
        articles = []
        url = f"{self.BASE_URL}/r/{subreddit}/hot.json?limit={min(limit, 100)}"

        try:
            logger.info(f"Fetching r/{subreddit} hot posts")
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch r/{subreddit}: HTTP {response.status}")
                    return []

                data = await response.json()
                posts = data.get('data', {}).get('children', [])

                for post in posts:
                    article = self._parse_post(post, subreddit)
                    if article:
                        articles.append(article)

                logger.info(f"Fetched {len(articles)} posts from r/{subreddit}")

        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching r/{subreddit}")
        except Exception as e:
            logger.error(f"Error fetching r/{subreddit}: {e}")

        return articles

    def _parse_post(self, post: Dict, subreddit: str) -> Optional[TrendingArticle]:
        try:
            data = post.get('data', {})
            title = data.get('title', '').strip()
            if not title:
                return None

            selftext = data.get('selftext', '')
            summary = selftext[:2000] if selftext else ''
            permalink = data.get('permalink', '')
            reddit_url = f"{self.BASE_URL}{permalink}"

            created_utc = data.get('created_utc', 0)
            published_at = (datetime.fromtimestamp(created_utc, tz=timezone.utc)
                            if created_utc else datetime.utcnow())

            return TrendingArticle(
                title=title,
                summary=summary,
                url=reddit_url,
                published_at=published_at,
                source_id=self.SUBREDDIT_SOURCE_MAP.get(subreddit, 100),
                source_priority="P1",
                fetched_at=datetime.utcnow(),
                heat_score=float(data.get('score', 0)),
                comment_count=data.get('num_comments', 0),
                is_processed=False
            )
        except Exception as e:
            logger.warning(f"Failed to parse Reddit post: {e}")
            return None

    async def fetch_all(self, limit: int = 25) -> List[TrendingArticle]:
        all_articles = []
        for subreddit in self.TARGET_SUBREDDITS:
            articles = await self.fetch_subreddit(subreddit, limit)
            all_articles.extend(articles)
        return all_articles

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
