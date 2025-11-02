#!/usr/bin/env python3
"""案例38：河口盐水楔三维模拟"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.estuary_coastal import SaltWedge

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例38：河口盐水楔三维模拟")
    print("=" * 70)
    
    # 河口参数
    estuary = SaltWedge(
        estuary_depth=10.0,  # 10m
        estuary_width=500.0,  # 500m
        river_discharge=500.0  # 500m³/s
    )
    
    print(f"\n河口基本参数:")
    print(f"  平均水深: {estuary.h:.1f} m")
    print(f"  河口宽度: {estuary.W:.1f} m")
    print(f"  径流量: {estuary.Q_r:.1f} m³/s")
    
    # 1. 混合类型分类
    mixing = estuary.mixing_type_classification()
    print(f"\n混合类型分类:")
    print(f"  密度弗劳德数: {mixing['froude_number']:.3f}")
    print(f"  混合类型: {mixing['mixing_type']}")
    print(f"  描述: {mixing['description']}")
    
    # 2. 盐水楔长度
    L_wedge = estuary.salt_wedge_length(tidal_range=2.5)
    print(f"\n盐水楔长度: {L_wedge:.2f} km")
    
    # 3. 盐度分布
    distances = np.linspace(0, 30, 100)
    
    S_surface = estuary.salinity_distribution(distances, 0.0)
    S_middle = estuary.salinity_distribution(distances, 0.5)
    S_bottom = estuary.salinity_distribution(distances, 1.0)
    
    print(f"\n典型位置盐度（距河口10km）:")
    idx = 33
    print(f"  表层: {S_surface[idx]:.1f} ppt")
    print(f"  中层: {S_middle[idx]:.1f} ppt")
    print(f"  底层: {S_bottom[idx]:.1f} ppt")
    
    # 4. 分层参数
    alpha = estuary.stratification_parameter(S_surface[idx], S_bottom[idx])
    print(f"  分层参数: {alpha:.3f}")
    
    # 5. 停留时间
    T = estuary.residence_time(20.0)
    print(f"\n河口水体停留时间: {T:.1f} 天")
    
    # 6. 生态影响
    print(f"\n生态影响评估:")
    for dist_km in [5, 10, 15, 20]:
        idx = int(dist_km / 30 * 100)
        avg_sal = (S_surface[idx] + S_bottom[idx]) / 2
        eco = estuary.ecological_impact_assessment(avg_sal)
        print(f"  {dist_km}km处: {eco['ecological_zone']}, "
              f"盐度{eco['salinity']:.1f}ppt, 多样性{eco['biodiversity']}")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 盐度纵向分布
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(distances, S_surface, 'b-', linewidth=2, label='表层')
    ax1.plot(distances, S_middle, 'g-', linewidth=2, label='中层')
    ax1.plot(distances, S_bottom, 'r-', linewidth=2, label='底层')
    ax1.axvline(L_wedge, color='k', linestyle='--', alpha=0.5, label=f'楔长{L_wedge:.1f}km')
    ax1.set_xlabel('距河口距离 (km)', fontsize=10)
    ax1.set_ylabel('盐度 (ppt)', fontsize=10)
    ax1.set_title('盐度纵向分布', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 30])
    ax1.set_ylim([0, 35])
    
    # 2. 盐度剖面（距河口10km）
    ax2 = plt.subplot(2, 3, 2)
    depths_frac = np.linspace(0, 1, 50)
    salinities_10km = estuary.salinity_distribution(np.ones(50) * 10, depths_frac)
    
    ax2.plot(salinities_10km, depths_frac * estuary.h, 'b-', linewidth=3)
    ax2.fill_betweenx(depths_frac * estuary.h, 0, salinities_10km, alpha=0.3, color='blue')
    ax2.set_xlabel('盐度 (ppt)', fontsize=10)
    ax2.set_ylabel('水深 (m)', fontsize=10)
    ax2.set_title('垂向盐度剖面（10km处）', fontsize=12, fontweight='bold')
    ax2.invert_yaxis()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 35])
    
    # 3. 密度弗劳德数对混合类型的影响
    ax3 = plt.subplot(2, 3, 3)
    discharges = np.linspace(100, 2000, 50)
    froude_nums = []
    
    for Q in discharges:
        est_temp = SaltWedge(10.0, 500.0, Q)
        froude_nums.append(est_temp.densimetric_froude_number())
    
    ax3.plot(discharges, froude_nums, 'r-', linewidth=2)
    ax3.axhline(1.0, color='g', linestyle='--', linewidth=2, label='高度混合型')
    ax3.axhline(0.08, color='orange', linestyle='--', linewidth=2, label='盐水楔型')
    ax3.fill_between(discharges, 0, 0.08, color='blue', alpha=0.2, label='盐水楔')
    ax3.fill_between(discharges, 0.08, 1.0, color='yellow', alpha=0.2, label='部分混合')
    ax3.fill_between(discharges, 1.0, 2.0, color='green', alpha=0.2, label='高度混合')
    ax3.axvline(estuary.Q_r, color='k', linestyle=':', linewidth=2, label='当前流量')
    ax3.set_xlabel('径流量 (m³/s)', fontsize=10)
    ax3.set_ylabel('密度弗劳德数', fontsize=10)
    ax3.set_title('径流量对混合类型的影响', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    ax3.set_yscale('log')
    
    # 4. 盐度三维示意图
    ax4 = plt.subplot(2, 3, 4, projection='3d')
    X, Y = np.meshgrid(distances[:50], np.linspace(0, 1, 20))
    Z = np.zeros_like(X)
    for i in range(X.shape[1]):
        Z[:, i] = estuary.salinity_distribution(np.ones(20) * distances[i], Y[:, 0])
    
    surf = ax4.plot_surface(X, Y * estuary.h, Z, cmap='coolwarm', alpha=0.8)
    ax4.set_xlabel('距离 (km)', fontsize=9)
    ax4.set_ylabel('水深 (m)', fontsize=9)
    ax4.set_zlabel('盐度 (ppt)', fontsize=9)
    ax4.set_title('河口盐度三维分布', fontsize=12, fontweight='bold')
    ax4.invert_yaxis()
    
    # 5. 生态分区
    ax5 = plt.subplot(2, 3, 5)
    zones = []
    zone_colors = []
    for d in distances[::5]:
        idx = int(d / 30 * 100)
        avg_sal = (S_surface[idx] + S_bottom[idx]) / 2
        eco = estuary.ecological_impact_assessment(avg_sal)
        zones.append(eco['ecological_zone'])
        
        if avg_sal < 0.5:
            zone_colors.append('lightblue')
        elif avg_sal < 5:
            zone_colors.append('lightgreen')
        elif avg_sal < 18:
            zone_colors.append('yellow')
        else:
            zone_colors.append('orange')
    
    ax5.bar(distances[::5], np.ones(len(distances[::5])), color=zone_colors,
           edgecolor='black', linewidth=0.5, width=1.5)
    ax5.set_xlabel('距河口距离 (km)', fontsize=10)
    ax5.set_ylabel('生态分区', fontsize=10)
    ax5.set_title('河口生态分区示意', fontsize=12, fontweight='bold')
    ax5.set_ylim([0, 1.2])
    ax5.set_yticks([])
    
    # 添加图例
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='lightblue', label='淡水区'),
                      Patch(facecolor='lightgreen', label='低盐区'),
                      Patch(facecolor='yellow', label='半咸水区'),
                      Patch(facecolor='orange', label='高盐区')]
    ax5.legend(handles=legend_elements, loc='upper right')
    
    # 6. 停留时间随流量变化
    ax6 = plt.subplot(2, 3, 6)
    Q_range = np.linspace(100, 1500, 30)
    residence_times = []
    
    for Q in Q_range:
        est_temp = SaltWedge(10.0, 500.0, Q)
        residence_times.append(est_temp.residence_time(20.0))
    
    ax6.plot(Q_range, residence_times, 'b-', linewidth=2, marker='o', markersize=4)
    ax6.axvline(estuary.Q_r, color='r', linestyle='--', linewidth=2,
               alpha=0.7, label=f'当前{estuary.Q_r:.0f}m³/s')
    ax6.set_xlabel('径流量 (m³/s)', fontsize=10)
    ax6.set_ylabel('停留时间 (天)', fontsize=10)
    ax6.set_title('停留时间随径流量变化', fontsize=12, fontweight='bold')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'salt_wedge_simulation.png', dpi=300)
    print(f"\n图表已保存: salt_wedge_simulation.png")
    print("=" * 70)

if __name__ == '__main__':
    main()
