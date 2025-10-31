"""
数据库初始化脚本
创建所有表并导入初始数据
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, Base
from app.core.config import settings
from app.models import *  # 导入所有模型
from loguru import logger


async def create_tables():
    """创建所有数据库表"""
    logger.info("🔧 开始创建数据库表...")
    
    async with engine.begin() as conn:
        # 删除所有表（开发环境）
        if settings.APP_ENV == "development":
            logger.warning("⚠️  开发环境：删除所有表")
            await conn.run_sync(Base.metadata.drop_all)
        
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ 数据库表创建完成！")


async def main():
    """主函数"""
    try:
        logger.info("="*50)
        logger.info("数据库初始化脚本")
        logger.info("="*50)
        
        # 创建表
        await create_tables()
        
        # 显示创建的表
        logger.info("\n已创建的表:")
        logger.info("  - users (用户表)")
        logger.info("  - books (书籍表)")
        logger.info("  - chapters (章节表)")
        logger.info("  - cases (案例表)")
        logger.info("  - user_progress (学习进度表)")
        logger.info("  - chapter_progress (章节进度表)")
        logger.info("  - case_progress (案例进度表)")
        logger.info("  - orders (订单表)")
        logger.info("  - subscriptions (订阅表)")
        logger.info("  - tool_executions (工具执行表)")
        
        logger.info("\n✅ 数据库初始化完成！")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
