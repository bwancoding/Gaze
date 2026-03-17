"""
RSS 抓取服务 - 异步并发抓取多个 RSS 源
"""
import asyncio
import aiohttp
import feedparser
from typing import List, Dict, Optional
from datetime import datetime, timezone
from app.services.trending_config import RSS_FETCH_TIMEOUT, RSS_MAX_ARTICLES_PER_FEED
from app.models.trending import TrendingArticle
import logging

logger = logging.getLogger(__name__)


class RSSFetcher:
    """RSS 抓取器"""

    def __init__(self, timeout: int = None):
        self.timeout = aiohttp.ClientTimeout(total=timeout or RSS_FETCH_TIMEOUT)
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={'User-Agent': 'WRHITW-RSS-Fetcher/1.0 (+https://wrhitw.com)'}
            )
        return self.session

    async def fetch(self, source: Dict) -> List[TrendingArticle]:
        session = await self._get_session()
        articles = []

        try:
            logger.info(f"Fetching {source['name']} ({source['url']})")
            async with session.get(source["url"]) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {source['name']}: HTTP {response.status}")
                    return []

                content = await response.text('utf-8')
                feed = feedparser.parse(content)

                for entry in feed.entries[:RSS_MAX_ARTICLES_PER_FEED]:
                    article = self._parse_entry(entry, source)
                    if article:
                        articles.append(article)

                logger.info(f"Fetched {len(articles)} articles from {source['name']}")

        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {source['name']}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching {source['name']}: {e}")
        except Exception as e:
            logger.error(f"Error fetching {source['name']}: {e}")

        return articles

    def _parse_entry(self, entry, source: Dict) -> Optional[TrendingArticle]:
        try:
            title = getattr(entry, 'title', '').strip()
            if not title:
                return None

            summary = ''
            if hasattr(entry, 'summary'):
                summary = entry.summary.strip()
            elif hasattr(entry, 'description'):
                summary = entry.description.strip()

            url = getattr(entry, 'link', '')
            if not url:
                return None

            published_at = self._parse_date(entry) or datetime.utcnow()

            return TrendingArticle(
                title=title,
                summary=summary[:2000] if summary else '',
                url=url,
                published_at=published_at,
                source_id=source["id"],
                source_priority=source["priority"],
                fetched_at=datetime.utcnow(),
                is_processed=False
            )
        except Exception as e:
            logger.warning(f"Failed to parse RSS entry: {e}")
            return None

    def _parse_date(self, entry) -> Optional[datetime]:
        for field in ['published_parsed', 'updated_parsed', 'created_parsed']:
            if hasattr(entry, field) and entry[field]:
                try:
                    ts = entry[field]
                    return datetime(ts.tm_year, ts.tm_mon, ts.tm_mday,
                                    ts.tm_hour, ts.tm_min, ts.tm_sec,
                                    tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    continue

        if hasattr(entry, 'published') and entry.published:
            try:
                from email.utils import parsedate_to_datetime
                return parsedate_to_datetime(entry.published)
            except Exception:
                pass

        return None

    async def fetch_all(self, sources: List[Dict]) -> List[TrendingArticle]:
        tasks = [self.fetch(source) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
        return all_articles

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
