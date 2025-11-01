"""
用户分析API端点
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.utils.analytics import UserAnalytics


router = APIRouter()


@router.get("/my-stats", tags=["分析"])
async def get_my_stats(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取我的学习统计
    
    返回指定时间段内的学习统计数据。
    """
    stats = await UserAnalytics.get_user_learning_stats(db, current_user.id, days)
    return stats


@router.get("/my-trend", tags=["分析"])
async def get_my_trend(
    days: int = Query(7, ge=1, le=30, description="统计天数"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取我的学习趋势
    
    返回每日学习数据，用于绘制趋势图表。
    """
    trend = await UserAnalytics.get_learning_trend(db, current_user.id, days)
    return {
        "days": days,
        "data": trend
    }


@router.get("/my-ranking", tags=["分析"])
async def get_my_ranking(
    metric: str = Query("score", regex="^(score|cases|time)$", description="排名指标"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取我的排名
    
    参数:
    - metric: 排名指标
      - score: 按平均得分排名
      - cases: 按完成案例数排名
      - time: 按学习时长排名
    """
    ranking = await UserAnalytics.get_user_ranking(db, current_user.id, metric)
    return ranking


@router.get("/my-insights", tags=["分析"])
async def get_my_insights(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取我的学习洞察
    
    AI分析您的学习行为，提供个性化建议。
    """
    insights = await UserAnalytics.get_learning_insights(db, current_user.id)
    return insights


@router.get("/popular-courses", tags=["分析"])
async def get_popular_courses(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取热门课程
    
    返回报名人数最多的课程列表。
    """
    courses = await UserAnalytics.get_popular_courses(db, limit)
    return {
        "total": len(courses),
        "courses": courses
    }
