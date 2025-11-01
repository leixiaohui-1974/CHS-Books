#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水面线S₂型计算（陡坡降水曲线）

问题：第四章题74 - 水面线数值计算
描述：分段求和法计算S₂型水面线（hc < h < h₀）

知识点：
1. S₂曲线特征：陡坡（i > ic），hc < h < h₀
2. 微分方程：dh/dx = (i - if)/(1 - Fr²)
3. 分段求和法：顺水流方向计算
4. 边界条件：上游给定水深

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
    """梯形断面几何特性"""
    A = (b + m * h) * h
    B = b + 2 * m * h
    P = b + 2 * h * np.sqrt(1 + m**2)
    R = A / P if P > 0 else 0
    return A, B, P, R


def manning_friction_slope(Q, A, R, n):
    """曼宁公式计算摩阻坡度"""
    if A <= 0 or R <= 0:
        return 0
    v = Q / A
    if_val = (n * v / R**(2/3))**2
    return if_val


def froude_number(Q, A, B, g=9.81):
    """弗劳德数计算"""
    if A <= 0 or B <= 0:
        return 0
    v = Q / A
    Fr = v / np.sqrt(g * A / B)
    return Fr


def solve_normal_depth(Q, b, m, n, i, g=9.81, h0=1.0, tol=1e-6, max_iter=100):
    """牛顿迭代法求正常水深 h₀"""
    h = h0
    for iteration in range(max_iter):
        A, B, P, R = trapezoidal_geometry(b, m, h)
        K = A * R**(2/3) / n
        f = K * np.sqrt(i) - Q
        
        dh = 0.001
        A2, B2, P2, R2 = trapezoidal_geometry(b, m, h + dh)
        K2 = A2 * R2**(2/3) / n
        df = (K2 * np.sqrt(i) - K * np.sqrt(i)) / dh
        
        if abs(df) < 1e-10:
            break
        delta_h = -f / df
        delta_h = np.clip(delta_h, -0.5*h, 0.5*h)
        h_new = h + delta_h
        
        if h_new <= 0:
            h_new = h * 0.5
        
        if abs(delta_h) < tol:
            return h_new
        h = h_new
    
    return h


def solve_critical_depth(Q, b, m, g=9.81, hc0=0.5, tol=1e-6, max_iter=100):
    """牛顿迭代法求临界水深 hc"""
    h = hc0
    for iteration in range(max_iter):
        A, B, P, R = trapezoidal_geometry(b, m, h)
        f = Q**2 * B / (g * A**3) - 1
        
        dh = 0.001
        A2, B2, P2, R2 = trapezoidal_geometry(b, m, h + dh)
        f2 = Q**2 * B2 / (g * A2**3) - 1
        df = (f2 - f) / dh
        
        if abs(df) < 1e-10:
            break
        delta_h = -f / df
        delta_h = np.clip(delta_h, -0.3*h, 0.3*h)
        h_new = h + delta_h
        
        if h_new <= 0:
            h_new = h * 0.5
        
        if abs(delta_h) < tol:
            return h_new
        h = h_new
    
    return h


def gvf_S2_profile(Q, b, m, n, i, h_upstream, L, g=9.81, num_steps=100):
    """
    分段求和法计算S₂型水面线
    
    S₂特征：陡坡（i > ic），hc < h < h₀
    计算方向：顺水流方向（从上游向下游）
    
    参数:
        Q: 流量 (m³/s)
        b: 底宽 (m)
        m: 边坡系数
        n: 糙率
        i: 渠底坡度（陡坡）
        h_upstream: 上游边界水深 (m)
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
    
    print(f"\n=== S₂水面线计算 ===")
    print(f"正常水深 h₀ = {h0:.3f} m")
    print(f"临界水深 hc = {hc:.3f} m")
    print(f"上游水深 h_up = {h_upstream:.3f} m")
    
    # 判断坡度类型
    if h0 < hc:
        print(f"判断：h₀ < hc → 陡坡 ✓")
        if hc < h_upstream < h0:
            print(f"判断：hc < h < h₀ → S₂型（陡坡降水曲线）✓")
        else:
            print(f"警告：h不在(hc, h₀)区间，可能不是S₂型曲线！")
    else:
        print(f"警告：h₀ > hc，这是缓坡，不是陡坡！")
    
    # 初始化
    x = np.zeros(num_steps + 1)
    h = np.zeros(num_steps + 1)
    
    # 边界条件（上游）
    x[0] = 0
    h[0] = h_upstream
    
    dx_base = L / num_steps
    
    # 顺水流方向计算（从上游到下游）
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
            # 接近临界流
            print(f"  警告：Fr={Fr:.3f}接近1，在x={x[i]:.1f}m处停止")
            x = x[:i+1]
            h = h[:i+1]
            break
        
        dh_dx = numerator / denominator
        
        # 自适应步长
        if abs(dh_dx) > 0.01:
            dx = dx_base * 0.5
        else:
            dx = dx_base
        
        # 向下游推进
        x[i+1] = x[i] + dx
        h[i+1] = h[i] + dh_dx * dx
        
        # 边界保护
        if h[i+1] < hc * 1.01:
            print(f"  警告：水深接近临界深度hc={hc:.3f}m，停止计算")
            x = x[:i+2]
            h = h[:i+2]
            break
        
        if h[i+1] > h_upstream * 1.5:
            print(f"  警告：水深异常增大，停止计算")
            x = x[:i+2]
            h = h[:i+2]
            break
        
        if x[i+1] >= L:
            x[i+1] = L
            x = x[:i+2]
            h = h[:i+2]
            break
    
    return x, h, h0, hc


def plot_S2_profile(x, h, h0, hc, b, m, i, Q, filename='gvf_profile_S2.png'):
    """绘制S₂水面线"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 子图1：水面线纵剖面
    ax1 = axes[0, 0]
    
    z_bed = -i * x
    z_water = z_bed + h
    
    ax1.plot(x, z_bed, 'k-', linewidth=2, label='渠底')
    ax1.plot(x, z_water, 'b-', linewidth=2.5, label='水面线（S₂）')
    ax1.axhline(z_bed[0] + h0, color='g', linestyle='--', 
                linewidth=1.5, label=f'正常水深线 h₀={h0:.3f}m')
    ax1.axhline(z_bed[0] + hc, color='r', linestyle='--', 
                linewidth=1.5, label=f'临界水深线 hc={hc:.3f}m')
    
    ax1.plot(x[0], z_water[0], 'go', markersize=8, 
             label=f'上游边界 h={h[0]:.3f}m')
    ax1.plot(x[-1], z_water[-1], 'ro', markersize=8, 
             label=f'下游 h={h[-1]:.3f}m')
    
    ax1.fill_between(x, z_bed, z_water, alpha=0.3, color='cyan')
    ax1.set_xlabel('距离 x (m)', fontsize=12)
    ax1.set_ylabel('高程 z (m)', fontsize=12)
    ax1.set_title('S₂型水面线纵剖面（陡坡降水曲线）', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10, loc='best')
    ax1.grid(True, alpha=0.3)
    
    # 子图2：水深变化
    ax2 = axes[0, 1]
    ax2.plot(x, h, 'b-', linewidth=2.5, label='实际水深')
    ax2.axhline(h0, color='g', linestyle='--', linewidth=1.5, label=f'h₀={h0:.3f}m')
    ax2.axhline(hc, color='r', linestyle='--', linewidth=1.5, label=f'hc={hc:.3f}m')
    ax2.fill_between(x, hc, h, alpha=0.2, color='red', 
                     where=(h >= hc), label='超临界流区')
    ax2.set_xlabel('距离 x (m)', fontsize=12)
    ax2.set_ylabel('水深 h (m)', fontsize=12)
    ax2.set_title('水深沿程变化', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 子图3：dh/dx和Fr
    ax3 = axes[1, 0]
    
    dh_dx_vals = []
    Fr_vals = []
    for i in range(len(h)):
        A, B, P, R = trapezoidal_geometry(b, m, h[i])
        if_val = manning_friction_slope(Q, A, R, n)
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
    ax3.legend(lines, labels, fontsize=10, loc='upper right')
    ax3.grid(True, alpha=0.3)
    
    # 子图4：参数表
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    A_up, B_up, P_up, R_up = trapezoidal_geometry(b, m, h[0])
    v_up = Q / A_up
    Fr_up = froude_number(Q, A_up, B_up)
    
    A_down, B_down, P_down, R_down = trapezoidal_geometry(b, m, h[-1])
    v_down = Q / A_down
    Fr_down = froude_number(Q, A_down, B_down)
    
    drawdown_height = h[0] - h[-1]
    drawdown_length = x[-1]
    
    info_text = f"""
    【S₂型水面线计算结果】
    
    渠道参数：
      底宽 b = {b:.2f} m
      边坡系数 m = {m:.2f}
      糙率 n = {n:.3f}
      底坡 i = {i:.4f}（陡坡）
      流量 Q = {Q:.2f} m³/s
    
    特征水深：
      正常水深 h₀ = {h0:.3f} m
      临界水深 hc = {hc:.3f} m
      坡度判别：h₀ < hc → 陡坡 ✓
    
    上游断面（x=0m）：
      水深 h = {h[0]:.3f} m
      面积 A = {A_up:.2f} m²
      流速 v = {v_up:.2f} m/s
      Fr = {Fr_up:.3f} < 1（缓流）
    
    下游断面（x={x[-1]:.1f}m）：
      水深 h = {h[-1]:.3f} m
      面积 A = {A_down:.2f} m²
      流速 v = {v_down:.2f} m/s
      Fr = {Fr_down:.3f} → 1（趋向临界）
    
    降水效应：
      降水高度 Δh = {drawdown_height:.3f} m
      影响长度 L = {drawdown_length:.1f} m
      相对降幅 Δh/h = {drawdown_height/h[0]*100:.1f}%
    
    曲线特征：
      • S₂曲线：陡坡降水曲线
      • dh/dx < 0（水深向下游递减）
      • Fr < 1 → 1（从缓流到临界）
      • 渐近于hc（下游跌落处）
    """
    
    ax4.text(0.05, 0.95, info_text, transform=ax4.transAxes,
             fontsize=10, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{filename}")
    plt.close()


def main():
    """
    主程序：第四章题74 - S₂水面线计算
    """
    print("="*60)
    print("第四章题74 - S₂型水面线计算（分段求和法）")
    print("="*60)
    
    # 题目数据
    Q = 20.0        # 流量 (m³/s)
    b = 6.0         # 底宽 (m)
    m = 1.0         # 边坡系数
    n = 0.025       # 糙率
    i = 0.01        # 渠底坡度（陡坡）
    h_upstream = 1.2   # 上游控制水深（闸门出流）(m)
    L = 500.0       # 计算河段长度 (m)
    
    print(f"\n【题目】")
    print(f"梯形渠道，底宽b={b}m，边坡m={m}，糙率n={n}")
    print(f"底坡i={i}（陡坡），流量Q={Q} m³/s")
    print(f"上游闸门控制，水深h={h_upstream}m")
    print(f"求：下游{L}m范围内的水面线")
    
    # 计算水面线
    x, h, h0, hc = gvf_S2_profile(Q, b, m, n, i, h_upstream, L)
    
    print(f"\n【计算结果】")
    print(f"降水高度：Δh = {h[0] - h[-1]:.3f} m")
    print(f"影响长度：L = {x[-1]:.1f} m")
    print(f"下游水深：h = {h[-1]:.3f} m（趋向hc={hc:.3f}m）")
    
    # 绘图
    plot_S2_profile(x, h, h0, hc, b, m, i, Q)
    
    print("\n" + "="*60)
    print("S₂水面线计算完成！")
    print("="*60)


def exercise():
    """练习题"""
    print("\n" + "="*60)
    print("【练习题】")
    print("="*60)
    
    print("""
    1. 如果上游水深增大到1.5m，水面线如何变化？
    2. 如果底坡减小到i=0.001（接近临界坡），会怎样？
    3. S₂曲线与跌水（自由跌落）的区别是什么？
    4. S₂曲线下游端如何与S₁曲线衔接？
    
    提示：
    - S₂曲线：hc < h < h₀，dh/dx < 0
    - 下游趋向hc（临界流）
    - 常见于闸门下游、陡槽进口
    """)


if __name__ == "__main__":
    main()
    exercise()
