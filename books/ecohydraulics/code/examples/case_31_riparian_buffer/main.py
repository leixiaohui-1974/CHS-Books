#!/usr/bin/env python3
"""案例31：湖滨带生态缓冲功能评估"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.lake_wetland import RiparianBuffer

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例31：湖滨带生态缓冲功能评估")
    print("=" * 70)
    
    # 缓冲带参数
    buffer = RiparianBuffer(
        buffer_width=20.0,  # 20m宽
        slope=3.0,          # 3%坡度
        vegetation_density=0.7  # 70%植被覆盖
    )
    
    print(f"\n缓冲带基本参数:")
    print(f"  宽度: {buffer.W:.1f} m")
    print(f"  坡度: {buffer.S * 100:.1f}%")
    print(f"  植被覆盖度: {buffer.V * 100:.0f}%")
    
    # 1. 径流特性分析
    rainfall = 50.0  # mm/h
    v = buffer.runoff_velocity(rainfall)
    t = buffer.residence_time(rainfall)
    
    print(f"\n径流水力特性（降雨强度{rainfall} mm/h）:")
    print(f"  径流流速: {v:.3f} m/s")
    print(f"  停留时间: {t:.1f} 分钟")
    
    # 2. 泥沙拦截
    sediment_trap = buffer.sediment_trapping()
    print(f"\n泥沙拦截率: {sediment_trap:.1f}%")
    
    # 3. 污染物削减
    pollutants = ['N', 'P', 'COD', 'TSS']
    inlet_concs = [5.0, 0.5, 80.0, 200.0]  # mg/L
    
    print(f"\n污染物削减效果:")
    results = []
    for pol, conc in zip(pollutants, inlet_concs):
        result = buffer.pollutant_removal(conc, pol)
        results.append(result)
        print(f"  {pol:4s}: {result['inlet_concentration']:6.1f} → "
              f"{result['outlet_concentration']:6.2f} mg/L "
              f"(削减{result['removal_rate']:.1f}%)")
    
    # 4. 宽度优化分析
    widths = np.linspace(5, 50, 20)
    removal_N = []
    removal_P = []
    removal_COD = []
    removal_TSS = []
    
    for w in widths:
        buffer_temp = RiparianBuffer(w, 3.0, 0.7)
        removal_N.append(buffer_temp.pollutant_removal(5.0, 'N')['removal_rate'])
        removal_P.append(buffer_temp.pollutant_removal(0.5, 'P')['removal_rate'])
        removal_COD.append(buffer_temp.pollutant_removal(80.0, 'COD')['removal_rate'])
        removal_TSS.append(buffer_temp.pollutant_removal(200.0, 'TSS')['removal_rate'])
    
    # 5. 最优宽度设计
    print(f"\n最优宽度设计（目标削减率70%）:")
    for pol in pollutants:
        optimal_w = buffer.optimal_width_design(70.0, pol)
        print(f"  {pol}: {optimal_w:.1f} m")
    
    # 6. 植被覆盖度影响
    densities = np.linspace(0.1, 0.9, 9)
    removal_by_density = []
    
    for density in densities:
        buffer_temp = RiparianBuffer(20.0, 3.0, density)
        removal_by_density.append(buffer_temp.pollutant_removal(5.0, 'N')['removal_rate'])
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 宽度对削减率的影响
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(widths, removal_N, 'b-', linewidth=2, marker='o', markersize=4, label='TN')
    ax1.plot(widths, removal_P, 'r-', linewidth=2, marker='s', markersize=4, label='TP')
    ax1.plot(widths, removal_COD, 'g-', linewidth=2, marker='^', markersize=4, label='COD')
    ax1.plot(widths, removal_TSS, 'orange', linewidth=2, marker='d', markersize=4, label='TSS')
    ax1.axhline(70, color='k', linestyle='--', alpha=0.5, label='目标70%')
    ax1.axvline(20, color='purple', linestyle='--', alpha=0.5, label='设计宽度')
    ax1.set_xlabel('缓冲带宽度 (m)', fontsize=10)
    ax1.set_ylabel('削减率 (%)', fontsize=10)
    ax1.set_title('缓冲带宽度对污染物削减的影响', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([5, 50])
    ax1.set_ylim([0, 100])
    
    # 2. 植被覆盖度影响
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(densities * 100, removal_by_density, 'g-', linewidth=3, marker='o', markersize=8)
    ax2.axvline(70, color='r', linestyle='--', linewidth=2, alpha=0.5, label='当前覆盖度')
    ax2.set_xlabel('植被覆盖度 (%)', fontsize=10)
    ax2.set_ylabel('TN削减率 (%)', fontsize=10)
    ax2.set_title('植被覆盖度对削减率的影响', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([10, 90])
    ax2.set_ylim([0, 100])
    
    # 3. 污染物削减效果对比
    ax3 = plt.subplot(2, 3, 3)
    x_pos = np.arange(len(pollutants))
    inlet_values = [r['inlet_concentration'] for r in results]
    outlet_values = [r['outlet_concentration'] for r in results]
    
    width = 0.35
    ax3.bar(x_pos - width/2, inlet_values, width, label='入流浓度', 
           color='lightcoral', edgecolor='black', linewidth=1.5)
    ax3.bar(x_pos + width/2, outlet_values, width, label='出流浓度',
           color='lightgreen', edgecolor='black', linewidth=1.5)
    
    ax3.set_xlabel('污染物', fontsize=10)
    ax3.set_ylabel('浓度 (mg/L)', fontsize=10)
    ax3.set_title('污染物削减效果对比', fontsize=12, fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(pollutants)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 在柱子上标注削减率
    for i, result in enumerate(results):
        ax3.text(i, max(inlet_values[i], outlet_values[i]) * 1.1,
                f'-{result["removal_rate"]:.0f}%',
                ha='center', va='bottom', fontsize=9, fontweight='bold', color='red')
    
    # 4. 缓冲带剖面示意图
    ax4 = plt.subplot(2, 3, 4)
    x = np.linspace(0, buffer.W, 100)
    y = -x * buffer.S  # 坡度
    
    ax4.fill_between(x, y - 0.5, y, color='brown', alpha=0.3, label='土壤层')
    ax4.fill_between(x, y, y + 0.3, color='lightgreen', alpha=0.5, label='植被层')
    
    # 径流路径
    flow_y = y + 0.05
    ax4.plot(x, flow_y, 'b-', linewidth=2, label='地表径流')
    ax4.arrow(buffer.W * 0.8, flow_y[-1], buffer.W * 0.1, 0,
             head_width=0.1, head_length=2, fc='blue', ec='blue')
    
    # 标注
    ax4.text(buffer.W / 2, y[50] + 0.4, '植被过滤带', ha='center',
            fontsize=11, fontweight='bold', bbox=dict(boxstyle='round', facecolor='wheat'))
    ax4.text(0, y[0] + 0.5, '农田/湖岸', ha='left', fontsize=10)
    ax4.text(buffer.W, y[-1] + 0.5, '湖泊', ha='right', fontsize=10)
    
    ax4.set_xlabel('距离 (m)', fontsize=10)
    ax4.set_ylabel('高程 (m)', fontsize=10)
    ax4.set_title('缓冲带剖面示意图', fontsize=12, fontweight='bold')
    ax4.legend(loc='upper right')
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim([0, buffer.W])
    
    # 5. 不同坡度下的效果
    ax5 = plt.subplot(2, 3, 5)
    slopes = [1, 2, 3, 5, 8, 10]
    removal_by_slope = []
    velocity_by_slope = []
    
    for slope in slopes:
        buffer_temp = RiparianBuffer(20.0, slope, 0.7)
        removal_by_slope.append(buffer_temp.pollutant_removal(5.0, 'N')['removal_rate'])
        velocity_by_slope.append(buffer_temp.runoff_velocity(50.0))
    
    ax5.plot(slopes, removal_by_slope, 'b-o', linewidth=2, markersize=8, label='削减率')
    ax5.set_xlabel('坡度 (%)', fontsize=10)
    ax5.set_ylabel('TN削减率 (%)', fontsize=10, color='b')
    ax5.tick_params(axis='y', labelcolor='b')
    ax5.set_title('坡度对削减效果的影响', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    ax5_twin = ax5.twinx()
    ax5_twin.plot(slopes, velocity_by_slope, 'r-s', linewidth=2, markersize=8, label='流速')
    ax5_twin.set_ylabel('径流流速 (m/s)', fontsize=10, color='r')
    ax5_twin.tick_params(axis='y', labelcolor='r')
    
    # 6. 经济效益分析
    ax6 = plt.subplot(2, 3, 6)
    
    # 简化经济分析
    annual_pollutant_load = 1000  # kg/year (假设)
    removal_rate_avg = np.mean([r['removal_rate'] for r in results])
    load_reduced = annual_pollutant_load * removal_rate_avg / 100
    
    # 效益（避免的水质处理成本）
    treatment_cost_per_kg = 20  # 元/kg
    annual_benefit = load_reduced * treatment_cost_per_kg
    
    # 成本
    construction_cost = buffer.W * 100 * 50  # 100m岸线，50元/m²
    maintenance_cost_annual = construction_cost * 0.05  # 年维护5%
    
    categories = ['建设成本', '年维护成本', '年效益']
    values = [construction_cost, maintenance_cost_annual, annual_benefit]
    colors_econ = ['red', 'orange', 'green']
    
    bars = ax6.bar(categories, np.array(values) / 1000, color=colors_econ,
                   edgecolor='black', linewidth=1.5)
    ax6.set_ylabel('金额 (千元)', fontsize=10)
    ax6.set_title('经济效益分析', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='y')
    
    for bar, value in zip(bars, values):
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{value/1000:.1f}', ha='center', va='bottom',
                fontsize=10, fontweight='bold')
    
    payback_period = construction_cost / (annual_benefit - maintenance_cost_annual)
    ax6.text(0.5, 0.95, f'投资回收期: {payback_period:.1f}年',
            transform=ax6.transAxes, ha='center',
            fontsize=10, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'riparian_buffer_analysis.png', dpi=300)
    print(f"\n图表已保存: riparian_buffer_analysis.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
