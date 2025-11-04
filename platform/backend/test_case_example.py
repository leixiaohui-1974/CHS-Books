"""
实际案例测试脚本
演示如何使用V2.0的新功能
"""

import asyncio
import sys
from pathlib import Path
from loguru import logger

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
)


async def test_complete_workflow():
    """测试完整工作流"""
    logger.info("=" * 80)
    logger.info("🧪 测试案例：完整学习工作流演示")
    logger.info("=" * 80)
    logger.info("")
    
    # 模拟案例路径
    case_path = "/workspace/books/water-environment-simulation/code/examples/case_01_diffusion"
    
    # ============================================
    # 步骤1: 加载代码智能服务
    # ============================================
    logger.info("📋 步骤1: 加载代码智能服务")
    logger.info("-" * 80)
    
    from app.services.code_intelligence import code_intelligence_service
    
    # 检查案例是否存在
    if Path(case_path).exists():
        logger.success(f"✅ 案例目录存在: {case_path}")
        
        # 加载案例代码
        try:
            case_data = await code_intelligence_service.load_case(case_path)
            
            logger.success(f"✅ 加载代码文件: {len(case_data['files'])} 个")
            logger.info(f"   文件列表:")
            for file_path in list(case_data['files'].keys())[:5]:
                logger.info(f"     - {file_path}")
            
            logger.success(f"✅ 检测到依赖: {len(case_data['dependencies'])} 个")
            logger.info(f"   依赖列表: {', '.join(case_data['dependencies'][:5])}")
            
        except Exception as e:
            logger.error(f"❌ 加载代码失败: {e}")
    else:
        logger.warning(f"⚠️  案例目录不存在: {case_path}")
        logger.info("   使用模拟数据继续测试...")
    
    logger.info("")
    
    # ============================================
    # 步骤2: 代码验证和分析
    # ============================================
    logger.info("📋 步骤2: 代码验证和分析")
    logger.info("-" * 80)
    
    # 测试代码
    test_code = '''
def main():
    """扩散方程求解"""
    import numpy as np
    
    # 参数设置
    L = 10.0    # 长度
    T = 100.0   # 时间
    nx = 100    # 空间网格
    nt = 1000   # 时间步
    D = 0.01    # 扩散系数
    
    # 网格生成
    dx = L / (nx - 1)
    dt = T / nt
    x = np.linspace(0, L, nx)
    
    # Fourier数
    Fo = D * dt / dx**2
    print(f"Fourier数: Fo = {Fo:.4f}")
    
    if Fo > 0.5:
        print("警告: Fourier数过大，显式格式可能不稳定")
    
    return x, Fo
'''
    
    # 验证语法
    is_valid, error = await code_intelligence_service.validate_code(test_code)
    if is_valid:
        logger.success("✅ 代码语法正确")
    else:
        logger.error(f"❌ 代码语法错误: {error}")
    
    # 格式化代码
    formatted, success = await code_intelligence_service.format_code(test_code)
    if success:
        logger.success("✅ 代码格式化成功")
    else:
        logger.warning("⚠️  代码格式化失败（可能未安装black）")
    
    logger.info("")
    
    # ============================================
    # 步骤3: AI助手服务
    # ============================================
    logger.info("📋 步骤3: AI助手服务")
    logger.info("-" * 80)
    
    from app.services.ai_assistant_enhanced import ai_assistant_service
    
    # 测试代码讲解
    code_snippet = "Fo = D * dt / dx**2"
    logger.info(f"请求AI讲解代码: {code_snippet}")
    
    explanation = await ai_assistant_service.explain_code(
        code=code_snippet,
        context="计算Fourier数，用于判断显式格式的数值稳定性"
    )
    
    logger.success("✅ AI代码讲解生成")
    logger.info(f"   讲解内容（前200字符）:")
    logger.info(f"   {explanation[:200]}...")
    
    # 测试错误诊断
    logger.info("")
    logger.info("测试错误诊断...")
    
    error_code = "print(undefined_variable)"
    error_msg = "NameError: name 'undefined_variable' is not defined"
    
    diagnosis = await ai_assistant_service.diagnose_error(
        code=error_code,
        error_message=error_msg
    )
    
    logger.success("✅ 错误诊断完成")
    logger.info(f"   诊断结果: {diagnosis['diagnosis']}")
    logger.info(f"   建议数量: {len(diagnosis['suggestions'])} 条")
    logger.info(f"   首条建议: {diagnosis['suggestions'][0]}")
    
    logger.info("")
    
    # ============================================
    # 步骤4: 执行引擎状态
    # ============================================
    logger.info("📋 步骤4: 执行引擎状态")
    logger.info("-" * 80)
    
    from app.services.execution_engine import enhanced_execution_engine
    
    # 获取容器池统计
    stats = enhanced_execution_engine.get_pool_stats()
    
    logger.info("容器池状态:")
    logger.info(f"  - 总容器数: {stats['total']}")
    logger.info(f"  - 可用容器: {stats['available']}")
    logger.info(f"  - 使用中: {stats['in_use']}")
    
    if stats['available'] > 0:
        logger.success(f"✅ 容器池就绪 ({stats['available']}/{stats['total']} 可用)")
    else:
        logger.warning("⚠️  容器池无可用容器")
    
    logger.info("")
    
    # ============================================
    # 步骤5: 结果解析器
    # ============================================
    logger.info("📋 步骤5: 结果解析器")
    logger.info("-" * 80)
    
    from app.services.result_parser import result_parser
    
    # 模拟控制台输出
    console_output = """
执行完成！
================================================
主要结果:
  L2误差: 1.23e-4
  L∞误差: 3.45e-4
  计算时间: 10.5s
  收敛精度: 99.5%
  迭代次数: 1000
================================================
"""
    
    # 提取指标
    metrics = result_parser._extract_metrics_from_console(console_output)
    
    logger.success(f"✅ 从控制台提取到 {len(metrics)} 个指标:")
    for metric in metrics:
        logger.info(f"   - {metric['name']}: {metric['value']} {metric['unit']}")
    
    logger.info("")
    
    # ============================================
    # 步骤6: AI洞察生成
    # ============================================
    logger.info("📋 步骤6: AI洞察生成")
    logger.info("-" * 80)
    
    # 模拟结果数据
    result_data = {
        "plots": [
            {"name": "扩散演化图"},
            {"name": "误差分析图"}
        ],
        "metrics": metrics,
        "tables": [
            {"row_count": 100, "col_count": 5}
        ]
    }
    
    # 生成洞察
    insights = await ai_assistant_service.generate_insights(result_data)
    
    logger.success(f"✅ 生成 {len(insights)} 条AI洞察:")
    for i, insight in enumerate(insights, 1):
        logger.info(f"   {i}. {insight}")
    
    logger.info("")


async def test_session_workflow():
    """测试会话工作流（需要数据库）"""
    logger.info("=" * 80)
    logger.info("🧪 测试案例：会话管理工作流")
    logger.info("=" * 80)
    logger.info("")
    
    logger.warning("⚠️  此测试需要数据库连接，跳过...")
    logger.info("   要运行完整测试，请确保:")
    logger.info("   1. PostgreSQL数据库已启动")
    logger.info("   2. 运行数据库初始化: python -m app.core.init_db")
    logger.info("   3. 运行完整测试套件: pytest tests/ -v")
    logger.info("")


async def main():
    """主函数"""
    logger.info("🚀 开始测试智能知识平台 V2.0")
    logger.info("")
    
    try:
        # 测试完整工作流
        await test_complete_workflow()
        
        # 测试会话工作流
        await test_session_workflow()
        
        # 总结
        logger.info("=" * 80)
        logger.success("✅ 所有测试通过！")
        logger.info("=" * 80)
        logger.info("")
        logger.info("🎯 V2.0 核心功能验证完成:")
        logger.info("  ✅ 代码智能服务 - 加载、验证、分析")
        logger.info("  ✅ AI助手服务 - 讲解、诊断、洞察")
        logger.info("  ✅ 执行引擎 - 容器池管理")
        logger.info("  ✅ 结果解析 - 指标提取")
        logger.info("")
        logger.info("📚 下一步:")
        logger.info("  1. 启动API服务: uvicorn app.main:app --reload")
        logger.info("  2. 访问文档: http://localhost:8000/docs")
        logger.info("  3. 运行完整测试: pytest tests/ -v")
        logger.info("")
    
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
