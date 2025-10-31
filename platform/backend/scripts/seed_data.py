"""
导入示例数据
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.services import UserService, BookService
from app.models.book import BookStatus, DifficultyLevel
from loguru import logger


async def seed_users(db: AsyncSession):
    """创建示例用户"""
    logger.info("👤 创建示例用户...")
    
    try:
        # 管理员用户
        admin = await UserService.create_user(
            db=db,
            email="admin@example.com",
            username="admin",
            password="admin123",
            full_name="管理员"
        )
        admin.role = "admin"
        await db.commit()
        logger.info(f"  ✅ 管理员: {admin.email}")
        
        # 普通用户
        user1 = await UserService.create_user(
            db=db,
            email="student@example.com",
            username="student1",
            password="password123",
            full_name="张三"
        )
        logger.info(f"  ✅ 用户1: {user1.email}")
        
        user2 = await UserService.create_user(
            db=db,
            email="teacher@example.com",
            username="teacher1",
            password="password123",
            full_name="李四"
        )
        logger.info(f"  ✅ 用户2: {user2.email}")
        
        return {"admin": admin, "user1": user1, "user2": user2}
        
    except Exception as e:
        logger.error(f"❌ 创建用户失败: {e}")
        return {}


async def seed_books(db: AsyncSession):
    """创建示例书籍"""
    logger.info("📚 创建示例书籍...")
    
    try:
        # 书籍1: 水系统控制论
        book1 = await BookService.create_book(
            db=db,
            slug="water-system-control",
            title="水系统控制论",
            subtitle="基于水箱案例的控制理论入门",
            description="通过12个经典水箱案例系统讲解控制理论基础知识...",
            authors=["张教授", "李教授"],
            version="1.0.0",
            status=BookStatus.PUBLISHED,
            difficulty=DifficultyLevel.BEGINNER,
            is_free=False,
            price=299.0,
            original_price=399.0,
            trial_chapters=[1, 2],
            total_chapters=6,
            total_cases=24,
            estimated_hours=192,
            enrollments=1523,
            avg_rating=4.8,
            tags=["控制理论", "水利工程", "PID控制"],
            github_path="books/water-system-control"
        )
        logger.info(f"  ✅ 书籍1: {book1.title}")
        
        # 创建章节
        chapter1 = await BookService.create_chapter(
            db=db,
            book_id=book1.id,
            slug="control-basics",
            order=1,
            title="第1章：控制系统基础",
            description="介绍控制系统的基本概念和开关控制",
            is_free=True,
            learning_objectives=["理解反馈控制原理", "掌握开关控制器设计"],
            estimated_minutes=120
        )
        
        # 创建案例
        case1 = await BookService.create_case(
            db=db,
            book_id=book1.id,
            chapter_id=chapter1.id,
            slug="home-water-tower",
            order=1,
            title="案例1：家庭水塔自动供水系统",
            subtitle="开关控制器设计与仿真",
            description="设计一个自动控制家庭水塔水位的系统...",
            difficulty=DifficultyLevel.BEGINNER,
            estimated_minutes=90,
            key_concepts=["开关控制", "滞环", "一阶系统"],
            has_tool=True,
            tool_config={
                "entry_function": "run_simulation",
                "inputs": [
                    {
                        "name": "tank_area",
                        "label": "水箱底面积",
                        "type": "number",
                        "unit": "m²",
                        "default": 1.0,
                        "min": 0.1,
                        "max": 10.0
                    }
                ]
            },
            script_path="books/water-system-control/code/examples/case_01_home_water_tower/main.py"
        )
        logger.info(f"    ✅ 案例1: {case1.title}")
        
        # 书籍2: 明渠水力学
        book2 = await BookService.create_book(
            db=db,
            slug="open-channel-hydraulics",
            title="明渠水力学计算",
            subtitle="基于工程案例的水力计算入门",
            description="通过30个经典水力工程案例系统讲解明渠水力学计算方法...",
            authors=["王教授", "赵教授"],
            version="1.0.0",
            status=BookStatus.PUBLISHED,
            difficulty=DifficultyLevel.INTERMEDIATE,
            is_free=False,
            price=399.0,
            original_price=499.0,
            trial_chapters=[1],
            total_chapters=13,
            total_cases=30,
            estimated_hours=288,
            enrollments=856,
            avg_rating=4.7,
            tags=["水力学", "明渠流", "非恒定流"],
            github_path="books/open-channel-hydraulics"
        )
        logger.info(f"  ✅ 书籍2: {book2.title}")
        
        # 书籍3: 运河管道控制
        book3 = await BookService.create_book(
            db=db,
            slug="canal-pipeline-control",
            title="运河与管道控制",
            subtitle="闸泵联合调度与智能控制",
            description="结合明渠水力学和控制理论，讲解运河系统的智能控制...",
            authors=["刘教授"],
            version="1.0.0",
            status=BookStatus.PUBLISHED,
            difficulty=DifficultyLevel.ADVANCED,
            is_free=False,
            price=299.0,
            trial_chapters=[1],
            total_chapters=8,
            total_cases=20,
            estimated_hours=160,
            enrollments=423,
            avg_rating=4.9,
            tags=["智能控制", "调度优化", "实时控制"],
            github_path="books/canal-pipeline-control"
        )
        logger.info(f"  ✅ 书籍3: {book3.title}")
        
        return {"book1": book1, "book2": book2, "book3": book3}
        
    except Exception as e:
        logger.error(f"❌ 创建书籍失败: {e}")
        import traceback
        traceback.print_exc()
        return {}


async def main():
    """主函数"""
    logger.info("="*50)
    logger.info("导入示例数据")
    logger.info("="*50)
    
    async with AsyncSessionLocal() as db:
        try:
            # 导入用户
            users = await seed_users(db)
            
            # 导入书籍
            books = await seed_books(db)
            
            logger.info("\n✅ 示例数据导入完成！")
            logger.info("="*50)
            logger.info("\n登录信息:")
            logger.info("  管理员: admin@example.com / admin123")
            logger.info("  用户1: student@example.com / password123")
            logger.info("  用户2: teacher@example.com / password123")
            logger.info("\n书籍:")
            logger.info(f"  - {len(books)}本书籍")
            logger.info("="*50)
            
        except Exception as e:
            logger.error(f"❌ 导入数据失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
