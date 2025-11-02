"""
案例4：瞬态地下水流动
=======================

学习目标：
1. 理解瞬态渗流方程
2. 掌握时间离散方法（隐式/显式）
3. 学习储水系数的作用
4. 模拟抽水试验
5. 分析降落漏斗的演化

问题描述：
一个矩形承压含水层，初始水头均匀分布为15m。
在t=0时刻开始在中心位置抽水，观察水位随时间的变化。

参数：
- 尺寸：Lx = 1000 m, Ly = 800 m
- 水力传导度：K = 10 m/day
- 储水系数：S = 0.001
- 初始水头：h0 = 15 m
- 边界条件：四周固定水头 h = 15 m
- 抽水量：Q = 100 m³/day

理论基础：
二维瞬态渗流方程：
    S * ∂h/∂t = ∂/∂x(K * ∂h/∂x) + ∂/∂y(K * ∂h/∂y) + Q

对于均质含水层：
    S * ∂h/∂t = K * (∂²h/∂x² + ∂²h/∂y²) + Q
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.abspath('../../..'))

from gwflow.solvers.transient import solve_2d_transient_gw, compute_drawdown
from gwflow.grid.structured import create_2d_grid
from gwflow.visualization.plots import plot_2d_head, plot_transient_animation


def theis_solution(r: float, t: float, T: float, S: float, Q: float) -> float:
    """
    Theis解析解（承压含水层）
    
    参数：
        r: 距抽水井的径向距离 [m]
        t: 时间 [day]
        T: 导水系数 [m²/day] (T = K * b, b为含水层厚度)
        S: 储水系数 [-]
        Q: 抽水量 [m³/day]
    
    返回：
        s: 降深 [m]
    """
    from scipy.special import expi
    
    if t <= 0 or r <= 0:
        return 0.0
    
    u = r**2 * S / (4 * T * t)
    
    # W(u) = -Ei(-u)
    W_u = -expi(-u)
    
    # 降深公式
    s = Q / (4 * np.pi * T) * W_u
    
    return s


def main():
    """主函数"""
    print("=" * 60)
    print("案例4：瞬态地下水流动")
    print("=" * 60)
    
    # ========== 第1步：定义问题参数 ==========
    print("\n第1步：定义问题参数")
    print("-" * 60)
    
    K = 10.0       # 水力传导度 [m/day]
    S = 0.001      # 储水系数 [-]
    Lx = 1000.0    # x方向长度 [m]
    Ly = 800.0     # y方向长度 [m]
    nx = 51        # x方向网格数
    ny = 41        # y方向网格数
    
    dt = 0.5       # 时间步长 [day]
    nt = 100       # 时间步数
    total_time = nt * dt
    
    h0 = 15.0      # 初始水头 [m]
    Q_well = 100.0 # 抽水量 [m³/day]
    
    print(f"水力传导度 K = {K} m/day")
    print(f"储水系数 S = {S}")
    print(f"区域尺寸：Lx = {Lx} m, Ly = {Ly} m")
    print(f"网格数量：nx = {nx}, ny = {ny}")
    print(f"时间步长 dt = {dt} day")
    print(f"模拟时长 = {total_time} day")
    print(f"初始水头 h0 = {h0} m")
    print(f"抽水量 Q = {Q_well} m³/day")
    
    # ========== 第2步：创建网格 ==========
    print("\n第2步：创建计算网格")
    print("-" * 60)
    
    X, Y, dx, dy = create_2d_grid(Lx, Ly, nx, ny)
    
    print(f"网格间距：dx = {dx:.2f} m, dy = {dy:.2f} m")
    
    # 检查CFL条件（显式方法稳定性）
    alpha_x = K * dt / (S * dx**2)
    alpha_y = K * dt / (S * dy**2)
    cfl_number = alpha_x + alpha_y
    
    print(f"\nCFL数：{cfl_number:.4f}")
    if cfl_number <= 0.5:
        print("✓ CFL条件满足，显式方法稳定")
    else:
        print("⚠ CFL条件不满足，建议使用隐式方法或减小时间步长")
    
    # ========== 第3步：设置初始条件和边界条件 ==========
    print("\n第3步：设置初始条件和边界条件")
    print("-" * 60)
    
    initial_h = h0 * np.ones((ny, nx))
    
    boundary_conditions = {
        'left': {'type': 'dirichlet', 'value': h0},
        'right': {'type': 'dirichlet', 'value': h0},
        'bottom': {'type': 'dirichlet', 'value': h0},
        'top': {'type': 'dirichlet', 'value': h0}
    }
    
    print(f"初始水头：均匀分布 {h0} m")
    print("边界条件：四周固定水头 15 m")
    
    # ========== 第4步：设置抽水井 ==========
    print("\n第4步：设置抽水井")
    print("-" * 60)
    
    well_i, well_j = ny // 2, nx // 2
    well_x, well_y = X[well_i, well_j], Y[well_i, well_j]
    cell_area = dx * dy
    
    source = np.zeros((nt, ny, nx))
    source[:, well_i, well_j] = -Q_well / cell_area  # 转换为 m/day
    
    print(f"抽水井位置：({well_x:.0f}, {well_y:.0f}) m")
    print(f"网格索引：(i={well_i}, j={well_j})")
    print(f"抽水量：{Q_well} m³/day")
    print(f"源汇项强度：{-Q_well / cell_area:.6f} m/day")
    
    # ========== 第5步：瞬态求解（隐式方法） ==========
    print("\n第5步：瞬态求解（隐式方法）")
    print("-" * 60)
    
    print("正在求解...")
    h_history = solve_2d_transient_gw(
        K, S, Lx, Ly, nx, ny, dt, nt,
        initial_h, boundary_conditions, source=source,
        method='implicit'
    )
    
    print(f"✓ 求解完成")
    print(f"时间步数：{len(h_history)}")
    print(f"最终时刻井处水头：{h_history[-1][well_i, well_j]:.2f} m")
    print(f"最大降深：{(initial_h - h_history[-1]).max():.2f} m")
    
    # ========== 第6步：计算降深 ==========
    print("\n第6步：计算降深")
    print("-" * 60)
    
    drawdown_history = compute_drawdown(h_history, initial_h)
    
    # 选择几个时间点分析
    time_points = [5, 20, 50, 100]  # 时间步索引
    
    print(f"{'时间(day)':>12} {'井处降深(m)':>15} {'最大降深(m)':>15}")
    print("-" * 45)
    for t_idx in time_points:
        t = t_idx * dt
        s_well = drawdown_history[t_idx][well_i, well_j]
        s_max = drawdown_history[t_idx].max()
        print(f"{t:>12.1f} {s_well:>15.4f} {s_max:>15.4f}")
    
    # ========== 第7步：与Theis解对比 ==========
    print("\n第7步：与Theis解析解对比")
    print("-" * 60)
    
    # 沿x方向中心线提取降深
    y_center = ny // 2
    x_line = X[y_center, :]
    
    # 计算距井的径向距离
    r = np.abs(x_line - well_x)
    r[r < dx/2] = dx/2  # 避免在井处r=0
    
    # 选择最后一个时间步
    t_final = nt * dt
    drawdown_numerical = drawdown_history[-1][y_center, :]
    
    # Theis解
    b = 10.0  # 假设含水层厚度10m
    T = K * b
    drawdown_theis = np.array([theis_solution(ri, t_final, T, S, Q_well) for ri in r])
    
    # 计算误差
    # 只在远离边界的区域对比
    inner_mask = (x_line > 200) & (x_line < 800)
    rmse = np.sqrt(np.mean((drawdown_numerical[inner_mask] - 
                            drawdown_theis[inner_mask])**2))
    
    print(f"与Theis解对比（t={t_final} day）：")
    print(f"RMSE（内部区域）：{rmse:.4f} m")
    print(f"井处降深（数值）：{drawdown_numerical[well_j]:.4f} m")
    print(f"井处降深（Theis）：{drawdown_theis[well_j]:.4f} m")
    
    # ========== 第8步：可视化 ==========
    print("\n第8步：可视化结果")
    print("-" * 60)
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 图1：最终时刻的水头分布
    fig1 = plot_2d_head(
        X, Y, h_history[-1],
        title=f"案例4：瞬态模拟最终水头分布 (t={total_time} day)",
        save_path=os.path.join(output_dir, "case_04_final_head.png")
    )
    
    # 图2：最终时刻的降深分布
    fig2 = plot_2d_head(
        X, Y, drawdown_history[-1],
        title=f"案例4：降落漏斗 (t={total_time} day)",
        save_path=os.path.join(output_dir, "case_04_drawdown.png")
    )
    
    # 图3：井处水头随时间变化
    fig3, ax = plt.subplots(figsize=(10, 6))
    time = np.arange(nt + 1) * dt
    h_well = np.array([h[well_i, well_j] for h in h_history])
    
    ax.plot(time, h_well, 'b-', linewidth=2, label='井处水头')
    ax.axhline(y=h0, color='r', linestyle='--', label='初始水头')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('时间 (day)', fontsize=12)
    ax.set_ylabel('水头 (m)', fontsize=12)
    ax.set_title('案例4：抽水井处水头随时间变化', fontsize=14, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_04_well_head_time.png"), dpi=300)
    
    # 图4：降深随时间变化
    fig4, ax = plt.subplots(figsize=(10, 6))
    s_well = np.array([drawdown[well_i, well_j] for drawdown in drawdown_history])
    
    ax.plot(time, s_well, 'b-', linewidth=2, label='数值解')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('时间 (day)', fontsize=12)
    ax.set_ylabel('降深 (m)', fontsize=12)
    ax.set_title('案例4：抽水井处降深随时间变化', fontsize=14, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_04_drawdown_time.png"), dpi=300)
    
    # 图5：降深剖面与Theis解对比
    fig5, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_line, drawdown_numerical, 'b-', linewidth=2, label='数值解',
            marker='o', markersize=4, markevery=5)
    ax.plot(x_line, drawdown_theis, 'r--', linewidth=2, label='Theis解')
    ax.axvline(x=well_x, color='g', linestyle=':', label='抽水井')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('x (m)', fontsize=12)
    ax.set_ylabel('降深 (m)', fontsize=12)
    ax.set_title(f'案例4：降深剖面对比 (t={total_time} day)', fontsize=14, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_04_profile_comparison.png"), dpi=300)
    
    # 图6：多个时刻的降深分布对比
    fig6, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.ravel()
    
    for idx, t_idx in enumerate(time_points):
        t = t_idx * dt
        ax = axes[idx]
        contourf = ax.contourf(X, Y, drawdown_history[t_idx], levels=20, cmap='Reds')
        ax.plot(well_x, well_y, 'k*', markersize=15, label='抽水井')
        ax.set_xlabel('x (m)', fontsize=10)
        ax.set_ylabel('y (m)', fontsize=10)
        ax.set_title(f't = {t:.1f} day', fontsize=12)
        ax.set_aspect('equal')
        plt.colorbar(contourf, ax=ax, label='降深 (m)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_04_multi_time.png"), dpi=300)
    
    print(f"✓ 图形已保存到 {output_dir}/ 目录")
    
    # 图7：动画（可选，如果matplotlib支持）
    try:
        print("\n正在创建动画...")
        anim = plot_transient_animation(
            X, Y, h_history, dt,
            title="案例4：瞬态地下水流动动画",
            save_path=os.path.join(output_dir, "case_04_animation.gif"),
            fps=10
        )
        print("✓ 动画已保存")
    except Exception as e:
        print(f"⚠ 动画创建失败：{e}")
    
    # ========== 总结 ==========
    print("\n" + "=" * 60)
    print("案例4总结")
    print("=" * 60)
    print("✓ 成功求解二维瞬态地下水流动问题")
    print("✓ 掌握了隐式时间离散方法")
    print("✓ 理解了储水系数的作用")
    print("✓ 模拟了抽水试验过程")
    print("✓ 与Theis解析解进行了对比验证")
    print("\n关键收获：")
    print("1. 瞬态问题的时间离散")
    print("2. CFL条件的重要性")
    print("3. 降落漏斗的时空演化")
    print("4. Theis解析解的应用")
    print("5. 瞬态结果的动画可视化")
    print("=" * 60)
    
    plt.show()


if __name__ == "__main__":
    main()
