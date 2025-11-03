"""
数据库初始化脚本
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from loguru import logger

from app.core.config import settings
from app.core.database import Base

# 导入所有模型以确保它们被注册
from app.models.user import User
from app.models.session import UserSession, CodeExecution


async def init_database():
    """初始化数据库表"""
    logger.info("🚀 开始初始化数据库...")
    
    # 创建引擎
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True
    )
    
    try:
        # 创建所有表
        async with engine.begin() as conn:
            # 删除所有表（谨慎使用！）
            # await conn.run_sync(Base.metadata.drop_all)
            # logger.info("✅ 已删除所有表")
            
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ 已创建所有表")
        
        logger.success("🎉 数据库初始化完成！")
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise
    
    finally:
        await engine.dispose()


async def check_tables():
    """检查数据库表"""
    logger.info("🔍 检查数据库表...")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    try:
        async with engine.begin() as conn:
            # 获取所有表名
            result = await conn.run_sync(
                lambda sync_conn: sync_conn.dialect.get_table_names(sync_conn)
            )
            
            logger.info(f"📋 数据库中的表: {result}")
            
            expected_tables = ['users', 'user_sessions', 'code_executions']
            for table in expected_tables:
                if table in result:
                    logger.success(f"  ✅ {table}")
                else:
                    logger.warning(f"  ⚠️  {table} (不存在)")
    
    except Exception as e:
        logger.error(f"❌ 检查表失败: {e}")
    
    finally:
        await engine.dispose()


if __name__ == "__main__":
    # 运行初始化
    asyncio.run(init_database())
    asyncio.run(check_tables())
