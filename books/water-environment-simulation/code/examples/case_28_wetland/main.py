"""案例28：湿地生态系统净化功能模拟"""
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.wetland_model import WetlandModel, assess_seasonal_variation
plt.switch_backend('Agg')

def main():
    print("="*70)
    print("案例28：湿地生态系统净化功能模拟")
    print("="*70)
    
    model = WetlandModel(area=1000, depth=0.5, porosity=0.4)
    
    # 不同HRT下的去除效率
    HRTs = np.linspace(1, 10, 10)
    efficiencies = []
    for HRT in HRTs:
        C_out, eff = model.calculate_removal(C_in=50, HRT=HRT, k_removal=0.3)
        efficiencies.append(eff)
    
    # 设计优化
    required_HRT, required_area = model.optimize_design(target_efficiency=80, C_in=50, k_removal=0.3)
    
    # 季节变化
    summer_k, winter_k = assess_seasonal_variation(25, 5)
    
    # 绘图
    plt.figure(figsize=(8, 6))
    plt.plot(HRTs, efficiencies, 'cs-', linewidth=2, markersize=8)
    plt.axhline(y=80, color='r', linestyle='--', label='Target (80%)')
    plt.xlabel('HRT (d)')
    plt.ylabel('Removal Efficiency (%)')
    plt.title('Wetland Treatment Performance')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('wetland.png', dpi=150)
    print("  ✓ 已保存: wetland.png")
    print("\n"+"="*70)
    print("案例28完成！")
    print("="*70)

if __name__ == '__main__':
    main()
