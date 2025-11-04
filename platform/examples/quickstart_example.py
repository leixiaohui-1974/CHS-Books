"""
快速入门示例
演示如何使用平台的基本功能
"""

import sys
from pathlib import Path

# 添加SDK到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "sdk" / "python"))

from platform_sdk import PlatformSDK, SessionContext


def example_1_basic_usage():
    """示例1: 基本使用"""
    print("=" * 70)
    print(" 示例1: 基本使用")
    print("=" * 70)
    print()
    
    # 初始化SDK
    sdk = PlatformSDK(base_url="http://localhost:8000")
    
    # 创建会话
    print("1. 创建学习会话...")
    session = sdk.create_session(
        user_id="demo_user",
        book_slug="water-environment-simulation",
        case_slug="case_01_diffusion"
    )
    print(f"   ✓ 会话ID: {session['session_id']}")
    print()
    
    # 加载代码
    print("2. 加载案例代码...")
    code = sdk.load_code(
        book_slug="water-environment-simulation",
        case_slug="case_01_diffusion"
    )
    print(f"   ✓ 加载了 {len(code.get('files', []))} 个文件")
    print()
    
    # 终止会话
    print("3. 终止会话...")
    sdk.terminate_session(session['session_id'])
    print("   ✓ 会话已终止")
    print()


def example_2_with_context():
    """示例2: 使用上下文管理器"""
    print("=" * 70)
    print(" 示例2: 使用上下文管理器")
    print("=" * 70)
    print()
    
    sdk = PlatformSDK()
    
    # 使用with语句自动管理会话
    with SessionContext(
        sdk,
        user_id="demo_user",
        book_slug="water-environment-simulation",
        case_slug="case_01_diffusion"
    ) as ctx:
        print(f"会话ID: {ctx.session_id}")
        print("在这里可以执行各种操作...")
        
        # 执行代码
        # execution = ctx.execute('main.py')
        # print(f"执行ID: {execution['execution_id']}")
    
    print("会话已自动终止")
    print()


def example_3_ai_assistant():
    """示例3: 使用AI助手"""
    print("=" * 70)
    print(" 示例3: 使用AI助手")
    print("=" * 70)
    print()
    
    sdk = PlatformSDK()
    
    # 代码讲解
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    
    print("1. 请求AI讲解代码...")
    try:
        explanation = sdk.explain_code(
            code=code,
            context="斐波那契数列"
        )
        
        print("   AI讲解:")
        print(f"   {explanation.get('explanation', '(需要API密钥)')}")
        print()
        
    except Exception as e:
        print(f"   (需要配置AI API密钥)")
        print()
    
    # 知识问答
    print("2. 知识问答...")
    try:
        answer = sdk.ask_question(
            question="什么是有限差分法？",
            context={"topic": "数值计算"}
        )
        
        print("   AI回答:")
        print(f"   {answer.get('answer', '(需要API密钥)')}")
        print()
        
    except Exception as e:
        print(f"   (需要配置AI API密钥)")
        print()


def example_4_code_analysis():
    """示例4: 代码分析"""
    print("=" * 70)
    print(" 示例4: 代码分析")
    print("=" * 70)
    print()
    
    sdk = PlatformSDK()
    
    code = """
import numpy as np
from scipy import integrate

class DiffusionSolver:
    \"\"\"扩散方程求解器\"\"\"
    
    def __init__(self, D, L, T):
        self.D = D
        self.L = L
        self.T = T
    
    def solve(self, nx=100, nt=1000):
        \"\"\"求解扩散方程\"\"\"
        dx = self.L / (nx - 1)
        dt = self.T / nt
        r = self.D * dt / (dx ** 2)
        
        # 初始化
        u = np.zeros(nx)
        u[int(nx/2)] = 1.0
        
        # 时间循环
        for n in range(nt):
            un = u.copy()
            for i in range(1, nx-1):
                u[i] = un[i] + r * (un[i+1] - 2*un[i] + un[i-1])
        
        return u
"""
    
    print("1. 分析代码结构...")
    try:
        analysis = sdk.analyze_code(code)
        
        print(f"   ✓ 函数数: {analysis.get('functions', '(未配置)')}")
        print(f"   ✓ 类数: {analysis.get('classes', '(未配置)')}")
        print(f"   ✓ 导入: {analysis.get('imports', '(未配置)')}")
        print()
        
    except Exception as e:
        print(f"   分析结果: (功能可用，需启动服务)")
        print()
    
    print("2. 验证代码语法...")
    try:
        result = sdk.validate_code(code)
        
        if result.get('is_valid'):
            print("   ✓ 代码语法正确")
        else:
            print("   ✗ 发现语法错误")
            for error in result.get('errors', []):
                print(f"     - {error}")
        print()
        
    except Exception as e:
        print(f"   验证结果: (功能可用，需启动服务)")
        print()


def example_5_quick_execute():
    """示例5: 快速执行"""
    print("=" * 70)
    print(" 示例5: 一键快速执行")
    print("=" * 70)
    print()
    
    sdk = PlatformSDK()
    
    print("使用quick_execute方法一键完成:")
    print("  • 创建会话")
    print("  • 加载代码")
    print("  • 启动执行")
    print()
    
    try:
        result = sdk.quick_execute(
            user_id="demo_user",
            book_slug="water-environment-simulation",
            case_slug="case_01_diffusion"
        )
        
        print("✓ 执行完成")
        print(f"  会话ID: {result['session']['session_id']}")
        print(f"  执行ID: {result['execution']['execution_id']}")
        print()
        
    except Exception as e:
        print(f"(需要启动服务才能执行)")
        print()


def main():
    """主函数"""
    print()
    print("*" * 70)
    print(" 智能知识平台 - 快速入门示例")
    print("*" * 70)
    print()
    print("提示: 这些示例需要平台服务运行在 http://localhost:8000")
    print("      启动方法: python3 deploy.py")
    print()
    
    input("按回车键开始示例...")
    print()
    
    try:
        # 运行示例
        example_1_basic_usage()
        
        input("按回车键继续下一个示例...")
        example_2_with_context()
        
        input("按回车键继续下一个示例...")
        example_3_ai_assistant()
        
        input("按回车键继续下一个示例...")
        example_4_code_analysis()
        
        input("按回车键继续下一个示例...")
        example_5_quick_execute()
        
        print("*" * 70)
        print(" 所有示例演示完成！")
        print("*" * 70)
        print()
        print("更多信息:")
        print("  • 用户手册: USER_MANUAL.md")
        print("  • SDK文档: sdk/python/platform_sdk.py")
        print("  • API文档: http://localhost:8000/docs")
        print()
        
    except KeyboardInterrupt:
        print("\n\n示例已中断。")


if __name__ == "__main__":
    main()
