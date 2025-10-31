#!/usr/bin/env python3
"""
填充示例数据脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.core.database import Base
from app.services import UserService, BookService
from app.models.book import BookStatus, DifficultyLevel
from loguru import logger


async def seed_users(db: AsyncSession):
    """创建示例用户"""
    logger.info("📝 创建示例用户...")
    
    users = [
        {
            "email": "admin@example.com",
            "username": "admin",
            "password": "admin123",
            "full_name": "系统管理员"
        },
        {
            "email": "demo@example.com",
            "username": "demo",
            "password": "demo123",
            "full_name": "演示用户"
        },
        {
            "email": "student@example.com",
            "username": "student",
            "password": "student123",
            "full_name": "学生用户"
        }
    ]
    
    for user_data in users:
        try:
            user = await UserService.create_user(
                db=db,
                **user_data
            )
            logger.info(f"✅ 创建用户: {user.email}")
        except Exception as e:
            logger.warning(f"⚠️  用户已存在或创建失败: {user_data['email']} - {e}")
    
    await db.commit()


async def seed_books(db: AsyncSession):
    """创建示例书籍"""
    logger.info("📚 创建示例书籍...")
    
    books_data = [
        {
            "slug": "water-system-control",
            "title": "水系统控制论",
            "subtitle": "基于水箱案例的控制理论入门",
            "description": "通过12个经典水箱案例系统讲解控制理论基础知识，适合控制工程、水利工程等专业学生学习。",
            "status": BookStatus.PUBLISHED,
            "difficulty": DifficultyLevel.BEGINNER,
            "price": 299.0,
            "original_price": 399.0,
            "is_free": False,
            "estimated_hours": 192,
            "tags": ["控制理论", "水利工程", "Python"],
            "authors": ["张教授", "李工程师"],
            "chapters": [
                {
                    "slug": "chapter-01",
                    "order": 1,
                    "title": "第1章：控制系统基础",
                    "is_free": True,
                    "estimated_minutes": 120,
                    "cases": [
                        {
                            "slug": "case-01-water-tower",
                            "order": 1,
                            "title": "案例1：家庭水塔自动供水系统",
                            "difficulty": DifficultyLevel.BEGINNER,
                            "estimated_minutes": 90,
                            "has_tool": True,
                            "is_free": True,
                        },
                        {
                            "slug": "case-02-water-tank",
                            "order": 2,
                            "title": "案例2：水箱液位控制",
                            "difficulty": DifficultyLevel.BEGINNER,
                            "estimated_minutes": 90,
                            "has_tool": True,
                            "is_free": True,
                        }
                    ]
                },
                {
                    "slug": "chapter-02",
                    "order": 2,
                    "title": "第2章：PID控制器设计",
                    "is_free": False,
                    "estimated_minutes": 180,
                    "cases": [
                        {
                            "slug": "case-03-pid-tuning",
                            "order": 1,
                            "title": "案例3：PID参数整定",
                            "difficulty": DifficultyLevel.INTERMEDIATE,
                            "estimated_minutes": 120,
                            "has_tool": True,
                            "is_free": False,
                        }
                    ]
                }
            ]
        },
        {
            "slug": "open-channel-hydraulics",
            "title": "明渠水力学计算",
            "subtitle": "Python编程与实践",
            "description": "使用Python语言实现明渠水力学的各种计算方法，包括30个典型案例。",
            "status": BookStatus.PUBLISHED,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "price": 399.0,
            "original_price": 499.0,
            "is_free": False,
            "estimated_hours": 240,
            "tags": ["水力学", "明渠", "Python", "数值计算"],
            "authors": ["王教授"],
            "chapters": [
                {
                    "slug": "chapter-01",
                    "order": 1,
                    "title": "第1章：明渠水流基础",
                    "is_free": True,
                    "estimated_minutes": 90,
                    "cases": [
                        {
                            "slug": "case-01-uniform-flow",
                            "order": 1,
                            "title": "案例1：均匀流计算",
                            "difficulty": DifficultyLevel.BEGINNER,
                            "estimated_minutes": 60,
                            "has_tool": True,
                            "is_free": True,
                        }
                    ]
                }
            ]
        },
        {
            "slug": "canal-pipeline-control",
            "title": "渠道管道控制",
            "subtitle": "现代输水系统调控技术",
            "description": "介绍大型渠道和管道系统的现代化控制技术，包括实时调度、优化控制等。",
            "status": BookStatus.DRAFT,
            "difficulty": DifficultyLevel.ADVANCED,
            "price": 499.0,
            "is_free": False,
            "estimated_hours": 300,
            "tags": ["渠道", "管道", "控制", "调度"],
            "authors": ["赵博士", "刘教授"],
            "chapters": []
        }
    ]
    
    for book_data in books_data:
        try:
            # 提取章节数据
            chapters_data = book_data.pop("chapters", [])
            
            # 创建书籍
            book = await BookService.create_book(db=db, **book_data)
            logger.info(f"✅ 创建书籍: {book.title}")
            
            # 创建章节和案例
            for chapter_data in chapters_data:
                cases_data = chapter_data.pop("cases", [])
                
                chapter = await BookService.create_chapter(
                    db=db,
                    book_id=book.id,
                    **chapter_data
                )
                logger.info(f"  ✅ 创建章节: {chapter.title}")
                
                for case_data in cases_data:
                    case = await BookService.create_case(
                        db=db,
                        book_id=book.id,
                        chapter_id=chapter.id,
                        **case_data
                    )
                    logger.info(f"    ✅ 创建案例: {case.title}")
        
        except Exception as e:
            logger.error(f"❌ 创建书籍失败: {book_data['title']} - {e}")
    
    await db.commit()


async def main():
    """主函数"""
    logger.info("🚀 开始填充示例数据...")
    
    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    # 创建会话工厂
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        try:
            # 填充用户数据
            await seed_users(db)
            
            # 填充书籍数据
            await seed_books(db)
            
            logger.info("✅ 示例数据填充完成！")
            
        except Exception as e:
            logger.error(f"❌ 填充数据失败: {e}")
            await db.rollback()
            raise
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
