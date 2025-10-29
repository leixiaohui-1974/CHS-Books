"""
案例3：景观水渠水流状态分析 - 主程序

问题描述：
某公园景观水渠设计，已知：
- 矩形断面，宽度 b = 2.0 m
- 渠底坡度 S0 = 0.002
- 曼宁糙率 n = 0.015
- 设计流量 Q = 1.0 m³/s

求解：
1. 正常水深和临界水深
2. 比能曲线分析
3. 不同流态的特征
4. 景观设计建议

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import RectangularChannel
from solvers.steady.uniform_flow import UniformFlowSolver


def specific_energy(Q, b, h, g=9.81):
    """
    计算比能

    E = h + v²/(2g) = h + Q²/(2gA²)
    """
    A = b * h
    v = Q / A
    E = h + v**2 / (2*g)
    return E


def find_conjugate_depth(E, Q, b, hc, g=9.81):
    """
    给定比能E和流量Q，找到两个共轭水深

    返回：(h_subcritical, h_supercritical)
    """
    # 临界比能
    Ec = specific_energy(Q, b, hc, g)

    if E < Ec:
        return None, None  # 比能太小，无解

    # 缓流水深（h > hc）
    h_sub = hc
    for _ in range(100):
        A = b * h_sub
        E_calc = h_sub + Q**2 / (2*g*A**2)
        f = E_calc - E
        if abs(f) < 1e-6:
            break
        # 导数
        dh = 1e-6
        A_plus = b * (h_sub + dh)
        E_plus = (h_sub + dh) + Q**2 / (2*g*A_plus**2)
        df = (E_plus - E_calc) / dh
        h_sub = h_sub - f / df

    # 急流水深（h < hc）
    h_super = hc * 0.5
    for _ in range(100):
        A = b * h_super
        E_calc = h_super + Q**2 / (2*g*A**2)
        f = E_calc - E
        if abs(f) < 1e-6:
            break
        # 导数
        dh = 1e-6
        A_plus = b * (h_super + dh)
        E_plus = (h_super + dh) + Q**2 / (2*g*A_plus**2)
        df = (E_plus - E_calc) / dh
        h_super = h_super - f / df

    return h_sub, h_super


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


def print_results(results_dict, title="计算结果"):
    """格式化打印结果"""
    print_separator(title)
    for key, value in results_dict.items():
        if isinstance(value, (int, float)):
            if abs(value) < 1e-2 or abs(value) > 1e4:
                print(f"{key:25s}: {value:.6e}")
            else:
                print(f"{key:25s}: {value:.4f}")
        else:
            print(f"{key:25s}: {value}")
    print_separator()


def main():
    """主函数"""
    print_separator("案例3：景观水渠水流状态分析")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    b = 2.0      # 渠宽 (m)
    n = 0.015    # 曼宁糙率系数
    S0 = 0.002   # 渠底坡度
    Q = 1.0      # 流量 (m³/s)
    g = 9.81     # 重力加速度

    print(f"渠道类型：矩形景观水渠（砌石）")
    print(f"渠道宽度 b = {b} m")
    print(f"曼宁糙率 n = {n}")
    print(f"渠底坡度 S0 = {S0} ({S0*100:.1f}%)")
    print(f"设计流量 Q = {Q} m³/s")

    # ==================== 第二步：计算正常水深和临界水深 ====================
    print("\n【步骤2】计算正常水深和临界水深")
    print("-" * 80)

    channel = RectangularChannel(b=b, n=n, S0=S0)
    solver = UniformFlowSolver(channel)

    # 正常水深
    results_normal = solver.compute_normal_depth(Q)
    h0 = results_normal["正常水深_h0"]
    v0 = results_normal["流速_v"]
    Fr0 = results_normal["弗劳德数_Fr"]

    # 临界水深
    hc = channel.compute_critical_depth(Q)
    q = Q / b
    vc = Q / (b * hc)
    Frc = vc / np.sqrt(g * hc)

    print(f"正常水深计算：")
    print(f"  h0 = {h0:.4f} m")
    print(f"  v0 = {v0:.4f} m/s")
    print(f"  Fr0 = {Fr0:.4f}")
    print(f"  流态：{results_normal['流态']}")

    print(f"\n临界水深计算：")
    print(f"  单宽流量 q = Q/b = {q:.4f} m²/s")
    print(f"  hc = (q²/g)^(1/3) = {hc:.4f} m")
    print(f"  vc = q/hc = {vc:.4f} m/s")
    print(f"  Frc = {Frc:.4f} ≈ 1")

    # ==================== 第三步：比能分析 ====================
    print("\n【步骤3】比能分析")
    print("-" * 80)

    # 计算正常水深和临界水深的比能
    E0 = specific_energy(Q, b, h0, g)
    Ec = specific_energy(Q, b, hc, g)

    print(f"比能公式：E = h + v²/(2g)")
    print(f"\n正常水深的比能：")
    print(f"  E0 = {h0:.4f} + {v0**2/(2*g):.4f} = {E0:.4f} m")

    print(f"\n临界水深的比能（最小比能）：")
    print(f"  Ec = {hc:.4f} + {vc**2/(2*g):.4f} = {Ec:.4f} m")
    print(f"  理论值 Ec = 1.5 * hc = {1.5*hc:.4f} m")

    print(f"\n比能关系：")
    print(f"  E0 = {E0:.4f} m > Ec = {Ec:.4f} m")
    print(f"  正常水深的比能大于临界比能，说明流态为缓流")

    # ==================== 第四步：比能曲线关键点 ====================
    print("\n【步骤4】比能曲线关键点")
    print("-" * 80)

    print(f"给定流量 Q = {Q} m³/s，比能曲线的关键点：")
    print(f"\n1. 临界点（曲线最低点）：")
    print(f"   水深 hc = {hc:.4f} m")
    print(f"   比能 Ec = {Ec:.4f} m")
    print(f"   弗劳德数 Fr = 1")

    # 计算几个特殊点
    print(f"\n2. 比能曲线上的其他点：")
    print("-" * 80)
    print(f"{'水深h(m)':^12} | {'流速v(m/s)':^12} | {'比能E(m)':^12} | {'Fr':^8} | {'流态':^8}")
    print("-" * 80)

    h_points = [0.2, 0.3, hc, 0.5, h0, 0.8, 1.0]
    for h in h_points:
        A = b * h
        v = Q / A
        E = specific_energy(Q, b, h, g)
        Fr = v / np.sqrt(g * h)
        flow_type = "急流" if Fr > 1.05 else ("临界" if Fr > 0.95 else "缓流")
        marker = " *" if abs(h - hc) < 0.01 or abs(h - h0) < 0.01 else ""
        print(f"{h:^12.4f} | {v:^12.4f} | {E:^12.4f} | {Fr:^8.4f} | {flow_type:^8}{marker}")

    print("-" * 80)
    print("注：* 标记表示正常水深或临界水深")

    # ==================== 第五步：共轭水深分析 ====================
    print("\n【步骤5】共轭水深分析")
    print("-" * 80)

    print(f"共轭水深：对于相同的比能，可能存在两个不同的水深")
    print(f"\n以正常水深的比能 E = {E0:.4f} m 为例：")

    h_sub, h_super = find_conjugate_depth(E0, Q, b, hc, g)

    if h_sub and h_super:
        v_sub = Q / (b * h_sub)
        Fr_sub = v_sub / np.sqrt(g * h_sub)
        v_super = Q / (b * h_super)
        Fr_super = v_super / np.sqrt(g * h_super)

        print(f"\n共轭水深1（缓流）：")
        print(f"  h1 = {h_sub:.4f} m")
        print(f"  v1 = {v_sub:.4f} m/s")
        print(f"  Fr1 = {Fr_sub:.4f} < 1")

        print(f"\n共轭水深2（急流）：")
        print(f"  h2 = {h_super:.4f} m")
        print(f"  v2 = {v_super:.4f} m/s")
        print(f"  Fr2 = {Fr_super:.4f} > 1")

        print(f"\n验证：")
        E1 = specific_energy(Q, b, h_sub, g)
        E2 = specific_energy(Q, b, h_super, g)
        print(f"  E1 = {E1:.4f} m")
        print(f"  E2 = {E2:.4f} m")
        print(f"  E1 ≈ E2（相同比能）")

    # ==================== 第六步：景观设计建议 ====================
    print("\n【步骤6】景观设计建议")
    print("-" * 80)

    print(f"基于水力分析的景观设计方案：")

    print(f"\n方案A：静态水景（倒影效果）")
    print(f"  - 保持较大水深（h > {h0:.2f} m）")
    print(f"  - 弗劳德数 Fr < 0.3")
    print(f"  - 水面平静，适合倒影")
    print(f"  - 建议水深：0.6-0.8 m")

    print(f"\n方案B：动态水景（流动效果）")
    print(f"  - 保持中等水深（h ≈ {h0:.2f} m）")
    print(f"  - 弗劳德数 0.5 < Fr < 0.8")
    print(f"  - 水流生动但不湍急")
    print(f"  - 建议水深：{h0:.2f} m（正常水深）")

    print(f"\n方案C：跌水景观（水跃效果）")
    print(f"  - 设计跌水段，从急流转为缓流")
    print(f"  - 跌水前：h < {hc:.2f} m（急流）")
    print(f"  - 跌水后：h > {h0:.2f} m（缓流）")
    print(f"  - 形成水跃，增加动感")

    print(f"\n方案D：涉水平台")
    print(f"  - 水深控制在 0.1-0.3 m")
    print(f"  - Fr < 0.5，水流平稳")
    print(f"  - 适合游人涉水游玩")
    print(f"  - 注意防滑措施")

    # ==================== 第七步：设计总结 ====================
    print("\n【步骤7】设计总结")
    print("-" * 80)

    print(f"✓ 水力分析完成！")

    print(f"\n关键参数：")
    print(f"  正常水深：h0 = {h0:.3f} m")
    print(f"  临界水深：hc = {hc:.3f} m")
    print(f"  正常流速：v0 = {v0:.3f} m/s")
    print(f"  弗劳德数：Fr0 = {Fr0:.3f}")
    print(f"  最小比能：Ec = {Ec:.3f} m")

    print(f"\n设计原则：")
    print(f"  1. 避免临界流（Fr ≈ 1），保持稳定流态")
    print(f"  2. 不同景观效果对应不同的Fr和水深")
    print(f"  3. 利用比能曲线理解水流转换")
    print(f"  4. 考虑水跃效应，可制造动态景观")

    print("\n推荐方案：")
    print(f"  - 主水道：保持正常水深 {h0:.2f} m，动态流动")
    print(f"  - 观赏区：增大水深至 0.7 m，平静倒影")
    print(f"  - 跌水区：设计 0.2-0.3 m 落差，形成水跃")
    print(f"  - 涉水区：控制水深 0.15-0.25 m，确保安全")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("分析完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
