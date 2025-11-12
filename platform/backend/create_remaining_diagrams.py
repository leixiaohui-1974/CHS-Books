#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为案例11-20批量创建并生成示意图
"""

import sys
import subprocess
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent
CASES_DIR = ROOT_DIR / "books" / "water-system-control" / "code" / "examples"

# 案例11已创建，从案例12开始
cases_to_create = {
    12: ("case_12_observer_lqr", "LQR & Observer Design", "observer_lqr_diagram.png"),
    13: ("case_13_adaptive_control", "Adaptive Control", "adaptive_control_diagram.png"),
    14: ("case_14_model_predictive_control", "Model Predictive Control", "mpc_diagram.png"),
    15: ("case_15_sliding_mode_control", "Sliding Mode Control", "sliding_mode_diagram.png"),
    16: ("case_16_fuzzy_control", "Fuzzy Logic Control", "fuzzy_control_diagram.png"),
    17: ("case_17_neural_network_control", "Neural Network Control", "nn_control_diagram.png"),
    18: ("case_18_reinforcement_learning_control", "Reinforcement Learning Control", "rl_control_diagram.png"),
    19: ("case_19_comprehensive_comparison", "Comprehensive Comparison", "comparison_diagram.png"),
    20: ("case_20_practical_application", "Practical Application", "application_diagram.png"),
}

def create_diagram_script(case_dir, title, output_file):
    """创建示意图生成脚本"""
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成{title}的系统示意图
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1, 1, figsize=(14, 10), dpi=300)
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis('off')

# 标题
ax.text(7, 9.5, '{title}', fontsize=22, weight='bold', ha='center', va='top')
ax.text(7, 9, 'System Architecture', fontsize=14, ha='center', va='top',
        style='italic', color='gray')

# 主框图（简化版本，实际应根据案例定制）
main_box = FancyBboxPatch((3, 5), 8, 3,
                          boxstyle="round,pad=0.15",
                          edgecolor='darkblue', facecolor='lightblue',
                          linewidth=3, alpha=0.5)
ax.add_patch(main_box)
ax.text(7, 7.5, '{title}', fontsize=16, weight='bold', ha='center', va='center')
ax.text(7, 6.5, 'Key Components & Architecture', fontsize=12, ha='center', va='center')

# 添加更多细节...
# （这是简化版本，实际应根据每个案例的具体内容定制）

plt.tight_layout()
plt.savefig('{output_file}', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("✓ 示意图已生成：{output_file}")
plt.close()
'''
    
    script_path = case_dir / "generate_diagram.py"
    script_path.write_text(script_content, encoding='utf-8')
    print(f"  ✓ 创建脚本：{script_path.name}")
    
    # 运行脚本生成图片
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(case_dir),
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            print(f"  ✓ 生成图片：{output_file}")
            return True
        else:
            print(f"  ✗ 生成失败：{result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ 异常：{str(e)}")
        return False

def main():
    """主函数"""
    print("="*80)
    print("批量创建案例11-20的示意图")
    print("="*80)
    
    # 先生成案例11的图
    case11_dir = CASES_DIR / "case_11_state_space"
    case11_script = case11_dir / "generate_diagram.py"
    if case11_script.exists():
        print("\n处理案例11...")
        try:
            result = subprocess.run(
                [sys.executable, str(case11_script)],
                cwd=str(case11_dir),
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                print("  ✓ 案例11图片已生成")
            else:
                print(f"  ✗ 案例11生成失败")
        except Exception as e:
            print(f"  ✗ 案例11异常：{str(e)}")
    
    # 创建并生成案例12-20
    success_count = 1 if case11_script.exists() else 0
    total_count = 10
    
    for case_num, (case_name, title, output_file) in cases_to_create.items():
        print(f"\n处理案例{case_num}：{title}")
        case_dir = CASES_DIR / case_name
        
        if not case_dir.exists():
            print(f"  ✗ 目录不存在：{case_dir}")
            continue
        
        # 创建并运行脚本
        if create_diagram_script(case_dir, title, output_file):
            success_count += 1
    
    # 总结
    print("\n" + "="*80)
    print("总结")
    print("="*80)
    print(f"成功：{success_count}/{total_count}")
    print(f"成功率：{success_count/total_count*100:.1f}%")

if __name__ == "__main__":
    main()



