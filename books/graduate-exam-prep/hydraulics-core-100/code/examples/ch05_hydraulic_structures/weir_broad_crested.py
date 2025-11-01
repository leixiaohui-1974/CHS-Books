#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""宽顶堰流量计算"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def broad_weir_free(b, H, m=0.32, g=9.81):
    """宽顶堰自由出流：Q = mb√(2g)H^(3/2)"""
    Q = m * b * np.sqrt(2 * g) * H**(3/2)
    return Q

def broad_weir_submerged(b, H, h_down, m=0.32, sigma=0.85, g=9.81):
    """宽顶堰淹没出流"""
    Q_free = broad_weir_free(b, H, m, g)
    if h_down / H > 0.75:
        Q = sigma * Q_free
        return Q, True
    else:
        return Q_free, False

def plot_broad_weir(filename='weir_broad_crested.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    b, H = 3.0, 1.2
    
    # 子图1：堰型对比
    ax1 = axes[0, 0]
    Q_broad = broad_weir_free(b, H, m=0.32)
    Q_sharp = 0.42 * b * np.sqrt(2*9.81) * H**(3/2)  # 薄壁堰
    
    labels = ['宽顶堰', '薄壁堰']
    Q_vals = [Q_broad, Q_sharp]
    ax1.bar(labels, Q_vals, color=['blue', 'green'], alpha=0.7)
    ax1.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax1.set_title(f'堰型流量对比（b={b}m, H={H}m）', fontsize=13, fontweight='bold')
    for i, v in enumerate(Q_vals):
        ax1.text(i, v+0.2, f'{v:.2f}', ha='center', fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 子图2：淹没影响
    ax2 = axes[0, 1]
    h_range = np.linspace(0, H*1.2, 30)
    Q_range = []
    for h_d in h_range:
        Q, is_sub = broad_weir_submerged(b, H, h_d)
        Q_range.append(Q)
    
    ax2.plot(h_range, Q_range, 'b-', linewidth=2)
    ax2.axvline(0.75*H, color='r', linestyle='--', label='淹没界限(0.75H)')
    ax2.set_xlabel('下游水深 h₃ (m)', fontsize=12)
    ax2.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax2.set_title('淹没对流量的影响', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 子图3：流量系数
    ax3 = axes[1, 0]
    m_vals = [0.32, 0.42]
    labels = ['宽顶堰', '薄壁堰']
    ax3.bar(labels, m_vals, color=['blue', 'green'], alpha=0.7)
    ax3.set_ylabel('流量系数 m', fontsize=12)
    ax3.set_title('流量系数对比', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 子图4：结果表
    ax4 = axes[1, 1]
    ax4.axis('off')
    info = f"""
    【宽顶堰计算结果】
    
    自由出流：
      堰宽 b = {b} m
      水头 H = {H} m
      流量系数 m = 0.32
      流量 Q = {Q_broad:.2f} m³/s
    
    淹没出流：
      淹没界限：h₃/H > 0.75
      淹没系数 σ = 0.85
      流量降低 15%
    
    宽顶堰特点：
      • 堰顶较宽（>0.67H）
      • 流量系数小（m=0.30-0.35）
      • 适合中大流量
      • 稳定性好
    
    与薄壁堰对比：
      宽顶堰流量更小
      但结构更稳定
      常用于溢洪道
    """
    ax4.text(0.1, 0.9, info, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"图片已保存：{filename}")
    plt.close()

def main():
    print("="*60)
    print("宽顶堰流量计算")
    print("="*60)
    
    b, H = 3.0, 1.2
    Q = broad_weir_free(b, H)
    
    print(f"\n参数：b={b}m, H={H}m")
    print(f"流量：Q={Q:.2f} m³/s")
    
    # 淹没情况
    h_down = 1.0
    Q_sub, is_sub = broad_weir_submerged(b, H, h_down)
    print(f"\n下游水深h₃={h_down}m时：")
    print(f"{'淹没' if is_sub else '自由'}出流，Q={Q_sub:.2f} m³/s")
    
    plot_broad_weir()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
