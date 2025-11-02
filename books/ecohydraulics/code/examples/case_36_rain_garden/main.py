#!/usr/bin/env python3
"""案例36：雨水花园/生物滞留系统"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.urban_ecohydraulics import RainGarden

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例36：雨水花园净化系统设计")
    print("=" * 70)
    
    # 雨水花园参数
    garden = RainGarden(
        garden_area=100.0,  # 100m²
        media_depth=0.6,    # 0.6m
        ponding_depth=0.3   # 0.3m
    )
    
    print(f"\n雨水花园基本参数:")
    print(f"  面积: {garden.A:.1f} m²")
    print(f"  介质层深度: {garden.d_media:.2f} m")
    print(f"  蓄水层深度: {garden.d_pond:.2f} m")
    
    # 1. 调蓄容量
    storage = garden.storage_capacity(porosity=0.4)
    print(f"\n调蓄容量:")
    print(f"  表面蓄水: {storage['surface_storage']:.1f} m³")
    print(f"  介质层蓄水: {storage['media_storage']:.1f} m³")
    print(f"  总容量: {storage['total_storage']:.1f} m³")
    print(f"  等效蓄水深度: {storage['storage_depth']:.0f} mm")
    
    # 2. 不同介质的渗透速率和排空时间
    soil_types = ['sand', 'loam', 'sandy_loam', 'clay']
    soil_names = ['砂土', '壤土', '砂壤土', '黏土']
    
    print(f"\n不同介质的排空时间:")
    inf_rates = []
    drawdown_times = []
    for soil, name in zip(soil_types, soil_names):
        inf_rate = garden.infiltration_rate(soil)
        time = garden.drawdown_time(inf_rate)
        inf_rates.append(inf_rate)
        drawdown_times.append(time)
        print(f"  {name}: 渗透速率{inf_rate}mm/h, 排空时间{time:.1f}h")
    
    # 3. 污染物去除效率
    inlet_load = {
        'TSS': 50.0,  # kg/year
        'TN': 5.0,
        'TP': 1.0,
        'Metals': 2.0
    }
    
    removal = garden.pollutant_removal_efficiency(inlet_load)
    print(f"\n污染物去除效率:")
    for pollutant in inlet_load.keys():
        print(f"  {pollutant}: 负荷{inlet_load[pollutant]:.1f}kg/年, "
              f"去除率{removal['removal_rates'][pollutant]:.0f}%, "
              f"去除量{removal['removal_amount'][pollutant]:.1f}kg/年")
    
    # 4. 植物配置方案
    print(f"\n植物配置方案:")
    water_levels = ['high', 'medium', 'low']
    water_names = ['高耐水', '中耐水', '低耐水']
    sunlight_types = ['full', 'partial', 'shade']
    sun_names = ['全日照', '半日照', '遮阴']
    
    for water, w_name in zip(water_levels[:2], water_names[:2]):
        for sun, s_name in zip(sunlight_types[:2], sun_names[:2]):
            plants = garden.plant_selection(water, sun)
            print(f"  {w_name}+{s_name}: {', '.join(plants[:3])}")
    
    # 5. 成本效益分析
    construction_cost = 300  # 元/m²
    annual_runoff = 150  # m³/年
    
    cba = garden.cost_benefit_analysis(construction_cost, annual_runoff)
    print(f"\n成本效益分析:")
    print(f"  建设成本: {cba['construction_cost']/1e4:.2f} 万元")
    print(f"  年维护成本: {cba['annual_maintenance']:.0f} 元")
    print(f"  年综合效益: {cba['annual_benefit']:.0f} 元")
    print(f"  投资回收期: {cba['payback_period']:.1f} 年")
    print(f"  20年NPV: {cba['npv_20years']/1e4:.1f} 万元")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 调蓄容量组成
    ax1 = plt.subplot(2, 3, 1)
    labels = ['表面蓄水', '介质层蓄水']
    sizes = [storage['surface_storage'], storage['media_storage']]
    colors_pie = ['lightblue', 'brown']
    explode = (0.05, 0)
    
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors_pie,
           autopct='%1.1f%%', shadow=True, startangle=90,
           textprops={'fontsize': 10, 'weight': 'bold'})
    ax1.set_title('调蓄容量组成', fontsize=12, fontweight='bold')
    
    # 2. 不同介质排空时间
    ax2 = plt.subplot(2, 3, 2)
    bars = ax2.bar(soil_names, drawdown_times, color='steelblue',
                   edgecolor='black', linewidth=1.5)
    ax2.axhline(24, color='r', linestyle='--', linewidth=2,
               alpha=0.7, label='24小时标准')
    ax2.set_ylabel('排空时间 (h)', fontsize=10)
    ax2.set_title('不同介质排空时间', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    for bar, time in zip(bars, drawdown_times):
        color = 'green' if time < 24 else 'red'
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{time:.0f}h', ha='center', va='bottom',
                fontsize=9, fontweight='bold', color=color)
    
    # 3. 污染物去除效果
    ax3 = plt.subplot(2, 3, 3)
    pollutants = list(inlet_load.keys())
    inlet_vals = list(inlet_load.values())
    removal_vals = [removal['removal_amount'][p] for p in pollutants]
    
    x = np.arange(len(pollutants))
    width = 0.35
    
    ax3.bar(x - width/2, inlet_vals, width, label='入流负荷',
           color='lightcoral', edgecolor='black', linewidth=1.5)
    ax3.bar(x + width/2, removal_vals, width, label='去除量',
           color='lightgreen', edgecolor='black', linewidth=1.5)
    
    ax3.set_xticks(x)
    ax3.set_xticklabels(pollutants)
    ax3.set_ylabel('负荷 (kg/年)', fontsize=10)
    ax3.set_title('污染物去除效果', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. 雨水花园剖面示意图
    ax4 = plt.subplot(2, 3, 4)
    
    # 绘制剖面
    width_garden = 10  # m
    x_prof = np.array([0, 0, 1, 9, 10, 10, 0])
    y_prof = np.array([0.5, 0, 0, 0, 0, 0.5, 0.5])
    
    ax4.fill(x_prof, y_prof, color='lightgreen', alpha=0.3, 
            edgecolor='black', linewidth=2, label='花园边界')
    
    # 蓄水层
    ax4.fill_between([1, 9], [0, 0], [garden.d_pond, garden.d_pond],
                    color='lightblue', alpha=0.5, label='蓄水层')
    
    # 介质层
    ax4.fill_between([1, 9], [garden.d_pond, garden.d_pond],
                    [garden.d_pond + garden.d_media, garden.d_pond + garden.d_media],
                    color='brown', alpha=0.4, label='介质层')
    
    # 原土层
    ax4.fill_between([0, 10], [-1, -1], [0, 0],
                    color='gray', alpha=0.3, label='原土层')
    
    # 标注
    ax4.text(5, garden.d_pond/2, '蓄水层', ha='center', fontsize=10,
            fontweight='bold')
    ax4.text(5, garden.d_pond + garden.d_media/2, '介质层\n(砂+壤土+堆肥)',
            ha='center', fontsize=9, fontweight='bold')
    
    # 进出水管
    ax4.arrow(0.5, 1, 0, -0.5, head_width=0.2, head_length=0.1,
             fc='blue', ec='blue', linewidth=2)
    ax4.text(0.5, 1.2, '进水', ha='center', fontsize=9, fontweight='bold')
    
    ax4.arrow(9.5, -0.5, 0, -0.3, head_width=0.2, head_length=0.1,
             fc='green', ec='green', linewidth=2)
    ax4.text(9.5, -1, '出水', ha='center', fontsize=9, fontweight='bold')
    
    ax4.set_xlabel('宽度 (m)', fontsize=10)
    ax4.set_ylabel('高程 (m)', fontsize=10)
    ax4.set_title('雨水花园剖面示意图', fontsize=12, fontweight='bold')
    ax4.legend(loc='upper right', fontsize=8)
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim([-0.5, 10.5])
    ax4.set_ylim([-1.2, 1.5])
    ax4.axhline(0, color='black', linewidth=1)
    
    # 5. 成本效益对比
    ax5 = plt.subplot(2, 3, 5)
    
    years = np.arange(0, 21)
    cumulative_cost = cba['construction_cost'] + cba['annual_maintenance'] * years
    cumulative_benefit = cba['annual_benefit'] * years
    net_benefit = cumulative_benefit - cumulative_cost
    
    ax5.plot(years, cumulative_cost / 1e4, 'r-', linewidth=2, label='累计成本')
    ax5.plot(years, cumulative_benefit / 1e4, 'g-', linewidth=2, label='累计效益')
    ax5.plot(years, net_benefit / 1e4, 'b--', linewidth=2, label='净效益')
    
    ax5.axhline(0, color='k', linestyle='-', linewidth=0.5)
    ax5.axvline(cba['payback_period'], color='orange', linestyle='--',
               linewidth=2, alpha=0.7, label=f"回收期{cba['payback_period']:.1f}年")
    
    ax5.set_xlabel('年限', fontsize=10)
    ax5.set_ylabel('金额 (万元)', fontsize=10)
    ax5.set_title('20年成本效益分析', fontsize=12, fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    ax5.set_xlim([0, 20])
    
    # 6. 综合效益评价
    ax6 = plt.subplot(2, 3, 6)
    
    categories = ['径流削减', '水质净化', '景观美化', '生物多样性', '碳汇功能']
    scores = [88, 85, 92, 78, 70]
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    scores_plot = scores + scores[:1]
    angles += angles[:1]
    
    ax6 = plt.subplot(2, 3, 6, projection='polar')
    ax6.plot(angles, scores_plot, 'o-', linewidth=2, color='green')
    ax6.fill(angles, scores_plot, alpha=0.25, color='green')
    ax6.set_xticks(angles[:-1])
    ax6.set_xticklabels(categories, fontsize=9)
    ax6.set_ylim(0, 100)
    ax6.set_title('综合效益雷达图', fontsize=12, fontweight='bold', pad=20)
    ax6.grid(True)
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'rain_garden_design.png', dpi=300)
    print(f"\n图表已保存: rain_garden_design.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
