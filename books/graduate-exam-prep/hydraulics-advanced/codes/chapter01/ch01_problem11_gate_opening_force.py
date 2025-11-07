"""
第01章 题目11: 闸门启闭力计算
===========================

知识点：
- 静水总压力
- 压力中心计算
- 力矩平衡
- 杠杆原理

Author: CHS-Books Team
Date: 2025-11-07
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def gate_opening_force(b=3, h=2, l_F=None):
    """
    计算闸门启闭力
    
    参数:
    ----
    b : float
        闸门宽度 (m)
    h : float
        闸门高度 (m)
    l_F : float
        力作用点距铰链的距离 (m)，None表示作用于门顶
    
    返回:
    ----
    dict : 包含所有计算结果的字典
    """
    rho = 1000  # kg/m³
    g = 9.81    # m/s²
    
    # 步骤1：计算静水总压力
    A = b * h
    h_c = h / 2
    P = rho * g * h_c * A
    
    # 步骤2：计算压力中心位置
    I_c = b * h**3 / 12
    y_D = h_c + I_c / (A * h_c)
    l_P = h - y_D  # 压力中心距铰链的距离
    
    # 步骤3：力矩平衡计算启闭力
    if l_F is None:
        l_F = h  # 作用于门顶
    
    F = P * l_P / l_F
    
    # 输出结果
    print("=" * 60)
    print("闸门启闭力计算")
    print("=" * 60)
    print(f"\n已知条件:")
    print(f"  闸门宽度 b = {b} m")
    print(f"  闸门高度 h = {h} m")
    print(f"  力作用点距铰链 l_F = {l_F} m")
    
    print(f"\n步骤1: 计算静水总压力")
    print(f"  闸门面积 A = b × h = {b} × {h} = {A} m²")
    print(f"  形心深度 h_c = h/2 = {h_c} m")
    print(f"  总压力 P = ρ·g·h_c·A")
    print(f"         = {rho} × {g} × {h_c} × {A}")
    print(f"         = {P:.0f} N = {P/1000:.2f} kN")
    
    print(f"\n步骤2: 计算压力中心位置")
    print(f"  惯性矩 I_c = b·h³/12 = {b} × {h}³/12 = {I_c:.4f} m⁴")
    print(f"  压力中心 y_D = h_c + I_c/(A·h_c)")
    print(f"            = {h_c} + {I_c:.4f}/({A} × {h_c})")
    print(f"            = {y_D:.4f} m")
    print(f"  距铰链 l_P = h - y_D = {h} - {y_D:.4f} = {l_P:.4f} m")
    
    print(f"\n步骤3: 力矩平衡")
    print(f"  F · l_F = P · l_P")
    print(f"  F = P · l_P / l_F")
    print(f"    = {P:.0f} × {l_P:.4f} / {l_F}")
    print(f"    = {F:.0f} N = {F/1000:.2f} kN")
    
    print(f"\n结论:")
    print(f"  所需启闭力 F = {F/1000:.2f} kN")
    print(f"  力臂比 l_P/l_F = {l_P/l_F:.4f}")
    print(f"  力放大系数 = {P/F:.2f}")
    
    return {
        'P': P,
        'y_D': y_D,
        'l_P': l_P,
        'l_F': l_F,
        'F': F,
        'h_c': h_c
    }


def plot_gate_forces(b=3, h=2, results=None):
    """绘制闸门受力示意图"""
    
    if results is None:
        results = gate_opening_force(b, h)
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    # 绘制闸门
    gate = Rectangle((0, 0), 0.2, h, 
                     facecolor='lightgray', edgecolor='black', 
                     linewidth=2, label='闸门')
    ax.add_patch(gate)
    
    # 绘制铰链
    ax.plot(0.1, 0, 'ko', markersize=15, label='铰链O')
    ax.text(-0.3, -0.1, 'O (铰链)', fontsize=11, fontweight='bold')
    
    # 绘制水域
    water = Rectangle((-1.5, 0), 1.5, h,
                     facecolor='lightblue', edgecolor='blue',
                     alpha=0.3, label='水域')
    ax.add_patch(water)
    
    # 绘制静水压力分布（三角形）
    y_pressure = np.array([0, h])
    x_pressure = np.array([0, -1])
    ax.fill_betweenx(y_pressure, 0, x_pressure, 
                    alpha=0.4, color='cyan', label='压力分布')
    
    # 绘制总压力 P
    y_P = results['y_D']
    arrow_P = FancyArrowPatch((-1.5, y_P), (-0.05, y_P),
                            arrowstyle='->', mutation_scale=30,
                            linewidth=3, color='red')
    ax.add_patch(arrow_P)
    ax.text(-1.3, y_P + 0.15, f"$P={results['P']/1000:.2f}$ kN",
           fontsize=12, color='red', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 绘制启闭力 F
    l_F = results['l_F']
    arrow_F = FancyArrowPatch((0.2, l_F), (0.8, l_F),
                            arrowstyle='->', mutation_scale=30,
                            linewidth=3, color='green')
    ax.add_patch(arrow_F)
    ax.text(0.5, l_F + 0.15, f"$F={results['F']/1000:.2f}$ kN",
           fontsize=12, color='green', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 标注尺寸
    # 高度 h
    ax.annotate('', xy=(1, h), xytext=(1, 0),
               arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text(1.15, h/2, f'$h={h}$ m', fontsize=11)
    
    # 形心深度 h_c
    ax.plot([-1.5, 0.2], [results['h_c'], results['h_c']], 
           'b--', linewidth=1, alpha=0.5)
    ax.text(-1.7, results['h_c'], f"$h_c={results['h_c']}$ m",
           fontsize=10, color='blue')
    
    # 压力中心 y_D
    ax.plot([-1.5, 0.2], [y_P, y_P], 'r--', linewidth=1, alpha=0.5)
    ax.text(-1.7, y_P, f"$y_D={y_P:.3f}$ m",
           fontsize=10, color='red')
    
    # 力臂 l_P
    ax.annotate('', xy=(0.5, y_P), xytext=(0.5, 0),
               arrowprops=dict(arrowstyle='<->', color='purple', lw=1.5))
    ax.text(0.6, y_P/2, f"$l_P={results['l_P']:.3f}$ m",
           fontsize=10, color='purple')
    
    # 力臂 l_F
    ax.annotate('', xy=(-0.5, l_F), xytext=(-0.5, 0),
               arrowprops=dict(arrowstyle='<->', color='green', lw=1.5))
    ax.text(-0.9, l_F/2, f"$l_F={l_F}$ m",
           fontsize=10, color='green')
    
    ax.set_xlim(-2, 1.5)
    ax.set_ylim(-0.5, h + 0.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_xlabel('水平距离 (m)', fontsize=12)
    ax.set_ylabel('高度 (m)', fontsize=12)
    ax.set_title('闸门启闭力示意图', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig


def compare_different_force_positions(b=3, h=2):
    """比较不同力作用点位置的启闭力"""
    
    # 力作用点位置范围：从门顶到门顶以上
    l_F_range = np.linspace(h, h + 2, 50)
    F_values = []
    
    results_base = gate_opening_force(b, h)
    P = results_base['P']
    l_P = results_base['l_P']
    
    for l_F in l_F_range:
        F = P * l_P / l_F
        F_values.append(F / 1000)  # 转换为kN
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(l_F_range, F_values, 'b-', linewidth=2, 
            label='启闭力 F')
    ax.axvline(x=h, color='r', linestyle='--', linewidth=1.5,
              label=f'门顶位置 (l_F={h}m)')
    ax.axvline(x=h+0.5, color='g', linestyle=':', linewidth=1.5,
              label='优化位置 (l_F=2.5m)')
    
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('力作用点距铰链距离 $l_F$ (m)', fontsize=12)
    ax.set_ylabel('启闭力 F (kN)', fontsize=12)
    ax.set_title('启闭力与力作用点位置关系', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    
    # 添加文本说明
    ax.text(h+1, 18, '力臂越长，启闭力越小\n（杠杆原理）',
           fontsize=11, color='blue',
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("题目11: 闸门启闭力计算")
    print("=" * 60 + "\n")
    
    # (1) 力作用于门顶
    print("\n(1) 力作用于门顶:")
    results1 = gate_opening_force(b=3, h=2, l_F=None)
    
    # (2) 力作用于门顶以上0.5m
    print("\n\n(2) 力作用于门顶以上0.5m:")
    results2 = gate_opening_force(b=3, h=2, l_F=2.5)
    
    # 比较
    print("\n\n" + "=" * 60)
    print("两种情况对比:")
    print("=" * 60)
    print(f"门顶位置 (l_F=2m):     F = {results1['F']/1000:.2f} kN")
    print(f"优化位置 (l_F=2.5m):  F = {results2['F']/1000:.2f} kN")
    print(f"减少量: ΔF = {(results1['F'] - results2['F'])/1000:.2f} kN")
    print(f"减少比例: {(results1['F'] - results2['F'])/results1['F']*100:.1f}%")
    
    # 绘制受力图
    fig1 = plot_gate_forces(b=3, h=2, results=results1)
    plt.savefig('gate_forces_diagram.png', dpi=150, bbox_inches='tight')
    print(f"\n✓ 受力图已保存: gate_forces_diagram.png")
    
    # 绘制比较图
    fig2 = compare_different_force_positions(b=3, h=2)
    plt.savefig('gate_force_comparison.png', dpi=150, bbox_inches='tight')
    print(f"✓ 比较图已保存: gate_force_comparison.png")
    
    plt.show()
    
    print("\n" + "=" * 60)
    print("计算完成！")
    print("=" * 60)
