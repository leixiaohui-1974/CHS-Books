"""
积分系统测试
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.points import (
    PointsAccount, PointsTransaction, PointsProduct, PointsRule,
    TransactionType, PointsReason, ProductType
)
from app.services.points_service import points_service


@pytest.mark.asyncio
async def test_create_points_account(db_session: AsyncSession):
    """测试创建积分账户"""
    # 创建测试用户
    user = User(
        username="testuser_points",
        email="points@test.com",
        hashed_password="hashed_password",
        full_name="Points Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建积分账户
    account = await points_service.get_or_create_account(db_session, user.id)
    
    assert account is not None
    assert account.user_id == user.id
    assert account.balance == 0
    assert account.total_earned == 0
    assert account.total_spent == 0


@pytest.mark.asyncio
async def test_earn_points(db_session: AsyncSession):
    """测试获得积分"""
    # 创建测试用户
    user = User(
        username="testuser_earn",
        email="earn@test.com",
        hashed_password="hashed_password",
        full_name="Earn Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建积分规则
    rule = PointsRule(
        reason=PointsReason.CASE_COMPLETE,
        points=20,
        description="完成案例",
        is_active=True
    )
    db_session.add(rule)
    await db_session.commit()
    
    # 获得积分
    result = await points_service.earn_points(
        db_session,
        user.id,
        reason=PointsReason.CASE_COMPLETE
    )
    
    assert result["success"] is True
    assert result["amount"] == 20
    assert result["balance"] == 20


@pytest.mark.asyncio
async def test_spend_points(db_session: AsyncSession):
    """测试消费积分"""
    # 创建测试用户
    user = User(
        username="testuser_spend",
        email="spend@test.com",
        hashed_password="hashed_password",
        full_name="Spend Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 先赚取积分
    account = await points_service.get_or_create_account(db_session, user.id)
    account.balance = 100
    account.total_earned = 100
    await db_session.commit()
    
    # 消费积分
    result = await points_service.spend_points(
        db_session,
        user.id,
        amount=30,
        reason=PointsReason.REDEEM_COUPON,
        description="兑换优惠券"
    )
    
    assert result["success"] is True
    assert result["amount"] == 30
    assert result["balance"] == 70


@pytest.mark.asyncio
async def test_insufficient_points(db_session: AsyncSession):
    """测试积分不足"""
    # 创建测试用户
    user = User(
        username="testuser_insufficient",
        email="insufficient@test.com",
        hashed_password="hashed_password",
        full_name="Insufficient Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 尝试消费超过余额的积分
    with pytest.raises(ValueError, match="积分余额不足"):
        await points_service.spend_points(
            db_session,
            user.id,
            amount=100,
            reason=PointsReason.REDEEM_COUPON
        )


@pytest.mark.asyncio
async def test_get_account_info(db_session: AsyncSession):
    """测试获取账户信息"""
    # 创建测试用户
    user = User(
        username="testuser_account",
        email="account@test.com",
        hashed_password="hashed_password",
        full_name="Account Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建账户并设置余额
    account = await points_service.get_or_create_account(db_session, user.id)
    account.balance = 200
    account.total_earned = 300
    account.total_spent = 100
    await db_session.commit()
    
    # 获取账户信息
    info = await points_service.get_account_info(db_session, user.id)
    
    assert info["balance"] == 200
    assert info["total_earned"] == 300
    assert info["total_spent"] == 100
    assert info["available"] == 200


@pytest.mark.asyncio
async def test_get_transactions(db_session: AsyncSession):
    """测试获取交易记录"""
    # 创建测试用户
    user = User(
        username="testuser_trans",
        email="trans@test.com",
        hashed_password="hashed_password",
        full_name="Transaction Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建积分账户
    account = await points_service.get_or_create_account(db_session, user.id)
    account.balance = 200
    await db_session.commit()
    
    # 创建交易记录
    trans1 = PointsTransaction(
        account_id=account.id,
        transaction_type=TransactionType.EARN,
        amount=100,
        reason=PointsReason.DAILY_LOGIN,
        description="每日登录",
        balance_before=0,
        balance_after=100
    )
    trans2 = PointsTransaction(
        account_id=account.id,
        transaction_type=TransactionType.EARN,
        amount=100,
        reason=PointsReason.CASE_COMPLETE,
        description="完成案例",
        balance_before=100,
        balance_after=200
    )
    db_session.add_all([trans1, trans2])
    await db_session.commit()
    
    # 获取交易记录
    transactions = await points_service.get_transactions(db_session, user.id, limit=10)
    
    assert len(transactions) == 2
    assert transactions[0]["amount"] == 100  # 最新的记录


@pytest.mark.asyncio
async def test_create_product(db_session: AsyncSession):
    """测试创建积分商品"""
    # 创建商品
    product = PointsProduct(
        name="10元优惠券",
        description="全场通用优惠券",
        product_type=ProductType.COUPON,
        points_cost=50,
        stock=100,
        is_active=True
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    
    assert product.id is not None
    assert product.name == "10元优惠券"
    assert product.points_cost == 50


@pytest.mark.asyncio
async def test_get_products(db_session: AsyncSession):
    """测试获取商品列表"""
    # 创建测试用户
    user = User(
        username="testuser_products",
        email="products@test.com",
        hashed_password="hashed_password",
        full_name="Products Test"
    )
    db_session.add(user)
    
    # 创建多个商品
    products = [
        PointsProduct(
            name="5元优惠券",
            product_type=ProductType.COUPON,
            points_cost=25,
            is_active=True
        ),
        PointsProduct(
            name="Python课程",
            product_type=ProductType.COURSE,
            points_cost=500,
            is_active=True
        ),
        PointsProduct(
            name="VIP会员月卡",
            product_type=ProductType.MEMBERSHIP,
            points_cost=1000,
            is_active=True
        )
    ]
    db_session.add_all(products)
    await db_session.commit()
    
    # 获取所有商品
    result = await points_service.get_products(db_session)
    assert len(result) >= 3
    
    # 获取优惠券类商品
    coupons = await points_service.get_products(db_session, product_type=ProductType.COUPON)
    assert len(coupons) >= 1
    assert all(p["type"] == ProductType.COUPON.value for p in coupons)


@pytest.mark.asyncio
async def test_redeem_product(db_session: AsyncSession):
    """测试兑换商品"""
    # 创建测试用户
    user = User(
        username="testuser_redeem",
        email="redeem@test.com",
        hashed_password="hashed_password",
        full_name="Redeem Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建积分账户并设置余额
    account = await points_service.get_or_create_account(db_session, user.id)
    account.balance = 100
    await db_session.commit()
    
    # 创建商品
    product = PointsProduct(
        name="测试优惠券",
        product_type=ProductType.COUPON,
        points_cost=50,
        stock=10,
        is_active=True
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    
    # 兑换商品
    result = await points_service.redeem_product(
        db_session,
        user.id,
        product.id,
        quantity=1
    )
    
    assert result["success"] is True
    assert result["points_cost"] == 50
    assert result["balance"] == 50  # 100 - 50
    
    # 验证库存减少
    await db_session.refresh(product)
    assert product.stock == 9
    assert product.sold_count == 1


@pytest.mark.asyncio
async def test_redeem_out_of_stock(db_session: AsyncSession):
    """测试兑换缺货商品"""
    # 创建测试用户
    user = User(
        username="testuser_oos",
        email="oos@test.com",
        hashed_password="hashed_password",
        full_name="OOS Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建积分账户
    account = await points_service.get_or_create_account(db_session, user.id)
    account.balance = 100
    await db_session.commit()
    
    # 创建缺货商品
    product = PointsProduct(
        name="缺货商品",
        product_type=ProductType.GIFT,
        points_cost=50,
        stock=0,
        is_active=True
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    
    # 尝试兑换
    with pytest.raises(ValueError, match="库存不足"):
        await points_service.redeem_product(db_session, user.id, product.id)


@pytest.mark.asyncio
async def test_points_transaction_flow(db_session: AsyncSession):
    """测试完整的积分流程"""
    # 创建测试用户
    user = User(
        username="testuser_flow",
        email="flow@test.com",
        hashed_password="hashed_password",
        full_name="Flow Test"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建积分规则
    rules = [
        PointsRule(
            reason=PointsReason.DAILY_LOGIN,
            points=10,
            description="每日登录",
            daily_limit=1,
            is_active=True
        ),
        PointsRule(
            reason=PointsReason.CASE_COMPLETE,
            points=20,
            description="完成案例",
            is_active=True
        )
    ]
    db_session.add_all(rules)
    await db_session.commit()
    
    # 1. 每日登录获得积分
    result1 = await points_service.earn_points(
        db_session,
        user.id,
        reason=PointsReason.DAILY_LOGIN
    )
    assert result1["balance"] == 10
    
    # 2. 完成案例获得积分
    result2 = await points_service.earn_points(
        db_session,
        user.id,
        reason=PointsReason.CASE_COMPLETE
    )
    assert result2["balance"] == 30
    
    # 3. 创建并兑换商品
    product = PointsProduct(
        name="测试商品",
        product_type=ProductType.COUPON,
        points_cost=20,
        stock=10,
        is_active=True
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    
    result3 = await points_service.redeem_product(db_session, user.id, product.id)
    assert result3["success"] is True
    assert result3["balance"] == 10  # 30 - 20
    
    # 4. 验证最终账户状态
    info = await points_service.get_account_info(db_session, user.id)
    assert info["balance"] == 10
    assert info["total_earned"] == 30
    assert info["total_spent"] == 20
