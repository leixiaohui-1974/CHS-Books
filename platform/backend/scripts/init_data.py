"""
初始化数据脚本
用于创建会员配置、积分规则等基础数据

使用方法:
cd /workspace/platform/backend
python3 -m scripts.init_data
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import async_session, engine, Base
from app.models.membership import MembershipConfig, MembershipLevel, BenefitType
from app.models.points import PointsRule, PointsReason, PointsProduct, ProductType
from loguru import logger


async def init_membership_configs():
    """初始化会员配置"""
    async with async_session() as session:
        # 检查是否已存在配置
        result = await session.execute(select(MembershipConfig))
        existing = result.scalars().all()
        
        if existing:
            logger.info(f"会员配置已存在 {len(existing)} 条，跳过初始化")
            return
        
        configs = [
            MembershipConfig(
                level=MembershipLevel.FREE,
                min_experience=0,
                max_experience=0,
                name="免费会员",
                description="基础功能访问权限",
                benefits={
                    "course_discount": 0,
                    "free_tool_uses": 10,
                    "ai_chat_quota": 20,
                    "concurrent_tasks": 2
                },
                color="#808080",
                icon="free",
                is_active=True
            ),
            MembershipConfig(
                level=MembershipLevel.BRONZE,
                min_experience=0,
                max_experience=1000,
                monthly_price=29.0,
                yearly_price=290.0,
                name="青铜会员",
                description="入门级会员，享受基础优惠",
                benefits={
                    "course_discount": 5,
                    "free_tool_uses": 50,
                    "ai_chat_quota": 100,
                    "concurrent_tasks": 3,
                    "priority_support": False
                },
                color="#CD7F32",
                icon="bronze",
                is_active=True
            ),
            MembershipConfig(
                level=MembershipLevel.SILVER,
                min_experience=1001,
                max_experience=5000,
                monthly_price=59.0,
                yearly_price=590.0,
                name="白银会员",
                description="进阶会员，享受更多优惠和功能",
                benefits={
                    "course_discount": 10,
                    "free_tool_uses": 100,
                    "ai_chat_quota": 300,
                    "concurrent_tasks": 5,
                    "priority_support": True,
                    "download_materials": True
                },
                color="#C0C0C0",
                icon="silver",
                is_active=True
            ),
            MembershipConfig(
                level=MembershipLevel.GOLD,
                min_experience=5001,
                max_experience=10000,
                monthly_price=99.0,
                yearly_price=990.0,
                lifetime_price=1999.0,
                name="黄金会员",
                description="高级会员，尊享专属服务",
                benefits={
                    "course_discount": 20,
                    "free_tool_uses": 300,
                    "ai_chat_quota": 1000,
                    "concurrent_tasks": 10,
                    "priority_support": True,
                    "download_materials": True,
                    "exclusive_content": True,
                    "video_courses": True
                },
                color="#FFD700",
                icon="gold",
                is_active=True
            ),
            MembershipConfig(
                level=MembershipLevel.PLATINUM,
                min_experience=10001,
                max_experience=30000,
                monthly_price=199.0,
                yearly_price=1990.0,
                lifetime_price=3999.0,
                name="铂金会员",
                description="顶级会员，全方位尊享体验",
                benefits={
                    "course_discount": 30,
                    "free_tool_uses": 1000,
                    "ai_chat_quota": 5000,
                    "concurrent_tasks": 20,
                    "priority_support": True,
                    "download_materials": True,
                    "exclusive_content": True,
                    "video_courses": True,
                    "one_on_one_coaching": True,
                    "custom_learning_path": True
                },
                color="#E5E4E2",
                icon="platinum",
                is_active=True
            ),
            MembershipConfig(
                level=MembershipLevel.DIAMOND,
                min_experience=30001,
                max_experience=None,
                monthly_price=399.0,
                yearly_price=3990.0,
                lifetime_price=7999.0,
                name="钻石会员",
                description="至尊会员，无限制全功能访问",
                benefits={
                    "course_discount": 50,
                    "free_tool_uses": -1,  # -1 表示无限制
                    "ai_chat_quota": -1,
                    "concurrent_tasks": 50,
                    "priority_support": True,
                    "download_materials": True,
                    "exclusive_content": True,
                    "video_courses": True,
                    "one_on_one_coaching": True,
                    "custom_learning_path": True,
                    "vip_community": True,
                    "offline_events": True
                },
                color="#B9F2FF",
                icon="diamond",
                is_active=True
            )
        ]
        
        session.add_all(configs)
        await session.commit()
        logger.success(f"✅ 成功初始化 {len(configs)} 个会员配置")


async def init_points_rules():
    """初始化积分规则"""
    async with async_session() as session:
        # 检查是否已存在规则
        result = await session.execute(select(PointsRule))
        existing = result.scalars().all()
        
        if existing:
            logger.info(f"积分规则已存在 {len(existing)} 条，跳过初始化")
            return
        
        rules = [
            PointsRule(
                reason=PointsReason.DAILY_LOGIN,
                points=10,
                description="每日登录奖励",
                daily_limit=1,
                is_active=True
            ),
            PointsRule(
                reason=PointsReason.CASE_COMPLETE,
                points=20,
                description="完成案例学习",
                daily_limit=10,
                is_active=True
            ),
            PointsRule(
                reason=PointsReason.SHARE_COURSE,
                points=5,
                description="分享课程到社交媒体",
                daily_limit=5,
                is_active=True
            ),
            PointsRule(
                reason=PointsReason.INVITE_FRIEND,
                points=50,
                description="成功邀请好友注册",
                is_active=True
            ),
            PointsRule(
                reason=PointsReason.WRITE_NOTE,
                points=15,
                description="撰写学习笔记",
                daily_limit=3,
                is_active=True
            ),
            PointsRule(
                reason=PointsReason.COURSE_REVIEW,
                points=10,
                description="评价课程",
                is_active=True
            ),
            PointsRule(
                reason=PointsReason.ACHIEVEMENT_UNLOCK,
                points=30,
                description="解锁成就",
                is_active=True
            )
        ]
        
        session.add_all(rules)
        await session.commit()
        logger.success(f"✅ 成功初始化 {len(rules)} 个积分规则")


async def init_points_products():
    """初始化积分商品"""
    async with async_session() as session:
        # 检查是否已存在商品
        result = await session.execute(select(PointsProduct))
        existing = result.scalars().all()
        
        if existing:
            logger.info(f"积分商品已存在 {len(existing)} 个，跳过初始化")
            return
        
        products = [
            # 优惠券类
            PointsProduct(
                name="5元优惠券",
                description="全场通用，满50可用",
                product_type=ProductType.COUPON,
                points_cost=25,
                details={"discount": 5, "min_amount": 50, "valid_days": 30},
                stock=1000,
                max_per_user=10,
                image_url="/images/coupon_5.png",
                sort_order=1,
                is_active=True
            ),
            PointsProduct(
                name="10元优惠券",
                description="全场通用，满100可用",
                product_type=ProductType.COUPON,
                points_cost=50,
                details={"discount": 10, "min_amount": 100, "valid_days": 30},
                stock=1000,
                max_per_user=5,
                image_url="/images/coupon_10.png",
                sort_order=2,
                is_active=True
            ),
            PointsProduct(
                name="20元优惠券",
                description="全场通用，满200可用",
                product_type=ProductType.COUPON,
                points_cost=100,
                details={"discount": 20, "min_amount": 200, "valid_days": 30},
                stock=500,
                max_per_user=3,
                image_url="/images/coupon_20.png",
                sort_order=3,
                is_active=True
            ),
            
            # 课程类
            PointsProduct(
                name="Python基础入门课程",
                description="零基础学Python，包含30个实战案例",
                product_type=ProductType.COURSE,
                points_cost=500,
                details={"course_id": 1, "duration": "30课时", "level": "初级"},
                stock=None,  # 虚拟商品无库存限制
                max_per_user=1,
                image_url="/images/course_python_basic.png",
                sort_order=10,
                is_active=True
            ),
            PointsProduct(
                name="数据分析实战课程",
                description="掌握数据分析核心技能",
                product_type=ProductType.COURSE,
                points_cost=800,
                details={"course_id": 2, "duration": "40课时", "level": "中级"},
                stock=None,
                max_per_user=1,
                image_url="/images/course_data_analysis.png",
                sort_order=11,
                is_active=True
            ),
            
            # 会员类
            PointsProduct(
                name="青铜会员月卡",
                description="青铜会员权益，有效期30天",
                product_type=ProductType.MEMBERSHIP,
                points_cost=300,
                details={"level": "BRONZE", "duration_days": 30},
                stock=None,
                max_per_user=12,
                image_url="/images/membership_bronze.png",
                sort_order=20,
                is_active=True
            ),
            PointsProduct(
                name="白银会员月卡",
                description="白银会员权益，有效期30天",
                product_type=ProductType.MEMBERSHIP,
                points_cost=600,
                details={"level": "SILVER", "duration_days": 30},
                stock=None,
                max_per_user=12,
                image_url="/images/membership_silver.png",
                sort_order=21,
                is_active=True
            ),
            
            # 礼品类
            PointsProduct(
                name="定制T恤",
                description="工程师专属定制T恤",
                product_type=ProductType.GIFT,
                points_cost=1000,
                details={"sizes": ["S", "M", "L", "XL", "XXL"]},
                stock=100,
                max_per_user=2,
                requires_level="SILVER",
                image_url="/images/gift_tshirt.png",
                sort_order=30,
                is_active=True
            ),
            PointsProduct(
                name="品牌保温杯",
                description="高品质保温杯，印有平台Logo",
                product_type=ProductType.GIFT,
                points_cost=500,
                details={"capacity": "500ml", "material": "不锈钢"},
                stock=200,
                max_per_user=3,
                image_url="/images/gift_cup.png",
                sort_order=31,
                is_active=True
            ),
            PointsProduct(
                name="机械键盘",
                description="程序员必备，樱桃轴机械键盘",
                product_type=ProductType.GIFT,
                points_cost=2000,
                details={"switch": "Cherry MX Blue", "backlight": "RGB"},
                stock=50,
                max_per_user=1,
                requires_level="GOLD",
                image_url="/images/gift_keyboard.png",
                sort_order=32,
                is_active=True
            )
        ]
        
        session.add_all(products)
        await session.commit()
        logger.success(f"✅ 成功初始化 {len(products)} 个积分商品")


async def create_tables():
    """创建所有数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.success("✅ 数据库表创建完成")


async def main():
    """主函数"""
    logger.info("开始初始化数据...")
    
    try:
        # 1. 确保表已创建
        await create_tables()
        
        # 2. 初始化会员配置
        await init_membership_configs()
        
        # 3. 初始化积分规则
        await init_points_rules()
        
        # 4. 初始化积分商品
        await init_points_products()
        
        logger.success("🎉 所有数据初始化完成！")
        
    except Exception as e:
        logger.error(f"❌ 初始化失败: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
