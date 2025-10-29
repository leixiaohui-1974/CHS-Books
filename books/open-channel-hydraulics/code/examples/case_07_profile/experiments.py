"""
案例7：渠道水面曲线计算 - 计算实验

实验内容：
1. 实验7.1：流量对壅水曲线的影响
2. 实验7.2：糙率对壅水曲线的影响
3. 实验7.3：渠底坡度对壅水曲线的影响
4. 实验7.4：不同水面曲线类型对比（M1, M2, S1等）

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import TrapezoidalChannel
from solvers.steady.profile import WaterSurfaceProfile


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def experiment_7_1():
    """
    实验7.1：流量对壅水曲线的影响

    保持其他参数不变，改变流量，观察壅水特性变化
    """
    print_separator("实验7.1：流量对壅水曲线的影响")

    # 基本参数
    b = 3.0
    m = 1.5
    S0 = 0.0008
    n = 0.020
    h_control = 2.5

    print(f"\n固定参数：b = {b}m, m = {m}, S₀ = {S0}, n = {n}")
    print(f"控制水深：h₀ = {h_control}m")

    print("\n不同流量下的壅水特性：")
    print("-" * 120)
    print(f"{'流量Q(m³/s)':^14} | {'正常水深hn(m)':^16} | {'临界水深hc(m)':^16} | {'壅水高度Δh(m)':^16} | {'壅水长度L(m)':^16}")
    print("-" * 120)

    Q_values = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]

    for Q in Q_values:
        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)

        try:
            hn = channel.compute_normal_depth(Q)
            hc = channel.compute_critical_depth(Q)

            profile_solver = WaterSurfaceProfile(channel=channel, Q=Q, dx=20.0)
            L_backwater = profile_solver.compute_backwater_length(h_control, h_threshold=0.05)

            dh = h_control - hn

            print(f"{Q:^14.2f} | {hn:^16.4f} | {hc:^16.4f} | {dh:^16.4f} | {L_backwater:^16.2f}")
        except:
            print(f"{Q:^14.2f} | {'计算失败':^16} | {'计算失败':^16} | {'计算失败':^16} | {'计算失败':^16}")

    print("-" * 120)

    print("\n【实验结论】")
    print("1. 流量增大，正常水深增大，但增速放缓")
    print("2. 流量增大，壅水高度减小（h₀固定，hn增大）")
    print("3. 流量增大，壅水长度减小")
    print("4. 小流量时，壅水影响更大、范围更广")
    print("5. 工程意义：枯水期壅水影响比丰水期更严重")


def experiment_7_2():
    """
    实验7.2：糙率对壅水曲线的影响

    糙率反映渠道粗糙程度，影响水流阻力和壅水特性
    """
    print_separator("实验7.2：糙率对壅水曲线的影响")

    # 基本参数
    b = 3.0
    m = 1.5
    S0 = 0.0008
    Q = 6.0
    h_control = 2.5

    print(f"\n固定参数：b = {b}m, m = {m}, S₀ = {S0}, Q = {Q}m³/s")
    print(f"控制水深：h₀ = {h_control}m")

    n_values = [0.015, 0.018, 0.020, 0.022, 0.025, 0.030]
    n_descriptions = [
        "光滑混凝土",
        "一般混凝土",
        "粗糙混凝土",
        "浆砌石",
        "干砌石",
        "土渠（杂草）"
    ]

    print("\n不同糙率下的壅水特性：")
    print("-" * 120)
    print(f"{'糙率n':^10} | {'渠道类型':^15} | {'正常水深hn(m)':^16} | {'壅水高度Δh(m)':^16} | {'壅水长度L(m)':^16}")
    print("-" * 120)

    for n, desc in zip(n_values, n_descriptions):
        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)

        try:
            hn = channel.compute_normal_depth(Q)

            profile_solver = WaterSurfaceProfile(channel=channel, Q=Q, dx=20.0)
            L_backwater = profile_solver.compute_backwater_length(h_control, h_threshold=0.05)

            dh = h_control - hn

            print(f"{n:^10.3f} | {desc:^15} | {hn:^16.4f} | {dh:^16.4f} | {L_backwater:^16.2f}")
        except:
            print(f"{n:^10.3f} | {desc:^15} | {'计算失败':^16} | {'计算失败':^16} | {'计算失败':^16}")

    print("-" * 120)

    print("\n【实验结论】")
    print("1. 糙率增大，正常水深增大（阻力增大，需要更深的水流）")
    print("2. 糙率增大，壅水高度减小（hn增大）")
    print("3. 糙率增大，壅水长度增大（摩阻大，水深恢复慢）")
    print("4. 渠道维护：保持低糙率可减小正常水深，但壅水影响更远")
    print("5. 设计建议：光滑渠道(n小)正常水深小但壅水远，粗糙渠道反之")


def experiment_7_3():
    """
    实验7.3：渠底坡度对壅水曲线的影响

    坡度是影响水流形态的关键参数
    """
    print_separator("实验7.3：渠底坡度对壅水曲线的影响")

    # 基本参数
    b = 3.0
    m = 1.5
    n = 0.020
    Q = 6.0
    h_control = 2.5

    print(f"\n固定参数：b = {b}m, m = {m}, n = {n}, Q = {Q}m³/s")
    print(f"控制水深：h₀ = {h_control}m")

    S0_values = [0.0002, 0.0004, 0.0006, 0.0008, 0.0010, 0.0015]

    print("\n不同坡度下的壅水特性：")
    print("-" * 120)
    print(f"{'坡度S₀':^12} | {'正常水深hn(m)':^16} | {'临界坡度Sc':^14} | {'渠道类型':^15} | {'壅水长度L(m)':^16}")
    print("-" * 120)

    for S0 in S0_values:
        channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)

        try:
            hn = channel.compute_normal_depth(Q)
            hc = channel.compute_critical_depth(Q)

            # 计算临界坡度
            Ac = channel.area(hc)
            Rc = Ac / channel.wetted_perimeter(hc)
            vc = Q / Ac
            Sc = (n**2 * vc**2) / (Rc**(4.0/3.0))

            if S0 < Sc:
                channel_type = "缓坡"
            elif S0 > Sc:
                channel_type = "陡坡"
            else:
                channel_type = "临界坡"

            profile_solver = WaterSurfaceProfile(channel=channel, Q=Q, dx=20.0)
            L_backwater = profile_solver.compute_backwater_length(h_control, h_threshold=0.05)

            print(f"{S0:^12.4f} | {hn:^16.4f} | {Sc:^14.6f} | {channel_type:^15} | {L_backwater:^16.2f}")
        except:
            print(f"{S0:^12.4f} | {'计算失败':^16} | {'计算失败':^14} | {'计算失败':^15} | {'计算失败':^16}")

    print("-" * 120)

    print("\n【实验结论】")
    print("1. 坡度增大，正常水深减小（重力分量增大，水流更快）")
    print("2. 坡度增大，壅水长度减小（坡度大，恢复快）")
    print("3. 临界坡度 Sc = 0.0054（本案例）")
    print("4. S₀ < Sc：缓坡渠道，正常流为缓流")
    print("5. 陡坡渠道壅水影响范围小，但容易产生急流")


def experiment_7_4():
    """
    实验7.4：不同水面曲线类型对比

    通过改变参数，展示M1, M2, S1等不同类型水面曲线
    """
    print_separator("实验7.4：不同水面曲线类型对比")

    print("\n案例1：M1型壅水曲线（缓坡，h₀ > hn > hc）")
    print("-" * 80)

    # M1: 缓坡壅水
    b1, m1, S01, n1, Q1 = 3.0, 1.5, 0.0008, 0.020, 6.0
    h_control1 = 2.5

    channel1 = TrapezoidalChannel(b=b1, m=m1, S0=S01, n=n1)
    hn1 = channel1.compute_normal_depth(Q1)
    hc1 = channel1.compute_critical_depth(Q1)

    profile1 = WaterSurfaceProfile(channel=channel1, Q=Q1, dx=20.0)
    result1 = profile1.compute_profile(h_start=h_control1, L=1000.0, direction='upstream')

    print(f"参数：b={b1}m, S₀={S01}, Q={Q1}m³/s, h₀={h_control1}m")
    print(f"hn={hn1:.3f}m, hc={hc1:.3f}m, h₀={h_control1:.3f}m")
    print(f"关系：h₀({h_control1:.3f}) > hn({hn1:.3f}) > hc({hc1:.3f})")
    print(f"曲线类型：{result1['type']}")
    print(f"特征：下游控制，水深向上游降低，渐近于hn")

    print("\n案例2：M2型落水曲线（缓坡，hn > h₀ > hc）")
    print("-" * 80)

    # M2: 缓坡落水（控制水深小于正常水深）
    h_control2 = 0.8

    print(f"参数：b={b1}m, S₀={S01}, Q={Q1}m³/s, h₀={h_control2}m")
    print(f"hn={hn1:.3f}m, hc={hc1:.3f}m, h₀={h_control2:.3f}m")
    print(f"关系：hn({hn1:.3f}) > h₀({h_control2:.3f}) > hc({hc1:.3f})")

    profile2 = WaterSurfaceProfile(channel=channel1, Q=Q1, dx=10.0)
    result2 = profile2.compute_profile(h_start=h_control2, L=500.0, direction='upstream')

    print(f"曲线类型：{result2['type']}")
    print(f"特征：水深向上游增大，渐近于hn")

    print("\n案例3：S1型壅水曲线（陡坡，h₀ > hc > hn）")
    print("-" * 80)

    # S1: 陡坡壅水（需要大坡度使hn < hc）
    b3, m3, S03, n3, Q3 = 2.0, 1.0, 0.010, 0.020, 4.0
    h_control3 = 1.5

    channel3 = TrapezoidalChannel(b=b3, m=m3, S0=S03, n=n3)
    hn3 = channel3.compute_normal_depth(Q3)
    hc3 = channel3.compute_critical_depth(Q3)

    print(f"参数：b={b3}m, S₀={S03}, Q={Q3}m³/s, h₀={h_control3}m")
    print(f"hn={hn3:.3f}m, hc={hc3:.3f}m, h₀={h_control3:.3f}m")

    if h_control3 > hc3 > hn3:
        print(f"关系：h₀({h_control3:.3f}) > hc({hc3:.3f}) > hn({hn3:.3f})")

        profile3 = WaterSurfaceProfile(channel=channel3, Q=Q3, dx=10.0)
        result3 = profile3.compute_profile(h_start=h_control3, L=300.0, direction='upstream')

        print(f"曲线类型：{result3['type']}")
        print(f"特征：陡坡渠道下游壅水，水深向上游降低，渐近于hc")
    else:
        print(f"注：未形成S1型曲线（需要 h₀ > hc > hn）")

    print("\n【实验总结】")
    print("-" * 80)

    print("\nM型曲线（缓坡，S₀ < Sc，hn > hc）：")
    print("  M1：h > hn > hc，壅水曲线，常见于闸前、坝前")
    print("  M2：hn > h > hc，落水曲线，常见于渠道进口")
    print("  M3：hn > hc > h，急流，较少见")

    print("\nS型曲线（陡坡，S₀ > Sc，hc > hn）：")
    print("  S1：h > hc > hn，壅水曲线，陡坡末端遇障碍")
    print("  S2：hc > h > hn，过渡段")
    print("  S3：hc > hn > h，急流")

    print("\n工程应用：")
    print("  - M1曲线：闸门壅水分析，堤防超高设计")
    print("  - M2曲线：渠道进口水面线，跌水上游")
    print("  - S1曲线：陡槽下游接明渠")


def main():
    """主函数"""
    print_separator("案例7：计算实验")
    print("\n本实验将探讨水面曲线的各种影响因素\n")

    # 运行各个实验
    experiment_7_1()  # 流量影响
    experiment_7_2()  # 糙率影响
    experiment_7_3()  # 坡度影响
    experiment_7_4()  # 不同曲线类型

    # 总结
    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 流量：影响正常水深和壅水程度，流量大壅水小")
    print("2. 糙率：影响正常水深和壅水长度，糙率大壅水长")
    print("3. 坡度：决定渠道类型和水流形态，坡度大壅水短")
    print("4. 曲线类型：M型（缓坡）和S型（陡坡）各有特点")
    print("\n水面曲线计算是明渠非均匀流分析的核心方法，")
    print("对闸门壅水、桥涵壅水、渠道设计等工程问题至关重要！")
    print_separator()


if __name__ == "__main__":
    main()
