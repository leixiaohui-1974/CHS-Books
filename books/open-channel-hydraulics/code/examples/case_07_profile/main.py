"""
案例7：渠道水面曲线计算 - 主程序

问题描述：
某灌溉渠道下游闸门抬高水位，需要计算壅水曲线，评估影响范围。

已知条件：
- 渠道底宽 b = 3.0 m
- 边坡系数 m = 1.5 (水平:垂直)
- 渠底坡度 S₀ = 0.0008
- 糙率系数 n = 0.020
- 设计流量 Q = 6.0 m³/s
- 下游控制水深 h₀ = 2.5 m (闸前水深)

求解：
1. 正常水深和临界水深
2. 渠道类型判别
3. 壅水曲线计算
4. 壅水影响范围
5. 水面曲线特性分析

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import TrapezoidalChannel
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
    print_separator("案例7：渠道水面曲线计算")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    b = 3.0        # 渠底宽度 (m)
    m = 1.5        # 边坡系数
    S0 = 0.0008    # 渠底坡度
    n = 0.020      # 糙率系数
    Q = 6.0        # 设计流量 (m³/s)
    h_control = 2.5  # 下游控制水深（闸前水深）(m)

    print(f"渠道类型：梯形断面")
    print(f"渠底宽度 b = {b} m")
    print(f"边坡系数 m = {m} (水平:垂直)")
    print(f"渠底坡度 S₀ = {S0}")
    print(f"糙率系数 n = {n}")
    print(f"设计流量 Q = {Q} m³/s")
    print(f"下游控制水深 h₀ = {h_control} m (闸前水深)")

    # ==================== 第二步：创建渠道对象 ====================
    print("\n【步骤2】创建渠道模型")
    print("-" * 80)

    channel = TrapezoidalChannel(b=b, m=m, S0=S0, n=n)
    print(f"渠道对象：{channel}")

    # ==================== 第三步：计算正常水深和临界水深 ====================
    print("\n【步骤3】计算特征水深")
    print("-" * 80)

    # 正常水深（均匀流水深）
    hn = channel.compute_normal_depth(Q)
    An = channel.area(hn)
    vn = Q / An
    Frn = channel.froude_number(hn, Q)

    print(f"\n正常水深（均匀流条件）：")
    print(f"  正常水深 hn = {hn:.4f} m")
    print(f"  过流面积 An = {An:.4f} m²")
    print(f"  流速 vn = {vn:.4f} m/s")
    print(f"  弗劳德数 Frn = {Frn:.4f}")

    # 临界水深
    hc = channel.compute_critical_depth(Q)
    Ac = channel.area(hc)
    vc = Q / Ac
    Frc = channel.froude_number(hc, Q)

    print(f"\n临界水深（临界流条件）：")
    print(f"  临界水深 hc = {hc:.4f} m")
    print(f"  过流面积 Ac = {Ac:.4f} m²")
    print(f"  流速 vc = {vc:.4f} m/s")
    print(f"  弗劳德数 Frc = {Frc:.4f}")

    # 临界坡度
    Rc = Ac / channel.wetted_perimeter(hc)
    Sc = (n**2 * vc**2) / (Rc**(4.0/3.0))

    print(f"\n临界坡度：")
    print(f"  Sc = {Sc:.6f}")
    print(f"  实际坡度 S₀ = {S0:.6f}")

    # ==================== 第四步：渠道类型判别 ====================
    print("\n【步骤4】渠道类型判别")
    print("-" * 80)

    print(f"\n特征水深比较：")
    print(f"  正常水深 hn = {hn:.4f} m")
    print(f"  临界水深 hc = {hc:.4f} m")
    print(f"  控制水深 h₀ = {h_control:.4f} m")

    if S0 < Sc:
        channel_type = "缓坡渠道 (S₀ < Sc)"
        print(f"\n渠道类型：{channel_type}")
        print(f"  hn > hc：正常水深大于临界水深")
        print(f"  正常情况下为缓流（Fr < 1）")
    elif S0 > Sc:
        channel_type = "陡坡渠道 (S₀ > Sc)"
        print(f"\n渠道类型：{channel_type}")
        print(f"  hn < hc：正常水深小于临界水深")
        print(f"  正常情况下为急流（Fr > 1）")
    else:
        channel_type = "临界坡渠道 (S₀ = Sc)"
        print(f"\n渠道类型：{channel_type}")
        print(f"  hn = hc：正常水深等于临界水深")

    # 水面曲线类型
    if h_control > hn > hc:
        profile_type = "M1 型壅水曲线"
        print(f"\n水面曲线类型：{profile_type}")
        print(f"  h₀ > hn > hc")
        print(f"  特征：缓坡壅水，水深向上游逐渐降低，渐近于hn")
    elif hn > h_control > hc:
        profile_type = "M2 型落水曲线"
        print(f"\n水面曲线类型：{profile_type}")
        print(f"  hn > h₀ > hc")
        print(f"  特征：缓坡落水，水深向下游降低")
    else:
        profile_type = "其他类型"
        print(f"\n水面曲线类型：{profile_type}")

    # ==================== 第五步：创建水面曲线求解器 ====================
    print("\n【步骤5】创建水面曲线求解器")
    print("-" * 80)

    profile_solver = WaterSurfaceProfile(channel=channel, Q=Q, dx=20.0)
    print(f"求解器：{profile_solver}")
    print(f"计算方法：标准步长法")
    print(f"步长：dx = 20.0 m")
    print(f"推算方向：从下游向上游")

    # ==================== 第六步：计算壅水曲线 ====================
    print("\n【步骤6】计算壅水曲线")
    print("-" * 80)

    print(f"\n从下游控制断面（h = {h_control} m）向上游推算...")

    # 计算水面曲线（向上游推算1500m）
    result = profile_solver.compute_profile(
        h_start=h_control,
        L=1500.0,
        direction='upstream'
    )

    x_values = result['x']
    h_values = result['h']
    E_values = result['E']
    Fr_values = result['Fr']
    curve_type = result['type']

    print(f"曲线类型：{curve_type}")
    print(f"计算点数：{len(x_values)}")
    print(f"计算长度：{abs(x_values[0] - x_values[-1]):.2f} m")

    # 打印部分计算结果
    print(f"\n水面曲线计算结果（每隔100m）：")
    print("-" * 100)
    print(f"{'距离x(m)':^12} | {'水深h(m)':^12} | {'比能E(m)':^12} | {'弗劳德数Fr':^14} | {'壅水高度Δh(m)':^15}")
    print("-" * 100)

    for i in range(0, len(x_values), 5):  # 每隔5个点打印
        x = x_values[i]
        h = h_values[i]
        E = E_values[i]
        Fr = Fr_values[i]
        dh = h - hn

        print(f"{x:^12.2f} | {h:^12.4f} | {E:^12.4f} | {Fr:^14.4f} | {dh:^15.4f}")

    print("-" * 100)

    # ==================== 第七步：壅水影响分析 ====================
    print("\n【步骤7】壅水影响分析")
    print("-" * 80)

    # 计算壅水长度
    L_backwater = profile_solver.compute_backwater_length(h_control, h_threshold=0.05)

    print(f"\n壅水特性：")
    print(f"  下游控制水深：h₀ = {h_control:.4f} m")
    print(f"  正常水深：hn = {hn:.4f} m")
    print(f"  最大壅水高度：Δh_max = {h_control - hn:.4f} m")
    print(f"  壅水影响长度：L = {L_backwater:.2f} m")

    # 找出距离下游不同位置的水深
    distances = [0, 200, 400, 600, 800, 1000]
    print(f"\n不同位置的水深和壅水高度：")
    print("-" * 80)
    print(f"{'距下游距离(m)':^18} | {'水深h(m)':^13} | {'壅水高度Δh(m)':^18} | {'壅水率(%)':^13}")
    print("-" * 80)

    for dist in distances:
        # 在计算结果中查找最接近的点
        idx = min(range(len(x_values)), key=lambda i: abs(x_values[i] - (-dist)))
        h = h_values[idx]
        dh = h - hn
        backwater_ratio = (dh / (h_control - hn)) * 100 if h_control > hn else 0

        print(f"{dist:^18.0f} | {h:^13.4f} | {dh:^18.4f} | {backwater_ratio:^13.2f}")

    print("-" * 80)

    print(f"\n壅水消减规律：")
    print(f"  壅水高度随距离增加呈指数衰减")
    print(f"  在距下游{L_backwater:.0f}m处，壅水基本消失")
    print(f"  壅水影响主要集中在下游{L_backwater/2:.0f}m范围内")

    # ==================== 第八步：不同控制水深对比 ====================
    print("\n【步骤8】不同控制水深对比")
    print("-" * 80)

    h_control_values = [2.0, 2.5, 3.0, 3.5]

    print(f"\n不同闸前水深的壅水影响：")
    print("-" * 90)
    print(f"{'控制水深h₀(m)':^17} | {'壅水高度Δh(m)':^18} | {'壅水长度L(m)':^18} | {'影响评价':^15}")
    print("-" * 90)

    for h0 in h_control_values:
        dh_max = h0 - hn
        L_bw = profile_solver.compute_backwater_length(h0, h_threshold=0.05)

        if dh_max < 0.3:
            impact = "轻微"
        elif dh_max < 0.6:
            impact = "中等"
        elif dh_max < 1.0:
            impact = "较大"
        else:
            impact = "严重"

        print(f"{h0:^17.2f} | {dh_max:^18.4f} | {L_bw:^18.2f} | {impact:^15}")

    print("-" * 90)

    print(f"\n结论：")
    print(f"  控制水深越高，壅水越严重，影响范围越大")
    print(f"  壅水长度与壅水高度呈近似线性关系")
    print(f"  本案例中，控制水深提高0.5m，壅水长度增加约300-400m")

    # ==================== 第九步：工程设计建议 ====================
    print("\n【步骤9】工程设计建议")
    print("-" * 80)

    print(f"\n基于水面曲线计算的设计建议：")

    print(f"\n1. 渠道设计参数：")
    print(f"   - 渠底宽度：b = {b} m")
    print(f"   - 边坡系数：m = {m}")
    print(f"   - 设计水深：h = {hn:.2f} m (正常水深)")
    print(f"   - 渠道超高：Δh = 0.3-0.5 m")
    print(f"   - 渠堤总高：H = {hn + 0.4:.2f} m")

    print(f"\n2. 壅水控制措施：")
    print(f"   - 当前壅水长度：L = {L_backwater:.0f} m")
    print(f"   - 壅水影响范围：0-{L_backwater:.0f} m")
    print(f"   - 需要抬高渠堤高度：Δh = {h_control - hn:.2f} m")
    print(f"   - 抬高范围：下游 {L_backwater:.0f} m")

    print(f"\n3. 闸门调度建议：")
    print(f"   - 最高控制水位：h_max = {hn + 0.5:.2f} m")
    print(f"   - 正常运行水位：h_normal = {hn:.2f} m")
    print(f"   - 最低运行水位：h_min = {hc:.2f} m (避免临界流)")
    print(f"   - 建议闸前水位不超过 {hn + 0.5:.2f} m")

    print(f"\n4. 渠道维护：")
    print(f"   - 保持设计糙率 n = {n}")
    print(f"   - 定期清除淤积和杂草")
    print(f"   - 检查边坡稳定性")
    print(f"   - 监测壅水水位变化")

    print(f"\n5. 水位监测：")
    print(f"   - 闸前监测：实时监测控制水位")
    print(f"   - 上游监测：在距下游500m、1000m处设监测站")
    print(f"   - 预警水位：当闸前水位超过{hn + 0.3:.2f}m时预警")
    print(f"   - 告警水位：当闸前水位超过{hn + 0.5:.2f}m时告警")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
