"""
创建评论表数据库迁移脚本
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base

# 导入所有模型以确保外键关系正确
from app.models import User, Event  # 都在 __init__.py 中
from app.models.personas import UserPersona, EventStakeholderVerification
from app.models.comments import Comment

def create_comments_table():
    """创建评论表"""
    print("Creating comments table...")
    
    # 创建所有表（如果不存在）
    Base.metadata.create_all(bind=engine)
    
    print("✅ Comments table created successfully!")
    
    # 验证表是否存在
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if "comments" in tables:
        print("✅ Verified: comments table exists")
    else:
        print("❌ Error: comments table not found")

if __name__ == "__main__":
    create_comments_table()
