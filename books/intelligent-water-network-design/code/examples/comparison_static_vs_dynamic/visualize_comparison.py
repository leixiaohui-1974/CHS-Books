#!/usr/bin/env python3
"""
性能对比可视化工具
==================

功能: 生成静态设计vs动态设计的详细对比图表

使用方法:
    python visualize_comparison.py
    
输出:
    - comprehensive_comparison.png (综合对比图)
    - performance_radar.png (雷达图)
    - lifecycle_cost.png (全生命周期成本)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# 对比数据
comparison_data = {
    '静态设计': {
        '工况数量': 2,
        '控制精度(cm)': 30,
        '响应时间(分钟)': 45,
        '初始投资(万元)': 30,
        '年运行成本(万元)': 180,
        '人工数量': 13,
        '智能化等级': 0,
        '代码行数': 400,
        '自动化程度': 20,
        '控制精度评分': 30,
        '响应速度评分': 30,
        '鲁棒性评分': 40,
        '可维护性评分': 50
    },
    'L2级动态设计': {
        '工况数量': 100,
        '控制精度(cm)': 3,
        '响应时间(分钟)': 4,
        '初始投资(万元)': 35,
        '年运行成本(万元)': 120,
        '人工数量': 3,
        '智能化等级': 2,
        '代码行数': 600,
        '自动化程度': 85,
        '控制精度评分': 90,
        '响应速度评分': 88,
        '鲁棒性评分': 82,
        '可维护性评分': 85
    },
    'L3级协调控制': {
        '工况数量': 200,
        '控制精度(cm)': 2,
        '响应时间(分钟)': 3.5,
        '初始投资(万元)': 180,
        '年运行成本(万元)': 380,
        '人工数量': 8,
        '智能化等级': 3,
        '代码行数': 900,
        '自动化程度': 95,
        '控制精度评分': 95,
        '响应速度评分': 90,
        '鲁棒性评分': 90,
        '可维护性评分': 90
    }
}

print("="*80)
print("  性能对比可视化工具")
print("="*80)
print()

# ============================================================================
# 图1: 综合对比图 (6个子图)
# ============================================================================

print("【图1】生成综合对比图...")

fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

designs = list(comparison_data.keys())
colors = ['#808080', '#4472C4', '#70AD47']  # 灰色、蓝色、绿色

# 子图1: 工况数量对比
ax1 = fig.add_subplot(gs[0, 0])
workloads = [comparison_data[d]['工况数量'] for d in designs]
bars = ax1.bar(range(len(designs)), workloads, color=colors, alpha=0.8)
ax1.set_ylabel('Test Cases', fontsize=11, fontweight='bold')
ax1.set_title('(1) Design Workload', fontsize=12, fontweight='bold')
ax1.set_xticks(range(len(designs)))
ax1.set_xticklabels(['Static', 'L2', 'L3'], fontsize=10)
ax1.grid(axis='y', alpha=0.3)
for i, (bar, val) in enumerate(zip(bars, workloads)):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(val)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# 子图2: 控制精度对比
ax2 = fig.add_subplot(gs[0, 1])
precision = [comparison_data[d]['控制精度(cm)'] for d in designs]
bars = ax2.bar(range(len(designs)), precision, color=colors, alpha=0.8)
ax2.set_ylabel('Error (cm)', fontsize=11, fontweight='bold')
ax2.set_title('(2) Control Precision', fontsize=12, fontweight='bold')
ax2.set_xticks(range(len(designs)))
ax2.set_xticklabels(['Static', 'L2', 'L3'], fontsize=10)
ax2.grid(axis='y', alpha=0.3)
# 反向标注(越小越好)
for bar, val in zip(bars, precision):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'±{val}cm', ha='center', va='bottom', fontsize=10, fontweight='bold')
# 添加改进箭头
ax2.annotate('', xy=(1, 3), xytext=(0, 30),
            arrowprops=dict(arrowstyle='->', lw=2, color='red'))
ax2.text(0.5, 16, '10x', fontsize=12, color='red', fontweight='bold')

# 子图3: 响应时间对比
ax3 = fig.add_subplot(gs[0, 2])
response = [comparison_data[d]['响应时间(分钟)'] for d in designs]
bars = ax3.bar(range(len(designs)), response, color=colors, alpha=0.8)
ax3.set_ylabel('Time (min)', fontsize=11, fontweight='bold')
ax3.set_title('(3) Response Speed', fontsize=12, fontweight='bold')
ax3.set_xticks(range(len(designs)))
ax3.set_xticklabels(['Static', 'L2', 'L3'], fontsize=10)
ax3.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, response):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:.1f}min', ha='center', va='bottom', fontsize=10, fontweight='bold')

# 子图4: 人工数量对比
ax4 = fig.add_subplot(gs[1, 0])
manpower = [comparison_data[d]['人工数量'] for d in designs]
bars = ax4.bar(range(len(designs)), manpower, color=colors, alpha=0.8)
ax4.set_ylabel('Staff', fontsize=11, fontweight='bold')
ax4.set_title('(4) Manpower Required', fontsize=12, fontweight='bold')
ax4.set_xticks(range(len(designs)))
ax4.set_xticklabels(['Static', 'L2', 'L3'], fontsize=10)
ax4.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, manpower):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(val)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# 子图5: 初始投资对比
ax5 = fig.add_subplot(gs[1, 1])
investment = [comparison_data[d]['初始投资(万元)'] for d in designs]
bars = ax5.bar(range(len(designs)), investment, color=colors, alpha=0.8)
ax5.set_ylabel('Investment (10K CNY)', fontsize=11, fontweight='bold')
ax5.set_title('(5) Initial Investment', fontsize=12, fontweight='bold')
ax5.set_xticks(range(len(designs)))
ax5.set_xticklabels(['Static', 'L2', 'L3*'], fontsize=10)
ax5.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, investment):
    height = bar.get_height()
    pct = (val/investment[0]-1)*100
    if pct > 0:
        label = f'{int(val)}\n(+{pct:.0f}%)'
    else:
        label = f'{int(val)}'
    ax5.text(bar.get_x() + bar.get_width()/2., height,
            label, ha='center', va='bottom', fontsize=9, fontweight='bold')
ax5.text(0.5, -30, '*4 gates', fontsize=8, ha='center')

# 子图6: 年运行成本对比
ax6 = fig.add_subplot(gs[1, 2])
annual_cost = [comparison_data[d]['年运行成本(万元)'] for d in designs]
bars = ax6.bar(range(len(designs)), annual_cost, color=colors, alpha=0.8)
ax6.set_ylabel('Cost (10K CNY/year)', fontsize=11, fontweight='bold')
ax6.set_title('(6) Annual Operating Cost', fontsize=12, fontweight='bold')
ax6.set_xticks(range(len(designs)))
ax6.set_xticklabels(['Static', 'L2', 'L3*'], fontsize=10)
ax6.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, annual_cost):
    height = bar.get_height()
    savings = annual_cost[0] - val
    if savings > 0:
        label = f'{int(val)}\n(-{int(savings)})'
    else:
        label = f'{int(val)}'
    ax6.text(bar.get_x() + bar.get_width()/2., height,
            label, ha='center', va='bottom', fontsize=9, fontweight='bold')

# 子图7: 智能化等级
ax7 = fig.add_subplot(gs[2, 0])
intelligence = [comparison_data[d]['智能化等级'] for d in designs]
bars = ax7.bar(range(len(designs)), intelligence, color=colors, alpha=0.8)
ax7.set_ylabel('Intelligence Level', fontsize=11, fontweight='bold')
ax7.set_title('(7) Intelligence Level', fontsize=12, fontweight='bold')
ax7.set_xticks(range(len(designs)))
ax7.set_xticklabels(['Static', 'L2', 'L3'], fontsize=10)
ax7.set_ylim(0, 5)
ax7.set_yticks(range(6))
ax7.set_yticklabels(['L0', 'L1', 'L2', 'L3', 'L4', 'L5'])
ax7.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, intelligence):
    height = bar.get_height()
    ax7.text(bar.get_x() + bar.get_width()/2., height,
            f'L{int(val)}', ha='center', va='bottom', fontsize=11, fontweight='bold')

# 子图8: 代码复杂度
ax8 = fig.add_subplot(gs[2, 1])
code_lines = [comparison_data[d]['代码行数'] for d in designs]
bars = ax8.bar(range(len(designs)), code_lines, color=colors, alpha=0.8)
ax8.set_ylabel('Lines of Code', fontsize=11, fontweight='bold')
ax8.set_title('(8) Code Complexity', fontsize=12, fontweight='bold')
ax8.set_xticks(range(len(designs)))
ax8.set_xticklabels(['Static', 'L2', 'L3'], fontsize=10)
ax8.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, code_lines):
    height = bar.get_height()
    ax8.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(val)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# 子图9: 性能提升总结
ax9 = fig.add_subplot(gs[2, 2])
ax9.axis('off')
summary_text = """
Performance Improvement:
━━━━━━━━━━━━━━━━━━━━━━━━
Static → L2:
  • Precision: 10x ↑
  • Speed: 11x ↑
  • Manpower: 77% ↓
  • Cost: +17% initial
         -33% annual

L2 → L3:
  • Precision: 1.5x ↑
  • Coordination: 4 gates
  • Global Optimization: ✓
  • Cost: +29% initial
         (4 gates system)

Key Findings:
  ✓ Dynamic inherits static
  ✓ 10-15x performance gain
  ✓ +17% investment (L2)
  ✓ Payback: 3-5 years
"""
ax9.text(0.1, 0.5, summary_text, fontsize=10, family='monospace',
        verticalalignment='center', bbox=dict(boxstyle='round', 
        facecolor='wheat', alpha=0.3))

plt.suptitle('Static Design vs Dynamic Design - Comprehensive Comparison',
            fontsize=16, fontweight='bold', y=0.98)

plt.savefig('comprehensive_comparison.png', dpi=200, bbox_inches='tight')
print("✓ comprehensive_comparison.png")

# ============================================================================
# 图2: 雷达图对比
# ============================================================================

print("【图2】生成雷达图...")

fig = plt.figure(figsize=(12, 10))

# 评估维度
categories = ['Automation', 'Precision', 'Response', 'Robustness', 'Maintainability']
N = len(categories)

# 计算角度
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

# 创建雷达图
ax = fig.add_subplot(111, projection='polar')

# 绘制三个设计方案
for design, color in zip(designs, colors):
    values = [
        comparison_data[design]['自动化程度'],
        comparison_data[design]['控制精度评分'],
        comparison_data[design]['响应速度评分'],
        comparison_data[design]['鲁棒性评分'],
        comparison_data[design]['可维护性评分']
    ]
    values += values[:1]
    
    ax.plot(angles, values, 'o-', linewidth=2, label=design, color=color)
    ax.fill(angles, values, alpha=0.15, color=color)

# 设置刻度
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=11)
ax.set_ylim(0, 100)
ax.set_yticks([20, 40, 60, 80, 100])
ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
ax.grid(True, alpha=0.3)

# 添加图例
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)

plt.title('Intelligence Level Assessment - Radar Chart\n(5 Dimensions, 0-100 Score)',
         fontsize=14, fontweight='bold', pad=20)

plt.savefig('performance_radar.png', dpi=200, bbox_inches='tight')
print("✓ performance_radar.png")

# ============================================================================
# 图3: 全生命周期成本对比
# ============================================================================

print("【图3】生成全生命周期成本图...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# 子图1: 20年累计成本
years = np.arange(0, 21)
costs_static = [30 + 180*y for y in years]
costs_L2 = [35 + 120*y for y in years]
costs_L3 = [180 + 380*y for y in years]  # 4个闸门

ax1.plot(years, costs_static, 'o-', linewidth=2, color=colors[0], label='Static Design', markersize=4)
ax1.plot(years, costs_L2, 's-', linewidth=2, color=colors[1], label='L2 Dynamic Design', markersize=4)
ax1.plot(years, costs_L3, '^-', linewidth=2, color=colors[2], label='L3 Coordinated (4 gates)', markersize=4)

ax1.set_xlabel('Years', fontsize=12, fontweight='bold')
ax1.set_ylabel('Cumulative Cost (10K CNY)', fontsize=12, fontweight='bold')
ax1.set_title('(a) 20-Year Lifecycle Cost Comparison', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=11)

# 标注投资回收期
# L2 vs Static: (35-30) = (180-120)*t → t = 5/60 ≈ 0.08年 (立即回收)
# 实际应该考虑增量投资和年节省
payback_L2 = (35-30) / (180-120)  # 年
ax1.axvline(x=payback_L2, color=colors[1], linestyle='--', alpha=0.5)
ax1.text(payback_L2+0.5, 2000, f'L2 Payback\n{payback_L2:.2f} years',
        fontsize=9, color=colors[1], bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# 子图2: 增量成本与节省
ax2 = fig.add_subplot(122)

x = np.arange(3)
width = 0.35

initial_inc = [0, 5, 150]  # 相对静态设计的增量
annual_save = [0, 60, 0]   # 年节省(相对静态设计)

bars1 = ax2.bar(x - width/2, initial_inc, width, label='Initial Investment Increment',
               color='coral', alpha=0.8)
bars2 = ax2.bar(x + width/2, annual_save, width, label='Annual Cost Savings',
               color='lightgreen', alpha=0.8)

ax2.set_ylabel('Cost (10K CNY)', fontsize=12, fontweight='bold')
ax2.set_title('(b) Investment Increment vs Annual Savings', fontsize=13, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(['Static', 'L2', 'L3 (4 gates)'])
ax2.legend(fontsize=10)
ax2.grid(axis='y', alpha=0.3)

# 添加数值标签
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('lifecycle_cost.png', dpi=200, bbox_inches='tight')
print("✓ lifecycle_cost.png")

# ============================================================================
# 总结
# ============================================================================

print()
print("="*80)
print("  可视化图表生成完成!")
print("="*80)
print()
print("生成的文件:")
print("  1. comprehensive_comparison.png - 综合对比图(9个子图)")
print("  2. performance_radar.png - 雷达图(5维度评估)")
print("  3. lifecycle_cost.png - 全生命周期成本分析")
print()
print("="*80)
