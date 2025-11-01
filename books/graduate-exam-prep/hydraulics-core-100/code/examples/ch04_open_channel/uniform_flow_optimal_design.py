#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
渠道均匀流水力最优断面设计
============================

题目：武汉大学2019年真题改编（第65题）
某灌溉渠道需输送流量Q=15 m³/s，渠道底坡i=0.0008，
采用梯形断面，边坡系数m=1.5，糙率n=0.020

求解：
1. 按水力最优断面设计底宽b和正常水深h₀
2. 计算流速v和弗劳德数Fr
3. 检验防冲（v≤1.5 m/s）和防淤（v≥0.6 m/s）要求
4. 绘制Q-h关系曲线

作者：CHS-Books
日期：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy.optimize import fsolve

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


def optimal_trapezoid_base(h, m):
    """
    计算梯形断面水力最优底宽
    
    水力最优条件：b = 2h(√(1+m²) - m)
    
    参数：
        h: 水深 (m)
        m: 边坡系数
    
    返回：
        b: 最优底宽 (m)
    """
    return 2 * h * (np.sqrt(1 + m**2) - m)


def optimal_trapezoid_R(h):
    """
    水力最优梯形断面的水力半径
    
    所有水力最优梯形断面都有：R = h/2
    
    参数：
        h: 水深 (m)
    
    返回：
        R: 水力半径 (m)
    """
    return h / 2


def trapezoid_geometry(b, h, m):
    """
    梯形断面几何要素
    
    参数：
        b: 底宽 (m)
        h: 水深 (m)
        m: 边坡系数
    
    返回：
        A, chi, R, B: 面积、湿周、水力半径、水面宽度
    """
    A = (b + m * h) * h
    chi = b + 2 * h * np.sqrt(1 + m**2)
    R = A / chi
    B = b + 2 * m * h
    return A, chi, R, B


def manning_Q(A, R, n, i):
    """
    曼宁公式计算流量
    
    参数：
        A: 过流面积 (m²)
        R: 水力半径 (m)
        n: 糙率系数
        i: 底坡
    
    返回：
        Q: 流量 (m³/s)
    """
    return (A / n) * (R ** (2/3)) * (i ** 0.5)


def solve_optimal_depth(Q, m, n, i):
    """
    求解水力最优断面的正常水深
    
    对于水力最优梯形断面：
    - b = 2h(√(1+m²) - m)
    - A = (b + mh)h = 2h²(√(1+m²) - m) + mh² = h²(2√(1+m²) - m)
    - R = h/2
    - Q = (A/n)·R^(2/3)·√i
    
    简化为关于h的方程：
    Q = [h²(2√(1+m²) - m)/n]·(h/2)^(2/3)·√i
    
    参数：
        Q: 设计流量 (m³/s)
        m: 边坡系数
        n: 糙率系数
        i: 底坡
    
    返回：
        h: 正常水深 (m)
    """
    # 系数
    c1 = 2 * np.sqrt(1 + m**2) - m  # A = c1·h²
    c2 = 0.5  # R = c2·h
    
    # Q = (c1·h²/n)·(c2·h)^(2/3)·√i
    # Q = (c1/n)·c2^(2/3)·h^(8/3)·√i
    
    coeff = (c1 / n) * (c2 ** (2/3)) * np.sqrt(i)
    
    # h^(8/3) = Q / coeff
    h = (Q / coeff) ** (3/8)
    
    return h


def froude_number(v, A, B, g=9.81):
    """
    计算弗劳德数
    
    Fr = v / √(g·hm)，其中 hm = A/B
    
    参数：
        v: 断面平均流速 (m/s)
        A: 过流面积 (m²)
        B: 水面宽度 (m)
        g: 重力加速度 (m/s²)
    
    返回：
        Fr: 弗劳德数
    """
    hm = A / B
    return v / np.sqrt(g * hm)


def main():
    """主函数：求解综合题65"""
    
    print("=" * 80)
    print("渠道均匀流水力最优断面设计")
    print("题目：武汉大学2019年真题改编（第65题）")
    print("=" * 80)
    
    # ========== 已知条件 ==========
    Q = 15.0         # 设计流量 (m³/s)
    i = 0.0008       # 底坡
    m = 1.5          # 边坡系数
    n = 0.020        # 糙率
    v_max = 1.5      # 防冲流速限制 (m/s)
    v_min = 0.6      # 防淤流速限制 (m/s)
    g = 9.81         # 重力加速度 (m/s²)
    
    print("\n【已知条件】")
    print(f"设计流量：Q = {Q} m³/s")
    print(f"底坡：i = {i}")
    print(f"边坡系数：m = {m}（边坡{m}:1）")
    print(f"糙率：n = {n}")
    print(f"防冲流速要求：v ≤ {v_max} m/s")
    print(f"防淤流速要求：v ≥ {v_min} m/s")
    
    # ========== (1) 水力最优断面设计 ==========
    print("\n" + "=" * 80)
    print("(1) 水力最优断面设计")
    print("=" * 80)
    
    print(f"\n水力最优条件（梯形，m={m}）：")
    print(f"  b = 2h(√(1+m²) - m)")
    print(f"    = 2h(√(1+{m}²) - {m})")
    print(f"    = 2h(√{1+m**2:.3f} - {m})")
    print(f"    = 2h({np.sqrt(1+m**2):.4f} - {m})")
    print(f"    = {2*(np.sqrt(1+m**2)-m):.4f}·h")
    print(f"  R = h/2（所有水力最优梯形断面的共同特性）")
    
    # 求解正常水深
    h0 = solve_optimal_depth(Q, m, n, i)
    
    # 计算最优底宽
    b0 = optimal_trapezoid_base(h0, m)
    
    # 验证几何要素
    A0, chi0, R0, B0 = trapezoid_geometry(b0, h0, m)
    Q_verify = manning_Q(A0, R0, n, i)
    
    print(f"\n求解结果：")
    print(f"  正常水深：h₀ = {h0:.3f} m")
    print(f"  底宽：b = {b0:.3f} m")
    
    print(f"\n验证计算：")
    print(f"  过流面积：A = {A0:.3f} m²")
    print(f"  湿周：χ = {chi0:.3f} m")
    print(f"  水力半径：R = {R0:.3f} m")
    print(f"  水面宽度：B = {B0:.3f} m")
    print(f"  流量：Q = {Q_verify:.3f} m³/s（误差{abs(Q_verify-Q)/Q*100:.4f}%）")
    
    # 理论验证
    R_theory = h0 / 2
    print(f"\n理论验证：R = h/2 = {h0:.3f}/2 = {R_theory:.3f} m")
    print(f"  实际计算：R = {R0:.3f} m")
    print(f"  误差：{abs(R0-R_theory)/R_theory*100:.4f}%（数值误差）")
    
    # ========== (2) 流速和弗劳德数 ==========
    print("\n" + "=" * 80)
    print("(2) 流速和弗劳德数")
    print("=" * 80)
    
    v = Q / A0
    Fr = froude_number(v, A0, B0, g)
    hm = A0 / B0
    
    print(f"\n流速：")
    print(f"  v = Q/A = {Q:.2f}/{A0:.3f} = {v:.3f} m/s")
    
    print(f"\n弗劳德数：")
    print(f"  水力深度：hm = A/B = {A0:.3f}/{B0:.3f} = {hm:.3f} m")
    print(f"  Fr = v/√(g·hm) = {v:.3f}/√({g}×{hm:.3f})")
    print(f"     = {v:.3f}/{np.sqrt(g*hm):.3f}")
    print(f"     = {Fr:.3f}")
    
    if Fr < 1:
        flow_state = "缓流（亚临界流）"
        stability = "稳定"
    elif Fr > 1:
        flow_state = "急流（超临界流）"
        stability = "不稳定，易产生水跃"
    else:
        flow_state = "临界流"
        stability = "极不稳定，避免设计"
    
    print(f"\n流态判别：")
    print(f"  Fr = {Fr:.3f} {'<' if Fr < 1 else ('>' if Fr > 1 else '=')} 1")
    print(f"  流态：{flow_state}")
    print(f"  稳定性：{stability}")
    
    # ========== (3) 流速要求检验 ==========
    print("\n" + "=" * 80)
    print("(3) 流速要求检验")
    print("=" * 80)
    
    print(f"\n设计要求：")
    print(f"  防淤：v ≥ {v_min} m/s")
    print(f"  防冲：v ≤ {v_max} m/s")
    print(f"  允许范围：{v_min} ≤ v ≤ {v_max} m/s")
    
    print(f"\n实际流速：v = {v:.3f} m/s")
    
    check_min = v >= v_min
    check_max = v <= v_max
    
    print(f"\n检验结果：")
    print(f"  防淤检验：v = {v:.3f} {'≥' if check_min else '<'} {v_min} m/s  {'✓ 满足' if check_min else '✗ 不满足'}")
    print(f"  防冲检验：v = {v:.3f} {'≤' if check_max else '>'} {v_max} m/s  {'✓ 满足' if check_max else '✗ 不满足'}")
    
    if check_min and check_max:
        print(f"\n结论：✓ 设计合理！流速在允许范围内。")
        print(f"  安全裕度：")
        print(f"    距防淤限：{(v-v_min)/v_min*100:.1f}%")
        print(f"    距防冲限：{(v_max-v)/v_max*100:.1f}%")
    else:
        print(f"\n结论：✗ 设计不满足要求，需要调整！")
        
        if not check_min:
            print(f"\n调整方案（增大流速）：")
            print(f"  1. 增大底坡i（不推荐，地形限制）")
            print(f"  2. 减小断面面积A（减小b或h，但会偏离最优断面）")
            print(f"  3. 减小糙率n（选用更光滑的衬砌材料）")
        
        if not check_max:
            print(f"\n调整方案（减小流速）：")
            A_required = Q / v_max
            print(f"  所需过流面积：A ≥ Q/v_max = {Q}/{v_max} = {A_required:.3f} m²")
            print(f"  当前面积：A = {A0:.3f} m²")
            print(f"  需增大：ΔA = {A_required - A0:.3f} m²")
            
            # 保持h不变，增大b
            b_new = A_required / h0 - m * h0
            print(f"\n  方案1：增大底宽（保持h={h0:.2f}m，偏离最优）")
            print(f"         b_新 = {b_new:.3f} m（增大{b_new-b0:.3f}m）")
            
            # 保持b不变，增大h
            # A = (b + mh)h → mh² + bh - A = 0
            h_new = (-b0 + np.sqrt(b0**2 + 4 * m * A_required)) / (2 * m)
            print(f"  方案2：增大水深（保持b={b0:.2f}m，偏离最优）")
            print(f"         h_新 = {h_new:.3f} m（增大{h_new-h0:.3f}m）")
            
            # 按最优断面放大
            scale = np.sqrt(A_required / A0)
            b_new_opt = b0 * scale
            h_new_opt = h0 * scale
            print(f"  方案3：按比例放大（保持最优断面形状）")
            print(f"         缩放系数 = √(A_新/A_旧) = {scale:.3f}")
            print(f"         b_新 = {b_new_opt:.3f} m, h_新 = {h_new_opt:.3f} m")
    
    # ========== (4) 绘制Q-h关系曲线 ==========
    print("\n" + "=" * 80)
    print("(4) 绘制Q-h关系曲线")
    print("=" * 80)
    
    fig = plt.figure(figsize=(18, 10))
    
    # 子图1：断面形状
    ax1 = fig.add_subplot(231)
    
    # 梯形顶点坐标
    x_trap = [0 - m*h0, 0, b0, b0 + m*h0, 0 - m*h0]
    y_trap = [h0, 0, 0, h0, h0]
    
    ax1.fill(x_trap, y_trap, color='cyan', alpha=0.5, edgecolor='black', linewidth=2, label='水体')
    ax1.plot([0-m*h0, 0, b0, b0+m*h0], [h0, 0, 0, h0], 'k-', linewidth=2)
    
    # 标注
    ax1.plot([0, b0], [-0.3, -0.3], 'r-', linewidth=2)
    ax1.plot([0, 0], [-0.3, -0.35], 'r-', linewidth=2)
    ax1.plot([b0, b0], [-0.3, -0.35], 'r-', linewidth=2)
    ax1.text(b0/2, -0.5, f'b={b0:.2f}m', ha='center', fontsize=10, color='red')
    
    ax1.plot([-0.3, -0.3], [0, h0], 'b-', linewidth=2)
    ax1.plot([-0.3, -0.35], [0, 0], 'b-', linewidth=2)
    ax1.plot([-0.3, -0.35], [h0, h0], 'b-', linewidth=2)
    ax1.text(-0.6, h0/2, f'h={h0:.2f}m', ha='center', fontsize=10, color='blue', rotation=90)
    
    ax1.text(b0+m*h0+0.3, h0/2, f'm={m}', fontsize=10, color='green')
    
    ax1.set_xlim(-2, b0+3)
    ax1.set_ylim(-1, h0+1)
    ax1.set_xlabel('宽度 (m)', fontsize=11)
    ax1.set_ylabel('高度 (m)', fontsize=11)
    ax1.set_title('水力最优断面形状', fontsize=12)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    
    # 子图2：Q-h曲线（固定b=b0）
    ax2 = fig.add_subplot(232)
    
    h_range = np.linspace(0.5, 4.0, 100)
    Q_range = []
    
    for h in h_range:
        A, chi, R, B = trapezoid_geometry(b0, h, m)
        Q_h = manning_Q(A, R, n, i)
        Q_range.append(Q_h)
    
    ax2.plot(h_range, Q_range, 'b-', linewidth=2)
    ax2.plot(h0, Q, 'ro', markersize=10, label=f'设计点：h={h0:.2f}m')
    ax2.axhline(y=Q, color='gray', linestyle='--', alpha=0.5)
    ax2.axvline(x=h0, color='gray', linestyle='--', alpha=0.5)
    
    ax2.set_xlabel('水深 h (m)', fontsize=11)
    ax2.set_ylabel('流量 Q (m³/s)', fontsize=11)
    ax2.set_title(f'Q-h关系（b={b0:.2f}m固定）', fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 子图3：v-h曲线
    ax3 = fig.add_subplot(233)
    
    v_range = []
    for h in h_range:
        A, chi, R, B = trapezoid_geometry(b0, h, m)
        Q_h = manning_Q(A, R, n, i)
        v_h = Q_h / A
        v_range.append(v_h)
    
    ax3.plot(h_range, v_range, 'g-', linewidth=2)
    ax3.plot(h0, v, 'ro', markersize=10, label=f'设计点：v={v:.2f}m/s')
    ax3.axhline(y=v_max, color='red', linestyle='--', linewidth=1.5, label=f'防冲限v_max={v_max}m/s')
    ax3.axhline(y=v_min, color='orange', linestyle='--', linewidth=1.5, label=f'防淤限v_min={v_min}m/s')
    ax3.axvline(x=h0, color='gray', linestyle='--', alpha=0.5)
    
    ax3.set_xlabel('水深 h (m)', fontsize=11)
    ax3.set_ylabel('流速 v (m/s)', fontsize=11)
    ax3.set_title('v-h关系', fontsize=12)
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # 子图4：Fr-h曲线
    ax4 = fig.add_subplot(234)
    
    Fr_range = []
    for h in h_range:
        A, chi, R, B = trapezoid_geometry(b0, h, m)
        Q_h = manning_Q(A, R, n, i)
        v_h = Q_h / A
        Fr_h = froude_number(v_h, A, B, g)
        Fr_range.append(Fr_h)
    
    ax4.plot(h_range, Fr_range, 'm-', linewidth=2)
    ax4.plot(h0, Fr, 'ro', markersize=10, label=f'设计点：Fr={Fr:.2f}')
    ax4.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5, label='临界流Fr=1')
    ax4.axvline(x=h0, color='gray', linestyle='--', alpha=0.5)
    
    ax4.set_xlabel('水深 h (m)', fontsize=11)
    ax4.set_ylabel('弗劳德数 Fr', fontsize=11)
    ax4.set_title('Fr-h关系', fontsize=12)
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    # 子图5：R-h曲线（对比最优vs非最优）
    ax5 = fig.add_subplot(235)
    
    R_optimal = []
    R_nonoptimal = []
    h_range2 = np.linspace(0.5, 4.0, 100)
    
    for h in h_range2:
        # 最优断面
        b_opt = optimal_trapezoid_base(h, m)
        A_opt, chi_opt, R_opt, B_opt = trapezoid_geometry(b_opt, h, m)
        R_optimal.append(R_opt)
        
        # 非最优断面（固定b=b0）
        A_non, chi_non, R_non, B_non = trapezoid_geometry(b0, h, m)
        R_nonoptimal.append(R_non)
    
    ax5.plot(h_range2, R_optimal, 'b-', linewidth=2, label='最优断面（b随h变化）')
    ax5.plot(h_range2, R_nonoptimal, 'r--', linewidth=2, label=f'固定b={b0:.2f}m')
    ax5.plot(h0, R0, 'ro', markersize=10, label=f'设计点：R={R0:.3f}m')
    
    # 理论线 R=h/2
    R_theory_line = h_range2 / 2
    ax5.plot(h_range2, R_theory_line, 'k:', linewidth=1.5, label='理论R=h/2', alpha=0.5)
    
    ax5.set_xlabel('水深 h (m)', fontsize=11)
    ax5.set_ylabel('水力半径 R (m)', fontsize=11)
    ax5.set_title('水力半径对比', fontsize=12)
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3)
    
    # 子图6：A-b-h等高线图
    ax6 = fig.add_subplot(236)
    
    b_range_grid = np.linspace(0.5, 5.0, 50)
    h_range_grid = np.linspace(0.5, 4.0, 50)
    B_grid, H_grid = np.meshgrid(b_range_grid, h_range_grid)
    
    A_grid = (B_grid + m * H_grid) * H_grid
    
    contour = ax6.contourf(B_grid, H_grid, A_grid, levels=20, cmap='viridis', alpha=0.7)
    ax6.contour(B_grid, H_grid, A_grid, levels=10, colors='black', linewidths=0.5, alpha=0.3)
    
    # 标注设计点
    ax6.plot(b0, h0, 'ro', markersize=12, label=f'设计点：A={A0:.2f}m²', zorder=5)
    
    # 最优断面曲线 b = 2h(√(1+m²) - m)
    h_opt_line = np.linspace(0.5, 4.0, 50)
    b_opt_line = [optimal_trapezoid_base(h, m) for h in h_opt_line]
    ax6.plot(b_opt_line, h_opt_line, 'r--', linewidth=2, label='最优断面线', zorder=4)
    
    ax6.set_xlabel('底宽 b (m)', fontsize=11)
    ax6.set_ylabel('水深 h (m)', fontsize=11)
    ax6.set_title('过流面积A等高线图', fontsize=12)
    ax6.legend(fontsize=9)
    ax6.grid(True, alpha=0.3)
    
    cbar = plt.colorbar(contour, ax=ax6)
    cbar.set_label('面积 A (m²)', fontsize=10)
    
    plt.tight_layout()
    
    # 保存图片
    output_file = 'uniform_flow_optimal_design.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{output_file}")
    
    plt.show()
    
    # ========== 总结 ==========
    print("\n" + "=" * 80)
    print("【总结】")
    print("=" * 80)
    print(f"1. 水力最优断面：h₀={h0:.2f}m, b={b0:.2f}m, R={R0:.3f}m≈h/2")
    print(f"2. 流速：v={v:.2f}m/s（{flow_state}，Fr={Fr:.2f}）")
    print(f"3. 防冲防淤：{'✓ 满足' if (check_min and check_max) else '✗ 不满足'}（{v_min}≤v≤{v_max}）")
    print(f"4. 水力最优断面使过流面积A最小，节省土方开挖")
    print(f"5. 所有最优梯形断面都满足R=h/2，无论边坡系数m为多少")
    print("=" * 80)


def compare_different_m():
    """
    对比不同边坡系数m的最优断面
    """
    print("\n" + "=" * 80)
    print("【扩展分析】不同边坡系数m的最优断面对比")
    print("=" * 80)
    
    Q = 15.0
    n = 0.020
    i = 0.0008
    
    m_values = [1.0, 1.5, 2.0, 2.5]
    
    print(f"\n设计参数：Q={Q}m³/s, n={n}, i={i}")
    print(f"\n{'m':<6} {'b(m)':<8} {'h(m)':<8} {'A(m²)':<8} {'R(m)':<8} {'v(m/s)':<8}")
    print("-" * 60)
    
    for m in m_values:
        h = solve_optimal_depth(Q, m, n, i)
        b = optimal_trapezoid_base(h, m)
        A, chi, R, B = trapezoid_geometry(b, h, m)
        v = Q / A
        print(f"{m:<6.1f} {b:<8.3f} {h:<8.3f} {A:<8.3f} {R:<8.3f} {v:<8.3f}")
    
    print("\n结论：")
    print("  - m越大（边坡越缓），最优底宽b越小")
    print("  - 但水深h增大，总体面积A也增大")
    print("  - 所有最优断面R=h/2保持不变")
    print("  - 边坡选择应综合考虑土壤稳定性和经济性")


def exercise():
    """练习题"""
    print("\n" + "=" * 80)
    print("【练习题】")
    print("=" * 80)
    print("\n1. 若流量Q增加到20 m³/s，水力最优断面的h和b如何变化？")
    print("2. 若底坡i改为0.001（加陡），h和b如何变化？")
    print("3. 为什么矩形断面（m=0）的最优条件是b=2h？")
    print("   提示：代入m=0到梯形公式")
    print("4. 为什么实际工程中的断面往往不是严格的水力最优？")
    print("   提示：考虑施工、维护、安全等因素")
    print("5. 绘制m-b-h关系图（固定Q=15 m³/s）")
    print("=" * 80)


if __name__ == "__main__":
    main()
    compare_different_m()
    exercise()
