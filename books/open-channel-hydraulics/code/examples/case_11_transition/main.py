"""
案例11：渠道变宽与收缩 - 主程序

问题描述：
某灌溉渠道需要进行断面变化，已知：
- 上游断面宽度 B₁ = 4.0 m
- 下游断面宽度（扩散）B₂ = 6.0 m
- 下游断面宽度（收缩）B₂ = 3.0 m
- 渠底坡度 S₀ = 0.0002
- 糙率 n = 0.020（混凝土衬砌）
- 设计流量 Q = 12 m³/s
- 渐变段长度 L = 20 m

求解：
1. 扩散段上下游水深及水面线
2. 收缩段上下游水深及水面线
3. 渐变段能量损失
4. 合理的渐变段长度
5. 渐变与突然过渡的比较

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


def expansion_loss_coefficient(theta_deg: float, gradual: bool = True) -> float:
    """计算扩散损失系数

    Args:
        theta_deg: 扩散角（度）
        gradual: True为渐变扩散，False为突然扩散
    """
    if not gradual:
        return 1.0  # 突然扩散，Borda-Carnot

    # 渐变扩散
    if theta_deg <= 10:
        return 0.15
    elif theta_deg <= 12.5:
        return 0.20
    else:
        return 0.30


def contraction_loss_coefficient(A1: float, A2: float, gradual: bool = True) -> float:
    """计算收缩损失系数

    Args:
        A1: 上游断面面积
        A2: 下游断面面积
        gradual: True为渐变收缩，False为突然收缩
    """
    if not gradual:
        return 0.5 * (1 - A2/A1)

    # 渐变收缩
    return 0.08


def compute_expansion_flow(B1: float, B2: float, Q: float, n: float, S0: float,
                          L: float, gradual: bool = True) -> dict:
    """计算扩散段流动

    Returns:
        包含上下游水深、流速、能量损失等信息的字典
    """
    g = 9.81

    # 下游断面（宽断面）- 正常水深作为控制水深
    channel2 = RectangularChannel(b=B2, S0=S0, n=n)
    h2 = channel2.compute_normal_depth(Q)
    v2 = Q / (B2 * h2)
    E2 = h2 + v2**2 / (2*g)
    Fr2 = channel2.froude_number(h2)

    # 计算扩散角
    theta_rad = np.arctan((B2 - B1) / (2 * L))
    theta_deg = np.degrees(theta_rad)

    # 扩散损失系数
    zeta = expansion_loss_coefficient(theta_deg, gradual)

    # 上游断面水深（迭代求解）
    # 能量方程：E1 + S0*L = E2 + hf
    # hf = zeta * (v1^2 - v2^2)/(2g) + Sf_avg*L

    h1 = h2 * 0.8  # 初始猜测
    for i in range(100):
        A1 = B1 * h1
        v1 = Q / A1
        E1 = h1 + v1**2 / (2*g)

        # 局部损失
        hf_local = zeta * (v1**2 - v2**2) / (2*g)

        # 沿程损失（平均摩阻坡度）
        # Sf = n² * Q² / (A² * R^(4/3))
        channel1 = RectangularChannel(b=B1, S0=S0, n=n)
        A1 = B1 * h1
        R1 = channel1.hydraulic_radius(h1)
        Sf1 = n**2 * Q**2 / (A1**2 * R1**(4.0/3.0))

        A2 = B2 * h2
        R2 = channel2.hydraulic_radius(h2)
        Sf2 = n**2 * Q**2 / (A2**2 * R2**(4.0/3.0))

        Sf_avg = (Sf1 + Sf2) / 2
        hf_friction = Sf_avg * L

        # 总损失
        hf_total = hf_local + hf_friction

        # 能量方程残差
        f = E1 - E2 - S0*L + hf_total

        if abs(f) < 1e-6:
            break

        # 数值导数
        dh = 1e-6
        A1_plus = B1 * (h1 + dh)
        v1_plus = Q / A1_plus
        E1_plus = (h1 + dh) + v1_plus**2 / (2*g)
        R1_plus = channel1.hydraulic_radius(h1 + dh)
        Sf1_plus = n**2 * Q**2 / (A1_plus**2 * R1_plus**(4.0/3.0))
        Sf_avg_plus = (Sf1_plus + Sf2) / 2
        hf_friction_plus = Sf_avg_plus * L
        hf_local_plus = zeta * (v1_plus**2 - v2**2) / (2*g)
        hf_total_plus = hf_local_plus + hf_friction_plus
        f_plus = E1_plus - E2 - S0*L + hf_total_plus

        df = (f_plus - f) / dh

        if abs(df) > 1e-12:
            h1 = h1 - f / df

        if h1 <= 0:
            h1 = h2 * 0.5

    # 上游断面参数
    v1 = Q / (B1 * h1)
    E1 = h1 + v1**2 / (2*g)
    Fr1 = v1 / np.sqrt(g * h1)

    return {
        'B1': B1,
        'B2': B2,
        'h1': h1,
        'h2': h2,
        'v1': v1,
        'v2': v2,
        'E1': E1,
        'E2': E2,
        'Fr1': Fr1,
        'Fr2': Fr2,
        'theta_deg': theta_deg,
        'zeta': zeta,
        'hf_local': hf_local,
        'hf_friction': hf_friction,
        'hf_total': hf_total,
        'water_rise': h2 - h1
    }


def compute_contraction_flow(B1: float, B2: float, Q: float, n: float, S0: float,
                             L: float, gradual: bool = True) -> dict:
    """计算收缩段流动"""
    g = 9.81

    # 上游断面（宽断面）- 正常水深
    channel1 = RectangularChannel(b=B1, S0=S0, n=n)
    h1 = channel1.compute_normal_depth(Q)
    v1 = Q / (B1 * h1)
    E1 = h1 + v1**2 / (2*g)
    Fr1 = channel1.froude_number(h1)

    # 计算收缩角
    theta_rad = np.arctan((B1 - B2) / (2 * L))
    theta_deg = np.degrees(theta_rad)

    # 收缩损失系数
    A1 = B1 * h1
    zeta = contraction_loss_coefficient(A1, B2*h1, gradual)

    # 下游断面水深（迭代求解）
    h2 = h1  # 初始猜测
    for i in range(100):
        A2 = B2 * h2
        v2 = Q / A2
        E2 = h2 + v2**2 / (2*g)

        # 局部损失（基于下游流速）
        hf_local = zeta * v2**2 / (2*g)

        # 沿程损失
        channel2 = RectangularChannel(b=B2, S0=S0, n=n)
        A1_temp = B1 * h1
        R1 = channel1.hydraulic_radius(h1)
        Sf1 = n**2 * Q**2 / (A1_temp**2 * R1**(4.0/3.0))

        R2 = channel2.hydraulic_radius(h2)
        Sf2 = n**2 * Q**2 / (A2**2 * R2**(4.0/3.0))

        Sf_avg = (Sf1 + Sf2) / 2
        hf_friction = Sf_avg * L

        # 总损失
        hf_total = hf_local + hf_friction

        # 能量方程
        f = E1 - E2 + S0*L - hf_total

        if abs(f) < 1e-6:
            break

        # 数值导数
        dh = 1e-6
        A2_plus = B2 * (h2 + dh)
        v2_plus = Q / A2_plus
        E2_plus = (h2 + dh) + v2_plus**2 / (2*g)
        R2_plus = channel2.hydraulic_radius(h2 + dh)
        Sf2_plus = n**2 * Q**2 / (A2_plus**2 * R2_plus**(4.0/3.0))
        Sf_avg_plus = (Sf1 + Sf2_plus) / 2
        hf_friction_plus = Sf_avg_plus * L
        hf_local_plus = zeta * v2_plus**2 / (2*g)
        hf_total_plus = hf_local_plus + hf_friction_plus
        f_plus = E1 - E2_plus + S0*L - hf_total_plus

        df = (f_plus - f) / dh

        if abs(df) > 1e-12:
            h2 = h2 - f / df

        if h2 <= 0:
            h2 = h1 * 0.9

    # 下游参数
    v2 = Q / (B2 * h2)
    E2 = h2 + v2**2 / (2*g)
    Fr2 = v2 / np.sqrt(g * h2)

    return {
        'B1': B1,
        'B2': B2,
        'h1': h1,
        'h2': h2,
        'v1': v1,
        'v2': v2,
        'E1': E1,
        'E2': E2,
        'Fr1': Fr1,
        'Fr2': Fr2,
        'theta_deg': theta_deg,
        'zeta': zeta,
        'hf_local': hf_local,
        'hf_friction': hf_friction,
        'hf_total': hf_total,
        'water_drop': h1 - h2
    }


def main():
    """主函数"""
    print_separator("案例11：渠道变宽与收缩")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    B1 = 4.0      # 上游断面宽度 (m)
    B2_exp = 6.0  # 扩散下游宽度 (m)
    B2_con = 3.0  # 收缩下游宽度 (m)
    Q = 12.0      # 流量 (m³/s)
    n = 0.020     # 糙率
    S0 = 0.0002   # 渠底坡度
    L = 20.0      # 渐变段长度 (m)

    print(f"渠道参数：")
    print(f"  上游断面宽度 B₁ = {B1} m")
    print(f"  扩散下游宽度 B₂ = {B2_exp} m")
    print(f"  收缩下游宽度 B₂ = {B2_con} m")
    print(f"  流量 Q = {Q} m³/s")
    print(f"  糙率 n = {n}")
    print(f"  渠底坡度 S₀ = {S0}")
    print(f"  渐变段长度 L = {L} m")

    # ==================== 第二步：扩散段计算（渐变） ====================
    print("\n【步骤2】扩散段计算（B₁ = 4m → B₂ = 6m，渐变）")
    print("-" * 80)

    exp_grad = compute_expansion_flow(B1, B2_exp, Q, n, S0, L, gradual=True)

    print(f"\n渐变参数：")
    print(f"  渐变段长度 L = {L} m")
    print(f"  宽度增量 ΔB = {B2_exp - B1} m")
    print(f"  渐变角 θ = {exp_grad['theta_deg']:.2f}°")

    if exp_grad['theta_deg'] <= 12.5:
        grade = "良好（推荐）"
    else:
        grade = "偏大（不推荐）"
    print(f"  角度评价：{grade}")

    print(f"\n水力参数：")
    print(f"  上游水深 h₁ = {exp_grad['h1']:.4f} m")
    print(f"  下游水深 h₂ = {exp_grad['h2']:.4f} m")
    print(f"  水面壅高 Δh = {exp_grad['water_rise']:.4f} m")
    print(f"  上游流速 v₁ = {exp_grad['v1']:.3f} m/s")
    print(f"  下游流速 v₂ = {exp_grad['v2']:.3f} m/s")
    print(f"  流速降低 Δv = {exp_grad['v1']-exp_grad['v2']:.3f} m/s")

    print(f"\n能量损失：")
    print(f"  局部损失 hf_local = {exp_grad['hf_local']:.5f} m")
    print(f"  沿程损失 hf_friction = {exp_grad['hf_friction']:.5f} m")
    print(f"  总损失 hf_total = {exp_grad['hf_total']:.5f} m")
    print(f"  损失系数 ζ = {exp_grad['zeta']:.2f}")
    print(f"  损失率 = {exp_grad['hf_total']/exp_grad['E1']*100:.2f}%")

    print(f"\n水流形态：")
    print(f"  上游Fr = {exp_grad['Fr1']:.3f}（{'缓流' if exp_grad['Fr1']<1 else '急流'}）")
    print(f"  下游Fr = {exp_grad['Fr2']:.3f}（{'缓流' if exp_grad['Fr2']<1 else '急流'}）")

    # ==================== 第三步：扩散段计算（突然） ====================
    print("\n【步骤3】扩散段计算（突然扩散，对比）")
    print("-" * 80)

    exp_sudden = compute_expansion_flow(B1, B2_exp, Q, n, S0, L, gradual=False)

    print(f"\n突然扩散特点：")
    print(f"  无渐变段或渐变角过大（θ > 12.5°）")
    print(f"  损失系数 ζ = {exp_sudden['zeta']:.2f}（Borda-Carnot公式）")

    print(f"\n水力参数（突然扩散）：")
    print(f"  上游水深 h₁ = {exp_sudden['h1']:.4f} m")
    print(f"  下游水深 h₂ = {exp_sudden['h2']:.4f} m")
    print(f"  水面壅高 Δh = {exp_sudden['water_rise']:.4f} m")

    print(f"\n能量损失对比：")
    print("-" * 80)
    print(f"{'过渡方式':^15} | {'局部损失(m)':^15} | {'总损失(m)':^13} | {'损失率(%)':^12} | {'增加倍数':^12}")
    print("-" * 80)
    print(f"{'渐变扩散':^15} | {exp_grad['hf_local']:^15.5f} | {exp_grad['hf_total']:^13.5f} | "
          f"{exp_grad['hf_total']/exp_grad['E1']*100:^12.2f} | {1.0:^12.2f}")
    print(f"{'突然扩散':^15} | {exp_sudden['hf_local']:^15.5f} | {exp_sudden['hf_total']:^13.5f} | "
          f"{exp_sudden['hf_total']/exp_sudden['E1']*100:^12.2f} | "
          f"{exp_sudden['hf_local']/exp_grad['hf_local']:^12.2f}")
    print("-" * 80)

    print("\n【结论】突然扩散的能量损失是渐变扩散的 "
          f"{exp_sudden['hf_local']/exp_grad['hf_local']:.1f} 倍！")

    # ==================== 第四步：收缩段计算（渐变） ====================
    print("\n【步骤4】收缩段计算（B₁ = 4m → B₂ = 3m，渐变）")
    print("-" * 80)

    con_grad = compute_contraction_flow(B1, B2_con, Q, n, S0, L, gradual=True)

    print(f"\n渐变参数：")
    print(f"  渐变段长度 L = {L} m")
    print(f"  宽度减量 ΔB = {B1 - B2_con} m")
    print(f"  渐变角 θ = {con_grad['theta_deg']:.2f}°")

    if con_grad['theta_deg'] <= 30:
        grade = "良好（推荐）"
    else:
        grade = "偏大（不推荐）"
    print(f"  角度评价：{grade}")

    print(f"\n水力参数：")
    print(f"  上游水深 h₁ = {con_grad['h1']:.4f} m")
    print(f"  下游水深 h₂ = {con_grad['h2']:.4f} m")
    print(f"  水面降低 Δh = {con_grad['water_drop']:.4f} m")
    print(f"  上游流速 v₁ = {con_grad['v1']:.3f} m/s")
    print(f"  下游流速 v₂ = {con_grad['v2']:.3f} m/s")
    print(f"  流速增加 Δv = {con_grad['v2']-con_grad['v1']:.3f} m/s")

    print(f"\n能量损失：")
    print(f"  局部损失 hf_local = {con_grad['hf_local']:.5f} m")
    print(f"  沿程损失 hf_friction = {con_grad['hf_friction']:.5f} m")
    print(f"  总损失 hf_total = {con_grad['hf_total']:.5f} m")
    print(f"  损失系数 ζ = {con_grad['zeta']:.2f}")
    print(f"  损失率 = {con_grad['hf_total']/con_grad['E1']*100:.2f}%")

    # ==================== 第五步：收缩段计算（突然） ====================
    print("\n【步骤5】收缩段计算（突然收缩，对比）")
    print("-" * 80)

    con_sudden = compute_contraction_flow(B1, B2_con, Q, n, S0, L, gradual=False)

    print(f"\n能量损失对比：")
    print("-" * 80)
    print(f"{'过渡方式':^15} | {'局部损失(m)':^15} | {'总损失(m)':^13} | {'损失率(%)':^12} | {'增加倍数':^12}")
    print("-" * 80)
    print(f"{'渐变收缩':^15} | {con_grad['hf_local']:^15.5f} | {con_grad['hf_total']:^13.5f} | "
          f"{con_grad['hf_total']/con_grad['E1']*100:^12.2f} | {1.0:^12.2f}")
    print(f"{'突然收缩':^15} | {con_sudden['hf_local']:^15.5f} | {con_sudden['hf_total']:^13.5f} | "
          f"{con_sudden['hf_total']/con_sudden['E1']*100:^12.2f} | "
          f"{con_sudden['hf_local']/con_grad['hf_local']:^12.2f}")
    print("-" * 80)

    print("\n【结论】收缩段的损失远小于扩散段")
    print(f"  - 扩散渐变损失：{exp_grad['hf_local']:.5f} m")
    print(f"  - 收缩渐变损失：{con_grad['hf_local']:.5f} m")
    print(f"  - 扩散/收缩比：{exp_grad['hf_local']/con_grad['hf_local']:.1f} 倍")

    # ==================== 第六步：渐变段长度设计 ====================
    print("\n【步骤6】渐变段长度设计")
    print("-" * 80)

    print("\n扩散段长度设计（B₁ = 4m → B₂ = 6m）：")
    print("-" * 100)
    print(f"{'渐变角θ(°)':^15} | {'渐变段长度L(m)':^18} | {'角度评价':^15} | {'推荐程度':^15}")
    print("-" * 100)

    angles_exp = [5, 8, 10, 12.5, 15, 20]
    for theta in angles_exp:
        L_design = (B2_exp - B1) / (2 * np.tan(np.radians(theta)))

        if theta <= 10:
            angle_grade = "优秀"
            recommend = "强烈推荐"
        elif theta <= 12.5:
            angle_grade = "良好"
            recommend = "推荐"
        elif theta <= 15:
            angle_grade = "可接受"
            recommend = "可用"
        else:
            angle_grade = "偏大"
            recommend = "不推荐"

        marker = " ←" if abs(theta - exp_grad['theta_deg']) < 1 else ""
        print(f"{theta:^15.1f} | {L_design:^18.2f} | {angle_grade:^15} | {recommend:^15}{marker}")

    print("-" * 100)

    print("\n收缩段长度设计（B₁ = 4m → B₂ = 3m）：")
    print("-" * 100)
    print(f"{'渐变角θ(°)':^15} | {'渐变段长度L(m)':^18} | {'角度评价':^15} | {'推荐程度':^15}")
    print("-" * 100)

    angles_con = [10, 15, 20, 30, 40, 50]
    for theta in angles_con:
        L_design = (B1 - B2_con) / (2 * np.tan(np.radians(theta)))

        if theta <= 20:
            angle_grade = "优秀"
            recommend = "推荐"
        elif theta <= 30:
            angle_grade = "良好"
            recommend = "推荐"
        elif theta <= 40:
            angle_grade = "可接受"
            recommend = "可用"
        else:
            angle_grade = "偏大"
            recommend = "不推荐"

        marker = " ←" if abs(theta - con_grad['theta_deg']) < 2 else ""
        print(f"{theta:^15.1f} | {L_design:^18.2f} | {angle_grade:^15} | {recommend:^15}{marker}")

    print("-" * 100)

    # ==================== 第七步：工程设计建议 ====================
    print("\n【步骤7】工程设计建议")
    print("-" * 80)

    print("\n基于水力计算的设计方案：")

    print(f"\n1. 扩散段设计（变宽）：")
    print(f"   - 推荐渐变角：θ = 10-12.5°")
    print(f"   - 推荐长度：L = {2.5*(B2_exp-B1):.1f}-{2.86*(B2_exp-B1):.1f} m")
    print(f"   - 简化公式：L ≥ 2.5 * (B₂ - B₁) = {2.5*(B2_exp-B1):.1f} m")
    print(f"   - 损失系数：ζ = 0.10-0.20")
    print(f"   - 避免突然扩散（损失增加 {exp_sudden['hf_local']/exp_grad['hf_local']:.1f} 倍）")

    print(f"\n2. 收缩段设计（变窄）：")
    print(f"   - 推荐渐变角：θ = 20-30°")
    print(f"   - 推荐长度：L = {0.87*(B1-B2_con):.1f}-{1.37*(B1-B2_con):.1f} m")
    print(f"   - 简化公式：L ≥ (B₁ - B₂) = {B1-B2_con:.1f} m")
    print(f"   - 损失系数：ζ = 0.05-0.10")
    print(f"   - 收缩损失小，长度要求较宽松")

    print(f"\n3. 水面线控制：")
    print(f"   - 扩散：壅水 Δh = +{exp_grad['water_rise']:.3f} m")
    print(f"   - 收缩：降水 Δh = -{con_grad['water_drop']:.3f} m")
    print(f"   - 影响上下游水位，需与系统协调")
    print(f"   - 避免影响上游灌溉取水")

    print(f"\n4. 施工要点：")
    print(f"   - 边壁必须平顺过渡，无突变")
    print(f"   - 底坡保持连续，避免台阶")
    print(f"   - 模板制作精确，控制渐变角")
    print(f"   - 混凝土浇筑分段合理")

    print(f"\n5. 特殊情况处理：")
    print(f"   - 地形限制无法满足长度：采用多级过渡")
    print(f"   - 与闸门结合：闸前扩散、闸后收缩")
    print(f"   - 与弯道结合：加强设计与防护")
    print(f"   - 急流条件：需专门分析")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
