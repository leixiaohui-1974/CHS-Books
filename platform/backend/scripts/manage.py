#!/usr/bin/env python3
"""
系统管理CLI工具
提供数据库管理、用户管理、系统维护等功能

使用方法:
    python3 -m scripts.manage [command] [options]

命令列表:
    db init           - 初始化数据库
    db migrate        - 运行数据库迁移
    db seed           - 填充测试数据
    db backup         - 备份数据库
    db restore        - 恢复数据库
    
    user create       - 创建用户
    user list         - 列出用户
    user delete       - 删除用户
    user set-admin    - 设置管理员
    
    system status     - 系统状态
    system clean      - 清理缓存
    system test       - 运行测试
"""

import asyncio
import sys
import click
from pathlib import Path
from loguru import logger
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, text
from app.core.database import get_db, engine, Base
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# 创建异步会话
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@click.group()
def cli():
    """工程学习平台管理工具"""
    pass


# ============ 数据库管理 ============
@cli.group()
def db():
    """数据库管理命令"""
    pass


@db.command()
def init():
    """初始化数据库表"""
    async def _init():
        logger.info("开始初始化数据库...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.success("✅ 数据库初始化完成！")
    
    asyncio.run(_init())


@db.command()
def seed():
    """填充测试数据"""
    async def _seed():
        logger.info("开始填充测试数据...")
        async with async_session() as session:
            # 创建管理员用户
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="系统管理员",
                is_superuser=True
            )
            session.add(admin)
            
            # 创建测试用户
            test_user = User(
                username="testuser",
                email="test@example.com",
                hashed_password=get_password_hash("test123"),
                full_name="测试用户"
            )
            session.add(test_user)
            
            await session.commit()
            
        logger.success("✅ 测试数据填充完成！")
        logger.info("  管理员: admin / admin123")
        logger.info("  测试用户: testuser / test123")
    
    asyncio.run(_seed())


@db.command()
def status():
    """显示数据库状态"""
    async def _status():
        logger.info("正在检查数据库状态...")
        
        async with async_session() as session:
            # 统计用户数
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            logger.info(f"📊 数据库统计:")
            logger.info(f"  用户总数: {len(users)}")
            logger.info(f"  管理员: {len([u for u in users if u.is_superuser])}")
    
    asyncio.run(_status())


# ============ 用户管理 ============
@cli.group()
def user():
    """用户管理命令"""
    pass


@user.command()
@click.option('--username', prompt=True, help='用户名')
@click.option('--email', prompt=True, help='邮箱')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='密码')
@click.option('--fullname', prompt=True, help='全名')
@click.option('--admin', is_flag=True, help='是否为管理员')
def create(username, email, password, fullname, admin):
    """创建新用户"""
    async def _create():
        async with async_session() as session:
            user = User(
                username=username,
                email=email,
                hashed_password=get_password_hash(password),
                full_name=fullname,
                is_superuser=admin
            )
            session.add(user)
            await session.commit()
            
            logger.success(f"✅ 用户创建成功: {username}")
            if admin:
                logger.info("  权限: 管理员")
    
    asyncio.run(_create())


@user.command()
def list():
    """列出所有用户"""
    async def _list():
        async with async_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            logger.info(f"\n📋 用户列表 (共 {len(users)} 个):\n")
            logger.info(f"{'ID':<6} {'用户名':<20} {'邮箱':<30} {'角色':<10} {'状态':<10}")
            logger.info("=" * 90)
            
            for user in users:
                role = "管理员" if user.is_superuser else "普通用户"
                status = "活跃" if user.is_active else "禁用"
                logger.info(
                    f"{user.id:<6} {user.username:<20} {user.email:<30} {role:<10} {status:<10}"
                )
    
    asyncio.run(_list())


@user.command()
@click.argument('username')
def delete(username):
    """删除用户"""
    async def _delete():
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error(f"❌ 用户不存在: {username}")
                return
            
            if click.confirm(f'确认删除用户 {username}?'):
                await session.delete(user)
                await session.commit()
                logger.success(f"✅ 用户已删除: {username}")
            else:
                logger.info("操作已取消")
    
    asyncio.run(_delete())


@user.command()
@click.argument('username')
def set_admin(username):
    """设置用户为管理员"""
    async def _set_admin():
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error(f"❌ 用户不存在: {username}")
                return
            
            user.is_superuser = True
            await session.commit()
            logger.success(f"✅ 用户 {username} 已设置为管理员")
    
    asyncio.run(_set_admin())


# ============ 系统管理 ============
@cli.group()
def system():
    """系统管理命令"""
    pass


@system.command()
def status():
    """显示系统状态"""
    import psutil
    
    logger.info("📊 系统状态:")
    logger.info("=" * 60)
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    logger.info(f"CPU使用率: {cpu_percent}%")
    
    # 内存
    memory = psutil.virtual_memory()
    logger.info(f"内存使用: {memory.percent}% ({memory.used / (1024**3):.2f}GB / {memory.total / (1024**3):.2f}GB)")
    
    # 磁盘
    disk = psutil.disk_usage('/')
    logger.info(f"磁盘使用: {disk.percent}% ({disk.used / (1024**3):.2f}GB / {disk.total / (1024**3):.2f}GB)")
    
    # 数据库状态
    async def _check_db():
        try:
            async with async_session() as session:
                await session.execute(text("SELECT 1"))
            return "✅ 正常"
        except Exception as e:
            return f"❌ 异常: {str(e)}"
    
    db_status = asyncio.run(_check_db())
    logger.info(f"数据库: {db_status}")


@system.command()
def test():
    """运行测试套件"""
    import subprocess
    
    logger.info("🧪 运行测试套件...")
    result = subprocess.run(
        ["python3", "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=Path(__file__).parent.parent
    )
    sys.exit(result.returncode)


@system.command()
def clean():
    """清理临时文件和缓存"""
    import shutil
    
    logger.info("🧹 清理系统...")
    
    # 清理__pycache__
    cache_dirs = list(Path(__file__).parent.parent.rglob("__pycache__"))
    for cache_dir in cache_dirs:
        shutil.rmtree(cache_dir, ignore_errors=True)
    
    logger.info(f"  清理 {len(cache_dirs)} 个缓存目录")
    
    # 清理.pyc文件
    pyc_files = list(Path(__file__).parent.parent.rglob("*.pyc"))
    for pyc_file in pyc_files:
        pyc_file.unlink(missing_ok=True)
    
    logger.info(f"  清理 {len(pyc_files)} 个.pyc文件")
    
    logger.success("✅ 清理完成！")


@system.command()
def info():
    """显示系统信息"""
    import platform
    
    logger.info("ℹ️  系统信息:")
    logger.info("=" * 60)
    logger.info(f"Python版本: {platform.python_version()}")
    logger.info(f"操作系统: {platform.system()} {platform.release()}")
    logger.info(f"架构: {platform.machine()}")
    logger.info(f"项目版本: v1.3.0-stable")
    logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    cli()
