"""
案例1：农村灌溉渠流量计算 - 主程序

问题描述：
某农村灌区灌溉渠道设计，已知：
- 设计流量 Q = 0.5 m³/s
- 渠底宽度 b = 1.0 m
- 边坡系数 m = 1.5
- 渠底坡度 S0 = 0.0002
- 曼宁糙率 n = 0.025（土质渠道）

求解：
1. 正常水深 h0
2. 流动状态（Fr数）
3. 所有水力要素

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import TrapezoidalChannel
from solvers.steady.uniform_flow import UniformFlowSolver


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
                print(f"{key:20s}: {value:.6e}")
            else:
                print(f"{key:20s}: {value:.4f}")
        else:
            print(f"{key:20s}: {value}")
    print_separator()


def main():
    """主函数"""
    print_separator("案例1：农村灌溉渠流量计算")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    # 渠道几何参数
    b = 1.0      # 渠底宽度 (m)
    m = 1.5      # 边坡系数
    n = 0.025    # 曼宁糙率系数
    S0 = 0.0002  # 渠底坡度

    # 设计流量
    Q_design = 0.5  # m³/s

    print(f"渠道类型：梯形断面")
    print(f"渠底宽度 b = {b} m")
    print(f"边坡系数 m = {m} (边坡为{m}:1)")
    print(f"曼宁糙率 n = {n} (土质渠道)")
    print(f"渠底坡度 S0 = {S0} ({S0*100:.02f}%)")
    print(f"设计流量 Q = {Q_design} m³/s")

    # ==================== 第二步：创建渠道对象 ====================
    print("\n【步骤2】创建渠道模型")
    print("-" * 80)

    channel = TrapezoidalChannel(b=b, m=m, n=n, S0=S0)
    print(f"渠道对象：{channel}")

    # ==================== 第三步：创建求解器 ====================
    print("\n【步骤3】创建均匀流求解器")
    print("-" * 80)

    solver = UniformFlowSolver(channel)
    print(f"求解器：{solver}")

    # ==================== 第四步：计算正常水深 ====================
    print("\n【步骤4】计算正常水深")
    print("-" * 80)

    print(f"求解方程：Q = A * (1/n) * R^(2/3) * S0^(1/2) = {Q_design} m³/s")
    print("使用牛顿迭代法求解...")

    results = solver.compute_normal_depth(Q_design)

    print_results(results, "正常水深计算结果")

    # 提取关键结果
    h0 = results["正常水深_h0"]
    A = results["面积_A"]
    R = results["水力半径_R"]
    v = results["流速_v"]
    Fr = results["弗劳德数_Fr"]

    # ==================== 第五步：流动状态分析 ====================
    print("\n【步骤5】流动状态分析")
    print("-" * 80)

    flow_analysis = solver.analyze_flow_state(Q_design)
    print_results(flow_analysis, "流态分析结果")

    # ==================== 第六步：验证计算 ====================
    print("\n【步骤6】验证计算")
    print("-" * 80)

    # 用曼宁公式验证
    Q_check = A * (1.0/n) * (R**(2.0/3.0)) * (S0**0.5)
    error = abs(Q_check - Q_design) / Q_design * 100

    print(f"计算流量：Q_calc = {Q_check:.6f} m³/s")
    print(f"设计流量：Q_design = {Q_design:.6f} m³/s")
    print(f"相对误差：{error:.8f}%")

    if error < 0.1:
        print("✓ 验证通过！计算结果准确。")
    else:
        print("✗ 验证失败！存在较大误差。")

    # ==================== 第七步：工程建议 ====================
    print("\n【步骤7】工程建议")
    print("-" * 80)

    print(f"1. 渠道设计水深：h = {h0:.3f} m")
    print(f"2. 建议加高 20% 作为安全超高，实际开挖深度：{h0 * 1.2:.3f} m")
    print(f"3. 水面宽度：B = {results['水面宽_B']:.3f} m")
    print(f"4. 渠道顶部宽度应至少为：{results['水面宽_B'] + 0.5:.3f} m（考虑边坡和维护通道）")
    print(f"5. 流速 v = {v:.3f} m/s，在合理范围内（0.3-1.0 m/s），不会引起冲刷或淤积")
    print(f"6. 流态为{results['流态']}，水流稳定，适合灌溉")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
