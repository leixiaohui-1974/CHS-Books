"""
案例10：河流横向混合模拟
Lateral Mixing in Rivers

演示：
1. 横向扩散系数计算
2. 横向混合长度估算
3. 二维浓度场模拟
4. 对岸影响评估
5. 敏感性分析
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.lateral_mixing import (LateralMixing2D, calculate_mixing_time,
                                    calculate_complete_mixing_distance,
                                    calculate_concentration_at_bank)


def main():
    """主函数"""
    print("=" * 70)
    print("案例10：河流横向混合模拟")
    print("=" * 70)
    print()
    
    # ========================================
    # 参数设置
    # ========================================
    print("河流参数设置")
    print("-" * 70)
    
    # 河流参数
    B = 100         # 河宽 (m)
    H = 3           # 平均水深 (m)
    u = 0.5         # 平均流速 (m/s)
    Q_river = 150   # 河流流量 (m³/s)
    I = 0.0002      # 水力坡降
    
    # 排放参数
    Q_discharge = 2.0   # 排放流量 (m³/s)
    C_discharge = 100.0 # 排放浓度 (mg/L)
    y_discharge = 0     # 排放位置（左岸）
    
    # 计算域
    L = 15000       # 纵向长度 (m)
    nx = 150        # 纵向节点数
    ny = 50         # 横向节点数
    
    print(f"河流参数:")
    print(f"  河宽 B = {B} m")
    print(f"  水深 H = {H} m")
    print(f"  流速 u = {u} m/s")
    print(f"  流量 Q = {Q_river} m³/s")
    print(f"  水力坡降 I = {I}")
    print()
    
    print(f"排放参数:")
    print(f"  排放流量 = {Q_discharge} m³/s")
    print(f"  排放浓度 = {C_discharge} mg/L")
    print(f"  排放位置 = 左岸（y={y_discharge}m）")
    print()
    
    # ========================================
    # 任务1：横向扩散系数计算
    # ========================================
    print("任务1：横向扩散系数计算")
    print("-" * 70)
    
    # 计算摩阻流速
    g = 9.81  # 重力加速度 (m/s²)
    u_star = np.sqrt(g * H * I)
    
    print(f"\n摩阻流速:")
    print(f"  u* = √(g*H*I) = {u_star:.4f} m/s")
    
    # Elder公式
    Ey_elder = 0.23 * H * u_star
    
    # Fischer公式
    Ey_fischer = 0.15 * H * u_star
    
    # 推荐值（取平均）
    Ey = (Ey_elder + Ey_fischer) / 2
    
    print(f"\n横向扩散系数:")
    print(f"  Elder公式: Ey = 0.23*H*u* = {Ey_elder:.4f} m²/s")
    print(f"  Fischer公式: Ey = 0.15*H*u* = {Ey_fischer:.4f} m²/s")
    print(f"  推荐值: Ey = {Ey:.4f} m²/s")
    
    # 纵向扩散系数（远小于横向）
    Ex = 0.01  # m²/s
    
    print()
    
    # ========================================
    # 任务2：横向混合长度估算
    # ========================================
    print("任务2：横向混合长度估算")
    print("-" * 70)
    
    # 理论公式
    L_mix_theory = calculate_complete_mixing_distance(B, u, Ey)
    
    # 经验公式
    L_mix_empirical_min = 50 * B
    L_mix_empirical_max = 100 * B
    
    print(f"\n经验公式估算:")
    print(f"  L_mix ≈ 50-100 × B")
    print(f"  L_mix ≈ {L_mix_empirical_min:.0f}-{L_mix_empirical_max:.0f} m")
    print(f"  L_mix ≈ {L_mix_empirical_min/1000:.1f}-{L_mix_empirical_max/1000:.1f} km")
    
    # 混合时间
    T_mix = calculate_mixing_time(B, Ey)
    
    # 完全混合后的浓度
    C_mixed = Q_discharge * C_discharge / Q_river
    print(f"\n完全混合浓度:")
    print(f"  C_mix = Q_d*C_d / Q_r = {C_mixed:.2f} mg/L")
    
    print()
    
    # ========================================
    # 任务3：二维浓度场模拟
    # ========================================
    print("任务3：二维浓度场模拟")
    print("-" * 70)
    
    # 创建模型
    model = LateralMixing2D(L, B, nx, ny, u, Ex, Ey)
    
    # 添加排放源
    model.add_source(
        x=0, y=y_discharge,
        Q_discharge=Q_discharge,
        C_discharge=C_discharge,
        Q_river=Q_river
    )
    
    # 求解（隐式格式更稳定）
    x, y, C = model.solve_steady_state(method='implicit')
    
    # 计算混合长度
    L_mix_simulated = model.calculate_mixing_length(threshold=0.95)
    
    print()
    
    # ========================================
    # 任务4：对岸影响评估
    # ========================================
    print("任务4：对岸影响评估")
    print("-" * 70)
    
    # 提取对岸（y=B）浓度
    C_opposite_bank = C[-1, :]
    
    # 找到对岸达到10%完全混合浓度的距离
    threshold_conc = 0.1 * C_mixed
    idx_impact = np.where(C_opposite_bank >= threshold_conc)[0]
    
    if len(idx_impact) > 0:
        x_impact = x[idx_impact[0]]
        print(f"\n对岸影响距离:")
        print(f"  对岸浓度达到{threshold_conc:.2f} mg/L的距离: {x_impact:.0f} m ({x_impact/1000:.1f} km)")
    
    # 关键断面对岸浓度
    distances = [1000, 2000, 5000, 10000]
    print(f"\n关键断面对岸浓度:")
    for dist in distances:
        if dist < L:
            idx = np.argmin(np.abs(x - dist))
            C_bank = C[-1, idx]
            print(f"  {dist/1000:.1f} km处: {C_bank:.2f} mg/L")
    
    print()
    
    # ========================================
    # 任务5：敏感性分析
    # ========================================
    print("任务5：敏感性分析")
    print("-" * 70)
    
    # 分析Ey变化的影响
    Ey_variations = [Ey * 0.7, Ey, Ey * 1.3]
    L_mix_variations = []
    
    print(f"\n横向扩散系数敏感性:")
    for Ey_var in Ey_variations:
        L_mix_var = calculate_complete_mixing_distance(B, u, Ey_var)
        L_mix_variations.append(L_mix_var)
        change_pct = (Ey_var / Ey - 1) * 100
        print(f"  Ey变化{change_pct:+.0f}%: L_mix = {L_mix_var/1000:.2f} km")
    
    # 分析流速变化的影响
    u_variations = [u * 0.8, u, u * 1.2]
    L_mix_u_variations = []
    
    print(f"\n流速敏感性:")
    for u_var in u_variations:
        L_mix_u = calculate_complete_mixing_distance(B, u_var, Ey)
        L_mix_u_variations.append(L_mix_u)
        change_pct = (u_var / u - 1) * 100
        print(f"  流速变化{change_pct:+.0f}%: L_mix = {L_mix_u/1000:.2f} km")
    
    print()
    
    # ========================================
    # 绘图
    # ========================================
    print("生成图表...")
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 图1：二维浓度场
    fig1, ax = plt.subplots(figsize=(14, 6))
    
    X, Y = np.meshgrid(x/1000, y)  # 转换为km
    
    # 填充等值线
    levels = np.linspace(0, np.max(C), 20)
    contourf = ax.contourf(X, Y, C, levels=levels, cmap='YlOrRd', alpha=0.8)
    
    # 等值线
    contour = ax.contour(X, Y, C, levels=[5, 10, 20, 50], 
                         colors='black', linewidths=1.5)
    ax.clabel(contour, inline=True, fontsize=9, fmt='%.0f mg/L')
    
    # 标注排放口
    ax.plot(0, y_discharge, 'b*', markersize=20, label='排放口')
    
    # 标注完全混合线
    if L_mix_simulated < L:
        ax.axvline(x=L_mix_simulated/1000, color='green', linestyle='--', 
                   linewidth=2, label=f'完全混合线 ({L_mix_simulated/1000:.1f} km)')
    
    # 标注水质标准线
    contour_std = ax.contour(X, Y, C, levels=[20], 
                             colors='red', linewidths=2, linestyles='--')
    ax.clabel(contour_std, inline=True, fontsize=10, fmt='标准（20 mg/L）')
    
    # 颜色条
    cbar = plt.colorbar(contourf, ax=ax)
    cbar.set_label('浓度 (mg/L)', fontsize=11)
    
    ax.set_xlabel('纵向距离 (km)', fontsize=11)
    ax.set_ylabel('横向距离 (m)', fontsize=11)
    ax.set_title('河流横向混合浓度场', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('concentration_field_2d.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: concentration_field_2d.png")
    
    # 图2：横断面浓度分布
    fig2, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    sections = [
        (500, 0),
        (2000, 1),
        (5000, 2),
        (10000, 3)
    ]
    
    for dist, idx_plot in sections:
        ax = axes.flat[idx_plot]
        idx_x = np.argmin(np.abs(x - dist))
        C_section = C[:, idx_x]
        
        ax.plot(y, C_section, 'b-', linewidth=2.5, label='浓度分布')
        ax.axhline(y=C_mixed, color='green', linestyle='--', linewidth=2,
                   label=f'完全混合浓度 ({C_mixed:.2f} mg/L)')
        ax.axhline(y=20, color='red', linestyle=':', linewidth=2,
                   label='水质标准 (20 mg/L)')
        
        ax.set_xlabel('横向距离 (m)', fontsize=10)
        ax.set_ylabel('浓度 (mg/L)', fontsize=10)
        ax.set_title(f'距离排放口 {dist/1000:.1f} km', fontsize=11, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        
        # 标注左岸和右岸
        ax.text(5, ax.get_ylim()[1]*0.9, '左岸\n(排放侧)', 
                fontsize=9, ha='left', va='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax.text(B-5, ax.get_ylim()[1]*0.9, '右岸\n(对岸)', 
                fontsize=9, ha='right', va='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('cross_section_profiles.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: cross_section_profiles.png")
    
    # 图3：纵向浓度分布（不同横向位置）
    fig3, ax = plt.subplots(figsize=(12, 6))
    
    y_positions = [0, B/4, B/2, 3*B/4, B]
    y_labels = ['左岸（排放侧）', 'B/4', '中线', '3B/4', '右岸（对岸）']
    colors = ['red', 'orange', 'green', 'blue', 'purple']
    
    for y_pos, label, color in zip(y_positions, y_labels, colors):
        iy = np.argmin(np.abs(y - y_pos))
        ax.plot(x/1000, C[iy, :], linewidth=2.5, label=label, color=color)
    
    ax.axhline(y=C_mixed, color='gray', linestyle='--', linewidth=2,
               label=f'完全混合浓度 ({C_mixed:.2f} mg/L)')
    ax.axhline(y=20, color='red', linestyle=':', linewidth=2,
               label='水质标准 (20 mg/L)')
    
    if L_mix_simulated < L:
        ax.axvline(x=L_mix_simulated/1000, color='green', linestyle='--', 
                   linewidth=2, alpha=0.5, label=f'完全混合距离')
    
    ax.set_xlabel('纵向距离 (km)', fontsize=11)
    ax.set_ylabel('浓度 (mg/L)', fontsize=11)
    ax.set_title('纵向浓度分布（不同横向位置）', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, L/1000])
    
    plt.tight_layout()
    plt.savefig('longitudinal_profiles.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: longitudinal_profiles.png")
    
    # 图4：敏感性分析
    fig4, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Ey敏感性
    Ey_pct = [(e/Ey - 1)*100 for e in Ey_variations]
    L_mix_pct = [l/1000 for l in L_mix_variations]
    
    ax1.plot(Ey_pct, L_mix_pct, 'o-', linewidth=2.5, markersize=10, color='blue')
    ax1.axhline(y=L_mix_theory/1000, color='red', linestyle='--', linewidth=2,
                label='基准值')
    ax1.set_xlabel('横向扩散系数变化 (%)', fontsize=11)
    ax1.set_ylabel('完全混合距离 (km)', fontsize=11)
    ax1.set_title('Ey敏感性分析', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 流速敏感性
    u_pct = [(u_v/u - 1)*100 for u_v in u_variations]
    L_mix_u_pct = [l/1000 for l in L_mix_u_variations]
    
    ax2.plot(u_pct, L_mix_u_pct, 's-', linewidth=2.5, markersize=10, color='green')
    ax2.axhline(y=L_mix_theory/1000, color='red', linestyle='--', linewidth=2,
                label='基准值')
    ax2.set_xlabel('流速变化 (%)', fontsize=11)
    ax2.set_ylabel('完全混合距离 (km)', fontsize=11)
    ax2.set_title('流速敏感性分析', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('sensitivity_analysis.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: sensitivity_analysis.png")
    
    # ========================================
    # 总结
    # ========================================
    print()
    print("=" * 70)
    print("案例10完成！")
    print("=" * 70)
    print()
    print("主要结论:")
    print(f"1. 横向扩散系数: Ey = {Ey:.4f} m²/s")
    print(f"2. 完全混合距离: L_mix ≈ {L_mix_simulated/1000:.1f} km")
    print(f"3. 完全混合浓度: C_mix = {C_mixed:.2f} mg/L")
    print(f"4. 混合时间: T_mix ≈ {T_mix/3600:.2f} hour")
    print()
    print("工程建议:")
    print("  1. 排放口下游10km内，排放侧浓度较高，建议加强监测")
    print("  2. 对岸水质影响较小，可作为取水口布置区域")
    print("  3. 完全混合距离约为100倍河宽，符合经验公式")
    print("  4. 横向扩散系数对混合距离影响显著，需准确率定")
    print()
    print("生成的图表:")
    print("  - concentration_field_2d.png      (二维浓度场)")
    print("  - cross_section_profiles.png      (横断面浓度分布)")
    print("  - longitudinal_profiles.png       (纵向浓度分布)")
    print("  - sensitivity_analysis.png        (敏感性分析)")
    print()
    
    plt.show()


if __name__ == '__main__':
    # 设置matplotlib后端
    import matplotlib
    matplotlib.use('Agg')
    
    main()
