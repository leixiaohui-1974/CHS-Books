"""
书籍相关API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.services import BookService
from loguru import logger

router = APIRouter()


# ========================================
# Pydantic Schemas
# ========================================

class BookResponse(BaseModel):
    """书籍响应"""
    id: int
    slug: str
    title: str
    subtitle: Optional[str]
    description: Optional[str]
    cover_image: Optional[str]
    authors: Optional[List[str]]
    version: str
    status: str
    difficulty: str
    is_free: bool
    price: float
    original_price: Optional[float]
    total_chapters: int
    total_cases: int
    estimated_hours: int
    enrollments: int
    avg_rating: float
    tags: Optional[List[str]]
    
    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    """书籍列表响应"""
    total: int
    items: List[BookResponse]


# ========================================
# API Endpoints
# ========================================

@router.get("", response_model=BookListResponse)
async def get_books(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    difficulty: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取书籍列表
    
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量
    - **status**: 筛选状态（draft/published/archived）
    - **difficulty**: 筛选难度（beginner/intermediate/advanced）
    - **tag**: 筛选标签
    - **search**: 搜索关键词（标题、描述）
    """
    logger.info(f"📚 获取书籍列表: page={page}, page_size={page_size}")
    
    # 使用服务层查询
    books, total = await BookService.get_books(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        difficulty=difficulty,
        tag=tag,
        search=search
    )
    
    # 转换为响应格式
    items = []
    for book in books:
        items.append({
            "id": book.id,
            "slug": book.slug,
            "title": book.title,
            "subtitle": book.subtitle,
            "description": book.description,
            "cover_image": book.cover_image,
            "authors": book.authors,
            "version": book.version,
            "status": book.status.value,
            "difficulty": book.difficulty.value,
            "is_free": book.is_free,
            "price": book.price,
            "original_price": book.original_price,
            "total_chapters": book.total_chapters,
            "total_cases": book.total_cases,
            "estimated_hours": book.estimated_hours,
            "enrollments": book.enrollments,
            "avg_rating": book.avg_rating,
            "tags": book.tags
        })
    
    return {
        "total": total,
        "items": items
    }


@router.get("/{book_id_or_slug}", response_model=BookResponse)
async def get_book(
    book_id_or_slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取单本书籍详情
    
    - **book_id_or_slug**: 书籍ID或slug
    """
    # TODO: 实现数据库查询
    
    logger.info(f"📖 获取书籍详情: {book_id_or_slug}")
    
    # 临时mock数据
    return {
        "id": 1,
        "slug": "water-system-control",
        "title": "水系统控制论",
        "subtitle": "基于水箱案例的控制理论入门",
        "description": "通过12个经典水箱案例系统讲解控制理论...",
        "cover_image": "/covers/book1.jpg",
        "authors": ["作者1"],
        "version": "1.0.0",
        "status": "published",
        "difficulty": "beginner",
        "is_free": False,
        "price": 299.0,
        "original_price": 399.0,
        "total_chapters": 6,
        "total_cases": 24,
        "estimated_hours": 192,
        "enrollments": 1523,
        "avg_rating": 4.8,
        "tags": ["控制理论", "水利工程"]
    }


@router.get("/{book_id}/chapters")
async def get_book_chapters(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取书籍的章节列表（树状结构）
    
    - **book_id**: 书籍ID
    """
    # TODO: 实现数据库查询，返回章节树
    
    logger.info(f"📑 获取书籍章节: book_id={book_id}")
    
    return {
        "book_id": book_id,
        "chapters": [
            {
                "id": 1,
                "order": 1,
                "title": "第1章：控制系统基础",
                "is_free": True,
                "estimated_minutes": 120,
                "cases": [
                    {
                        "id": 1,
                        "order": 1,
                        "title": "案例1：家庭水塔自动供水",
                        "difficulty": "beginner",
                        "estimated_minutes": 90,
                        "has_tool": True
                    }
                ]
            }
        ]
    }


@router.post("/{book_id}/enroll")
async def enroll_book(
    book_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    注册学习书籍（购买后或免费书籍）
    
    - **book_id**: 书籍ID
    - 需要认证
    """
    # TODO: 实现注册逻辑
    # 1. 检查用户是否已购买或是VIP
    # 2. 创建学习进度记录
    
    logger.info(f"✅ 用户注册书籍: user_id={current_user['id']}, book_id={book_id}")
    
    return {
        "message": "注册成功",
        "book_id": book_id
    }


@router.post("/{book_id}/rate")
async def rate_book(
    book_id: int,
    rating: float = Query(..., ge=1, le=5),
    comment: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    评价书籍
    
    - **book_id**: 书籍ID
    - **rating**: 评分（1-5）
    - **comment**: 评论内容（可选）
    - 需要认证
    """
    # TODO: 实现评价逻辑
    
    logger.info(f"⭐ 用户评价书籍: user_id={current_user['id']}, book_id={book_id}, rating={rating}")
    
    return {
        "message": "评价成功"
    }
