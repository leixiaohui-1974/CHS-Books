"""
案例9：河道糙率率定 - 主程序

问题描述：
某天然河道进行水文测验，需要根据实测数据反算糙率系数。

实测数据：
- 断面1（上游）：宽度 B₁ = 45 m，水深 h₁ = 3.2 m
- 断面2（下游）：宽度 B₂ = 48 m，水深 h₂ = 3.0 m
- 实测流量：Q = 180 m³/s
- 断面间距：L = 500 m
- 河床平均坡度：S₀ ≈ 0.0004（估算值）

求解：
1. 单断面法率定糙率
2. 双断面法率定糙率
3. 糙率合理性分析
4. 不确定性评估
5. 流量-水位关系

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import RectangularChannel


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def calibrate_roughness_single(Q, B, h, S0):
    """
    单断面法率定糙率

    从 Q = A * (1/n) * R^(2/3) * S^(1/2)
    反算 n = A * R^(2/3) * S^(1/2) / Q
    """
    A = B * h
    P = B + 2 * h
    R = A / P

    n = A * (R ** (2.0/3.0)) * (S0 ** 0.5) / Q

    return n, A, R


def main():
    """主函数"""
    print_separator("案例9：河道糙率率定")

    # ==================== 第一步：实测数据 ====================
    print("\n【步骤1】实测数据")
    print("-" * 80)

    # 断面参数（矩形断面近似）
    B1 = 45.0       # 断面1宽度 (m)
    h1 = 3.2        # 断面1水深 (m)
    B2 = 48.0       # 断面2宽度 (m)
    h2 = 3.0        # 断面2水深 (m)
    Q = 180.0       # 实测流量 (m³/s)
    L = 500.0       # 断面间距 (m)
    S0 = 0.0004     # 河床坡度估算值
    g = 9.81        # 重力加速度

    print(f"断面1（上游）：")
    print(f"  河宽 B₁ = {B1} m")
    print(f"  水深 h₁ = {h1} m")

    print(f"\n断面2（下游）：")
    print(f"  河宽 B₂ = {B2} m")
    print(f"  水深 h₂ = {h2} m")

    print(f"\n测量条件：")
    print(f"  实测流量 Q = {Q} m³/s")
    print(f"  断面间距 L = {L} m")
    print(f"  河床坡度 S₀ = {S0}（估算）")

    # ==================== 第二步：单断面法率定（断面1） ====================
    print("\n【步骤2】单断面法率定糙率（断面1）")
    print("-" * 80)

    n1, A1, R1 = calibrate_roughness_single(Q, B1, h1, S0)
    v1 = Q / A1
    Fr1 = v1 / np.sqrt(g * h1)

    print(f"\n断面1几何参数：")
    print(f"  过流面积 A₁ = {A1:.4f} m²")
    print(f"  湿周 P₁ = {B1 + 2*h1:.4f} m")
    print(f"  水力半径 R₁ = {R1:.4f} m")

    print(f"\n断面1水力参数：")
    print(f"  流速 v₁ = Q/A₁ = {v1:.4f} m/s")
    print(f"  弗劳德数 Fr₁ = {Fr1:.4f}")

    print(f"\n糙率率定结果：")
    print(f"  Manning糙率 n₁ = {n1:.4f}")

    # ==================== 第三步：单断面法率定（断面2） ====================
    print("\n【步骤3】单断面法率定糙率（断面2）")
    print("-" * 80)

    n2, A2, R2 = calibrate_roughness_single(Q, B2, h2, S0)
    v2 = Q / A2
    Fr2 = v2 / np.sqrt(g * h2)

    print(f"\n断面2几何参数：")
    print(f"  过流面积 A₂ = {A2:.4f} m²")
    print(f"  湿周 P₂ = {B2 + 2*h2:.4f} m")
    print(f"  水力半径 R₂ = {R2:.4f} m")

    print(f"\n断面2水力参数：")
    print(f"  流速 v₂ = Q/A₂ = {v2:.4f} m/s")
    print(f"  弗劳德数 Fr₂ = {Fr2:.4f}")

    print(f"\n糙率率定结果：")
    print(f"  Manning糙率 n₂ = {n2:.4f}")

    # ==================== 第四步：双断面法率定 ====================
    print("\n【步骤4】双断面法率定糙率")
    print("-" * 80)

    # 计算比能
    E1 = h1 + v1**2 / (2*g)
    E2 = h2 + v2**2 / (2*g)

    # 水面坡度
    Sf = (E1 - E2) / L

    print(f"\n能量分析：")
    print(f"  断面1比能 E₁ = {E1:.4f} m")
    print(f"  断面2比能 E₂ = {E2:.4f} m")
    print(f"  能量损失 ΔE = {E1 - E2:.4f} m")

    print(f"\n水面坡度：")
    print(f"  Sf = ΔE / L = {Sf:.6f}")
    print(f"  河床坡度 S₀ = {S0:.6f}（估算）")
    print(f"  比较：Sf/S₀ = {Sf/S0:.3f}")

    # 使用平均断面参数计算糙率
    A_avg = (A1 + A2) / 2
    R_avg = (R1 + R2) / 2

    n_avg = A_avg * (R_avg ** (2.0/3.0)) * (Sf ** 0.5) / Q

    print(f"\n平均断面参数：")
    print(f"  平均面积 A_avg = {A_avg:.4f} m²")
    print(f"  平均水力半径 R_avg = {R_avg:.4f} m")

    print(f"\n双断面法糙率率定结果：")
    print(f"  Manning糙率 n_avg = {n_avg:.4f}")
    print(f"  （基于实测水面坡度）")

    # ==================== 第五步：率定结果综合分析 ====================
    print("\n【步骤5】率定结果综合分析")
    print("-" * 80)

    print(f"\n糙率率定结果汇总：")
    print("-" * 80)
    print(f"{'方法':^20} | {'糙率n':^15} | {'依据':^35}")
    print("-" * 80)
    print(f"{'断面1（单断面法）':^20} | {n1:^15.4f} | {'基于河床坡度S₀':^35}")
    print(f"{'断面2（单断面法）':^20} | {n2:^15.4f} | {'基于河床坡度S₀':^35}")
    print(f"{'双断面法':^20} | {n_avg:^15.4f} | {'基于实测水面坡度Sf':^35}")
    print("-" * 80)

    # 推荐值
    n_recommended = n_avg
    n_min = min(n1, n2, n_avg)
    n_max = max(n1, n2, n_avg)
    n_range = n_max - n_min

    print(f"\n统计特征：")
    print(f"  最小值：n_min = {n_min:.4f}")
    print(f"  最大值：n_max = {n_max:.4f}")
    print(f"  变化范围：Δn = {n_range:.4f}")
    print(f"  变异系数：CV = {n_range/(n_min+n_max)*2:.2%}")

    print(f"\n推荐糙率值：")
    print(f"  n = {n_recommended:.4f}（采用双断面法结果）")
    print(f"  不确定性：±{n_range/2:.4f}")

    # ==================== 第六步：糙率合理性检验 ====================
    print("\n【步骤6】糙率合理性检验")
    print("-" * 80)

    # 经验糙率值
    roughness_table = [
        ("光滑混凝土", 0.012, 0.015),
        ("浆砌石", 0.020, 0.025),
        ("卵石河床", 0.025, 0.035),
        ("天然河道（清洁）", 0.025, 0.035),
        ("天然河道（一般）", 0.030, 0.040),
        ("天然河道（杂草）", 0.035, 0.050),
        ("淤泥、水草", 0.040, 0.060),
    ]

    print(f"\n经验糙率值对照表：")
    print("-" * 90)
    print(f"{'河床类型':^20} | {'糙率范围n':^20} | {'本案例n={n_recommended:.3f}':^30}")
    print("-" * 90)

    for bed_type, n_low, n_high in roughness_table:
        if n_low <= n_recommended <= n_high:
            match = "✓ 符合"
        else:
            match = ""

        print(f"{bed_type:^20} | {f'{n_low:.3f} - {n_high:.3f}':^20} | {match:^30}")

    print("-" * 90)

    # 判断河床类型
    if 0.025 <= n_recommended <= 0.035:
        bed_description = "卵石河床或清洁天然河道"
    elif 0.030 <= n_recommended <= 0.040:
        bed_description = "一般天然河道"
    elif 0.035 <= n_recommended <= 0.050:
        bed_description = "有杂草的天然河道"
    else:
        bed_description = "需要现场确认"

    print(f"\n河床类型判断：{bed_description}")

    # ==================== 第七步：不确定性分析 ====================
    print("\n【步骤7】糙率不确定性分析")
    print("-" * 80)

    print(f"\n测量误差假设：")
    delta_Q = 0.05 * Q  # 流量误差±5%
    delta_h = 0.02      # 水深误差±2cm
    delta_B = 0.5       # 宽度误差±0.5m
    delta_S = 0.00005   # 坡度误差

    print(f"  流量误差：ΔQ = ±{delta_Q/Q*100:.1f}% = ±{delta_Q:.2f} m³/s")
    print(f"  水深误差：Δh = ±{delta_h} m")
    print(f"  宽度误差：ΔB = ±{delta_B} m")
    print(f"  坡度误差：ΔS = ±{delta_S:.6f}")

    # 计算糙率的不确定性（简化分析）
    delta_A = B1 * delta_h + h1 * delta_B  # 面积误差
    delta_R = delta_A / (B1 + 2*h1)  # 水力半径误差（简化）

    # 糙率相对误差（从公式微分得到）
    delta_n_Q = delta_Q / Q
    delta_n_A = delta_A / A1
    delta_n_R = (2.0/3.0) * delta_R / R1
    delta_n_S = (1.0/2.0) * delta_S / S0

    delta_n_total = np.sqrt(delta_n_Q**2 + delta_n_A**2 + delta_n_R**2 + delta_n_S**2)
    delta_n_absolute = n_recommended * delta_n_total

    print(f"\n糙率不确定性分析：")
    print(f"  流量影响：Δn/n ≈ ΔQ/Q = {delta_n_Q*100:.2f}%")
    print(f"  面积影响：Δn/n ≈ ΔA/A = {delta_n_A*100:.2f}%")
    print(f"  水力半径影响：Δn/n ≈ (2/3)*ΔR/R = {delta_n_R*100:.2f}%")
    print(f"  坡度影响：Δn/n ≈ (1/2)*ΔS/S = {delta_n_S*100:.2f}%")

    print(f"\n总不确定性（均方根）：")
    print(f"  相对不确定性：Δn/n = {delta_n_total*100:.2f}%")
    print(f"  绝对不确定性：Δn = ±{delta_n_absolute:.4f}")

    print(f"\n糙率取值建议：")
    print(f"  n = {n_recommended:.3f} ± {delta_n_absolute:.3f}")
    print(f"  或 n = {n_recommended:.3f}（变化范围{n_recommended-delta_n_absolute:.3f}-{n_recommended+delta_n_absolute:.3f}）")

    # ==================== 第八步：流量-水位关系 ====================
    print("\n【步骤8】建立流量-水位关系")
    print("-" * 80)

    print(f"\n使用率定的糙率计算不同流量下的水深：")

    # 创建河道对象
    channel = RectangularChannel(b=B1, S0=S0, n=n_recommended)

    Q_values = [50, 100, 150, 180, 200, 250, 300]

    print("-" * 90)
    print(f"{'流量Q(m³/s)':^15} | {'正常水深h(m)':^16} | {'流速v(m/s)':^14} | {'弗劳德数Fr':^15}")
    print("-" * 90)

    Q_list = []
    h_list = []

    for Q_test in Q_values:
        try:
            h_test = channel.compute_normal_depth(Q_test)
            v_test = Q_test / (B1 * h_test)
            Fr_test = channel.froude_number(h_test, Q_test)

            Q_list.append(Q_test)
            h_list.append(h_test)

            print(f"{Q_test:^15.0f} | {h_test:^16.4f} | {v_test:^14.4f} | {Fr_test:^15.4f}")
        except:
            print(f"{Q_test:^15.0f} | {'计算失败':^16} | {'':^14} | {'':^15}")

    print("-" * 90)

    # 拟合Q-h关系（幂函数）
    if len(Q_list) >= 3:
        log_Q = np.log(Q_list)
        log_h = np.log(h_list)
        coeffs = np.polyfit(log_Q, log_h, 1)
        b_coef = coeffs[0]
        log_a = coeffs[1]
        a_coef = np.exp(log_a)

        print(f"\n流量-水位关系拟合：")
        print(f"  h = a * Q^b")
        print(f"  其中：a = {a_coef:.6f}, b = {b_coef:.4f}")
        print(f"  或：Q = {1/a_coef:.4f} * h^{1/b_coef:.4f}")

        print(f"\n说明：")
        print(f"  - 该关系适用于本河段")
        print(f"  - 适用流量范围：{min(Q_list):.0f}-{max(Q_list):.0f} m³/s")
        print(f"  - 糙率n = {n_recommended:.3f}")
        print(f"  - 需要定期复核（河床变化时）")

    # ==================== 第九步：工程应用建议 ====================
    print("\n【步骤9】工程应用建议")
    print("-" * 80)

    print(f"\n基于糙率率定的工程建议：")

    print(f"\n1. 糙率取值：")
    print(f"   - 率定糙率：n = {n_recommended:.3f}")
    print(f"   - 不确定性：±{delta_n_absolute:.3f}")
    print(f"   - 河床类型：{bed_description}")
    print(f"   - 建议范围：{n_recommended-delta_n_absolute:.3f} - {n_recommended+delta_n_absolute:.3f}")

    print(f"\n2. 适用条件：")
    print(f"   - 流量范围：{min(Q_list):.0f} - {max(Q_list):.0f} m³/s")
    print(f"   - 水深范围：{min(h_list):.1f} - {max(h_list):.1f} m")
    print(f"   - 河床状况：当前测量时期")
    print(f"   - 植被状况：需要季节性调整")

    print(f"\n3. 使用建议：")
    print(f"   - 洪水位推算：采用偏大值 n = {n_recommended+delta_n_absolute:.3f}（保守）")
    print(f"   - 一般计算：采用推荐值 n = {n_recommended:.3f}")
    print(f"   - 设计流量：Q = {Q:.0f} m³/s，h = {h1:.2f} m")

    print(f"\n4. 注意事项：")
    print(f"   - 季节变化：汛期糙率小，枯水期糙率大")
    print(f"   - 河床变化：定期复核糙率（建议每年一次）")
    print(f"   - 分段考虑：不同河段糙率可能不同")
    print(f"   - 复合断面：主槽和滩地分别考虑")

    print(f"\n5. 后续工作：")
    print(f"   - 多次测量：不同流量下的率定")
    print(f"   - 建立数据库：糙率-流量-季节关系")
    print(f"   - 现场调查：核实河床状况")
    print(f"   - 敏感性分析：糙率变化对水位的影响")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
