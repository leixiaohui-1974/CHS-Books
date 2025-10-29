"""
案例9：河道糙率率定 - 计算实验

实验内容：
1. 实验9.1：测量误差对糙率率定的影响
2. 实验9.2：不同流量下的糙率率定
3. 实验9.3：季节变化对糙率的影响
4. 实验9.4：Q-h关系曲线验证

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


def calibrate_n(Q, B, h, S):
    """率定糙率"""
    A = B * h
    P = B + 2 * h
    R = A / P
    n = A * (R ** (2.0/3.0)) * (S ** 0.5) / Q
    return n


def experiment_9_1():
    """实验9.1：测量误差对糙率率定的影响"""
    print_separator("实验9.1：测量误差对糙率率定的影响")

    # 基准参数
    Q0, B0, h0, S0 = 180.0, 45.0, 3.2, 0.0004
    n0 = calibrate_n(Q0, B0, h0, S0)

    print(f"\n基准条件：Q={Q0}m³/s, B={B0}m, h={h0}m, S={S0}")
    print(f"基准糙率：n₀ = {n0:.4f}")

    print("\n测量误差影响分析：")
    print("-" * 100)
    print(f"{'误差项':^15} | {'误差值':^12} | {'率定糙率n':^14} | {'相对偏差(%)':^14} | {'影响程度':^15}")
    print("-" * 100)

    errors = [
        ("基准值", 0, Q0, B0, h0, S0),
        ("Q误差+5%", 0.05, Q0*1.05, B0, h0, S0),
        ("Q误差-5%", -0.05, Q0*0.95, B0, h0, S0),
        ("h误差+2cm", 0.02/h0, Q0, B0, h0+0.02, S0),
        ("h误差-2cm", -0.02/h0, Q0, B0, h0-0.02, S0),
        ("B误差+0.5m", 0.5/B0, Q0, B0+0.5, h0, S0),
        ("S误差+25%", 0.25, Q0, B0, h0, S0*1.25),
    ]

    for label, err_pct, Q, B, h, S in errors:
        n = calibrate_n(Q, B, h, S)
        deviation = (n - n0) / n0 * 100
        impact = "严重" if abs(deviation) > 5 else "显著" if abs(deviation) > 3 else "一般" if abs(deviation) > 1 else "较小"
        err_str = f"{err_pct*100:+.1f}%" if err_pct != 0 else "-"
        print(f"{label:^15} | {err_str:^12} | {n:^14.4f} | {deviation:^14.2f} | {impact:^15}")

    print("-" * 100)
    print("\n【实验结论】")
    print("1. 流量误差影响最大：5%流量误差导致5%糙率误差")
    print("2. 坡度误差影响明显：25%坡度误差导致11%糙率误差")
    print("3. 水深误差影响中等：2cm误差导致1-2%糙率误差")
    print("4. 工程建议：提高流量和坡度测量精度最重要")


def experiment_9_2():
    """实验9.2：不同流量下的糙率率定"""
    print_separator("实验9.2：不同流量下的糙率率定")

    B, S = 45.0, 0.0004
    n_true = 0.031  # 假设的真实糙率

    # 使用真实糙率计算不同流量下的水深
    channel = RectangularChannel(b=B, S0=S, n=n_true)

    print(f"\n假设真实糙率 n = {n_true:.3f}")
    print("\n不同流量下的率定对比：")
    print("-" * 100)
    print(f"{'流量Q(m³/s)':^14} | {'真实水深h(m)':^15} | {'率定糙率n':^14} | {'相对偏差(%)':^15}")
    print("-" * 100)

    Q_values = [50, 100, 150, 180, 200, 250, 300]
    for Q in Q_values:
        h = channel.compute_normal_depth(Q)
        n_cal = calibrate_n(Q, B, h, S)
        deviation = (n_cal - n_true) / n_true * 100
        print(f"{Q:^14.0f} | {h:^15.4f} | {n_cal:^14.4f} | {deviation:^15.2f}")

    print("-" * 100)
    print("\n【实验结论】")
    print("1. 理论上，不同流量下率定的糙率应相同")
    print("2. 实际中，糙率可能随流量略有变化（相对粗糙度效应）")
    print("3. 多次测量取平均可提高精度")
    print("4. 建议在不同流量下多次率定，建立n-Q关系")


def experiment_9_3():
    """实验9.3：季节变化对糙率的影响"""
    print_separator("实验9.3：季节变化对糙率的影响")

    print("\n天然河道糙率的季节变化：")
    print("-" * 100)
    print(f"{'季节':^15} | {'河床状况':^25} | {'糙率n':^12} | {'相对变化(%)':^15}")
    print("-" * 100)

    seasons = [
        ("春季（4-5月）", "河床清洁，流量中等", 0.030, 0),
        ("夏季（6-8月）", "汛期，水流急，冲刷作用强", 0.028, -6.7),
        ("秋季（9-11月）", "水位下降，杂草开始生长", 0.033, +10.0),
        ("冬季（12-2月）", "枯水期，杂草茂盛，可能结冰", 0.038, +26.7),
    ]

    n_base = seasons[0][2]
    for season, condition, n, change in seasons:
        print(f"{season:^15} | {condition:^25} | {n:^12.3f} | {change:^15.1f}")

    print("-" * 100)

    print("\n【实验结论】")
    print("1. 糙率具有明显的季节变化")
    print("2. 汛期糙率最小（水流冲刷，杂草少）")
    print("3. 枯水期糙率最大（杂草茂盛）")
    print("4. 冬季结冰会增大糙率20-30%")
    print("5. 工程建议：")
    print("   - 洪水计算：采用汛期糙率（偏小值）")
    print("   - 一般计算：采用年平均糙率")
    print("   - 标注测量季节和河床状况")


def experiment_9_4():
    """实验9.4：Q-h关系曲线验证"""
    print_separator("实验9.4：Q-h关系曲线精度验证")

    # 实测数据点（假设）
    measured_data = [
        (80, 2.0),
        (120, 2.5),
        (180, 3.2),
        (220, 3.7),
        (280, 4.3),
    ]

    # 率定糙率
    B, S = 45.0, 0.0004
    n_list = []
    for Q, h in measured_data:
        n = calibrate_n(Q, B, h, S)
        n_list.append(n)

    n_avg = np.mean(n_list)

    print(f"\n基于{len(measured_data)}个测点率定糙率：")
    print(f"  平均糙率 n = {n_avg:.4f}")
    print(f"  标准差 σ = {np.std(n_list):.4f}")

    # 使用平均糙率建立Q-h关系
    channel = RectangularChannel(b=B, S0=S, n=n_avg)

    print("\nQ-h关系验证：")
    print("-" * 90)
    print(f"{'流量Q(m³/s)':^14} | {'实测水深(m)':^14} | {'计算水深(m)':^14} | {'误差(m)':^12} | {'相对误差(%)':^14}")
    print("-" * 90)

    for Q, h_measured in measured_data:
        h_calculated = channel.compute_normal_depth(Q)
        error = h_calculated - h_measured
        rel_error = error / h_measured * 100
        print(f"{Q:^14.0f} | {h_measured:^14.2f} | {h_calculated:^14.4f} | {error:^12.4f} | {rel_error:^14.2f}")

    print("-" * 90)

    errors = [abs(channel.compute_normal_depth(Q) - h) for Q, h in measured_data]
    rmse = np.sqrt(np.mean([e**2 for e in errors]))

    print(f"\n拟合精度评价：")
    print(f"  均方根误差 RMSE = {rmse:.4f} m")
    print(f"  最大误差 = {max(errors):.4f} m")
    print(f"  平均误差 = {np.mean(errors):.4f} m")

    print("\n【实验结论】")
    print("1. Q-h关系曲线拟合精度较好")
    print("2. RMSE < 0.1m 为优秀，< 0.2m 为良好")
    print("3. 该关系可用于水位预报和流量推算")
    print("4. 需要注意适用范围和河床变化")


def main():
    """主函数"""
    print_separator("案例9：计算实验")
    print("\n本实验将探讨糙率率定的各种影响因素\n")

    experiment_9_1()  # 测量误差影响
    experiment_9_2()  # 不同流量
    experiment_9_3()  # 季节变化
    experiment_9_4()  # Q-h关系验证

    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 测量误差：流量和坡度误差影响最大")
    print("2. 流量影响：理论上糙率不变，实际略有波动")
    print("3. 季节变化：糙率随季节变化可达30%")
    print("4. Q-h关系：糙率率定是建立水位流量关系的基础")
    print("\n糙率率定是河道水文分析的关键参数，")
    print("需要通过实测数据反复率定和验证！")
    print_separator()


if __name__ == "__main__":
    main()
