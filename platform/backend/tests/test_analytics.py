"""
用户分析测试
"""

import pytest
import pytest_asyncio
import os
os.environ["TESTING"] = "1"

from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.models.book import Book, Chapter, Case
from app.models.progress import UserProgress, CaseProgress, ProgressStatus
from app.utils.analytics import UserAnalytics


@pytest_asyncio.fixture
async def db_session():
    """测试数据库会话"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = async_session()
    
    yield session
    
    await session.close()
    await engine.dispose()


@pytest_asyncio.fixture
async def test_user(db_session):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_book(db_session):
    """创建测试书籍和章节"""
    book = Book(
        slug="test-course",
        title="测试课程",
        description="测试描述"
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)
    
    # 创建章节
    chapter = Chapter(
        book_id=book.id,
        slug="chapter-1",
        title="第一章",
        order=1
    )
    db_session.add(chapter)
    await db_session.commit()
    await db_session.refresh(chapter)
    
    # 创建案例
    for i in range(5):
        case = Case(
            book_id=book.id,
            chapter_id=chapter.id,
            slug=f"case-{i+1}",
            title=f"案例{i+1}",
            order=i+1
        )
        db_session.add(case)
    
    await db_session.commit()
    return book


@pytest_asyncio.fixture
async def test_progress(db_session, test_user, test_book):
    """创建测试进度数据"""
    # 创建用户进度
    user_progress = UserProgress(
        user_id=test_user.id,
        book_id=test_book.id,
        total_time_spent=7200,  # 7200秒 = 120分钟
        enrollment_date=datetime.now(timezone.utc)
    )
    db_session.add(user_progress)
    await db_session.commit()
    
    # 创建案例进度
    from sqlalchemy import select
    from app.models.book import Case
    
    result = await db_session.execute(select(Case))
    cases = result.scalars().all()
    
    for i, case in enumerate(cases[:3]):  # 完成3个案例
        case_progress = CaseProgress(
            user_progress_id=user_progress.id,
            case_id=case.id,
            status="completed",
            score=85.0 + i * 5,  # 85, 90, 95
            attempts=1,
            completed_at=datetime.now(timezone.utc) - timedelta(days=i),
            last_accessed=datetime.now(timezone.utc) - timedelta(days=i)
        )
        db_session.add(case_progress)
    
    await db_session.commit()
    return user_progress


@pytest.mark.asyncio
async def test_get_user_learning_stats(db_session, test_user, test_progress):
    """测试获取用户学习统计"""
    stats = await UserAnalytics.get_user_learning_stats(db_session, test_user.id, 30)
    
    assert stats["user_id"] == test_user.id
    assert stats["total_learning_minutes"] == 120
    assert stats["completed_cases"] == 3
    assert stats["average_score"] > 0
    assert stats["enrolled_courses"] == 1


@pytest.mark.asyncio
async def test_get_learning_trend(db_session, test_user, test_progress):
    """测试获取学习趋势"""
    trend = await UserAnalytics.get_learning_trend(db_session, test_user.id, 7)
    
    assert len(trend) == 7
    assert all("date" in item for item in trend)
    assert all("cases_completed" in item for item in trend)
    assert all("study_minutes" in item for item in trend)


@pytest.mark.asyncio
async def test_get_popular_courses(db_session, test_user, test_progress):
    """测试获取热门课程"""
    courses = await UserAnalytics.get_popular_courses(db_session, limit=10)
    
    assert len(courses) >= 1
    assert all("book_id" in course for course in courses)
    assert all("title" in course for course in courses)
    assert all("enrollments" in course for course in courses)


@pytest.mark.asyncio
async def test_get_user_ranking(db_session, test_user, test_progress):
    """测试获取用户排名"""
    ranking = await UserAnalytics.get_user_ranking(db_session, test_user.id, "score")
    
    assert ranking["user_id"] == test_user.id
    assert ranking["rank"] >= 0
    assert "percentile" in ranking
    assert ranking["metric"] == "average_score"


@pytest.mark.asyncio
async def test_get_learning_insights(db_session, test_user, test_progress):
    """测试获取学习洞察"""
    insights = await UserAnalytics.get_learning_insights(db_session, test_user.id)
    
    assert "total_cases" in insights
    assert "completed_cases" in insights
    assert "insights" in insights
    assert isinstance(insights["insights"], list)
