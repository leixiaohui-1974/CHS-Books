"""
用户模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    USER = "user"          # 普通用户
    VIP = "vip"            # VIP用户
    ADMIN = "admin"        # 管理员
    SUPER_ADMIN = "super_admin"  # 超级管理员


class User(Base):
    """用户模型"""
    
    __tablename__ = "users"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # 个人信息
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(String(500), nullable=True)
    
    # 角色和权限
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # 会员信息
    is_premium = Column(Boolean, default=False, nullable=False)
    premium_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # OAuth登录信息
    github_id = Column(String(100), unique=True, nullable=True)
    wechat_openid = Column(String(100), unique=True, nullable=True)
    
    # 统计信息
    total_learning_time = Column(Integer, default=0, nullable=False)  # 总学习时长（秒）
    login_count = Column(Integer, default=0, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    tool_executions = relationship("ToolExecution", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    @property
    def is_admin(self) -> bool:
        """是否为管理员"""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    @property
    def has_active_premium(self) -> bool:
        """是否有激活的会员"""
        if not self.is_premium:
            return False
        if self.premium_expires_at is None:
            return True
        return datetime.now(timezone.utc) < self.premium_expires_at
