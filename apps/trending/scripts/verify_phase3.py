#!/usr/bin/env python3
"""
快速验证脚本 - 验证阶段 3 开发的代码可以正常导入和运行
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*80)
print("🔍 阶段 3 代码验证")
print("="*80)

try:
    # 测试导入
    print("\n1️⃣  测试导入...")
    
    from app.services.heat_calculator import HeatCalculator, calculate_all_heat_scores
    print("  ✅ heat_calculator 导入成功")
    
    from app.services.event_clusterer import (
        EventClusterer,
        cluster_new_articles,
        TextPreprocessor,
        TFIDFVectorizer
    )
    print("  ✅ event_clusterer 导入成功")
    
    from app.services import (
        HeatCalculator,
        calculate_all_heat_scores,
        EventClusterer,
        cluster_new_articles,
    )
    print("  ✅ services.__init__ 导出正确")
    
    # 测试文本预处理（不需要数据库）
    print("\n2️⃣  测试文本预处理...")
    
    test_text = "Breaking News: Major Event Happens in Technology Sector!"
    cleaned = TextPreprocessor.clean_text(test_text)
    print(f"  原文：{test_text}")
    print(f"  清洗：{cleaned}")
    
    tokens = TextPreprocessor.tokenize(test_text)
    print(f"  分词：{tokens}")
    
    keywords = TextPreprocessor.extract_keywords(test_text, top_n=3)
    print(f"  关键词：{keywords}")
    print("  ✅ 文本预处理正常")
    
    # 测试 TF-IDF 向量化
    print("\n3️⃣  测试 TF-IDF 向量化...")
    
    docs = [
        "Technology news about innovation",
        "Political news from government",
        "Sports championship results",
    ]
    
    vectorizer = TFIDFVectorizer()
    vectorizer.fit(docs)
    
    query = "Technology innovation"
    vec = vectorizer.transform(query)
    
    print(f"  词汇表大小：{len(vectorizer.vocabulary)}")
    print(f"  查询：{query}")
    print(f"  向量维度：{len(vec)}")
    print("  ✅ TF-IDF 向量化正常")
    
    # 测试余弦相似度
    print("\n4️⃣  测试余弦相似度...")
    
    clusterer = EventClusterer.__new__(EventClusterer)
    
    vec1 = {"tech": 0.5, "news": 0.3, "innovation": 0.2}
    vec2 = {"tech": 0.4, "news": 0.4, "innovation": 0.2}
    
    sim = clusterer.cosine_similarity(vec1, vec2)
    print(f"  相似度：{sim:.4f}")
    print("  ✅ 余弦相似度正常")
    
    # 测试 HeatCalculator 类初始化
    print("\n5️⃣  测试 HeatCalculator 类...")
    
    # 注意：需要数据库会话才能完全测试
    print("  ⚠️  HeatCalculator 需要数据库会话")
    print("  运行 'python scripts/test_heat_algorithm.py' 进行完整测试")
    
    # 测试 EventClusterer 类
    print("\n6️⃣  测试 EventClusterer 类...")
    print("  ⚠️  EventClusterer 需要数据库会话")
    print("  运行 'python scripts/test_event_clustering.py' 进行完整测试")
    
    print("\n" + "="*80)
    print("✅ 所有验证通过！")
    print("="*80)
    
    print("\n💡 提示:")
    print("  - 基础功能验证通过")
    print("  - 完整测试需要数据库")
    print("  - 运行以下命令进行完整测试:")
    print("    python scripts/test_heat_algorithm.py")
    print("    python scripts/test_event_clustering.py")
    print("    python scripts/demo_heat_and_clustering.py")
    print()
    
except Exception as e:
    print(f"\n❌ 验证失败：{str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
