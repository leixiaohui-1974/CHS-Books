#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
薄壁堰流量测量与计算

问题：第五章题86 - 薄壁堰流量计算与测流
描述：矩形堰和三角堰流量公式应用与比较

知识点：
1. 矩形薄壁堰公式：Q = (2/3)·m·b·√(2g)·H^(3/2)
2. 三角形堰公式：Q = (8/15)·m·tan(α/2)·√(2g)·H^(5/2)
3. 流量系数m的影响
4. 堰型选择与适用范围

作者：CHS-Books项目组
日期：2025-11-01
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def rectangular_weir_flow(b, H, m=0.42, g=9.81):
    """
    矩形薄壁堰流量计算
    
    Q = (2/3)·m·b·√(2g)·H^(3/2)
    
    参数:
        b: 堰宽 (m)
        H: 堰顶水头 (m)
        m: 流量系数（默认0.42）
        g: 重力加速度 (m/s²)
    
    返回:
        Q: 流量 (m³/s)
        v: 平均流速 (m/s)
    """
    Q = (2/3) * m * b * np.sqrt(2*g) * H**(3/2)
    v = Q / (b * H)  # 近似流速
    return Q, v


def triangular_weir_flow(H, theta=90, m=0.42, g=9.81):
    """
    三角形薄壁堰流量计算
    
    Q = (8/15)·m·tan(θ/2)·√(2g)·H^(5/2)
    
    参数:
        H: 堰顶水头 (m)
        theta: 堰口角度（度）
        m: 流量系数（默认0.42）
        g: 重力加速度 (m/s²)
    
    返回:
        Q: 流量 (m³/s)
    """
    theta_rad = np.deg2rad(theta)
    Q = (8/15) * m * np.tan(theta_rad/2) * np.sqrt(2*g) * H**(5/2)
    return Q


def solve_head_from_flow_rectangular(Q, b, m=0.42, g=9.81):
    """
    已知流量求堰顶水头（矩形堰）
    
    H = (Q / ((2/3)·m·b·√(2g)))^(2/3)
    
    参数:
        Q: 流量 (m³/s)
        b: 堰宽 (m)
        m: 流量系数
        g: 重力加速度 (m/s²)
    
    返回:
        H: 堰顶水头 (m)
    """
    coeff = (2/3) * m * b * np.sqrt(2*g)
    H = (Q / coeff)**(2/3)
    return H


def solve_head_from_flow_triangular(Q, theta=90, m=0.42, g=9.81):
    """
    已知流量求堰顶水头（三角堰）
    
    H = (Q / ((8/15)·m·tan(θ/2)·√(2g)))^(2/5)
    
    参数:
        Q: 流量 (m³/s)
        theta: 堰口角度（度）
        m: 流量系数
        g: 重力加速度 (m/s²)
    
    返回:
        H: 堰顶水头 (m)
    """
    theta_rad = np.deg2rad(theta)
    coeff = (8/15) * m * np.tan(theta_rad/2) * np.sqrt(2*g)
    H = (Q / coeff)**(2/5)
    return H


def weir_sensitivity_analysis(b, H_range, m_values):
    """
    流量系数敏感性分析
    
    参数:
        b: 堰宽 (m)
        H_range: 水头范围数组 (m)
        m_values: 流量系数数组
    
    返回:
        Q_matrix: 流量矩阵 [len(m_values), len(H_range)]
    """
    Q_matrix = np.zeros((len(m_values), len(H_range)))
    
    for i, m in enumerate(m_values):
        for j, H in enumerate(H_range):
            Q_matrix[i, j], _ = rectangular_weir_flow(b, H, m)
    
    return Q_matrix


def plot_weir_analysis(filename='weir_sharp_crested.png'):
    """
    绘制薄壁堰综合分析图（6子图）
    
    参数:
        filename: 保存文件名
    """
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # 参数设置
    b_rect = 1.5  # 矩形堰宽
    theta_tri = 90  # 三角堰角度
    m = 0.42
    g = 9.81
    
    # 子图1：矩形堰Q-H曲线
    ax1 = fig.add_subplot(gs[0, 0])
    
    H_range = np.linspace(0.05, 0.6, 100)
    Q_rect = np.array([rectangular_weir_flow(b_rect, H, m, g)[0] for H in H_range])
    
    ax1.plot(H_range, Q_rect, 'b-', linewidth=2.5, label=f'矩形堰 b={b_rect}m')
    
    # 标注设计点
    H_design = 0.35
    Q_design, _ = rectangular_weir_flow(b_rect, H_design, m, g)
    ax1.plot(H_design, Q_design, 'ro', markersize=10, 
             label=f'设计点 H={H_design}m, Q={Q_design:.3f}m³/s')
    
    ax1.set_xlabel('堰顶水头 H (m)', fontsize=12)
    ax1.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax1.set_title('矩形薄壁堰流量曲线', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 子图2：三角堰Q-H曲线
    ax2 = fig.add_subplot(gs[0, 1])
    
    Q_tri = np.array([triangular_weir_flow(H, theta_tri, m, g) for H in H_range])
    
    ax2.plot(H_range, Q_tri, 'g-', linewidth=2.5, label=f'三角堰 θ={theta_tri}°')
    
    # 同流量下水头对比
    H_tri_same_Q = solve_head_from_flow_triangular(Q_design, theta_tri, m, g)
    ax2.plot(H_tri_same_Q, Q_design, 'ro', markersize=10,
             label=f'同流量点 H={H_tri_same_Q:.3f}m')
    
    ax2.set_xlabel('堰顶水头 H (m)', fontsize=12)
    ax2.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax2.set_title('三角形薄壁堰流量曲线', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 子图3：矩形vs三角堰对比
    ax3 = fig.add_subplot(gs[1, 0])
    
    ax3.plot(H_range, Q_rect, 'b-', linewidth=2.5, label='矩形堰')
    ax3.plot(H_range, Q_tri, 'g-', linewidth=2.5, label='三角堰90°')
    
    # 填充小流量优势区
    idx_small = H_range < 0.3
    ax3.fill_between(H_range[idx_small], Q_tri[idx_small], alpha=0.2, 
                     color='green', label='三角堰优势区')
    
    # 填充大流量优势区
    idx_large = H_range > 0.3
    ax3.fill_between(H_range[idx_large], Q_rect[idx_large], alpha=0.2, 
                     color='blue', label='矩形堰优势区')
    
    ax3.set_xlabel('堰顶水头 H (m)', fontsize=12)
    ax3.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax3.set_title('矩形堰与三角堰对比', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # 子图4：流量系数m影响
    ax4 = fig.add_subplot(gs[1, 1])
    
    m_values = [0.38, 0.40, 0.42, 0.44, 0.46]
    colors = plt.cm.viridis(np.linspace(0, 1, len(m_values)))
    
    for i, m_val in enumerate(m_values):
        Q_m = np.array([rectangular_weir_flow(b_rect, H, m_val, g)[0] for H in H_range])
        ax4.plot(H_range, Q_m, linewidth=2, color=colors[i], label=f'm={m_val}')
    
    ax4.set_xlabel('堰顶水头 H (m)', fontsize=12)
    ax4.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax4.set_title('流量系数m对流量的影响', fontsize=14, fontweight='bold')
    ax4.legend(fontsize=10, loc='upper left')
    ax4.grid(True, alpha=0.3)
    
    # 子图5：测流精度分析
    ax5 = fig.add_subplot(gs[2, 0])
    
    # 相对误差 ΔQ/Q vs H
    delta_m = 0.02  # 流量系数误差
    relative_error = []
    
    for H in H_range:
        Q0, _ = rectangular_weir_flow(b_rect, H, m, g)
        Q1, _ = rectangular_weir_flow(b_rect, H, m+delta_m, g)
        rel_err = abs(Q1 - Q0) / Q0 * 100
        relative_error.append(rel_err)
    
    ax5.plot(H_range, relative_error, 'r-', linewidth=2.5)
    ax5.axhline(5, color='orange', linestyle='--', linewidth=1.5, label='±5%精度线')
    
    ax5.set_xlabel('堰顶水头 H (m)', fontsize=12)
    ax5.set_ylabel('流量相对误差 (%)', fontsize=12)
    ax5.set_title(f'测流精度分析（Δm=±{delta_m}）', fontsize=14, fontweight='bold')
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3)
    
    # 子图6：堰型选择建议
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.axis('off')
    
    info_text = """
    【薄壁堰测流选型指南】
    
    矩形薄壁堰：
      适用流量：Q > 0.1 m³/s
      优点：
        • 量程大（0.1-10 m³/s）
        • 精度高（±2%）
        • 适合中大流量
      缺点：
        • 小流量误差大
        • 需要较宽渠道
      
      公式：Q = (2/3)·m·b·H^(3/2)·√(2g)
      流量系数：m = 0.40~0.45
    
    三角形薄壁堰（90°）：
      适用流量：Q < 0.5 m³/s
      优点：
        • 小流量精度高（±1%）
        • 对水头变化敏感
        • 不需要测量堰宽
      缺点：
        • 大流量水头过大
        • 量程较小
      
      公式：Q = (8/15)·m·tan(45°)·H^(5/2)·√(2g)
      流量系数：m = 0.40~0.45
    
    选型建议：
      Q < 0.2 m³/s    → 三角堰（小流量高精度）
      0.2~1.0 m³/s    → 矩形堰或三角堰
      Q > 1.0 m³/s    → 矩形堰（大流量）
    
    工程应用：
      • 水文测站流量监测
      • 灌溉渠道配水
      • 污水处理流量计量
      • 实验室流量标定
    
    注意事项：
      ✓ 堰板垂直，堰顶锋利
      ✓ 堰前充分通气
      ✓ H测量准确（±1mm）
      ✓ 最小水头Hmin>5cm
    """
    
    ax6.text(0.05, 0.95, info_text, transform=ax6.transAxes,
             fontsize=9, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
    
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\n图片已保存：{filename}")
    plt.close()


def main():
    """
    主程序：第五章题86 - 薄壁堰流量计算
    """
    print("="*70)
    print("第五章题86 - 薄壁堰流量计算与测流")
    print("="*70)
    
    # 题目数据
    b = 1.5         # 矩形堰宽 (m)
    H_rect = 0.35   # 矩形堰水头 (m)
    m = 0.42        # 流量系数
    theta = 90      # 三角堰角度 (度)
    
    print(f"\n【题目】")
    print(f"矩形薄壁堰，堰宽b={b}m，堰顶水头H={H_rect}m")
    print(f"流量系数m={m}")
    print(f"求：(1) 通过流量Q")
    print(f"    (2) 若改用90°三角堰，相同流量下的水头")
    print(f"    (3) 分析两种堰的适用范围")
    
    # (1) 矩形堰流量
    print(f"\n【解】")
    print(f"\n(1) 矩形薄壁堰流量：")
    Q_rect, v_rect = rectangular_weir_flow(b, H_rect, m)
    print(f"    Q = (2/3)×m×b×√(2g)×H^(3/2)")
    print(f"      = (2/3)×{m}×{b}×√(2×9.81)×{H_rect}^(3/2)")
    print(f"      = {Q_rect:.4f} m³/s")
    print(f"      ≈ {Q_rect:.3f} m³/s")
    
    # (2) 三角堰水头
    print(f"\n(2) 三角形堰水头（相同流量）：")
    H_tri = solve_head_from_flow_triangular(Q_rect, theta, m)
    Q_tri_check = triangular_weir_flow(H_tri, theta, m)
    
    print(f"    Q = (8/15)×m×tan(θ/2)×√(2g)×H'^(5/2)")
    print(f"    {Q_rect:.4f} = (8/15)×{m}×tan(45°)×√(2×9.81)×H'^(5/2)")
    print(f"    H' = {H_tri:.4f} m")
    print(f"      ≈ {H_tri:.3f} m")
    print(f"\n    验证：Q' = {Q_tri_check:.4f} m³/s ✓")
    print(f"\n    水头比：H'/H = {H_tri/H_rect:.2f}")
    print(f"    结论：三角堰水头是矩形堰的{H_tri/H_rect:.2f}倍")
    
    # (3) 适用范围对比
    print(f"\n(3) 适用范围对比：")
    print(f"\n    {'堰型':<12} {'适用流量':<20} {'优点':<25} {'缺点':<20}")
    print(f"    {'-'*80}")
    print(f"    {'矩形堰':<12} {'中大流量>0.1m³/s':<20} {'精度高、量程大':<25} {'小流量误差大':<20}")
    print(f"    {'三角堰':<12} {'小流量<0.5m³/s':<20} {'小流量精度高':<25} {'大流量水头过大':<20}")
    
    print(f"\n    本例流量Q={Q_rect:.3f} m³/s：")
    print(f"      • 矩形堰：H={H_rect}m（合适）✓")
    print(f"      • 三角堰：H={H_tri:.3f}m（水头较大，但可用）")
    print(f"      • 建议：优先选用矩形堰")
    
    # 绘图
    print(f"\n正在生成综合分析图...")
    plot_weir_analysis()
    
    print(f"\n" + "="*70)
    print("薄壁堰流量计算完成！")
    print("="*70)


def exercise():
    """练习题"""
    print("\n" + "="*70)
    print("【练习题】")
    print("="*70)
    
    print("""
    1. 如果流量系数从0.42变为0.40，流量变化多少？
    2. 对于Q=0.05 m³/s的小流量，应选择哪种堰？
    3. 如何标定和校准薄壁堰的流量系数？
    4. 堰顶水头测量误差±5mm时，流量误差是多少？
    
    提示：
    - 流量与m成正比
    - 小流量(<0.2 m³/s)选三角堰
    - 标定：用标准容积法或流速仪法
    - 矩形堰：ΔQ/Q = (3/2)×ΔH/H
    """)


if __name__ == "__main__":
    main()
    exercise()
