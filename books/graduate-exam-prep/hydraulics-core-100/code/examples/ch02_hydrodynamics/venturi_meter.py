#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文丘里流量计"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def venturi_flow(d1, d2, delta_h, g=9.81):
    """文丘里流量：Q = (A₂/√(1-(A₂/A₁)²))√(2gΔh)"""
    A1 = np.pi * d1**2 / 4
    A2 = np.pi * d2**2 / 4
    Q = (A2 / np.sqrt(1 - (A2/A1)**2)) * np.sqrt(2 * g * delta_h)
    return Q

def plot_venturi(filename='venturi_meter.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    d1, d2 = 0.2, 0.1
    delta_h = 0.5
    Q = venturi_flow(d1, d2, delta_h)
    
    # 子图1：文丘里管示意图
    ax1 = axes[0, 0]
    x = [0, 1, 2, 3, 4]
    y1 = [d1/2, d1/2, d2/2, d1/2, d1/2]
    y2 = [-d1/2, -d1/2, -d2/2, -d1/2, -d1/2]
    ax1.fill_between(x, y1, y2, alpha=0.3, color='cyan')
    ax1.plot(x, y1, 'b-', linewidth=2)
    ax1.plot(x, y2, 'b-', linewidth=2)
    
    # 测压管
    ax1.plot([0.5, 0.5], [d1/2, d1/2+delta_h], 'r-', linewidth=2)
    ax1.plot([2, 2], [d2/2, d2/2+0], 'r-', linewidth=2)
    ax1.plot([0.3, 0.7], [d1/2+delta_h, d1/2+delta_h], 'r-', linewidth=2)
    ax1.annotate('', xy=(1.5, d1/2+delta_h/2), xytext=(1.5, d1/2),
                arrowprops=dict(arrowstyle='<->', color='orange', lw=2))
    ax1.text(1.7, d1/2+delta_h/2, f'Δh={delta_h}m', fontsize=10, color='orange')
    
    ax1.set_xlim([-0.5, 4.5])
    ax1.set_ylim([-0.2, 0.8])
    ax1.set_aspect('equal')
    ax1.set_title('文丘里流量计原理', fontsize=13, fontweight='bold')
    ax1.axis('off')
    
    # 子图2：流量vs压差
    ax2 = axes[0, 1]
    dh_range = np.linspace(0.1, 1.0, 20)
    Q_range = [venturi_flow(d1, d2, dh) for dh in dh_range]
    ax2.plot(dh_range, Q_range, 'b-', linewidth=2)
    ax2.set_xlabel('压差 Δh (m)', fontsize=12)
    ax2.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax2.set_title('流量vs压差', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 子图3：不同收缩比
    ax3 = axes[1, 0]
    d2_range = np.linspace(0.05, 0.15, 20)
    Q_d2 = [venturi_flow(d1, d, delta_h) for d in d2_range]
    ax3.plot(d2_range/d1, Q_d2, 'g-', linewidth=2)
    ax3.set_xlabel('收缩比 d₂/d₁', fontsize=12)
    ax3.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax3.set_title('收缩比对流量的影响', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 子图4：结果
    ax4 = axes[1, 1]
    ax4.axis('off')
    A1 = np.pi * d1**2 / 4
    A2 = np.pi * d2**2 / 4
    v1 = Q / A1
    v2 = Q / A2
    info = f"""
    【文丘里流量计计算】
    
    参数：
      进口直径 d₁ = {d1} m
      喉部直径 d₂ = {d2} m
      压差 Δh = {delta_h} m
    
    计算：
      A₁ = {A1:.4f} m²
      A₂ = {A2:.4f} m²
      
      Q = (A₂/√(1-(A₂/A₁)²))√(2gΔh)
        = {Q:.4f} m³/s
        = {Q*1000:.2f} L/s
    
    流速：
      v₁ = {v1:.2f} m/s
      v₂ = {v2:.2f} m/s
      v₂/v₁ = {v2/v1:.1f}
    
    应用：
      • 流量测量
      • 精度±1-2%
      • 压力损失小
      • 工业常用
    """
    ax4.text(0.1, 0.9, info, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"图片已保存：{filename}")
    plt.close()

def main():
    print("="*60)
    print("文丘里流量计计算")
    print("="*60)
    Q = venturi_flow(0.2, 0.1, 0.5)
    print(f"\nQ={Q:.4f} m³/s = {Q*1000:.2f} L/s")
    plot_venturi()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
