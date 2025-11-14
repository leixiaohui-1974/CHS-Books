#!/usr/bin/env python3
"""案例33：退化湿地生态补水方案"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.lake_wetland import WetlandRestoration

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例33：退化湿地生态补水方案设计")
    print("=" * 70)
    
    # 湿地参数
    wetland = WetlandRestoration(
        wetland_area=500.0,  # 500 ha
        target_water_depth=0.8  # 目标水深0.8m
    )
    
    print(f"\n湿地基本参数:")
    print(f"  面积: {wetland.A / 1e4:.1f} ha")
    print(f"  目标水深: {wetland.h_target:.2f} m")
    
    # 1. 生态需水量
    monthly_et = np.array([30, 40, 80, 120, 150, 180,
                          200, 180, 120, 80, 50, 35])  # mm/month
    seepage = 20.0  # mm/d平均值
    
    typical_et = 150.0  # mm/d (夏季)
    Q_eco = wetland.ecological_water_requirement(typical_et, seepage)
    
    print(f"\n生态需水量（夏季典型值）:")
    print(f"  蒸散发: {typical_et} mm/d")
    print(f"  渗漏: {seepage} mm/d")
    print(f"  日需水量: {Q_eco:.1f} m³/d")
    print(f"  年需水量: {Q_eco * 365 / 1e4:.2f} 万m³/年")
    
    # 2. 水位恢复时间
    current_depth = 0.2  # m
    # 补水流量需要超过蒸散发量(~750,000 m³/d)才能恢复水位
    inflow_scenarios = [800000, 1000000, 1500000, 2000000]  # m³/d
    
    print(f"\n水位恢复时间分析（当前水深{current_depth}m）:")
    recovery_times = []
    for inflow in inflow_scenarios:
        days = wetland.water_level_recovery_time(current_depth, inflow, typical_et)
        recovery_times.append(days)
        print(f"  补水{inflow} m³/d: {days:.1f} 天")
    
    # 3. 植被适宜性
    water_depths = np.linspace(0, 3.0, 50)
    inundation_period = 240  # 天
    
    print(f"\n植被适宜性评价（淹没{inundation_period}天）:")
    suitability_scores = []
    for depth in water_depths:
        result = wetland.vegetation_suitability(depth, inundation_period)
        suitability_scores.append(result['suitability_score'])
    
    # 典型水深的适宜植被
    typical_depths = [0.2, 0.5, 1.0, 2.0]
    for depth in typical_depths:
        result = wetland.vegetation_suitability(depth, inundation_period)
        print(f"  水深{depth}m: {', '.join(result['suitable_vegetation']) if result['suitable_vegetation'] else '无适宜植被'}")
    
    # 4. 最优补水方案
    available_water = 800000  # m³/year
    schedule = wetland.optimal_supplement_schedule(monthly_et, available_water)
    
    print(f"\n年度补水方案:")
    print(f"  总需水量: {schedule['total_demand'] / 1e4:.2f} 万m³")
    print(f"  可用水量: {schedule['available_water'] / 1e4:.2f} 万m³")
    print(f"  水量缺口: {schedule['water_deficit'] / 1e4:.2f} 万m³")
    print(f"  满足率: {schedule['satisfaction_rate']:.1f}%")
    
    print(f"\n月度补水计划:")
    for i, (month, demand, supply) in enumerate(zip(
        schedule['months'],
        schedule['monthly_demand'],
        schedule['monthly_supplement']
    )):
        print(f"  {month}: 需求{demand/1000:.1f}千m³, 补给{supply/1000:.1f}千m³")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 月度蒸散发与补水方案
    ax1 = plt.subplot(2, 3, 1)
    x_pos = np.arange(12)
    width = 0.35
    
    ax1.bar(x_pos - width/2, schedule['monthly_demand'] / 1000, width,
           label='需水量', color='lightcoral', edgecolor='black', linewidth=1.5)
    ax1.bar(x_pos + width/2, schedule['monthly_supplement'] / 1000, width,
           label='补水量', color='lightblue', edgecolor='black', linewidth=1.5)
    
    ax1.set_xlabel('月份', fontsize=10)
    ax1.set_ylabel('水量 (千m³)', fontsize=10)
    ax1.set_title('月度需水量与补水方案', fontsize=12, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(schedule['months'], rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 2. 水位恢复时间
    ax2 = plt.subplot(2, 3, 2)
    ax2.bar(range(len(inflow_scenarios)), recovery_times,
           color='steelblue', edgecolor='black', linewidth=1.5)
    ax2.set_xlabel('补水流量方案', fontsize=10)
    ax2.set_ylabel('恢复时间 (天)', fontsize=10)
    ax2.set_title('不同补水流量下的水位恢复时间', fontsize=12, fontweight='bold')
    ax2.set_xticks(range(len(inflow_scenarios)))
    ax2.set_xticklabels([f'{q/1000:.0f}千' for q in inflow_scenarios])
    ax2.grid(True, alpha=0.3, axis='y')
    
    for i, (flow, time) in enumerate(zip(inflow_scenarios, recovery_times)):
        ax2.text(i, time + 2, f'{time:.0f}天',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 3. 植被适宜性随水深变化
    ax3 = plt.subplot(2, 3, 3)
    ax3.plot(water_depths, suitability_scores, 'g-', linewidth=2)
    ax3.axvline(wetland.h_target, color='r', linestyle='--', linewidth=2,
               alpha=0.7, label=f'目标水深 {wetland.h_target}m')
    ax3.fill_between(water_depths, 0, suitability_scores, alpha=0.3, color='green')
    
    ax3.set_xlabel('水深 (m)', fontsize=10)
    ax3.set_ylabel('适宜性评分', fontsize=10)
    ax3.set_title('植被适宜性随水深变化', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim([0, 3])
    ax3.set_ylim([0, 1])
    
    # 4. 水量平衡示意图
    ax4 = plt.subplot(2, 3, 4)
    
    # 水量平衡组分
    components = ['补水', '降雨', '蒸散发', '渗漏', '地表径流']
    inflows = [schedule['available_water'], 300000]  # 补水 + 降雨
    outflows = [schedule['total_demand'], 100000, 50000]  # ET + 渗漏 + 径流
    
    # 入流
    bottom = 0
    colors_in = ['blue', 'skyblue']
    for i, (label, value) in enumerate(zip(['补水', '降雨'], inflows)):
        ax4.bar(0, value / 1e4, bottom=bottom, label=label,
               color=colors_in[i], edgecolor='black', linewidth=1.5)
        ax4.text(0, bottom + value / 1e4 / 2, f'{value/1e4:.0f}万m³',
                ha='center', va='center', fontsize=9, fontweight='bold')
        bottom += value / 1e4
    
    # 出流
    bottom = 0
    colors_out = ['red', 'orange', 'gray']
    for i, (label, value) in enumerate(zip(['蒸散发', '渗漏', '径流'], outflows)):
        ax4.bar(1, value / 1e4, bottom=bottom, label=label,
               color=colors_out[i], edgecolor='black', linewidth=1.5)
        ax4.text(1, bottom + value / 1e4 / 2, f'{value/1e4:.0f}万m³',
                ha='center', va='center', fontsize=9, fontweight='bold')
        bottom += value / 1e4
    
    ax4.set_xticks([0, 1])
    ax4.set_xticklabels(['入流', '出流'])
    ax4.set_ylabel('水量 (万m³)', fontsize=10)
    ax4.set_title('年度水量平衡', fontsize=12, fontweight='bold')
    ax4.legend(loc='upper left', fontsize=8)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. 不同淹没天数下的植被类型
    ax5 = plt.subplot(2, 3, 5)
    
    inundation_days_range = np.arange(30, 366, 30)
    vegetation_counts = {
        '挺水植物': [],
        '浮叶植物': [],
        '沉水植物': [],
        '湿生植物': []
    }
    
    for days in inundation_days_range:
        result = wetland.vegetation_suitability(wetland.h_target, days)
        for veg_type in vegetation_counts.keys():
            vegetation_counts[veg_type].append(1 if veg_type in result['suitable_vegetation'] else 0)
    
    # 堆叠面积图
    bottom = np.zeros(len(inundation_days_range))
    colors_veg = ['green', 'lightgreen', 'darkgreen', 'yellowgreen']
    
    for (veg_type, counts), color in zip(vegetation_counts.items(), colors_veg):
        ax5.bar(inundation_days_range, counts, bottom=bottom, label=veg_type,
               color=color, edgecolor='black', linewidth=0.5, width=25)
        bottom += counts
    
    ax5.set_xlabel('淹没天数', fontsize=10)
    ax5.set_ylabel('适宜植被类型数', fontsize=10)
    ax5.set_title(f'淹没时长对植被适宜性的影响（水深{wetland.h_target}m）',
                 fontsize=12, fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 6. 湿地恢复效果预期
    ax6 = plt.subplot(2, 3, 6)
    
    years = np.arange(0, 6)
    indicators = {
        '植被覆盖度': [10, 30, 50, 70, 85, 90],
        '鸟类种类数': [5, 12, 20, 28, 35, 40],
        '水质指标': [40, 55, 70, 80, 88, 92]
    }
    
    for indicator, values in indicators.items():
        ax6.plot(years, values, marker='o', linewidth=2, markersize=8, label=indicator)
    
    ax6.set_xlabel('补水年限', fontsize=10)
    ax6.set_ylabel('恢复程度 (%)', fontsize=10)
    ax6.set_title('湿地生态恢复效果预期', fontsize=12, fontweight='bold')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    ax6.set_xlim([0, 5])
    ax6.set_ylim([0, 100])
    
    # 标注关键节点
    ax6.axvline(3, color='r', linestyle='--', alpha=0.5)
    ax6.text(3, 95, '达标年限', ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'wetland_restoration_plan.png', dpi=300)
    print(f"\n图表已保存: wetland_restoration_plan.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
