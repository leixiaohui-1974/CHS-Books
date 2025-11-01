#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""水工建筑物综合对比分析"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def weir_flow(m, b, H):
    """堰流：Q = mbH^(3/2)"""
    return m * b * H**(3/2)

def gate_flow(epsilon, b, e, H):
    """闸孔出流：Q = εbe√(2gH)"""
    return epsilon * b * e * np.sqrt(2 * 9.81 * H)

def orifice_flow(mu, A, H):
    """孔口出流：Q = μA√(2gH)"""
    return mu * A * np.sqrt(2 * 9.81 * H)

def plot_comparison(filename='hydraulic_structures_comp.png'):
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    # 子图1：三种泄流建筑物示意
    ax1 = axes[0, 0]
    ax1.text(0.5, 0.8, '堰流', ha='center', fontsize=14, fontweight='bold')
    ax1.text(0.5, 0.6, 'Q = mbH^(3/2)', ha='center', fontsize=10, family='monospace')
    ax1.text(0.5, 0.4, '• 薄壁堰', fontsize=9)
    ax1.text(0.5, 0.3, '• 实用堰', fontsize=9)
    ax1.text(0.5, 0.2, '• WES堰', fontsize=9)
    ax1.axis('off')
    ax1.set_title('(a) 溢流堰', fontsize=12, fontweight='bold')
    
    ax2 = axes[0, 1]
    ax2.text(0.5, 0.8, '闸孔出流', ha='center', fontsize=14, fontweight='bold')
    ax2.text(0.5, 0.6, 'Q = εbe√(2gH)', ha='center', fontsize=10, family='monospace')
    ax2.text(0.5, 0.4, '• 平板闸门', fontsize=9)
    ax2.text(0.5, 0.3, '• 弧形闸门', fontsize=9)
    ax2.text(0.5, 0.2, '• 可调节', fontsize=9)
    ax2.axis('off')
    ax2.set_title('(b) 闸孔', fontsize=12, fontweight='bold')
    
    ax3 = axes[0, 2]
    ax3.text(0.5, 0.8, '孔口出流', ha='center', fontsize=14, fontweight='bold')
    ax3.text(0.5, 0.6, 'Q = μA√(2gH)', ha='center', fontsize=10, family='monospace')
    ax3.text(0.5, 0.4, '• 有压/无压', fontsize=9)
    ax3.text(0.5, 0.3, '• 大孔/小孔', fontsize=9)
    ax3.text(0.5, 0.2, '• 管嘴', fontsize=9)
    ax3.axis('off')
    ax3.set_title('(c) 孔口', fontsize=12, fontweight='bold')
    
    # 子图4：流量对比
    ax4 = axes[1, 0]
    H_range = np.linspace(1, 5, 30)
    Q_weir = [weir_flow(0.5, 10, h) for h in H_range]
    Q_gate = [gate_flow(0.65, 10, 2, h) for h in H_range]
    Q_orifice = [orifice_flow(0.62, 4, h) for h in H_range]
    
    ax4.plot(H_range, Q_weir, 'b-', linewidth=2, label='堰流')
    ax4.plot(H_range, Q_gate, 'r-', linewidth=2, label='闸孔')
    ax4.plot(H_range, Q_orifice, 'g-', linewidth=2, label='孔口')
    ax4.set_xlabel('水头 H (m)', fontsize=12)
    ax4.set_ylabel('流量 Q (m³/s)', fontsize=12)
    ax4.set_title('流量-水头关系对比', fontsize=13, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    # 子图5：流量系数对比
    ax5 = axes[1, 1]
    structures = ['薄壁堰', '实用堰', '闸孔', '孔口', '管嘴']
    coeffs = [0.42, 0.5, 0.65, 0.62, 0.82]
    colors = ['skyblue', 'lightblue', 'orange', 'lightgreen', 'pink']
    bars = ax5.bar(structures, coeffs, color=colors, alpha=0.7)
    ax5.set_ylabel('流量系数', fontsize=12)
    ax5.set_title('流量系数对比', fontsize=13, fontweight='bold')
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax5.text(bar.get_x()+bar.get_width()/2, height+0.02, f'{coeffs[i]:.2f}',
                ha='center', va='bottom', fontsize=9)
    ax5.set_ylim([0, 1])
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 子图6：综合对比表
    ax6 = axes[1, 2]
    ax6.axis('off')
    info = """
    【水工建筑物综合对比】
    
    ┌─────────┬──────┬──────┬──────┐
    │ 建筑物   │ 堰流  │ 闸孔  │ 孔口  │
    ├─────────┼──────┼──────┼──────┤
    │公式指数  │ 3/2  │ 1/2  │ 1/2  │
    │流量系数  │0.42  │0.65  │0.62  │
    │可调节性  │ ✗   │ ✓   │ ✗   │
    │淹没影响  │ 大   │ 中   │ 小   │
    │消能要求  │ 高   │ 高   │ 中   │
    └─────────┴──────┴──────┴──────┘
    
    应用场景：
    
    堰流：
      • 溢洪道泄流
      • 自动泄水
      • 高水头
    
    闸孔：
      • 防洪调度
      • 灌溉供水
      • 航运过闸
    
    孔口：
      • 低水头泄流
      • 排沙排污
      • 取水口
    
    设计考虑：
      ✓ 泄流能力
      ✓ 水流条件
      ✓ 调节要求
      ✓ 消能措施
    """
    ax6.text(0.05, 0.95, info, transform=ax6.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"图片已保存：{filename}")
    plt.close()

def main():
    print("="*60)
    print("水工建筑物综合对比")
    print("="*60)
    H = 3
    print(f"\n水头H={H}m时：")
    print(f"堰流：Q={weir_flow(0.5, 10, H):.1f} m³/s")
    print(f"闸孔：Q={gate_flow(0.65, 10, 2, H):.1f} m³/s")
    print(f"孔口：Q={orifice_flow(0.62, 4, H):.1f} m³/s")
    plot_comparison()
    print("\n分析完成！")

if __name__ == "__main__":
    main()
