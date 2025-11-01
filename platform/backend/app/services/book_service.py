"""
书籍服务 - 业务逻辑层
"""

from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.models.book import Book, Chapter, Case, BookStatus
from loguru import logger


class BookService:
    """书籍服务类"""
    
    @staticmethod
    async def get_books(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        difficulty: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Book], int]:
        """
        获取书籍列表（分页）
        
        Args:
            db: 数据库会话
            page: 页码
            page_size: 每页数量
            status: 状态筛选
            difficulty: 难度筛选
            tag: 标签筛选
            search: 搜索关键词
            
        Returns:
            (书籍列表, 总数)
        """
        # 构建查询
        query = select(Book)
        
        # 筛选条件
        if status:
            query = query.where(Book.status == status)
        
        if difficulty:
            query = query.where(Book.difficulty == difficulty)
        
        if tag:
            # PostgreSQL JSONB数组包含查询
            query = query.where(Book.tags.contains([tag]))
        
        if search:
            # 搜索标题和描述
            query = query.where(
                or_(
                    Book.title.ilike(f"%{search}%"),
                    Book.description.ilike(f"%{search}%")
                )
            )
        
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        books = result.scalars().all()
        
        logger.info(f"📚 查询书籍: page={page}, total={total}")
        return list(books), total
    
    @staticmethod
    async def get_book_by_id(
        db: AsyncSession,
        book_id: int
    ) -> Optional[Book]:
        """通过ID获取书籍"""
        result = await db.execute(
            select(Book).where(Book.id == book_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_book_by_slug(
        db: AsyncSession,
        slug: str
    ) -> Optional[Book]:
        """通过slug获取书籍"""
        result = await db.execute(
            select(Book).where(Book.slug == slug)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_book_chapters(
        db: AsyncSession,
        book_id: int
    ) -> List[Chapter]:
        """
        获取书籍的所有章节（含案例）
        
        Args:
            db: 数据库会话
            book_id: 书籍ID
            
        Returns:
            章节列表（按order排序）
        """
        result = await db.execute(
            select(Chapter)
            .where(Chapter.book_id == book_id)
            .options(selectinload(Chapter.cases))
            .order_by(Chapter.order)
        )
        chapters = result.scalars().all()
        
        logger.info(f"📑 查询章节: book_id={book_id}, count={len(chapters)}")
        return list(chapters)
    
    @staticmethod
    async def get_case_by_id(
        db: AsyncSession,
        case_id: int
    ) -> Optional[Case]:
        """通过ID获取案例"""
        result = await db.execute(
            select(Case).where(Case.id == case_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_book(
        db: AsyncSession,
        **kwargs
    ) -> Book:
        """
        创建书籍
        
        Args:
            db: 数据库会话
            **kwargs: 书籍字段
            
        Returns:
            创建的书籍对象
        """
        book = Book(**kwargs)
        db.add(book)
        await db.commit()
        await db.refresh(book)
        
        logger.info(f"✅ 创建书籍: {book.title}")
        return book
    
    @staticmethod
    async def create_chapter(
        db: AsyncSession,
        **kwargs
    ) -> Chapter:
        """创建章节"""
        chapter = Chapter(**kwargs)
        db.add(chapter)
        await db.commit()
        await db.refresh(chapter)
        
        logger.info(f"✅ 创建章节: {chapter.title}")
        return chapter
    
    @staticmethod
    async def create_case(
        db: AsyncSession,
        **kwargs
    ) -> Case:
        """创建案例"""
        case = Case(**kwargs)
        db.add(case)
        await db.commit()
        await db.refresh(case)
        
        logger.info(f"✅ 创建案例: {case.title}")
        return case
    
    @staticmethod
    async def update_book(
        db: AsyncSession,
        book_id: int,
        **kwargs
    ) -> Optional[Book]:
        """更新书籍信息"""
        book = await BookService.get_book_by_id(db, book_id)
        if not book:
            return None
        
        for key, value in kwargs.items():
            if hasattr(book, key):
                setattr(book, key, value)
        
        await db.commit()
        await db.refresh(book)
        
        logger.info(f"✅ 更新书籍: {book.title}")
        return book
