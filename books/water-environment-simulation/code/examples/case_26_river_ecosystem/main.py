"""案例26：河流生态系统模拟"""
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.river_ecosystem import RiverEcosystemModel, calculate_biodiversity_index
plt.switch_backend('Agg')

def main():
    print("="*70)
    print("案例26：河流生态系统模拟")
    print("="*70)
    
    model = RiverEcosystemModel()
    t = np.linspace(0, 100, 500)
    t_out, result = model.solve(t)
    
    # 生物多样性
    H = calculate_biodiversity_index(result[-1, :])
    
    # 绘图
    plt.figure(figsize=(10, 6))
    plt.plot(t_out, result[:, 0], 'g-', linewidth=2, label='Algae')
    plt.plot(t_out, result[:, 1], 'b-', linewidth=2, label='Zooplankton')
    plt.plot(t_out, result[:, 2], 'r-', linewidth=2, label='Fish')
    plt.xlabel('Time (d)')
    plt.ylabel('Biomass (mg/L)')
    plt.title('River Ecosystem Dynamics')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('river_ecosystem.png', dpi=150)
    print("  ✓ 已保存: river_ecosystem.png")
    print("\n"+"="*70)
    print("案例26完成！")
    print("="*70)

if __name__ == '__main__':
    main()
