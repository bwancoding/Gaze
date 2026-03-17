"""
WRHITW Stakeholder Models
相关方认证系统数据库模型
"""

from sqlalchemy import Column, String, Text as _Text, Integer, Boolean, DateTime, DECIMAL, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import UUID, JSONColumn
import uuid


class StakeholderType(Base):
    """相关方类型表（预定义）"""
    __tablename__ = "stakeholder_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)  # e.g., "Country", "Company", "Organization", "Group"
    description = Column(_Text)
    category = Column(String(50))  # geopolitics, technology, economy
    verification_required = Column(Boolean, default=True)
    verification_method = Column(String(200))  # e.g., "IP address", "Email domain", "Document upload"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Stakeholder(Base):
    """相关方定义表"""
    __tablename__ = "stakeholders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)  # e.g., "Iranian Civilians", "US Soldiers", "NVIDIA Employees"
    type_id = Column(UUID(as_uuid=True), ForeignKey('stakeholder_types.id'), nullable=False)
    description = Column(_Text)  # e.g., "Ordinary citizens living in Iran"
    category = Column(String(50))  # geopolitics, technology, economy
    verification_required = Column(Boolean, default=True)
    verification_method = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    # type = relationship("StakeholderType", backref="stakeholders")


class EventStakeholder(Base):
    """事件 - 相关方关联表"""
    __tablename__ = "event_stakeholders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    stakeholder_id = Column(UUID(as_uuid=True), ForeignKey('stakeholders.id'), nullable=False)
    relevance_score = Column(DECIMAL(3, 2), default=0.5)  # AI 判断的相关性分数 0-1
    perspective_summary = Column(_Text)  # AI-generated stakeholder perspective for this event
    key_concerns = Column(JSONColumn)  # ["concern1", "concern2"]
    is_ai_generated = Column(Boolean, default=False)  # Whether this was auto-created by AI
    status = Column(String(20), default='pending')  # pending, approved, rejected
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('event_id', 'stakeholder_id', name='uq_event_stakeholder'),
    )


class StakeholderVerification(Base):
    """相关方身份认证申请表"""
    __tablename__ = "stakeholder_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    stakeholder_id = Column(UUID(as_uuid=True), ForeignKey('stakeholders.id'), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'))
    
    # 申请信息
    application_text = Column(_Text)  # 用户说明为什么自己是相关方
    proof_type = Column(String(50))  # ip_address, email, document, other
    proof_data = Column(_Text)  # 存储证明数据（加密）
    
    # 审核状态
    status = Column(String(20), default='pending')  # pending, approved, rejected
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(_Text)  # 审核备注
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserStakeholderRole(Base):
    """用户 - 相关方角色关联表（已认证的角色）"""
    __tablename__ = "user_stakeholder_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    stakeholder_id = Column(UUID(as_uuid=True), ForeignKey('stakeholders.id'), nullable=False)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True))
    
    # 元数据
    display_name = Column(String(255))  # 显示名称（可与 stakeholder.name 不同）
    badge_color = Column(String(20), default='blue')  # 徽章颜色
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'stakeholder_id', name='uq_user_stakeholder'),
    )
