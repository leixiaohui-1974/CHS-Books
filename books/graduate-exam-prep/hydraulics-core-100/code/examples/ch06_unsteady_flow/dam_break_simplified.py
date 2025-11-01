#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""溃坝波简化计算（理想情况）"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def dam_break_wave_speed(h0, g=9.81):
    """溃坝波波速：c = √(gh)"""
    c = np.sqrt(g * h0)
    return c

def dam_break_depth_profile(x, t, h0, g=9.81):
    """溃坝后水深分布（简化Ritter解）"""
    c0 = np.sqrt(g * h0)
    
    # 波前位置
    x_front = 2 * c0 * t
    # 波尾位置
    x_tail = -c0 * t
    
    h = np.zeros_like(x)
    for i, xi in enumerate(x):
        if xi < x_tail:
            h[i] = h0  # 上游未扰动
        elif xi > x_front:
            h[i] = 0  # 下游干河床
        else:
            # 中间膨胀波区域
            h[i] = (4 / (9 * g)) * (c0 - xi / (2 * t))**2
    
    return h, x_front, x_tail

def plot_dam_break(filename='dam_break_simplified.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    h0 = 10  # 初始水深
    g = 9.81
    
    # 子图1：不同时刻水深分布
    ax1 = axes[0, 0]
    x = np.linspace(-200, 400, 200)
    t_vals = [5, 10, 15, 20]
    colors = plt.cm.Blues(np.linspace(0.4, 1, len(t_vals)))
    
    for i, t in enumerate(t_vals):
        h, x_front, x_tail = dam_break_depth_profile(x, t, h0, g)
        ax1.plot(x, h, linewidth=2, color=colors[i], label=f't={t}s')
    
    ax1.axvline(0, color='r', linestyle='--', linewidth=1.5, label='坝址')
    ax1.set_xlabel('距离 x (m)', fontsize=12)
    ax1.set_ylabel('水深 h (m)', fontsize=12)
    ax1.set_title('溃坝波传播过程', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 12])
    
    # 子图2：波前传播距离
    ax2 = axes[0, 1]
    t_range = np.linspace(0, 30, 50)
    c0 = dam_break_wave_speed(h0, g)
    x_front_range = 2 * c0 * t_range
    
    ax2.plot(t_range, x_front_range, 'r-', linewidth=2)
    ax2.set_xlabel('时间 t (s)', fontsize=12)
    ax2.set_ylabel('波前位置 x (m)', fontsize=12)
    ax2.set_title('波前传播距离 vs 时间', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 子图3：初始水深对波速影响
    ax3 = axes[1, 0]
    h0_range = np.linspace(1, 20, 30)
    c0_range = [dam_break_wave_speed(h) for h in h0_range]
    
    ax3.plot(h0_range, c0_range, 'b-', linewidth=2)
    ax3.set_xlabel('初始水深 h₀ (m)', fontsize=12)
    ax3.set_ylabel('波速 c₀ (m/s)', fontsize=12)
    ax3.set_title('波速 c = √(gh₀)', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 子图4：结果
    ax4 = axes[1, 1]
    ax4.axis('off')
    c0 = dam_break_wave_speed(h0)
    t_example = 20
    x_front_example = 2 * c0 * t_example
    
    info = f"""
    【溃坝波计算（Ritter解）】
    
    初始条件：
      上游水深 h₀ = {h0} m
      下游干河床
      瞬时全溃
    
    波速：
      c₀ = √(gh₀) = {c0:.2f} m/s
    
    波前传播：
      x_front = 2c₀t
      
      t = {t_example}s时：
      x_front = {x_front_example:.1f} m
    
    Ritter解（1892）：
      • 理想矩形断面
      • 水平河床
      • 无摩阻
      • 瞬时全溃
    
    水深分布：
      h = (4/9g)(c₀ - x/2t)²
      
    实际情况：
      • 有摩阻损失
      • 河床不规则
      • 溃坝有过程
      • 需数值模拟
    
    应用：
      ⚠ 溃坝风险分析
      ⚠ 洪水影响范围
      ⚠ 应急预案
    """
    ax4.text(0.05, 0.95, info, transform=ax4.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"图片已保存：{filename}")
    plt.close()

def main():
    print("="*60)
    print("溃坝波简化计算（Ritter解）")
    print("="*60)
    h0 = 10
    c0 = dam_break_wave_speed(h0)
    print(f"\n初始水深：h₀={h0} m")
    print(f"波速：c₀={c0:.2f} m/s")
    
    t = 20
    x_front = 2 * c0 * t
    print(f"\nt={t}s时，波前位置：{x_front:.1f} m")
    
    plot_dam_break()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
