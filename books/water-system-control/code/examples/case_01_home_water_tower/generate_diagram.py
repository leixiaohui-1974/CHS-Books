#!/usr/bin/env python3
"""
生成水塔示意图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# 设置matplotlib不显示图形（后台模式）
import matplotlib
matplotlib.use('Agg')

# 创建图形 - 缩小尺寸，使用更合适的比例
fig, ax = plt.subplots(1, 1, figsize=(8, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 15)
ax.axis('off')

# 使用更现代、更美观的配色方案
water_color = '#3498DB'  # 明亮的蓝色
tank_color = '#2C3E50'   # 深灰蓝色
pump_color = '#E74C3C'   # 鲜艳的红色
pipe_color = '#7F8C8D'   # 中性灰色
text_color = '#2C3E50'   # 深色文字
highlight_color = '#F39C12'  # 橙色高亮
bg_color = '#ECF0F1'     # 浅灰背景色

# 1. 绘制屋顶 - 添加阴影效果
roof_points = [[2, 12], [5, 14], [8, 12], [2, 12]]
# 阴影
roof_shadow = patches.Polygon([[p[0]+0.1, p[1]-0.1] for p in roof_points], 
                              closed=True, facecolor='black', alpha=0.2, zorder=1)
ax.add_patch(roof_shadow)
# 主体
roof = patches.Polygon(roof_points, closed=True, facecolor='#95A5A6', 
                      edgecolor='#2C3E50', linewidth=2.5, zorder=2)
ax.add_patch(roof)

# 2. 绘制水塔（圆柱形）- 添加渐变效果和阴影
tank_x, tank_y = 3.5, 10
tank_width, tank_height = 3, 2
# 阴影
tank_shadow = patches.Rectangle((tank_x+0.15, tank_y-0.15), tank_width, tank_height, 
                                facecolor='black', alpha=0.15, zorder=1)
ax.add_patch(tank_shadow)
# 主体
tank = patches.Rectangle((tank_x, tank_y), tank_width, tank_height, 
                         facecolor='white', edgecolor=tank_color, linewidth=3, zorder=2)
ax.add_patch(tank)

# 水塔支架
support_left = patches.Rectangle((3.8, 9), 0.2, 1, facecolor=tank_color)
support_right = patches.Rectangle((6, 9), 0.2, 1, facecolor=tank_color)
ax.add_patch(support_left)
ax.add_patch(support_right)

# 3. 绘制水位
water_level = 10.6  # 当前水位高度
water_rect = patches.Rectangle((tank_x, tank_y), tank_width, water_level - tank_y, 
                               facecolor=water_color, alpha=0.6, edgecolor='none')
ax.add_patch(water_rect)

# 水位线
ax.plot([tank_x, tank_x + tank_width], [water_level, water_level], 
        'b--', linewidth=2, label='Current Water Level')

# 水位标注
ax.annotate('h = 3.0m', xy=(tank_x + tank_width + 0.2, water_level), 
           fontsize=14, fontweight='bold', color=text_color)

# 上限线
high_threshold = 11.5
ax.plot([tank_x, tank_x + tank_width], [high_threshold, high_threshold], 
        'r--', linewidth=2, alpha=0.7)
ax.annotate('High: 3.5m', xy=(tank_x + tank_width + 0.2, high_threshold), 
           fontsize=12, color='red')

# 下限线
low_threshold = 10.5
ax.plot([tank_x, tank_x + tank_width], [low_threshold, low_threshold], 
        'r--', linewidth=2, alpha=0.7)
ax.annotate('Low: 2.5m', xy=(tank_x + tank_width + 0.2, low_threshold), 
           fontsize=12, color='red')

# 4. 绘制水龙头（出水口）
tap_x, tap_y = 6.8, 10.2
tap_pipe = patches.Rectangle((tap_x, tap_y), 0.8, 0.15, 
                             facecolor=pipe_color, edgecolor='black', linewidth=1)
ax.add_patch(tap_pipe)

# 出水箭头
ax.arrow(tap_x + 0.8, tap_y + 0.075, 0.5, 0, 
        head_width=0.2, head_length=0.15, fc=water_color, ec=water_color, linewidth=2)
ax.text(tap_x + 1.5, tap_y, 'Q_out', fontsize=13, fontweight='bold', color=text_color)

# 5. 绘制水泵（地面）
pump_x, pump_y = 4, 2
pump_width, pump_height = 2, 1
pump = patches.Rectangle((pump_x, pump_y), pump_width, pump_height, 
                         facecolor=pump_color, edgecolor='black', linewidth=2)
ax.add_patch(pump)
ax.text(pump_x + 1, pump_y + 0.5, 'Pump', fontsize=14, fontweight='bold', 
       color='white', ha='center', va='center')

# 泵状态指示
# title text removed for cleaner look

# 6. 绘制进水管道
pipe1_x = pump_x + pump_width / 2
pipe1 = patches.Rectangle((pipe1_x - 0.1, pump_y + pump_height), 0.2, 7.5, 
                         facecolor=pipe_color, edgecolor='black', linewidth=1)
ax.add_patch(pipe1)

# 进水箭头
arrow_y = pump_y + pump_height + 3
ax.arrow(pipe1_x, arrow_y, 0, 2, 
        head_width=0.3, head_length=0.3, fc=water_color, ec=water_color, linewidth=2)
ax.text(pipe1_x - 0.8, arrow_y + 1, 'Q_in', fontsize=13, fontweight='bold', color=text_color)

# 7. 绘制地面水源
source_x, source_y = 1, 0.5
source = patches.Rectangle((source_x, source_y), 8, 0.5, 
                          facecolor=water_color, alpha=0.4, edgecolor='black', linewidth=2)
ax.add_patch(source)
ax.text(5, 0.25, 'Water Source', fontsize=13, fontweight='bold', 
       color=text_color, ha='center', va='center')

# 8. 绘制水源到水泵的管道
source_pipe = patches.Rectangle((1.5, 1), 0.2, 1, 
                               facecolor=pipe_color, edgecolor='black', linewidth=1)
ax.add_patch(source_pipe)

# 横向连接管
h_pipe = patches.Rectangle((1.5, pump_y + 0.4), pump_x - 1.5, 0.2, 
                          facecolor=pipe_color, edgecolor='black', linewidth=1)
ax.add_patch(h_pipe)

# 9. 添加传感器
sensor_x = tank_x - 0.5
sensor_y = water_level
sensor_circle = plt.Circle((sensor_x, sensor_y), 0.15, 
                          facecolor='orange', edgecolor='black', linewidth=2)
ax.add_patch(sensor_circle)
ax.text(sensor_x - 0.8, sensor_y, 'Level\nSensor', fontsize=11, 
       fontweight='bold', color='orange', ha='center')

# 传感器到控制器的连线
ax.plot([sensor_x, sensor_x - 0.5, sensor_x - 0.5, pump_x + 0.5], 
       [sensor_y, sensor_y, pump_y + 1.5, pump_y + 1.5], 
       'orange', linewidth=2, linestyle='--')

# 控制器
controller = patches.Rectangle((pump_x + 0.3, pump_y + 1.2), 1.4, 0.6, 
                              facecolor='#F39C12', edgecolor='black', linewidth=2)
ax.add_patch(controller)
# title text removed for cleaner look

# 控制器到泵的连线
ax.plot([pump_x + 1, pump_x + 1], [pump_y + 1.2, pump_y + pump_height], 
       'orange', linewidth=2, linestyle='--')

# 10. 添加标题和注释
# title text removed for cleaner look

# 添加系统参数文本框
param_text = (
    'System Parameters:\n'
    '• Tank Area: A = 2.0 m²\n'
    '• Resistance: R = 5.0 min/m²\n'
    '• Pump Gain: K = 1.2 m³/min\n'
    '• Time Constant: τ = 10.0 min'
)
ax.text(0.5, 6, param_text, fontsize=11, 
       bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
       verticalalignment='top', family='monospace')

# 添加控制逻辑文本框
control_text = (
    'Control Logic:\n'
    '• h < 2.5m → Pump ON\n'
    '• h > 3.5m → Pump OFF\n'
    '• 2.5m < h < 3.5m → Keep State\n'
    '  (Hysteresis / Dead Band)'
)
ax.text(0.5, 4, control_text, fontsize=11, 
       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
       verticalalignment='top', family='monospace')

# 保存图形
plt.tight_layout()
plt.savefig('water_tower_diagram.png', dpi=300, bbox_inches='tight', facecolor='white')
print("Generated: water_tower_diagram.png")
plt.close()

print("Water tower diagram generated successfully!")

