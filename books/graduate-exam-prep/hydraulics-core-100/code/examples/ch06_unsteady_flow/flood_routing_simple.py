#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简化洪水演进计算（运动波法）"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def flood_hydrograph(t, Q_peak=1000, t_peak=12):
    """洪水过程线（简化三角形）"""
    if t < t_peak:
        return Q_peak * t / t_peak
    else:
        return Q_peak * (24 - t) / (24 - t_peak) if t < 24 else 0

def kinematic_wave_routing(Q_in, dt, dx, c):
    """运动波演进：∂Q/∂t + c∂Q/∂x = 0"""
    # c = 波速，简化为常数
    n_time = len(Q_in)
    Q_out = np.zeros(n_time)
    delay = int(dx / (c * dt))
    
    for i in range(n_time):
        if i >= delay:
            Q_out[i] = Q_in[i - delay]  # 平移
        else:
            Q_out[i] = 0
    
    return Q_out

def plot_flood_routing(filename='flood_routing_simple.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 时间序列
    t = np.linspace(0, 48, 100)
    Q_upstream = np.array([flood_hydrograph(ti) for ti in t])
    
    # 演进参数
    dt = 0.5  # 时间步长
    dx = 10000  # 河段长度
    c = 2.0  # 波速 m/s
    
    Q_downstream = kinematic_wave_routing(Q_upstream, dt, dx, c)
    
    # 子图1：洪水过程线
    ax1 = axes[0, 0]
    ax1.plot(t, Q_upstream, 'b-', linewidth=2, label='上游断面')
    ax1.plot(t, Q_downstream, 'r--', linewidth=2, label='下游断面')
    ax1.set_xlabel('时间 t (h)', fontsize=12)
    ax1.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax1.set_title('洪水演进过程', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 子图2：峰现时间延迟
    ax2 = axes[0, 1]
    t_peak_up = t[np.argmax(Q_upstream)]
    t_peak_down = t[np.argmax(Q_downstream)]
    delay_time = t_peak_down - t_peak_up
    
    ax2.bar(['上游峰现', '下游峰现', '时间延迟'], 
           [t_peak_up, t_peak_down, delay_time],
           color=['blue', 'red', 'green'], alpha=0.6)
    ax2.set_ylabel('时间 (h)', fontsize=12)
    ax2.set_title('洪峰时间分析', fontsize=13, fontweight='bold')
    for i, val in enumerate([t_peak_up, t_peak_down, delay_time]):
        ax2.text(i, val+0.5, f'{val:.1f}h', ha='center', fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 子图3：波速影响
    ax3 = axes[1, 0]
    c_range = [1, 2, 3, 4]
    colors_c = plt.cm.Reds(np.linspace(0.4, 1, len(c_range)))
    ax3.plot(t, Q_upstream, 'b-', linewidth=2, label='上游')
    for i, c_val in enumerate(c_range):
        Q_down = kinematic_wave_routing(Q_upstream, dt, dx, c_val)
        ax3.plot(t, Q_down, '--', linewidth=2, color=colors_c[i],
                label=f'c={c_val}m/s')
    ax3.set_xlabel('时间 t (h)', fontsize=12)
    ax3.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax3.set_title('波速对演进的影响', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # 子图4：结果
    ax4 = axes[1, 1]
    ax4.axis('off')
    travel_time = dx / c / 3600  # 转为小时
    info = f"""
    【洪水演进计算】
    
    上游洪水：
      峰值流量 Qmax = {np.max(Q_upstream):.0f} m³/s
      峰现时间 tpeak = {t_peak_up:.1f} h
    
    河段参数：
      河段长度 Δx = {dx/1000:.1f} km
      波速 c = {c} m/s
      传播时间 = {travel_time:.2f} h
    
    下游洪水：
      峰值流量 = {np.max(Q_downstream):.0f} m³/s
      峰现时间 = {t_peak_down:.1f} h
      时间延迟 = {delay_time:.1f} h
    
    运动波法：
      ∂Q/∂t + c∂Q/∂x = 0
      • 简化方法
      • 仅考虑平移
      • 不考虑削峰展宽
    
    应用：
      • 洪水预报
      • 防洪调度
      • 水库设计
    
    说明：
      实际洪水演进更复杂
      需用完整Saint-Venant方程
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
    print("简化洪水演进计算")
    print("="*60)
    t = np.linspace(0, 48, 100)
    Q_upstream = np.array([flood_hydrograph(ti) for ti in t])
    Q_downstream = kinematic_wave_routing(Q_upstream, 0.5, 10000, 2.0)
    
    print(f"\n上游洪峰：{np.max(Q_upstream):.0f} m³/s")
    print(f"下游洪峰：{np.max(Q_downstream):.0f} m³/s")
    print(f"峰现时间差：{t[np.argmax(Q_downstream)] - t[np.argmax(Q_upstream)]:.1f} h")
    
    plot_flood_routing()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
