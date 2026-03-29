"""
Trending Topics Fetcher - Fetches hot/trending topics from multiple platforms,
then uses them as seeds to organize articles into events.

Approach: Topics First → Articles Second
1. Fetch trending topics from Reddit (hot posts with high scores), Google Trends, HN top stories
2. Deduplicate/merge similar topics
3. Each topic becomes a candidate event
4. Match RSS articles to these topic-events
"""
import aiohttp
import asyncio
import logging
import time
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
from collections import Counter

logger = logging.getLogger(__name__)


class TrendingTopicsFetcher:
    """Fetches trending topics from multiple platforms to use as event seeds"""

    REDDIT_BASE = "https://www.reddit.com"
    HN_API = "https://hacker-news.firebaseio.com/v0"

    # Subreddits focused on news (not memes/entertainment)
    NEWS_SUBREDDITS = [
        ("worldnews", 102),
        ("news", 103),
        ("technology", 104),
    ]

    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(ssl=False)
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={'User-Agent': 'Gaze-Bot/1.0'},
                connector=connector,
            )
        return self.session

    async def _rate_limit(self, delay: float = 1.0):
        elapsed = time.time() - self.last_request_time
        if elapsed < delay:
            await asyncio.sleep(delay - elapsed)
        self.last_request_time = time.time()

    async def fetch_reddit_trending(self, limit: int = 25) -> List[Dict]:
        """Fetch top/hot posts from news subreddits as topic seeds"""
        topics = []
        session = await self._get_session()

        for subreddit, source_id in self.NEWS_SUBREDDITS:
            await self._rate_limit()
            url = f"{self.REDDIT_BASE}/r/{subreddit}/hot.json?limit={limit}"
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        logger.warning(f"Reddit r/{subreddit}: HTTP {resp.status}")
                        continue
                    data = await resp.json()
                    posts = data.get('data', {}).get('children', [])

                    for post in posts:
                        d = post.get('data', {})
                        score = d.get('score', 0)
                        # Only take posts with significant engagement
                        if score < 100:
                            continue
                        title = d.get('title', '').strip()
                        if not title:
                            continue

                        topics.append({
                            'title': title,
                            'source': f'Reddit r/{subreddit}',
                            'source_id': source_id,
                            'score': score,
                            'comments': d.get('num_comments', 0),
                            'url': f"{self.REDDIT_BASE}{d.get('permalink', '')}",
                            'selftext': (d.get('selftext', '') or '')[:500],
                            'created_at': datetime.fromtimestamp(
                                d.get('created_utc', 0), tz=timezone.utc
                            ) if d.get('created_utc') else datetime.utcnow(),
                        })

                logger.info(f"Reddit r/{subreddit}: {len([t for t in topics if t['source_id'] == source_id])} topics")
            except Exception as e:
                logger.error(f"Reddit r/{subreddit} error: {e}")

        return topics

    async def fetch_hn_trending(self, limit: int = 15) -> List[Dict]:
        """Fetch top Hacker News stories as topic seeds"""
        topics = []
        session = await self._get_session()

        try:
            async with session.get(f"{self.HN_API}/topstories.json") as resp:
                if resp.status != 200:
                    return []
                story_ids = await resp.json()

            for story_id in story_ids[:limit]:
                await self._rate_limit(0.3)
                try:
                    async with session.get(f"{self.HN_API}/item/{story_id}.json") as resp:
                        if resp.status != 200:
                            continue
                        item = await resp.json()
                        if not item or item.get('type') != 'story':
                            continue
                        score = item.get('score', 0)
                        if score < 50:
                            continue

                        # Filter out non-news HN posts (Show HN, personal projects, etc.)
                        hn_title = item.get('title', '')
                        hn_title_lower = hn_title.lower()
                        if any(prefix in hn_title_lower for prefix in [
                            'show hn:', 'ask hn:', 'launch hn:', 'tell hn:',
                        ]):
                            continue
                        # Skip entries that look like domain names / product launches
                        if hn_title.endswith('.com') or hn_title.endswith('.io') or hn_title.endswith('.camera'):
                            continue

                        topics.append({
                            'title': item.get('title', ''),
                            'source': 'Hacker News',
                            'source_id': 105,
                            'score': score,
                            'comments': item.get('descendants', 0),
                            'url': item.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                            'selftext': '',
                            'created_at': datetime.fromtimestamp(
                                item.get('time', 0), tz=timezone.utc
                            ) if item.get('time') else datetime.utcnow(),
                        })
                except Exception as e:
                    logger.warning(f"HN item {story_id}: {e}")

            logger.info(f"HN: {len(topics)} topics")
        except Exception as e:
            logger.error(f"HN error: {e}")

        return topics

    async def fetch_all_trending(self) -> List[Dict]:
        """Fetch trending topics from all platforms"""
        reddit_topics, hn_topics = await asyncio.gather(
            self.fetch_reddit_trending(),
            self.fetch_hn_trending(),
        )

        all_topics = reddit_topics + hn_topics
        logger.info(f"Total raw topics: {len(all_topics)}")

        # Deduplicate similar topics
        merged = self._merge_similar_topics(all_topics)
        logger.info(f"After merging: {len(merged)} unique topics")

        # Sort by combined score
        merged.sort(key=lambda t: t['score'], reverse=True)
        return merged

    def _merge_similar_topics(self, topics: List[Dict]) -> List[Dict]:
        """
        Merge topics about the same story using two strategies:
        1. Title word overlap (>0.4)
        2. Shared key entities — if two topics share 2+ key entities, they're likely the same story
           (e.g. "Iran threatens Hormuz" + "Iran warns infrastructure attack" both have Iran+Trump)
        """
        if not topics:
            return []

        # Extract entities for each topic
        topic_entities = [self._extract_entities(t['title']) for t in topics]

        merged = []
        used = set()

        for i, t1 in enumerate(topics):
            if i in used:
                continue
            group = [t1]
            for j, t2 in enumerate(topics[i + 1:], start=i + 1):
                if j in used:
                    continue

                # Strategy 1: title word overlap
                word_sim = self._title_similarity(t1['title'], t2['title'])
                if word_sim > 0.4:
                    group.append(t2)
                    used.add(j)
                    continue

                # Strategy 2: shared key entities
                shared_entities = topic_entities[i] & topic_entities[j]
                # 2+ shared entities → definitely same story
                if len(shared_entities) >= 2:
                    group.append(t2)
                    used.add(j)
                    continue
                # 1 shared entity + some word overlap → likely same story
                if len(shared_entities) >= 1 and word_sim >= 0.2:
                    group.append(t2)
                    used.add(j)
                    continue

            used.add(i)

            # Merge group: keep highest-scored title, combine all data
            best = max(group, key=lambda x: x['score'])
            best['sources'] = list(set(t['source'] for t in group))
            best['total_score'] = sum(t['score'] for t in group)
            best['total_comments'] = sum(t['comments'] for t in group)
            best['related_urls'] = [t['url'] for t in group]
            # Combine all titles as extra keywords for better article matching
            best['all_titles'] = [t['title'] for t in group]
            merged.append(best)

        return merged

    def _extract_entities(self, text: str) -> set:
        """
        Extract key named entities from text.
        Uses a curated list + stemming normalization for reliable matching.
        """
        # Normalize text: strip possessives, lowercase
        normalized = re.sub(r"'s\b", '', text.lower())
        normalized = re.sub(r'[^a-z0-9\s]', ' ', normalized)
        words = normalized.split()

        # Known high-value entities for news (normalized forms)
        known_entities = {
            # Countries & Regions
            'iran', 'iranian', 'iraq', 'iraqi', 'israel', 'israeli', 'gaza',
            'palestine', 'palestinian', 'ukraine', 'ukrainian', 'russia', 'russian',
            'china', 'chinese', 'taiwan', 'cuba', 'cuban', 'korea', 'korean',
            'japan', 'japanese', 'india', 'indian', 'brazil', 'mexico',
            'syria', 'syrian', 'yemen', 'afghanistan', 'pakistan',
            # Key locations
            'hormuz', 'crimea', 'arctic', 'sahara',
            # People
            'trump', 'trumps', 'biden', 'putin', 'obama', 'zelensky',
            'modi', 'macron', 'pope', 'musk', 'netanyahu',
            # Organizations
            'nato', 'fbi', 'cia', 'dhs', 'ice', 'fda', 'pentagon', 'kremlin',
            'congress', 'senate',
            # Tech
            'openai', 'chatgpt', 'google', 'apple', 'meta', 'microsoft',
            'tesla', 'spacex', 'nvidia',
            # Topics (high-signal)
            'climate', 'earthquake', 'hurricane', 'pandemic', 'vaccine',
            'nuclear', 'missile', 'sanctions', 'tariff',
        }

        # Normalize variants to canonical form
        entity_canonical = {
            'iranian': 'iran', 'iraqi': 'iraq', 'israeli': 'israel',
            'palestinian': 'palestine', 'ukrainian': 'ukraine',
            'russian': 'russia', 'chinese': 'china', 'cuban': 'cuba',
            'korean': 'korea', 'japanese': 'japan', 'indian': 'india',
            'syrian': 'syria', 'trumps': 'trump',
        }

        entities = set()
        for w in words:
            if w in known_entities:
                canonical = entity_canonical.get(w, w)
                entities.add(canonical)

        return entities

    def _title_similarity(self, t1: str, t2: str) -> float:
        """Simple word overlap similarity"""
        words1 = set(self._clean_words(t1))
        words2 = set(self._clean_words(t2))
        if not words1 or not words2:
            return 0.0
        overlap = words1 & words2
        return len(overlap) / min(len(words1), len(words2))

    def _clean_words(self, text: str) -> List[str]:
        """Extract meaningful words from text"""
        stop = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'has', 'have',
                'its', 'it', 'this', 'that', 'as', 'be', 'been', 'will', 'would',
                'not', 'no', 'can', 'could', 'how', 'what', 'who', 'which', 'new'}
        words = re.sub(r'[^a-z0-9\s]', ' ', text.lower()).split()
        return [w for w in words if w not in stop and len(w) > 2]

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
