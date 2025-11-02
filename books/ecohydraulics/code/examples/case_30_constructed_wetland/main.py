#!/usr/bin/env python3
"""案例30：人工湿地水力停留时间优化"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.lake_wetland import ConstructedWetland, design_wetland_system

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例30：人工湿地水力停留时间（HRT）优化设计")
    print("=" * 70)
    
    # 设计参数
    inlet_flow = 1000.0  # m³/d
    inlet_COD = 150.0  # mg/L
    target_removal = 80.0  # %
    
    print(f"\n设计条件:")
    print(f"  进水流量: {inlet_flow} m³/d")
    print(f"  进水COD浓度: {inlet_COD} mg/L")
    print(f"  目标去除率: {target_removal}%")
    
    # 1. 系统设计
    design = design_wetland_system(
        target_removal_rate=target_removal,
        inlet_flow=inlet_flow,
        inlet_concentration=inlet_COD,
        pollutant='COD'
    )
    
    print(f"\n推荐设计方案:")
    print(f"  长度: {design['dimensions']['length']:.1f} m")
    print(f"  宽度: {design['dimensions']['width']:.1f} m")
    print(f"  深度: {design['dimensions']['depth']:.1f} m")
    print(f"  总面积: {design['dimensions']['area']:.1f} m²")
    print(f"  有效容积: {design['dimensions']['volume']:.1f} m³")
    
    print(f"\n水力参数:")
    print(f"  水力停留时间: {design['hydraulics']['HRT']:.2f} 天")
    print(f"  水力负荷: {design['hydraulics']['hydraulic_loading']:.2f} m³/(m²·d)")
    
    print(f"\n处理效果:")
    perf = design['performance']
    print(f"  进水浓度: {perf['inlet_concentration']:.1f} mg/L")
    print(f"  出水浓度: {perf['outlet_concentration']:.1f} mg/L")
    print(f"  去除率: {perf['removal_rate']:.1f}%")
    print(f"  去除系数: {perf['removal_coefficient']:.2f} 1/d")
    
    # 2. HRT对去除率的影响
    wetland = ConstructedWetland(
        length=design['dimensions']['length'],
        width=design['dimensions']['width'],
        depth=design['dimensions']['depth']
    )
    
    HRTs = np.linspace(0.5, 10, 50)
    removals_COD = []
    removals_TN = []
    removals_TP = []
    
    for HRT in HRTs:
        result_COD = wetland.pollutant_removal(inlet_COD, HRT, 'COD')
        result_TN = wetland.pollutant_removal(30.0, HRT, 'TN')
        result_TP = wetland.pollutant_removal(3.0, HRT, 'TP')
        
        removals_COD.append(result_COD['removal_rate'])
        removals_TN.append(result_TN['removal_rate'])
        removals_TP.append(result_TP['removal_rate'])
    
    # 3. 长宽比优化
    optimization = wetland.aspect_ratio_optimization(
        target_HRT=design['hydraulics']['HRT'],
        total_area=design['dimensions']['area']
    )
    
    print(f"\n长宽比优化分析:")
    print(f"  推荐长宽比: {optimization['optimal_ratio']}:1")
    optimal = optimization['optimal_scenario']
    print(f"  长度: {optimal['length']:.1f} m")
    print(f"  宽度: {optimal['width']:.1f} m")
    print(f"  有效容积比: {optimal['effective_volume_ratio']:.2f}")
    
    # 4. 多污染物处理
    pollutants = ['COD', 'BOD', 'TN', 'TP', 'NH3N']
    inlet_concs = [150, 80, 30, 3, 15]
    
    print(f"\n多污染物处理效果（HRT={design['hydraulics']['HRT']:.1f}天）:")
    results_table = []
    for pol, conc in zip(pollutants, inlet_concs):
        result = wetland.pollutant_removal(conc, design['hydraulics']['HRT'], pol)
        results_table.append(result)
        print(f"  {pol:6s}: {conc:6.1f} → {result['outlet_concentration']:6.2f} mg/L "
              f"(去除{result['removal_rate']:.1f}%)")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. HRT-去除率关系
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(HRTs, removals_COD, 'b-', linewidth=2, label='COD')
    ax1.plot(HRTs, removals_TN, 'g-', linewidth=2, label='TN')
    ax1.plot(HRTs, removals_TP, 'r-', linewidth=2, label='TP')
    ax1.axhline(target_removal, color='k', linestyle='--', alpha=0.5, label='目标去除率')
    ax1.axvline(design['hydraulics']['HRT'], color='orange', linestyle='--', 
               alpha=0.5, label='设计HRT')
    ax1.set_xlabel('水力停留时间 (天)', fontsize=10)
    ax1.set_ylabel('去除率 (%)', fontsize=10)
    ax1.set_title('HRT对去除率的影响', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 10])
    ax1.set_ylim([0, 100])
    
    # 2. 长宽比优化
    ax2 = plt.subplot(2, 3, 2)
    ratios = [s['length_width_ratio'] for s in optimization['all_scenarios']]
    e_values = [s['effective_volume_ratio'] for s in optimization['all_scenarios']]
    
    ax2.bar(ratios, e_values, color='steelblue', edgecolor='black', linewidth=1.5)
    ax2.axhline(optimization['optimal_scenario']['effective_volume_ratio'],
               color='r', linestyle='--', linewidth=2, label='最优值')
    ax2.set_xlabel('长宽比', fontsize=10)
    ax2.set_ylabel('有效容积比', fontsize=10)
    ax2.set_title('长宽比对有效容积的影响', fontsize=12, fontweight='bold')
    ax2.set_ylim([0, 1])
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. 示踪剂曲线（理论）
    ax3 = plt.subplot(2, 3, 3)
    t = np.linspace(0, design['hydraulics']['HRT'] * 3, 100)
    
    # 理想推流式
    C_plug = np.zeros_like(t)
    C_plug[abs(t - design['hydraulics']['HRT']) < 0.1 * design['hydraulics']['HRT']] = 1.0
    
    # 理想完全混合式
    C_cstr = np.exp(-t / design['hydraulics']['HRT']) / design['hydraulics']['HRT']
    
    # 实际湿地（介于两者之间）
    e = optimal['effective_volume_ratio']
    t_p = design['hydraulics']['HRT'] * e
    C_actual = np.exp(-(t - t_p)**2 / (2 * (design['hydraulics']['HRT'] * 0.3)**2))
    C_actual = C_actual / np.max(C_actual)
    
    ax3.plot(t, C_plug, 'b-', linewidth=2, label='理想推流')
    ax3.plot(t, C_cstr, 'r-', linewidth=2, label='理想混合')
    ax3.plot(t, C_actual, 'g-', linewidth=2, label='实际湿地')
    ax3.axvline(design['hydraulics']['HRT'], color='k', linestyle='--', 
               alpha=0.5, label='理论HRT')
    ax3.set_xlabel('时间 (天)', fontsize=10)
    ax3.set_ylabel('归一化浓度', fontsize=10)
    ax3.set_title('示踪剂响应曲线', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 多污染物去除效果
    ax4 = plt.subplot(2, 3, 4)
    x_pos = np.arange(len(pollutants))
    removal_rates = [r['removal_rate'] for r in results_table]
    colors = ['blue', 'green', 'orange', 'red', 'purple']
    
    bars = ax4.bar(x_pos, removal_rates, color=colors, edgecolor='black', linewidth=1.5)
    ax4.set_xlabel('污染物', fontsize=10)
    ax4.set_ylabel('去除率 (%)', fontsize=10)
    ax4.set_title('多污染物去除效果', fontsize=12, fontweight='bold')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(pollutants)
    ax4.set_ylim([0, 100])
    ax4.axhline(target_removal, color='k', linestyle='--', linewidth=2, 
               alpha=0.5, label=f'目标{target_removal}%')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 在柱子上标注数值
    for i, (bar, rate) in enumerate(zip(bars, removal_rates)):
        ax4.text(bar.get_x() + bar.get_width()/2, rate + 2,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 5. 湿地平面布置图
    ax5 = plt.subplot(2, 3, 5)
    L = design['dimensions']['length']
    W = design['dimensions']['width']
    
    # 绘制湿地外框
    ax5.add_patch(plt.Rectangle((0, 0), L, W, fill=False, 
                                edgecolor='black', linewidth=3))
    
    # 绘制内部分区（多级串联）
    n_cells = 3
    cell_length = L / n_cells
    for i in range(n_cells - 1):
        ax5.axvline((i + 1) * cell_length, color='gray', linestyle='--', linewidth=2)
    
    # 标注进出水口
    ax5.plot([0, 0], [W*0.4, W*0.6], 'b-', linewidth=8, label='进水口')
    ax5.plot([L, L], [W*0.4, W*0.6], 'r-', linewidth=8, label='出水口')
    
    # 标注流向
    for i in range(n_cells):
        x = (i + 0.5) * cell_length
        ax5.arrow(x, W/2, cell_length*0.3, 0, head_width=W*0.1,
                 head_length=cell_length*0.1, fc='green', ec='green', alpha=0.5)
    
    # 标注尺寸
    ax5.text(L/2, -W*0.15, f'L = {L:.1f} m', ha='center', fontsize=10)
    ax5.text(-L*0.1, W/2, f'W = {W:.1f} m', ha='center', va='center',
            rotation=90, fontsize=10)
    
    ax5.set_xlim([-L*0.15, L*1.05])
    ax5.set_ylim([-W*0.2, W*1.1])
    ax5.set_aspect('equal')
    ax5.set_title('湿地平面布置图', fontsize=12, fontweight='bold')
    ax5.legend(loc='upper right')
    ax5.axis('off')
    
    # 6. 投资与运行成本估算
    ax6 = plt.subplot(2, 3, 6)
    
    # 成本估算（简化）
    construction_cost = design['dimensions']['area'] * 300  # 元/m²
    operation_cost_annual = inlet_flow * 365 * 0.5  # 元/年
    
    categories = ['土建工程', '设备安装', '植物种植', '运行维护\n(年)']
    costs = [
        construction_cost * 0.5,
        construction_cost * 0.3,
        construction_cost * 0.2,
        operation_cost_annual
    ]
    colors_cost = ['brown', 'gray', 'green', 'blue']
    
    bars = ax6.bar(categories, np.array(costs) / 1e4, color=colors_cost,
                   edgecolor='black', linewidth=1.5)
    ax6.set_ylabel('成本 (万元)', fontsize=10)
    ax6.set_title('投资与运行成本估算', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='y')
    
    # 标注数值
    for bar, cost in zip(bars, costs):
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{cost/1e4:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    total_construction = sum(costs[:3])
    ax6.text(0.5, 0.95, f'总投资: {total_construction/1e4:.1f}万元',
            transform=ax6.transAxes, ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'constructed_wetland_design.png', dpi=300)
    print(f"\n图表已保存: constructed_wetland_design.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
