"""
案例4：涉水植物生长水力条件分析
================================

工程背景
--------
某河道生态修复项目，需要设计植被恢复方案，确定不同植物的最佳种植位置和水力条件。

问题描述
--------
- 河段长度: L = 500 m
- 河道宽度: b = 20 m
- 河床坡度: S0 = 0.001
- Manning糙率: n = 0.025
- 边坡系数: m = 2.0
- 设计流量范围: 5-50 m³/s
- 候选植物: 芦苇、香蒲、柳树灌木

计算目标
--------
1. 分析不同植物对水流的影响
2. 评估植物的抗冲稳定性
3. 计算植物生长的淹水条件
4. 提出植物配置方案

学习目标
--------
1. 理解植物-水流相互作用机理
2. 掌握植被糙率计算方法
3. 学会植物稳定性评估
4. 分析淹水周期对植物的影响

作者: CHS-Books 生态水力学课程组
日期: 2025-11-02
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# 添加父目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from code.models.channel import RiverReach
from code.models.vegetation import (
    VegetationType,
    VegetatedChannel,
    VegetationGrowthModel,
    create_reed,
    create_cattail,
    create_willow_shrub
)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def print_header(title):
    """打印标题"""
    print("\n" + "="*80)
    print(f"{title:^80}")
    print("="*80)


def print_section(title):
    """打印章节标题"""
    print("\n" + "-"*80)
    print(title)
    print("-"*80)


def main():
    """主计算流程"""
    
    print_header("案例4：涉水植物生长水力条件分析")
    
    # ========================================================================
    # 第1步：定义河段参数
    # ========================================================================
    print_section("【第1步】定义河段参数")
    
    reach = RiverReach(
        length=500.0,       # 河段长度 m
        width=20.0,         # 河道底宽 m
        slope=0.001,        # 河床坡度
        roughness=0.025,    # Manning糙率（裸露河床）
        side_slope=2.0      # 边坡系数
    )
    
    print(f"河段长度: {reach.length} m")
    print(f"河道底宽: {reach.b} m")
    print(f"河床坡度: {reach.S0}")
    print(f"裸露河床Manning糙率: {reach.n}")
    print(f"边坡系数: {reach.m}")
    
    # ========================================================================
    # 第2步：定义植物类型
    # ========================================================================
    print_section("【第2步】定义植物类型")
    
    # 创建植物类型
    reed = create_reed()
    cattail = create_cattail()
    willow = create_willow_shrub()
    
    plants = [reed, cattail, willow]
    
    print("\n候选植物类型:")
    print(f"{'植物名称':<15} {'高度(m)':<10} {'茎径(m)':<10} {'密度(stems/m²)':<15} {'临界流速(m/s)':<15}")
    print("-" * 75)
    for plant in plants:
        print(f"{plant.name:<15} {plant.height:<10.2f} {plant.stem_diameter:<10.3f} "
              f"{plant.density:<15.0f} {plant.critical_velocity:<15.2f}")
    
    # ========================================================================
    # 第3步：分析植被对流速的影响
    # ========================================================================
    print_section("【第3步】分析植被对流速的影响")
    
    # 设计流量
    Q_design = 20.0  # m³/s
    h_bare = reach.solve_depth(Q_design)
    v_bare = reach.velocity_manning(h_bare)
    
    print(f"\n设计流量: {Q_design} m³/s")
    print(f"裸露河床:")
    print(f"  水深: {h_bare:.2f} m")
    print(f"  流速: {v_bare:.2f} m/s")
    
    print(f"\n不同植被覆盖率下的流速（50%覆盖率）:")
    print(f"{'植物':<15} {'有效糙率':<12} {'流速(m/s)':<12} {'流速衰减':<12}")
    print("-" * 55)
    
    coverage = 0.5  # 50%覆盖率
    
    for plant in plants:
        veg_channel = VegetatedChannel(reach, plant, coverage)
        n_eff = veg_channel.effective_roughness(h_bare)
        v_veg = veg_channel.velocity_manning_with_vegetation(h_bare)
        reduction = (v_bare - v_veg) / v_bare * 100
        
        print(f"{plant.name:<15} {n_eff:<12.4f} {v_veg:<12.2f} {reduction:<12.1f}%")
    
    # ========================================================================
    # 第4步：植物稳定性评估
    # ========================================================================
    print_section("【第4步】植物稳定性评估")
    
    # 不同流量下的稳定性
    Q_range = [10, 20, 30, 40, 50]
    
    print(f"\n植物抗冲稳定性（覆盖率50%）:")
    
    for plant in plants:
        print(f"\n{plant.name}:")
        print(f"{'流量(m³/s)':<15} {'水深(m)':<12} {'流速(m/s)':<12} {'安全系数':<12} {'稳定性':<15}")
        print("-" * 70)
        
        veg_channel = VegetatedChannel(reach, plant, coverage)
        
        for Q in Q_range:
            h = reach.solve_depth(Q)
            stability = veg_channel.check_stability(h, Q)
            
            print(f"{Q:<15.1f} {h:<12.2f} {stability['velocity']:<12.2f} "
                  f"{stability['safety_factor']:<12.2f} {stability['stability']:<15}")
    
    # ========================================================================
    # 第5步：淹水条件分析
    # ========================================================================
    print_section("【第5步】淹水条件分析")
    
    # 模拟年流量序列
    np.random.seed(42)
    n_days = 365
    
    # 生成季节性流量（春季高、夏秋低）
    days = np.arange(n_days)
    seasonal_pattern = 20 + 15 * np.sin(2 * np.pi * days / 365 - np.pi/2)
    noise = np.random.normal(0, 5, n_days)
    flow_series = np.maximum(seasonal_pattern + noise, 5)
    
    # 不同高程的种植位置
    channel_bottom = 0.0  # 河床底高程
    elevations = {
        '低滩': channel_bottom + 0.5,
        '中滩': channel_bottom + 1.0,
        '高滩': channel_bottom + 1.5
    }
    
    print(f"\n年流量统计:")
    print(f"  平均流量: {np.mean(flow_series):.2f} m³/s")
    print(f"  最大流量: {np.max(flow_series):.2f} m³/s")
    print(f"  最小流量: {np.min(flow_series):.2f} m³/s")
    
    print(f"\n不同高程的淹水特征:")
    print(f"{'高程位置':<15} {'高程(m)':<12} {'淹水天数':<12} {'淹水比例':<12} {'平均淹深(m)':<15}")
    print("-" * 70)
    
    dates = np.arange(n_days)  # 简化为天数
    submergence_results = {}
    
    for location, elevation in elevations.items():
        result = VegetationGrowthModel.submergence_duration(
            flow_series, dates, elevation, channel_bottom, reach
        )
        submergence_results[location] = result
        
        print(f"{location:<15} {elevation:<12.2f} {result['submerged_days']:<12.0f} "
              f"{result['submergence_ratio']:<12.1%} {result['mean_submergence_depth']:<15.2f}")
    
    # ========================================================================
    # 第6步：植物配置方案优选
    # ========================================================================
    print_section("【第6步】植物配置方案优选")
    
    print(f"\n不同植物在不同高程的生长适宜性:")
    
    for plant in plants:
        print(f"\n{plant.name}:")
        print(f"{'高程位置':<15} {'淹水比例':<12} {'平均流速(m/s)':<15} {'综合适宜性':<15} {'评级':<10}")
        print("-" * 72)
        
        for location, elevation in elevations.items():
            # 计算平均流速
            velocities = []
            for Q in flow_series:
                h = reach.solve_depth(Q)
                water_surface = channel_bottom + h
                if water_surface > elevation:
                    # 该位置被淹没时的流速
                    veg_channel = VegetatedChannel(reach, plant, coverage)
                    v = veg_channel.velocity_manning_with_vegetation(h)
                    velocities.append(v)
            
            mean_velocity = np.mean(velocities) if velocities else 0
            
            # 评估生长适宜性
            submergence_ratio = submergence_results[location]['submergence_ratio']
            suitability = VegetationGrowthModel.growth_suitability(
                submergence_ratio, mean_velocity, plant
            )
            
            print(f"{location:<15} {submergence_ratio:<12.1%} {mean_velocity:<15.2f} "
                  f"{suitability['overall_suitability']:<15.2f} {suitability['grade']:<10}")
    
    # ========================================================================
    # 第7步：生成可视化图表
    # ========================================================================
    print_section("【第7步】生成可视化图表")
    
    create_visualizations(reach, plants, coverage, flow_series, 
                         elevations, channel_bottom, submergence_results)
    
    print("\n✓ 可视化图表已生成:")
    print("  - vegetation_roughness.png: 植被糙率影响")
    print("  - velocity_reduction.png: 流速衰减分析")
    print("  - stability_assessment.png: 稳定性评估")
    print("  - submergence_analysis.png: 淹水分析")
    print("  - suitability_matrix.png: 适宜性矩阵")
    
    # ========================================================================
    # 第8步：推荐配置方案
    # ========================================================================
    print_section("【第8步】推荐配置方案")
    
    print(f"\n植物配置建议:")
    print(f"\n  1. 低滩区（0.5m高程）:")
    print(f"     推荐: 芦苇、香蒲")
    print(f"     理由: 耐淹能力强，高淹水比例（{submergence_results['低滩']['submergence_ratio']:.1%}）")
    print(f"     覆盖率: 40-60%")
    
    print(f"\n  2. 中滩区（1.0m高程）:")
    print(f"     推荐: 芦苇、柳树灌木")
    print(f"     理由: 适中的淹水比例（{submergence_results['中滩']['submergence_ratio']:.1%}），生长条件较好")
    print(f"     覆盖率: 50-70%")
    
    print(f"\n  3. 高滩区（1.5m高程）:")
    print(f"     推荐: 柳树灌木")
    print(f"     理由: 淹水较少（{submergence_results['高滩']['submergence_ratio']:.1%}），适合耐旱植物")
    print(f"     覆盖率: 30-50%")
    
    # ========================================================================
    # 总结
    # ========================================================================
    print_header("分析完成！")
    
    print(f"\n✓ 植物类型: 3种")
    print(f"✓ 分析流量范围: 5-50 m³/s")
    print(f"✓ 配置方案: 分区种植")
    print(f"✓ 预期效果: 增加生物多样性，提高河道糙率，减缓流速")


def create_visualizations(reach, plants, coverage, flow_series,
                         elevations, channel_bottom, submergence_results):
    """创建可视化图表"""
    
    # 图1：植被糙率影响
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 不同水深下的有效糙率
    depths = np.linspace(0.3, 2.5, 50)
    
    ax1.axhline(reach.n, color='gray', linestyle='--', linewidth=2, label='Bare bed')
    
    for plant in plants:
        veg_channel = VegetatedChannel(reach, plant, coverage)
        n_effs = [veg_channel.effective_roughness(h) for h in depths]
        ax1.plot(depths, n_effs, linewidth=2, label=plant.name, marker='o', markersize=3)
    
    ax1.set_xlabel('Water Depth (m)', fontsize=11)
    ax1.set_ylabel("Manning's n", fontsize=11)
    ax1.set_title('Effective Roughness with Vegetation', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 不同覆盖率的影响（以芦苇为例）
    coverages = [0.2, 0.4, 0.6, 0.8]
    plant = plants[0]  # 芦苇
    
    for cov in coverages:
        veg_channel = VegetatedChannel(reach, plant, cov)
        n_effs = [veg_channel.effective_roughness(h) for h in depths]
        ax2.plot(depths, n_effs, linewidth=2, label=f'{cov*100:.0f}% coverage', marker='s', markersize=3)
    
    ax2.set_xlabel('Water Depth (m)', fontsize=11)
    ax2.set_ylabel("Manning's n", fontsize=11)
    ax2.set_title(f'Effect of Coverage Rate ({plant.name})', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('vegetation_roughness.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: vegetation_roughness.png")
    plt.close()
    
    # 图2：流速衰减分析
    fig, ax = plt.subplots(figsize=(12, 6))
    
    Q_range = np.linspace(5, 50, 30)
    
    # 裸露河床的流速
    v_bare_list = []
    for Q in Q_range:
        h = reach.solve_depth(Q)
        v = reach.velocity_manning(h)
        v_bare_list.append(v)
    
    ax.plot(Q_range, v_bare_list, 'k-', linewidth=2.5, label='Bare bed', marker='o', markersize=4)
    
    # 有植被的流速
    for plant in plants:
        veg_channel = VegetatedChannel(reach, plant, coverage)
        v_veg_list = []
        for Q in Q_range:
            h = reach.solve_depth(Q)
            v = veg_channel.velocity_manning_with_vegetation(h)
            v_veg_list.append(v)
        
        ax.plot(Q_range, v_veg_list, linewidth=2, label=f'{plant.name} (50%)', 
               marker='s', markersize=3, linestyle='--')
        
        # 标注临界流速
        ax.axhline(plant.critical_velocity, color='r', linestyle=':', alpha=0.3)
        ax.text(Q_range[-1]*0.95, plant.critical_velocity, 
               f'{plant.name}\n临界', fontsize=8, ha='right')
    
    ax.set_xlabel('Flow (m³/s)', fontsize=12)
    ax.set_ylabel('Velocity (m/s)', fontsize=12)
    ax.set_title('Velocity Reduction by Vegetation', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('velocity_reduction.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: velocity_reduction.png")
    plt.close()
    
    # 图3：稳定性评估
    fig, axes = plt.subplots(len(plants), 1, figsize=(12, 10))
    
    Q_range_fine = np.linspace(5, 50, 50)
    
    for idx, (plant, ax) in enumerate(zip(plants, axes)):
        veg_channel = VegetatedChannel(reach, plant, coverage)
        
        velocities = []
        safety_factors = []
        
        for Q in Q_range_fine:
            h = reach.solve_depth(Q)
            stability = veg_channel.check_stability(h, Q)
            velocities.append(stability['velocity'])
            safety_factors.append(min(stability['safety_factor'], 5))  # Cap at 5 for visualization
        
        # 双y轴
        ax2 = ax.twinx()
        
        line1 = ax.plot(Q_range_fine, velocities, 'b-', linewidth=2, label='Velocity')
        ax.axhline(plant.critical_velocity, color='r', linestyle='--', linewidth=1.5, label='Critical velocity')
        
        line2 = ax2.plot(Q_range_fine, safety_factors, 'g-', linewidth=2, label='Safety factor')
        ax2.axhline(1.0, color='orange', linestyle=':', linewidth=1, label='Safety limit')
        
        ax.set_ylabel('Velocity (m/s)', fontsize=11, color='b')
        ax2.set_ylabel('Safety Factor', fontsize=11, color='g')
        ax.set_title(f'{plant.name} Stability Assessment', fontsize=12, fontweight='bold')
        ax.tick_params(axis='y', labelcolor='b')
        ax2.tick_params(axis='y', labelcolor='g')
        ax.grid(True, alpha=0.3)
        
        # 合并图例
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax.legend(lines + [ax.axhline(plant.critical_velocity, color='r', linestyle='--'),
                          ax2.axhline(1.0, color='orange', linestyle=':')],
                 labels + ['Critical velocity', 'Safety limit'], loc='upper left', fontsize=9)
    
    axes[-1].set_xlabel('Flow (m³/s)', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('stability_assessment.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: stability_assessment.png")
    plt.close()
    
    # 图4：淹水分析
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 流量时间序列和水位
    days = np.arange(len(flow_series))
    water_levels = []
    for Q in flow_series:
        h = reach.solve_depth(Q)
        water_levels.append(channel_bottom + h)
    
    ax1.fill_between(days, channel_bottom, water_levels, alpha=0.3, color='blue', label='Water')
    ax1.plot(days, water_levels, 'b-', linewidth=1, alpha=0.6)
    
    # 标注高程线
    colors = ['green', 'orange', 'red']
    for (location, elevation), color in zip(elevations.items(), colors):
        ax1.axhline(elevation, color=color, linestyle='--', linewidth=2, label=location)
    
    ax1.set_xlabel('Day of Year', fontsize=11)
    ax1.set_ylabel('Elevation (m)', fontsize=11)
    ax1.set_title('Water Level Variation', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 淹水特征对比
    locations = list(elevations.keys())
    submerged_days = [submergence_results[loc]['submerged_days'] for loc in locations]
    non_submerged_days = [365 - days for days in submerged_days]
    
    x = np.arange(len(locations))
    width = 0.6
    
    bars1 = ax2.bar(x, submerged_days, width, label='Submerged', color='#3498db', alpha=0.8)
    bars2 = ax2.bar(x, non_submerged_days, width, bottom=submerged_days, 
                   label='Non-submerged', color='#95a5a6', alpha=0.8)
    
    # 添加百分比标签
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        height1 = bar1.get_height()
        height2 = bar2.get_height()
        ax2.text(bar1.get_x() + bar1.get_width()/2., height1/2,
                f'{height1/365*100:.1f}%',
                ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    
    ax2.set_ylabel('Days', fontsize=11)
    ax2.set_title('Submergence Duration', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(locations)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('submergence_analysis.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: submergence_analysis.png")
    plt.close()
    
    # 图5：适宜性矩阵
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 计算适宜性矩阵
    suitability_matrix = np.zeros((len(plants), len(elevations)))
    
    for i, plant in enumerate(plants):
        for j, (location, elevation) in enumerate(elevations.items()):
            velocities = []
            for Q in flow_series:
                h = reach.solve_depth(Q)
                water_surface = channel_bottom + h
                if water_surface > elevation:
                    veg_channel = VegetatedChannel(reach, plant, coverage)
                    v = veg_channel.velocity_manning_with_vegetation(h)
                    velocities.append(v)
            
            mean_velocity = np.mean(velocities) if velocities else 0
            submergence_ratio = submergence_results[location]['submergence_ratio']
            suitability = VegetationGrowthModel.growth_suitability(
                submergence_ratio, mean_velocity, plant
            )
            suitability_matrix[i, j] = suitability['overall_suitability']
    
    im = ax.imshow(suitability_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    
    # 设置刻度
    ax.set_xticks(np.arange(len(elevations)))
    ax.set_yticks(np.arange(len(plants)))
    ax.set_xticklabels(list(elevations.keys()))
    ax.set_yticklabels([p.name for p in plants])
    
    # 添加数值标签
    for i in range(len(plants)):
        for j in range(len(elevations)):
            text = ax.text(j, i, f'{suitability_matrix[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=12, fontweight='bold')
    
    ax.set_title('Growth Suitability Matrix', fontsize=13, fontweight='bold')
    plt.colorbar(im, ax=ax, label='Suitability (0-1)')
    
    plt.tight_layout()
    plt.savefig('suitability_matrix.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: suitability_matrix.png")
    plt.close()


if __name__ == "__main__":
    main()
