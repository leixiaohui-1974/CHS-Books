#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
梯形断面临界水深计算（牛顿迭代法）

问题：第四章题67 - 梯形临界水深计算
描述：非矩形断面临界水深无显式解，需迭代求解

知识点：
1. 临界流条件：Fr = 1
2. 临界流方程：Q²B/(gA³) = 1
3. 牛顿迭代法求解
4. 比能曲线与临界比能

作者：CHS-Books项目组
日期：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def trapezoidal_geometry(b, m, h):
    """
    梯形断面几何特性
    
    参数:
        b: 底宽 (m)
        m: 边坡系数
        h: 水深 (m)
    
    返回:
        A: 过流面积 (m²)
        B: 水面宽 (m)
        P: 湿周 (m)
        R: 水力半径 (m)
    """
    A = (b + m * h) * h
    B = b + 2 * m * h
    P = b + 2 * h * np.sqrt(1 + m**2)
    R = A / P if P > 0 else 0
    return A, B, P, R


def solve_critical_depth_newton(Q, b, m, g=9.81, hc0=1.0, tol=1e-6, max_iter=100):
    """
    牛顿迭代法求临界水深
    
    临界流条件：Q²B/(gA³) = 1
    即：f(h) = Q²B/(gA³) - 1 = 0
    
    参数:
        Q: 流量 (m³/s)
        b: 底宽 (m)
        m: 边坡系数
        g: 重力加速度 (m/s²)
        hc0: 初始猜测值 (m)
        tol: 收敛精度
        max_iter: 最大迭代次数
    
    返回:
        hc: 临界水深 (m)
        iterations: 迭代次数
        residuals: 残差历史
    """
    h = hc0
    residuals = []
    
    print(f"\n=== 牛顿迭代法求临界水深 ===")
    print(f"初始猜测：hc₀ = {hc0:.4f} m")
    print(f"\n迭代过程：")
    print(f"{'Iter':<6} {'h (m)':<12} {'f(h)':<15} {'df/dh':<15} {'Δh (m)':<12}")
    print("-" * 70)
    
    for iteration in range(max_iter):
        # 计算当前断面几何
        A, B, P, R = trapezoidal_geometry(b, m, h)
        
        # 目标函数：f(h) = Q²B/(gA³) - 1
        f = Q**2 * B / (g * A**3) - 1
        residuals.append(abs(f))
        
        # 数值导数法计算 df/dh
        dh = 0.001  # 微小增量
        A2, B2, P2, R2 = trapezoidal_geometry(b, m, h + dh)
        f2 = Q**2 * B2 / (g * A2**3) - 1
        df = (f2 - f) / dh
        
        # 牛顿步
        if abs(df) < 1e-10:
            print(f"  警告：导数接近零，迭代停止")
            break
        
        delta_h = -f / df
        
        # 步长限制（防止负值或过大跳跃）
        delta_h = np.clip(delta_h, -0.3*h, 0.3*h)
        
        # 打印迭代信息
        print(f"{iteration+1:<6} {h:<12.6f} {f:<15.8e} {df:<15.6f} {delta_h:<12.6f}")
        
        # 更新h
        h_new = h + delta_h
        
        # 边界保护
        if h_new <= 0:
            h_new = h * 0.5
            print(f"  警告：h变负，调整为 {h_new:.6f} m")
        
        # 收敛判断
        if abs(delta_h) < tol:
            print(f"\n✓ 收敛！临界水深 hc = {h_new:.6f} m（{iteration+1}次迭代）")
            return h_new, iteration + 1, residuals
        
        h = h_new
    
    print(f"\n⚠ 未收敛（达到最大迭代次数{max_iter}）")
    return h, max_iter, residuals


def critical_specific_energy(Q, b, m, hc, g=9.81):
    """
    临界比能计算
    
    E_c = hc + Q²/(2gA_c²)
    
    参数:
        Q: 流量 (m³/s)
        b: 底宽 (m)
        m: 边坡系数
        hc: 临界水深 (m)
        g: 重力加速度 (m/s²)
    
    返回:
        Ec: 临界比能 (m)
        vc: 临界流速 (m/s)
        Ac: 临界断面积 (m²)
    """
    Ac, Bc, Pc, Rc = trapezoidal_geometry(b, m, hc)
    vc = Q / Ac
    Ec = hc + vc**2 / (2 * g)
    return Ec, vc, Ac


def specific_energy_curve(Q, b, m, g=9.81, h_min=0.1, h_max=5.0, num_points=200):
    """
    计算比能曲线 E-h
    
    参数:
        Q: 流量 (m³/s)
        b: 底宽 (m)
        m: 边坡系数
        g: 重力加速度 (m/s²)
        h_min, h_max: 水深范围 (m)
        num_points: 点数
    
    返回:
        h_array: 水深数组
        E_array: 比能数组
        Fr_array: 弗劳德数数组
    """
    h_array = np.linspace(h_min, h_max, num_points)
    E_array = np.zeros(num_points)
    Fr_array = np.zeros(num_points)
    
    for i, h in enumerate(h_array):
        A, B, P, R = trapezoidal_geometry(b, m, h)
        v = Q / A
        E = h + v**2 / (2 * g)
        Fr = v / np.sqrt(g * A / B)
        
        E_array[i] = E
        Fr_array[i] = Fr
    
    return h_array, E_array, Fr_array


def plot_critical_depth_analysis(Q, b, m, hc, residuals, filename='critical_depth_trapezoidal.png'):
    """
    绘制临界水深分析图（4子图）
    
    参数:
        Q: 流量 (m³/s)
        b: 底宽 (m)
        m: 边坡系数
        hc: 临界水深 (m)
        residuals: 残差历史
        filename: 保存文件名
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 子图1：比能曲线
    ax1 = axes[0, 0]
    
    h_array, E_array, Fr_array = specific_energy_curve(Q, b, m, h_max=hc*3)
    Ec, vc, Ac = critical_specific_energy(Q, b, m, hc)
    
    ax1.plot(E_array, h_array, 'b-', linewidth=2.5, label='比能曲线 E-h')
    ax1.plot(Ec, hc, 'ro', markersize=10, label=f'临界点 (Ec={Ec:.3f}m, hc={hc:.3f}m)')
    ax1.axhline(hc, color='r', linestyle='--', linewidth=1, alpha=0.5)
    ax1.axvline(Ec, color='r', linestyle='--', linewidth=1, alpha=0.5)
    
    # 标注缓流区和急流区
    hc_idx = np.argmin(np.abs(h_array - hc))
    ax1.text(E_array[hc_idx*2], hc*1.8, '缓流区\n(Fr<1)', 
             fontsize=11, ha='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax1.text(E_array[hc_idx//2], hc*0.5, '急流区\n(Fr>1)', 
             fontsize=11, ha='center', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    ax1.set_xlabel('比能 E (m)', fontsize=12)
    ax1.set_ylabel('水深 h (m)', fontsize=12)
    ax1.set_title('比能曲线与临界点', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10, loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(left=Ec*0.8)
    
    # 子图2：弗劳德数曲线
    ax2 = axes[0, 1]
    
    ax2.plot(h_array, Fr_array, 'g-', linewidth=2.5, label='Fr-h曲线')
    ax2.axhline(1, color='r', linestyle='--', linewidth=1.5, label='Fr=1（临界流）')
    ax2.axvline(hc, color='r', linestyle='--', linewidth=1, alpha=0.5)
    ax2.plot(hc, 1.0, 'ro', markersize=10, label=f'临界水深 hc={hc:.3f}m')
    
    ax2.fill_between(h_array, 0, Fr_array, where=(Fr_array>=1), 
                     alpha=0.2, color='blue', label='急流区(Fr>1)')
    ax2.fill_between(h_array, Fr_array, 3, where=(Fr_array<1), 
                     alpha=0.2, color='orange', label='缓流区(Fr<1)')
    
    ax2.set_xlabel('水深 h (m)', fontsize=12)
    ax2.set_ylabel('弗劳德数 Fr', fontsize=12)
    ax2.set_title('弗劳德数与水深关系', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10, loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 3])
    
    # 子图3：迭代收敛曲线
    ax3 = axes[1, 0]
    
    iterations = range(1, len(residuals) + 1)
    ax3.semilogy(iterations, residuals, 'bo-', linewidth=2, markersize=6)
    ax3.axhline(1e-6, color='r', linestyle='--', linewidth=1.5, label='收敛精度 (10⁻⁶)')
    
    ax3.set_xlabel('迭代次数', fontsize=12)
    ax3.set_ylabel('残差 |f(h)|（对数坐标）', fontsize=12)
    ax3.set_title('牛顿迭代收敛过程', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, which='both')
    
    # 子图4：断面形状与参数表
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    Ac, Bc, Pc, Rc = trapezoidal_geometry(b, m, hc)
    
    # 绘制断面形状
    ax4_sub = fig.add_axes([0.56, 0.12, 0.18, 0.25])
    
    # 断面坐标
    x_left = -m * hc
    x_right = b + m * hc
    x_coords = [x_left, 0, b, x_right, x_left]
    y_coords = [0, -hc, -hc, 0, 0]
    
    ax4_sub.plot(x_coords, y_coords, 'k-', linewidth=2)
    ax4_sub.fill(x_coords, y_coords, alpha=0.3, color='cyan')
    ax4_sub.axhline(-hc, color='r', linestyle='--', linewidth=1, alpha=0.7)
    ax4_sub.text(b/2, -hc/2, f'hc={hc:.3f}m', ha='center', fontsize=10, 
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    ax4_sub.text(b/2, 0.2, f'b={b}m', ha='center', fontsize=9)
    ax4_sub.text(-m*hc/2-0.3, -hc*0.6, f'1:{m}', fontsize=9, rotation=65)
    
    ax4_sub.set_aspect('equal')
    ax4_sub.set_xlim([-m*hc-0.5, b+m*hc+0.5])
    ax4_sub.set_ylim([-hc*1.3, hc*0.5])
    ax4_sub.axis('off')
    ax4_sub.set_title('临界流断面', fontsize=10)
    
    # 参数表
    info_text = f"""
    【梯形断面临界水深计算结果】
    
    渠道参数：
      底宽 b = {b:.2f} m
      边坡系数 m = {m:.2f}
      流量 Q = {Q:.2f} m³/s
      重力加速度 g = 9.81 m/s²
    
    临界水深：hc = {hc:.6f} m
    
    临界断面几何：
      过流面积 Ac = {Ac:.3f} m²
      水面宽 Bc = {Bc:.3f} m
      湿周 Pc = {Pc:.3f} m
      水力半径 Rc = {Rc:.3f} m
    
    临界流参数：
      流速 vc = {vc:.3f} m/s
      弗劳德数 Fr = 1.000（临界流）
      比能 Ec = {Ec:.3f} m
    
    计算方法：
      • 牛顿迭代法
      • 收敛精度：10⁻⁶
      • 迭代次数：{len(residuals)}次
      • 初值：hc₀ = 1.0 m
    
    临界流判别：
      Fr < 1  →  缓流（h > hc）
      Fr = 1  →  临界流（h = hc）✓
      Fr > 1  →  急流（h < hc）
    """
    
    ax4.text(0.05, 0.95, info_text, transform=ax4.transAxes,
             fontsize=9.5, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{filename}")
    plt.close()


def main():
    """
    主程序：第四章题67 - 梯形临界水深计算
    """
    print("="*70)
    print("第四章题67 - 梯形断面临界水深计算（牛顿迭代法）")
    print("="*70)
    
    # 题目数据
    Q = 15.0        # 流量 (m³/s)
    b = 5.0         # 底宽 (m)
    m = 1.5         # 边坡系数
    
    print(f"\n【题目】")
    print(f"梯形渠道，底宽b={b}m，边坡系数m={m}，流量Q={Q} m³/s")
    print(f"求：临界水深hc")
    
    # 求解临界水深
    hc, iterations, residuals = solve_critical_depth_newton(Q, b, m, hc0=1.0)
    
    # 计算临界流参数
    Ec, vc, Ac = critical_specific_energy(Q, b, m, hc)
    Ac_calc, Bc, Pc, Rc = trapezoidal_geometry(b, m, hc)
    Fr_c = vc / np.sqrt(9.81 * Ac / Bc)
    
    print(f"\n【计算结果】")
    print(f"临界水深：hc = {hc:.6f} m")
    print(f"临界流速：vc = {vc:.3f} m/s")
    print(f"临界比能：Ec = {Ec:.3f} m")
    print(f"弗劳德数：Fr = {Fr_c:.6f} ≈ 1.000 ✓")
    print(f"断面面积：Ac = {Ac:.3f} m²")
    print(f"水面宽度：Bc = {Bc:.3f} m")
    
    # 绘图
    plot_critical_depth_analysis(Q, b, m, hc, residuals)
    
    print("\n" + "="*70)
    print("临界水深计算完成！")
    print("="*70)


def exercise():
    """练习题"""
    print("\n" + "="*70)
    print("【练习题】")
    print("="*70)
    
    print("""
    1. 如果流量增大到Q=20 m³/s，临界水深如何变化？
    2. 如果边坡系数增大到m=2.0，对hc有何影响？
    3. 矩形断面（m=0）的临界水深有显式解吗？
    4. 为什么临界流时比能最小？
    
    提示：
    - 临界水深随Q增大而增大
    - 断面形状（m）影响hc
    - 矩形：hc = (Q²/(gb²))^(1/3)（显式解）
    - 临界流：Ec = (3/2)hc（梯形近似）
    """)


if __name__ == "__main__":
    main()
    exercise()
