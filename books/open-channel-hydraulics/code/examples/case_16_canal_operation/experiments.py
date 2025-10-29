"""
案例16：渠道非恒定流调度 - 计算实验

实验内容：
1. 实验16.1：调度速度的影响
2. 实验16.2：调度幅度的影响
3. 实验16.3：渠道长度的影响

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


def run_canal_schedule(L, b, S0, n, Q_init, Q_final, t_schedule_duration,
                      t_schedule_start=600.0, t_total=7200.0, dx=100.0, g=9.81):
    """
    运行渠道调度模拟

    Args:
        L: 渠道长度 (m)
        b: 渠道宽度 (m)
        S0: 渠道坡度
        n: 糙率
        Q_init: 初始流量 (m³/s)
        Q_final: 最终流量 (m³/s)
        t_schedule_duration: 调度持续时间 (s)
        t_schedule_start: 调度开始时间 (s)
        t_total: 总模拟时长 (s)
        dx: 空间步长 (m)
        g: 重力加速度 (m/s²)

    Returns:
        results: 模拟结果字典
    """
    # 创建渠道和求解器
    channel = RectangularChannel(b=b, S0=S0, n=n)
    nx = int(L / dx) + 1
    solver = SaintVenantSolver(L=L, b=b, S0=S0, n=n, dx=dx, dt=None, g=g)

    # 初始条件
    h0 = channel.compute_normal_depth(Q_init)
    h_init = np.full(nx, h0)
    Q_init_array = np.full(nx, Q_init)
    solver.set_initial_conditions(h_init, Q_init_array)

    # 边界条件
    t_schedule_end = t_schedule_start + t_schedule_duration

    def bc_upstream(t):
        """上游流量边界"""
        if t < t_schedule_start:
            Q = Q_init
        elif t > t_schedule_end:
            Q = Q_final
        else:
            tau = (t - t_schedule_start) / t_schedule_duration
            # S曲线平滑过渡
            Q = Q_init + (Q_final - Q_init) * 0.5 * (1 + np.tanh(6 * (tau - 0.5)))

        h = channel.compute_normal_depth(Q) if Q > 0.1 else h0
        return h, Q

    solver.set_boundary_conditions(upstream=bc_upstream, downstream=None)

    # 运行模拟
    try:
        results = solver.run(t_end=t_total, dt_output=300.0, verbose=False)
        return results
    except Exception as e:
        print(f"    模拟出错：{e}")
        return None


def analyze_response(results, Q_init, Q_final):
    """
    分析调度响应特性

    Args:
        results: 模拟结果
        Q_init: 初始流量
        Q_final: 最终流量

    Returns:
        response_time: 响应时间 (s)
        overshoot: 超调量 (%)
    """
    if results is None:
        return np.nan, np.nan

    # 分析下游流量响应
    Q_down = results['Q'][:, -1]
    times = results['times']

    # 90%响应时间
    Q_target_90 = Q_init + 0.9 * (Q_final - Q_init)

    if Q_final > Q_init:
        # 增加流量
        idx = np.where(Q_down >= Q_target_90)[0]
    else:
        # 减少流量
        idx = np.where(Q_down <= Q_target_90)[0]

    if len(idx) > 0:
        response_time = times[idx[0]]
    else:
        response_time = np.nan

    # 超调量
    if Q_final > Q_init:
        Q_max = np.max(Q_down)
        overshoot = (Q_max - Q_final) / (Q_final - Q_init) * 100 if Q_final != Q_init else 0
    else:
        Q_min = np.min(Q_down)
        overshoot = (Q_final - Q_min) / (Q_init - Q_final) * 100 if Q_final != Q_init else 0

    return response_time, overshoot


def experiment_16_1():
    """实验16.1：调度速度的影响"""
    print_separator("实验16.1：调度速度的影响")

    L = 5000.0
    b = 10.0
    S0 = 0.0002
    n = 0.025
    Q_init = 20.0
    Q_final = 32.0  # 增加60%
    t_schedule_start = 600.0

    # 不同的调度持续时间
    durations = [600, 1200, 1800, 2400, 3000]  # 10, 20, 30, 40, 50分钟

    print(f"\n固定参数：L={L/1000}km, Q_init={Q_init}m³/s, Q_final={Q_final}m³/s")
    print("变化参数：调度持续时间")

    print(f"\n调度速度对响应的影响：")
    print("-" * 100)
    print(f"{'调度时长(min)':^15} | {'调度速率(m³/s/min)':^20} | "
          f"{'响应时间(min)':^18} | {'超调量(%)':^12}")
    print("-" * 100)

    for duration in durations:
        results = run_canal_schedule(L, b, S0, n, Q_init, Q_final, duration,
                                    t_schedule_start=t_schedule_start)

        if results is not None:
            response_time, overshoot = analyze_response(results, Q_init, Q_final)
            schedule_rate = (Q_final - Q_init) / (duration / 60)

            print(f"{duration/60:^15.0f} | {schedule_rate:^20.3f} | "
                  f"{response_time/60:^18.1f} | {overshoot:^12.1f}")

    print("-" * 100)

    print(f"\n【实验结论】")
    print("1. 调度速度越快，响应时间越短")
    print("2. 但快速调度可能引起较大超调")
    print("3. 慢速调度更平稳但响应慢")
    print("4. 实际应选择适中的调度速度")
    print("5. 建议调度时长为传播时间的2-3倍")


def experiment_16_2():
    """实验16.2：调度幅度的影响"""
    print_separator("实验16.2：调度幅度的影响")

    L = 5000.0
    b = 10.0
    S0 = 0.0002
    n = 0.025
    Q_init = 20.0
    t_schedule_duration = 1200.0  # 20分钟
    t_schedule_start = 600.0

    # 不同的流量变化幅度
    increase_ratios = [0.2, 0.4, 0.6, 0.8, 1.0]  # 20%, 40%, 60%, 80%, 100%

    print(f"\n固定参数：L={L/1000}km, Q_init={Q_init}m³/s, 调度时长={t_schedule_duration/60}min")
    print("变化参数：流量变化幅度")

    print(f"\n调度幅度对响应的影响：")
    print("-" * 100)
    print(f"{'变化幅度(%)':^14} | {'最终流量(m³/s)':^16} | "
          f"{'响应时间(min)':^18} | {'超调量(%)':^12}")
    print("-" * 100)

    for ratio in increase_ratios:
        Q_final = Q_init * (1 + ratio)

        results = run_canal_schedule(L, b, S0, n, Q_init, Q_final, t_schedule_duration,
                                    t_schedule_start=t_schedule_start)

        if results is not None:
            response_time, overshoot = analyze_response(results, Q_init, Q_final)

            print(f"{ratio*100:^14.0f} | {Q_final:^16.1f} | "
                  f"{response_time/60:^18.1f} | {overshoot:^12.1f}")

    print("-" * 100)

    print(f"\n【实验结论】")
    print("1. 变化幅度越大，系统调整时间越长")
    print("2. 大幅度调整可能引起更大的超调")
    print("3. 响应时间与变化幅度基本无关（主要取决于波速）")
    print("4. 超调量随变化幅度增大而增加")
    print("5. 大幅度调整应放缓调度速度")


def experiment_16_3():
    """实验16.3：渠道长度的影响"""
    print_separator("实验16.3：渠道长度的影响")

    b = 10.0
    S0 = 0.0002
    n = 0.025
    Q_init = 20.0
    Q_final = 32.0
    t_schedule_duration = 1200.0  # 20分钟
    t_schedule_start = 600.0
    g = 9.81

    # 不同的渠道长度
    lengths = [2000, 3000, 5000, 8000, 10000]  # 2, 3, 5, 8, 10 km

    print(f"\n固定参数：b={b}m, Q_init={Q_init}m³/s, Q_final={Q_final}m³/s")
    print("变化参数：渠道长度L")

    print(f"\n渠道长度对响应的影响：")
    print("-" * 110)
    print(f"{'渠道长度(km)':^14} | {'理论传播时间(min)':^20} | "
          f"{'响应时间(min)':^18} | {'延迟系数':^12}")
    print("-" * 110)

    channel = RectangularChannel(b=b, S0=S0, n=n)

    for L in lengths:
        # 理论波传播时间
        h0 = channel.compute_normal_depth(Q_init)
        v0 = Q_init / (b * h0)
        c0 = np.sqrt(g * h0)
        t_theory = L / (v0 + c0)

        # 数值模拟
        results = run_canal_schedule(L, b, S0, n, Q_init, Q_final, t_schedule_duration,
                                    t_schedule_start=t_schedule_start,
                                    t_total=max(10000, L/2))

        if results is not None:
            response_time, _ = analyze_response(results, Q_init, Q_final)
            delay_factor = (response_time - t_schedule_start) / t_theory if not np.isnan(response_time) else np.nan

            print(f"{L/1000:^14.1f} | {t_theory/60:^20.1f} | "
                  f"{response_time/60:^18.1f} | {delay_factor:^12.2f}")

    print("-" * 110)

    print(f"\n【实验结论】")
    print("1. 渠道越长，响应延迟越大")
    print("2. 响应时间与理论传播时间成正比")
    print("3. 延迟系数约为1.2-1.5（包含调整时间）")
    print("4. 长渠道需要更长的预见期")
    print("5. 建议提前1-2倍传播时间开始调度")


def main():
    """主函数"""
    print_separator("案例16：计算实验")
    print("\n本实验将探讨渠道调度的关键影响因素\n")

    experiment_16_1()  # 调度速度影响
    experiment_16_2()  # 调度幅度影响
    experiment_16_3()  # 渠道长度影响

    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 调度速度：权衡响应快慢与超调大小")
    print("2. 调度幅度：大幅度调整需更谨慎")
    print("3. 渠道长度：决定响应延迟和预见期")
    print("\n渠道非恒定流调度对灌溉供水至关重要：")
    print("- 精确满足用水需求")
    print("- 保持渠道水位稳定")
    print("- 提高水资源利用效率")
    print("- 减少水量损失")
    print_separator()


if __name__ == "__main__":
    main()
