#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""溢流堰设计"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def spillway_flow(m, b, H, g=9.81):
    """Q = mbH^(3/2)"""
    Q = m * b * H**(3/2)
    return Q

def spillway_profile_WES(x, H0):
    """WES堰面曲线 y = Kx^n"""
    K = 0.5 / H0**0.85
    n = 1.85
    y = -K * x**n
    return y

def plot_spillway(filename='spillway_design.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    m, b, H = 0.5, 20, 3
    Q = spillway_flow(m, b, H)
    
    # 子图1：溢流堰剖面
    ax1 = axes[0, 0]
    x_profile = np.linspace(0, 6, 50)
    y_profile = spillway_profile_WES(x_profile, H)
    
    # 堰体
    ax1.fill_between([-2, 0], [0, 0], [-5, -5], alpha=0.5, color='gray')
    ax1.plot(x_profile, y_profile, 'b-', linewidth=3, label='WES堰面')
    ax1.fill_between(x_profile, y_profile, -10, alpha=0.3, color='gray')
    
    # 水面
    ax1.fill_between([-2, 0, 6], [H, H, -2], [H+1, H+1, -1], alpha=0.3, color='cyan')
    ax1.plot([-2, 0], [H, H], 'c-', linewidth=2)
    ax1.annotate('', xy=(0, H), xytext=(0, 0),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax1.text(0.3, H/2, f'H={H}m', fontsize=10, color='red')
    
    ax1.set_xlim([-2, 7])
    ax1.set_ylim([-6, 5])
    ax1.set_aspect('equal')
    ax1.set_title('溢流堰纵剖面', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 子图2：流量vs水头
    ax2 = axes[0, 1]
    H_range = np.linspace(1, 5, 30)
    Q_range = [spillway_flow(m, b, h, 9.81) for h in H_range]
    ax2.plot(H_range, Q_range, 'b-', linewidth=2)
    ax2.set_xlabel('堰上水头 H (m)', fontsize=12)
    ax2.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax2.set_title('溢流堰流量曲线', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 子图3：不同堰宽
    ax3 = axes[1, 0]
    b_range = np.linspace(10, 50, 30)
    Q_b = [spillway_flow(m, b_val, H) for b_val in b_range]
    ax3.plot(b_range, Q_b, 'g-', linewidth=2)
    ax3.set_xlabel('堰宽 b (m)', fontsize=12)
    ax3.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax3.set_title('堰宽对流量的影响', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 子图4：结果
    ax4 = axes[1, 1]
    ax4.axis('off')
    v = (Q/b) / H  # 近似流速
    info = f"""
    【溢流堰设计计算】
    
    参数：
      流量系数 m = {m}
      堰宽 b = {b} m
      堰上水头 H = {H} m
    
    流量公式：
      Q = mbH^(3/2)
      Q = {Q:.1f} m³/s
    
    单宽流量：
      q = Q/b = {Q/b:.2f} m²/s
    
    堰面曲线（WES）：
      y = Kx^1.85
      K = 0.5/H^0.85
      真空不分离
    
    设计要点：
      ✓ 堰面与水舌吻合
      ✓ 避免负压
      ✓ 泄流能力充足
      ✓ 下游消能
    
    应用：
      • 水库溢洪道
      • 防洪泄流
      • 大坝安全
    """
    ax4.text(0.1, 0.9, info, transform=ax4.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"图片已保存：{filename}")
    plt.close()

def main():
    print("="*60)
    print("溢流堰设计计算")
    print("="*60)
    Q = spillway_flow(0.5, 20, 3)
    print(f"\nQ={Q:.1f} m³/s")
    plot_spillway()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
