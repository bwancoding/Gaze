"""
事件去重聚类测试脚本

测试内容：
- TF-IDF + 余弦相似度
- 事件中心向量
- 增量更新
- 重复检测
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
from app.services.event_clusterer import (
    TextPreprocessor,
    TFIDFVectorizer,
    EventClusterer,
    cluster_new_articles
)


def test_text_preprocessing():
    """测试文本预处理"""
    print("="*80)
    print("📝 测试文本预处理")
    print("="*80)
    
    test_texts = [
        "Breaking News: Major Event Happens!",
        "The quick brown fox jumps over the lazy dog.",
        "President announces new policy in Washington D.C.",
        "Tech Giants Report Q4 Earnings: Apple, Google, Microsoft",
    ]
    
    print("\n1️⃣  文本清洗测试:")
    for text in test_texts:
        cleaned = TextPreprocessor.clean_text(text)
        print(f"  原始：{text}")
        print(f"  清洗：{cleaned}")
        print()
    
    print("\n2️⃣  分词测试:")
    for text in test_texts:
        tokens = TextPreprocessor.tokenize(text)
        print(f"  原文：{text[:50]}...")
        print(f"  分词：{tokens}")
        print()
    
    print("\n3️⃣  关键词提取测试:")
    for text in test_texts:
        keywords = TextPreprocessor.extract_keywords(text, top_n=5)
        print(f"  原文：{text[:50]}...")
        print(f"  关键词：{keywords}")
        print()
    
    print("✅ 文本预处理测试完成")


def test_tfidf_vectorizer():
    """测试 TF-IDF 向量化"""
    print("\n" + "="*80)
    print("📊 测试 TF-IDF 向量化")
    print("="*80)
    
    # 测试文档
    documents = [
        "Breaking news about technology innovation",
        "Technology companies report earnings",
        "Political news from Washington",
        "Breaking political scandal in government",
        "Sports championship results",
    ]
    
    print("\n1️⃣  拟合文档集:")
    vectorizer = TFIDFVectorizer()
    vectorizer.fit(documents)
    
    print(f"  文档数量：{len(documents)}")
    print(f"  词汇表大小：{len(vectorizer.vocabulary)}")
    print(f"  IDF 词项数：{len(vectorizer.idf)}")
    
    print("\n2️⃣  部分 IDF 值:")
    sample_words = list(vectorizer.idf.keys())[:10]
    for word in sample_words:
        print(f"  {word}: {vectorizer.idf[word]:.4f}")
    
    print("\n3️⃣  文档向量化测试:")
    query = "Breaking technology news"
    vec = vectorizer.transform(query)
    
    print(f"  查询：{query}")
    print(f"  向量维度：{len(vec)}")
    print(f"  Top 权重词:")
    sorted_words = sorted(vec.items(), key=lambda x: x[1], reverse=True)[:5]
    for word, weight in sorted_words:
        print(f"    {word}: {weight:.4f}")
    
    print("\n✅ TF-IDF 向量化测试完成")


def test_cosine_similarity():
    """测试余弦相似度计算"""
    print("\n" + "="*80)
    print("🔍 测试余弦相似度")
    print("="*80)
    
    clusterer = EventClusterer.__new__(EventClusterer)  # 不初始化 DB
    
    # 测试向量
    test_cases = [
        (
            {"technology": 0.5, "news": 0.3, "innovation": 0.2},
            {"technology": 0.4, "news": 0.4, "innovation": 0.2},
            "高度相似"
        ),
        (
            {"technology": 0.5, "news": 0.3},
            {"sports": 0.5, "championship": 0.3},
            "完全不同"
        ),
        (
            {"politics": 0.4, "government": 0.3, "policy": 0.3},
            {"politics": 0.3, "government": 0.2, "scandal": 0.5},
            "部分相似"
        ),
        (
            {},
            {"anything": 0.5},
            "空向量"
        ),
    ]
    
    print(f"  {'场景':<15} {'相似度':<12} {'说明':<20}")
    print(f"  {'-'*50}")
    
    for vec1, vec2, label in test_cases:
        similarity = clusterer.cosine_similarity(vec1, vec2)
        print(f"  {label:<15} {similarity:<12.4f} {'':<20}")
    
    print("\n✅ 余弦相似度测试完成")


def create_test_data(db: Session):
    """创建测试数据"""
    print("\n" + "="*80)
    print("📊 创建聚类测试数据")
    print("="*80)
    
    # 创建测试源
    sources = [
        Source(name="Reuters Test", url="https://reuters.com/test1", stance="center", region="international", priority="P0"),
        Source(name="CNN Test", url="https://cnn.com/test1", stance="left", region="us", priority="P1"),
        Source(name="BBC Test", url="https://bbc.com/test1", stance="center-left", region="uk", priority="P0"),
    ]
    
    for source in sources:
        db.add(source)
    
    db.commit()
    print(f"  ✅ 创建 {len(sources)} 个测试源")
    
    # 创建测试事件（3 个不同主题）
    now = datetime.utcnow()
    
    # 事件 1: 科技新闻
    event1 = Event(
        title="Tech Giants Report Record Earnings",
        summary="Major technology companies announce Q4 results",
        keywords=["technology", "earnings", "tech", "companies"],
        source_id=sources[0].id,
        created_at=now - timedelta(hours=5),
        heat_score=150.0,
    )
    
    # 事件 2: 政治新闻
    event2 = Event(
        title="President Announces New Climate Policy",
        summary="New environmental regulations proposed",
        keywords=["politics", "climate", "policy", "government"],
        source_id=sources[1].id,
        created_at=now - timedelta(hours=3),
        heat_score=200.0,
    )
    
    # 事件 3: 体育新闻
    event3 = Event(
        title="Championship Finals Tonight",
        summary="Teams prepare for decisive match",
        keywords=["sports", "championship", "finals", "game"],
        source_id=sources[2].id,
        created_at=now - timedelta(hours=1),
        heat_score=100.0,
    )
    
    db.add_all([event1, event2, event3])
    db.flush()
    print(f"  ✅ 创建 {3} 个测试事件")
    
    # 创建测试文章（有些属于现有事件，有些是新事件）
    articles_data = [
        # 属于事件 1（科技）
        {"title": "Apple Reports Massive Profit Growth", "event_id": event1.id, "hours_ago": 4},
        {"title": "Google Earnings Beat Expectations", "event_id": event1.id, "hours_ago": 3},
        {"title": "Microsoft Cloud Revenue Surges", "event_id": event1.id, "hours_ago": 2},
        
        # 属于事件 2（政治）
        {"title": "White House Unveils Green Plan", "event_id": event2.id, "hours_ago": 2},
        {"title": "New Environmental Rules Announced", "event_id": event2.id, "hours_ago": 1},
        
        # 属于事件 3（体育）
        {"title": "Teams Ready for Big Game", "event_id": event3.id, "hours_ago": 1},
        
        # 新文章（未聚类）- 科技主题，应聚类到事件 1
        {"title": "Tech Stocks Soar After Earnings", "event_id": None, "hours_ago": 1},
        {"title": "Silicon Valley Companies Excel", "event_id": None, "hours_ago": 0.5},
        
        # 新文章 - 政治主题，应聚类到事件 2
        {"title": "Congress Debates Climate Bill", "event_id": None, "hours_ago": 0.5},
        
        # 新文章 - 全新主题（国际新闻），应创建新事件
        {"title": "International Summit Addresses Trade", "event_id": None, "hours_ago": 0.25},
        {"title": "Global Leaders Meet for Economic Talks", "event_id": None, "hours_ago": 0.1},
    ]
    
    articles = []
    for i, data in enumerate(articles_data):
        article = Article(
            title=data["title"],
            summary=f"Summary for article {i+1}",
            url=f"https://example.com/article/test{i+1}",
            published_at=now - timedelta(hours=data["hours_ago"]),
            source_id=sources[i % len(sources)].id,
            event_id=data["event_id"],
            is_processed=(data["event_id"] is not None),
        )
        db.add(article)
        articles.append(article)
    
    db.commit()
    print(f"  ✅ 创建 {len(articles)} 个测试文章")
    
    return sources, [event1, event2, event3], articles


def test_event_centroid(db: Session):
    """测试事件中心向量计算"""
    print("\n" + "="*80)
    print("🎯 测试事件中心向量")
    print("="*80)
    
    clusterer = EventClusterer(db)
    events = db.query(Event).all()
    
    print(f"\n  计算 {len(events)} 个事件的中心向量:")
    
    for event in events:
        db.refresh(event)
        centroid = clusterer.calculate_event_centroid(event)
        
        print(f"\n  事件：{event.title[:50]}")
        print(f"  向量维度：{len(centroid)}")
        print(f"  Top 5 权重词:")
        sorted_words = sorted(centroid.items(), key=lambda x: x[1], reverse=True)[:5]
        for word, weight in sorted_words:
            print(f"    {word}: {weight:.4f}")
    
    print("\n✅ 事件中心向量测试完成")


def test_similar_events_search(db: Session):
    """测试相似事件搜索"""
    print("\n" + "="*80)
    print("🔍 测试相似事件搜索")
    print("="*80)
    
    clusterer = EventClusterer(db)
    
    # 测试查询
    queries = [
        "Technology companies earnings report",
        "Government climate change policy",
        "Sports championship game results",
        "International trade summit",
    ]
    
    for query in queries:
        print(f"\n  查询：{query}")
        similar = clusterer.find_similar_events(query, limit=3, min_similarity=0.1)
        
        if similar:
            print(f"  找到 {len(similar)} 个相似事件:")
            for event, sim in similar:
                print(f"    - {event.title[:45]} (相似度：{sim:.4f})")
        else:
            print(f"  未找到相似事件")
    
    print("\n✅ 相似事件搜索测试完成")


def test_article_clustering(db: Session):
    """测试文章聚类"""
    print("\n" + "="*80)
    print("📚 测试文章聚类到事件")
    print("="*80)
    
    clusterer = EventClusterer(db)
    
    # 获取未处理的文章
    unprocessed = db.query(Article).filter(Article.is_processed == False).all()
    
    if not unprocessed:
        print("  ⚠️  没有未处理的文章")
        return
    
    print(f"  待聚类文章数：{len(unprocessed)}")
    
    # 聚类
    clustering = clusterer.cluster_articles_to_events(unprocessed)
    
    print(f"\n  聚类结果:")
    for event, articles in clustering.items():
        print(f"\n  事件：{event.title[:50]}")
        print(f"  匹配文章数：{len(articles)}")
        for article in articles:
            print(f"    - {article.title[:45]}")
    
    print("\n✅ 文章聚类测试完成")


def test_new_event_detection(db: Session):
    """测试新事件检测"""
    print("\n" + "="*80)
    print("✨ 测试新事件检测")
    print("="*80)
    
    clusterer = EventClusterer(db)
    
    # 测试文章
    test_articles = [
        "Tech innovation continues",  # 应匹配现有科技事件
        "Political debate in congress",  # 应匹配现有政治事件
        "Breaking international news",  # 可能是新事件
        "Celebrity gossip scandal",  # 全新主题
    ]
    
    for title in test_articles:
        article = Article(
            title=title,
            summary=f"Summary for {title}",
            url="https://example.com/test",
            published_at=datetime.utcnow(),
            source_id=1,
        )
        
        is_new, matched_event, similarity = clusterer.detect_new_event(article)
        
        print(f"\n  文章：{title}")
        if is_new:
            print(f"  → 新事件 (最高相似度：{similarity:.4f})")
        else:
            print(f"  → 匹配现有事件：{matched_event.title[:40]} (相似度：{similarity:.4f})")
    
    print("\n✅ 新事件检测测试完成")


def test_duplicate_detection(db: Session):
    """测试重复事件检测"""
    print("\n" + "="*80)
    print("🔄 测试重复事件检测")
    print("="*80)
    
    clusterer = EventClusterer(db)
    
    # 创建两个相似事件
    now = datetime.utcnow()
    
    event1 = Event(
        title="Major Earthquake Strikes Region",
        summary="Powerful earthquake causes damage",
        keywords=["earthquake", "disaster", "region"],
        source_id=1,
        created_at=now - timedelta(hours=2),
        heat_score=300.0,
    )
    
    event2 = Event(
        title="Earthquake Hits Area with Strong Tremors",
        summary="Strong tremors reported in region",
        keywords=["earthquake", "tremors", "area"],
        source_id=2,
        created_at=now - timedelta(hours=1),
        heat_score=250.0,
    )
    
    db.add_all([event1, event2])
    db.commit()
    
    # 检测重复
    duplicates = clusterer.find_duplicate_events(time_window_days=1)
    
    if duplicates:
        print(f"  发现 {len(duplicates)} 对重复事件:")
        for e1, e2, sim in duplicates:
            print(f"\n  事件 1: {e1.title}")
            print(f"  事件 2: {e2.title}")
            print(f"  相似度：{sim:.4f}")
    else:
        print("  未发现重复事件")
    
    print("\n✅ 重复事件检测测试完成")


def test_incremental_update(db: Session):
    """测试增量更新"""
    print("\n" + "="*80)
    print("🔄 测试增量更新")
    print("="*80)
    
    # 创建新文章
    now = datetime.utcnow()
    new_articles = [
        Article(
            title="Tech Earnings Season Continues",
            summary="More companies report",
            url="https://example.com/new1",
            published_at=now,
            source_id=1,
            is_processed=False,
        ),
        Article(
            title="Climate Policy Debate Intensifies",
            summary="More discussions",
            url="https://example.com/new2",
            published_at=now,
            source_id=2,
            is_processed=False,
        ),
        Article(
            title="Health Crisis Updates",
            summary="New developments",
            url="https://example.com/new3",
            published_at=now,
            source_id=3,
            is_processed=False,
        ),
    ]
    
    db.add_all(new_articles)
    db.commit()
    
    print(f"  新增文章数：{len(new_articles)}")
    
    # 增量更新
    result = cluster_new_articles(db, new_articles)
    
    print(f"\n  更新结果:")
    print(f"    聚类文章数：{result['clustered_count']}")
    print(f"    新事件数：{result['new_events_count']}")
    print(f"    合并事件数：{result['merged_events_count']}")
    
    # 显示新创建的事件
    new_events = db.query(Event).filter(
        Event.created_at >= now - timedelta(minutes=5)
    ).all()
    
    if new_events:
        print(f"\n  新事件:")
        for event in new_events:
            print(f"    - {event.title} (文章数：{event.article_count})")
    
    print("\n✅ 增量更新测试完成")


def run_all_tests():
    """运行所有测试"""
    print("\n🐶 WRHITW 事件去重聚类测试")
    print("="*80)
    
    # 文本预处理测试（不需要数据库）
    test_text_preprocessing()
    test_tfidf_vectorizer()
    test_cosine_similarity()
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 创建测试数据
        sources, events, articles = create_test_data(db)
        
        # 运行数据库相关测试
        test_event_centroid(db)
        test_similar_events_search(db)
        test_article_clustering(db)
        test_new_event_detection(db)
        test_duplicate_detection(db)
        test_incremental_update(db)
        
        print("\n" + "="*80)
        print("✅ 所有聚类测试完成！")
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
