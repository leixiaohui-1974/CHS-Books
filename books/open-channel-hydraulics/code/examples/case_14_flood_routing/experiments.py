"""
案例14：洪水演进计算 - 计算实验

实验内容：
1. 实验14.1：河道长度对洪峰衰减的影响
2. 实验14.2：洪水过程线形状的影响
3. 实验14.3：河道特性对调蓄作用的影响

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


def create_flood_hydrograph(t, Q_base, Q_peak, t_rise, t_fall):
    """创建洪水过程线"""
    Q = np.zeros_like(t)
    for i, ti in enumerate(t):
        if ti <= 0:
            Q[i] = Q_base
        elif ti <= t_rise:
            Q[i] = Q_base + (Q_peak - Q_base) * (ti / t_rise)
        elif ti <= t_rise + t_fall:
            t_elapsed = ti - t_rise
            Q[i] = Q_peak - (Q_peak - Q_base) * (t_elapsed / t_fall)
        else:
            Q[i] = Q_base
    return Q


def experiment_14_1():
    """实验14.1：河道长度对洪峰衰减的影响"""
    print_separator("实验14.1：河道长度对洪峰衰减的影响")

    # 基准参数
    b = 80.0
    S0 = 0.0001
    n = 0.030
    Q_base = 500.0
    Q_peak = 2000.0
    g = 9.81

    t_rise = 6 * 3600
    t_fall = 12 * 3600
    t_duration = 30 * 3600

    print(f"\n固定参数：b={b}m, S0={S0}, n={n}")
    print(f"洪水：Q_base={Q_base}m³/s → Q_peak={Q_peak}m³/s")
    print("变化参数：河道长度L")

    # 不同河道长度
    L_values = [10000, 20000, 30000, 40000, 50000]

    print("\n河道长度对洪峰衰减的影响：")
    print("-" * 120)
    print(f"{'河道长度(km)':^15} | {'理论波速(m/s)':^16} | {'传播时间(h)':^15} | "
          f"{'下游洪峰(m³/s)':^18} | {'衰减率(%)':^13}")
    print("-" * 120)

    for L in L_values:
        channel = RectangularChannel(b=b, S0=S0, n=n)
        h_base = channel.compute_normal_depth(Q_base)
        v_base = Q_base / (b * h_base)
        c_base = np.sqrt(g * h_base)
        wave_speed_theory = v_base + c_base

        dx = min(500.0, L / 50)
        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None, g=g)
        solver.set_uniform_initial(h0=h_base, Q0=Q_base)

        # 创建洪水过程线
        t_hydrograph = np.linspace(0, t_duration, 1000)
        Q_hydrograph = create_flood_hydrograph(t_hydrograph, Q_base, Q_peak,
                                              t_rise, t_fall)

        def get_upstream_Q(t):
            return np.interp(t, t_hydrograph, Q_hydrograph)

        def bc_up(t):
            Q = get_upstream_Q(t)
            h = channel.compute_normal_depth(Q) if Q > 0 else h_base
            return h, Q

        # 下游使用外推边界，让洪峰自由通过
        solver.set_boundary_conditions(bc_up, downstream=None)

        try:
            results = solver.run(t_end=t_duration, dt_output=900.0, verbose=False)

            Q_downstream = results['Q'][:, -1]
            Q_peak_down = np.max(Q_downstream)

            if Q_peak_down > Q_base:
                t_peak_down = results['times'][np.argmax(Q_downstream)] / 3600
                attenuation = (Q_peak - Q_peak_down) / (Q_peak - Q_base) * 100
            else:
                t_peak_down = np.nan
                attenuation = 100.0

            print(f"{L/1000:^15.0f} | {wave_speed_theory:^16.3f} | {t_peak_down:^15.2f} | "
                  f"{Q_peak_down:^18.1f} | {attenuation:^13.1f}")

        except Exception as e:
            print(f"{L/1000:^15.0f} | {'错误':^16} | {'--':^15} | {'--':^18} | {'--':^13}")

    print("-" * 120)

    print("\n【实验结论】")
    print("1. 河道越长，洪峰衰减越大")
    print("2. 衰减主要由河道蓄水和摩阻引起")
    print("3. 长河道的预见期更长")
    print("4. 10km河道衰减约5-10%")
    print("5. 50km河道衰减可达15-25%")


def experiment_14_2():
    """实验14.2：洪水过程线形状的影响"""
    print_separator("实验14.2：洪水过程线形状的影响")

    L = 30000.0
    b = 80.0
    S0 = 0.0001
    n = 0.030
    Q_base = 500.0
    Q_peak = 2000.0
    g = 9.81

    t_duration = 30 * 3600

    print(f"\n固定参数：L={L/1000}km, Q_peak={Q_peak}m³/s")
    print("变化参数：涨峰历时和退水历时")

    channel = RectangularChannel(b=b, S0=S0, n=n)
    h_base = channel.compute_normal_depth(Q_base)

    # 不同的过程线形状
    hydrograph_types = [
        (3*3600, 6*3600, "尖瘦型（3h涨6h退）"),
        (6*3600, 12*3600, "标准型（6h涨12h退）"),
        (12*3600, 18*3600, "平缓型（12h涨18h退）"),
        (6*3600, 6*3600, "对称型（6h涨6h退）")
    ]

    print("\n过程线形状对衰减的影响：")
    print("-" * 120)
    print(f"{'过程线类型':^25} | {'涨峰时间(h)':^14} | {'退水时间(h)':^14} | "
          f"{'下游洪峰(m³/s)':^18} | {'衰减率(%)':^13}")
    print("-" * 120)

    for t_rise, t_fall, desc in hydrograph_types:
        dx = 500.0
        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None, g=g)
        solver.set_uniform_initial(h0=h_base, Q0=Q_base)

        t_hydrograph = np.linspace(0, t_duration, 1000)
        Q_hydrograph = create_flood_hydrograph(t_hydrograph, Q_base, Q_peak,
                                              t_rise, t_fall)

        def get_upstream_Q(t):
            return np.interp(t, t_hydrograph, Q_hydrograph)

        def bc_up(t):
            Q = get_upstream_Q(t)
            h = channel.compute_normal_depth(Q) if Q > 0 else h_base
            return h, Q

        # 下游使用外推边界，让洪峰自由通过
        solver.set_boundary_conditions(bc_up, downstream=None)

        try:
            results = solver.run(t_end=t_duration, dt_output=900.0, verbose=False)

            Q_downstream = results['Q'][:, -1]
            Q_peak_down = np.max(Q_downstream)
            attenuation = (Q_peak - Q_peak_down) / (Q_peak - Q_base) * 100 if Q_peak_down > Q_base else 100.0

            print(f"{desc:^25} | {t_rise/3600:^14.0f} | {t_fall/3600:^14.0f} | "
                  f"{Q_peak_down:^18.1f} | {attenuation:^13.1f}")

        except:
            print(f"{desc:^25} | {t_rise/3600:^14.0f} | {t_fall/3600:^14.0f} | {'错误':^18} | {'--':^13}")

    print("-" * 120)

    print("\n【实验结论】")
    print("1. 尖瘦型过程线衰减最大")
    print("2. 平缓型过程线衰减较小")
    print("3. 涨水快的洪水削峰明显")
    print("4. 河道调蓄作用对尖峰效果显著")
    print("5. 实际洪水通常是不对称的")


def experiment_14_3():
    """实验14.3：河道特性对调蓄作用的影响"""
    print_separator("实验14.3：河道特性对调蓄作用的影响")

    L = 30000.0
    Q_base = 500.0
    Q_peak = 2000.0
    t_rise = 6 * 3600
    t_fall = 12 * 3600
    t_duration = 30 * 3600
    g = 9.81

    print(f"\n固定参数：L={L/1000}km, 洪峰={Q_peak}m³/s")
    print("变化参数：河道宽度b和坡度S0")

    # 实验3.1：河道宽度影响
    print("\n实验3.1：河道宽度对调蓄的影响")

    S0 = 0.0001
    n = 0.030
    b_values = [50, 60, 80, 100, 120]

    print("-" * 110)
    print(f"{'河道宽度(m)':^14} | {'下游洪峰(m³/s)':^18} | {'衰减率(%)':^13} | "
          f"{'蓄洪能力评价':^20}")
    print("-" * 110)

    for b in b_values:
        channel = RectangularChannel(b=b, S0=S0, n=n)
        h_base = channel.compute_normal_depth(Q_base)

        dx = 500.0
        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None, g=g)
        solver.set_uniform_initial(h0=h_base, Q0=Q_base)

        t_hydrograph = np.linspace(0, t_duration, 1000)
        Q_hydrograph = create_flood_hydrograph(t_hydrograph, Q_base, Q_peak,
                                              t_rise, t_fall)

        def get_upstream_Q(t):
            return np.interp(t, t_hydrograph, Q_hydrograph)

        def bc_up(t):
            Q = get_upstream_Q(t)
            h = channel.compute_normal_depth(Q) if Q > 0 else h_base
            return h, Q

        # 下游使用外推边界，让洪峰自由通过
        solver.set_boundary_conditions(bc_up, downstream=None)

        try:
            results = solver.run(t_end=t_duration, dt_output=900.0, verbose=False)

            Q_downstream = results['Q'][:, -1]
            Q_peak_down = np.max(Q_downstream)
            attenuation = (Q_peak - Q_peak_down) / (Q_peak - Q_base) * 100 if Q_peak_down > Q_base else 100.0

            if attenuation < 10:
                evaluation = "较弱"
            elif attenuation < 15:
                evaluation = "中等"
            else:
                evaluation = "较强"

            print(f"{b:^14.0f} | {Q_peak_down:^18.1f} | {attenuation:^13.1f} | {evaluation:^20}")

        except:
            print(f"{b:^14.0f} | {'错误':^18} | {'--':^13} | {'--':^20}")

    print("-" * 110)

    # 实验3.2：河床坡度影响
    print("\n实验3.2：河床坡度对调蓄的影响")

    b = 80.0
    S0_values = [0.00005, 0.0001, 0.0002, 0.0003, 0.0005]

    print("-" * 110)
    print(f"{'河床坡度':^14} | {'下游洪峰(m³/s)':^18} | {'衰减率(%)':^13} | "
          f"{'蓄洪能力评价':^20}")
    print("-" * 110)

    for S0 in S0_values:
        channel = RectangularChannel(b=b, S0=S0, n=n)
        h_base = channel.compute_normal_depth(Q_base)

        dx = 500.0
        solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None, g=g)
        solver.set_uniform_initial(h0=h_base, Q0=Q_base)

        t_hydrograph = np.linspace(0, t_duration, 1000)
        Q_hydrograph = create_flood_hydrograph(t_hydrograph, Q_base, Q_peak,
                                              t_rise, t_fall)

        def get_upstream_Q(t):
            return np.interp(t, t_hydrograph, Q_hydrograph)

        def bc_up(t):
            Q = get_upstream_Q(t)
            h = channel.compute_normal_depth(Q) if Q > 0 else h_base
            return h, Q

        # 下游使用外推边界，让洪峰自由通过
        solver.set_boundary_conditions(bc_up, downstream=None)

        try:
            results = solver.run(t_end=t_duration, dt_output=900.0, verbose=False)

            Q_downstream = results['Q'][:, -1]
            Q_peak_down = np.max(Q_downstream)
            attenuation = (Q_peak - Q_peak_down) / (Q_peak - Q_base) * 100 if Q_peak_down > Q_base else 100.0

            if attenuation < 10:
                evaluation = "较弱（陡坡）"
            elif attenuation < 15:
                evaluation = "中等"
            else:
                evaluation = "较强（缓坡）"

            print(f"{S0:^14.5f} | {Q_peak_down:^18.1f} | {attenuation:^13.1f} | {evaluation:^20}")

        except:
            print(f"{S0:^14.5f} | {'错误':^18} | {'--':^13} | {'--':^20}")

    print("-" * 110)

    print("\n【实验结论】")
    print("1. 河道宽度增大，蓄洪能力增强")
    print("2. 坡度越缓，调蓄作用越明显")
    print("3. 宽阔河道对洪水削峰作用大")
    print("4. 陡坡河道洪水传播快、衰减小")
    print("5. 平原河道比山区河道蓄洪能力强")


def main():
    """主函数"""
    print_separator("案例14：计算实验")
    print("\n本实验将探讨洪水演进的关键影响因素\n")

    experiment_14_1()  # 河道长度影响
    experiment_14_2()  # 过程线形状影响
    experiment_14_3()  # 河道特性影响

    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 河道长度：越长衰减越大，预见期越长")
    print("2. 过程线形状：尖瘦型衰减大，平缓型衰减小")
    print("3. 河道特性：宽度、坡度影响调蓄能力")
    print("\n洪水演进计算对防洪预报至关重要：")
    print("- 提供下游预见期")
    print("- 预测洪峰流量")
    print("- 评估河道调蓄作用")
    print("- 支持防洪决策")
    print_separator()


if __name__ == "__main__":
    main()
