"""
案例17：潮汐河口非恒定流 - 计算实验

实验内容：
1. 实验17.1：潮汐振幅的影响
2. 实验17.2：径流量的影响
3. 实验17.3：河口长度的影响

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


def tidal_elevation(t, h0, A, T, phi=0):
    """计算潮汐水位"""
    omega = 2 * np.pi / T
    return h0 + A * np.sin(omega * t + phi)


def run_tidal_simulation(L, b, S0, n, Qr, h0_tide, A_tide, T_tide,
                         t_total, dx=1000.0, dt_output=3600.0, g=9.81):
    """
    运行潮汐河口模拟

    Args:
        L: 河道长度 (m)
        b: 河道宽度 (m)
        S0: 河道坡度
        n: 糙率
        Qr: 上游径流 (m³/s)
        h0_tide: 平均潮位 (m)
        A_tide: 潮汐振幅 (m)
        T_tide: 潮汐周期 (s)
        t_total: 模拟时长 (s)
        dx: 空间步长 (m)
        dt_output: 输出间隔 (s)
        g: 重力加速度 (m/s²)

    Returns:
        results: 模拟结果字典
    """
    channel = RectangularChannel(b=b, S0=S0, n=n)
    nx = int(L / dx) + 1
    solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None, g=g)

    # 初始条件
    h_init = h0_tide
    h_init_array = np.full(nx, h_init)
    Q_init_array = np.full(nx, Qr)
    solver.set_initial_conditions(h_init_array, Q_init_array)

    # 边界条件
    def bc_upstream(t):
        Q = Qr
        h = channel.compute_normal_depth(Q) if Q > 0.1 else h_init
        return h, Q

    def bc_downstream(t):
        h_tide = tidal_elevation(t, h0_tide, A_tide, T_tide, phi=0)
        Q_down = Qr * 0.8
        return h_tide, Q_down

    solver.set_boundary_conditions(upstream=bc_upstream, downstream=bc_downstream)

    # 运行模拟
    try:
        results = solver.run(t_end=t_total, dt_output=dt_output, verbose=False)
        return results
    except Exception as e:
        print(f"    模拟出错：{e}")
        return None


def analyze_tidal_range(results, x_grid):
    """分析潮差分布"""
    if results is None:
        return None, None

    h_results = results['h']

    # 计算每个位置的潮差
    tidal_ranges = []
    for i in range(len(x_grid)):
        h_series = h_results[:, i]
        tidal_range = np.max(h_series) - np.min(h_series)
        tidal_ranges.append(tidal_range)

    # 河口和上游潮差
    tidal_range_mouth = tidal_ranges[0]
    tidal_range_upstream = tidal_ranges[-1]

    return tidal_range_mouth, tidal_range_upstream


def experiment_17_1():
    """实验17.1：潮汐振幅的影响"""
    print_separator("实验17.1：潮汐振幅的影响")

    L = 20000.0
    b = 200.0
    S0 = 0.00005
    n = 0.03
    Qr = 500.0
    h0_tide = 5.0
    T_tide = 12.42 * 3600
    t_total = 1.5 * T_tide

    # 不同的潮汐振幅
    amplitudes = [0.5, 1.0, 1.5, 2.0, 2.5]  # m

    print(f"\n固定参数：L={L/1000}km, Qr={Qr}m³/s, T={T_tide/3600:.1f}h")
    print("变化参数：潮汐振幅A")

    print(f"\n潮汐振幅对传播的影响：")
    print("-" * 100)
    print(f"{'潮汐振幅(m)':^14} | {'河口潮差(m)':^14} | {'上游潮差(m)':^14} | {'衰减率(%)':^12}")
    print("-" * 100)

    for A in amplitudes:
        results = run_tidal_simulation(L, b, S0, n, Qr, h0_tide, A, T_tide, t_total)

        if results is not None:
            x_grid = results['x']
            tidal_range_mouth, tidal_range_upstream = analyze_tidal_range(results, x_grid)

            attenuation = (1 - tidal_range_upstream / tidal_range_mouth) * 100 if tidal_range_mouth > 0.01 else 0

            print(f"{A:^14.1f} | {tidal_range_mouth:^14.3f} | {tidal_range_upstream:^14.3f} | {attenuation:^12.1f}")

    print("-" * 100)

    print(f"\n【实验结论】")
    print("1. 潮汐振幅越大，潮差传播越远")
    print("2. 衰减率相对稳定（主要取决于摩阻）")
    print("3. 大潮差下潮汐影响范围更大")
    print("4. 小振幅潮汐衰减较快")


def experiment_17_2():
    """实验17.2：径流量的影响"""
    print_separator("实验17.2：径流量的影响")

    L = 20000.0
    b = 200.0
    S0 = 0.00005
    n = 0.03
    h0_tide = 5.0
    A_tide = 2.0
    T_tide = 12.42 * 3600
    t_total = 1.5 * T_tide
    g = 9.81

    # 不同的径流量
    runoffs = [100, 300, 500, 700, 1000]  # m³/s

    print(f"\n固定参数：L={L/1000}km, A={A_tide}m, T={T_tide/3600:.1f}h")
    print("变化参数：上游径流Qr")

    print(f"\n径流量对潮汐传播的影响：")
    print("-" * 110)
    print(f"{'径流量(m³/s)':^14} | {'径流-潮汐比':^14} | {'上游潮差(m)':^14} | {'流态特征':^16}")
    print("-" * 110)

    c = np.sqrt(g * h0_tide)  # 波速估算

    for Qr in runoffs:
        R_ratio = Qr / (A_tide * b * c)

        results = run_tidal_simulation(L, b, S0, n, Qr, h0_tide, A_tide, T_tide, t_total)

        if results is not None:
            x_grid = results['x']
            _, tidal_range_upstream = analyze_tidal_range(results, x_grid)

            if R_ratio < 0.1:
                regime = "潮汐主导"
            elif R_ratio > 1.0:
                regime = "径流主导"
            else:
                regime = "径流-潮汐相当"

            print(f"{Qr:^14.0f} | {R_ratio:^14.3f} | {tidal_range_upstream:^14.3f} | {regime:^16}")

    print("-" * 110)

    print(f"\n【实验结论】")
    print("1. 径流量增大，潮汐传播受阻")
    print("2. 径流主导时潮汐影响很小")
    print("3. 径流-潮汐比R决定流态特征")
    print("4. 实际河口多为混合型（R≈0.1~1）")


def experiment_17_3():
    """实验17.3：河口长度的影响"""
    print_separator("实验17.3：河口长度的影响")

    b = 200.0
    S0 = 0.00005
    n = 0.03
    Qr = 500.0
    h0_tide = 5.0
    A_tide = 2.0
    T_tide = 12.42 * 3600
    t_total = 1.5 * T_tide

    # 不同的河口长度
    lengths = [10000, 15000, 20000, 25000, 30000]  # 10, 15, 20, 25, 30 km

    print(f"\n固定参数：Qr={Qr}m³/s, A={A_tide}m, T={T_tide/3600:.1f}h")
    print("变化参数：河口长度L")

    print(f"\n河口长度对潮汐影响范围：")
    print("-" * 100)
    print(f"{'河口长度(km)':^14} | {'上游潮差(m)':^14} | {'衰减率(%)':^14} | {'潮汐影响':^14}")
    print("-" * 100)

    for L in lengths:
        results = run_tidal_simulation(L, b, S0, n, Qr, h0_tide, A_tide, T_tide,
                                      t_total, dx=1000.0)

        if results is not None:
            x_grid = results['x']
            tidal_range_mouth, tidal_range_upstream = analyze_tidal_range(results, x_grid)

            attenuation = (1 - tidal_range_upstream / tidal_range_mouth) * 100 if tidal_range_mouth > 0.01 else 0

            # 判断潮汐影响范围
            if tidal_range_upstream > 0.5:
                influence = "全程影响"
            elif tidal_range_upstream > 0.1:
                influence = "部分影响"
            else:
                influence = "仅下游影响"

            print(f"{L/1000:^14.0f} | {tidal_range_upstream:^14.3f} | {attenuation:^14.1f} | {influence:^14}")

    print("-" * 100)

    print(f"\n【实验结论】")
    print("1. 河口越长，潮汐衰减越大")
    print("2. 存在潮汐影响极限长度")
    print("3. 摩阻导致潮差指数衰减")
    print("4. 长河口上游基本不受潮汐影响")


def main():
    """主函数"""
    print_separator("案例17：计算实验")
    print("\n本实验将探讨潮汐河口的关键影响因素\n")

    experiment_17_1()  # 潮汐振幅影响
    experiment_17_2()  # 径流量影响
    experiment_17_3()  # 河口长度影响

    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 潮汐振幅：决定潮差传播强度")
    print("2. 径流量：与潮汐竞争，影响传播范围")
    print("3. 河口长度：决定潮汐影响范围")
    print("\n潮汐河口非恒定流对工程设计至关重要：")
    print("- 港口和码头设计")
    print("- 取水口位置选择")
    print("- 航道维护规划")
    print("- 河口生态保护")
    print_separator()


if __name__ == "__main__":
    main()
