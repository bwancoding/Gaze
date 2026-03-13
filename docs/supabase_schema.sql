-- ============================================================
-- WRHITW Database Schema for Supabase PostgreSQL
-- 多视角新闻聚合平台
-- 
-- 数据库：PostgreSQL 15+ (Supabase)
-- 创建时间：2026-03-13
-- 版本：v2.0 (Supabase Migration)
-- ============================================================

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 核心表：信息源 (sources)
-- ============================================================

CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 基本信息
    name VARCHAR(255) NOT NULL,
    url VARCHAR(512) NOT NULL,
    logo_url VARCHAR(512),
    
    -- 立场标签
    bias_label VARCHAR(20) DEFAULT 'center',
    bias_score DECIMAL(3,2) CHECK (bias_score BETWEEN -1.0 AND 1.0),
    
    -- 地域信息
    country VARCHAR(2),
    language VARCHAR(10) DEFAULT 'en',
    
    -- 可信度评分
    credibility_score DECIMAL(3,2) CHECK (credibility_score BETWEEN 0 AND 1),
    
    -- 抓取配置
    rss_feed_url VARCHAR(512),
    api_endpoint VARCHAR(512),
    scrape_interval INTEGER DEFAULT 900,
    
    -- 状态
    is_active BOOLEAN DEFAULT true,
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sources_bias ON sources(bias_label);
CREATE INDEX idx_sources_country ON sources(country);
CREATE INDEX idx_sources_active ON sources(is_active);

COMMENT ON TABLE sources IS '信息源表：存储新闻媒体、通讯社等信息源';

-- ============================================================
-- 核心表：事件 (events)
-- ============================================================

CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 事件信息
    title VARCHAR(512) NOT NULL,
    summary TEXT,
    description TEXT,
    
    -- 分类
    category VARCHAR(50),
    tags TEXT[],
    
    -- 时间信息
    occurred_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    archived_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,
    
    -- 热度指标
    hot_score DECIMAL(5,2) DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    bookmark_count INTEGER DEFAULT 0,
    
    -- 状态
    status VARCHAR(20) DEFAULT 'active',
    source_count INTEGER DEFAULT 0
);

CREATE INDEX idx_events_category ON events(category);
CREATE INDEX idx_events_created ON events(created_at DESC);
CREATE INDEX idx_events_occurred ON events(occurred_at DESC);
CREATE INDEX idx_events_hot ON events(hot_score DESC);
CREATE INDEX idx_events_tags ON events USING GIN(tags);
CREATE INDEX idx_events_status ON events(status);

COMMENT ON TABLE events IS '事件表：存储新闻事件的核心信息';

-- ============================================================
-- 核心表：事件 - 来源关联 (event_sources)
-- ============================================================

CREATE TABLE event_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 关联
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    
    -- 文章信息
    article_url VARCHAR(1024) NOT NULL,
    article_title VARCHAR(512) NOT NULL,
    article_content TEXT,
    article_summary TEXT,
    
    -- 发布时间
    published_at TIMESTAMP WITH TIME ZONE,
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 分析数据
    sentiment_score DECIMAL(3,2),
    word_count INTEGER,
    
    -- 唯一性约束
    UNIQUE(event_id, source_id)
);

CREATE INDEX idx_event_sources_event ON event_sources(event_id);
CREATE INDEX idx_event_sources_source ON event_sources(source_id);
CREATE INDEX idx_event_sources_published ON event_sources(published_at);

COMMENT ON TABLE event_sources IS '事件 - 来源关联表：存储事件的各来源报道';

-- ============================================================
-- 核心表：AI 摘要 (ai_summaries)
-- ============================================================

CREATE TABLE ai_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 关联
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    
    -- 摘要内容
    left_perspective TEXT NOT NULL,
    center_perspective TEXT NOT NULL,
    right_perspective TEXT NOT NULL,
    
    -- 来源引用 (存储 UUID 数组的文本表示)
    left_sources TEXT,
    center_sources TEXT,
    right_sources TEXT,
    
    -- AI 元数据
    model_name VARCHAR(100),
    prompt_version VARCHAR(20),
    token_count INTEGER,
    
    -- 质量评估
    quality_score DECIMAL(3,2),
    
    -- 时间
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- 约束
    UNIQUE(event_id)
);

CREATE INDEX idx_ai_summaries_event ON ai_summaries(event_id);
CREATE INDEX idx_ai_summaries_generated ON ai_summaries(generated_at DESC);

COMMENT ON TABLE ai_summaries IS 'AI 摘要表：存储 AI 生成的多视角摘要';

-- ============================================================
-- 核心表：用户 (users)
-- ============================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 认证信息
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255),
    
    -- 第三方登录
    provider VARCHAR(50),
    provider_id VARCHAR(255),
    
    -- 个人信息
    display_name VARCHAR(100),
    avatar_url VARCHAR(512),
    
    -- 偏好设置
    preferred_language VARCHAR(10) DEFAULT 'zh-CN',
    preferred_categories TEXT[],
    
    -- 状态
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_provider ON users(provider, provider_id);

COMMENT ON TABLE users IS '用户表：存储用户基本信息';

-- ============================================================
-- 核心表：阅读历史 (reading_history)
-- ============================================================

CREATE TABLE reading_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 关联
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    
    -- 阅读信息
    read_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_duration INTEGER,
    device_type VARCHAR(20),
    
    -- 唯一性约束
    UNIQUE(user_id, event_id)
);

CREATE INDEX idx_reading_history_user ON reading_history(user_id);
CREATE INDEX idx_reading_history_event ON reading_history(event_id);
CREATE INDEX idx_reading_history_read_at ON reading_history(read_at DESC);

COMMENT ON TABLE reading_history IS '阅读历史表：记录用户阅读事件的历史';

-- ============================================================
-- 核心表：收藏 (bookmarks)
-- ============================================================

CREATE TABLE bookmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- 关联
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    
    -- 收藏信息
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    
    -- 唯一性约束
    UNIQUE(user_id, event_id)
);

CREATE INDEX idx_bookmarks_user ON bookmarks(user_id);
CREATE INDEX idx_bookmarks_event ON bookmarks(event_id);
CREATE INDEX idx_bookmarks_created ON bookmarks(created_at DESC);

COMMENT ON TABLE bookmarks IS '收藏表：用户收藏的事件';

-- ============================================================
-- 扩展表：利益相关者类型 (stakeholder_types)
-- ============================================================

CREATE TABLE stakeholder_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(100),
    verification_required BOOLEAN DEFAULT true,
    verification_method TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_stakeholder_types_category ON stakeholder_types(category);

COMMENT ON TABLE stakeholder_types IS '利益相关者类型表';

-- ============================================================
-- 扩展表：利益相关者 (stakeholders)
-- ============================================================

CREATE TABLE stakeholders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type_id UUID REFERENCES stakeholder_types(id),
    description TEXT,
    category VARCHAR(100),
    verification_required BOOLEAN DEFAULT true,
    verification_method TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_stakeholders_type ON stakeholders(type_id);
CREATE INDEX idx_stakeholders_category ON stakeholders(category);
CREATE INDEX idx_stakeholders_active ON stakeholders(is_active);

COMMENT ON TABLE stakeholders IS '利益相关者表';

-- ============================================================
-- 扩展表：事件 - 利益相关者关联 (event_stakeholders)
-- ============================================================

CREATE TABLE event_stakeholders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    stakeholder_id UUID NOT NULL REFERENCES stakeholders(id),
    relevance_score DECIMAL(3,2) DEFAULT 0.5,
    status VARCHAR(50) DEFAULT 'pending',
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(event_id, stakeholder_id)
);

CREATE INDEX idx_event_stakeholders_event ON event_stakeholders(event_id);
CREATE INDEX idx_event_stakeholders_stakeholder ON event_stakeholders(stakeholder_id);
CREATE INDEX idx_event_stakeholders_status ON event_stakeholders(status);

COMMENT ON TABLE event_stakeholders IS '事件 - 利益相关者关联表';

-- ============================================================
-- 扩展表：利益相关者验证 (stakeholder_verifications)
-- ============================================================

CREATE TABLE stakeholder_verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stakeholder_id UUID NOT NULL REFERENCES stakeholders(id),
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    application_text TEXT,
    proof_type VARCHAR(50),
    proof_data TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_stakeholder_verifications_user ON stakeholder_verifications(user_id);
CREATE INDEX idx_stakeholder_verifications_stakeholder ON stakeholder_verifications(stakeholder_id);
CREATE INDEX idx_stakeholder_verifications_status ON stakeholder_verifications(status);

COMMENT ON TABLE stakeholder_verifications IS '利益相关者验证申请表';

-- ============================================================
-- 扩展表：用户 - 利益相关者角色 (user_stakeholder_roles)
-- ============================================================

CREATE TABLE user_stakeholder_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stakeholder_id UUID NOT NULL REFERENCES stakeholders(id),
    is_verified BOOLEAN DEFAULT false,
    verified_at TIMESTAMP WITH TIME ZONE,
    display_name VARCHAR(255),
    badge_color VARCHAR(20) DEFAULT 'blue',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, stakeholder_id)
);

CREATE INDEX idx_user_stakeholder_roles_user ON user_stakeholder_roles(user_id);
CREATE INDEX idx_user_stakeholder_roles_stakeholder ON user_stakeholder_roles(stakeholder_id);

COMMENT ON TABLE user_stakeholder_roles IS '用户 - 利益相关者角色关联表';

-- ============================================================
-- 扩展表：用户角色 (user_personas)
-- ============================================================

CREATE TABLE user_personas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    persona_name VARCHAR(255) NOT NULL,
    avatar_color VARCHAR(20) DEFAULT 'blue',
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_user_personas_user ON user_personas(user_id);
CREATE INDEX idx_user_personas_deleted ON user_personas(is_deleted, deleted_at);

COMMENT ON TABLE user_personas IS '用户角色表';

-- ============================================================
-- 扩展表：事件 - 利益相关者验证 (event_stakeholder_verifications)
-- ============================================================

CREATE TABLE event_stakeholder_verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_persona_id UUID NOT NULL REFERENCES user_personas(id) ON DELETE CASCADE,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    stakeholder_id UUID NOT NULL REFERENCES stakeholders(id),
    application_text TEXT,
    proof_type VARCHAR(50),
    proof_data TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_persona_id, event_id)
);

CREATE INDEX idx_event_stakeholder_verifications_persona ON event_stakeholder_verifications(user_persona_id);
CREATE INDEX idx_event_stakeholder_verifications_event ON event_stakeholder_verifications(event_id);
CREATE INDEX idx_event_stakeholder_verifications_status ON event_stakeholder_verifications(status);

COMMENT ON TABLE event_stakeholder_verifications IS '事件 - 利益相关者验证申请表';

-- ============================================================
-- 扩展表：评论 (comments)
-- ============================================================

CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_persona_id UUID REFERENCES user_personas(id) ON DELETE SET NULL,
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_deleted BOOLEAN DEFAULT false,
    is_edited BOOLEAN DEFAULT false,
    like_count INTEGER DEFAULT 0,
    dislike_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_comments_event ON comments(event_id);
CREATE INDEX idx_comments_user ON comments(user_id);
CREATE INDEX idx_comments_parent ON comments(parent_id);
CREATE INDEX idx_comments_created ON comments(created_at DESC);

COMMENT ON TABLE comments IS '评论表';

-- ============================================================
-- 扩展表：评论投票 (comment_votes)
-- ============================================================

CREATE TABLE comment_votes (
    comment_id UUID NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vote_type VARCHAR(10) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (comment_id, user_id)
);

CREATE INDEX idx_comment_votes_user ON comment_votes(user_id);

COMMENT ON TABLE comment_votes IS '评论投票表';

-- ============================================================
-- 更新时间触发器函数
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

CREATE TRIGGER update_stakeholders_updated_at
    BEFORE UPDATE ON stakeholders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stakeholder_types_updated_at
    BEFORE UPDATE ON stakeholder_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_event_stakeholders_updated_at
    BEFORE UPDATE ON event_stakeholders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stakeholder_verifications_updated_at
    BEFORE UPDATE ON stakeholder_verifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_personas_updated_at
    BEFORE UPDATE ON user_personas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_event_stakeholder_verifications_updated_at
    BEFORE UPDATE ON event_stakeholder_verifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comments_updated_at
    BEFORE UPDATE ON comments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- Schema 版本
-- ============================================================

CREATE TABLE schema_version (
    version VARCHAR(20) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT
);

INSERT INTO schema_version (version, description) VALUES 
('2.0', 'Supabase PostgreSQL migration - Full schema with stakeholder support');

-- ============================================================
-- 初始数据：默认信息源
-- ============================================================

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
-- 结束
-- ============================================================
