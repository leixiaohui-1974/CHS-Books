#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
梯形渠道均匀流计算
====================

题目：武汉大学2020年真题改编（第62题）
梯形断面土质渠道，底宽b=4m，边坡系数m=1.5，底坡i=0.0005，糙率n=0.025，流量Q=20 m³/s

求解：
1. 正常水深h₀
2. 断面平均流速v
3. 谢才系数C
4. 防冲流速要求（v≤1.2 m/s）

作者：CHS-Books
日期：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from mpl_toolkits.mplot3d import Axes3D

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


def trapezoidal_geometry(b, h, m):
    """
    计算梯形断面几何要素
    
    参数：
        b: 底宽 (m)
        h: 水深 (m)
        m: 边坡系数（水平:垂直）
    
    返回：
        A: 过流面积 (m²)
        chi: 湿周 (m)
        R: 水力半径 (m)
        B: 水面宽度 (m)
    """
    A = (b + m * h) * h  # 面积
    chi = b + 2 * h * np.sqrt(1 + m**2)  # 湿周
    R = A / chi  # 水力半径
    B = b + 2 * m * h  # 水面宽度
    return A, chi, R, B


def manning_Q_trapezoidal(b, h, m, n, i):
    """
    梯形断面曼宁公式计算流量
    
    参数：
        b: 底宽 (m)
        h: 水深 (m)
        m: 边坡系数
        n: 糙率系数
        i: 底坡
    
    返回：
        Q: 流量 (m³/s)
    """
    A, chi, R, B = trapezoidal_geometry(b, h, m)
    Q = (A / n) * (R ** (2/3)) * (i ** 0.5)
    return Q


def solve_normal_depth_trapezoidal(Q, b, m, n, i, h_init=1.0, tol=1e-6, max_iter=100):
    """
    迭代求解梯形断面正常水深
    
    参数：
        Q: 设计流量 (m³/s)
        b: 底宽 (m)
        m: 边坡系数
        n: 糙率系数
        i: 底坡
        h_init: 初始水深猜测值 (m)
        tol: 收敛容差
        max_iter: 最大迭代次数
    
    返回：
        h: 正常水深 (m)
        iterations: 迭代次数
    """
    h = h_init
    
    for iteration in range(max_iter):
        # 计算当前h对应的流量
        Q_calc = manning_Q_trapezoidal(b, h, m, n, i)
        
        # 残差
        f = Q_calc - Q
        
        # 检查收敛
        if abs(f) < tol:
            return h, iteration + 1
        
        # 数值导数
        dh = 0.001
        Q_plus = manning_Q_trapezoidal(b, h + dh, m, n, i)
        Q_minus = manning_Q_trapezoidal(b, h - dh, m, n, i)
        df_dh = (Q_plus - Q_minus) / (2 * dh)
        
        # 牛顿迭代更新
        if abs(df_dh) < 1e-10:
            h = h + 0.1 * np.sign(f)
        else:
            h_new = h - f / df_dh
            if h_new < 0.1:
                h = 0.1
            elif h_new > 10 * h:
                h = h * 2
            else:
                h = h_new
    
    print(f"警告：未在{max_iter}次迭代内收敛！")
    return h, max_iter


def chezy_coefficient(R, n):
    """
    计算谢才系数C（曼宁公式）
    
    C = (1/n) * R^(1/6)
    
    参数：
        R: 水力半径 (m)
        n: 糙率系数
    
    返回：
        C: 谢才系数 (m^(1/2)/s)
    """
    return (1 / n) * (R ** (1/6))


def froude_number(v, A, B, g=9.81):
    """
    计算弗劳德数
    
    Fr = v / sqrt(g*hm)，其中 hm = A/B 为水力深度
    
    参数：
        v: 断面平均流速 (m/s)
        A: 过流面积 (m²)
        B: 水面宽度 (m)
        g: 重力加速度 (m/s²)
    
    返回：
        Fr: 弗劳德数
        hm: 水力深度 (m)
    """
    hm = A / B  # 水力深度
    Fr = v / np.sqrt(g * hm)
    return Fr, hm


def main():
    """主函数：求解基础题62"""
    
    print("=" * 70)
    print("梯形渠道均匀流计算")
    print("题目：武汉大学2020年真题改编（第62题）")
    print("=" * 70)
    
    # ========== 已知条件 ==========
    b = 4.0          # 底宽 (m)
    m = 1.5          # 边坡系数
    i = 0.0005       # 底坡
    n = 0.025        # 糙率
    Q = 20.0         # 设计流量 (m³/s)
    g = 9.81         # 重力加速度 (m/s²)
    v_max = 1.2      # 防冲流速限制 (m/s)
    
    print("\n【已知条件】")
    print(f"底宽 b = {b} m")
    print(f"边坡系数 m = {m}（边坡为{m}:1）")
    print(f"底坡 i = {i}")
    print(f"糙率 n = {n}")
    print(f"设计流量 Q = {Q} m³/s")
    print(f"防冲流速要求 v ≤ {v_max} m/s")
    
    # ========== (1) 求正常水深h₀ ==========
    print("\n" + "=" * 70)
    print("(1) 求正常水深h₀")
    print("=" * 70)
    
    h0, iterations = solve_normal_depth_trapezoidal(Q, b, m, n, i, h_init=2.0)
    
    # 计算几何要素
    A0, chi0, R0, B0 = trapezoidal_geometry(b, h0, m)
    Q_verify = manning_Q_trapezoidal(b, h0, m, n, i)
    
    print(f"\n迭代求解（牛顿法）：")
    print(f"  迭代次数：{iterations}")
    print(f"  正常水深 h₀ = {h0:.3f} m")
    print(f"\n断面几何要素：")
    print(f"  过流面积 A = {A0:.3f} m²")
    print(f"  湿周 χ = {chi0:.3f} m")
    print(f"  水力半径 R = {R0:.3f} m")
    print(f"  水面宽度 B = {B0:.3f} m")
    print(f"\n流量验证：Q = {Q_verify:.3f} m³/s（误差：{abs(Q_verify-Q)/Q*100:.4f}%）")
    
    # ========== (2) 求断面平均流速v ==========
    print("\n" + "=" * 70)
    print("(2) 求断面平均流速v")
    print("=" * 70)
    
    v = Q / A0
    print(f"\nv = Q/A = {Q:.2f}/{A0:.3f} = {v:.3f} m/s")
    
    # 计算弗劳德数
    Fr, hm = froude_number(v, A0, B0, g)
    print(f"\n弗劳德数：")
    print(f"  水力深度 hm = A/B = {A0:.3f}/{B0:.3f} = {hm:.3f} m")
    print(f"  Fr = v/√(g·hm) = {v:.3f}/√({g}×{hm:.3f}) = {Fr:.3f}")
    
    if Fr < 1:
        flow_state = "缓流（亚临界流）"
    elif Fr > 1:
        flow_state = "急流（超临界流）"
    else:
        flow_state = "临界流"
    
    print(f"  流态：{flow_state}")
    
    # ========== (3) 求谢才系数C ==========
    print("\n" + "=" * 70)
    print("(3) 求谢才系数C")
    print("=" * 70)
    
    C = chezy_coefficient(R0, n)
    print(f"\n谢才系数（曼宁公式）：")
    print(f"  C = (1/n) · R^(1/6)")
    print(f"    = (1/{n}) × {R0:.3f}^(1/6)")
    print(f"    = {C:.3f} m^(1/2)/s")
    
    # 验证谢才公式：v = C√(Ri)
    v_chezy = C * np.sqrt(R0 * i)
    print(f"\n验证谢才公式：")
    print(f"  v = C√(Ri) = {C:.3f} × √({R0:.3f}×{i})")
    print(f"    = {v_chezy:.3f} m/s")
    print(f"  与v={v:.3f} m/s 对比，误差{abs(v_chezy-v)/v*100:.2f}%")
    
    # ========== (4) 防冲流速检验 ==========
    print("\n" + "=" * 70)
    print("(4) 防冲流速检验")
    print("=" * 70)
    
    print(f"\n防冲流速要求：v ≤ {v_max} m/s")
    print(f"实际流速：v = {v:.3f} m/s")
    
    if v <= v_max:
        print(f"\n✓ 满足防冲要求！（v = {v:.3f} m/s < {v_max} m/s）")
        print(f"  安全裕度：{(v_max - v)/v_max * 100:.1f}%")
    else:
        print(f"\n✗ 不满足防冲要求！（v = {v:.3f} m/s > {v_max} m/s）")
        print(f"  超标：{(v - v_max)/v_max * 100:.1f}%")
        
        # 计算所需断面面积
        A_required = Q / v_max
        print(f"\n调整方案：")
        print(f"  所需过流面积：A ≥ Q/v_max = {Q}/{v_max} = {A_required:.3f} m²")
        print(f"  当前面积：A = {A0:.3f} m²")
        print(f"  需增加：ΔA = {A_required - A0:.3f} m²")
        
        # 方案1：增大底宽b（保持水深h₀）
        # A = (b + mh)h → b = A/h - mh
        b_new = A_required / h0 - m * h0
        print(f"\n  方案1：增大底宽（保持h={h0:.2f}m）")
        print(f"         b_新 = {b_new:.3f} m（增加{b_new-b:.3f}m）")
        
        # 方案2：增大水深h（保持底宽b）
        # A = (b + mh)h → mh² + bh - A = 0
        # h = [-b + sqrt(b² + 4mA)] / (2m)
        h_new = (-b + np.sqrt(b**2 + 4 * m * A_required)) / (2 * m)
        print(f"  方案2：增大水深（保持b={b:.2f}m）")
        print(f"         h_新 = {h_new:.3f} m（增加{h_new-h0:.3f}m）")
    
    # ========== 绘图1：断面形状 ==========
    print("\n" + "=" * 70)
    print("绘制断面形状图")
    print("=" * 70)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 左图：断面形状
    y_bottom = np.array([0, b, b])
    z_bottom = np.array([0, 0, 0])
    
    # 水深h₀时的水面
    y_water = np.array([0 - m*h0, 0, b, b + m*h0])
    z_water = np.array([h0, 0, 0, h0])
    
    # 绘制渠道断面
    ax1.plot(y_bottom, z_bottom, 'k-', linewidth=2, label='渠底')
    ax1.plot([0-m*h0, 0], [h0, 0], 'k-', linewidth=2, label='边坡')
    ax1.plot([b, b+m*h0], [0, h0], 'k-', linewidth=2)
    
    # 填充水体
    y_fill = [0-m*h0, 0, b, b+m*h0, 0-m*h0]
    z_fill = [h0, 0, 0, h0, h0]
    ax1.fill(y_fill, z_fill, color='cyan', alpha=0.4, label='水体')
    
    # 标注尺寸
    ax1.annotate('', xy=(0, -0.2), xytext=(b, -0.2),
                arrowprops=dict(arrowstyle='<->', color='red'))
    ax1.text(b/2, -0.4, f'b={b}m', ha='center', fontsize=10, color='red')
    
    ax1.annotate('', xy=(-0.3, 0), xytext=(-0.3, h0),
                arrowprops=dict(arrowstyle='<->', color='blue'))
    ax1.text(-0.6, h0/2, f'h₀={h0:.2f}m', ha='center', fontsize=10, color='blue', rotation=90)
    
    ax1.text(b+m*h0+0.3, h0/2, f'm={m}', fontsize=10, color='green')
    
    ax1.set_xlabel('宽度 (m)', fontsize=11)
    ax1.set_ylabel('高度 (m)', fontsize=11)
    ax1.set_title('梯形渠道断面', fontsize=13)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    ax1.set_xlim(-2, b+3)
    ax1.set_ylim(-1, h0+1)
    
    # 右图：Q-h曲线
    h_range = np.linspace(0.5, 4.0, 100)
    Q_values = [manning_Q_trapezoidal(b, h, m, n, i) for h in h_range]
    
    ax2.plot(h_range, Q_values, 'b-', linewidth=2)
    ax2.plot(h0, Q, 'ro', markersize=10, label=f'设计点：h={h0:.2f}m, Q={Q:.1f}m³/s')
    ax2.axhline(y=Q, color='gray', linestyle='--', alpha=0.5)
    ax2.axvline(x=h0, color='gray', linestyle='--', alpha=0.5)
    
    ax2.set_xlabel('水深 h (m)', fontsize=11)
    ax2.set_ylabel('流量 Q (m³/s)', fontsize=11)
    ax2.set_title(f'Q-h关系曲线（b={b}m, m={m}, n={n}, i={i}）', fontsize=13)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    output_file = 'uniform_flow_trapezoidal.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{output_file}")
    
    plt.show()
    
    # ========== 总结 ==========
    print("\n" + "=" * 70)
    print("【总结】")
    print("=" * 70)
    print(f"1. 正常水深：h₀ = {h0:.2f} m")
    print(f"2. 断面流速：v = {v:.2f} m/s（{flow_state}，Fr={Fr:.2f}）")
    print(f"3. 谢才系数：C = {C:.2f} m^(1/2)/s")
    print(f"4. 防冲检验：{'✓ 满足' if v <= v_max else '✗ 不满足'}（v={'<' if v <= v_max else '>'}{v_max} m/s）")
    print(f"5. 水力半径：R = {R0:.3f} m")
    print("=" * 70)


def compare_slope_coefficients():
    """
    对比不同边坡系数m的影响
    """
    print("\n" + "=" * 70)
    print("【扩展分析】不同边坡系数m的影响")
    print("=" * 70)
    
    b = 4.0
    Q = 20.0
    n = 0.025
    i = 0.0005
    
    m_values = [1.0, 1.5, 2.0, 2.5]
    results = []
    
    for m in m_values:
        h0, _ = solve_normal_depth_trapezoidal(Q, b, m, n, i, h_init=2.0)
        A0, chi0, R0, B0 = trapezoidal_geometry(b, h0, m)
        v = Q / A0
        results.append((m, h0, A0, R0, v))
    
    print("\n边坡系数m对正常水深h₀的影响：")
    print(f"{'m':<6} {'h₀(m)':<8} {'A(m²)':<8} {'R(m)':<8} {'v(m/s)':<8}")
    print("-" * 50)
    for m, h0, A, R, v in results:
        print(f"{m:<6.1f} {h0:<8.3f} {A:<8.3f} {R:<8.3f} {v:<8.3f}")
    
    print("\n结论：")
    print("  - m越大（边坡越缓），相同Q下h₀越小")
    print("  - 但过流面积A增大，流速v减小")
    print("  - 边坡选择需兼顾土壤稳定性和经济性")


def exercise():
    """练习题"""
    print("\n" + "=" * 70)
    print("【练习题】")
    print("=" * 70)
    print("\n1. 将底坡i改为0.001（加陡），h₀如何变化？")
    print("2. 若流量Q增加到30 m³/s，是否仍满足防冲要求？")
    print("3. 对于砂土边坡（需m≥1.5-2.0），如何平衡防冲和稳定？")
    print("4. 绘制m-h₀关系曲线（固定其他参数）")
    print("=" * 70)


if __name__ == "__main__":
    main()
    compare_slope_coefficients()
    exercise()
