"""
学习路径规划服务
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.learning import (
    KnowledgePoint, UserKnowledgeProgress, LearningPath,
    DifficultyLevel, MasteryLevel
)


class LearningPathService:
    """学习路径规划服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_learning_path(
        self,
        user_id: int,
        name: str,
        knowledge_point_ids: List[int],
        target_subject_id: Optional[int] = None,
        description: Optional[str] = None,
        difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    ) -> LearningPath:
        """创建学习路径"""
        # 估算学习时长（每个知识点预估30分钟）
        estimated_hours = len(knowledge_point_ids) * 0.5
        
        path = LearningPath(
            user_id=user_id,
            name=name,
            description=description,
            target_subject_id=target_subject_id,
            knowledge_points=knowledge_point_ids,
            estimated_hours=int(estimated_hours),
            difficulty=difficulty,
            current_index=0,
            completed_count=0,
            progress_percentage=0.0,
            is_active=True,
            started_at=datetime.utcnow()
        )
        
        self.db.add(path)
        await self.db.commit()
        await self.db.refresh(path)
        
        return path
    
    async def generate_adaptive_path(
        self,
        user_id: int,
        subject_id: int,
        target_difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    ) -> LearningPath:
        """
        生成自适应学习路径
        根据用户当前掌握情况和目标难度，智能规划学习路径
        """
        # 1. 获取该学科的所有知识点
        result = await self.db.execute(
            select(KnowledgePoint)
            .join(KnowledgePoint.chapter)
            .where(
                and_(
                    KnowledgePoint.chapter.has(subject_id=subject_id),
                    KnowledgePoint.is_active == True
                )
            )
            .order_by(KnowledgePoint.order)
        )
        all_kps = list(result.scalars().all())
        
        # 2. 获取用户已有的进度
        progress_result = await self.db.execute(
            select(UserKnowledgeProgress).where(
                and_(
                    UserKnowledgeProgress.user_id == user_id,
                    UserKnowledgeProgress.knowledge_point_id.in_([kp.id for kp in all_kps])
                )
            )
        )
        user_progress_map = {
            progress.knowledge_point_id: progress
            for progress in progress_result.scalars().all()
        }
        
        # 3. 智能排序知识点
        planned_kps = []
        
        for kp in all_kps:
            progress = user_progress_map.get(kp.id)
            
            # 跳过已精通的知识点
            if progress and progress.mastery_level == MasteryLevel.EXPERT:
                continue
            
            # 检查前置条件
            if kp.prerequisites:
                prerequisites_met = True
                for prereq_id in kp.prerequisites:
                    prereq_progress = user_progress_map.get(prereq_id)
                    if not prereq_progress or prereq_progress.mastery_level not in [
                        MasteryLevel.MASTERED, MasteryLevel.EXPERT
                    ]:
                        prerequisites_met = False
                        break
                
                if not prerequisites_met:
                    continue
            
            # 根据难度筛选
            if target_difficulty == DifficultyLevel.BEGINNER:
                if kp.difficulty in [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE]:
                    planned_kps.append(kp)
            elif target_difficulty == DifficultyLevel.INTERMEDIATE:
                if kp.difficulty in [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED]:
                    planned_kps.append(kp)
            else:
                planned_kps.append(kp)
        
        # 4. 按优先级排序
        # 优先学习：未开始 > 学习中 > 练习中
        def get_priority(kp: KnowledgePoint) -> tuple:
            progress = user_progress_map.get(kp.id)
            
            if not progress or progress.mastery_level == MasteryLevel.NOT_STARTED:
                priority = 1
            elif progress.mastery_level == MasteryLevel.LEARNING:
                priority = 2
            else:
                priority = 3
            
            # 难度低的优先
            difficulty_order = {
                DifficultyLevel.BEGINNER: 1,
                DifficultyLevel.INTERMEDIATE: 2,
                DifficultyLevel.ADVANCED: 3,
                DifficultyLevel.EXPERT: 4
            }
            
            return (priority, difficulty_order.get(kp.difficulty, 2), kp.order)
        
        planned_kps.sort(key=get_priority)
        
        # 5. 创建学习路径
        path_name = f"自适应学习路径 - {target_difficulty.value}"
        path_description = f"根据您的学习情况智能生成的{target_difficulty.value}难度学习路径"
        
        return await self.create_learning_path(
            user_id=user_id,
            name=path_name,
            knowledge_point_ids=[kp.id for kp in planned_kps],
            target_subject_id=subject_id,
            description=path_description,
            difficulty=target_difficulty
        )
    
    async def update_path_progress(
        self,
        path_id: int,
        completed_knowledge_point_id: int
    ) -> LearningPath:
        """更新路径进度"""
        result = await self.db.execute(
            select(LearningPath).where(LearningPath.id == path_id)
        )
        path = result.scalar_one_or_none()
        
        if not path:
            return None
        
        # 检查知识点是否在路径中
        if completed_knowledge_point_id in path.knowledge_points:
            # 更新完成数
            if completed_knowledge_point_id not in path.knowledge_points[:path.completed_count]:
                path.completed_count += 1
                
                # 更新当前索引
                try:
                    current_index = path.knowledge_points.index(completed_knowledge_point_id)
                    if current_index >= path.current_index:
                        path.current_index = current_index + 1
                except ValueError:
                    pass
                
                # 更新进度百分比
                total = len(path.knowledge_points)
                path.progress_percentage = (path.completed_count / total * 100) if total > 0 else 0
                
                # 检查是否完成
                if path.completed_count >= total:
                    path.completed_at = datetime.utcnow()
                    path.is_active = False
                
                await self.db.commit()
                await self.db.refresh(path)
        
        return path
    
    async def get_user_paths(
        self,
        user_id: int,
        is_active: Optional[bool] = None
    ) -> List[LearningPath]:
        """获取用户的学习路径"""
        query = select(LearningPath).where(LearningPath.user_id == user_id)
        
        if is_active is not None:
            query = query.where(LearningPath.is_active == is_active)
        
        query = query.order_by(LearningPath.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_path_details(self, path_id: int) -> Dict[str, Any]:
        """获取路径详情（包括知识点信息）"""
        result = await self.db.execute(
            select(LearningPath).where(LearningPath.id == path_id)
        )
        path = result.scalar_one_or_none()
        
        if not path:
            return None
        
        # 获取所有知识点详情
        kp_result = await self.db.execute(
            select(KnowledgePoint).where(
                KnowledgePoint.id.in_(path.knowledge_points)
            )
        )
        kps_map = {kp.id: kp for kp in kp_result.scalars().all()}
        
        # 按路径顺序排列知识点
        ordered_kps = []
        for kp_id in path.knowledge_points:
            if kp_id in kps_map:
                ordered_kps.append(kps_map[kp_id])
        
        # 获取用户进度
        progress_result = await self.db.execute(
            select(UserKnowledgeProgress).where(
                and_(
                    UserKnowledgeProgress.user_id == path.user_id,
                    UserKnowledgeProgress.knowledge_point_id.in_(path.knowledge_points)
                )
            )
        )
        progress_map = {
            p.knowledge_point_id: p
            for p in progress_result.scalars().all()
        }
        
        # 构造详细信息
        knowledge_points_details = []
        for i, kp in enumerate(ordered_kps):
            progress = progress_map.get(kp.id)
            knowledge_points_details.append({
                "id": kp.id,
                "name": kp.name,
                "description": kp.description,
                "difficulty": kp.difficulty.value,
                "order_in_path": i,
                "is_current": i == path.current_index,
                "is_completed": i < path.completed_count,
                "mastery_level": progress.mastery_level.value if progress else "not_started",
                "mastery_score": progress.mastery_score if progress else 0.0,
                "study_time": progress.study_time if progress else 0,
                "practice_count": progress.practice_count if progress else 0
            })
        
        return {
            "id": path.id,
            "name": path.name,
            "description": path.description,
            "difficulty": path.difficulty.value,
            "estimated_hours": path.estimated_hours,
            "progress_percentage": path.progress_percentage,
            "current_index": path.current_index,
            "completed_count": path.completed_count,
            "total_count": len(path.knowledge_points),
            "is_active": path.is_active,
            "started_at": path.started_at.isoformat() if path.started_at else None,
            "completed_at": path.completed_at.isoformat() if path.completed_at else None,
            "knowledge_points": knowledge_points_details
        }
    
    async def get_recommended_next_points(
        self,
        user_id: int,
        path_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """获取推荐的下一批学习知识点"""
        path_details = await self.get_path_details(path_id)
        
        if not path_details:
            return []
        
        # 找出未完成的知识点
        unfinished_points = [
            kp for kp in path_details["knowledge_points"]
            if not kp["is_completed"]
        ]
        
        # 返回前N个
        return unfinished_points[:limit]
    
    async def suggest_review_points(
        self,
        user_id: int,
        path_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """建议需要复习的知识点"""
        path_details = await self.get_path_details(path_id)
        
        if not path_details:
            return []
        
        # 找出已学习但掌握度不高的知识点
        review_candidates = [
            kp for kp in path_details["knowledge_points"]
            if kp["mastery_level"] in ["learning", "practicing"]
            and kp["mastery_score"] < 80
        ]
        
        # 按掌握度排序（低的优先）
        review_candidates.sort(key=lambda x: x["mastery_score"])
        
        return review_candidates[:limit]
