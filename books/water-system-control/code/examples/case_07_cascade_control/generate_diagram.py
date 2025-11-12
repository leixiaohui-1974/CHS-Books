#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成案例7（双水箱串级控制）的系统示意图

目的：
- 展示双水箱串级控制系统架构
- 说明副回路（副PID）和主回路（主PID）的结构
- 清晰显示各组件及其连接关系
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig, ax = plt.subplots(1, 1, figsize=(16, 10), dpi=300)
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis('off')

# 标题
# title text removed for cleaner look
# title text removed for cleaner look

# ==================== 主回路控制器 ====================
main_ctrl_box = FancyBboxPatch((0.5, 6), 2.5, 1.5, 
                                boxstyle="round,pad=0.1", 
                                edgecolor='darkblue', facecolor='lightblue', 
                                linewidth=3, zorder=10)
ax.add_patch(main_ctrl_box)
# ax.text(1.75, 7.2, 'Master PID', fontsize=16, weight='bold', ha='center', va='top')
# title text removed for cleaner look
ax.text(1.75, 6.5, 'Kp1, Ki1, Kd1', fontsize=14, ha='center', va='center', 
        color='darkblue', style='italic')

# ==================== 副回路控制器 ====================
slave_ctrl_box = FancyBboxPatch((4, 6), 2.5, 1.5,
                                 boxstyle="round,pad=0.1",
                                 edgecolor='darkgreen', facecolor='lightgreen',
                                 linewidth=3, zorder=10)
ax.add_patch(slave_ctrl_box)
# ax.text(5.25, 7.2, 'Slave PID', fontsize=16, weight='bold', ha='center', va='top')
# title text removed for cleaner look
ax.text(5.25, 6.5, 'Kp2, Ki2, Kd2', fontsize=14, ha='center', va='center',
        color='darkgreen', style='italic')

# ==================== 泵 ====================
pump_circle = Circle((8, 6.75), 0.6, edgecolor='red', facecolor='lightsalmon', linewidth=3)
ax.add_patch(pump_circle)
ax.text(8, 6.75, 'Pump', fontsize=16, weight='bold', ha='center', va='center')
ax.text(8, 6.2, 'u(t)', fontsize=14, ha='center', va='top', style='italic')

# ==================== 水箱1（上游）====================
tank1_x, tank1_y = 10, 5
tank1_width, tank1_height = 2, 2.5

# 水箱外壁
tank1_outer = Rectangle((tank1_x, tank1_y), tank1_width, tank1_height,
                         edgecolor='black', facecolor='lightcyan', linewidth=3)
ax.add_patch(tank1_outer)

# 水位
water1_height = 1.8
water1 = Rectangle((tank1_x, tank1_y), tank1_width, water1_height,
                    facecolor='deepskyblue', alpha=0.6, linewidth=0)
ax.add_patch(water1)

# 标签
ax.text(11, 7.8, 'Tank 1', fontsize=16, weight='bold', ha='center', va='bottom')
ax.text(11, 5.2, 'A₁, R₁', fontsize=14, ha='center', va='bottom', style='italic')

# 水位线
ax.plot([tank1_x, tank1_x + tank1_width], [tank1_y + water1_height]*2, 
        'b--', linewidth=2)
ax.text(tank1_x + tank1_width + 0.1, tank1_y + water1_height, 'h₁(t)', 
        fontsize=15, ha='left', va='center', color='blue', weight='bold')

# 出口
outlet1_y = tank1_y + 0.3
ax.plot([tank1_x + tank1_width, tank1_x + tank1_width + 0.3], [outlet1_y]*2,
        'k-', linewidth=3)

# ==================== 水箱2（下游）====================
tank2_x, tank2_y = 13.5, 5
tank2_width, tank2_height = 2, 2.5

# 水箱外壁
tank2_outer = Rectangle((tank2_x, tank2_y), tank2_width, tank2_height,
                         edgecolor='black', facecolor='lightcyan', linewidth=3)
ax.add_patch(tank2_outer)

# 水位
water2_height = 1.5
water2 = Rectangle((tank2_x, tank2_y), tank2_width, water2_height,
                    facecolor='dodgerblue', alpha=0.6, linewidth=0)
ax.add_patch(water2)

# 标签
ax.text(14.5, 7.8, 'Tank 2', fontsize=16, weight='bold', ha='center', va='bottom')
ax.text(14.5, 5.2, 'A₂, R₂', fontsize=14, ha='center', va='bottom', style='italic')

# 水位线
ax.plot([tank2_x, tank2_x + tank2_width], [tank2_y + water2_height]*2,
        'b--', linewidth=2)
ax.text(tank2_x + tank2_width + 0.1, tank2_y + water2_height, 'h₂(t)', 
        fontsize=15, ha='left', va='center', color='blue', weight='bold')

# 出口
outlet2_y = tank2_y + 0.3
ax.arrow(tank2_x + tank2_width/2, tank2_y, 0, -0.5, 
         head_width=0.2, head_length=0.2, fc='blue', ec='blue', linewidth=2)
ax.text(tank2_x + tank2_width/2, tank2_y - 0.7, 'Outflow', 
        fontsize=14, ha='center', va='top')

# ==================== 信号流 ====================

# 设定值 -> 主控制器
arrow1 = FancyArrowPatch((0.2, 6.75), (0.5, 6.75),
                         arrowstyle='->', mutation_scale=30, 
                         linewidth=2.5, color='purple')
ax.add_patch(arrow1)
ax.text(0.1, 6.4, '(Setpoint)', fontsize=13, ha='right', va='center', 
        style='italic', color='purple')

# 主控制器 -> 副控制器
arrow2 = FancyArrowPatch((3, 6.75), (4, 6.75),
                         arrowstyle='->', mutation_scale=30,
                         linewidth=2.5, color='darkblue')
ax.add_patch(arrow2)
# ax.text(3.5, 7, 'SP₁(t)', fontsize=14, ha='center', va='bottom', color='darkblue')

# 副控制器 -> 泵
arrow3 = FancyArrowPatch((6.5, 6.75), (7.4, 6.75),
                         arrowstyle='->', mutation_scale=30,
                         linewidth=2.5, color='darkgreen')
ax.add_patch(arrow3)
# ax.text(7, 7, 'u(t)', fontsize=14, ha='center', va='bottom', color='darkgreen')

# 泵 -> 水箱1
arrow4 = FancyArrowPatch((8.6, 6.75), (10, 6.75),
                         arrowstyle='->', mutation_scale=30,
                         linewidth=2.5, color='red')
ax.add_patch(arrow4)
ax.text(9.3, 7, 'Qᵢₙ', fontsize=14, ha='center', va='bottom', color='red')

# 水箱1 -> 水箱2（流量）
flow_arrow = FancyArrowPatch((12, outlet1_y), (13.5, outlet1_y),
                             arrowstyle='->', mutation_scale=30,
                             linewidth=2.5, color='blue')
ax.add_patch(flow_arrow)
ax.text(12.75, outlet1_y + 0.3, 'Q₁₂', fontsize=14, ha='center', va='bottom', color='blue')

# 水箱1反馈 -> 副控制器（副回路）
ax.plot([11, 11, 5.25, 5.25], [tank1_y + water1_height, 4.5, 4.5, 6], 
        'b--', linewidth=2)
arrow_fb1 = FancyArrowPatch((5.25, 4.5), (5.25, 6),
                            arrowstyle='->', mutation_scale=25,
                            linewidth=0, color='blue')
ax.add_patch(arrow_fb1)
ax.text(5.5, 4.7, 'Feedback 1', fontsize=13, ha='left', va='center',
        style='italic', color='blue')

# 水箱2反馈 -> 主控制器（主回路）
ax.plot([14.5, 14.5, 1.75, 1.75], [tank2_y + water2_height, 3.5, 3.5, 6],
        'r--', linewidth=2)
arrow_fb2 = FancyArrowPatch((1.75, 3.5), (1.75, 6),
                            arrowstyle='->', mutation_scale=25,
                            linewidth=0, color='red')
ax.add_patch(arrow_fb2)
ax.text(2, 4.2, 'Feedback 2', fontsize=13, ha='left', va='center',
        style='italic', color='red')

# ==================== 控制回路标注 ====================

# 副回路（内环）
slave_loop = mpatches.FancyBboxPatch((3.5, 4), 8.5, 4.3,
                                      boxstyle="round,pad=0.15",
                                      edgecolor='green', facecolor='none',
                                      linewidth=2, linestyle='--', alpha=0.6)
ax.add_patch(slave_loop)

# 主回路（外环）
master_loop = mpatches.FancyBboxPatch((0.3, 3), 15.3, 5.3,
                                       boxstyle="round,pad=0.15",
                                       edgecolor='darkred', facecolor='none',
                                       linewidth=2, linestyle='--', alpha=0.6)
ax.add_patch(master_loop)
ax.text(8, 2.5, 'Master Loop (Outer Loop)', fontsize=16, weight='bold',
        ha='center', va='top', color='darkred',
        bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))

# ==================== 系统参数说明 ====================
param_text = (
    "System Parameters:\n"
    "• Tank 1: A₁=1.0m², R₁=2.0min/m²\n"
    "• Tank 2: A₂=1.0m², R₂=2.0min/m²\n"
    "• Master PID: Kp1, Ki1, Kd1\n"
    "• Slave PID: Kp2, Ki2, Kd2\n"
    "• Target: h₂(t) → Setpoint"
)

# ==================== 控制策略说明 ====================
strategy_text = (
    "Cascade Control Strategy:\n"
    "1. Master Controller:\n"
    "   Controls final output h₂(t)\n"
    "   Sets SP for slave loop\n\n"
    "2. Slave Controller:\n"
    "   Controls intermediate h₁(t)\n"
    "   Fast disturbance rejection\n\n"
    "3. Advantages:\n"
    "   • Better disturbance rejection\n"
    "   • Faster response\n"
    "   • Improved stability"
)

# 保存图形
plt.tight_layout()
plt.savefig('cascade_control_diagram.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print("✓ 示意图已生成：cascade_control_diagram.png")

plt.close()

