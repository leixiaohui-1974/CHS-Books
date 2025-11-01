"""
添加数据库索引优化脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine
from loguru import logger


# 定义需要添加的索引
INDEXES = [
    # 用户表索引
    ("idx_users_email", "users", "email"),
    ("idx_users_username", "users", "username"),
    
    # 学习进度表索引
    ("idx_case_progress_user_case", "case_progress", "user_id, case_id"),
    ("idx_case_progress_updated", "case_progress", "updated_at"),
    
    # 订单表索引
    ("idx_orders_user_status", "orders", "user_id, status"),
    ("idx_orders_created", "orders", "created_at"),
    
    # 积分交易表索引
    ("idx_points_transactions_account", "points_transactions", "account_id"),
    ("idx_points_transactions_created", "points_transactions", "created_at"),
    ("idx_points_transactions_type", "points_transactions", "transaction_type"),
    
    # 会员经验历史索引
    ("idx_experience_history_membership", "experience_history", "user_membership_id"),
    ("idx_experience_history_created", "experience_history", "created_at"),
    
    # 知识库文档索引
    ("idx_documents_kb", "documents", "knowledge_base_id"),
    ("idx_documents_type", "documents", "doc_type"),
    
    # 文档分块索引
    ("idx_document_chunks_doc", "document_chunks", "document_id"),
    ("idx_document_chunks_index", "document_chunks", "chunk_index"),
    
    # 积分兑换记录索引
    ("idx_points_redemptions_user", "points_redemptions", "user_id"),
    ("idx_points_redemptions_product", "points_redemptions", "product_id"),
    ("idx_points_redemptions_status", "points_redemptions", "status"),
    
    # 优惠券使用记录索引
    ("idx_user_coupons_user", "user_coupons", "user_id"),
    ("idx_user_coupons_status", "user_coupons", "status"),
]


async def index_exists(conn, index_name: str) -> bool:
    """检查索引是否存在"""
    result = await conn.execute(
        text("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE indexname = :index_name
        """),
        {"index_name": index_name}
    )
    count = result.scalar()
    return count > 0


async def create_index(conn, index_name: str, table_name: str, columns: str):
    """创建索引"""
    try:
        # 检查索引是否已存在
        if await index_exists(conn, index_name):
            logger.info(f"索引 {index_name} 已存在，跳过")
            return False
        
        # 创建索引
        sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns})"
        await conn.execute(text(sql))
        await conn.commit()
        logger.success(f"✅ 成功创建索引: {index_name} ON {table_name}({columns})")
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建索引失败 {index_name}: {str(e)}")
        await conn.rollback()
        return False


async def add_all_indexes():
    """添加所有索引"""
    created_count = 0
    skipped_count = 0
    failed_count = 0
    
    async with engine.begin() as conn:
        logger.info(f"开始创建 {len(INDEXES)} 个索引...")
        
        for index_name, table_name, columns in INDEXES:
            result = await create_index(conn, index_name, table_name, columns)
            if result is True:
                created_count += 1
            elif result is False:
                skipped_count += 1
            else:
                failed_count += 1
        
        logger.info("━" * 60)
        logger.success(f"✅ 索引创建完成!")
        logger.info(f"  创建: {created_count} 个")
        logger.info(f"  跳过: {skipped_count} 个 (已存在)")
        logger.info(f"  失败: {failed_count} 个")


async def analyze_tables():
    """分析表以更新统计信息"""
    async with engine.begin() as conn:
        logger.info("开始分析表...")
        
        tables = set([table_name for _, table_name, _ in INDEXES])
        
        for table_name in tables:
            try:
                await conn.execute(text(f"ANALYZE {table_name}"))
                logger.success(f"✅ 分析表: {table_name}")
            except Exception as e:
                logger.error(f"❌ 分析表失败 {table_name}: {str(e)}")
        
        await conn.commit()


async def show_index_usage():
    """显示索引使用情况"""
    async with engine.begin() as conn:
        logger.info("查询索引使用情况...")
        
        result = await conn.execute(
            text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan as index_scans,
                    idx_tup_read as tuples_read,
                    idx_tup_fetch as tuples_fetched
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                ORDER BY idx_scan DESC
                LIMIT 20
            """)
        )
        
        rows = result.fetchall()
        if rows:
            logger.info("\n最常使用的20个索引:")
            logger.info(f"{'表名':<25} {'索引名':<30} {'扫描次数':<12} {'读取行数':<12} {'获取行数':<12}")
            logger.info("━" * 100)
            for row in rows:
                logger.info(
                    f"{row.tablename:<25} {row.indexname:<30} "
                    f"{row.index_scans:<12} {row.tuples_read:<12} {row.tuples_fetched:<12}"
                )


async def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("数据库索引优化脚本")
    logger.info("=" * 60)
    
    try:
        # 1. 添加索引
        await add_all_indexes()
        
        # 2. 分析表
        await analyze_tables()
        
        # 3. 显示索引使用情况（仅用于生产环境）
        # await show_index_usage()
        
        logger.success("🎉 所有操作完成！")
        
    except Exception as e:
        logger.error(f"❌ 执行失败: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
