#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""连续性方程应用 - 变直径管道流速流量关系"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def continuity_equation(Q, d):
    """Q = Av，求流速"""
    A = np.pi * d**2 / 4
    v = Q / A
    return v, A

def plot_continuity(filename='continuity_equation.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    Q = 0.05  # 流量恒定
    
    # 子图1：变直径管道
    ax1 = axes[0, 0]
    d1, d2 = 0.2, 0.1
    v1, A1 = continuity_equation(Q, d1)
    v2, A2 = continuity_equation(Q, d2)
    
    x = [0, 2, 2, 4]
    y1 = [d1/2, d1/2, d2/2, d2/2]
    y2 = [-d1/2, -d1/2, -d2/2, -d2/2]
    ax1.fill_between(x, y1, y2, alpha=0.3, color='cyan')
    ax1.plot(x, y1, 'b-', linewidth=2)
    ax1.plot(x, y2, 'b-', linewidth=2)
    ax1.text(1, 0, f'd₁={d1}m\nv₁={v1:.2f}m/s', ha='center', fontsize=10)
    ax1.text(3, 0, f'd₂={d2}m\nv₂={v2:.2f}m/s', ha='center', fontsize=10)
    ax1.set_xlim([-0.5, 4.5])
    ax1.set_ylim([-0.15, 0.15])
    ax1.set_aspect('equal')
    ax1.set_title(f'变直径管道（Q={Q} m³/s恒定）', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 子图2：流速vs管径
    ax2 = axes[0, 1]
    d_range = np.linspace(0.05, 0.3, 30)
    v_range = [continuity_equation(Q, d)[0] for d in d_range]
    ax2.plot(d_range, v_range, 'b-', linewidth=2)
    ax2.set_xlabel('管径 d (m)', fontsize=12)
    ax2.set_ylabel('流速 v (m/s)', fontsize=12)
    ax2.set_title('连续性方程：v = Q/A', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 子图3：面积vs流速（双对数）
    ax3 = axes[1, 0]
    ax3.loglog(d_range, v_range, 'g-', linewidth=2)
    ax3.set_xlabel('管径 d (m)', fontsize=12)
    ax3.set_ylabel('流速 v (m/s)', fontsize=12)
    ax3.set_title('v-d关系（对数坐标）', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, which='both')
    
    # 子图4：结果
    ax4 = axes[1, 1]
    ax4.axis('off')
    info = f"""
    【连续性方程计算】
    
    恒定流量 Q = {Q} m³/s
    
    断面1（大管）：
      直径 d₁ = {d1} m
      面积 A₁ = {A1:.4f} m²
      流速 v₁ = {v1:.2f} m/s
    
    断面2（小管）：
      直径 d₂ = {d2} m
      面积 A₂ = {A2:.4f} m²
      流速 v₂ = {v2:.2f} m/s
    
    验证：
      Q₁ = A₁v₁ = {A1*v1:.4f} m³/s ✓
      Q₂ = A₂v₂ = {A2*v2:.4f} m³/s ✓
      Q₁ = Q₂（流量守恒）
    
    连续性方程：
      Q = Av = 常数
      v ∝ 1/d²
      
    结论：
      管径减小→流速增大
      d₂/d₁ = {d2/d1}
      v₂/v₁ = {v2/v1:.1f}
    """
    ax4.text(0.1, 0.9, info, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"图片已保存：{filename}")
    plt.close()

def main():
    print("="*60)
    print("连续性方程计算")
    print("="*60)
    Q = 0.05
    d1, d2 = 0.2, 0.1
    v1, A1 = continuity_equation(Q, d1)
    v2, A2 = continuity_equation(Q, d2)
    print(f"\n流量Q={Q} m³/s")
    print(f"断面1：d={d1}m, v={v1:.2f}m/s")
    print(f"断面2：d={d2}m, v={v2:.2f}m/s")
    print(f"流速比：v₂/v₁={v2/v1:.1f}")
    plot_continuity()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
