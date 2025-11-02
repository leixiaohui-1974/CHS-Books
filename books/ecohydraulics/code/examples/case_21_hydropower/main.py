#!/usr/bin/env python3
"""案例21：水电站生态调度（代表性案例）"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.hydraulic_structures import HydropowerScheduling

rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 70)
    print("案例21：水电站生态调度多目标优化")
    print("=" * 70)
    
    # 参数
    scheduler = HydropowerScheduling(capacity_MW=100, ecological_flow=50)
    
    print(f"\n装机容量: {scheduler.capacity} MW")
    print(f"生态流量: {scheduler.Q_eco} m³/s")
    
    # 不同流量方案
    discharges = np.linspace(30, 200, 50)
    head = 50.0  # 水头50m
    
    result = scheduler.multi_objective_optimization(discharges, head)
    
    print(f"\nPareto最优解数量: {len(result['pareto_indices'])}")
    
    # 推荐方案（平衡点）
    pareto_Q = discharges[result['pareto_indices']]
    pareto_P = result['powers'][result['pareto_indices']]
    pareto_E = result['eco_benefits'][result['pareto_indices']]
    
    # 选择综合得分最高的
    综合得分 = pareto_P / np.max(pareto_P) * 0.5 + pareto_E / 100 * 0.5
    best_idx = np.argmax(综合得分)
    
    print(f"\n推荐调度方案:")
    print(f"  流量: {pareto_Q[best_idx]:.1f} m³/s")
    print(f"  发电量: {pareto_P[best_idx]:.1f} MW")
    print(f"  生态效益: {pareto_E[best_idx]:.1f} 分")
    
    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Pareto前沿
    ax1 = axes[0]
    ax1.scatter(result['powers'], result['eco_benefits'], 
               c='lightgray', alpha=0.5, s=30, label='所有方案')
    ax1.scatter(pareto_P, pareto_E,
               c='red', s=100, marker='*', label='Pareto最优')
    ax1.scatter([pareto_P[best_idx]], [pareto_E[best_idx]],
               c='green', s=300, marker='*', label='推荐方案', edgecolors='darkgreen', linewidths=2)
    ax1.set_xlabel('发电量 (MW)', fontsize=10)
    ax1.set_ylabel('生态效益 (分)', fontsize=10)
    ax1.set_title('多目标优化Pareto前沿', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 流量-双目标关系
    ax2 = axes[1]
    ax2.plot(discharges, result['powers'], 'b-', linewidth=2, label='发电量')
    ax2.set_xlabel('流量 (m³/s)', fontsize=10)
    ax2.set_ylabel('发电量 (MW)', color='b', fontsize=10)
    ax2.tick_params(axis='y', labelcolor='b')
    
    ax2_twin = ax2.twinx()
    ax2_twin.plot(discharges, result['eco_benefits'], 'g-', linewidth=2, label='生态效益')
    ax2_twin.set_ylabel('生态效益 (分)', color='g', fontsize=10)
    ax2_twin.tick_params(axis='y', labelcolor='g')
    
    ax2.axvline(pareto_Q[best_idx], color='r', linestyle='--', alpha=0.5)
    ax2.set_title('流量-目标关系', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / 'hydropower_scheduling.png', dpi=300)
    print(f"\n图表已保存")
    print("=" * 70)

if __name__ == '__main__':
    main()
