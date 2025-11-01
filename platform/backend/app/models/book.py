"""
书籍、章节、案例模型
"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class BookStatus(str, enum.Enum):
    """书籍状态"""
    DRAFT = "draft"              # 草稿
    PUBLISHED = "published"      # 已发布
    ARCHIVED = "archived"        # 已归档


class DifficultyLevel(str, enum.Enum):
    """难度级别"""
    BEGINNER = "beginner"           # 初级
    INTERMEDIATE = "intermediate"   # 中级
    ADVANCED = "advanced"           # 高级


class Book(Base):
    """书籍模型"""
    
    __tablename__ = "books"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    subtitle = Column(String(300), nullable=True)
    description = Column(Text, nullable=True)
    cover_image = Column(String(500), nullable=True)
    
    # 作者和版本
    authors = Column(JSON, nullable=True)  # ["作者1", "作者2"]
    version = Column(String(20), default="1.0.0", nullable=False)
    
    # 状态和难度
    status = Column(SQLEnum(BookStatus), default=BookStatus.DRAFT, nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.BEGINNER, nullable=False)
    
    # 定价信息
    is_free = Column(Boolean, default=False, nullable=False)
    price = Column(Float, default=0.0, nullable=False)
    original_price = Column(Float, nullable=True)
    discount_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # 试读配置
    trial_chapters = Column(JSON, nullable=True)  # [1, 2] 章节序号
    
    # 统计信息
    total_chapters = Column(Integer, default=0, nullable=False)
    total_cases = Column(Integer, default=0, nullable=False)
    estimated_hours = Column(Integer, default=0, nullable=False)
    enrollments = Column(Integer, default=0, nullable=False)
    avg_rating = Column(Float, default=0.0, nullable=False)
    completion_rate = Column(Float, default=0.0, nullable=False)
    
    # 标签
    tags = Column(JSON, nullable=True)  # ["控制理论", "水力学"]
    
    # 前置课程
    prerequisites = Column(JSON, nullable=True)  # [book_id1, book_id2]
    related_books = Column(JSON, nullable=True)  # [book_id1, book_id2]
    
    # 元数据
    github_path = Column(String(500), nullable=True)  # 在Git仓库中的路径
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    chapters = relationship("Chapter", back_populates="book", cascade="all, delete-orphan", order_by="Chapter.order")
    
    def __repr__(self):
        return f"<Book(id={self.id}, slug={self.slug}, title={self.title})>"


class Chapter(Base):
    """章节模型"""
    
    __tablename__ = "chapters"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    slug = Column(String(100), index=True, nullable=False)
    order = Column(Integer, nullable=False)  # 章节顺序
    
    # 标题和内容
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 是否免费
    is_free = Column(Boolean, default=False, nullable=False)
    
    # 学习目标
    learning_objectives = Column(JSON, nullable=True)  # ["目标1", "目标2"]
    
    # 预计学习时间
    estimated_minutes = Column(Integer, default=0, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    book = relationship("Book", back_populates="chapters")
    cases = relationship("Case", back_populates="chapter", cascade="all, delete-orphan", order_by="Case.order")
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, book_id={self.book_id}, title={self.title})>"


class Case(Base):
    """案例模型"""
    
    __tablename__ = "cases"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    slug = Column(String(100), index=True, nullable=False)
    order = Column(Integer, nullable=False)
    
    # 标题和描述
    title = Column(String(200), nullable=False)
    subtitle = Column(String(300), nullable=True)
    description = Column(Text, nullable=True)
    
    # 难度和时长
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.BEGINNER, nullable=False)
    estimated_minutes = Column(Integer, default=0, nullable=False)
    
    # 关键概念
    key_concepts = Column(JSON, nullable=True)  # ["概念1", "概念2"]
    
    # 工具配置
    has_tool = Column(Boolean, default=False, nullable=False)
    tool_config = Column(JSON, nullable=True)  # 工具配置的JSON
    
    # 代码信息
    script_path = Column(String(500), nullable=True)  # Python脚本路径
    entry_function = Column(String(100), nullable=True)  # 入口函数名
    github_url = Column(String(500), nullable=True)
    
    # 资源
    resources = Column(JSON, nullable=True)  # [{"type": "video", "url": "..."}]
    
    # 习题
    exercises = Column(JSON, nullable=True)  # 习题配置JSON
    
    # 统计
    total_runs = Column(Integer, default=0, nullable=False)
    avg_completion_time = Column(Integer, default=0, nullable=False)  # 平均完成时间（秒）
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    chapter = relationship("Chapter", back_populates="cases")
    executions = relationship("ToolExecution", back_populates="case", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Case(id={self.id}, chapter_id={self.chapter_id}, title={self.title})>"
