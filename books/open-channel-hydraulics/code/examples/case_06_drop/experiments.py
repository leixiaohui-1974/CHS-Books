"""
案例6：跌水消能设计 - 计算实验

实验内容：
1. 实验6.1：跌水高度对消能效率的影响
2. 实验6.2：流量对水跃特性的影响
3. 实验6.3：弗劳德数与消能效率的关系
4. 实验6.4：最优跌水高度设计

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.structures import HydraulicJump


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def experiment_6_1():
    """
    实验6.1：跌水高度对消能效率的影响
    """
    print_separator("实验6.1：跌水高度对消能效率的影响")

    # 基本参数
    Q = 5.0
    b = 2.5
    h0 = 1.2
    g = 9.81

    jump = HydraulicJump(b=b)

    # 上游比能
    v0 = Q / (b * h0)
    E0 = h0 + v0**2 / (2*g)

    # 临界水深
    q = Q / b
    hc = (q**2 / g) ** (1.0/3.0)

    print(f"\n基础条件：Q = {Q} m³/s, b = {b} m, h0 = {h0} m")
    print(f"临界水深：hc = {hc:.4f} m")
    print("\n不同跌水高度的消能效果：")
    print("-" * 120)
    print(f"{'跌水Δz(m)':^12} | {'跃前h1(m)':^12} | {'跃前Fr1':^12} | {'跃后h2(m)':^12} | {'能量损失(m)':^14} | {'消散效率(%)':^14}")
    print("-" * 120)

    dz_values = np.arange(0.5, 4.1, 0.5)

    for dz in dz_values:
        E1 = E0 + dz

        # 求跌水后水深（急流解）
        h1 = hc * 0.5
        for i in range(100):
            E1_calc = h1 + Q**2 / (2 * g * (b * h1)**2)
            f = E1_calc - E1

            if abs(f) < 1e-6:
                break

            dh = 1e-6
            E1_plus = (h1 + dh) + Q**2 / (2 * g * (b * (h1 + dh))**2)
            df = (E1_plus - E1_calc) / dh

            h1 = h1 - f / df
            if h1 <= 0:
                h1 = hc / 2
            elif h1 > hc:
                h1 = (h1 + hc * 0.9) / 2

        v1 = Q / (b * h1)
        Fr1 = v1 / np.sqrt(g * h1)

        if Fr1 > 1:
            h2 = jump.conjugate_depth(h1, Fr1)
            dE = jump.energy_loss(h1, h2)
            eta = jump.energy_dissipation_ratio(h1, h2, Q)
        else:
            h2 = h1
            dE = 0.0
            eta = 0.0

        print(f"{dz:^12.2f} | {h1:^12.4f} | {Fr1:^12.4f} | {h2:^12.4f} | {dE:^14.4f} | {eta:^14.2f}")

    print("-" * 120)

    print("\n【实验结论】")
    print("1. 跌水高度越大，跃前弗劳德数越大")
    print("2. 弗劳德数越大，共轭水深比（h2/h1）越大")
    print("3. 能量损失随跌水高度增大而增大")
    print("4. 消散效率存在最优值，一般在Fr1 = 4-9范围")
    print("5. 过大的跌水高度可能导致数值计算困难")


def experiment_6_2():
    """
    实验6.2：流量对水跃特性的影响
    """
    print_separator("实验6.2：流量对水跃特性的影响")

    # 基本参数
    b = 2.5
    dz = 2.0
    h0 = 1.2
    g = 9.81

    jump = HydraulicJump(b=b)

    print(f"\n固定条件：b = {b} m, Δz = {dz} m, h0 = {h0} m")
    print("\n不同流量下的水跃特性：")
    print("-" * 120)
    print(f"{'流量Q(m³/s)':^15} | {'跃前h1(m)':^12} | {'跃前Fr1':^12} | {'跃后h2(m)':^12} | {'能量损失(m)':^14} | {'水跃类型':^20}")
    print("-" * 120)

    Q_values = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]

    for Q in Q_values:
        v0 = Q / (b * h0)
        E0 = h0 + v0**2 / (2*g)
        E1 = E0 + dz

        q = Q / b
        hc = (q**2 / g) ** (1.0/3.0)

        # 求跌水后水深
        h1 = hc * 0.5
        for i in range(100):
            E1_calc = h1 + Q**2 / (2 * g * (b * h1)**2)
            f = E1_calc - E1

            if abs(f) < 1e-6:
                break

            dh = 1e-6
            E1_plus = (h1 + dh) + Q**2 / (2 * g * (b * (h1 + dh))**2)
            df = (E1_plus - E1_calc) / dh

            h1 = h1 - f / df
            if h1 <= 0:
                h1 = hc / 2
            elif h1 > hc:
                h1 = (h1 + hc * 0.9) / 2

        v1 = Q / (b * h1)
        Fr1 = v1 / np.sqrt(g * h1)

        if Fr1 > 1:
            h2 = jump.conjugate_depth(h1, Fr1)
            dE = jump.energy_loss(h1, h2)
            jump_type = jump.jump_type(Fr1)
        else:
            h2 = h1
            dE = 0.0
            jump_type = "无水跃"

        print(f"{Q:^15.2f} | {h1:^12.4f} | {Fr1:^12.4f} | {h2:^12.4f} | {dE:^14.4f} | {jump_type:^20}")

    print("-" * 120)

    print("\n【实验结论】")
    print("1. 流量越大，跃前水深越大，但弗劳德数变化不大")
    print("2. 流量主要影响水跃的尺度（h1, h2, Lj），不太影响水跃类型")
    print("3. 同样的跌水高度，不同流量下的消能机理相似")
    print("4. 设计时应考虑流量变化范围，确保各种流量下都能有效消能")


def experiment_6_3():
    """
    实验6.3：弗劳德数与消能效率的关系
    """
    print_separator("实验6.3：弗劳德数与消能效率的关系")

    # 理论分析：不同Fr1对应的消能效率
    print("\n理论分析：消能效率与弗劳德数的关系")
    print("公式：η = ΔE/E1 = (Fr1² - 1)³ / [8*Fr1²*(1 + Fr1²/2)]")
    print("-" * 100)
    print(f"{'弗劳德数Fr1':^15} | {'水深比h2/h1':^15} | {'消散效率η(%)':^18} | {'水跃类型':^25}")
    print("-" * 100)

    Fr1_values = [1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]

    for Fr1 in Fr1_values:
        # 水深比
        depth_ratio = 0.5 * (np.sqrt(1 + 8*Fr1**2) - 1)

        # 消散效率（理论公式）
        eta = ((Fr1**2 - 1)**3) / (8 * Fr1**2 * (1 + Fr1**2/2)) * 100

        # 水跃类型
        if Fr1 < 1.7:
            jump_type = "波状水跃"
        elif Fr1 < 2.5:
            jump_type = "弱水跃"
        elif Fr1 < 4.5:
            jump_type = "稳定水跃"
        elif Fr1 < 9.0:
            jump_type = "强水跃"
        else:
            jump_type = "剧烈水跃"

        print(f"{Fr1:^15.2f} | {depth_ratio:^15.4f} | {eta:^18.2f} | {jump_type:^25}")

    print("-" * 100)

    print("\n【实验结论】")
    print("1. 消能效率随Fr1增大而增大，但增速逐渐放缓")
    print("2. Fr1 = 4-9时，消能效率为45-70%，效果最佳")
    print("3. Fr1 < 2.5时，消能效率小于20%，效果较差")
    print("4. Fr1 > 10时，消能效率虽高，但水流紊动剧烈，需加强防护")
    print("5. 最佳设计范围：Fr1 = 4.5-9.0")


def experiment_6_4():
    """
    实验6.4：最优跌水高度设计
    """
    print_separator("实验6.4：最优跌水高度设计")

    # 基本参数
    Q = 5.0
    b = 2.5
    h0 = 1.2
    g = 9.81

    jump = HydraulicJump(b=b)

    v0 = Q / (b * h0)
    E0 = h0 + v0**2 / (2*g)
    q = Q / b
    hc = (q**2 / g) ** (1.0/3.0)

    print(f"\n设计条件：Q = {Q} m³/s, b = {b} m, h0 = {h0} m")
    print(f"\n寻找最优跌水高度（目标：Fr1 = 4.5-9.0，消能效率最高）")
    print("-" * 120)
    print(f"{'跌水Δz(m)':^12} | {'跃前Fr1':^12} | {'消散效率(%)':^14} | {'池长L(m)':^12} | {'综合评价':^30}")
    print("-" * 120)

    dz_values = np.linspace(1.0, 4.0, 13)

    best_design = {"dz": 0, "score": 0}

    for dz in dz_values:
        E1 = E0 + dz

        # 求跌水后水深
        h1 = hc * 0.5
        for i in range(100):
            E1_calc = h1 + Q**2 / (2 * g * (b * h1)**2)
            f = E1_calc - E1

            if abs(f) < 1e-6:
                break

            dh = 1e-6
            E1_plus = (h1 + dh) + Q**2 / (2 * g * (b * (h1 + dh))**2)
            df = (E1_plus - E1_calc) / dh

            h1 = h1 - f / df
            if h1 <= 0:
                h1 = hc / 2
            elif h1 > hc:
                h1 = (h1 + hc * 0.9) / 2

        v1 = Q / (b * h1)
        Fr1 = v1 / np.sqrt(g * h1)

        if Fr1 > 1:
            h2 = jump.conjugate_depth(h1, Fr1)
            eta = jump.energy_dissipation_ratio(h1, h2, Q)
            L_pool = 1.2 * jump.jump_length(h1, h2)
        else:
            eta = 0.0
            L_pool = 0.0

        # 综合评价（0-100分）
        score = 0
        evaluation = []

        # Fr1 评分（最佳4.5-9.0）
        if 4.5 <= Fr1 <= 9.0:
            fr_score = 40
            evaluation.append("Fr最优")
        elif 3.0 <= Fr1 < 4.5 or 9.0 < Fr1 <= 12.0:
            fr_score = 30
            evaluation.append("Fr良好")
        elif Fr1 < 3.0:
            fr_score = 10
            evaluation.append("Fr偏小")
        else:
            fr_score = 20
            evaluation.append("Fr偏大")

        # 消能效率评分
        if eta > 60:
            eta_score = 30
        elif eta > 45:
            eta_score = 25
        elif eta > 30:
            eta_score = 15
        else:
            eta_score = 5

        # 池长评分（越短越好，但不能太短）
        if 8 <= L_pool <= 15:
            length_score = 20
        elif L_pool < 8:
            length_score = 10
        elif L_pool <= 20:
            length_score = 15
        else:
            length_score = 5

        # 经济性评分（跌水高度越小越好）
        economy_score = max(0, 10 - dz)

        score = fr_score + eta_score + length_score + economy_score

        if score > best_design["score"]:
            best_design = {"dz": dz, "Fr1": Fr1, "eta": eta, "L": L_pool, "score": score}

        evaluation_str = ", ".join(evaluation)
        if score >= 70:
            evaluation_str += "★★★"
        elif score >= 60:
            evaluation_str += "★★"
        elif score >= 50:
            evaluation_str += "★"

        print(f"{dz:^12.2f} | {Fr1:^12.4f} | {eta:^14.2f} | {L_pool:^12.2f} | {evaluation_str:^30}")

    print("-" * 120)

    print(f"\n最优设计方案：")
    print(f"  跌水高度：Δz = {best_design['dz']:.2f} m")
    print(f"  跃前弗劳德数：Fr1 = {best_design['Fr1']:.4f}")
    print(f"  消散效率：η = {best_design['eta']:.2f}%")
    print(f"  消力池长度：L = {best_design['L']:.2f} m")
    print(f"  综合评分：{best_design['score']:.0f} 分")

    print("\n【实验结论】")
    print("1. 最优跌水高度需要综合考虑水力、结构和经济因素")
    print("2. 水力性能：Fr1 = 4.5-9.0，消能效率45-70%")
    print("3. 结构尺寸：消力池长度适中，便于施工")
    print("4. 经济性：跌水高度适度，减少土石方工程量")
    print("5. 对本案例（Q=5m³/s，b=2.5m），最优跌水高度约2.0-2.5m")


def main():
    """主函数"""
    print_separator("案例6：计算实验")
    print("\n本实验将探讨跌水消能的各种影响因素\n")

    # 运行各个实验
    experiment_6_1()  # 跌水高度影响
    experiment_6_2()  # 流量影响
    experiment_6_3()  # Fr与消能效率关系
    experiment_6_4()  # 最优设计

    # 总结
    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 跌水高度：决定跃前Fr，是最关键的设计参数")
    print("2. 流量：影响水跃尺度，但对水跃类型影响较小")
    print("3. 弗劳德数：与消能效率密切相关，Fr1=4.5-9最佳")
    print("4. 综合设计：需要平衡水力、结构和经济因素")
    print("\n跌水消能设计的核心是通过合理的跌水高度，")
    print("使跌水后形成合适的急流（Fr=4.5-9），")
    print("然后利用水跃有效消散能量，保护下游渠道！")
    print_separator()


if __name__ == "__main__":
    main()
