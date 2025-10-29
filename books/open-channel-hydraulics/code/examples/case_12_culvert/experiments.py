"""
案例12：涵洞过流 - 计算实验

实验内容：
1. 实验12.1：进口形式对过流能力的影响
2. 实验12.2：涵洞尺寸对流态的影响
3. 实验12.3：上下游水位变化对流量的影响
4. 实验12.4：涵洞长度对水头损失的影响

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# 导入主程序中的函数
from main import (print_separator, compute_critical_depth, free_flow_discharge,
                 submerged_flow_discharge, pressure_flow_discharge, determine_flow_type)
from models.channel import RectangularChannel


def experiment_12_1():
    """实验12.1：进口形式对过流能力的影响"""
    print_separator("实验12.1：进口形式对过流能力的影响")

    # 基准参数
    b = 2.0
    H = 1.5
    h1 = 1.2  # 上游水深
    g = 9.81

    print(f"\n固定参数：b={b}m, H={H}m, h1={h1}m")
    print("变化参数：进口类型（流量系数Cd和损失系数ζe）")

    # 不同进口类型
    inlet_types = [
        ("直角进口（无处理）", 0.60, 0.50),
        ("小圆角进口(r=0.1H)", 0.65, 0.35),
        ("标准圆角(r=0.15H)", 0.70, 0.20),
        ("大圆角进口(r=0.2H)", 0.75, 0.15),
        ("渐变喇叭口(15°)", 0.85, 0.12),
        ("标准喇叭口", 0.90, 0.10)
    ]

    print("\n不同进口形式的过流能力：")
    print("-" * 130)
    print(f"{'进口类型':^25} | {'流量系数Cd':^13} | {'损失系数ζe':^13} | "
          f"{'流量Q(m³/s)':^15} | {'相对流量(%)':^14} | {'工程评价':^20}")
    print("-" * 130)

    Q_base = None
    for inlet_name, Cd, zeta_e in inlet_types:
        Q = free_flow_discharge(b, H, h1, Cd, g)

        if Q_base is None:
            Q_base = Q
            relative = 100.0
        else:
            relative = Q / Q_base * 100

        # 评价
        if Cd < 0.65:
            evaluation = "差（不推荐）"
        elif Cd < 0.75:
            evaluation = "良好（经济）"
        elif Cd < 0.85:
            evaluation = "优秀（推荐）"
        else:
            evaluation = "最优（造价高）"

        print(f"{inlet_name:^25} | {Cd:^13.2f} | {zeta_e:^13.2f} | "
              f"{Q:^15.2f} | {relative:^14.1f} | {evaluation:^20}")

    print("-" * 130)

    print("\n【实验结论】")
    print("1. 进口形式对过流能力影响显著")
    print("2. 喇叭口比直角进口流量增加50%")
    print("3. 标准圆角是最经济的选择（Cd=0.70）")
    print("4. 直角进口损失大，应避免使用")
    print("5. 推荐：小涵洞用圆角，大涵洞用喇叭口")


def experiment_12_2():
    """实验12.2：涵洞尺寸对流态的影响"""
    print_separator("实验12.2：涵洞尺寸对流态的影响")

    # 固定流量和水位
    Q_fixed = 4.0
    h1 = 1.5
    h3 = 1.0
    g = 9.81

    print(f"\n固定参数：Q={Q_fixed}m³/s, h1={h1}m, h3={h3}m")
    print("变化参数：涵洞宽度b和高度H")

    # 测试不同尺寸
    sizes = [
        (1.5, 1.2),
        (1.8, 1.3),
        (2.0, 1.5),
        (2.2, 1.6),
        (2.5, 1.8),
        (3.0, 2.0)
    ]

    print("\n不同尺寸涵洞的流态分析：")
    print("-" * 140)
    print(f"{'宽度b(m)':^11} | {'高度H(m)':^11} | {'断面A(m²)':^12} | "
          f"{'临界hc(m)':^12} | {'h1/H':^8} | {'h3/hc':^8} | {'流态':^12} | {'设计评价':^20}")
    print("-" * 140)

    for b, H in sizes:
        A = b * H
        hc = compute_critical_depth(Q_fixed, b, g)

        flow_type = determine_flow_type(h1, h3, H, hc)

        if flow_type == 'free':
            type_name = "自由出流"
        elif flow_type == 'submerged':
            type_name = "淹没出流"
        else:
            type_name = "压力流"

        ratio_h1 = h1 / H
        ratio_h3 = h3 / hc

        # 评价
        if A < 2.5:
            evaluation = "偏小（流速过大）"
        elif A < 3.5:
            evaluation = "合理"
        elif A < 5.0:
            evaluation = "偏大（造价高）"
        else:
            evaluation = "过大（不经济）"

        print(f"{b:^11.2f} | {H:^11.2f} | {A:^12.2f} | "
              f"{hc:^12.3f} | {ratio_h1:^8.2f} | {ratio_h3:^8.2f} | "
              f"{type_name:^12} | {evaluation:^20}")

    print("-" * 140)

    print("\n【实验结论】")
    print("1. 尺寸过小导致满管压力流（不经济）")
    print("2. 尺寸过大造价高且流速过小（易淤积）")
    print("3. 合理尺寸使涵洞处于自由或淹没流")
    print("4. 本案例：b=2.0m, H=1.5m 较为合理")
    print("5. 设计准则：A = (1.2-1.5) × Q / v_design")


def experiment_12_3():
    """实验12.3：上下游水位变化对流量的影响"""
    print_separator("实验12.3：上下游水位变化对流量的影响")

    # 涵洞参数
    b = 2.0
    H = 1.5
    L = 30.0
    n = 0.014
    S0 = 0.001
    g = 9.81

    print(f"\n涵洞参数：b={b}m, H={H}m, L={L}m, n={n}, S0={S0}")

    # 实验3.1：固定下游，改变上游水位
    print("\n实验3.1：固定下游水位h3=0.5m，改变上游水位h1")
    h3_fixed = 0.5
    h1_values = [0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.5]

    hc = compute_critical_depth(4.0, b, g)  # 估算临界水深

    print("-" * 130)
    print(f"{'上游h1(m)':^12} | {'h1/H':^8} | {'流态':^12} | "
          f"{'流量Q(m³/s)':^15} | {'流速v(m/s)':^13} | {'备注':^30}")
    print("-" * 130)

    for h1 in h1_values:
        flow_type = determine_flow_type(h1, h3_fixed, H, hc)

        if flow_type == 'free':
            Q = free_flow_discharge(b, H, h1, Cd=0.70, g=g)
            v = Q / (b * min(h1, H))
            type_name = "自由出流"
            note = "进口控制，Q随h1增大"
        elif flow_type == 'submerged':
            result = submerged_flow_discharge(b, H, L, n, S0, h1, h3_fixed,
                                             zeta_e=0.2, zeta_o=1.0, g=g)
            Q = result['Q']
            v = result['v']
            type_name = "淹没出流"
            note = "出口控制"
        else:
            result = pressure_flow_discharge(b, H, L, n, S0, h1, h3_fixed,
                                            zeta_e=0.2, zeta_o=1.0, g=g)
            Q = result['Q']
            v = result['v']
            type_name = "压力流"
            note = "满管流，Q随水位差增大"

        print(f"{h1:^12.2f} | {h1/H:^8.2f} | {type_name:^12} | "
              f"{Q:^15.2f} | {v:^13.3f} | {note:^30}")

    print("-" * 130)

    # 实验3.2：固定上游，改变下游水位
    print("\n实验3.2：固定上游水位h1=2.0m，改变下游水位h3")
    h1_fixed = 2.0
    h3_values = [0.3, 0.5, 0.8, 1.0, 1.3, 1.5, 1.8, 2.0]

    print("-" * 130)
    print(f"{'下游h3(m)':^12} | {'h3/H':^8} | {'流态':^12} | "
          f"{'流量Q(m³/s)':^15} | {'流速v(m/s)':^13} | {'备注':^30}")
    print("-" * 130)

    for h3 in h3_values:
        flow_type = determine_flow_type(h1_fixed, h3, H, hc)

        if flow_type == 'free':
            Q = free_flow_discharge(b, H, h1_fixed, Cd=0.70, g=g)
            v = Q / (b * min(h1_fixed, H))
            type_name = "自由出流"
            note = "Q不受下游影响"
        elif flow_type == 'submerged':
            result = submerged_flow_discharge(b, H, L, n, S0, h1_fixed, h3,
                                             zeta_e=0.2, zeta_o=1.0, g=g)
            Q = result['Q']
            v = result['v']
            type_name = "淹没出流"
            note = "Q随h3升高而减小"
        else:
            result = pressure_flow_discharge(b, H, L, n, S0, h1_fixed, h3,
                                            zeta_e=0.2, zeta_o=1.0, g=g)
            Q = result['Q']
            v = result['v']
            type_name = "压力流"
            note = "Q随h3升高而减小"

        print(f"{h3:^12.2f} | {h3/H:^8.2f} | {type_name:^12} | "
              f"{Q:^15.2f} | {v:^13.3f} | {note:^30}")

    print("-" * 130)

    print("\n【实验结论】")
    print("1. 自由出流：Q仅与上游水位有关")
    print("2. 淹没出流：Q受上下游水位差控制")
    print("3. 压力流：Q取决于上下游水位差")
    print("4. 下游水位升高会显著降低过流能力")
    print("5. 设计应避免下游顶托影响")


def experiment_12_4():
    """实验12.4：涵洞长度对水头损失的影响"""
    print_separator("实验12.4：涵洞长度对水头损失的影响")

    # 基准参数
    b = 2.0
    H = 1.5
    n = 0.014
    S0 = 0.001
    h1 = 2.0
    h3 = 1.6
    g = 9.81

    print(f"\n固定参数：b={b}m, H={H}m, h1={h1}m, h3={h3}m")
    print("变化参数：涵洞长度L（代表不同路堤宽度）")

    # 测试不同长度
    L_values = [10, 20, 30, 40, 50, 60, 80, 100]

    print("\n涵洞长度对损失的影响（淹没出流）：")
    print("-" * 140)
    print(f"{'长度L(m)':^11} | {'流量Q(m³/s)':^15} | {'进口损失(m)':^14} | "
          f"{'沿程损失(m)':^14} | {'出口损失(m)':^14} | {'总损失(m)':^12} | {'损失比例(%)':^14}")
    print("-" * 140)

    for L in L_values:
        result = submerged_flow_discharge(b, H, L, n, S0, h1, h3,
                                         zeta_e=0.2, zeta_o=1.0, g=g)

        loss_ratio = result['hf_friction'] / result['hf_total'] * 100

        print(f"{L:^11.1f} | {result['Q']:^15.2f} | {result['hf_entrance']:^14.4f} | "
              f"{result['hf_friction']:^14.4f} | {result['hf_exit']:^14.4f} | "
              f"{result['hf_total']:^12.4f} | {loss_ratio:^14.1f}")

    print("-" * 140)

    print("\n【实验结论】")
    print("1. 涵洞越长，沿程损失越大")
    print("2. 短涵洞（L<30m）：局部损失占主导")
    print("3. 长涵洞（L>50m）：沿程损失占主导")
    print("4. L增加1倍，沿程损失近似增加1倍")
    print("5. 设计建议：")
    print("   - 短涵洞：重点优化进出口")
    print("   - 长涵洞：降低糙率更重要")
    print("   - L>100m：考虑采用箱涵或桥梁")


def main():
    """主函数"""
    print_separator("案例12：计算实验")
    print("\n本实验将探讨涵洞过流的各种影响因素\n")

    experiment_12_1()  # 进口形式影响
    experiment_12_2()  # 尺寸影响
    experiment_12_3()  # 水位影响
    experiment_12_4()  # 长度影响

    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 进口形式：对过流能力影响显著（可差50%）")
    print("2. 涵洞尺寸：需平衡过流能力与工程造价")
    print("3. 水位条件：决定流态和过流能力")
    print("4. 涵洞长度：影响损失分布和总流量")
    print("\n涵洞设计是一个综合优化问题，")
    print("需要考虑水力、结构、经济、施工等多方面因素！")
    print_separator()


if __name__ == "__main__":
    main()
