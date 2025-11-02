"""
案例2：示踪剂在渠道中的对流-扩散
Tracer Transport in Open Channel

演示：
1. 4种数值格式对比（迎风、中心差分、QUICK、Lax-Wendroff）
2. 数值耗散和数值振荡分析
3. 稳定性条件验证
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.advection_diffusion import AdvectionDiffusion1D
from utils.plotting import plot_1d_evolution, plot_scheme_comparison
from utils.validation import calculate_error, check_stability


def main():
    """主函数"""
    print("=" * 70)
    print("案例2：示踪剂在渠道中的对流-扩散")
    print("=" * 70)
    print()
    
    # 问题参数
    L = 100.0         # 渠道长度 (m)
    T = 150.0         # 模拟时间 (s)
    nx = 200          # 空间网格数
    nt = 3000         # 时间步数
    u = 0.5           # 流速 (m/s)
    D = 0.1           # 扩散系数 (m²/s)
    
    print(f"问题参数:")
    print(f"  渠道长度: L = {L} m")
    print(f"  模拟时间: T = {T} s")
    print(f"  空间网格: nx = {nx}")
    print(f"  时间步数: nt = {nt}")
    print(f"  流速: u = {u} m/s")
    print(f"  扩散系数: D = {D} m²/s")
    print()
    
    # 创建模型
    model = AdvectionDiffusion1D(L=L, T=T, nx=nx, nt=nt, u=u, D=D)
    
    print(f"网格参数:")
    print(f"  空间步长: dx = {model.dx:.4f} m")
    print(f"  时间步长: dt = {model.dt:.4f} s")
    print()
    
    print(f"无量纲数:")
    print(f"  Peclet数: Pe = {model.Pe:.2f}")
    print(f"  Courant数: Cr = {model.Cr:.4f}")
    print(f"  Fourier数: Fo = {model.Fo:.4f}")
    print()
    
    # 分析无量纲数
    if model.Pe < 1:
        print("  → 扩散主导")
    elif model.Pe > 10:
        print("  → 对流主导")
    else:
        print("  → 对流-扩散平衡")
    print()
    
    # 初始条件：上游脉冲
    x0 = 10.0  # 投放位置
    sigma0 = 1.0  # 初始宽度
    M = 1.0  # 总质量
    C0 = lambda x: M / (sigma0 * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((x - x0) / sigma0)**2)
    
    # 边界条件：左侧流入浓度为0，右侧自然流出
    bc_left = 0.0
    bc_right = None  # 自然流出
    
    # ========================================
    # 任务1：迎风格式
    # ========================================
    print("任务1：迎风格式（Upwind）求解")
    print("-" * 70)
    
    # 检查稳定性
    is_stable, message = check_stability('upwind', Cr=model.Cr, Fo=model.Fo)
    print("稳定性检查:")
    print(message)
    print()
    
    model.set_initial_condition(C0)
    model.set_boundary_conditions(bc_left, bc_right)
    
    C_upwind = model.solve_upwind()
    print("✓ 迎风格式求解完成")
    print(f"  最终最大浓度: {np.max(C_upwind[-1, :]):.6f}")
    print()
    
    # ========================================
    # 任务2：中心差分格式
    # ========================================
    print("任务2：中心差分格式（Central）求解")
    print("-" * 70)
    
    # 检查稳定性和振荡
    is_stable, message = check_stability('central', Cr=model.Cr, Fo=model.Fo, Pe=model.Pe)
    print("稳定性检查:")
    print(message)
    print()
    
    model.set_initial_condition(C0)
    model.set_boundary_conditions(bc_left, bc_right)
    
    C_central = model.solve_central()
    print("✓ 中心差分格式求解完成")
    print(f"  最终最大浓度: {np.max(C_central[-1, :]):.6f}")
    print(f"  最终最小浓度: {np.min(C_central[-1, :]):.6f}")
    if np.min(C_central[-1, :]) < -0.01:
        print("  ⚠️  出现负浓度（非物理振荡）！")
    print()
    
    # ========================================
    # 任务3：QUICK格式
    # ========================================
    print("任务3：QUICK格式求解")
    print("-" * 70)
    
    model.set_initial_condition(C0)
    model.set_boundary_conditions(bc_left, bc_right)
    
    C_quick = model.solve_quick()
    print("✓ QUICK格式求解完成")
    print(f"  最终最大浓度: {np.max(C_quick[-1, :]):.6f}")
    print()
    
    # ========================================
    # 任务4：Lax-Wendroff格式
    # ========================================
    print("任务4：Lax-Wendroff格式求解")
    print("-" * 70)
    
    # 检查稳定性
    is_stable_lw = model.Cr**2 <= 2*model.Fo
    print(f"稳定性条件: Cr² ≤ 2*Fo")
    print(f"  Cr² = {model.Cr**2:.4f}")
    print(f"  2*Fo = {2*model.Fo:.4f}")
    if is_stable_lw:
        print(f"  ✓ 满足稳定性条件")
    else:
        print(f"  ⚠️  不满足稳定性条件")
    print()
    
    model.set_initial_condition(C0)
    model.set_boundary_conditions(bc_left, bc_right)
    
    C_lw = model.solve_lax_wendroff()
    print("✓ Lax-Wendroff格式求解完成")
    print(f"  最终最大浓度: {np.max(C_lw[-1, :]):.6f}")
    print()
    
    # ========================================
    # 任务5：结果对比分析
    # ========================================
    print("任务5：结果对比分析")
    print("-" * 70)
    
    # 选择几个时刻进行对比
    t_indices = [nt//4, nt//2, 3*nt//4, nt-1]
    
    for idx in t_indices:
        t = model.t[idx]
        print(f"\nt = {t:.1f} s:")
        
        # 峰值位置和大小
        peak_upwind = np.max(C_upwind[idx, :])
        peak_central = np.max(C_central[idx, :])
        peak_quick = np.max(C_quick[idx, :])
        peak_lw = np.max(C_lw[idx, :])
        
        pos_upwind = model.x[np.argmax(C_upwind[idx, :])]
        pos_central = model.x[np.argmax(C_central[idx, :])]
        pos_quick = model.x[np.argmax(C_quick[idx, :])]
        pos_lw = model.x[np.argmax(C_lw[idx, :])]
        
        print(f"  迎风格式:    峰值 = {peak_upwind:.4f}, 位置 = {pos_upwind:.2f} m")
        print(f"  中心差分:    峰值 = {peak_central:.4f}, 位置 = {pos_central:.2f} m")
        print(f"  QUICK:       峰值 = {peak_quick:.4f}, 位置 = {pos_quick:.2f} m")
        print(f"  Lax-Wendroff: 峰值 = {peak_lw:.4f}, 位置 = {pos_lw:.2f} m")
        
        # 理论峰值位置（对流为主时）
        x_theory = x0 + u * t
        print(f"  理论位置:    {x_theory:.2f} m")
    
    # ========================================
    # 绘图
    # ========================================
    print("\n生成图表...")
    
    # 图1：4种格式对比（选定时刻）
    fig1, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    schemes = {
        '迎风': C_upwind,
        '中心差分': C_central,
        'QUICK': C_quick,
        'Lax-Wendroff': C_lw
    }
    
    colors = {'迎风': 'b', '中心差分': 'r', 'QUICK': 'g', 'Lax-Wendroff': 'm'}
    
    time_indices = [nt//4, nt//2, 3*nt//4, nt-1]
    
    for i, idx in enumerate(time_indices):
        ax = axes[i]
        for label, C in schemes.items():
            ax.plot(model.x, C[idx, :], linewidth=2, label=label, color=colors[label])
        
        # 理论峰值位置
        x_theory = x0 + u * model.t[idx]
        ax.axvline(x=x_theory, color='k', linestyle='--', linewidth=1, 
                   label=f'理论位置 ({x_theory:.1f}m)')
        
        ax.set_xlabel('位置 x (m)', fontsize=11)
        ax.set_ylabel('浓度 C (kg/m³)', fontsize=11)
        ax.set_title(f't = {model.t[idx]:.1f} s', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, L])
    
    plt.suptitle('对流-扩散：四种数值格式对比', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('advection_diffusion_comparison.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: advection_diffusion_comparison.png")
    
    # 图2：数值耗散分析（迎风 vs QUICK）
    fig2, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for i, idx in enumerate(time_indices):
        ax = axes[i]
        ax.plot(model.x, C_upwind[idx, :], 'b-', linewidth=2, label='迎风（一阶，耗散大）')
        ax.plot(model.x, C_quick[idx, :], 'g-', linewidth=2, label='QUICK（三阶，耗散小）')
        
        # 标注峰值
        peak_upwind = np.max(C_upwind[idx, :])
        peak_quick = np.max(C_quick[idx, :])
        dissipation = (peak_quick - peak_upwind) / peak_quick * 100
        
        ax.text(0.05, 0.95, f'峰值降低: {dissipation:.1f}%',
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel('位置 x (m)', fontsize=11)
        ax.set_ylabel('浓度 C (kg/m³)', fontsize=11)
        ax.set_title(f't = {model.t[idx]:.1f} s', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, L])
    
    plt.suptitle('数值耗散分析：迎风格式 vs QUICK格式', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('numerical_dissipation.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: numerical_dissipation.png")
    
    # 图3：数值振荡分析（中心差分）
    fig3, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for i, idx in enumerate(time_indices):
        ax = axes[i]
        ax.plot(model.x, C_central[idx, :], 'r-', linewidth=2, label='中心差分')
        ax.plot(model.x, C_quick[idx, :], 'g--', linewidth=2, label='QUICK（参考）')
        ax.axhline(y=0, color='k', linestyle=':', linewidth=1)
        
        # 检查负值
        min_val = np.min(C_central[idx, :])
        if min_val < 0:
            ax.text(0.05, 0.05, f'⚠️ 最小值: {min_val:.4f} (非物理)',
                    transform=ax.transAxes, color='red',
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
        
        ax.set_xlabel('位置 x (m)', fontsize=11)
        ax.set_ylabel('浓度 C (kg/m³)', fontsize=11)
        ax.set_title(f't = {model.t[idx]:.1f} s', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, L])
    
    plt.suptitle(f'数值振荡分析：中心差分格式 (Pe = {model.Pe:.1f})', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('numerical_oscillation.png', dpi=150, bbox_inches='tight')
    print("  ✓ 已保存: numerical_oscillation.png")
    
    # ========================================
    # 总结
    # ========================================
    print()
    print("=" * 70)
    print("案例2完成！")
    print("=" * 70)
    print()
    print("主要结论:")
    print("1. 对流-扩散过程包含污染物的输送和扩散")
    print("2. 迎风格式稳定但数值耗散大（峰值降低）")
    print("3. 中心差分格式精度高但可能产生振荡（Pe > 2时）")
    print("4. QUICK格式精度高且耗散小，接近真实解")
    print("5. Lax-Wendroff格式二阶精度，表现良好")
    print()
    print("数值格式选择建议:")
    print("  - Pe < 2: 可用中心差分")
    print("  - Pe > 2: 建议用迎风或QUICK")
    print("  - 高精度要求: 使用QUICK或Lax-Wendroff")
    print("  - 快速计算: 使用迎风格式")
    print()
    print("生成的图表:")
    print("  - advection_diffusion_comparison.png  (4种格式对比)")
    print("  - numerical_dissipation.png           (数值耗散分析)")
    print("  - numerical_oscillation.png           (数值振荡分析)")
    print()
    
    plt.show()


if __name__ == '__main__':
    main()
