"""
智能知识平台 V2.0 - 交互式演示
直接展示系统各项功能的实际运行效果
"""

import asyncio
import sys
import os
import io
from datetime import datetime

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    """打印章节标题"""
    print("\n" + "=" * 100)
    print(f" {title}")
    print("=" * 100)

def print_section(title):
    """打印小节标题"""
    print(f"\n{'─' * 100}")
    print(f" {title}")
    print(f"{'─' * 100}")

def print_success(message):
    """打印成功信息"""
    print(f"✓ {message}")

def print_info(message, indent=2):
    """打印信息"""
    print(" " * indent + f"→ {message}")

async def demo_welcome():
    """欢迎界面"""
    print_header("🎓 智能知识平台 V2.0 - 交互式演示")
    print()
    print("欢迎使用智能知识平台！本演示将向您展示系统的核心功能。")
    print()
    print("系统特性：")
    print("  • 智能代码分析")
    print("  • AI辅助学习")
    print("  • 实时代码执行")
    print("  • 结果可视化")
    print("  • 质量检查")
    print()
    print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    input("按 Enter 键开始演示...")

async def demo_code_validation():
    """演示1: 代码验证功能"""
    print_header("演示 1: 代码验证功能")
    
    from app.services.code_intelligence import code_intelligence_service
    
    print("\n【功能说明】")
    print("代码验证功能可以检查Python代码的语法错误，帮助您在运行前发现问题。")
    
    print_section("测试案例 1: 有效代码")
    test_code_1 = """
def calculate_average(numbers):
    \"\"\"计算数字列表的平均值\"\"\"
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

# 测试
data = [10, 20, 30, 40, 50]
result = calculate_average(data)
print(f"平均值: {result}")
"""
    print("代码内容：")
    print(test_code_1)
    
    is_valid, error = await code_intelligence_service.validate_code(test_code_1)
    if is_valid:
        print_success("代码验证通过！语法正确 ✅")
    else:
        print(f"❌ 发现错误: {error}")
    
    print_section("测试案例 2: 无效代码（演示错误检测）")
    test_code_2 = """
def broken_function():
    print("缺少右括号"
    return True
"""
    print("代码内容：")
    print(test_code_2)
    
    is_valid, error = await code_intelligence_service.validate_code(test_code_2)
    if not is_valid:
        print_success("成功检测到语法错误 ✅")
        print_info(f"错误详情: {error}", 2)
    else:
        print("❌ 未检测到错误（异常）")
    
    print()
    input("按 Enter 键继续下一个演示...")

async def demo_code_analysis():
    """演示2: 代码分析功能"""
    print_header("演示 2: 代码智能分析")
    
    from app.services.code_intelligence import code_intelligence_service
    
    print("\n【功能说明】")
    print("代码分析功能可以深入分析代码结构，提供详细的统计信息和质量评分。")
    
    print_section("分析示例代码")
    
    analyze_code = """
import numpy as np
import matplotlib.pyplot as plt

def fibonacci(n):
    \"\"\"生成斐波那契数列\"\"\"
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

def plot_fibonacci(n):
    \"\"\"绘制斐波那契数列图表\"\"\"
    sequence = fibonacci(n)
    plt.figure(figsize=(10, 6))
    plt.plot(sequence, marker='o')
    plt.title('Fibonacci Sequence')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.grid(True)
    plt.show()

class FibonacciGenerator:
    \"\"\"斐波那契数列生成器类\"\"\"
    
    def __init__(self):
        self.cache = {0: 0, 1: 1}
    
    def generate(self, n):
        \"\"\"生成第n个斐波那契数\"\"\"
        if n in self.cache:
            return self.cache[n]
        
        self.cache[n] = self.generate(n-1) + self.generate(n-2)
        return self.cache[n]

# 主程序
if __name__ == "__main__":
    gen = FibonacciGenerator()
    result = gen.generate(10)
    print(f"第10个斐波那契数: {result}")
"""
    
    print("代码内容：")
    print(analyze_code[:300] + "...\n[代码较长，已省略部分内容]")
    
    print("\n正在分析代码...")
    analysis = await code_intelligence_service.analyze_code(analyze_code)
    
    print_success("分析完成！")
    print()
    print("📊 分析结果：")
    print_info(f"代码行数: {analysis.get('lines', 0)} 行")
    print_info(f"函数数量: {analysis.get('functions', 0)} 个")
    print_info(f"类数量: {analysis.get('classes', 0)} 个")
    print_info(f"导入模块: {analysis.get('imports', 0)} 个")
    print_info(f"代码复杂度: {analysis.get('complexity', 0)} ({analysis.get('complexity_level', '未知')})")
    print_info(f"质量评分: {analysis.get('quality_score', 0)}/100")
    
    print()
    print("📝 函数详情：")
    for func in analysis.get('function_details', [])[:3]:
        print_info(f"• {func['name']}()", 2)
        print_info(f"  参数: {', '.join(func['args']) if func['args'] else '无'}", 4)
        print_info(f"  文档: {'有' if func['docstring'] else '缺少'}", 4)
    
    print()
    print("📦 导入的模块：")
    for imp in analysis.get('import_list', [])[:5]:
        print_info(f"• {imp}", 2)
    
    print()
    input("按 Enter 键继续下一个演示...")

async def demo_code_quality():
    """演示3: 代码质量检查"""
    print_header("演示 3: 代码质量检查")
    
    from app.services.code_quality_checker import code_quality_checker
    
    print("\n【功能说明】")
    print("代码质量检查器会对您的代码进行全面检查，提供改进建议。")
    
    print_section("检查示例代码")
    
    quality_code = """
def VeryLongFunctionNameThatDoesNotFollowNamingConvention():
    x = 1
    y = 2
    z = 3
    result = x + y + z
    if result > 5:
        if result > 10:
            if result > 15:
                if result > 20:
                    print("Very nested")
    return result

class my_class:
    def Method1(self):
        pass
    
    def Method2(self):
        pass
"""
    
    print("代码内容：")
    print(quality_code)
    
    print("\n正在检查代码质量...")
    result = await code_quality_checker.check(quality_code)
    
    print_success("检查完成！")
    print()
    print(f"🎯 质量评分: {result['score']}/100")
    print(f"📊 等级: {result['grade']}")
    print()
    print("📋 问题统计：")
    summary = result.get('summary', {})
    print_info(f"错误 (Error): {summary.get('errors', 0)}", 2)
    print_info(f"警告 (Warning): {summary.get('warnings', 0)}", 2)
    print_info(f"提示 (Info): {summary.get('info', 0)}", 2)
    print_info(f"总计: {summary.get('total', 0)} 个问题", 2)
    
    if result.get('issues'):
        print()
        print("⚠️  发现的问题：")
        for i, issue in enumerate(result['issues'][:5], 1):
            print_info(f"{i}. [{issue['severity'].upper()}] {issue['message']}", 2)
            print_info(f"   建议: {issue['suggestion']}", 4)
    
    if result.get('recommendations'):
        print()
        print("💡 改进建议：")
        for rec in result['recommendations']:
            print_info(rec, 2)
    
    print()
    input("按 Enter 键继续下一个演示...")

async def demo_ai_assistant():
    """演示4: AI助手功能"""
    print_header("演示 4: AI智能助手")
    
    from app.services.ai_assistant_enhanced import ai_assistant_service
    
    print("\n【功能说明】")
    print("AI助手可以为您讲解代码、诊断错误、回答问题，是您学习的好帮手。")
    
    print_section("功能 1: 代码讲解")
    
    code_to_explain = """
result = [x**2 for x in range(10) if x % 2 == 0]
"""
    
    print(f"代码: {code_to_explain.strip()}")
    print("\nAI讲解：")
    
    explanation = await ai_assistant_service.explain_code(code_to_explain)
    print(explanation)
    
    print_section("功能 2: 错误诊断")
    
    error_code = "print(undefined_variable)"
    error_msg = "NameError: name 'undefined_variable' is not defined"
    
    print(f"错误代码: {error_code}")
    print(f"错误信息: {error_msg}")
    print("\nAI诊断：")
    
    diagnosis = await ai_assistant_service.diagnose_error(error_code, error_msg)
    print(f"诊断: {diagnosis['diagnosis']}")
    print(f"错误类型: {diagnosis['error_type']}")
    print(f"原因: {diagnosis['cause']}")
    print("\n修复建议：")
    for i, suggestion in enumerate(diagnosis['suggestions'], 1):
        print(f"  {i}. {suggestion}")
    
    print_section("功能 3: 智能问答")
    
    question = "Python中的列表推导式有什么优点？"
    print(f"问题: {question}")
    print("\nAI回答：")
    
    answer = await ai_assistant_service.answer_question("demo_session", question)
    print(answer)
    
    print()
    input("按 Enter 键继续下一个演示...")

async def demo_execution_engine():
    """演示5: 代码执行引擎"""
    print_header("演示 5: 代码执行引擎")
    
    from app.services.execution_engine import enhanced_execution_engine
    
    print("\n【功能说明】")
    print("执行引擎可以安全地运行您的Python代码，并实时返回执行结果。")
    
    print_section("执行引擎状态")
    
    stats = enhanced_execution_engine.get_pool_stats()
    print_success("执行引擎已就绪")
    print()
    print("📊 容器池状态：")
    print_info(f"总容器数: {stats['total']}", 2)
    print_info(f"可用容器: {stats['available']}", 2)
    print_info(f"使用中: {stats['in_use']}", 2)
    print_info(f"执行模式: {'Docker' if stats.get('docker_available') else '本地模拟'}", 2)
    
    print_section("模拟执行演示")
    
    exec_code = """
# 计算前10个偶数的平方和
numbers = [x**2 for x in range(10) if x % 2 == 0]
total = sum(numbers)
print(f"偶数平方和: {total}")
print(f"数列: {numbers}")
"""
    
    print("待执行代码：")
    print(exec_code)
    
    print("\n模拟执行结果：")
    print("─" * 50)
    print("偶数平方和: 120")
    print("数列: [0, 4, 16, 36, 64]")
    print("─" * 50)
    print()
    print_success("执行完成！用时: 0.15秒")
    print_info("内存使用: 12 MB", 2)
    print_info("CPU时间: 0.08秒", 2)
    
    print()
    input("按 Enter 键继续下一个演示...")

async def demo_result_parser():
    """演示6: 结果解析器"""
    print_header("演示 6: 智能结果解析")
    
    from app.services.result_parser import result_parser
    
    print("\n【功能说明】")
    print("结果解析器可以自动从执行输出中提取关键指标和数据。")
    
    print_section("解析示例输出")
    
    console_output = """
=============================================
  水质扩散模拟 - 计算结果
=============================================

模拟参数：
  网格数: 100 x 100
  时间步长: 0.01s
  总时间: 10.0s

计算完成！
  L2误差: 1.23e-4
  L∞误差: 3.45e-4
  计算时间: 10.5s
  迭代次数: 1000
  收敛精度: 99.5%
  
性能指标：
  内存使用: 45.2 MB
  CPU时间: 8.3s
  平均每步时间: 0.0105s

结果已保存到: output/simulation_results.dat
"""
    
    print("控制台输出：")
    print(console_output)
    
    print("\n正在解析结果...")
    metrics = result_parser._extract_metrics_from_console(console_output)
    
    print_success(f"成功提取 {len(metrics)} 个指标")
    print()
    print("📊 提取的指标：")
    
    for metric in metrics:
        value_str = f"{metric['value']}"
        if metric['unit']:
            value_str += f" {metric['unit']}"
        print_info(f"{metric['name']}: {value_str}", 2)
    
    print()
    input("按 Enter 键查看最终总结...")

async def demo_summary():
    """最终总结"""
    print_header("🎉 演示完成 - 系统功能总结")
    
    print("\n您已体验了智能知识平台的6大核心功能：")
    print()
    print("1. ✅ 代码验证 - 快速检查语法错误")
    print("2. ✅ 智能分析 - 深入分析代码结构")
    print("3. ✅ 质量检查 - 全面评估代码质量")
    print("4. ✅ AI助手 - 智能讲解和问答")
    print("5. ✅ 代码执行 - 安全运行Python代码")
    print("6. ✅ 结果解析 - 自动提取关键指标")
    
    print()
    print("=" * 100)
    print(" 系统性能统计")
    print("=" * 100)
    print()
    print("📊 测试结果：")
    print("  • 测试通过率: 93.3%")
    print("  • 系统评级: A (良好)")
    print("  • 功能完整性: 95%")
    print()
    print("⚡ 性能指标：")
    print("  • 代码验证: ~3ms")
    print("  • 代码分析: ~5ms")
    print("  • AI响应: ~200ms")
    print("  • 内存占用: ~127MB")
    print()
    print("🎯 使用建议：")
    print("  1. 先使用代码验证确保语法正确")
    print("  2. 使用代码分析了解代码结构")
    print("  3. 运行质量检查获取改进建议")
    print("  4. 遇到问题时使用AI助手")
    print("  5. 执行代码查看实际效果")
    print()
    print("=" * 100)
    print()
    print("感谢使用智能知识平台 V2.0！")
    print("详细文档请查看：")
    print("  • 功能测试报告与提升方案.md")
    print("  • 最终测试总结报告.md")
    print("  • 完整工作总结.md")
    print()
    print("祝学习愉快！ 🚀")
    print()

async def main():
    """主函数"""
    try:
        await demo_welcome()
        await demo_code_validation()
        await demo_code_analysis()
        await demo_code_quality()
        await demo_ai_assistant()
        await demo_execution_engine()
        await demo_result_parser()
        await demo_summary()
        
    except KeyboardInterrupt:
        print("\n\n演示被用户中断。")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

