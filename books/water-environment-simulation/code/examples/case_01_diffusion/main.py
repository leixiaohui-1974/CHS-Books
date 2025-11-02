"""
案例1：污染物在静水中的扩散
Diffusion of Pollutant in Static Water

演示：
1. 1D扩散模型
2. 显式、隐式、Crank-Nicolson三种格式
3. 与解析解对比验证
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.diffusion import Diffusion1D
from utils.plotting import plot_1d_evolution, compare_solutions
from utils.validation import calculate_error, check_stability


def main():
    """主函数"""
    print("=" * 60)
    print("案例1：污染物在静水中的扩散")
    print("=" * 60)
    print()
    
    # 问题参数
    L = 10.0          # 水槽长度 (m)
    T = 100.0         # 模拟时间 (s)
    nx = 100          # 空间网格数
    nt = 1000         # 时间步数
    D = 0.01          # 扩散系数 (m²/s)
    M = 1.0           # 初始投放质量 (kg)
    
    print(f"问题参数:")
    print(f"  水槽长度: L = {L} m")
    print(f"  模拟时间: T = {T} s")
    print(f"  空间网格: nx = {nx}")
    print(f"  时间步数: nt = {nt}")
    print(f"  扩散系数: D = {D} m²/s")
    print(f"  投放质量: M = {M} kg")
    print()
    
    # 创建模型
    model = Diffusion1D(L=L, T=T, nx=nx, nt=nt, D=D)
    
    print(f"网格参数:")
    print(f"  空间步长: dx = {model.dx:.4f} m")
    print(f"  时间步长: dt = {model.dt:.4f} s")
    print(f"  Fourier数: Fo = {model.Fo:.4f}")
    print()
    
    # 检查稳定性
    is_stable, message = check_stability('explicit_diffusion', Fo=model.Fo)
    print("稳定性检查:")
    print(message)
    print()
    
    # 初始条件：中心点脉冲
    x0 = L / 2
    sigma0 = 0.1  # 初始宽度
    C0 = lambda x: M / (sigma0 * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((x - x0) / sigma0)**2)
    
    # ========================================
    # 任务1：显式格式求解
    # ========================================
    print("任务1：显式格式（FTCS）求解")
    print("-" * 60)
    
    model.set_initial_condition(C0)
    model.set_boundary_conditions('dirichlet', 0.0, 0.0)
    
    C_explicit = model.solve_explicit()
    print("✓ 显式格式求解完成")
    print()
    
    # ========================================
    # 任务2：隐式格式求解
    # ========================================
    print("任务2：隐式格式（BTCS）求解")
    print("-" * 60)
    
    model.set_initial_condition(C0)
    model.set_boundary_conditions('dirichlet', 0.0, 0.0)
    
    C_implicit = model.solve_implicit()
    print("✓ 隐式格式求解完成")
    print()
    
    # ========================================
    # 任务3：Crank-Nicolson格式求解
    # ========================================
    print("任务3：Crank-Nicolson格式求解")
    print("-" * 60)
    
    model.set_initial_condition(C0)
    model.set_boundary_conditions('dirichlet', 0.0, 0.0)
    
    C_cn = model.solve_crank_nicolson()
    print("✓ Crank-Nicolson格式求解完成")
    print()
    
    # ========================================
    # 任务4：与解析解对比
    # ========================================
    print("任务4：与解析解对比")
    print("-" * 60)
    
    # 选择一个时刻进行对比（t = T/2）
    t_compare = T / 2
    idx_compare = nt // 2
    
    # 解析解（高斯解）
    t = t_compare
    C_analytical = M / np.sqrt(4 * np.pi * D * t) * np.exp(-(model.x - x0)**2 / (4 * D * t))
    
    # 计算误差
    error_explicit = calculate_error(C_explicit[idx_compare, :], C_analytical, 'L2')
    error_implicit = calculate_error(C_implicit[idx_compare, :], C_analytical, 'L2')
    error_cn = calculate_error(C_cn[idx_compare, :], C_analytical, 'L2')
    
    print(f"L2误差 (t = {t_compare} s):")
    print(f"  显式格式: {error_explicit:.6e}")
    print(f"  隐式格式: {error_implicit:.6e}")
    print(f"  Crank-Nicolson: {error_cn:.6e}")
    print()
    
    # ========================================
    # 绘图
    # ========================================
    print("生成图表...")
    
    # 图1：显式格式演化
    fig1 = plot_1d_evolution(model.x, model.t, C_explicit, 
                              title='扩散过程演化（显式格式）',
                              xlabel='位置 x (m)',
                              ylabel='时间 t (s)',
                              zlabel='浓度 C (kg/m³)')
    plt.savefig('diffusion_explicit_evolution.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: diffusion_explicit_evolution.png")
    
    # 图2：数值解与解析解对比
    fig2 = compare_solutions(model.x, C_explicit[idx_compare, :], C_analytical, 
                             t=t_compare,
                             title='显式格式与解析解对比')
    plt.savefig('diffusion_validation.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: diffusion_validation.png")
    
    # 图3：三种格式对比
    fig3, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 选择几个时刻
    time_indices = [0, nt//4, nt//2, nt-1]
    
    for i, idx in enumerate(time_indices):
        ax = axes[i//2, i%2]
        ax.plot(model.x, C_explicit[idx, :], 'b-', linewidth=2, label='显式')
        ax.plot(model.x, C_implicit[idx, :], 'r--', linewidth=2, label='隐式')
        ax.plot(model.x, C_cn[idx, :], 'g-.', linewidth=2, label='C-N')
        
        # 在t>0时添加解析解
        if idx > 0:
            t_idx = model.t[idx]
            C_ana = M / np.sqrt(4 * np.pi * D * t_idx) * np.exp(
                -(model.x - x0)**2 / (4 * D * t_idx)
            )
            ax.plot(model.x, C_ana, 'k:', linewidth=2, label='解析解')
        
        ax.set_xlabel('位置 x (m)')
        ax.set_ylabel('浓度 C (kg/m³)')
        ax.set_title(f't = {model.t[idx]:.1f} s')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('三种数值格式对比', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('diffusion_scheme_comparison.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: diffusion_scheme_comparison.png")
    
    # ========================================
    # 总结
    # ========================================
    print()
    print("=" * 60)
    print("案例1完成！")
    print("=" * 60)
    print()
    print("主要结论:")
    print("1. 扩散过程使污染物从高浓度区向低浓度区扩散")
    print("2. 浓度峰值随时间降低，污染带宽度增大")
    print("3. 显式格式需要满足 Fo ≤ 0.5 的稳定性条件")
    print("4. 隐式和C-N格式无条件稳定")
    print("5. C-N格式精度最高（二阶时间精度）")
    print()
    print("生成的图表:")
    print("  - diffusion_explicit_evolution.png")
    print("  - diffusion_validation.png")
    print("  - diffusion_scheme_comparison.png")
    print()
    
    plt.show()


if __name__ == '__main__':
    main()
