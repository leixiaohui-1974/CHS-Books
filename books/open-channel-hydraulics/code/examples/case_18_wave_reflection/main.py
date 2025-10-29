"""
案例18：明渠波动与反射 - 主程序

问题描述：
研究闸门扰动产生的波动在封闭端的反射现象。

参数：
- 渠道长度 L = 1000 m
- 渠道宽度 b = 10 m
- 初始水深 h₀ = 3.0 m
- 糙率 n = 0.02
- 扰动振幅 = 0.5 m

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import RectangularChannel
from solvers.saint_venant import SaintVenantSolver


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def main():
    """主函数"""
    print_separator("案例18：明渠波动与反射")

    # ==================== 参数设置 ====================
    L = 1000.0; b = 10.0; h0 = 3.0; n = 0.02; g = 9.81
    disturbance_amplitude = 0.5; disturbance_duration = 10.0

    print(f"\n渠道参数：L={L}m, b={b}m, h₀={h0}m, n={n}")
    print(f"扰动：振幅={disturbance_amplitude}m, 持续时间={disturbance_duration}s")

    # 波速
    c = np.sqrt(g * h0)
    print(f"\n理论波速：c = √(gh₀) = {c:.2f} m/s")
    print(f"往返时间：2L/c = {2*L/c:.0f} s")

    # ==================== 数值模拟 ====================
    dx = 20.0; nx = int(L/dx) + 1
    t_total = 600.0  # 10分钟

    solver = SaintVenantSolver(L=L, b=b, S0=0.0, n=n, dx=dx, dt=None, g=g)

    # 初始条件：静水
    h_init = np.full(nx, h0)
    Q_init = np.zeros(nx)
    solver.set_initial_conditions(h_init, Q_init)

    # 边界条件
    def bc_upstream(t):
        """上游：水位脉冲扰动"""
        if t < disturbance_duration:
            h = h0 + disturbance_amplitude * np.sin(np.pi * t / disturbance_duration)
        else:
            h = h0
        return h, 0.0

    def bc_downstream(t):
        """下游：封闭端（零流量）

        封闭端边界条件：
        - 流量Q = 0（刚性边界）
        - 水深由动量方程确定，这里简化为保持初始水深
        """
        return h0, 0.0

    solver.set_boundary_conditions(bc_upstream, bc_downstream)

    print(f"\n开始模拟...")
    results = solver.run(t_end=t_total, dt_output=5.0, verbose=False)
    print(f"完成！时间步数：{solver.time_step}")

    # ==================== 分析 ====================
    times = results['times']
    h_results = results['h']
    x_grid = results['x']

    # 计算水位扰动
    eta = h_results - h0

    # 找到最大扰动位置和时刻
    eta_max = np.max(np.abs(eta))
    idx_max = np.unravel_index(np.argmax(np.abs(eta)), eta.shape)

    print(f"\n最大扰动：{eta_max:.3f}m")
    print(f"发生位置：x={x_grid[idx_max[1]]:.0f}m")
    print(f"发生时刻：t={times[idx_max[0]]:.0f}s")

    # ==================== 绘图 ====================
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('明渠波动与反射', fontsize=16, fontweight='bold')

    # 图1：不同时刻的水位分布
    ax1 = axes[0, 0]
    for i in [5, 20, 40, 60, 80]:
        if i < len(times):
            ax1.plot(x_grid, h_results[i,:], label=f't={times[i]:.0f}s')
    ax1.axhline(y=h0, color='k', linestyle='--', alpha=0.3)
    ax1.set_xlabel('距离 (m)'); ax1.set_ylabel('水位 (m)')
    ax1.set_title('水位沿程分布'); ax1.legend(); ax1.grid(True, alpha=0.3)

    # 图2：特定位置水位时程
    ax2 = axes[0, 1]
    for idx in [0, nx//4, nx//2, 3*nx//4, nx-1]:
        ax2.plot(times, h_results[:,idx], label=f'x={x_grid[idx]:.0f}m')
    ax2.axhline(y=h0, color='k', linestyle='--', alpha=0.3)
    ax2.set_xlabel('时间 (s)'); ax2.set_ylabel('水位 (m)')
    ax2.set_title('各位置水位变化'); ax2.legend(); ax2.grid(True, alpha=0.3)

    # 图3：水位扰动时空图
    ax3 = axes[1, 0]
    T, X = np.meshgrid(times, x_grid)
    c = ax3.contourf(T.T, X.T, eta, levels=20, cmap='RdBu_r')
    plt.colorbar(c, ax=ax3, label='水位扰动 (m)')
    ax3.set_xlabel('时间 (s)'); ax3.set_ylabel('距离 (m)')
    ax3.set_title('水位扰动时空分布')

    # 图4：能量时程
    ax4 = axes[1, 1]
    energy = np.sum(0.5 * g * eta**2 * dx, axis=1)
    ax4.plot(times, energy/energy[10], 'b-', linewidth=2)
    ax4.set_xlabel('时间 (s)'); ax4.set_ylabel('相对能量')
    ax4.set_title('波动能量变化'); ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('case_18_wave_reflection.png', dpi=150, bbox_inches='tight')
    print(f"\n图形已保存：case_18_wave_reflection.png")

    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
