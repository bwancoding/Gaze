"""
RSS 抓取服务
- 支持异步并发抓取
- 自动解析 RSS/Atom 格式
- 错误处理和重试机制
"""
import aiohttp
import feedparser
from typing import List, Dict, Optional
from datetime import datetime, timezone
from app.config import settings
from app.models.article import Article
import logging

logger = logging.getLogger(__name__)


class RSSFetcher:
    """RSS 抓取器"""
    
    def __init__(self, timeout: int = None):
        """
        初始化抓取器
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout or settings.RSS_FETCH_TIMEOUT)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建 HTTP 会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    'User-Agent': 'WRHITW-RSS-Fetcher/1.0 (+https://wrhitw.com; bot@wrhitw.com)'
                }
            )
        return self.session
    
    async def fetch(self, source: Dict) -> List[Article]:
        """
        抓取单个 RSS 源
        
        Args:
            source: 数据源配置字典
            
        Returns:
            文章列表
        """
        session = await self._get_session()
        articles = []
        
        try:
            logger.info(f"📰 开始抓取 {source['name']} ({source['url']})")
            
            async with session.get(source["url"]) as response:
                if response.status != 200:
                    logger.warning(f"⚠️  抓取 {source['name']} 失败：HTTP {response.status}")
                    return []
                
                content = await response.text('utf-8')
                feed = feedparser.parse(content)
                
                # 解析文章
                for entry in feed.entries[:settings.RSS_MAX_ARTICLES_PER_FEED]:
                    article = self._parse_entry(entry, source)
                    if article:
                        articles.append(article)
                
                logger.info(f"✅ 从 {source['name']} 抓取 {len(articles)} 篇文章")
                
        except asyncio.TimeoutError:
            logger.error(f"❌ 抓取 {source['name']} 超时")
        except aiohttp.ClientError as e:
            logger.error(f"❌ 抓取 {source['name']} 网络错误：{e}")
        except Exception as e:
            logger.error(f"❌ 抓取 {source['name']} 异常：{e}")
        
        return articles
    
    def _parse_entry(self, entry, source: Dict) -> Optional[Article]:
        """
        解析 RSS 条目为文章对象
        
        Args:
            entry: RSS 条目
            source: 数据源配置
            
        Returns:
            Article 对象或 None
        """
        try:
            # 提取标题
            title = getattr(entry, 'title', '').strip()
            if not title:
                return None
            
            # 提取摘要
            summary = ''
            if hasattr(entry, 'summary'):
                summary = entry.summary.strip()
            elif hasattr(entry, 'description'):
                summary = entry.description.strip()
            
            # 提取链接
            url = getattr(entry, 'link', '')
            if not url:
                return None
            
            # 提取发布时间
            published_at = self._parse_date(entry)
            if not published_at:
                published_at = datetime.utcnow()
            
            # 创建文章对象
            article = Article(
                title=title,
                summary=summary[:2000] if summary else '',  # 限制摘要长度
                url=url,
                published_at=published_at,
                source_id=source["id"],
                source_priority=source["priority"],
                fetched_at=datetime.utcnow(),
                is_processed=False
            )
            
            return article
            
        except Exception as e:
            logger.warning(f"⚠️  解析 RSS 条目失败：{e}")
            return None
    
    def _parse_date(self, entry) -> Optional[datetime]:
        """
        解析发布日期
        
        Args:
            entry: RSS 条目
            
        Returns:
            datetime 对象或 None
        """
        # 尝试多个可能的时间字段
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in date_fields:
            if hasattr(entry, field) and entry[field]:
                try:
                    time_struct = entry[field]
                    return datetime(
                        time_struct.tm_year,
                        time_struct.tm_mon,
                        time_struct.tm_mday,
                        time_struct.tm_hour,
                        time_struct.tm_min,
                        time_struct.tm_sec,
                        tzinfo=timezone.utc
                    )
                except (ValueError, TypeError):
                    continue
        
        # 尝试原始时间字符串
        if hasattr(entry, 'published') and entry.published:
            try:
                # feedparser 会自动解析常见格式
                from email.utils import parsedate_to_datetime
                return parsedate_to_datetime(entry.published)
            except:
                pass
        
        return None
    
    async def fetch_all(self, sources: List[Dict]) -> Dict[str, List[Article]]:
        """
        并发抓取多个源
        
        Args:
            sources: 数据源配置列表
            
        Returns:
            {源名称：文章列表} 字典
        """
        import asyncio
        
        tasks = [self.fetch(source) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            source["name"]: result if not isinstance(result, Exception) else []
            for source, result in zip(sources, results)
        }
    
    async def close(self):
        """关闭 HTTP 会话"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("🔒 HTTP 会话已关闭")
