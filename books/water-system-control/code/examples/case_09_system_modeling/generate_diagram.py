#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成案例9（传递函数建模）的系统示意图

目的：
- 展示从物理系统到传递函数的建模过程
- 说明状态空间模型和传递函数的关系
- 清晰显示建模的各个步骤
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig, ax = plt.subplots(1, 1, figsize=(16, 12), dpi=300)
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.axis('off')

# 标题
# title text removed for cleaner look
# title text removed for cleaner look

# ==================== 第1步：物理系统 ====================
# 标题
# title text removed for cleaner look

# 水箱
tank_x, tank_y = 0.5, 7.5
tank_width, tank_height = 3, 2

tank_outer = Rectangle((tank_x, tank_y), tank_width, tank_height,
                        edgecolor='black', facecolor='lightcyan', linewidth=2.5)
ax.add_patch(tank_outer)

# 水位
water_height = 1.2
water = Rectangle((tank_x, tank_y), tank_width, water_height,
                   facecolor='deepskyblue', alpha=0.6, linewidth=0)
ax.add_patch(water)
ax.plot([tank_x, tank_x + tank_width], [tank_y + water_height]*2, 'b--', linewidth=2)

# 进水
arrow_in = FancyArrowPatch((tank_x + tank_width/2, 9.5), 
                           (tank_x + tank_width/2, 9.5),
                           arrowstyle='->', mutation_scale=25,
                           linewidth=0, color='red')
ax.arrow(tank_x + tank_width/2, 10, 0, -0.5, 
         head_width=0.2, head_length=0.15, fc='red', ec='red', linewidth=2)
ax.text(tank_x + tank_width/2 + 0.3, 9.7, 'Qᵢₙ(t)', fontsize=14, 
        ha='left', va='center', color='red')

# 出水
ax.arrow(tank_x + tank_width/2, tank_y, 0, -0.5,
         head_width=0.2, head_length=0.15, fc='blue', ec='blue', linewidth=2)
ax.text(tank_x + tank_width/2 + 0.3, 7.2, 'Qₒᵤₜ(t)', fontsize=14,
        ha='left', va='center', color='blue')

# 参数
params = "A: Cross-section\nR: Resistance"
ax.text(2, 7, params, fontsize=13, ha='center', va='top',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# ==================== 第2步：物理方程 ====================
ax.text(6, 10, 'Step 2: Physical Equations', fontsize=16, weight='bold',
        ha='center', va='bottom', color='darkblue')

eq_box = FancyBboxPatch((4.5, 7.5), 3, 2,
                         boxstyle="round,pad=0.15",
                         edgecolor='darkgreen', facecolor='lightgreen',
                         linewidth=2.5, alpha=0.3)
ax.add_patch(eq_box)

equations = (
    "Mass Balance:\n"
    "A·dh/dt = Qᵢₙ - Qₒᵤₜ\n\n"
    "Outlet Flow:\n"
    "Qₒᵤₜ = h/R\n\n"
    "Differential Eq:\n"
    "A·dh/dt = Qᵢₙ - h/R"
)
ax.text(6, 8.8, equations, fontsize=14, ha='center', va='top',
        family='monospace')

# ==================== 第3步：拉普拉斯变换 ====================
ax.text(10, 10, 'Step 3: Laplace Transform', fontsize=16, weight='bold',
        ha='center', va='bottom', color='darkblue')

laplace_box = FancyBboxPatch((8.5, 7.5), 3, 2,
                             boxstyle="round,pad=0.15",
                             edgecolor='purple', facecolor='lavender',
                             linewidth=2.5, alpha=0.3)
ax.add_patch(laplace_box)

laplace_eq = (
    "Time Domain → s-Domain:\n\n"
    "A·s·H(s) = Qᵢₙ(s) - H(s)/R\n\n"
    "Rearrange:\n"
    "(A·R·s + 1)·H(s) = R·Qᵢₙ(s)"
)
ax.text(10, 8.8, laplace_eq, fontsize=14, ha='center', va='top',
        family='monospace')

# ==================== 第4步：传递函数 ====================
ax.text(14, 10, 'Step 4: Transfer Function', fontsize=16, weight='bold',
        ha='center', va='bottom', color='darkblue')

tf_box = FancyBboxPatch((12.5, 7.5), 3, 2,
                        boxstyle="round,pad=0.15",
                        edgecolor='darkred', facecolor='mistyrose',
                        linewidth=2.5, alpha=0.3)
ax.add_patch(tf_box)

tf_eq = (
    "G(s) = H(s)/Qᵢₙ(s)\n\n"
    "G(s) = R/(A·R·s + 1)\n\n"
    "G(s) = K/(τ·s + 1)\n\n"
    "K=R, τ=A·R"
)
ax.text(14, 8.8, tf_eq, fontsize=14, ha='center', va='top',
        family='monospace', weight='bold')

# 步骤之间的箭头
arrow1 = FancyArrowPatch((3.5, 8.5), (4.5, 8.5),
                         arrowstyle='->', mutation_scale=30,
                         linewidth=2.5, color='darkblue')
ax.add_patch(arrow1)

arrow2 = FancyArrowPatch((7.5, 8.5), (8.5, 8.5),
                         arrowstyle='->', mutation_scale=30,
                         linewidth=2.5, color='darkblue')
ax.add_patch(arrow2)

arrow3 = FancyArrowPatch((11.5, 8.5), (12.5, 8.5),
                         arrowstyle='->', mutation_scale=30,
                         linewidth=2.5, color='darkblue')
ax.add_patch(arrow3)

# ==================== 中部：传递函数框图 ====================
# title text removed for cleaner look

# 输入
ax.text(1, 5.5, 'Qᵢₙ(s)', fontsize=16, ha='center', va='center',
        weight='bold', color='red')

# 传递函数框
tf_block = FancyBboxPatch((3, 5), 5, 1,
                          boxstyle="round,pad=0.1",
                          edgecolor='darkblue', facecolor='lightsteelblue',
                          linewidth=3)
ax.add_patch(tf_block)
ax.text(5.5, 5.7, 'G(s) = K/(τs+1)', fontsize=16, ha='center', va='top',
        weight='bold', family='monospace')
# title text removed for cleaner look

# 输出
ax.text(10, 5.5, 'H(s)', fontsize=16, ha='center', va='center',
        weight='bold', color='blue')

# 箭头
arrow_in_tf = FancyArrowPatch((1.5, 5.5), (3, 5.5),
                              arrowstyle='->', mutation_scale=30,
                              linewidth=2.5, color='red')
ax.add_patch(arrow_in_tf)

arrow_out_tf = FancyArrowPatch((8, 5.5), (9.5, 5.5),
                               arrowstyle='->', mutation_scale=30,
                               linewidth=2.5, color='blue')
ax.add_patch(arrow_out_tf)

# ==================== 下部：状态空间模型 ====================
# title text removed for cleaner look

ss_box = FancyBboxPatch((1, 2), 5, 1.5,
                        boxstyle="round,pad=0.15",
                        edgecolor='darkgreen', facecolor='honeydew',
                        linewidth=2.5, alpha=0.8)
ax.add_patch(ss_box)

ss_eq = (
    "State Equation:\n"
    "dx/dt = A·x + B·u\n"
    "y = C·x + D·u\n\n"
    "For water tank:\n"
    "A = -1/(A·R), B = 1/A\n"
    "C = 1, D = 0"
)
ax.text(3.5, 3.3, ss_eq, fontsize=13, ha='center', va='top',
        family='monospace')

# ==================== 下部：频域特性 ====================
# title text removed for cleaner look

freq_box = FancyBboxPatch((8, 2), 5, 1.5,
                          boxstyle="round,pad=0.15",
                          edgecolor='purple', facecolor='lavender',
                          linewidth=2.5, alpha=0.8)
ax.add_patch(freq_box)

freq_eq = (
    "G(jω) = K/(jωτ + 1)\n\n"
    "Magnitude:\n"
    "|G(jω)| = K/√(1 + ω²τ²)\n\n"
    "Phase:\n"
    "∠G(jω) = -arctan(ωτ)"
)
ax.text(10.5, 3.3, freq_eq, fontsize=13, ha='center', va='top',
        family='monospace')

# 连接线
ax.plot([5.5, 5.5, 3.5, 3.5], [5, 4.5, 4.5, 4], 'g--', linewidth=2, alpha=0.6)
ax.plot([5.5, 5.5, 10.5, 10.5], [5, 4.5, 4.5, 4], 'purple', 
        linestyle='--', linewidth=2, alpha=0.6)

# ==================== 底部：模型特性 ====================
characteristics = (
    "Model Characteristics:\n\n"
    "• System Type: First-order lag\n"
    "• Time Constant: τ = A·R (response speed)\n"
    "• Static Gain: K = R (steady-state)\n"
    "• Pole Location: s = -1/τ (stability)\n"
    "• Cutoff Frequency: ωc = 1/τ\n"
    "• Response: Exponential approach to steady-state"
)

# ==================== 建模流程总结 ====================
flow_text = (
    "Modeling Process Summary:\n"
    "Physical System → Equations → Transform → Transfer Function\n"
    "         ↓              ↓           ↓              ↓\n"
    "     Components    Conservation  s-Domain    Control Design"
)

# 保存图形
plt.tight_layout()
plt.savefig('system_modeling_diagram.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("✓ 示意图已生成：system_modeling_diagram.png")

plt.close()

