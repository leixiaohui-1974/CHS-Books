"""
学习进度模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ProgressStatus(str, enum.Enum):
    """进度状态"""
    NOT_STARTED = "not_started"  # 未开始
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"      # 已完成


class UserProgress(Base):
    """用户学习进度（书籍级别）"""
    
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    
    # 注册时间
    enrollment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    
    # 整体进度
    chapters_completed = Column(Integer, default=0, nullable=False)
    chapters_total = Column(Integer, default=0, nullable=False)
    cases_completed = Column(Integer, default=0, nullable=False)
    cases_total = Column(Integer, default=0, nullable=False)
    percentage = Column(Float, default=0.0, nullable=False)
    
    # 学习行为
    total_time_spent = Column(Integer, default=0, nullable=False)  # 总学习时长（秒）
    tool_usage_count = Column(Integer, default=0, nullable=False)  # 工具使用次数
    study_streak_days = Column(Integer, default=0, nullable=False)  # 连续学习天数
    last_streak_date = Column(DateTime(timezone=True), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    user = relationship("User", back_populates="progress")
    chapter_progress = relationship("ChapterProgress", back_populates="user_progress", cascade="all, delete-orphan")
    case_progress = relationship("CaseProgress", back_populates="user_progress", cascade="all, delete-orphan")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('user_id', 'book_id', name='uq_user_book'),
    )
    
    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, book_id={self.book_id}, percentage={self.percentage})>"


class ChapterProgress(Base):
    """章节学习进度"""
    
    __tablename__ = "chapter_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    
    # 状态
    status = Column(SQLEnum(ProgressStatus), default=ProgressStatus.NOT_STARTED, nullable=False)
    
    # 时间
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent = Column(Integer, default=0, nullable=False)  # 学习时长（秒）
    
    # 阅读进度
    reading_percentage = Column(Float, default=0.0, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    user_progress = relationship("UserProgress", back_populates="chapter_progress")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('user_progress_id', 'chapter_id', name='uq_user_chapter'),
    )
    
    def __repr__(self):
        return f"<ChapterProgress(chapter_id={self.chapter_id}, status={self.status})>"


class CaseProgress(Base):
    """案例学习进度"""
    
    __tablename__ = "case_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id", ondelete="CASCADE"), nullable=False)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    
    # 状态
    status = Column(SQLEnum(ProgressStatus), default=ProgressStatus.NOT_STARTED, nullable=False)
    
    # 时间
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent = Column(Integer, default=0, nullable=False)  # 学习时长（秒）
    
    # 工具使用
    attempts = Column(Integer, default=0, nullable=False)  # 尝试次数
    successful_runs = Column(Integer, default=0, nullable=False)  # 成功运行次数
    
    # 习题成绩
    exercise_score = Column(Float, nullable=True)  # 0-100
    
    # 笔记
    notes = Column(String(2000), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    user_progress = relationship("UserProgress", back_populates="case_progress")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('user_progress_id', 'case_id', name='uq_user_case'),
    )
    
    def __repr__(self):
        return f"<CaseProgress(case_id={self.case_id}, status={self.status})>"
