#!/usr/bin/env python3
"""
RSS 抓取测试脚本
- 测试抓取 3 个 P0 数据源
- 验证解析结果
"""
import sys
import os
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rss_fetcher import RSSFetcher
from app.config import get_sources_by_priority
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_fetch():
    """测试 RSS 抓取"""
    print("=" * 60)
    print("WRHITW Trending MVP - RSS 抓取测试")
    print("=" * 60)
    
    # 获取 P0 优先级数据源（测试前 3 个）
    sources = get_sources_by_priority("P0")[:3]
    
    print(f"\n📰 测试数据源:")
    for source in sources:
        print(f"  - {source['name']} ({source['url']})")
    
    print("\n🚀 开始抓取...\n")
    
    fetcher = RSSFetcher()
    
    try:
        # 并发抓取
        results = await fetcher.fetch_all(sources)
        
        # 输出结果
        print("\n" + "=" * 60)
        print("📊 抓取结果统计:")
        print("=" * 60)
        
        total_articles = 0
        for source_name, articles in results.items():
            article_count = len(articles)
            total_articles += article_count
            status = "✅" if article_count > 0 else "❌"
            print(f"{status} {source_name}: {article_count} 篇文章")
            
            # 显示前 3 篇文章标题
            if articles:
                for i, article in enumerate(articles[:3], 1):
                    print(f"    {i}. {article.title[:60]}...")
        
        print("\n" + "-" * 60)
        print(f"📈 总计：{total_articles} 篇文章")
        print("=" * 60)
        
        if total_articles > 0:
            print("\n✅ RSS 抓取测试成功！")
        else:
            print("\n⚠️  未抓取到任何文章，请检查网络或 RSS 源")
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await fetcher.close()


if __name__ == "__main__":
    asyncio.run(test_fetch())
