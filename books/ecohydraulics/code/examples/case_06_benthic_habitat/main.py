"""案例6：底栖生物栖息地水力条件评价（简化版）"""
import sys, os
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from code.models.channel import RiverReach
from code.models.benthic import BenthicHabitatModel

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def main():
    print("\n" + "="*80)
    print("案例6：底栖生物栖息地水力条件评价".center(80))
    print("="*80)
    
    reach = RiverReach(length=1000, width=15, slope=0.002, roughness=0.030, side_slope=2.0)
    d50 = 0.02  # 底质中值粒径20mm
    
    print(f"\n河段参数: 长{reach.length}m, 宽{reach.b}m, 坡度{reach.S0}")
    print(f"底质粒径: {d50*1000:.0f}mm")
    
    Q_range = np.linspace(5, 30, 10)
    print(f"\n不同流量下的底质稳定性:")
    print(f"{'流量(m³/s)':<12} {'水深(m)':<10} {'剪应力(Pa)':<12} {'Shields数':<12} {'稳定性':<12}")
    print("-"*65)
    
    for Q in Q_range:
        h = reach.solve_depth(Q)
        tau = BenthicHabitatModel.bed_shear_stress(reach, h)
        theta = BenthicHabitatModel.shields_number(tau, d50)
        stability = BenthicHabitatModel.substrate_stability(theta)
        print(f"{Q:<12.1f} {h:<10.2f} {tau:<12.2f} {theta:<12.4f} {stability['status']:<12}")
    
    # 可视化
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    taus = [BenthicHabitatModel.bed_shear_stress(reach, reach.solve_depth(Q)) for Q in Q_range]
    thetas = [BenthicHabitatModel.shields_number(tau, d50) for tau in taus]
    
    ax1.plot(Q_range, taus, 'b-', linewidth=2, marker='o')
    ax1.set_xlabel('Flow (m³/s)', fontsize=11)
    ax1.set_ylabel('Shear Stress (Pa)', fontsize=11)
    ax1.set_title('Bed Shear Stress', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(Q_range, thetas, 'r-', linewidth=2, marker='s')
    ax2.axhline(0.05, color='orange', linestyle='--', label='Critical')
    ax2.set_xlabel('Flow (m³/s)', fontsize=11)
    ax2.set_ylabel('Shields Number', fontsize=11)
    ax2.set_title('Substrate Stability', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('benthic_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ 已保存: benthic_analysis.png")
    
    print("\n" + "="*80)
    print("评估完成！".center(80))
    print("="*80)

if __name__ == "__main__":
    main()
