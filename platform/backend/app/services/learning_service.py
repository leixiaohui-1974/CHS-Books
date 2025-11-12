"""
学习追踪服务
"""

from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, update
from sqlalchemy.orm import selectinload

from app.models.learning import (
    Subject, Chapter, KnowledgePoint,
    UserKnowledgeProgress, LearningActivity, StudySession,
    LearningPath, DailyGoal, Achievement, UserAchievement, LearningStats,
    DifficultyLevel, MasteryLevel, ActivityType, AchievementType
)
from app.models.user import User


class LearningService:
    """学习追踪服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========================================
    # 知识点管理
    # ========================================
    
    async def get_subjects(self, is_active: bool = True) -> List[Subject]:
        """获取学科列表"""
        query = select(Subject)
        if is_active:
            query = query.where(Subject.is_active == True)
        query = query.order_by(Subject.order, Subject.id)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_chapters(
        self,
        subject_id: int,
        is_active: bool = True
    ) -> List[Chapter]:
        """获取章节列表"""
        query = select(Chapter).where(Chapter.subject_id == subject_id)
        if is_active:
            query = query.where(Chapter.is_active == True)
        query = query.order_by(Chapter.order, Chapter.id)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_knowledge_points(
        self,
        chapter_id: int,
        is_active: bool = True
    ) -> List[KnowledgePoint]:
        """获取知识点列表"""
        query = select(KnowledgePoint).where(KnowledgePoint.chapter_id == chapter_id)
        if is_active:
            query = query.where(KnowledgePoint.is_active == True)
        query = query.order_by(KnowledgePoint.order, KnowledgePoint.id)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_knowledge_point(self, kp_id: int) -> Optional[KnowledgePoint]:
        """获取知识点详情"""
        result = await self.db.execute(
            select(KnowledgePoint).where(KnowledgePoint.id == kp_id)
        )
        return result.scalar_one_or_none()
    
    # ========================================
    # 用户学习进度
    # ========================================
    
    async def get_or_create_progress(
        self,
        user_id: int,
        knowledge_point_id: int
    ) -> UserKnowledgeProgress:
        """获取或创建用户知识点进度"""
        # 尝试获取现有进度
        result = await self.db.execute(
            select(UserKnowledgeProgress).where(
                and_(
                    UserKnowledgeProgress.user_id == user_id,
                    UserKnowledgeProgress.knowledge_point_id == knowledge_point_id
                )
            )
        )
        progress = result.scalar_one_or_none()
        
        if not progress:
            # 创建新进度
            progress = UserKnowledgeProgress(
                user_id=user_id,
                knowledge_point_id=knowledge_point_id,
                mastery_level=MasteryLevel.NOT_STARTED,
                mastery_score=0.0,
                first_studied_at=datetime.utcnow()
            )
            self.db.add(progress)
            await self.db.commit()
            await self.db.refresh(progress)
        
        return progress
    
    async def update_progress(
        self,
        user_id: int,
        knowledge_point_id: int,
        is_correct: bool,
        time_spent: int = 0
    ) -> UserKnowledgeProgress:
        """更新学习进度（练习后）"""
        progress = await self.get_or_create_progress(user_id, knowledge_point_id)
        
        # 更新统计
        progress.practice_count += 1
        progress.study_time += time_spent
        progress.last_studied_at = datetime.utcnow()
        
        if is_correct:
            progress.correct_count += 1
        else:
            progress.wrong_count += 1
        
        # 计算正确率
        total_attempts = progress.correct_count + progress.wrong_count
        if total_attempts > 0:
            accuracy = progress.correct_count / total_attempts
        else:
            accuracy = 0
        
        # 更新掌握度分数 (考虑正确率和练习次数)
        # 分数 = 正确率 * 80 + min(练习次数/10, 1) * 20
        progress.mastery_score = accuracy * 80 + min(progress.practice_count / 10, 1) * 20
        
        # 更新掌握级别
        if progress.mastery_score >= 90:
            progress.mastery_level = MasteryLevel.EXPERT
            if not progress.mastered_at:
                progress.mastered_at = datetime.utcnow()
        elif progress.mastery_score >= 75:
            progress.mastery_level = MasteryLevel.MASTERED
            if not progress.mastered_at:
                progress.mastered_at = datetime.utcnow()
        elif progress.mastery_score >= 50:
            progress.mastery_level = MasteryLevel.PRACTICING
        elif progress.mastery_score > 0:
            progress.mastery_level = MasteryLevel.LEARNING
        
        # 使用SM-2算法更新复习间隔
        if is_correct:
            # 正确回答，增加间隔
            quality = 4 if progress.mastery_score >= 80 else 3
            progress = self._update_spaced_repetition(progress, quality)
        else:
            # 错误回答，重置
            progress.repetitions = 0
            progress.interval = 1
            progress.next_review_date = datetime.utcnow() + timedelta(days=1)
        
        await self.db.commit()
        await self.db.refresh(progress)
        
        return progress
    
    def _update_spaced_repetition(
        self,
        progress: UserKnowledgeProgress,
        quality: int  # 0-5, 3以上为正确
    ) -> UserKnowledgeProgress:
        """
        使用SM-2算法更新间隔重复参数
        quality: 回答质量 (0-5)
          5 - 完美回答
          4 - 正确但犹豫
          3 - 正确但困难
          2 - 错误但记得
          1 - 错误且不记得
          0 - 完全遗忘
        """
        if quality >= 3:
            # 正确回答
            if progress.repetitions == 0:
                progress.interval = 1
            elif progress.repetitions == 1:
                progress.interval = 6
            else:
                progress.interval = int(progress.interval * progress.easiness_factor)
            
            progress.repetitions += 1
        else:
            # 错误回答，重新开始
            progress.repetitions = 0
            progress.interval = 1
        
        # 更新难度因子
        progress.easiness_factor = max(
            1.3,
            progress.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        )
        
        # 设置下次复习日期
        progress.next_review_date = datetime.utcnow() + timedelta(days=progress.interval)
        
        return progress
    
    async def get_user_progress(
        self,
        user_id: int,
        knowledge_point_id: Optional[int] = None
    ) -> List[UserKnowledgeProgress]:
        """获取用户学习进度"""
        query = select(UserKnowledgeProgress).where(
            UserKnowledgeProgress.user_id == user_id
        )
        
        if knowledge_point_id:
            query = query.where(
                UserKnowledgeProgress.knowledge_point_id == knowledge_point_id
            )
        
        query = query.options(selectinload(UserKnowledgeProgress.knowledge_point))
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_review_due_knowledge_points(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[UserKnowledgeProgress]:
        """获取需要复习的知识点"""
        now = datetime.utcnow()
        
        query = select(UserKnowledgeProgress).where(
            and_(
                UserKnowledgeProgress.user_id == user_id,
                UserKnowledgeProgress.next_review_date <= now,
                UserKnowledgeProgress.mastery_level != MasteryLevel.NOT_STARTED
            )
        ).options(
            selectinload(UserKnowledgeProgress.knowledge_point)
        ).order_by(
            UserKnowledgeProgress.next_review_date
        ).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    # ========================================
    # 学习活动记录
    # ========================================
    
    async def create_activity(
        self,
        user_id: int,
        activity_type: ActivityType,
        title: str,
        knowledge_point_id: Optional[int] = None,
        description: Optional[str] = None,
        duration: int = 0,
        score: Optional[float] = None,
        result_data: Optional[Dict[str, Any]] = None
    ) -> LearningActivity:
        """创建学习活动记录"""
        activity = LearningActivity(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id,
            activity_type=activity_type,
            title=title,
            description=description,
            duration=duration,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow() if duration > 0 else None,
            score=score,
            is_completed=duration > 0,
            result_data=result_data
        )
        
        self.db.add(activity)
        await self.db.commit()
        await self.db.refresh(activity)
        
        return activity
    
    async def get_user_activities(
        self,
        user_id: int,
        activity_type: Optional[ActivityType] = None,
        limit: int = 50
    ) -> List[LearningActivity]:
        """获取用户学习活动"""
        query = select(LearningActivity).where(
            LearningActivity.user_id == user_id
        )
        
        if activity_type:
            query = query.where(LearningActivity.activity_type == activity_type)
        
        query = query.order_by(desc(LearningActivity.started_at)).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    # ========================================
    # 学习会话
    # ========================================
    
    async def create_study_session(
        self,
        user_id: int,
        device_type: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> StudySession:
        """创建学习会话"""
        session = StudySession(
            user_id=user_id,
            started_at=datetime.utcnow(),
            device_type=device_type,
            ip_address=ip_address
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def end_study_session(
        self,
        session_id: int,
        activities_count: int = 0,
        knowledge_points_studied: int = 0,
        exercises_completed: int = 0
    ) -> StudySession:
        """结束学习会话"""
        result = await self.db.execute(
            select(StudySession).where(StudySession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if session:
            session.ended_at = datetime.utcnow()
            session.duration = int((session.ended_at - session.started_at).total_seconds())
            session.activities_count = activities_count
            session.knowledge_points_studied = knowledge_points_studied
            session.exercises_completed = exercises_completed
            
            await self.db.commit()
            await self.db.refresh(session)
        
        return session
    
    async def get_active_session(self, user_id: int) -> Optional[StudySession]:
        """获取活跃会话"""
        result = await self.db.execute(
            select(StudySession).where(
                and_(
                    StudySession.user_id == user_id,
                    StudySession.ended_at == None
                )
            ).order_by(desc(StudySession.started_at)).limit(1)
        )
        return result.scalar_one_or_none()
    
    # ========================================
    # 每日目标
    # ========================================
    
    async def get_or_create_daily_goal(
        self,
        user_id: int,
        target_date: Optional[date] = None
    ) -> DailyGoal:
        """获取或创建每日目标"""
        if target_date is None:
            target_date = date.today()
        
        target_datetime = datetime.combine(target_date, datetime.min.time())
        
        result = await self.db.execute(
            select(DailyGoal).where(
                and_(
                    DailyGoal.user_id == user_id,
                    func.date(DailyGoal.date) == target_date
                )
            )
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            goal = DailyGoal(
                user_id=user_id,
                date=target_datetime,
                target_study_time=3600,  # 默认1小时
                target_exercises=10,
                target_knowledge_points=3
            )
            self.db.add(goal)
            await self.db.commit()
            await self.db.refresh(goal)
        
        return goal
    
    async def update_daily_goal_progress(
        self,
        user_id: int,
        study_time: int = 0,
        exercises: int = 0,
        knowledge_points: int = 0
    ) -> DailyGoal:
        """更新每日目标进度"""
        goal = await self.get_or_create_daily_goal(user_id)
        
        goal.actual_study_time += study_time
        goal.actual_exercises += exercises
        goal.actual_knowledge_points += knowledge_points
        
        # 计算完成度
        time_completion = min(goal.actual_study_time / goal.target_study_time * 100, 100)
        exercise_completion = min(goal.actual_exercises / goal.target_exercises * 100, 100)
        kp_completion = min(goal.actual_knowledge_points / goal.target_knowledge_points * 100, 100)
        
        goal.completion_percentage = (time_completion + exercise_completion + kp_completion) / 3
        goal.is_completed = goal.completion_percentage >= 100
        
        await self.db.commit()
        await self.db.refresh(goal)
        
        return goal
    
    # ========================================
    # 学习统计
    # ========================================
    
    async def get_or_create_daily_stats(
        self,
        user_id: int,
        target_date: Optional[date] = None
    ) -> LearningStats:
        """获取或创建每日统计"""
        if target_date is None:
            target_date = date.today()
        
        target_datetime = datetime.combine(target_date, datetime.min.time())
        
        result = await self.db.execute(
            select(LearningStats).where(
                and_(
                    LearningStats.user_id == user_id,
                    func.date(LearningStats.date) == target_date
                )
            )
        )
        stats = result.scalar_one_or_none()
        
        if not stats:
            stats = LearningStats(
                user_id=user_id,
                date=target_datetime
            )
            self.db.add(stats)
            await self.db.commit()
            await self.db.refresh(stats)
        
        return stats
    
    async def update_daily_stats(
        self,
        user_id: int,
        study_time: int = 0,
        session_count: int = 0,
        activity_count: int = 0,
        knowledge_points_studied: int = 0,
        knowledge_points_mastered: int = 0,
        exercises_attempted: int = 0,
        exercises_correct: int = 0,
        achievements_unlocked: int = 0,
        points_earned: int = 0
    ) -> LearningStats:
        """更新每日统计"""
        stats = await self.get_or_create_daily_stats(user_id)
        
        stats.total_study_time += study_time
        stats.session_count += session_count
        stats.activity_count += activity_count
        stats.knowledge_points_studied += knowledge_points_studied
        stats.knowledge_points_mastered += knowledge_points_mastered
        stats.exercises_attempted += exercises_attempted
        stats.exercises_correct += exercises_correct
        stats.achievements_unlocked += achievements_unlocked
        stats.points_earned += points_earned
        
        # 计算平均分
        if stats.exercises_attempted > 0:
            stats.average_score = (stats.exercises_correct / stats.exercises_attempted) * 100
        
        await self.db.commit()
        await self.db.refresh(stats)
        
        return stats
    
    async def get_user_stats_range(
        self,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> List[LearningStats]:
        """获取用户指定日期范围的统计"""
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        result = await self.db.execute(
            select(LearningStats).where(
                and_(
                    LearningStats.user_id == user_id,
                    LearningStats.date >= start_datetime,
                    LearningStats.date <= end_datetime
                )
            ).order_by(LearningStats.date)
        )
        
        return list(result.scalars().all())
    
    async def get_user_summary_stats(self, user_id: int) -> Dict[str, Any]:
        """获取用户总体统计"""
        # 获取所有进度
        progress_result = await self.db.execute(
            select(UserKnowledgeProgress).where(
                UserKnowledgeProgress.user_id == user_id
            )
        )
        all_progress = list(progress_result.scalars().all())
        
        # 统计掌握情况
        mastery_counts = {
            MasteryLevel.NOT_STARTED: 0,
            MasteryLevel.LEARNING: 0,
            MasteryLevel.PRACTICING: 0,
            MasteryLevel.MASTERED: 0,
            MasteryLevel.EXPERT: 0
        }
        
        total_study_time = 0
        total_practice_count = 0
        total_correct = 0
        total_wrong = 0
        
        for progress in all_progress:
            mastery_counts[progress.mastery_level] += 1
            total_study_time += progress.study_time
            total_practice_count += progress.practice_count
            total_correct += progress.correct_count
            total_wrong += progress.wrong_count
        
        # 获取最近7天统计
        seven_days_ago = date.today() - timedelta(days=7)
        recent_stats = await self.get_user_stats_range(
            user_id,
            seven_days_ago,
            date.today()
        )
        
        # 计算连续学习天数
        streak_days = await self._calculate_streak_days(user_id)
        
        return {
            "total_knowledge_points": len(all_progress),
            "mastery_distribution": mastery_counts,
            "total_study_time": total_study_time,
            "total_practice_count": total_practice_count,
            "total_correct": total_correct,
            "total_wrong": total_wrong,
            "accuracy": total_correct / (total_correct + total_wrong) * 100 if (total_correct + total_wrong) > 0 else 0,
            "recent_7_days": [
                {
                    "date": stat.date.strftime("%Y-%m-%d"),
                    "study_time": stat.total_study_time,
                    "activities": stat.activity_count,
                    "exercises": stat.exercises_attempted,
                    "average_score": stat.average_score
                }
                for stat in recent_stats
            ],
            "streak_days": streak_days
        }
    
    async def _calculate_streak_days(self, user_id: int) -> int:
        """计算连续学习天数"""
        today = date.today()
        streak = 0
        current_date = today
        
        while True:
            stats = await self.get_or_create_daily_stats(user_id, current_date)
            
            if stats.activity_count > 0 or stats.total_study_time > 0:
                streak += 1
                current_date = current_date - timedelta(days=1)
            else:
                break
            
            # 最多查询90天
            if streak >= 90 or (today - current_date).days > 90:
                break
        
        return streak
