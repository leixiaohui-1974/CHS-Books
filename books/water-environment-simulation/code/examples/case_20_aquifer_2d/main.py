"""
案例20：二维含水层污染羽迁移
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.aquifer_2d import Aquifer2D, assess_well_risk

plt.switch_backend('Agg')

def main():
    print("=" * 70)
    print("案例20：二维含水层污染羽迁移")
    print("=" * 70)
    
    # 初始化
    model = Aquifer2D(Lx=500, Ly=300, nx=100, ny=60)
    
    # 参数
    vx = 0.5  # 主流向速度 (m/d)
    vy = 0.0  # 横向速度 (m/d)
    Dx = 5.0  # 纵向弥散 (m²/d)
    Dy = 2.0  # 横向弥散 (m²/d)
    decay = 0.01  # 衰减系数 (1/d)
    
    # 污染源位置
    source_x = 50  # m
    source_y = 150  # m
    source_C = 100  # mg/L
    
    # 下游水井位置
    well_x = 300  # m
    well_y = 150  # m
    
    # 模拟
    t = np.linspace(0, 365, 200)
    t_out, C_history = model.solve_transport(t, vx, vy, Dx, Dy, decay, 
                                              source_x, source_y, source_C)
    
    # 风险评估
    at_risk, conc = assess_well_risk(model.C, well_x, well_y, model.Lx, model.Ly, threshold=10)
    
    # 绘图
    print("\n生成图表...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 选择4个时刻
    time_indices = [0, len(C_history)//3, 2*len(C_history)//3, -1]
    time_labels = ['t=0d', 't=122d', 't=244d', 't=365d']
    
    for idx, (ti, label) in enumerate(zip(time_indices, time_labels)):
        ax = axes[idx//2, idx%2]
        
        im = ax.contourf(model.x, model.y, C_history[ti], levels=20, cmap='RdYlBu_r')
        ax.plot(source_x, source_y, 'r*', markersize=15, label='Source')
        ax.plot(well_x, well_y, 'bs', markersize=10, label='Well')
        ax.set_xlabel('X (m)', fontsize=11)
        ax.set_ylabel('Y (m)', fontsize=11)
        ax.set_title(label, fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.set_aspect('equal')
        plt.colorbar(im, ax=ax, label='C (mg/L)')
    
    plt.tight_layout()
    plt.savefig('aquifer_2d_plume.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: aquifer_2d_plume.png")
    
    print("\n" + "=" * 70)
    print("案例20完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()
