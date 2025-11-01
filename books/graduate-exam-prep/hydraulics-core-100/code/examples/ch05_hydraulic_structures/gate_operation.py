#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""闸门启闭运行工况分析"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def gate_force(H_up, H_down, b, rho=1000, g=9.81):
    """闸门水压力"""
    P_up = 0.5 * rho * g * H_up**2 * b
    P_down = 0.5 * rho * g * H_down**2 * b
    P_net = P_up - P_down
    return P_net, P_up, P_down

def opening_flow(e, H_up, b, epsilon=0.65, g=9.81):
    """启门流量"""
    Q = epsilon * b * e * np.sqrt(2 * g * H_up)
    return Q

def plot_gate_operation(filename='gate_operation.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    H_up, H_down, b = 5, 1, 8
    P_net, P_up, P_down = gate_force(H_up, H_down, b)
    
    # 子图1：闸门受力
    ax1 = axes[0, 0]
    # 上游水位
    ax1.fill_between([0, 2], [0, 0], [H_up, H_up], alpha=0.3, color='cyan')
    ax1.plot([0, 2], [H_up, H_up], 'c-', linewidth=2)
    # 闸门
    ax1.fill_between([2, 2.2], [0, 0], [H_up, H_up], alpha=0.5, color='gray')
    # 下游水位
    ax1.fill_between([2.2, 5], [0, 0], [H_down, H_down], alpha=0.3, color='lightblue')
    ax1.plot([2.2, 5], [H_down, H_down], 'b--', linewidth=2)
    
    # 压力图示
    ax1.arrow(1, H_up/2, 0.5, 0, head_width=0.3, head_length=0.2, fc='red', ec='red')
    ax1.text(0.5, H_up/2, f'P₁={P_up/1e6:.1f}MN', fontsize=9, color='red')
    ax1.arrow(4, H_down/2, -0.5, 0, head_width=0.3, head_length=0.2, fc='blue', ec='blue')
    ax1.text(4.5, H_down/2, f'P₂={P_down/1e6:.1f}MN', fontsize=9, color='blue')
    
    ax1.set_xlim([-0.5, 5.5])
    ax1.set_ylim([-0.5, 6])
    ax1.set_title('闸门受力分析', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 子图2：开度vs流量
    ax2 = axes[0, 1]
    e_range = np.linspace(0.1, 3, 30)
    Q_range = [opening_flow(e, H_up, b) for e in e_range]
    ax2.plot(e_range, Q_range, 'b-', linewidth=2)
    ax2.set_xlabel('闸门开度 e (m)', fontsize=12)
    ax2.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax2.set_title('闸门开度-流量关系', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 子图3：上下游水位对净压力影响
    ax3 = axes[1, 0]
    H_up_range = np.linspace(2, 10, 20)
    P_net_range = [gate_force(h, H_down, b)[0]/1e6 for h in H_up_range]
    ax3.plot(H_up_range, P_net_range, 'r-', linewidth=2)
    ax3.set_xlabel('上游水位 H₁ (m)', fontsize=12)
    ax3.set_ylabel('净压力 P (MN)', fontsize=12)
    ax3.set_title('水位对净压力的影响', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 子图4：结果
    ax4 = axes[1, 1]
    ax4.axis('off')
    e_test = 1.5
    Q_test = opening_flow(e_test, H_up, b)
    info = f"""
    【闸门运行工况】
    
    参数：
      上游水位 H₁ = {H_up} m
      下游水位 H₂ = {H_down} m
      闸门宽度 b = {b} m
    
    受力分析：
      上游压力 P₁ = {P_up/1e6:.2f} MN
      下游压力 P₂ = {P_down/1e6:.2f} MN
      净压力 P = {P_net/1e6:.2f} MN
    
    启门流量（e={e_test}m）：
      Q = εbe√(2gH₁)
      Q = {Q_test:.1f} m³/s
    
    运行工况：
      • 正常泄流
      • 防洪调度
      • 灌溉供水
      • 航运过闸
    
    控制要点：
      ✓ 开度与流量匹配
      ✓ 振动控制
      ✓ 空化预防
      ✓ 下游消能
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
    print("闸门运行工况分析")
    print("="*60)
    P_net, P_up, P_down = gate_force(5, 1, 8)
    print(f"\n上游压力：{P_up/1e6:.2f} MN")
    print(f"下游压力：{P_down/1e6:.2f} MN")
    print(f"净压力：{P_net/1e6:.2f} MN")
    plot_gate_operation()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
