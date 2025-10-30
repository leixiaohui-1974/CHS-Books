"""
案例15：溃坝波计算 - 主程序

问题描述：
某水库大坝突然溃决，研究溃坝波的传播过程。

参数：
- 上游水深 h₀ = 10.0 m
- 下游水深 hd = 2.0 m（湿河床）
- 河道宽度 b = 50.0 m
- 河道长度 L = 10000 m
- 溃坝位置 x_dam = 5000 m
- 河床坡度 S₀ = 0（水平）

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import RectangularChannel
from solvers.saint_venant import SaintVenantSolver
from utils.chinese_font import configure_chinese_font

# 配置中文字体
configure_chinese_font()


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def riemann_solution_dry(x, t, h0, x_dam, g=9.81):
    """
    计算干河床溃坝波的理论解（Riemann问题）

    Args:
        x: 位置数组 (m)
        t: 时间 (s)
        h0: 上游初始水深 (m)
        x_dam: 溃坝位置 (m)
        g: 重力加速度 (m/s²)

    Returns:
        h, v: 水深和流速数组
    """
    if t <= 0:
        # 初始状态
        h = np.where(x < x_dam, h0, 0.0)
        v = np.zeros_like(x)
        return h, v

    c0 = np.sqrt(g * h0)  # 左侧静水区波速

    # 相似变量 ξ = (x - x_dam) / t
    xi = (x - x_dam) / t

    h = np.zeros_like(x)
    v = np.zeros_like(x)

    # 区域1：左侧静水区 (ξ < -c0)
    mask1 = xi < -c0
    h[mask1] = h0
    v[mask1] = 0.0

    # 区域2：膨胀波区 (-c0 < ξ < 2c0)
    mask2 = (xi >= -c0) & (xi <= 2 * c0)
    v[mask2] = (2.0 / 3.0) * (c0 + xi[mask2])
    c = (1.0 / 3.0) * (2 * c0 - xi[mask2])
    h[mask2] = c**2 / g

    # 区域3：右侧干河床 (ξ > 2c0)
    mask3 = xi > 2 * c0
    h[mask3] = 0.0
    v[mask3] = 0.0

    return h, v


def riemann_solution_wet(x, t, h0, hd, x_dam, g=9.81):
    """
    计算湿河床溃坝波的理论解（Riemann问题）

    Args:
        x: 位置数组 (m)
        t: 时间 (s)
        h0: 上游初始水深 (m)
        hd: 下游初始水深 (m)
        x_dam: 溃坝位置 (m)
        g: 重力加速度 (m/s²)

    Returns:
        h, v: 水深和流速数组
    """
    if t <= 0:
        # 初始状态
        h = np.where(x < x_dam, h0, hd)
        v = np.zeros_like(x)
        return h, v

    c0 = np.sqrt(g * h0)  # 左侧静水区波速
    cd = np.sqrt(g * hd)  # 右侧初始波速

    # 计算中间区参数
    v_star = c0 - cd
    c_star = (c0 + cd) / 2.0
    h_star = c_star**2 / g

    # 激波速度（简化公式）
    U = v_star + c_star * np.sqrt((h_star + hd) / (2 * hd))

    # 相似变量 ξ = (x - x_dam) / t
    xi = (x - x_dam) / t

    h = np.zeros_like(x)
    v = np.zeros_like(x)

    # 区域1：左侧静水区 (ξ < -c0)
    mask1 = xi < -c0
    h[mask1] = h0
    v[mask1] = 0.0

    # 区域2：膨胀波区 (-c0 < ξ < v_star - c_star)
    xi2_max = v_star - c_star
    mask2 = (xi >= -c0) & (xi <= xi2_max)
    v[mask2] = (2.0 / 3.0) * (c0 + xi[mask2])
    c = (1.0 / 3.0) * (2 * c0 - xi[mask2])
    h[mask2] = c**2 / g

    # 区域3：中间恒定区 (v_star - c_star < ξ < U)
    mask3 = (xi > xi2_max) & (xi < U)
    h[mask3] = h_star
    v[mask3] = v_star

    # 区域4：激波右侧 (ξ >= U)
    mask4 = xi >= U
    h[mask4] = hd
    v[mask4] = 0.0

    return h, v


def compute_wave_characteristics(h0, hd, g=9.81):
    """计算波的特征参数

    Args:
        h0: 上游水深 (m)
        hd: 下游水深 (m)
        g: 重力加速度 (m/s²)

    Returns:
        dict: 特征参数字典
    """
    c0 = np.sqrt(g * h0)

    if hd == 0:
        # 干河床
        return {
            'type': 'dry',
            'c0': c0,
            'wave_front_speed': 2 * c0,
            'v_max': (2.0 / 3.0) * c0
        }
    else:
        # 湿河床
        cd = np.sqrt(g * hd)
        v_star = c0 - cd
        c_star = (c0 + cd) / 2.0
        h_star = c_star**2 / g
        U = v_star + c_star * np.sqrt((h_star + hd) / (2 * hd))

        return {
            'type': 'wet',
            'c0': c0,
            'cd': cd,
            'v_star': v_star,
            'c_star': c_star,
            'h_star': h_star,
            'shock_speed': U
        }


def main():
    """主函数"""
    print_separator("案例15：溃坝波计算")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】溃坝问题参数")
    print("-" * 80)

    L = 10000.0   # 河道长度 (m)
    b = 50.0      # 河道宽度 (m)
    h0 = 10.0     # 上游初始水深 (m)
    hd = 2.0      # 下游初始水深 (m)
    x_dam = 5000.0  # 溃坝位置 (m)
    S0 = 0.0      # 河床坡度（水平）
    n = 0.0       # 糙率（理论解忽略摩阻）
    g = 9.81

    print(f"河道参数：")
    print(f"  长度 L = {L} m")
    print(f"  宽度 b = {b} m")
    print(f"  坝址位置 = {x_dam} m（河道中部）")
    print(f"  河床坡度 S₀ = {S0}（水平）")

    print(f"\n初始水深：")
    print(f"  上游水深 h₀ = {h0} m")
    print(f"  下游水深 hd = {hd} m")
    print(f"  水深比 h₀/hd = {h0/hd:.2f}")

    # ==================== 第二步：理论解分析 ====================
    print("\n【步骤2】理论解（Riemann问题）")
    print("-" * 80)

    # 计算特征参数
    params = compute_wave_characteristics(h0, hd, g)

    print(f"\n波动特征参数：")
    print(f"  上游波速 c₀ = √(gh₀) = {params['c0']:.3f} m/s")

    if params['type'] == 'dry':
        print(f"\n干河床情况：")
        print(f"  波前速度 = 2c₀ = {params['wave_front_speed']:.3f} m/s")
        print(f"  最大流速 v_max = (2/3)c₀ = {params['v_max']:.3f} m/s")
        print(f"  波前到达下游5km时间 = {5000/params['wave_front_speed']:.1f} s")
    else:
        print(f"  下游波速 cd = √(ghd) = {params['cd']:.3f} m/s")
        print(f"\n湿河床情况（产生激波）：")
        print(f"  中间区水深 h* = {params['h_star']:.3f} m")
        print(f"  中间区流速 v* = {params['v_star']:.3f} m/s")
        print(f"  中间区波速 c* = {params['c_star']:.3f} m/s")
        print(f"  激波传播速度 U = {params['shock_speed']:.3f} m/s")
        print(f"  激波到达下游5km时间 = {5000/params['shock_speed']:.1f} s")

    print(f"\n理论解性质：")
    print(f"  自相似解：h和v仅为ξ=x/t的函数")
    print(f"  膨胀波：连续变化区域")
    if params['type'] == 'wet':
        print(f"  激波（bore）：间断传播")

    # ==================== 第三步：理论解计算 ====================
    print("\n【步骤3】计算理论解的时空分布")
    print("-" * 80)

    # 空间网格
    nx_theory = 1001
    x_theory = np.linspace(0, L, nx_theory)

    # 时间点
    times_theory = [100, 300, 500, 700]  # 秒

    print(f"\n计算设置：")
    print(f"  空间节点数 = {nx_theory}")
    print(f"  计算时刻 = {times_theory} s")

    # 存储理论解
    theory_results = {}
    for t in times_theory:
        h_th, v_th = riemann_solution_wet(x_theory, t, h0, hd, x_dam, g)
        theory_results[t] = {'h': h_th, 'v': v_th}
        h_max = np.max(h_th)
        v_max = np.max(v_th)
        print(f"  t={t}s: h_max={h_max:.2f}m, v_max={v_max:.2f}m/s")

    # ==================== 第四步：数值模拟 ====================
    print("\n【步骤4】数值模拟（Saint-Venant方程）")
    print("-" * 80)

    # 网格设置
    dx = 50.0  # 空间步长 (m)
    nx = int(L / dx) + 1

    print(f"\n数值网格：")
    print(f"  空间步长 Δx = {dx} m")
    print(f"  节点数 nx = {nx}")
    print(f"  时间步长：自动（CFL=0.4）")

    # 创建求解器
    solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None, g=g)

    # 初始条件：溃坝前状态
    h_init = np.zeros(nx)
    Q_init = np.zeros(nx)
    x_grid = solver.x

    # 设置初始水深分布
    for i, xi in enumerate(x_grid):
        if xi < x_dam:
            h_init[i] = h0
        else:
            h_init[i] = hd

    solver.set_initial_conditions(h_init, Q_init)

    print(f"\n初始条件：")
    print(f"  溃坝位置：x = {x_dam} m")
    print(f"  左侧（上游）：h = {h0} m, Q = 0")
    print(f"  右侧（下游）：h = {hd} m, Q = 0")

    # 边界条件：使用外推边界（None）
    solver.set_boundary_conditions(
        upstream=None,  # 外推
        downstream=None  # 外推
    )

    print(f"\n边界条件：")
    print(f"  上游：外推边界（自然边界）")
    print(f"  下游：外推边界（自然边界）")

    # 运行模拟
    t_end = 800.0  # 模拟800秒
    dt_output = 100.0  # 每100秒输出一次

    print(f"\n运行数值模拟...")
    print(f"  模拟时长 = {t_end} s")
    print(f"  输出间隔 = {dt_output} s")

    try:
        results = solver.run(t_end=t_end, dt_output=dt_output, verbose=True)
        print(f"\n计算完成！")
    except Exception as e:
        print(f"\n计算出错：{e}")
        return

    # ==================== 第五步：结果对比 ====================
    print("\n【步骤5】理论解与数值解对比")
    print("-" * 80)

    # 选择几个时刻对比
    compare_times = [300, 500, 700]

    print(f"\n对比时刻：{compare_times} s")
    print(f"\n各时刻波前位置对比：")
    print("-" * 80)
    print(f"{'时间(s)':^10} | {'理论波前位置(m)':^18} | {'数值波前位置(m)':^18} | {'误差(m)':^12}")
    print("-" * 80)

    for t in compare_times:
        # 理论波前位置
        if params['type'] == 'wet':
            x_front_theory = x_dam + params['shock_speed'] * t
        else:
            x_front_theory = x_dam + 2 * params['c0'] * t

        # 数值波前位置（定义为水深超过hd+0.1的最远位置）
        time_idx = np.argmin(np.abs(results['times'] - t))
        h_num = results['h'][time_idx, :]
        mask = h_num > hd + 0.1
        if np.any(mask):
            indices = np.where(mask)[0]
            x_front_num = x_grid[indices[-1]]
        else:
            x_front_num = x_dam

        error = x_front_num - x_front_theory

        print(f"{t:^10.0f} | {x_front_theory:^18.1f} | {x_front_num:^18.1f} | {error:^12.1f}")

    print("-" * 80)

    # ==================== 第六步：绘制结果 ====================
    print("\n【步骤6】绘制结果图形")
    print("-" * 80)

    # 配置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('溃坝波传播分析', fontsize=16, fontweight='bold')

    # 图1：不同时刻的水深分布对比
    ax1 = axes[0, 0]
    for t in [300, 500, 700]:
        # 理论解
        h_th, _ = riemann_solution_wet(x_theory, t, h0, hd, x_dam, g)
        ax1.plot(x_theory/1000, h_th, '--', label=f't={t}s (理论)', linewidth=2, alpha=0.7)

        # 数值解
        time_idx = np.argmin(np.abs(results['times'] - t))
        h_num = results['h'][time_idx, :]
        ax1.plot(x_grid/1000, h_num, '-', label=f't={t}s (数值)', linewidth=2)

    ax1.axvline(x=x_dam/1000, color='r', linestyle=':', alpha=0.5, label='坝址')
    ax1.set_xlabel('距离 (km)', fontsize=12)
    ax1.set_ylabel('水深 (m)', fontsize=12)
    ax1.set_title('水深沿程分布（理论 vs 数值）', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9, ncol=2)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, h0 * 1.1])

    # 图2：流速分布对比
    ax2 = axes[0, 1]
    for t in [300, 500, 700]:
        # 理论解
        _, v_th = riemann_solution_wet(x_theory, t, h0, hd, x_dam, g)
        ax2.plot(x_theory/1000, v_th, '--', label=f't={t}s (理论)', linewidth=2, alpha=0.7)

        # 数值解
        time_idx = np.argmin(np.abs(results['times'] - t))
        v_num = results['v'][time_idx, :]
        ax2.plot(x_grid/1000, v_num, '-', label=f't={t}s (数值)', linewidth=2)

    ax2.axvline(x=x_dam/1000, color='r', linestyle=':', alpha=0.5, label='坝址')
    ax2.set_xlabel('距离 (km)', fontsize=12)
    ax2.set_ylabel('流速 (m/s)', fontsize=12)
    ax2.set_title('流速沿程分布（理论 vs 数值）', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9, ncol=2)
    ax2.grid(True, alpha=0.3)

    # 图3：水深时空分布（数值解）
    ax3 = axes[1, 0]
    T, X = np.meshgrid(results['times'], x_grid/1000)
    levels = np.linspace(0, h0, 20)
    contour = ax3.contourf(T.T, X.T, results['h'], levels=levels, cmap='Blues')
    plt.colorbar(contour, ax=ax3, label='水深 (m)')

    # 叠加理论波前轨迹
    if params['type'] == 'wet':
        t_line = np.linspace(0, t_end, 100)
        x_front_line = (x_dam + params['shock_speed'] * t_line) / 1000
        ax3.plot(t_line, x_front_line, 'r--', linewidth=2, label='理论波前')

    ax3.axhline(y=x_dam/1000, color='k', linestyle=':', alpha=0.5, label='坝址')
    ax3.set_xlabel('时间 (s)', fontsize=12)
    ax3.set_ylabel('距离 (km)', fontsize=12)
    ax3.set_title('水深时空分布（数值解）', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=10)

    # 图4：特征线图（理论解）
    ax4 = axes[1, 1]
    t_char = np.linspace(1, t_end, 20)

    # 膨胀波特征线
    if params['type'] == 'wet':
        # 左侧膨胀波
        for xi_val in np.linspace(-params['c0'], params['v_star'] - params['c_star'], 10):
            x_char = x_dam + xi_val * t_char
            ax4.plot(t_char, x_char/1000, 'b-', alpha=0.5, linewidth=1)

        # 激波轨迹
        x_shock = x_dam + params['shock_speed'] * t_char
        ax4.plot(t_char, x_shock/1000, 'r-', linewidth=3, label='激波')

    ax4.axhline(y=x_dam/1000, color='k', linestyle='--', alpha=0.5, label='坝址')
    ax4.set_xlabel('时间 (s)', fontsize=12)
    ax4.set_ylabel('距离 (km)', fontsize=12)
    ax4.set_title('特征线与波前轨迹', fontsize=13, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('case_15_dam_break.png', dpi=150, bbox_inches='tight')
    print(f"\n图形已保存：case_15_dam_break.png")

    # ==================== 第七步：安全分析 ====================
    print("\n【步骤7】溃坝安全分析")
    print("-" * 80)

    # 危险水深阈值
    h_critical = 2.0  # m

    print(f"\n危险水深阈值：h_crit = {h_critical} m")

    # 分析最终时刻的淹没范围
    h_final = results['h'][-1, :]
    dangerous_mask = h_final > h_critical
    if np.any(dangerous_mask):
        x_danger = x_grid[dangerous_mask]
        danger_range = [x_danger.min(), x_danger.max()]
        danger_length = danger_range[1] - danger_range[0]

        print(f"\n淹没危险区：")
        print(f"  起点：{danger_range[0]:.0f} m")
        print(f"  终点：{danger_range[1]:.0f} m")
        print(f"  长度：{danger_length:.0f} m = {danger_length/1000:.2f} km")
    else:
        print(f"\n未检测到危险区（h > {h_critical}m）")

    # 下游关键点到达时间
    x_checkpoints = [5500, 6000, 7000, 8000, 9000]  # m

    print(f"\n下游关键点波前到达时间：")
    print("-" * 60)
    print(f"{'位置(m)':^12} | {'理论到达时间(s)':^18} | {'预警时间(min)':^15}")
    print("-" * 60)

    for x_check in x_checkpoints:
        if x_check > x_dam:
            distance = x_check - x_dam
            if params['type'] == 'wet':
                t_arrival = distance / params['shock_speed']
            else:
                t_arrival = distance / (2 * params['c0'])

            warning_time = t_arrival / 60  # 转换为分钟

            print(f"{x_check:^12.0f} | {t_arrival:^18.1f} | {warning_time:^15.1f}")

    print("-" * 60)

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
