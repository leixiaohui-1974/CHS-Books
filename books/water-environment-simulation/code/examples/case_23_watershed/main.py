"""案例23：流域水文-水质耦合模拟"""
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.watershed_model import WatershedModel, assess_land_use_impact
plt.switch_backend('Agg')

def main():
    print("="*70)
    print("案例23：流域水文-水质耦合模拟")
    print("="*70)
    
    model = WatershedModel(area=500, n_subbasins=5)
    
    # 模拟不同降雨
    rainfalls = [20, 50, 100, 150]
    runoffs = [model.simulate_runoff(r) for r in rainfalls]
    loads = [model.calculate_pollutant_load(r, EMC=50) for r in runoffs]
    
    # 土地利用影响
    impact = assess_land_use_impact(0.4, 0.3)
    
    # 绘图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.plot(rainfalls, runoffs, 'bo-', linewidth=2)
    ax1.set_xlabel('Rainfall (mm)')
    ax1.set_ylabel('Runoff (mm)')
    ax1.set_title('Rainfall-Runoff')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(rainfalls, loads, 'ro-', linewidth=2)
    ax2.set_xlabel('Rainfall (mm)')
    ax2.set_ylabel('Pollutant Load (kg)')
    ax2.set_title('Pollutant Load')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('watershed.png', dpi=150)
    print("  ✓ 已保存: watershed.png")
    print("\n"+"="*70)
    print("案例23完成！")
    print("="*70)

if __name__ == '__main__':
    main()
