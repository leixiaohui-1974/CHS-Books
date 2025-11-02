#!/usr/bin/env python3
"""
案例14：生态护岸水力设计

设计生态护岸，既满足防洪要求，又提供生境功能
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.ecological_revetment import (
    EcologicalRevetment,
    VegetatedRevetment,
    RevetmentStability,
    design_ecological_revetment
)

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例14：生态护岸水力设计")
    print("=" * 70)
    
    # 设计条件
    channel_width = 30.0  # m
    water_depth = 2.0  # m
    velocity = 1.2  # m/s
    slope_angle = 35.0  # 度
    
    print(f"\n【设计条件】")
    print(f"河道宽度: {channel_width} m")
    print(f"设计水深: {water_depth} m")
    print(f"设计流速: {velocity} m/s")
    print(f"边坡角度: {slope_angle}°")
    
    # 对比不同护岸类型
    revetment_types = ['植被护坡', '石笼', '生态袋', '格宾', '混凝土']
    results = {}
    
    print(f"\n{'='*70}")
    print("【不同护岸类型对比】")
    print(f"{'='*70}")
    
    for rev_type in revetment_types:
        result = design_ecological_revetment(
            channel_width, water_depth, velocity, slope_angle, rev_type
        )
        results[rev_type] = result
        
        print(f"\n--- {rev_type} ---")
        print(f"粗糙系数: {result['roughness']:.4f}")
        print(f"流速削减: {result['velocity_reduction']:.2f}")
        print(f"庇护所比例: {result['shelter_ratio']:.1%}")
        print(f"庇护所面积: {result['shelter_area_per_100m']:.1f} m²/100m")
        
        stab = result['stability']
        print(f"安全系数: {stab['safety_factor']:.2f}")
        print(f"稳定性评价: {stab['stability']} ({stab['erosion_risk']}风险)")
        
        if 'root_reinforcement' in result:
            print(f"根系加固: {result['root_reinforcement']:.1f} kPa")
    
    # 详细分析植被护坡
    print(f"\n{'='*70}")
    print("【植被护坡详细分析】")
    print(f"{'='*70}")
    
    veg_rev = VegetatedRevetment(
        height=0.5,
        coverage=0.7,
        stem_diameter=0.005,
        stem_density=1000.0
    )
    
    # 不同水深下的有效糙率
    depths = np.linspace(0.3, 3.0, 10)
    roughness_values = [veg_rev.effective_roughness(h, velocity) for h in depths]
    
    print(f"\n水深变化对糙率的影响：")
    for h, n in zip(depths[::3], roughness_values[::3]):
        submergence = veg_rev.height / h
        status = "非淹没" if submergence >= 1 else f"淹没({submergence:.1%})"
        print(f"水深 {h:.1f}m: n={n:.4f} ({status})")
    
    # 可视化
    fig = plt.figure(figsize=(16, 10))
    
    # 1. 粗糙系数对比
    ax1 = plt.subplot(2, 3, 1)
    types = list(results.keys())
    roughness = [results[t]['roughness'] for t in types]
    colors = ['green', 'gray', 'brown', 'darkgray', 'lightgray']
    bars = ax1.bar(range(len(types)), roughness, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_xticks(range(len(types)))
    ax1.set_xticklabels(types, rotation=15, ha='right', fontsize=9)
    ax1.set_ylabel('Manning粗糙系数', fontsize=10)
    ax1.set_title('不同护岸粗糙系数对比', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{roughness[i]:.3f}', ha='center', va='bottom', fontsize=8)
    
    # 2. 流速削减效果
    ax2 = plt.subplot(2, 3, 2)
    reduction = [results[t]['velocity_reduction'] for t in types]
    bars2 = ax2.bar(range(len(types)), reduction, color=colors, alpha=0.7, edgecolor='black')
    ax2.set_xticks(range(len(types)))
    ax2.set_xticklabels(types, rotation=15, ha='right', fontsize=9)
    ax2.set_ylabel('流速削减系数', fontsize=10)
    ax2.set_title('护岸流速削减效果', fontsize=12, fontweight='bold')
    ax2.set_ylim([0, 1])
    ax2.grid(True, alpha=0.3, axis='y')
    for i, bar in enumerate(bars2):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{reduction[i]:.2f}', ha='center', va='bottom', fontsize=8)
    
    # 3. 庇护所面积
    ax3 = plt.subplot(2, 3, 3)
    shelter = [results[t]['shelter_area_per_100m'] for t in types]
    bars3 = ax3.bar(range(len(types)), shelter, color=colors, alpha=0.7, edgecolor='black')
    ax3.set_xticks(range(len(types)))
    ax3.set_xticklabels(types, rotation=15, ha='right', fontsize=9)
    ax3.set_ylabel('庇护所面积 (m²/100m)', fontsize=10)
    ax3.set_title('护岸庇护所面积', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    for i, bar in enumerate(bars3):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{shelter[i]:.0f}', ha='center', va='bottom', fontsize=8)
    
    # 4. 安全系数
    ax4 = plt.subplot(2, 3, 4)
    safety = [results[t]['stability']['safety_factor'] for t in types]
    bar_colors = ['green' if s > 2 else 'orange' if s > 1.5 else 'red' for s in safety]
    bars4 = ax4.bar(range(len(types)), safety, color=bar_colors, alpha=0.7, edgecolor='black')
    ax4.axhline(2.0, color='g', linestyle='--', label='安全 (SF>2.0)')
    ax4.axhline(1.5, color='orange', linestyle='--', label='基本安全 (SF>1.5)')
    ax4.set_xticks(range(len(types)))
    ax4.set_xticklabels(types, rotation=15, ha='right', fontsize=9)
    ax4.set_ylabel('安全系数', fontsize=10)
    ax4.set_title('护岸稳定性安全系数', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.legend(fontsize=8)
    for i, bar in enumerate(bars4):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{safety[i]:.2f}', ha='center', va='bottom', fontsize=8)
    
    # 5. 植被糙率随水深变化
    ax5 = plt.subplot(2, 3, 5)
    ax5.plot(depths, roughness_values, 'g-', linewidth=2, marker='o')
    ax5.axhline(veg_rev.roughness_coefficient(), color='r', linestyle='--', 
                alpha=0.5, label=f'基准糙率 {veg_rev.roughness_coefficient():.3f}')
    ax5.axvline(veg_rev.height, color='b', linestyle=':', 
                label=f'植被高度 {veg_rev.height}m')
    ax5.set_xlabel('水深 (m)', fontsize=10)
    ax5.set_ylabel('有效糙率 n', fontsize=10)
    ax5.set_title('植被护岸糙率-水深关系', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    ax5.legend(fontsize=8)
    
    # 6. 综合评价
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    # 推荐方案
    best_type = max(results.keys(), 
                   key=lambda t: (results[t]['shelter_ratio'] * 0.4 + 
                                 results[t]['velocity_reduction'] * 0.3 +
                                 min(results[t]['stability']['safety_factor']/2, 1) * 0.3))
    
    summary_text = f"""
    【生态护岸设计推荐】
    
    ═══ 最优方案 ═══
    推荐类型: {best_type}
    
    ═══ 性能指标 ═══
    • 流速削减: {results[best_type]['velocity_reduction']:.1%}
    • 庇护所面积: {results[best_type]['shelter_area_per_100m']:.0f} m²/100m
    • 安全系数: {results[best_type]['stability']['safety_factor']:.2f}
    • 稳定性: {results[best_type]['stability']['stability']}
    
    ═══ 生态效益 ═══
    • 降低近岸流速，保护鱼卵幼鱼
    • 提供庇护所和栖息空间
    • 增加生境异质性
    • 促进水陆生态交换
    
    ═══ 工程特点 ═══
    • 满足防洪安全要求
    • 施工简便，成本适中
    • 兼顾生态与景观功能
    • 可持续性强
    
    ═══ 维护建议 ═══
    • 定期检查护岸完整性
    • 补种植被，保持覆盖度
    • 清理淤积，维持通水
    """
    
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes,
             fontsize=9, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8),
             family='monospace')
    
    plt.tight_layout()
    output_file = Path(__file__).parent / 'ecological_revetment_design.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n图表已保存: {output_file}")
    
    print("\n" + "=" * 70)
    print("设计完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()
