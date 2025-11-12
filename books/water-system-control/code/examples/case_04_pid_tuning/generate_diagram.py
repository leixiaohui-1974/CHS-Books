#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成案例4 PID控制系统示意图
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle
import numpy as np

# 设置英文字体（避免乱码）
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
ax.set_xlim(0, 12)
ax.set_ylim(0, 10)
ax.axis('off')

# ============================================================================
# 1. 水浴系统主体
# ============================================================================

# 水箱
tank_x, tank_y = 5, 2
tank_width, tank_height = 3, 4

tank = Rectangle((tank_x, tank_y), tank_width, tank_height,
                 facecolor='#E1F5FE', edgecolor='#01579B', linewidth=3)
ax.add_patch(tank)

# 水位
water_level = tank_y + (tank_height * 0.67)
water = Rectangle((tank_x, tank_y), tank_width, water_level - tank_y,
                  facecolor='#4FC3F7', edgecolor='none', alpha=0.7)
ax.add_patch(water)

# 标题
# title text removed for cleaner look
# ax.text(6.5, 9, 'Precision Water Bath', fontsize=18, ha='center', va='top', style='italic', color='#555')

# 水位标注
ax.plot([tank_x + tank_width + 0.2, tank_x + tank_width + 0.6],
        [water_level, water_level], 'k--', linewidth=1.5)
ax.text(tank_x + tank_width + 0.8, water_level, 'h = 3.0m',
        fontsize=16, weight='bold', va='center',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.7))

# ============================================================================
# 2. 传感器
# ============================================================================

sensor_x, sensor_y = tank_x + tank_width/2, water_level
sensor = Circle((sensor_x, sensor_y), 0.25, facecolor='#FFF59D',
                edgecolor='#F57C00', linewidth=2.5)
ax.add_patch(sensor)
ax.text(sensor_x, sensor_y, 'S', fontsize=18, weight='bold',
        ha='center', va='center', color='#E65100')
ax.text(sensor_x, sensor_y - 0.45, 'Sensor', fontsize=15,
        ha='center', va='top', style='italic')

# ============================================================================
# 3. PID控制器（三部分展示）
# ============================================================================

controller_x, controller_y = 1, 5
controller_w, controller_h = 2.5, 3

# 主框
controller_box = FancyBboxPatch((controller_x, controller_y), controller_w, controller_h,
                                 boxstyle="round,pad=0.15", facecolor='#C8E6C9',
                                 edgecolor='#2E7D32', linewidth=3)
ax.add_patch(controller_box)

# 标题
# title text removed for cleaner look

# P项
p_y = controller_y + controller_h - 0.8
ax.text(controller_x + 0.8, p_y, 'Kp · e', fontsize=16, ha='left', va='center',
        style='italic')
# title text removed for cleaner look

# I项
i_y = controller_y + controller_h/2
ax.text(controller_x + 0.8, i_y, 'Ki · ∫e dt', fontsize=16, ha='left', va='center',
        style='italic')

# D项
d_y = controller_y + 0.7
ax.text(controller_x + 0.3, d_y, 'D', fontsize=18, weight='bold',
        ha='left', va='center', color='#6A1B9A',
        bbox=dict(boxstyle='circle,pad=0.2', facecolor='#E1BEE7', edgecolor='#6A1B9A', linewidth=2))
ax.text(controller_x + controller_w - 0.3, d_y, 'Damping', fontsize=14,
        ha='right', va='center', color='#555')

# 总输出

# ============================================================================
# 4. 可调速泵
# ============================================================================

pump_x, pump_y = 3, 1.2
pump_r = 0.5

pump = Circle((pump_x, pump_y), pump_r, facecolor='#A5D6A7',
              edgecolor='#2E7D32', linewidth=2.5)
ax.add_patch(pump)
ax.text(pump_x, pump_y, 'P', fontsize=20, weight='bold',
        ha='center', va='center', color='#1B5E20')
ax.text(pump_x, pump_y - pump_r - 0.35, 'Variable\nSpeed Pump',
        fontsize=15, ha='center', va='top')

# ============================================================================
# 5. 管道系统
# ============================================================================

# 进水管
pipe_in_y = tank_y + 0.3
ax.plot([pump_x + pump_r, tank_x], [pump_y, pipe_in_y],
        'g-', linewidth=4, solid_capstyle='round')
ax.text((pump_x + pump_r + tank_x)/2, (pump_y + pipe_in_y)/2 + 0.25,
        'Inflow', fontsize=16, ha='center', weight='bold', color='darkgreen')
ax.annotate('', xy=(tank_x - 0.1, pipe_in_y), xytext=(tank_x - 0.4, pipe_in_y),
            arrowprops=dict(arrowstyle='->', lw=2, color='darkgreen'))

# 出水管
outflow_x = tank_x + tank_width
outflow_y = tank_y + 0.5
ax.plot([outflow_x, outflow_x + 1.5], [outflow_y, outflow_y],
        'b-', linewidth=4, solid_capstyle='round')
ax.annotate('', xy=(outflow_x + 1.4, outflow_y), xytext=(outflow_x + 1.0, outflow_y),
            arrowprops=dict(arrowstyle='->', lw=2, color='darkblue'))

# ============================================================================
# 6. 信号线
# ============================================================================

# 从传感器到控制器（测量信号）
signal1 = FancyArrowPatch((sensor_x - 0.3, sensor_y + 0.15),
                          (controller_x + controller_w, controller_y + controller_h/2),
                          connectionstyle="arc3,rad=0.3", arrowstyle='->', mutation_scale=15,
                          linewidth=2, color='orange', linestyle='--')
ax.add_patch(signal1)

# 从控制器到泵（控制信号）
signal2 = FancyArrowPatch((controller_x + controller_w/2, controller_y),
                          (pump_x, pump_y + pump_r),
                          connectionstyle="arc3,rad=-0.15", arrowstyle='->', mutation_scale=15,
                          linewidth=2, color='red', linestyle='--')
ax.add_patch(signal2)
# title text removed for cleaner look

# ============================================================================
# 7. 参数说明框
# ============================================================================

# 系统参数
param_box = FancyBboxPatch((9, 6), 2.8, 3.5,
                            boxstyle="round,pad=0.15", facecolor='#FFF9C4',
                            edgecolor='#F57F17', linewidth=2)
ax.add_patch(param_box)

# title text removed for cleaner look

params_text = """
A = 2.0 m²
R = 2.0 min/m²  
K = 1.0 m³/min
τ = 4.0 min

Target: 3.0m
Tolerance: ±0.01m
"""


# PID参数
pid_param_box = FancyBboxPatch((9, 2), 2.8, 3.5,
                                boxstyle="round,pad=0.15", facecolor='#E8F5E9',
                                edgecolor='#388E3C', linewidth=2)
ax.add_patch(pid_param_box)

ax.text(10.4, 5.2, 'PID Parameters', fontsize=17, weight='bold',
        ha='center', va='top', color='#1B5E20')

pid_text = """
Kp = 2.0
(Proportional)

Ki = 0.5
(Integral)

Kd = 0.5
(Derivative)

Tuning: ZN Method
"""

ax.text(10.4, 4.7, pid_text, fontsize=14, ha='center', va='top',
        family='monospace', linespacing=1.2)

# ============================================================================
# 8. 性能指标框
# ============================================================================

perf_box = FancyBboxPatch((9, 0.2), 2.8, 1.5,
                           boxstyle="round,pad=0.1", facecolor='#E3F2FD',
                           edgecolor='#1976D2', linewidth=2)
ax.add_patch(perf_box)

ax.text(10.4, 1.5, 'Performance', fontsize=16, weight='bold',
        ha='center', va='top', color='#0D47A1')

perf_text = """Rise Time: < 5 min
Overshoot: < 5%
Settling: < 15 min
Steady Error: ≈ 0"""

ax.text(10.4, 1.2, perf_text, fontsize=14, ha='center', va='top',
        linespacing=1.2)

# ============================================================================
# 9. 底部说明
# ============================================================================

title_box = FancyBboxPatch((0.5, 0.2), 7.5, 0.7,
                            boxstyle="round,pad=0.1", facecolor='#FFF3E0',
                            edgecolor='#E65100', linewidth=2)
ax.add_patch(title_box)

# title text removed for cleaner look

# 保存
plt.tight_layout()
plt.savefig('pid_system_diagram.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Generated: pid_system_diagram.png")
plt.close()



