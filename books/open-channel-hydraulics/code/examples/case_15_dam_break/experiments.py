"""
案例15：溃坝波计算 - 计算实验

实验内容：
1. 实验15.1：上下游水深比的影响
2. 实验15.2：溃坝位置的影响
3. 实验15.3：干河床vs湿河床对比

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from solvers.saint_venant import SaintVenantSolver


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def compute_wave_characteristics(h0, hd, g=9.81):
    """计算波的特征参数"""
    c0 = np.sqrt(g * h0)

    if hd <= 0.01:
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


def run_dam_break_simulation(L, b, h0, hd, x_dam, t_end, dx=50.0, g=9.81):
    """运行溃坝波数值模拟

    Args:
        L: 河道长度 (m)
        b: 河道宽度 (m)
        h0: 上游水深 (m)
        hd: 下游水深 (m)
        x_dam: 溃坝位置 (m)
        t_end: 模拟时长 (s)
        dx: 空间步长 (m)
        g: 重力加速度 (m/s²)

    Returns:
        results: 模拟结果字典
    """
    nx = int(L / dx) + 1
    solver = SaintVenantSolver(L=L, b=b, S0=0.0, n=0.0, dx=dx, dt=None, g=g)

    # 初始条件
    h_init = np.zeros(nx)
    Q_init = np.zeros(nx)
    x_grid = solver.x

    for i, xi in enumerate(x_grid):
        if xi < x_dam:
            h_init[i] = h0
        else:
            h_init[i] = max(hd, 0.01)  # 避免零水深

    solver.set_initial_conditions(h_init, Q_init)

    # 边界条件：外推
    solver.set_boundary_conditions(upstream=None, downstream=None)

    # 运行模拟
    dt_output = min(t_end / 10, 100.0)

    try:
        results = solver.run(t_end=t_end, dt_output=dt_output, verbose=False)
        return results
    except Exception as e:
        print(f"    模拟出错：{e}")
        return None


def analyze_wave_front(results, x_grid, hd, x_dam, g=9.81):
    """分析波前传播特性

    Args:
        results: 模拟结果
        x_grid: 空间网格
        hd: 下游初始水深
        x_dam: 溃坝位置
        g: 重力加速度

    Returns:
        wave_front_speed: 波前平均速度 (m/s)
    """
    if results is None:
        return np.nan

    # 找到波前到达下游的时间
    threshold = hd + 0.5  # 水深增加0.5m作为波前判据

    # 选择距坝址1km的下游位置
    x_target = x_dam + 1000.0
    idx_target = np.argmin(np.abs(x_grid - x_target))

    h_series = results['h'][:, idx_target]
    times = results['times']

    # 找到波前到达时间
    arrival_idx = np.where(h_series > threshold)[0]
    if len(arrival_idx) > 0:
        t_arrival = times[arrival_idx[0]]
        wave_speed = (x_target - x_dam) / t_arrival
        return wave_speed
    else:
        return np.nan


def experiment_15_1():
    """实验15.1：上下游水深比的影响"""
    print_separator("实验15.1：上下游水深比的影响")

    L = 10000.0
    b = 50.0
    x_dam = 5000.0
    h0 = 10.0  # 固定上游水深
    g = 9.81

    # 不同的下游水深
    hd_values = [0.0, 1.0, 2.0, 3.0, 5.0]

    print(f"\n固定参数：h₀={h0}m, L={L/1000}km")
    print("变化参数：下游水深hd")

    print(f"\n水深比对溃坝波传播的影响：")
    print("-" * 120)
    print(f"{'下游水深(m)':^12} | {'水深比h₀/hd':^14} | {'理论波速(m/s)':^16} | "
          f"{'激波速度(m/s)':^16} | {'中间区水深(m)':^16}")
    print("-" * 120)

    for hd in hd_values:
        params = compute_wave_characteristics(h0, hd, g)

        if params['type'] == 'dry':
            wave_speed = params['wave_front_speed']
            shock_speed = np.nan
            h_star = np.nan
            ratio_str = "∞"
        else:
            wave_speed = params['shock_speed']
            shock_speed = params['shock_speed']
            h_star = params['h_star']
            ratio_str = f"{h0/hd:.2f}"

        print(f"{hd:^12.1f} | {ratio_str:^14} | {wave_speed:^16.3f} | "
              f"{shock_speed if not np.isnan(shock_speed) else '--':^16} | "
              f"{h_star if not np.isnan(h_star) else '--':^16}")

    print("-" * 120)

    print(f"\n【实验结论】")
    print("1. 水深比越大，激波传播越快")
    print("2. 干河床情况波速最快（2c₀）")
    print("3. 湿河床产生激波，波速取决于水深比")
    print("4. 中间区水深随下游水深增加而增大")
    print("5. 下游水深越浅，洪水危险性越大")


def experiment_15_2():
    """实验15.2：溃坝位置的影响"""
    print_separator("实验15.2：溃坝位置的影响")

    L = 10000.0
    b = 50.0
    h0 = 10.0
    hd = 2.0
    t_end = 600.0
    g = 9.81

    # 不同的溃坝位置
    x_dam_values = [2000, 3000, 5000, 7000, 8000]

    print(f"\n固定参数：L={L/1000}km, h₀={h0}m, hd={hd}m")
    print("变化参数：溃坝位置x_dam")

    print(f"\n溃坝位置对洪水影响范围：")
    print("-" * 100)
    print(f"{'溃坝位置(m)':^14} | {'上游影响(m)':^14} | {'下游影响(m)':^14} | {'总影响长度(m)':^16}")
    print("-" * 100)

    for x_dam in x_dam_values:
        # 理论分析
        c0 = np.sqrt(g * h0)
        cd = np.sqrt(g * hd)
        v_star = c0 - cd
        c_star = (c0 + cd) / 2.0
        h_star = c_star**2 / g
        U = v_star + c_star * np.sqrt((h_star + hd) / (2 * hd))

        # 上游影响范围（负向波）
        upstream_reach = c0 * t_end
        x_upstream_limit = max(0, x_dam - upstream_reach)

        # 下游影响范围（激波）
        downstream_reach = U * t_end
        x_downstream_limit = min(L, x_dam + downstream_reach)

        total_length = (x_dam - x_upstream_limit) + (x_downstream_limit - x_dam)

        print(f"{x_dam:^14.0f} | {x_dam - x_upstream_limit:^14.1f} | "
              f"{x_downstream_limit - x_dam:^14.1f} | {total_length:^16.1f}")

    print("-" * 100)

    print(f"\n【实验结论】")
    print("1. 溃坝位置决定上下游的影响范围")
    print("2. 上游影响速度较慢（-c₀）")
    print("3. 下游影响速度较快（激波速度U）")
    print("4. 中部溃坝对整个河道影响最大")
    print("5. 靠近上游溃坝，下游受影响范围更大")


def experiment_15_3():
    """实验15.3：干河床vs湿河床对比"""
    print_separator("实验15.3：干河床vs湿河床对比")

    L = 10000.0
    b = 50.0
    x_dam = 5000.0
    h0 = 10.0
    t_end = 600.0
    dx = 50.0
    g = 9.81

    # 两种情况
    cases = [
        (0.0, "干河床"),
        (2.0, "湿河床")
    ]

    print(f"\n固定参数：h₀={h0}m, L={L/1000}km")
    print("对比：干河床（hd=0）vs 湿河床（hd=2m）")

    print(f"\n干湿河床溃坝波特性对比：")
    print("-" * 120)
    print(f"{'河床类型':^12} | {'下游水深(m)':^14} | {'波前速度(m/s)':^16} | "
          f"{'最大流速(m/s)':^16} | {'波传播类型':^16}")
    print("-" * 120)

    for hd, desc in cases:
        params = compute_wave_characteristics(h0, hd, g)

        if params['type'] == 'dry':
            wave_speed = params['wave_front_speed']
            v_max = params['v_max']
            wave_type = "膨胀波"
        else:
            wave_speed = params['shock_speed']
            v_max = params['v_star']
            wave_type = "膨胀波+激波"

        print(f"{desc:^12} | {hd:^14.1f} | {wave_speed:^16.3f} | "
              f"{v_max:^16.3f} | {wave_type:^16}")

    print("-" * 120)

    # 数值模拟对比
    print(f"\n数值模拟对比（t={t_end}s）：")
    print("-" * 100)
    print(f"{'河床类型':^12} | {'下游最大水深(m)':^18} | {'下游最大流速(m/s)':^20} | {'能量耗散':^14}")
    print("-" * 100)

    for hd, desc in cases:
        results = run_dam_break_simulation(L, b, h0, hd, x_dam, t_end, dx, g)

        if results is not None:
            # 下游区域（x > x_dam + 1000）
            x_grid = results['x']
            downstream_mask = x_grid > (x_dam + 1000)

            h_downstream = results['h'][:, downstream_mask]
            v_downstream = results['v'][:, downstream_mask]

            h_max_down = np.max(h_downstream)
            v_max_down = np.max(np.abs(v_downstream))

            # 能量耗散指示（激波的特征）
            if hd > 0.01:
                energy_loss = "显著（激波）"
            else:
                energy_loss = "较小"

            print(f"{desc:^12} | {h_max_down:^18.2f} | {v_max_down:^20.3f} | {energy_loss:^14}")
        else:
            print(f"{desc:^12} | {'--':^18} | {'--':^20} | {'--':^14}")

    print("-" * 100)

    print(f"\n【实验结论】")
    print("1. 干河床波速更快但无激波")
    print("2. 湿河床产生激波，能量耗散大")
    print("3. 干河床洪水传播距离更远")
    print("4. 湿河床下游受冲击力更大（激波）")
    print("5. 实际工程需考虑河床初始状态")


def main():
    """主函数"""
    print_separator("案例15：计算实验")
    print("\n本实验将探讨溃坝波传播的关键影响因素\n")

    experiment_15_1()  # 水深比影响
    experiment_15_2()  # 溃坝位置影响
    experiment_15_3()  # 干湿河床对比

    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 水深比：决定波速和激波强度")
    print("2. 溃坝位置：影响上下游受灾范围")
    print("3. 河床状态：干湿河床波传播特性差异显著")
    print("\n溃坝波计算对防洪减灾至关重要：")
    print("- 预测洪水到达时间")
    print("- 估算淹没范围和水深")
    print("- 制定应急撤离方案")
    print("- 评估溃坝风险")
    print_separator()


if __name__ == "__main__":
    main()
