#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成案例6 阶跃响应法系统建模示意图
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle
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
# 左侧：实验装置
# ============================================================================

# 水箱
tank_x, tank_y = 1.5, 2.5
tank_width, tank_height = 2.5, 3.5

tank = Rectangle((tank_x, tank_y), tank_width, tank_height,
                 facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=3)
ax.add_patch(tank)

# 水位
water_level = tank_y + tank_height * 0.6
water = Rectangle((tank_x, tank_y), tank_width, water_level - tank_y,
                  facecolor='#64B5F6', edgecolor='none', alpha=0.6)
ax.add_patch(water)

# title text removed for cleaner look

# 传感器
sensor = Circle((tank_x + tank_width/2, water_level), 0.2,
                facecolor='#FFF59D', edgecolor='#F57C00', linewidth=2)
ax.add_patch(sensor)

# 泵
pump = Circle((tank_x - 0.6, tank_y + 0.5), 0.35,
              facecolor='#C8E6C9', edgecolor='#2E7D32', linewidth=2)
ax.add_patch(pump)
ax.text(pump.center[0], pump.center[1], 'P', fontsize=16, weight='bold',
        ha='center', va='center')

# 阶跃输入标识
step_box = FancyBboxPatch((tank_x - 0.8, tank_y - 0.8), 1.8, 0.6,
                          boxstyle="round,pad=0.1", facecolor='#FFEB3B',
                          edgecolor='#F57C00', linewidth=2)
ax.add_patch(step_box)
ax.text(tank_x + 0.2, tank_y - 0.5, 'Step Input', fontsize=14,
        ha='center', va='center', weight='bold')

# ============================================================================
# 中上：阶跃响应曲线
# ============================================================================

# 响应曲线框
curve_x, curve_y = 5, 5.5
curve_w, curve_h = 4, 3.5

curve_box = Rectangle((curve_x, curve_y), curve_w, curve_h,
                       facecolor='white', edgecolor='#666', linewidth=2)
ax.add_patch(curve_box)

# title text removed for cleaner look

# 绘制典型阶跃响应曲线
t = np.linspace(0, 10, 100)
tau = 2.5  # 时间常数
K = 1.0    # 增益
h = K * (1 - np.exp(-t/tau))

t_scaled = curve_x + 0.3 + t * (curve_w - 0.6) / 10
h_scaled = curve_y + 0.3 + h * (curve_h - 0.6)

ax.plot(t_scaled, h_scaled, 'b-', linewidth=2.5)

# 标注关键点
# 稳态值
ax.plot([curve_x + 0.3, curve_x + curve_w - 0.3],
        [curve_y + 0.3 + K*(curve_h - 0.6), curve_y + 0.3 + K*(curve_h - 0.6)],
        'r--', linewidth=1.5, alpha=0.7)
ax.text(curve_x + curve_w - 0.5, curve_y + 0.3 + K*(curve_h - 0.6) + 0.15,
        'K', fontsize=14, color='red', weight='bold')

# 63.2%点（时间常数）
h_63 = K * 0.632
t_63_idx = np.argmin(np.abs(h - h_63))
t_63 = t[t_63_idx]
t_63_scaled = curve_x + 0.3 + t_63 * (curve_w - 0.6) / 10
h_63_scaled = curve_y + 0.3 + h_63 * (curve_h - 0.6)

ax.plot([t_63_scaled, t_63_scaled], [curve_y + 0.3, h_63_scaled],
        'g--', linewidth=1.5, alpha=0.7)
ax.plot([curve_x + 0.3, t_63_scaled], [h_63_scaled, h_63_scaled],
        'g--', linewidth=1.5, alpha=0.7)
ax.plot(t_63_scaled, h_63_scaled, 'go', markersize=8)
ax.text(t_63_scaled, curve_y + 0.15, 'τ', fontsize=15, ha='center',
        color='green', weight='bold')

# 坐标轴标签
ax.text(curve_x + 0.15, curve_y + 0.15, '0', fontsize=13, ha='center')
ax.text(curve_x + curve_w/2, curve_y + 0.05, 'Time', fontsize=13, ha='center')
ax.text(curve_x + 0.05, curve_y + curve_h/2, 'h(t)', fontsize=13,
        ha='center', rotation=90)

# ============================================================================
# 中下：参数提取
# ============================================================================

param_x, param_y = 5, 1.5
param_w, param_h = 4, 3.5

param_box = FancyBboxPatch((param_x, param_y), param_w, param_h,
                            boxstyle="round,pad=0.2", facecolor='#E8F5E9',
                            edgecolor='#2E7D32', linewidth=2)
ax.add_patch(param_box)

ax.text(param_x + param_w/2, param_y + param_h - 0.3,
        'Parameter Extraction', fontsize=15, weight='bold',
        ha='center', va='top', color='#1B5E20')

# 参数提取步骤
steps_text = """
Step 1: Measure Steady-State
   K = h∞ / u₀

Step 2: Find 63.2% Point
   τ = time at h = 0.632×K

Step 3: Calculate Parameters
   A = τ / R  (if R known)
   R = τ / A  (if A known)

Result: Transfer Function
   G(s) = K / (τs + 1)
"""

ax.text(param_x + param_w/2, param_y + param_h - 0.7,
        steps_text, fontsize=12, ha='center', va='top',
        family='monospace', linespacing=1.2)

# ============================================================================
# 右侧：模型验证
# ============================================================================

valid_x, valid_y = 10, 2
valid_w, valid_h = 3.5, 6.5

valid_box = FancyBboxPatch((valid_x, valid_y), valid_w, valid_h,
                            boxstyle="round,pad=0.2", facecolor='#FFF9C4',
                            edgecolor='#F57C00', linewidth=2)
ax.add_patch(valid_box)

ax.text(valid_x + valid_w/2, valid_y + valid_h - 0.3,
        'Model Validation', fontsize=15, weight='bold',
        ha='center', va='top', color='#E65100')

# 验证流程
validation_steps = [
    ("① Data Split", "#FFE082"),
    ("Training Set", "#FFECB3"),
    ("Test Set", "#FFECB3"),
    ("", ""),
    ("② Fit Model", "#FFE082"),
    ("Optimize τ, K", "#FFECB3"),
    ("", ""),
    ("③ Evaluate", "#FFE082"),
    ("R² Score", "#FFECB3"),
    ("RMSE", "#FFECB3"),
]

y_offset = valid_y + valid_h - 0.8
for i, (step, color) in enumerate(validation_steps):
    if step:
        if color == "#FFE082":
            box_w = valid_w - 0.6
            box_h = 0.35
        else:
            box_w = valid_w - 1.2
            box_h = 0.3
        
        step_box = FancyBboxPatch((valid_x + (valid_w - box_w)/2, y_offset - 0.05),
                                   box_w, box_h,
                                   boxstyle="round,pad=0.05",
                                   facecolor=color, edgecolor='#F57C00', linewidth=1)
        ax.add_patch(step_box)
        ax.text(valid_x + valid_w/2, y_offset + box_h/2 - 0.05,
                step, fontsize=12, ha='center', va='center',
                weight='bold' if color == "#FFE082" else 'normal')
        y_offset -= (box_h + 0.1)

# ============================================================================
# 底部：方法优势
# ============================================================================

adv_box = FancyBboxPatch((0.5, 0.2), 8.5, 1.3,
                          boxstyle="round,pad=0.15", facecolor='#E3F2FD',
                          edgecolor='#1976D2', linewidth=2)
ax.add_patch(adv_box)

ax.text(4.75, 1.3, 'Method Advantages', fontsize=15, weight='bold',
        ha='center', va='top', color='#0D47A1')

advantages = """
✓ Fast: Single step test, < 5 min  |  ✓ Simple: Easy to implement in field  |  ✓ Accurate: Suitable for 1st order systems
✓ Non-invasive: Normal operation  |  ✓ Robust: Insensitive to noise  |  ✓ Practical: Widely used in industry
"""

ax.text(4.75, 0.9, advantages, fontsize=12.5, ha='center', va='top',
        linespacing=1.2)

# ============================================================================
# 箭头连接
# ============================================================================

# 从系统到响应曲线
arrow1 = FancyArrowPatch((tank_x + tank_width, tank_y + tank_height/2),
                         (curve_x, curve_y + curve_h/2),
                         connectionstyle="arc3,rad=0.2", arrowstyle='->',
                         mutation_scale=20, linewidth=2.5, color='#1976D2')
ax.add_patch(arrow1)
# title text removed for cleaner look

# 从响应曲线到参数提取
arrow2 = FancyArrowPatch((curve_x + curve_w/2, curve_y),
                         (param_x + param_w/2, param_y + param_h),
                         connectionstyle="arc3,rad=0", arrowstyle='->',
                         mutation_scale=20, linewidth=2.5, color='#2E7D32')
ax.add_patch(arrow2)

# 从参数提取到验证
arrow3 = FancyArrowPatch((param_x + param_w, param_y + param_h/2),
                         (valid_x, valid_y + valid_h/2),
                         connectionstyle="arc3,rad=0", arrowstyle='->',
                         mutation_scale=20, linewidth=2.5, color='#F57C00')
ax.add_patch(arrow3)
ax.text(9.5, 5, 'Validate', fontsize=12, ha='center', color='#F57C00',
        weight='bold')

# 保存
plt.tight_layout()
plt.savefig('step_response_diagram.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Generated: step_response_diagram.png")
plt.close()



