#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Saint-Venant方程基础（理论展示）"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def plot_saint_venant_concepts(filename='saint_venant_basic.png'):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 子图1：控制体示意
    ax1 = axes[0, 0]
    # 绘制河道控制体
    x = [0, 1, 1, 0, 0]
    y_bottom = [0, 0, 0, 0, 0]
    y_surface = [2, 2.2, 2.2, 2, 2]
    
    ax1.fill_between([0, 1], [0, 0], [2, 2.2], alpha=0.3, color='cyan')
    ax1.plot([0, 1], [2, 2.2], 'b-', linewidth=2, label='自由水面')
    ax1.plot([0, 1], [0, 0], 'brown', linewidth=3, label='河床')
    
    # 箭头表示流速
    ax1.arrow(0.1, 1, 0.15, 0, head_width=0.15, head_length=0.05, 
             fc='red', ec='red', linewidth=2)
    ax1.arrow(0.8, 1.1, 0.15, 0, head_width=0.15, head_length=0.05,
             fc='red', ec='red', linewidth=2)
    ax1.text(0.2, 1.4, 'v', fontsize=12, color='red', fontweight='bold')
    ax1.text(0.9, 1.5, 'v+Δv', fontsize=10, color='red')
    
    ax1.set_xlim([-0.2, 1.3])
    ax1.set_ylim([-0.3, 3])
    ax1.set_xlabel('x', fontsize=12)
    ax1.set_ylabel('z', fontsize=12)
    ax1.set_title('Saint-Venant方程控制体', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 子图2：两个方程
    ax2 = axes[0, 1]
    ax2.axis('off')
    equations = """
    【Saint-Venant方程组】
    
    连续方程（质量守恒）：
    ∂A/∂t + ∂Q/∂x = 0
    
    或：
    ∂h/∂t + ∂(vh)/∂x = 0
    
    
    动量方程（动量守恒）：
    ∂Q/∂t + ∂(Q²/A)/∂x + gA∂h/∂x 
              = gA(S₀ - Sf)
    
    或：
    ∂v/∂t + v∂v/∂x + g∂h/∂x 
              = g(S₀ - Sf)
    
    
    符号：
    A - 过水断面积
    Q - 流量
    h - 水深
    v - 流速
    S₀ - 河床坡度
    Sf - 摩阻坡度
    """
    ax2.text(0.05, 0.95, equations, transform=ax2.transAxes, 
            fontsize=10, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8))
    
    # 子图3：特征线方法
    ax3 = axes[1, 0]
    # x-t平面特征线
    t = np.linspace(0, 10, 50)
    x_C_plus = 2 + (5 + 3) * t  # C+ 特征线
    x_C_minus = 8 + (5 - 3) * t  # C- 特征线
    
    ax3.plot(x_C_plus, t, 'r-', linewidth=2, label='C⁺: dx/dt=v+c')
    ax3.plot(x_C_minus, t, 'b-', linewidth=2, label='C⁻: dx/dt=v-c')
    ax3.set_xlabel('x (距离)', fontsize=12)
    ax3.set_ylabel('t (时间)', fontsize=12)
    ax3.set_title('特征线方法（MOC）', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim([0, 100])
    ax3.set_ylim([0, 10])
    
    # 子图4：简化形式对比
    ax4 = axes[1, 1]
    ax4.axis('off')
    info = """
    【简化形式】
    
    运动波（Kinematic Wave）：
    ∂Q/∂t + c∂Q/∂x = 0
    • 最简单
    • 仅考虑平移
    • c = 波速
    
    扩散波（Diffusion Wave）：
    ∂Q/∂t + c∂Q/∂x = D∂²Q/∂x²
    • 考虑扩散
    • 有削峰展宽
    
    动力波（Dynamic Wave）：
    • 完整Saint-Venant方程
    • 最精确
    • 计算复杂
    
    适用条件：
    运动波：S₀ >> Sf, Fr << 1
    扩散波：S₀ ≈ Sf
    动力波：一般情况
    
    应用：
    • 洪水演进
    • 溃坝波
    • 水锤分析
    • 潮汐模拟
    """
    ax4.text(0.05, 0.95, info, transform=ax4.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"图片已保存：{filename}")
    plt.close()

def main():
    print("="*60)
    print("Saint-Venant方程基础")
    print("="*60)
    print("\nSaint-Venant方程是描述明渠非恒定流的基本方程")
    print("由连续方程和动量方程组成")
    print("求解方法：特征线法、有限差分、有限元等")
    plot_saint_venant_concepts()
    print("\n示意图已生成！")

if __name__ == "__main__":
    main()
