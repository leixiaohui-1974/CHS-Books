#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""水锤分析 - 管道水力瞬变"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def wave_speed(K, E, d, delta, rho=1000):
    """水锤波速 a = √(K/ρ(1 + Kd/(Eδ)))"""
    a = np.sqrt(K / (rho * (1 + K * d / (E * delta))))
    return a

def water_hammer_pressure(v0, a, g=9.81):
    """Joukowsky公式：Δp = ρav₀"""
    rho = 1000
    delta_p = rho * a * v0
    delta_h = delta_p / (rho * g)
    return delta_p, delta_h

def plot_water_hammer(filename='water_hammer_analysis.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 参数
    v0 = 2.0  # 初始流速
    K = 2.1e9  # 水的体积模量
    E = 2e11  # 钢管弹性模量
    d, delta = 0.5, 0.01  # 管径和壁厚
    
    a = wave_speed(K, E, d, delta)
    delta_p, delta_h = water_hammer_pressure(v0, a)
    
    # 子图1：水锤压力波传播
    ax1 = axes[0, 0]
    L = 1000  # 管长
    x = np.linspace(0, L, 100)
    t_vals = [0, 0.25, 0.5, 0.75, 1.0]
    colors = plt.cm.Blues(np.linspace(0.3, 1, len(t_vals)))
    
    for i, t_frac in enumerate(t_vals):
        # 简化的压力波传播模型
        wave_pos = t_frac * L
        p_wave = np.zeros_like(x)
        mask = x <= wave_pos
        p_wave[mask] = delta_h
        ax1.plot(x, p_wave, color=colors[i], linewidth=2, 
                label=f't={t_frac:.2f}T')
    
    ax1.set_xlabel('管道位置 x (m)', fontsize=12)
    ax1.set_ylabel('压强升高 Δh (m)', fontsize=12)
    ax1.set_title('水锤波传播过程', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 子图2：流速vs水锤压强
    ax2 = axes[0, 1]
    v_range = np.linspace(0.5, 5, 30)
    dh_range = [water_hammer_pressure(v, a)[1] for v in v_range]
    ax2.plot(v_range, dh_range, 'r-', linewidth=2)
    ax2.set_xlabel('初始流速 v₀ (m/s)', fontsize=12)
    ax2.set_ylabel('水锤压强 Δh (m)', fontsize=12)
    ax2.set_title('Joukowsky公式：Δh = av₀/g', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 子图3：管材对波速影响
    ax3 = axes[1, 0]
    materials = ['钢管', '铸铁', 'PVC', '混凝土']
    E_vals = [2e11, 1e11, 3e9, 3e10]
    a_vals = [wave_speed(K, E_val, d, delta) for E_val in E_vals]
    colors_mat = ['gray', 'brown', 'blue', 'orange']
    bars = ax3.bar(materials, a_vals, color=colors_mat, alpha=0.7)
    ax3.set_ylabel('波速 a (m/s)', fontsize=12)
    ax3.set_title('不同管材的波速', fontsize=13, fontweight='bold')
    for bar, a_val in zip(bars, a_vals):
        height = bar.get_height()
        ax3.text(bar.get_x()+bar.get_width()/2, height+20, f'{a_val:.0f}',
                ha='center', va='bottom', fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 子图4：结果
    ax4 = axes[1, 1]
    ax4.axis('off')
    T = 2 * L / a  # 相位
    info = f"""
    【水锤计算结果】
    
    管道参数：
      管长 L = {L} m
      管径 d = {d} m
      壁厚 δ = {delta} m
      材料：钢管 (E={E:.1e} Pa)
    
    水锤波速：
      a = √(K/ρ(1+Kd/(Eδ)))
      a = {a:.1f} m/s
    
    初始流速：v₀ = {v0} m/s
    
    Joukowsky公式：
      Δp = ρav₀ = {delta_p:.0f} Pa
      Δh = av₀/g = {delta_h:.1f} m
    
    相位：
      T = 2L/a = {T:.2f} s
    
    防护措施：
      • 缓闭阀门（t > T）
      • 调压塔
      • 安全阀
      • 空气罐
    
    危险性：
      ⚠ 压强过高→爆管
      ⚠ 负压→断流、振动
    """
    ax4.text(0.1, 0.9, info, transform=ax4.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"图片已保存：{filename}")
    plt.close()

def main():
    print("="*60)
    print("水锤分析")
    print("="*60)
    K, E = 2.1e9, 2e11
    d, delta = 0.5, 0.01
    a = wave_speed(K, E, d, delta)
    print(f"\n波速：a={a:.1f} m/s")
    
    v0 = 2.0
    delta_p, delta_h = water_hammer_pressure(v0, a)
    print(f"初始流速：v₀={v0} m/s")
    print(f"水锤压强：Δh={delta_h:.1f} m")
    
    plot_water_hammer()
    print("\n计算完成！")

if __name__ == "__main__":
    main()
