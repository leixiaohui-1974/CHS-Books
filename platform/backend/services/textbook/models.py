#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教材数据模型
定义教材章节、内容、元数据的数据结构
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Float, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

Base = declarative_base()


def generate_uuid():
    """生成UUID"""
    return str(uuid.uuid4())


class DifficultyLevel(str, enum.Enum):
    """难度等级"""
    BEGINNER = "初级"
    INTERMEDIATE = "中级"
    ADVANCED = "高级"
    EXPERT = "专家"


class ContentType(str, enum.Enum):
    """内容类型"""
    TEXT = "文本"
    CODE = "代码"
    FORMULA = "公式"
    IMAGE = "图片"
    TABLE = "表格"


class Textbook(Base):
    """教材表"""
    __tablename__ = "textbooks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False, index=True)
    subtitle = Column(String(200))
    author = Column(String(100))
    version = Column(String(20), default="1.0")
    
    description = Column(Text)  # 教材简介
    target_audience = Column(String(200))  # 目标受众
    prerequisites = Column(JSON)  # 前置知识列表
    
    # 元数据
    total_chapters = Column(Integer, default=0)
    total_words = Column(Integer, default=0)
    estimated_hours = Column(Integer)  # 预计学习时长（小时）
    
    # 状态
    is_published = Column(Integer, default=1)  # 1:已发布 0:草稿
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    chapters = relationship("TextbookChapter", back_populates="textbook", cascade="all, delete-orphan")


class TextbookChapter(Base):
    """教材章节表"""
    __tablename__ = "textbook_chapters"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    textbook_id = Column(String(36), ForeignKey("textbooks.id"), nullable=False, index=True)
    
    # 章节信息
    chapter_number = Column(String(20), nullable=False)  # 章节号，如 "1.2.3"
    title = Column(String(300), nullable=False, index=True)
    level = Column(Integer, nullable=False)  # 层级: 1(章), 2(节), 3(小节), 4(子小节)
    order_num = Column(Integer, nullable=False)  # 排序序号
    
    # 章节层级关系
    parent_id = Column(String(36), ForeignKey("textbook_chapters.id"), nullable=True)
    
    # 内容
    content = Column(Text)  # Markdown格式的内容
    content_html = Column(Text)  # HTML格式的内容（预渲染）
    summary = Column(Text)  # 章节摘要
    
    # 教学属性
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    estimated_minutes = Column(Integer)  # 预计学习时长（分钟）
    learning_objectives = Column(JSON)  # 学习目标列表
    
    # 知识关联
    keywords = Column(JSON)  # 关键词列表
    concepts = Column(JSON)  # 核心概念列表
    prerequisites = Column(JSON)  # 前置知识点ID列表
    
    # 元数据
    word_count = Column(Integer, default=0)
    has_code = Column(Integer, default=0)  # 是否包含代码示例
    has_formula = Column(Integer, default=0)  # 是否包含公式
    has_image = Column(Integer, default=0)  # 是否包含图片
    
    # 向量数据库ID
    vector_ids = Column(JSON)  # 在向量库中的文档ID列表
    
    # 统计信息
    view_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)  # 完成学习的人数
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    textbook = relationship("Textbook", back_populates="chapters")
    parent = relationship("TextbookChapter", remote_side=[id], backref="children")
    case_mappings = relationship("ChapterCaseMapping", back_populates="chapter")
    knowledge_mappings = relationship("ChapterKnowledgeMapping", back_populates="chapter")


class ChapterCaseMapping(Base):
    """章节-案例关联表"""
    __tablename__ = "chapter_case_mappings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(String(36), ForeignKey("textbook_chapters.id"), nullable=False, index=True)
    case_id = Column(String(100), nullable=False, index=True)  # 案例ID
    
    # 关联属性
    relation_type = Column(String(20), default="practice")  # theory/practice/extension/comparison
    relevance_score = Column(Float, default=0.8)  # 关联度 0-1
    description = Column(Text)  # 关联说明
    order_num = Column(Integer, default=0)  # 推荐顺序
    
    # 是否自动生成
    is_auto_generated = Column(Integer, default=0)  # 0:手动 1:自动
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    chapter = relationship("TextbookChapter", back_populates="case_mappings")


class ChapterKnowledgeMapping(Base):
    """章节-知识库关联表"""
    __tablename__ = "chapter_knowledge_mappings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(String(36), ForeignKey("textbook_chapters.id"), nullable=False, index=True)
    knowledge_id = Column(String(36), nullable=False, index=True)  # 知识库条目ID
    
    # 关联属性
    is_auto_generated = Column(Integer, default=0)  # 0:手动 1:自动
    last_synced = Column(DateTime, default=datetime.utcnow)  # 最后同步时间
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    chapter = relationship("TextbookChapter", back_populates="knowledge_mappings")


class LearningProgress(Base):
    """学习进度表"""
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), nullable=False, index=True)  # 用户ID（预留）
    chapter_id = Column(String(36), ForeignKey("textbook_chapters.id"), nullable=False, index=True)
    
    # 进度信息
    status = Column(String(20), default="not_started")  # not_started/in_progress/completed
    progress_percent = Column(Float, default=0.0)  # 进度百分比 0-100
    
    # 学习时间
    time_spent = Column(Integer, default=0)  # 学习时长（秒）
    last_position = Column(String(100))  # 最后阅读位置（锚点）
    
    # 互动数据
    bookmark_count = Column(Integer, default=0)  # 书签数
    note_count = Column(Integer, default=0)  # 笔记数
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class LearningBookmark(Base):
    """学习书签表"""
    __tablename__ = "learning_bookmarks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), nullable=False, index=True)
    chapter_id = Column(String(36), ForeignKey("textbook_chapters.id"), nullable=False, index=True)
    
    title = Column(String(200))  # 书签标题
    position = Column(String(100))  # 位置（锚点）
    note = Column(Text)  # 备注
    
    created_at = Column(DateTime, default=datetime.utcnow)


class LearningNote(Base):
    """学习笔记表"""
    __tablename__ = "learning_notes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), nullable=False, index=True)
    chapter_id = Column(String(36), ForeignKey("textbook_chapters.id"), nullable=False, index=True)
    
    title = Column(String(200))
    content = Column(Text)  # 笔记内容（Markdown）
    position = Column(String(100))  # 关联位置
    tags = Column(JSON)  # 标签列表
    
    is_public = Column(Integer, default=0)  # 是否公开
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 用于存储章节中提取的代码示例
class CodeExample(Base):
    """代码示例表"""
    __tablename__ = "code_examples"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(String(36), ForeignKey("textbook_chapters.id"), nullable=False, index=True)
    
    title = Column(String(200))
    description = Column(Text)
    code = Column(Text, nullable=False)  # 代码内容
    language = Column(String(50), default="python")  # 编程语言
    
    is_runnable = Column(Integer, default=1)  # 是否可运行
    output_example = Column(Text)  # 示例输出
    
    order_num = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


