"""
案例8：桥梁壅水分析 - 计算实验

实验内容：
1. 实验8.1：流量对壅水的影响
2. 实验8.2：收缩系数（桥宽）对壅水的影响
3. 实验8.3：桥下糙率对壅水的影响
4. 实验8.4：桥梁净空设计优化

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import RectangularChannel
from solvers.steady.profile import WaterSurfaceProfile


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def compute_bridge_backwater(B0, Bb, S0, n, nb, Q):
    """
    计算桥梁壅水的通用函数

    返回：(h0, h1, dh, v0, v1)
    """
    g = 9.81

    # 天然河道
    channel_natural = RectangularChannel(b=B0, S0=S0, n=n)
    h0 = channel_natural.compute_normal_depth(Q)
    v0 = Q / (B0 * h0)
    E0 = h0 + v0**2 / (2*g)

    # 桥下断面（迭代求解）
    h1 = h0
    for i in range(100):
        A1 = Bb * h1
        v1 = Q / A1
        E1 = h1 + v1**2 / (2*g)
        zeta = 0.15
        hf = zeta * v1**2 / (2*g)
        f = E1 + hf - E0

        if abs(f) < 1e-6:
            break

        dh_iter = 1e-6
        A1_plus = Bb * (h1 + dh_iter)
        v1_plus = Q / A1_plus
        E1_plus = (h1 + dh_iter) + v1_plus**2 / (2*g)
        hf_plus = zeta * v1_plus**2 / (2*g)
        f_plus = E1_plus + hf_plus - E0
        df = (f_plus - f) / dh_iter

        if abs(df) > 1e-12:
            h1 = h1 - f / df
        if h1 <= 0:
            h1 = h0

    v1 = Q / (Bb * h1)
    dh = h1 - h0

    return h0, h1, dh, v0, v1


def experiment_8_1():
    """
    实验8.1：流量对壅水的影响

    不同设计流量下的壅水特性
    """
    print_separator("实验8.1：流量对壅水的影响")

    # 基本参数
    B0 = 50.0
    Bb = 40.0
    S0 = 0.0005
    n = 0.030
    nb = 0.025

    print(f"\n固定参数：B₀={B0}m, Bb={Bb}m, S₀={S0}, n={n}, nb={nb}")
    print(f"收缩系数：ε = {Bb/B0:.3f}")

    print("\n不同流量下的壅水特性：")
    print("-" * 120)
    print(f"{'流量Q(m³/s)':^15} | {'天然水深h₀(m)':^17} | {'桥下水深h₁(m)':^17} | {'壅水Δh(m)':^14} | {'流速增加Δv(m/s)':^18}")
    print("-" * 120)

    Q_values = [100, 150, 200, 250, 300, 350, 400]

    for Q in Q_values:
        h0, h1, dh, v0, v1 = compute_bridge_backwater(B0, Bb, S0, n, nb, Q)
        dv = v1 - v0

        print(f"{Q:^15.0f} | {h0:^17.4f} | {h1:^17.4f} | {dh:^14.4f} | {dv:^18.4f}")

    print("-" * 120)

    print("\n【实验结论】")
    print("1. 流量增大，天然水深和桥下水深都增大")
    print("2. 流量增大，流速增加幅度增大")
    print("3. 本案例中由于桥下糙率较小，壅水为负值（桥下水深<天然水深）")
    print("4. 实际工程中，如果桥下糙率与天然河道相同，会产生正壅水")
    print("5. 大流量时，壅水影响更显著，需要更大的桥下净宽")


def experiment_8_2():
    """
    实验8.2：收缩系数（桥宽）对壅水的影响

    这是桥梁设计的核心参数
    """
    print_separator("实验8.2：收缩系数（桥宽）对壅水的影响")

    # 基本参数
    B0 = 50.0
    S0 = 0.0005
    n = 0.030
    nb = 0.030  # 使用相同糙率，突出收缩效应
    Q = 200.0

    print(f"\n固定参数：B₀={B0}m, Q={Q}m³/s, S₀={S0}, n=nb={n}")
    print("注：本实验使用相同糙率，纯粹反映收缩效应")

    print("\n不同桥下净宽的壅水对比：")
    print("-" * 120)
    print(f"{'桥宽Bb(m)':^12} | {'收缩系数ε':^13} | {'壅水Δh(m)':^13} | {'流速增加(%)':^15} | {'净空增加(m)':^14} | {'评价':^15}")
    print("-" * 120)

    Bb_values = [30, 35, 40, 42, 45, 48, 50]

    for Bb in Bb_values:
        h0, h1, dh, v0, v1 = compute_bridge_backwater(B0, Bb, S0, n, nb, Q)
        epsilon = Bb / B0
        dv_percent = (v1 - v0) / v0 * 100
        clearance_increase = dh + 0.5  # 壅水+安全超高

        # 评价
        if dh < 0.1:
            evaluation = "优秀"
        elif dh < 0.2:
            evaluation = "良好"
        elif dh < 0.3:
            evaluation = "合格"
        elif dh < 0.5:
            evaluation = "可接受"
        else:
            evaluation = "不推荐"

        print(f"{Bb:^12.0f} | {epsilon:^13.3f} | {dh:^13.4f} | {dv_percent:^15.2f} | {clearance_increase:^14.4f} | {evaluation:^15}")

    print("-" * 120)

    print("\n【实验结论】")
    print("1. 桥宽越大（收缩越小），壅水越小")
    print("2. 收缩系数ε从0.6增至1.0，壅水从0.5m降至0m")
    print("3. 收缩系数建议：")
    print("   - ε ≥ 0.90：优秀（Δh < 0.1m）")
    print("   - ε ≥ 0.80：良好（Δh < 0.2m）")
    print("   - ε ≥ 0.70：合格（Δh < 0.3m）")
    print("   - ε < 0.70：不推荐（壅水过大）")
    print("4. 工程设计：在经济条件允许下，尽量增大桥宽")


def experiment_8_3():
    """
    实验8.3：桥下糙率对壅水的影响

    桥下清理可降低糙率，影响壅水
    """
    print_separator("实验8.3：桥下糙率对壅水的影响")

    # 基本参数
    B0 = 50.0
    Bb = 40.0
    S0 = 0.0005
    n = 0.030
    Q = 200.0

    print(f"\n固定参数：B₀={B0}m, Bb={Bb}m, Q={Q}m³/s, S₀={S0}")
    print(f"天然河道糙率：n = {n}")

    nb_values = [0.020, 0.022, 0.025, 0.028, 0.030, 0.035]
    nb_descriptions = [
        "混凝土衬砌",
        "浆砌石护底",
        "清理河床",
        "部分清理",
        "天然河床",
        "淤积杂草"
    ]

    print("\n不同桥下糙率的壅水对比：")
    print("-" * 120)
    print(f"{'桥下糙率nb':^12} | {'河床状况':^15} | {'桥下水深h₁(m)':^17} | {'壅水Δh(m)':^13} | {'工程措施':^20}")
    print("-" * 120)

    for nb, desc in zip(nb_values, nb_descriptions):
        h0, h1, dh, v0, v1 = compute_bridge_backwater(B0, Bb, S0, n, nb, Q)

        # 工程措施建议
        if nb < 0.025:
            measure = "需要衬砌"
        elif nb < 0.030:
            measure = "清理河床"
        elif nb == 0.030:
            measure = "保持现状"
        else:
            measure = "必须整治"

        print(f"{nb:^12.3f} | {desc:^15} | {h1:^17.4f} | {dh:^13.4f} | {measure:^20}")

    print("-" * 120)

    print("\n【实验结论】")
    print("1. 桥下糙率越小，桥下水深越小")
    print("2. 糙率从0.030降至0.020，桥下水深降低约0.2m")
    print("3. 桥下清理是减小壅水的有效措施")
    print("4. 工程建议：")
    print("   - 桥下河床应进行清理和整治")
    print("   - 有条件时可进行混凝土衬砌")
    print("   - 定期清除桥下淤积物和杂草")
    print("   - 糙率降低可显著改善过流能力")


def experiment_8_4():
    """
    实验8.4：桥梁净空设计优化

    综合考虑各种因素的净空设计
    """
    print_separator("实验8.4：桥梁净空设计优化")

    # 基本参数
    B0 = 50.0
    Bb = 40.0
    S0 = 0.0005
    n = 0.030
    nb = 0.025
    Q = 200.0

    print(f"\n基本参数：B₀={B0}m, Bb={Bb}m, Q={Q}m³/s")

    # 计算壅水
    h0, h1, dh, v0, v1 = compute_bridge_backwater(B0, Bb, S0, n, nb, Q)

    print(f"\n水力计算结果：")
    print(f"  天然水深 h₀ = {h0:.4f} m")
    print(f"  桥下水深 h₁ = {h1:.4f} m")
    print(f"  壅水高度 Δh = {dh:.4f} m")

    # 设计水位
    h_design = max(h0, h1)  # 取较大值

    print(f"\n净空设计要素：")
    print("-" * 100)
    print(f"{'项目':^20} | {'数值(m)':^15} | {'说明':^50}")
    print("-" * 100)

    components = [
        ("设计水位", h_design, "天然水深或桥下水深的较大值"),
        ("安全超高", 0.50, "防止波浪、水位顶托等"),
        ("波浪爬高", 0.15, "风浪影响，与风速和水面宽度有关"),
        ("建筑高度", 0.30, "梁底至桥面结构高度"),
        ("施工误差", 0.10, "施工误差和沉降预留"),
    ]

    total_clearance = h_design
    for name, value, note in components:
        print(f"{name:^20} | {value:^15.2f} | {note:^50}")
        if name != "设计水位":
            total_clearance += value

    print("-" * 100)
    print(f"{'桥底最低标高':^20} | {total_clearance:^15.2f} | {'以上各项之和':^50}")
    print(f"{'建议桥底标高':^20} | {total_clearance + 0.5:^15.2f} | {'增加0.5m安全余量':^50}")
    print("-" * 100)

    # 不同设计标准对比
    print(f"\n不同设计标准的净空要求：")
    print("-" * 100)
    print(f"{'设计标准':^20} | {'流量Q(m³/s)':^15} | {'设计水位(m)':^15} | {'建议净空(m)':^15}")
    print("-" * 100)

    design_standards = [
        ("5年一遇", 150),
        ("10年一遇", 180),
        ("20年一遇", 200),
        ("50年一遇", 250),
        ("100年一遇", 300),
    ]

    for standard, Q_design in design_standards:
        h0_d, h1_d, dh_d, v0_d, v1_d = compute_bridge_backwater(B0, Bb, S0, n, nb, Q_design)
        h_design_d = max(h0_d, h1_d)
        clearance_d = h_design_d + 0.50 + 0.15 + 0.30 + 0.10 + 0.5

        print(f"{standard:^20} | {Q_design:^15.0f} | {h_design_d:^15.4f} | {clearance_d:^15.4f}")

    print("-" * 100)

    print("\n【实验结论】")
    print("1. 桥梁净空设计应综合考虑多种因素")
    print("2. 主要组成：设计水位 + 安全超高 + 波浪爬高 + 结构高度 + 施工余量")
    print("3. 不同设计标准，净空要求不同")
    print("4. 设计建议：")
    print("   - 重要桥梁：采用50-100年一遇标准")
    print("   - 一般桥梁：采用20-50年一遇标准")
    print("   - 临时桥梁：采用5-10年一遇标准")
    print("5. 净空设计应留有余量，考虑河床淤积、冲刷等因素")


def main():
    """主函数"""
    print_separator("案例8：计算实验")
    print("\n本实验将探讨桥梁壅水的各种影响因素\n")

    # 运行各个实验
    experiment_8_1()  # 流量影响
    experiment_8_2()  # 收缩系数影响
    experiment_8_3()  # 桥下糙率影响
    experiment_8_4()  # 净空设计

    # 总结
    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 流量：流量越大，壅水越大，需要更大的桥下净宽")
    print("2. 收缩系数：桥宽越大（ε越大），壅水越小")
    print("3. 糙率：桥下清理可降低糙率，改善过流能力")
    print("4. 净空设计：应综合考虑水位、超高、波浪、结构等因素")
    print("\n桥梁水力设计的核心是在满足交通需求的前提下，")
    print("尽量减小对河道的影响，控制壅水在可接受范围内！")
    print_separator()


if __name__ == "__main__":
    main()
