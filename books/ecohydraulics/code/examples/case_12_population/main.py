#!/usr/bin/env python3
"""
案例12：洄游通道水力连通性分析

评估梯级开发对鱼类洄游的影响，计算连通性指数，模拟种群恢复
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.fish_population import (
    RiverConnectivityIndex, 
    FishPopulationModel, 
    create_connectivity_scenario
)

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例12：洄游通道水力连通性分析")
    print("=" * 70)
    
    # === 1. 连通性分析 ===
    print("\n【河流连通性分析】")
    
    # 场景1：无障碍
    scenario1 = RiverConnectivityIndex([100, 100, 100], [])
    dci1 = scenario1.calculate_dci()
    
    # 场景2：一座坝
    scenario2 = RiverConnectivityIndex(
        [100, 100, 100],
        [{'position': 1, 'passability': 0.3}]
    )
    dci2 = scenario2.calculate_dci()
    
    # 场景3：两座坝
    scenario3 = RiverConnectivityIndex(
        [100, 100, 100],
        [
            {'position': 0, 'passability': 0.3},
            {'position': 1, 'passability': 0.3}
        ]
    )
    dci3 = scenario3.calculate_dci()
    
    # 场景4：五座梯级坝
    scenario4 = create_connectivity_scenario(5)
    dci4 = scenario4.calculate_dci()
    
    print(f"无障碍河流 DCIp: {dci1:.3f} (100%)")
    print(f"一座坝 DCIp: {dci2:.3f} ({dci2*100:.1f}%)")
    print(f"两座坝 DCIp: {dci3:.3f} ({dci3*100:.1f}%)")
    print(f"五座梯级坝 DCIp: {dci4:.3f} ({dci4*100:.1f}%)")
    
    # === 2. 种群动力学分析 ===
    print("\n【种群恢复模拟】")
    
    # 原始种群
    pop_original = FishPopulationModel(
        initial_population=10000,
        carrying_capacity=50000,
        growth_rate=0.5
    )
    
    # 受损种群
    pop_damaged = FishPopulationModel(
        initial_population=2000,
        carrying_capacity=50000,
        growth_rate=0.3
    )
    
    # 恢复后种群
    pop_restored = FishPopulationModel(
        initial_population=2000,
        carrying_capacity=50000,
        growth_rate=0.5
    )
    
    # 模拟
    t_orig, N_orig = pop_original.simulate_population(20)
    t_damaged, N_damaged = pop_damaged.simulate_population(20)
    t_restored, N_restored = pop_restored.simulate_population(20)
    
    # 恢复时间
    recovery_time = pop_restored.recovery_time(0.9)
    
    print(f"\n种群容纳量: 50000")
    print(f"初始种群: 10000 (健康)")
    print(f"受损种群: 2000 (80%下降)")
    print(f"\n恢复时间（90%容纳量）:")
    print(f"• 低增长率(r=0.3): {pop_damaged.recovery_time(0.9):.1f} 年")
    print(f"• 正常增长率(r=0.5): {recovery_time:.1f} 年")
    
    # === 3. 恢复方案对比 ===
    print("\n【恢复方案对比】")
    
    # 方案A：移除1座坝
    scenario_A = RiverConnectivityIndex(
        [100, 100, 100],
        [{'position': 0, 'passability': 1.0}]  # 移除下游坝
    )
    dci_A = scenario_A.calculate_dci()
    
    # 方案B：改造2座坝（增加鱼道）
    scenario_B = RiverConnectivityIndex(
        [100, 100, 100],
        [
            {'position': 0, 'passability': 0.7},
            {'position': 1, 'passability': 0.7}
        ]
    )
    dci_B = scenario_B.calculate_dci()
    
    print(f"\n现状 DCIp: {dci3:.3f}")
    print(f"方案A（移除1坝）DCIp: {dci_A:.3f} (提升 {(dci_A-dci3)*100:.1f}%)")
    print(f"方案B（改造2坝）DCIp: {dci_B:.3f} (提升 {(dci_B-dci3)*100:.1f}%)")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 连通性对比
    ax1 = plt.subplot(2, 3, 1)
    scenarios = ['无障碍', '1座坝', '2座坝', '5座梯级坝']
    dcis = [dci1, dci2, dci3, dci4]
    colors = ['green', 'yellow', 'orange', 'red']
    bars = ax1.bar(scenarios, dcis, color=colors, alpha=0.7)
    ax1.set_ylabel('DCIp', fontsize=10)
    ax1.set_title('河流连通性指数对比', fontsize=12, fontweight='bold')
    ax1.set_ylim([0, 1.1])
    ax1.grid(True, alpha=0.3, axis='y')
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    # 2. 种群恢复曲线
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(t_orig, N_orig, 'g-', linewidth=2, label='健康种群')
    ax2.plot(t_damaged, N_damaged, 'r-', linewidth=2, label='受损种群(低增长)')
    ax2.plot(t_restored, N_restored, 'b--', linewidth=2, label='恢复后种群')
    ax2.axhline(50000, color='k', linestyle='--', alpha=0.5, label='容纳量')
    ax2.axhline(45000, color='purple', linestyle=':', alpha=0.5, label='90%目标')
    ax2.set_xlabel('时间 (年)', fontsize=10)
    ax2.set_ylabel('种群数量', fontsize=10)
    ax2.set_title('种群动态模拟', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. 恢复方案效果
    ax3 = plt.subplot(2, 3, 3)
    restoration_scenarios = ['现状', '方案A\n(移除1坝)', '方案B\n(改造2坝)']
    restoration_dcis = [dci3, dci_A, dci_B]
    colors3 = ['red', 'orange', 'yellow']
    bars3 = ax3.bar(restoration_scenarios, restoration_dcis, color=colors3, alpha=0.7)
    ax3.set_ylabel('DCIp', fontsize=10)
    ax3.set_title('恢复方案效果对比', fontsize=12, fontweight='bold')
    ax3.set_ylim([0, 1.0])
    ax3.grid(True, alpha=0.3, axis='y')
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    # 4. 通过率影响
    ax4 = plt.subplot(2, 3, 4)
    passabilities = np.linspace(0, 1, 21)
    dcis_pass = []
    for p in passabilities:
        scenario = RiverConnectivityIndex(
            [100, 100, 100],
            [{'position': 1, 'passability': p}]
        )
        dcis_pass.append(scenario.calculate_dci())
    ax4.plot(passabilities * 100, dcis_pass, 'b-', linewidth=2)
    ax4.axhline(0.9, color='g', linestyle='--', alpha=0.5, label='良好阈值')
    ax4.set_xlabel('鱼道通过率 (%)', fontsize=10)
    ax4.set_ylabel('DCIp', fontsize=10)
    ax4.set_title('通过率-连通性关系', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # 5. 恢复时间分析
    ax5 = plt.subplot(2, 3, 5)
    growth_rates = np.linspace(0.1, 0.8, 20)
    recovery_times = []
    for r in growth_rates:
        pop = FishPopulationModel(2000, 50000, r)
        recovery_times.append(pop.recovery_time(0.9))
    ax5.plot(growth_rates, recovery_times, 'purple', linewidth=2)
    ax5.axhline(10, color='r', linestyle='--', alpha=0.5, label='10年目标')
    ax5.set_xlabel('种群增长率', fontsize=10)
    ax5.set_ylabel('恢复时间 (年)', fontsize=10)
    ax5.set_title('增长率-恢复时间关系', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    ax5.legend()
    
    # 6. 综合评价
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    summary_text = f"""
    【连通性恢复建议】
    
    现状:
    • DCIp = {dci3:.3f} (严重阻隔)
    • 种群下降 80%
    
    优先方案:
    • 移除下游第1座坝
    • DCIp提升至 {dci_A:.3f}
    • 预计恢复时间: {recovery_time:.1f}年
    
    次优方案:
    • 改造所有坝为鱼道
    • 通过率提升至70%
    • DCIp达到 {dci_B:.3f}
    
    长期目标:
    • DCIp > 0.8 (优良)
    • 种群恢复至90%容纳量
    """
    ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes,
             fontsize=9, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5),
             family='monospace')
    
    plt.tight_layout()
    output_file = Path(__file__).parent / 'connectivity_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n图表已保存: {output_file}")
    
    print("\n" + "=" * 70)
    print("分析完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()
