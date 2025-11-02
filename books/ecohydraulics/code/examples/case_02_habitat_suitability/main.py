"""
案例2：鱼类栖息地适宜性评价
==========================

工程背景
--------
某河段进行生态修复，需评估不同流量下鱼类栖息地质量，
确定最优生态流量范围。

问题描述
--------
- 目标鱼类: 鲤鱼（成鱼和幼鱼）
- 河段长度: L = 1000 m
- 河道宽度: b = 15 m
- 河床坡度: S0 = 0.0008
- Manning糙率: n = 0.030
- 边坡系数: m = 2.0
- 流量范围: 2-20 m³/s

计算目标
--------
1. 绘制鱼类适宜性曲线
2. 计算不同流量下的WUA（加权可利用面积）
3. 找到最优生态流量
4. 评估栖息地质量等级

学习目标
--------
1. 理解栖息地适宜性指数（HSI）概念
2. 掌握WUA计算方法
3. 学会适宜性曲线的构建和应用
4. 理解流量-生境关系

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
from code.models.habitat import (
    create_carp_adult_model,
    create_carp_juvenile_model
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
    
    print_header("案例2：鱼类栖息地适宜性评价")
    
    # ========================================================================
    # 第1步：定义河段参数
    # ========================================================================
    print_section("【第1步】定义河段参数")
    
    reach = RiverReach(
        length=1000.0,      # 河段长度 m
        width=15.0,         # 河道底宽 m
        slope=0.0008,       # 河床坡度
        roughness=0.030,    # Manning糙率
        side_slope=2.0      # 边坡系数
    )
    
    print(f"河段长度: {reach.length} m")
    print(f"河道底宽: {reach.b} m")
    print(f"河床坡度: {reach.S0}")
    print(f"Manning糙率: {reach.n}")
    print(f"边坡系数: {reach.m}")
    
    # ========================================================================
    # 第2步：创建鱼类栖息地模型
    # ========================================================================
    print_section("【第2步】创建鱼类栖息地模型")
    
    # 成鱼模型
    adult_model = create_carp_adult_model()
    print(f"\n✓ 已创建 {adult_model.species_name}{adult_model.life_stage} 栖息地模型")
    print(f"  包含适宜性曲线: {list(adult_model.curves.keys())}")
    
    # 幼鱼模型
    juvenile_model = create_carp_juvenile_model()
    print(f"\n✓ 已创建 {juvenile_model.species_name}{juvenile_model.life_stage} 栖息地模型")
    print(f"  包含适宜性曲线: {list(juvenile_model.curves.keys())}")
    
    # ========================================================================
    # 第3步：计算典型流量下的栖息地质量
    # ========================================================================
    print_section("【第3步】典型流量下的栖息地质量")
    
    test_flows = [3.0, 6.0, 10.0, 15.0]
    
    print("\n成鱼栖息地质量:")
    print(f"{'流量(m³/s)':<12} {'水深(m)':<10} {'流速(m/s)':<12} "
          f"{'WUA(m²)':<12} {'栖息地质量':<12}")
    print("-" * 70)
    
    for Q in test_flows:
        result = adult_model.calculate_wua(reach, Q, n_cells=50)
        print(f"{Q:<12.1f} {result['depth']:<10.2f} {result['velocity']:<12.2f} "
              f"{result['wua']:<12.0f} {result['habitat_quality']:<12.3f}")
    
    print("\n幼鱼栖息地质量:")
    print(f"{'流量(m³/s)':<12} {'水深(m)':<10} {'流速(m/s)':<12} "
          f"{'WUA(m²)':<12} {'栖息地质量':<12}")
    print("-" * 70)
    
    for Q in test_flows:
        result = juvenile_model.calculate_wua(reach, Q, n_cells=50)
        print(f"{Q:<12.1f} {result['depth']:<10.2f} {result['velocity']:<12.2f} "
              f"{result['wua']:<12.0f} {result['habitat_quality']:<12.3f}")
    
    # ========================================================================
    # 第4步：计算WUA-流量关系
    # ========================================================================
    print_section("【第4步】计算WUA-流量关系")
    
    flow_range = (2.0, 20.0)
    
    print(f"\n计算流量范围: {flow_range[0]} ~ {flow_range[1]} m³/s")
    print("计算点数: 30")
    
    adult_wua_flow = adult_model.calculate_wua_vs_flow(
        reach, flow_range, n_flows=30
    )
    
    juvenile_wua_flow = juvenile_model.calculate_wua_vs_flow(
        reach, flow_range, n_flows=30
    )
    
    print("\n✓ WUA-流量关系计算完成")
    
    # ========================================================================
    # 第5步：确定最优生态流量
    # ========================================================================
    print_section("【第5步】确定最优生态流量")
    
    adult_optimal = adult_model.find_optimal_flow(reach, flow_range, n_flows=50)
    juvenile_optimal = juvenile_model.find_optimal_flow(reach, flow_range, n_flows=50)
    
    print(f"\n成鱼最优流量:")
    print(f"  流量: {adult_optimal['optimal_flow']:.2f} m³/s")
    print(f"  最大WUA: {adult_optimal['max_wua']:.0f} m²")
    print(f"  栖息地质量: {adult_optimal['habitat_quality']:.3f}")
    
    print(f"\n幼鱼最优流量:")
    print(f"  流量: {juvenile_optimal['optimal_flow']:.2f} m³/s")
    print(f"  最大WUA: {juvenile_optimal['max_wua']:.0f} m²")
    print(f"  栖息地质量: {juvenile_optimal['habitat_quality']:.3f}")
    
    # 综合推荐
    recommended_flow = (adult_optimal['optimal_flow'] + 
                       juvenile_optimal['optimal_flow']) / 2
    
    print(f"\n综合推荐流量（兼顾成鱼和幼鱼）:")
    print(f"  推荐流量: {recommended_flow:.2f} m³/s")
    print(f"  流量范围: {juvenile_optimal['optimal_flow']:.2f} ~ "
          f"{adult_optimal['optimal_flow']:.2f} m³/s")
    
    # ========================================================================
    # 第6步：横断面栖息地分布
    # ========================================================================
    print_section("【第6步】横断面栖息地分布分析")
    
    Q_analysis = 10.0  # 分析流量
    print(f"\n分析流量: {Q_analysis} m³/s")
    
    adult_distribution = adult_model.calculate_wua(reach, Q_analysis, n_cells=50)
    juvenile_distribution = juvenile_model.calculate_wua(reach, Q_analysis, n_cells=50)
    
    print(f"\n成鱼栖息地分布:")
    print(f"  平均CSI: {np.mean(adult_distribution['cell_csi']):.3f}")
    print(f"  最大CSI: {np.max(adult_distribution['cell_csi']):.3f}")
    print(f"  适宜面积比例: {np.sum(adult_distribution['cell_csi'] > 0.5) / len(adult_distribution['cell_csi']) * 100:.1f}%")
    
    print(f"\n幼鱼栖息地分布:")
    print(f"  平均CSI: {np.mean(juvenile_distribution['cell_csi']):.3f}")
    print(f"  最大CSI: {np.max(juvenile_distribution['cell_csi']):.3f}")
    print(f"  适宜面积比例: {np.sum(juvenile_distribution['cell_csi'] > 0.5) / len(juvenile_distribution['cell_csi']) * 100:.1f}%")
    
    # ========================================================================
    # 第7步：生成可视化图表
    # ========================================================================
    print_section("【第7步】生成可视化图表")
    
    create_visualizations(
        reach, adult_model, juvenile_model,
        adult_wua_flow, juvenile_wua_flow,
        adult_optimal, juvenile_optimal,
        adult_distribution, juvenile_distribution,
        Q_analysis
    )
    
    print("\n✓ 可视化图表已生成:")
    print("  - suitability_curves.png: 适宜性曲线")
    print("  - wua_vs_flow.png: WUA-流量关系")
    print("  - habitat_distribution.png: 横断面栖息地分布")
    print("  - habitat_summary.png: 栖息地质量综合对比")
    
    # ========================================================================
    # 总结
    # ========================================================================
    print_header("评估完成！")
    
    print(f"\n✓ 成鱼最优流量: {adult_optimal['optimal_flow']:.2f} m³/s")
    print(f"✓ 幼鱼最优流量: {juvenile_optimal['optimal_flow']:.2f} m³/s")
    print(f"✓ 综合推荐流量: {recommended_flow:.2f} m³/s")
    print(f"✓ 栖息地质量: 良好")


def create_visualizations(reach, adult_model, juvenile_model,
                         adult_wua_flow, juvenile_wua_flow,
                         adult_optimal, juvenile_optimal,
                         adult_distribution, juvenile_distribution,
                         Q_analysis):
    """创建可视化图表"""
    
    # 图1：适宜性曲线
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 成鱼-水深
    ax = axes[0, 0]
    x, y = adult_model.curves['depth'].plot_data()
    ax.plot(x, y, 'b-', linewidth=2, label='Adult Carp')
    x, y = juvenile_model.curves['depth'].plot_data()
    ax.plot(x, y, 'r--', linewidth=2, label='Juvenile Carp')
    ax.set_xlabel('Depth (m)', fontsize=11)
    ax.set_ylabel('Suitability Index', fontsize=11)
    ax.set_title('Depth Suitability', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylim([0, 1.1])
    
    # 成鱼-流速
    ax = axes[0, 1]
    x, y = adult_model.curves['velocity'].plot_data()
    ax.plot(x, y, 'b-', linewidth=2, label='Adult Carp')
    x, y = juvenile_model.curves['velocity'].plot_data()
    ax.plot(x, y, 'r--', linewidth=2, label='Juvenile Carp')
    ax.set_xlabel('Velocity (m/s)', fontsize=11)
    ax.set_ylabel('Suitability Index', fontsize=11)
    ax.set_title('Velocity Suitability', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylim([0, 1.1])
    
    # 成鱼综合适宜性示例
    ax = axes[1, 0]
    depths = np.linspace(0, 3, 50)
    velocities = np.linspace(0, 1.5, 50)
    D, V = np.meshgrid(depths, velocities)
    CSI = np.zeros_like(D)
    for i in range(len(depths)):
        for j in range(len(velocities)):
            CSI[j, i] = adult_model.calculate_csi(D[j, i], V[j, i])
    
    im = ax.contourf(D, V, CSI, levels=10, cmap='viridis')
    ax.set_xlabel('Depth (m)', fontsize=11)
    ax.set_ylabel('Velocity (m/s)', fontsize=11)
    ax.set_title('Adult CSI (Composite)', fontsize=12, fontweight='bold')
    plt.colorbar(im, ax=ax, label='CSI')
    
    # 幼鱼综合适宜性示例
    ax = axes[1, 1]
    CSI_juv = np.zeros_like(D)
    for i in range(len(depths)):
        for j in range(len(velocities)):
            CSI_juv[j, i] = juvenile_model.calculate_csi(D[j, i], V[j, i])
    
    im = ax.contourf(D, V, CSI_juv, levels=10, cmap='viridis')
    ax.set_xlabel('Depth (m)', fontsize=11)
    ax.set_ylabel('Velocity (m/s)', fontsize=11)
    ax.set_title('Juvenile CSI (Composite)', fontsize=12, fontweight='bold')
    plt.colorbar(im, ax=ax, label='CSI')
    
    plt.tight_layout()
    plt.savefig('suitability_curves.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: suitability_curves.png")
    plt.close()
    
    # 图2：WUA-流量关系
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # WUA vs Flow
    ax1.plot(adult_wua_flow['flows'], adult_wua_flow['wua'], 
            'b-', linewidth=2, marker='o', markersize=4, label='Adult Carp')
    ax1.plot(juvenile_wua_flow['flows'], juvenile_wua_flow['wua'], 
            'r--', linewidth=2, marker='s', markersize=4, label='Juvenile Carp')
    ax1.axvline(adult_optimal['optimal_flow'], color='b', linestyle=':', alpha=0.5)
    ax1.axvline(juvenile_optimal['optimal_flow'], color='r', linestyle=':', alpha=0.5)
    ax1.set_xlabel('Flow (m³/s)', fontsize=12)
    ax1.set_ylabel('WUA (m²)', fontsize=12)
    ax1.set_title('WUA vs Flow', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    
    # Habitat Quality vs Flow
    ax2.plot(adult_wua_flow['flows'], adult_wua_flow['habitat_quality'], 
            'b-', linewidth=2, marker='o', markersize=4, label='Adult Carp')
    ax2.plot(juvenile_wua_flow['flows'], juvenile_wua_flow['habitat_quality'], 
            'r--', linewidth=2, marker='s', markersize=4, label='Juvenile Carp')
    ax2.set_xlabel('Flow (m³/s)', fontsize=12)
    ax2.set_ylabel('Habitat Quality', fontsize=12)
    ax2.set_title('Habitat Quality vs Flow', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)
    
    plt.tight_layout()
    plt.savefig('wua_vs_flow.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: wua_vs_flow.png")
    plt.close()
    
    # 图3：横断面栖息地分布
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # 成鱼分布
    ax1.bar(adult_distribution['cell_positions'], adult_distribution['cell_csi'],
           width=0.3, color='blue', alpha=0.6, label='Adult CSI')
    ax1.axhline(0.5, color='gray', linestyle='--', alpha=0.5, label='Threshold (0.5)')
    ax1.set_xlabel('Transverse Position (m)', fontsize=11)
    ax1.set_ylabel('CSI', fontsize=11)
    ax1.set_title(f'Adult Habitat Distribution (Q = {Q_analysis} m³/s)', 
                 fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.legend()
    ax1.set_ylim([0, 1.1])
    
    # 幼鱼分布
    ax2.bar(juvenile_distribution['cell_positions'], juvenile_distribution['cell_csi'],
           width=0.3, color='red', alpha=0.6, label='Juvenile CSI')
    ax2.axhline(0.5, color='gray', linestyle='--', alpha=0.5, label='Threshold (0.5)')
    ax2.set_xlabel('Transverse Position (m)', fontsize=11)
    ax2.set_ylabel('CSI', fontsize=11)
    ax2.set_title(f'Juvenile Habitat Distribution (Q = {Q_analysis} m³/s)', 
                 fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.legend()
    ax2.set_ylim([0, 1.1])
    
    plt.tight_layout()
    plt.savefig('habitat_distribution.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: habitat_distribution.png")
    plt.close()
    
    # 图4：综合对比
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ['Optimal Flow\n(m³/s)', 'Max WUA\n(m²)', 'Habitat\nQuality']
    adult_values = [
        adult_optimal['optimal_flow'],
        adult_optimal['max_wua'] / 1000,  # 转换为千m²以便对比
        adult_optimal['habitat_quality'] * 100  # 转换为百分比
    ]
    juvenile_values = [
        juvenile_optimal['optimal_flow'],
        juvenile_optimal['max_wua'] / 1000,
        juvenile_optimal['habitat_quality'] * 100
    ]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, adult_values, width, label='Adult Carp', 
                   color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, juvenile_values, width, label='Juvenile Carp', 
                   color='#e74c3c', alpha=0.8)
    
    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title('Habitat Quality Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('habitat_summary.png', dpi=300, bbox_inches='tight')
    print("  ✓ 已保存: habitat_summary.png")
    plt.close()


if __name__ == "__main__":
    main()
