#!/usr/bin/env python3
"""
WRHITW RSS 新闻抓取器
从免费 RSS 源获取真实新闻
"""

import feedparser
import sqlite3
import uuid
import json
import ssl
from datetime import datetime, timedelta
import sys
import os
import urllib3

# 禁用 SSL 警告（开发环境）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 切换到 API 目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# RSS 源列表
RSS_FEEDS = [
    {
        "name": "BBC World",
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "政治",
        "language": "en",
        "bias_label": "center",
    },
    {
        "name": "Reuters Top News",
        "url": "https://feeds.reuters.com/reuters/topNews",
        "category": "政治",
        "language": "en",
        "bias_label": "center",
    },
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "category": "科技",
        "language": "en",
        "bias_label": "left",
    },
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "category": "科技",
        "language": "en",
        "bias_label": "left",
    },
]

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect('wrhitw.db')
    cursor = conn.cursor()
    
    # 确保 sources 表存在
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            bias_label TEXT DEFAULT 'center',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 确保 events 表存在
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            summary TEXT,
            category TEXT,
            tags TEXT,
            occurred_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hot_score REAL DEFAULT 0,
            view_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            source_count INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    return conn

def fetch_rss_feed(feed_info, limit=10):
    """抓取单个 RSS 源"""
    print(f"📡 抓取 {feed_info['name']} ({feed_info['url']})...")
    
    try:
        # 使用 requests 获取内容（更好地处理 SSL）
        import requests
        response = requests.get(
            feed_info['url'],
            timeout=10,
            verify=False  # 跳过 SSL 验证（开发环境）
        )
        feed = feedparser.parse(response.content)
        
        if feed.bozo:
            print(f"  ⚠️  RSS 解析警告：{feed.bozo_exception}")
            return []
        
        entries = []
        for entry in feed.entries[:limit]:
            # 提取数据
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])
            
            # 提取摘要（清理 HTML）
            summary = ""
            if hasattr(entry, 'summary'):
                # 简单清理 HTML 标签
                summary = entry.summary[:500].strip()
            
            entry_data = {
                "id": str(uuid.uuid4()),
                "title": entry.title,
                "summary": summary[:300] if summary else entry.title,
                "category": feed_info['category'],
                "url": entry.link,
                "published": published,
                "source_name": feed_info['name'],
                "bias_label": feed_info['bias_label'],
            }
            entries.append(entry_data)
        
        print(f"  ✅ 获取 {len(entries)} 条新闻")
        return entries
        
    except Exception as e:
        print(f"  ❌ 抓取失败：{e}")
        return []

def save_to_database(conn, entries):
    """保存新闻到数据库"""
    cursor = conn.cursor()
    
    saved_count = 0
    for entry in entries:
        try:
            # 检查是否已存在（通过标题去重）
            cursor.execute(
                "SELECT id FROM events WHERE title = ?",
                (entry['title'],)
            )
            if cursor.fetchone():
                continue
            
            # 插入事件
            cursor.execute('''
                INSERT INTO events (
                    id, title, summary, category, tags, 
                    occurred_at, status, source_count, hot_score
                ) VALUES (?, ?, ?, ?, ?, ?, 'active', 1, 75.0)
            ''', (
                entry['id'],
                entry['title'],
                entry['summary'],
                entry['category'],
                json.dumps([entry['source_name']]),
                entry['published'] or datetime.now(),
            ))
            
            saved_count += 1
            
        except Exception as e:
            print(f"  ⚠️ 保存失败：{entry['title'][:50]}... - {e}")
    
    conn.commit()
    return saved_count

def main():
    print("=" * 60)
    print("📰 WRHITW RSS 新闻抓取器")
    print("=" * 60)
    print()
    
    # 初始化数据库
    print("📊 初始化数据库...")
    conn = init_database()
    print("✅ 数据库就绪")
    print()
    
    # 抓取所有 RSS 源
    all_entries = []
    for feed_info in RSS_FEEDS:
        entries = fetch_rss_feed(feed_info, limit=5)
        all_entries.extend(entries)
    
    print()
    print(f"📦 共获取 {len(all_entries)} 条新闻")
    print()
    
    # 保存到数据库
    print("💾 保存到数据库...")
    saved = save_to_database(conn, all_entries)
    print(f"✅ 成功保存 {saved} 条新闻（已去重）")
    
    # 统计
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    total = cursor.fetchone()[0]
    print(f"📊 数据库共有 {total} 个事件")
    
    conn.close()
    
    print()
    print("=" * 60)
    print("🎉 抓取完成！")
    print()
    print("下一步:")
    print("  1. 刷新前端：http://localhost:3000")
    print("  2. 查看 API: http://localhost:8080/api/events")
    print("=" * 60)

if __name__ == "__main__":
    # 检查依赖
    try:
        import feedparser
    except ImportError:
        print("❌ 缺少依赖：feedparser")
        print("安装：pip install feedparser")
        sys.exit(1)
    
    main()
