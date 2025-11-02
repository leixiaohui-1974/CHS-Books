"""
案例21：多层含水层垂向迁移
"""

import numpy as np
import matplotlib.pyplot as plt
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from models.multilayer_aquifer import MultilayerAquifer, assess_aquitard_protection

plt.switch_backend('Agg')

def main():
    print("=" * 70)
    print("案例21：多层含水层垂向迁移")
    print("=" * 70)
    
    # 初始化
    model = MultilayerAquifer(layers=20, dz=2)
    
    # 顶层污染源
    model.C[0] = 100  # mg/L
    
    # 模拟
    t = np.linspace(0, 365, 200)
    t_out, z_out, C_history = model.solve(t, Kz=0.1, theta=0.3)
    
    # 评估保护效果
    protection = assess_aquitard_protection(C_history[-1, 5], C_history[-1, 15])
    
    # 绘图
    print("\n生成图表...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 时空图
    im = ax1.contourf(t_out, z_out, C_history.T, levels=20, cmap='RdYlBu_r')
    ax1.set_xlabel('Time (d)', fontsize=12)
    ax1.set_ylabel('Depth (m)', fontsize=12)
    ax1.set_title('Vertical Transport', fontsize=14, fontweight='bold')
    ax1.invert_yaxis()
    plt.colorbar(im, ax=ax1, label='C (mg/L)')
    
    # 浓度剖面
    for i in [0, len(t_out)//2, -1]:
        ax2.plot(C_history[i, :], z_out, linewidth=2, label=f't={t_out[i]:.0f}d')
    ax2.set_xlabel('Concentration (mg/L)', fontsize=12)
    ax2.set_ylabel('Depth (m)', fontsize=12)
    ax2.set_title('Concentration Profiles', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.invert_yaxis()
    
    plt.tight_layout()
    plt.savefig('multilayer_aquifer.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: multilayer_aquifer.png")
    
    print("\n" + "=" * 70)
    print("案例21完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()
