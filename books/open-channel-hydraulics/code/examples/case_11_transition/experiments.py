"""
案例11：渠道变宽与收缩 - 计算实验

实验内容：
1. 实验11.1：渐变角对能量损失的影响
2. 实验11.2：宽度变化比对损失的影响
3. 实验11.3：流量对过渡段水力特性的影响

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# 导入主程序中的函数
from main import compute_expansion_flow, compute_contraction_flow, print_separator


def experiment_11_1():
    """实验11.1：渐变角对能量损失的影响"""
    print_separator("实验11.1：渐变角对能量损失的影响")

    # 基准参数
    B1 = 4.0
    B2 = 6.0
    Q = 12.0
    n = 0.020
    S0 = 0.0002

    print(f"\n固定参数：B₁={B1}m, B₂={B2}m, Q={Q}m³/s, n={n}, S₀={S0}")
    print("变化参数：渐变段长度L（决定渐变角θ）")

    # 测试不同长度（对应不同渐变角）
    L_values = [3, 5, 7, 10, 15, 20, 30, 50]

    print("\n扩散段：渐变角对损失的影响")
    print("-" * 120)
    print(f"{'长度L(m)':^12} | {'渐变角θ(°)':^13} | {'损失系数ζ':^12} | "
          f"{'局部损失(m)':^14} | {'总损失(m)':^12} | {'损失率(%)':^12} | {'角度评价':^12}")
    print("-" * 120)

    for L in L_values:
        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        loss_rate = result['hf_total'] / result['E1'] * 100

        if result['theta_deg'] <= 10:
            grade = "优秀"
        elif result['theta_deg'] <= 12.5:
            grade = "良好"
        else:
            grade = "一般"

        print(f"{L:^12.1f} | {result['theta_deg']:^13.2f} | {result['zeta']:^12.2f} | "
              f"{result['hf_local']:^14.5f} | {result['hf_total']:^12.5f} | "
              f"{loss_rate:^12.2f} | {grade:^12}")

    print("-" * 120)

    print("\n【实验结论】")
    print("1. 渐变角越小（长度越长），能量损失越小")
    print("2. θ ≤ 10°：损失最小，推荐")
    print("3. θ > 12.5°：损失增大，开始接近突然扩散")
    print("4. 工程权衡：长度↑ → 造价↑，损失↓")
    print("5. 推荐设计：L = 2.5-3.0 * (B₂-B₁)")


def experiment_11_2():
    """实验11.2：宽度变化比对损失的影响"""
    print_separator("实验11.2：宽度变化比对损失的影响")

    # 基准参数
    B1 = 4.0
    Q = 12.0
    n = 0.020
    S0 = 0.0002
    L = 20.0

    print(f"\n固定参数：B₁={B1}m, Q={Q}m³/s, L={L}m")
    print("变化参数：下游宽度B₂（扩散比B₂/B₁）")

    # 测试不同扩散比
    expansion_ratios = [1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0]

    print("\n扩散比对能量损失的影响：")
    print("-" * 130)
    print(f"{'下游宽度B₂(m)':^15} | {'扩散比B₂/B₁':^13} | {'渐变角θ(°)':^13} | "
          f"{'局部损失(m)':^14} | {'总损失(m)':^12} | {'水面壅高(m)':^13} | {'评价':^10}")
    print("-" * 130)

    for ratio in expansion_ratios:
        B2 = B1 * ratio
        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        if ratio < 1.4:
            eval_text = "较小"
        elif ratio < 1.6:
            eval_text = "适中"
        else:
            eval_text = "较大"

        print(f"{B2:^15.2f} | {ratio:^13.2f} | {result['theta_deg']:^13.2f} | "
              f"{result['hf_local']:^14.5f} | {result['hf_total']:^12.5f} | "
              f"{result['water_rise']:^13.4f} | {eval_text:^10}")

    print("-" * 130)

    print("\n【实验结论】")
    print("1. 扩散比越大，能量损失和水面壅高越大")
    print("2. 扩散比从1.2增至2.0，损失增加约4倍")
    print("3. 扩散比1.5：合理范围")
    print("4. 扩散比>2.0：应分段过渡")
    print("5. 大扩散比需要更长的渐变段")


def experiment_11_3():
    """实验11.3：流量对过渡段水力特性的影响"""
    print_separator("实验11.3：流量对过渡段水力特性的影响")

    # 基准参数
    B1 = 4.0
    B2 = 6.0
    n = 0.020
    S0 = 0.0002
    L = 20.0

    print(f"\n固定参数：B₁={B1}m, B₂={B2}m, L={L}m")
    print("变化参数：流量Q")

    # 测试不同流量
    Q_values = [6, 9, 12, 15, 18, 21, 24]

    print("\n不同流量下的扩散段特性：")
    print("-" * 140)
    print(f"{'流量Q(m³/s)':^14} | {'上游水深h₁(m)':^16} | {'下游水深h₂(m)':^16} | "
          f"{'上游Fr':^10} | {'局部损失(m)':^14} | {'损失率(%)':^12} | {'流态':^10}")
    print("-" * 140)

    for Q in Q_values:
        result = compute_expansion_flow(B1, B2, Q, n, S0, L, gradual=True)

        loss_rate = result['hf_local'] / result['E1'] * 100

        flow_type = "缓流" if result['Fr1'] < 1 else "急流"

        print(f"{Q:^14.1f} | {result['h1']:^16.4f} | {result['h2']:^16.4f} | "
              f"{result['Fr1']:^10.3f} | {result['hf_local']:^14.5f} | "
              f"{loss_rate:^12.2f} | {flow_type:^10}")

    print("-" * 140)

    print("\n不同流量下的收缩段特性：")
    B2_con = 3.0

    print("-" * 140)
    print(f"{'流量Q(m³/s)':^14} | {'上游水深h₁(m)':^16} | {'下游水深h₂(m)':^16} | "
          f"{'下游Fr':^10} | {'局部损失(m)':^14} | {'损失率(%)':^12} | {'流态':^10}")
    print("-" * 140)

    for Q in Q_values:
        result = compute_contraction_flow(B1, B2_con, Q, n, S0, L, gradual=True)

        loss_rate = result['hf_local'] / result['E1'] * 100

        flow_type = "缓流" if result['Fr2'] < 1 else "急流"

        print(f"{Q:^14.1f} | {result['h1']:^16.4f} | {result['h2']:^16.4f} | "
              f"{result['Fr2']:^10.3f} | {result['hf_local']:^14.5f} | "
              f"{loss_rate:^12.2f} | {flow_type:^10}")

    print("-" * 140)

    print("\n【实验结论】")
    print("1. 流量增大，水深和流速都增大")
    print("2. 流量增大，能量损失绝对值增大")
    print("3. 但损失率（相对值）基本保持稳定")
    print("4. 本案例中均为缓流，符合设计预期")
    print("5. 若Fr接近1，需特别注意临界流")


def main():
    """主函数"""
    print_separator("案例11：计算实验")
    print("\n本实验将探讨渠道过渡段的各种影响因素\n")

    experiment_11_1()  # 渐变角影响
    experiment_11_2()  # 宽度变化比影响
    experiment_11_3()  # 流量影响

    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 渐变角：越小越好，但工程成本也越高")
    print("2. 宽度变化：扩散比过大需分段过渡")
    print("3. 流量影响：损失率相对稳定")
    print("\n渠道过渡段设计的核心：平衡水力性能与工程经济性，")
    print("扩散段优先采用渐变过渡，避免突然扩散！")
    print_separator()


if __name__ == "__main__":
    main()
