#!/usr/bin/env python3
"""
数据库初始化脚本
- 创建所有表
- 初始化 15 家媒体数据源
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, init_db, SessionLocal
from app.models.source import Source
from app.config import RSS_SOURCES
from datetime import datetime


def create_tables():
    """创建所有数据库表"""
    print("📦 正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")


def init_sources():
    """初始化数据源"""
    print("\n📰 正在初始化数据源...")
    
    db = SessionLocal()
    try:
        # 检查是否已存在数据源
        existing_count = db.query(Source).count()
        if existing_count > 0:
            print(f"⚠️  数据库中已有 {existing_count} 个数据源，跳过初始化")
            return
        
        # 插入所有数据源
        for source_data in RSS_SOURCES:
            source = Source(
                name=source_data["name"],
                url=source_data["url"],
                stance=source_data["stance"],
                region=source_data["region"],
                priority=source_data["priority"],
                update_interval_minutes=source_data["update_interval_minutes"],
                enabled=source_data["enabled"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(source)
            print(f"  ✓ 添加数据源：{source_data['name']} ({source_data['priority']})")
        
        db.commit()
        print(f"\n✅ 成功初始化 {len(RSS_SOURCES)} 个数据源")
        
        # 统计信息
        p0_count = db.query(Source).filter(Source.priority == "P0").count()
        p1_count = db.query(Source).filter(Source.priority == "P1").count()
        p2_count = db.query(Source).filter(Source.priority == "P2").count()
        
        print(f"\n📊 数据源统计:")
        print(f"  P0 优先级：{p0_count} 个")
        print(f"  P1 优先级：{p1_count} 个")
        print(f"  P2 优先级：{p2_count} 个")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败：{e}")
        raise
    finally:
        db.close()


def main():
    """主函数"""
    print("=" * 60)
    print("WRHITW Trending MVP - 数据库初始化")
    print("=" * 60)
    
    try:
        # 创建表
        create_tables()
        
        # 初始化数据源
        init_sources()
        
        print("\n" + "=" * 60)
        print("✅ 数据库初始化完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 初始化过程中出错：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
