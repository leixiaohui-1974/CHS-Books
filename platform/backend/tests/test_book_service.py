"""
书籍服务测试
"""

import pytest
from app.services.book_service import BookService
from app.models.book import BookStatus, DifficultyLevel


@pytest.mark.asyncio
async def test_create_book(db_session):
    """测试创建书籍"""
    book = await BookService.create_book(
        db=db_session,
        slug="test-book",
        title="测试书籍",
        subtitle="这是一本测试书籍",
        description="测试描述",
        status=BookStatus.PUBLISHED,
        difficulty=DifficultyLevel.BEGINNER,
        price=299.0,
        tags=["测试", "教材"]
    )
    
    assert book.id is not None
    assert book.slug == "test-book"
    assert book.title == "测试书籍"
    assert book.status == BookStatus.PUBLISHED
    assert book.difficulty == DifficultyLevel.BEGINNER
    assert book.price == 299.0
    assert "测试" in book.tags


@pytest.mark.asyncio
async def test_get_books_pagination(db_session):
    """测试书籍分页查询"""
    # 创建多本书
    for i in range(5):
        await BookService.create_book(
            db=db_session,
            slug=f"book-{i}",
            title=f"书籍{i}",
            status=BookStatus.PUBLISHED,
            difficulty=DifficultyLevel.BEGINNER,
            price=299.0
        )
    
    # 第1页（2条）
    books, total = await BookService.get_books(
        db=db_session,
        page=1,
        page_size=2
    )
    assert total == 5
    assert len(books) == 2
    
    # 第2页（2条）
    books, total = await BookService.get_books(
        db=db_session,
        page=2,
        page_size=2
    )
    assert len(books) == 2


@pytest.mark.asyncio
async def test_get_book_by_slug(db_session):
    """测试通过slug查询书籍"""
    # 创建书籍
    await BookService.create_book(
        db=db_session,
        slug="water-control",
        title="水系统控制论",
        status=BookStatus.PUBLISHED,
        difficulty=DifficultyLevel.BEGINNER,
        price=299.0
    )
    
    # 查询
    book = await BookService.get_book_by_slug(db_session, "water-control")
    
    assert book is not None
    assert book.slug == "water-control"
    assert book.title == "水系统控制论"


@pytest.mark.asyncio
async def test_create_chapter_and_case(db_session):
    """测试创建章节和案例"""
    # 创建书籍
    book = await BookService.create_book(
        db=db_session,
        slug="test-book",
        title="测试书籍",
        status=BookStatus.PUBLISHED,
        difficulty=DifficultyLevel.BEGINNER,
        price=299.0
    )
    
    # 创建章节
    chapter = await BookService.create_chapter(
        db=db_session,
        book_id=book.id,
        slug="chapter-1",
        order=1,
        title="第1章：基础",
        is_free=True,
        estimated_minutes=120
    )
    
    assert chapter.id is not None
    assert chapter.book_id == book.id
    assert chapter.title == "第1章：基础"
    
    # 创建案例
    case = await BookService.create_case(
        db=db_session,
        book_id=book.id,
        chapter_id=chapter.id,
        slug="case-1",
        order=1,
        title="案例1：测试案例",
        difficulty=DifficultyLevel.BEGINNER,
        has_tool=True
    )
    
    assert case.id is not None
    assert case.chapter_id == chapter.id
    assert case.title == "案例1：测试案例"


@pytest.mark.asyncio
async def test_get_book_chapters(db_session):
    """测试获取书籍章节"""
    # 创建书籍
    book = await BookService.create_book(
        db=db_session,
        slug="test-book",
        title="测试书籍",
        status=BookStatus.PUBLISHED,
        difficulty=DifficultyLevel.BEGINNER,
        price=299.0
    )
    
    # 创建章节
    chapter1 = await BookService.create_chapter(
        db=db_session,
        book_id=book.id,
        slug="chapter-1",
        order=1,
        title="第1章"
    )
    
    chapter2 = await BookService.create_chapter(
        db=db_session,
        book_id=book.id,
        slug="chapter-2",
        order=2,
        title="第2章"
    )
    
    # 查询章节
    chapters = await BookService.get_book_chapters(db_session, book.id)
    
    assert len(chapters) == 2
    assert chapters[0].order == 1
    assert chapters[1].order == 2
