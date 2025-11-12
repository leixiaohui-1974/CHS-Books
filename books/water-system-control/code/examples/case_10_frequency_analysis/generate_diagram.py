#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成案例10（频域分析与Bode图）的系统示意图

目的：
- 展示频域分析的概念和方法
- 说明Bode图的构成和意义
- 清晰显示频域分析在控制设计中的应用
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Wedge
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

# ==================== 顶部：频域分析概念 ====================
concept_box = FancyBboxPatch((0.5, 9.5), 7, 1.3,
                             boxstyle="round,pad=0.15",
                             edgecolor='darkblue', facecolor='lightblue',
                             linewidth=2.5, alpha=0.5)
ax.add_patch(concept_box)

concept_text = (
    "Input: u(t) = A·sin(ωt)\n"
    "Output: y(t) = B·sin(ωt + φ)\n"
    "Magnitude: |G(jω)| = B/A,  Phase: ∠G(jω) = φ"
)
ax.text(4, 10.2, concept_text, fontsize=13, ha='center', va='top',
        family='monospace')

# ==================== 顶部右：Bode图概念 ====================
bode_concept_box = FancyBboxPatch((8.5, 9.5), 7, 1.3,
                                  boxstyle="round,pad=0.15",
                                  edgecolor='darkgreen', facecolor='lightgreen',
                                  linewidth=2.5, alpha=0.5)
ax.add_patch(bode_concept_box)

ax.text(12, 10.6, 'Bode Plot Components', fontsize=17, weight='bold',
        ha='center', va='top', color='darkgreen')
bode_text = (
    "Magnitude Plot: 20·log₁₀|G(jω)| vs log(ω)  [dB]\n"
    "Phase Plot: ∠G(jω) vs log(ω)  [deg]\n"
    "Reveals: Gain, Bandwidth, Stability margins"
)
ax.text(12, 10.2, bode_text, fontsize=13, ha='center', va='top',
        family='monospace')

# ==================== 中部：系统框图 ====================
# title text removed for cleaner look

# 正弦输入
sine_x, sine_y = 1, 7.5
ax.text(sine_x, sine_y + 0.5, 'Sine Input', fontsize=15, ha='center', 
        va='bottom', weight='bold')
# 简化正弦波
t_sine = np.linspace(0, 2*np.pi, 100)
sine_wave = 0.3 * np.sin(3*t_sine)
ax.plot(sine_x + t_sine*0.3 - 0.47, sine_y + sine_wave, 'r-', linewidth=2)

# 系统框
system_box = FancyBboxPatch((4, 7), 5, 1,
                            boxstyle="round,pad=0.1",
                            edgecolor='darkblue', facecolor='lightsteelblue',
                            linewidth=3)
ax.add_patch(system_box)
# title text removed for cleaner look

# 正弦输出
output_x, output_y = 12, 7.5
ax.text(output_x, output_y + 0.5, 'Sine Output', fontsize=15, ha='center',
        va='bottom', weight='bold')
# 输出正弦波（幅值和相位改变）
sine_wave_out = 0.4 * np.sin(3*t_sine - 0.5)
ax.plot(output_x + t_sine*0.3 - 0.47, output_y + sine_wave_out, 'b-', linewidth=2)
ax.text(output_x, output_y - 0.5, 'y(t) = B·sin(ωt+φ)', fontsize=13,
        ha='center', va='top', style='italic', family='monospace')

# 箭头
arrow1 = FancyArrowPatch((2.5, 7.5), (4, 7.5),
                         arrowstyle='->', mutation_scale=30,
                         linewidth=2.5, color='red')
ax.add_patch(arrow1)
ax.text(3.25, 7.8, 'Freq ω', fontsize=13, ha='center', va='bottom')

arrow2 = FancyArrowPatch((9, 7.5), (10.5, 7.5),
                         arrowstyle='->', mutation_scale=30,
                         linewidth=2.5, color='blue')
ax.add_patch(arrow2)
ax.text(9.75, 7.8, 'Gain & Phase', fontsize=13, ha='center', va='bottom')

# ==================== Bode图示意 ====================
ax.text(4, 6.2, 'Bode Magnitude Plot', fontsize=16, weight='bold',
        ha='center', va='bottom', color='darkblue')

# 幅值图框
mag_box = Rectangle((1, 4), 6, 2, edgecolor='darkblue', facecolor='white',
                     linewidth=2)
ax.add_patch(mag_box)

# 简化Bode幅值曲线
omega_bode = np.logspace(-2, 2, 100)
K = 2
tau = 1
mag_db = 20 * np.log10(K / np.sqrt(1 + (omega_bode * tau)**2))
# 归一化到框内
mag_norm = 4.5 + (mag_db - mag_db.min()) / (mag_db.max() - mag_db.min()) * 1.5
log_omega = 1 + np.log10(omega_bode) / 4 * 5.5

ax.plot(log_omega, mag_norm, 'b-', linewidth=2.5)
ax.plot([1, 7], [5, 5], 'k--', linewidth=1, alpha=0.5)  # 0dB线
ax.text(0.8, 5, '0dB', fontsize=12, ha='right', va='center')

# 标注
ax.text(1.2, 4.2, 'Low ω', fontsize=13, ha='left', va='bottom', style='italic')
ax.text(6.8, 4.2, 'High ω', fontsize=13, ha='right', va='bottom', style='italic')
ax.text(3.5, 3.7, 'log(ω)', fontsize=14, ha='center', va='top', weight='bold')
ax.text(0.7, 5.5, '|G(jω)|', fontsize=14, ha='right', va='center', 
        weight='bold', rotation=90)

# 截止频率标注
ax.plot([4, 4], [4, mag_norm[50]], 'r--', linewidth=1.5)
ax.text(4, 3.7, 'ωc', fontsize=14, ha='center', va='top', color='red',
        weight='bold')
ax.text(4.5, 4.5, 'Cutoff Freq', fontsize=12, ha='left', va='center',
        color='red', style='italic')

# 相位图
ax.text(12, 6.2, 'Bode Phase Plot', fontsize=16, weight='bold',
        ha='center', va='bottom', color='darkblue')

phase_box = Rectangle((9, 4), 6, 2, edgecolor='darkblue', facecolor='white',
                       linewidth=2)
ax.add_patch(phase_box)

# 简化Bode相位曲线
phase_deg = -np.arctan(omega_bode * tau) * 180 / np.pi
phase_norm = 5.5 + phase_deg / 90 * 1.5

ax.plot(log_omega + 8, phase_norm, 'g-', linewidth=2.5)
ax.plot([9, 15], [5.5, 5.5], 'k--', linewidth=1, alpha=0.5)  # 0度线
ax.plot([9, 15], [4, 4], 'k--', linewidth=1, alpha=0.5)  # -90度线

ax.text(8.8, 5.5, '0°', fontsize=12, ha='right', va='center')
ax.text(8.8, 4, '-90°', fontsize=12, ha='right', va='center')
ax.text(11.5, 3.7, 'log(ω)', fontsize=14, ha='center', va='top', weight='bold')
ax.text(8.7, 5.5, '∠G(jω)', fontsize=14, ha='right', va='center',
        weight='bold', rotation=90)

# 相位裕度标注
ax.plot([12, 12], [4, phase_norm[70]], 'm--', linewidth=1.5)
ax.text(12, 3.7, 'ωπ', fontsize=14, ha='center', va='top', color='magenta',
        weight='bold')
ax.text(12.5, 4.5, 'Phase Margin', fontsize=12, ha='left', va='center',
        color='magenta', style='italic')

# ==================== 底部：关键参数说明 ====================
ax.text(4, 3.3, 'Key Parameters from Bode Plot', fontsize=17, weight='bold',
        ha='center', va='bottom', color='darkblue')

params_box1 = FancyBboxPatch((0.5, 1.5), 7, 1.5,
                             boxstyle="round,pad=0.15",
                             edgecolor='darkgreen', facecolor='honeydew',
                             linewidth=2.5, alpha=0.8)
ax.add_patch(params_box1)

params_text1 = (
    "Bandwidth (BW):\n"
    "  Frequency range where |G(jω)| > -3dB\n"
    "  Determines response speed\n\n"
    "Cutoff Frequency (ωc):\n"
    "  Where |G(jωc)| = -3dB = 0.707\n"
    "  ωc ≈ 1/τ for first-order system"
)

# ==================== 底部右：稳定性裕度 ====================
ax.text(12, 3.3, 'Stability Margins', fontsize=17, weight='bold',
        ha='center', va='bottom', color='darkblue')

params_box2 = FancyBboxPatch((8.5, 1.5), 7, 1.5,
                             boxstyle="round,pad=0.15",
                             edgecolor='purple', facecolor='lavender',
                             linewidth=2.5, alpha=0.8)
ax.add_patch(params_box2)

params_text2 = (
    "Gain Margin (GM):\n"
    "  Extra gain before instability\n"
    "  GM = |G(jωπ)|⁻¹ where ∠G(jωπ) = -180°\n\n"
    "Phase Margin (PM):\n"
    "  Extra phase lag before instability\n"
    "  PM = 180° + ∠G(jωc) where |G(jωc)| = 1"
)
ax.text(12, 2.8, params_text2, fontsize=13, ha='center', va='top',
        family='monospace')

# ==================== 底部：应用说明 ====================
application_text = (
    "Applications in Control Design:\n"
    "• Bandwidth → Response Speed   • Roll-off → Noise Rejection\n"
    "• GM & PM → Stability Assessment   • Resonance Peak → Overshoot Prediction"
)

# ==================== 顶部装饰：频率扫描示意 ====================
# 低频、中频、高频标注
freq_labels = [
    (1.5, 9, 'Low Freq\n(DC Gain)', 'blue'),
    (8, 9, 'Mid Freq\n(Transition)', 'green'),
    (14.5, 9, 'High Freq\n(Roll-off)', 'red')
]

for x, y, text, color in freq_labels:
    ax.text(x, y, text, fontsize=13, ha='center', va='center',
            bbox=dict(boxstyle='round', facecolor='white',
                     edgecolor=color, linewidth=2, alpha=0.8))

# 保存图形
plt.tight_layout()
plt.savefig('frequency_analysis_diagram.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("✓ 示意图已生成：frequency_analysis_diagram.png")

plt.close()

