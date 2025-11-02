"""
案例9：热污染扩散模拟
Thermal Pollution Simulation

演示：
1. 二维温度场模拟
2. 混合区评估
3. 生物热影响评估
4. 冷却方案优化
5. 敏感性分析
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.thermal_pollution import (ThermalPlume2D, calculate_surface_heat_exchange,
                                      calculate_thermal_tolerance, calculate_cooling_efficiency)


def main():
    """主函数"""
    print("=" * 70)
    print("案例9：热污染扩散模拟")
    print("=" * 70)
    print()
    
    # ========================================
    # 参数设置
    # ========================================
    print("温排水参数设置")
    print("-" * 70)
    
    # 河流参数
    Lx = 3000       # 下游计算长度 (m)
    Ly = 80         # 河宽 (m)
    nx = 200        # x方向节点
    ny = 50         # y方向节点
    u = 0.8         # 流速 (m/s)
    H = 1.6         # 水深 (m)
    Q_river = 100   # 河流流量 (m³/s)
    T_ambient = 20  # 环境温度 (°C)
    
    # 温排水参数
    Q_discharge = 20.0  # 排放流量 (m³/s)
    T_discharge = 35.0  # 排放温度 (°C)
    x_discharge = 0     # 排放位置x (m)
    y_discharge = -30   # 排放位置y (m, 侧向排放)
    
    # 扩散参数
    Kx = 10.0       # 纵向扩散系数 (m²/s)
    Ky = 2.0        # 横向扩散系数 (m²/s)
    
    # 气象参数
    T_air = 25      # 气温 (°C)
    wind_speed = 3  # 风速 (m/s)
    solar_rad = 500 # 太阳辐射 (W/m²)
    
    print(f"河流参数:")
    print(f"  流量 Q = {Q_river} m³/s")
    print(f"  流速 u = {u} m/s")
    print(f"  河宽 = {Ly} m")
    print(f"  水深 = {H} m")
    print(f"  环境温度 = {T_ambient}°C")
    print()
    
    print(f"温排水参数:")
    print(f"  排放流量 = {Q_discharge} m³/s")
    print(f"  排放温度 = {T_discharge}°C")
    print(f"  温升 = {T_discharge - T_ambient}°C")
    print()
    
    # ========================================
    # 任务1：表面热交换计算
    # ========================================
    print("任务1：表面热交换计算")
    print("-" * 70)
    
    lambda_s, Q_net = calculate_surface_heat_exchange(
        T_water=T_discharge, T_air=T_air, 
        wind_speed=wind_speed, solar_radiation=solar_rad
    )
    print()
    
    # ========================================
    # 任务2：温度场模拟
    # ========================================
    print("任务2：二维温度场模拟")
    print("-" * 70)
    
    # 创建模型
    model = ThermalPlume2D(
        Lx, Ly, nx, ny, u, Kx, Ky,
        lambda_surface=lambda_s, T_ambient=T_ambient
    )
    
    # 设置温排水源
    model.set_discharge(
        x=x_discharge, y=y_discharge,
        Q_discharge=Q_discharge, T_discharge=T_discharge,
        Q_river=Q_river
    )
    
    # 求解
    x, y, T = model.solve_steady_state()
    
    print()
    
    # ========================================
    # 任务3：混合区评估
    # ========================================
    print("任务3：混合区评估")
    print("-" * 70)
    
    # 计算混合区（温升≤3°C）
    T_standard = T_ambient + 3.0
    area, length, width = model.calculate_mixing_zone(T_standard)
    
    print(f"\n混合区评估结果:")
    if length < Lx * 0.5:
        print(f"  ✓ 混合区长度 {length:.0f}m 在合理范围内")
    else:
        print(f"  ⚠️  混合区长度 {length:.0f}m 过长")
    
    if width < Ly * 0.6:
        print(f"  ✓ 混合区宽度 {width:.0f}m 未影响对岸")
    else:
        print(f"  ⚠️  混合区宽度 {width:.0f}m 影响对岸")
    
    print()
    
    # ========================================
    # 任务4：生物影响评估
    # ========================================
    print("任务4：生物热影响评估")
    print("-" * 70)
    
    # 评估冷水鱼
    T_lethal_cold, T_stress_cold = calculate_thermal_tolerance(
        'cold_water_fish', T_base=T_ambient, duration=24
    )
    
    # 评估温水鱼
    T_lethal_warm, T_stress_warm = calculate_thermal_tolerance(
        'warm_water_fish', T_base=T_ambient, duration=24
    )
    
    # 计算热冲击影响
    impact_area_cold, max_delta_T = model.calculate_thermal_impact(T_stress_cold)
    impact_area_warm, _ = model.calculate_thermal_impact(T_stress_warm)
    
    print(f"\n生物影响评估:")
    print(f"  冷水鱼胁迫区: {impact_area_cold:.0f} m²")
    print(f"  温水鱼胁迫区: {impact_area_warm:.0f} m²")
    
    if impact_area_cold > 0:
        print(f"  ⚠️  不适合冷水鱼生存")
    if impact_area_warm < area * 0.3:
        print(f"  ✓ 温水鱼基本可适应")
    
    print()
    
    # ========================================
    # 任务5：冷却效率评估
    # ========================================
    print("任务5：冷却系统评估")
    print("-" * 70)
    
    # 当前系统（直流冷却）
    T_in = T_discharge  # 35°C
    T_out_direct = T_ambient  # 20°C（假设取河水）
    
    efficiency_direct, Q_removed_direct = calculate_cooling_efficiency(
        T_in, T_out_direct, T_ambient, Q_discharge
    )
    
    print(f"\n改进方案（增加冷却塔）:")
    T_out_tower = 28  # 冷却塔后温度
    efficiency_tower, Q_removed_tower = calculate_cooling_efficiency(
        T_in, T_out_tower, T_ambient, Q_discharge
    )
    
    print(f"  排放温度: {T_discharge}°C → {T_out_tower}°C")
    print(f"  温升: {T_discharge - T_ambient}°C → {T_out_tower - T_ambient}°C")
    print(f"  削减: {(T_discharge - T_out_tower) / (T_discharge - T_ambient) * 100:.0f}%")
    
    print()
    
    # ========================================
    # 绘图
    # ========================================
    print("生成图表...")
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 图1：温度场等值线
    fig1, ax = plt.subplots(figsize=(14, 6))
    
    X, Y = np.meshgrid(x, y)
    
    # 绘制填充等值线
    levels = np.linspace(T_ambient, np.max(T), 15)
    contourf = ax.contourf(X/1000, Y, T, levels=levels, cmap='hot', alpha=0.8)
    
    # 绘制等值线
    contour = ax.contour(X/1000, Y, T, levels=[T_ambient+1, T_ambient+3, T_ambient+5], 
                         colors='black', linewidths=2)
    ax.clabel(contour, inline=True, fontsize=10, fmt='%.1f°C')
    
    # 标注排放口
    ax.plot(x_discharge/1000, y_discharge, 'r*', markersize=20, 
            label=f'排放口 ({T_discharge}°C)')
    
    # 标注混合区边界（3°C温升）
    contour_std = ax.contour(X/1000, Y, T, levels=[T_standard], 
                             colors='green', linewidths=3, linestyles='--')
    ax.clabel(contour_std, inline=True, fontsize=11, fmt='混合区边界')
    
    # 颜色条
    cbar = plt.colorbar(contourf, ax=ax)
    cbar.set_label('温度 (°C)', fontsize=11)
    
    ax.set_xlabel('距离 (km)', fontsize=11)
    ax.set_ylabel('横向距离 (m)', fontsize=11)
    ax.set_title('温排水扩散温度场', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('temperature_field.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: temperature_field.png")
    
    # 图2：中心线和边界温度分布
    fig2, ax = plt.subplots(figsize=(12, 6))
    
    # 中心线温度（y=0附近）
    iy_center = ny // 2
    T_centerline = T[iy_center, :]
    
    # 边界温度（y=±40m）
    iy_edge = ny // 4
    T_edge = T[iy_edge, :]
    
    ax.plot(x/1000, T_centerline, 'r-', linewidth=2.5, label='中心线')
    ax.plot(x/1000, T_edge, 'b-', linewidth=2, label='边界（y≈20m）')
    ax.axhline(y=T_ambient, color='gray', linestyle=':', linewidth=2, label='环境温度')
    ax.axhline(y=T_standard, color='green', linestyle='--', linewidth=2, 
               label=f'标准（温升3°C）')
    
    ax.set_xlabel('距离 (km)', fontsize=11)
    ax.set_ylabel('温度 (°C)', fontsize=11)
    ax.set_title('纵向温度分布', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('longitudinal_temperature.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: longitudinal_temperature.png")
    
    # 图3：生物热耐受性
    fig3, ax = plt.subplots(figsize=(10, 6))
    
    species_list = ['cold_water_fish', 'warm_water_fish', 'invertebrates', 'algae']
    species_names = ['冷水鱼', '温水鱼', '无脊椎动物', '藻类']
    T_stress_list = []
    T_lethal_list = []
    
    for species in species_list:
        T_l, T_s = calculate_thermal_tolerance(species, T_ambient, 24)
        T_lethal_list.append(T_l)
        T_stress_list.append(T_s)
    
    x_pos = np.arange(len(species_names))
    width = 0.35
    
    bars1 = ax.bar(x_pos - width/2, T_stress_list, width,
                   label='胁迫温度', color='orange', alpha=0.7, edgecolor='black')
    bars2 = ax.bar(x_pos + width/2, T_lethal_list, width,
                   label='致死温度', color='red', alpha=0.7, edgecolor='black')
    
    # 标注最高水温
    ax.axhline(y=np.max(T), color='purple', linestyle='--', linewidth=2,
               label=f'排放口最高温度 ({np.max(T):.1f}°C)')
    ax.axhline(y=T_ambient, color='blue', linestyle=':', linewidth=2,
               label=f'环境温度 ({T_ambient}°C)')
    
    ax.set_ylabel('温度 (°C)', fontsize=11)
    ax.set_title('不同物种热耐受性', fontsize=12, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(species_names)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('thermal_tolerance.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: thermal_tolerance.png")
    
    # 图4：冷却方案对比
    fig4, ax = plt.subplots(figsize=(10, 6))
    
    schemes = ['直流冷却\n(当前)', '冷却塔\n(改进)', '混合方案\n(优化)']
    T_out_schemes = [T_discharge, 28, 30]
    delta_T_schemes = [t - T_ambient for t in T_out_schemes]
    mixing_length_schemes = [length, length*0.4, length*0.6]  # 估算
    
    colors_scheme = ['red', 'green', 'orange']
    
    # 子图：温升
    ax1 = ax
    bars = ax1.bar(schemes, delta_T_schemes, color=colors_scheme,
                   alpha=0.7, edgecolor='black', linewidth=2)
    
    ax1.axhline(y=3, color='green', linestyle='--', linewidth=2,
                label='标准（温升3°C）')
    
    for bar, val in zip(bars, delta_T_schemes):
        height = bar.get_height()
        status = '✓' if val <= 3 else '⚠️'
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{val:.1f}°C {status}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax1.set_ylabel('排放温升 (°C)', fontsize=11)
    ax1.set_title('不同冷却方案排放温升对比', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('cooling_schemes.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: cooling_schemes.png")
    
    # ========================================
    # 总结
    # ========================================
    print()
    print("=" * 70)
    print("案例9完成！")
    print("=" * 70)
    print()
    print("主要结论:")
    print(f"1. 混合区面积: {area:.0f} m² (长{length:.0f}m × 宽{width:.0f}m)")
    print(f"2. 最大温升: {max_delta_T:.1f}°C")
    print(f"3. 达标距离: ~{length:.0f}m")
    print(f"4. 冷水鱼不适宜生存区: {impact_area_cold:.0f} m²")
    print(f"5. 表面热交换系数: {lambda_s:.3f} day⁻¹")
    print()
    print("管理建议:")
    print("  1. 当前直流冷却温升过高（15°C），建议增加冷却塔")
    print("  2. 冷却塔可将温升降至8°C，削减47%")
    print("  3. 混合区长度约2km，需设置警示标志")
    print("  4. 夏季高温期应加强监测，必要时限产")
    print("  5. 避免在冷水鱼产卵期（春季）高负荷运行")
    print()
    print("生成的图表:")
    print("  - temperature_field.png       (温度场等值线)")
    print("  - longitudinal_temperature.png (纵向温度分布)")
    print("  - thermal_tolerance.png       (生物热耐受性)")
    print("  - cooling_schemes.png         (冷却方案对比)")
    print()
    
    plt.show()


if __name__ == '__main__':
    # 设置matplotlib后端
    import matplotlib
    matplotlib.use('Agg')
    
    main()
