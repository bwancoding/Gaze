#!/usr/bin/env python3
"""
WRHITW Test Data Generation Script
Add sample events to the database
"""

import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"

# Test event data
test_events = [
    {
        "title": "Global Climate Summit Reaches New Agreement, Countries Pledge to Reduce Carbon Emissions",
        "summary": "The two-week climate summit concluded in Dubai, with nearly 200 countries agreeing to gradually reduce fossil fuel use, marking the first agreement to explicitly mention fossil fuels.",
        "category": "Environment",
        "tags": ["climate", "environment", "international"],
    },
    {
        "title": "Federal Reserve Announces Unchanged Interest Rates, Inflation Pressure Persists",
        "summary": "The Federal Reserve's FOMC decided to maintain the benchmark interest rate at 5.25%-5.50%, indicating continued close monitoring of economic data.",
        "category": "Economy",
        "tags": ["Federal Reserve", "interest rates", "economy"],
    },
    {
        "title": "AI Regulation Act Passed by EU Parliament",
        "summary": "The EU Parliament overwhelmingly passed the AI Act, imposing strict regulations on high-risk AI systems, with tech companies facing new compliance requirements.",
        "category": "Technology",
        "tags": ["AI", "regulation", "EU"],
    },
    {
        "title": "National Election Results Revealed, Opposition Party Wins",
        "summary": "After vote counting, the opposition candidate won by a narrow margin, with the incumbent PM conceding defeat. Analysts say this marks a major shift in the country's political landscape.",
        "category": "Politics",
        "tags": ["election", "politics", "international"],
    },
    {
        "title": "Quantum Computing Breakthrough, Speed Increased 1000x",
        "summary": "A research team announced a major breakthrough in quantum error correction. The new quantum computer performs certain tasks 1000 times faster than traditional supercomputers.",
        "category": "Technology",
        "tags": ["quantum computing", "technology", "breakthrough"],
    },
    {
        "title": "International Space Station Welcomes New Mission, Multinational Astronauts Arrive",
        "summary": "Six astronauts from five countries successfully arrived at the ISS, where they will conduct six months of scientific experiments and technology tests.",
        "category": "Technology",
        "tags": ["space", "ISS", "science"],
    },
]

def create_event(event_data):
    """创建单个事件"""
    url = f"{API_BASE}/api/events"
    
    try:
        response = requests.post(url, json=event_data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 创建成功：{data.get('title', 'Unknown')}")
            return True
        else:
            print(f"❌ 创建失败 ({response.status_code}): {event_data['title']}")
            print(f"   响应：{response.text[:200]}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 API 服务器：{API_BASE}")
        print(f"   请确保后端服务正在运行：uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def main():
    print("🚀 WRHITW 测试数据生成")
    print("=" * 50)
    print(f"API 地址：{API_BASE}")
    print(f"事件数量：{len(test_events)}")
    print("=" * 50)
    print()
    
    # 检查 API 是否可用
    try:
        response = requests.get(f"{API_BASE}/health", timeout=3)
        if response.status_code == 200:
            print("✅ 后端服务正常")
        else:
            print(f"⚠️  后端服务响应异常：{response.status_code}")
    except:
        print("❌ 无法连接到后端服务")
        print()
        print("请先启动后端服务:")
        print("  cd /Users/bwan/.openclaw/workspace/wrhitw/apps/api")
        print("  ./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    print()
    print("开始创建事件...")
    print()
    
    success_count = 0
    for event in test_events:
        if create_event(event):
            success_count += 1
    
    print()
    print("=" * 50)
    print(f"✅ 完成：成功 {success_count}/{len(test_events)} 个事件")
    print()
    print("下一步:")
    print("  1. 刷新前端页面：http://localhost:3000")
    print("  2. 查看 API 文档：http://localhost:8000/docs")
    print("=" * 50)

if __name__ == "__main__":
    main()
