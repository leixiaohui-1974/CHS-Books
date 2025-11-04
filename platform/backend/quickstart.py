"""
快速启动和测试脚本
用于验证增强功能是否正常工作
"""

import asyncio
import sys
from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")


async def test_code_intelligence():
    """测试代码智能服务"""
    logger.info("=" * 60)
    logger.info("测试1: 代码智能服务")
    logger.info("=" * 60)
    
    from app.services.code_intelligence import code_intelligence_service
    
    # 测试代码验证
    test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
"""
    
    is_valid, error = await code_intelligence_service.validate_code(test_code)
    logger.info(f"✅ 代码验证: {'通过' if is_valid else '失败'}")
    
    if not is_valid:
        logger.error(f"错误: {error}")


async def test_ai_assistant():
    """测试AI助手服务"""
    logger.info("=" * 60)
    logger.info("测试2: AI助手服务")
    logger.info("=" * 60)
    
    from app.services.ai_assistant_enhanced import ai_assistant_service
    
    # 测试代码讲解
    code = "result = [x**2 for x in range(10)]"
    explanation = await ai_assistant_service.explain_code(code)
    logger.info(f"✅ 代码讲解生成 ({len(explanation)} 字符)")
    
    # 测试错误诊断
    error_msg = "NameError: name 'undefined_var' is not defined"
    diagnosis = await ai_assistant_service.diagnose_error("print(undefined_var)", error_msg)
    logger.info(f"✅ 错误诊断: {diagnosis['diagnosis']}")
    logger.info(f"   建议: {diagnosis['suggestions'][0]}")


async def test_execution_engine():
    """测试执行引擎"""
    logger.info("=" * 60)
    logger.info("测试3: 执行引擎")
    logger.info("=" * 60)
    
    from app.services.execution_engine import enhanced_execution_engine
    
    # 获取容器池统计
    stats = enhanced_execution_engine.get_pool_stats()
    logger.info(f"✅ 容器池统计:")
    logger.info(f"   - 可用: {stats['available']}")
    logger.info(f"   - 使用中: {stats['in_use']}")
    logger.info(f"   - 总数: {stats['total']}")


async def test_result_parser():
    """测试结果解析器"""
    logger.info("=" * 60)
    logger.info("测试4: 结果解析器")
    logger.info("=" * 60)
    
    from app.services.result_parser import result_parser
    
    # 测试从控制台提取指标
    console_output = """
执行完成！
  L2误差: 1.23e-4
  L∞误差: 3.45e-4
  计算时间: 10.5s
  精度: 99.5%
"""
    
    metrics = result_parser._extract_metrics_from_console(console_output)
    logger.info(f"✅ 提取到 {len(metrics)} 个指标:")
    for metric in metrics:
        logger.info(f"   - {metric['name']}: {metric['value']} {metric['unit']}")


async def main():
    """主函数"""
    logger.info("🚀 开始测试智能知识平台 V2.0 核心功能")
    logger.info("")
    
    try:
        await test_code_intelligence()
        logger.info("")
        
        await test_ai_assistant()
        logger.info("")
        
        await test_execution_engine()
        logger.info("")
        
        await test_result_parser()
        logger.info("")
        
        logger.success("=" * 60)
        logger.success("✅ 所有测试通过！")
        logger.success("=" * 60)
        logger.info("")
        logger.info("📖 后续步骤:")
        logger.info("  1. 启动FastAPI服务: uvicorn app.main:app --reload")
        logger.info("  2. 访问API文档: http://localhost:8000/docs")
        logger.info("  3. 运行完整测试: pytest tests/ -v")
        logger.info("")
    
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
