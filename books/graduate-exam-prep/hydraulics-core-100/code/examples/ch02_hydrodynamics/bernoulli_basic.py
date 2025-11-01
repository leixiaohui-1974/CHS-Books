#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""伯努利方程基本应用"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def bernoulli_head(z, p, v, rho=1000, g=9.81):
    """总水头 = z + p/(ρg) + v²/(2g)"""
    return z + p/(rho*g) + v**2/(2*g)

def plot_bernoulli_basic(filename='bernoulli_basic.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 子图1：伯努利方程演示
    ax1 = axes[0, 0]
    x = np.array([0, 1, 2, 3, 4])
    z = np.array([10, 8, 5, 3, 0])
    p = np.array([0, 1, 2, 1.5, 0]) * 9810  # Pa
    v = np.array([1, 2, 3, 2.5, 1])
    
    H_z = z
    H_p = z + p/9810
    H_total = H_z + p/9810 + v**2/(2*9.81)
    
    ax1.plot(x, z, 'b-', linewidth=2, label='位置水头 z')
    ax1.plot(x, H_p, 'g--', linewidth=2, label='z + p/(ρg)')
    ax1.plot(x, H_total, 'r-', linewidth=3, label='总水头 H')
    ax1.fill_between(x, 0, z, alpha=0.3, color='brown')
    ax1.set_xlabel('x (m)', fontsize=12)
    ax1.set_ylabel('水头 (m)', fontsize=12)
    ax1.set_title('伯努利方程三项', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 子图2：三种水头
    ax2 = axes[0, 1]
    labels = ['位置水头', '压力水头', '流速水头']
    colors = ['blue', 'green', 'red']
    example_H = [5, 3, 2]
    y_pos = np.arange(len(labels))
    bars = ax2.barh(y_pos, example_H, color=colors, alpha=0.6)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(labels)
    ax2.set_xlabel('水头 (m)', fontsize=12)
    ax2.set_title('水头构成（示例）', fontsize=13, fontweight='bold')
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax2.text(width+0.2, bar.get_y()+bar.get_height()/2, f'{example_H[i]:.1f}m',
                ha='left', va='center', fontsize=10)
    ax2.grid(True, alpha=0.3, axis='x')
    
    # 子图3：能量转换
    ax3 = axes[1, 0]
    x_conv = [0, 1, 2]
    E_kinetic = [2, 5, 3]
    E_pressure = [8, 5, 7]
    ax3.bar(x_conv, E_kinetic, label='动能 v²/(2g)', color='red', alpha=0.6)
    ax3.bar(x_conv, E_pressure, bottom=E_kinetic, label='压能 p/(ρg)', color='blue', alpha=0.6)
    ax3.set_xticks(x_conv)
    ax3.set_xticklabels(['断面1', '断面2', '断面3'])
    ax3.set_ylabel('能量 (m)', fontsize=12)
    ax3.set_title('动能与压能转换', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 子图4：结果
    ax4 = axes[1, 1]
    ax4.axis('off')
    info = f"""
    【伯努利方程】
    
    z + p/(ρg) + v²/(2g) = H = 常数
    
    三项水头：
      • 位置水头 z：重力势能
      • 压力水头 p/(ρg)：压强势能
      • 流速水头 v²/(2g)：动能
    
    物理意义：
      能量守恒
      势能↔动能
      总能量不变
    
    适用条件：
      ✓ 理想流体
      ✓ 定常流动
      ✓ 同一流线
      ✓ 不可压缩
    
    实际应用：
      → 有能量损失
      → 需修正系数
      → 考虑沿程/局部损失
    
    示例：
      z₁=10m, p₁=0
      z₂=0m, p₂=?
      v₁≈0 → v₂=√(2gz₁)
    """
    ax4.text(0.1, 0.9, info, transform=ax4.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"图片已保存：{filename}")
    plt.close()

def main():
    print("="*60)
    print("伯努利方程基本应用")
    print("="*60)
    z1, p1, v1 = 10, 0, 0
    z2, p2 = 0, None
    H = bernoulli_head(z1, p1, v1)
    v2 = np.sqrt(2*9.81*(H-z2))
    print(f"\n断面1：z₁={z1}m, v₁={v1}m/s, H={H:.2f}m")
    print(f"断面2：z₂={z2}m, v₂={v2:.2f}m/s")
    plot_bernoulli_basic()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
