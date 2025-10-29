"""
案例13：明渠非恒定流基础 - 计算实验

实验内容：
1. 实验13.1：CFL条件对稳定性的影响
2. 实验13.2：流量变化幅度对波传播的影响
3. 实验13.3：河道糙率对波速的影响

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
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


def experiment_13_1():
    """实验13.1：CFL条件对稳定性的影响"""
    print_separator("实验13.1：CFL条件对稳定性的影响")

    # 基准参数
    L = 10000.0
    b = 20.0
    S0 = 0.0002
    n = 0.025
    Q0 = 100.0
    Q1 = 150.0
    g = 9.81

    # 计算初始正常水深
    channel = RectangularChannel(b=b, S0=S0, n=n)
    h0 = channel.compute_normal_depth(Q0)
    h1 = channel.compute_normal_depth(Q1)
    v0 = Q0 / (b * h0)
    c0 = np.sqrt(g * h0)

    print(f"\n固定参数：L={L}m, b={b}m, Q₀={Q0}m³/s→Q₁={Q1}m³/s")
    print(f"波速：c≈{c0:.2f} m/s, 理论dt_max={0.9*100/c0:.2f}s")

    dx = 100.0

    # 测试不同的Courant数
    cfl_values = [0.3, 0.5, 0.7, 0.9, 1.0, 1.2]

    print("\n不同Courant数的计算稳定性：")
    print("-" * 110)
    print(f"{'Courant数':^12} | {'时间步dt(s)':^14} | {'计算状态':^12} | "
          f"{'完成时间(s)':^14} | {'步数':^10} | {'稳定性评价':^20}")
    print("-" * 110)

    for cfl in cfl_values:
        dt = cfl * dx / (v0 + c0)

        try:
            solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=dt, g=g)
            solver.set_uniform_initial(h0=h0, Q0=Q0)

            def bc_up(t):
                return (h1 if t >= 0 else h0), (Q1 if t >= 0 else Q0)

            def bc_down(t):
                return h0, Q0

            solver.set_boundary_conditions(bc_up, bc_down)

            # 短时间模拟测试稳定性
            results = solver.run(t_end=600.0, dt_output=600.0, verbose=False)

            status = "成功"
            t_comp = results['times'][-1]
            n_steps = solver.time_step

            # 检查是否有异常值
            if np.any(np.isnan(results['h'])) or np.any(np.isinf(results['h'])):
                status = "发散（NaN）"
                evaluation = "不稳定"
            elif np.max(results['h']) > 10 * h0:
                status = "发散（爆炸）"
                evaluation = "不稳定"
            elif cfl > 1.0:
                evaluation = "违反CFL"
            elif cfl < 0.5:
                evaluation = "过分保守"
            else:
                evaluation = "稳定（推荐）"

        except Exception as e:
            status = f"失败"
            t_comp = 0
            n_steps = 0
            evaluation = "不稳定"

        print(f"{cfl:^12.2f} | {dt:^14.3f} | {status:^12} | "
              f"{t_comp:^14.1f} | {n_steps:^10} | {evaluation:^20}")

    print("-" * 110)

    print("\n【实验结论】")
    print("1. Courant数必须 ≤ 1.0 才能保证稳定")
    print("2. Cr > 1.0 导致计算发散")
    print("3. 推荐 Cr = 0.5-0.8（稳定且高效）")
    print("4. Cr 过小导致时间步太小，计算耗时")
    print("5. CFL条件是显式格式的必要条件")


def experiment_13_2():
    """实验13.2：流量变化幅度对波传播的影响"""
    print_separator("实验13.2：流量变化幅度对波传播的影响")

    L = 10000.0
    b = 20.0
    S0 = 0.0002
    n = 0.025
    Q0 = 100.0
    g = 9.81
    dx = 100.0

    channel = RectangularChannel(b=b, S0=S0, n=n)
    h0 = channel.compute_normal_depth(Q0)

    print(f"\n固定参数：Q₀={Q0}m³/s")
    print("变化参数：上游增加流量Q₁")

    # 不同的流量增幅
    Q1_values = [110, 120, 130, 150, 180, 200]

    print("\n流量变化对波传播的影响：")
    print("-" * 120)
    print(f"{'上游流量Q₁':^13} | {'增幅(%)':^10} | {'水深增加(m)':^14} | "
          f"{'波速(m/s)':^12} | {'到达时间(min)':^16} | {'峰值衰减(%)':^14}")
    print("-" * 120)

    for Q1 in Q1_values:
        h1 = channel.compute_normal_depth(Q1)
        increase_pct = (Q1 - Q0) / Q0 * 100

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None, g=g)
        solver.set_uniform_initial(h0=h0, Q0=Q0)

        def bc_up(t):
            return (h1 if t >= 0 else h0), (Q1 if t >= 0 else Q0)

        def bc_down(t):
            return h0, Q0

        solver.set_boundary_conditions(bc_up, bc_down)

        results = solver.run(t_end=3600.0, dt_output=300.0, verbose=False)

        # 分析结果
        h_increase = np.max(results['h']) - h0
        Q_down = results['Q'][:, -1]

        # 波到达时间
        Q_threshold = Q0 + 0.5 * (Q1 - Q0)
        arrival_idx = np.where(Q_down > Q_threshold)[0]
        if len(arrival_idx) > 0:
            t_arrival = results['times'][arrival_idx[0]]
            wave_speed = L / t_arrival
        else:
            t_arrival = np.nan
            wave_speed = np.nan

        # 峰值衰减
        Q_max_down = np.max(Q_down)
        if Q_max_down > Q0:
            attenuation = (Q1 - Q_max_down) / (Q1 - Q0) * 100
        else:
            attenuation = 100.0

        print(f"{Q1:^13.0f} | {increase_pct:^10.0f} | {h_increase:^14.4f} | "
              f"{wave_speed:^12.2f} | {t_arrival/60:^16.1f} | {attenuation:^14.1f}")

    print("-" * 120)

    print("\n【实验结论】")
    print("1. 流量增幅越大，水深增加越多")
    print("2. 波速随流量增大而略有增加")
    print("3. 峰值衰减随流量增大而增大")
    print("4. 河道蓄水作用明显")
    print("5. 大流量变化时非线性效应显著")


def experiment_13_3():
    """实验13.3：河道糙率对波速的影响"""
    print_separator("实验13.3：河道糙率对波速的影响")

    L = 10000.0
    b = 20.0
    S0 = 0.0002
    Q0 = 100.0
    Q1 = 150.0
    g = 9.81
    dx = 100.0

    print(f"\n固定参数：L={L}m, Q₀={Q0}→Q₁={Q1}m³/s")
    print("变化参数：糙率n")

    # 不同糙率
    n_values = [0.015, 0.020, 0.025, 0.030, 0.035, 0.040]
    n_conditions = [
        "光滑混凝土",
        "一般混凝土",
        "天然河道（清洁）",
        "天然河道（一般）",
        "有植被",
        "植被茂密"
    ]

    print("\n糙率对波传播的影响：")
    print("-" * 130)
    print(f"{'糙率n':^10} | {'河床状况':^20} | {'初始水深(m)':^14} | "
          f"{'波速(m/s)':^12} | {'到达时间(min)':^16} | {'峰值衰减(%)':^14}")
    print("-" * 130)

    for n, condition in zip(n_values, n_conditions):
        channel = RectangularChannel(b=b, S0=S0, n=n)
        h0 = channel.compute_normal_depth(Q0)
        h1 = channel.compute_normal_depth(Q1)

        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None, g=g)
        solver.set_uniform_initial(h0=h0, Q0=Q0)

        def bc_up(t):
            return (h1 if t >= 0 else h0), (Q1 if t >= 0 else Q0)

        def bc_down(t):
            return h0, Q0

        solver.set_boundary_conditions(bc_up, bc_down)

        results = solver.run(t_end=3600.0, dt_output=300.0, verbose=False)

        # 分析
        Q_down = results['Q'][:, -1]
        Q_threshold = Q0 + 0.5 * (Q1 - Q0)
        arrival_idx = np.where(Q_down > Q_threshold)[0]

        if len(arrival_idx) > 0:
            t_arrival = results['times'][arrival_idx[0]]
            wave_speed = L / t_arrival
        else:
            t_arrival = np.nan
            wave_speed = np.nan

        Q_max_down = np.max(Q_down)
        attenuation = (Q1 - Q_max_down) / (Q1 - Q0) * 100

        print(f"{n:^10.3f} | {condition:^20} | {h0:^14.4f} | "
              f"{wave_speed:^12.2f} | {t_arrival/60:^16.1f} | {attenuation:^14.1f}")

    print("-" * 130)

    print("\n【实验结论】")
    print("1. 糙率增大，初始水深增大")
    print("2. 糙率对波速影响相对较小")
    print("3. 糙率增大导致更大的峰值衰减")
    print("4. 摩阻作用消耗洪水能量")
    print("5. 实际应用需准确率定糙率")


def main():
    """主函数"""
    print_separator("案例13：计算实验")
    print("\n本实验将探讨非恒定流的关键影响因素\n")

    experiment_13_1()  # CFL条件影响
    experiment_13_2()  # 流量变化影响
    experiment_13_3()  # 糙率影响

    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. CFL条件：数值稳定性的必要条件")
    print("2. 流量变化：影响波速、水深和衰减")
    print("3. 河道糙率：影响水深和峰值衰减")
    print("\nSaint-Venant方程数值求解需要：")
    print("- 满足CFL条件保证稳定性")
    print("- 合理的空间和时间离散")
    print("- 准确的物理参数（糙率、断面）")
    print("- 可靠的边界条件")
    print_separator()


if __name__ == "__main__":
    main()
