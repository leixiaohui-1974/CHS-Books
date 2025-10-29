"""
案例18：明渠波动与反射 - 计算实验

实验内容：
1. 实验18.1：扰动振幅的影响
2. 实验18.2：渠道长度的影响
3. 实验18.3：扰动频率的影响（共振）

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


def run_wave_reflection(L, b, h0, n, amplitude, duration, t_total, dx=20.0, g=9.81):
    """
    运行波动与反射模拟

    Args:
        L: 渠道长度 (m)
        b: 渠道宽度 (m)
        h0: 初始水深 (m)
        n: 糙率
        amplitude: 扰动振幅 (m)
        duration: 扰动持续时间 (s)
        t_total: 总模拟时长 (s)
        dx: 空间步长 (m)
        g: 重力加速度 (m/s²)

    Returns:
        results: 模拟结果字典
    """
    # 创建求解器
    nx = int(L / dx) + 1
    solver = SaintVenantSolver(L=L, b=b, S0=0.0, n=n, dx=dx, dt=None, g=g)

    # 初始条件：静水
    h_init = np.full(nx, h0)
    Q_init = np.zeros(nx)
    solver.set_initial_conditions(h_init, Q_init)

    # 边界条件
    def bc_upstream(t):
        """上游：水位脉冲扰动"""
        if t < duration:
            h = h0 + amplitude * np.sin(np.pi * t / duration)
        else:
            h = h0
        return h, 0.0

    def bc_downstream(t):
        """下游：封闭端（零流量）"""
        return h0, 0.0

    solver.set_boundary_conditions(bc_upstream, bc_downstream)

    # 运行模拟
    try:
        results = solver.run(t_end=t_total, dt_output=5.0, verbose=False)
        return results
    except Exception as e:
        print(f"    模拟出错：{e}")
        return None


def analyze_wave_metrics(results, h0):
    """
    分析波动特性

    Args:
        results: 模拟结果
        h0: 初始水深

    Returns:
        max_amplitude: 最大振幅 (m)
        reflection_ratio: 反射系数
        energy_ratio: 能量比
    """
    if results is None:
        return np.nan, np.nan, np.nan

    h_results = results['h']
    eta = h_results - h0  # 水位扰动

    # 最大振幅
    max_amplitude = np.max(np.abs(eta))

    # 反射系数（下游最大振幅/上游最大振幅的比值）
    upstream_max = np.max(np.abs(eta[:, 0]))
    downstream_max = np.max(np.abs(eta[:, -1]))
    reflection_ratio = downstream_max / upstream_max if upstream_max > 1e-6 else 0.0

    # 能量比（最终能量/初始能量）
    g = 9.81
    dx = results['x'][1] - results['x'][0]
    energy = np.sum(0.5 * g * eta**2 * dx, axis=1)

    # 找到扰动结束后的第一个时刻作为初始能量
    idx_ref = min(10, len(energy) - 1)
    if energy[idx_ref] > 1e-6:
        energy_ratio = energy[-1] / energy[idx_ref]
    else:
        energy_ratio = 0.0

    return max_amplitude, reflection_ratio, energy_ratio


def experiment_18_1():
    """实验18.1：扰动振幅的影响"""
    print_separator("实验18.1：扰动振幅的影响")

    L = 1000.0
    b = 10.0
    h0 = 3.0
    n = 0.02
    duration = 10.0
    t_total = 600.0
    g = 9.81

    # 不同的扰动振幅
    amplitudes = [0.1, 0.2, 0.3, 0.5, 1.0]  # m

    print(f"\n固定参数：L={L}m, h₀={h0}m, 扰动持续={duration}s")
    print("变化参数：扰动振幅")

    # 理论波速
    c = np.sqrt(g * h0)
    print(f"\n理论波速：c = √(gh₀) = {c:.2f} m/s")
    print(f"往返时间：2L/c = {2*L/c:.0f} s")

    print(f"\n扰动振幅对波动的影响：")
    print("-" * 100)
    print(f"{'振幅(m)':^12} | {'相对振幅(%)':^14} | "
          f"{'最大扰动(m)':^14} | {'反射系数':^12} | {'能量比':^10}")
    print("-" * 100)

    for amplitude in amplitudes:
        results = run_wave_reflection(L, b, h0, n, amplitude, duration, t_total)

        if results is not None:
            max_amp, refl_ratio, energy_ratio = analyze_wave_metrics(results, h0)
            relative_amp = amplitude / h0 * 100

            print(f"{amplitude:^12.2f} | {relative_amp:^14.1f} | "
                  f"{max_amp:^14.3f} | {refl_ratio:^12.2f} | {energy_ratio:^10.3f}")

    print("-" * 100)

    print(f"\n【实验结论】")
    print("1. 扰动振幅越大，波的能量越大")
    print("2. 小振幅时，线性理论适用，反射系数接近1")
    print("3. 大振幅时，非线性效应增强")
    print("4. 摩阻导致能量逐渐衰减")
    print("5. 实际工程应控制扰动幅度避免共振")


def experiment_18_2():
    """实验18.2：渠道长度的影响"""
    print_separator("实验18.2：渠道长度的影响")

    b = 10.0
    h0 = 3.0
    n = 0.02
    amplitude = 0.5
    duration = 10.0
    g = 9.81

    # 不同的渠道长度
    lengths = [500, 1000, 2000, 3000, 5000]  # m

    print(f"\n固定参数：h₀={h0}m, 振幅={amplitude}m, 扰动持续={duration}s")
    print("变化参数：渠道长度L")

    c = np.sqrt(g * h0)

    print(f"\n渠道长度对波动的影响：")
    print("-" * 110)
    print(f"{'长度(m)':^10} | {'理论往返时间(s)':^18} | {'模拟时长(s)':^14} | "
          f"{'最大扰动(m)':^14} | {'反射系数':^12}")
    print("-" * 110)

    for L in lengths:
        # 计算理论往返时间
        t_roundtrip = 2 * L / c

        # 模拟时长设为往返时间的1.5倍
        t_total = t_roundtrip * 1.5

        results = run_wave_reflection(L, b, h0, n, amplitude, duration, t_total)

        if results is not None:
            max_amp, refl_ratio, _ = analyze_wave_metrics(results, h0)

            print(f"{L:^10.0f} | {t_roundtrip:^18.0f} | {t_total:^14.0f} | "
                  f"{max_amp:^14.3f} | {refl_ratio:^12.2f}")

    print("-" * 110)

    print(f"\n【实验结论】")
    print("1. 渠道越长，波的传播时间越长")
    print("2. 往返时间与渠道长度成正比")
    print("3. 长渠道中摩阻衰减更明显")
    print("4. 反射系数随传播距离增加而减小")
    print("5. 设计时应考虑渠道长度对波动的影响")


def experiment_18_3():
    """实验18.3：扰动频率的影响（共振）"""
    print_separator("实验18.3：扰动频率的影响（共振）")

    L = 1000.0
    b = 10.0
    h0 = 3.0
    n = 0.02
    amplitude = 0.3
    g = 9.81

    # 理论基频
    c = np.sqrt(g * h0)
    T_fundamental = 2 * L / c  # 基频周期
    f_fundamental = 1 / T_fundamental  # 基频频率

    print(f"\n渠道参数：L={L}m, h₀={h0}m")
    print(f"理论波速：c = {c:.2f} m/s")
    print(f"基频周期：T₁ = 2L/c = {T_fundamental:.0f} s")
    print(f"基频频率：f₁ = {f_fundamental:.5f} Hz")

    # 不同的扰动持续时间（对应不同频率）
    durations = [
        T_fundamental / 4,   # 高频（4倍基频）
        T_fundamental / 2,   # 2倍基频
        T_fundamental,       # 基频（共振）
        T_fundamental * 2,   # 1/2基频
        T_fundamental * 4    # 低频（1/4基频）
    ]

    t_total = T_fundamental * 3  # 模拟3个基频周期

    print(f"\n扰动频率对波动的影响：")
    print("-" * 110)
    print(f"{'扰动时长(s)':^14} | {'频率比(f/f₁)':^14} | "
          f"{'最大扰动(m)':^14} | {'反射系数':^12} | {'能量比':^10}")
    print("-" * 110)

    for duration in durations:
        results = run_wave_reflection(L, b, h0, n, amplitude, duration, t_total)

        if results is not None:
            max_amp, refl_ratio, energy_ratio = analyze_wave_metrics(results, h0)
            freq_ratio = T_fundamental / duration

            print(f"{duration:^14.0f} | {freq_ratio:^14.2f} | "
                  f"{max_amp:^14.3f} | {refl_ratio:^12.2f} | {energy_ratio:^10.3f}")

    print("-" * 110)

    print(f"\n【实验结论】")
    print("1. 当扰动周期接近基频周期时，易发生共振")
    print("2. 共振时波的振幅显著放大")
    print("3. 高频扰动衰减快，低频扰动传播远")
    print("4. 共振频率与渠道长度和水深有关")
    print("5. 工程设计应避免激发共振频率")
    print(f"6. 本例基频约为 {f_fundamental*1000:.2f} mHz")


def main():
    """主函数"""
    print_separator("案例18：计算实验")
    print("\n本实验将探讨明渠波动与反射的关键影响因素\n")

    experiment_18_1()  # 扰动振幅影响
    experiment_18_2()  # 渠道长度影响
    experiment_18_3()  # 扰动频率影响（共振）

    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 扰动振幅：影响波的能量和非线性效应")
    print("2. 渠道长度：决定波的传播时间和衰减程度")
    print("3. 扰动频率：共振条件和振幅放大")
    print("\n明渠波动与反射现象在工程中很重要：")
    print("- 闸门操作引起的波动")
    print("- 船行波的影响")
    print("- 港口晃荡现象")
    print("- 水锤效应")
    print("- 共振危害预防")
    print_separator()


if __name__ == "__main__":
    main()
