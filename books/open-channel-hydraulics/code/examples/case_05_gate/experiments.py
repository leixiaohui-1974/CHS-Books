"""
案例5：渠道闸门出流计算 - 计算实验

实验内容：
1. 实验5.1：闸门开度 e 对流量的影响
2. 实验5.2：上游水头 H 对流量的影响
3. 实验5.3：淹没度对流量的影响分析
4. 实验5.4：流量系数对流量的影响
5. 实验5.5：最优开度分析

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.structures import Gate


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def experiment_5_1():
    """
    实验5.1：闸门开度 e 对流量的影响

    保持其他参数不变，改变闸门开度，观察流量变化
    """
    print_separator("实验5.1：闸门开度 e 对流量的影响")

    # 基本参数
    b = 2.0
    mu = 0.60
    H = 3.0

    # 不同的闸门开度
    e_values = np.arange(0.2, 2.1, 0.2)

    gate = Gate(b=b, mu=mu)

    print(f"\n固定参数：b = {b} m, μ = {mu}, H = {H} m")
    print("\n不同闸门开度的流量对比：")
    print("-" * 100)
    print(f"{'开度e(m)':^12} | {'流量Q(m³/s)':^15} | {'单宽流量q(m²/s)':^18} | {'闸下流速v(m/s)':^16}")
    print("-" * 100)

    for e in e_values:
        Q = gate.discharge_free(e, H)
        q = Q / b
        v = Q / (b * e)

        print(f"{e:^12.2f} | {Q:^15.4f} | {q:^18.4f} | {v:^16.4f}")

    print("-" * 100)

    # 分析结论
    print("\n【实验结论】")
    print("1. 流量与开度成正比：Q = μ * b * e * sqrt(2gH)，Q ∝ e")
    print("2. 单宽流量 q 随开度线性增加")
    print("3. 闸下平均流速 v = Q/(b*e) 保持恒定（约4.60 m/s）")
    print("4. 工程应用：")
    print("   - 调节开度可以精确控制流量")
    print("   - 开度增大一倍，流量增大一倍")
    print("   - 闸门是良好的流量调节装置")


def experiment_5_2():
    """
    实验5.2：上游水头 H 对流量的影响

    保持开度不变，改变上游水头，观察流量变化
    """
    print_separator("实验5.2：上游水头 H 对流量的影响")

    # 基本参数
    b = 2.0
    mu = 0.60
    e = 0.8

    # 不同的上游水头
    H_values = np.arange(1.0, 5.1, 0.5)

    gate = Gate(b=b, mu=mu)

    print(f"\n固定参数：b = {b} m, μ = {mu}, e = {e} m")
    print("\n不同上游水头的流量对比：")
    print("-" * 100)
    print(f"{'上游水头H(m)':^15} | {'流量Q(m³/s)':^15} | {'sqrt(H)':^12} | {'Q/Q₀比值':^15}")
    print("-" * 100)

    Q0 = None
    for H in H_values:
        Q = gate.discharge_free(e, H)
        sqrt_H = np.sqrt(H)

        if Q0 is None:
            Q0 = Q
            ratio = 1.0
        else:
            ratio = Q / Q0

        print(f"{H:^15.2f} | {Q:^15.4f} | {sqrt_H:^12.4f} | {ratio:^15.3f}")

    print("-" * 100)

    # 分析结论
    print("\n【实验结论】")
    print("1. 流量与水头的平方根成正比：Q ∝ sqrt(H)")
    print("2. 水头增大4倍，流量增大2倍")
    print("3. 上游水位变化对流量影响显著")
    print("4. 工程意义：")
    print("   - 维持恒定流量需要稳定的上游水位")
    print("   - 上游水位波动会导致流量波动")
    print("   - 可以通过调节开度补偿水位变化")


def experiment_5_3():
    """
    实验5.3：淹没度对流量的影响分析

    固定上游水深和开度，改变下游水深，分析淹没效应
    """
    print_separator("实验5.3：淹没度对流量的影响分析")

    # 基本参数
    b = 2.0
    mu = 0.60
    H1 = 3.0
    e = 0.8

    gate = Gate(b=b, mu=mu)

    # 不同的下游水深
    H2_values = np.arange(0.5, 3.0, 0.25)

    print(f"\n固定参数：b = {b} m, μ = {mu}, H1 = {H1} m, e = {e} m")
    print("\n不同下游水深的淹没影响：")
    print("-" * 120)
    print(f"{'下游水深H2(m)':^15} | {'淹没度σ':^12} | {'自由流量(m³/s)':^16} | {'淹没流量(m³/s)':^16} | {'流量比':^12} | {'出流状态':^12}")
    print("-" * 120)

    Q_free = gate.discharge_free(e, H1)

    for H2 in H2_values:
        sigma = H2 / H1
        is_submerged = gate.check_submergence(e, H1, H2)

        if is_submerged and H2 < H1:
            try:
                Q_sub = gate.discharge_submerged(e, H1, H2)
                Q_ratio = Q_sub / Q_free
                flow_state = "淹没"
            except:
                Q_sub = 0.0
                Q_ratio = 0.0
                flow_state = "无效"
        else:
            Q_sub = Q_free
            Q_ratio = 1.0
            flow_state = "自由"

        print(f"{H2:^15.2f} | {sigma:^12.3f} | {Q_free:^16.4f} | {Q_sub:^16.4f} | {Q_ratio:^12.3f} | {flow_state:^12}")

    print("-" * 120)

    # 分析结论
    print("\n【实验结论】")
    print("1. 淹没度 σ = H2/H1 是判断出流形态的关键参数")
    print("2. σ < 0.6：自由出流，流量不受下游水深影响")
    print("3. σ > 0.6：淹没出流，流量随下游水深增加而减小")
    print("4. 完全淹没时（σ→1），流量趋近于零")
    print("5. 工程对策：")
    print("   - 控制下游水位，避免淹没")
    print("   - 设置消力池，降低下游水位")
    print("   - 淹没运行时，需增大开度以保证设计流量")


def experiment_5_4():
    """
    实验5.4：流量系数对流量的影响

    不同类型闸门的流量系数不同，影响过流能力
    """
    print_separator("实验5.4：流量系数对流量的影响")

    # 基本参数
    b = 2.0
    H = 3.0
    e = 0.8

    # 不同的流量系数
    mu_values = [0.50, 0.55, 0.60, 0.65, 0.70]
    mu_descriptions = [
        "深孔闸门（矩形）",
        "老旧平板闸门",
        "标准平板闸门",
        "良好平板闸门",
        "弧形闸门"
    ]

    print(f"\n固定参数：b = {b} m, H = {H} m, e = {e} m")
    print("\n不同流量系数的对比：")
    print("-" * 110)
    print(f"{'流量系数μ':^12} | {'闸门类型':^20} | {'流量Q(m³/s)':^15} | {'与标准值差异(%)':^20}")
    print("-" * 110)

    Q_standard = None
    for mu, desc in zip(mu_values, mu_descriptions):
        gate = Gate(b=b, mu=mu)
        Q = gate.discharge_free(e, H)

        if abs(mu - 0.60) < 1e-6:
            Q_standard = Q
            diff = 0.0
        elif Q_standard is not None:
            diff = (Q - Q_standard) / Q_standard * 100
        else:
            diff = 0.0

        print(f"{mu:^12.3f} | {desc:^20} | {Q:^15.4f} | {diff:^20.2f}")

    print("-" * 110)

    # 分析结论
    print("\n【实验结论】")
    print("1. 流量系数反映闸门的过流性能")
    print("2. 弧形闸门流量系数最大（μ≈0.65-0.70）")
    print("3. 平板闸门流量系数适中（μ≈0.60）")
    print("4. 深孔闸门流量系数较小（μ≈0.50-0.55）")
    print("5. 流量系数的影响因素：")
    print("   - 闸门形状（弧形、平板、深孔）")
    print("   - 闸底与渠底的平齐程度")
    print("   - 闸门开度与水头的比值 e/H")
    print("   - 侧收缩程度")
    print("6. 工程建议：")
    print("   - 新建闸门应进行现场流量率定")
    print("   - 定期检测流量系数变化")
    print("   - 老化闸门流量系数会降低，需要维修")


def experiment_5_5():
    """
    实验5.5：最优开度分析

    在给定流量下，分析不同开度和水头组合的优劣
    """
    print_separator("实验5.5：最优开度分析")

    # 基本参数
    b = 2.0
    mu = 0.60
    Q_target = 8.0  # 目标流量

    gate = Gate(b=b, mu=mu)

    # 不同的上游水头
    H_values = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

    print(f"\n目标流量：Q = {Q_target} m³/s")
    print(f"闸门宽度：b = {b} m，流量系数：μ = {mu}")
    print("\n不同水头下的开度方案对比：")
    print("-" * 110)
    print(f"{'上游水头H(m)':^15} | {'所需开度e(m)':^16} | {'开度比e/H':^13} | {'闸下流速v(m/s)':^16} | {'方案评价':^20}")
    print("-" * 110)

    for H in H_values:
        e = gate.opening_from_discharge(Q_target, H)
        e_ratio = e / H
        v = Q_target / (b * e)

        # 评价方案
        if e < 0.1:
            evaluation = "开度过小，易堵塞"
        elif e > 0.8 * H:
            evaluation = "开度过大，不稳定"
        elif v > 6.0:
            evaluation = "流速过大，易冲刷"
        elif e_ratio < 0.15:
            evaluation = "调节范围小"
        elif 0.2 <= e_ratio <= 0.4:
            evaluation = "最优方案★★★"
        else:
            evaluation = "可行方案★★"

        print(f"{H:^15.2f} | {e:^16.4f} | {e_ratio:^13.3f} | {v:^16.4f} | {evaluation:^20}")

    print("-" * 110)

    # 分析结论
    print("\n【实验结论】")
    print("1. 给定流量可以由不同的（H, e）组合实现")
    print("2. 最优开度比：e/H = 0.2-0.4")
    print("   - 开度不太小，避免堵塞和调节困难")
    print("   - 开度不太大，保证出流稳定")
    print("   - 闸下流速适中，减小冲刷")
    print("3. 高水头小开度方案：")
    print("   - 优点：节省闸门高度，减小启闭力")
    print("   - 缺点：调节灵敏度差，流速大")
    print("4. 低水头大开度方案：")
    print("   - 优点：调节灵活，流速小")
    print("   - 缺点：需要较高的闸门")
    print("5. 工程设计建议：")
    print("   - 根据地形条件选择合理的设计水头")
    print("   - 保证闸门开度在0.2H-0.6H范围")
    print("   - 设置调节范围，应对流量变化")


def main():
    """主函数"""
    print_separator("案例5：计算实验")
    print("\n本实验将探讨闸门出流的各种影响因素\n")

    # 运行各个实验
    experiment_5_1()  # 闸门开度影响
    experiment_5_2()  # 上游水头影响
    experiment_5_3()  # 淹没度影响
    experiment_5_4()  # 流量系数影响
    experiment_5_5()  # 最优开度分析

    # 总结
    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 开度e：流量与开度成正比，是最主要的调节手段")
    print("2. 水头H：流量与水头平方根成正比，上游水位需要稳定")
    print("3. 淹没度σ：控制下游水位，避免淹没影响流量")
    print("4. 流量系数μ：反映闸门性能，需要现场率定")
    print("5. 最优开度：e/H = 0.2-0.4，兼顾调节性和稳定性")
    print("\n这些参数的合理选择，是闸门水力设计和运行调度的关键！")
    print_separator()


if __name__ == "__main__":
    main()
