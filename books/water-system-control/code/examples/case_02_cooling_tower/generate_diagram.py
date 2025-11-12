#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成案例2冷却塔水位控制系统示意图
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle
import numpy as np

# 设置字体为英文（避免乱码）
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig, ax = plt.subplots(1, 1, figsize=(10, 12))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

# ============================================================================
# 1. 冷却塔主体（圆柱形水箱）
# ============================================================================

# 塔身
tower_x, tower_y = 3.5, 3
tower_width, tower_height = 3, 4.5

# 绘制塔身（浅蓝色）
tower = Rectangle((tower_x, tower_y), tower_width, tower_height,
                   facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=3)
ax.add_patch(tower)

# 水位线（当前水位3.0m）
water_level = tower_y + (tower_height * 0.67)  # 3.0m相对位置
water = Rectangle((tower_x, tower_y), tower_width, water_level - tower_y,
                   facecolor='#64B5F6', edgecolor='none', alpha=0.6)
ax.add_patch(water)

# 顶部（锥形屋顶）
roof_points = np.array([
    [tower_x, tower_y + tower_height],
    [tower_x + tower_width/2, tower_y + tower_height + 0.8],
    [tower_x + tower_width, tower_y + tower_height]
])
roof = patches.Polygon(roof_points, facecolor='#B71C1C', edgecolor='#D32F2F',
                        linewidth=2, alpha=0.8)
ax.add_patch(roof)

# 添加阴影效果
roof_shadow = patches.Polygon(roof_points + [0.05, -0.05], facecolor='#000000',
                               alpha=0.2, zorder=0)
ax.add_patch(roof_shadow)

# ============================================================================
# 2. 标注
# ============================================================================

# 标题
# title text removed for cleaner look
# title text removed for cleaner look

# 水位标注
ax.plot([tower_x + tower_width + 0.2, tower_x + tower_width + 0.8],
        [water_level, water_level], 'k--', linewidth=1.5)
ax.text(tower_x + tower_width + 0.95, water_level, 'h(t) = 3.0m\n(Target)',
        fontsize=13, weight='bold', va='center',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.7))

# 塔高标注
ax.annotate('', xy=(tower_x - 0.3, tower_y), xytext=(tower_x - 0.3, tower_y + tower_height),
            arrowprops=dict(arrowstyle='<->', lw=1.5, color='black'))
ax.text(tower_x - 0.6, tower_y + tower_height/2, 'H = 4.5m',
        fontsize=12, rotation=90, va='center', ha='right')

# ============================================================================
# 3. 传感器
# ============================================================================

# 水位传感器
sensor_x, sensor_y = tower_x + tower_width/2, water_level
sensor = Circle((sensor_x, sensor_y), 0.25, facecolor='#FFF9C4',
                edgecolor='#F57C00', linewidth=2.5)
ax.add_patch(sensor)
ax.text(sensor_x, sensor_y, 'H', fontsize=14, weight='bold',
        ha='center', va='center', color='#E65100')

# 传感器标签
ax.text(sensor_x, sensor_y - 0.5, 'Level\nSensor', fontsize=11,
        ha='center', va='top', style='italic')

# ============================================================================
# 4. 比例控制器
# ============================================================================

controller_x, controller_y = 1.5, 5.5
controller_w, controller_h = 1.5, 1.2

controller = FancyBboxPatch((controller_x, controller_y), controller_w, controller_h,
                             boxstyle="round,pad=0.1", facecolor='#E1F5FE',
                             edgecolor='#0288D1', linewidth=2.5)
ax.add_patch(controller)
# title text removed for cleaner look
ax.text(controller_x + controller_w/2, controller_y + controller_h/2 - 0.2,
        'u = Kp·e', fontsize=11, ha='center', va='center',
        style='italic', color='#01579B')

# ============================================================================
# 5. 可调速泵
# ============================================================================

pump_x, pump_y = 1.5, 1.5
pump_r = 0.5

# 泵主体
pump = Circle((pump_x, pump_y), pump_r, facecolor='#C8E6C9',
              edgecolor='#388E3C', linewidth=2.5)
ax.add_patch(pump)

# 泵标识
ax.text(pump_x, pump_y, 'P', fontsize=16, weight='bold',
        ha='center', va='center', color='#1B5E20')
ax.text(pump_x, pump_y - pump_r - 0.3, 'Variable\nSpeed Pump',
        fontsize=11, ha='center', va='top')

# PWM标识（表示可调速）
ax.text(pump_x, pump_y - pump_r - 0.8, '(0-100%)',
        fontsize=10, ha='center', va='top', style='italic', color='#2E7D32')

# ============================================================================
# 6. 管道系统
# ============================================================================

# 进水管（从泵到塔底）
pipe_in_y = tower_y + 0.3
ax.plot([pump_x + pump_r, tower_x], [pump_y, pipe_in_y],
        'g-', linewidth=4, solid_capstyle='round')
ax.text((pump_x + pump_r + tower_x)/2, (pump_y + pipe_in_y)/2 + 0.3,
        'Inflow', fontsize=12, ha='center', weight='bold', color='darkgreen')

# 进水箭头
ax.annotate('', xy=(tower_x - 0.1, pipe_in_y), xytext=(tower_x - 0.5, pipe_in_y),
            arrowprops=dict(arrowstyle='->', lw=2, color='darkgreen'))

# 出水管（从塔底流出）
outflow_x = tower_x + tower_width
outflow_y = tower_y + 0.5
ax.plot([outflow_x, outflow_x + 1.5], [outflow_y, outflow_y],
        'b-', linewidth=4, solid_capstyle='round')
ax.text(outflow_x + 0.75, outflow_y + 0.3, 'Outflow',
        fontsize=12, ha='center', weight='bold', color='darkblue')

# 出水箭头
ax.annotate('', xy=(outflow_x + 1.4, outflow_y), xytext=(outflow_x + 1.0, outflow_y),
            arrowprops=dict(arrowstyle='->', lw=2, color='darkblue'))

# 出水标注
ax.text(outflow_x + 1.5, outflow_y - 0.4, 'To Process',
        fontsize=10, ha='center', style='italic', color='navy')

# ============================================================================
# 7. 信号线
# ============================================================================

# 从传感器到控制器（测量信号）
signal1 = FancyArrowPatch((sensor_x - 0.3, sensor_y + 0.2),
                          (controller_x + controller_w, controller_y + controller_h/2),
                          connectionstyle="arc3,rad=0.3", arrowstyle='->', mutation_scale=15,
                          linewidth=1.5, color='orange', linestyle='--')
ax.add_patch(signal1)
ax.text(3, 6.3, 'Measurement', fontsize=10, color='darkorange',
        style='italic', rotation=-10)

# 从控制器到泵（控制信号）
signal2 = FancyArrowPatch((controller_x + controller_w/2, controller_y),
                          (pump_x, pump_y + pump_r),
                          connectionstyle="arc3,rad=-0.2", arrowstyle='->', mutation_scale=15,
                          linewidth=1.5, color='red', linestyle='--')
ax.add_patch(signal2)
# title text removed for cleaner look

# ============================================================================
# 8. 系统参数说明
# ============================================================================

# 参数框
param_box = FancyBboxPatch((7.2, 7.5), 2.5, 3.5,
                            boxstyle="round,pad=0.15", facecolor='#FFFDE7',
                            edgecolor='#F57F17', linewidth=2)
ax.add_patch(param_box)

# title text removed for cleaner look

params_text = """
A = 2.0 m²
R = 2.0 min/m²
K = 1.0 m³/min
τ = 4.0 min

Target: 3.0m
Tolerance: ±0.1m
"""

ax.text(8.45, 10.2, params_text, fontsize=10, ha='center', va='top',
        family='monospace', linespacing=1.2)

# 控制逻辑说明
control_box = FancyBboxPatch((7.2, 3.5), 2.5, 3.5,
                              boxstyle="round,pad=0.15", facecolor='#E8F5E9',
                              edgecolor='#388E3C', linewidth=2)
ax.add_patch(control_box)

# title text removed for cleaner look

control_text = """
Error:
e = h_sp - h(t)

Control Law:
u = Kp × e

Output:
0 ≤ u ≤ 100%

Kp = 0.8
(Optimal)
"""

ax.text(8.45, 6.2, control_text, fontsize=10, ha='center', va='top',
        family='monospace', linespacing=1.2)

# ============================================================================
# 9. 标题说明
# ============================================================================

title_box = FancyBboxPatch((0.5, 0.2), 9, 0.8,
                            boxstyle="round,pad=0.1", facecolor='#FFF9C4',
                            edgecolor='#F57C00', linewidth=2)
ax.add_patch(title_box)

# title text removed for cleaner look

# 保存图片
plt.tight_layout()
plt.savefig('cooling_tower_diagram.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Generated: cooling_tower_diagram.png")
plt.close()

