"""
案例17：湖泊藻类生长动力学模拟
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.algae_dynamics import AlgaeGrowthModel, assess_bloom_risk

plt.switch_backend('Agg')

def main():
    print("=" * 70)
    print("案例17：湖泊藻类生长动力学模拟")
    print("=" * 70)
    
    # 初始化
    model = AlgaeGrowthModel(Chl0=5, N0=500, P0=50, DO0=8)
    
    # 模拟180天（春-夏-秋）
    t = np.linspace(0, 180, 1000)
    t_out, result = model.solve(t, I=200, T=25)
    
    Chl = result[:, 0]
    N = result[:, 1]
    P = result[:, 2]
    DO = result[:, 3]
    
    # 水华风险评估
    status, level = assess_bloom_risk(Chl[-1])
    print(f"\n水华风险: {status}")
    
    # 绘图
    print("\n生成图表...")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    ax1.plot(t, Chl, 'g-', linewidth=2)
    ax1.axhline(y=10, color='orange', linestyle='--', label='Warning')
    ax1.axhline(y=30, color='r', linestyle='--', label='Bloom')
    ax1.set_xlabel('Time (d)')
    ax1.set_ylabel('Chl-a (μg/L)')
    ax1.set_title('Algae Growth')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(t, N, 'b-', linewidth=2, label='N')
    ax2.plot(t, P, 'r-', linewidth=2, label='P')
    ax2.set_xlabel('Time (d)')
    ax2.set_ylabel('Concentration (μg/L)')
    ax2.set_title('Nutrients')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    ax3.plot(t, DO, 'c-', linewidth=2)
    ax3.set_xlabel('Time (d)')
    ax3.set_ylabel('DO (mg/L)')
    ax3.set_title('Dissolved Oxygen')
    ax3.grid(True, alpha=0.3)
    
    ax4.plot(N, Chl, 'b-', linewidth=2, label='N vs Chl')
    ax4.plot(P, Chl, 'r-', linewidth=2, label='P vs Chl')
    ax4.set_xlabel('Nutrient (μg/L)')
    ax4.set_ylabel('Chl-a (μg/L)')
    ax4.set_title('Nutrient Limitation')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('algae_dynamics.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: algae_dynamics.png")
    
    print("\n" + "=" * 70)
    print("案例17完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()
