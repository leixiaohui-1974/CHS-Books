#!/usr/bin/env python3
"""
初始化数据库脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.database import Base
from loguru import logger


async def init_db():
    """初始化数据库"""
    logger.info("🚀 开始初始化数据库...")
    logger.info(f"📍 数据库URL: {settings.DATABASE_URL.split('@')[-1]}")  # 只显示主机部分
    
    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    try:
        # 创建所有表
        async with engine.begin() as conn:
            logger.info("📝 创建数据库表...")
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ 数据库初始化完成！")
        logger.info("")
        logger.info("📊 已创建的表:")
        for table_name in Base.metadata.tables.keys():
            logger.info(f"  - {table_name}")
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise
    finally:
        await engine.dispose()


async def drop_db():
    """删除所有表（谨慎使用！）"""
    logger.warning("⚠️  即将删除所有数据库表...")
    
    confirm = input("确认删除所有表？(yes/no): ")
    if confirm.lower() != "yes":
        logger.info("❌ 操作已取消")
        return
    
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    try:
        async with engine.begin() as conn:
            logger.info("🗑️  删除数据库表...")
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("✅ 数据库表已删除")
        
    except Exception as e:
        logger.error(f"❌ 删除表失败: {e}")
        raise
    finally:
        await engine.dispose()


async def reset_db():
    """重置数据库（删除后重建）"""
    logger.info("🔄 重置数据库...")
    await drop_db()
    await init_db()
    logger.info("✅ 数据库已重置")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库管理工具")
    parser.add_argument(
        "action",
        choices=["init", "drop", "reset"],
        help="操作类型: init=初始化, drop=删除, reset=重置"
    )
    
    args = parser.parse_args()
    
    if args.action == "init":
        asyncio.run(init_db())
    elif args.action == "drop":
        asyncio.run(drop_db())
    elif args.action == "reset":
        asyncio.run(reset_db())


if __name__ == "__main__":
    main()
