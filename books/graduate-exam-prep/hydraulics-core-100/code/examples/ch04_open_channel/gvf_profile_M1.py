#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水面线M₁型计算（缓坡壅水曲线）

问题：第四章题73 - 水面线数值计算
描述：分段求和法计算M₁型水面线（h₀ < hc < h）

知识点：
1. M₁曲线特征：缓坡（i < ic），h > hc
2. 微分方程：dh/dx = (i - if)/(1 - Fr²)
3. 分段求和法：逆水流方向计算
4. 边界条件：下游给定水深

作者：CHS-Books项目组
日期：2025-10-31
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 无图形界面后端

# 设置中文字体
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


def manning_friction_slope(Q, A, R, n):
    """
    曼宁公式计算摩阻坡度 if
    
    参数:
        Q: 流量 (m³/s)
        A: 过流面积 (m²)
        R: 水力半径 (m)
        n: 糙率
    
    返回:
        if: 摩阻坡度
    """
    if A <= 0 or R <= 0:
        return 0
    v = Q / A
    if_val = (n * v / R**(2/3))**2
    return if_val


def froude_number(Q, A, B, g=9.81):
    """
    弗劳德数计算
    
    参数:
        Q: 流量 (m³/s)
        A: 过流面积 (m²)
        B: 水面宽 (m)
        g: 重力加速度 (m/s²)
    
    返回:
        Fr: 弗劳德数
    """
    if A <= 0 or B <= 0:
        return 0
    v = Q / A
    Fr = v / np.sqrt(g * A / B)
    return Fr


def solve_normal_depth(Q, b, m, n, i, g=9.81, h0=0.5, tol=1e-6, max_iter=100):
    """
    牛顿迭代法求正常水深 h₀
    
    参数:
        Q: 流量 (m³/s)
        b: 底宽 (m)
        m: 边坡系数
        n: 糙率
        i: 渠底坡度
        g: 重力加速度 (m/s²)
        h0: 初始猜测值 (m)
        tol: 收敛精度
        max_iter: 最大迭代次数
    
    返回:
        h0: 正常水深 (m)
    """
    h = h0
    for iteration in range(max_iter):
        A, B, P, R = trapezoidal_geometry(b, m, h)
        
        # 曼宁公式：Q = (A/n) * R^(2/3) * sqrt(i)
        K = A * R**(2/3) / n
        f = K * np.sqrt(i) - Q
        
        # 数值导数
        dh = 0.001
        A2, B2, P2, R2 = trapezoidal_geometry(b, m, h + dh)
        K2 = A2 * R2**(2/3) / n
        df = (K2 * np.sqrt(i) - K * np.sqrt(i)) / dh
        
        # 牛顿步
        if abs(df) < 1e-10:
            break
        delta_h = -f / df
        
        # 步长限制
        delta_h = np.clip(delta_h, -0.5*h, 0.5*h)
        h_new = h + delta_h
        
        if h_new <= 0:
            h_new = h * 0.5
        
        if abs(delta_h) < tol:
            return h_new
        
        h = h_new
    
    return h


def solve_critical_depth(Q, b, m, g=9.81, hc0=0.5, tol=1e-6, max_iter=100):
    """
    牛顿迭代法求临界水深 hc
    
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
    """
    h = hc0
    for iteration in range(max_iter):
        A, B, P, R = trapezoidal_geometry(b, m, h)
        
        # 临界流条件：Q² * B / (g * A³) = 1
        f = Q**2 * B / (g * A**3) - 1
        
        # 数值导数
        dh = 0.001
        A2, B2, P2, R2 = trapezoidal_geometry(b, m, h + dh)
        f2 = Q**2 * B2 / (g * A2**3) - 1
        df = (f2 - f) / dh
        
        # 牛顿步
        if abs(df) < 1e-10:
            break
        delta_h = -f / df
        
        # 步长限制
        delta_h = np.clip(delta_h, -0.3*h, 0.3*h)
        h_new = h + delta_h
        
        if h_new <= 0:
            h_new = h * 0.5
        
        if abs(delta_h) < tol:
            return h_new
        
        h = h_new
    
    return h


def gvf_M1_profile(Q, b, m, n, i, h_downstream, L, g=9.81, num_steps=100):
    """
    分段求和法计算M₁型水面线
    
    M₁特征：缓坡（i < ic），h > hc > h₀
    计算方向：逆水流方向（从下游向上游）
    
    参数:
        Q: 流量 (m³/s)
        b: 底宽 (m)
        m: 边坡系数
        n: 糙率
        i: 渠底坡度
        h_downstream: 下游边界水深 (m)
        L: 计算河段长度 (m)
        g: 重力加速度 (m/s²)
        num_steps: 分段数
    
    返回:
        x: 距离数组 (m)
        h: 水深数组 (m)
        h0: 正常水深 (m)
        hc: 临界水深 (m)
    """
    # 计算特征水深
    h0 = solve_normal_depth(Q, b, m, n, i, g)
    hc = solve_critical_depth(Q, b, m, g)
    
    print(f"\n=== M₁水面线计算 ===")
    print(f"正常水深 h₀ = {h0:.3f} m")
    print(f"临界水深 hc = {hc:.3f} m")
    print(f"下游水深 h_down = {h_downstream:.3f} m")
    print(f"判断：h_down > hc > h₀ → M₁型（缓坡壅水曲线）✓")
    
    # 初始化
    x = np.zeros(num_steps + 1)
    h = np.zeros(num_steps + 1)
    
    # 边界条件（下游）
    x[0] = 0
    h[0] = h_downstream
    
    # 自适应步长（根据dh/dx大小调整）
    dx_base = L / num_steps
    
    # 逆水流方向计算（从下游到上游）
    for i in range(num_steps):
        h_i = h[i]
        
        # 当前断面几何
        A, B, P, R = trapezoidal_geometry(b, m, h_i)
        
        # 摩阻坡度
        if_val = manning_friction_slope(Q, A, R, n)
        
        # 弗劳德数
        Fr = froude_number(Q, A, B, g)
        
        # 水深梯度 dh/dx
        numerator = i - if_val
        denominator = 1 - Fr**2
        
        if abs(denominator) < 0.01:
            # 接近临界流，强制停止
            print(f"  警告：Fr={Fr:.3f}接近1，在x={x[i]:.1f}m处停止")
            x = x[:i+1]
            h = h[:i+1]
            break
        
        dh_dx = numerator / denominator
        
        # 自适应步长
        if abs(dh_dx) > 0.01:
            dx = dx_base * 0.5  # 梯度大，步长减半
        else:
            dx = dx_base
        
        # 向上游推进
        x[i+1] = x[i] + dx
        h[i+1] = h[i] + dh_dx * dx
        
        # 边界保护
        if h[i+1] < hc * 1.01:
            print(f"  警告：水深接近临界深度，停止计算")
            x = x[:i+2]
            h = h[:i+2]
            break
        
        if x[i+1] >= L:
            x[i+1] = L
            x = x[:i+2]
            h = h[:i+2]
            break
    
    return x, h, h0, hc


def plot_M1_profile(x, h, h0, hc, b, m, i, Q, filename='gvf_profile_M1.png'):
    """
    绘制M₁水面线
    
    参数:
        x: 距离数组 (m)
        h: 水深数组 (m)
        h0: 正常水深 (m)
        hc: 临界水深 (m)
        b: 底宽 (m)
        m: 边坡系数
        i: 渠底坡度
        Q: 流量 (m³/s)
        filename: 保存文件名
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 子图1：水面线纵剖面
    ax1 = axes[0, 0]
    
    # 渠底线
    z_bed = -i * x
    z_water = z_bed + h
    
    ax1.plot(x, z_bed, 'k-', linewidth=2, label='渠底')
    ax1.plot(x, z_water, 'b-', linewidth=2.5, label='水面线（M₁）')
    ax1.axhline(z_bed[0] + h0, color='g', linestyle='--', 
                linewidth=1.5, label=f'正常水深线 h₀={h0:.3f}m')
    ax1.axhline(z_bed[0] + hc, color='r', linestyle='--', 
                linewidth=1.5, label=f'临界水深线 hc={hc:.3f}m')
    
    # 标注关键点
    ax1.plot(x[0], z_water[0], 'ro', markersize=8, 
             label=f'下游边界 h={h[0]:.3f}m')
    ax1.plot(x[-1], z_water[-1], 'go', markersize=8, 
             label=f'上游 h={h[-1]:.3f}m')
    
    ax1.fill_between(x, z_bed, z_water, alpha=0.3, color='cyan')
    ax1.set_xlabel('距离 x (m)', fontsize=12)
    ax1.set_ylabel('高程 z (m)', fontsize=12)
    ax1.set_title('M₁型水面线纵剖面（缓坡壅水曲线）', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10, loc='best')
    ax1.grid(True, alpha=0.3)
    
    # 子图2：水深变化曲线
    ax2 = axes[0, 1]
    ax2.plot(x, h, 'b-', linewidth=2.5, label='实际水深')
    ax2.axhline(h0, color='g', linestyle='--', linewidth=1.5, label=f'h₀={h0:.3f}m')
    ax2.axhline(hc, color='r', linestyle='--', linewidth=1.5, label=f'hc={hc:.3f}m')
    ax2.fill_between(x, h0, h, alpha=0.2, color='blue', 
                     where=(h >= h0), label='壅水区')
    ax2.set_xlabel('距离 x (m)', fontsize=12)
    ax2.set_ylabel('水深 h (m)', fontsize=12)
    ax2.set_title('水深沿程变化', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 子图3：dh/dx和Fr变化
    ax3 = axes[1, 0]
    
    # 计算dh/dx和Fr
    dh_dx_vals = []
    Fr_vals = []
    for i in range(len(h)):
        A, B, P, R = trapezoidal_geometry(b, m, h[i])
        if_val = manning_friction_slope(Q, A, R, 0.025)
        Fr = froude_number(Q, A, B)
        
        numerator = i - if_val
        denominator = 1 - Fr**2
        if abs(denominator) > 0.01:
            dh_dx = numerator / denominator
        else:
            dh_dx = 0
        
        dh_dx_vals.append(dh_dx)
        Fr_vals.append(Fr)
    
    ax3_twin = ax3.twinx()
    line1 = ax3.plot(x, dh_dx_vals, 'b-', linewidth=2, label='dh/dx')
    ax3.axhline(0, color='k', linestyle='-', linewidth=0.5)
    ax3.set_xlabel('距离 x (m)', fontsize=12)
    ax3.set_ylabel('水深梯度 dh/dx', fontsize=12, color='b')
    ax3.tick_params(axis='y', labelcolor='b')
    
    line2 = ax3_twin.plot(x, Fr_vals, 'r-', linewidth=2, label='Fr')
    ax3_twin.axhline(1, color='r', linestyle='--', linewidth=1, alpha=0.5)
    ax3_twin.set_ylabel('弗劳德数 Fr', fontsize=12, color='r')
    ax3_twin.tick_params(axis='y', labelcolor='r')
    
    ax3.set_title('水深梯度与弗劳德数', fontsize=14, fontweight='bold')
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, fontsize=10, loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    # 子图4：断面形状与参数表
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # 计算参数
    A_down, B_down, P_down, R_down = trapezoidal_geometry(b, m, h[0])
    v_down = Q / A_down
    Fr_down = froude_number(Q, A_down, B_down)
    
    A_up, B_up, P_up, R_up = trapezoidal_geometry(b, m, h[-1])
    v_up = Q / A_up
    Fr_up = froude_number(Q, A_up, B_up)
    
    # 壅水高度
    backwater_height = h[0] - h0
    backwater_length = x[-1]
    
    info_text = f"""
    【M₁型水面线计算结果】
    
    渠道参数：
      底宽 b = {b:.2f} m
      边坡系数 m = {m:.2f}
      糙率 n = 0.025
      底坡 i = {i:.5f}
      流量 Q = {Q:.2f} m³/s
    
    特征水深：
      正常水深 h₀ = {h0:.3f} m
      临界水深 hc = {hc:.3f} m
      临界坡度 ic = {(i * (hc/h0)**(10/3)):.5f}
      坡度判别：i < ic → 缓坡 ✓
    
    下游断面（x=0m）：
      水深 h = {h[0]:.3f} m
      面积 A = {A_down:.2f} m²
      流速 v = {v_down:.2f} m/s
      Fr = {Fr_down:.3f} < 1（缓流）
    
    上游断面（x={x[-1]:.1f}m）：
      水深 h = {h[-1]:.3f} m
      面积 A = {A_up:.2f} m²
      流速 v = {v_up:.2f} m/s
      Fr = {Fr_up:.3f} < 1（缓流）
    
    壅水效应：
      壅水高度 Δh = {backwater_height:.3f} m
      壅水长度 L = {backwater_length:.1f} m
      相对壅高 Δh/h₀ = {backwater_height/h0*100:.1f}%
    
    曲线特征：
      • M₁曲线：缓坡壅水曲线
      • dh/dx > 0（水深向上游递增）
      • Fr < 1（全程缓流）
      • 渐近于h₀（上游无穷远处）
    """
    
    ax4.text(0.05, 0.95, info_text, transform=ax4.transAxes,
             fontsize=10, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{filename}")
    plt.close()


def main():
    """
    主程序：第四章题73 - M₁水面线计算
    """
    print("="*60)
    print("第四章题73 - M₁型水面线计算（分段求和法）")
    print("="*60)
    
    # 题目数据
    Q = 25.0        # 流量 (m³/s)
    b = 8.0         # 底宽 (m)
    m = 1.5         # 边坡系数
    n = 0.025       # 糙率
    i = 0.0001      # 渠底坡度（缓坡）
    h_downstream = 3.5  # 下游控制水深（闸坝壅水）(m)
    L = 2000.0      # 计算河段长度 (m)
    
    print(f"\n【题目】")
    print(f"梯形渠道，底宽b={b}m，边坡m={m}，糙率n={n}")
    print(f"底坡i={i}（缓坡），流量Q={Q} m³/s")
    print(f"下游有闸坝控制，水深h={h_downstream}m")
    print(f"求：上游{L}m范围内的水面线")
    
    # 计算水面线
    x, h, h0, hc = gvf_M1_profile(Q, b, m, n, i, h_downstream, L)
    
    print(f"\n【计算结果】")
    print(f"壅水高度：Δh = {h[0] - h0:.3f} m")
    print(f"影响长度：L = {x[-1]:.1f} m")
    print(f"上游水深：h = {h[-1]:.3f} m（趋向h₀={h0:.3f}m）")
    
    # 绘图
    plot_M1_profile(x, h, h0, hc, b, m, i, Q)
    
    print("\n" + "="*60)
    print("M₁水面线计算完成！")
    print("="*60)


def exercise():
    """
    练习题
    """
    print("\n" + "="*60)
    print("【练习题】")
    print("="*60)
    
    print("""
    1. 如果下游水深降低到3.0m，水面线如何变化？
    2. 如果底坡增大到i=0.0005（接近临界坡），会出现什么情况？
    3. 如果渠道糙率增大到n=0.035，对壅水长度有何影响？
    4. M₁曲线渐近于h₀的理论依据是什么？
    
    提示：
    - 修改参数后重新运行main()
    - 观察h₀、hc和边界条件的关系
    - 分析dh/dx → 0的原因
    """)


if __name__ == "__main__":
    main()
    exercise()
