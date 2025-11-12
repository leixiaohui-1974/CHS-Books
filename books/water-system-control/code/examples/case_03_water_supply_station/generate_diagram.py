#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成案例3供水泵站PI控制系统示意图
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle, Polygon
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
# 1. 高位水箱（供水压力源）
# ============================================================================

tank_x, tank_y = 3.5, 6
tank_width, tank_height = 3, 3.5

# 水箱主体
tank = Rectangle((tank_x, tank_y), tank_width, tank_height,
                  facecolor='#E1F5FE', edgecolor='#0277BD', linewidth=3)
ax.add_patch(tank)

# 水位（3.0m目标）
water_level = tank_y + (tank_height * 0.75)
water = Rectangle((tank_x, tank_y), tank_width, water_level - tank_y,
                   facecolor='#4FC3F7', edgecolor='none', alpha=0.6)
ax.add_patch(water)

# 顶部平台
roof_points = np.array([
    [tank_x - 0.2, tank_y + tank_height],
    [tank_x + tank_width + 0.2, tank_y + tank_height],
    [tank_x + tank_width + 0.2, tank_y + tank_height + 0.3],
    [tank_x - 0.2, tank_y + tank_height + 0.3]
])
roof = Polygon(roof_points, facecolor='#546E7A', edgecolor='#37474F', linewidth=2)
ax.add_patch(roof)

# ============================================================================
# 2. 标注
# ============================================================================

# 标题
# title text removed for cleaner look

# 水位标注
ax.plot([tank_x + tank_width + 0.3, tank_x + tank_width + 0.9],
        [water_level, water_level], 'k--', linewidth=1.5)
ax.text(tank_x + tank_width + 1.1, water_level, 'h(t) = 3.0m\n(Target)',
        fontsize=12, weight='bold', va='center',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.7))

# ============================================================================
# 3. 传感器
# ============================================================================

sensor_x, sensor_y = tank_x + tank_width/2, water_level
sensor = Circle((sensor_x, sensor_y), 0.22, facecolor='#FFF59D',
                edgecolor='#F57C00', linewidth=2.5)
ax.add_patch(sensor)
ax.text(sensor_x, sensor_y, 'H', fontsize=15, weight='bold',
        ha='center', va='center', color='#E65100')

# 传感器标签
ax.text(sensor_x, sensor_y - 0.45, 'Level\nSensor', fontsize=10,
        ha='center', va='top', style='italic')

# ============================================================================
# 4. PI控制器（核心）
# ============================================================================

controller_x, controller_y = 1.2, 7.5
controller_w, controller_h = 1.8, 1.5

controller = FancyBboxPatch((controller_x, controller_y), controller_w, controller_h,
                             boxstyle="round,pad=0.12", facecolor='#C5E1A5',
                             edgecolor='#558B2F', linewidth=3)
ax.add_patch(controller)
# title text removed for cleaner look
ax.text(controller_x + controller_w/2, controller_y + controller_h/2 - 0.05,
        'u = Kp·e + Ki·∫e', fontsize=11, ha='center', va='center',
        style='italic', family='monospace', color='#558B2F')
ax.text(controller_x + controller_w/2, controller_y + controller_h/2 - 0.45,
        '(No Error!)', fontsize=10, ha='center', va='center',
        weight='bold', color='#1B5E20')

# ============================================================================
# 5. 变频泵
# ============================================================================

pump_x, pump_y = 1.5, 3.5
pump_r = 0.55

# 泵主体
pump = Circle((pump_x, pump_y), pump_r, facecolor='#B2DFDB',
              edgecolor='#00695C', linewidth=2.5)
ax.add_patch(pump)

# 泵标识
ax.text(pump_x, pump_y, 'P', fontsize=17, weight='bold',
        ha='center', va='center', color='#004D40')
ax.text(pump_x, pump_y - pump_r - 0.35, 'Variable\nFrequency Pump',
        fontsize=11, ha='center', va='top')

# 变频器标识
ax.text(pump_x, pump_y - pump_r - 0.9, '(VFD)', fontsize=10,
        ha='center', va='top', style='italic', color='#00796B')

# ============================================================================
# 6. 管道系统
# ============================================================================

# 进水管（从泵到水箱）
pipe_in_y = tank_y + 0.4
ax.plot([pump_x + pump_r, tank_x], [pump_y + 0.3, pipe_in_y],
        'g-', linewidth=4.5, solid_capstyle='round')
ax.text((pump_x + pump_r + tank_x)/2 - 0.2, (pump_y + pipe_in_y)/2 + 0.4,
        'Inflow', fontsize=12, ha='center', weight='bold', color='darkgreen')

# 进水箭头
ax.annotate('', xy=(tank_x - 0.1, pipe_in_y), xytext=(tank_x - 0.5, pipe_in_y),
            arrowprops=dict(arrowstyle='->', lw=2.5, color='darkgreen'))

# 出水管1（居民用水 - 变化）
out1_x, out1_y = tank_x + tank_width, tank_y + 1.5
ax.plot([out1_x, out1_x + 1.8], [out1_y, out1_y],
        'b-', linewidth=4, solid_capstyle='round')
ax.text(out1_x + 0.9, out1_y + 0.35, 'To Residents',
        fontsize=11, ha='center', weight='bold', color='darkblue')
ax.text(out1_x + 0.9, out1_y - 0.35, '(Variable Demand)',
        fontsize=10, ha='center', style='italic', color='navy')

# 出水箭头1
ax.annotate('', xy=(out1_x + 1.7, out1_y), xytext=(out1_x + 1.3, out1_y),
            arrowprops=dict(arrowstyle='->', lw=2, color='darkblue'))

# 出水管2（工业用水）
out2_x, out2_y = tank_x + tank_width, tank_y + 0.8
ax.plot([out2_x, out2_x + 1.8], [out2_y, out2_y],
        'b-', linewidth=3.5, solid_capstyle='round')
ax.text(out2_x + 0.9, out2_y + 0.35, 'To Industry',
        fontsize=11, ha='center', weight='bold', color='darkblue')

# 出水箭头2
ax.annotate('', xy=(out2_x + 1.7, out2_y), xytext=(out2_x + 1.3, out2_y),
            arrowprops=dict(arrowstyle='->', lw=2, color='darkblue'))

# ============================================================================
# 7. 信号线
# ============================================================================

# 从传感器到控制器
signal1 = FancyArrowPatch((sensor_x - 0.25, sensor_y + 0.2),
                          (controller_x + controller_w, controller_y + controller_h/2 + 0.2),
                          connectionstyle="arc3,rad=0.25", arrowstyle='->', mutation_scale=15,
                          linewidth=1.8, color='orange', linestyle='--')
ax.add_patch(signal1)
ax.text(3.3, 8.3, 'Measurement', fontsize=10, color='darkorange',
        style='italic', rotation=-5)

# 从控制器到泵
signal2 = FancyArrowPatch((controller_x + controller_w/2, controller_y),
                          (pump_x, pump_y + pump_r + 0.1),
                          connectionstyle="arc3,rad=-0.15", arrowstyle='->', mutation_scale=15,
                          linewidth=1.8, color='red', linestyle='--')
ax.add_patch(signal2)
# title text removed for cleaner look

# ============================================================================
# 8. 扰动标识（用水需求变化）
# ============================================================================

# 扰动箭头（指向出水口）
disturbance_arrow = FancyArrowPatch((8.5, 1.2), (7.3, 1.2),
                                    arrowstyle='->', mutation_scale=20,
                                    linewidth=2, color='purple', linestyle=':')
ax.add_patch(disturbance_arrow)
ax.text(8.5, 1.7, 'Disturbance:\nDemand Change', fontsize=11,
        ha='left', va='center', color='purple', weight='bold')

# ============================================================================
# 9. 系统参数框
# ============================================================================

param_box = FancyBboxPatch((7, 7.5), 2.7, 3.7,
                            boxstyle="round,pad=0.15", facecolor='#FFF9C4',
                            edgecolor='#F57F17', linewidth=2)
ax.add_patch(param_box)

# title text removed for cleaner look

params_text = """
A = 2.0 m²
R = 3.0 min/m²
K = 1.2 m³/min
τ = 6.0 min

Target: 3.0m
Error: 0m (Zero!)
Accuracy: ±0.01m
"""

ax.text(8.35, 10.5, params_text, fontsize=10, ha='center', va='top',
        family='monospace', linespacing=1.2)

# ============================================================================
# 10. PI控制逻辑框
# ============================================================================

control_box = FancyBboxPatch((7, 3.3), 2.7, 3.7,
                              boxstyle="round,pad=0.15", facecolor='#E8F5E9',
                              edgecolor='#388E3C', linewidth=2)
ax.add_patch(control_box)

# title text removed for cleaner look

control_text = """
Error:
e(t) = h_sp - h(t)

P Action:
u_p = Kp × e(t)

I Action:
u_i = Ki × ∫e(t)dt

Total:
u = u_p + u_i

Kp = 1.5, Ki = 0.3
"""

ax.text(8.35, 6.3, control_text, fontsize=10, ha='center', va='top',
        family='monospace', linespacing=1.2)

# ============================================================================
# 11. 底部标题框
# ============================================================================

title_box = FancyBboxPatch((0.3, 0.15), 9.4, 0.85,
                            boxstyle="round,pad=0.1", facecolor='#BBDEFB',
                            edgecolor='#1976D2', linewidth=2)
ax.add_patch(title_box)

# title text removed for cleaner look
# title text removed for cleaner look

# 保存图片
plt.tight_layout()
plt.savefig('water_supply_station_diagram.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Generated: water_supply_station_diagram.png")
plt.close()
