#!/usr/bin/env python3
"""案例9：丹尼尔式鱼道设计"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.denil_fishway import DenilFishway, create_denil_design

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例9：丹尼尔式鱼道水力设计")
    print("=" * 70)
    
    # 工程参数
    dam_height = 5.0  # 坝高5m
    Q_design = 0.5  # 设计流量0.5 m³/s
    fish_species = 'cyprinid'  # 鲤科鱼类
    
    print(f"\n工程条件:")
    print(f"  坝高: {dam_height} m")
    print(f"  设计流量: {Q_design} m³/s")
    print(f"  目标鱼类: 鲤科鱼类")
    
    # 创建设计方案
    design = create_denil_design(dam_height, Q_design, fish_species)
    
    print(f"\n推荐设计方案:")
    print(f"  槽道宽度: {design['channel_width']:.2f} m")
    print(f"  槽道长度: {design['channel_length']:.2f} m")
    print(f"  底坡: 1:{design['slope']}")
    print(f"  挡板数量: {design['baffle_config']['number_of_baffles']} 个")
    print(f"  挡板间距: {design['baffle_config']['baffle_spacing']:.2f} m")
    
    print(f"\n水力条件:")
    hc = design['hydraulic_conditions']
    print(f"  水深: {hc['water_depth']:.3f} m")
    print(f"  流速: {hc['velocity']:.2f} m/s")
    print(f"  弗劳德数: {hc['froude_number']:.3f}")
    print(f"  单位功率: {hc['unit_power']:.1f} W/m²")
    
    print(f"\n鱼类通过能力:")
    fp = design['fish_passage']
    print(f"  实际流速: {fp['velocity']:.2f} m/s")
    print(f"  临界流速: {fp['critical_velocity']:.2f} m/s")
    print(f"  实际功率: {fp['unit_power']:.1f} W/m²")
    print(f"  临界功率: {fp['critical_power']:.1f} W/m²")
    print(f"  适宜性评价: {fp['suitability']}")
    print(f"  评分: {fp['score']:.2f}")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 纵剖面图
    ax1 = plt.subplot(2, 3, 1)
    L = design['channel_length']
    x = np.linspace(0, L, 100)
    z_bottom = -x / design['slope']
    z_water = z_bottom + hc['water_depth']
    
    ax1.fill_between(x, z_bottom - 0.2, z_bottom, color='gray', alpha=0.5, label='底板')
    ax1.fill_between(x, z_bottom, z_water, color='lightblue', alpha=0.6, label='水体')
    ax1.plot(x, z_water, 'b-', linewidth=2, label='水面线')
    
    # 标注挡板位置
    baffle_x = np.arange(0, L, design['baffle_config']['baffle_spacing'])
    for bx in baffle_x[:10]:  # 只画前10个
        bz = -bx / design['slope']
        ax1.plot([bx, bx], [bz, bz + 0.15], 'r-', linewidth=3, alpha=0.7)
    
    ax1.set_xlabel('距离 (m)', fontsize=10)
    ax1.set_ylabel('高程 (m)', fontsize=10)
    ax1.set_title('丹尼尔鱼道纵剖面', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal', adjustable='box')
    
    # 2. 不同底坡下的流速对比
    ax2 = plt.subplot(2, 3, 2)
    opt_results = design['optimization_results']['all_results']
    slopes = [r['slope'] for r in opt_results]
    velocities = [r['velocity'] for r in opt_results]
    scores = [r['score'] for r in opt_results]
    
    color_map = plt.cm.RdYlGn(np.array(scores))
    bars = ax2.bar(slopes, velocities, color=color_map, edgecolor='black', linewidth=1.5)
    ax2.axhline(fp['critical_velocity'], color='r', linestyle='--', 
                linewidth=2, label=f'临界流速 {fp["critical_velocity"]:.1f} m/s')
    ax2.set_xlabel('底坡 (1:n)', fontsize=10)
    ax2.set_ylabel('流速 (m/s)', fontsize=10)
    ax2.set_title('不同底坡流速对比', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. 单位功率对比
    ax3 = plt.subplot(2, 3, 3)
    powers = [r['unit_power'] for r in opt_results]
    bars = ax3.bar(slopes, powers, color=color_map, edgecolor='black', linewidth=1.5)
    ax3.axhline(fp['critical_power'], color='r', linestyle='--',
                linewidth=2, label=f'临界功率 {fp["critical_power"]:.0f} W/m²')
    ax3.set_xlabel('底坡 (1:n)', fontsize=10)
    ax3.set_ylabel('单位功率 (W/m²)', fontsize=10)
    ax3.set_title('不同底坡单位功率对比', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. 适宜性评分
    ax4 = plt.subplot(2, 3, 4)
    bars = ax4.bar(slopes, scores, color=color_map, edgecolor='black', linewidth=1.5)
    ax4.set_xlabel('底坡 (1:n)', fontsize=10)
    ax4.set_ylabel('适宜性评分', fontsize=10)
    ax4.set_title('不同底坡适宜性评分', fontsize=12, fontweight='bold')
    ax4.set_ylim([0, 1.1])
    ax4.grid(True, alpha=0.3, axis='y')
    
    for i, (slope, score) in enumerate(zip(slopes, scores)):
        ax4.text(slope, score + 0.03, f'{score:.2f}', 
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 5. 流量-水深关系
    ax5 = plt.subplot(2, 3, 5)
    fishway = DenilFishway(design['channel_width'], 
                          design['channel_length'], 
                          design['slope'])
    Q_range = np.linspace(0.1, 1.5, 50)
    depths = [fishway.water_depth(q) for q in Q_range]
    vels = [fishway.flow_velocity(q) for q in Q_range]
    
    ax5.plot(Q_range, depths, 'b-', linewidth=2, label='水深')
    ax5.axvline(Q_design, color='g', linestyle='--', linewidth=2, 
                alpha=0.7, label=f'设计流量 {Q_design} m³/s')
    ax5.set_xlabel('流量 (m³/s)', fontsize=10)
    ax5.set_ylabel('水深 (m)', fontsize=10, color='b')
    ax5.tick_params(axis='y', labelcolor='b')
    ax5.set_title('流量-水深-流速关系', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    ax5_twin = ax5.twinx()
    ax5_twin.plot(Q_range, vels, 'r-', linewidth=2, label='流速')
    ax5_twin.set_ylabel('流速 (m/s)', fontsize=10, color='r')
    ax5_twin.tick_params(axis='y', labelcolor='r')
    
    # 合并图例
    lines1, labels1 = ax5.get_legend_handles_labels()
    lines2, labels2 = ax5_twin.get_legend_handles_labels()
    ax5.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    # 6. 挡板布置俯视图
    ax6 = plt.subplot(2, 3, 6)
    B = design['channel_width']
    s = design['baffle_config']['baffle_spacing']
    
    # 画几组挡板
    for i in range(8):
        x_pos = i * s
        # 交替倾斜的挡板
        if i % 2 == 0:
            ax6.plot([x_pos, x_pos + s*0.3], [0, B], 'r-', linewidth=4, alpha=0.7)
            ax6.plot([x_pos + s*0.3, x_pos + s*0.6], [B, 0], 'r-', linewidth=4, alpha=0.7)
            ax6.plot([x_pos + s*0.6, x_pos + s*0.9], [0, B], 'r-', linewidth=4, alpha=0.7)
        else:
            ax6.plot([x_pos, x_pos + s*0.3], [B, 0], 'b-', linewidth=4, alpha=0.7)
            ax6.plot([x_pos + s*0.3, x_pos + s*0.6], [0, B], 'b-', linewidth=4, alpha=0.7)
            ax6.plot([x_pos + s*0.6, x_pos + s*0.9], [B, 0], 'b-', linewidth=4, alpha=0.7)
    
    # 槽道边界
    ax6.plot([0, 8*s], [0, 0], 'k-', linewidth=2)
    ax6.plot([0, 8*s], [B, B], 'k-', linewidth=2)
    
    ax6.set_xlabel('纵向距离 (m)', fontsize=10)
    ax6.set_ylabel('横向距离 (m)', fontsize=10)
    ax6.set_title('挡板布置俯视图（局部）', fontsize=12, fontweight='bold')
    ax6.set_aspect('equal')
    ax6.grid(True, alpha=0.3)
    ax6.set_xlim([0, 8*s])
    ax6.set_ylim([-0.1, B + 0.1])
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'denil_fishway_design.png', dpi=300)
    print(f"\n图表已保存: denil_fishway_design.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
