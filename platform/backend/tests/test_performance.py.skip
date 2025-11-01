#!/usr/bin/env python3
"""
性能测试
测试API端点的响应时间和并发能力
"""

import asyncio
import time
import pytest
import pytest_asyncio
import os
from httpx import AsyncClient

# 设置测试环境
os.environ["TESTING"] = "1"

from app.main import app
from app.core.config import settings


@pytest.mark.asyncio
async def test_api_response_time():
    """测试API响应时间"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 健康检查
        start = time.time()
        response = await client.get("/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.1, f"健康检查响应时间过长: {elapsed:.3f}s"
        print(f"✅ 健康检查响应时间: {elapsed*1000:.2f}ms")


@pytest.mark.asyncio
async def test_book_list_performance():
    """测试书籍列表性能"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        start = time.time()
        response = await client.get("/api/v1/books?page=1&page_size=10")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.5, f"书籍列表响应时间过长: {elapsed:.3f}s"
        print(f"✅ 书籍列表响应时间: {elapsed*1000:.2f}ms")


@pytest.mark.asyncio
async def test_concurrent_requests():
    """测试并发请求处理能力"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 模拟10个并发请求
        tasks = []
        for _ in range(10):
            task = client.get("/health")
            tasks.append(task)
        
        start = time.time()
        responses = await asyncio.gather(*tasks)
        elapsed = time.time() - start
        
        # 检查所有请求都成功
        assert all(r.status_code == 200 for r in responses)
        
        # 平均响应时间
        avg_time = elapsed / 10
        assert avg_time < 0.1, f"平均响应时间过长: {avg_time:.3f}s"
        print(f"✅ 10个并发请求总时间: {elapsed*1000:.2f}ms")
        print(f"✅ 平均响应时间: {avg_time*1000:.2f}ms")


@pytest.mark.asyncio
@pytest_asyncio.fixture
async def db_session():
    """数据库会话fixture"""
    from app.core.database import async_session
    session = async_session()
    yield session
    await session.close()


@pytest.mark.asyncio
async def test_database_query_performance(db_session):
    """测试数据库查询性能"""
    from app.models.user import User
    from sqlalchemy import select
    
    # 创建测试用户
    for i in range(50):
        user = User(
            email=f"perf_test_{i}@example.com",
            username=f"perf_user_{i}",
            hashed_password="hashed"
        )
        db_session.add(user)
    await db_session.commit()
    
    # 测试查询性能
    start = time.time()
    result = await db_session.execute(
        select(User).where(User.email.like("perf_test_%")).limit(20)
    )
    users = result.scalars().all()
    elapsed = time.time() - start
    
    assert len(users) == 20
    assert elapsed < 0.1, f"数据库查询时间过长: {elapsed:.3f}s"
    print(f"✅ 数据库查询20条记录: {elapsed*1000:.2f}ms")
    
    # 清理测试数据
    for user in users:
        await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_large_payload_handling():
    """测试大数据量处理"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 模拟大量查询参数
        start = time.time()
        response = await client.get(
            "/api/v1/books",
            params={
                "page": 1,
                "page_size": 50,
                "search": "水",
                "difficulty": "beginner"
            }
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0, f"大数据量查询时间过长: {elapsed:.3f}s"
        print(f"✅ 大数据量查询响应时间: {elapsed*1000:.2f}ms")


@pytest.mark.asyncio
async def test_endpoint_stress():
    """压力测试 - 快速连续请求"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        start = time.time()
        
        # 连续发送100个请求
        for _ in range(100):
            response = await client.get("/health")
            assert response.status_code == 200
        
        elapsed = time.time() - start
        qps = 100 / elapsed
        
        print(f"✅ 100个连续请求总时间: {elapsed:.2f}s")
        print(f"✅ QPS: {qps:.2f} 请求/秒")
        assert qps > 50, f"QPS过低: {qps:.2f}"


def test_memory_usage():
    """测试内存使用情况"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / 1024 / 1024
    
    print(f"✅ 当前内存使用: {memory_mb:.2f}MB")
    assert memory_mb < 500, f"内存使用过高: {memory_mb:.2f}MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
