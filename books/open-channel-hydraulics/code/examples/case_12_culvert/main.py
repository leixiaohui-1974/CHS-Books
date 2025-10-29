"""
案例12：涵洞过流 - 主程序

问题描述：
某道路下方需要修建涵洞，已知：
- 涵洞宽度 b = 2.0 m
- 涵洞高度 H = 1.5 m
- 涵洞长度 L = 30 m
- 涵洞底坡 S₀ = 0.001
- 涵洞糙率 n = 0.014（混凝土）
- 设计流量 Q = 4.0 m³/s

求解：
1. 临界水深和正常水深
2. 自由出流计算
3. 淹没出流计算
4. 压力流计算
5. 流态判别和设计建议

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


def compute_critical_depth(Q: float, b: float, g: float = 9.81) -> float:
    """计算矩形断面临界水深

    hc = (Q²/(g*b²))^(1/3)
    """
    hc = (Q**2 / (g * b**2)) ** (1.0/3.0)
    return hc


def compute_critical_velocity(hc: float, g: float = 9.81) -> float:
    """计算临界流速"""
    vc = np.sqrt(g * hc)
    return vc


def free_flow_discharge(b: float, H: float, h1: float, Cd: float = 0.70, g: float = 9.81) -> float:
    """自由出流流量计算（进口控制）

    Q = Cd * A * sqrt(2*g*H1)

    Args:
        b: 涵洞宽度
        H: 涵洞高度
        h1: 上游水深（从涵洞底起算）
        Cd: 流量系数（0.6-0.9）
    """
    # 有效过流面积
    if h1 <= H:
        A = b * h1
    else:
        A = b * H

    # 上游水头（取水面到涵洞中心的高度）
    if h1 <= H:
        H1 = h1 / 2  # 水深的一半作为有效水头
    else:
        H1 = h1 - H / 2

    Q = Cd * A * np.sqrt(2 * g * H1)
    return Q


def submerged_flow_discharge(b: float, H: float, L: float, n: float, S0: float,
                             h1: float, h3: float,
                             zeta_e: float = 0.2, zeta_o: float = 1.0,
                             g: float = 9.81) -> dict:
    """淹没出流计算（出口控制）

    能量方程：H1 + S0*L = H3 + hf

    Args:
        h1: 上游水深（从涵洞底起算）
        h3: 下游水深
        zeta_e: 进口损失系数
        zeta_o: 出口损失系数
    """
    # 迭代求解洞内流速和流量
    A = b * H  # 满管断面
    P = b + 2*H
    R = A / P

    # 初始猜测
    v = 1.0

    for i in range(100):
        # 沿程损失
        hf_friction = (n**2 * L * v**2) / (R**(4.0/3.0))

        # 进口损失
        hf_entrance = zeta_e * v**2 / (2*g)

        # 出口损失
        hf_exit = zeta_o * v**2 / (2*g)

        # 总损失
        hf_total = hf_entrance + hf_friction + hf_exit

        # 能量方程
        H1 = h1  # 上游水头
        H3 = h3  # 下游水头

        # H1 + S0*L = H3 + hf
        # 求解 v
        available_head = H1 + S0*L - H3
        total_loss_coeff = zeta_e + zeta_o + (n**2 * L) / (R**(4.0/3.0))

        v_new = np.sqrt((2*g*available_head) / total_loss_coeff)

        if abs(v_new - v) < 1e-6:
            v = v_new
            break

        v = v_new

    Q = A * v

    return {
        'Q': Q,
        'v': v,
        'hf_entrance': hf_entrance,
        'hf_friction': hf_friction,
        'hf_exit': hf_exit,
        'hf_total': hf_total,
        'H1': H1,
        'H3': H3
    }


def pressure_flow_discharge(b: float, H: float, L: float, n: float, S0: float,
                           h1: float, h3: float,
                           zeta_e: float = 0.2, zeta_o: float = 1.0,
                           g: float = 9.81) -> dict:
    """压力流计算（满管流）

    Q = A * sqrt[(2g*(H1-H3-ΔZ)) / (1 + ζe + ζf + ζo)]
    """
    A = b * H
    P = b + 2*H
    R = A / P

    # 底高程差
    delta_Z = -S0 * L  # 注意符号：顺坡为负

    # 沿程损失系数
    zeta_f = (n**2 * L) / (R**(4.0/3.0))

    # 总损失系数
    zeta_total = 1 + zeta_e + zeta_f + zeta_o

    # 有效水头
    delta_H = h1 - h3 - delta_Z

    # 流量
    Q = A * np.sqrt((2*g*delta_H) / zeta_total)

    # 平均流速
    v = Q / A

    # 各项损失
    hf_entrance = zeta_e * v**2 / (2*g)
    hf_friction = zeta_f * v**2 / (2*g)
    hf_exit = zeta_o * v**2 / (2*g)
    hf_total = hf_entrance + hf_friction + hf_exit

    return {
        'Q': Q,
        'v': v,
        'hf_entrance': hf_entrance,
        'hf_friction': hf_friction,
        'hf_exit': hf_exit,
        'hf_total': hf_total,
        'delta_H': delta_H,
        'zeta_total': zeta_total
    }


def determine_flow_type(h1: float, h3: float, H: float, hc: float) -> str:
    """判别涵洞流态

    Returns:
        'free': 自由出流（进口控制）
        'submerged': 淹没出流（出口控制）
        'pressure': 压力流（满管流）
    """
    # 进口淹没比
    submergence_inlet = h1 / H

    # 出口淹没比
    submergence_outlet = h3 / H

    # 判别准则
    if submergence_inlet > 1.2 and submergence_outlet > 1.0:
        return 'pressure'  # 压力流
    elif h3 < hc and submergence_inlet < 1.2:
        return 'free'  # 自由出流
    else:
        return 'submerged'  # 淹没出流


def main():
    """主函数"""
    print_separator("案例12：涵洞过流")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】涵洞参数")
    print("-" * 80)

    b = 2.0       # 涵洞宽度 (m)
    H = 1.5       # 涵洞高度 (m)
    L = 30.0      # 涵洞长度 (m)
    S0 = 0.001    # 底坡
    n = 0.014     # 糙率（混凝土）
    Q_design = 4.0  # 设计流量 (m³/s)
    g = 9.81

    print(f"几何参数：")
    print(f"  宽度 b = {b} m")
    print(f"  高度 H = {H} m")
    print(f"  长度 L = {L} m")
    print(f"  断面面积 A = {b*H} m²")
    print(f"  高宽比 H/b = {H/b:.2f}")

    print(f"\n水力参数：")
    print(f"  底坡 S₀ = {S0}")
    print(f"  糙率 n = {n}")
    print(f"  设计流量 Q = {Q_design} m³/s")

    # ==================== 第二步：临界水深和正常水深 ====================
    print("\n【步骤2】特征水深计算")
    print("-" * 80)

    hc = compute_critical_depth(Q_design, b, g)
    vc = compute_critical_velocity(hc, g)
    Frc = vc / np.sqrt(g * hc)

    print(f"\n临界水深：")
    print(f"  hc = {hc:.4f} m")
    print(f"  vc = {vc:.3f} m/s")
    print(f"  Frc = {Frc:.3f}（验证：应该=1.0）")
    print(f"  临界比 hc/H = {hc/H:.3f}")

    # 正常水深
    channel = RectangularChannel(b=b, S0=S0, n=n)
    hn = channel.compute_normal_depth(Q_design)
    vn = Q_design / (b * hn)
    Frn = channel.froude_number(hn)

    print(f"\n正常水深：")
    print(f"  hn = {hn:.4f} m")
    print(f"  vn = {vn:.3f} m/s")
    print(f"  Frn = {Frn:.3f}")

    if hn < H:
        print(f"  状态：正常流时未满管")
    else:
        print(f"  状态：正常流时满管（hn > H）")

    # ==================== 第三步：自由出流计算 ====================
    print("\n【步骤3】自由出流计算（进口控制）")
    print("-" * 80)

    print("\n进口类型及流量系数：")
    inlet_types = [
        ("直角进口", 0.60, 0.5),
        ("圆角进口(r=0.15H)", 0.70, 0.2),
        ("喇叭口进口", 0.90, 0.1)
    ]

    print("-" * 100)
    print(f"{'进口类型':^20} | {'流量系数Cd':^13} | {'进口损失ζe':^13} | "
          f"{'计算流量Q(m³/s)':^19} | {'评价':^15}")
    print("-" * 100)

    # 假设上游水深 h1 = 1.2m（接近涵洞高度）
    h1_free = 1.2

    for inlet_name, Cd, zeta_e in inlet_types:
        Q_calc = free_flow_discharge(b, H, h1_free, Cd, g)

        if abs(Q_calc - Q_design) < 0.5:
            evaluation = "满足设计"
        elif Q_calc > Q_design:
            evaluation = "偏大"
        else:
            evaluation = "偏小"

        print(f"{inlet_name:^20} | {Cd:^13.2f} | {zeta_e:^13.2f} | "
              f"{Q_calc:^19.2f} | {evaluation:^15}")

    print("-" * 100)

    print(f"\n自由出流特征（采用圆角进口，h1={h1_free}m）：")
    Q_free = free_flow_discharge(b, H, h1_free, Cd=0.70, g=g)
    v_free = Q_free / (b * h1_free)

    print(f"  上游水深 h1 = {h1_free} m")
    print(f"  计算流量 Q = {Q_free:.2f} m³/s")
    print(f"  进口流速 v = {v_free:.3f} m/s")
    print(f"  适用条件：h3 < hc = {hc:.3f} m（出口自由）")
    print(f"  适用条件：h1/H = {h1_free/H:.2f} < 1.2（未满管）")

    # ==================== 第四步：淹没出流计算 ====================
    print("\n【步骤4】淹没出流计算（出口控制）")
    print("-" * 80)

    h1_sub = 2.0  # 上游水深（高于涵洞）
    h3_sub = 1.6  # 下游水深（淹没出口）

    print(f"\n工况参数：")
    print(f"  上游水深 h1 = {h1_sub} m")
    print(f"  下游水深 h3 = {h3_sub} m")
    print(f"  进口淹没比 h1/H = {h1_sub/H:.2f}")
    print(f"  出口淹没比 h3/H = {h3_sub/H:.2f}")

    result_sub = submerged_flow_discharge(b, H, L, n, S0, h1_sub, h3_sub,
                                         zeta_e=0.2, zeta_o=1.0, g=g)

    print(f"\n计算结果：")
    print(f"  流量 Q = {result_sub['Q']:.2f} m³/s")
    print(f"  洞内流速 v = {result_sub['v']:.3f} m/s")

    print(f"\n水头损失明细：")
    print(f"  进口损失 hf_e = {result_sub['hf_entrance']:.4f} m")
    print(f"  沿程损失 hf_f = {result_sub['hf_friction']:.4f} m")
    print(f"  出口损失 hf_o = {result_sub['hf_exit']:.4f} m")
    print(f"  总损失 hf = {result_sub['hf_total']:.4f} m")

    print(f"\n能量平衡验证：")
    print(f"  H1 + S0*L = {result_sub['H1'] + S0*L:.4f} m")
    print(f"  H3 + hf = {result_sub['H3'] + result_sub['hf_total']:.4f} m")
    print(f"  差值 = {abs(result_sub['H1'] + S0*L - result_sub['H3'] - result_sub['hf_total']):.6f} m（应≈0）")

    # ==================== 第五步：压力流计算 ====================
    print("\n【步骤5】压力流计算（满管流）")
    print("-" * 80)

    h1_press = 2.5  # 上游水深（进口淹没）
    h3_press = 2.0  # 下游水深（出口淹没）

    print(f"\n工况参数：")
    print(f"  上游水深 h1 = {h1_press} m")
    print(f"  下游水深 h3 = {h3_press} m")
    print(f"  进口淹没比 h1/H = {h1_press/H:.2f} > 1.2（满管）")
    print(f"  出口淹没比 h3/H = {h3_press/H:.2f} > 1.0（淹没）")

    result_press = pressure_flow_discharge(b, H, L, n, S0, h1_press, h3_press,
                                          zeta_e=0.2, zeta_o=1.0, g=g)

    print(f"\n计算结果：")
    print(f"  流量 Q = {result_press['Q']:.2f} m³/s")
    print(f"  洞内流速 v = {result_press['v']:.3f} m/s")
    print(f"  有效水头 ΔH = {result_press['delta_H']:.4f} m")
    print(f"  综合损失系数 Σζ = {result_press['zeta_total']:.3f}")

    print(f"\n水头损失明细：")
    print(f"  进口损失 hf_e = {result_press['hf_entrance']:.4f} m")
    print(f"  沿程损失 hf_f = {result_press['hf_friction']:.4f} m")
    print(f"  出口损失 hf_o = {result_press['hf_exit']:.4f} m")
    print(f"  总损失 hf = {result_press['hf_total']:.4f} m")

    # ==================== 第六步：流态对比 ====================
    print("\n【步骤6】不同流态对比")
    print("-" * 80)

    print("\n三种流态的流量对比：")
    print("-" * 110)
    print(f"{'流态类型':^15} | {'上游水深h1(m)':^16} | {'下游水深h3(m)':^16} | "
          f"{'流量Q(m³/s)':^15} | {'洞内流速v(m/s)':^18}")
    print("-" * 110)
    print(f"{'自由出流':^15} | {h1_free:^16.2f} | {'<hc='+str(round(hc,2)):^16} | "
          f"{Q_free:^15.2f} | {v_free:^18.3f}")
    print(f"{'淹没出流':^15} | {h1_sub:^16.2f} | {h3_sub:^16.2f} | "
          f"{result_sub['Q']:^15.2f} | {result_sub['v']:^18.3f}")
    print(f"{'压力流':^15} | {h1_press:^16.2f} | {h3_press:^16.2f} | "
          f"{result_press['Q']:^15.2f} | {result_press['v']:^18.3f}")
    print("-" * 110)

    print("\n【关键观察】")
    print("1. 压力流过流能力最大（满管流）")
    print("2. 淹没出流受下游水位影响")
    print("3. 自由出流受进口控制，流量较小")
    print("4. 流速控制：一般要求 v < 3-4 m/s（防止冲刷）")

    # ==================== 第七步：流态判别示例 ====================
    print("\n【步骤7】流态自动判别")
    print("-" * 80)

    test_cases = [
        (1.2, 0.5, "小流量工况"),
        (1.5, 1.0, "中等流量工况"),
        (2.0, 1.6, "淹没出流工况"),
        (2.5, 2.0, "压力流工况"),
        (3.0, 2.5, "高水位工况")
    ]

    print("\n不同工况的流态判别：")
    print("-" * 120)
    print(f"{'工况描述':^15} | {'上游h1(m)':^12} | {'下游h3(m)':^12} | "
          f"{'h1/H':^8} | {'h3/hc':^8} | {'判别流态':^15} | {'备注':^20}")
    print("-" * 120)

    for h1, h3, desc in test_cases:
        flow_type = determine_flow_type(h1, h3, H, hc)

        ratio_h1 = h1 / H
        ratio_h3 = h3 / hc

        if flow_type == 'free':
            type_name = "自由出流"
            note = "进口控制"
        elif flow_type == 'submerged':
            type_name = "淹没出流"
            note = "出口控制"
        else:
            type_name = "压力流"
            note = "满管流"

        print(f"{desc:^15} | {h1:^12.2f} | {h3:^12.2f} | "
              f"{ratio_h1:^8.2f} | {ratio_h3:^8.2f} | {type_name:^15} | {note:^20}")

    print("-" * 120)

    # ==================== 第八步：设计建议 ====================
    print("\n【步骤8】涵洞水力设计建议")
    print("-" * 80)

    print(f"\n基于本案例的设计方案：")

    print(f"\n1. 尺寸设计：")
    print(f"   - 宽度 b = {b} m（合理）")
    print(f"   - 高度 H = {H} m")
    print(f"   - 高宽比 H/b = {H/b:.2f}（推荐0.5-1.0）")
    print(f"   - 断面面积 A = {b*H} m²")

    Q_capacity_free = free_flow_discharge(b, H, H*0.8, Cd=0.70, g=g)
    print(f"   - 自由出流能力：Q ≈ {Q_capacity_free:.1f} m³/s")
    print(f"   - 设计流量：Q = {Q_design} m³/s")
    print(f"   - 安全系数：{Q_capacity_free/Q_design:.2f}")

    print(f"\n2. 进口设计：")
    print(f"   - 推荐：圆角进口")
    print(f"   - 圆角半径：r = 0.15H = {0.15*H:.2f} m")
    print(f"   - 流量系数：Cd = 0.70")
    print(f"   - 进口损失：ζe = 0.2")
    print(f"   - 设置翼墙：角度30-45°")

    print(f"\n3. 洞身设计：")
    print(f"   - 长度：L = {L} m（由路堤宽度确定）")
    print(f"   - 底坡：S₀ = {S0}（与渠道坡度协调）")
    print(f"   - 糙率：n = {n}（混凝土标准）")
    print(f"   - 覆土厚度：≥ 0.5 m（结构要求）")

    print(f"\n4. 出口设计：")
    print(f"   - 设置消能设施（护坦+海漫）")
    print(f"   - 护坦长度：≥ 3H = {3*H:.1f} m")
    print(f"   - 海漫长度：≥ 5H = {5*H:.1f} m")
    print(f"   - 防止下游冲刷")
    print(f"   - 出口损失系数：ζo = 1.0")

    print(f"\n5. 水力控制：")
    print(f"   - 设计流态：自由出流（经济合理）")
    print(f"   - 校核流态：淹没出流（大流量时）")
    print(f"   - 控制流速：v < 3.5 m/s")
    print(f"   - 防止进口淹没：h1 < 1.2H = {1.2*H:.2f} m")

    print(f"\n6. 设计标准：")
    print(f"   - 设计频率：10年一遇（一般涵洞）")
    print(f"   - 校核频率：20-50年一遇")
    print(f"   - 特大洪水：允许短时满管")
    print(f"   - 安全超高：0.2-0.5 m")

    print(f"\n7. 施工要点：")
    print(f"   - 基础处理：承载力校核")
    print(f"   - 混凝土浇筑：强度C25-C30")
    print(f"   - 表面处理：光滑平整")
    print(f"   - 伸缩缝：每10-15m设置")
    print(f"   - 防渗处理：止水带设置")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
