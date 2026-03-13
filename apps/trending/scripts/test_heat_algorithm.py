"""
热度算法测试脚本

测试内容：
- 时间衰减函数
- 互动权重计算
- 源优先级加权
- Top20 筛选
- 排序算法
"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.article import Article
from app.models.event import Event
from app.models.source import Source
from app.services.heat_calculator import HeatCalculator, calculate_all_heat_scores


def create_test_data(db: Session):
    """创建测试数据"""
    print("\n📊 创建测试数据...")
    
    # 创建测试源
    test_sources = [
        {"name": "Test Reuters", "url": "https://reuters.com/test", "stance": "center", "region": "international", "priority": "P0"},
        {"name": "Test CNN", "url": "https://cnn.com/test", "stance": "left", "region": "us", "priority": "P1"},
        {"name": "Test Fox", "url": "https://foxnews.com/test", "stance": "right", "region": "us", "priority": "P1"},
        {"name": "Test Local", "url": "https://local.com/test", "stance": "center", "region": "us", "priority": "P2"},
    ]
    
    sources = []
    for src in test_sources:
        source = Source(**src)
        db.add(source)
        db.flush()
        sources.append(source)
    
    print(f"  ✅ 创建 {len(sources)} 个测试源")
    
    # 创建测试事件
    now = datetime.utcnow()
    events = []
    for i in range(5):
        event = Event(
            title=f"测试事件 {i+1}",
            summary=f"这是测试事件 {i+1} 的摘要",
            keywords=["测试", "新闻", f"事件{i+1}"],
            source_id=sources[i % len(sources)].id,
            created_at=now - timedelta(hours=i*2),
        )
        db.add(event)
        db.flush()
        events.append(event)
    
    print(f"  ✅ 创建 {len(events)} 个测试事件")
    
    # 创建测试文章（不同时间、不同互动量）
    articles_data = [
        # 新文章，高互动
        {"title": "突发新闻：重大事件发生", "hours_ago": 1, "comments": 500, "shares": 200, "source_idx": 0},
        # 新文章，中等互动
        {"title": "重要更新：事件进展", "hours_ago": 2, "comments": 200, "shares": 100, "source_idx": 1},
        # 中等时间，高互动
        {"title": "深度分析：事件背后", "hours_ago": 6, "comments": 800, "shares": 400, "source_idx": 0},
        # 中等时间，低互动
        {"title": "简短报道：事件概要", "hours_ago": 8, "comments": 50, "shares": 20, "source_idx": 2},
        # 旧文章，高互动
        {"title": "回顾：事件起源", "hours_ago": 24, "comments": 1000, "shares": 500, "source_idx": 0},
        # 旧文章，低互动
        {"title": "早期报道：初始消息", "hours_ago": 48, "comments": 100, "shares": 30, "source_idx": 3},
        # 很旧的文章
        {"title": "最早报道", "hours_ago": 72, "comments": 50, "shares": 10, "source_idx": 1},
    ]
    
    articles = []
    for i, data in enumerate(articles_data):
        article = Article(
            title=data["title"],
            summary=f"文章摘要 {i+1}",
            url=f"https://example.com/article/{i+1}",
            published_at=now - timedelta(hours=data["hours_ago"]),
            comment_count=data["comments"],
            share_count=data["shares"],
            source_id=sources[data["source_idx"]].id,
            event_id=events[i % len(events)].id,
        )
        db.add(article)
        articles.append(article)
    
    db.commit()
    print(f"  ✅ 创建 {len(articles)} 个测试文章")
    
    return sources, events, articles


def test_time_decay(calculator: HeatCalculator):
    """测试时间衰减函数"""
    print("\n⏰ 测试时间衰减函数...")
    
    now = datetime.utcnow()
    test_cases = [
        (0, "刚刚"),
        (1, "1 小时前"),
        (6, "6 小时前"),
        (12, "12 小时前"),
        (24, "24 小时前"),
        (48, "48 小时前"),
        (72, "72 小时前"),
    ]
    
    print(f"  {'时间':<15} {'衰减因子':<15} {'保留热度':<15}")
    print(f"  {'-'*45}")
    
    for hours, label in test_cases:
        published_at = now - timedelta(hours=hours)
        decay = calculator.calculate_time_decay(published_at, now)
        retained = decay * 100
        print(f"  {label:<15} {decay:<15.4f} {retained:<15.2f}%")
    
    print("  ✅ 时间衰减测试完成")


def test_interaction_score(calculator: HeatCalculator):
    """测试互动分数计算"""
    print("\n💬 测试互动权重计算...")
    
    test_cases = [
        (0, 0, "无互动"),
        (10, 5, "低互动"),
        (100, 50, "中等互动"),
        (500, 200, "高互动"),
        (1000, 500, "爆款"),
        (5000, 2000, "超级爆款"),
    ]
    
    print(f"  {'场景':<15} {'评论':<10} {'分享':<10} {'互动分数':<15}")
    print(f"  {'-'*50}")
    
    for comments, shares, label in test_cases:
        score = calculator.calculate_interaction_score(comments, shares)
        print(f"  {label:<15} {comments:<10} {shares:<10} {score:<15.2f}")
    
    print("  ✅ 互动分数测试完成")


def test_source_weight(calculator: HeatCalculator, db: Session):
    """测试源优先级加权"""
    print("\n📰 测试源优先级加权...")
    
    sources = db.query(Source).all()
    
    print(f"  {'媒体名称':<25} {'优先级':<10} {'权重':<10}")
    print(f"  {'-'*45}")
    
    for source in sources:
        weight = calculator.get_source_weight(source.id)
        print(f"  {source.name:<25} {source.priority:<10} {weight:<10.2f}")
    
    print("  ✅ 源权重测试完成")


def test_article_heat(calculator: HeatCalculator, db: Session):
    """测试文章热度计算"""
    print("\n🔥 测试文章热度计算...")
    
    articles = db.query(Article).order_by(Article.published_at).all()
    
    print(f"  {'标题':<35} {'时间':<12} {'互动':<12} {'源':<8} {'热度':<10}")
    print(f"  {'-'*80}")
    
    for article in articles:
        heat = calculator.calculate_article_heat(article)
        hours_ago = (datetime.utcnow() - article.published_at).total_seconds() / 3600
        interactions = article.comment_count + article.share_count
        source = db.query(Source).filter(Source.id == article.source_id).first()
        
        print(f"  {article.title[:33]:<35} {hours_ago:>5.1f}h     {interactions:<12} {source.priority:<8} {heat:<10.2f}")
    
    print("  ✅ 文章热度测试完成")


def test_event_heat(calculator: HeatCalculator, db: Session):
    """测试事件热度计算"""
    print("\n🌟 测试事件热度计算...")
    
    events = db.query(Event).all()
    
    print(f"  {'事件标题':<35} {'文章数':<8} {'媒体数':<8} {'热度':<10}")
    print(f"  {'-'*70}")
    
    for event in events:
        db.refresh(event)  # 刷新以获取最新文章
        heat = calculator.calculate_event_heat(event)
        print(f"  {event.title[:33]:<35} {event.article_count:<8} {event.unique_media_count:<8} {heat:<10.2f}")
    
    print("  ✅ 事件热度测试完成")


def test_top20_filter(db: Session):
    """测试 Top20 筛选逻辑"""
    print("\n🏆 测试 Top20 筛选逻辑...")
    
    calculator = HeatCalculator(db)
    
    # 先更新所有热度
    calculate_all_heat_scores(db)
    
    # 获取 Top20 事件
    top_events = calculator.get_top_events(limit=20)
    
    print(f"  获取到 {len(top_events)} 个热门事件")
    print(f"  {'排名':<6} {'热度':<12} {'标题':<40}")
    print(f"  {'-'*60}")
    
    for i, event in enumerate(top_events, 1):
        print(f"  {i:<6} {event.heat_score:<12.2f} {event.title[:38]:<40}")
    
    # 获取 Top50 文章
    top_articles = calculator.get_top_articles(limit=50)
    
    print(f"\n  获取到 {len(top_articles)} 篇热门文章")
    print(f"  {'排名':<6} {'热度':<12} {'标题':<40}")
    print(f"  {'-'*60}")
    
    for i, article in enumerate(top_articles[:10], 1):  # 只显示前 10
        print(f"  {i:<6} {article.heat_score:<12.2f} {article.title[:38]:<40}")
    
    if len(top_articles) > 10:
        print(f"  ... 还有 {len(top_articles) - 10} 篇")
    
    print("  ✅ Top20 筛选测试完成")


def test_trending_events(db: Session):
    """测试 trending 事件（热度增长最快）"""
    print("\n📈 测试 Trending 事件（热度增长率）...")
    
    calculator = HeatCalculator(db)
    
    # 获取 trending 事件
    trending = calculator.get_trending_events(limit=10, time_window_hours=48)
    
    if not trending:
        print("  ⚠️  暂无 trending 事件数据")
        return
    
    print(f"  {'排名':<6} {'增长率':<12} {'热度':<12} {'标题':<35}")
    print(f"  {'-'*70}")
    
    for i, (event, growth_rate) in enumerate(trending, 1):
        print(f"  {i:<6} {growth_rate:<12.2f}x {event.heat_score:<12.2f} {event.title[:33]:<35}")
    
    print("  ✅ Trending 事件测试完成")


def test_heat_distribution(db: Session):
    """测试热度分布统计"""
    print("\n📊 测试热度分布统计...")
    
    calculator = HeatCalculator(db)
    distribution = calculator.calculate_heat_distribution()
    
    print("\n  文章热度分布:")
    print(f"    总数：{distribution['articles']['count']}")
    print(f"    最小：{distribution['articles']['min']:.2f}")
    print(f"    最大：{distribution['articles']['max']:.2f}")
    print(f"    平均：{distribution['articles']['avg']:.2f}")
    
    print("\n  事件热度分布:")
    print(f"    总数：{distribution['events']['count']}")
    print(f"    最小：{distribution['events']['min']:.2f}")
    print(f"    最大：{distribution['events']['max']:.2f}")
    print(f"    平均：{distribution['events']['avg']:.2f}")
    
    print("  ✅ 热度分布测试完成")


def run_all_tests():
    """运行所有测试"""
    print("="*80)
    print("🔥 WRHITW 热度算法测试")
    print("="*80)
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 创建测试数据
        sources, events, articles = create_test_data(db)
        
        # 创建热度计算器
        calculator = HeatCalculator(db)
        
        # 运行各项测试
        test_time_decay(calculator)
        test_interaction_score(calculator)
        test_source_weight(calculator, db)
        test_article_heat(calculator, db)
        test_event_heat(calculator, db)
        test_top20_filter(db)
        test_trending_events(db)
        test_heat_distribution(db)
        
        print("\n" + "="*80)
        print("✅ 所有测试完成！")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_all_tests()
