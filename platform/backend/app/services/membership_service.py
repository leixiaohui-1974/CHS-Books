"""
会员体系服务
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from loguru import logger

from app.models.membership import (
    UserMembership, ExperienceHistory, MembershipConfig,
    MembershipLevel, BenefitType
)
from app.models.user import User


class MembershipService:
    """会员体系服务"""
    
    # 会员等级经验值范围
    LEVEL_RANGES = {
        MembershipLevel.FREE: (0, 0),
        MembershipLevel.BRONZE: (0, 1000),
        MembershipLevel.SILVER: (1001, 5000),
        MembershipLevel.GOLD: (5001, 10000),
        MembershipLevel.PLATINUM: (10001, 30000),
        MembershipLevel.DIAMOND: (30001, float('inf'))
    }
    
    async def get_or_create_membership(
        self,
        db: AsyncSession,
        user_id: int
    ) -> UserMembership:
        """获取或创建用户会员信息"""
        try:
            # 查询用户会员信息
            result = await db.execute(
                select(UserMembership).where(UserMembership.user_id == user_id)
            )
            membership = result.scalar_one_or_none()
            
            if not membership:
                # 创建新会员信息
                membership = UserMembership(
                    user_id=user_id,
                    level=MembershipLevel.FREE,
                    experience_points=0,
                    benefits_usage={}
                )
                db.add(membership)
                await db.commit()
                await db.refresh(membership)
                logger.info(f"Created new membership for user {user_id}")
            
            return membership
            
        except Exception as e:
            logger.error(f"Failed to get/create membership: {str(e)}")
            await db.rollback()
            raise
    
    async def add_experience(
        self,
        db: AsyncSession,
        user_id: int,
        amount: int,
        reason: str,
        related_type: Optional[str] = None,
        related_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """添加经验值"""
        try:
            membership = await self.get_or_create_membership(db, user_id)
            old_level = membership.level
            old_exp = membership.experience_points
            
            # 增加经验值
            membership.experience_points += amount
            
            # 记录经验值历史
            exp_history = ExperienceHistory(
                user_membership_id=membership.id,
                amount=amount,
                reason=reason,
                related_type=related_type,
                related_id=related_id
            )
            db.add(exp_history)
            
            # 检查是否升级
            new_level = self._calculate_level(membership.experience_points)
            level_up = False
            
            if new_level != old_level:
                membership.level = new_level
                membership.last_upgrade_at = datetime.now(timezone.utc)
                membership.upgrade_count += 1
                level_up = True
                logger.info(f"User {user_id} leveled up: {old_level} -> {new_level}")
            
            await db.commit()
            await db.refresh(membership)
            
            return {
                "success": True,
                "old_experience": old_exp,
                "new_experience": membership.experience_points,
                "gained": amount,
                "old_level": old_level.value if old_level else None,
                "new_level": new_level.value,
                "level_up": level_up
            }
            
        except Exception as e:
            logger.error(f"Failed to add experience: {str(e)}")
            await db.rollback()
            raise
    
    async def get_membership_info(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """获取会员信息"""
        try:
            membership = await self.get_or_create_membership(db, user_id)
            
            # 获取会员配置
            config = await self._get_level_config(db, membership.level)
            
            # 计算等级进度
            progress = membership.level_progress
            
            # 获取下一等级
            next_level = self._get_next_level(membership.level)
            next_level_exp = None
            if next_level:
                _, max_exp = self.LEVEL_RANGES[next_level]
                next_level_exp = max_exp if max_exp != float('inf') else None
            
            return {
                "user_id": user_id,
                "level": membership.level.value,
                "level_name": config.get("name", "未知"),
                "experience_points": membership.experience_points,
                "level_progress": round(progress, 2),
                "next_level": next_level.value if next_level else None,
                "next_level_exp": next_level_exp,
                "is_lifetime": membership.is_lifetime,
                "expires_at": membership.expires_at.isoformat() if membership.expires_at else None,
                "total_spent": membership.total_spent,
                "upgrade_count": membership.upgrade_count,
                "benefits": config.get("benefits", {}),
                "benefits_usage": membership.benefits_usage or {}
            }
            
        except Exception as e:
            logger.error(f"Failed to get membership info: {str(e)}")
            raise
    
    async def get_experience_history(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取经验值历史"""
        try:
            membership = await self.get_or_create_membership(db, user_id)
            
            result = await db.execute(
                select(ExperienceHistory)
                .where(ExperienceHistory.user_membership_id == membership.id)
                .order_by(ExperienceHistory.created_at.desc())
                .limit(limit)
            )
            history = result.scalars().all()
            
            return [
                {
                    "amount": h.amount,
                    "reason": h.reason,
                    "related_type": h.related_type,
                    "related_id": h.related_id,
                    "created_at": h.created_at.isoformat()
                }
                for h in history
            ]
            
        except Exception as e:
            logger.error(f"Failed to get experience history: {str(e)}")
            raise
    
    async def use_benefit(
        self,
        db: AsyncSession,
        user_id: int,
        benefit_type: BenefitType,
        amount: int = 1
    ) -> Dict[str, Any]:
        """使用会员权益"""
        try:
            membership = await self.get_or_create_membership(db, user_id)
            
            # 获取权益配置
            config = await self._get_level_config(db, membership.level)
            benefits = config.get("benefits", {})
            
            benefit_key = benefit_type.value
            if benefit_key not in benefits:
                raise ValueError(f"该等级没有{benefit_key}权益")
            
            # 检查使用次数
            usage = membership.benefits_usage or {}
            if benefit_key not in usage:
                usage[benefit_key] = {"used": 0, "total": benefits[benefit_key]}
            
            if usage[benefit_key]["used"] + amount > usage[benefit_key]["total"]:
                raise ValueError(f"{benefit_key}权益次数不足")
            
            # 更新使用次数
            usage[benefit_key]["used"] += amount
            membership.benefits_usage = usage
            
            await db.commit()
            
            return {
                "success": True,
                "benefit_type": benefit_key,
                "used": usage[benefit_key]["used"],
                "total": usage[benefit_key]["total"],
                "remaining": usage[benefit_key]["total"] - usage[benefit_key]["used"]
            }
            
        except Exception as e:
            logger.error(f"Failed to use benefit: {str(e)}")
            await db.rollback()
            raise
    
    async def upgrade_membership(
        self,
        db: AsyncSession,
        user_id: int,
        target_level: MembershipLevel,
        duration_days: Optional[int] = None,
        is_lifetime: bool = False
    ) -> Dict[str, Any]:
        """升级会员（通过购买）"""
        try:
            membership = await self.get_or_create_membership(db, user_id)
            
            # 更新会员等级
            old_level = membership.level
            membership.level = target_level
            membership.last_upgrade_at = datetime.now(timezone.utc)
            membership.upgrade_count += 1
            
            # 设置会员期限
            if is_lifetime:
                membership.is_lifetime = True
                membership.expires_at = None
            elif duration_days:
                if membership.expires_at and membership.expires_at > datetime.now(timezone.utc):
                    # 在现有期限基础上延长
                    membership.expires_at += timedelta(days=duration_days)
                else:
                    # 从现在开始计算
                    membership.expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)
            
            await db.commit()
            await db.refresh(membership)
            
            logger.info(f"User {user_id} upgraded membership: {old_level} -> {target_level}")
            
            return {
                "success": True,
                "old_level": old_level.value,
                "new_level": target_level.value,
                "is_lifetime": membership.is_lifetime,
                "expires_at": membership.expires_at.isoformat() if membership.expires_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to upgrade membership: {str(e)}")
            await db.rollback()
            raise
    
    def _calculate_level(self, experience: int) -> MembershipLevel:
        """根据经验值计算会员等级"""
        for level, (min_exp, max_exp) in self.LEVEL_RANGES.items():
            if level == MembershipLevel.FREE:
                continue
            if min_exp <= experience <= max_exp:
                return level
        return MembershipLevel.DIAMOND
    
    def _get_next_level(self, current_level: MembershipLevel) -> Optional[MembershipLevel]:
        """获取下一等级"""
        levels = [
            MembershipLevel.FREE,
            MembershipLevel.BRONZE,
            MembershipLevel.SILVER,
            MembershipLevel.GOLD,
            MembershipLevel.PLATINUM,
            MembershipLevel.DIAMOND
        ]
        
        try:
            current_index = levels.index(current_level)
            if current_index < len(levels) - 1:
                return levels[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    async def _get_level_config(
        self,
        db: AsyncSession,
        level: MembershipLevel
    ) -> Dict[str, Any]:
        """获取等级配置"""
        try:
            result = await db.execute(
                select(MembershipConfig).where(MembershipConfig.level == level)
            )
            config = result.scalar_one_or_none()
            
            if config:
                return {
                    "name": config.name,
                    "description": config.description,
                    "benefits": config.benefits or {},
                    "monthly_price": config.monthly_price,
                    "yearly_price": config.yearly_price,
                    "lifetime_price": config.lifetime_price
                }
            
            # 返回默认配置
            return {
                "name": level.value.title(),
                "description": f"{level.value}会员",
                "benefits": {},
                "monthly_price": None,
                "yearly_price": None,
                "lifetime_price": None
            }
            
        except Exception as e:
            logger.error(f"Failed to get level config: {str(e)}")
            return {}


# 创建全局实例
membership_service = MembershipService()
