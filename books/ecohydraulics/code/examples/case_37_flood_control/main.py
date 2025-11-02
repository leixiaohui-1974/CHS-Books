#!/usr/bin/env python3
"""案例37：城市内涝生态化防治"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.urban_ecohydraulics import UrbanFloodControl

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例37：城市内涝生态化防治方案")
    print("=" * 70)
    
    # 城市区域参数
    flood = UrbanFloodControl(
        district_area=2.0,  # 2km²
        design_return_period=20  # 20年一遇
    )
    
    print(f"\n区域基本参数:")
    print(f"  面积: {flood.A / 1e6:.1f} km²")
    print(f"  设计重现期: {flood.T} 年")
    
    # 1. 设计暴雨强度
    durations = [10, 20, 30, 60, 120, 180]  # 分钟
    print(f"\n设计暴雨强度（{flood.T}年一遇）:")
    
    intensities = []
    for dur in durations:
        intensity = flood.design_rainfall_intensity(dur, 'beijing')
        intensities.append(intensity)
        print(f"  历时{dur:3d}min: {intensity:.2f} mm/h")
    
    # 2. 不同不透水率下的径流
    imperviousness_scenarios = [0.4, 0.6, 0.75, 0.9]
    rainfall_int = flood.design_rainfall_intensity(120, 'beijing')
    
    print(f"\n不同不透水率下的径流（历时120min, 强度{rainfall_int:.1f}mm/h）:")
    runoff_scenarios = []
    for imp in imperviousness_scenarios:
        runoff = flood.runoff_calculation(rainfall_int, imp)
        runoff_scenarios.append(runoff)
        print(f"  不透水率{imp*100:.0f}%: 径流系数{runoff['runoff_coefficient']:.2f}, "
              f"峰值流量{runoff['peak_flow']:.1f}m³/s")
    
    # 3. 调蓄池设计
    inflow_vol = 5000  # m³
    outlet_cap = 0.5  # m³/s
    
    basin = flood.detention_basin_design(inflow_vol, outlet_cap)
    print(f"\n调蓄池设计:")
    print(f"  调蓄容积: {basin['storage_volume']:.0f} m³")
    print(f"  池深: {basin['basin_depth']:.1f} m")
    print(f"  池面积: {basin['basin_area']:.0f} m²")
    print(f"  排空时间: {basin['drawdown_time']:.1f} 小时")
    
    # 4. 绿色基础设施效能
    lid_coverages = [10, 20, 30, 40, 50]
    print(f"\nLID设施覆盖率效能:")
    
    effectiveness_results = []
    for coverage in lid_coverages:
        effect = flood.green_infrastructure_effectiveness(coverage)
        effectiveness_results.append(effect)
        print(f"  覆盖率{coverage:2d}%: 径流削减{effect['runoff_reduction']:.1f}%, "
              f"峰值削减{effect['peak_reduction']:.1f}%, "
              f"风险{effect['flood_risk_level']}")
    
    # 5. 综合管理策略
    budgets = [500, 1000, 1500, 2000]
    print(f"\n综合管理策略:")
    
    strategies = []
    for budget in budgets:
        strategy = flood.integrated_management_strategy(budget)
        strategies.append(strategy)
        print(f"  预算{budget}万元: 综合效能{strategy['total_effectiveness']:.1f}%, "
              f"预期削减{strategy['expected_reduction']:.1f}%")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 暴雨强度-历时关系
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(durations, intensities, 'r-o', linewidth=2, markersize=8)
    ax1.set_xlabel('降雨历时 (min)', fontsize=10)
    ax1.set_ylabel('暴雨强度 (mm/h)', fontsize=10)
    ax1.set_title(f'设计暴雨强度曲线（{flood.T}年一遇）',
                 fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 2. 不透水率对径流的影响
    ax2 = plt.subplot(2, 3, 2)
    imp_percent = [imp * 100 for imp in imperviousness_scenarios]
    peak_flows = [r['peak_flow'] for r in runoff_scenarios]
    runoff_coefs = [r['runoff_coefficient'] for r in runoff_scenarios]
    
    ax2.bar(imp_percent, peak_flows, color='steelblue',
           edgecolor='black', linewidth=1.5)
    ax2.set_xlabel('不透水率 (%)', fontsize=10)
    ax2.set_ylabel('峰值流量 (m³/s)', fontsize=10)
    ax2.set_title('不透水率对径流峰值的影响', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    for x, y in zip(imp_percent, peak_flows):
        ax2.text(x, y + 1, f'{y:.1f}', ha='center', va='bottom',
                fontsize=9, fontweight='bold')
    
    # 3. 调蓄池示意图
    ax3 = plt.subplot(2, 3, 3)
    
    # 简化的入流-出流过程
    time = np.linspace(0, 24, 100)
    inflow = 20 * np.exp(-((time - 6)**2) / 10)  # 峰值在6小时
    outflow = np.minimum(inflow, outlet_cap)
    storage = np.cumsum(inflow - outflow) * 0.24
    storage = np.maximum(storage, 0)
    storage = np.minimum(storage, basin['storage_volume'])
    
    ax3.plot(time, inflow, 'r-', linewidth=2, label='入流')
    ax3.plot(time, outflow, 'g-', linewidth=2, label='出流')
    
    ax3_twin = ax3.twinx()
    ax3_twin.plot(time, storage, 'b--', linewidth=2, label='蓄水量')
    ax3_twin.set_ylabel('蓄水量 (m³)', fontsize=10, color='b')
    ax3_twin.tick_params(axis='y', labelcolor='b')
    
    ax3.set_xlabel('时间 (h)', fontsize=10)
    ax3.set_ylabel('流量 (m³/s)', fontsize=10)
    ax3.set_title('调蓄池运行过程', fontsize=12, fontweight='bold')
    ax3.legend(loc='upper left')
    ax3_twin.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim([0, 24])
    
    # 4. LID设施效能
    ax4 = plt.subplot(2, 3, 4)
    runoff_red = [e['runoff_reduction'] for e in effectiveness_results]
    peak_red = [e['peak_reduction'] for e in effectiveness_results]
    pollutant_red = [e['pollutant_reduction'] for e in effectiveness_results]
    
    ax4.plot(lid_coverages, runoff_red, 'b-o', linewidth=2, 
            markersize=8, label='径流削减')
    ax4.plot(lid_coverages, peak_red, 'r-s', linewidth=2,
            markersize=8, label='峰值削减')
    ax4.plot(lid_coverages, pollutant_red, 'g-^', linewidth=2,
            markersize=8, label='污染物削减')
    
    ax4.set_xlabel('LID覆盖率 (%)', fontsize=10)
    ax4.set_ylabel('削减率 (%)', fontsize=10)
    ax4.set_title('绿色基础设施效能', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim([10, 50])
    ax4.set_ylim([0, 100])
    
    # 5. 预算分配方案
    ax5 = plt.subplot(2, 3, 5)
    
    # 选择1000万元预算的分配
    strategy = strategies[1]
    measures = list(strategy['allocation'].keys())
    allocations = [v * 100 for v in strategy['allocation'].values()]
    colors_alloc = ['green', 'gray', 'lightgreen', 'blue', 'lime']
    
    ax5.pie(allocations, labels=measures, colors=colors_alloc,
           autopct='%1.0f%%', shadow=True, startangle=90,
           textprops={'fontsize': 9, 'weight': 'bold'})
    ax5.set_title(f'预算分配方案（{strategy["budget"]}万元）',
                 fontsize=12, fontweight='bold')
    
    # 6. 综合效益对比
    ax6 = plt.subplot(2, 3, 6)
    
    # 灰色基础设施 vs 绿色基础设施
    scenarios = ['纯灰色\n基础设施', '灰绿结合\n(30%LID)', '高比例绿色\n(50%LID)']
    
    # 多指标评分
    indicators = ['径流控制', '峰值削减', '水质改善', '生态效益', '景观价值', '经济性']
    gray_scores = [75, 80, 40, 20, 30, 60]
    hybrid_scores = [85, 82, 75, 70, 75, 75]
    green_scores = [88, 85, 85, 90, 90, 70]
    
    x = np.arange(len(indicators))
    width = 0.25
    
    ax6.bar(x - width, gray_scores, width, label=scenarios[0],
           color='gray', edgecolor='black', linewidth=1)
    ax6.bar(x, hybrid_scores, width, label=scenarios[1],
           color='lightgreen', edgecolor='black', linewidth=1)
    ax6.bar(x + width, green_scores, width, label=scenarios[2],
           color='green', edgecolor='black', linewidth=1)
    
    ax6.set_xticks(x)
    ax6.set_xticklabels(indicators, rotation=45, ha='right', fontsize=8)
    ax6.set_ylabel('评分', fontsize=10)
    ax6.set_title('不同方案综合效益对比', fontsize=12, fontweight='bold')
    ax6.legend(fontsize=8)
    ax6.grid(True, alpha=0.3, axis='y')
    ax6.set_ylim([0, 100])
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'flood_control_strategy.png', dpi=300)
    print(f"\n图表已保存: flood_control_strategy.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
