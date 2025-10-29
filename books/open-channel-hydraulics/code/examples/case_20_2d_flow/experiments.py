"""
案例20：二维明渠水流模拟 - 计算实验

实验内容：
1. 实验20.1：网格密度影响
2. 实验20.2：地形对流场的影响
3. 实验20.3：一维与二维模型对比

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from main import (ShallowWater2DSolver, create_channel_floodplain_topography,
                 print_separator)


def experiment_20_1():
    """实验20.1：网格密度对计算精度的影响"""
    print_separator("实验20.1：网格密度影响")

    Lx = 500.0
    Ly = 200.0
    Q_inflow = 500.0
    t_end = 300.0  # 缩短时间

    print(f"\n固定参数：L={Lx}×{Ly}m, Q={Q_inflow}m³/s, t={t_end}s")
    print("变化参数：网格密度")

    # 不同网格配置
    grid_configs = [
        (25, 10, "粗网格"),
        (50, 20, "中等网格"),
    ]

    print(f"\n网格密度对计算的影响：")
    print("-" * 100)
    print(f"{'配置':^14} | {'Nx×Ny':^12} | {'Δx(m)':^10} | "
          f"{'计算步数':^12} | {'最大水深(m)':^14} | {'淹没面积(m²)':^14}")
    print("-" * 100)

    for Nx, Ny, label in grid_configs:
        try:
            solver = ShallowWater2DSolver(Lx, Ly, Nx, Ny)

            # 地形
            z_b, n_manning = create_channel_floodplain_topography(solver.X, solver.Y)
            solver.set_topography(z_b, n_manning)

            # 初始条件
            h0 = np.zeros((Nx, Ny))
            for i in range(Nx):
                for j in range(Ny):
                    if abs(solver.Y[i, j] - Ly/2) < 25:
                        h0[i, j] = 3.0

            solver.set_initial_conditions(h0, np.zeros((Nx, Ny)), np.zeros((Nx, Ny)))

            # 运行（不输出）
            print(f"  {label}: 计算中...", end='', flush=True)
            results = solver.run(t_end, Q_inflow, dt_output=t_end+1, CFL=0.3)

            h_final = results['h'][-1]
            max_depth = np.max(h_final)
            flooded_area = np.sum(h_final > 0.01) * (Lx/Nx) * (Ly/Ny)

            print(f" 完成")
            print(f"{label:^14} | {Nx}×{Ny:^12} | {Lx/Nx:^10.1f} | "
                  f"{len(results['times']):^12} | {max_depth:^14.2f} | {flooded_area:^14.0f}")

        except Exception as e:
            print(f"{label:^14} | {Nx}×{Ny:^12} | {Lx/Nx:^10.1f} | {'失败':^12} | "
                  f"{'-':^14} | {'-':^14}")

    print("-" * 100)

    print(f"\n【实验结论】")
    print("1. 网格越密，计算精度越高")
    print("2. 网格越密，计算时间越长（∝ Nx×Ny）")
    print("3. 需要在精度和效率之间平衡")
    print("4. 关键区域可使用局部加密网格")
    print("5. 推荐：主槽Δx=5-10m，滩地Δx=10-20m")


def experiment_20_2():
    """实验20.2：不同地形对流场的影响"""
    print_separator("实验20.2：地形对流场的影响")

    Lx = 500.0
    Ly = 200.0
    Nx = 50
    Ny = 20
    Q_inflow = 500.0
    t_end = 300.0

    print(f"\n固定参数：网格{Nx}×{Ny}, Q={Q_inflow}m³/s")
    print("变化参数：地形配置")

    # 不同地形场景
    scenarios = []

    # 场景1：标准河道
    solver1 = ShallowWater2DSolver(Lx, Ly, Nx, Ny)
    z_b1, n1 = create_channel_floodplain_topography(solver1.X, solver1.Y)
    scenarios.append((solver1, z_b1, n1, "标准河道"))

    # 场景2：无滩地（整个宽度都是主槽）
    solver2 = ShallowWater2DSolver(Lx, Ly, Nx, Ny)
    z_b2 = np.zeros_like(solver2.X)
    n2 = np.full_like(solver2.X, 0.03)
    scenarios.append((solver2, z_b2, n2, "宽浅河道"))

    # 场景3：高滩地（4m高程）
    solver3 = ShallowWater2DSolver(Lx, Ly, Nx, Ny)
    z_b3, n3 = create_channel_floodplain_topography(solver3.X, solver3.Y)
    for i in range(Nx):
        for j in range(Ny):
            if abs(solver3.Y[i, j] - Ly/2) > 25:
                z_b3[i, j] = 4.0  # 更高的滩地
    scenarios.append((solver3, z_b3, n3, "高滩地"))

    print(f"\n地形对水流的影响：")
    print("-" * 100)
    print(f"{'场景':^14} | {'主槽宽度(m)':^14} | {'滩地高程(m)':^14} | "
          f"{'最大水深(m)':^14} | {'淹没面积(m²)':^14}")
    print("-" * 100)

    for solver, z_b, n, scenario_name in scenarios:
        try:
            solver.set_topography(z_b, n)

            # 初始条件
            h0 = np.zeros((Nx, Ny))
            for i in range(Nx):
                for j in range(Ny):
                    if abs(solver.Y[i, j] - Ly/2) < 25:
                        h0[i, j] = 3.0

            solver.set_initial_conditions(h0, np.zeros((Nx, Ny)), np.zeros((Nx, Ny)))

            # 运行
            print(f"  {scenario_name}: 计算中...", end='', flush=True)
            results = solver.run(t_end, Q_inflow, dt_output=t_end+1, CFL=0.3)

            h_final = results['h'][-1]
            max_depth = np.max(h_final)
            flooded_area = np.sum(h_final > 0.01) * (Lx/Nx) * (Ly/Ny)

            # 地形特征
            channel_width = 50.0 if scenario_name != "宽浅河道" else 200.0
            floodplain_elev = np.max(z_b)

            print(f" 完成")
            print(f"{scenario_name:^14} | {channel_width:^14.0f} | {floodplain_elev:^14.1f} | "
                  f"{max_depth:^14.2f} | {flooded_area:^14.0f}")

        except Exception as e:
            print(f"{scenario_name:^14} | {'-':^14} | {'-':^14} | "
                  f"{'-':^14} | {'-':^14}")

    print("-" * 100)

    print(f"\n【实验结论】")
    print("1. 主槽宽度影响主槽流速")
    print("2. 滩地高程决定漫滩程度")
    print("3. 高滩地延迟漫滩发生时间")
    print("4. 复合断面增加过流能力")
    print("5. 地形是二维模拟的关键输入")


def experiment_20_3():
    """实验20.3：一维与二维模型对比"""
    print_separator("实验20.3：一维与二维模型对比")

    print(f"\n一维与二维模型的对比：")
    print("-" * 110)
    print(f"{'特性':^16} | {'一维模型':^40} | {'二维模型':^40}")
    print("-" * 110)

    comparisons = [
        ("方程数", "2个（h, Q）", "3个（h, hu, hv）"),
        ("空间维度", "1个（沿程x）", "2个（x, y平面）"),
        ("网格", "一维数组", "二维数组（Nx×Ny）"),
        ("计算量", "小（N个单元）", "大（Nx×Ny个单元）"),
        ("通量方向", "1个（纵向）", "2个（纵向+横向）"),
        ("流动模式", "单向流", "多向流、回流、涡旋"),
        ("适用场景", "河道、渠道", "河口、湖泊、漫滩"),
        ("边界条件", "2个（上下游）", "4个（上下左右）"),
        ("干湿处理", "相对简单", "复杂（二维界面）"),
        ("可视化", "曲线图", "等值线图、矢量场"),
    ]

    for feature, one_d, two_d in comparisons:
        print(f"{feature:^16} | {one_d:^40} | {two_d:^40}")

    print("-" * 110)

    print(f"\n【实验结论】")
    print("1. 一维模型：简单高效，适合规则河道")
    print("2. 二维模型：准确但复杂，适合复杂地形")
    print("3. 选择原则：")
    print("   - 主槽流动：一维模型")
    print("   - 漫滩、河口：二维模型")
    print("   - 工程设计：先一维后二维")
    print("4. 二维模型计算量约为一维的100-1000倍")
    print("5. 现代CFD软件多采用二维/三维模型")


def main():
    """主函数"""
    print_separator("案例20：计算实验")
    print("\n本实验将探讨二维明渠水流模拟的关键问题\n")

    experiment_20_1()  # 网格密度
    experiment_20_2()  # 地形影响
    experiment_20_3()  # 一维二维对比

    print_separator("实验总结")
    print("\n通过以上实验，我们深入理解了：")
    print("1. 网格密度：影响计算精度和效率")
    print("2. 地形影响：决定流场分布和漫滩过程")
    print("3. 模型选择：一维与二维各有优势")
    print("\n二维水流模拟的工程价值：")
    print("- 洪水风险评估：准确预测淹没范围")
    print("- 河道整治设计：优化断面形状")
    print("- 环境影响评价：污染物扩散模拟")
    print("- 生态修复：栖息地水动力分析")
    print("- 防洪规划：堤防选址与高程确定")
    print_separator()


if __name__ == "__main__":
    main()
