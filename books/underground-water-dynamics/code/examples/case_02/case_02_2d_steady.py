"""
案例2：二维稳态地下水流动与网格剖分
=====================================

学习目标：
1. 理解二维稳态渗流方程
2. 掌握二维网格剖分方法
3. 学习不同边界条件的处理
4. 进行网格独立性验证
5. 可视化二维水头场和流速场

问题描述：
一个矩形承压含水层：
- 尺寸：Lx = 1000 m, Ly = 800 m
- 水力传导度：K = 10 m/day（均质）
- 边界条件：
  - 左边界：h = 20 m（第一类边界条件）
  - 右边界：h = 10 m（第一类边界条件）
  - 上下边界：无流边界（第二类边界条件，dh/dn = 0）

求解：二维稳态水头分布 h(x,y)

理论基础：
二维稳态渗流方程：
    ∂/∂x(K * ∂h/∂x) + ∂/∂y(K * ∂h/∂y) = 0

对于均质含水层：
    ∂²h/∂x² + ∂²h/∂y² = 0  (拉普拉斯方程)

边界条件：
    h(0, y) = 20 (左)
    h(Lx, y) = 10 (右)
    ∂h/∂y(x, 0) = 0 (下)
    ∂h/∂y(x, Ly) = 0 (上)

由于上下边界无流，且左右边界条件仅依赖于x，
解应该与y坐标无关（一维流动特征）。
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.abspath('../../..'))

from gwflow.solvers.steady_state import solve_2d_steady_gw, compute_darcy_velocity
from gwflow.grid.structured import create_2d_grid
from gwflow.visualization.plots import plot_2d_head, plot_2d_velocity


def main():
    """主函数"""
    print("=" * 60)
    print("案例2：二维稳态地下水流动与网格剖分")
    print("=" * 60)
    
    # ========== 第1步：定义问题参数 ==========
    print("\n第1步：定义问题参数")
    print("-" * 60)
    
    K = 10.0       # 水力传导度 [m/day]
    Lx = 1000.0    # x方向长度 [m]
    Ly = 800.0     # y方向长度 [m]
    nx = 51        # x方向网格数
    ny = 41        # y方向网格数
    
    print(f"水力传导度 K = {K} m/day")
    print(f"区域尺寸：Lx = {Lx} m, Ly = {Ly} m")
    print(f"网格数量：nx = {nx}, ny = {ny}")
    
    # ========== 第2步：创建网格 ==========
    print("\n第2步：创建二维计算网格")
    print("-" * 60)
    
    X, Y, dx, dy = create_2d_grid(Lx, Ly, nx, ny)
    
    print(f"网格间距：dx = {dx:.2f} m, dy = {dy:.2f} m")
    print(f"总节点数 = {nx} × {ny} = {nx * ny}")
    
    # ========== 第3步：定义边界条件 ==========
    print("\n第3步：定义边界条件")
    print("-" * 60)
    
    boundary_conditions = {
        'left': {'type': 'dirichlet', 'value': 20.0},
        'right': {'type': 'dirichlet', 'value': 10.0},
        'bottom': {'type': 'neumann', 'value': 0.0},
        'top': {'type': 'neumann', 'value': 0.0}
    }
    
    print("左边界：h = 20 m (Dirichlet)")
    print("右边界：h = 10 m (Dirichlet)")
    print("下边界：dh/dy = 0 (Neumann, 无流)")
    print("上边界：dh/dy = 0 (Neumann, 无流)")
    
    # ========== 第4步：数值求解 ==========
    print("\n第4步：数值求解")
    print("-" * 60)
    
    print("正在求解...")
    h = solve_2d_steady_gw(K, Lx, Ly, nx, ny, boundary_conditions)
    
    print(f"✓ 求解完成")
    print(f"水头范围：{h.min():.2f} ~ {h.max():.2f} m")
    print(f"左边界平均水头：{h[:, 0].mean():.2f} m")
    print(f"右边界平均水头：{h[:, -1].mean():.2f} m")
    print(f"中心点水头：{h[ny//2, nx//2]:.2f} m")
    
    # ========== 第5步：验证结果 ==========
    print("\n第5步：验证结果")
    print("-" * 60)
    
    # 检查边界条件
    bc_error_left = np.abs(h[:, 0] - 20.0).max()
    bc_error_right = np.abs(h[:, -1] - 10.0).max()
    
    print(f"左边界误差：{bc_error_left:.2e} m")
    print(f"右边界误差：{bc_error_right:.2e} m")
    
    # 由于无流边界，水头应该在y方向上基本不变
    y_variation = np.std(h, axis=0).mean()
    print(f"水头在y方向的变异性：{y_variation:.4f} m")
    
    if y_variation < 0.01:
        print("✓ 水头在y方向基本不变，符合理论预期")
    
    # 与一维解对比（中心线）
    x_center = X[ny//2, :]
    h_center = h[ny//2, :]
    h_1d_theory = 20.0 + (10.0 - 20.0) * x_center / Lx
    
    error_1d = np.sqrt(np.mean((h_center - h_1d_theory)**2))
    print(f"中心线与一维理论解的RMSE：{error_1d:.4f} m")
    
    # ========== 第6步：计算流速场 ==========
    print("\n第6步：计算达西速度场")
    print("-" * 60)
    
    vx, vy = compute_darcy_velocity(h, K, dx, dy)
    
    print(f"x方向平均流速：{vx.mean():.6f} m/day")
    print(f"y方向平均流速：{vy.mean():.6f} m/day")
    print(f"理论x方向流速：{-K * (10.0 - 20.0) / Lx:.6f} m/day")
    
    # ========== 第7步：可视化 ==========
    print("\n第7步：可视化结果")
    print("-" * 60)
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 图1：水头等值线图
    fig1 = plot_2d_head(
        X, Y, h,
        title="案例2：二维稳态地下水水头分布",
        save_path=os.path.join(output_dir, "case_02_head_contour.png")
    )
    
    # 图2：流速场
    fig2 = plot_2d_velocity(
        X, Y, vx, vy, h,
        title="案例2：地下水流速场",
        skip=3,
        save_path=os.path.join(output_dir, "case_02_velocity.png")
    )
    
    # 图3：沿y=Ly/2的水头分布（与一维理论解对比）
    fig3, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_center, h_center, 'b-', linewidth=2, label='数值解', marker='o',
            markersize=4, markevery=5)
    ax.plot(x_center, h_1d_theory, 'r--', linewidth=2, label='一维理论解')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('x (m)', fontsize=12)
    ax.set_ylabel('水头 (m)', fontsize=12)
    ax.set_title('案例2：中心线水头分布', fontsize=14, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_02_centerline.png"), dpi=300)
    
    print(f"✓ 图形已保存到 {output_dir}/ 目录")
    
    # ========== 第8步：网格独立性验证 ==========
    print("\n第8步：网格独立性验证")
    print("-" * 60)
    
    grid_configs = [
        (11, 9),
        (21, 17),
        (41, 33),
        (81, 65)
    ]
    
    h_center_values = []
    grid_spacings = []
    
    print(f"{'网格配置':>15} {'dx(m)':>10} {'dy(m)':>10} {'中心水头(m)':>15}")
    print("-" * 55)
    
    for nx_test, ny_test in grid_configs:
        X_test, Y_test, dx_test, dy_test = create_2d_grid(Lx, Ly, nx_test, ny_test)
        h_test = solve_2d_steady_gw(K, Lx, Ly, nx_test, ny_test, boundary_conditions)
        h_center_test = h_test[ny_test//2, nx_test//2]
        
        h_center_values.append(h_center_test)
        grid_spacings.append(max(dx_test, dy_test))
        
        print(f"{nx_test}×{ny_test:>4} {dx_test:>10.2f} {dy_test:>10.2f} {h_center_test:>15.6f}")
    
    # 图4：网格独立性分析
    fig4, ax = plt.subplots(figsize=(10, 6))
    ax.semilogx(grid_spacings, h_center_values, 'bo-', linewidth=2,
                markersize=8, label='中心点水头')
    ax.axhline(y=15.0, color='r', linestyle='--', label='理论值(15.0 m)')
    ax.grid(True, alpha=0.3, which='both')
    ax.set_xlabel('最大网格间距 (m)', fontsize=12)
    ax.set_ylabel('中心点水头 (m)', fontsize=12)
    ax.set_title('案例2：网格独立性分析', fontsize=14, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_02_grid_independence.png"), dpi=300)
    
    print(f"\n✓ 网格独立性分析完成")
    print(f"最细网格的中心水头：{h_center_values[-1]:.6f} m")
    print(f"理论值（一维）：15.0 m")
    print(f"误差：{abs(h_center_values[-1] - 15.0):.6f} m")
    
    # ========== 第9步：添加抽水井 ==========
    print("\n第9步：添加抽水井的影响")
    print("-" * 60)
    
    # 创建源汇项（在中心附近设置一个抽水井）
    source = np.zeros((ny, nx))
    well_i, well_j = ny // 2, nx // 2
    pumping_rate = -100.0  # m³/day
    cell_area = dx * dy
    source[well_i, well_j] = pumping_rate / cell_area  # 转换为 m/day
    
    print(f"抽水井位置：({X[well_i, well_j]:.0f}, {Y[well_i, well_j]:.0f}) m")
    print(f"抽水量：{-pumping_rate:.0f} m³/day")
    
    print("正在求解带抽水井的问题...")
    h_pumping = solve_2d_steady_gw(K, Lx, Ly, nx, ny, boundary_conditions, source=source)
    
    print(f"✓ 求解完成")
    print(f"抽水井处水头：{h_pumping[well_i, well_j]:.2f} m")
    print(f"最大降深：{(h - h_pumping).max():.2f} m")
    
    # 图5：抽水影响下的水头分布
    fig5 = plot_2d_head(
        X, Y, h_pumping,
        title="案例2：带抽水井的水头分布",
        save_path=os.path.join(output_dir, "case_02_pumping.png")
    )
    
    # 图6：降深分布
    drawdown = h - h_pumping
    fig6 = plot_2d_head(
        X, Y, drawdown,
        title="案例2：抽水引起的降深",
        save_path=os.path.join(output_dir, "case_02_drawdown.png")
    )
    
    print(f"✓ 抽水影响分析完成")
    
    # ========== 总结 ==========
    print("\n" + "=" * 60)
    print("案例2总结")
    print("=" * 60)
    print("✓ 成功求解二维稳态地下水流动问题")
    print("✓ 掌握了二维网格剖分方法")
    print("✓ 理解了不同类型边界条件的处理")
    print("✓ 完成了网格独立性验证")
    print("✓ 分析了抽水井对流场的影响")
    print("\n关键收获：")
    print("1. 二维问题的求解方法")
    print("2. 边界条件的正确处理")
    print("3. 网格分辨率对结果精度的影响")
    print("4. 源汇项的添加方法")
    print("5. 二维流场的可视化技巧")
    print("=" * 60)
    
    plt.show()


if __name__ == "__main__":
    main()
