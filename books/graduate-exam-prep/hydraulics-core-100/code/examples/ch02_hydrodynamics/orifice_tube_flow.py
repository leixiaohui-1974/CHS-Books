#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
孔口管嘴出流计算

知识点：
1. 小孔口出流：Q = μ·A·√(2gH)
2. 管嘴出流：Q = μ·A·√(2gH)
3. 收缩系数、流速系数、流量系数
4. 孔口vs管嘴对比

作者：CHS-Books项目组
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def orifice_flow(H, d, mu=0.62, g=9.81):
    """孔口出流：Q = μ·A·√(2gH)"""
    A = np.pi * d**2 / 4
    Q = mu * A * np.sqrt(2 * g * H)
    v = np.sqrt(2 * g * H)
    return Q, v

def tube_flow(H, d, mu=0.82, g=9.81):
    """管嘴出流：Q = μ·A·√(2gH)"""
    A = np.pi * d**2 / 4
    Q = mu * A * np.sqrt(2 * g * H)
    v_theory = np.sqrt(2 * g * H)
    v_actual = mu * v_theory
    return Q, v_actual

def plot_comparison(filename='orifice_tube_flow.png'):
    """绘制孔口管嘴对比图"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    H = 2.0  # 水头
    d = 0.05  # 直径
    
    # 孔口
    Q_o, v_o = orifice_flow(H, d)
    # 管嘴
    Q_t, v_t = tube_flow(H, d)
    
    # 子图1：流量对比
    ax1 = axes[0, 0]
    labels = ['孔口', '管嘴']
    Q_values = [Q_o, Q_t]
    ax1.bar(labels, Q_values, color=['blue', 'green'], alpha=0.7)
    ax1.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax1.set_title(f'孔口vs管嘴流量对比（H={H}m, d={d}m）', fontsize=13, fontweight='bold')
    for i, v in enumerate(Q_values):
        ax1.text(i, v+0.001, f'{v:.4f}', ha='center', fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 子图2：流速对比
    ax2 = axes[0, 1]
    v_theory = np.sqrt(2*9.81*H)
    v_values = [v_o, v_t, v_theory]
    labels2 = ['孔口\n实际', '管嘴\n实际', '理论']
    colors = ['blue', 'green', 'red']
    ax2.bar(labels2, v_values, color=colors, alpha=0.7)
    ax2.set_ylabel('流速 v (m/s)', fontsize=12)
    ax2.set_title('流速对比', fontsize=13, fontweight='bold')
    for i, v in enumerate(v_values):
        ax2.text(i, v+0.2, f'{v:.2f}', ha='center', fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 子图3：流量系数
    ax3 = axes[1, 0]
    mu_values = [0.62, 0.82]
    ax3.bar(labels, mu_values, color=['blue', 'green'], alpha=0.7)
    ax3.set_ylabel('流量系数 μ', fontsize=12)
    ax3.set_title('流量系数对比', fontsize=13, fontweight='bold')
    ax3.axhline(1.0, color='r', linestyle='--', linewidth=1, label='理想值')
    for i, v in enumerate(mu_values):
        ax3.text(i, v+0.02, f'{v:.2f}', ha='center', fontsize=10)
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_ylim([0, 1.1])
    
    # 子图4：结果表
    ax4 = axes[1, 1]
    ax4.axis('off')
    info = f"""
    【孔口管嘴出流对比】
    
    参数：H={H}m, d={d}m
    
    小孔口出流：
      流量系数 μ = 0.62
      流量 Q = {Q_o:.4f} m³/s
      流速 v = {v_o:.2f} m/s
    
    管嘴出流：
      流量系数 μ = 0.82
      流量 Q = {Q_t:.4f} m³/s
      流速 v = {v_t:.2f} m/s
    
    对比：
      管嘴流量是孔口的 {Q_t/Q_o:.2f} 倍
      增加 {(Q_t/Q_o-1)*100:.1f}%
    
    原因：
      孔口：收缩断面处流速最大
      管嘴：负压吸水，流量增大
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
    print("孔口管嘴出流计算")
    print("="*60)
    
    H = 2.0
    d = 0.05
    
    Q_o, v_o = orifice_flow(H, d)
    Q_t, v_t = tube_flow(H, d)
    
    print(f"\n参数：H={H}m, d={d}m")
    print(f"\n孔口出流：Q={Q_o:.4f} m³/s, v={v_o:.2f} m/s")
    print(f"管嘴出流：Q={Q_t:.4f} m³/s, v={v_t:.2f} m/s")
    print(f"\n管嘴流量增加：{(Q_t/Q_o-1)*100:.1f}%")
    
    plot_comparison()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
