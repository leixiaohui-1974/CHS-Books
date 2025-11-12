"""
数据库模型 - 独立Textbook服务器
简化版，仅包含必要的Book, Chapter, Case模型
"""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, Float, Boolean, JSON, ForeignKey
from typing import Optional, List
from datetime import datetime


class Base(AsyncAttrs, DeclarativeBase):
    """异步Base类"""
    pass


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), default="beginner")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    is_free: Mapped[bool] = mapped_column(Boolean, default=True)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_hours: Mapped[int] = mapped_column(Integer, default=0)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # 关系
    chapters: Mapped[List["Chapter"]] = relationship(back_populates="book", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Book {self.slug}>"


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    slug: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(200))
    order: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 关系
    book: Mapped["Book"] = relationship(back_populates="chapters")
    cases: Mapped[List["Case"]] = relationship(back_populates="chapter", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chapter {self.slug}>"


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id"), index=True)
    slug: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(200))
    order: Mapped[int] = mapped_column(Integer, default=0)
    difficulty: Mapped[str] = mapped_column(String(20), default="beginner")
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=30)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    starter_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    solution_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # 关系
    chapter: Mapped["Chapter"] = relationship(back_populates="cases")

    def __repr__(self):
        return f"<Case {self.slug}>"
