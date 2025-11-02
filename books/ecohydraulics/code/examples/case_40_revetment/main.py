#!/usr/bin/env python3
"""案例40：海岸带生态护岸设计"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.estuary_coastal import EcologicalRevetment

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例40：海岸带生态护岸设计")
    print("=" * 70)
    
    # 护岸参数
    revetment = EcologicalRevetment(
        revetment_length=200.0,  # 200m
        slope_angle=30.0,        # 30度
        design_wave_height=2.0   # 2m
    )
    
    print(f"\n护岸基本参数:")
    print(f"  护岸长度: {revetment.L:.1f} m")
    print(f"  坡度角: {revetment.alpha:.1f}°")
    print(f"  设计波高: {revetment.H_design:.1f} m")
    
    # 1. 波浪爬高
    runup = revetment.wave_runup(2.0, 10.0)
    print(f"\n波浪爬高: {runup:.2f} m")
    
    # 2. 稳定性分析
    stability = revetment.stability_analysis(0.5, 2650)
    print(f"\n稳定性分析:")
    print(f"  所需块石重量: {stability['required_weight']:.1f} kg")
    print(f"  实际块石重量: {stability['actual_weight']:.1f} kg")
    print(f"  安全系数: {stability['safety_factor']:.2f}")
    print(f"  稳定性评价: {stability['stability']}")
    
    # 3. 植被设计
    print(f"\n植被配置设计:")
    for zone in ['high', 'middle', 'low']:
        veg = revetment.vegetation_design(zone)
        print(f"  {veg['tidal_zone']}潮区: {', '.join(veg['species'][:2])}, "
              f"密度{veg['planting_density']}株/m²")
    
    # 4. 生态功能
    eco_func = revetment.ecological_function_assessment()
    print(f"\n生态功能评估:")
    print(f"  生境面积: {eco_func['habitat_area']:.0f} m²")
    print(f"  生物多样性评分: {eco_func['biodiversity_score']:.0f}")
    print(f"  综合评分: {eco_func['overall_score']:.0f}")
    
    # 5. 成本对比
    cost = revetment.cost_comparison(5000)
    print(f"\n成本对比分析:")
    print(f"  生态护岸建设成本: {cost['ecological_initial']:.1f} 万元")
    print(f"  传统护岸建设成本: {cost['traditional_initial']:.1f} 万元")
    print(f"  20年生命周期节约: {cost['lifecycle_savings']:.1f} 万元")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 波浪爬高vs波高
    ax1 = plt.subplot(2, 3, 1)
    wave_heights = np.linspace(0.5, 3.0, 20)
    runups = [revetment.wave_runup(H, 10.0) for H in wave_heights]
    
    ax1.plot(wave_heights, runups, 'b-o', linewidth=2, markersize=6)
    ax1.set_xlabel('波高 (m)', fontsize=10)
    ax1.set_ylabel('波浪爬高 (m)', fontsize=10)
    ax1.set_title('波浪爬高计算', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 2. 稳定性分析
    ax2 = plt.subplot(2, 3, 2)
    stone_sizes = np.linspace(0.2, 1.0, 20)
    safety_factors = []
    for size in stone_sizes:
        stab = revetment.stability_analysis(size)
        safety_factors.append(stab['safety_factor'])
    
    ax2.plot(stone_sizes, safety_factors, 'g-', linewidth=2)
    ax2.axhline(1.5, color='g', linestyle='--', linewidth=2, label='安全标准')
    ax2.axhline(1.0, color='orange', linestyle='--', linewidth=2, label='临界值')
    ax2.fill_between(stone_sizes, 0, 1.0, color='red', alpha=0.2)
    ax2.fill_between(stone_sizes, 1.0, 1.5, color='yellow', alpha=0.2)
    ax2.fill_between(stone_sizes, 1.5, 4, color='green', alpha=0.2)
    ax2.set_xlabel('块石粒径 (m)', fontsize=10)
    ax2.set_ylabel('安全系数', fontsize=10)
    ax2.set_title('块石稳定性分析', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 4])
    
    # 3. 护岸剖面示意图
    ax3 = plt.subplot(2, 3, 3)
    
    x = np.linspace(0, 20, 100)
    slope_line = x * np.tan(np.radians(revetment.alpha))
    
    ax3.fill_between(x, 0, slope_line, color='brown', alpha=0.3, label='护岸坡面')
    ax3.fill_between(x, 0, -2, color='lightblue', alpha=0.5, label='水体')
    
    # 植被分带
    ax3.fill_between([0, 5], [0, 0], [3, 3], color='darkgreen', alpha=0.5, label='高潮带植被')
    ax3.fill_between([5, 12], [0, 0], [3, 3], color='green', alpha=0.5, label='中潮带植被')
    ax3.fill_between([12, 20], [0, 0], [1, 1], color='lightgreen', alpha=0.5, label='低潮带植被')
    
    ax3.set_xlabel('距离 (m)', fontsize=10)
    ax3.set_ylabel('高程 (m)', fontsize=10)
    ax3.set_title('生态护岸剖面示意图', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim([0, 20])
    ax3.set_ylim([-2, 8])
    
    # 4. 成本对比
    ax4 = plt.subplot(2, 3, 4)
    
    categories = ['建设成本', '20年维护', '20年总成本']
    eco_costs = [cost['ecological_initial'], 
                cost['ecological_lifecycle'] - cost['ecological_initial'],
                cost['ecological_lifecycle']]
    trad_costs = [cost['traditional_initial'],
                 cost['traditional_lifecycle'] - cost['traditional_initial'],
                 cost['traditional_lifecycle']]
    
    x = np.arange(len(categories))
    width = 0.35
    
    ax4.bar(x - width/2, eco_costs, width, label='生态护岸', 
           color='lightgreen', edgecolor='black', linewidth=1.5)
    ax4.bar(x + width/2, trad_costs, width, label='传统护岸',
           color='lightcoral', edgecolor='black', linewidth=1.5)
    
    ax4.set_xticks(x)
    ax4.set_xticklabels(categories)
    ax4.set_ylabel('成本 (万元)', fontsize=10)
    ax4.set_title('全生命周期成本对比', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. 综合效益雷达图
    ax5 = plt.subplot(2, 3, 5, projection='polar')
    
    categories = ['防浪效果', '稳定性', '生态功能', '景观价值', '经济性']
    eco_scores = [85, 80, 90, 95, 85]
    trad_scores = [90, 95, 20, 40, 70]
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    eco_scores += eco_scores[:1]
    trad_scores += trad_scores[:1]
    angles += angles[:1]
    
    ax5.plot(angles, eco_scores, 'go-', linewidth=2, label='生态护岸')
    ax5.fill(angles, eco_scores, alpha=0.25, color='green')
    ax5.plot(angles, trad_scores, 'ro-', linewidth=2, label='传统护岸')
    ax5.fill(angles, trad_scores, alpha=0.25, color='red')
    
    ax5.set_xticks(angles[:-1])
    ax5.set_xticklabels(categories, fontsize=9)
    ax5.set_ylim(0, 100)
    ax5.set_title('综合效益对比', fontsize=12, fontweight='bold', pad=20)
    ax5.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax5.grid(True)
    
    # 6. 植被配置方案
    ax6 = plt.subplot(2, 3, 6)
    
    zones = ['高潮带', '中潮带', '低潮带']
    densities = [4, 16, 100]
    colors_veg = ['darkgreen', 'green', 'lightgreen']
    
    bars = ax6.bar(zones, densities, color=colors_veg,
                   edgecolor='black', linewidth=1.5)
    ax6.set_ylabel('种植密度 (株/m²)', fontsize=10)
    ax6.set_title('植被配置方案', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='y')
    ax6.set_yscale('log')
    
    for bar, density in zip(bars, densities):
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.5,
                f'{density}', ha='center', va='bottom',
                fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'ecological_revetment_design.png', dpi=300)
    print(f"\n图表已保存: ecological_revetment_design.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
