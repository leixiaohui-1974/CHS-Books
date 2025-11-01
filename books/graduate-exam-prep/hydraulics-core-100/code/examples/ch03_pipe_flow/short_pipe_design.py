#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""短管计算 - 局部损失不可忽略"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def short_pipe_flow(H, L, d, lambda_=0.02, zeta_sum=3.0, g=9.81):
    """短管流量：H = (λL/d + Σζ)(v²/2g)"""
    v = np.sqrt(2 * g * H / (lambda_ * L / d + zeta_sum))
    A = np.pi * d**2 / 4
    Q = A * v
    return Q, v

def plot_short_pipe(filename='short_pipe_design.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    H, L, d = 5, 50, 0.15
    Q, v = short_pipe_flow(H, L, d)
    
    # 子图1：短管vs长管对比
    ax1 = axes[0, 0]
    L_range = np.linspace(10, 500, 30)
    Q_short = []
    Q_long = []
    for L_val in L_range:
        q_s, _ = short_pipe_flow(H, L_val, d)  # 考虑局部损失
        q_l = np.pi * d**2 / 4 * np.sqrt(2*9.81*H / (0.02*L_val/d))  # 仅沿程
        Q_short.append(q_s)
        Q_long.append(q_l)
    
    ax1.plot(L_range, Q_short, 'b-', linewidth=2, label='短管（含局部损失）')
    ax1.plot(L_range, Q_long, 'r--', linewidth=2, label='长管（仅沿程）')
    ax1.axvline(L, color='g', linestyle=':', linewidth=1.5, label=f'设计L={L}m')
    ax1.set_xlabel('管长 L (m)', fontsize=12)
    ax1.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax1.set_title('短管vs长管流量对比', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 子图2：损失构成
    ax2 = axes[0, 1]
    hf = 0.02 * (L/d) * (v**2/(2*9.81))
    hj = 3.0 * (v**2/(2*9.81))
    labels = ['沿程损失', '局部损失']
    values = [hf, hj]
    colors = ['blue', 'orange']
    ax2.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax2.set_title(f'损失构成（L={L}m）', fontsize=13, fontweight='bold')
    
    # 子图3：局部阻力系数影响
    ax3 = axes[1, 0]
    zeta_range = np.linspace(1, 10, 20)
    Q_zeta = [short_pipe_flow(H, L, d, zeta_sum=z)[0] for z in zeta_range]
    ax3.plot(zeta_range, Q_zeta, 'r-', linewidth=2)
    ax3.set_xlabel('Σζ', fontsize=12)
    ax3.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax3.set_title('局部阻力系数对流量的影响', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 子图4：结果
    ax4 = axes[1, 1]
    ax4.axis('off')
    info = f"""
    【短管计算结果】
    
    参数：
      水头 H = {H} m
      管长 L = {L} m
      管径 d = {d} m
      λ = 0.02
      Σζ = 3.0
    
    短管判别：
      L/d = {L/d:.1f}
      λL/d = {0.02*L/d:.2f}
      Σζ = 3.0
      Σζ/(λL/d) = {3.0/(0.02*L/d):.2f}
      → Σζ不可忽略 ✓
    
    计算：
      v = √(2gH/(λL/d+Σζ))
      v = {v:.2f} m/s
      Q = {Q:.4f} m³/s
    
    损失分析：
      沿程：hf = {hf:.2f} m
      局部：hj = {hj:.2f} m
      总计：h = {hf+hj:.2f} m
    
    短管特点：
      • 管长较短
      • 局部损失重要
      • 需考虑所有损失
    """
    ax4.text(0.1, 0.9, info, transform=ax4.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"图片已保存：{filename}")
    plt.close()

def main():
    print("="*60)
    print("短管水力计算")
    print("="*60)
    H, L, d = 5, 50, 0.15
    Q, v = short_pipe_flow(H, L, d)
    print(f"\n参数：H={H}m, L={L}m, d={d}m")
    print(f"流速：v={v:.2f} m/s")
    print(f"流量：Q={Q:.4f} m³/s")
    plot_short_pipe()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
