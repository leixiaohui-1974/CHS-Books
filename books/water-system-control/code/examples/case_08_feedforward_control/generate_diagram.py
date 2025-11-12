#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成案例8 前馈控制示意图
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle
import numpy as np

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1, 1, figsize=(14, 9))
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis('off')

# 标题
# title text removed for cleaner look
# ax.text(7, 8, 'Disturbance Compensation', fontsize=16, ha='center', style='italic', color='#555')

# 水箱
tank_x, tank_y = 6, 2
tank_width, tank_height = 3, 3.5
tank = Rectangle((tank_x, tank_y), tank_width, tank_height,
                 facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=3)
ax.add_patch(tank)

water_level = tank_y + tank_height * 0.6
water = Rectangle((tank_x, tank_y), tank_width, water_level - tank_y,
                  facecolor='#64B5F6', alpha=0.6)
ax.add_patch(water)

ax.text(tank_x + tank_width/2, tank_y - 0.3, 'Water Tank', fontsize=16, weight='bold', ha='center')

# 前馈控制器
ff_x, ff_y = 1, 5.5
ff_w, ff_h = 2, 1.5
ff_box = FancyBboxPatch((ff_x, ff_y), ff_w, ff_h,
                        boxstyle="round,pad=0.15", facecolor='#FFF9C4',
                        edgecolor='#F57C00', linewidth=3)
ax.add_patch(ff_box)
# title text removed for cleaner look
# title text removed for cleaner look

# 反馈控制器
fb_x, fb_y = 1, 3
fb_w, fb_h = 2, 1.5
fb_box = FancyBboxPatch((fb_x, fb_y), fb_w, fb_h,
                        boxstyle="round,pad=0.15", facecolor='#E8F5E9',
                        edgecolor='#2E7D32', linewidth=3)
ax.add_patch(fb_box)
# ax.text(fb_x + fb_w/2, fb_y + fb_h/2 + 0.2, 'Feedback', fontsize=15, weight='bold', ha='center')
ax.text(fb_x + fb_w/2, fb_y + fb_h/2 - 0.2, 'PID', fontsize=15, weight='bold', ha='center')

# 扰动源
dist_x, dist_y = 10, 6.5
dist = Circle((dist_x, dist_y), 0.4, facecolor='#FFCDD2', edgecolor='#C62828', linewidth=3)
ax.add_patch(dist)
ax.text(dist_x, dist_y, 'D', fontsize=18, weight='bold', ha='center', va='center', color='#C62828')
ax.text(dist_x, dist_y - 0.8, 'Disturbance\n(Outflow)', fontsize=13, ha='center')

# 传感器
sensor_x, sensor_y = tank_x + tank_width/2, water_level
sensor = Circle((sensor_x, sensor_y), 0.25, facecolor='#FFF59D', edgecolor='#F57C00', linewidth=2)
ax.add_patch(sensor)
ax.text(sensor_x, sensor_y, 'S', fontsize=16, weight='bold', ha='center', va='center')

# 泵
pump_x, pump_y = 4.5, 1.5
pump = Circle((pump_x, pump_y), 0.4, facecolor='#C8E6C9', edgecolor='#2E7D32', linewidth=2)
ax.add_patch(pump)
ax.text(pump_x, pump_y, 'P', fontsize=16, weight='bold', ha='center', va='center')

# 加法器
sum_x, sum_y = 4.5, 4.5
sum_circle = Circle((sum_x, sum_y), 0.35, facecolor='white', edgecolor='black', linewidth=2)
ax.add_patch(sum_circle)
ax.text(sum_x, sum_y + 0.08, '+', fontsize=20, weight='bold', ha='center', va='center')
ax.plot([sum_x - 0.25, sum_x + 0.25], [sum_y, sum_y], 'k-', linewidth=2)
ax.plot([sum_x, sum_x], [sum_y - 0.25, sum_y + 0.25], 'k-', linewidth=2)

# 信号流
# 前馈路径
arrow1 = FancyArrowPatch((dist_x - 0.5, dist_y), (ff_x + ff_w, ff_y + ff_h/2),
                         connectionstyle="arc3,rad=0.2", arrowstyle='->', mutation_scale=20,
                         linewidth=2.5, color='#F57C00')
ax.add_patch(arrow1)
ax.text(6, 6.5, 'Measure', fontsize=13, color='#F57C00', weight='bold')

arrow2 = FancyArrowPatch((ff_x + ff_w, ff_y + ff_h/2), (sum_x - 0.35, sum_y + 0.2),
                         connectionstyle="arc3,rad=-0.15", arrowstyle='->', mutation_scale=20,
                         linewidth=2.5, color='#F57C00')
ax.add_patch(arrow2)
ax.text(3.5, 5.3, 'FF', fontsize=13, color='#F57C00', weight='bold')

# 反馈路径
arrow3 = FancyArrowPatch((sensor_x, sensor_y - 0.3), (fb_x + fb_w, fb_y + fb_h/2),
                         connectionstyle="arc3,rad=-0.3", arrowstyle='->', mutation_scale=20,
                         linewidth=2.5, color='#2E7D32')
ax.add_patch(arrow3)
ax.text(5, 3, 'Feedback', fontsize=13, color='#2E7D32', weight='bold')

arrow4 = FancyArrowPatch((fb_x + fb_w, fb_y + fb_h/2), (sum_x - 0.35, sum_y - 0.2),
                         connectionstyle="arc3,rad=0.15", arrowstyle='->', mutation_scale=20,
                         linewidth=2.5, color='#2E7D32')
ax.add_patch(arrow4)
ax.text(3.5, 3.8, 'FB', fontsize=13, color='#2E7D32', weight='bold')

# 控制到泵
arrow5 = FancyArrowPatch((sum_x, sum_y - 0.35), (pump_x, pump_y + 0.45),
                         connectionstyle="arc3,rad=0", arrowstyle='->', mutation_scale=20,
                         linewidth=2.5, color='blue')
ax.add_patch(arrow5)
# ax.text(4.5, 3.2, 'u', fontsize=14, color='blue', weight='bold')

# 扰动到水箱
arrow6 = FancyArrowPatch((dist_x, dist_y - 0.5), (tank_x + tank_width, tank_y + tank_height*0.8),
                         connectionstyle="arc3,rad=0.2", arrowstyle='->', mutation_scale=20,
                         linewidth=2.5, color='#C62828', linestyle='--')
ax.add_patch(arrow6)

# 对比框
comp_box = FancyBboxPatch((10.5, 0.5), 3, 4.5,
                          boxstyle="round,pad=0.15", facecolor='#E8EAF6',
                          edgecolor='#3F51B5', linewidth=2)
ax.add_patch(comp_box)

# title text removed for cleaner look

comp_text = """
Feedback Only:
• Slow response
• Large overshoot
• Poor disturbance
  rejection

Feedforward + FB:
• Fast response
• Small overshoot
• Excellent
  disturbance
  rejection
"""
ax.text(12, 4, comp_text, fontsize=12, ha='center', va='top', linespacing=1.2)

# 底部说明
adv_box = FancyBboxPatch((0.5, 0.2), 9.5, 1,
                         boxstyle="round,pad=0.1", facecolor='#FFF9C4',
                         edgecolor='#F57C00', linewidth=2)
ax.add_patch(adv_box)

# title text removed for cleaner look
ax.text(5.25, 0.5, 'FF measures disturbance and compensates IMMEDIATELY | FB waits for error to appear',
        fontsize=12, ha='center')

plt.tight_layout()
plt.savefig('feedforward_control_diagram.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Generated: feedforward_control_diagram.png")
plt.close()



