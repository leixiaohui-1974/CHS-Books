#!/usr/bin/env python3
"""
数据库迁移工具
使用Alembic进行数据库版本管理
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


async def create_revision(message: str):
    """创建新的迁移版本"""
    import subprocess
    
    logger.info(f"📝 创建迁移: {message}")
    
    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", message],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        logger.info("✅ 迁移文件已创建")
        print(result.stdout)
    else:
        logger.error(f"❌ 创建失败: {result.stderr}")
        sys.exit(1)


async def upgrade(revision: str = "head"):
    """升级到指定版本"""
    import subprocess
    
    logger.info(f"⬆️  升级数据库到: {revision}")
    
    result = subprocess.run(
        ["alembic", "upgrade", revision],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        logger.info("✅ 数据库升级成功")
        print(result.stdout)
    else:
        logger.error(f"❌ 升级失败: {result.stderr}")
        sys.exit(1)


async def downgrade(revision: str = "-1"):
    """降级到指定版本"""
    import subprocess
    
    logger.warning(f"⬇️  降级数据库到: {revision}")
    
    confirm = input("确认降级？这可能导致数据丢失 (yes/no): ")
    if confirm.lower() != "yes":
        logger.info("❌ 操作已取消")
        return
    
    result = subprocess.run(
        ["alembic", "downgrade", revision],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        logger.info("✅ 数据库降级成功")
        print(result.stdout)
    else:
        logger.error(f"❌ 降级失败: {result.stderr}")
        sys.exit(1)


async def show_current():
    """显示当前版本"""
    import subprocess
    
    result = subprocess.run(
        ["alembic", "current"],
        capture_output=True,
        text=True
    )
    
    logger.info("📍 当前数据库版本:")
    print(result.stdout or "未找到版本信息")


async def show_history():
    """显示迁移历史"""
    import subprocess
    
    result = subprocess.run(
        ["alembic", "history", "-v"],
        capture_output=True,
        text=True
    )
    
    logger.info("📜 迁移历史:")
    print(result.stdout or "暂无迁移历史")


async def check_db():
    """检查数据库连接"""
    logger.info("🔍 检查数据库连接...")
    
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        await engine.dispose()
        logger.info("✅ 数据库连接正常")
        return True
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        return False


async def backup_db(output_file: str = None):
    """备份数据库"""
    import subprocess
    from datetime import datetime
    
    if not output_file:
        output_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    logger.info(f"💾 备份数据库到: {output_file}")
    
    # 这里需要根据实际数据库类型调整
    # PostgreSQL示例:
    db_url = settings.DATABASE_URL
    if "postgresql" in db_url:
        # 提取连接信息
        logger.info("📦 使用pg_dump备份...")
        logger.warning("⚠️  请手动运行: pg_dump -U user dbname > backup.sql")
    else:
        logger.warning("⚠️  请根据数据库类型手动备份")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库迁移工具")
    parser.add_argument(
        "action",
        choices=["revision", "upgrade", "downgrade", "current", "history", "check", "backup"],
        help="操作类型"
    )
    parser.add_argument(
        "-m", "--message",
        help="迁移消息（用于revision）"
    )
    parser.add_argument(
        "-r", "--revision",
        default="head",
        help="目标版本（用于upgrade/downgrade）"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出文件（用于backup）"
    )
    
    args = parser.parse_args()
    
    logger.info("🔧 数据库迁移工具")
    logger.info(f"📍 数据库: {settings.DATABASE_URL.split('@')[-1]}")
    logger.info("")
    
    if args.action == "revision":
        if not args.message:
            logger.error("❌ 请提供迁移消息: -m \"message\"")
            sys.exit(1)
        asyncio.run(create_revision(args.message))
    
    elif args.action == "upgrade":
        asyncio.run(upgrade(args.revision))
    
    elif args.action == "downgrade":
        asyncio.run(downgrade(args.revision))
    
    elif args.action == "current":
        asyncio.run(show_current())
    
    elif args.action == "history":
        asyncio.run(show_history())
    
    elif args.action == "check":
        result = asyncio.run(check_db())
        sys.exit(0 if result else 1)
    
    elif args.action == "backup":
        asyncio.run(backup_db(args.output))


if __name__ == "__main__":
    main()
