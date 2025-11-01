"""
学习进度服务测试
"""

import pytest
from app.services.progress_service import ProgressService
from app.services.book_service import BookService
from app.services.user_service import UserService
from app.models.book import BookStatus, DifficultyLevel
from app.models.progress import ProgressStatus


@pytest.mark.asyncio
async def test_create_book_progress(db_session):
    """测试创建书籍学习进度"""
    # 创建用户
    user = await UserService.create_user(
        db=db_session,
        email="student@example.com",
        username="student",
        password="password123"
    )
    
    # 创建书籍
    book = await BookService.create_book(
        db=db_session,
        slug="test-book",
        title="测试书籍",
        status=BookStatus.PUBLISHED,
        difficulty=DifficultyLevel.BEGINNER,
        price=299.0
    )
    
    # 创建学习进度（注册学习）
    progress = await ProgressService.create_or_update_book_progress(
        db=db_session,
        user_id=user.id,
        book_id=book.id
    )
    
    assert progress.id is not None
    assert progress.user_id == user.id
    assert progress.book_id == book.id
    assert progress.percentage == 0.0


@pytest.mark.asyncio
async def test_update_case_progress(db_session):
    """测试更新案例学习进度"""
    # 创建用户
    user = await UserService.create_user(
        db=db_session,
        email="student@example.com",
        username="student",
        password="password123"
    )
    
    # 创建书籍和章节
    book = await BookService.create_book(
        db=db_session,
        slug="test-book",
        title="测试书籍",
        status=BookStatus.PUBLISHED,
        difficulty=DifficultyLevel.BEGINNER,
        price=299.0
    )
    
    # 注册学习
    user_progress = await ProgressService.create_or_update_book_progress(
        db=db_session,
        user_id=user.id,
        book_id=book.id
    )
    
    chapter = await BookService.create_chapter(
        db=db_session,
        book_id=book.id,
        slug="chapter-1",
        order=1,
        title="第1章"
    )
    
    case = await BookService.create_case(
        db=db_session,
        book_id=book.id,
        chapter_id=chapter.id,
        slug="case-1",
        order=1,
        title="案例1",
        difficulty=DifficultyLevel.BEGINNER,
        has_tool=True
    )
    
    # 更新案例进度
    progress = await ProgressService.update_case_progress(
        db=db_session,
        user_progress_id=user_progress.id,
        case_id=case.id,
        status=ProgressStatus.COMPLETED,
        score=95.0,
        time_spent=300
    )
    
    assert progress.id is not None
    assert progress.user_progress_id == user_progress.id
    assert progress.case_id == case.id
    assert progress.status == ProgressStatus.COMPLETED
    assert progress.exercise_score == 95.0
    assert progress.time_spent == 300


@pytest.mark.asyncio
async def test_get_user_all_progress(db_session):
    """测试获取用户所有学习进度"""
    # 创建用户
    user = await UserService.create_user(
        db=db_session,
        email="student@example.com",
        username="student",
        password="password123"
    )
    
    # 创建两本书
    book1 = await BookService.create_book(
        db=db_session,
        slug="book-1",
        title="书籍1",
        status=BookStatus.PUBLISHED,
        difficulty=DifficultyLevel.BEGINNER,
        price=299.0
    )
    
    book2 = await BookService.create_book(
        db=db_session,
        slug="book-2",
        title="书籍2",
        status=BookStatus.PUBLISHED,
        difficulty=DifficultyLevel.BEGINNER,
        price=399.0
    )
    
    # 创建学习进度
    await ProgressService.create_or_update_book_progress(
        db=db_session,
        user_id=user.id,
        book_id=book1.id
    )
    
    await ProgressService.create_or_update_book_progress(
        db=db_session,
        user_id=user.id,
        book_id=book2.id
    )
    
    # 获取所有进度
    progress_list = await ProgressService.get_user_all_progress(
        db=db_session,
        user_id=user.id
    )
    
    assert len(progress_list) == 2
    assert progress_list[0]["book_title"] in ["书籍1", "书籍2"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
