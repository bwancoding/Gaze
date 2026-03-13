"""
热度算法与事件聚类综合使用示例

演示如何使用热度计算和事件聚类服务
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.article import Article
from app.models.event import Event
from app.services import (
    HeatCalculator,
    calculate_all_heat_scores,
    EventClusterer,
    cluster_new_articles,
)


def demo_heat_calculation():
    """演示热度计算"""
    print("="*80)
    print("🔥 热度计算演示")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        calculator = HeatCalculator(db)
        
        # 1. 更新所有热度分数
        print("\n1️⃣  更新所有热度分数...")
        result = calculate_all_heat_scores(db)
        
        print(f"  ✅ 更新文章：{result['articles_updated']} 篇")
        print(f"  ✅ 更新事件：{result['events_updated']} 个")
        
        # 2. 获取 Top20 热门事件
        print("\n2️⃣  获取 Top20 热门事件...")
        top_events = calculator.get_top_events(limit=20)
        
        print(f"  共 {len(top_events)} 个热门事件:")
        for i, event in enumerate(top_events[:5], 1):
            print(f"    {i}. {event.title[:50]} (热度：{event.heat_score:.2f})")
        
        if len(top_events) > 5:
            print(f"    ... 还有 {len(top_events) - 5} 个")
        
        # 3. 获取 Trending 事件（增长最快）
        print("\n3️⃣  获取 Trending 事件...")
        trending = calculator.get_trending_events(limit=10, time_window_hours=24)
        
        if trending:
            print(f"  共 {len(trending)} 个 trending 事件:")
            for i, (event, growth) in enumerate(trending[:3], 1):
                print(f"    {i}. {event.title[:45]} (增长率：{growth:.2f}x)")
        else:
            print("  暂无 trending 数据")
        
        # 4. 获取热度分布
        print("\n4️⃣  热度分布统计...")
        distribution = calculator.calculate_heat_distribution()
        
        print("  文章:")
        print(f"    总数：{distribution['articles']['count']}")
        print(f"    平均热度：{distribution['articles']['avg']:.2f}")
        print(f"    最高热度：{distribution['articles']['max']:.2f}")
        
        print("  事件:")
        print(f"    总数：{distribution['events']['count']}")
        print(f"    平均热度：{distribution['events']['avg']:.2f}")
        print(f"    最高热度：{distribution['events']['max']:.2f}")
        
    finally:
        db.close()
    
    print("\n✅ 热度计算演示完成")


def demo_event_clustering():
    """演示事件聚类"""
    print("\n" + "="*80)
    print("📚 事件聚类演示")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        clusterer = EventClusterer(db)
        
        # 1. 获取未处理的文章
        print("\n1️⃣  获取未处理的文章...")
        unprocessed = db.query(Article).filter(
            Article.is_processed == False,
            Article.event_id.is_(None)
        ).all()
        
        print(f"  找到 {len(unprocessed)} 篇未处理文章")
        
        if unprocessed:
            # 2. 为每篇文章检测是否属于新事件
            print("\n2️⃣  检测新事件...")
            new_event_articles = []
            clustered_count = 0
            
            for article in unprocessed[:10]:  # 演示前 10 篇
                is_new, matched_event, similarity = clusterer.detect_new_event(article)
                
                if is_new:
                    new_event_articles.append(article)
                    print(f"  新事件：{article.title[:40]}")
                else:
                    clustered_count += 1
                    print(f"  聚类到：{matched_event.title[:40]} (相似度：{similarity:.3f})")
            
            # 3. 创建新事件
            if new_event_articles:
                print(f"\n3️⃣  创建 {len(new_event_articles)} 个新事件...")
                for article in new_event_articles:
                    event = clusterer.create_event_from_articles([article])
                    print(f"  ✅ 创建事件：{event.title[:40]}")
            
            # 4. 检测重复事件
            print("\n4️⃣  检测重复事件...")
            duplicates = clusterer.find_duplicate_events(time_window_days=3)
            
            if duplicates:
                print(f"  发现 {len(duplicates)} 对重复事件:")
                for e1, e2, sim in duplicates[:3]:
                    print(f"    - {e1.title[:35]} & {e2.title[:35]} (相似度：{sim:.3f})")
            else:
                print("  未发现重复事件")
        
        # 5. 增量更新示例
        print("\n5️⃣  增量更新演示...")
        result = cluster_new_articles(db)
        
        print(f"  聚类文章：{result['clustered_count']}")
        print(f"  新事件：{result['new_events_count']}")
        print(f"  合并事件：{result['merged_events_count']}")
        
    finally:
        db.close()
    
    print("\n✅ 事件聚类演示完成")


def demo_complete_workflow():
    """演示完整工作流"""
    print("\n" + "="*80)
    print("🚀 完整工作流演示")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        print("\n完整流程:")
        print("  1. 抓取新文章（RSS/Reddit/HN）")
        print("  2. 事件去重聚类")
        print("  3. 计算热度分数")
        print("  4. 获取 Top20 热榜")
        
        # 步骤 1: 假设已经抓取了新文章（这里省略抓取步骤）
        print("\n✅ 步骤 1: 文章抓取完成（假设）")
        
        # 步骤 2: 聚类
        print("\n⏳ 步骤 2: 事件聚类...")
        cluster_result = cluster_new_articles(db)
        print(f"  聚类文章：{cluster_result['clustered_count']}")
        print(f"  新事件：{cluster_result['new_events_count']}")
        
        # 步骤 3: 计算热度
        print("\n⏳ 步骤 3: 计算热度...")
        heat_result = calculate_all_heat_scores(db)
        print(f"  更新文章：{heat_result['articles_updated']}")
        print(f"  更新事件：{heat_result['events_updated']}")
        
        # 步骤 4: 获取热榜
        print("\n⏳ 步骤 4: 获取热榜...")
        calculator = HeatCalculator(db)
        top_events = calculator.get_top_events(limit=20)
        
        print(f"\n🏆 Top 10 热榜:")
        print(f"  {'排名':<6} {'热度':<12} {'标题':<45}")
        print(f"  {'-'*65}")
        
        for i, event in enumerate(top_events[:10], 1):
            print(f"  {i:<6} {event.heat_score:<12.2f} {event.title[:43]:<45}")
        
    finally:
        db.close()
    
    print("\n✅ 完整工作流演示完成")


def main():
    """主函数"""
    print("\n🐶 WRHITW 热度算法与事件聚类演示")
    print("="*80)
    
    # 演示各个功能
    demo_heat_calculation()
    demo_event_clustering()
    demo_complete_workflow()
    
    print("\n" + "="*80)
    print("✅ 所有演示完成！")
    print("="*80)
    print("\n💡 提示:")
    print("  - 实际使用时，请先运行数据抓取脚本")
    print("  - 热度算法和聚类可以定时运行（如每 30 分钟）")
    print("  - 通过 API 接口提供热榜数据给前端")
    print()


if __name__ == "__main__":
    main()
