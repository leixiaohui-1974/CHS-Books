#!/usr/bin/env python3
"""案例41：河口湿地碳汇功能"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.estuary_coastal import EstuarineWetlandCarbon

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例41：河口湿地碳汇功能评估")
    print("=" * 70)
    
    # 湿地参数
    wetland = EstuarineWetlandCarbon(
        wetland_area=100.0,  # 100公顷
        vegetation_type='mangrove'
    )
    
    print(f"\n湿地基本参数:")
    print(f"  面积: {wetland.A / 1e4:.1f} ha")
    print(f"  植被类型: {wetland.veg_type}")
    
    # 1. 净初级生产力
    npp = wetland.net_primary_production()
    print(f"\n净初级生产力: {npp:.0f} gC/m²/year")
    
    # 2. 碳固定速率
    seq = wetland.carbon_sequestration_rate()
    print(f"\n碳固定速率:")
    print(f"  埋藏效率: {seq['burial_efficiency']:.1f}%")
    print(f"  埋藏速率: {seq['burial_rate']:.1f} gC/m²/year")
    print(f"  总碳固定: {seq['total_sequestration']:.1f} tC/year")
    print(f"  CO2当量: {seq['co2_equivalent']:.1f} tCO2/year")
    
    # 3. 土壤碳储量
    soil_c = wetland.soil_carbon_stock(1.0)
    print(f"\n土壤碳储量（1m深度）: {soil_c:.0f} tC/ha")
    
    # 4. 蓝碳项目潜力
    blue_carbon = wetland.blue_carbon_potential(20)
    print(f"\n蓝碳项目潜力（20年）:")
    print(f"  总固碳量: {blue_carbon['total_carbon_sequestration']:.1f} tC")
    print(f"  碳信用价值: {blue_carbon['carbon_credit_value']:.1f} 万元")
    print(f"  总生态价值: {blue_carbon['total_ecosystem_value']:.1f} 万元")
    print(f"  年均价值: {blue_carbon['annual_value_per_ha']:.2f} 万元/ha/年")
    
    # 5. 温室气体排放
    ghg = wetland.greenhouse_gas_emissions(5.0)
    print(f"\n温室气体评估:")
    print(f"  CH4排放: {ghg['ch4_emission']:.2f} tCH4/year")
    print(f"  N2O排放: {ghg['n2o_emission']:.3f} tN2O/year")
    print(f"  总排放（CO2eq）: {ghg['total_ghg_emission']:.1f} tCO2eq/year")
    print(f"  净碳平衡: {ghg['net_carbon_balance']:.1f} tCO2eq/year")
    print(f"  是否为碳汇: {'是' if ghg['is_carbon_sink'] else '否'}")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 不同植被类型NPP对比
    ax1 = plt.subplot(2, 3, 1)
    veg_types = ['mangrove', 'salt_marsh', 'seagrass', 'mudflat']
    veg_names = ['红树林', '盐沼', '海草床', '光滩']
    npps = []
    
    for veg in veg_types:
        wl_temp = EstuarineWetlandCarbon(100, veg)
        npps.append(wl_temp.net_primary_production())
    
    colors_veg = ['darkgreen', 'green', 'lightgreen', 'brown']
    bars = ax1.bar(veg_names, npps, color=colors_veg,
                   edgecolor='black', linewidth=1.5)
    ax1.set_ylabel('NPP (gC/m²/year)', fontsize=10)
    ax1.set_title('不同植被类型净初级生产力', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    for bar, npp_val in zip(bars, npps):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                f'{npp_val:.0f}', ha='center', va='bottom',
                fontsize=9, fontweight='bold')
    
    # 2. 碳固定速率对比
    ax2 = plt.subplot(2, 3, 2)
    seq_rates = []
    for veg in veg_types:
        wl_temp = EstuarineWetlandCarbon(100, veg)
        seq_rates.append(wl_temp.carbon_sequestration_rate()['burial_rate'])
    
    ax2.bar(veg_names, seq_rates, color=colors_veg,
           edgecolor='black', linewidth=1.5)
    ax2.set_ylabel('碳埋藏速率 (gC/m²/year)', fontsize=10)
    ax2.set_title('碳固定速率对比', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. 20年碳累积
    ax3 = plt.subplot(2, 3, 3)
    years = np.arange(0, 21)
    cumulative_carbon = years * seq['total_sequestration']
    cumulative_value = cumulative_carbon * 44/12 * 50 / 1e4  # 万元
    
    ax3.plot(years, cumulative_carbon, 'g-', linewidth=2, marker='o',
            markersize=6, label='累积固碳')
    ax3.set_xlabel('年份', fontsize=10)
    ax3.set_ylabel('累积碳固定 (tC)', fontsize=10)
    ax3.set_title('20年碳累积曲线', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    ax3_twin = ax3.twinx()
    ax3_twin.plot(years, cumulative_value, 'b--', linewidth=2, label='累积价值')
    ax3_twin.set_ylabel('累积价值 (万元)', fontsize=10, color='b')
    ax3_twin.tick_params(axis='y', labelcolor='b')
    
    # 4. 碳平衡示意图
    ax4 = plt.subplot(2, 3, 4)
    
    components = ['NPP', '埋藏', 'CH4排放', 'N2O排放', '净固碳']
    values = [npp * wetland.A / 1e6,  # tC/year
             seq['total_sequestration'],
             -ghg['ch4_co2_equivalent'] * 12/44,  # 转为tC
             -ghg['n2o_co2_equivalent'] * 12/44,
             ghg['net_carbon_balance'] * 12/44]
    colors_comp = ['green', 'darkgreen', 'red', 'orange', 'blue']
    
    bars = ax4.barh(components, values, color=colors_comp,
                    edgecolor='black', linewidth=1.5)
    ax4.set_xlabel('碳通量 (tC/year)', fontsize=10)
    ax4.set_title('碳平衡组分', fontsize=12, fontweight='bold')
    ax4.axvline(0, color='k', linewidth=1)
    ax4.grid(True, alpha=0.3, axis='x')
    
    for bar, val in zip(bars, values):
        x_pos = bar.get_width() + (5 if val > 0 else -5)
        ax4.text(x_pos, bar.get_y() + bar.get_height()/2,
                f'{val:.0f}', va='center', fontsize=9, fontweight='bold')
    
    # 5. 蓝碳项目经济价值
    ax5 = plt.subplot(2, 3, 5)
    
    value_components = ['碳信用', '生物多样性', '水质净化']
    value_amounts = [blue_carbon['carbon_credit_value'],
                    blue_carbon['biodiversity_value'],
                    blue_carbon['water_purification_value']]
    colors_val = ['green', 'yellow', 'cyan']
    
    bars = ax5.bar(value_components, value_amounts, color=colors_val,
                   edgecolor='black', linewidth=1.5)
    ax5.set_ylabel('价值 (万元)', fontsize=10)
    ax5.set_title('蓝碳项目生态服务价值（20年）', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, value_amounts):
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                f'{val:.0f}', ha='center', va='bottom',
                fontsize=9, fontweight='bold')
    
    # 6. 土壤碳储量垂向分布
    ax6 = plt.subplot(2, 3, 6)
    depths = np.linspace(0, 2, 50)
    carbon_density = 250  # tC/ha/m (红树林)
    cumulative_stocks = carbon_density * depths
    
    ax6.fill_betweenx(depths, 0, cumulative_stocks, color='brown', alpha=0.5)
    ax6.plot(cumulative_stocks, depths, 'k-', linewidth=2)
    ax6.set_xlabel('土壤碳储量 (tC/ha)', fontsize=10)
    ax6.set_ylabel('土壤深度 (m)', fontsize=10)
    ax6.set_title('土壤碳储量垂向分布', fontsize=12, fontweight='bold')
    ax6.invert_yaxis()
    ax6.grid(True, alpha=0.3)
    ax6.set_xlim([0, 600])
    
    # 标注典型深度
    for d, label in [(1.0, '1m: 250 tC/ha'), (2.0, '2m: 500 tC/ha')]:
        stock = carbon_density * d
        ax6.plot(stock, d, 'ro', markersize=8)
        ax6.text(stock + 30, d, label, va='center', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'wetland_carbon_sequestration.png', dpi=300)
    print(f"\n图表已保存: wetland_carbon_sequestration.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
