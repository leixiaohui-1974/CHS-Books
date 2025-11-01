"""
会员体系测试
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.membership import (
    UserMembership, MembershipLevel, ExperienceHistory, MembershipConfig
)
from app.services.membership_service import membership_service


@pytest.mark.asyncio
async def test_create_membership(db_session: AsyncSession):
    """测试创建会员"""
    # 创建测试用户
    user = User(
        username="testuser_membership",
        email="membership@test.com",
        hashed_password="hashed_password",
        full_name="Membership Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建会员
    membership = await membership_service.get_or_create_membership(db_session, user.id)
    
    assert membership is not None
    assert membership.user_id == user.id
    assert membership.level == MembershipLevel.FREE
    assert membership.experience_points == 0


@pytest.mark.asyncio
async def test_add_experience(db_session: AsyncSession):
    """测试添加经验值"""
    # 创建测试用户
    user = User(
        username="testuser_exp",
        email="exp@test.com",
        hashed_password="hashed_password",
        full_name="Experience Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 添加经验值
    result = await membership_service.add_experience(
        db_session,
        user.id,
        amount=500,
        reason="完成案例测试"
    )
    
    assert result["success"] is True
    assert result["gained"] == 500
    assert result["new_experience"] == 500
    assert result["old_level"] in [None, MembershipLevel.FREE.value]
    assert result["new_level"] == MembershipLevel.BRONZE.value


@pytest.mark.asyncio
async def test_level_upgrade(db_session: AsyncSession):
    """测试等级升级"""
    # 创建测试用户
    user = User(
        username="testuser_upgrade",
        email="upgrade@test.com",
        hashed_password="hashed_password",
        full_name="Upgrade Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 添加足够的经验值升级到白银
    result = await membership_service.add_experience(
        db_session,
        user.id,
        amount=2000,
        reason="大量学习"
    )
    
    assert result["level_up"] is True
    assert result["new_level"] == MembershipLevel.SILVER.value
    assert result["new_experience"] == 2000


@pytest.mark.asyncio
async def test_get_membership_info(db_session: AsyncSession):
    """测试获取会员信息"""
    # 创建测试用户
    user = User(
        username="testuser_info",
        email="info@test.com",
        hashed_password="hashed_password",
        full_name="Info Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 添加经验值
    await membership_service.add_experience(
        db_session,
        user.id,
        amount=1500,
        reason="测试"
    )
    
    # 获取会员信息
    info = await membership_service.get_membership_info(db_session, user.id)
    
    assert info["user_id"] == user.id
    assert info["level"] == MembershipLevel.SILVER.value
    assert info["experience_points"] == 1500
    assert "level_progress" in info
    assert "next_level" in info


@pytest.mark.asyncio
async def test_experience_history(db_session: AsyncSession):
    """测试经验值历史"""
    # 创建测试用户
    user = User(
        username="testuser_history",
        email="history@test.com",
        hashed_password="hashed_password",
        full_name="History Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 多次添加经验值
    await membership_service.add_experience(db_session, user.id, 100, "任务1")
    await membership_service.add_experience(db_session, user.id, 200, "任务2")
    await membership_service.add_experience(db_session, user.id, 300, "任务3")
    
    # 获取历史记录
    history = await membership_service.get_experience_history(db_session, user.id, limit=10)
    
    assert len(history) == 3
    assert history[0]["amount"] == 300  # 最新的记录
    assert history[1]["amount"] == 200
    assert history[2]["amount"] == 100


@pytest.mark.asyncio
async def test_upgrade_membership_purchase(db_session: AsyncSession):
    """测试购买升级会员"""
    # 创建测试用户
    user = User(
        username="testuser_purchase",
        email="purchase@test.com",
        hashed_password="hashed_password",
        full_name="Purchase Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 购买升级到黄金会员
    result = await membership_service.upgrade_membership(
        db_session,
        user.id,
        target_level=MembershipLevel.GOLD,
        duration_days=30
    )
    
    assert result["success"] is True
    assert result["new_level"] == MembershipLevel.GOLD.value
    assert result["expires_at"] is not None


@pytest.mark.asyncio
async def test_lifetime_membership(db_session: AsyncSession):
    """测试终身会员"""
    # 创建测试用户
    user = User(
        username="testuser_lifetime",
        email="lifetime@test.com",
        hashed_password="hashed_password",
        full_name="Lifetime Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 购买终身钻石会员
    result = await membership_service.upgrade_membership(
        db_session,
        user.id,
        target_level=MembershipLevel.DIAMOND,
        is_lifetime=True
    )
    
    assert result["success"] is True
    assert result["new_level"] == MembershipLevel.DIAMOND.value
    assert result["is_lifetime"] is True
    assert result["expires_at"] is None


@pytest.mark.asyncio
async def test_multiple_level_upgrades(db_session: AsyncSession):
    """测试多次等级升级"""
    # 创建测试用户
    user = User(
        username="testuser_multi",
        email="multi@test.com",
        hashed_password="hashed_password",
        full_name="Multi Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 第一次升级
    result1 = await membership_service.add_experience(db_session, user.id, 800, "第一阶段")
    assert result1["new_level"] == MembershipLevel.BRONZE.value
    
    # 第二次升级
    result2 = await membership_service.add_experience(db_session, user.id, 1500, "第二阶段")
    assert result2["new_level"] == MembershipLevel.SILVER.value
    assert result2["new_experience"] == 2300
    
    # 第三次升级
    result3 = await membership_service.add_experience(db_session, user.id, 3000, "第三阶段")
    assert result3["new_level"] == MembershipLevel.GOLD.value
    assert result3["new_experience"] == 5300
    
    # 验证最终状态
    info = await membership_service.get_membership_info(db_session, user.id)
    assert info["level"] == MembershipLevel.GOLD.value
    assert info["experience_points"] == 5300
    assert info["upgrade_count"] == 3
