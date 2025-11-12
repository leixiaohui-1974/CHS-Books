#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成案例5 系统参数辨识示意图
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle, Polygon
import numpy as np

# 设置英文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis('off')

# 标题
# title text removed for cleaner look
# title text removed for cleaner look

# ============================================================================
# 左侧：未知系统
# ============================================================================

# 未知水箱（加问号）
tank_x, tank_y = 2, 2.5
tank_width, tank_height = 2.5, 3.5

tank = Rectangle((tank_x, tank_y), tank_width, tank_height,
                 facecolor='#FFEBEE', edgecolor='#C62828', linewidth=3, linestyle='--')
ax.add_patch(tank)

# 大问号

# title text removed for cleaner look

# 未知参数标注
unknown_params = """
A = ?
R = ?  
K = ?
"""
ax.text(tank_x + tank_width/2, tank_y - 0.7, unknown_params,
        fontsize=14, ha='center', va='top', family='monospace',
        color='#C62828', bbox=dict(boxstyle='round,pad=0.2',
        facecolor='#FFCDD2', edgecolor='#C62828', linewidth=2))

# 传感器
sensor = Circle((tank_x + tank_width/2, tank_y + tank_height*0.7), 0.2,
                facecolor='#FFF59D', edgecolor='#F57C00', linewidth=2)
ax.add_patch(sensor)

# 泵
pump = Circle((tank_x - 0.8, tank_y + 0.5), 0.35, facecolor='#C8E6C9',
              edgecolor='#2E7D32', linewidth=2)
ax.add_patch(pump)
ax.text(pump.center[0], pump.center[1], 'P', fontsize=16, weight='bold',
        ha='center', va='center')

# ============================================================================
# 中间：辨识过程
# ============================================================================

# 辨识算法框
id_x, id_y = 5.5, 3
id_w, id_h = 3, 4

id_box = FancyBboxPatch((id_x, id_y), id_w, id_h,
                         boxstyle="round,pad=0.2", facecolor='#E3F2FD',
                         edgecolor='#1976D2', linewidth=3)
ax.add_patch(id_box)

# title text removed for cleaner look
ax.text(id_x + id_w/2, id_y + id_h - 0.8, 'Algorithm',
        fontsize=16, weight='bold', ha='center', va='top', color='#0D47A1')

# 步骤
steps_y = id_y + id_h - 1.6
step_height = 0.6

steps = [
    "1. Collect Data",
    "2. Build Model",
    "3. Optimize Params",
    "4. Validate"
]

colors = ['#BBDEFB', '#90CAF9', '#64B5F6', '#42A5F5']

for i, (step, color) in enumerate(zip(steps, colors)):
    step_box = FancyBboxPatch((id_x + 0.3, steps_y - i*step_height - 0.1),
                               id_w - 0.6, step_height - 0.15,
                               boxstyle="round,pad=0.1", facecolor=color,
                               edgecolor='#1976D2', linewidth=1.5)
    ax.add_patch(step_box)
    ax.text(id_x + id_w/2, steps_y - i*step_height + step_height/2 - 0.2,
            step, fontsize=14, ha='center', va='center', weight='bold')

# 数学公式
ax.text(id_x + id_w/2, id_y + 0.6,
        'min J = Σ(y - ŷ)²', fontsize=15, ha='center', va='center',
        style='italic', family='monospace',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFF9C4',
        edgecolor='#F57C00', linewidth=2))

# ============================================================================
# 右侧：已辨识系统
# ============================================================================

# 已知水箱（加勾号）
tank2_x, tank2_y = 10.5, 2.5
tank2 = Rectangle((tank2_x, tank2_y), tank_width, tank_height,
                  facecolor='#E8F5E9', edgecolor='#2E7D32', linewidth=3)
ax.add_patch(tank2)

# 大勾号
check_x, check_y = tank2_x + tank_width/2, tank2_y + tank_height/2
check_points = np.array([
    [check_x - 0.6, check_y - 0.2],
    [check_x - 0.2, check_y - 0.6],
    [check_x + 0.8, check_y + 0.8]
])
ax.plot(check_points[:, 0], check_points[:, 1], 'g-',
        linewidth=12, solid_capstyle='round', alpha=0.3)

# title text removed for cleaner look

# 已知参数标注
known_params = """
A = 2.00
R = 2.05  
K = 0.98
"""

# 传感器
sensor2 = Circle((tank2_x + tank_width/2, tank2_y + tank_height*0.7), 0.2,
                 facecolor='#FFF59D', edgecolor='#F57C00', linewidth=2)
ax.add_patch(sensor2)

# 泵
pump2 = Circle((tank2_x - 0.8, tank2_y + 0.5), 0.35, facecolor='#C8E6C9',
               edgecolor='#2E7D32', linewidth=2)
ax.add_patch(pump2)
ax.text(pump2.center[0], pump2.center[1], 'P', fontsize=16, weight='bold',
        ha='center', va='center')

# ============================================================================
# 箭头连接
# ============================================================================

# 从未知到辨识
arrow1 = FancyArrowPatch((tank_x + tank_width, tank_y + tank_height/2),
                         (id_x, id_y + id_h/2),
                         connectionstyle="arc3,rad=0", arrowstyle='->',
                         mutation_scale=25, linewidth=3, color='#1976D2')
ax.add_patch(arrow1)
ax.text((tank_x + tank_width + id_x)/2, tank_y + tank_height/2 + 0.3,
        'Input: u(t), y(t)', fontsize=13, ha='center', color='#1976D2',
        style='italic')

# 从辨识到已知
arrow2 = FancyArrowPatch((id_x + id_w, id_y + id_h/2),
                         (tank2_x, tank2_y + tank_height/2),
                         connectionstyle="arc3,rad=0", arrowstyle='->',
                         mutation_scale=25, linewidth=3, color='#2E7D32')
ax.add_patch(arrow2)
ax.text((id_x + id_w + tank2_x)/2, tank2_y + tank_height/2 + 0.3,
        'Output: A, R, K', fontsize=13, ha='center', color='#2E7D32',
        style='italic', weight='bold')

# ============================================================================
# 底部：辨识方法说明
# ============================================================================

# 方法对比框
method_box = FancyBboxPatch((0.5, 0.2), 13, 1.5,
                             boxstyle="round,pad=0.15", facecolor='#FFF9C4',
                             edgecolor='#F57C00', linewidth=2)
ax.add_patch(method_box)

methods_text = """
Identification Methods:  ① Least Squares (最小二乘)  ② Maximum Likelihood (最大似然)  
③ Recursive Estimation (递推估计)  ④ Kalman Filter (卡尔曼滤波)  ⑤ Neural Network (神经网络)
"""
# title text removed for cleaner look
ax.text(7, 1.0, methods_text, fontsize=12, ha='center', va='top',
        linespacing=1.2)

# ============================================================================
# 顶部：数据图示
# ============================================================================

# 输入输出数据示意
data_ax_pos = [0.5, 7, 4, 1.8]
data_box = FancyBboxPatch((data_ax_pos[0], data_ax_pos[1]),
                           data_ax_pos[2], data_ax_pos[3],
                           boxstyle="round,pad=0.1", facecolor='white',
                           edgecolor='#666', linewidth=2)
ax.add_patch(data_box)

# 模拟输入信号
t_data = np.linspace(0, 10, 50)
u_data = 0.5 + 0.3*np.sin(t_data*0.8) + 0.1*np.random.randn(50)
u_scaled = 0.5 + data_ax_pos[1] + 0.6*(u_data - u_data.min())/(u_data.max() - u_data.min())
ax.plot(data_ax_pos[0] + 0.2 + t_data*0.35, u_scaled, 'b-', linewidth=2, label='Input u(t)')
ax.text(data_ax_pos[0] + 0.3, data_ax_pos[1] + data_ax_pos[3] - 0.3,
        'Input u(t)', fontsize=13, color='blue', weight='bold')

# 模拟输出信号
y_data = 0.6 + 0.25*np.sin(t_data*0.8 - 0.5) + 0.08*np.random.randn(50)
y_scaled = data_ax_pos[1] + 0.4 + 0.6*(y_data - y_data.min())/(y_data.max() - y_data.min())
ax.plot(data_ax_pos[0] + 0.2 + t_data*0.35, y_scaled, 'r-', linewidth=2, label='Output y(t)')
ax.text(data_ax_pos[0] + 0.3, data_ax_pos[1] + 0.6,
        'Output y(t)', fontsize=13, color='red', weight='bold')

ax.text(data_ax_pos[0] + data_ax_pos[2]/2, data_ax_pos[1] + data_ax_pos[3] + 0.2,
        'Experimental Data Collection', fontsize=15, ha='center', weight='bold')

# ============================================================================
# 右上：应用价值
# ============================================================================

value_box = FancyBboxPatch((9.5, 7), 4, 1.8,
                            boxstyle="round,pad=0.15", facecolor='#E8F5E9',
                            edgecolor='#388E3C', linewidth=2)
ax.add_patch(value_box)

# title text removed for cleaner look

value_text = """
✓ Design Control System
✓ Predict System Behavior
✓ Optimize Performance
✓ Fault Diagnosis
"""
ax.text(11.5, 8.2, value_text, fontsize=13, ha='center', va='top',
        linespacing=1.2)

# 保存
plt.tight_layout()
plt.savefig('parameter_identification_diagram.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Generated: parameter_identification_diagram.png")
plt.close()



