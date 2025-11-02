#!/usr/bin/env python3
"""
案例13：河流形态多样性设计

将渠化河道改造为近自然河道，增加深潭-浅滩序列
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.river_morphology import (
    PoolRiffleSequence,
    MeanderChannel,
    BedStability,
    design_naturalized_channel
)

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例13：河流形态多样性设计")
    print("=" * 70)
    
    # 设计参数
    width = 20.0  # 河道宽度 m
    length = 500.0  # 河段长度 m
    slope = 0.001  # 河道坡度
    discharge = 30.0  # 设计流量 m³/s
    d50 = 15.0  # 床沙粒径 mm
    
    print(f"\n【设计条件】")
    print(f"河道宽度: {width} m")
    print(f"河段长度: {length} m")
    print(f"河道坡度: {slope}")
    print(f"设计流量: {discharge} m³/s")
    print(f"床沙粒径 d50: {d50} mm")
    
    # 综合设计
    design = design_naturalized_channel(width, length, slope, discharge, d50)
    
    # 输出设计成果
    print(f"\n【深潭-浅滩设计】")
    print(f"深潭间距: {design['pool_spacing']:.1f} m ({design['pool_spacing']/width:.1f}倍河宽)")
    print(f"深潭水深: {design['pool_depth']:.2f} m")
    print(f"浅滩水深: {design['riffle_depth']:.2f} m")
    print(f"深潭数量: {int(length / design['pool_spacing'])} 个")
    
    print(f"\n【弯道设计】")
    print(f"弯道半径: {design['meander_radius']:.1f} m ({design['meander_radius']/width:.1f}倍河宽)")
    print(f"内外岸流速比: {design['velocity_ratio']:.2f}")
    print(f"环流强度: {design['secondary_flow']:.3f}")
    print(f"外岸冲刷深度: {design['bend_scour']:.2f} m")
    
    print(f"\n【水力多样性】")
    div = design['hydraulic_diversity']
    print(f"Shannon指数: {div['shannon_index']:.3f}")
    print(f"Simpson指数: {div['simpson_index']:.3f}")
    print(f"流速变化范围: {div['velocity_range']:.2f} m/s")
    print(f"流速变异系数: {div['velocity_cv']:.3f}")
    
    print(f"\n【河床稳定性】")
    stab = design['stability']
    print(f"Shields应力: {stab['shields_stress']:.4f}")
    print(f"起动流速: {stab['critical_velocity']:.2f} m/s")
    print(f"实际流速: {stab['actual_velocity']:.2f} m/s")
    print(f"稳定性评价: {stab['stability']}")
    print(f"冲刷风险: {stab['erosion_risk']}")
    print(f"输沙状态: {stab['transport_status']}")
    
    # 可视化
    x, h, v = design['profile']
    
    fig = plt.figure(figsize=(16, 10))
    
    # 1. 纵剖面
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(x, h, 'b-', linewidth=2)
    ax1.axhline(design['pool_depth'], color='r', linestyle='--', 
                alpha=0.5, label=f"深潭水深 {design['pool_depth']:.2f}m")
    ax1.axhline(design['riffle_depth'], color='g', linestyle='--', 
                alpha=0.5, label=f"浅滩水深 {design['riffle_depth']:.2f}m")
    ax1.fill_between(x, 0, h, alpha=0.3, color='lightblue')
    ax1.set_xlabel('距离 (m)', fontsize=10)
    ax1.set_ylabel('水深 (m)', fontsize=10)
    ax1.set_title('深潭-浅滩纵剖面', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=8)
    ax1.invert_yaxis()
    
    # 2. 流速分布
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(x, v, 'purple', linewidth=2)
    ax2.axhline(stab['critical_velocity'], color='r', linestyle='--', 
                label=f"起动流速 {stab['critical_velocity']:.2f}m/s")
    ax2.fill_between(x, 0, v, alpha=0.3, color='orange')
    ax2.set_xlabel('距离 (m)', fontsize=10)
    ax2.set_ylabel('流速 (m/s)', fontsize=10)
    ax2.set_title('流速沿程分布', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8)
    
    # 3. 流速频率分布
    ax3 = plt.subplot(2, 3, 3)
    ax3.hist(v, bins=30, color='steelblue', alpha=0.7, edgecolor='black')
    ax3.axvline(np.mean(v), color='r', linestyle='--', linewidth=2, label=f'平均 {np.mean(v):.2f}m/s')
    ax3.axvline(stab['critical_velocity'], color='orange', linestyle='--', 
                linewidth=2, label=f'起动 {stab["critical_velocity"]:.2f}m/s')
    ax3.set_xlabel('流速 (m/s)', fontsize=10)
    ax3.set_ylabel('频次', fontsize=10)
    ax3.set_title('流速频率分布', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.legend(fontsize=8)
    
    # 4. 水深-流速关系
    ax4 = plt.subplot(2, 3, 4)
    scatter = ax4.scatter(h, v, c=x, cmap='viridis', s=20, alpha=0.6)
    ax4.set_xlabel('水深 (m)', fontsize=10)
    ax4.set_ylabel('流速 (m/s)', fontsize=10)
    ax4.set_title('水深-流速关系', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('距离 (m)', fontsize=8)
    
    # 5. 弯道横断面示意
    ax5 = plt.subplot(2, 3, 5)
    # 绘制弯道横断面
    y_coords = np.linspace(0, width, 50)
    # 外岸深、内岸浅
    z_bed = design['bend_scour'] * (1 - y_coords / width) + design['riffle_depth'] * (y_coords / width)
    z_surface = np.zeros_like(y_coords)
    
    ax5.fill_between(y_coords, z_bed, z_surface, alpha=0.4, color='lightblue', label='水体')
    ax5.plot(y_coords, z_bed, 'brown', linewidth=2, label='河床')
    ax5.axhline(0, color='blue', linestyle='--', alpha=0.5)
    ax5.text(width*0.1, -design['bend_scour']*0.5, '外岸\n(深槽)', 
             ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat'))
    ax5.text(width*0.9, -design['riffle_depth']*0.5, '内岸\n(浅滩)', 
             ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='lightgreen'))
    ax5.set_xlabel('横向距离 (m)', fontsize=10)
    ax5.set_ylabel('高程 (m)', fontsize=10)
    ax5.set_title('弯道横断面', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    ax5.legend(fontsize=8)
    ax5.invert_yaxis()
    
    # 6. 设计成果汇总
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    summary_text = f"""
    【近自然河道设计成果】
    
    ═══ 形态设计 ═══
    深潭间距: {design['pool_spacing']:.1f} m
    深潭深度: {design['pool_depth']:.2f} m
    浅滩深度: {design['riffle_depth']:.2f} m
    弯道半径: {design['meander_radius']:.1f} m
    
    ═══ 水力特性 ═══
    流速范围: {v.min():.2f}-{v.max():.2f} m/s
    Shannon指数: {div['shannon_index']:.3f}
    环流强度: {design['secondary_flow']:.3f}
    
    ═══ 稳定性 ═══
    评价等级: {stab['stability']}
    冲刷风险: {stab['erosion_risk']}
    输沙状态: {stab['transport_status']}
    
    ═══ 生态效益 ═══
    • 生境多样性显著提升
    • 深潭为鱼类提供庇护所
    • 浅滩适合水生植物生长
    • 弯道形成多样微生境
    """
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes,
             fontsize=9, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8),
             family='monospace')
    
    plt.tight_layout()
    output_file = Path(__file__).parent / 'river_morphology_design.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n图表已保存: {output_file}")
    
    print("\n" + "=" * 70)
    print("设计完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()
