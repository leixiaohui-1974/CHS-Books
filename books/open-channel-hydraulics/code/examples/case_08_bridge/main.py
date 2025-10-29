"""
案例8：桥梁壅水分析 - 主程序

问题描述：
某河道上拟建公路桥，需要分析桥梁收缩河道后的壅水影响。

已知条件：
- 天然河道宽度 B₀ = 50 m
- 河床平均坡度 S₀ = 0.0005
- 河道糙率 n = 0.030（天然河床）
- 设计流量 Q = 200 m³/s（20年一遇）
- 桥下净宽 Bb = 40 m（双墩三孔）
- 桥墩总宽度 = 10 m
- 桥区糙率 nb = 0.025（桥下清理、衬砌）

求解：
1. 天然河道正常水深和流速
2. 桥下收缩断面水深和流速
3. 桥前壅水高度
4. 壅水曲线和影响范围
5. 桥梁净空设计

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import RectangularChannel
from solvers.steady.profile import WaterSurfaceProfile


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
    print_separator("案例8：桥梁壅水分析")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    B0 = 50.0       # 天然河道宽度 (m)
    Bb = 40.0       # 桥下净宽 (m)
    S0 = 0.0005     # 河床坡度
    n = 0.030       # 天然河道糙率
    nb = 0.025      # 桥下糙率（清理、衬砌）
    Q = 200.0       # 设计流量 (m³/s)
    g = 9.81        # 重力加速度

    print(f"天然河道：")
    print(f"  河道宽度 B₀ = {B0} m")
    print(f"  河床坡度 S₀ = {S0}")
    print(f"  河道糙率 n = {n}")

    print(f"\n桥梁参数：")
    print(f"  桥下净宽 Bb = {Bb} m")
    print(f"  桥墩总宽 = {B0 - Bb} m")
    print(f"  收缩系数 ε = Bb/B₀ = {Bb/B0:.3f}")
    print(f"  桥区糙率 nb = {nb}")

    print(f"\n水文条件：")
    print(f"  设计流量 Q = {Q} m³/s")
    print(f"  设计标准：20年一遇")

    # ==================== 第二步：天然河道水力计算 ====================
    print("\n【步骤2】天然河道水力计算（无桥情况）")
    print("-" * 80)

    # 天然河道（矩形断面近似）
    channel_natural = RectangularChannel(b=B0, S0=S0, n=n)

    # 正常水深
    h0 = channel_natural.compute_normal_depth(Q)
    A0 = channel_natural.area(h0)
    v0 = Q / A0
    Fr0 = channel_natural.froude_number(h0, Q)
    E0 = h0 + v0**2 / (2*g)

    print(f"\n天然河道水流特性：")
    print(f"  正常水深 h₀ = {h0:.4f} m")
    print(f"  过流面积 A₀ = {A0:.4f} m²")
    print(f"  平均流速 v₀ = {v0:.4f} m/s")
    print(f"  弗劳德数 Fr₀ = {Fr0:.4f}")
    print(f"  比能 E₀ = {E0:.4f} m")
    print(f"  流态：{'缓流' if Fr0 < 1 else '急流'}")

    # ==================== 第三步：桥下收缩断面计算 ====================
    print("\n【步骤3】桥下收缩断面水力计算")
    print("-" * 80)

    # 桥下河段（矩形断面，宽度为Bb）
    channel_bridge = RectangularChannel(b=Bb, S0=S0, n=nb)

    # 桥下正常水深（如果足够长的均匀流）
    hb_normal = channel_bridge.compute_normal_depth(Q)

    # 但实际上桥下是收缩段，水深会增加
    # 使用能量方程估算：E₀ + hf_loss ≈ E₁
    # 简化假设：hf_loss ≈ 0.1 * v₁²/(2g)（局部损失）

    # 迭代求解桥下水深
    h1 = hb_normal  # 初始猜测

    for i in range(100):
        A1 = Bb * h1
        v1 = Q / A1
        E1 = h1 + v1**2 / (2*g)

        # 局部损失系数（桥墩+收缩）
        zeta = 0.15
        hf = zeta * v1**2 / (2*g)

        # 能量方程：E₀ = E₁ + hf
        f = E1 + hf - E0

        if abs(f) < 1e-6:
            break

        # 数值导数
        dh = 1e-6
        A1_plus = Bb * (h1 + dh)
        v1_plus = Q / A1_plus
        E1_plus = (h1 + dh) + v1_plus**2 / (2*g)
        hf_plus = zeta * v1_plus**2 / (2*g)
        f_plus = E1_plus + hf_plus - E0

        df = (f_plus - f) / dh

        if abs(df) < 1e-12:
            break

        h1 = h1 - f / df

        if h1 <= 0:
            h1 = h0 / 2

    A1 = Bb * h1
    v1 = Q / A1
    Fr1 = v1 / np.sqrt(g * h1)
    E1 = h1 + v1**2 / (2*g)

    print(f"\n桥下收缩断面水流特性：")
    print(f"  桥下水深 h₁ = {h1:.4f} m")
    print(f"  过流面积 A₁ = {A1:.4f} m²")
    print(f"  平均流速 v₁ = {v1:.4f} m/s")
    print(f"  弗劳德数 Fr₁ = {Fr1:.4f}")
    print(f"  比能 E₁ = {E1:.4f} m")

    print(f"\n流速增加：")
    print(f"  Δv = v₁ - v₀ = {v1 - v0:.4f} m/s")
    print(f"  增加率 = {(v1 - v0)/v0 * 100:.2f}%")

    # ==================== 第四步：壅水高度计算 ====================
    print("\n【步骤4】壅水高度计算")
    print("-" * 80)

    # 壅水高度（桥前水深相对于天然水深的增加）
    dh_backwater = h1 - h0

    print(f"\n壅水高度估算：")
    print(f"  桥前水深 ≈ 桥下水深 = {h1:.4f} m")
    print(f"  天然水深 = {h0:.4f} m")
    print(f"  壅水高度 Δh = {dh_backwater:.4f} m")

    # 经验公式验证
    K = 1.2  # 壅水系数
    dh_empirical = K * (v1**2 - v0**2) / (2*g)

    print(f"\n经验公式验证：")
    print(f"  Δh = K*(v₁² - v₀²)/(2g)")
    print(f"  其中 K = {K}")
    print(f"  计算得 Δh = {dh_empirical:.4f} m")

    # 能量损失
    hf = E0 - E1
    print(f"\n能量分析：")
    print(f"  桥前比能 E₀ = {E0:.4f} m")
    print(f"  桥下比能 E₁ = {E1:.4f} m")
    print(f"  能量损失 hf = {hf:.4f} m")

    # ==================== 第五步：壅水曲线计算 ====================
    print("\n【步骤5】壅水曲线计算（桥前水面线）")
    print("-" * 80)

    # 使用天然河道的参数，从桥前控制水深向上游推算
    h_control = h1  # 桥前水深等于桥下水深

    profile_solver = WaterSurfaceProfile(channel=channel_natural, Q=Q, dx=20.0)

    print(f"\n从桥前断面（h = {h_control:.4f} m）向上游推算...")

    # 计算壅水曲线
    result = profile_solver.compute_profile(
        h_start=h_control,
        L=1000.0,
        direction='upstream'
    )

    x_values = result['x']
    h_values = result['h']
    curve_type = result['type']

    print(f"曲线类型：{curve_type}")
    print(f"计算点数：{len(x_values)}")

    # 计算壅水影响长度
    L_backwater = profile_solver.compute_backwater_length(h_control, h_threshold=0.05)

    print(f"\n壅水影响分析：")
    print(f"  壅水影响长度：L = {L_backwater:.2f} m")
    print(f"  最大壅水高度：Δh_max = {dh_backwater:.4f} m")

    # 打印部分结果
    print(f"\n桥前壅水曲线（部分结果）：")
    print("-" * 90)
    print(f"{'距桥距离(m)':^15} | {'水深h(m)':^12} | {'壅水高度Δh(m)':^18} | {'壅水率(%)':^15}")
    print("-" * 90)

    distances = [0, 50, 100, 200, 300, 400, 500]
    for dist in distances:
        if dist <= abs(x_values[-1] - x_values[0]):
            idx = min(range(len(x_values)), key=lambda i: abs(x_values[i] - (-dist)))
            h = h_values[idx]
            dh = h - h0
            ratio = (dh / dh_backwater) * 100 if dh_backwater > 0 else 0

            print(f"{dist:^15.0f} | {h:^12.4f} | {dh:^18.4f} | {ratio:^15.2f}")

    print("-" * 90)

    # ==================== 第六步：桥梁净空设计 ====================
    print("\n【步骤6】桥梁净空设计")
    print("-" * 80)

    # 设计水位（桥前最高水位）
    h_design = h1

    # 安全超高
    delta_safety = 0.50  # 安全超高0.5m

    # 波浪爬高（简化计算）
    wave_height = 0.15  # 波浪影响0.15m

    # 桥梁最低净空
    H_clearance = h_design + delta_safety + wave_height

    print(f"\n桥梁净空计算：")
    print(f"  设计水位（桥前最高水位）：h_max = {h_design:.4f} m")
    print(f"  安全超高：δ₁ = {delta_safety:.2f} m")
    print(f"  波浪爬高：δ₂ = {wave_height:.2f} m")
    print(f"  桥梁最低净空：H = {H_clearance:.4f} m")

    # 假设河床高程为0
    print(f"\n桥梁标高设计（假设河床高程为0）：")
    print(f"  河床高程：Z₀ = 0.00 m")
    print(f"  设计水位：Z_water = {h_design:.2f} m")
    print(f"  桥底标高（最低）：Z_bridge ≥ {H_clearance:.2f} m")
    print(f"  建议桥底标高：Z_bridge = {H_clearance + 0.5:.2f} m（留0.5m余量）")

    # ==================== 第七步：不同桥宽方案对比 ====================
    print("\n【步骤7】不同桥宽方案对比")
    print("-" * 80)

    Bb_options = [35, 40, 45, 48]

    print(f"\n不同桥下净宽方案对比：")
    print("-" * 100)
    print(f"{'桥宽Bb(m)':^12} | {'收缩系数ε':^13} | {'壅水Δh(m)':^13} | {'影响长度L(m)':^16} | {'方案评价':^20}")
    print("-" * 100)

    for Bb_opt in Bb_options:
        # 创建桥下河段
        channel_b = RectangularChannel(b=Bb_opt, S0=S0, n=nb)

        # 求解桥下水深
        h1_opt = channel_natural.compute_normal_depth(Q)
        for i in range(50):
            A1_opt = Bb_opt * h1_opt
            v1_opt = Q / A1_opt
            E1_opt = h1_opt + v1_opt**2 / (2*g)
            zeta = 0.15
            hf_opt = zeta * v1_opt**2 / (2*g)
            f = E1_opt + hf_opt - E0

            if abs(f) < 1e-6:
                break

            dh = 1e-6
            A1_plus = Bb_opt * (h1_opt + dh)
            v1_plus = Q / A1_plus
            E1_plus = (h1_opt + dh) + v1_plus**2 / (2*g)
            hf_plus = zeta * v1_plus**2 / (2*g)
            f_plus = E1_plus + hf_plus - E0
            df = (f_plus - f) / dh

            if abs(df) > 1e-12:
                h1_opt = h1_opt - f / df
            if h1_opt <= 0:
                h1_opt = h0

        dh_opt = h1_opt - h0
        epsilon = Bb_opt / B0

        # 估算影响长度
        profile_opt = WaterSurfaceProfile(channel=channel_natural, Q=Q, dx=20.0)
        try:
            L_opt = profile_opt.compute_backwater_length(h1_opt, h_threshold=0.05)
        except:
            L_opt = 0

        # 评价
        if epsilon >= 0.9:
            evaluation = "优秀★★★"
        elif epsilon >= 0.8:
            evaluation = "良好★★"
        elif epsilon >= 0.7:
            evaluation = "合格★"
        else:
            evaluation = "不推荐"

        print(f"{Bb_opt:^12.0f} | {epsilon:^13.3f} | {dh_opt:^13.4f} | {L_opt:^16.2f} | {evaluation:^20}")

    print("-" * 100)

    print(f"\n结论：")
    print(f"  桥宽越大，收缩越小，壅水越小，影响越小")
    print(f"  建议收缩系数 ε ≥ 0.80（即 Bb ≥ {B0*0.8:.0f}m）")
    print(f"  当前设计 Bb = {Bb}m，ε = {Bb/B0:.3f}，符合要求")

    # ==================== 第八步：工程设计建议 ====================
    print("\n【步骤8】工程设计建议")
    print("-" * 80)

    print(f"\n基于水力计算的设计方案：")

    print(f"\n1. 桥孔布置：")
    print(f"   - 桥下净宽：Bb = {Bb} m")
    print(f"   - 桥孔形式：3孔（2墩）")
    print(f"   - 单孔跨度：约{Bb/3:.1f} m")
    print(f"   - 桥墩宽度：约{(B0-Bb)/2:.1f} m × 2")

    print(f"\n2. 桥梁净空：")
    print(f"   - 设计水位：{h_design:.2f} m")
    print(f"   - 安全超高：{delta_safety:.2f} m")
    print(f"   - 桥底标高：≥{H_clearance:.2f} m")
    print(f"   - 建议采用：{H_clearance + 0.5:.2f} m")

    print(f"\n3. 壅水控制：")
    print(f"   - 最大壅水：Δh = {dh_backwater:.2f} m")
    print(f"   - 影响范围：L = {L_backwater:.0f} m")
    print(f"   - 控制措施：采用流线型桥墩，桥下河床清理")
    print(f"   - 评价：{'符合要求（Δh<0.5m）' if dh_backwater < 0.5 else '需要优化设计'}")

    print(f"\n4. 桥墩设计：")
    print(f"   - 桥墩形式：圆端形或流线型")
    print(f"   - 桥墩方向：顺水流方向")
    print(f"   - 桥墩间距：{Bb/3:.1f} m（均匀分布）")
    print(f"   - 防护措施：桥墩周围抛石防护")

    print(f"\n5. 河道整治：")
    print(f"   - 桥下河床清理，降低糙率至n={nb}")
    print(f"   - 桥前后{50:.0f}m范围内护岸")
    print(f"   - 主槽对准主流，避免斜交")
    print(f"   - 设置导流堤引导水流")

    print(f"\n6. 监测要求：")
    print(f"   - 桥前水位监测点：距桥{50:.0f}m")
    print(f"   - 桥下流速监测")
    print(f"   - 桥墩周围冲刷监测")
    print(f"   - 预警水位：{h_design - 0.5:.2f} m")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
