"""
案例11：河流弯道水质模拟
River Bend Water Quality Simulation

演示：
1. 弯道几何参数计算
2. 二次流特征分析
3. 弯道浓度场模拟
4. 弯道与直道对比
5. 工程优化建议
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.river_bend import (RiverBend2D, calculate_bend_mixing_length,
                                calculate_curvature_radius, calculate_secondary_flow_strength)
from models.lateral_mixing import LateralMixing2D, calculate_complete_mixing_distance


def main():
    """主函数"""
    print("=" * 70)
    print("案例11：河流弯道水质模拟")
    print("=" * 70)
    print()
    
    # ========================================
    # 参数设置
    # ========================================
    print("河流参数设置")
    print("-" * 70)
    
    # 河流参数
    B = 80          # 河宽 (m)
    H = 2.5         # 水深 (m)
    u = 0.6         # 流速 (m/s)
    Q_river = 120   # 河流流量 (m³/s)
    Ey_straight = 0.05  # 直道横向扩散系数 (m²/s)
    
    # 弯道参数
    bend_length = 1500  # 弯道长度 (m)
    bend_angle = 90     # 转角 (度)
    
    # 排放参数
    Q_discharge = 1.5   # 排放流量 (m³/s)
    C_discharge = 80.0  # 排放浓度 (mg/L)
    y_discharge = 10    # 排放位置（凸岸侧）
    
    # 计算域
    L = 3000        # 纵向长度 (m)
    nx = 150        # 纵向节点数
    ny = 40         # 横向节点数
    
    print(f"河流参数:")
    print(f"  河宽 B = {B} m")
    print(f"  水深 H = {H} m")
    print(f"  流速 u = {u} m/s")
    print(f"  流量 Q = {Q_river} m³/s")
    print(f"  直道Ey = {Ey_straight} m²/s")
    print()
    
    print(f"排放参数:")
    print(f"  排放流量 = {Q_discharge} m³/s")
    print(f"  排放浓度 = {C_discharge} mg/L")
    print(f"  排放位置 = 凸岸侧（y={y_discharge}m）")
    print()
    
    # ========================================
    # 任务1：弯道几何参数
    # ========================================
    print("任务1：弯道几何参数计算")
    print("-" * 70)
    
    # 计算曲率半径
    R = calculate_curvature_radius(bend_length, bend_angle)
    
    # 宽曲比
    width_curvature_ratio = B / R
    print(f"\n宽曲比:")
    print(f"  B/R = {width_curvature_ratio:.4f}")
    
    print()
    
    # ========================================
    # 任务2：二次流特征
    # ========================================
    print("任务2：二次流特征分析")
    print("-" * 70)
    
    v_max, Fr = calculate_secondary_flow_strength(u, R, B, H)
    
    print()
    
    # ========================================
    # 任务3：弯道浓度场模拟
    # ========================================
    print("任务3：弯道浓度场模拟")
    print("-" * 70)
    
    # 创建弯道模型
    model_bend = RiverBend2D(
        L, B, nx, ny, u, Ey_straight, R, bend_angle
    )
    
    # 添加排放源
    model_bend.add_source(
        x=0, y=y_discharge,
        Q_discharge=Q_discharge,
        C_discharge=C_discharge,
        Q_river=Q_river
    )
    
    # 求解
    x, y, C_bend = model_bend.solve_with_secondary_flow()
    
    # 浓度偏向分析
    shift_ratio = model_bend.calculate_concentration_shift()
    
    print()
    
    # ========================================
    # 任务4：直道模拟（对比）
    # ========================================
    print("任务4：直道模拟（对比）")
    print("-" * 70)
    
    # 创建直道模型
    model_straight = LateralMixing2D(
        L, B, nx, ny, u, 0.01, Ey_straight
    )
    
    # 添加排放源（相同位置）
    model_straight.add_source(
        x=0, y=y_discharge,
        Q_discharge=Q_discharge,
        C_discharge=C_discharge,
        Q_river=Q_river
    )
    
    # 求解
    x_s, y_s, C_straight = model_straight.solve_steady_state(method='implicit')
    
    print()
    
    # ========================================
    # 任务5：混合长度对比
    # ========================================
    print("任务5：混合长度对比")
    print("-" * 70)
    
    # 直道混合长度
    L_mix_straight = calculate_complete_mixing_distance(B, u, Ey_straight)
    
    # 弯道混合长度
    L_mix_bend_calc, _ = calculate_bend_mixing_length(
        B, u, Ey_straight, model_bend.K_bend
    )
    
    # 完全混合浓度
    C_mixed = Q_discharge * C_discharge / Q_river
    print(f"\n完全混合浓度:")
    print(f"  C_mix = {C_mixed:.2f} mg/L")
    
    print()
    
    # ========================================
    # 绘图
    # ========================================
    print("生成图表...")
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 图1：弯道与直道浓度场对比
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    X, Y = np.meshgrid(x/1000, y)
    
    # 弯道浓度场
    levels = np.linspace(0, np.max(C_bend), 20)
    contourf1 = ax1.contourf(X, Y, C_bend, levels=levels, cmap='YlOrRd', alpha=0.8)
    contour1 = ax1.contour(X, Y, C_bend, levels=[10, 20, 40], 
                           colors='black', linewidths=1.5)
    ax1.clabel(contour1, inline=True, fontsize=9, fmt='%.0f mg/L')
    ax1.plot(0, y_discharge, 'b*', markersize=15, label='排放口（凸岸）')
    ax1.axhline(y=B, color='red', linestyle='--', alpha=0.5, label='凹岸')
    ax1.axhline(y=0, color='blue', linestyle='--', alpha=0.5, label='凸岸')
    
    cbar1 = plt.colorbar(contourf1, ax=ax1)
    cbar1.set_label('浓度 (mg/L)', fontsize=10)
    ax1.set_xlabel('纵向距离 (km)', fontsize=10)
    ax1.set_ylabel('横向距离 (m)', fontsize=10)
    ax1.set_title(f'弯道浓度场（增强系数K={model_bend.K_bend:.2f}）', 
                  fontsize=11, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 直道浓度场
    contourf2 = ax2.contourf(X, Y, C_straight, levels=levels, cmap='YlOrRd', alpha=0.8)
    contour2 = ax2.contour(X, Y, C_straight, levels=[10, 20, 40], 
                           colors='black', linewidths=1.5)
    ax2.clabel(contour2, inline=True, fontsize=9, fmt='%.0f mg/L')
    ax2.plot(0, y_discharge, 'b*', markersize=15, label='排放口')
    
    cbar2 = plt.colorbar(contourf2, ax=ax2)
    cbar2.set_label('浓度 (mg/L)', fontsize=10)
    ax2.set_xlabel('纵向距离 (km)', fontsize=10)
    ax2.set_ylabel('横向距离 (m)', fontsize=10)
    ax2.set_title('直道浓度场（对比）', fontsize=11, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('bend_vs_straight_field.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: bend_vs_straight_field.png")
    
    # 图2：横断面浓度对比
    fig2, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    sections = [
        (500, 0, '0.5 km'),
        (1000, 1, '1.0 km'),
        (2000, 2, '2.0 km'),
        (3000, 3, '3.0 km')
    ]
    
    for dist, idx_plot, label in sections:
        ax = axes.flat[idx_plot]
        if dist < L:
            idx_x = np.argmin(np.abs(x - dist))
            C_bend_section = C_bend[:, idx_x]
            C_straight_section = C_straight[:, idx_x]
            
            ax.plot(y, C_bend_section, 'r-', linewidth=2.5, label='弯道')
            ax.plot(y, C_straight_section, 'b--', linewidth=2.5, label='直道')
            ax.axhline(y=C_mixed, color='green', linestyle=':', linewidth=2,
                       label=f'完全混合（{C_mixed:.2f} mg/L）')
            
            ax.set_xlabel('横向距离 (m)', fontsize=10)
            ax.set_ylabel('浓度 (mg/L)', fontsize=10)
            ax.set_title(f'断面：{label}', fontsize=11, fontweight='bold')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
            
            # 标注凸岸和凹岸
            ax.axvline(x=0, color='blue', linestyle=':', alpha=0.3)
            ax.axvline(x=B, color='red', linestyle=':', alpha=0.3)
            ax.text(2, ax.get_ylim()[1]*0.9, '凸岸', fontsize=8, color='blue')
            ax.text(B-10, ax.get_ylim()[1]*0.9, '凹岸', fontsize=8, color='red')
    
    plt.tight_layout()
    plt.savefig('cross_section_comparison.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: cross_section_comparison.png")
    
    # 图3：纵向浓度对比（凸岸vs凹岸）
    fig3, ax = plt.subplots(figsize=(12, 6))
    
    # 凸岸（y≈0）
    iy_inner = 2
    C_bend_inner = C_bend[iy_inner, :]
    C_straight_inner = C_straight[iy_inner, :]
    
    # 凹岸（y≈B）
    iy_outer = ny - 3
    C_bend_outer = C_bend[iy_outer, :]
    C_straight_outer = C_straight[iy_outer, :]
    
    ax.plot(x/1000, C_bend_inner, 'b-', linewidth=2.5, label='弯道-凸岸')
    ax.plot(x/1000, C_bend_outer, 'r-', linewidth=2.5, label='弯道-凹岸')
    ax.plot(x/1000, C_straight_inner, 'b--', linewidth=2, label='直道-同侧（近排放口）', alpha=0.7)
    ax.plot(x/1000, C_straight_outer, 'r--', linewidth=2, label='直道-同侧（远排放口）', alpha=0.7)
    ax.axhline(y=C_mixed, color='green', linestyle=':', linewidth=2,
               label=f'完全混合（{C_mixed:.2f} mg/L）')
    
    ax.set_xlabel('纵向距离 (km)', fontsize=11)
    ax.set_ylabel('浓度 (mg/L)', fontsize=11)
    ax.set_title('纵向浓度分布对比', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('longitudinal_comparison.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: longitudinal_comparison.png")
    
    # 图4：混合长度对比
    fig4, ax = plt.subplots(figsize=(10, 6))
    
    categories = ['直道', '弯道']
    L_mix_values = [L_mix_straight/1000, L_mix_bend_calc/1000]
    colors = ['blue', 'red']
    
    bars = ax.bar(categories, L_mix_values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    # 标注数值
    for bar, val in zip(bars, L_mix_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                f'{val:.2f} km',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # 标注缩短比例
    reduction = (1 - L_mix_bend_calc/L_mix_straight) * 100
    ax.text(0.5, max(L_mix_values)*0.5,
            f'缩短{reduction:.0f}%',
            ha='center', fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    ax.set_ylabel('混合长度 (km)', fontsize=11)
    ax.set_title('弯道vs直道混合长度对比', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('mixing_length_comparison.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: mixing_length_comparison.png")
    
    # ========================================
    # 总结
    # ========================================
    print()
    print("=" * 70)
    print("案例11完成！")
    print("=" * 70)
    print()
    print("主要结论:")
    print(f"1. 曲率半径: R = {R:.0f} m")
    print(f"2. 宽曲比: B/R = {width_curvature_ratio:.4f}")
    print(f"3. 弯道增强系数: K = {model_bend.K_bend:.2f}")
    print(f"4. 有效扩散系数: Ey_eff = {model_bend.Ey_effective:.4f} m²/s")
    print(f"5. 最大横向流速: v_max = {v_max:.4f} m/s")
    print(f"6. 直道混合长度: {L_mix_straight/1000:.2f} km")
    print(f"7. 弯道混合长度: {L_mix_bend_calc/1000:.2f} km")
    print(f"8. 缩短比例: {reduction:.0f}%")
    print(f"9. 浓度偏向比: {shift_ratio:.2f}")
    print()
    print("工程建议:")
    print("  1. 弯道段横向混合增强，混合长度缩短约54%")
    print("  2. 排放在凸岸，污染物向凹岸偏移")
    print("  3. 取水口应避开凹岸侧，或布置在弯道上游")
    print("  4. 可利用弯道增强混合，优化排污口选址")
    print("  5. 监测时需注意浓度偏向现象，凹岸侧加密布点")
    print()
    print("生成的图表:")
    print("  - bend_vs_straight_field.png       (弯道vs直道浓度场)")
    print("  - cross_section_comparison.png     (横断面浓度对比)")
    print("  - longitudinal_comparison.png      (纵向浓度对比)")
    print("  - mixing_length_comparison.png     (混合长度对比)")
    print()
    
    plt.show()


if __name__ == '__main__':
    # 设置matplotlib后端
    import matplotlib
    matplotlib.use('Agg')
    
    main()
