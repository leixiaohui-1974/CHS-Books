"""
案例4：灌区量水堰流量测量 - 主程序

问题描述：
某灌区量水堰设计，已知：
- 矩形薄壁堰
- 堰顶宽度 b = 0.8 m
- 流量系数 m = 0.40
- 堰顶水头范围 H = 0.05-0.40 m

求解：
1. 不同水头下的流量
2. 流量反算水头
3. Q-H关系曲线
4. 侧收缩影响分析

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


def main():
    """主函数"""
    print_separator("案例4：灌区量水堰流量测量")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    b = 0.8      # 堰顶宽度 (m)
    m = 0.40     # 流量系数
    weir_type = 'thin'  # 薄壁堰

    print(f"量水建筑物：矩形薄壁堰")
    print(f"堰顶宽度 b = {b} m")
    print(f"流量系数 m = {m}")
    print(f"堰的类型：{weir_type} (thin-plate weir)")

    # ==================== 第二步：创建堰对象 ====================
    print("\n【步骤2】创建堰模型")
    print("-" * 80)

    weir = Weir(b=b, weir_type=weir_type, m=m)
    print(f"堰对象：{weir}")

    # ==================== 第三步：流量计算 ====================
    print("\n【步骤3】流量计算（已知水头）")
    print("-" * 80)

    H_values = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]

    print("\n堰流公式：Q = m * b * sqrt(2g) * H^(3/2)\n")
    print("无侧收缩情况：")
    print("-" * 80)
    print(f"{'水头H(m)':^12} | {'流量Q(m³/s)':^15} | {'单宽流量q(m²/s)':^18}")
    print("-" * 80)

    Q_no_contraction = []
    for H in H_values:
        Q = weir.discharge_rectangular(H, with_contraction=False)
        q = Q / b
        Q_no_contraction.append(Q)
        print(f"{H:^12.3f} | {Q:^15.4f} | {q:^18.4f}")

    print("-" * 80)

    print("\n有侧收缩情况（两侧收缩，n=2）：")
    print("修正公式：Q = m * (b - 0.1*n*H) * sqrt(2g) * H^(3/2)")
    print("-" * 90)
    print(f"{'水头H(m)':^12} | {'有效宽度(m)':^15} | {'流量Q(m³/s)':^15} | {'流量减少率(%)':^15}")
    print("-" * 90)

    for i, H in enumerate(H_values):
        Q_no = Q_no_contraction[i]
        Q_yes = weir.discharge_rectangular(H, with_contraction=True)
        b_eff = b - 0.1 * 2 * H
        reduction = (Q_no - Q_yes) / Q_no * 100

        print(f"{H:^12.3f} | {b_eff:^15.4f} | {Q_yes:^15.4f} | {reduction:^15.2f}")

    print("-" * 90)

    # ==================== 第四步：水头反算 ====================
    print("\n【步骤4】水头反算（已知流量）")
    print("-" * 80)

    Q_design_values = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50]

    print("\n设计流量对应的堰顶水头：")
    print("-" * 80)
    print(f"{'设计流量Q(m³/s)':^18} | {'所需水头H(m)':^18} | {'上游水深h(m)':^18}")
    print("-" * 80)

    P = 0.20  # 假设堰顶高程为0.20m

    for Q_design in Q_design_values:
        H_required = weir.head_from_discharge(Q_design)
        h_upstream = P + H_required  # 上游水深

        print(f"{Q_design:^18.3f} | {H_required:^18.4f} | {h_upstream:^18.4f}")

    print("-" * 80)
    print(f"注：假设堰顶高程 P = {P} m")

    # ==================== 第五步：三角形堰对比 ====================
    print("\n【步骤5】三角形堰对比")
    print("-" * 80)

    print("\n90度三角形堰（V型堰）：")
    print("公式：Q = (8/15) * m * sqrt(2g) * tan(θ/2) * H^(5/2)")
    print("\n三角形堰适用于小流量测量：")
    print("-" * 80)
    print(f"{'水头H(m)':^15} | {'矩形堰Q(m³/s)':^18} | {'三角形堰Q(m³/s)':^20} | {'Q比值':^12}")
    print("-" * 80)

    H_small = [0.05, 0.10, 0.15, 0.20, 0.25]
    for H in H_small:
        Q_rect = weir.discharge_rectangular(H, with_contraction=False)
        Q_tri = weir.discharge_triangular(H, theta=90.0)
        ratio = Q_tri / Q_rect

        print(f"{H:^15.3f} | {Q_rect:^18.4f} | {Q_tri:^20.4f} | {ratio:^12.3f}")

    print("-" * 80)
    print("结论：三角形堰在小水头时流量较小，测量精度更高")

    # ==================== 第六步：测量精度分析 ====================
    print("\n【步骤6】测量精度分析")
    print("-" * 80)

    print("\n水头测量误差对流量的影响：")
    print("假设水头测量误差 ΔH = ±1 mm = ±0.001 m")

    H_test = 0.20  # 测试水头
    dH = 0.001     # 水头误差

    Q_nominal = weir.discharge_rectangular(H_test, with_contraction=False)
    Q_plus = weir.discharge_rectangular(H_test + dH, with_contraction=False)
    Q_minus = weir.discharge_rectangular(H_test - dH, with_contraction=False)

    dQ_plus = Q_plus - Q_nominal
    dQ_minus = Q_nominal - Q_minus

    error_percent_plus = dQ_plus / Q_nominal * 100
    error_percent_minus = dQ_minus / Q_nominal * 100

    print(f"\n在 H = {H_test} m 时：")
    print(f"  标称流量：Q = {Q_nominal:.4f} m³/s")
    print(f"  水头增加1mm：Q = {Q_plus:.4f} m³/s，流量增加 {dQ_plus:.4f} m³/s ({error_percent_plus:.2f}%)")
    print(f"  水头减少1mm：Q = {Q_minus:.4f} m³/s，流量减少 {dQ_minus:.4f} m³/s ({error_percent_minus:.2f}%)")

    print(f"\n结论：水头误差1mm导致流量误差约±{(error_percent_plus+error_percent_minus)/2:.2f}%")
    print(f"       要保证流量精度在5%以内，水头测量精度应优于±5mm")

    # ==================== 第七步：工程设计建议 ====================
    print("\n【步骤7】工程设计建议")
    print("-" * 80)

    print("\n基于水力计算的设计方案：")

    print(f"\n1. 堰体结构：")
    print(f"   - 堰型：矩形薄壁堰")
    print(f"   - 堰顶宽度：b = {b} m")
    print(f"   - 堰顶厚度：<2 mm（保持锐利边缘）")
    print(f"   - 堰高：P = 0.20-0.30 m（保证通气）")
    print(f"   - 材料：不锈钢板或铜板（耐腐蚀）")

    print(f"\n2. 测量设施：")
    print(f"   - 水尺位置：堰前 3H_max = {3*0.40:.2f} m 处")
    print(f"   - 水尺精度：±1 mm")
    print(f"   - 读数方式：人工读数或自动水位计")
    print(f"   - 静水井：必要时设置，保证水面平稳")

    print(f"\n3. 流量范围：")
    H_min, H_max = 0.05, 0.40
    Q_min = weir.discharge_rectangular(H_min, with_contraction=False)
    Q_max = weir.discharge_rectangular(H_max, with_contraction=False)
    print(f"   - 最小流量：Q_min = {Q_min:.4f} m³/s (H = {H_min} m)")
    print(f"   - 最大流量：Q_max = {Q_max:.4f} m³/s (H = {H_max} m)")
    print(f"   - 量程比：Q_max/Q_min = {Q_max/Q_min:.1f}")

    print(f"\n4. 使用注意事项：")
    print(f"   - 定期清理堰前淤积")
    print(f"   - 检查堰顶锐利度")
    print(f"   - 避免杂物堵塞")
    print(f"   - 每年率定校核一次")
    print(f"   - 冬季注意防冻")

    print(f"\n5. 精度指标：")
    print(f"   - 水头测量精度：±1 mm")
    print(f"   - 流量测量精度：±3-5%")
    print(f"   - 适用条件：自由出流，通气良好")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
