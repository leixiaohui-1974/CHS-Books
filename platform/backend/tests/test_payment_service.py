"""
支付服务测试
"""

import pytest
import pytest_asyncio
import os
os.environ["TESTING"] = "1"

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.models.book import Book
from app.models.payment import Order, OrderStatus, PaymentMethod
from app.services.payment_service import PaymentService


@pytest_asyncio.fixture
async def db_session():
    """测试数据库会话"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = async_session()
    
    yield session
    
    await session.close()
    await engine.dispose()


@pytest_asyncio.fixture
async def test_user(db_session):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_book(db_session):
    """创建测试书籍"""
    book = Book(
        slug="test-course",
        title="测试课程",
        description="测试描述",
        is_free=False,
        price=99.0
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)
    return book


@pytest.mark.asyncio
async def test_create_order(db_session, test_user, test_book):
    """测试创建订单"""
    order = await PaymentService.create_order(
        db_session,
        user_id=test_user.id,
        book_id=test_book.id,
        amount=99.0,
        payment_method=PaymentMethod.STRIPE
    )
    
    assert order.id is not None
    assert order.order_no.startswith("ORD")
    assert order.user_id == test_user.id
    assert order.book_id == test_book.id
    assert order.final_price == 99.0
    assert order.status == OrderStatus.PENDING
    assert order.payment_method == PaymentMethod.STRIPE


@pytest.mark.asyncio
async def test_process_stripe_payment(db_session, test_user, test_book):
    """测试Stripe支付处理"""
    # 创建订单
    order = await PaymentService.create_order(
        db_session,
        user_id=test_user.id,
        book_id=test_book.id,
        amount=99.0,
        payment_method=PaymentMethod.STRIPE
    )
    
    # 处理支付
    result = await PaymentService.process_stripe_payment(
        db_session,
        order.id,
        "tok_test_12345"
    )
    
    assert result["success"] is True
    assert result["order_no"] == order.order_no
    assert "paid_at" in result
    
    # 验证订单状态
    await db_session.refresh(order)
    assert order.status == OrderStatus.PAID
    assert order.payment_time is not None


@pytest.mark.asyncio
async def test_get_user_orders(db_session, test_user, test_book):
    """测试获取用户订单列表"""
    # 创建多个订单
    for i in range(3):
        await PaymentService.create_order(
            db_session,
            user_id=test_user.id,
            book_id=test_book.id,
            amount=99.0 + i
        )
    
    # 获取订单列表
    orders = await PaymentService.get_user_orders(db_session, test_user.id)
    
    assert len(orders) == 3
    assert all(order.user_id == test_user.id for order in orders)


@pytest.mark.asyncio
async def test_cancel_order(db_session, test_user, test_book):
    """测试取消订单"""
    # 创建订单
    order = await PaymentService.create_order(
        db_session,
        user_id=test_user.id,
        book_id=test_book.id,
        amount=99.0
    )
    
    # 取消订单
    cancelled_order = await PaymentService.cancel_order(
        db_session,
        order.id,
        "用户取消"
    )
    
    assert cancelled_order.status == OrderStatus.CANCELLED
    assert cancelled_order.cancelled_at is not None


@pytest.mark.asyncio
async def test_refund_order(db_session, test_user, test_book):
    """测试退款"""
    # 创建并支付订单
    order = await PaymentService.create_order(
        db_session,
        user_id=test_user.id,
        book_id=test_book.id,
        amount=99.0,
        payment_method=PaymentMethod.STRIPE
    )
    
    await PaymentService.process_stripe_payment(
        db_session,
        order.id,
        "tok_test_12345"
    )
    
    # 申请退款
    result = await PaymentService.refund_order(
        db_session,
        order.id,
        refund_amount=99.0,
        reason="用户申请"
    )
    
    assert result["success"] is True
    assert result["refund_amount"] == 99.0
    
    # 验证订单状态
    await db_session.refresh(order)
    assert order.status == OrderStatus.REFUNDED
    assert order.refund_time is not None


@pytest.mark.asyncio
async def test_get_order_by_no(db_session, test_user, test_book):
    """测试通过订单号获取订单"""
    # 创建订单
    order = await PaymentService.create_order(
        db_session,
        user_id=test_user.id,
        book_id=test_book.id,
        amount=99.0
    )
    
    # 通过订单号查询
    found_order = await PaymentService.get_order_by_no(db_session, order.order_no)
    
    assert found_order is not None
    assert found_order.id == order.id
    assert found_order.order_no == order.order_no
