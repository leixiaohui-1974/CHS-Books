"""
第01章 题目6: U型测压管计算
=========================

知识点：
- 等压面原理
- 压强传递
- 多种液体的压强计算

Author: CHS-Books Team
Date: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def u_tube_manometer(rho_water=1000, rho_hg=13600, h1=0.5, delta_h=0.2):
    """
    U型测压管计算
    
    参数:
    ----
    rho_water : float
        水的密度 (kg/m³)
    rho_hg : float
        水银的密度 (kg/m³)
    h1 : float
        管道中心在水面以下的深度 (m)
    delta_h : float
        两侧水银面高差 (m)
    
    返回:
    ----
    p_pipe : float
        管道压强 (Pa)
    """
    g = 9.81  # m/s²
    
    # 计算管道压强
    p_pipe = g * (rho_hg * delta_h - rho_water * h1)
    
    # 输出结果
    print("=" * 60)
    print("U型测压管计算")
    print("=" * 60)
    print(f"\n已知条件:")
    print(f"  水密度 ρ_water = {rho_water} kg/m³")
    print(f"  水银密度 ρ_Hg = {rho_hg} kg/m³")
    print(f"  管道中心深度 h1 = {h1} m")
    print(f"  水银面高差 Δh = {delta_h} m")
    
    print(f"\n计算步骤:")
    print(f"  1. 水侧压强贡献: ρ_water·g·h1 = {rho_water * g * h1:.0f} Pa")
    print(f"  2. 水银侧压强贡献: ρ_Hg·g·Δh = {rho_hg * g * delta_h:.0f} Pa")
    print(f"  3. 管道压强: p = {rho_hg * g * delta_h:.0f} - {rho_water * g * h1:.0f}")
    print(f"               = {p_pipe:.0f} Pa")
    print(f"               = {p_pipe/1000:.2f} kPa")
    
    print(f"\n结论:")
    print(f"  管道中心处压强（表压）= {p_pipe/1000:.2f} kPa")
    print(f"  高于大气压强 {p_pipe/1000:.2f} kPa")
    
    return p_pipe


def plot_u_tube(rho_water=1000, rho_hg=13600, h1=0.5, delta_h=0.2):
    """绘制U型测压管示意图"""
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    # 绘制管道
    ax.plot([0, 2], [2, 2], 'k-', linewidth=3, label='管道')
    ax.plot([1, 1], [2, 2.5], 'k-', linewidth=2)
    
    # 绘制U型管
    # 左侧
    ax.plot([0.8, 0.8], [0, 2.5], 'b-', linewidth=2)
    # 底部
    ax.plot([0.8, 2.2], [0, 0], 'b-', linewidth=2)
    # 右侧
    ax.plot([2.2, 2.2], [0, 3], 'b-', linewidth=2)
    
    # 绘制液体
    # 左侧水
    water_left = Rectangle((0.8, 0.2), 0.2, 2.3, 
                           facecolor='lightblue', edgecolor='blue', 
                           alpha=0.6, label='水')
    ax.add_patch(water_left)
    
    # 底部水银
    hg_bottom = Rectangle((0.8, 0), 0.4, 0.2,
                          facecolor='silver', edgecolor='gray',
                          alpha=0.8, label='水银')
    ax.add_patch(hg_bottom)
    
    # 右侧水银
    hg_right = Rectangle((2.2, 0.2), 0.2, delta_h,
                         facecolor='silver', edgecolor='gray', alpha=0.8)
    ax.add_patch(hg_right)
    
    # 标注尺寸
    # h1
    ax.annotate('', xy=(0.5, 2.5), xytext=(0.5, 2),
               arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    ax.text(0.3, 2.25, f'$h_1={h1}m$', fontsize=12, color='red')
    
    # Δh
    ax.annotate('', xy=(2.5, 0.2 + delta_h), xytext=(2.5, 0.2),
               arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    ax.text(2.6, 0.2 + delta_h/2, f'$\\Delta h={delta_h}m$', 
            fontsize=12, color='red')
    
    # 水面线
    ax.plot([0, 3], [2.5, 2.5], 'b--', linewidth=1, alpha=0.5)
    ax.text(3.1, 2.5, '水面', fontsize=10, color='blue')
    
    # 等压面
    ax.plot([0.8, 2.2], [0.2, 0.2], 'g--', linewidth=2, alpha=0.7)
    ax.text(1.3, 0.05, '等压面', fontsize=10, color='green', 
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    
    # 压强值标注
    g = 9.81
    p_pipe = g * (rho_hg * delta_h - rho_water * h1)
    ax.text(1, 2.7, f'$p_{{管}}={p_pipe/1000:.2f}$ kPa', 
            fontsize=12, color='red',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 3.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=10)
    ax.set_xlabel('水平距离 (m)', fontsize=12)
    ax.set_ylabel('高度 (m)', fontsize=12)
    ax.set_title('U型测压管示意图', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig


def sensitivity_analysis():
    """敏感性分析：水银面高差对压强的影响"""
    
    delta_h_range = np.linspace(0.05, 0.5, 50)
    p_values = []
    
    g = 9.81
    rho_water = 1000
    rho_hg = 13600
    h1 = 0.5
    
    for dh in delta_h_range:
        p = g * (rho_hg * dh - rho_water * h1)
        p_values.append(p / 1000)  # 转换为kPa
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(delta_h_range * 100, p_values, 'b-', linewidth=2, 
            label='管道压强')
    ax.axhline(y=0, color='r', linestyle='--', linewidth=1, 
              label='大气压线')
    ax.axvline(x=20, color='g', linestyle=':', linewidth=1.5, 
              label='设计值 Δh=20cm')
    
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('水银面高差 Δh (cm)', fontsize=12)
    ax.set_ylabel('管道压强 (kPa)', fontsize=12)
    ax.set_title('U型测压管敏感性分析', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    # 基础计算
    print("\n" + "=" * 60)
    print("题目6: U型测压管计算")
    print("=" * 60 + "\n")
    
    p_pipe = u_tube_manometer()
    
    # 绘制示意图
    fig1 = plot_u_tube()
    plt.savefig('u_tube_manometer.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ 示意图已保存: u_tube_manometer.png")
    
    # 敏感性分析
    fig2 = sensitivity_analysis()
    plt.savefig('u_tube_sensitivity.png', dpi=150, bbox_inches='tight')
    print(f"✓ 敏感性分析图已保存: u_tube_sensitivity.png")
    
    plt.show()
    
    print("\n" + "=" * 60)
    print("计算完成！")
    print("=" * 60)
