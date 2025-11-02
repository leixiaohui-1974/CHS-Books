#!/usr/bin/env python3
"""案例17：河口感潮河段生态水力学"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.sediment_gravel import EstuaryHydraulics

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例17：河口感潮河段生态水力学")
    print("=" * 70)
    
    estuary = EstuaryHydraulics(tidal_range=3.0)
    
    print(f"\n潮差: {estuary.tidal_range} m")
    
    # 潮汐过程
    t = np.linspace(0, 24, 100)
    water_levels = [estuary.tidal_water_level(ti) for ti in t]
    
    # 盐水楔
    flows = [50, 100, 200, 500]
    print(f"\n盐水楔侵入距离:")
    for Q in flows:
        L = estuary.saltwater_intrusion(Q)
        print(f"  流量{Q:4.0f}m³/s: {L:.1f} km")
    
    eco_flow = estuary.ecological_water_requirement()
    print(f"\n生态需水量: {eco_flow:.0f} m³/s")
    
    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 潮汐水位
    ax1 = axes[0]
    ax1.plot(t, water_levels, 'b-', linewidth=2)
    ax1.fill_between(t, 0, water_levels, where=np.array(water_levels)>0, 
                     color='lightblue', alpha=0.3, label='涨潮')
    ax1.fill_between(t, 0, water_levels, where=np.array(water_levels)<0,
                     color='lightcoral', alpha=0.3, label='落潮')
    ax1.set_xlabel('时间 (小时)', fontsize=10)
    ax1.set_ylabel('水位 (m)', fontsize=10)
    ax1.set_title('潮汐水位过程', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 盐水楔
    ax2 = axes[1]
    flow_range = np.linspace(50, 500, 50)
    intrusion = [estuary.saltwater_intrusion(Q) for Q in flow_range]
    ax2.plot(flow_range, intrusion, 'purple', linewidth=2)
    ax2.axvline(eco_flow, color='g', linestyle='--', label=f'生态需水 {eco_flow:.0f}m³/s')
    ax2.set_xlabel('径流量 (m³/s)', fontsize=10)
    ax2.set_ylabel('盐水楔侵入距离 (km)', fontsize=10)
    ax2.set_title('径流-盐水楔关系', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'estuary_hydraulics.png', dpi=300)
    print(f"\n图表已保存")
    print("=" * 70)

if __name__ == '__main__':
    main()
