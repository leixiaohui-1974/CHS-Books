"""
知识库模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class KnowledgeBaseStatus(str, enum.Enum):
    """知识库状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROCESSING = "processing"


class DocumentType(str, enum.Enum):
    """文档类型"""
    TEXT = "text"
    PDF = "pdf"
    MARKDOWN = "markdown"
    HTML = "html"


class KnowledgeBase(Base):
    """知识库"""
    
    __tablename__ = "knowledge_bases"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 所有者
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # 配置
    embedding_model = Column(String(100), default="text-embedding-ada-002", nullable=False)
    chunk_size = Column(Integer, default=1000, nullable=False)
    chunk_overlap = Column(Integer, default=200, nullable=False)
    
    # 状态
    status = Column(SQLEnum(KnowledgeBaseStatus), default=KnowledgeBaseStatus.ACTIVE, nullable=False)
    
    # 统计
    document_count = Column(Integer, default=0, nullable=False)
    total_chunks = Column(Integer, default=0, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, name={self.name})>"


class Document(Base):
    """文档"""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    
    # 文档信息
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    doc_type = Column(SQLEnum(DocumentType), default=DocumentType.TEXT, nullable=False)
    
    # 文件信息
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # bytes
    file_hash = Column(String(64), nullable=True)  # SHA-256
    
    # 元数据
    meta_data = Column(JSON, nullable=True)
    
    # 统计
    chunk_count = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title})>"


class DocumentChunk(Base):
    """文档块（用于向量化）"""
    
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    # 块信息
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    
    # 向量信息
    vector_id = Column(String(100), nullable=True)  # 向量数据库中的ID
    embedding = Column(JSON, nullable=True)  # 可选：存储向量（如果不用外部向量数据库）
    
    # 相似度（查询时使用）
    similarity_score = Column(Float, nullable=True)
    
    # 元数据
    meta_data = Column(JSON, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, index={self.chunk_index})>"
