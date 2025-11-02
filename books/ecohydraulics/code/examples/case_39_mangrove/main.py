#!/usr/bin/env python3
"""案例39：红树林湿地水动力"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.estuary_coastal import MangroveHydrodynamics, simulate_storm_surge_protection

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例39：红树林湿地水动力与防护功能")
    print("=" * 70)
    
    # 红树林参数
    mangrove = MangroveHydrodynamics(
        forest_width=100.0,  # 100m
        tree_density=1.0,    # 1株/m²
        tree_diameter=0.15   # 15cm
    )
    
    print(f"\n红树林基本参数:")
    print(f"  林带宽度: {mangrove.W:.1f} m")
    print(f"  树木密度: {mangrove.n:.1f} 株/m²")
    print(f"  树干直径: {mangrove.d:.2f} m")
    
    # 1. 波浪消减
    wave_result = mangrove.wave_attenuation(1.5, 8.0, 2.0)
    print(f"\n波浪消减效果:")
    print(f"  入射波高: {wave_result['incident_height']:.2f} m")
    print(f"  透射波高: {wave_result['transmitted_height']:.2f} m")
    print(f"  消减率: {wave_result['attenuation_rate']:.1f}%")
    
    # 2. 潮流消减
    current_result = mangrove.current_reduction(1.0, 2.0)
    print(f"\n潮流消减效果:")
    print(f"  入流流速: {current_result['inlet_velocity']:.2f} m/s")
    print(f"  出流流速: {current_result['outlet_velocity']:.2f} m/s")
    print(f"  消减率: {current_result['reduction_rate']:.1f}%")
    
    # 3. 泥沙捕获
    ssc_efficiency = mangrove.sediment_trapping_efficiency(100, 0.5)
    print(f"\n泥沙捕获效率: {ssc_efficiency:.1f}%")
    
    # 4. 防护价值
    protection = mangrove.coastal_protection_value(3.0, 50.0)
    print(f"\n海岸防护价值评估:")
    print(f"  波浪消减: {protection['wave_attenuation']:.1f}%")
    print(f"  防护价值: {protection['protection_value']:.1f} 万元")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 流速沿程变化
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(current_result['distances'], current_result['velocity_profile'],
            'b-', linewidth=2)
    ax1.set_xlabel('距林带起点距离 (m)', fontsize=10)
    ax1.set_ylabel('流速 (m/s)', fontsize=10)
    ax1.set_title('流速沿程衰减', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 2. 不同波高的消减效果
    ax2 = plt.subplot(2, 3, 2)
    wave_heights = np.linspace(0.5, 3.0, 20)
    attenuation_rates = []
    for H in wave_heights:
        result = mangrove.wave_attenuation(H, 8.0, 2.0)
        attenuation_rates.append(result['attenuation_rate'])
    
    ax2.plot(wave_heights, attenuation_rates, 'g-o', linewidth=2, markersize=6)
    ax2.set_xlabel('入射波高 (m)', fontsize=10)
    ax2.set_ylabel('消减率 (%)', fontsize=10)
    ax2.set_title('波浪消减率vs波高', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. 林带宽度影响
    ax3 = plt.subplot(2, 3, 3)
    widths = np.linspace(20, 200, 20)
    wave_atten = []
    current_atten = []
    
    for w in widths:
        mg_temp = MangroveHydrodynamics(w, 1.0, 0.15)
        wave_atten.append(mg_temp.wave_attenuation(1.5, 8.0, 2.0)['attenuation_rate'])
        current_atten.append(mg_temp.current_reduction(1.0, 2.0)['reduction_rate'])
    
    ax3.plot(widths, wave_atten, 'b-', linewidth=2, label='波浪消减')
    ax3.plot(widths, current_atten, 'r-', linewidth=2, label='流速消减')
    ax3.set_xlabel('林带宽度 (m)', fontsize=10)
    ax3.set_ylabel('消减率 (%)', fontsize=10)
    ax3.set_title('林带宽度对防护效果的影响', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 红树林剖面示意
    ax4 = plt.subplot(2, 3, 4)
    x = np.linspace(0, 100, 100)
    water_level = np.ones(100) * 2.0
    ground = np.zeros(100)
    
    ax4.fill_between(x, ground, water_level, color='lightblue', alpha=0.5, label='水体')
    ax4.fill_between(x, ground - 1, ground, color='brown', alpha=0.3, label='底泥')
    
    # 绘制树木
    for i in range(0, 100, 10):
        ax4.plot([i, i], [0, 3], 'g-', linewidth=3)
        ax4.plot([i-2, i, i+2], [3, 4, 3], 'g-', linewidth=2)
    
    ax4.set_xlabel('距离 (m)', fontsize=10)
    ax4.set_ylabel('高程 (m)', fontsize=10)
    ax4.set_title('红树林断面示意图', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim([-1.5, 5])
    
    # 5. 综合防护效益
    ax5 = plt.subplot(2, 3, 5)
    benefits = ['波浪消减', '流速消减', '泥沙捕获', '生物多样性', '碳汇功能']
    scores = [wave_result['attenuation_rate'], current_result['reduction_rate'],
             ssc_efficiency, 85, 90]
    colors = ['blue', 'cyan', 'green', 'yellow', 'lime']
    
    bars = ax5.barh(benefits, scores, color=colors, edgecolor='black', linewidth=1.5)
    ax5.set_xlabel('评分/效率 (%)', fontsize=10)
    ax5.set_title('红树林综合防护效益', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='x')
    ax5.set_xlim([0, 100])
    
    for bar, score in zip(bars, scores):
        ax5.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                f'{score:.0f}', va='center', fontsize=9, fontweight='bold')
    
    # 6. 风暴潮防护模拟
    ax6 = plt.subplot(2, 3, 6)
    surge_heights = np.linspace(1, 4, 10)
    protection_scores = []
    
    for surge in surge_heights:
        result = simulate_storm_surge_protection(100, surge, 1.0)
        protection_scores.append(result['protection_score'])
    
    ax6.plot(surge_heights, protection_scores, 'r-o', linewidth=2, markersize=8)
    ax6.axhline(50, color='orange', linestyle='--', linewidth=2, label='中等防护')
    ax6.fill_between(surge_heights, 0, 50, color='red', alpha=0.2)
    ax6.fill_between(surge_heights, 50, 100, color='green', alpha=0.2)
    ax6.set_xlabel('风暴潮高度 (m)', fontsize=10)
    ax6.set_ylabel('防护评分', fontsize=10)
    ax6.set_title('风暴潮防护能力', fontsize=12, fontweight='bold')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    ax6.set_ylim([0, 100])
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'mangrove_hydrodynamics.png', dpi=300)
    print(f"\n图表已保存: mangrove_hydrodynamics.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
