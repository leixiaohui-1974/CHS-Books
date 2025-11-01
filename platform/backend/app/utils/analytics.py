"""
用户行为分析工具
追踪和分析用户学习行为
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from loguru import logger

from app.models.user import User
from app.models.progress import UserProgress, CaseProgress, ProgressStatus
from app.models.book import Book, Case


class UserAnalytics:
    """用户行为分析类"""
    
    @staticmethod
    async def get_user_learning_stats(
        db: AsyncSession,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取用户学习统计
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 统计天数
        
        Returns:
            学习统计数据
        """
        # 时间范围
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # 总学习时长
        result = await db.execute(
            select(func.sum(UserProgress.total_time_spent))
            .where(UserProgress.user_id == user_id)
        )
        total_time = result.scalar() or 0
        
        # 完成的案例数 (通过UserProgress关联)
        result = await db.execute(
            select(func.count(CaseProgress.id))
            .join(UserProgress, UserProgress.id == CaseProgress.user_progress_id)
            .where(
                and_(
                    UserProgress.user_id == user_id,
                    CaseProgress.status == ProgressStatus.COMPLETED
                )
            )
        )
        completed_cases = result.scalar() or 0
        
        # 平均得分 (通过UserProgress关联)
        result = await db.execute(
            select(func.avg(CaseProgress.score))
            .join(UserProgress, UserProgress.id == CaseProgress.user_progress_id)
            .where(
                and_(
                    UserProgress.user_id == user_id,
                    CaseProgress.status == ProgressStatus.COMPLETED,
                    CaseProgress.score.isnot(None)
                )
            )
        )
        avg_score = result.scalar() or 0
        
        # 最近活跃天数 (通过UserProgress关联)
        result = await db.execute(
            select(func.count(func.distinct(func.date(CaseProgress.last_accessed))))
            .join(UserProgress, UserProgress.id == CaseProgress.user_progress_id)
            .where(
                and_(
                    UserProgress.user_id == user_id,
                    CaseProgress.last_accessed >= start_date
                )
            )
        )
        active_days = result.scalar() or 0
        
        # 报名课程数
        result = await db.execute(
            select(func.count(UserProgress.id))
            .where(UserProgress.user_id == user_id)
        )
        enrolled_courses = result.scalar() or 0
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_learning_minutes": int(total_time),
            "completed_cases": completed_cases,
            "average_score": round(float(avg_score), 2),
            "active_days": active_days,
            "enrolled_courses": enrolled_courses,
            "daily_average_minutes": round(total_time / max(active_days, 1), 2)
        }
    
    @staticmethod
    async def get_learning_trend(
        db: AsyncSession,
        user_id: int,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        获取学习趋势数据
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 统计天数
        
        Returns:
            每日学习数据列表
        """
        trend_data = []
        
        for i in range(days):
            date = datetime.now(timezone.utc) - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # 当日完成案例数 (通过UserProgress关联)
            result = await db.execute(
                select(func.count(CaseProgress.id))
                .join(UserProgress, UserProgress.id == CaseProgress.user_progress_id)
                .where(
                    and_(
                        UserProgress.user_id == user_id,
                        CaseProgress.status == ProgressStatus.COMPLETED,
                        CaseProgress.completed_at.between(date_start, date_end)
                    )
                )
            )
            cases_count = result.scalar() or 0
            
            # 当日学习时长（估算）
            study_time = cases_count * 30  # 假设每个案例平均30分钟
            
            trend_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "cases_completed": cases_count,
                "study_minutes": study_time
            })
        
        return list(reversed(trend_data))
    
    @staticmethod
    async def get_popular_courses(
        db: AsyncSession,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取热门课程
        
        Args:
            db: 数据库会话
            limit: 返回数量
        
        Returns:
            热门课程列表
        """
        result = await db.execute(
            select(
                Book.id,
                Book.title,
                func.count(UserProgress.id).label("enrollment_count")
            )
            .join(UserProgress, UserProgress.book_id == Book.id)
            .group_by(Book.id, Book.title)
            .order_by(func.count(UserProgress.id).desc())
            .limit(limit)
        )
        
        courses = result.all()
        
        return [
            {
                "book_id": course.id,
                "title": course.title,
                "enrollments": course.enrollment_count
            }
            for course in courses
        ]
    
    @staticmethod
    async def get_user_ranking(
        db: AsyncSession,
        user_id: int,
        metric: str = "score"
    ) -> Dict[str, Any]:
        """
        获取用户排名
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            metric: 排名指标（score/time/cases）
        
        Returns:
            用户排名信息
        """
        if metric == "score":
            # 按平均得分排名 (通过UserProgress关联)
            result = await db.execute(
                select(
                    UserProgress.user_id,
                    func.avg(CaseProgress.score).label("avg_score")
                )
                .join(CaseProgress, CaseProgress.user_progress_id == UserProgress.id)
                .where(CaseProgress.score.isnot(None))
                .group_by(UserProgress.user_id)
                .order_by(func.avg(CaseProgress.score).desc())
            )
            rankings = result.all()
            
            for rank, item in enumerate(rankings, 1):
                if item.user_id == user_id:
                    return {
                        "user_id": user_id,
                        "rank": rank,
                        "total_users": len(rankings),
                        "percentile": round((1 - rank / len(rankings)) * 100, 2),
                        "metric": "average_score",
                        "value": round(float(item.avg_score), 2)
                    }
        
        elif metric == "cases":
            # 按完成案例数排名 (通过UserProgress关联)
            result = await db.execute(
                select(
                    UserProgress.user_id,
                    func.count(CaseProgress.id).label("case_count")
                )
                .join(CaseProgress, CaseProgress.user_progress_id == UserProgress.id)
                .where(CaseProgress.status == ProgressStatus.COMPLETED)
                .group_by(UserProgress.user_id)
                .order_by(func.count(CaseProgress.id).desc())
            )
            rankings = result.all()
            
            for rank, item in enumerate(rankings, 1):
                if item.user_id == user_id:
                    return {
                        "user_id": user_id,
                        "rank": rank,
                        "total_users": len(rankings),
                        "percentile": round((1 - rank / len(rankings)) * 100, 2),
                        "metric": "completed_cases",
                        "value": item.case_count
                    }
        
        return {
            "user_id": user_id,
            "rank": 0,
            "total_users": 0,
            "percentile": 0,
            "metric": metric,
            "value": 0
        }
    
    @staticmethod
    async def get_learning_insights(
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """
        获取学习洞察
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            学习洞察数据
        """
        # 获取用户的所有案例进度 (通过UserProgress关联)
        result = await db.execute(
            select(CaseProgress)
            .join(UserProgress, UserProgress.id == CaseProgress.user_progress_id)
            .where(UserProgress.user_id == user_id)
        )
        case_progresses = result.scalars().all()
        
        if not case_progresses:
            return {
                "total_cases": 0,
                "insights": []
            }
        
        insights = []
        
        # 分析1: 学习时间段偏好
        hour_distribution = {}
        for progress in case_progresses:
            if progress.last_accessed:
                hour = progress.last_accessed.hour
                hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
        
        if hour_distribution:
            peak_hour = max(hour_distribution, key=hour_distribution.get)
            insights.append({
                "type": "time_preference",
                "message": f"您最常在{peak_hour}:00学习",
                "data": hour_distribution
            })
        
        # 分析2: 学习速度
        completed = [p for p in case_progresses if p.status == ProgressStatus.COMPLETED]
        if completed:
            avg_attempts = sum(p.attempts for p in completed) / len(completed)
            if avg_attempts < 2:
                insights.append({
                    "type": "learning_speed",
                    "message": "您的学习效率很高，通常一次就能掌握",
                    "data": {"avg_attempts": round(avg_attempts, 2)}
                })
            elif avg_attempts > 3:
                insights.append({
                    "type": "learning_speed",
                    "message": "建议放慢节奏，多次复习巩固知识",
                    "data": {"avg_attempts": round(avg_attempts, 2)}
                })
        
        # 分析3: 得分趋势
        scored = [p for p in completed if p.score is not None]
        if len(scored) >= 5:
            recent_5 = sorted(scored, key=lambda x: x.completed_at, reverse=True)[:5]
            avg_recent = sum(p.score for p in recent_5) / 5
            
            if avg_recent >= 90:
                insights.append({
                    "type": "performance",
                    "message": "最近表现优秀！继续保持！",
                    "data": {"recent_avg_score": round(avg_recent, 2)}
                })
            elif avg_recent < 70:
                insights.append({
                    "type": "performance",
                    "message": "建议回顾基础知识，巩固学习",
                    "data": {"recent_avg_score": round(avg_recent, 2)}
                })
        
        return {
            "total_cases": len(case_progresses),
            "completed_cases": len(completed),
            "insights": insights
        }


# 便捷函数
async def get_user_stats(db: AsyncSession, user_id: int, days: int = 30) -> Dict[str, Any]:
    """获取用户统计"""
    return await UserAnalytics.get_user_learning_stats(db, user_id, days)


async def get_trend_data(db: AsyncSession, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
    """获取趋势数据"""
    return await UserAnalytics.get_learning_trend(db, user_id, days)


async def get_insights(db: AsyncSession, user_id: int) -> Dict[str, Any]:
    """获取学习洞察"""
    return await UserAnalytics.get_learning_insights(db, user_id)
