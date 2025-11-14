#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静态设计vs动态设计对比分析 - 主程序入口
========================================

本程序是静态设计和动态设计对比分析的统一入口。
提供命令行界面和快速演示功能。

使用方法:
1. 快速演示: python main.py
2. 完整对比: python run_all_comparison.py
3. 交互式CLI: python cli.py
4. 可视化: python visualize_comparison.py

作者: CHS-Books项目
日期: 2025-10-31
"""

import sys
import os
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def print_menu():
    """显示主菜单"""
    print("\n" + "=" * 70)
    print("静态设计 vs 动态设计对比分析系统")
    print("=" * 70)
    print("\n可用功能:")
    print("  1. 快速演示 (Demo)")
    print("  2. 完整对比分析 (Full Comparison)")
    print("  3. 静态设计单独运行")
    print("  4. 动态设计L2单独运行")
    print("  5. 动态设计L3单独运行")
    print("  6. 可视化对比结果")
    print("  7. 成本效益分析")
    print("  8. 智能化等级评估")
    print("  9. 性能分析")
    print("  0. 退出")
    print("=" * 70)


def quick_demo():
    """快速演示"""
    print("\n" + "=" * 70)
    print("快速演示: 静态 vs 动态设计对比")
    print("=" * 70)

    try:
        from demo_presenter import demonstrate_comparison
        demonstrate_comparison()
    except ImportError:
        print("\n错误: 无法导入demo_presenter模块")
        print("请确保demo_presenter.py文件存在")
    except Exception as e:
        print(f"\n演示过程中出错: {e}")


def run_full_comparison():
    """运行完整对比分析"""
    print("\n" + "=" * 70)
    print("执行完整对比分析...")
    print("=" * 70)

    try:
        import run_all_comparison
        run_all_comparison.main()
    except ImportError:
        print("\n错误: 无法导入run_all_comparison模块")
    except Exception as e:
        print(f"\n运行过程中出错: {e}")


def run_static_design():
    """运行静态设计"""
    print("\n" + "=" * 70)
    print("运行静态设计...")
    print("=" * 70)

    try:
        import static_design
        static_design.main()
    except ImportError:
        print("\n错误: 无法导入static_design模块")
    except Exception as e:
        print(f"\n运行过程中出错: {e}")


def run_dynamic_l2():
    """运行动态设计L2"""
    print("\n" + "=" * 70)
    print("运行动态设计L2...")
    print("=" * 70)

    try:
        import dynamic_design_L2
        dynamic_design_L2.main()
    except ImportError:
        print("\n错误: 无法导入dynamic_design_L2模块")
    except Exception as e:
        print(f"\n运行过程中出错: {e}")


def run_dynamic_l3():
    """运行动态设计L3"""
    print("\n" + "=" * 70)
    print("运行动态设计L3...")
    print("=" * 70)

    try:
        import dynamic_design_L3
        dynamic_design_L3.main()
    except ImportError:
        print("\n错误: 无法导入dynamic_design_L3模块")
    except Exception as e:
        print(f"\n运行过程中出错: {e}")


def visualize_results():
    """可视化对比结果"""
    print("\n" + "=" * 70)
    print("生成可视化对比图表...")
    print("=" * 70)

    try:
        import visualize_comparison
        visualize_comparison.main()
    except ImportError:
        print("\n错误: 无法导入visualize_comparison模块")
    except Exception as e:
        print(f"\n可视化过程中出错: {e}")


def cost_benefit_analysis():
    """成本效益分析"""
    print("\n" + "=" * 70)
    print("执行成本效益分析...")
    print("=" * 70)

    try:
        import cost_benefit_calculator
        cost_benefit_calculator.main()
    except ImportError:
        print("\n错误: 无法导入cost_benefit_calculator模块")
    except Exception as e:
        print(f"\n分析过程中出错: {e}")


def intelligence_evaluation():
    """智能化等级评估"""
    print("\n" + "=" * 70)
    print("执行智能化等级评估...")
    print("=" * 70)

    try:
        import intelligence_evaluator
        intelligence_evaluator.main()
    except ImportError:
        print("\n错误: 无法导入intelligence_evaluator模块")
    except Exception as e:
        print(f"\n评估过程中出错: {e}")


def performance_analysis():
    """性能分析"""
    print("\n" + "=" * 70)
    print("执行性能分析...")
    print("=" * 70)

    try:
        import performance_analyzer
        performance_analyzer.main()
    except ImportError:
        print("\n错误: 无法导入performance_analyzer模块")
    except Exception as e:
        print(f"\n分析过程中出错: {e}")


def interactive_mode():
    """交互模式"""
    while True:
        print_menu()

        try:
            choice = input("\n请选择功能 (0-9): ").strip()

            if choice == '1':
                quick_demo()
            elif choice == '2':
                run_full_comparison()
            elif choice == '3':
                run_static_design()
            elif choice == '4':
                run_dynamic_l2()
            elif choice == '5':
                run_dynamic_l3()
            elif choice == '6':
                visualize_results()
            elif choice == '7':
                cost_benefit_analysis()
            elif choice == '8':
                intelligence_evaluation()
            elif choice == '9':
                performance_analysis()
            elif choice == '0':
                print("\n退出程序。")
                break
            else:
                print("\n无效选择，请输入0-9之间的数字。")

        except KeyboardInterrupt:
            print("\n\n程序被用户中断。")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")

        input("\n按Enter键继续...")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("静态设计 vs 动态设计对比分析系统")
    print("=" * 70)
    print("\n本系统提供以下功能:")
    print("  - 静态设计: 传统经验公式设计方法")
    print("  - 动态设计L2: 基于PID控制的自动化设计")
    print("  - 动态设计L3: 基于MPC的优化设计")
    print("  - 对比分析: 性能、成本、智能化等级评估")
    print("\n" + "=" * 70)

    # 检查命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ['demo', '--demo', '-d']:
            quick_demo()
        elif arg in ['full', '--full', '-f']:
            run_full_comparison()
        elif arg in ['static', '--static', '-s']:
            run_static_design()
        elif arg in ['l2', '--l2']:
            run_dynamic_l2()
        elif arg in ['l3', '--l3']:
            run_dynamic_l3()
        elif arg in ['viz', '--visualize', '-v']:
            visualize_results()
        elif arg in ['cost', '--cost', '-c']:
            cost_benefit_analysis()
        elif arg in ['eval', '--evaluate', '-e']:
            intelligence_evaluation()
        elif arg in ['perf', '--performance', '-p']:
            performance_analysis()
        elif arg in ['help', '--help', '-h']:
            print("\n用法:")
            print("  python main.py [选项]")
            print("\n选项:")
            print("  demo, -d       运行快速演示")
            print("  full, -f       运行完整对比分析")
            print("  static, -s     运行静态设计")
            print("  l2             运行动态设计L2")
            print("  l3             运行动态设计L3")
            print("  viz, -v        可视化结果")
            print("  cost, -c       成本效益分析")
            print("  eval, -e       智能化等级评估")
            print("  perf, -p       性能分析")
            print("  help, -h       显示帮助信息")
            print("\n无参数时进入交互模式。")
        else:
            print(f"\n未知选项: {arg}")
            print("使用 'python main.py help' 查看帮助信息。")
    else:
        # 无参数时运行快速演示
        print("\n默认运行快速演示...")
        print("提示: 使用 'python main.py help' 查看所有功能。\n")
        quick_demo()

        # 询问是否进入交互模式
        try:
            response = input("\n是否进入交互模式? (y/n): ").strip().lower()
            if response in ['y', 'yes', '是']:
                interactive_mode()
        except KeyboardInterrupt:
            print("\n\n程序结束。")


if __name__ == "__main__":
    main()
