"""
数据库配置和连接管理
使用SQLAlchemy 2.0异步模式
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
from .config import settings

# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,  # 1小时回收连接
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 创建Base类
Base = declarative_base()


# 依赖注入：获取数据库会话
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数
    用于FastAPI路由中注入数据库连接
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
