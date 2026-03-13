"""
Reddit & Hacker News 抓取测试脚本（独立版）
- 不依赖数据库连接
- 直接测试 API 抓取功能
- 验证数据格式
- 支持禁用 SSL 验证（用于测试环境）
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aiohttp
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleArticle:
    """简化版 Article 模型（用于测试，不依赖数据库）"""
    
    def __init__(self, title: str, url: str, published_at: datetime, 
                 source_id: int, summary: str = '', heat_score: float = 0.0,
                 comment_count: int = 0, is_processed: bool = False):
        self.title = title
        self.summary = summary
        self.url = url
        self.published_at = published_at
        self.source_id = source_id
        self.heat_score = heat_score
        self.comment_count = comment_count
        self.is_processed = is_processed
        self.fetched_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<SimpleArticle(title='{self.title[:50]}...', score={self.heat_score})>"


class RedditFetcher:
    """Reddit 抓取器（简化版）"""
    
    TARGET_SUBREDDITS = ["all", "worldnews", "news", "technology"]
    BASE_URL = "https://www.reddit.com"
    RATE_LIMIT_DELAY = 1.0
    
    def __init__(self, timeout: int = 30, verify_ssl: bool = False):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0
        self.user_agent = "WRHITW-Reddit-Fetcher/1.0 (by /u/wrhitw_bot)"
        self.verify_ssl = verify_ssl
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={'User-Agent': self.user_agent},
                connector=connector
            )
        return self.session
    
    async def _respect_rate_limit(self):
        import time
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - time_since_last)
        self.last_request_time = time.time()
    
    async def fetch_subreddit(self, subreddit: str, limit: int = 10) -> List[SimpleArticle]:
        """抓取单个 Subreddit 的 Hot 帖子"""
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
    
    def _parse_post(self, post: Dict, subreddit: str) -> Optional[SimpleArticle]:
        """解析 Reddit 帖子为 Article 对象"""
        try:
            data = post.get('data', {})
            
            title = data.get('title', '').strip()
            if not title:
                return None
            
            selftext = data.get('selftext', '')
            summary = selftext[:2000] if selftext else ''
            
            permalink = data.get('permalink', '')
            url = f"{self.BASE_URL}{permalink}"
            
            created_utc = data.get('created_utc', 0)
            if created_utc:
                published_at = datetime.fromtimestamp(created_utc, tz=timezone.utc)
            else:
                published_at = datetime.utcnow()
            
            score = data.get('score', 0)
            num_comments = data.get('num_comments', 0)
            
            subreddit_id_map = {"all": 101, "worldnews": 102, "news": 103, "technology": 104}
            source_id = subreddit_id_map.get(subreddit, 100)
            
            return SimpleArticle(
                title=title,
                summary=summary,
                url=url,
                published_at=published_at,
                source_id=source_id,
                heat_score=float(score),
                comment_count=num_comments
            )
            
        except Exception as e:
            logger.warning(f"⚠️  解析 Reddit 帖子失败：{e}")
            return None
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


class HackerNewsFetcher:
    """Hacker News 抓取器（简化版）"""
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    RATE_LIMIT_DELAY = 0.5
    
    def __init__(self, timeout: int = 30, max_stories: int = 30, verify_ssl: bool = False):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0
        self.max_stories = max_stories
        self.user_agent = "WRHITW-HN-Fetcher/1.0 (+https://wrhitw.com)"
        self.verify_ssl = verify_ssl
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={'User-Agent': self.user_agent},
                connector=connector
            )
        return self.session
    
    async def _respect_rate_limit(self):
        import time
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - time_since_last)
        self.last_request_time = time.time()
    
    async def get_top_stories_ids(self, limit: int = None) -> List[int]:
        """获取 Top Stories ID 列表"""
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
                if limit:
                    story_ids = story_ids[:limit]
                
                logger.info(f"✅ 获取 {len(story_ids)} 个 Top Stories IDs")
                return story_ids
                
        except Exception as e:
            logger.error(f"❌ 获取 Top Stories 异常：{e}")
            return []
    
    async def get_story(self, story_id: int) -> Optional[Dict]:
        """获取单个故事详情"""
        await self._respect_rate_limit()
        session = await self._get_session()
        url = f"{self.BASE_URL}/item/{story_id}.json"
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                return await response.json()
        except Exception as e:
            logger.warning(f"⚠️  获取故事 {story_id} 失败：{e}")
            return None
    
    async def fetch_top_stories(self, limit: int = None) -> List[SimpleArticle]:
        """获取 Top Stories 并转换为文章列表"""
        limit = limit or self.max_stories
        story_ids = await self.get_top_stories_ids(limit=limit)
        
        if not story_ids:
            return []
        
        articles = []
        semaphore = asyncio.Semaphore(10)
        
        async def fetch_with_semaphore(story_id):
            async with semaphore:
                return await self.get_story(story_id)
        
        tasks = [fetch_with_semaphore(sid) for sid in story_ids]
        stories = await asyncio.gather(*tasks, return_exceptions=True)
        
        for story_id, story in zip(story_ids, stories):
            if isinstance(story, Exception) or story is None:
                continue
            
            article = self._parse_story(story, story_id)
            if article:
                articles.append(article)
        
        logger.info(f"✅ 解析 {len(articles)} 个 Hacker News 故事")
        return articles
    
    def _parse_story(self, story: Dict, story_id: int) -> Optional[SimpleArticle]:
        """解析 Hacker News 故事为 Article 对象"""
        try:
            title = story.get('title', '').strip()
            if not title:
                return None
            
            url = story.get('url', '')
            hn_url = f"https://news.ycombinator.com/item?id={story_id}"
            if not url:
                url = hn_url
            
            text = story.get('text', '')
            summary = text[:2000] if text else ''
            
            time_utc = story.get('time', 0)
            if time_utc:
                published_at = datetime.fromtimestamp(time_utc, tz=timezone.utc)
            else:
                published_at = datetime.utcnow()
            
            score = story.get('score', 0)
            descendants = story.get('descendants', 0)
            
            return SimpleArticle(
                title=title,
                summary=summary,
                url=url,
                published_at=published_at,
                source_id=105,
                heat_score=float(score),
                comment_count=descendants
            )
            
        except Exception as e:
            logger.warning(f"⚠️  解析 Hacker News 故事失败：{e}")
            return None
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


async def test_reddit(verify_ssl: bool = False):
    """测试 Reddit 抓取器"""
    print("\n" + "="*60)
    print("🔴 测试 Reddit API 抓取")
    print("="*60)
    
    fetcher = RedditFetcher(timeout=30, verify_ssl=verify_ssl)
    
    try:
        print("\n📌 测试：抓取 r/technology Hot 帖子")
        articles = await fetcher.fetch_subreddit("technology", limit=10)
        print(f"✅ 抓取成功：{len(articles)} 个帖子")
        
        if articles:
            print("\n📊 前 3 个帖子示例:")
            for i, article in enumerate(articles[:3], 1):
                print(f"\n  {i}. {article.title[:80]}...")
                print(f"     URL: {article.url}")
                print(f"     热度：{article.heat_score}")
                print(f"     评论：{article.comment_count}")
            return True
        else:
            print("⚠️  未获取到文章（可能是网络问题）")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await fetcher.close()


async def test_hackernews(verify_ssl: bool = False):
    """测试 Hacker News 抓取器"""
    print("\n" + "="*60)
    print("🟠 测试 Hacker News API 抓取")
    print("="*60)
    
    fetcher = HackerNewsFetcher(timeout=30, max_stories=20, verify_ssl=verify_ssl)
    
    try:
        print("\n📌 测试：获取 Top Stories")
        articles = await fetcher.fetch_top_stories(limit=15)
        print(f"✅ 抓取成功：{len(articles)} 个故事")
        
        if articles:
            print("\n📊 前 3 个故事示例:")
            for i, article in enumerate(articles[:3], 1):
                print(f"\n  {i}. {article.title[:80]}...")
                print(f"     URL: {article.url}")
                print(f"     热度：{article.heat_score}")
                print(f"     评论：{article.comment_count}")
            return True
        else:
            print("⚠️  未获取到文章（可能是网络问题）")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await fetcher.close()


async def main():
    """主测试函数"""
    print("\n" + "🚀"*30)
    print("WRHITW - Reddit & Hacker News API 集成测试")
    print("🚀"*30)
    
    # 尝试使用 SSL 验证，如果失败则禁用
    verify_ssl = False  # 默认禁用，避免 macOS Python SSL 问题
    
    results = {
        "Reddit API": await test_reddit(verify_ssl=verify_ssl),
        "Hacker News API": await test_hackernews(verify_ssl=verify_ssl)
    }
    
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查日志")
    print("="*60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
