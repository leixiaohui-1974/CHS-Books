"""
案例3：景观水渠水流状态分析 - 计算实验

实验内容：
1. 实验3.1：比能曲线的数值分析
2. 实验3.2：不同流量的比能曲线对比
3. 实验3.3：水跃共轭水深分析

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import RectangularChannel


def specific_energy(Q, b, h, g=9.81):
    """计算比能"""
    A = b * h
    v = Q / A
    E = h + v**2 / (2*g)
    return E


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def experiment_3_1():
    """
    实验3.1：比能曲线的数值分析

    绘制给定流量下的比能曲线
    """
    print_separator("实验3.1：比能曲线的数值分析")

    b = 2.0
    Q = 1.0
    g = 9.81

    # 临界水深
    q = Q / b
    hc = (q**2 / g) ** (1.0/3.0)
    Ec = 1.5 * hc

    print(f"\n流量 Q = {Q} m³/s，渠宽 b = {b} m")
    print(f"临界水深 hc = {hc:.4f} m")
    print(f"最小比能 Ec = {Ec:.4f} m\n")

    print("比能曲线数据表：")
    print("-" * 90)
    print(f"{'水深h(m)':^12} | {'流速v(m/s)':^12} | {'动能v²/2g(m)':^15} | {'比能E(m)':^12} | {'Fr':^8} | {'流态':^8}")
    print("-" * 90)

    # 生成水深序列
    h_values = np.concatenate([
        np.linspace(0.1, hc-0.05, 5),
        [hc],
        np.linspace(hc+0.05, 1.0, 8)
    ])

    for h in h_values:
        A = b * h
        v = Q / A
        KE = v**2 / (2*g)
        E = specific_energy(Q, b, h, g)
        Fr = v / np.sqrt(g * h)
        flow_type = "急流" if Fr > 1.05 else ("临界" if Fr > 0.95 else "缓流")
        marker = " *" if abs(h - hc) < 0.01 else ""

        print(f"{h:^12.4f} | {v:^12.4f} | {KE:^15.4f} | {E:^12.4f} | {Fr:^8.4f} | {flow_type:^8}{marker}")

    print("-" * 90)
    print("注：* 标记表示临界点（比能最小点）")

    print("\n【实验结论】")
    print("1. 比能曲线呈 U 型，存在最小值")
    print("2. 最小比能点对应临界水深（Fr = 1）")
    print("3. 同一比能可对应两个水深：")
    print("   - h > hc：缓流水深（Fr < 1，动能小，势能大）")
    print("   - h < hc：急流水深（Fr > 1，动能大，势能小）")
    print("4. 离临界点越远，比能越大，能量损失越小")


def experiment_3_2():
    """
    实验3.2：不同流量的比能曲线对比

    比较不同流量下的比能曲线特征
    """
    print_separator("实验3.2：不同流量的比能曲线对比")

    b = 2.0
    g = 9.81

    Q_values = [0.5, 1.0, 1.5, 2.0]

    print(f"\n不同流量下的临界点对比（渠宽 b = {b} m）：")
    print("-" * 80)
    print(f"{'流量Q(m³/s)':^15} | {'临界水深hc(m)':^18} | {'最小比能Ec(m)':^18} | {'临界流速vc(m/s)':^18}")
    print("-" * 80)

    for Q in Q_values:
        q = Q / b
        hc = (q**2 / g) ** (1.0/3.0)
        Ec = 1.5 * hc
        vc = q / hc

        print(f"{Q:^15.2f} | {hc:^18.4f} | {Ec:^18.4f} | {vc:^18.4f}")

    print("-" * 80)

    print("\n比能曲线特征对比：")
    print("\n当水深 h = 0.5 m 时，不同流量的比能和流态：")
    print("-" * 80)
    print(f"{'流量Q(m³/s)':^15} | {'流速v(m/s)':^15} | {'比能E(m)':^15} | {'Fr':^10} | {'流态':^10}")
    print("-" * 80)

    h_fixed = 0.5
    for Q in Q_values:
        A = b * h_fixed
        v = Q / A
        E = specific_energy(Q, b, h_fixed, g)
        Fr = v / np.sqrt(g * h_fixed)
        flow_type = "急流" if Fr > 1.05 else ("临界" if Fr > 0.95 else "缓流")

        print(f"{Q:^15.2f} | {v:^15.4f} | {E:^15.4f} | {Fr:^10.4f} | {flow_type:^10}")

    print("-" * 80)

    print("\n【实验结论】")
    print("1. 流量越大，临界水深和最小比能都越大")
    print("2. 临界水深与流量的关系：hc ∝ Q^(2/3)")
    print("3. 最小比能与流量的关系：Ec ∝ Q^(2/3)")
    print("4. 相同水深下，流量越大，弗劳德数越大，越容易出现急流")


def experiment_3_3():
    """
    实验3.3：水跃共轭水深分析

    分析水跃前后的水深关系
    """
    print_separator("实验3.3：水跃共轭水深分析")

    b = 2.0
    Q = 1.0
    g = 9.81

    print(f"\n水跃共轭水深关系（矩形断面）：")
    print(f"流量 Q = {Q} m³/s，渠宽 b = {b} m\n")

    print("给定急流水深 h1，计算跃后缓流水深 h2：")
    print("-" * 100)
    print(f"{'急流水深h1(m)':^15} | {'急流流速v1(m/s)':^18} | {'Fr1':^10} | {'缓流水深h2(m)':^18} | {'缓流流速v2(m/s)':^18}")
    print("-" * 100)

    # 急流水深序列
    h1_values = [0.15, 0.20, 0.25, 0.30]

    for h1 in h1_values:
        A1 = b * h1
        v1 = Q / A1
        Fr1 = v1 / np.sqrt(g * h1)

        # 共轭水深公式（矩形断面）
        # h2 = h1/2 * (sqrt(1 + 8*Fr1^2) - 1)
        h2 = h1 / 2 * (np.sqrt(1 + 8*Fr1**2) - 1)

        A2 = b * h2
        v2 = Q / A2

        print(f"{h1:^15.4f} | {v1:^18.4f} | {Fr1:^10.4f} | {h2:^18.4f} | {v2:^18.4f}")

    print("-" * 100)

    print("\n能量损失分析：")
    print("-" * 100)
    print(f"{'急流水深h1(m)':^15} | {'比能E1(m)':^15} | {'缓流水深h2(m)':^18} | {'比能E2(m)':^15} | {'能量损失ΔE(m)':^18}")
    print("-" * 100)

    for h1 in h1_values:
        E1 = specific_energy(Q, b, h1, g)

        # 共轭水深
        A1 = b * h1
        v1 = Q / A1
        Fr1 = v1 / np.sqrt(g * h1)
        h2 = h1 / 2 * (np.sqrt(1 + 8*Fr1**2) - 1)

        E2 = specific_energy(Q, b, h2, g)
        dE = E1 - E2

        print(f"{h1:^15.4f} | {E1:^15.4f} | {h2:^18.4f} | {E2:^15.4f} | {dE:^18.4f}")

    print("-" * 100)

    print("\n【实验结论】")
    print("1. 水跃前后水深满足共轭水深关系：h2 = h1/2 * (sqrt(1 + 8*Fr1²) - 1)")
    print("2. Fr1 越大（急流越强），h2/h1 比值越大（水跃越剧烈）")
    print("3. 水跃过程中有能量损失（ΔE > 0），用于消能")
    print("4. Fr1 越大，能量损失越多，消能效果越好")
    print("5. 水跃前后动量守恒，但能量不守恒（部分转化为热能和紊动能）")


def main():
    """主函数"""
    print_separator("案例3：计算实验")
    print("\n本实验将深入探讨比能曲线和水跃现象\n")

    # 运行各个实验
    experiment_3_1()  # 比能曲线分析
    experiment_3_2()  # 不同流量对比
    experiment_3_3()  # 水跃分析

    # 总结
    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 比能曲线的形状和物理意义")
    print("2. 临界流是比能最小的状态")
    print("3. 共轭水深的概念和计算方法")
    print("4. 水跃的能量损失特征")
    print("\n实际应用：")
    print("• 比能曲线：分析水流状态，判断流态转换")
    print("• 临界流：设计中应避免，保持稳定流态")
    print("• 水跃：用于消能工设计，如溢洪道、跌水等")
    print("• 景观设计：利用不同Fr值制造不同的水景效果")
    print_separator()


if __name__ == "__main__":
    main()
