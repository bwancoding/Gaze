# WRHITW Trending MVP

热榜话题聚合服务 - 抓取全球新闻媒体，计算事件热度，提供实时热榜 API

## 📋 项目状态

- ✅ **任务 1**: RSS 新闻源配置 - 完成
- ✅ **任务 2**: 数据库表结构实现 - 完成
- 🚧 **任务 3**: Reddit API 集成 - 进行中
- ⏳ **任务 4**: Hacker News API 集成
- ⏳ **任务 5**: 热度算法实现
- ⏳ **任务 6**: 事件去重聚类
- ⏳ **任务 7**: API 开发
- ⏳ **任务 8**: 定时任务调度
- ⏳ **任务 9**: 前端热榜页面
- ⏳ **任务 10**: 集成测试 + 部署

## 🚀 快速开始

### 1. 环境准备

```bash
# Python 3.11+
python --version

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置数据库连接等
```

### 3. 初始化数据库

```bash
# 方式 1: 使用 Python 脚本（推荐）
python scripts/init_db.py

# 方式 2: 使用 SQL 迁移文件
psql -U wrhitw -d wrhitw -f migrations/001_initial_schema.sql
```

### 4. 测试 RSS 抓取

```bash
python scripts/test_rss_fetch.py
```

### 5. 启动服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
python app/main.py
```

### 6. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查：http://localhost:8000/health

## 📁 项目结构

```
trending/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理（含 15 家媒体 RSS 源）
│   ├── database.py          # 数据库连接
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── source.py        # 数据源模型
│   │   ├── event.py         # 事件聚类模型
│   │   └── article.py       # 文章模型
│   ├── services/            # 业务逻辑
│   │   ├── __init__.py
│   │   └── rss_fetcher.py   # RSS 抓取服务
│   ├── api/                 # API 路由
│   │   ├── __init__.py
│   │   └── health.py        # 健康检查
│   ├── scheduler/           # 定时任务（待实现）
│   └── utils/               # 工具函数（待实现）
├── tests/                   # 测试（待实现）
├── scripts/                 # 脚本
│   ├── init_db.py          # 数据库初始化
│   └── test_rss_fetch.py   # RSS 抓取测试
├── migrations/              # 数据库迁移
│   └── 001_initial_schema.sql
├── requirements.txt         # Python 依赖
├── .env.example            # 环境变量模板
└── README.md               # 本文件
```

## 🗄️ 数据库表结构

### sources (数据源表)
- `id`: 主键
- `name`: 媒体名称
- `url`: RSS URL
- `stance`: 政治立场 (left/center/right)
- `region`: 地区 (us/uk/international)
- `priority`: 优先级 (P0/P1/P2)
- `enabled`: 是否启用

### events (事件表)
- `id`: 主键
- `title`: 事件标题
- `summary`: 事件摘要
- `keywords`: 关键词列表 (JSONB)
- `heat_score`: 热度分数
- `article_count`: 文章数量
- `media_count`: 媒体数量

### articles (文章表)
- `id`: 主键
- `event_id`: 所属事件 ID
- `source_id`: 数据源 ID
- `title`: 文章标题
- `summary`: 文章摘要
- `url`: 文章链接
- `published_at`: 发布时间
- `heat_score`: 热度分数
- `is_processed`: 是否已聚类

## 📊 已配置媒体源 (15 家)

### P0 优先级 (每 15-30 分钟)
1. Reuters (中间，国际)
2. Associated Press (中间，国际)
3. BBC News (中间偏左，英国)
4. The Guardian (左派，英国)
5. Financial Times (中间，英国)
6. Bloomberg (中间，美国)

### P1 优先级 (每 30-60 分钟)
7. CNN (左派，美国)
8. Fox News (右派，美国)
9. The New York Times (左派，美国)
10. The Wall Street Journal (右派，美国)
11. The Economist (中间偏右，英国)
12. Al Jazeera (中间，卡塔尔)

### P2 优先级 (每小时)
13. Politico (中间偏左，美国)
14. The Hill (中间，美国)
15. NPR (左派，美国)

## 🧪 测试

```bash
# RSS 抓取测试
python scripts/test_rss_fetch.py

# 数据库初始化测试
python scripts/init_db.py
```

## 📝 下一步

1. ✅ ~~RSS 新闻源配置~~
2. ✅ ~~数据库表结构实现~~
3. 🚧 Reddit API 集成
4. ⏳ Hacker News API 集成
5. ⏳ 热度算法实现
6. ⏳ 事件去重聚类
7. ⏳ API 开发
8. ⏳ 定时任务调度
9. ⏳ 前端热榜页面
10. ⏳ 集成测试 + 部署

## 📄 许可证

MIT License

---

**开发团队**: WRHITW  
**最后更新**: 2026-03-13
