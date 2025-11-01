#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闸孔出流流型判别与计算

问题：第五章题88 - 闸孔出流流型判别
描述：根据闸门开度判断堰流、孔流或过渡流，并计算流量

知识点：
1. 流型判别：e/H < 0.65(孔流)，e/H > 0.80(堰流)
2. 孔流公式：Q = ε·b·e·√(2gH)
3. 堰流公式：Q = m·b·H^(3/2)·√(2g)
4. 过渡流：线性插值

作者：CHS-Books项目组
日期：2025-11-01
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def flow_type_classification(e, H):
    """
    闸孔出流流型判别
    
    参数:
        e: 闸门开度 (m)
        H: 上游水深 (m)
    
    返回:
        flow_type: 流型字符串
        ratio: e/H比值
    """
    ratio = e / H
    
    if ratio < 0.65:
        flow_type = "孔流（orifice flow）"
    elif ratio > 0.80:
        flow_type = "堰流（weir flow）"
    else:
        flow_type = "过渡流（transition flow）"
    
    return flow_type, ratio


def orifice_flow(b, e, H, epsilon=0.60, g=9.81):
    """
    孔流公式计算
    
    Q = ε·b·e·√(2gH)
    
    参数:
        b: 闸孔宽度 (m)
        e: 闸门开度 (m)
        H: 上游水深 (m)
        epsilon: 流量系数（默认0.60）
        g: 重力加速度 (m/s²)
    
    返回:
        Q: 流量 (m³/s)
        v: 闸下流速 (m/s)
        h: 闸下水深 (m)
    """
    Q = epsilon * b * e * np.sqrt(2 * g * H)
    v = np.sqrt(2 * g * H)  # 理论流速
    h = epsilon * e  # 收缩水深
    return Q, v, h


def weir_flow(b, H, m=0.35, g=9.81):
    """
    堰流公式计算
    
    Q = m·b·H^(3/2)·√(2g)
    
    参数:
        b: 闸孔宽度 (m)
        H: 上游水深 (m)
        m: 流量系数（默认0.35）
        g: 重力加速度 (m/s²)
    
    返回:
        Q: 流量 (m³/s)
    """
    Q = m * b * np.sqrt(2 * g) * H**(3/2)
    return Q


def transition_flow(b, e, H, epsilon=0.60, m=0.35, g=9.81):
    """
    过渡流计算（线性插值）
    
    参数:
        b: 闸孔宽度 (m)
        e: 闸门开度 (m)
        H: 上游水深 (m)
        epsilon: 孔流系数
        m: 堰流系数
        g: 重力加速度 (m/s²)
    
    返回:
        Q: 流量 (m³/s)
    """
    ratio = e / H
    
    # 边界值
    Q_orifice, _, _ = orifice_flow(b, e, H, epsilon, g)
    Q_weir = weir_flow(b, H, m, g)
    
    # 线性插值
    if ratio <= 0.65:
        Q = Q_orifice
    elif ratio >= 0.80:
        Q = Q_weir
    else:
        # 0.65 < ratio < 0.80
        weight = (ratio - 0.65) / (0.80 - 0.65)
        Q = Q_orifice * (1 - weight) + Q_weir * weight
    
    return Q


def submerged_flow_check(H1, H2, e, sigma_s=0.85):
    """
    检查是否为淹没出流
    
    判据：H2/H1 > 0.75 → 淹没
    
    参数:
        H1: 上游水深 (m)
        H2: 下游水深 (m)
        e: 闸门开度 (m)
        sigma_s: 淹没系数（默认0.85）
    
    返回:
        is_submerged: 是否淹没
        submergence_ratio: 淹没比 H2/H1
        flow_reduction: 流量减少系数
    """
    submergence_ratio = H2 / H1
    
    if submergence_ratio > 0.75:
        is_submerged = True
        flow_reduction = sigma_s  # 流量减少到85%
    else:
        is_submerged = False
        flow_reduction = 1.0
    
    return is_submerged, submergence_ratio, flow_reduction


def plot_sluice_gate_analysis(filename='sluice_gate_flow.png'):
    """
    绘制闸孔出流综合分析图（6子图）
    
    参数:
        filename: 保存文件名
    """
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # 参数
    b = 6.0  # 闸孔宽度
    H = 5.0  # 上游水深
    epsilon = 0.60
    m = 0.35
    g = 9.81
    
    # 子图1：流型分区图
    ax1 = fig.add_subplot(gs[0, 0])
    
    e_range = np.linspace(0.1, 5.0, 100)
    ratio_range = e_range / H
    
    # 标注流型分区
    ax1.axhspan(0, 0.65, alpha=0.2, color='blue', label='孔流区 (e/H<0.65)')
    ax1.axhspan(0.65, 0.80, alpha=0.2, color='yellow', label='过渡区 (0.65≤e/H≤0.80)')
    ax1.axhspan(0.80, 1.0, alpha=0.2, color='green', label='堰流区 (e/H>0.80)')
    
    ax1.plot(e_range, ratio_range, 'r-', linewidth=2.5, label=f'e/H曲线 (H={H}m)')
    
    # 标注关键点
    e_key = [0.5, 1.5, 2.5, 4.0]
    for e_val in e_key:
        ratio_val = e_val / H
        flow_type, _ = flow_type_classification(e_val, H)
        ax1.plot(e_val, ratio_val, 'ko', markersize=8)
        ax1.text(e_val+0.2, ratio_val, f'e={e_val}m\n{flow_type[:2]}', fontsize=8)
    
    ax1.axhline(0.65, color='b', linestyle='--', linewidth=1.5)
    ax1.axhline(0.80, color='g', linestyle='--', linewidth=1.5)
    
    ax1.set_xlabel('闸门开度 e (m)', fontsize=12)
    ax1.set_ylabel('相对开度 e/H', fontsize=12)
    ax1.set_title('闸孔出流流型分区', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10, loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 1.0])
    
    # 子图2：流量曲线对比
    ax2 = fig.add_subplot(gs[0, 1])
    
    Q_orifice_list = []
    Q_weir_list = []
    Q_actual_list = []
    
    for e in e_range:
        Q_o, _, _ = orifice_flow(b, e, H, epsilon, g)
        Q_w = weir_flow(b, H, m, g)
        Q_a = transition_flow(b, e, H, epsilon, m, g)
        
        Q_orifice_list.append(Q_o)
        Q_weir_list.append(Q_w)
        Q_actual_list.append(Q_a)
    
    ax2.plot(e_range, Q_orifice_list, 'b--', linewidth=2, label='孔流公式', alpha=0.7)
    ax2.plot(e_range, Q_weir_list, 'g--', linewidth=2, label='堰流公式', alpha=0.7)
    ax2.plot(e_range, Q_actual_list, 'r-', linewidth=2.5, label='实际流量（综合）')
    
    ax2.set_xlabel('闸门开度 e (m)', fontsize=12)
    ax2.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax2.set_title('流量随开度变化', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 子图3：流量系数影响
    ax3 = fig.add_subplot(gs[1, 0])
    
    epsilon_values = [0.55, 0.60, 0.65]
    colors = ['blue', 'green', 'red']
    
    for eps, color in zip(epsilon_values, colors):
        Q_eps = []
        for e in e_range:
            if e/H < 0.65:
                Q, _, _ = orifice_flow(b, e, H, eps, g)
                Q_eps.append(Q)
            else:
                Q_eps.append(np.nan)
        ax3.plot(e_range, Q_eps, linewidth=2, color=color, label=f'ε={eps}')
    
    ax3.set_xlabel('闸门开度 e (m)', fontsize=12)
    ax3.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax3.set_title('流量系数ε对孔流的影响', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim([0, H*0.65])
    
    # 子图4：淹没出流影响
    ax4 = fig.add_subplot(gs[1, 1])
    
    e_fixed = 1.2  # 固定开度
    H1_fixed = 5.0
    H2_range = np.linspace(0, 5.0, 100)
    
    Q_free, _, _ = orifice_flow(b, e_fixed, H1_fixed, epsilon, g)
    Q_submerged_list = []
    
    for H2 in H2_range:
        is_sub, ratio, reduction = submerged_flow_check(H1_fixed, H2, e_fixed)
        Q_sub = Q_free * reduction
        Q_submerged_list.append(Q_sub)
    
    ax4.plot(H2_range, Q_submerged_list, 'b-', linewidth=2.5)
    ax4.axhline(Q_free, color='r', linestyle='--', linewidth=1.5, label=f'自由出流 Q={Q_free:.1f}m³/s')
    ax4.axvline(0.75*H1_fixed, color='orange', linestyle='--', linewidth=1.5, label='淹没界限 H₂=0.75H₁')
    
    ax4.fill_between(H2_range, 0, Q_submerged_list, 
                     where=(H2_range>0.75*H1_fixed), alpha=0.2, color='red', label='淹没区')
    
    ax4.set_xlabel('下游水深 H₂ (m)', fontsize=12)
    ax4.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax4.set_title(f'淹没出流流量变化（e={e_fixed}m, H₁={H1_fixed}m）', fontsize=14, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    # 子图5：断面流速分布
    ax5 = fig.add_subplot(gs[2, 0])
    
    # 绘制闸门断面示意图
    e_demo = 1.2
    H_demo = 5.0
    Q_demo, v_demo, h_demo = orifice_flow(b, e_demo, H_demo, epsilon, g)
    
    # 上游断面
    x_up = np.array([0, 0, 1, 1, 0])
    y_up = np.array([0, H_demo, H_demo, 0, 0])
    ax5.plot(x_up, y_up, 'b-', linewidth=2, label='上游')
    ax5.fill(x_up, y_up, alpha=0.2, color='cyan')
    
    # 闸门
    x_gate = np.array([1, 1])
    y_gate = np.array([e_demo, H_demo])
    ax5.plot(x_gate, y_gate, 'k-', linewidth=4, label='闸门')
    
    # 下游断面（收缩段）
    x_down = np.array([1, 1.5, 2, 2, 1])
    y_down = np.array([0, 0, 0, h_demo, 0])
    ax5.plot(x_down, y_down, 'g-', linewidth=2, label='下游（收缩）')
    ax5.fill(x_down, y_down, alpha=0.2, color='lightgreen')
    
    # 水面线
    x_surface = np.array([0, 1, 1, 1.5, 2])
    y_surface = np.array([H_demo, H_demo, e_demo, h_demo, h_demo])
    ax5.plot(x_surface, y_surface, 'b-', linewidth=2, linestyle='--')
    
    # 标注
    ax5.text(0.5, H_demo/2, f'H={H_demo}m\nv≈0', ha='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    ax5.text(1.7, h_demo/2, f'h={h_demo:.2f}m\nv={v_demo:.2f}m/s', ha='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    ax5.text(1, e_demo/2, f'e={e_demo}m', ha='right', fontsize=10)
    
    # 能量线
    E_up = H_demo
    E_down = h_demo + v_demo**2/(2*g)
    x_energy = np.array([0, 2])
    y_energy = np.array([E_up, E_down])
    ax5.plot(x_energy, y_energy, 'r-', linewidth=1.5, linestyle=':', label='能量线')
    
    ax5.set_xlabel('距离 (m)', fontsize=12)
    ax5.set_ylabel('高程 (m)', fontsize=12)
    ax5.set_title('闸孔出流断面示意图', fontsize=14, fontweight='bold')
    ax5.legend(fontsize=10, loc='upper right')
    ax5.grid(True, alpha=0.3)
    ax5.set_xlim([-0.5, 2.5])
    ax5.set_ylim([0, H_demo*1.1])
    ax5.set_aspect('equal')
    
    # 子图6：参数表
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.axis('off')
    
    info_text = """
    【闸孔出流计算指南】
    
    流型判别标准：
      e/H < 0.65  →  孔流（orifice flow）
      0.65≤e/H≤0.80  →  过渡流（transition）
      e/H > 0.80  →  堰流（weir flow）
    
    孔流公式：
      Q = ε·b·e·√(2gH)
      流量系数：ε = 0.55~0.65
      收缩系数：Cc = 0.61（平板闸门）
      闸下水深：h = Cc·e
    
    堰流公式：
      Q = m·b·H^(3/2)·√(2g)
      流量系数：m = 0.30~0.35
    
    淹没出流判别：
      H₂/H₁ > 0.75  →  淹没出流
      流量：Q_sub = σs·Q_free
      淹没系数：σs = 0.85~0.90
    
    工程应用：
      • 水闸泄洪调度
      • 灌溉渠道配水
      • 水位控制
      • 流量调节
    
    设计要点：
      ✓ 闸门平稳启闭
      ✓ 避免淹没出流（增大开度）
      ✓ 防止振动（避免e/H=0.7）
      ✓ 下游消能设施
    
    计算实例（本图参数）：
      b=6m, H=5m, e=1.2m
      e/H=0.24 → 孔流 ✓
      Q=29.7 m³/s
      v=9.90 m/s
      h=0.72 m
    """
    
    ax6.text(0.05, 0.95, info_text, transform=ax6.transAxes,
             fontsize=9, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{filename}")
    plt.close()


def main():
    """
    主程序：第五章题88 - 闸孔出流流型判别
    """
    print("="*70)
    print("第五章题88 - 闸孔出流流型判别")
    print("="*70)
    
    # 题目数据
    b = 6.0         # 闸孔宽度 (m)
    d = 3.0         # 闸门高度 (m)
    H = 5.0         # 上游水深 (m)
    e_list = [0.5, 1.5, 2.5]  # 不同开度 (m)
    
    print(f"\n【题目】")
    print(f"平板闸门，宽b={b}m，高d={d}m，上游水深H={H}m")
    print(f"闸门开度e分别为{e_list}m")
    print(f"判断出流型式并计算流量")
    
    print(f"\n【解】")
    print(f"\n判别准则：")
    print(f"  e/H < 0.65  →  孔流（闸孔出流）")
    print(f"  e/H > 0.80  →  堰流")
    print(f"  0.65 ≤ e/H ≤ 0.80  →  过渡流")
    
    print(f"\n计算结果：\n")
    print(f"{'e(m)':<8} {'e/H':<10} {'流型':<20} {'公式':<25} {'Q(m³/s)':<12}")
    print("-" * 80)
    
    for e in e_list:
        flow_type, ratio = flow_type_classification(e, H)
        
        if ratio < 0.65:
            Q, v, h = orifice_flow(b, e, H)
            formula = "Q=ε·b·e·√(2gH)"
        elif ratio > 0.80:
            Q = weir_flow(b, H)
            formula = "Q=m·b·H^(3/2)·√(2g)"
        else:
            Q = transition_flow(b, e, H)
            formula = "插值法"
        
        print(f"{e:<8.1f} {ratio:<10.2f} {flow_type:<20} {formula:<25} {Q:<12.1f}")
    
    print(f"\n分析：")
    print(f"  • 所有工况均为孔流（e/H < 0.65）")
    print(f"  • 流量与开度e成正比")
    print(f"  • 开度加倍，流量加倍")
    
    # 绘图
    print(f"\n正在生成综合分析图...")
    plot_sluice_gate_analysis()
    
    print(f"\n" + "="*70)
    print("闸孔出流计算完成！")
    print("="*70)


def exercise():
    """练习题"""
    print("\n" + "="*70)
    print("【练习题】")
    print("="*70)
    
    print("""
    1. 如果开度e=4.5m，流型是什么？流量多少？
    2. 下游水深H₂=4.0m时，是否为淹没出流？
    3. 如何选择闸门开度以获得最大流量？
    4. 孔流与堰流的本质区别是什么？
    
    提示：
    - e=4.5m时，e/H=0.90 > 0.80 → 堰流
    - H₂/H₁=0.80 > 0.75 → 淹没出流
    - 最大流量：全开（e=d）且不淹没
    - 孔流：闸下收缩；堰流：堰顶跌落
    """)


if __name__ == "__main__":
    main()
    exercise()
