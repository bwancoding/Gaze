# 外部 API 集成使用说明

本文档说明如何使用 Reddit 和 Hacker News API 抓取服务。

---

## 📦 新增服务

### 1. RedditFetcher - Reddit API 抓取器

**文件位置**: `app/services/reddit_fetcher.py`

**功能**:
- 抓取 Reddit Hot 帖子（r/all, r/worldnews, r/news, r/technology）
- 自动转换为统一 Article 模型
- 限流处理（60 次/分钟）
- 异步并发支持

**使用示例**:

```python
from app.services.reddit_fetcher import RedditFetcher
import asyncio

async def main():
    fetcher = RedditFetcher(timeout=30, verify_ssl=False)
    
    # 抓取单个 Subreddit
    articles = await fetcher.fetch_subreddit("technology", limit=25)
    
    # 抓取所有目标 Subreddits
    all_articles = await fetcher.fetch_all(limit=10)
    
    # 顺序抓取（严格遵守限流）
    all_articles = await fetcher.fetch_all_sequential(limit=10)
    
    await fetcher.close()

asyncio.run(main())
```

**参数说明**:
- `timeout`: 请求超时时间（秒），默认 30
- `verify_ssl`: 是否验证 SSL 证书，默认 False（避免 macOS Python 环境问题）

**数据映射**:
```
Reddit 帖子 → Article 模型
- title → title
- selftext → summary
- permalink → url
- created_utc → published_at
- score → heat_score
- num_comments → comment_count
```

---

### 2. HackerNewsFetcher - Hacker News API 抓取器

**文件位置**: `app/services/hackernews_fetcher.py`

**功能**:
- 使用 Firebase API 获取 Top Stories
- 数据格式转换为统一 Article 模型
- 并发控制（10 个并发请求）
- 限流处理（0.5 秒/请求）

**使用示例**:

```python
from app.services.hackernews_fetcher import HackerNewsFetcher
import asyncio

async def main():
    fetcher = HackerNewsFetcher(timeout=30, max_stories=50, verify_ssl=False)
    
    # 获取 Top Stories
    articles = await fetcher.fetch_top_stories(limit=30)
    
    await fetcher.close()

asyncio.run(main())
```

**参数说明**:
- `timeout`: 请求超时时间（秒），默认 30
- `max_stories`: 最多抓取故事数，默认 50
- `verify_ssl`: 是否验证 SSL 证书，默认 False

**数据映射**:
```
Hacker News 故事 → Article 模型
- title → title
- text → summary
- url (或 item?id=) → url
- time → published_at
- score → heat_score
- descendants → comment_count
```

---

## 🧪 测试脚本

### 测试外部 API 抓取

**脚本位置**: `scripts/test_external_apis_simple.py`

**运行方式**:
```bash
cd /Users/bwan/.openclaw/workspace/main/wrhitw/apps/trending
python3 scripts/test_external_apis_simple.py
```

**测试内容**:
- Reddit API 抓取测试（r/technology）
- Hacker News API 抓取测试（Top Stories）
- Article 模型数据完整性验证

**预期输出**:
```
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
WRHITW - Reddit & Hacker News API 集成测试
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

============================================================
🔴 测试 Reddit API 抓取
============================================================

📌 测试：抓取 r/technology Hot 帖子
✅ 抓取成功：10 个帖子

📊 前 3 个帖子示例:
  1. [标题]...
     URL: https://www.reddit.com/r/technology/comments/...
     热度：27993.0
     评论：2092

============================================================
🟠 测试 Hacker News API 抓取
============================================================

📌 测试：获取 Top Stories
✅ 抓取成功：15 个故事

============================================================
📊 测试结果汇总
============================================================
Reddit API: ✅ 通过
Hacker News API: ✅ 通过
============================================================
🎉 所有测试通过！
============================================================
```

---

## ⚠️ 注意事项

### 1. SSL 证书问题

在 macOS 上使用 Python 3.13 可能会遇到 SSL 证书验证错误：
```
SSLCertVerificationError: certificate verify failed
```

**解决方案**: 设置 `verify_ssl=False`（默认值）

```python
fetcher = RedditFetcher(verify_ssl=False)
fetcher = HackerNewsFetcher(verify_ssl=False)
```

### 2. API 限流

- **Reddit**: 60 次/分钟，已实现自动限流（1 秒/请求）
- **Hacker News**: 比较宽松，已实现礼貌请求（0.5 秒/请求）

### 3. 数据源 ID 配置

需要在数据库 `sources` 表中配置对应的数据源：

```sql
INSERT INTO sources (id, name, url, stance, region, priority, enabled) VALUES
(101, 'Reddit - r/all', 'https://www.reddit.com/r/all/hot.json', 'mixed', 'international', 'P1', true),
(102, 'Reddit - r/worldnews', 'https://www.reddit.com/r/worldnews/hot.json', 'center', 'international', 'P1', true),
(103, 'Reddit - r/news', 'https://www.reddit.com/r/news/hot.json', 'center', 'us', 'P1', true),
(104, 'Reddit - r/technology', 'https://www.reddit.com/r/technology/hot.json', 'center', 'international', 'P1', true),
(105, 'Hacker News', 'https://news.ycombinator.com/', 'center', 'international', 'P1', true);
```

---

## 🔧 集成到定时任务

在 `app/scheduler/` 中创建定时任务，定期抓取外部 API：

```python
from app.services.reddit_fetcher import RedditFetcher
from app.services.hackernews_fetcher import HackerNewsFetcher
from app.database import get_db
from app.models.article import Article

async def fetch_external_sources():
    """定时抓取外部数据源"""
    db = next(get_db())
    
    # 抓取 Reddit
    reddit_fetcher = RedditFetcher()
    reddit_articles = await reddit_fetcher.fetch_all_sequential(limit=25)
    
    # 保存到数据库
    for article in reddit_articles:
        db.add(article)
    
    # 抓取 Hacker News
    hn_fetcher = HackerNewsFetcher()
    hn_articles = await hn_fetcher.fetch_top_stories(limit=30)
    
    # 保存到数据库
    for article in hn_articles:
        db.add(article)
    
    db.commit()
    
    await reddit_fetcher.close()
    await hn_fetcher.close()
    db.close()
```

---

## 📝 下一步

1. **任务 5**: 实现热度算法
2. **任务 6**: 实现事件去重聚类
3. **任务 7**: 开发 API 接口
4. **任务 8**: 配置定时任务

---

**文档更新**: 2026-03-13  
**开发者**: 小狗 🐶
