"""案例27：湖泊生态系统稳态转换"""
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.lake_regime_shift import LakeRegimeShiftModel, find_critical_load
plt.switch_backend('Agg')

def main():
    print("="*70)
    print("案例27：湖泊生态系统稳态转换")
    print("="*70)
    
    # 低磷负荷（清水态）
    model1 = LakeRegimeShiftModel(P_load=0.3)
    t = np.linspace(0, 200, 500)
    t1, result1, regime1 = model1.solve(t)
    
    # 高磷负荷（浊水态）
    model2 = LakeRegimeShiftModel(P_load=0.8)
    t2, result2, regime2 = model2.solve(t)
    
    # 临界负荷
    critical_load = find_critical_load([0.1, 1.0])
    
    # 绘图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.plot(t1, result1[:, 0], 'g-', linewidth=2, label='Macrophytes')
    ax1.plot(t1, result1[:, 1], 'brown', linewidth=2, label='Algae')
    ax1.set_xlabel('Time (d)')
    ax1.set_ylabel('Biomass (g/m²)')
    ax1.set_title(f'Low P Load: {regime1}')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(t2, result2[:, 0], 'g-', linewidth=2, label='Macrophytes')
    ax2.plot(t2, result2[:, 1], 'brown', linewidth=2, label='Algae')
    ax2.set_xlabel('Time (d)')
    ax2.set_ylabel('Biomass (g/m²)')
    ax2.set_title(f'High P Load: {regime2}')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('lake_regime_shift.png', dpi=150)
    print("  ✓ 已保存: lake_regime_shift.png")
    print("\n"+"="*70)
    print("案例27完成！")
    print("="*70)

if __name__ == '__main__':
    main()
