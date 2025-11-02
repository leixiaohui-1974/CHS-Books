#!/usr/bin/env python3
"""
案例11：鱼类索饵场水力-饵料关系分析

分析不同流速下的饵料分布、摄食效率和能量收支
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from models.fish_behavior import FeedingGroundModel, create_grass_carp_feeding_model

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

def main():
    print("=" * 60)
    print("案例11：鱼类索饵场水力-饵料关系分析")
    print("=" * 60)
    
    # 创建模型
    model = create_grass_carp_feeding_model()
    
    # 流速范围
    velocities = np.linspace(0.1, 2.0, 50)
    
    # 计算结果
    prey_densities = []
    feeding_efficiencies = []
    net_energies = []
    
    for v in velocities:
        prey_dens = model.prey_density_by_velocity(v)
        balance = model.energy_balance(v)
        
        prey_densities.append(prey_dens)
        feeding_efficiencies.append(balance['feeding_efficiency'])
        net_energies.append(balance['net_energy_J'])
    
    # 找最优流速
    optimal_v = model.optimal_feeding_velocity()
    
    print(f"\n鱼类: {model.species}")
    print(f"体长: {model.body_length} cm")
    print(f"体重: {model.body_weight} g")
    print(f"\n最优索饵流速: {optimal_v:.3f} m/s")
    
    # 详细结果
    print("\n流速 (m/s) | 饵料密度 (个/m³) | 摄食效率 | 净能量 (J)")
    print("-" * 60)
    for i, v in enumerate([0.3, 0.5, 0.7, 1.0, 1.5]):
        idx = int((v - 0.1) / (2.0 - 0.1) * 49)
        print(f"{v:8.2f}   | {prey_densities[idx]:16.1f} | {feeding_efficiencies[idx]:10.1f} | {net_energies[idx]:10.1f}")
    
    # 可视化
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 饵料密度分布
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(velocities, prey_densities, 'b-', linewidth=2)
    ax1.axvline(optimal_v, color='r', linestyle='--', label='最优流速')
    ax1.set_xlabel('流速 (m/s)', fontsize=10)
    ax1.set_ylabel('饵料密度 (个/m³)', fontsize=10)
    ax1.set_title('饵料密度-流速关系', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. 摄食效率
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(velocities, feeding_efficiencies, 'g-', linewidth=2)
    ax2.axvline(optimal_v, color='r', linestyle='--', label='最优流速')
    ax2.set_xlabel('流速 (m/s)', fontsize=10)
    ax2.set_ylabel('摄食效率', fontsize=10)
    ax2.set_title('摄食效率-流速关系', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. 净能量收支
    ax3 = plt.subplot(2, 3, 3)
    ax3.plot(velocities, net_energies, 'purple', linewidth=2)
    ax3.axhline(0, color='k', linestyle='-', alpha=0.3)
    ax3.axvline(optimal_v, color='r', linestyle='--', label='最优流速')
    ax3.fill_between(velocities, 0, net_energies, where=np.array(net_energies)>0, 
                     color='green', alpha=0.3, label='正收益区')
    ax3.fill_between(velocities, 0, net_energies, where=np.array(net_energies)<0,
                     color='red', alpha=0.3, label='负收益区')
    ax3.set_xlabel('流速 (m/s)', fontsize=10)
    ax3.set_ylabel('净能量 (J/h)', fontsize=10)
    ax3.set_title('能量收支平衡', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 4. 能量分项
    ax4 = plt.subplot(2, 3, 4)
    energy_gains = [model.energy_balance(v)['energy_gain_J'] for v in velocities]
    energy_costs = [model.energy_balance(v)['energy_cost_J'] for v in velocities]
    ax4.plot(velocities, energy_gains, 'g-', linewidth=2, label='能量收入')
    ax4.plot(velocities, energy_costs, 'r-', linewidth=2, label='能量支出')
    ax4.axvline(optimal_v, color='purple', linestyle='--', label='最优流速')
    ax4.set_xlabel('流速 (m/s)', fontsize=10)
    ax4.set_ylabel('能量 (J/h)', fontsize=10)
    ax4.set_title('能量收支分项', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # 5. 适宜流速区间
    ax5 = plt.subplot(2, 3, 5)
    is_favorable = [model.energy_balance(v)['is_favorable'] for v in velocities]
    colors = ['green' if f else 'red' for f in is_favorable]
    ax5.scatter(velocities, [1]*len(velocities), c=colors, s=100, alpha=0.6)
    ax5.axvline(optimal_v, color='purple', linestyle='--', linewidth=2, label='最优流速')
    ax5.set_xlabel('流速 (m/s)', fontsize=10)
    ax5.set_yticks([])
    ax5.set_title('适宜流速区间（绿色=适宜）', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='x')
    ax5.legend()
    
    # 6. 综合评价
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    summary_text = f"""
    【索饵场水力条件评价】
    
    物种: {model.species}
    体长: {model.body_length} cm
    体重: {model.body_weight} g
    
    最优流速: {optimal_v:.3f} m/s
    
    适宜流速范围:
    • 下限: 0.3 m/s
    • 上限: 1.2 m/s
    
    设计建议:
    • 营造多样化流速环境
    • 保留缓流区（< 0.5 m/s）
    • 避免高速冲刷（> 1.5 m/s）
    """
    ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes,
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
             family='monospace')
    
    plt.tight_layout()
    output_file = Path(__file__).parent / 'feeding_ground_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n图表已保存: {output_file}")
    
    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
