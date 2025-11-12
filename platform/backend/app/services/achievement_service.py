"""
成就系统服务
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.learning import (
    Achievement, UserAchievement, AchievementType,
    UserKnowledgeProgress, LearningStats,
    MasteryLevel
)


class AchievementService:
    """成就系统服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def initialize_default_achievements(self) -> List[Achievement]:
        """初始化默认成就"""
        default_achievements = [
            # 学习时长成就
            {
                "name": "first_hour",
                "title": "初学者",
                "description": "累计学习时长达到1小时",
                "icon": "⏰",
                "achievement_type": AchievementType.STUDY_TIME,
                "requirement_value": 3600,  # 秒
                "points": 10,
                "rarity": "common"
            },
            {
                "name": "ten_hours",
                "title": "勤奋学者",
                "description": "累计学习时长达到10小时",
                "icon": "📚",
                "achievement_type": AchievementType.STUDY_TIME,
                "requirement_value": 36000,
                "points": 50,
                "rarity": "rare"
            },
            {
                "name": "hundred_hours",
                "title": "学习达人",
                "description": "累计学习时长达到100小时",
                "icon": "🎓",
                "achievement_type": AchievementType.STUDY_TIME,
                "requirement_value": 360000,
                "points": 200,
                "rarity": "epic"
            },
            {
                "name": "thousand_hours",
                "title": "学习大师",
                "description": "累计学习时长达到1000小时",
                "icon": "👑",
                "achievement_type": AchievementType.STUDY_TIME,
                "requirement_value": 3600000,
                "points": 1000,
                "rarity": "legendary"
            },
            
            # 练习次数成就
            {
                "name": "first_ten_exercises",
                "title": "初试牛刀",
                "description": "完成10次练习",
                "icon": "💪",
                "achievement_type": AchievementType.EXERCISE_COUNT,
                "requirement_value": 10,
                "points": 10,
                "rarity": "common"
            },
            {
                "name": "hundred_exercises",
                "title": "勤于练习",
                "description": "完成100次练习",
                "icon": "🎯",
                "achievement_type": AchievementType.EXERCISE_COUNT,
                "requirement_value": 100,
                "points": 50,
                "rarity": "rare"
            },
            {
                "name": "thousand_exercises",
                "title": "练习狂人",
                "description": "完成1000次练习",
                "icon": "🔥",
                "achievement_type": AchievementType.EXERCISE_COUNT,
                "requirement_value": 1000,
                "points": 200,
                "rarity": "epic"
            },
            
            # 知识点掌握成就
            {
                "name": "first_mastery",
                "title": "初窥门径",
                "description": "掌握第1个知识点",
                "icon": "✨",
                "achievement_type": AchievementType.MASTERY_COUNT,
                "requirement_value": 1,
                "points": 10,
                "rarity": "common"
            },
            {
                "name": "ten_mastery",
                "title": "略有所成",
                "description": "掌握10个知识点",
                "icon": "⭐",
                "achievement_type": AchievementType.MASTERY_COUNT,
                "requirement_value": 10,
                "points": 50,
                "rarity": "rare"
            },
            {
                "name": "fifty_mastery",
                "title": "融会贯通",
                "description": "掌握50个知识点",
                "icon": "🌟",
                "achievement_type": AchievementType.MASTERY_COUNT,
                "requirement_value": 50,
                "points": 150,
                "rarity": "epic"
            },
            {
                "name": "hundred_mastery",
                "title": "博学多才",
                "description": "掌握100个知识点",
                "icon": "💎",
                "achievement_type": AchievementType.MASTERY_COUNT,
                "requirement_value": 100,
                "points": 500,
                "rarity": "legendary"
            },
            
            # 连续学习成就
            {
                "name": "seven_days_streak",
                "title": "坚持一周",
                "description": "连续学习7天",
                "icon": "📅",
                "achievement_type": AchievementType.STREAK_DAYS,
                "requirement_value": 7,
                "points": 30,
                "rarity": "rare"
            },
            {
                "name": "thirty_days_streak",
                "title": "持之以恒",
                "description": "连续学习30天",
                "icon": "🔥",
                "achievement_type": AchievementType.STREAK_DAYS,
                "requirement_value": 30,
                "points": 100,
                "rarity": "epic"
            },
            {
                "name": "hundred_days_streak",
                "title": "百日筑基",
                "description": "连续学习100天",
                "icon": "🏆",
                "achievement_type": AchievementType.STREAK_DAYS,
                "requirement_value": 100,
                "points": 500,
                "rarity": "legendary"
            },
            
            # 满分成就
            {
                "name": "first_perfect",
                "title": "完美开始",
                "description": "首次获得满分",
                "icon": "💯",
                "achievement_type": AchievementType.PERFECT_SCORE,
                "requirement_value": 1,
                "points": 20,
                "rarity": "common"
            },
            {
                "name": "ten_perfect",
                "title": "精益求精",
                "description": "获得10次满分",
                "icon": "🎯",
                "achievement_type": AchievementType.PERFECT_SCORE,
                "requirement_value": 10,
                "points": 100,
                "rarity": "epic"
            },
            
            # 快速学习者
            {
                "name": "fast_learner_day",
                "title": "日学百题",
                "description": "单日完成100道练习",
                "icon": "⚡",
                "achievement_type": AchievementType.FAST_LEARNER,
                "requirement_value": 100,
                "points": 50,
                "rarity": "rare"
            },
        ]
        
        created_achievements = []
        for ach_data in default_achievements:
            # 检查是否已存在
            result = await self.db.execute(
                select(Achievement).where(Achievement.name == ach_data["name"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                achievement = Achievement(**ach_data)
                self.db.add(achievement)
                created_achievements.append(achievement)
        
        if created_achievements:
            await self.db.commit()
        
        return created_achievements
    
    async def check_and_unlock_achievements(
        self,
        user_id: int
    ) -> List[UserAchievement]:
        """检查并解锁用户成就"""
        # 获取所有成就
        achievements_result = await self.db.execute(
            select(Achievement).where(Achievement.is_active == True)
        )
        all_achievements = list(achievements_result.scalars().all())
        
        # 获取用户已有成就
        user_achievements_result = await self.db.execute(
            select(UserAchievement).where(UserAchievement.user_id == user_id)
        )
        user_achievements_map = {
            ua.achievement_id: ua
            for ua in user_achievements_result.scalars().all()
        }
        
        # 获取用户统计数据
        user_stats = await self._get_user_achievement_stats(user_id)
        
        newly_unlocked = []
        
        for achievement in all_achievements:
            # 跳过已解锁的
            if achievement.id in user_achievements_map and user_achievements_map[achievement.id].is_unlocked:
                continue
            
            # 获取当前进度值
            current_value = user_stats.get(achievement.achievement_type.value, 0)
            
            # 检查是否达成
            if current_value >= achievement.requirement_value:
                # 解锁成就
                user_achievement = user_achievements_map.get(achievement.id)
                
                if user_achievement:
                    # 更新现有记录
                    user_achievement.is_unlocked = True
                    user_achievement.unlocked_at = datetime.utcnow()
                    user_achievement.progress_value = current_value
                else:
                    # 创建新记录
                    user_achievement = UserAchievement(
                        user_id=user_id,
                        achievement_id=achievement.id,
                        is_unlocked=True,
                        unlocked_at=datetime.utcnow(),
                        progress_value=current_value
                    )
                    self.db.add(user_achievement)
                
                newly_unlocked.append(user_achievement)
            else:
                # 更新进度
                user_achievement = user_achievements_map.get(achievement.id)
                
                if user_achievement:
                    user_achievement.progress_value = current_value
                else:
                    # 创建进度记录
                    user_achievement = UserAchievement(
                        user_id=user_id,
                        achievement_id=achievement.id,
                        is_unlocked=False,
                        progress_value=current_value
                    )
                    self.db.add(user_achievement)
        
        await self.db.commit()
        
        return newly_unlocked
    
    async def _get_user_achievement_stats(self, user_id: int) -> Dict[str, int]:
        """获取用户成就相关统计"""
        stats = {}
        
        # 学习时长
        progress_result = await self.db.execute(
            select(func.sum(UserKnowledgeProgress.study_time)).where(
                UserKnowledgeProgress.user_id == user_id
            )
        )
        total_study_time = progress_result.scalar() or 0
        stats["study_time"] = int(total_study_time)
        
        # 练习次数
        practice_result = await self.db.execute(
            select(func.sum(UserKnowledgeProgress.practice_count)).where(
                UserKnowledgeProgress.user_id == user_id
            )
        )
        total_practice = practice_result.scalar() or 0
        stats["exercise_count"] = int(total_practice)
        
        # 掌握知识点数
        mastery_result = await self.db.execute(
            select(func.count(UserKnowledgeProgress.id)).where(
                and_(
                    UserKnowledgeProgress.user_id == user_id,
                    UserKnowledgeProgress.mastery_level.in_([
                        MasteryLevel.MASTERED,
                        MasteryLevel.EXPERT
                    ])
                )
            )
        )
        mastery_count = mastery_result.scalar() or 0
        stats["mastery_count"] = mastery_count
        
        # 连续学习天数（需要从学习统计计算）
        streak_days = await self._calculate_streak_days(user_id)
        stats["streak_days"] = streak_days
        
        # 满分次数（简化处理，从practice计算正确率100%的次数）
        # 这里需要更详细的活动记录来准确统计
        stats["perfect_score"] = 0
        
        # 单日最多练习（从学习统计获取）
        daily_max_result = await self.db.execute(
            select(func.max(LearningStats.exercises_attempted)).where(
                LearningStats.user_id == user_id
            )
        )
        daily_max_exercises = daily_max_result.scalar() or 0
        stats["fast_learner"] = daily_max_exercises
        
        return stats
    
    async def _calculate_streak_days(self, user_id: int) -> int:
        """计算连续学习天数"""
        from datetime import date, timedelta
        
        today = date.today()
        streak = 0
        current_date = today
        
        while True:
            # 检查当天是否有学习记录
            result = await self.db.execute(
                select(LearningStats).where(
                    and_(
                        LearningStats.user_id == user_id,
                        func.date(LearningStats.date) == current_date
                    )
                )
            )
            stats = result.scalar_one_or_none()
            
            if stats and (stats.activity_count > 0 or stats.total_study_time > 0):
                streak += 1
                current_date = current_date - timedelta(days=1)
            else:
                break
            
            # 最多查询90天
            if streak >= 90:
                break
        
        return streak
    
    async def get_user_achievements(
        self,
        user_id: int,
        unlocked_only: bool = False
    ) -> List[Dict[str, Any]]:
        """获取用户成就列表"""
        query = (
            select(UserAchievement, Achievement)
            .join(Achievement, UserAchievement.achievement_id == Achievement.id)
            .where(UserAchievement.user_id == user_id)
        )
        
        if unlocked_only:
            query = query.where(UserAchievement.is_unlocked == True)
        
        query = query.order_by(UserAchievement.unlocked_at.desc())
        
        result = await self.db.execute(query)
        rows = result.all()
        
        achievements_list = []
        for user_achievement, achievement in rows:
            achievements_list.append({
                "id": achievement.id,
                "name": achievement.name,
                "title": achievement.title,
                "description": achievement.description,
                "icon": achievement.icon,
                "type": achievement.achievement_type.value,
                "requirement_value": achievement.requirement_value,
                "points": achievement.points,
                "rarity": achievement.rarity,
                "is_unlocked": user_achievement.is_unlocked,
                "progress_value": user_achievement.progress_value,
                "progress_percentage": min(
                    (user_achievement.progress_value / achievement.requirement_value * 100),
                    100
                ) if achievement.requirement_value > 0 else 0,
                "unlocked_at": user_achievement.unlocked_at.isoformat() if user_achievement.unlocked_at else None
            })
        
        return achievements_list
    
    async def get_achievement_summary(self, user_id: int) -> Dict[str, Any]:
        """获取成就摘要"""
        # 获取所有成就
        achievements = await self.get_user_achievements(user_id)
        
        unlocked_count = sum(1 for a in achievements if a["is_unlocked"])
        total_count = len(achievements)
        total_points = sum(a["points"] for a in achievements if a["is_unlocked"])
        
        # 按稀有度统计
        rarity_counts = {"common": 0, "rare": 0, "epic": 0, "legendary": 0}
        for a in achievements:
            if a["is_unlocked"]:
                rarity_counts[a["rarity"]] += 1
        
        return {
            "total_achievements": total_count,
            "unlocked_achievements": unlocked_count,
            "unlock_percentage": (unlocked_count / total_count * 100) if total_count > 0 else 0,
            "total_points": total_points,
            "rarity_distribution": rarity_counts,
            "recent_unlocked": [
                a for a in achievements
                if a["is_unlocked"]
            ][:5]
        }
