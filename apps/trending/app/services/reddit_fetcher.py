"""
Reddit API 抓取服务
- 抓取 Reddit Hot 帖子（r/all, r/worldnews, r/news, r/technology）
- 数据格式转换为统一 Article 模型
- 限流处理（遵守 Reddit API 规则：60 次/分钟）
- 异步并发支持
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


class RedditFetcher:
    """Reddit 抓取器"""
    
    # 目标 Subreddits 列表
    TARGET_SUBREDDITS = [
        "all",
        "worldnews",
        "news",
        "technology"
    ]
    
    # Reddit API 基础 URL
    BASE_URL = "https://www.reddit.com"
    
    # 限流配置
    RATE_LIMIT_DELAY = 1.0  # 请求间隔（秒），确保不超过 60 次/分钟
    
    def __init__(self, timeout: int = 30, verify_ssl: bool = False):
        """
        初始化抓取器
        
        Args:
            timeout: 请求超时时间（秒）
            verify_ssl: 是否验证 SSL 证书（默认 False，避免 macOS Python 环境问题）
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0  # 上次请求时间戳
        self.user_agent = "WRHITW-Reddit-Fetcher/1.0 (by /u/wrhitw_bot)"
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
    
    async def fetch_subreddit(self, subreddit: str, limit: int = 25) -> List[Article]:
        """
        抓取单个 Subreddit 的 Hot 帖子
        
        Args:
            subreddit: Subreddit 名称
            limit: 最多抓取帖子数（Reddit API 最大 100）
            
        Returns:
            文章列表
        """
        await self._respect_rate_limit()
        
        session = await self._get_session()
        articles = []
        
        url = f"{self.BASE_URL}/r/{subreddit}/hot.json?limit={min(limit, 100)}"
        
        try:
            logger.info(f"📰 开始抓取 r/{subreddit} Hot 帖子")
            
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"⚠️  抓取 r/{subreddit} 失败：HTTP {response.status}")
                    return []
                
                data = await response.json()
                
                # 解析帖子
                posts = data.get('data', {}).get('children', [])
                
                for post in posts:
                    article = self._parse_post(post, subreddit)
                    if article:
                        articles.append(article)
                
                logger.info(f"✅ 从 r/{subreddit} 抓取 {len(articles)} 个帖子")
                
        except asyncio.TimeoutError:
            logger.error(f"❌ 抓取 r/{subreddit} 超时")
        except aiohttp.ClientError as e:
            logger.error(f"❌ 抓取 r/{subreddit} 网络错误：{e}")
        except Exception as e:
            logger.error(f"❌ 抓取 r/{subreddit} 异常：{e}")
        
        return articles
    
    def _parse_post(self, post: Dict, subreddit: str) -> Optional[Article]:
        """
        解析 Reddit 帖子为 Article 对象
        
        Args:
            post: Reddit 帖子数据
            subreddit: 所属 Subreddit
            
        Returns:
            Article 对象或 None
        """
        try:
            data = post.get('data', {})
            
            # 提取标题
            title = data.get('title', '').strip()
            if not title:
                return None
            
            # 提取自文本内容（如果有）
            selftext = data.get('selftext', '')
            summary = selftext[:2000] if selftext else ''
            
            # 提取链接（优先使用外部链接，如果没有则使用 Reddit 链接）
            url = data.get('url', '')
            permalink = data.get('permalink', '')
            
            # 如果是 Reddit 内部链接，构建完整 URL
            if url.startswith('/r/') or not url.startswith('http'):
                url = f"{self.BASE_URL}{permalink}"
            
            if not url:
                return None
            
            # 提取发布时间
            created_utc = data.get('created_utc', 0)
            if created_utc:
                published_at = datetime.fromtimestamp(created_utc, tz=timezone.utc)
            else:
                published_at = datetime.utcnow()
            
            # 提取热度数据
            score = data.get('score', 0)  # 点赞数
            num_comments = data.get('num_comments', 0)  # 评论数
            
            # 构建唯一 URL（使用 Reddit 永久链接）
            reddit_url = f"{self.BASE_URL}{permalink}"
            
            # 创建文章对象
            article = Article(
                title=title,
                summary=summary,
                url=reddit_url,
                published_at=published_at,
                source_id=self._get_source_id(subreddit),
                source_priority="P1",  # Reddit 设为 P1 优先级
                fetched_at=datetime.utcnow(),
                heat_score=float(score),  # 使用 score 作为初始热度
                comment_count=num_comments,
                is_processed=False
            )
            
            return article
            
        except Exception as e:
            logger.warning(f"⚠️  解析 Reddit 帖子失败：{e}")
            return None
    
    def _get_source_id(self, subreddit: str) -> int:
        """
        根据 subreddit 获取 source_id
        
        Args:
            subreddit: Subreddit 名称
            
        Returns:
            source_id（需要在数据库中预先配置）
        """
        # 临时映射，实际应该在数据库中配置
        subreddit_id_map = {
            "all": 101,
            "worldnews": 102,
            "news": 103,
            "technology": 104
        }
        return subreddit_id_map.get(subreddit, 100)
    
    async def fetch_all(self, limit: int = 25) -> Dict[str, List[Article]]:
        """
        并发抓取所有目标 Subreddits
        
        Args:
            limit: 每个 Subreddit 最多抓取帖子数
            
        Returns:
            {subreddit 名称：文章列表} 字典
        """
        tasks = [self.fetch_subreddit(sub, limit) for sub in self.TARGET_SUBREDDITS]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            sub: result if not isinstance(result, Exception) else []
            for sub, result in zip(self.TARGET_SUBREDDITS, results)
        }
    
    async def fetch_all_sequential(self, limit: int = 25) -> List[Article]:
        """
        顺序抓取所有目标 Subreddits（严格遵守限流）
        
        Args:
            limit: 每个 Subreddit 最多抓取帖子数
            
        Returns:
            所有文章列表
        """
        all_articles = []
        
        for subreddit in self.TARGET_SUBREDDITS:
            articles = await self.fetch_subreddit(subreddit, limit)
            all_articles.extend(articles)
            logger.info(f"📊 累计抓取 {len(all_articles)} 个帖子")
        
        return all_articles
    
    async def close(self):
        """关闭 HTTP 会话"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("🔒 Reddit HTTP 会话已关闭")
