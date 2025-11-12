#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成案例11（状态空间方法）的系统示意图
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1, 1, figsize=(16, 12), dpi=300)
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.axis('off')

# 标题
# title text removed for cleaner look
# title text removed for cleaner look

# 状态空间表示
ss_box = FancyBboxPatch((1, 8), 6, 2.5,
                        boxstyle="round,pad=0.15",
                        edgecolor='darkblue', facecolor='lightblue',
                        linewidth=3, alpha=0.5)
ax.add_patch(ss_box)
# title text removed for cleaner look
ss_eq = (
    "State Equation:\n"
    "dx/dt = Ax + Bu\n\n"
    "Output Equation:\n"
    "y = Cx + Du\n\n"
    "x: state vector\n"
    "u: input, y: output"
)
# ax.text(4, 9.8, ss_eq, fontsize=14, ha='center', va='top', family='monospace')

# 状态反馈控制
fb_box = FancyBboxPatch((9, 8), 6, 2.5,
                        boxstyle="round,pad=0.15",
                        edgecolor='darkgreen', facecolor='lightgreen',
                        linewidth=3, alpha=0.5)
ax.add_patch(fb_box)
# title text removed for cleaner look
fb_eq = (
    "Control Law:\n"
    "u = -Kx + r\n\n"
    "Closed-loop:\n"
    "dx/dt = (A-BK)x + Br\n\n"
    "K: feedback gain matrix\n"
    "r: reference input"
)
# ax.text(12, 9.8, fb_eq, fontsize=14, ha='center', va='top', family='monospace')

# 系统框图
system_box = FancyBboxPatch((5, 5), 3, 1.5,
                            boxstyle="round,pad=0.1",
                            edgecolor='darkblue', facecolor='lightsteelblue',
                            linewidth=3)
ax.add_patch(system_box)
ax.text(6.5, 5.4, 'y=Cx', fontsize=14, ha='center', va='bottom', family='monospace')

# 状态反馈
fb_ctrl = FancyBboxPatch((10, 5), 2, 1.5,
                         boxstyle="round,pad=0.1",
                         edgecolor='darkgreen', facecolor='lightgreen',
                         linewidth=2)
ax.add_patch(fb_ctrl)
# title text removed for cleaner look
ax.text(11, 5.8, 'Feedback', fontsize=14, weight='bold', ha='center', va='center')
ax.text(11, 5.4, 'u=-Kx+r', fontsize=13, ha='center', va='bottom', family='monospace')

# 输入输出箭头
arrow1 = FancyArrowPatch((3.5, 5.75), (5, 5.75),
                         arrowstyle='->', mutation_scale=30,
                         linewidth=2.5, color='red')
ax.add_patch(arrow1)
ax.text(4.25, 6, 'u', fontsize=15, ha='center', va='bottom', color='red', weight='bold')

arrow2 = FancyArrowPatch((8, 5.75), (9.5, 5.75),
                         arrowstyle='->', mutation_scale=30,
                         linewidth=2.5, color='blue')
ax.add_patch(arrow2)
ax.text(8.75, 6, 'y', fontsize=15, ha='center', va='bottom', color='blue', weight='bold')

# 反馈箭头
ax.plot([6.5, 6.5, 13, 13, 11, 11], [5, 4.5, 4.5, 5.75, 5.75, 5], 'g--', linewidth=2)
arrow_fb = FancyArrowPatch((11, 5.75), (11, 5),
                           arrowstyle='->', mutation_scale=25,
                           linewidth=0, color='green')
ax.add_patch(arrow_fb)
ax.text(13.2, 5, 'x (states)', fontsize=14, ha='left', va='center', color='green')

# 参考输入
ax.text(2, 5.75, 'r', fontsize=16, ha='center', va='center',
        weight='bold', color='purple')
arrow_r = FancyArrowPatch((2.3, 5.75), (3.5, 5.75),
                          arrowstyle='->', mutation_scale=25,
                          linewidth=2, color='purple')
ax.add_patch(arrow_r)

# 能控性能观性
ctrl_obs_box = FancyBboxPatch((1, 3), 6, 1.5,
                              boxstyle="round,pad=0.15",
                              edgecolor='purple', facecolor='lavender',
                              linewidth=2.5, alpha=0.8)
ax.add_patch(ctrl_obs_box)
# title text removed for cleaner look
ctrl_text = (
    "Controllability: rank(Qc)=n\n"
    "Qc = [B AB A²B ... Aⁿ⁻¹B]\n\n"
    "Observability: rank(Qo)=n\n"
    "Qo = [C; CA; CA²; ...; CAⁿ⁻¹]"
)
# ax.text(4, 4, ctrl_text, fontsize=13, ha='center', va='top', family='monospace')

# 极点配置
pole_box = FancyBboxPatch((9, 3), 6, 1.5,
                          boxstyle="round,pad=0.15",
                          edgecolor='darkred', facecolor='mistyrose',
                          linewidth=2.5, alpha=0.8)
ax.add_patch(pole_box)
ax.text(12, 4.3, 'Pole Placement', fontsize=16, weight='bold',
        ha='center', va='top', color='darkred')
pole_text = (
    "Design K such that:\n"
    "eig(A-BK) = desired poles\n\n"
    "Fast response: poles far left\n"
    "Stable: Re(λ) < 0"
)
ax.text(12, 4, pole_text, fontsize=13, ha='center', va='top', family='monospace')

# 优势
adv_text = (
    "Advantages of State-Space Method:\n"
    "• Handle MIMO systems naturally\n"
    "• Time-domain design\n"
    "• Direct pole placement\n"
    "• Optimal control (LQR)\n"
    "• State estimation (Kalman filter)"
)

# 对比表
compare_text = (
    "Classical vs Modern Control:\n"
    "Transfer Function ↔ State-Space\n"
    "SISO ↔ MIMO\n"
    "Frequency Domain ↔ Time Domain\n"
    "PID Tuning ↔ Pole Placement/LQR"
)

plt.tight_layout()
plt.savefig('state_space_diagram.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("✓ 示意图已生成：state_space_diagram.png")
plt.close()



