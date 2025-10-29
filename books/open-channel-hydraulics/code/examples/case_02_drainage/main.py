"""
案例2：城市雨水排水渠设计 - 主程序

问题描述：
某城市居民小区雨水排水渠设计，已知：
- 设计流量 Q = 1.2 m³/s
- 渠道宽度 b = 1.5 m
- 渠底坡度 S0 = 0.003
- 曼宁糙率 n = 0.013（混凝土）

求解：
1. 正常水深 h0
2. 流态判别（Fr数）
3. 流速校核
4. 设计建议

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from models.channel import RectangularChannel
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
    print_separator("案例2：城市雨水排水渠设计")

    # ==================== 第一步：定义问题参数 ====================
    print("\n【步骤1】问题参数")
    print("-" * 80)

    # 渠道几何参数
    b = 1.5      # 渠宽 (m)
    n = 0.013    # 曼宁糙率系数（混凝土）
    S0 = 0.003   # 渠底坡度

    # 设计流量
    Q_design = 1.2  # m³/s

    print(f"渠道类型：矩形断面（混凝土）")
    print(f"渠道宽度 b = {b} m")
    print(f"曼宁糙率 n = {n} (混凝土光滑表面)")
    print(f"渠底坡度 S0 = {S0} ({S0*100:.1f}%)")
    print(f"设计流量 Q = {Q_design} m³/s")

    # ==================== 第二步：创建渠道对象 ====================
    print("\n【步骤2】创建渠道模型")
    print("-" * 80)

    channel = RectangularChannel(b=b, n=n, S0=S0)
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

    # ==================== 第五步：临界水深和流态分析 ====================
    print("\n【步骤5】临界水深和流态分析")
    print("-" * 80)

    # 计算临界水深
    hc = channel.compute_critical_depth(Q_design)
    q = Q_design / b  # 单宽流量

    print(f"单宽流量 q = Q/b = {q:.4f} m²/s")
    print(f"临界水深公式（矩形）：hc = (q²/g)^(1/3)")

    # 矩形断面理论临界水深
    import numpy as np
    g = 9.81
    hc_theory = (q**2 / g) ** (1.0/3.0)
    print(f"理论临界水深：hc = {hc_theory:.4f} m")
    print(f"数值计算临界水深：hc = {hc:.4f} m")
    print(f"正常水深：h0 = {h0:.4f} m")

    print(f"\n流态判别：")
    if h0 > hc * 1.05:  # 留5%余量
        print(f"  h0 ({h0:.3f} m) > hc ({hc:.3f} m)")
        print(f"  Fr = {Fr:.3f} < 1")
        print(f"  ✓ 流态为【缓流】（亚临界流），水流稳定")
    elif h0 < hc * 0.95:
        print(f"  h0 ({h0:.3f} m) < hc ({hc:.3f} m)")
        print(f"  Fr = {Fr:.3f} > 1")
        print(f"  ✗ 流态为【急流】（超临界流），可能不稳定")
    else:
        print(f"  h0 ({h0:.3f} m) ≈ hc ({hc:.3f} m)")
        print(f"  Fr = {Fr:.3f} ≈ 1")
        print(f"  ⚠ 流态为【临界流】，应避免！")

    # ==================== 第六步：流速校核 ====================
    print("\n【步骤6】流速校核")
    print("-" * 80)

    v_min = 0.6  # 最小流速，防止淤积
    v_max = 3.0  # 最大流速（混凝土），防止冲刷

    print(f"设计流速 v = {v:.4f} m/s")
    print(f"\n流速控制标准：")
    print(f"  最小流速（防淤积）：v_min = {v_min} m/s")
    print(f"  最大流速（防冲刷）：v_max = {v_max} m/s（混凝土渠道）")

    print(f"\n校核结果：")
    if v < v_min:
        print(f"  ✗ 流速过小（v = {v:.3f} < {v_min} m/s）")
        print(f"     可能导致泥沙淤积，建议增大坡度或减小断面")
        velocity_ok = False
    elif v > v_max:
        print(f"  ✗ 流速过大（v = {v:.3f} > {v_max} m/s）")
        print(f"     可能冲刷渠底，建议减小坡度或增大断面")
        velocity_ok = False
    else:
        print(f"  ✓ 流速合适（{v_min} < {v:.3f} < {v_max} m/s）")
        print(f"     满足防淤积和防冲刷要求")
        velocity_ok = True

    # ==================== 第七步：断面校核 ====================
    print("\n【步骤7】断面尺寸校核")
    print("-" * 80)

    # 渠深（含安全超高）
    freeboard_ratio = 0.25  # 安全超高比例
    freeboard = h0 * freeboard_ratio
    total_depth = h0 + freeboard

    print(f"设计水深：h0 = {h0:.3f} m")
    print(f"安全超高：Δh = {freeboard:.3f} m（取水深的{freeboard_ratio*100:.0f}%）")
    print(f"渠道总深：H = {total_depth:.3f} m")
    print(f"\n渠道尺寸：")
    print(f"  内宽 b = {b:.2f} m")
    print(f"  内高 H = {total_depth:.2f} m")
    print(f"  建议采用 {b:.1f} m × {np.ceil(total_depth*10)/10:.1f} m 的矩形断面")

    # ==================== 第八步：设计总结 ====================
    print("\n【步骤8】设计总结与建议")
    print("-" * 80)

    print("✓ 设计计算完成！")
    print(f"\n1. 水力计算结果：")
    print(f"   - 正常水深：{h0:.3f} m")
    print(f"   - 设计流速：{v:.3f} m/s")
    print(f"   - 弗劳德数：{Fr:.3f}")
    print(f"   - 流动状态：{results['流态']}")

    print(f"\n2. 断面设计：")
    print(f"   - 渠道形式：矩形混凝土渠道")
    print(f"   - 渠道宽度：{b:.2f} m")
    print(f"   - 渠道深度：{total_depth:.2f} m（含安全超高）")

    print(f"\n3. 设计检验：")
    if velocity_ok and Fr < 0.8:
        print(f"   ✓ 流速满足要求（{v_min} ~ {v_max} m/s）")
        print(f"   ✓ 流态为稳定缓流（Fr < 0.8）")
        print(f"   ✓ 设计合理，可以采用")
    else:
        print(f"   ⚠ 存在问题，需要优化设计")
        if not velocity_ok:
            print(f"      - 流速不满足要求")
        if Fr >= 0.8:
            print(f"      - 弗劳德数较大，接近临界流")

    print(f"\n4. 施工建议：")
    print(f"   - 采用现浇或预制混凝土结构")
    print(f"   - 渠底应平整，坡度均匀")
    print(f"   - 转弯处应设置过渡段")
    print(f"   - 每隔 50-100m 设置沉砂井")
    print(f"   - 渠顶加盖或设栅栏，确保安全")

    # ==================== 完成 ====================
    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
