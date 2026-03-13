"""
Hacker News API 抓取服务
- 使用 Firebase API 获取 Top Stories
- 数据格式转换为统一 Article 模型
- 异步并发支持
- 限流处理
"""
import aiohttp
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timezone
from app.config import settings
from app.models.article import Article
import logging
import time

logger = logging.getLogger(__name__)


class HackerNewsFetcher:
    """Hacker News 抓取器"""
    
    # Hacker News Firebase API 基础 URL
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    # 限流配置（Firebase API 比较宽松，但仍需礼貌请求）
    RATE_LIMIT_DELAY = 0.5  # 请求间隔（秒）
    
    def __init__(self, timeout: int = 30, max_stories: int = 50, verify_ssl: bool = False):
        """
        初始化抓取器
        
        Args:
            timeout: 请求超时时间（秒）
            max_stories: 最多抓取故事数
            verify_ssl: 是否验证 SSL 证书（默认 False，避免 macOS Python 环境问题）
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0
        self.max_stories = max_stories
        self.user_agent = "WRHITW-HN-Fetcher/1.0 (+https://wrhitw.com)"
        self.verify_ssl = verify_ssl
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建 HTTP 会话"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    'User-Agent': self.user_agent
                },
                connector=connector
            )
        return self.session
    
    async def _respect_rate_limit(self):
        """遵守 API 限流规则"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.RATE_LIMIT_DELAY:
            wait_time = self.RATE_LIMIT_DELAY - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def get_top_stories_ids(self, limit: int = None) -> List[int]:
        """
        获取 Top Stories ID 列表
        
        Args:
            limit: 最多获取的故事数量
            
        Returns:
            故事 ID 列表
        """
        await self._respect_rate_limit()
        
        session = await self._get_session()
        url = f"{self.BASE_URL}/topstories.json"
        
        try:
            logger.info(f"📰 获取 Hacker News Top Stories")
            
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"⚠️  获取 Top Stories 失败：HTTP {response.status}")
                    return []
                
                story_ids = await response.json()
                
                # 限制数量
                if limit:
                    story_ids = story_ids[:limit]
                
                logger.info(f"✅ 获取 {len(story_ids)} 个 Top Stories IDs")
                return story_ids
                
        except Exception as e:
            logger.error(f"❌ 获取 Top Stories 异常：{e}")
            return []
    
    async def get_story(self, story_id: int) -> Optional[Dict]:
        """
        获取单个故事详情
        
        Args:
            story_id: 故事 ID
            
        Returns:
            故事数据字典或 None
        """
        await self._respect_rate_limit()
        
        session = await self._get_session()
        url = f"{self.BASE_URL}/item/{story_id}.json"
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                
                story = await response.json()
                return story
                
        except Exception as e:
            logger.warning(f"⚠️  获取故事 {story_id} 失败：{e}")
            return None
    
    async def fetch_stories(self, story_ids: List[int]) -> List[Article]:
        """
        批量获取故事详情并转换为 Article 对象
        
        Args:
            story_ids: 故事 ID 列表
            
        Returns:
            文章列表
        """
        articles = []
        
        # 并发获取故事详情（限制并发数）
        semaphore = asyncio.Semaphore(10)  # 最多 10 个并发请求
        
        async def fetch_with_semaphore(story_id):
            async with semaphore:
                return await self.get_story(story_id)
        
        tasks = [fetch_with_semaphore(sid) for sid in story_ids]
        stories = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 解析故事
        for story_id, story in zip(story_ids, stories):
            if isinstance(story, Exception) or story is None:
                continue
            
            article = self._parse_story(story, story_id)
            if article:
                articles.append(article)
        
        logger.info(f"✅ 解析 {len(articles)} 个 Hacker News 故事")
        return articles
    
    def _parse_story(self, story: Dict, story_id: int) -> Optional[Article]:
        """
        解析 Hacker News 故事为 Article 对象
        
        Args:
            story: 故事数据
            story_id: 故事 ID
            
        Returns:
            Article 对象或 None
        """
        try:
            # 提取标题
            title = story.get('title', '').strip()
            if not title:
                return None
            
            # 提取 URL（如果没有外部链接，使用 HN 链接）
            url = story.get('url', '')
            hn_url = f"https://news.ycombinator.com/item?id={story_id}"
            
            if not url:
                url = hn_url
            
            # 提取文本内容（如果有）
            text = story.get('text', '')
            summary = text[:2000] if text else ''
            
            # 提取发布时间
            time_utc = story.get('time', 0)
            if time_utc:
                published_at = datetime.fromtimestamp(time_utc, tz=timezone.utc)
            else:
                published_at = datetime.utcnow()
            
            # 提取热度数据
            score = story.get('score', 0)  # 点赞数
            descendants = story.get('descendants', 0)  # 评论数
            
            # 创建文章对象
            article = Article(
                title=title,
                summary=summary,
                url=url,
                published_at=published_at,
                source_id=105,  # Hacker News source_id
                source_priority="P1",  # HN 设为 P1 优先级
                fetched_at=datetime.utcnow(),
                heat_score=float(score),  # 使用 score 作为初始热度
                comment_count=descendants,
                is_processed=False
            )
            
            return article
            
        except Exception as e:
            logger.warning(f"⚠️  解析 Hacker News 故事失败：{e}")
            return None
    
    async def fetch_top_stories(self, limit: int = None) -> List[Article]:
        """
        获取 Top Stories 并转换为文章列表
        
        Args:
            limit: 最多获取的故事数量
            
        Returns:
            文章列表
        """
        limit = limit or self.max_stories
        
        # 获取 Top Stories IDs
        story_ids = await self.get_top_stories_ids(limit=limit)
        
        if not story_ids:
            return []
        
        # 获取故事详情
        articles = await self.fetch_stories(story_ids)
        
        return articles
    
    async def close(self):
        """关闭 HTTP 会话"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("🔒 Hacker News HTTP 会话已关闭")
