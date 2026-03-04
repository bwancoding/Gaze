-- ============================================================
-- WRHITW Database Schema
-- 多视角新闻聚合平台
-- 
-- 数据库：PostgreSQL 15+
-- 创建时间：2026-03-04
-- 版本：v1.0
-- ============================================================

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. 信息源表 (sources)
-- 存储新闻媒体、通讯社等信息源
-- ============================================================

CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 基本信息
    name VARCHAR(255) NOT NULL,              -- 媒体名称（如：Reuters, BBC）
    url VARCHAR(512) NOT NULL,               -- 官方网站
    logo_url VARCHAR(512),                   -- Logo URL
    
    -- 立场标签
    bias_label VARCHAR(20) DEFAULT 'center', -- left/center/right
    bias_score DECIMAL(3,2) CHECK (bias_score BETWEEN -1.0 AND 1.0), -- -1(极左) 到 1(极右)
    
    -- 地域信息
    country VARCHAR(2),                      -- ISO 3166-1 alpha-2 国家代码
    language VARCHAR(10) DEFAULT 'en',       -- 语言代码
    
    -- 可信度评分
    credibility_score DECIMAL(3,2) CHECK (credibility_score BETWEEN 0 AND 1),
    
    -- 抓取配置
    rss_feed_url VARCHAR(512),               -- RSS 订阅地址
    api_endpoint VARCHAR(512),               -- API 地址（如果有）
    scrape_interval INTEGER DEFAULT 900,     -- 抓取间隔（秒），默认 15 分钟
    
    -- 状态
    is_active BOOLEAN DEFAULT true,          -- 是否启用
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_sources_bias ON sources(bias_label);
CREATE INDEX idx_sources_country ON sources(country);
CREATE INDEX idx_sources_active ON sources(is_active);

-- 注释
COMMENT ON TABLE sources IS '信息源表：存储新闻媒体、通讯社等信息源';
COMMENT ON COLUMN sources.bias_label IS '媒体立场标签：left(左倾), center(中立), right(右倾)';
COMMENT ON COLUMN sources.bias_score IS '立场分数：-1(极左) 到 1(极右), 0 为中立';
COMMENT ON COLUMN sources.credibility_score IS '可信度评分：0(最低) 到 1(最高)';

-- ============================================================
-- 2. 事件表 (events)
-- 存储新闻事件的核心信息
-- ============================================================

CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 事件信息
    title VARCHAR(512) NOT NULL,             -- 事件标题（中性表述）
    summary TEXT,                            -- 事件摘要
    description TEXT,                        -- 详细描述
    
    -- 分类
    category VARCHAR(50),                    -- 类别：politics, economy, technology, society, etc.
    tags TEXT[],                             -- 标签数组
    
    -- 时间信息
    occurred_at TIMESTAMP WITH TIME ZONE,    -- 事件发生时间
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 热度指标
    hot_score DECIMAL(5,2) DEFAULT 0,        -- 热度分数
    view_count INTEGER DEFAULT 0,            -- 浏览次数
    bookmark_count INTEGER DEFAULT 0,        -- 收藏次数
    
    -- 状态
    status VARCHAR(20) DEFAULT 'active',     -- active, archived, merged
    
    -- 来源数量
    source_count INTEGER DEFAULT 0           -- 关联的信息源数量
);

-- 索引
CREATE INDEX idx_events_category ON events(category);
CREATE INDEX idx_events_created ON events(created_at DESC);
CREATE INDEX idx_events_occurred ON events(occurred_at DESC);
CREATE INDEX idx_events_hot ON events(hot_score DESC);
CREATE INDEX idx_events_tags ON events USING GIN(tags);
CREATE INDEX idx_events_status ON events(status);

-- 注释
COMMENT ON TABLE events IS '事件表：存储新闻事件的核心信息';
COMMENT ON COLUMN events.bias_label IS '事件本身无立场，但聚合了不同立场的报道';
COMMENT ON COLUMN events.hot_score IS '热度分数：根据浏览量、来源数、时间衰减计算';

-- ============================================================
-- 3. 事件 - 来源关联表 (event_sources)
-- 存储事件的各来源报道
-- ============================================================

CREATE TABLE event_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 关联
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    
    -- 文章信息
    article_url VARCHAR(1024) NOT NULL,      -- 原文链接
    article_title VARCHAR(512) NOT NULL,     -- 文章标题
    article_content TEXT,                    -- 文章内容（抓取后存储）
    article_summary TEXT,                    -- 文章摘要
    
    -- 发布时间
    published_at TIMESTAMP WITH TIME ZONE,   -- 文章发布时间
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- 抓取时间
    
    -- 分析数据
    sentiment_score DECIMAL(3,2),            -- 情感分数：-1(负面) 到 1(正面)
    word_count INTEGER,                      -- 字数
    
    -- 唯一性约束（同一事件的同一来源只存一篇）
    UNIQUE(event_id, source_id)
);

-- 索引
CREATE INDEX idx_event_sources_event ON event_sources(event_id);
CREATE INDEX idx_event_sources_source ON event_sources(source_id);
CREATE INDEX idx_event_sources_published ON event_sources(published_at);

-- 注释
COMMENT ON TABLE event_sources IS '事件 - 来源关联表：存储事件的各来源报道';
COMMENT ON COLUMN event_sources.sentiment_score IS '情感分数：分析文章的情感倾向';

-- ============================================================
-- 4. AI 摘要表 (ai_summaries)
-- 存储 AI 生成的多视角摘要
-- ============================================================

CREATE TABLE ai_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 关联
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    
    -- 摘要内容
    left_perspective TEXT NOT NULL,          -- 左倾视角摘要
    center_perspective TEXT NOT NULL,        -- 中立视角摘要
    right_perspective TEXT NOT NULL,         -- 右倾视角摘要
    
    -- 来源引用
    left_sources UUID[] REFERENCES sources(id),    -- 左倾视角来源
    center_sources UUID[] REFERENCES sources(id),  -- 中立视角来源
    right_sources UUID[] REFERENCES sources(id),   -- 右倾视角来源
    
    -- AI 元数据
    model_name VARCHAR(100),                 -- 使用的 AI 模型
    prompt_version VARCHAR(20),              -- 提示词版本
    token_count INTEGER,                     -- 消耗的 token 数
    
    -- 质量评估
    quality_score DECIMAL(3,2),              -- 质量评分 (人工或自动评估)
    
    -- 时间
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,     -- 过期时间（用于缓存）
    
    -- 约束（一个事件只存一个摘要）
    UNIQUE(event_id)
);

-- 索引
CREATE INDEX idx_ai_summaries_event ON ai_summaries(event_id);
CREATE INDEX idx_ai_summaries_generated ON ai_summaries(generated_at DESC);

-- 注释
COMMENT ON TABLE ai_summaries IS 'AI 摘要表：存储 AI 生成的多视角摘要';
COMMENT ON COLUMN ai_summaries.left_perspective IS '从左倾媒体报道中生成的摘要';
COMMENT ON COLUMN ai_summaries.center_perspective IS '从中立媒体报道中生成的摘要';
COMMENT ON COLUMN ai_summaries.right_perspective IS '从右倾媒体报道中生成的摘要';

-- ============================================================
-- 5. 用户表 (users)
-- 存储用户基本信息
-- ============================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 认证信息
    email VARCHAR(255) UNIQUE,               -- 邮箱（可选，如果用手机登录）
    phone VARCHAR(20) UNIQUE,                -- 手机号（可选）
    password_hash VARCHAR(255),              -- 密码哈希
    
    -- 第三方登录
    provider VARCHAR(50),                    -- 登录提供商：github, google, etc.
    provider_id VARCHAR(255),                -- 第三方 ID
    
    -- 个人信息
    display_name VARCHAR(100),               -- 显示名称
    avatar_url VARCHAR(512),                 -- 头像 URL
    
    -- 偏好设置
    preferred_language VARCHAR(10) DEFAULT 'zh-CN',
    preferred_categories TEXT[],             -- 偏好的类别
    
    -- 状态
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_provider ON users(provider, provider_id);

-- 注释
COMMENT ON TABLE users IS '用户表：存储用户基本信息';

-- ============================================================
-- 6. 阅读历史表 (reading_history)
-- 记录用户阅读事件的历史
-- ============================================================

CREATE TABLE reading_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 关联
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    
    -- 阅读信息
    read_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_duration INTEGER,                   -- 阅读时长（秒）
    device_type VARCHAR(20),                 -- 设备类型：mobile, desktop, tablet
    
    -- 唯一性约束（同一用户同一事件只存一条）
    UNIQUE(user_id, event_id)
);

-- 索引
CREATE INDEX idx_reading_history_user ON reading_history(user_id);
CREATE INDEX idx_reading_history_event ON reading_history(event_id);
CREATE INDEX idx_reading_history_read_at ON reading_history(read_at DESC);

-- 注释
COMMENT ON TABLE reading_history IS '阅读历史表：记录用户阅读事件的历史';

-- ============================================================
-- 7. 收藏表 (bookmarks)
-- 用户收藏的事件
-- ============================================================

CREATE TABLE bookmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 关联
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    
    -- 收藏信息
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,                              -- 用户备注
    
    -- 唯一性约束
    UNIQUE(user_id, event_id)
);

-- 索引
CREATE INDEX idx_bookmarks_user ON bookmarks(user_id);
CREATE INDEX idx_bookmarks_event ON bookmarks(event_id);
CREATE INDEX idx_bookmarks_created ON bookmarks(created_at DESC);

-- 注释
COMMENT ON TABLE bookmarks IS '收藏表：用户收藏的事件';

-- ============================================================
-- 8. 更新时间触发器函数
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为需要自动更新 updated_at 的表添加触发器
CREATE TRIGGER update_sources_updated_at
    BEFORE UPDATE ON sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 9. 初始数据插入
-- ============================================================

-- 插入默认信息源（示例）
INSERT INTO sources (name, url, bias_label, bias_score, country, language, credibility_score) VALUES
('Reuters', 'https://www.reuters.com', 'center', 0.0, 'GB', 'en', 0.95),
('Associated Press', 'https://apnews.com', 'center', 0.0, 'US', 'en', 0.94),
('BBC News', 'https://www.bbc.com/news', 'center', -0.1, 'GB', 'en', 0.90),
('The Guardian', 'https://www.theguardian.com', 'left', -0.4, 'GB', 'en', 0.85),
('The New York Times', 'https://www.nytimes.com', 'left', -0.3, 'US', 'en', 0.88),
('The Wall Street Journal', 'https://www.wsj.com', 'right', 0.3, 'US', 'en', 0.87),
('Fox News', 'https://www.foxnews.com', 'right', 0.6, 'US', 'en', 0.75),
('新华社', 'https://www.xinhuanet.com', 'left', -0.2, 'CN', 'zh', 0.80),
('央视新闻', 'https://news.cctv.com', 'left', -0.3, 'CN', 'zh', 0.78),
('联合早报', 'https://www.zaobao.com', 'center', 0.0, 'SG', 'zh', 0.85);

-- ============================================================
-- 10. 视图（Views）
-- ============================================================

-- 事件热度视图（包含来源数量）
CREATE VIEW events_with_stats AS
SELECT 
    e.*,
    COUNT(DISTINCT es.source_id) as actual_source_count,
    COUNT(DISTINCT rh.user_id) as unique_readers
FROM events e
LEFT JOIN event_sources es ON e.id = es.event_id
LEFT JOIN reading_history rh ON e.id = rh.event_id
GROUP BY e.id;

-- 信息源统计视图
CREATE VIEW sources_with_stats AS
SELECT 
    s.*,
    COUNT(DISTINCT es.event_id) as total_events,
    COUNT(DISTINCT es.event_id) FILTER (WHERE es.published_at > NOW() - INTERVAL '24 hours') as events_24h
FROM sources s
LEFT JOIN event_sources es ON s.id = es.source_id
GROUP BY s.id;

-- ============================================================
-- Schema 版本
-- ============================================================

CREATE TABLE schema_version (
    version VARCHAR(20) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT
);

INSERT INTO schema_version (version, description) VALUES 
('1.0', 'Initial schema - Core tables for WRHITW MVP');

-- ============================================================
-- 结束
-- ============================================================
