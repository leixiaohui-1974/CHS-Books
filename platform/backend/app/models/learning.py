"""
学习追踪相关数据模型
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import (
    Integer, String, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DifficultyLevel(str, Enum):
    """难度级别"""
    BEGINNER = "beginner"  # 初级
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"  # 高级
    EXPERT = "expert"  # 专家


class MasteryLevel(str, Enum):
    """掌握程度"""
    NOT_STARTED = "not_started"  # 未开始
    LEARNING = "learning"  # 学习中
    PRACTICING = "practicing"  # 练习中
    MASTERED = "mastered"  # 已掌握
    EXPERT = "expert"  # 精通


class ActivityType(str, Enum):
    """活动类型"""
    VIDEO_WATCH = "video_watch"  # 观看视频
    READING = "reading"  # 阅读
    EXERCISE = "exercise"  # 练习
    QUIZ = "quiz"  # 测验
    EXAM = "exam"  # 考试
    DISCUSSION = "discussion"  # 讨论
    PROJECT = "project"  # 项目


class AchievementType(str, Enum):
    """成就类型"""
    STUDY_TIME = "study_time"  # 学习时长
    EXERCISE_COUNT = "exercise_count"  # 练习次数
    MASTERY_COUNT = "mastery_count"  # 掌握知识点数
    STREAK_DAYS = "streak_days"  # 连续学习天数
    PERFECT_SCORE = "perfect_score"  # 满分
    FAST_LEARNER = "fast_learner"  # 快速学习者
    MILESTONE = "milestone"  # 里程碑


# ========================================
# 知识点体系
# ========================================

class Subject(Base):
    """学科"""
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    chapters: Mapped[List["Chapter"]] = relationship(
        "Chapter", back_populates="subject", cascade="all, delete-orphan"
    )


class Chapter(Base):
    """章节"""
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    subject: Mapped["Subject"] = relationship("Subject", back_populates="chapters")
    knowledge_points: Mapped[List["KnowledgePoint"]] = relationship(
        "KnowledgePoint", back_populates="chapter", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_chapter_subject", "subject_id"),
    )


class KnowledgePoint(Base):
    """知识点"""
    __tablename__ = "knowledge_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chapter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        String(20), default=DifficultyLevel.INTERMEDIATE
    )
    
    # 知识点关系
    prerequisites: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)  # 前置知识点ID列表
    related_points: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)  # 相关知识点ID列表
    
    # 学习资源
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    reading_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    exercise_count: Mapped[int] = mapped_column(Integer, default=0)  # 练习题数量
    
    order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="knowledge_points")
    user_progress: Mapped[List["UserKnowledgeProgress"]] = relationship(
        "UserKnowledgeProgress", back_populates="knowledge_point", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_kp_chapter", "chapter_id"),
        Index("idx_kp_difficulty", "difficulty"),
    )


# ========================================
# 用户学习进度
# ========================================

class UserKnowledgeProgress(Base):
    """用户知识点掌握进度"""
    __tablename__ = "user_knowledge_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    knowledge_point_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_points.id", ondelete="CASCADE"), nullable=False
    )
    
    # 掌握度
    mastery_level: Mapped[MasteryLevel] = mapped_column(
        String(20), default=MasteryLevel.NOT_STARTED
    )
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    
    # 学习统计
    study_time: Mapped[int] = mapped_column(Integer, default=0)  # 学习时长（秒）
    practice_count: Mapped[int] = mapped_column(Integer, default=0)  # 练习次数
    correct_count: Mapped[int] = mapped_column(Integer, default=0)  # 正确次数
    wrong_count: Mapped[int] = mapped_column(Integer, default=0)  # 错误次数
    
    # 间隔重复算法参数 (SM-2算法)
    easiness_factor: Mapped[float] = mapped_column(Float, default=2.5)  # 难度因子
    interval: Mapped[int] = mapped_column(Integer, default=0)  # 复习间隔（天）
    repetitions: Mapped[int] = mapped_column(Integer, default=0)  # 重复次数
    next_review_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 时间戳
    first_studied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_studied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    mastered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    knowledge_point: Mapped["KnowledgePoint"] = relationship(
        "KnowledgePoint", back_populates="user_progress"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "knowledge_point_id", name="uq_user_knowledge"),
        Index("idx_ukp_user", "user_id"),
        Index("idx_ukp_knowledge", "knowledge_point_id"),
        Index("idx_ukp_mastery", "mastery_level"),
        Index("idx_ukp_next_review", "next_review_date"),
    )


class LearningActivity(Base):
    """学习活动记录"""
    __tablename__ = "learning_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    knowledge_point_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("knowledge_points.id", ondelete="SET NULL"), nullable=True
    )
    
    # 活动信息
    activity_type: Mapped[ActivityType] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 时间统计
    duration: Mapped[int] = mapped_column(Integer, default=0)  # 持续时间（秒）
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 结果数据
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 分数
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    result_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # 详细结果数据
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_la_user", "user_id"),
        Index("idx_la_knowledge", "knowledge_point_id"),
        Index("idx_la_type", "activity_type"),
        Index("idx_la_started", "started_at"),
    )


class StudySession(Base):
    """学习会话"""
    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    
    # 会话信息
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, default=0)  # 秒
    
    # 会话统计
    activities_count: Mapped[int] = mapped_column(Integer, default=0)
    knowledge_points_studied: Mapped[int] = mapped_column(Integer, default=0)
    exercises_completed: Mapped[int] = mapped_column(Integer, default=0)
    
    # 设备信息
    device_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_ss_user", "user_id"),
        Index("idx_ss_started", "started_at"),
    )


# ========================================
# 学习路径和计划
# ========================================

class LearningPath(Base):
    """学习路径"""
    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    
    # 路径信息
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_subject_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True
    )
    
    # 路径配置
    knowledge_points: Mapped[List[int]] = mapped_column(JSON, nullable=False)  # 知识点ID列表（有序）
    estimated_hours: Mapped[int] = mapped_column(Integer, default=0)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        String(20), default=DifficultyLevel.INTERMEDIATE
    )
    
    # 进度
    current_index: Mapped[int] = mapped_column(Integer, default=0)
    completed_count: Mapped[int] = mapped_column(Integer, default=0)
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index("idx_lp_user", "user_id"),
        Index("idx_lp_subject", "target_subject_id"),
    )


class DailyGoal(Base):
    """每日学习目标"""
    __tablename__ = "daily_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # 目标日期
    
    # 目标设置
    target_study_time: Mapped[int] = mapped_column(Integer, default=3600)  # 秒
    target_exercises: Mapped[int] = mapped_column(Integer, default=10)
    target_knowledge_points: Mapped[int] = mapped_column(Integer, default=3)
    
    # 实际完成
    actual_study_time: Mapped[int] = mapped_column(Integer, default=0)
    actual_exercises: Mapped[int] = mapped_column(Integer, default=0)
    actual_knowledge_points: Mapped[int] = mapped_column(Integer, default=0)
    
    # 完成度
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_user_daily_goal"),
        Index("idx_dg_user", "user_id"),
        Index("idx_dg_date", "date"),
    )


# ========================================
# 成就系统
# ========================================

class Achievement(Base):
    """成就定义"""
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # 成就信息
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # 成就类型和条件
    achievement_type: Mapped[AchievementType] = mapped_column(String(20), nullable=False)
    requirement_value: Mapped[int] = mapped_column(Integer, nullable=False)  # 达成条件值
    points: Mapped[int] = mapped_column(Integer, default=10)  # 成就积分
    
    # 稀有度
    rarity: Mapped[str] = mapped_column(String(20), default="common")  # common, rare, epic, legendary
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    user_achievements: Mapped[List["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="achievement", cascade="all, delete-orphan"
    )


class UserAchievement(Base):
    """用户成就"""
    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    achievement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False
    )
    
    # 达成信息
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    progress_value: Mapped[int] = mapped_column(Integer, default=0)  # 当前进度值
    is_unlocked: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    achievement: Mapped["Achievement"] = relationship(
        "Achievement", back_populates="user_achievements"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
        Index("idx_ua_user", "user_id"),
        Index("idx_ua_achievement", "achievement_id"),
    )


# ========================================
# 学习统计
# ========================================

class LearningStats(Base):
    """学习统计汇总（按天）"""
    __tablename__ = "learning_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # 学习统计
    total_study_time: Mapped[int] = mapped_column(Integer, default=0)  # 秒
    session_count: Mapped[int] = mapped_column(Integer, default=0)
    activity_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # 知识点统计
    knowledge_points_studied: Mapped[int] = mapped_column(Integer, default=0)
    knowledge_points_mastered: Mapped[int] = mapped_column(Integer, default=0)
    
    # 练习统计
    exercises_attempted: Mapped[int] = mapped_column(Integer, default=0)
    exercises_correct: Mapped[int] = mapped_column(Integer, default=0)
    average_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # 成就统计
    achievements_unlocked: Mapped[int] = mapped_column(Integer, default=0)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_user_stats_date"),
        Index("idx_ls_user", "user_id"),
        Index("idx_ls_date", "date"),
    )
