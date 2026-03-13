"""
数据库连接配置
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.config import settings
import time

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # 连接池大小
    max_overflow=40,        # 最大溢出连接数
    pool_timeout=30,        # 连接获取超时
    pool_recycle=3600,      # 连接回收时间
    pool_pre_ping=True,     # 使用前检查连接
    echo=settings.DEBUG     # 开发环境开启 SQL 日志
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 模型基类
Base = declarative_base()


# 慢查询日志（超过 1 秒的查询）
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 1.0:  # 超过 1 秒的查询
        print(f"⚠️ 慢查询：{total:.2f}s - {statement[:100]}...")


def get_db():
    """获取数据库会话（依赖注入用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库（创建所有表）"""
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")


def drop_db():
    """删除所有表（仅用于开发环境）"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️ 所有数据库表已删除")
