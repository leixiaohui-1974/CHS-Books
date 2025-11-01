#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""管道系统综合计算"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def series_pipes(H, L1, d1, L2, d2, lambda_=0.02, g=9.81):
    """串联管道"""
    # H = (λL₁/d₁ + λL₂/d₂)(v²/2g)，v在不同管中不同，需要Q守恒
    # 简化：假设同直径
    v = np.sqrt(2*g*H / (lambda_*(L1/d1 + L2/d2)))
    Q = np.pi * d1**2 / 4 * v
    return Q, v

def parallel_pipes(H, L, d1, d2, lambda_=0.02, g=9.81):
    """并联管道：水头损失相等"""
    # h₁ = h₂ → Q₁/Q₂ = √(d₁⁵/d₂⁵)
    v1 = np.sqrt(2*g*H / (lambda_*L/d1))
    v2 = np.sqrt(2*g*H / (lambda_*L/d2))
    Q1 = np.pi * d1**2 / 4 * v1
    Q2 = np.pi * d2**2 / 4 * v2
    return Q1 + Q2, Q1, Q2

def plot_system(filename='pipe_system_analysis.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 子图1：串联管道
    ax1 = axes[0, 0]
    ax1.fill_between([0, 1], [5, 5], [6, 6], alpha=0.3, color='cyan')
    ax1.plot([0, 1, 1, 3, 3, 5], [5, 5, 2, 2, 0, 0], 'b-', linewidth=3)
    ax1.text(0.5, 5.5, '水箱', fontsize=9)
    ax1.text(1.5, 2.3, 'd₁', fontsize=9)
    ax1.text(4, 0.3, 'd₂', fontsize=9)
    ax1.set_title('串联管道', fontsize=13, fontweight='bold')
    ax1.set_xlim([-0.5, 5.5])
    ax1.set_ylim([-1, 7])
    ax1.grid(True, alpha=0.3)
    
    # 子图2：并联管道
    ax2 = axes[0, 1]
    ax2.fill_between([0, 1], [5, 5], [6, 6], alpha=0.3, color='cyan')
    ax2.plot([0, 1, 1, 3], [5, 5, 3, 0], 'b-', linewidth=3, label='管1')
    ax2.plot([1, 3], [5, 0], 'g-', linewidth=3, label='管2')
    ax2.text(2, 4, 'd₁', fontsize=9, color='blue')
    ax2.text(2, 2, 'd₂', fontsize=9, color='green')
    ax2.set_title('并联管道', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.set_xlim([-0.5, 3.5])
    ax2.set_ylim([-1, 7])
    ax2.grid(True, alpha=0.3)
    
    # 子图3：串联流量
    ax3 = axes[1, 0]
    H, L1, L2 = 10, 100, 100
    d_range = np.linspace(0.1, 0.3, 20)
    Q_series = [series_pipes(H, L1, d, L2, d)[0] for d in d_range]
    ax3.plot(d_range, Q_series, 'b-', linewidth=2)
    ax3.set_xlabel('管径 d (m)', fontsize=12)
    ax3.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax3.set_title('串联管道流量vs管径', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 子图4：并联流量分配
    ax4 = axes[1, 1]
    ax4.axis('off')
    Q_total, Q1, Q2 = parallel_pipes(H, 100, 0.2, 0.15)
    info = f"""
    【管道系统计算结果】
    
    串联管道：
      总阻力 = R₁ + R₂
      流量相同
      水头损失叠加
    
    并联管道：
      H = {H} m
      L = 100 m
      d₁ = 0.2 m
      d₂ = 0.15 m
      
      Q₁ = {Q1:.4f} m³/s
      Q₂ = {Q2:.4f} m³/s
      Q总 = {Q_total:.4f} m³/s
      
      水头损失相等
      流量按阻力反比分配
    
    设计原则：
      串联：小管控制流量
      并联：大管分流更多
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
    print("管道系统计算")
    print("="*60)
    Q_total, Q1, Q2 = parallel_pipes(10, 100, 0.2, 0.15)
    print(f"\n并联管道：")
    print(f"Q₁={Q1:.4f} m³/s")
    print(f"Q₂={Q2:.4f} m³/s")
    print(f"Q总={Q_total:.4f} m³/s")
    plot_system()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
