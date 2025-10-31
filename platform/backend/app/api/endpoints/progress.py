"""
学习进度API端点
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.services import ProgressService
from app.models.user import User
from app.models.progress import ProgressStatus
from loguru import logger

router = APIRouter()


# ========================================
# Pydantic Schemas
# ========================================

class EnrollBookRequest(BaseModel):
    """注册学习书籍请求"""
    book_id: int


class UpdateCaseProgressRequest(BaseModel):
    """更新案例进度请求"""
    user_progress_id: int
    case_id: int
    status: str  # "not_started", "in_progress", "completed"
    score: Optional[float] = None
    time_spent: Optional[int] = None


class ProgressResponse(BaseModel):
    """进度响应"""
    book_id: int
    book_title: str
    book_slug: str
    progress_percentage: float
    chapters_completed: int
    chapters_total: int
    cases_completed: int
    cases_total: int
    enrollment_date: Optional[str]
    last_accessed: Optional[str]


class UserDashboardResponse(BaseModel):
    """用户仪表盘响应"""
    user_info: dict
    statistics: dict
    enrolled_courses: list
    recent_activities: list


# ========================================
# API Endpoints
# ========================================

@router.post("/enroll/{book_id}", status_code=status.HTTP_201_CREATED)
async def enroll_book(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    注册学习书籍
    
    - **book_id**: 书籍ID
    """
    logger.info(f"📚 用户 {current_user.id} 注册学习书籍 {book_id}")
    
    try:
        progress = await ProgressService.create_or_update_book_progress(
            db=db,
            user_id=current_user.id,
            book_id=book_id
        )
        
        logger.info(f"✅ 注册成功: progress_id={progress.id}")
        
        return {
            "message": "注册学习成功",
            "progress_id": progress.id,
            "book_id": book_id
        }
    except Exception as e:
        logger.error(f"❌ 注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册学习失败: {str(e)}"
        )


@router.get("/my-progress")
async def get_my_progress(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的所有学习进度
    """
    logger.info(f"📊 获取用户 {current_user.id} 的学习进度")
    
    progress_list = await ProgressService.get_user_all_progress(
        db=db,
        user_id=current_user.id
    )
    
    return {
        "total": len(progress_list),
        "items": progress_list
    }


@router.get("/books/{book_id}")
async def get_book_progress(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户在特定书籍的学习进度
    
    - **book_id**: 书籍ID
    """
    logger.info(f"📖 获取用户 {current_user.id} 在书籍 {book_id} 的进度")
    
    progress = await ProgressService.get_user_book_progress(
        db=db,
        user_id=current_user.id,
        book_id=book_id
    )
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到学习进度，请先注册学习该课程"
        )
    
    return {
        "id": progress.id,
        "user_id": progress.user_id,
        "book_id": progress.book_id,
        "percentage": progress.percentage,
        "chapters_completed": progress.chapters_completed,
        "chapters_total": progress.chapters_total,
        "cases_completed": progress.cases_completed,
        "cases_total": progress.cases_total,
        "total_time_spent": progress.total_time_spent,
        "enrollment_date": progress.enrollment_date.isoformat() if progress.enrollment_date else None,
        "last_accessed": progress.last_accessed.isoformat() if progress.last_accessed else None
    }


@router.post("/cases/{case_id}/update")
async def update_case_progress(
    case_id: int,
    status_value: str,
    score: Optional[float] = None,
    time_spent: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新案例学习进度
    
    - **case_id**: 案例ID
    - **status_value**: 状态（not_started/in_progress/completed）
    - **score**: 得分（0-100）
    - **time_spent**: 学习时长（秒）
    """
    logger.info(f"📝 更新用户 {current_user.id} 案例 {case_id} 进度")
    
    # 获取或创建书籍进度
    # 这里需要先查询case所属的book
    from app.models.book import Case
    from sqlalchemy import select
    
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="案例不存在"
        )
    
    # 获取用户进度
    user_progress = await ProgressService.get_user_book_progress(
        db=db,
        user_id=current_user.id,
        book_id=case.book_id
    )
    
    if not user_progress:
        # 自动注册学习
        user_progress = await ProgressService.create_or_update_book_progress(
            db=db,
            user_id=current_user.id,
            book_id=case.book_id
        )
    
    # 转换状态
    try:
        progress_status = ProgressStatus(status_value)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的状态值: {status_value}"
        )
    
    # 更新案例进度
    case_progress = await ProgressService.update_case_progress(
        db=db,
        user_progress_id=user_progress.id,
        case_id=case_id,
        status=progress_status,
        score=score,
        time_spent=time_spent
    )
    
    # 更新书籍统计
    await ProgressService.update_book_stats(db, user_progress, case.book_id)
    
    logger.info(f"✅ 案例进度更新成功")
    
    return {
        "message": "进度更新成功",
        "case_progress_id": case_progress.id,
        "status": case_progress.status.value,
        "score": case_progress.exercise_score
    }


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户仪表盘数据
    """
    logger.info(f"📊 获取用户 {current_user.id} 仪表盘数据")
    
    # 获取所有进度
    progress_list = await ProgressService.get_user_all_progress(
        db=db,
        user_id=current_user.id
    )
    
    # 计算统计数据
    total_enrolled = len(progress_list)
    total_completed = sum(1 for p in progress_list if p["progress_percentage"] >= 100)
    total_cases_completed = sum(p["cases_completed"] for p in progress_list)
    
    return {
        "user_info": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name
        },
        "statistics": {
            "enrolled_courses": total_enrolled,
            "completed_courses": total_completed,
            "total_cases_completed": total_cases_completed,
            "avg_progress": sum(p["progress_percentage"] for p in progress_list) / total_enrolled if total_enrolled > 0 else 0
        },
        "enrolled_courses": progress_list
    }
