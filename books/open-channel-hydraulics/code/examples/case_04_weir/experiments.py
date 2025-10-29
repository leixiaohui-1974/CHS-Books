"""
案例4：灌区量水堰流量测量 - 计算实验

实验内容：
1. 实验4.1：堰顶宽度 b 对流量的影响
2. 实验4.2：流量系数 m 对流量的影响
3. 实验4.3：侧收缩影响的定量分析
4. 实验4.4：三角形堰与矩形堰的适用范围对比

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.structures import Weir


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def experiment_4_1():
    """
    实验4.1：堰顶宽度 b 对流量的影响

    保持其他参数不变，改变堰顶宽度，观察流量变化
    """
    print_separator("实验4.1：堰顶宽度 b 对流量的影响")

    # 基本参数
    m = 0.40
    H = 0.20  # 固定水头

    # 不同的堰顶宽度
    b_values = [0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0]

    print(f"\n固定水头 H = {H} m，流量系数 m = {m}")
    print("\n不同堰顶宽度的流量对比：")
    print("-" * 90)
    print(f"{'堰顶宽度b(m)':^15} | {'流量Q(m³/s)':^15} | {'单宽流量q(m²/s)':^18} | {'流量比Q/Q₀':^15}")
    print("-" * 90)

    Q0 = None
    for b in b_values:
        weir = Weir(b=b, weir_type='thin', m=m)
        Q = weir.discharge_rectangular(H, with_contraction=False)
        q = Q / b

        if Q0 is None:
            Q0 = Q
            ratio = 1.0
        else:
            ratio = Q / Q0

        print(f"{b:^15.2f} | {Q:^15.4f} | {q:^18.4f} | {ratio:^15.2f}")

    print("-" * 90)

    # 分析结论
    print("\n【实验结论】")
    print("1. 流量与堰顶宽度成正比：Q ∝ b")
    print("2. 单宽流量 q = Q/b 保持恒定（相同水头下）")
    print("3. 选择堰宽时需考虑：")
    print("   - 渠道宽度限制")
    print("   - 测量流量范围")
    print("   - 侧收缩影响（宽堰侧收缩相对较小）")
    print("4. 工程建议：b = 0.6-0.9倍渠道宽度（减小侧收缩）")


def experiment_4_2():
    """
    实验4.2：流量系数 m 对流量的影响

    不同的堰体结构和加工精度会影响流量系数
    """
    print_separator("实验4.2：流量系数 m 对流量的影响")

    # 基本参数
    b = 0.8
    H = 0.20

    # 不同的流量系数
    m_values = [0.35, 0.38, 0.40, 0.42, 0.45]
    m_descriptions = [
        "粗糙堰顶",
        "一般加工",
        "标准薄壁堰",
        "精密加工",
        "理想薄壁堰"
    ]

    print(f"\n固定水头 H = {H} m，堰顶宽度 b = {b} m")
    print("\n不同流量系数对比（反映堰体质量）：")
    print("-" * 100)
    print(f"{'流量系数m':^12} | {'堰体描述':^15} | {'流量Q(m³/s)':^15} | {'与标准值差异(%)':^18}")
    print("-" * 100)

    Q_standard = None
    for m, desc in zip(m_values, m_descriptions):
        weir = Weir(b=b, weir_type='thin', m=m)
        Q = weir.discharge_rectangular(H, with_contraction=False)

        if abs(m - 0.40) < 1e-6:  # 找到标准值
            Q_standard = Q
            diff = 0.0
        elif Q_standard is not None:
            diff = (Q - Q_standard) / Q_standard * 100
        else:
            diff = 0.0  # 标准值尚未找到

        print(f"{m:^12.3f} | {desc:^15} | {Q:^15.4f} | {diff:^18.2f}")

    print("-" * 100)

    # 分析结论
    print("\n【实验结论】")
    print("1. 流量与流量系数成正比：Q ∝ m")
    print("2. 流量系数偏差5%会导致流量偏差5%")
    print("3. 流量系数的影响因素：")
    print("   - 堰顶锐利度（磨损会降低m值）")
    print("   - 堰顶厚度（厚堰m值较小）")
    print("   - 通气条件（通气不良m值降低）")
    print("   - 堰高与水头比（P/H应>2）")
    print("4. 工程建议：")
    print("   - 新建堰应进行流量率定，确定实际m值")
    print("   - 定期检查堰顶锐利度，及时维护")
    print("   - 使用标准薄壁堰时，可采用 m = 0.40-0.42")


def experiment_4_3():
    """
    实验4.3：侧收缩影响的定量分析

    分析不同水头下侧收缩对流量的影响程度
    """
    print_separator("实验4.3：侧收缩影响的定量分析")

    # 基本参数
    b = 0.8
    m = 0.40

    # 不同的水头
    H_values = np.arange(0.05, 0.45, 0.05)

    print(f"\n堰顶宽度 b = {b} m，流量系数 m = {m}")
    print("侧收缩公式：b_eff = b - 0.1 * n * H  (n=2 表示两侧收缩)")
    print("\n不同水头下的侧收缩影响：")
    print("-" * 110)
    print(f"{'水头H(m)':^12} | {'无收缩Q(m³/s)':^16} | {'有收缩Q(m³/s)':^16} | {'流量减少(%)':^14} | {'有效宽度(m)':^14}")
    print("-" * 110)

    weir = Weir(b=b, weir_type='thin', m=m)

    for H in H_values:
        Q_no = weir.discharge_rectangular(H, with_contraction=False)
        Q_yes = weir.discharge_rectangular(H, with_contraction=True)
        reduction = (Q_no - Q_yes) / Q_no * 100
        b_eff = b - 0.1 * 2 * H

        print(f"{H:^12.3f} | {Q_no:^16.4f} | {Q_yes:^16.4f} | {reduction:^14.2f} | {b_eff:^14.4f}")

    print("-" * 110)

    # 分析结论
    print("\n【实验结论】")
    print("1. 侧收缩使流量减少，且水头越大影响越大")
    print("2. 本案例中，水头从0.05m增至0.40m时：")
    print("   - 流量减少率从1.25%增至10.00%")
    print("   - 有效宽度从0.79m减至0.72m")
    print("3. 侧收缩的物理机制：")
    print("   - 水流从侧墙离开，形成收缩断面")
    print("   - 收缩程度与水头成正比")
    print("   - 修正系数0.1来自经验公式（Francis公式）")
    print("4. 工程对策：")
    print("   - 采用无侧收缩堰（堰宽等于渠宽）")
    print("   - 设置侧墙导流，减小收缩")
    print("   - 流量计算时考虑侧收缩修正")


def experiment_4_4():
    """
    实验4.4：三角形堰与矩形堰的适用范围对比

    比较两种堰型在不同流量范围下的特点
    """
    print_separator("实验4.4：三角形堰与矩形堰的适用范围对比")

    # 矩形堰参数
    b_rect = 0.8
    m_rect = 0.40

    # 三角形堰参数（90度V型堰）
    theta = 90.0
    m_tri = 0.40

    print("\n矩形堰：b = 0.8 m, m = 0.40")
    print("三角形堰：θ = 90°, m = 0.40")

    # 不同的水头
    H_values = np.arange(0.02, 0.32, 0.02)

    print("\n两种堰型的流量对比：")
    print("-" * 120)
    print(f"{'水头H(m)':^12} | {'矩形堰Q(m³/s)':^18} | {'三角形堰Q(m³/s)':^18} | {'流量比Qt/Qr':^14} | {'测量精度':^15}")
    print("-" * 120)

    weir_rect = Weir(b=b_rect, weir_type='thin', m=m_rect)
    weir_tri = Weir(b=1.0, weir_type='thin', m=m_tri)  # 三角形堰不使用b参数，传入任意正值

    for H in H_values:
        Q_rect = weir_rect.discharge_rectangular(H, with_contraction=False)
        Q_tri = weir_tri.discharge_triangular(H, theta=theta)
        ratio = Q_tri / Q_rect if Q_rect > 0 else 0

        # 根据流量大小判断测量精度
        if Q_rect < 0.05:
            precision = "三角形堰优"
        elif Q_rect < 0.20:
            precision = "两者相当"
        else:
            precision = "矩形堰优"

        print(f"{H:^12.3f} | {Q_rect:^18.5f} | {Q_tri:^18.5f} | {ratio:^14.3f} | {precision:^15}")

    print("-" * 120)

    # 分析结论
    print("\n【实验结论】")
    print("1. 三角形堰的特点：")
    print("   - 小流量时测量精度高（流量对水头变化敏感）")
    print("   - 不受侧收缩影响")
    print("   - 自冲刷能力强（V型断面）")
    print("   - 流量公式：Q ∝ H^(5/2)（比矩形堰的H^(3/2)指数更大）")

    print("\n2. 矩形堰的特点：")
    print("   - 适用于较大流量")
    print("   - 加工制造简单")
    print("   - 流量范围大")
    print("   - 需要考虑侧收缩影响")

    print("\n3. 适用范围建议：")
    print("   - Q < 0.05 m³/s：优先选用三角形堰")
    print("   - 0.05 < Q < 0.50 m³/s：矩形堰或三角形堰均可")
    print("   - Q > 0.50 m³/s：优先选用矩形堰或宽顶堰")

    print("\n4. 工程实例：")
    print("   - 灌溉试验站量水：三角形堰（测量田间小流量）")
    print("   - 渠道分水口：矩形堰（中等流量）")
    print("   - 河道测流：宽顶堰（大流量）")


def experiment_4_5():
    """
    实验4.5：水头测量精度对流量误差的影响

    分析在不同水头下，测量误差对流量精度的影响
    """
    print_separator("实验4.5：水头测量精度对流量误差的影响")

    # 基本参数
    b = 0.8
    m = 0.40
    dH = 0.001  # 水头测量误差 ±1mm

    weir = Weir(b=b, weir_type='thin', m=m)

    # 不同的水头
    H_values = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]

    print(f"\n堰顶宽度 b = {b} m，流量系数 m = {m}")
    print(f"水头测量误差 ΔH = ±{dH*1000:.0f} mm")
    print("\n不同水头下的流量误差传播：")
    print("-" * 110)
    print(f"{'水头H(m)':^12} | {'流量Q(m³/s)':^15} | {'ΔQ增(m³/s)':^15} | {'ΔQ减(m³/s)':^15} | {'误差率(%)':^12}")
    print("-" * 110)

    for H in H_values:
        Q = weir.discharge_rectangular(H, with_contraction=False)
        Q_plus = weir.discharge_rectangular(H + dH, with_contraction=False)
        Q_minus = weir.discharge_rectangular(H - dH, with_contraction=False)

        dQ_plus = Q_plus - Q
        dQ_minus = Q - Q_minus
        error_rate = ((dQ_plus + dQ_minus) / 2) / Q * 100

        print(f"{H:^12.3f} | {Q:^15.4f} | {dQ_plus:^15.5f} | {dQ_minus:^15.5f} | {error_rate:^12.2f}")

    print("-" * 110)

    # 分析结论
    print("\n【实验结论】")
    print("1. 误差传播关系：")
    print("   - 从 Q = m * b * sqrt(2g) * H^(3/2) 微分得：")
    print("   - dQ/Q = (3/2) * dH/H")
    print("   - 流量相对误差是水头相对误差的1.5倍")

    print("\n2. 水头越小，相对误差越大：")
    print("   - H = 0.05m 时，1mm误差导致流量误差 3.0%")
    print("   - H = 0.40m 时，1mm误差导致流量误差 0.4%")

    print("\n3. 精度要求：")
    print("   - 要保证流量精度 ±3%，水头精度需要：")
    print("     * H = 0.05m：±0.5 mm")
    print("     * H = 0.20m：±2 mm")
    print("     * H = 0.40m：±4 mm")

    print("\n4. 工程措施：")
    print("   - 采用高精度水位计（±0.5-1mm）")
    print("   - 设置静水井，消除水面波动")
    print("   - 水尺安装在堰前3-4倍最大水头处")
    print("   - 避免在极小水头下测量（H < 0.03m）")
    print("   - 定期校准测量设备")


def main():
    """主函数"""
    print_separator("案例4：计算实验")
    print("\n本实验将探讨堰流测量的各种影响因素\n")

    # 运行各个实验
    experiment_4_1()  # 堰顶宽度影响
    experiment_4_2()  # 流量系数影响
    experiment_4_3()  # 侧收缩影响
    experiment_4_4()  # 三角形堰与矩形堰对比
    experiment_4_5()  # 测量精度影响

    # 总结
    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 堰顶宽度b：影响总流量，但不影响单宽流量")
    print("2. 流量系数m：反映堰体质量，需要实测率定")
    print("3. 侧收缩：使流量减少5-10%，大水头时影响更显著")
    print("4. 堰型选择：小流量用三角形堰，大流量用矩形堰")
    print("5. 测量精度：水头测量精度直接决定流量测量精度")
    print("\n这些参数的合理选择和精确测量，是准确量水的关键！")
    print_separator()


if __name__ == "__main__":
    main()
