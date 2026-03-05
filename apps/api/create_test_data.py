#!/usr/bin/env python3
"""
WRHITW 测试数据生成脚本
添加一些示例事件到数据库
"""

import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"

# 测试事件数据
test_events = [
    {
        "title": "全球气候峰会达成新协议，各国承诺减少碳排放",
        "summary": "为期两周的气候峰会在迪拜落幕，近 200 个国家同意逐步减少化石燃料使用，这是历史上首次明确提及化石燃料的协议。",
        "category": "环境",
        "tags": ["气候", "环境", "国际"],
    },
    {
        "title": "美联储宣布维持利率不变，通胀压力仍存",
        "summary": "美联储联邦公开市场委员会决定将基准利率维持在 5.25%-5.50% 区间，表示将继续密切关注经济数据。",
        "category": "财经",
        "tags": ["美联储", "利率", "经济"],
    },
    {
        "title": "人工智能监管法案在欧盟议会获得通过",
        "summary": "欧盟议会以压倒性多数通过《人工智能法案》，将对高风险 AI 系统实施严格监管，科技公司面临新的合规要求。",
        "category": "科技",
        "tags": ["AI", "监管", "欧盟"],
    },
    {
        "title": "某国大选结果揭晓，反对党获胜",
        "summary": "经过计票，反对党候选人以微弱优势获胜，现任总理承认败选。分析人士称这标志着该国政治格局的重大变化。",
        "category": "政治",
        "tags": ["大选", "政治", "国际"],
    },
    {
        "title": "新型量子计算机突破，计算速度提升 1000 倍",
        "summary": "研究团队宣布在量子纠错方面取得重大进展，新型量子计算机在特定任务上的计算速度比传统超级计算机快 1000 倍。",
        "category": "科技",
        "tags": ["量子计算", "科技", "突破"],
    },
    {
        "title": "国际空间站迎来新任务，多国宇航员入驻",
        "summary": "来自 5 个国家的 6 名宇航员成功抵达国际空间站，将开展为期 6 个月的科学实验和技术测试。",
        "category": "科技",
        "tags": ["航天", "国际空间站", "科学"],
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
