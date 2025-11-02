#!/usr/bin/env python3
"""
案例15：河流侧向连通性恢复（滩涂湿地）

分析洪泛区湿地与河流的水力连通性，评估生态功能
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.floodplain_wetland import (
    FloodplainHydraulics,
    WetlandConnectivity,
    JuvenileFishGrowth,
    design_ecological_gate_operation
)

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例15：河流侧向连通性恢复（滩涂湿地）")
    print("=" * 70)
    
    # === 1. 漫滩水力学分析 ===
    print("\n【漫滩水力学分析】")
    
    floodplain = FloodplainHydraulics(
        channel_width=50.0,
        channel_depth=3.0,
        floodplain_width=200.0,
        floodplain_elevation=2.5,
        slope=0.0005
    )
    
    # 不同流量下的淹没情况
    flows = np.array([50, 100, 200, 400, 600, 800])
    inundations = []
    
    print(f"\n河道宽度: {floodplain.Bc} m")
    print(f"洪泛区宽度: {floodplain.Bf} m")
    print(f"漫滩高程: {floodplain.Hf} m")
    
    Q_threshold = floodplain.overbank_threshold_discharge()
    print(f"\n漫滩临界流量: {Q_threshold:.1f} m³/s")
    
    print(f"\n流量(m³/s) | 水深(m) | 淹没宽度(m) | 是否漫滩 | 漫滩深度(m)")
    print("-" * 70)
    
    for Q in flows:
        result = floodplain.inundation_area(Q)
        inundations.append(result)
        
        print(f"{Q:10.0f} | {result['water_depth']:7.2f} | "
              f"{result['inundated_width']:11.1f} | "
              f"{'是' if result['is_overbank'] else '否':8s} | "
              f"{result['overbank_depth']:11.2f}")
    
    # === 2. 湿地连通性分析 ===
    print("\n" + "=" * 70)
    print("【湿地连通性分析】")
    
    wetland = WetlandConnectivity(
        wetland_elevation=2.0,
        wetland_area=50.0
    )
    
    # 模拟全年水深变化
    days = 365
    np.random.seed(42)
    # 基础水深 + 季节变化 + 随机波动
    water_depths = 2.0 + 0.8 * np.sin(2 * np.pi * np.arange(days) / 365) + \
                   np.random.normal(0, 0.3, days)
    water_depths = np.maximum(water_depths, 1.0)  # 最小水深
    
    freq_result = wetland.inundation_frequency(water_depths)
    CI = wetland.connectivity_index(freq_result['inundation_frequency'])
    
    print(f"\n湿地高程: {wetland.elevation} m")
    print(f"湿地面积: {wetland.area} ha")
    print(f"\n淹没天数: {freq_result['inundation_days']} 天")
    print(f"淹没频率: {freq_result['inundation_frequency']:.1%}")
    print(f"平均淹没深度: {freq_result['avg_inundation_depth']:.2f} m")
    print(f"最大淹没深度: {freq_result['max_inundation_depth']:.2f} m")
    print(f"连通性指数: {CI:.3f}")
    
    # === 3. 幼鱼生长分析 ===
    print("\n" + "=" * 70)
    print("【幼鱼生长分析】")
    
    juvenile = JuvenileFishGrowth("四大家鱼", initial_length=1.0)
    
    # 不同条件下的生长
    conditions = [
        {'temp': 20, 'food': 0.6, 'name': '一般条件'},
        {'temp': 25, 'food': 0.8, 'name': '良好条件'},
        {'temp': 28, 'food': 1.0, 'name': '最优条件'}
    ]
    
    growth_curves = []
    
    for cond in conditions:
        t, L = juvenile.simulate_growth(60, cond['temp'], cond['food'])
        growth_curves.append((t, L, cond['name']))
        print(f"\n{cond['name']}:")
        print(f"  温度: {cond['temp']}°C")
        print(f"  饵料丰度: {cond['food']:.1%}")
        print(f"  60天后体长: {L[-1]:.1f} cm")
        print(f"  日均生长: {(L[-1]-L[0])/60:.3f} cm/day")
    
    # 湿地适宜性评价
    print("\n【湿地育肥场适宜性】")
    suitability = juvenile.wetland_suitability(1.5, 25, 0.5)
    
    print(f"水深: 1.5 m")
    print(f"温度: 25°C")
    print(f"植被覆盖: 50%")
    print(f"\n水深适宜性: {suitability['depth_suitability']:.2f}")
    print(f"温度适宜性: {suitability['temperature_suitability']:.2f}")
    print(f"植被适宜性: {suitability['vegetation_suitability']:.2f}")
    print(f"综合适宜性: {suitability['overall_suitability']:.2f}")
    print(f"适宜等级: {suitability['grade']}")
    
    # === 4. 生态调度方案 ===
    print("\n" + "=" * 70)
    print("【生态水闸调度方案】")
    
    # 模拟月均流量
    monthly_flows = np.array([80, 90, 150, 300, 500, 600,
                             400, 250, 180, 120, 100, 85])
    
    gate_plan = design_ecological_gate_operation(
        monthly_flows,
        wetland_elevation=2.0,
        target_inundation_freq=0.3
    )
    
    print(f"\n开闸流量阈值: {gate_plan['flow_threshold']:.1f} m³/s")
    print(f"目标淹没频率: {gate_plan['expected_frequency']:.1%}")
    
    print(f"\n月份 | 流量(m³/s) | 调度决策 | 效果")
    print("-" * 70)
    for op in gate_plan['operations']:
        print(f"{op['month']:4d} | {op['flow']:10.0f} | {op['operation']:8s} | "
              f"{op['effect'][:30]}")
    
    # === 可视化 ===
    fig = plt.figure(figsize=(16, 10))
    
    # 1. 流量-淹没关系
    ax1 = plt.subplot(2, 3, 1)
    widths = [r['inundated_width'] for r in inundations]
    colors = ['blue' if r['is_overbank'] else 'lightblue' for r in inundations]
    ax1.bar(flows, widths, color=colors, edgecolor='black', alpha=0.7)
    ax1.axhline(floodplain.Bc, color='r', linestyle='--', label=f'河道宽度 {floodplain.Bc}m')
    ax1.axvline(Q_threshold, color='g', linestyle='--', label=f'漫滩临界 {Q_threshold:.0f}m³/s')
    ax1.set_xlabel('流量 (m³/s)', fontsize=10)
    ax1.set_ylabel('淹没宽度 (m)', fontsize=10)
    ax1.set_title('流量-淹没宽度关系', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.legend(fontsize=8)
    
    # 2. 全年水深变化
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(np.arange(days), water_depths, 'b-', linewidth=1, alpha=0.7)
    ax2.axhline(wetland.elevation, color='r', linestyle='--', 
                label=f'湿地高程 {wetland.elevation}m')
    ax2.fill_between(np.arange(days), wetland.elevation, water_depths,
                     where=water_depths > wetland.elevation,
                     color='cyan', alpha=0.3, label='淹没期')
    ax2.set_xlabel('时间 (天)', fontsize=10)
    ax2.set_ylabel('水深 (m)', fontsize=10)
    ax2.set_title('全年水深变化与湿地淹没', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8)
    
    # 3. 幼鱼生长曲线
    ax3 = plt.subplot(2, 3, 3)
    for t, L, name in growth_curves:
        ax3.plot(t, L, linewidth=2, label=name)
    ax3.set_xlabel('时间 (天)', fontsize=10)
    ax3.set_ylabel('体长 (cm)', fontsize=10)
    ax3.set_title('不同条件下幼鱼生长曲线', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=8)
    
    # 4. 适宜性雷达图
    ax4 = plt.subplot(2, 3, 4, projection='polar')
    categories = ['水深', '温度', '植被']
    values = [suitability['depth_suitability'],
             suitability['temperature_suitability'],
             suitability['vegetation_suitability']]
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
    values = np.concatenate((values, [values[0]]))
    angles = np.concatenate((angles, [angles[0]]))
    
    ax4.plot(angles, values, 'o-', linewidth=2, label='实际条件')
    ax4.fill(angles, values, alpha=0.25)
    ax4.set_xticks(angles[:-1])
    ax4.set_xticklabels(categories, fontsize=10)
    ax4.set_ylim(0, 1)
    ax4.set_title('湿地育肥场适宜性', fontsize=12, fontweight='bold', pad=20)
    ax4.grid(True)
    
    # 5. 月度调度方案
    ax5 = plt.subplot(2, 3, 5)
    months = np.arange(1, 13)
    colors5 = ['green' if op['operation'] == '开闸' else 'gray' 
              for op in gate_plan['operations']]
    bars5 = ax5.bar(months, monthly_flows, color=colors5, alpha=0.7, edgecolor='black')
    ax5.axhline(gate_plan['flow_threshold'], color='r', linestyle='--',
               label=f"开闸阈值 {gate_plan['flow_threshold']:.0f}m³/s")
    ax5.set_xlabel('月份', fontsize=10)
    ax5.set_ylabel('流量 (m³/s)', fontsize=10)
    ax5.set_title('生态水闸月度调度方案', fontsize=12, fontweight='bold')
    ax5.set_xticks(months)
    ax5.grid(True, alpha=0.3, axis='y')
    ax5.legend(fontsize=8)
    
    # 6. 综合评价
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    summary_text = f"""
    【侧向连通性恢复效果】
    
    ═══ 水文连通性 ═══
    淹没频率: {freq_result['inundation_frequency']:.1%}
    连通性指数: {CI:.3f}
    评价: {'优良' if CI > 0.8 else '良好' if CI > 0.6 else '一般'}
    
    ═══ 生态功能 ═══
    幼鱼育肥场适宜性: {suitability['grade']}
    生长条件: {suitability['overall_suitability']:.1%}
    饵料充足度: 良好
    
    ═══ 调度方案 ═══
    开闸月份: 4-9月（丰水期）
    开闸天数: 约 {int(12*gate_plan['expected_frequency'])} 个月
    预期效果: 恢复自然洪泛节律
    
    ═══ 生态效益 ═══
    • 恢复河流-洪泛区水文联系
    • 提供鱼类繁殖和幼鱼育肥空间
    • 增加湿地生物多样性
    • 提升生态系统服务功能
    """
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes,
             fontsize=9, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8),
             family='monospace')
    
    plt.tight_layout()
    output_file = Path(__file__).parent / 'floodplain_wetland_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n图表已保存: {output_file}")
    
    print("\n" + "=" * 70)
    print("分析完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()
