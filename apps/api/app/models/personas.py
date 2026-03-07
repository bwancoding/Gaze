"""
WRHITW User Persona Models
用户身份系统数据库模型
"""

from sqlalchemy import Column, String, Text as _Text, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import os

# 根据数据库类型选择兼容的类型
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wrhitw.db")
IS_SQLITE = DATABASE_URL.startswith("sqlite")

if IS_SQLITE:
    from sqlalchemy import String as _String
    from sqlalchemy import TypeDecorator
    
    class SQLiteUUID(TypeDecorator):
        """SQLite UUID 类型，存储为字符串"""
        impl = _String
        cache_ok = True
        
        def process_bind_param(self, value, dialect):
            if value is None:
                return value
            return str(value) if hasattr(value, '__str__') else value
        
        def process_result_value(self, value, dialect):
            return value
    
    def UUID(as_uuid=False):
        return SQLiteUUID(36)
else:
    UUID = PG_UUID


class UserPersona(Base):
    """用户身份表"""
    __tablename__ = "user_personas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    persona_name = Column(String(100), nullable=False)  # e.g., "Iranian Civilian"
    avatar_color = Column(String(20), default='blue')  # 随机颜色标识
    is_verified = Column(Boolean, default=False)  # 是否有已认证的关联
    
    # Soft delete fields
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    # verifications = relationship("EventStakeholderVerification", backref="persona")
    # comments = relationship("Comment", backref="persona")


class EventStakeholderVerification(Base):
    """事件 - 身份 - 相关方 认证关系表"""
    __tablename__ = "event_stakeholder_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_persona_id = Column(UUID(as_uuid=True), ForeignKey('user_personas.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    stakeholder_id = Column(UUID(as_uuid=True), ForeignKey('stakeholders.id'), nullable=False)
    
    # 申请信息
    application_text = Column(_Text)
    proof_type = Column(String(50))
    proof_data = Column(_Text)
    
    # 审核状态
    status = Column(String(20), default='pending')  # pending, approved, rejected
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(_Text)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 唯一约束：一个身份在一个事件中只能有一个认证
    __table_args__ = (
        UniqueConstraint('user_persona_id', 'event_id', name='uq_persona_event'),
    )


# Comment 模型在单独的文件中，这里只添加外键引用说明
# class Comment(Base):
#     """评论表（需要添加以下字段）"""
#     __tablename__ = "comments"
#     
#     # 现有字段...
#     user_persona_id = Column(UUID(as_uuid=True), ForeignKey('user_personas.id', ondelete='SET NULL'))
#     # 评论时是否显示认证徽章，通过查询 EventStakeholderVerification 判断
