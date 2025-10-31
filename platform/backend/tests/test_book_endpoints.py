"""
书籍端点集成测试
"""

import os
os.environ["TESTING"] = "1"

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from main import app
from app.core.database import Base, get_db
from app.services.book_service import BookService
from app.models.book import BookStatus, DifficultyLevel


# 测试数据库配置
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    """创建测试数据库会话"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建会话工厂
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # 创建会话
    session = async_session()
    yield session
    
    # 清理
    await session.close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    """创建测试客户端"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_books(db_session):
    """创建示例书籍数据"""
    # 创建3本书
    books = []
    for i in range(3):
        book = await BookService.create_book(
            db=db_session,
            slug=f"test-book-{i}",
            title=f"测试书籍{i}",
            subtitle=f"这是测试书籍{i}的副标题",
            description=f"这是测试书籍{i}的描述",
            status=BookStatus.PUBLISHED,
            difficulty=DifficultyLevel.BEGINNER,
            price=299.0,
            tags=["测试", "教材"]
        )
        
        # 为每本书创建章节
        chapter = await BookService.create_chapter(
            db=db_session,
            book_id=book.id,
            slug=f"chapter-1",
            order=1,
            title="第1章：基础知识",
            is_free=True,
            estimated_minutes=120
        )
        
        # 为每个章节创建案例
        await BookService.create_case(
            db=db_session,
            book_id=book.id,
            chapter_id=chapter.id,
            slug="case-1",
            order=1,
            title="案例1：入门案例",
            difficulty=DifficultyLevel.BEGINNER,
            has_tool=True
        )
        
        books.append(book)
    
    return books


@pytest.mark.asyncio
async def test_get_books_list(client, sample_books):
    """测试获取书籍列表"""
    response = await client.get("/api/v1/books")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["items"][0]["title"] == "测试书籍0"


@pytest.mark.asyncio
async def test_get_books_pagination(client, sample_books):
    """测试书籍分页"""
    response = await client.get("/api/v1/books?page=1&page_size=2")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_book_by_id(client, sample_books):
    """测试通过ID获取书籍详情"""
    book_id = sample_books[0].id
    response = await client.get(f"/api/v1/books/{book_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == "测试书籍0"


@pytest.mark.asyncio
async def test_get_book_by_slug(client, sample_books):
    """测试通过slug获取书籍详情"""
    response = await client.get("/api/v1/books/test-book-1")
    
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "test-book-1"
    assert data["title"] == "测试书籍1"


@pytest.mark.asyncio
async def test_get_book_not_found(client, sample_books):
    """测试获取不存在的书籍"""
    response = await client.get("/api/v1/books/999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_book_chapters(client, sample_books):
    """测试获取书籍章节"""
    book_id = sample_books[0].id
    response = await client.get(f"/api/v1/books/{book_id}/chapters")
    
    assert response.status_code == 200
    data = response.json()
    assert data["book_id"] == book_id
    assert data["total_chapters"] == 1
    assert len(data["chapters"]) == 1
    assert data["chapters"][0]["title"] == "第1章：基础知识"
    assert len(data["chapters"][0]["cases"]) == 1


@pytest.mark.asyncio
async def test_search_books(client, sample_books):
    """测试搜索书籍"""
    response = await client.get("/api/v1/books?search=书籍1")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "测试书籍1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
