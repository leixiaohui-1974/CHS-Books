#!/usr/bin/env python3
"""
静态设计与动态设计对比 - 命令行工具
====================================

功能: 整合所有工具的命令行界面

使用方法:
    python3 cli.py [command] [options]
    
    或交互模式:
    python3 cli.py

可用命令:
    run         - 运行仿真脚本
    analyze     - 性能分析
    optimize    - PID参数优化
    evaluate    - 智能化等级评估
    cost        - 成本效益分析
    visualize   - 快速可视化
    config      - 配置生成
    help        - 显示帮助
"""

import sys
import os
import subprocess
from typing import List, Dict

# ============================================================================
# 工具映射
# ============================================================================

TOOLS = {
    'static': {
        'script': 'static_design.py',
        'desc': '运行静态设计脚本',
        'time': '~5秒',
        'outputs': ['static_design_discharge_curve.png', 'static_design_operation_manual.txt']
    },
    'l2': {
        'script': 'dynamic_design_L2.py',
        'desc': '运行L2级动态设计脚本',
        'time': '~15分钟',
        'outputs': ['dynamic_L2_*.png (4张)']
    },
    'l3': {
        'script': 'dynamic_design_L3.py',
        'desc': '运行L3级协调控制脚本',
        'time': '~30分钟',
        'outputs': ['dynamic_L3_*.png (4张)']
    },
    'compare': {
        'script': 'run_all_comparison.py',
        'desc': '一键对比运行所有脚本',
        'time': '~50分钟',
        'outputs': ['comparison_report.txt', 'comparison_chart.png']
    },
    'visualize': {
        'script': 'visualize_comparison.py',
        'desc': '快速生成对比图表',
        'time': '~5秒',
        'outputs': ['comprehensive_comparison.png', 'performance_radar.png', 'lifecycle_cost.png']
    },
    'analyze': {
        'script': 'performance_analyzer.py',
        'desc': '详细性能分析',
        'time': '~5秒',
        'outputs': ['performance_analysis_report.txt', 'performance_comparison_detailed.png']
    },
    'optimize': {
        'script': 'pid_tuner.py',
        'desc': 'PID参数自动优化',
        'time': '~0.1秒',
        'outputs': ['pid_tuning_results.txt', 'pid_tuning_comparison.png', 'pid_optimal_performance.png']
    },
    'evaluate': {
        'script': 'intelligence_evaluator.py',
        'desc': '智能化等级评估',
        'time': '~5秒',
        'outputs': ['intelligence_evaluation_*.txt', 'intelligence_radar_*.png']
    },
    'cost': {
        'script': 'cost_benefit_calculator.py',
        'desc': '成本效益分析',
        'time': '~5秒',
        'outputs': ['cost_benefit_report.txt', 'cost_benefit_comparison.png']
    },
    'config': {
        'script': 'config_generator.py',
        'desc': '配置文件生成',
        'time': '~5秒',
        'outputs': ['project_config.json']
    }
}

# ============================================================================
# CLI类
# ============================================================================

class CLI:
    """命令行界面"""
    
    def __init__(self):
        self.banner = """
================================================================================
     静态设计 vs 动态设计 - 综合工具箱 v1.0
================================================================================
"""
    
    def print_banner(self):
        print(self.banner)
    
    def print_help(self):
        """显示帮助信息"""
        print("""
可用命令:

【运行仿真】
  run static      - 运行静态设计 (~5秒)
  run l2          - 运行L2级动态设计 (~15分钟)
  run l3          - 运行L3级协调控制 (~30分钟)
  run compare     - 一键对比运行全部 (~50分钟)

【分析工具】
  visualize       - 快速可视化对比 (~5秒) ⭐推荐
  analyze         - 详细性能分析 (~5秒)
  optimize        - PID参数优化 (~0.1秒)
  evaluate        - 智能化等级评估 (~5秒)
  cost            - 成本效益分析 (~5秒)

【配置工具】
  config          - 配置文件生成 (~5秒)
  config -i       - 交互式配置

【其他】
  list            - 列出所有工具
  status          - 查看输出文件状态
  clean           - 清理输出文件
  help            - 显示此帮助
  exit/quit       - 退出

示例:
  cli.py visualize         # 快速查看对比图
  cli.py run static        # 运行静态设计
  cli.py optimize          # 优化PID参数
  cli.py cost              # 成本分析
        """)
    
    def list_tools(self):
        """列出所有工具"""
        print("\n所有可用工具:")
        print("="*80)
        print(f"{'命令':<15} {'描述':<30} {'预计耗时':<15} {'状态'}")
        print("-"*80)
        
        for name, info in TOOLS.items():
            script = info['script']
            exists = '✅' if os.path.exists(script) else '❌'
            print(f"{name:<15} {info['desc']:<30} {info['time']:<15} {exists}")
        
        print("="*80)
    
    def check_status(self):
        """检查输出文件状态"""
        print("\n输出文件状态:")
        print("="*80)
        
        all_outputs = []
        for name, info in TOOLS.items():
            for output in info['outputs']:
                if '*' not in output:
                    all_outputs.append((name, output))
        
        existing = 0
        missing = 0
        
        for tool, filename in all_outputs:
            exists = os.path.exists(filename)
            status = '✅' if exists else '❌'
            print(f"{status} {filename:<50} ({tool})")
            if exists:
                existing += 1
            else:
                missing += 1
        
        print("="*80)
        print(f"统计: ✅{existing}个  ❌{missing}个")
    
    def run_tool(self, tool_name: str, args: List[str] = None):
        """运行工具"""
        if tool_name not in TOOLS:
            print(f"错误: 未知工具 '{tool_name}'")
            print("使用 'list' 查看所有工具")
            return False
        
        info = TOOLS[tool_name]
        script = info['script']
        
        if not os.path.exists(script):
            print(f"错误: 脚本不存在 '{script}'")
            return False
        
        print(f"\n运行: {info['desc']}")
        print(f"脚本: {script}")
        print(f"预计耗时: {info['time']}")
        print(f"输出: {', '.join(info['outputs'])}")
        print("-"*80)
        
        cmd = ['python3', script]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(cmd, capture_output=False, text=True)
            
            if result.returncode == 0:
                print("-"*80)
                print(f"✓ {info['desc']}完成")
                return True
            else:
                print(f"✗ 运行失败 (退出码: {result.returncode})")
                return False
        
        except KeyboardInterrupt:
            print("\n\n用户中断")
            return False
        except Exception as e:
            print(f"错误: {e}")
            return False
    
    def clean_outputs(self):
        """清理输出文件"""
        print("\n清理输出文件...")
        
        patterns = ['*.png', '*.txt', '*.json']
        exclude = ['requirements.txt']
        
        import glob
        
        cleaned = 0
        for pattern in patterns:
            for filename in glob.glob(pattern):
                if filename not in exclude and not filename.startswith('config'):
                    try:
                        os.remove(filename)
                        print(f"  删除: {filename}")
                        cleaned += 1
                    except Exception as e:
                        print(f"  失败: {filename} ({e})")
        
        print(f"\n✓ 已清理 {cleaned} 个文件")
    
    def interactive_mode(self):
        """交互模式"""
        self.print_banner()
        print("欢迎使用综合工具箱!")
        print("输入 'help' 查看帮助, 'exit' 退出\n")
        
        while True:
            try:
                cmd = input("tool> ").strip()
                
                if not cmd:
                    continue
                
                parts = cmd.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if command in ['exit', 'quit']:
                    print("再见!")
                    break
                
                elif command == 'help':
                    self.print_help()
                
                elif command == 'list':
                    self.list_tools()
                
                elif command == 'status':
                    self.check_status()
                
                elif command == 'clean':
                    self.clean_outputs()
                
                elif command == 'run':
                    if not args:
                        print("用法: run <tool_name>")
                        print("可用: static, l2, l3, compare")
                    else:
                        self.run_tool(args[0], args[1:])
                
                elif command in TOOLS:
                    self.run_tool(command, args)
                
                else:
                    print(f"未知命令: {command}")
                    print("输入 'help' 查看帮助")
            
            except KeyboardInterrupt:
                print("\n(使用 'exit' 退出)")
            except Exception as e:
                print(f"错误: {e}")
    
    def command_mode(self, args: List[str]):
        """命令模式"""
        if not args:
            self.interactive_mode()
            return
        
        command = args[0].lower()
        cmd_args = args[1:] if len(args) > 1 else []
        
        if command in ['help', '-h', '--help']:
            self.print_banner()
            self.print_help()
        
        elif command == 'list':
            self.list_tools()
        
        elif command == 'status':
            self.check_status()
        
        elif command == 'clean':
            self.clean_outputs()
        
        elif command == 'run':
            if not cmd_args:
                print("用法: cli.py run <tool_name>")
                print("可用: static, l2, l3, compare")
            else:
                self.run_tool(cmd_args[0], cmd_args[1:])
        
        elif command in TOOLS:
            self.run_tool(command, cmd_args)
        
        else:
            print(f"未知命令: {command}")
            print("使用 'cli.py help' 查看帮助")

# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序"""
    cli = CLI()
    
    # 去掉脚本名
    args = sys.argv[1:]
    
    cli.command_mode(args)

if __name__ == '__main__':
    main()
