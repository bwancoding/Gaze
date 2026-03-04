# WRHITW 数据字典

📊 **数据库版本**: v1.0  
**创建时间**: 2026-03-04  
**数据库**: PostgreSQL 15+

---

## 📋 总览

| 表名 | 中文名 | 记录数预估 | 说明 |
|------|--------|-----------|------|
| `sources` | 信息源表 | 50-100 | 新闻媒体、通讯社等 |
| `events` | 事件表 | 1000-5000/天 | 新闻事件 |
| `event_sources` | 事件 - 来源表 | 5000-25000/天 | 事件的各来源报道 |
| `ai_summaries` | AI 摘要表 | 1000-5000/天 | AI 生成的多视角摘要 |
| `users` | 用户表 | 10000+ (MVP 目标) | 注册用户 |
| `reading_history` | 阅读历史表 | 100000+ | 用户阅读记录 |
| `bookmarks` | 收藏表 | 50000+ | 用户收藏 |

---

## 📊 核心表详解

### 1. sources - 信息源表

**用途**: 存储新闻媒体、通讯社等信息源的基本信息和抓取配置

#### 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | UUID | ✅ | uuid() | 主键 |
| `name` | VARCHAR(255) | ✅ | - | 媒体名称（如：Reuters） |
| `url` | VARCHAR(512) | ✅ | - | 官方网站 |
| `logo_url` | VARCHAR(512) | ❌ | NULL | Logo URL |
| `bias_label` | VARCHAR(20) | ✅ | 'center' | 立场标签：left/center/right |
| `bias_score` | DECIMAL(3,2) | ❌ | NULL | 立场分数：-1(极左) ~ 1(极右) |
| `country` | VARCHAR(2) | ❌ | NULL | ISO 国家代码（US, CN, GB） |
| `language` | VARCHAR(10) | ✅ | 'en' | 语言代码 |
| `credibility_score` | DECIMAL(3,2) | ❌ | NULL | 可信度：0 ~ 1 |
| `rss_feed_url` | VARCHAR(512) | ❌ | NULL | RSS 订阅地址 |
| `api_endpoint` | VARCHAR(512) | ❌ | NULL | API 地址 |
| `scrape_interval` | INTEGER | ✅ | 900 | 抓取间隔（秒） |
| `is_active` | BOOLEAN | ✅ | true | 是否启用 |
| `last_scraped_at` | TIMESTAMP | ❌ | NULL | 最后抓取时间 |
| `created_at` | TIMESTAMP | ✅ | NOW() | 创建时间 |
| `updated_at` | TIMESTAMP | ✅ | NOW() | 更新时间 |

#### 示例数据

```sql
INSERT INTO sources (name, url, bias_label, bias_score, country, credibility_score) VALUES
('Reuters', 'https://www.reuters.com', 'center', 0.0, 'GB', 0.95),
('The Guardian', 'https://www.theguardian.com', 'left', -0.4, 'GB', 0.85),
('Fox News', 'https://www.foxnews.com', 'right', 0.6, 'US', 0.75);
```

---

### 2. events - 事件表

**用途**: 存储新闻事件的核心信息（中性表述，无立场）

#### 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | UUID | ✅ | uuid() | 主键 |
| `title` | VARCHAR(512) | ✅ | - | 事件标题（中性） |
| `summary` | TEXT | ❌ | NULL | 事件摘要 |
| `description` | TEXT | ❌ | NULL | 详细描述 |
| `category` | VARCHAR(50) | ❌ | NULL | 类别：politics, economy 等 |
| `tags` | TEXT[] | ❌ | NULL | 标签数组 |
| `occurred_at` | TIMESTAMP | ❌ | NULL | 事件发生时间 |
| `created_at` | TIMESTAMP | ✅ | NOW() | 创建时间 |
| `updated_at` | TIMESTAMP | ✅ | NOW() | 更新时间 |
| `hot_score` | DECIMAL(5,2) | ✅ | 0 | 热度分数 |
| `view_count` | INTEGER | ✅ | 0 | 浏览次数 |
| `bookmark_count` | INTEGER | ✅ | 0 | 收藏次数 |
| `status` | VARCHAR(20) | ✅ | 'active' | 状态：active/archived/merged |
| `source_count` | INTEGER | ✅ | 0 | 来源数量 |

#### 热度分数计算逻辑

```python
def calculate_hot_score(event):
    """
    热度分数 = 基础分 + 时间衰减 + 来源加分 + 互动加分
    """
    base_score = event.source_count * 10  # 每个来源 10 分
    time_decay = 1 / (hours_since_created + 1)  # 时间衰减
    interaction = event.view_count * 0.1 + event.bookmark_count * 0.5
    return base_score * time_decay + interaction
```

---

### 3. event_sources - 事件 - 来源关联表

**用途**: 存储事件的各来源报道（一篇事件可以有多个来源）

#### 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | UUID | ✅ | uuid() | 主键 |
| `event_id` | UUID | ✅ | - | 关联事件 |
| `source_id` | UUID | ✅ | - | 关联信息源 |
| `article_url` | VARCHAR(1024) | ✅ | - | 原文链接 |
| `article_title` | VARCHAR(512) | ✅ | - | 文章标题 |
| `article_content` | TEXT | ❌ | NULL | 文章内容 |
| `article_summary` | TEXT | ❌ | NULL | 文章摘要 |
| `published_at` | TIMESTAMP | ❌ | NULL | 发布时间 |
| `fetched_at` | TIMESTAMP | ✅ | NOW() | 抓取时间 |
| `sentiment_score` | DECIMAL(3,2) | ❌ | NULL | 情感分数：-1 ~ 1 |
| `word_count` | INTEGER | ❌ | NULL | 字数 |

#### 唯一约束

```sql
UNIQUE(event_id, source_id)  -- 同一事件的同一来源只存一篇
```

---

### 4. ai_summaries - AI 摘要表

**用途**: 存储 AI 生成的多视角摘要（左/中/右三个视角）

#### 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | UUID | ✅ | uuid() | 主键 |
| `event_id` | UUID | ✅ | - | 关联事件（唯一） |
| `left_perspective` | TEXT | ✅ | - | 左倾视角摘要 |
| `center_perspective` | TEXT | ✅ | - | 中立视角摘要 |
| `right_perspective` | TEXT | ✅ | - | 右倾视角摘要 |
| `left_sources` | UUID[] | ❌ | NULL | 左倾视角来源 ID 数组 |
| `center_sources` | UUID[] | ❌ | NULL | 中立视角来源 ID 数组 |
| `right_sources` | UUID[] | ❌ | NULL | 右倾视角来源 ID 数组 |
| `model_name` | VARCHAR(100) | ❌ | NULL | AI 模型名称 |
| `prompt_version` | VARCHAR(20) | ❌ | NULL | 提示词版本 |
| `token_count` | INTEGER | ❌ | NULL | 消耗 token 数 |
| `quality_score` | DECIMAL(3,2) | ❌ | NULL | 质量评分 |
| `generated_at` | TIMESTAMP | ✅ | NOW() | 生成时间 |
| `expires_at` | TIMESTAMP | ❌ | NULL | 过期时间（缓存用） |

#### AI 摘要生成 Prompt 示例

```
你是一个专业的新闻分析师。请根据以下媒体报道，生成三个不同视角的摘要：

【左倾媒体】
{left_media_content}

【中立媒体】
{center_media_content}

【右倾媒体】
{right_media_content}

要求：
1. 每个视角 100-200 字
2. 客观陈述，不添加个人评价
3. 标注信息来源
4. 突出不同视角的关注点差异
```

---

### 5. users - 用户表

**用途**: 存储用户基本信息和认证信息

#### 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | UUID | ✅ | uuid() | 主键 |
| `email` | VARCHAR(255) | ❌ | NULL | 邮箱（唯一） |
| `phone` | VARCHAR(20) | ❌ | NULL | 手机号（唯一） |
| `password_hash` | VARCHAR(255) | ❌ | NULL | 密码哈希 |
| `provider` | VARCHAR(50) | ❌ | NULL | 第三方提供商 |
| `provider_id` | VARCHAR(255) | ❌ | NULL | 第三方 ID |
| `display_name` | VARCHAR(100) | ❌ | NULL | 显示名称 |
| `avatar_url` | VARCHAR(512) | ❌ | NULL | 头像 URL |
| `preferred_language` | VARCHAR(10) | ✅ | 'zh-CN' | 偏好语言 |
| `preferred_categories` | TEXT[] | ❌ | NULL | 偏好类别 |
| `is_active` | BOOLEAN | ✅ | true | 是否激活 |
| `is_verified` | BOOLEAN | ✅ | false | 是否验证 |
| `last_login_at` | TIMESTAMP | ❌ | NULL | 最后登录时间 |
| `created_at` | TIMESTAMP | ✅ | NOW() | 创建时间 |
| `updated_at` | TIMESTAMP | ✅ | NOW() | 更新时间 |

---

### 6. reading_history - 阅读历史表

**用途**: 记录用户阅读事件的历史

#### 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | UUID | ✅ | uuid() | 主键 |
| `user_id` | UUID | ✅ | - | 用户 ID |
| `event_id` | UUID | ✅ | - | 事件 ID |
| `read_at` | TIMESTAMP | ✅ | NOW() | 阅读时间 |
| `read_duration` | INTEGER | ❌ | NULL | 阅读时长（秒） |
| `device_type` | VARCHAR(20) | ❌ | NULL | 设备类型 |

#### 唯一约束

```sql
UNIQUE(user_id, event_id)  -- 同一用户同一事件只存一条
```

---

### 7. bookmarks - 收藏表

**用途**: 用户收藏的事件

#### 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | UUID | ✅ | uuid() | 主键 |
| `user_id` | UUID | ✅ | - | 用户 ID |
| `event_id` | UUID | ✅ | - | 事件 ID |
| `created_at` | TIMESTAMP | ✅ | NOW() | 收藏时间 |
| `notes` | TEXT | ❌ | NULL | 用户备注 |

#### 唯一约束

```sql
UNIQUE(user_id, event_id)  -- 同一用户同一事件只收藏一次
```

---

## 🔗 表关系图

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│   sources   │──────<│  event_sources  │>──────│    events   │
└─────────────┘       └─────────────────┘       └─────────────┘
                              │                        │
                              │                        │
                              ▼                        ▼
                        ┌───────────┐           ┌───────────┐
                        │ ai_summary│           │ bookmarks │
                        └───────────┘           └───────────┘
                                                      ▲
                                                      │
                        ┌───────────┐           ┌───────────┐
                        │   users   │>──────────│ reading_  │
                        └───────────┘           │ history   │
                                                └───────────┘
```

---

## 📈 性能优化

### 索引策略

| 表 | 索引字段 | 类型 | 用途 |
|------|----------|------|------|
| events | created_at | DESC | 按时间排序 |
| events | hot_score | DESC | 热榜查询 |
| events | category | BTREE | 分类筛选 |
| event_sources | event_id | BTREE | 关联查询 |
| reading_history | user_id, read_at | COMPOSITE | 用户历史 |

### 分区策略（未来扩展）

```sql
-- 当 reading_history 超过 1000 万行时考虑按月分区
CREATE TABLE reading_history_2026_03 PARTITION OF reading_history
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
```

---

## 🔒 安全考虑

### 敏感数据

| 表 | 敏感字段 | 加密方式 |
|------|----------|----------|
| users | password_hash | bcrypt |
| users | phone | 应用层加密（可选） |

### 权限控制

```sql
-- 创建只读用户（用于分析）
CREATE ROLE reader WITH LOGIN PASSWORD 'xxx';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO reader;

-- 创建应用用户（用于 API）
CREATE ROLE app_user WITH LOGIN PASSWORD 'xxx';
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
```

---

## 📊 查询示例

### 获取热榜事件（前 20）

```sql
SELECT e.*, COUNT(es.source_id) as source_count
FROM events e
LEFT JOIN event_sources es ON e.id = es.event_id
WHERE e.status = 'active'
GROUP BY e.id
ORDER BY e.hot_score DESC, e.created_at DESC
LIMIT 20;
```

### 获取事件的多视角摘要

```sql
SELECT 
    e.title,
    s.left_perspective,
    s.center_perspective,
    s.right_perspective
FROM events e
JOIN ai_summaries s ON e.id = s.event_id
WHERE e.id = 'xxx';
```

### 获取用户的阅读历史

```sql
SELECT e.title, e.category, rh.read_at, rh.read_duration
FROM reading_history rh
JOIN events e ON rh.event_id = e.id
WHERE rh.user_id = 'xxx'
ORDER BY rh.read_at DESC
LIMIT 50;
```

---

## 🔄 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v1.0 | 2026-03-04 | 初始版本 | Dev Bot |

---

**最后更新**: 2026-03-04  
**状态**: ✅ 已完成
