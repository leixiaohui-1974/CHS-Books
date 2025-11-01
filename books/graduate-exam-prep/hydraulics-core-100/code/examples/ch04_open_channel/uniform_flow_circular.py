#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圆形管道非满流均匀流计算
========================

题目：清华大学2018年真题改编（第63题）
直径D=1.0m的圆形混凝土排水管道，底坡i=0.003，糙率n=0.013，设计流量Q=0.8 m³/s

求解：
1. 正常水深h₀（管道非满流）
2. 充满度α = h₀/D
3. 断面平均流速v
4. 比较满流情况下的输水能力

作者：CHS-Books
日期：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Circle, Wedge
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


def circular_geometry_from_filling(D, alpha):
    """
    根据充满度计算圆形断面几何要素
    
    参数：
        D: 管道直径 (m)
        alpha: 充满度，alpha = h/D
    
    返回：
        h: 水深 (m)
        A: 过流面积 (m²)
        chi: 湿周 (m)
        R: 水力半径 (m)
        theta: 充满角 (rad)
    """
    h = alpha * D
    
    # 充满角θ（从圆心到水面弦两端的圆心角）
    # h = D/2 - D/2 * cos(θ/2)
    # cos(θ/2) = 1 - 2h/D = 1 - 2α
    cos_half_theta = 1 - 2 * alpha
    
    # 限制cos范围[-1, 1]
    cos_half_theta = np.clip(cos_half_theta, -1, 1)
    
    half_theta = np.arccos(cos_half_theta)
    theta = 2 * half_theta
    
    # 面积
    A = (D**2 / 8) * (theta - np.sin(theta))
    
    # 湿周
    chi = D * theta / 2
    
    # 水力半径
    R = A / chi if chi > 0 else 0
    
    return h, A, chi, R, theta


def manning_Q_circular_from_filling(D, alpha, n, i):
    """
    根据充满度计算圆形管道流量
    
    参数：
        D: 管道直径 (m)
        alpha: 充满度
        n: 糙率系数
        i: 底坡
    
    返回：
        Q: 流量 (m³/s)
    """
    h, A, chi, R, theta = circular_geometry_from_filling(D, alpha)
    Q = (A / n) * (R ** (2/3)) * (i ** 0.5)
    return Q


def solve_normal_filling_circular(Q, D, n, i, alpha_init=0.5, tol=1e-6, max_iter=100):
    """
    迭代求解圆形管道正常充满度
    
    参数：
        Q: 设计流量 (m³/s)
        D: 管道直径 (m)
        n: 糙率系数
        i: 底坡
        alpha_init: 初始充满度猜测值
        tol: 收敛容差
        max_iter: 最大迭代次数
    
    返回：
        alpha: 充满度
        iterations: 迭代次数
    """
    alpha = alpha_init
    
    # 确保初始值在合理范围
    alpha = np.clip(alpha, 0.01, 0.99)
    
    for iteration in range(max_iter):
        # 计算当前alpha对应的流量
        Q_calc = manning_Q_circular_from_filling(D, alpha, n, i)
        
        # 残差
        f = Q_calc - Q
        
        # 检查收敛
        if abs(f) < tol:
            return alpha, iteration + 1
        
        # 数值导数
        dalpha = 0.001
        alpha_plus = min(alpha + dalpha, 0.99)
        alpha_minus = max(alpha - dalpha, 0.01)
        Q_plus = manning_Q_circular_from_filling(D, alpha_plus, n, i)
        Q_minus = manning_Q_circular_from_filling(D, alpha_minus, n, i)
        df_dalpha = (Q_plus - Q_minus) / (alpha_plus - alpha_minus)
        
        # 牛顿迭代更新
        if abs(df_dalpha) < 1e-10:
            # 导数太小，改用简单搜索
            alpha = alpha + 0.01 * np.sign(f)
        else:
            alpha_new = alpha - f / df_dalpha
            # 限制在合理范围
            alpha = np.clip(alpha_new, 0.01, 0.99)
    
    print(f"警告：未在{max_iter}次迭代内收敛！")
    return alpha, max_iter


def main():
    """主函数：求解强化题63"""
    
    print("=" * 70)
    print("圆形管道非满流均匀流计算")
    print("题目：清华大学2018年真题改编（第63题）")
    print("=" * 70)
    
    # ========== 已知条件 ==========
    D = 1.0          # 管道直径 (m)
    i = 0.003        # 底坡
    n = 0.013        # 糙率
    Q = 0.8          # 设计流量 (m³/s)
    g = 9.81         # 重力加速度 (m/s²)
    
    print("\n【已知条件】")
    print(f"管道直径 D = {D} m")
    print(f"底坡 i = {i}")
    print(f"糙率 n = {n}（混凝土）")
    print(f"设计流量 Q = {Q} m³/s")
    
    # ========== (1) 求充满度α和正常水深h₀ ==========
    print("\n" + "=" * 70)
    print("(1) 求充满度α和正常水深h₀")
    print("=" * 70)
    
    alpha0, iterations = solve_normal_filling_circular(Q, D, n, i, alpha_init=0.5)
    
    # 计算几何要素
    h0, A0, chi0, R0, theta0 = circular_geometry_from_filling(D, alpha0)
    Q_verify = manning_Q_circular_from_filling(D, alpha0, n, i)
    
    print(f"\n迭代求解（牛顿法）：")
    print(f"  迭代次数：{iterations}")
    print(f"  充满度 α = h₀/D = {alpha0:.4f} = {alpha0*100:.2f}%")
    print(f"  正常水深 h₀ = {h0:.4f} m = {h0*1000:.1f} mm")
    print(f"  充满角 θ = {theta0:.4f} rad = {np.degrees(theta0):.2f}°")
    
    print(f"\n断面几何要素：")
    print(f"  过流面积 A = {A0:.4f} m²")
    print(f"  湿周 χ = {chi0:.4f} m")
    print(f"  水力半径 R = {R0:.4f} m")
    
    print(f"\n流量验证：Q = {Q_verify:.4f} m³/s（误差：{abs(Q_verify-Q)/Q*100:.4f}%）")
    
    # ========== (2) 求断面平均流速v ==========
    print("\n" + "=" * 70)
    print("(2) 求断面平均流速v")
    print("=" * 70)
    
    v = Q / A0
    print(f"\nv = Q/A = {Q:.3f}/{A0:.4f} = {v:.3f} m/s")
    
    # ========== (3) 满流情况对比 ==========
    print("\n" + "=" * 70)
    print("(3) 满流情况对比")
    print("=" * 70)
    
    # 满流（α=1.0）
    h_full = D
    A_full = np.pi * D**2 / 4
    chi_full = np.pi * D
    R_full = A_full / chi_full
    Q_full = (A_full / n) * (R_full ** (2/3)) * (i ** 0.5)
    v_full = Q_full / A_full
    
    print(f"\n满流情况（α=1.0）：")
    print(f"  水深 h = {h_full:.3f} m")
    print(f"  面积 A = {A_full:.4f} m²")
    print(f"  湿周 χ = {chi_full:.4f} m")
    print(f"  水力半径 R = {R_full:.4f} m")
    print(f"  流量 Q = {Q_full:.4f} m³/s")
    print(f"  流速 v = {v_full:.3f} m/s")
    
    print(f"\n对比分析：")
    print(f"  非满流（α={alpha0:.3f}）：Q = {Q:.3f} m³/s, v = {v:.3f} m/s")
    print(f"  满流（α=1.000）：    Q = {Q_full:.3f} m³/s, v = {v_full:.3f} m/s")
    print(f"  流量比：Q_非满/Q_满 = {Q/Q_full*100:.1f}%")
    print(f"  流速比：v_非满/v_满 = {v/v_full*100:.1f}%")
    
    # ========== (4) 最大输水能力（α≈0.938） ==========
    print("\n" + "=" * 70)
    print("(4) 最大输水能力分析")
    print("=" * 70)
    
    # 寻找最大输水能力对应的充满度
    alpha_range = np.linspace(0.1, 1.0, 200)
    Q_range = [manning_Q_circular_from_filling(D, a, n, i) for a in alpha_range]
    
    idx_max = np.argmax(Q_range)
    alpha_max = alpha_range[idx_max]
    Q_max = Q_range[idx_max]
    
    h_max, A_max, chi_max, R_max, theta_max = circular_geometry_from_filling(D, alpha_max)
    
    print(f"\n圆形管道的最大输水能力：")
    print(f"  最优充满度 α_max = {alpha_max:.4f} = {alpha_max*100:.2f}%")
    print(f"  对应水深 h_max = {h_max:.4f} m")
    print(f"  最大流量 Q_max = {Q_max:.4f} m³/s")
    print(f"  水力半径 R_max = {R_max:.4f} m")
    
    print(f"\n与满流对比：")
    print(f"  Q_max / Q_满流 = {Q_max/Q_full*100:.2f}%")
    print(f"  R_max / R_满流 = {R_max/R_full*100:.2f}%")
    
    print(f"\n结论：")
    print(f"  圆形管道在α≈0.94时达到最大输水能力，")
    print(f"  此时Q和R均大于满流！")
    
    # ========== 绘图1：断面形状 ==========
    print("\n" + "=" * 70)
    print("绘制图形")
    print("=" * 70)
    
    fig = plt.figure(figsize=(16, 5))
    
    # 子图1：断面形状
    ax1 = fig.add_subplot(131, aspect='equal')
    
    # 绘制管道轮廓
    circle = Circle((0, 0), D/2, fill=False, edgecolor='black', linewidth=2)
    ax1.add_patch(circle)
    
    # 绘制水体
    theta_water = np.linspace(-np.pi, -np.pi + theta0, 100)
    x_water = (D/2) * np.cos(theta_water)
    y_water = (D/2) * np.sin(theta_water)
    
    # 闭合水体区域
    x_water = np.append(x_water, x_water[0])
    y_water = np.append(y_water, y_water[0])
    
    ax1.fill(x_water, y_water, color='cyan', alpha=0.5, label='水体')
    
    # 水面线
    x_surface = [x_water[0], x_water[-2]]
    y_surface = [y_water[0], y_water[-2]]
    ax1.plot(x_surface, y_surface, 'b-', linewidth=2, label='水面')
    
    # 标注水深
    ax1.plot([0, 0], [-D/2, h0-D/2], 'r--', linewidth=1.5, label=f'h₀={h0:.3f}m')
    ax1.plot([-0.05, 0.05], [h0-D/2, h0-D/2], 'r-', linewidth=2)
    
    # 标注直径
    ax1.plot([0, 0], [-D/2, D/2], 'k--', alpha=0.3, linewidth=1)
    ax1.text(0.05, 0, f'D={D}m', fontsize=10)
    
    ax1.set_xlim(-D, D)
    ax1.set_ylim(-D, D)
    ax1.set_xlabel('x (m)', fontsize=11)
    ax1.set_ylabel('y (m)', fontsize=11)
    ax1.set_title(f'圆形管道断面（α={alpha0:.3f}）', fontsize=12)
    ax1.legend(fontsize=9, loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # 子图2：Q-α曲线
    ax2 = fig.add_subplot(132)
    
    ax2.plot(alpha_range, Q_range, 'b-', linewidth=2)
    ax2.plot(alpha0, Q, 'ro', markersize=10, label=f'设计点：α={alpha0:.3f}')
    ax2.plot(alpha_max, Q_max, 'g^', markersize=10, label=f'最大点：α={alpha_max:.3f}')
    ax2.plot(1.0, Q_full, 'ks', markersize=8, label=f'满流：α=1.0')
    
    ax2.axhline(y=Q, color='red', linestyle='--', alpha=0.3)
    ax2.axvline(x=alpha0, color='red', linestyle='--', alpha=0.3)
    
    ax2.set_xlabel('充满度 α = h/D', fontsize=11)
    ax2.set_ylabel('流量 Q (m³/s)', fontsize=11)
    ax2.set_title(f'Q-α关系曲线（D={D}m, n={n}, i={i}）', fontsize=12)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 子图3：R-α曲线
    ax3 = fig.add_subplot(133)
    
    R_range = []
    for a in alpha_range:
        _, _, _, R, _ = circular_geometry_from_filling(D, a)
        R_range.append(R)
    
    ax3.plot(alpha_range, R_range, 'g-', linewidth=2)
    ax3.plot(alpha0, R0, 'ro', markersize=10, label=f'设计点：R={R0:.4f}m')
    ax3.plot(1.0, R_full, 'ks', markersize=8, label=f'满流：R={R_full:.4f}m')
    ax3.axhline(y=R_full, color='gray', linestyle='--', alpha=0.3, label='满流R')
    
    ax3.set_xlabel('充满度 α = h/D', fontsize=11)
    ax3.set_ylabel('水力半径 R (m)', fontsize=11)
    ax3.set_title('R-α关系曲线', fontsize=12)
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    output_file = 'uniform_flow_circular.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{output_file}")
    
    plt.show()
    
    # ========== 总结 ==========
    print("\n" + "=" * 70)
    print("【总结】")
    print("=" * 70)
    print(f"1. 充满度：α = {alpha0:.3f} = {alpha0*100:.1f}%")
    print(f"2. 正常水深：h₀ = {h0:.3f} m")
    print(f"3. 断面流速：v = {v:.2f} m/s")
    print(f"4. 非满流占满流流量的{Q/Q_full*100:.1f}%")
    print(f"5. 最大输水能力出现在α≈{alpha_max:.3f}，Q_max={Q_max:.3f} m³/s")
    print(f"6. 满流时R={R_full:.4f}m，最大R={R_max:.4f}m（大{(R_max/R_full-1)*100:.1f}%）")
    print("=" * 70)


def design_table():
    """
    生成圆形管道设计查算表
    """
    print("\n" + "=" * 70)
    print("【扩展】圆形管道设计查算表")
    print("=" * 70)
    
    D = 1.0
    n = 0.013
    i = 0.003
    
    print(f"\n管道参数：D={D}m, n={n}, i={i}")
    print(f"\n{'α':<8} {'h(m)':<8} {'A(m²)':<10} {'R(m)':<10} {'Q(m³/s)':<10} {'v(m/s)':<10}")
    print("-" * 70)
    
    for alpha in np.linspace(0.1, 1.0, 19):
        h, A, chi, R, theta = circular_geometry_from_filling(D, alpha)
        Q = manning_Q_circular_from_filling(D, alpha, n, i)
        v = Q / A
        print(f"{alpha:<8.2f} {h:<8.4f} {A:<10.4f} {R:<10.4f} {Q:<10.4f} {v:<10.3f}")
    
    print("\n说明：")
    print("  - α在0.93-0.95时Q达到最大")
    print("  - 设计充满度一般取0.65-0.75")
    print("  - 满流（α=1.0）虽然A最大，但R不是最大")


def exercise():
    """练习题"""
    print("\n" + "=" * 70)
    print("【练习题】")
    print("=" * 70)
    print("\n1. 若流量Q增加到1.0 m³/s，充满度α会如何变化？")
    print("2. 若底坡i改为0.005（加陡），α会如何变化？")
    print("3. 为什么圆形管道的最大输水能力不在满流时？")
    print("4. 设计充满度为何选择0.7而非0.94（最大Q处）？")
    print("   提示：考虑水位波动、通气、管道压力等因素")
    print("=" * 70)


if __name__ == "__main__":
    main()
    design_table()
    exercise()
