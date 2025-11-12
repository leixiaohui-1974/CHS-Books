"""
数据库模型定义
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List
from sqlalchemy import (
    Column, String, Text, Integer, DateTime, 
    ForeignKey, Enum, JSON, Date, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


def generate_uuid():
    """生成UUID"""
    return str(uuid.uuid4())


class AcademicLevel(str, PyEnum):
    """学术层级"""
    UNDERGRADUATE = "本科"
    MASTER = "硕士"
    DOCTORAL = "博士"
    GENERAL = "通用"


class SourceType(str, PyEnum):
    """来源类型"""
    TEXTBOOK = "教材"
    PAPER = "论文"
    STANDARD = "规范标准"
    MANUAL = "手册"
    COURSE = "课程资料"
    OTHER = "其他"


class StandardType(str, PyEnum):
    """规范类型"""
    NATIONAL = "国家标准"
    INDUSTRY = "行业标准"
    LOCAL = "地方标准"
    INTERNATIONAL = "国际标准"


class Category(Base):
    """知识分类表"""
    __tablename__ = "categories"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, index=True)
    parent_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    level = Column(Integer, default=0)
    description = Column(Text)
    order_num = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    parent = relationship("Category", remote_side=[id], backref="children")
    knowledge_entries = relationship("KnowledgeEntry", back_populates="category")


class KnowledgeEntry(Base):
    """知识条目表"""
    __tablename__ = "knowledge_entries"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=False)
    level = Column(Enum(AcademicLevel), default=AcademicLevel.GENERAL)
    source_type = Column(Enum(SourceType), default=SourceType.OTHER)
    source_name = Column(String(200))
    author = Column(String(200))
    
    keywords = Column(JSON)  # 关键词数组
    tags = Column(JSON)  # 标签数组
    
    # 向量数据库中的文档ID
    vector_ids = Column(JSON)  # 存储切块后在向量库中的ID列表
    
    # 统计信息
    view_count = Column(Integer, default=0)
    reference_count = Column(Integer, default=0)
    
    # 质量评分
    quality_score = Column(Float, default=0.0)
    
    # 审核状态
    is_approved = Column(Integer, default=0)  # 0:待审核, 1:已通过, 2:未通过
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    category = relationship("Category", back_populates="knowledge_entries")


class Standard(Base):
    """规范标准表"""
    __tablename__ = "standards"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    type = Column(Enum(StandardType), nullable=False)
    version = Column(String(20))
    publish_date = Column(Date)
    implement_date = Column(Date)
    
    abstract = Column(Text)
    content = Column(Text)
    
    category_id = Column(String(36), ForeignKey("categories.id"))
    
    # 文件信息
    file_path = Column(String(500))
    file_size = Column(Integer)  # 字节
    
    # 向量数据库中的文档ID
    vector_ids = Column(JSON)
    
    # 状态
    is_active = Column(Integer, default=1)  # 1:有效, 0:废止
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    
    is_active = Column(Integer, default=1)
    is_superuser = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)


class QueryLog(Base):
    """查询日志表"""
    __tablename__ = "query_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"))
    query = Column(Text, nullable=False)
    response = Column(Text)
    
    # 检索信息
    retrieved_docs = Column(JSON)  # 检索到的文档ID列表
    relevance_scores = Column(JSON)  # 相关性得分列表
    
    # 时间信息
    retrieval_time = Column(Float)  # 检索耗时(秒)
    generation_time = Column(Float)  # 生成耗时(秒)
    
    # 用户反馈
    is_helpful = Column(Integer)  # 1:有帮助, 0:无帮助, null:未评价
    feedback = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
