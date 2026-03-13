-- WRHITW Trending MVP - 初始数据库迁移
-- 创建时间：2026-03-13
-- 描述：创建基础表结构和索引

-- 启用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 数据源表
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(500) NOT NULL UNIQUE,
    stance VARCHAR(20) NOT NULL,
    region VARCHAR(50) NOT NULL,
    priority VARCHAR(10) DEFAULT 'P2',
    update_interval_minutes INTEGER DEFAULT 60,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 事件表
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    keywords JSONB,
    heat_score FLOAT DEFAULT 0.0,
    article_count INTEGER DEFAULT 0,
    media_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 事件表索引
CREATE INDEX idx_event_heat_created ON events(heat_score, created_at);
CREATE INDEX idx_event_created ON events(created_at);

-- 文章表
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id) ON DELETE SET NULL,
    source_id INTEGER REFERENCES sources(id),
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content TEXT,
    url VARCHAR(1000) NOT NULL UNIQUE,
    published_at TIMESTAMP NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    heat_score FLOAT DEFAULT 0.0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    is_processed BOOLEAN DEFAULT FALSE,
    source_priority VARCHAR(10) DEFAULT 'P2'
);

-- 文章表索引
CREATE INDEX idx_article_event ON articles(event_id);
CREATE INDEX idx_article_published_source ON articles(published_at, source_id);
CREATE INDEX idx_article_heat ON articles(heat_score, published_at);
CREATE INDEX idx_article_url ON articles(url);

-- 初始化数据源（15 家媒体）
INSERT INTO sources (name, url, stance, region, priority, update_interval_minutes) VALUES
-- P0 优先级
('Reuters', 'https://www.reutersagency.com/feed/', 'center', 'international', 'P0', 15),
('Associated Press', 'https://apnews.com/apf-topnews', 'center', 'international', 'P0', 15),
('BBC News', 'https://feeds.bbci.co.uk/news/rss.xml', 'center-left', 'uk', 'P0', 15),
('The Guardian', 'https://www.theguardian.com/uk/rss', 'left', 'uk', 'P0', 15),
('Financial Times', 'https://www.ft.com/?format=rss', 'center', 'uk', 'P0', 30),
('Bloomberg', 'https://www.bloomberg.com/feed/podcast/businessweek.xml', 'center', 'us', 'P0', 30),
-- P1 优先级
('CNN', 'http://rss.cnn.com/rss/edition.rss', 'left', 'us', 'P1', 15),
('Fox News', 'https://moxie.foxnews.com/google-publisher/top_stories.xml', 'right', 'us', 'P1', 15),
('The New York Times', 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml', 'left', 'us', 'P1', 30),
('The Wall Street Journal', 'https://feeds.a.dj.com/rss/RSSOpinion.xml', 'right', 'us', 'P1', 30),
('The Economist', 'https://www.economist.com/the-world-this-week/rss.xml', 'center-right', 'uk', 'P1', 60),
('Al Jazeera', 'https://www.aljazeera.com/xml/rss/all.xml', 'center', 'international', 'P1', 30),
-- P2 优先级
('Politico', 'https://www.politico.com/rss/politics08.xml', 'center-left', 'us', 'P2', 30),
('The Hill', 'https://thehill.com/feed/', 'center', 'us', 'P2', 30),
('NPR', 'https://feeds.npr.org/1001/rss.xml', 'left', 'us', 'P2', 60);

-- 输出统计信息
SELECT 
    priority,
    COUNT(*) as count,
    array_agg(name) as sources
FROM sources
GROUP BY priority
ORDER BY priority;
