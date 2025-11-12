"""
数据库连接 - 独立Textbook服务器
使用SQLite进行开发测试
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from typing import AsyncGenerator
from models import Base

# SQLite数据库URL
DATABASE_URL = "sqlite+aiosqlite:///./textbook_test.db"

# 创建异步引擎（SQLite需要StaticPool和check_same_thread=False）
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 打印SQL语句
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    """初始化数据库（创建所有表）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数
    用于FastAPI路由
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
