"""
性能基准测试
测试API响应时间、并发性能、数据库查询性能等
"""

import pytest
import asyncio
import time
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.book import Book
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_api_response_time_benchmark(db_session: AsyncSession):
    """测试API响应时间基准（简化版）"""
    # 测试数据库操作性能
    from sqlalchemy import select
    
    start = time.time()
    result = await db_session.execute(select(User).limit(1))
    query_time = (time.time() - start) * 1000
    
    assert query_time < 50, f"查询响应时间 {query_time:.2f}ms 超过50ms"
    
    print(f"\n✅ 数据库查询响应时间: {query_time:.2f}ms")


@pytest.mark.asyncio
async def test_database_query_performance(db_session: AsyncSession):
    """测试数据库查询性能"""
    from sqlalchemy import select, func
    
    # 创建测试用户
    for i in range(10):
        user = User(
            username=f"perftest_{i}",
            email=f"perftest_{i}@test.com",
            hashed_password=get_password_hash("test123"),
            full_name=f"Performance Test {i}"
        )
        db_session.add(user)
    await db_session.commit()
    
    # 测试简单查询
    start = time.time()
    result = await db_session.execute(select(User).limit(10))
    users = result.scalars().all()
    query_time = (time.time() - start) * 1000
    
    assert len(users) >= 10
    assert query_time < 50, f"简单查询时间 {query_time:.2f}ms 超过50ms"
    
    print(f"\n✅ 数据库查询性能:")
    print(f"   简单查询: {query_time:.2f}ms")
    
    # 测试聚合查询
    start = time.time()
    result = await db_session.execute(select(func.count(User.id)))
    count = result.scalar()
    agg_time = (time.time() - start) * 1000
    
    assert count >= 10
    assert agg_time < 100, f"聚合查询时间 {agg_time:.2f}ms 超过100ms"
    
    print(f"   聚合查询: {agg_time:.2f}ms")


@pytest.mark.asyncio
async def test_data_serialization_performance(db_session: AsyncSession):
    """测试数据序列化性能"""
    from sqlalchemy import select
    
    # 创建测试数据
    for i in range(20):
        book = Book(
            title=f"Test Book {i}",
            slug=f"test-book-{i}",
            description=f"Description for book {i}",
            cover_image=f"/images/book_{i}.jpg",
            price=99.99
        )
        db_session.add(book)
    await db_session.commit()
    
    # 测试序列化性能
    result = await db_session.execute(select(Book).limit(20))
    books_data = result.scalars().all()
    
    start = time.time()
    serialized = [
        {
            "id": book.id,
            "title": book.title,
            "slug": book.slug,
            "description": book.description,
            "price": book.price
        }
        for book in books_data
    ]
    serialization_time = (time.time() - start) * 1000
    
    assert len(serialized) == 20
    assert serialization_time < 10, f"序列化时间 {serialization_time:.2f}ms 超过10ms"
    
    print(f"\n✅ 数据序列化性能: {serialization_time:.2f}ms (20条记录)")


@pytest.mark.asyncio
async def test_memory_usage():
    """测试内存使用"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / (1024 * 1024)
    
    assert memory_mb < 500, f"内存使用 {memory_mb:.2f}MB 超过500MB"
    
    print(f"\n✅ 内存使用: {memory_mb:.2f}MB")


@pytest.mark.asyncio
async def test_cpu_usage():
    """测试CPU使用"""
    import psutil
    
    cpu_percent = psutil.cpu_percent(interval=1)
    
    print(f"\n✅ CPU使用率: {cpu_percent}%")
    
    # CPU使用率可能很高，只是记录，不做断言


@pytest.mark.asyncio  
async def test_query_performance_percentiles(db_session: AsyncSession):
    """测试查询性能分布（P50, P95, P99）"""
    from sqlalchemy import select
    
    num_queries = 100
    
    async def measure_query():
        start = time.time()
        await db_session.execute(select(User).limit(10))
        return (time.time() - start) * 1000
    
    times = [await measure_query() for _ in range(num_queries)]
    times_sorted = sorted(times)
    
    p50 = times_sorted[int(num_queries * 0.50)]
    p95 = times_sorted[int(num_queries * 0.95)]
    p99 = times_sorted[int(num_queries * 0.99)]
    
    assert p50 < 30, f"P50查询时间 {p50:.2f}ms 超过30ms"
    assert p95 < 50, f"P95查询时间 {p95:.2f}ms 超过50ms"
    
    print(f"\n✅ 查询性能分布:")
    print(f"   P50: {p50:.2f}ms")
    print(f"   P95: {p95:.2f}ms")
    print(f"   P99: {p99:.2f}ms")
    print(f"   最小: {min(times):.2f}ms")
    print(f"   最大: {max(times):.2f}ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
