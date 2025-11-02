#!/usr/bin/env python3
"""案例16：卵石河床补充与稳定性分析"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.sediment_gravel import GravelSupplementDesign

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例16：卵石河床补充与稳定性分析")
    print("=" * 70)
    
    design = GravelSupplementDesign(target_d50=25.0)
    
    print(f"\n目标粒径 d50: {design.target_d50} mm")
    
    # 粒径配比
    size_dist = design.gravel_size_distribution()
    print(f"\n粒径配比设计:")
    for key, val in size_dist.items():
        print(f"  {key}: {val:.1f} mm")
    
    # 稳定性分析
    print(f"\n稳定性分析 (水深2m, 坡度0.001):")
    velocities = [0.5, 0.8, 1.0, 1.5]
    for v in velocities:
        result = design.stability_assessment(v, 2.0, 0.001)
        print(f"  流速{v:.1f}m/s: {result['stability_status']}, "
              f"安全系数={result['safety_factor']:.2f}")
    
    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 粒径分布
    ax1 = axes[0]
    sizes = list(size_dist.values())
    labels = list(size_dist.keys())
    ax1.bar(labels, sizes, color='brown', alpha=0.7, edgecolor='black')
    ax1.set_ylabel('粒径 (mm)', fontsize=10)
    ax1.set_title('卵石粒径配比', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 稳定性曲线
    ax2 = axes[1]
    v_range = np.linspace(0.3, 2.0, 50)
    safety_factors = [design.stability_assessment(v, 2.0, 0.001)['safety_factor'] 
                     for v in v_range]
    ax2.plot(v_range, safety_factors, 'b-', linewidth=2)
    ax2.axhline(1.0, color='r', linestyle='--', label='临界线')
    ax2.axhline(1.5, color='orange', linestyle='--', label='安全线')
    ax2.set_xlabel('流速 (m/s)', fontsize=10)
    ax2.set_ylabel('安全系数', fontsize=10)
    ax2.set_title('卵石稳定性分析', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'gravel_supplement.png', dpi=300)
    print(f"\n图表已保存")
    print("=" * 70)

if __name__ == '__main__':
    main()
