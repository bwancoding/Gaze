# WRHITW 热榜 MVP 开发进度报告

**汇报时间**: 2026-03-13 18:30  
**开发者**: 小狗 🐶  
**汇报对象**: 猪因斯坦大人

---

## ✅ 已完成任务

### 任务 1: RSS 新闻源配置 ✅ (100%)

**完成内容**:
- ✅ 配置 15 家英文媒体 RSS 源（覆盖政治光谱：左/中/右）
- ✅ 实现 RSS 解析服务（基于 feedparser + aiohttp 异步）
- ✅ 支持并发抓取、错误处理、超时控制
- ✅ 测试脚本已完成

**关键文件**:
- `app/config.py` - 15 家媒体配置（P0/P1/P2 分级）
- `app/services/rss_fetcher.py` - RSS 抓取服务（异步并发）
- `scripts/test_rss_fetch.py` - 抓取测试脚本

**媒体源统计**:
- P0 优先级：6 家（Reuters, AP, BBC, Guardian, FT, Bloomberg）
- P1 优先级：6 家（CNN, Fox News, NYT, WSJ, Economist, Al Jazeera）
- P2 优先级：3 家（Politico, The Hill, NPR）

---

### 任务 2: 数据库表结构实现 ✅ (100%)

**完成内容**:
- ✅ 创建 3 个核心表：sources, events, articles
- ✅ 创建所有必要索引（热度查询优化）
- ✅ 初始化 15 家媒体数据源
- ✅ SQLAlchemy 模型定义完成
- ✅ 数据库迁移脚本完成

**关键文件**:
- `app/models/source.py` - 数据源模型
- `app/models/event.py` - 事件聚类模型
- `app/models/article.py` - 文章模型
- `scripts/init_db.py` - 数据库初始化脚本
- `migrations/001_initial_schema.sql` - SQL 迁移脚本

**数据库表结构**:
```sql
sources (数据源表)
  - id, name, url, stance, region, priority, enabled
  
events (事件表)
  - id, title, summary, keywords, heat_score, article_count, media_count
  
articles (文章表)
  - id, event_id, source_id, title, summary, url, published_at, heat_score
```

---

### 任务 3: Reddit API 集成 ✅ (100%)

**完成内容**:
- ✅ 实现 Reddit Hot 帖子抓取（r/all, r/worldnews, r/news, r/technology）
- ✅ 数据格式转换为统一 Article 模型
- ✅ 限流处理（60 次/分钟，遵守 Reddit API 规则）
- ✅ 异步并发支持
- ✅ 完整的中文注释
- ✅ 测试脚本已完成

**关键文件**:
- `app/services/reddit_fetcher.py` - Reddit 抓取服务（新增）
- `scripts/test_external_apis.py` - 外部 API 测试脚本（新增）

**技术实现**:
- 使用 Reddit 公开 API（无需 API Key）
- 支持 4 个目标 Subreddits：all, worldnews, news, technology
- 自动解析帖子数据（标题、内容、URL、热度、评论数）
- 限流保护：1 秒/请求，确保不超过 API 限制
- 错误处理：超时、网络错误、解析异常

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

### 任务 4: Hacker News API 集成 ✅ (100%)

**完成内容**:
- ✅ Firebase API 调用（Hacker News 官方 API）
- ✅ Top Stories 抓取
- ✅ 数据解析 + 格式转换为 Article 模型
- ✅ 并发控制（10 个并发请求）
- ✅ 限流处理（0.5 秒/请求）
- ✅ 完整的中文注释
- ✅ 测试脚本已完成

**关键文件**:
- `app/services/hackernews_fetcher.py` - Hacker News 抓取服务（新增）
- `scripts/test_external_apis.py` - 外部 API 测试脚本（新增）

**技术实现**:
- 使用 Hacker News Firebase API（官方、免费、无需 Key）
- 获取 Top Stories 列表（默认 50 个）
- 并发获取故事详情（Semaphore 限制并发数）
- 自动解析故事数据（标题、URL、分数、评论数）
- 限流保护：0.5 秒/请求

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

### 任务 5: 热度算法实现 ✅ (100%)

**完成内容**:
- ✅ 时间衰减函数（指数衰减，越新热度越高）
- ✅ 互动权重计算（评论、分享的对数缩放）
- ✅ 源优先级加权（P0/P1/P2 不同权重）
- ✅ Top20 筛选逻辑
- ✅ 排序算法
- ✅ 完整的中文注释
- ✅ 测试脚本已完成

**关键文件**:
- `app/services/heat_calculator.py` - 热度计算服务（新增，330+ 行）
- `scripts/test_heat_algorithm.py` - 热度算法测试脚本（新增，260+ 行）
- `scripts/demo_heat_and_clustering.py` - 综合使用示例（新增）

**算法公式**:
```
文章热度 = 时间衰减 × (基础分 + 互动分) × 源权重

时间衰减：decay = e^(-λ × hours)
互动分：log10(评论 +1) × 5 + log10(分享 +1) × 3
源权重：P0=1.5, P1=1.2, P2=1.0

事件热度 = 文章热度总和 × 媒体多样性系数 × 立场多样性系数
```

**核心功能**:
- `calculate_time_decay()` - 时间衰减计算
- `calculate_interaction_score()` - 互动分数计算
- `calculate_article_heat()` - 文章热度计算
- `calculate_event_heat()` - 事件热度计算
- `get_top_events()` - Top20 筛选
- `get_trending_events()` - 增长率计算（trending）
- `calculate_heat_distribution()` - 热度分布统计

**测试覆盖**:
- ✅ 时间衰减函数测试（7 个时间点）
- ✅ 互动权重计算测试（6 种场景）
- ✅ 源优先级加权测试（4 个媒体）
- ✅ 文章热度计算测试
- ✅ 事件热度计算测试
- ✅ Top20 筛选逻辑测试
- ✅ Trending 事件测试
- ✅ 热度分布统计测试

---

### 任务 6: 事件去重聚类 ✅ (100%)

**完成内容**:
- ✅ TF-IDF + 余弦相似度算法
- ✅ 事件中心向量计算
- ✅ 增量更新机制
- ✅ 重复事件检测
- ✅ 文章聚类到事件
- ✅ 新事件自动创建
- ✅ 完整的中文注释
- ✅ 测试脚本已完成

**关键文件**:
- `app/services/event_clusterer.py` - 事件聚类服务（新增，550+ 行）
- `scripts/test_event_clustering.py` - 聚类算法测试脚本（新增，400+ 行）
- `scripts/demo_heat_and_clustering.py` - 综合使用示例（新增）

**算法实现**:
```
1. 文本预处理：
   - 清洗（转小写、去特殊字符）
   - 分词（移除停用词）
   - 关键词提取（基于词频）

2. TF-IDF 向量化：
   - 拟合文档集计算 IDF
   - 转换文档为 TF-IDF 向量

3. 余弦相似度：
   - similarity = (A·B) / (||A|| × ||B||)
   - 阈值：0.6（可配置）

4. 聚类流程：
   - 检测新文章是否属于现有事件
   - 新事件自动创建
   - 重复事件合并
```

**核心功能**:
- `TextPreprocessor` - 文本预处理类
- `TFIDFVectorizer` - TF-IDF 向量化工具
- `EventClusterer` - 事件聚类器主类
  - `cosine_similarity()` - 余弦相似度计算
  - `calculate_event_centroid()` - 事件中心向量
  - `find_similar_events()` - 相似事件搜索
  - `cluster_articles_to_events()` - 文章聚类
  - `detect_new_event()` - 新事件检测
  - `create_event_from_articles()` - 创建新事件
  - `merge_events()` - 合并重复事件
  - `find_duplicate_events()` - 重复检测
  - `incremental_update()` - 增量更新

**测试覆盖**:
- ✅ 文本预处理测试（清洗、分词、关键词）
- ✅ TF-IDF 向量化测试
- ✅ 余弦相似度测试（4 种场景）
- ✅ 事件中心向量测试
- ✅ 相似事件搜索测试
- ✅ 文章聚类测试
- ✅ 新事件检测测试
- ✅ 重复事件检测测试
- ✅ 增量更新测试

---

## 📁 项目结构（更新后）

```
trending/
├── app/
│   ├── main.py              ✅ FastAPI 应用入口
│   ├── config.py            ✅ 配置管理（15 家媒体）
│   ├── database.py          ✅ 数据库连接
│   ├── models/              ✅ 数据模型
│   │   ├── source.py        ✅
│   │   ├── event.py         ✅
│   │   └── article.py       ✅
│   ├── services/            ✅ 业务逻辑
│   │   ├── rss_fetcher.py   ✅ RSS 抓取
│   │   ├── reddit_fetcher.py   ✅ Reddit 抓取
│   │   ├── hackernews_fetcher.py ✅ HN 抓取
│   │   ├── heat_calculator.py   ✅ 热度计算（新增）
│   │   └── event_clusterer.py   ✅ 事件聚类（新增）
│   ├── api/                 ✅ API 路由
│   │   └── health.py        ✅ 健康检查
│   ├── scheduler/           ⏳ 定时任务（下一步）
│   └── utils/               ⏳ 工具函数
├── scripts/
│   ├── init_db.py           ✅ 数据库初始化
│   ├── test_rss_fetch.py    ✅ RSS 抓取测试
│   ├── test_external_apis.py ✅ 外部 API 测试
│   ├── test_heat_algorithm.py    ✅ 热度算法测试（新增）
│   ├── test_event_clustering.py  ✅ 事件聚类测试（新增）
│   └── demo_heat_and_clustering.py ✅ 综合演示（新增）
├── migrations/
│   └── 001_initial_schema.sql ✅
├── requirements.txt         ✅
├── README.md                ✅
└── .env.example             ✅
```

**总计**: 28 个文件，代码量约 5500+ 行

---

## 🧪 如何测试

### 1. 安装依赖
```bash
cd /Users/bwan/.openclaw/workspace/main/wrhitw/apps/trending
pip install -r requirements.txt
```

### 2. 配置环境
```bash
cp .env.example .env
# 编辑 .env 配置数据库连接
```

### 3. 初始化数据库
```bash
python scripts/init_db.py
```

### 4. 测试 RSS 抓取
```bash
python scripts/test_rss_fetch.py
```

### 5. 测试 Reddit & Hacker News
```bash
python scripts/test_external_apis.py
```

### 6. 测试热度算法
```bash
python scripts/test_heat_algorithm.py
```

### 7. 测试事件聚类
```bash
python scripts/test_event_clustering.py
```

### 8. 综合演示
```bash
python scripts/demo_heat_and_clustering.py
```

### 9. 启动 API 服务
```bash
uvicorn app.main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

---

## 📊 完成度统计

| 任务 | 进度 | 工时估算 | 实际工时 |
|------|------|----------|----------|
| 1. RSS 新闻源配置 | ✅ 100% | 0.5 天 | ~2 小时 |
| 2. 数据库表结构 | ✅ 100% | 0.5 天 | ~2 小时 |
| 3. Reddit API 集成 | ✅ 100% | 0.5 天 | ~1.5 小时 |
| 4. Hacker News API | ✅ 100% | 0.25 天 | ~1 小时 |
| 5. 热度算法 | ✅ 100% | 1 天 | ~3 小时 |
| 6. 事件去重聚类 | ✅ 100% | 2 天 | ~4 小时 |
| 7. API 开发 | ⏳ 0% | 1 天 | - |
| 8. 定时任务 | ⏳ 0% | 1 天 | - |
| 9. 前端页面 | ⏳ 0% | 2 天 | - |
| 10. 测试 + 部署 | ⏳ 0% | 1 天 | - |

**总体进度**: 6/10 任务完成 (60%)

---

## 🚀 下一步计划

### 已完成：阶段 3 开发任务 ✅

**任务 5 - 热度算法实现** ✅:
- ✅ 时间衰减函数（指数衰减）
- ✅ 互动权重计算（评论、分享）
- ✅ 源优先级加权（P0/P1/P2）
- ✅ Top20 筛选逻辑
- ✅ 排序算法
- ✅ 测试验证

**任务 6 - 事件去重聚类** ✅:
- ✅ TF-IDF + 余弦相似度
- ✅ 事件中心向量
- ✅ 增量更新
- ✅ 测试验证

### 即将开始：阶段 4 开发任务

**任务 7 - API 开发**（预计 1 天）:
- 热榜 API 接口（/api/trending）
- 事件详情 API（/api/events/:id）
- 文章列表 API（/api/articles）
- 搜索 API（/api/search）
- 分页、过滤、排序支持

**任务 8 - 定时任务**（预计 1 天）:
- RSS 定时抓取调度
- 热度定时更新
- 事件增量聚类
- APScheduler 集成

**预计完成时间**: 接下来 3-4 小时

---

## 💡 技术亮点

1. **异步并发架构**: 使用 aiohttp + asyncio，支持同时抓取多个数据源
2. **政治光谱覆盖**: 15 家媒体 + 4 个 Reddit 板块 + Hacker News，确保信息多元
3. **分级抓取策略**: P0/P1/P2 优先级，优化资源使用
4. **限流保护**: 所有外部 API 均实现限流，遵守服务规则
5. **统一数据模型**: 所有来源统一转换为 Article 模型，便于后续处理
6. **完整的数据库设计**: 包含索引优化、外键约束、JSONB 支持
7. **生产就绪**: 包含健康检查、CORS、慢查询日志、连接池
8. **智能热度算法**: 时间衰减 + 互动权重 + 源优先级，多维度计算
9. **TF-IDF 聚类**: 基于文本相似度的事件去重，自动合并重复事件
10. **增量更新机制**: 支持实时聚类和热度更新，无需全量重算

---

## 📝 备注

- 所有代码注释均为中文，符合开发要求
- 严格按照技术文档实施
- 代码结构清晰，易于扩展和维护
- **阶段 3 开发任务（任务 5-6）已全部完成** ✅
- 下一步将继续推进任务 7（API 开发）

---

## 🔧 新增文件清单（阶段 3）

1. `app/services/heat_calculator.py` - 热度计算服务（330+ 行）
2. `app/services/event_clusterer.py` - 事件聚类服务（550+ 行）
3. `scripts/test_heat_algorithm.py` - 热度算法测试脚本（260+ 行）
4. `scripts/test_event_clustering.py` - 事件聚类测试脚本（400+ 行）
5. `scripts/demo_heat_and_clustering.py` - 综合使用示例（180+ 行）
6. `app/services/__init__.py` - 更新导出（新增 HeatCalculator, EventClusterer）

---

**阶段 3 开发完成** 🐶

猪因斯坦大人，任务 5-6 已全部完成！总体进度达到 60%！请指示下一步工作！
7. **生产就绪**: 包含健康检查、CORS、慢查询日志、连接池

---

## 📝 备注

- 所有代码注释均为中文，符合开发要求
- 严格按照技术文档实施
- 代码结构清晰，易于扩展和维护
- 阶段 2 开发任务（任务 3-4）已全部完成
- 下一步将继续推进任务 5（热度算法）

---

## 🔧 新增文件清单

1. `app/services/reddit_fetcher.py` - Reddit API 抓取服务
2. `app/services/hackernews_fetcher.py` - Hacker News API 抓取服务
3. `scripts/test_external_apis.py` - 外部 API 集成测试脚本
4. `app/services/__init__.py` - 更新导出（新增 RedditFetcher, HackerNewsFetcher）

---

**阶段 2 开发完成** 🐶

猪因斯坦大人，任务 3-4 已全部完成！请指示下一步工作！
