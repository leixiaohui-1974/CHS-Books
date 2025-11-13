"""
练习题系统数据模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlalchemy import (
    Integer, String, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class QuestionType(str, Enum):
    """题目类型"""
    SINGLE_CHOICE = "single_choice"  # 单选题
    MULTIPLE_CHOICE = "multiple_choice"  # 多选题
    TRUE_FALSE = "true_false"  # 判断题
    FILL_BLANK = "fill_blank"  # 填空题
    SHORT_ANSWER = "short_answer"  # 简答题
    CODE = "code"  # 编程题
    CALCULATION = "calculation"  # 计算题


class QuestionDifficulty(str, Enum):
    """题目难度"""
    EASY = "easy"  # 简单
    MEDIUM = "medium"  # 中等
    HARD = "hard"  # 困难
    EXPERT = "expert"  # 专家


class ExerciseStatus(str, Enum):
    """练习状态"""
    NOT_STARTED = "not_started"  # 未开始
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    PAUSED = "paused"  # 已暂停


class SubmissionStatus(str, Enum):
    """提交状态"""
    PENDING = "pending"  # 待判题
    JUDGING = "judging"  # 判题中
    ACCEPTED = "accepted"  # 通过
    WRONG_ANSWER = "wrong_answer"  # 答案错误
    PARTIALLY_CORRECT = "partially_correct"  # 部分正确
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"  # 超时
    RUNTIME_ERROR = "runtime_error"  # 运行错误
    COMPILE_ERROR = "compile_error"  # 编译错误


# ========================================
# 题目相关
# ========================================

class Question(Base):
    """题目"""
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # 题目信息
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # 题目内容（支持Markdown）
    question_type: Mapped[QuestionType] = mapped_column(String(30), nullable=False)
    difficulty: Mapped[QuestionDifficulty] = mapped_column(String(20), nullable=False)
    
    # 关联
    knowledge_point_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_points.id", ondelete="SET NULL"), nullable=True
    )
    chapter_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True
    )
    subject_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True
    )
    
    # 题目选项和答案
    options: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # 选择题选项
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)  # 正确答案
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 答案解析
    
    # 题目配置
    score: Mapped[float] = mapped_column(Float, default=1.0)  # 分值
    time_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 时间限制（秒）
    
    # 题目标签
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)  # 标签列表
    
    # 统计信息
    submit_count: Mapped[int] = mapped_column(Integer, default=0)  # 提交次数
    correct_count: Mapped[int] = mapped_column(Integer, default=0)  # 正确次数
    accuracy_rate: Mapped[float] = mapped_column(Float, default=0.0)  # 正确率
    average_time: Mapped[float] = mapped_column(Float, default=0.0)  # 平均用时（秒）
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 创建者
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    submissions: Mapped[List["Submission"]] = relationship(
        "Submission", back_populates="question", cascade="all, delete-orphan"
    )
    wrong_records: Mapped[List["WrongQuestion"]] = relationship(
        "WrongQuestion", back_populates="question", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_question_type", "question_type"),
        Index("idx_question_difficulty", "difficulty"),
        Index("idx_question_kp", "knowledge_point_id"),
        Index("idx_question_chapter", "chapter_id"),
        Index("idx_question_subject", "subject_id"),
    )


class QuestionSet(Base):
    """题目集合/试卷"""
    __tablename__ = "question_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # 题集信息
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 题集类型
    set_type: Mapped[str] = mapped_column(String(30), default="practice")  # practice, exam, homework
    
    # 关联
    subject_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True
    )
    chapter_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True
    )
    
    # 题目列表
    question_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False)  # 题目ID列表（有序）
    
    # 题集配置
    total_score: Mapped[float] = mapped_column(Float, default=100.0)  # 总分
    pass_score: Mapped[float] = mapped_column(Float, default=60.0)  # 及格分
    time_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 时间限制（分钟）
    
    # 开放设置
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 统计
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)  # 参与次数
    average_score: Mapped[float] = mapped_column(Float, default=0.0)  # 平均分
    
    # 创建者
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    exercises: Mapped[List["Exercise"]] = relationship(
        "Exercise", back_populates="question_set", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_qset_type", "set_type"),
        Index("idx_qset_subject", "subject_id"),
        Index("idx_qset_chapter", "chapter_id"),
    )


# ========================================
# 用户练习记录
# ========================================

class Exercise(Base):
    """用户练习记录"""
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    question_set_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("question_sets.id", ondelete="SET NULL"), nullable=True
    )
    
    # 练习信息
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    exercise_type: Mapped[str] = mapped_column(String(30), default="practice")
    
    # 练习状态
    status: Mapped[ExerciseStatus] = mapped_column(String(20), default=ExerciseStatus.NOT_STARTED)
    
    # 题目和答案
    question_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False)
    answers: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # {question_id: answer}
    
    # 时间
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    time_spent: Mapped[int] = mapped_column(Integer, default=0)  # 用时（秒）
    
    # 成绩
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    total_score: Mapped[float] = mapped_column(Float, default=100.0)
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)  # 正确率
    
    # 详细结果
    result_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    question_set: Mapped[Optional["QuestionSet"]] = relationship("QuestionSet", back_populates="exercises")

    __table_args__ = (
        Index("idx_exercise_user", "user_id"),
        Index("idx_exercise_qset", "question_set_id"),
        Index("idx_exercise_status", "status"),
    )


class Submission(Base):
    """单题提交记录"""
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("exercises.id", ondelete="SET NULL"), nullable=True
    )
    
    # 提交内容
    answer: Mapped[str] = mapped_column(Text, nullable=False)  # 用户答案
    code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 代码（如果是编程题）
    
    # 判题结果
    status: Mapped[SubmissionStatus] = mapped_column(String(30), default=SubmissionStatus.PENDING)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # 判题详情
    judge_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 时间统计
    time_spent: Mapped[int] = mapped_column(Integer, default=0)  # 用时（秒）
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    judged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    question: Mapped["Question"] = relationship("Question", back_populates="submissions")

    __table_args__ = (
        Index("idx_submission_user", "user_id"),
        Index("idx_submission_question", "question_id"),
        Index("idx_submission_exercise", "exercise_id"),
        Index("idx_submission_status", "status"),
    )


class WrongQuestion(Base):
    """错题本"""
    __tablename__ = "wrong_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    
    # 错题信息
    wrong_count: Mapped[int] = mapped_column(Integer, default=1)  # 错误次数
    correct_count: Mapped[int] = mapped_column(Integer, default=0)  # 后续正确次数
    
    # 用户答案记录
    wrong_answers: Mapped[List[str]] = mapped_column(JSON, default=list)  # 历史错误答案
    
    # 掌握状态
    is_mastered: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否已掌握
    mastered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 笔记
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 用户笔记
    
    # 时间
    first_wrong_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_wrong_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_review_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    question: Mapped["Question"] = relationship("Question", back_populates="wrong_records")

    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_user_wrong_question"),
        Index("idx_wrong_user", "user_id"),
        Index("idx_wrong_question", "question_id"),
        Index("idx_wrong_mastered", "is_mastered"),
    )


# ========================================
# 学习资源
# ========================================

class LearningResource(Base):
    """学习资源"""
    __tablename__ = "learning_resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # 资源信息
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resource_type: Mapped[str] = mapped_column(String(30), nullable=False)  # video, document, link, file
    
    # 资源URL
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # 资源属性
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 时长（秒）
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 文件大小（字节）
    format: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 格式
    
    # 关联
    knowledge_point_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("knowledge_points.id", ondelete="SET NULL"), nullable=True
    )
    chapter_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True
    )
    subject_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True
    )
    
    # 标签
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # 统计
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_free: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 创建者
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    view_records: Mapped[List["ResourceView"]] = relationship(
        "ResourceView", back_populates="resource", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_resource_type", "resource_type"),
        Index("idx_resource_kp", "knowledge_point_id"),
        Index("idx_resource_chapter", "chapter_id"),
        Index("idx_resource_subject", "subject_id"),
    )


class ResourceView(Base):
    """资源查看记录"""
    __tablename__ = "resource_views"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    resource_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learning_resources.id", ondelete="CASCADE"), nullable=False
    )
    
    # 观看进度
    progress: Mapped[float] = mapped_column(Float, default=0.0)  # 进度百分比
    current_position: Mapped[int] = mapped_column(Integer, default=0)  # 当前位置（秒）
    
    # 时间统计
    view_time: Mapped[int] = mapped_column(Integer, default=0)  # 观看时长（秒）
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    first_viewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_viewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    resource: Mapped["LearningResource"] = relationship("LearningResource", back_populates="view_records")

    __table_args__ = (
        UniqueConstraint("user_id", "resource_id", name="uq_user_resource"),
        Index("idx_rv_user", "user_id"),
        Index("idx_rv_resource", "resource_id"),
    )
