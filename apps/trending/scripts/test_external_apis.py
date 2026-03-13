"""
Reddit & Hacker News 抓取测试脚本
- 测试 Reddit API 抓取功能
- 测试 Hacker News API 抓取功能
- 验证数据格式转换
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.reddit_fetcher import RedditFetcher
from app.services.hackernews_fetcher import HackerNewsFetcher
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_reddit_fetcher():
    """测试 Reddit 抓取器"""
    print("\n" + "="*60)
    print("🔴 测试 Reddit API 抓取")
    print("="*60)
    
    fetcher = RedditFetcher(timeout=30)
    
    try:
        # 测试单个 Subreddit
        print("\n📌 测试 1: 抓取 r/technology Hot 帖子")
        articles = await fetcher.fetch_subreddit("technology", limit=10)
        print(f"✅ 抓取成功：{len(articles)} 个帖子")
        
        if articles:
            print("\n📊 前 3 个帖子示例:")
            for i, article in enumerate(articles[:3], 1):
                print(f"\n  {i}. {article.title[:80]}...")
                print(f"     URL: {article.url}")
                print(f"     热度：{article.heat_score}")
                print(f"     评论：{article.comment_count}")
                print(f"     时间：{article.published_at}")
        
        # 测试所有 Subreddits
        print("\n📌 测试 2: 抓取所有目标 Subreddits")
        all_results = await fetcher.fetch_all(limit=5)
        
        total = sum(len(arts) for arts in all_results.values())
        print(f"✅ 总计抓取：{total} 个帖子")
        
        for subreddit, articles in all_results.items():
            print(f"   - r/{subreddit}: {len(articles)} 个")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await fetcher.close()


async def test_hackernews_fetcher():
    """测试 Hacker News 抓取器"""
    print("\n" + "="*60)
    print("🟠 测试 Hacker News API 抓取")
    print("="*60)
    
    fetcher = HackerNewsFetcher(timeout=30, max_stories=30)
    
    try:
        # 测试获取 Top Stories
        print("\n📌 测试 1: 获取 Top Stories")
        articles = await fetcher.fetch_top_stories(limit=20)
        print(f"✅ 抓取成功：{len(articles)} 个故事")
        
        if articles:
            print("\n📊 前 3 个故事示例:")
            for i, article in enumerate(articles[:3], 1):
                print(f"\n  {i}. {article.title[:80]}...")
                print(f"     URL: {article.url}")
                print(f"     热度：{article.heat_score}")
                print(f"     评论：{article.comment_count}")
                print(f"     时间：{article.published_at}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await fetcher.close()


async def test_article_model():
    """测试 Article 模型数据完整性"""
    print("\n" + "="*60)
    print("📝 测试 Article 模型数据完整性")
    print("="*60)
    
    fetcher_reddit = RedditFetcher(timeout=30)
    fetcher_hn = HackerNewsFetcher(timeout=30, max_stories=10)
    
    try:
        # 获取示例文章
        reddit_articles = await fetcher_reddit.fetch_subreddit("news", limit=5)
        hn_articles = await fetcher_hn.fetch_top_stories(limit=5)
        
        all_articles = reddit_articles + hn_articles
        
        print(f"\n📊 测试 {len(all_articles)} 个 Article 对象")
        
        # 验证必填字段
        required_fields = ['title', 'url', 'published_at', 'source_id']
        
        for i, article in enumerate(all_articles, 1):
            errors = []
            
            for field in required_fields:
                if not getattr(article, field, None):
                    errors.append(f"缺少 {field}")
            
            if errors:
                print(f"  ❌ Article {i}: {', '.join(errors)}")
            else:
                print(f"  ✅ Article {i}: 所有必填字段完整")
        
        # 验证 to_dict 方法
        print("\n📌 测试 to_dict() 方法:")
        if all_articles:
            sample = all_articles[0]
            data = sample.to_dict()
            print(f"✅ 转换成功，包含字段：{list(data.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await fetcher_reddit.close()
        await fetcher_hn.close()


async def main():
    """主测试函数"""
    print("\n" + "🚀"*30)
    print("WRHITW - Reddit & Hacker News API 集成测试")
    print("🚀"*30)
    
    results = {
        "Reddit API": await test_reddit_fetcher(),
        "Hacker News API": await test_hackernews_fetcher(),
        "Article 模型": await test_article_model()
    }
    
    # 汇总结果
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
