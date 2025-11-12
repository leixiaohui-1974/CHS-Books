"""
会话管理模型
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum as SQLEnum, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class SessionStatus(str, Enum):
    """会话状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class UserSession(Base):
    """
    用户学习会话
    
    每个会话代表用户在一个案例中的完整学习过程
    """
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 关联的教材和案例
    book_slug = Column(String(100), nullable=False)
    chapter_slug = Column(String(100), nullable=True)
    case_slug = Column(String(100), nullable=False)
    
    # 会话状态
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False)
    
    # 工作区数据（存储在MongoDB，这里只存引用）
    workspace_id = Column(String(50), nullable=True)
    
    # 代码文件快照
    original_files = Column(JSON, default={})  # 原始代码文件
    modified_files = Column(JSON, default={})  # 用户修改的文件
    
    # 执行历史
    execution_count = Column(Integer, default=0)
    last_execution_id = Column(String(50), nullable=True)
    
    # AI上下文
    ai_context = Column(JSON, default={})  # AI对话上下文
    conversation_count = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # 资源配额
    max_executions = Column(Integer, default=100)
    max_cpu_time = Column(Integer, default=3600)  # 秒
    max_memory = Column(String(20), default="2GB")
    
    # 统计数据
    total_execution_time = Column(Integer, default=0)  # 秒
    total_ai_requests = Column(Integer, default=0)
    
    # 关联
    user = relationship("User", back_populates="sessions")
    executions = relationship("CodeExecution", back_populates="session", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            # 默认24小时后过期
            self.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return datetime.utcnow() > self.expires_at
    
    def is_active(self) -> bool:
        """检查是否活跃"""
        return self.status == SessionStatus.ACTIVE and not self.is_expired()
    
    def can_execute(self) -> bool:
        """检查是否可以执行代码"""
        if not self.is_active():
            return False
        if self.execution_count >= self.max_executions:
            return False
        return True
    
    def update_activity(self):
        """更新活跃时间"""
        self.last_active_at = datetime.utcnow()
    
    def extend_expiration(self, hours: int = 24):
        """延长过期时间"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "book_slug": self.book_slug,
            "chapter_slug": self.chapter_slug,
            "case_slug": self.case_slug,
            "status": self.status.value,
            "execution_count": self.execution_count,
            "last_execution_id": self.last_execution_id,
            "conversation_count": self.conversation_count,
            "created_at": self.created_at.isoformat(),
            "last_active_at": self.last_active_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_expired": self.is_expired(),
            "is_active": self.is_active(),
            "resource_quota": {
                "max_executions": self.max_executions,
                "remaining_executions": self.max_executions - self.execution_count,
                "max_cpu_time": self.max_cpu_time,
                "max_memory": self.max_memory
            },
            "statistics": {
                "total_execution_time": self.total_execution_time,
                "total_ai_requests": self.total_ai_requests
            }
        }


class CodeExecution(Base):
    """
    代码执行记录
    """
    __tablename__ = "code_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(50), unique=True, index=True, nullable=False)
    session_id = Column(String(50), ForeignKey("user_sessions.session_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 执行状态
    status = Column(String(20), default="pending", nullable=False)  # pending, running, completed, failed, timeout
    
    # 执行参数
    script_path = Column(String(500), nullable=False)
    input_params = Column(JSON, default={})
    
    # 代码快照（记录执行时的代码）
    code_snapshot = Column(JSON, default={})
    
    # 执行结果
    output_data = Column(JSON, nullable=True)
    console_output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # 资源使用
    execution_time = Column(Integer, default=0)  # 秒
    cpu_time = Column(Integer, default=0)
    memory_peak = Column(String(20), nullable=True)
    
    # 结果文件（存储在MinIO）
    result_files = Column(JSON, default=[])  # [{"type": "plot", "path": "...", ...}]
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # 关联
    session = relationship("UserSession", back_populates="executions")
    user = relationship("User")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "execution_id": self.execution_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "status": self.status,
            "script_path": self.script_path,
            "input_params": self.input_params,
            "output_data": self.output_data,
            "console_output": self.console_output,
            "error_message": self.error_message,
            "execution_time": self.execution_time,
            "resource_usage": {
                "cpu_time": self.cpu_time,
                "memory_peak": self.memory_peak
            },
            "result_files": self.result_files,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
