"""
学习进度服务
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone

from app.models.progress import UserProgress, ChapterProgress, CaseProgress, ProgressStatus
from app.models.book import Book, Chapter, Case


class ProgressService:
    """学习进度管理服务"""

    @staticmethod
    async def get_user_book_progress(
        db: AsyncSession,
        user_id: int,
        book_id: int
    ) -> Optional[UserProgress]:
        """
        获取用户的书籍学习进度
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            book_id: 书籍ID
            
        Returns:
            用户进度对象，如果不存在则返回None
        """
        result = await db.execute(
            select(UserProgress).where(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.book_id == book_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_or_update_book_progress(
        db: AsyncSession,
        user_id: int,
        book_id: int
    ) -> UserProgress:
        """
        创建或更新书籍学习进度（注册学习）
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            book_id: 书籍ID
            
        Returns:
            进度对象
        """
        # 查找现有进度
        progress = await ProgressService.get_user_book_progress(db, user_id, book_id)
        
        if progress:
            # 更新访问时间
            progress.last_accessed = datetime.now(timezone.utc)
        else:
            # 创建新进度
            progress = UserProgress(
                user_id=user_id,
                book_id=book_id
            )
            db.add(progress)
        
        await db.commit()
        await db.refresh(progress)
        return progress

    @staticmethod
    async def update_book_stats(
        db: AsyncSession,
        user_progress: UserProgress,
        book_id: int
    ) -> None:
        """更新书籍统计信息"""
        # 统计完成的章节数和案例数
        result = await db.execute(
            select(ChapterProgress).where(
                ChapterProgress.user_progress_id == user_progress.id
            )
        )
        chapter_progresses = result.scalars().all()
        
        completed_chapters = sum(
            1 for cp in chapter_progresses 
            if cp.status == ProgressStatus.COMPLETED
        )
        
        result = await db.execute(
            select(CaseProgress).where(
                CaseProgress.user_progress_id == user_progress.id
            )
        )
        case_progresses = result.scalars().all()
        
        completed_cases = sum(
            1 for cp in case_progresses 
            if cp.status == ProgressStatus.COMPLETED
        )
        
        # 获取书籍总章节数和案例数
        book_result = await db.execute(
            select(Book).where(Book.id == book_id)
        )
        book = book_result.scalar_one()
        
        user_progress.chapters_completed = completed_chapters
        user_progress.chapters_total = book.total_chapters or 0
        user_progress.cases_completed = completed_cases
        user_progress.cases_total = book.total_cases or 0
        
        # 计算完成百分比
        if user_progress.cases_total > 0:
            user_progress.percentage = (completed_cases / user_progress.cases_total) * 100
        else:
            user_progress.percentage = 0.0
        
        await db.commit()

    @staticmethod
    async def get_or_create_chapter_progress(
        db: AsyncSession,
        user_progress_id: int,
        chapter_id: int
    ) -> ChapterProgress:
        """获取或创建章节进度"""
        result = await db.execute(
            select(ChapterProgress).where(
                and_(
                    ChapterProgress.user_progress_id == user_progress_id,
                    ChapterProgress.chapter_id == chapter_id
                )
            )
        )
        progress = result.scalar_one_or_none()
        
        if not progress:
            progress = ChapterProgress(
                user_progress_id=user_progress_id,
                chapter_id=chapter_id
            )
            db.add(progress)
            await db.commit()
            await db.refresh(progress)
        
        return progress

    @staticmethod
    async def update_chapter_progress(
        db: AsyncSession,
        user_progress_id: int,
        chapter_id: int,
        status: ProgressStatus
    ) -> ChapterProgress:
        """更新章节学习进度"""
        progress = await ProgressService.get_or_create_chapter_progress(
            db, user_progress_id, chapter_id
        )
        
        progress.status = status
        if status == ProgressStatus.IN_PROGRESS and not progress.started_at:
            progress.started_at = datetime.now(timezone.utc)
        elif status == ProgressStatus.COMPLETED and not progress.completed_at:
            progress.completed_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(progress)
        return progress

    @staticmethod
    async def get_or_create_case_progress(
        db: AsyncSession,
        user_progress_id: int,
        case_id: int
    ) -> CaseProgress:
        """获取或创建案例进度"""
        result = await db.execute(
            select(CaseProgress).where(
                and_(
                    CaseProgress.user_progress_id == user_progress_id,
                    CaseProgress.case_id == case_id
                )
            )
        )
        progress = result.scalar_one_or_none()
        
        if not progress:
            progress = CaseProgress(
                user_progress_id=user_progress_id,
                case_id=case_id
            )
            db.add(progress)
            await db.commit()
            await db.refresh(progress)
        
        return progress

    @staticmethod
    async def update_case_progress(
        db: AsyncSession,
        user_progress_id: int,
        case_id: int,
        status: ProgressStatus,
        score: Optional[float] = None,
        time_spent: Optional[int] = None
    ) -> CaseProgress:
        """
        更新案例学习进度
        
        Args:
            db: 数据库会话
            user_progress_id: 用户进度ID
            case_id: 案例ID
            status: 进度状态
            score: 得分
            time_spent: 花费时间（秒）
            
        Returns:
            更新后的进度对象
        """
        progress = await ProgressService.get_or_create_case_progress(
            db, user_progress_id, case_id
        )
        
        progress.status = status
        if status == ProgressStatus.IN_PROGRESS and not progress.started_at:
            progress.started_at = datetime.now(timezone.utc)
        elif status == ProgressStatus.COMPLETED and not progress.completed_at:
            progress.completed_at = datetime.now(timezone.utc)
        
        if score is not None:
            progress.exercise_score = score
        if time_spent is not None:
            progress.time_spent += time_spent
        
        await db.commit()
        await db.refresh(progress)
        return progress

    @staticmethod
    async def get_user_all_progress(
        db: AsyncSession,
        user_id: int
    ) -> List[dict]:
        """
        获取用户所有课程的学习进度
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            进度列表
        """
        result = await db.execute(
            select(UserProgress)
            .where(UserProgress.user_id == user_id)
            .order_by(UserProgress.last_accessed.desc())
        )
        progresses = result.scalars().all()
        
        progress_list = []
        for progress in progresses:
            # 获取书籍信息
            book_result = await db.execute(
                select(Book).where(Book.id == progress.book_id)
            )
            book = book_result.scalar_one_or_none()
            
            if book:
                progress_list.append({
                    "book_id": book.id,
                    "book_title": book.title,
                    "book_slug": book.slug,
                    "progress_percentage": round(progress.percentage, 1),
                    "chapters_completed": progress.chapters_completed,
                    "chapters_total": progress.chapters_total,
                    "cases_completed": progress.cases_completed,
                    "cases_total": progress.cases_total,
                    "enrollment_date": progress.enrollment_date.isoformat() if progress.enrollment_date else None,
                    "last_accessed": progress.last_accessed.isoformat() if progress.last_accessed else None
                })
        
        return progress_list
