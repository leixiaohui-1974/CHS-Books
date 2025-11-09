"""
第01章 题目9: 曲面闸门总压力计算
===============================

知识点：
- 曲面静水总压力分解
- 水平分力（投影面积法）
- 铅直分力（压力体法）
- 矢量合成

Author: CHS-Books Team
Date: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Wedge, FancyArrowPatch

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def curved_gate_pressure(R=2, b=3, theta=90):
    """
    计算曲面闸门总压力
    
    参数:
    ----
    R : float
        圆弧半径 (m)
    b : float
        闸门宽度 (m)
    theta : float
        圆心角 (度)
    
    返回:
    ----
    dict : 包含所有计算结果的字典
    """
    rho = 1000  # kg/m³
    g = 9.81    # m/s²
    theta_rad = np.deg2rad(theta)
    
    print("=" * 60)
    print("曲面闸门总压力计算")
    print("=" * 60)
    print(f"\n已知条件:")
    print(f"  圆弧半径 R = {R} m")
    print(f"  闸门宽度 b = {b} m")
    print(f"  圆心角 θ = {theta}°")
    
    # (1) 水平分力 F_x
    print(f"\n(1) 水平分力 F_x:")
    print(f"    原理：曲面在铅直平面上的投影面积上的总压力")
    
    # 投影面积（矩形）
    A_x = R * b
    print(f"    投影面积 A_x = R × b = {R} × {b} = {A_x} m²")
    
    # 形心深度
    h_c = R / 2
    print(f"    形心深度 h_c = R/2 = {h_c} m")
    
    # 水平分力
    F_x = rho * g * h_c * A_x
    print(f"    水平分力 F_x = ρ·g·h_c·A_x")
    print(f"                 = {rho} × {g} × {h_c} × {A_x}")
    print(f"                 = {F_x:.0f} N = {F_x/1000:.2f} kN")
    
    # 压力中心位置
    I_c = b * R**3 / 12
    y_D = h_c + I_c / (A_x * h_c)
    print(f"    压力中心 y_D = {y_D:.3f} m （距水面）")
    
    # (2) 铅直分力 F_z
    print(f"\n(2) 铅直分力 F_z:")
    print(f"    原理：压力体（曲面以上水体）的重量")
    
    # 压力体横截面积（扇形 - 三角形）
    A_sector = np.pi * R**2 / 4  # 90度扇形
    A_triangle = R**2 / 2         # 直角三角形
    A_pressure_body = A_sector - A_triangle
    print(f"    扇形面积 = π·R²/4 = {A_sector:.4f} m²")
    print(f"    三角形面积 = R²/2 = {A_triangle:.4f} m²")
    print(f"    压力体横截面积 = {A_pressure_body:.4f} m²")
    
    # 压力体体积
    V = A_pressure_body * b
    print(f"    压力体体积 V = {A_pressure_body:.4f} × {b} = {V:.4f} m³")
    
    # 铅直分力
    F_z = rho * g * V
    print(f"    铅直分力 F_z = ρ·g·V")
    print(f"                 = {rho} × {g} × {V:.4f}")
    print(f"                 = {F_z:.0f} N = {F_z/1000:.2f} kN")
    print(f"    方向：向下")
    
    # (3) 总压力
    print(f"\n(3) 总压力 F:")
    F = np.sqrt(F_x**2 + F_z**2)
    print(f"    F = √(F_x² + F_z²)")
    print(f"      = √({F_x:.0f}² + {F_z:.0f}²)")
    print(f"      = √{F_x**2 + F_z**2:.0f}")
    print(f"      = {F:.0f} N = {F/1000:.2f} kN")
    
    # 方向角
    alpha = np.rad2deg(np.arctan(F_z / F_x))
    print(f"\n    方向角 α = arctan(F_z/F_x)")
    print(f"            = arctan({F_z/1000:.2f}/{F_x/1000:.2f})")
    print(f"            = arctan({F_z/F_x:.3f})")
    print(f"            = {alpha:.1f}°")
    print(f"    （与水平方向夹角）")
    
    print(f"\n重要性质：")
    print(f"  ✓ 总压力作用线通过圆心O")
    print(f"  ✓ 这是圆弧曲面的重要特性")
    
    return {
        'F_x': F_x,
        'F_z': F_z,
        'F': F,
        'alpha': alpha,
        'y_D': y_D,
        'V': V,
        'A_pressure_body': A_pressure_body
    }


def plot_curved_gate(R=2, b=3, results=None):
    """绘制曲面闸门示意图"""
    
    if results is None:
        results = curved_gate_pressure(R, b)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # === 左图：几何示意图 ===
    ax1.set_aspect('equal')
    
    # 绘制圆弧闸门
    arc = Arc((0, 0), 2*R, 2*R, angle=0, theta1=0, theta2=90,
             linewidth=3, color='black', label='闸门AB')
    ax1.add_patch(arc)
    
    # 标记A点和B点
    ax1.plot(R, 0, 'ro', markersize=10)
    ax1.text(R+0.15, -0.1, 'A', fontsize=14, fontweight='bold')
    ax1.plot(0, R, 'ro', markersize=10)
    ax1.text(-0.2, R+0.1, 'B', fontsize=14, fontweight='bold')
    
    # 标记圆心O
    ax1.plot(0, 0, 'ko', markersize=10)
    ax1.text(-0.2, -0.15, 'O', fontsize=14, fontweight='bold')
    
    # 绘制水域
    water_x = np.linspace(0, R, 100)
    water_y = np.sqrt(R**2 - water_x**2)
    ax1.fill_between(water_x, 0, water_y, alpha=0.3, color='lightblue')
    ax1.plot([0, R], [R, 0], 'b--', linewidth=1, alpha=0.5)
    
    # 绘制投影面积（虚线矩形）
    ax1.plot([0, 0], [0, R], 'g--', linewidth=2, label='投影面')
    ax1.text(-0.3, R/2, '投影\n面积', fontsize=10, color='green')
    
    # 标注压力体
    ax1.text(R*0.4, R*0.3, '压力体', fontsize=12, color='blue',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    # 标注尺寸
    ax1.plot([0, R], [0, 0], 'k-', linewidth=1)
    ax1.text(R/2, -0.25, f'R={R}m', fontsize=11)
    
    ax1.set_xlim(-0.5, R+0.5)
    ax1.set_ylim(-0.5, R+0.5)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=10)
    ax1.set_xlabel('x (m)', fontsize=12)
    ax1.set_ylabel('y (m)', fontsize=12)
    ax1.set_title('曲面闸门几何示意图', fontsize=13, fontweight='bold')
    
    # === 右图：受力分析图 ===
    ax2.set_aspect('equal')
    
    # 绘制圆弧
    arc2 = Arc((0, 0), 2*R, 2*R, angle=0, theta1=0, theta2=90,
              linewidth=3, color='black')
    ax2.add_patch(arc2)
    
    # 绘制水域
    ax2.fill_between(water_x, 0, water_y, alpha=0.3, color='lightblue')
    
    # 绘制水平分力 F_x
    F_x_scale = results['F_x'] / 50000  # 缩放用于显示
    arrow_Fx = FancyArrowPatch((0, results['y_D']), 
                              (F_x_scale, results['y_D']),
                              arrowstyle='->', mutation_scale=30,
                              linewidth=3, color='red')
    ax2.add_patch(arrow_Fx)
    ax2.text(F_x_scale/2, results['y_D']+0.2, 
            f"$F_x={results['F_x']/1000:.2f}$ kN",
            fontsize=11, color='red', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 绘制铅直分力 F_z
    F_z_scale = results['F_z'] / 50000
    arrow_Fz = FancyArrowPatch((R/2, R/2), (R/2, R/2-F_z_scale),
                              arrowstyle='->', mutation_scale=30,
                              linewidth=3, color='blue')
    ax2.add_patch(arrow_Fz)
    ax2.text(R/2+0.3, R/2-F_z_scale/2,
            f"$F_z={results['F_z']/1000:.2f}$ kN",
            fontsize=11, color='blue', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 绘制总压力 F
    F_scale = results['F'] / 50000
    alpha_rad = np.deg2rad(results['alpha'])
    F_end_x = F_scale * np.cos(alpha_rad)
    F_end_y = results['y_D'] - F_scale * np.sin(alpha_rad)
    arrow_F = FancyArrowPatch((0, results['y_D']), (F_end_x, F_end_y),
                             arrowstyle='->', mutation_scale=30,
                             linewidth=4, color='green')
    ax2.add_patch(arrow_F)
    ax2.text(F_end_x/2-0.3, (results['y_D']+F_end_y)/2,
            f"$F={results['F']/1000:.2f}$ kN\n$α={results['alpha']:.1f}°$",
            fontsize=11, color='green', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 绘制作用线通过圆心O
    ax2.plot([0, 0], [0, 0], 'ko', markersize=10)
    ax2.plot([0, R], [0, 0], 'g--', linewidth=1.5, alpha=0.5)
    ax2.text(0.1, -0.3, '作用线通过O', fontsize=10, color='green')
    
    ax2.set_xlim(-0.5, R+0.5)
    ax2.set_ylim(-0.5, R+0.5)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('x (m)', fontsize=12)
    ax2.set_ylabel('y (m)', fontsize=12)
    ax2.set_title('曲面闸门受力分析', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    return fig


def compare_different_angles():
    """比较不同圆心角的压力变化"""
    
    theta_range = np.linspace(30, 180, 50)
    F_x_values = []
    F_z_values = []
    F_values = []
    
    R = 2
    b = 3
    rho = 1000
    g = 9.81
    
    for theta in theta_range:
        theta_rad = np.deg2rad(theta)
        
        # 水平分力（投影高度随角度变化）
        h_proj = R * np.sin(theta_rad)
        A_x = h_proj * b
        h_c = h_proj / 2
        F_x = rho * g * h_c * A_x
        
        # 铅直分力（压力体体积随角度变化）
        A_sector = theta_rad * R**2 / 2
        A_triangle = R**2 * np.sin(theta_rad) / 2
        A_pressure = A_sector - A_triangle
        V = A_pressure * b
        F_z = rho * g * V
        
        # 总压力
        F = np.sqrt(F_x**2 + F_z**2)
        
        F_x_values.append(F_x / 1000)
        F_z_values.append(F_z / 1000)
        F_values.append(F / 1000)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(theta_range, F_x_values, 'r-', linewidth=2, label='水平分力 $F_x$')
    ax.plot(theta_range, F_z_values, 'b-', linewidth=2, label='铅直分力 $F_z$')
    ax.plot(theta_range, F_values, 'g-', linewidth=2, label='总压力 $F$')
    ax.axvline(x=90, color='k', linestyle='--', linewidth=1, label='设计角度 90°')
    
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('圆心角 θ (°)', fontsize=12)
    ax.set_ylabel('压力 (kN)', fontsize=12)
    ax.set_title('曲面闸门压力随圆心角变化', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("题目9: 曲面闸门总压力计算")
    print("=" * 60 + "\n")
    
    # 基础计算
    results = curved_gate_pressure(R=2, b=3, theta=90)
    
    # 绘制示意图
    fig1 = plot_curved_gate(R=2, b=3, results=results)
    plt.savefig('curved_gate_pressure.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ 示意图已保存: curved_gate_pressure.png")
    
    # 不同圆心角比较
    fig2 = compare_different_angles()
    plt.savefig('curved_gate_angle_comparison.png', dpi=150, bbox_inches='tight')
    print(f"✓ 圆心角对比图已保存: curved_gate_angle_comparison.png")
    
    plt.show()
    
    print("\n" + "=" * 60)
    print("计算完成！")
    print("=" * 60)
