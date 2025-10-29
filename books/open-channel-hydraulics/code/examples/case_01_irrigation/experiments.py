"""
案例1：农村灌溉渠流量计算 - 计算实验

实验内容：
1. 实验1.1：糙率系数 n 对正常水深的影响
2. 实验1.2：渠底坡度 S0 对正常水深的影响
3. 实验1.3：边坡系数 m 对水力要素的影响

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import TrapezoidalChannel
from solvers.steady.uniform_flow import UniformFlowSolver


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def experiment_1_1():
    """
    实验1.1：糙率系数 n 对正常水深的影响

    保持其他参数不变，改变糙率系数，观察正常水深的变化
    """
    print_separator("实验1.1：糙率系数 n 对正常水深的影响")

    # 基本参数
    b = 1.0
    m = 1.5
    S0 = 0.0002
    Q = 0.5

    # 不同的糙率系数
    n_values = [0.015, 0.020, 0.025, 0.030, 0.035]
    n_materials = ["混凝土衬砌", "砂浆抹面", "土质渠道", "杂草较多", "灌木丛生"]

    print("\n不同渠道材料的糙率系数对比：")
    print("-" * 100)
    print(f"{'糙率n':^8} | {'材料描述':^12} | {'正常水深h0(m)':^15} | {'流速v(m/s)':^12} | {'弗劳德数Fr':^12}")
    print("-" * 100)

    results_list = []

    for n, material in zip(n_values, n_materials):
        # 创建渠道和求解器
        channel = TrapezoidalChannel(b=b, m=m, n=n, S0=S0)
        solver = UniformFlowSolver(channel)

        # 计算正常水深
        results = solver.compute_normal_depth(Q)
        h0 = results["正常水深_h0"]
        v = results["流速_v"]
        Fr = results["弗劳德数_Fr"]

        print(f"{n:^8.3f} | {material:^12} | {h0:^15.4f} | {v:^12.4f} | {Fr:^12.4f}")

        results_list.append((n, h0, v, Fr))

    print("-" * 100)

    # 分析结论
    print("\n【实验结论】")
    print("1. 糙率系数越大，正常水深越大（阻力增加，水深加深）")
    print("2. 糙率系数越大，流速越小（同流量下，断面增大，流速减小）")
    print("3. 弗劳德数随糙率增大而减小（流速减小效应）")
    print("4. 工程建议：选择合适的渠道材料，保持渠道清洁，减小糙率，降低水头损失")


def experiment_1_2():
    """
    实验1.2：渠底坡度 S0 对正常水深的影响

    保持其他参数不变，改变渠底坡度，观察正常水深的变化
    """
    print_separator("实验1.2：渠底坡度 S0 对正常水深的影响")

    # 基本参数
    b = 1.0
    m = 1.5
    n = 0.025
    Q = 0.5

    # 不同的渠底坡度
    S0_values = [0.0001, 0.0002, 0.0005, 0.001, 0.002]

    print("\n不同渠底坡度对比：")
    print("-" * 100)
    print(f"{'坡度S0':^10} | {'坡度(%)':^10} | {'正常水深h0(m)':^15} | {'流速v(m/s)':^12} | {'弗劳德数Fr':^12}")
    print("-" * 100)

    for S0 in S0_values:
        # 创建渠道和求解器
        channel = TrapezoidalChannel(b=b, m=m, n=n, S0=S0)
        solver = UniformFlowSolver(channel)

        # 计算正常水深
        results = solver.compute_normal_depth(Q)
        h0 = results["正常水深_h0"]
        v = results["流速_v"]
        Fr = results["弗劳德数_Fr"]

        print(f"{S0:^10.4f} | {S0*100:^10.3f} | {h0:^15.4f} | {v:^12.4f} | {Fr:^12.4f}")

    print("-" * 100)

    # 分析结论
    print("\n【实验结论】")
    print("1. 坡度越大，正常水深越小（重力分量增大，水流加速，水深减小）")
    print("2. 坡度越大，流速越大（同流量下，坡度增大促进水流加速）")
    print("3. 弗劳德数随坡度增大而增大，可能从缓流转为急流")
    print("4. 工程建议：平原地区坡度较缓，需要较大断面；山区坡度较陡，断面可以较小")


def experiment_1_3():
    """
    实验1.3：边坡系数 m 对水力要素的影响

    保持流量和水深不变，改变边坡系数，观察水力要素的变化
    """
    print_separator("实验1.3：边坡系数 m 对水力要素的影响")

    # 基本参数
    b = 1.0
    n = 0.025
    S0 = 0.0002
    Q = 0.5

    # 不同的边坡系数
    m_values = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]
    m_descriptions = [
        "矩形（垂直边墙）",
        "很陡（0.5:1）",
        "较陡（1:1）",
        "中等（1.5:1）",
        "较缓（2:1）",
        "很缓（2.5:1）"
    ]

    print("\n不同边坡系数对比：")
    print("-" * 110)
    print(f"{'边坡m':^8} | {'边坡描述':^20} | {'正常水深(m)':^12} | {'断面积(m²)':^12} | {'水力半径(m)':^12} | {'流速(m/s)':^10}")
    print("-" * 110)

    for m, desc in zip(m_values, m_descriptions):
        # 创建渠道和求解器
        channel = TrapezoidalChannel(b=b, m=m, n=n, S0=S0)
        solver = UniformFlowSolver(channel)

        # 计算正常水深
        results = solver.compute_normal_depth(Q)
        h0 = results["正常水深_h0"]
        A = results["面积_A"]
        R = results["水力半径_R"]
        v = results["流速_v"]

        print(f"{m:^8.1f} | {desc:^20} | {h0:^12.4f} | {A:^12.4f} | {R:^12.4f} | {v:^10.4f}")

    print("-" * 110)

    # 分析结论
    print("\n【实验结论】")
    print("1. 边坡系数越大，同流量下正常水深越小（断面更宽，水深减小）")
    print("2. 边坡系数增大，过水断面积增大（相同水深下）")
    print("3. 存在最优边坡系数，使水力半径最大，输水效率最高")
    print("4. 工程建议：")
    print("   - 岩石渠道：m=0.25-0.5（边坡较陡）")
    print("   - 混凝土渠道：m=0.5-1.0")
    print("   - 土质渠道：m=1.5-2.5（边坡较缓，防止坍塌）")


def experiment_1_4():
    """
    实验1.4：流量 Q 对正常水深的影响

    保持渠道参数不变，改变流量，绘制Q-h曲线
    """
    print_separator("实验1.4：流量 Q 对正常水深的影响")

    # 基本参数
    b = 1.0
    m = 1.5
    n = 0.025
    S0 = 0.0002

    # 不同的流量
    Q_values = np.arange(0.1, 2.1, 0.2)

    print("\n流量-水深关系：")
    print("-" * 80)
    print(f"{'流量Q(m³/s)':^15} | {'正常水深h0(m)':^15} | {'流速v(m/s)':^15} | {'流态':^15}")
    print("-" * 80)

    # 创建渠道和求解器
    channel = TrapezoidalChannel(b=b, m=m, n=n, S0=S0)
    solver = UniformFlowSolver(channel)

    for Q in Q_values:
        results = solver.compute_normal_depth(Q)
        h0 = results["正常水深_h0"]
        v = results["流速_v"]
        flow_state = results["流态"]

        print(f"{Q:^15.2f} | {h0:^15.4f} | {v:^15.4f} | {flow_state:^15}")

    print("-" * 80)

    # 分析结论
    print("\n【实验结论】")
    print("1. 流量越大，正常水深越大（非线性关系）")
    print("2. 流量增加，流速也增加，但增速小于流量增速（断面增大）")
    print("3. 在本渠道参数下，流动始终保持缓流状态")
    print("4. Q-h关系可用于渠道设计：给定流量，查表得水深")


def main():
    """主函数"""
    print_separator("案例1：计算实验")
    print("\n本实验将探讨各参数对明渠均匀流的影响\n")

    # 运行各个实验
    experiment_1_1()  # 糙率系数影响
    experiment_1_2()  # 渠底坡度影响
    experiment_1_3()  # 边坡系数影响
    experiment_1_4()  # 流量影响

    # 总结
    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 糙率系数n：反映渠道表面粗糙程度，n越大阻力越大，水深越大")
    print("2. 渠底坡度S0：坡度越大流速越大，水深越小")
    print("3. 边坡系数m：影响断面形状和稳定性，需要综合考虑水力和结构要求")
    print("4. 流量Q：决定了所需的过水断面，是设计的基本条件")
    print("\n这些参数的合理选择，是明渠设计的关键！")
    print_separator()


if __name__ == "__main__":
    main()
