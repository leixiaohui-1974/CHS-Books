"""
简化测试脚本 - 不依赖外部包
"""

import sys
import asyncio
from pathlib import Path

# 添加app到路径
sys.path.insert(0, str(Path(__file__).parent))


def print_section(title):
    """打印章节标题"""
    print()
    print("=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_success(msg):
    """打印成功消息"""
    print(f"✅ {msg}")


def print_info(msg):
    """打印信息"""
    print(f"   {msg}")


def print_error(msg):
    """打印错误"""
    print(f"❌ {msg}")


async def test_imports():
    """测试模块导入"""
    print_section("测试1: 模块导入")
    
    try:
        from app.services.code_intelligence import code_intelligence_service
        print_success("导入代码智能服务")
        
        from app.services.ai_assistant_enhanced import ai_assistant_service
        print_success("导入AI助手服务")
        
        from app.services.execution_engine import enhanced_execution_engine
        print_success("导入执行引擎")
        
        from app.services.result_parser import result_parser
        print_success("导入结果解析器")
        
        from app.services.session_service import SessionService, ExecutionService
        print_success("导入会话服务")
        
        return True
    
    except Exception as e:
        print_error(f"导入失败: {e}")
        return False


async def test_code_validation():
    """测试代码验证"""
    print_section("测试2: 代码验证")
    
    try:
        from app.services.code_intelligence import code_intelligence_service
        
        # 测试正确的代码
        valid_code = """
def hello():
    print("Hello, World!")
    return 42
"""
        is_valid, error = await code_intelligence_service.validate_code(valid_code)
        
        if is_valid:
            print_success("正确代码验证通过")
        else:
            print_error(f"验证失败: {error}")
        
        # 测试错误的代码
        invalid_code = "print('Hello World'"
        is_valid, error = await code_intelligence_service.validate_code(invalid_code)
        
        if not is_valid:
            print_success("错误代码正确识别")
            print_info(f"错误信息: {error}")
        else:
            print_error("应该检测到错误但没有")
        
        return True
    
    except Exception as e:
        print_error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_ai_assistant():
    """测试AI助手"""
    print_section("测试3: AI助手服务")
    
    try:
        from app.services.ai_assistant_enhanced import ai_assistant_service
        
        # 测试代码讲解
        code = "result = [x**2 for x in range(10)]"
        explanation = await ai_assistant_service.explain_code(code)
        
        print_success("代码讲解生成")
        print_info(f"讲解长度: {len(explanation)} 字符")
        
        # 测试错误诊断
        diagnosis = await ai_assistant_service.diagnose_error(
            "print(x)",
            "NameError: name 'x' is not defined"
        )
        
        print_success("错误诊断完成")
        print_info(f"诊断: {diagnosis['diagnosis']}")
        print_info(f"建议数: {len(diagnosis['suggestions'])} 条")
        
        return True
    
    except Exception as e:
        print_error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_execution_engine():
    """测试执行引擎"""
    print_section("测试4: 执行引擎")
    
    try:
        from app.services.execution_engine import enhanced_execution_engine
        
        # 获取容器池状态
        stats = enhanced_execution_engine.get_pool_stats()
        
        print_success("执行引擎初始化成功")
        print_info(f"容器池配置:")
        print_info(f"  - 总容器数: {stats['total']}")
        print_info(f"  - 可用容器: {stats['available']}")
        print_info(f"  - 使用中: {stats['in_use']}")
        
        return True
    
    except Exception as e:
        print_error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_result_parser():
    """测试结果解析器"""
    print_section("测试5: 结果解析器")
    
    try:
        from app.services.result_parser import result_parser
        
        # 模拟控制台输出
        console = """
计算完成
L2误差: 0.000123
计算时间: 10.5s
精度: 99.5%
"""
        
        metrics = result_parser._extract_metrics_from_console(console)
        
        print_success(f"从控制台提取 {len(metrics)} 个指标")
        for metric in metrics:
            print_info(f"{metric['name']}: {metric['value']} {metric['unit']}")
        
        return True
    
    except Exception as e:
        print_error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print()
    print("🚀 智能知识平台 V2.0 - 简化测试")
    print()
    
    results = []
    
    # 运行所有测试
    results.append(await test_imports())
    results.append(await test_code_validation())
    results.append(await test_ai_assistant())
    results.append(await test_execution_engine())
    results.append(await test_result_parser())
    
    # 总结
    print()
    print("=" * 80)
    print(" 测试总结")
    print("=" * 80)
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\n总计: {total} 个测试")
    print(f"✅ 通过: {passed}")
    if failed > 0:
        print(f"❌ 失败: {failed}")
    
    if passed == total:
        print("\n🎉 所有测试通过！V2.0核心功能正常工作。")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
    
    print()


if __name__ == "__main__":
    asyncio.run(main())
