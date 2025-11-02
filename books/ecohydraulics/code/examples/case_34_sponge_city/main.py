#!/usr/bin/env python3
"""案例34：海绵城市雨洪管理"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.urban_ecohydraulics import SpongeCityDesign, design_sponge_city_system

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例34：海绵城市雨洪管理设计")
    print("=" * 70)
    
    # 区域参数
    sponge = SpongeCityDesign(
        catchment_area=50.0,  # 50公顷
        imperviousness=0.65   # 65%不透水率
    )
    
    print(f"\n区域基本参数:")
    print(f"  汇水面积: {sponge.A / 1e4:.1f} ha")
    print(f"  不透水率: {sponge.imp * 100:.0f}%")
    
    # 1. 不同降雨情景下的径流
    rainfalls = [10, 20, 30, 50, 75, 100]
    print(f"\n不同降雨情景径流量:")
    
    runoff_results = []
    for rain in rainfalls:
        result = sponge.runoff_volume(rain)
        runoff_results.append(result)
        print(f"  降雨{rain:3.0f}mm: 径流系数{result['runoff_coefficient']:.2f}, "
              f"径流量{result['runoff_volume']:.0f}m³")
    
    # 2. LID设施规模设计
    design_rain = 30  # mm
    lid_types = ['bioretention', 'permeable', 'green_roof', 'rain_barrel']
    lid_names = ['生物滞留', '透水铺装', '绿色屋顶', '雨水罐']
    
    print(f"\nLID设施规模设计（设计降雨{design_rain}mm）:")
    lid_designs = []
    for lid_type, lid_name in zip(lid_types, lid_names):
        design = sponge.lid_facility_sizing(design_rain, lid_type)
        lid_designs.append(design)
        print(f"  {lid_name}: 面积{design['facility_area']:.0f}m², "
              f"削减率{design['reduction_rate']:.1f}%, "
              f"成本{design['cost_estimate']/1e4:.1f}万元")
    
    # 3. 年径流总量控制率
    np.random.seed(42)
    annual_rainfall = np.random.exponential(15, 365)
    annual_result = sponge.annual_control_rate(annual_rainfall)
    
    print(f"\n年径流总量控制率:")
    print(f"  年降雨事件: {annual_result['total_events']}次")
    print(f"  控制事件数: {annual_result['controlled_events']}次")
    print(f"  次数控制率: {annual_result['control_rate_count']:.1f}%")
    print(f"  容积控制率: {annual_result['control_rate_volume']:.1f}%")
    
    # 4. 水质改善
    inlet_conc = {
        'TSS': 150.0,  # mg/L
        'TN': 3.5,
        'TP': 0.8,
        'COD': 80.0
    }
    
    wq_result = sponge.water_quality_improvement(inlet_conc)
    print(f"\n水质改善效果:")
    for pollutant in inlet_conc.keys():
        print(f"  {pollutant}: {wq_result['inlet_concentration'][pollutant]:.1f} → "
              f"{wq_result['outlet_concentration'][pollutant]:.1f} mg/L "
              f"(削减{wq_result['removal_rates'][pollutant]:.0f}%)")
    
    # 5. 系统集成设计
    integrated = design_sponge_city_system(50.0, 0.65, 80.0)
    print(f"\n系统集成设计:")
    print(f"  当前控制率: {integrated['current_control_rate']:.1f}%")
    print(f"  目标控制率: {integrated['target_control_rate']:.1f}%")
    print(f"  控制率缺口: {integrated['gap']:.1f}%")
    if integrated['additional_facilities']:
        print(f"  需要额外设施:")
        for facility, area in integrated['additional_facilities'].items():
            print(f"    {facility}: {area:.0f} m²")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 降雨-径流关系
    ax1 = plt.subplot(2, 3, 1)
    rain_vals = [r['rainfall'] for r in runoff_results]
    runoff_vals = [r['runoff_volume'] for r in runoff_results]
    
    ax1.plot(rain_vals, runoff_vals, 'b-o', linewidth=2, markersize=8)
    ax1.set_xlabel('降雨量 (mm)', fontsize=10)
    ax1.set_ylabel('径流量 (m³)', fontsize=10)
    ax1.set_title('降雨-径流关系', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 2. LID设施对比
    ax2 = plt.subplot(2, 3, 2)
    x_pos = np.arange(len(lid_names))
    reduction_rates = [d['reduction_rate'] for d in lid_designs]
    colors = ['green', 'gray', 'lightgreen', 'blue']
    
    bars = ax2.bar(x_pos, reduction_rates, color=colors, 
                   edgecolor='black', linewidth=1.5)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(lid_names, rotation=15)
    ax2.set_ylabel('径流削减率 (%)', fontsize=10)
    ax2.set_title('不同LID设施削减效果', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim([0, 100])
    
    for bar, rate in zip(bars, reduction_rates):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{rate:.0f}%', ha='center', va='bottom',
                fontsize=9, fontweight='bold')
    
    # 3. 年降雨序列
    ax3 = plt.subplot(2, 3, 3)
    ax3.plot(annual_rainfall, 'b-', linewidth=1, alpha=0.7)
    ax3.axhline(25, color='r', linestyle='--', linewidth=2, label='控制阈值')
    ax3.set_xlabel('时间 (天)', fontsize=10)
    ax3.set_ylabel('降雨量 (mm)', fontsize=10)
    ax3.set_title('年降雨序列', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim([0, 365])
    
    # 4. 水质改善对比
    ax4 = plt.subplot(2, 3, 4)
    pollutants = list(inlet_conc.keys())
    x_pos = np.arange(len(pollutants))
    inlet_vals = [wq_result['inlet_concentration'][p] for p in pollutants]
    outlet_vals = [wq_result['outlet_concentration'][p] for p in pollutants]
    
    width = 0.35
    ax4.bar(x_pos - width/2, inlet_vals, width, label='入流', 
           color='lightcoral', edgecolor='black', linewidth=1.5)
    ax4.bar(x_pos + width/2, outlet_vals, width, label='出流',
           color='lightgreen', edgecolor='black', linewidth=1.5)
    
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(pollutants)
    ax4.set_ylabel('浓度 (mg/L)', fontsize=10)
    ax4.set_title('水质改善效果', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. LID设施成本对比
    ax5 = plt.subplot(2, 3, 5)
    costs = [d['cost_estimate'] / 1e4 for d in lid_designs]
    
    bars = ax5.barh(lid_names, costs, color=colors, 
                    edgecolor='black', linewidth=1.5)
    ax5.set_xlabel('成本 (万元)', fontsize=10)
    ax5.set_title('LID设施成本对比', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='x')
    
    for bar, cost in zip(bars, costs):
        ax5.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{cost:.0f}', va='center', fontsize=9, fontweight='bold')
    
    # 6. 海绵城市综合效益
    ax6 = plt.subplot(2, 3, 6)
    
    benefits = ['径流削减', '峰值削减', '水质改善', '生态价值', '景观提升']
    scores = [85, 78, 75, 90, 88]
    colors_ben = ['blue', 'green', 'cyan', 'lime', 'yellow']
    
    bars = ax6.barh(benefits, scores, color=colors_ben,
                    edgecolor='black', linewidth=1.5)
    ax6.set_xlabel('综合评分', fontsize=10)
    ax6.set_title('海绵城市综合效益评价', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='x')
    ax6.set_xlim([0, 100])
    
    for bar, score in zip(bars, scores):
        ax6.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                f'{score}', va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'sponge_city_design.png', dpi=300)
    print(f"\n图表已保存: sponge_city_design.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
