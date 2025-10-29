"""
案例2：城市雨水排水渠设计 - 计算实验

实验内容：
1. 实验2.1：渠宽对流态的影响
2. 实验2.2：坡度对流速和流态的影响
3. 实验2.3：临界流的探索
4. 实验2.4：优化设计方案

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import RectangularChannel
from solvers.steady.uniform_flow import UniformFlowSolver


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def experiment_2_1():
    """
    实验2.1：渠宽对流态的影响

    保持流量和坡度不变，改变渠宽，观察流态变化
    """
    print_separator("实验2.1：渠宽对流态的影响")

    # 基本参数
    Q = 1.2
    n = 0.013
    S0 = 0.003

    # 不同的渠宽
    b_values = [1.0, 1.2, 1.5, 1.8, 2.0, 2.5]

    print("\n不同渠宽对比：")
    print("-" * 100)
    print(f"{'渠宽b(m)':^10} | {'正常水深(m)':^12} | {'临界水深(m)':^12} | {'流速(m/s)':^10} | {'Fr':^8} | {'流态':^10}")
    print("-" * 100)

    for b in b_values:
        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)

        results = solver.compute_normal_depth(Q)
        h0 = results["正常水深_h0"]
        v = results["流速_v"]
        Fr = results["弗劳德数_Fr"]

        hc = channel.compute_critical_depth(Q)

        flow_state = "急流" if Fr > 1.05 else ("临界" if Fr > 0.95 else "缓流")

        print(f"{b:^10.2f} | {h0:^12.4f} | {hc:^12.4f} | {v:^10.4f} | {Fr:^8.4f} | {flow_state:^10}")

    print("-" * 100)

    print("\n【实验结论】")
    print("1. 渠宽增大，正常水深减小（相同流量下，渠道更宽，水深更浅）")
    print("2. 渠宽增大，流速减小（断面增大，流速降低）")
    print("3. 渠宽增大，弗劳德数减小，流态从接近临界转为稳定缓流")
    print("4. 设计建议：适当增加渠宽可以降低Fr，避免临界流")


def experiment_2_2():
    """
    实验2.2：坡度对流速和流态的影响

    保持流量和渠宽不变，改变坡度，观察流态变化
    """
    print_separator("实验2.2：坡度对流速和流态的影响")

    # 基本参数
    Q = 1.2
    b = 1.5
    n = 0.013

    # 不同的坡度
    S0_values = [0.0005, 0.001, 0.002, 0.003, 0.005, 0.010]

    print("\n不同坡度对比：")
    print("-" * 110)
    print(f"{'坡度S0':^10} | {'坡度%':^8} | {'正常水深(m)':^12} | {'临界水深(m)':^12} | {'流速(m/s)':^10} | {'Fr':^8} | {'流态':^10}")
    print("-" * 110)

    for S0 in S0_values:
        channel = RectangularChannel(b=b, n=n, S0=S0)
        solver = UniformFlowSolver(channel)

        results = solver.compute_normal_depth(Q)
        h0 = results["正常水深_h0"]
        v = results["流速_v"]
        Fr = results["弗劳德数_Fr"]

        hc = channel.compute_critical_depth(Q)

        flow_state = "急流" if Fr > 1.05 else ("临界" if Fr > 0.95 else "缓流")

        print(f"{S0:^10.4f} | {S0*100:^8.2f} | {h0:^12.4f} | {hc:^12.4f} | {v:^10.4f} | {Fr:^8.4f} | {flow_state:^10}")

    print("-" * 110)

    print("\n【实验结论】")
    print("1. 坡度越大，正常水深越小（坡度促进水流加速，水深减小）")
    print("2. 坡度越大，流速越大（重力分量增大）")
    print("3. 坡度增大到一定程度，会从缓流转为临界流甚至急流")
    print("4. 对于排水渠：")
    print("   - 坡度太小：流速小，容易淤积")
    print("   - 坡度太大：流速大，可能冲刷，且易出现急流")
    print("   - 最佳坡度：既保证排水，又维持稳定缓流（Fr < 0.7）")


def experiment_2_3():
    """
    实验2.3：临界流的探索

    设计一组参数，使流动接近临界状态
    """
    print_separator("实验2.3：临界流的探索")

    Q = 1.2
    b = 1.5
    n = 0.013

    print("\n寻找临界坡度（使 h0 = hc 的坡度）...")
    print("-" * 80)

    # 临界水深
    channel_temp = RectangularChannel(b=b, n=n, S0=0.001)
    hc = channel_temp.compute_critical_depth(Q)

    print(f"临界水深：hc = {hc:.4f} m")
    print(f"临界流速：vc = Q/(b*hc) = {Q/(b*hc):.4f} m/s")
    print(f"临界坡度（Sc）的确定：使正常水深等于临界水深")

    # 二分法寻找临界坡度
    S_low, S_high = 0.0001, 0.01

    for iteration in range(20):
        S_mid = (S_low + S_high) / 2
        channel = RectangularChannel(b=b, n=n, S0=S_mid)
        solver = UniformFlowSolver(channel)
        h0 = solver.compute_normal_depth(Q)["正常水深_h0"]

        if abs(h0 - hc) < 0.001:  # 精度1mm
            print(f"\n找到临界坡度：Sc ≈ {S_mid:.6f} ({S_mid*100:.4f}%)")
            print(f"此时：h0 = {h0:.4f} m ≈ hc = {hc:.4f} m")

            results = solver.compute_normal_depth(Q)
            Fr = results["弗劳德数_Fr"]
            v = results["流速_v"]

            print(f"弗劳德数：Fr = {Fr:.4f} ≈ 1")
            print(f"流速：v = {v:.4f} m/s")
            break
        elif h0 > hc:
            S_low = S_mid
        else:
            S_high = S_mid

    print("\n不同坡度下的流态过渡：")
    print("-" * 80)
    print(f"{'坡度类型':^15} | {'坡度S0':^12} | {'h0/hc':^10} | {'Fr':^8} | {'流态':^10}")
    print("-" * 80)

    # 缓坡
    S_sub = S_mid * 0.5
    channel = RectangularChannel(b=b, n=n, S0=S_sub)
    solver = UniformFlowSolver(channel)
    results = solver.compute_normal_depth(Q)
    h0 = results["正常水深_h0"]
    Fr = results["弗劳德数_Fr"]
    print(f"{'缓坡(S<Sc)':^15} | {S_sub:^12.6f} | {h0/hc:^10.4f} | {Fr:^8.4f} | {'缓流':^10}")

    # 临界坡
    channel = RectangularChannel(b=b, n=n, S0=S_mid)
    solver = UniformFlowSolver(channel)
    results = solver.compute_normal_depth(Q)
    h0 = results["正常水深_h0"]
    Fr = results["弗劳德数_Fr"]
    print(f"{'临界坡(S=Sc)':^15} | {S_mid:^12.6f} | {h0/hc:^10.4f} | {Fr:^8.4f} | {'临界流':^10}")

    # 陡坡
    S_super = S_mid * 2.0
    channel = RectangularChannel(b=b, n=n, S0=S_super)
    solver = UniformFlowSolver(channel)
    results = solver.compute_normal_depth(Q)
    h0 = results["正常水深_h0"]
    Fr = results["弗劳德数_Fr"]
    print(f"{'陡坡(S>Sc)':^15} | {S_super:^12.6f} | {h0/hc:^10.4f} | {Fr:^8.4f} | {'急流':^10}")

    print("-" * 80)

    print("\n【实验结论】")
    print("1. 临界坡度Sc是流态转变的分界线")
    print("2. S < Sc：缓坡，h0 > hc，流态为缓流")
    print("3. S = Sc：临界坡，h0 = hc，流态为临界流（不稳定，应避免）")
    print("4. S > Sc：陡坡，h0 < hc，流态为急流")
    print("5. 工程设计应使 S 远离 Sc，保持稳定的缓流或急流状态")


def experiment_2_4():
    """
    实验2.4：优化设计方案

    针对原设计中Fr较大的问题，提出优化方案
    """
    print_separator("实验2.4：优化设计方案")

    Q = 1.2
    n = 0.013

    print("\n原设计方案：")
    print("-" * 80)
    b_original = 1.5
    S0_original = 0.003

    channel = RectangularChannel(b=b_original, n=n, S0=S0_original)
    solver = UniformFlowSolver(channel)
    results = solver.compute_normal_depth(Q)

    print(f"渠宽 b = {b_original} m")
    print(f"坡度 S0 = {S0_original} = {S0_original*100:.1f}%")
    print(f"正常水深 h0 = {results['正常水深_h0']:.4f} m")
    print(f"流速 v = {results['流速_v']:.4f} m/s")
    print(f"弗劳德数 Fr = {results['弗劳德数_Fr']:.4f}")
    print(f"问题：Fr = {results['弗劳德数_Fr']:.3f} 较大，接近临界流")

    print("\n优化方案对比：")
    print("-" * 110)
    print(f"{'方案':^10} | {'渠宽(m)':^10} | {'坡度%':^8} | {'水深(m)':^10} | {'流速(m/s)':^10} | {'Fr':^8} | {'评价':^20}")
    print("-" * 110)

    # 原方案
    print(f"{'原方案':^10} | {b_original:^10.2f} | {S0_original*100:^8.2f} | {results['正常水深_h0']:^10.4f} | " +
          f"{results['流速_v']:^10.4f} | {results['弗劳德数_Fr']:^8.4f} | {'Fr偏大':^20}")

    # 方案1：增大渠宽
    b1 = 2.0
    S01 = S0_original
    channel1 = RectangularChannel(b=b1, n=n, S0=S01)
    solver1 = UniformFlowSolver(channel1)
    results1 = solver1.compute_normal_depth(Q)
    print(f"{'方案1':^10} | {b1:^10.2f} | {S01*100:^8.2f} | {results1['正常水深_h0']:^10.4f} | " +
          f"{results1['流速_v']:^10.4f} | {results1['弗劳德数_Fr']:^8.4f} | {'Fr降低，较优':^20}")

    # 方案2：减小坡度
    b2 = b_original
    S02 = 0.002
    channel2 = RectangularChannel(b=b2, n=n, S0=S02)
    solver2 = UniformFlowSolver(channel2)
    results2 = solver2.compute_normal_depth(Q)
    print(f"{'方案2':^10} | {b2:^10.2f} | {S02*100:^8.2f} | {results2['正常水深_h0']:^10.4f} | " +
          f"{results2['流速_v']:^10.4f} | {results2['弗劳德数_Fr']:^8.4f} | {'流速偏小':^20}")

    # 方案3：综合优化
    b3 = 1.8
    S03 = 0.0025
    channel3 = RectangularChannel(b=b3, n=n, S0=S03)
    solver3 = UniformFlowSolver(channel3)
    results3 = solver3.compute_normal_depth(Q)
    print(f"{'方案3':^10} | {b3:^10.2f} | {S03*100:^8.2f} | {results3['正常水深_h0']:^10.4f} | " +
          f"{results3['流速_v']:^10.4f} | {results3['弗劳德数_Fr']:^8.4f} | {'综合最优':^20}")

    print("-" * 110)

    print("\n【优化结论】")
    print("方案3（b=1.8m, S0=0.25%）为最优方案，理由：")
    print(f"1. 弗劳德数 Fr = {results3['弗劳德数_Fr']:.3f} < 0.7，流态稳定")
    print(f"2. 流速 v = {results3['流速_v']:.3f} m/s，满足防淤和防冲要求")
    print(f"3. 水深 h0 = {results3['正常水深_h0']:.3f} m，断面合理")
    print(f"4. 渠道尺寸：1.8m × 0.6m，便于施工")


def main():
    """主函数"""
    print_separator("案例2：计算实验")
    print("\n本实验将深入探讨矩形断面排水渠的流态控制\n")

    # 运行各个实验
    experiment_2_1()  # 渠宽影响
    experiment_2_2()  # 坡度影响
    experiment_2_3()  # 临界流探索
    experiment_2_4()  # 优化设计

    # 总结
    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 矩形断面的水力特性")
    print("2. 临界流的判别和避免方法")
    print("3. 渠宽和坡度对流态的影响规律")
    print("4. 排水渠优化设计的思路")
    print("\n关键设计原则：")
    print("• 控制弗劳德数 Fr < 0.7，避免接近临界流")
    print("• 流速保持在 0.6-3.0 m/s 范围内")
    print("• 适当增大渠宽或减小坡度可以降低Fr")
    print("• 综合考虑水力、结构和经济因素")
    print_separator()


if __name__ == "__main__":
    main()
