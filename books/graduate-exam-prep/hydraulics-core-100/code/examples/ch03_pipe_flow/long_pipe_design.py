#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""长管计算 - 沿程损失占主导"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def long_pipe_flow(H, L, d, lambda_=0.02, g=9.81):
    """长管流量计算：H = λ(L/d)(v²/2g)"""
    v = np.sqrt(2 * g * H / (lambda_ * L / d))
    A = np.pi * d**2 / 4
    Q = A * v
    return Q, v

def plot_long_pipe(filename='long_pipe_design.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    H = 10  # 水头
    L = 1000  # 管长
    d = 0.2  # 管径
    
    # 子图1：系统示意图
    ax1 = axes[0, 0]
    ax1.fill_between([0, 1], 10, 12, alpha=0.3, color='cyan')
    ax1.plot([0, 1, 1, 5, 5], [10, 10, 0, 0, -2], 'b-', linewidth=3)
    ax1.plot([0, 5], [10, -2], 'r--', linewidth=2, label='能量线')
    ax1.text(0.5, 11, '水箱', fontsize=10)
    ax1.text(3, -1, f'L={L}m, d={d}m', fontsize=10)
    ax1.set_xlim([-0.5, 5.5])
    ax1.set_ylim([-3, 13])
    ax1.set_title('长管系统示意图', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 子图2：流量vs管径
    ax2 = axes[0, 1]
    d_range = np.linspace(0.1, 0.5, 20)
    Q_range = [long_pipe_flow(H, L, d_val)[0] for d_val in d_range]
    ax2.plot(d_range, Q_range, 'g-', linewidth=2)
    ax2.set_xlabel('管径 d (m)', fontsize=12)
    ax2.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax2.set_title('流量vs管径', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 子图3：流量vs管长
    ax3 = axes[1, 0]
    L_range = np.linspace(100, 2000, 20)
    Q_L = [long_pipe_flow(H, L_val, d)[0] for L_val in L_range]
    ax3.plot(L_range, Q_L, 'r-', linewidth=2)
    ax3.set_xlabel('管长 L (m)', fontsize=12)
    ax3.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax3.set_title('流量vs管长', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 子图4：计算结果
    ax4 = axes[1, 1]
    ax4.axis('off')
    Q, v = long_pipe_flow(H, L, d)
    info = f"""
    【长管计算结果】
    
    参数：
      水头 H = {H} m
      管长 L = {L} m
      管径 d = {d} m
      λ = 0.02
    
    长管特点：
      沿程损失占主导
      忽略局部损失
    
    计算：
      H = λ(L/d)(v²/2g)
      v = √(2gH/(λL/d))
      v = {v:.2f} m/s
      Q = {Q:.4f} m³/s
      Q = {Q*1000:.2f} L/s
    
    设计要点：
      • 增大管径→流量增大
      • 减小管长→流量增大
      • 选用光滑管→λ减小
    """
    ax4.text(0.1, 0.9, info, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"图片已保存：{filename}")
    plt.close()

def main():
    print("="*60)
    print("长管水力计算")
    print("="*60)
    
    H, L, d = 10, 1000, 0.2
    Q, v = long_pipe_flow(H, L, d)
    
    print(f"\n参数：H={H}m, L={L}m, d={d}m")
    print(f"流速：v={v:.2f} m/s")
    print(f"流量：Q={Q:.4f} m³/s = {Q*1000:.2f} L/s")
    
    plot_long_pipe()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
