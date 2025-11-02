#!/usr/bin/env python3
"""案例35：城市河道生态修复"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.urban_ecohydraulics import UrbanRiverRestoration

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例35：城市河道生态修复评估与设计")
    print("=" * 70)
    
    # 河道参数
    river = UrbanRiverRestoration(
        river_length=5.0,  # 5km
        channel_width=30.0,  # 30m
        average_depth=2.0   # 2m
    )
    
    print(f"\n河道基本参数:")
    print(f"  长度: {river.L / 1000:.1f} km")
    print(f"  宽度: {river.W:.1f} m")
    print(f"  平均水深: {river.H:.1f} m")
    print(f"  水面面积: {river.A_surface / 1e4:.2f} ha")
    
    # 1. 水力多样性评估
    np.random.seed(42)
    velocity_data = np.random.normal(0.5, 0.2, 100)
    velocity_data = np.clip(velocity_data, 0.1, 1.5)
    depth_data = np.random.normal(2.0, 0.5, 100)
    depth_data = np.clip(depth_data, 0.5, 3.5)
    
    HDI = river.hydraulic_diversity_index(velocity_data, depth_data)
    print(f"\n水力多样性指数: {HDI:.3f}")
    print(f"  评价: {'优' if HDI > 1.2 else '良' if HDI > 0.8 else '中'}")
    
    # 2. 生境适宜性评价
    test_conditions = [
        (0.3, 1.0, 'gravel'),
        (0.8, 1.5, 'cobble'),
        (1.2, 0.5, 'sand'),
        (0.5, 2.5, 'gravel')
    ]
    
    print(f"\n生境适宜性评价:")
    HSI_values = []
    for v, d, s in test_conditions:
        HSI = river.habitat_suitability_index(v, d, s)
        HSI_values.append(HSI)
        print(f"  流速{v:.1f}m/s, 水深{d:.1f}m, {s}: HSI={HSI:.3f}")
    
    # 3. 生态流量需求
    base_flow = 8.0  # m³/s
    eco_flows = river.ecological_flow_requirement(base_flow)
    
    print(f"\n生态流量需求（基流{base_flow}m³/s）:")
    for level, flow in eco_flows.items():
        print(f"  {level:12s}: {flow:.2f} m³/s")
    
    # 4. 滨岸植被设计
    slopes = [10, 25, 35]
    print(f"\n滨岸植被设计方案:")
    veg_designs = []
    for slope in slopes:
        design = river.riparian_vegetation_design(slope, 'loam')
        veg_designs.append(design)
        print(f"  坡度{slope}°: 稳定性{design['stability']}, "
              f"维护{design['maintenance']}")
    
    # 5. 自净能力评估
    flow_scenarios = [5, 8, 12, 15]
    temp = 20  # °C
    
    print(f"\n自净能力评估（水温{temp}°C）:")
    self_purif = []
    for flow in flow_scenarios:
        result = river.self_purification_capacity(flow, temp)
        self_purif.append(result)
        print(f"  流量{flow:2d}m³/s: K2={result['reaeration_rate']:.2f}/d, "
              f"自净能力{result['self_purification']}")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 流速和水深分布
    ax1 = plt.subplot(2, 3, 1)
    ax1.hist(velocity_data, bins=15, alpha=0.7, color='blue',
            edgecolor='black', label='流速')
    ax1.set_xlabel('流速 (m/s)', fontsize=10)
    ax1.set_ylabel('频数', fontsize=10)
    ax1.set_title('流速分布', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    ax1_twin = ax1.twinx()
    ax1_twin.hist(depth_data, bins=15, alpha=0.5, color='green',
                 edgecolor='black', label='水深')
    ax1_twin.set_ylabel('频数', fontsize=10)
    
    # 2. 生境适宜性对比
    ax2 = plt.subplot(2, 3, 2)
    conditions = [f"V={v}\nD={d}\n{s[:3]}" for v, d, s in test_conditions]
    colors = ['green' if h > 0.7 else 'yellow' if h > 0.5 else 'red' 
             for h in HSI_values]
    
    bars = ax2.bar(range(len(conditions)), HSI_values, color=colors,
                   edgecolor='black', linewidth=1.5)
    ax2.set_xticks(range(len(conditions)))
    ax2.set_xticklabels(conditions, fontsize=8)
    ax2.set_ylabel('HSI', fontsize=10)
    ax2.set_title('生境适宜性评价', fontsize=12, fontweight='bold')
    ax2.axhline(0.7, color='g', linestyle='--', alpha=0.5, label='良好阈值')
    ax2.axhline(0.5, color='orange', linestyle='--', alpha=0.5, label='一般阈值')
    ax2.legend(loc='upper right', fontsize=8)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim([0, 1])
    
    # 3. 生态流量等级
    ax3 = plt.subplot(2, 3, 3)
    levels = list(eco_flows.keys())
    flows_vals = list(eco_flows.values())
    colors_eco = plt.cm.YlGnBu(np.linspace(0.3, 0.9, len(levels)))
    
    bars = ax3.barh(levels, flows_vals, color=colors_eco,
                    edgecolor='black', linewidth=1.5)
    ax3.set_xlabel('流量 (m³/s)', fontsize=10)
    ax3.set_title('生态流量分级', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')
    
    for bar, flow in zip(bars, flows_vals):
        ax3.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'{flow:.1f}', va='center', fontsize=9, fontweight='bold')
    
    # 4. 滨岸植被分带示意图
    ax4 = plt.subplot(2, 3, 4)
    
    # 绘制岸坡剖面
    slope_angle = 20  # 度
    bank_length = 10  # m
    x = np.linspace(0, bank_length, 100)
    y = x * np.tan(np.radians(slope_angle))
    
    ax4.fill_between(x, 0, y, color='brown', alpha=0.3, label='岸坡')
    
    # 植被分带
    ax4.fill_between([0, 2], [0, 0], [0.8, 0.8], color='darkgreen',
                    alpha=0.5, label='水边带')
    ax4.fill_between([2, 6], [0.8, 0.8], [2.5, 2.5], color='green',
                    alpha=0.5, label='中间带')
    ax4.fill_between([6, 10], [2.5, 2.5], [4.0, 4.0], color='lightgreen',
                    alpha=0.5, label='上部带')
    
    ax4.set_xlabel('距离 (m)', fontsize=10)
    ax4.set_ylabel('高程 (m)', fontsize=10)
    ax4.set_title('滨岸植被分带示意', fontsize=12, fontweight='bold')
    ax4.legend(loc='upper left')
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim([0, 10])
    ax4.set_ylim([0, 5])
    
    # 5. 自净能力随流量变化
    ax5 = plt.subplot(2, 3, 5)
    K2_vals = [s['reaeration_rate'] for s in self_purif]
    K1_vals = [s['deoxygenation_rate'] for s in self_purif]
    
    ax5.plot(flow_scenarios, K2_vals, 'b-o', linewidth=2, 
            markersize=8, label='复氧系数K2')
    ax5.plot(flow_scenarios, K1_vals, 'r-s', linewidth=2,
            markersize=8, label='耗氧系数K1')
    ax5.set_xlabel('流量 (m³/s)', fontsize=10)
    ax5.set_ylabel('系数 (1/d)', fontsize=10)
    ax5.set_title('河流自净能力', fontsize=12, fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. 修复效果综合评价
    ax6 = plt.subplot(2, 3, 6)
    
    # 修复前后对比
    indicators = ['水力\n多样性', '生境\n质量', '生态\n流量', '自净\n能力', '景观\n价值']
    before = [0.5, 0.4, 0.3, 0.4, 0.3]
    after = [0.85, 0.75, 0.80, 0.78, 0.88]
    
    x = np.arange(len(indicators))
    width = 0.35
    
    ax6.bar(x - width/2, before, width, label='修复前',
           color='lightcoral', edgecolor='black', linewidth=1.5)
    ax6.bar(x + width/2, after, width, label='修复后',
           color='lightgreen', edgecolor='black', linewidth=1.5)
    
    ax6.set_xticks(x)
    ax6.set_xticklabels(indicators, fontsize=9)
    ax6.set_ylabel('评分', fontsize=10)
    ax6.set_title('修复效果综合评价', fontsize=12, fontweight='bold')
    ax6.legend()
    ax6.grid(True, alpha=0.3, axis='y')
    ax6.set_ylim([0, 1])
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'urban_river_restoration.png', dpi=300)
    print(f"\n图表已保存: urban_river_restoration.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
