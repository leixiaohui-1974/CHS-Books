"""
学习追踪API端点
"""

from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.learning import (
    ActivityType, DifficultyLevel, MasteryLevel
)
from app.services.learning_service import LearningService
from app.services.learning_path_service import LearningPathService
from app.services.achievement_service import AchievementService


router = APIRouter()


# ========================================
# 请求/响应模型
# ========================================

class SubjectResponse(BaseModel):
    """学科响应"""
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    order: int


class ChapterResponse(BaseModel):
    """章节响应"""
    id: int
    subject_id: int
    name: str
    description: Optional[str]
    order: int


class KnowledgePointResponse(BaseModel):
    """知识点响应"""
    id: int
    chapter_id: int
    name: str
    description: Optional[str]
    difficulty: str
    video_url: Optional[str]
    reading_url: Optional[str]
    exercise_count: int
    order: int


class ProgressResponse(BaseModel):
    """学习进度响应"""
    id: int
    knowledge_point_id: int
    knowledge_point_name: str
    mastery_level: str
    mastery_score: float
    study_time: int
    practice_count: int
    correct_count: int
    wrong_count: int
    accuracy: float
    next_review_date: Optional[str]
    last_studied_at: Optional[str]


class UpdateProgressRequest(BaseModel):
    """更新进度请求"""
    knowledge_point_id: int = Field(..., description="知识点ID")
    is_correct: bool = Field(..., description="是否回答正确")
    time_spent: int = Field(0, description="花费时间（秒）")


class CreateActivityRequest(BaseModel):
    """创建活动请求"""
    activity_type: str = Field(..., description="活动类型")
    title: str = Field(..., description="标题")
    knowledge_point_id: Optional[int] = Field(None, description="知识点ID")
    description: Optional[str] = Field(None, description="描述")
    duration: int = Field(0, description="时长（秒）")
    score: Optional[float] = Field(None, description="分数")


class DailyGoalResponse(BaseModel):
    """每日目标响应"""
    id: int
    date: str
    target_study_time: int
    target_exercises: int
    target_knowledge_points: int
    actual_study_time: int
    actual_exercises: int
    actual_knowledge_points: int
    completion_percentage: float
    is_completed: bool


class CreateLearningPathRequest(BaseModel):
    """创建学习路径请求"""
    name: str = Field(..., description="路径名称")
    knowledge_point_ids: List[int] = Field(..., description="知识点ID列表")
    target_subject_id: Optional[int] = Field(None, description="目标学科ID")
    description: Optional[str] = Field(None, description="描述")
    difficulty: str = Field("intermediate", description="难度")


class GenerateAdaptivePathRequest(BaseModel):
    """生成自适应路径请求"""
    subject_id: int = Field(..., description="学科ID")
    target_difficulty: str = Field("intermediate", description="目标难度")


class AchievementResponse(BaseModel):
    """成就响应"""
    id: int
    name: str
    title: str
    description: str
    icon: Optional[str]
    type: str
    requirement_value: int
    points: int
    rarity: str
    is_unlocked: bool
    progress_value: int
    progress_percentage: float
    unlocked_at: Optional[str]


# ========================================
# 知识点相关端点
# ========================================

@router.get("/subjects", response_model=List[SubjectResponse])
async def get_subjects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取学科列表"""
    service = LearningService(db)
    subjects = await service.get_subjects()
    
    return [
        SubjectResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            icon=s.icon,
            color=s.color,
            order=s.order
        )
        for s in subjects
    ]


@router.get("/subjects/{subject_id}/chapters", response_model=List[ChapterResponse])
async def get_chapters(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取章节列表"""
    service = LearningService(db)
    chapters = await service.get_chapters(subject_id)
    
    return [
        ChapterResponse(
            id=c.id,
            subject_id=c.subject_id,
            name=c.name,
            description=c.description,
            order=c.order
        )
        for c in chapters
    ]


@router.get("/chapters/{chapter_id}/knowledge-points", response_model=List[KnowledgePointResponse])
async def get_knowledge_points(
    chapter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取知识点列表"""
    service = LearningService(db)
    kps = await service.get_knowledge_points(chapter_id)
    
    return [
        KnowledgePointResponse(
            id=kp.id,
            chapter_id=kp.chapter_id,
            name=kp.name,
            description=kp.description,
            difficulty=kp.difficulty.value,
            video_url=kp.video_url,
            reading_url=kp.reading_url,
            exercise_count=kp.exercise_count,
            order=kp.order
        )
        for kp in kps
    ]


# ========================================
# 学习进度相关端点
# ========================================

@router.get("/progress", response_model=List[ProgressResponse])
async def get_user_progress(
    knowledge_point_id: Optional[int] = Query(None, description="知识点ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户学习进度"""
    service = LearningService(db)
    progress_list = await service.get_user_progress(
        current_user.id,
        knowledge_point_id
    )
    
    return [
        ProgressResponse(
            id=p.id,
            knowledge_point_id=p.knowledge_point_id,
            knowledge_point_name=p.knowledge_point.name if p.knowledge_point else "",
            mastery_level=p.mastery_level.value,
            mastery_score=p.mastery_score,
            study_time=p.study_time,
            practice_count=p.practice_count,
            correct_count=p.correct_count,
            wrong_count=p.wrong_count,
            accuracy=(p.correct_count / (p.correct_count + p.wrong_count) * 100)
                if (p.correct_count + p.wrong_count) > 0 else 0,
            next_review_date=p.next_review_date.isoformat() if p.next_review_date else None,
            last_studied_at=p.last_studied_at.isoformat() if p.last_studied_at else None
        )
        for p in progress_list
    ]


@router.post("/progress/update")
async def update_progress(
    request: UpdateProgressRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新学习进度"""
    service = LearningService(db)
    
    progress = await service.update_progress(
        user_id=current_user.id,
        knowledge_point_id=request.knowledge_point_id,
        is_correct=request.is_correct,
        time_spent=request.time_spent
    )
    
    # 更新每日目标
    await service.update_daily_goal_progress(
        user_id=current_user.id,
        study_time=request.time_spent,
        exercises=1,
        knowledge_points=1 if progress.mastery_level != MasteryLevel.NOT_STARTED else 0
    )
    
    # 更新每日统计
    await service.update_daily_stats(
        user_id=current_user.id,
        study_time=request.time_spent,
        activity_count=1,
        knowledge_points_studied=1 if progress.mastery_level != MasteryLevel.NOT_STARTED else 0,
        knowledge_points_mastered=1 if progress.mastery_level in [MasteryLevel.MASTERED, MasteryLevel.EXPERT] else 0,
        exercises_attempted=1,
        exercises_correct=1 if request.is_correct else 0
    )
    
    # 检查成就
    achievement_service = AchievementService(db)
    newly_unlocked = await achievement_service.check_and_unlock_achievements(current_user.id)
    
    return {
        "message": "进度更新成功",
        "progress": {
            "mastery_level": progress.mastery_level.value,
            "mastery_score": progress.mastery_score,
            "practice_count": progress.practice_count
        },
        "newly_unlocked_achievements": [
            {
                "title": ua.achievement.title,
                "description": ua.achievement.description,
                "points": ua.achievement.points
            }
            for ua in newly_unlocked
        ] if newly_unlocked else []
    }


@router.get("/progress/review-due", response_model=List[ProgressResponse])
async def get_review_due_knowledge_points(
    limit: int = Query(20, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取需要复习的知识点"""
    service = LearningService(db)
    progress_list = await service.get_review_due_knowledge_points(
        current_user.id,
        limit
    )
    
    return [
        ProgressResponse(
            id=p.id,
            knowledge_point_id=p.knowledge_point_id,
            knowledge_point_name=p.knowledge_point.name if p.knowledge_point else "",
            mastery_level=p.mastery_level.value,
            mastery_score=p.mastery_score,
            study_time=p.study_time,
            practice_count=p.practice_count,
            correct_count=p.correct_count,
            wrong_count=p.wrong_count,
            accuracy=(p.correct_count / (p.correct_count + p.wrong_count) * 100)
                if (p.correct_count + p.wrong_count) > 0 else 0,
            next_review_date=p.next_review_date.isoformat() if p.next_review_date else None,
            last_studied_at=p.last_studied_at.isoformat() if p.last_studied_at else None
        )
        for p in progress_list
    ]


# ========================================
# 学习活动相关端点
# ========================================

@router.post("/activities")
async def create_activity(
    request: CreateActivityRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建学习活动记录"""
    service = LearningService(db)
    
    activity = await service.create_activity(
        user_id=current_user.id,
        activity_type=ActivityType(request.activity_type),
        title=request.title,
        knowledge_point_id=request.knowledge_point_id,
        description=request.description,
        duration=request.duration,
        score=request.score
    )
    
    return {
        "message": "活动创建成功",
        "activity_id": activity.id
    }


@router.get("/activities")
async def get_user_activities(
    activity_type: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户学习活动"""
    service = LearningService(db)
    
    activities = await service.get_user_activities(
        current_user.id,
        ActivityType(activity_type) if activity_type else None,
        limit
    )
    
    return {
        "activities": [
            {
                "id": a.id,
                "type": a.activity_type.value,
                "title": a.title,
                "description": a.description,
                "duration": a.duration,
                "score": a.score,
                "started_at": a.started_at.isoformat(),
                "is_completed": a.is_completed
            }
            for a in activities
        ]
    }


# ========================================
# 每日目标相关端点
# ========================================

@router.get("/daily-goal", response_model=DailyGoalResponse)
async def get_daily_goal(
    target_date: Optional[str] = Query(None, description="目标日期 YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取每日目标"""
    service = LearningService(db)
    
    if target_date:
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    else:
        target_date_obj = date.today()
    
    goal = await service.get_or_create_daily_goal(current_user.id, target_date_obj)
    
    return DailyGoalResponse(
        id=goal.id,
        date=goal.date.strftime("%Y-%m-%d"),
        target_study_time=goal.target_study_time,
        target_exercises=goal.target_exercises,
        target_knowledge_points=goal.target_knowledge_points,
        actual_study_time=goal.actual_study_time,
        actual_exercises=goal.actual_exercises,
        actual_knowledge_points=goal.actual_knowledge_points,
        completion_percentage=goal.completion_percentage,
        is_completed=goal.is_completed
    )


# ========================================
# 学习统计相关端点
# ========================================

@router.get("/stats/summary")
async def get_user_summary_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户总体统计"""
    service = LearningService(db)
    stats = await service.get_user_summary_stats(current_user.id)
    return stats


@router.get("/stats/range")
async def get_user_stats_range(
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定日期范围的统计"""
    service = LearningService(db)
    
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    stats_list = await service.get_user_stats_range(current_user.id, start, end)
    
    return {
        "stats": [
            {
                "date": stat.date.strftime("%Y-%m-%d"),
                "study_time": stat.total_study_time,
                "sessions": stat.session_count,
                "activities": stat.activity_count,
                "knowledge_points_studied": stat.knowledge_points_studied,
                "knowledge_points_mastered": stat.knowledge_points_mastered,
                "exercises_attempted": stat.exercises_attempted,
                "exercises_correct": stat.exercises_correct,
                "average_score": stat.average_score
            }
            for stat in stats_list
        ]
    }


# ========================================
# 学习路径相关端点
# ========================================

@router.post("/paths")
async def create_learning_path(
    request: CreateLearningPathRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建学习路径"""
    service = LearningPathService(db)
    
    path = await service.create_learning_path(
        user_id=current_user.id,
        name=request.name,
        knowledge_point_ids=request.knowledge_point_ids,
        target_subject_id=request.target_subject_id,
        description=request.description,
        difficulty=DifficultyLevel(request.difficulty)
    )
    
    return {
        "message": "学习路径创建成功",
        "path_id": path.id
    }


@router.post("/paths/generate-adaptive")
async def generate_adaptive_path(
    request: GenerateAdaptivePathRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成自适应学习路径"""
    service = LearningPathService(db)
    
    path = await service.generate_adaptive_path(
        user_id=current_user.id,
        subject_id=request.subject_id,
        target_difficulty=DifficultyLevel(request.target_difficulty)
    )
    
    return {
        "message": "自适应学习路径生成成功",
        "path_id": path.id,
        "knowledge_points_count": len(path.knowledge_points)
    }


@router.get("/paths")
async def get_user_paths(
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户学习路径列表"""
    service = LearningPathService(db)
    paths = await service.get_user_paths(current_user.id, is_active)
    
    return {
        "paths": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "difficulty": p.difficulty.value,
                "progress_percentage": p.progress_percentage,
                "total_knowledge_points": len(p.knowledge_points),
                "completed_count": p.completed_count,
                "is_active": p.is_active
            }
            for p in paths
        ]
    }


@router.get("/paths/{path_id}")
async def get_path_details(
    path_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取学习路径详情"""
    service = LearningPathService(db)
    details = await service.get_path_details(path_id)
    
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路径不存在"
        )
    
    return details


# ========================================
# 成就系统相关端点
# ========================================

@router.get("/achievements", response_model=List[AchievementResponse])
async def get_user_achievements(
    unlocked_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户成就列表"""
    service = AchievementService(db)
    achievements = await service.get_user_achievements(current_user.id, unlocked_only)
    
    return [
        AchievementResponse(**a)
        for a in achievements
    ]


@router.get("/achievements/summary")
async def get_achievement_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取成就摘要"""
    service = AchievementService(db)
    summary = await service.get_achievement_summary(current_user.id)
    return summary


@router.post("/achievements/check")
async def check_achievements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """手动检查并解锁成就"""
    service = AchievementService(db)
    newly_unlocked = await service.check_and_unlock_achievements(current_user.id)
    
    return {
        "message": f"检查完成，解锁 {len(newly_unlocked)} 个新成就",
        "newly_unlocked": [
            {
                "title": ua.achievement.title,
                "description": ua.achievement.description,
                "points": ua.achievement.points,
                "rarity": ua.achievement.rarity
            }
            for ua in newly_unlocked
        ]
    }
