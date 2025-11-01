#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""动量方程应用 - 水流对平板、弯管的作用力"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def force_on_plate(Q, A, rho=1000):
    """射流冲击平板：F = ρQv"""
    v = Q / A
    F = rho * Q * v
    return F, v

def force_on_bend(Q, A, theta, p1, p2, rho=1000):
    """弯管作用力"""
    v = Q / A
    Fx = rho * Q * v * (1 - np.cos(np.deg2rad(theta))) + (p1 - p2) * A * np.cos(np.deg2rad(theta))
    Fy = rho * Q * v * np.sin(np.deg2rad(theta)) - (p1 - p2) * A * np.sin(np.deg2rad(theta))
    F_total = np.sqrt(Fx**2 + Fy**2)
    return Fx, Fy, F_total

def plot_momentum(filename='momentum_equation.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 子图1：射流冲击平板
    ax1 = axes[0, 0]
    Q = 0.05
    d = 0.1
    A = np.pi * d**2 / 4
    F, v = force_on_plate(Q, A)
    
    ax1.arrow(0, 0, 2, 0, head_width=0.3, head_length=0.3, fc='blue', ec='blue')
    ax1.plot([2.5, 2.5], [-1, 1], 'k-', linewidth=4)
    ax1.text(1, 0.5, f'v={v:.2f}m/s', fontsize=11)
    ax1.text(3, 0, f'F={F/1000:.1f}kN→', fontsize=11, color='red')
    ax1.set_xlim([-0.5, 4])
    ax1.set_ylim([-1.5, 1.5])
    ax1.set_aspect('equal')
    ax1.set_title('射流冲击平板', fontsize=13, fontweight='bold')
    ax1.axis('off')
    
    # 子图2：弯管受力
    ax2 = axes[0, 1]
    theta = 90
    Fx, Fy, F_total = force_on_bend(Q, A, theta, 200000, 100000)
    
    ax2.plot([0, 2], [0, 0], 'b-', linewidth=8, label='进口')
    ax2.plot([2, 2], [0, 2], 'b-', linewidth=8, label='出口')
    ax2.arrow(2.5, 1, -Fx/10000, -Fy/10000, head_width=0.2, head_length=0.2, 
             fc='red', ec='red', linewidth=2)
    ax2.text(1.5, 1.5, f'F={F_total/1000:.1f}kN', fontsize=11, color='red')
    ax2.set_xlim([-0.5, 3.5])
    ax2.set_ylim([-0.5, 3])
    ax2.set_aspect('equal')
    ax2.set_title(f'弯管受力（θ={theta}°）', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 子图3：力随流量变化
    ax3 = axes[1, 0]
    Q_range = np.linspace(0.01, 0.1, 20)
    F_range = [force_on_plate(q, A)[0] for q in Q_range]
    ax3.plot(Q_range, np.array(F_range)/1000, 'b-', linewidth=2)
    ax3.set_xlabel('流量 Q (m³/s)', fontsize=12)
    ax3.set_ylabel('作用力 F (kN)', fontsize=12)
    ax3.set_title('射流作用力vs流量', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 子图4：计算结果
    ax4 = axes[1, 1]
    ax4.axis('off')
    info = f"""
    【动量方程计算结果】
    
    射流冲击平板：
      流量 Q = {Q:.3f} m³/s
      直径 d = {d} m
      流速 v = {v:.2f} m/s
      作用力 F = ρQv
              = {F:.0f} N
              = {F/1000:.2f} kN
    
    弯管（θ=90°）：
      Fx = {Fx/1000:.2f} kN
      Fy = {Fy/1000:.2f} kN
      F总 = {F_total/1000:.2f} kN
    
    动量方程：
      ΣF = ρQ(v₂ - v₁)
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
    print("动量方程应用计算")
    print("="*60)
    
    Q = 0.05
    d = 0.1
    A = np.pi * d**2 / 4
    F, v = force_on_plate(Q, A)
    
    print(f"\n射流冲击平板：")
    print(f"Q={Q} m³/s, d={d}m")
    print(f"v={v:.2f} m/s")
    print(f"F={F/1000:.2f} kN")
    
    plot_momentum()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
