"""
案例5：渠道闸门出流计算 - 主程序

问题描述：
某灌区干渠闸门设计，已知：
- 闸门宽度 b = 2.0 m
- 流量系数 μ = 0.60
- 上游水深 H = 3.0 m
- 闸门开度 e = 0.3-1.2 m
- 下游水深 h2 = 1.0-2.5 m

求解：
1. 不同开度下的自由出流流量
2. 淹没出流计算
3. 出流形态判别
4. 给定流量反算开度
5. 下游水深影响分析

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


def main():
    """主函数"""
    print_separator("案例5：渠道闸门出流计算")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    b = 2.0      # 闸门宽度 (m)
    mu = 0.60    # 流量系数
    H = 3.0      # 上游水深 (m)

    print(f"水工建筑物：平板闸门")
    print(f"闸门宽度 b = {b} m")
    print(f"流量系数 μ = {mu}")
    print(f"上游水深 H = {H} m")
    print(f"重力加速度 g = 9.81 m/s²")

    # ==================== 第二步：创建闸门对象 ====================
    print("\n【步骤2】创建闸门模型")
    print("-" * 80)

    gate = Gate(b=b, mu=mu)
    print(f"闸门对象：{gate}")

    # ==================== 第三步：自由出流计算 ====================
    print("\n【步骤3】自由出流计算（忽略下游水深影响）")
    print("-" * 80)

    e_values = [0.3, 0.5, 0.7, 0.9, 1.2, 1.5]

    print("\n自由出流公式：Q = μ * b * e * sqrt(2g * H)")
    print("假设：下游水深足够小，不影响出流")
    print("-" * 100)
    print(f"{'开度e(m)':^12} | {'流量Q(m³/s)':^15} | {'闸下流速v(m/s)':^16} | {'单宽流量q(m²/s)':^18}")
    print("-" * 100)

    for e in e_values:
        Q = gate.discharge_free(e, H)
        v = Q / (b * e)  # 闸下平均流速（近似）
        q = Q / b

        print(f"{e:^12.2f} | {Q:^15.4f} | {v:^16.4f} | {q:^18.4f}")

    print("-" * 100)
    print("说明：流量与开度成正比，开度增大一倍，流量也增大一倍")

    # ==================== 第四步：淹没出流计算 ====================
    print("\n【步骤4】淹没出流计算（考虑下游水深影响）")
    print("-" * 80)

    e_test = 0.8  # 测试开度
    h2_values = [0.5, 1.0, 1.5, 2.0, 2.5]

    print(f"\n固定开度 e = {e_test} m")
    print("淹没出流公式：Q = μ * b * e * sqrt(2g * (H - h2))")
    print("-" * 110)
    print(f"{'下游水深h2(m)':^15} | {'作用水头(m)':^15} | {'流量Q(m³/s)':^15} | {'淹没度σ':^12} | {'出流形态':^15}")
    print("-" * 110)

    Q_free_ref = gate.discharge_free(e_test, H)

    for h2 in h2_values:
        # 判断出流形态
        is_submerged = gate.check_submergence(e_test, H, h2)

        if is_submerged:
            Q = gate.discharge_submerged(e_test, H, h2)
            flow_type = "淹没出流"
        else:
            Q = Q_free_ref
            flow_type = "自由出流"

        delta_H = H - h2
        sigma = h2 / H

        print(f"{h2:^15.2f} | {delta_H:^15.2f} | {Q:^15.4f} | {sigma:^12.3f} | {flow_type:^15}")

    print("-" * 110)
    print("说明：")
    print("  - 淹没度 σ = h2/H < 0.6：自由出流")
    print("  - 淹没度 σ = h2/H > 0.8：完全淹没出流")
    print("  - 0.6 < σ < 0.8：过渡区")

    # ==================== 第五步：出流形态判别 ====================
    print("\n【步骤5】出流形态判别")
    print("-" * 80)

    print("\n临界淹没条件分析：")
    print("-" * 100)
    print(f"{'开度e(m)':^12} | {'收缩水深hc(m)':^16} | {'临界h2(m)':^15} | {'判别条件':^35}")
    print("-" * 100)

    Cc = 0.61  # 收缩系数
    for e in [0.3, 0.5, 0.7, 1.0, 1.2]:
        hc = Cc * e
        h2_crit = 0.8 * H  # 临界淹没水深（经验值）
        condition = f"h2 < {h2_crit:.2f}m 为自由出流"

        print(f"{e:^12.2f} | {hc:^16.3f} | {h2_crit:^15.2f} | {condition:^35}")

    print("-" * 100)

    # ==================== 第六步：开度反算 ====================
    print("\n【步骤6】开度反算（给定流量求开度）")
    print("-" * 80)

    Q_design_values = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0]

    print("\n设计流量对应的闸门开度：")
    print("假设自由出流条件")
    print("-" * 90)
    print(f"{'设计流量Q(m³/s)':^18} | {'所需开度e(m)':^18} | {'开度比e/H':^15} | {'适用性':^15}")
    print("-" * 90)

    for Q_design in Q_design_values:
        e_required = gate.opening_from_discharge(Q_design, H)
        e_ratio = e_required / H

        # 判断开度是否合理
        if e_required < 0.1:
            suitability = "过小（易堵）"
        elif e_required > 0.8 * H:
            suitability = "过大（不稳）"
        else:
            suitability = "合理"

        print(f"{Q_design:^18.2f} | {e_required:^18.4f} | {e_ratio:^15.3f} | {suitability:^15}")

    print("-" * 90)
    print("建议：开度比 e/H 应在 0.1-0.6 范围内，保证出流稳定且便于调节")

    # ==================== 第七步：流量系数影响 ====================
    print("\n【步骤7】流量系数 μ 的影响分析")
    print("-" * 80)

    e_ref = 0.8
    mu_values = [0.55, 0.58, 0.60, 0.62, 0.65]
    mu_descriptions = ["老旧闸门", "一般闸门", "标准平板", "良好状态", "弧形闸门"]

    print(f"\n固定参数：H = {H} m, e = {e_ref} m")
    print("-" * 100)
    print(f"{'流量系数μ':^12} | {'闸门描述':^15} | {'流量Q(m³/s)':^15} | {'与标准值差异(%)':^20}")
    print("-" * 100)

    Q_standard = None
    for mu_val, desc in zip(mu_values, mu_descriptions):
        gate_temp = Gate(b=b, mu=mu_val)
        Q = gate_temp.discharge_free(e_ref, H)

        if abs(mu_val - 0.60) < 1e-6:
            Q_standard = Q
            diff = 0.0
        elif Q_standard is not None:
            diff = (Q - Q_standard) / Q_standard * 100
        else:
            diff = 0.0

        print(f"{mu_val:^12.3f} | {desc:^15} | {Q:^15.4f} | {diff:^20.2f}")

    print("-" * 100)
    print("结论：流量系数偏差8%会导致流量偏差约8%，需要现场率定")

    # ==================== 第八步：能量损失分析 ====================
    print("\n【步骤8】能量损失分析")
    print("-" * 80)

    e_loss = 0.8
    Q_loss = gate.discharge_free(e_loss, H)

    print(f"\n计算条件：H = {H} m, e = {e_loss} m, Q = {Q_loss:.4f} m³/s")
    print("\n不同下游水深的能量损失：")
    print("-" * 110)
    print(f"{'下游水深h2(m)':^15} | {'下游流速v2(m/s)':^18} | {'速度水头(m)':^15} | {'水头损失(m)':^15} | {'损失率(%)':^12}")
    print("-" * 110)

    for h2 in [1.0, 1.5, 2.0, 2.5, 3.0]:
        v2 = Q_loss / (b * h2)  # 下游流速
        v2_head = v2**2 / (2 * 9.81)  # 速度水头

        # 水头损失（近似）
        dH = H - h2 - v2_head

        # 损失率
        loss_ratio = dH / H * 100 if H > 0 else 0

        print(f"{h2:^15.2f} | {v2:^18.4f} | {v2_head:^15.4f} | {dH:^15.4f} | {loss_ratio:^12.2f}")

    print("-" * 110)

    # ==================== 第九步：工程设计建议 ====================
    print("\n【步骤9】工程设计建议")
    print("-" * 80)

    print("\n基于水力计算的设计方案：")

    print(f"\n1. 闸门结构：")
    print(f"   - 闸型：平板闸门")
    print(f"   - 闸门宽度：b = {b} m")
    print(f"   - 开度范围：0.2-{0.6*H:.1f} m")
    print(f"   - 启闭方式：电动或手动")

    print(f"\n2. 流量控制：")
    Q_min = gate.discharge_free(0.2, H)
    Q_max = gate.discharge_free(0.6*H, H)
    print(f"   - 最小流量：Q_min = {Q_min:.4f} m³/s (e = 0.2 m)")
    print(f"   - 最大流量：Q_max = {Q_max:.4f} m³/s (e = {0.6*H:.1f} m)")
    print(f"   - 调节比：Q_max/Q_min = {Q_max/Q_min:.1f}")

    print(f"\n3. 运行条件：")
    print(f"   - 上游水深：H = {H-0.5:.1f}-{H+0.5:.1f} m")
    print(f"   - 下游水深：h2 < {0.6*H:.2f} m（保证自由出流）")
    print(f"   - 流量系数：μ = {mu}（需现场率定）")

    print(f"\n4. 消能措施：")
    print(f"   - 闸后海漫长度：L = 5-8倍闸孔宽度")
    print(f"   - 消力池深度：d = 0.3-0.5倍水头差")
    print(f"   - 防冲刷：混凝土护底或抛石")

    print(f"\n5. 运行管理：")
    print(f"   - 启闭速度：< 0.2 m/min（防止水锤）")
    print(f"   - 检修周期：每年汛前汛后各一次")
    print(f"   - 监测项目：闸前水位、闸后水位、流量")
    print(f"   - 维护重点：密封橡皮、启闭机、闸槽")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
