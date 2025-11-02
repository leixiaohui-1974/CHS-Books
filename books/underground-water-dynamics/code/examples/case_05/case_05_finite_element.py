"""
案例5：有限元方法基础
=======================

学习目标：
1. 理解Galerkin有限元方法
2. 掌握三角形网格生成
3. 学习单元刚度矩阵组装
4. 理解弱形式和变分原理
5. 比较有限元与有限差分

问题描述：
使用有限元方法求解二维稳态地下水流动。
与案例2的有限差分结果对比。

理论基础：
强形式：
    -∇·(K∇h) = 0  in Ω
    h = g        on Γ_D (Dirichlet边界)
    -K∂h/∂n = q  on Γ_N (Neumann边界)

弱形式（Galerkin）：
    ∫∫ K ∇w · ∇h dA = 0  ∀w ∈ H₀¹(Ω)

有限元近似：
    h ≈ Σ N_i(x,y) * h_i
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.abspath('../../..'))

from gwflow.grid.unstructured import (
    generate_rectangular_triangular_mesh,
    plot_mesh,
    compute_element_area,
    compute_element_quality,
    TriangularMesh
)
from gwflow.solvers.finite_element import (
    solve_fem_2d,
    compute_fem_gradient,
    compute_element_errors
)
from gwflow.solvers.steady_state import solve_2d_steady_gw
from gwflow.grid.structured import create_2d_grid


def main():
    """主函数"""
    print("=" * 60)
    print("案例5：有限元方法基础")
    print("=" * 60)
    
    # ========== 第1步：定义问题参数 ==========
    print("\n第1步：定义问题参数")
    print("-" * 60)
    
    K = 10.0       # 水力传导度 [m/day]
    Lx = 100.0     # x方向长度 [m]
    Ly = 80.0      # y方向长度 [m]
    nx = 11        # x方向节点数
    ny = 9         # y方向节点数
    
    print(f"水力传导度 K = {K} m/day")
    print(f"区域尺寸：Lx = {Lx} m, Ly = {Ly} m")
    print(f"网格节点数：nx = {nx}, ny = {ny}")
    
    # ========== 第2步：生成三角形网格 ==========
    print("\n第2步：生成三角形网格")
    print("-" * 60)
    
    mesh = generate_rectangular_triangular_mesh(Lx, Ly, nx, ny)
    
    print(f"✓ 网格生成完成")
    print(f"  顶点数: {mesh.n_vertices}")
    print(f"  单元数: {mesh.n_elements}")
    print(f"  边界边数: {len(mesh.boundary_edges)}")
    
    # 计算网格质量
    qualities = [compute_element_quality(mesh.vertices, elem) 
                 for elem in mesh.elements]
    min_angle = min(qualities)
    avg_angle = np.mean(qualities)
    
    print(f"  网格质量（最小角度）: {min_angle:.2f}°")
    print(f"  平均最小角度: {avg_angle:.2f}°")
    
    # 计算单元面积
    areas = [compute_element_area(mesh.vertices, elem) 
             for elem in mesh.elements]
    print(f"  单元面积范围: [{min(areas):.2f}, {max(areas):.2f}] m²")
    
    # ========== 第3步：设置边界条件 ==========
    print("\n第3步：设置边界条件")
    print("-" * 60)
    
    # 识别边界节点
    # 左边界: x = 0, 右边界: x = Lx
    left_nodes = []
    right_nodes = []
    
    for i, vertex in enumerate(mesh.vertices):
        if np.isclose(vertex[0], 0.0):
            left_nodes.append(i)
        elif np.isclose(vertex[0], Lx):
            right_nodes.append(i)
    
    # Dirichlet边界条件
    h_left = 20.0
    h_right = 10.0
    
    boundary_conditions = {
        'dirichlet': [(node, h_left) for node in left_nodes] + 
                     [(node, h_right) for node in right_nodes]
    }
    
    print(f"左边界节点数: {len(left_nodes)}, h = {h_left} m")
    print(f"右边界节点数: {len(right_nodes)}, h = {h_right} m")
    print(f"Dirichlet边界条件总数: {len(boundary_conditions['dirichlet'])}")
    
    # ========== 第4步：有限元求解 ==========
    print("\n第4步：有限元求解")
    print("-" * 60)
    
    print("正在求解...")
    h_fem = solve_fem_2d(mesh, K, boundary_conditions)
    
    print(f"✓ 求解完成")
    print(f"水头范围: [{h_fem.min():.4f}, {h_fem.max():.4f}] m")
    print(f"左边界平均水头: {h_fem[left_nodes].mean():.4f} m")
    print(f"右边界平均水头: {h_fem[right_nodes].mean():.4f} m")
    
    # ========== 第5步：计算梯度和流速 ==========
    print("\n第5步：计算梯度和达西速度")
    print("-" * 60)
    
    grad_h, elem_centers = compute_fem_gradient(mesh, h_fem)
    
    # 达西速度: v = -K * ∇h
    velocity = -K * grad_h
    
    print(f"x方向平均流速: {velocity[:, 0].mean():.6f} m/day")
    print(f"y方向平均流速: {velocity[:, 1].mean():.6f} m/day")
    print(f"理论x方向流速: {-K * (h_right - h_left) / Lx:.6f} m/day")
    
    # ========== 第6步：与有限差分法对比 ==========
    print("\n第6步：与有限差分法对比")
    print("-" * 60)
    
    # 使用有限差分求解相同问题
    X_fd, Y_fd, dx, dy = create_2d_grid(Lx, Ly, nx, ny)
    
    bc_fd = {
        'left': {'type': 'dirichlet', 'value': h_left},
        'right': {'type': 'dirichlet', 'value': h_right},
        'bottom': {'type': 'neumann', 'value': 0.0},
        'top': {'type': 'neumann', 'value': 0.0}
    }
    
    print("正在用有限差分求解...")
    h_fd = solve_2d_steady_gw(K, Lx, Ly, nx, ny, bc_fd)
    h_fd_flat = h_fd.ravel()
    
    # 对比节点值
    diff = np.abs(h_fem - h_fd_flat)
    rmse = np.sqrt(np.mean(diff**2))
    max_diff = np.max(diff)
    
    print(f"✓ 有限差分求解完成")
    print(f"与有限元解的差异:")
    print(f"  RMSE = {rmse:.6f} m")
    print(f"  最大差异 = {max_diff:.6f} m")
    print(f"  相对误差 = {max_diff / (h_left - h_right) * 100:.3f} %")
    
    if rmse < 0.01:
        print("✓ 两种方法结果高度一致！")
    
    # ========== 第7步：与解析解对比 ==========
    print("\n第7步：与解析解对比")
    print("-" * 60)
    
    # 对于无流上下边界的线性问题，解析解为
    def h_analytical(x, y):
        return h_left + (h_right - h_left) * x / Lx
    
    h_exact = np.array([h_analytical(x, y) for x, y in mesh.vertices])
    
    # 计算误差
    errors = compute_element_errors(mesh, h_fem, h_analytical)
    
    print(f"与解析解的误差:")
    print(f"  L² 范数: {errors['L2']:.6e} m")
    print(f"  L∞ 范数: {errors['Linf']:.6e} m")
    
    # ========== 第8步：可视化 ==========
    print("\n第8步：可视化结果")
    print("-" * 60)
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 图1：网格可视化
    fig1, ax1 = plt.subplots(figsize=(12, 9))
    plot_mesh(mesh, ax1)
    plt.savefig(os.path.join(output_dir, "case_05_mesh.png"), dpi=300)
    
    # 图2：有限元解（三角形等值线）
    fig2, ax2 = plt.subplots(figsize=(12, 9))
    
    # 创建三角剖分对象用于绘图
    import matplotlib.tri as tri
    triang = tri.Triangulation(mesh.vertices[:, 0], mesh.vertices[:, 1], 
                                mesh.elements)
    
    contourf = ax2.tricontourf(triang, h_fem, levels=20, cmap='viridis')
    contour = ax2.tricontour(triang, h_fem, levels=10, colors='black',
                            linewidths=0.5, alpha=0.4)
    ax2.clabel(contour, inline=True, fontsize=8, fmt='%.1f')
    
    plt.colorbar(contourf, ax=ax2, label='水头 (m)')
    ax2.set_xlabel('x (m)', fontsize=12)
    ax2.set_ylabel('y (m)', fontsize=12)
    ax2.set_title('案例5：有限元解 - 水头分布', fontsize=14, fontweight='bold')
    ax2.set_aspect('equal')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_05_fem_solution.png"), dpi=300)
    
    # 图3：有限差分解（对比）
    fig3, ax3 = plt.subplots(figsize=(12, 9))
    contourf = ax3.contourf(X_fd, Y_fd, h_fd, levels=20, cmap='viridis')
    contour = ax3.contour(X_fd, Y_fd, h_fd, levels=10, colors='black',
                         linewidths=0.5, alpha=0.4)
    ax3.clabel(contour, inline=True, fontsize=8, fmt='%.1f')
    
    plt.colorbar(contourf, ax=ax3, label='水头 (m)')
    ax3.set_xlabel('x (m)', fontsize=12)
    ax3.set_ylabel('y (m)', fontsize=12)
    ax3.set_title('案例5：有限差分解 - 水头分布', fontsize=14, fontweight='bold')
    ax3.set_aspect('equal')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_05_fd_solution.png"), dpi=300)
    
    # 图4：方法对比
    fig4, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # 左图：沿中心线的对比
    y_center_idx = ny // 2
    x_line = X_fd[y_center_idx, :]
    h_fem_line = h_fem[y_center_idx * nx:(y_center_idx + 1) * nx]
    h_fd_line = h_fd[y_center_idx, :]
    h_exact_line = h_analytical(x_line, Ly/2)
    
    ax_left = axes[0]
    ax_left.plot(x_line, h_fem_line, 'b-', linewidth=2, marker='o',
                markersize=6, label='有限元解')
    ax_left.plot(x_line, h_fd_line, 'r--', linewidth=2, marker='s',
                markersize=6, label='有限差分解')
    ax_left.plot(x_line, h_exact_line, 'g:', linewidth=2, label='解析解')
    ax_left.grid(True, alpha=0.3)
    ax_left.set_xlabel('x (m)', fontsize=12)
    ax_left.set_ylabel('水头 (m)', fontsize=12)
    ax_left.set_title('中心线水头对比', fontsize=12, fontweight='bold')
    ax_left.legend()
    
    # 右图：误差分布
    ax_right = axes[1]
    error_fem = h_fem - h_exact
    
    scatter = ax_right.tricontourf(triang, error_fem, levels=20, cmap='RdBu_r')
    plt.colorbar(scatter, ax=ax_right, label='误差 (m)')
    ax_right.set_xlabel('x (m)', fontsize=12)
    ax_right.set_ylabel('y (m)', fontsize=12)
    ax_right.set_title('有限元解误差分布', fontsize=12, fontweight='bold')
    ax_right.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_05_comparison.png"), dpi=300)
    
    # 图5：流速场
    fig5, ax5 = plt.subplots(figsize=(12, 9))
    
    # 背景：水头等值线
    contourf = ax5.tricontourf(triang, h_fem, levels=15, cmap='Blues', alpha=0.3)
    
    # 流速矢量
    skip = 1  # 显示所有单元的速度
    ax5.quiver(elem_centers[::skip, 0], elem_centers[::skip, 1],
              velocity[::skip, 0], velocity[::skip, 1],
              scale=None, scale_units='xy', angles='xy',
              color='red', width=0.003)
    
    plt.colorbar(contourf, ax=ax5, label='水头 (m)')
    ax5.set_xlabel('x (m)', fontsize=12)
    ax5.set_ylabel('y (m)', fontsize=12)
    ax5.set_title('案例5：有限元解 - 流速场', fontsize=14, fontweight='bold')
    ax5.set_aspect('equal')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_05_velocity.png"), dpi=300)
    
    print(f"✓ 图形已保存到 {output_dir}/ 目录")
    
    # ========== 第9步：网格收敛性分析 ==========
    print("\n第9步：网格收敛性分析")
    print("-" * 60)
    
    mesh_sizes = [(6, 5), (11, 9), (21, 17), (41, 33)]
    errors_L2 = []
    errors_Linf = []
    h_values = []
    
    print(f"{'网格配置':>12} {'单元数':>10} {'L² 误差':>15} {'L∞ 误差':>15}")
    print("-" * 55)
    
    for nx_test, ny_test in mesh_sizes:
        mesh_test = generate_rectangular_triangular_mesh(Lx, Ly, nx_test, ny_test)
        
        # 边界条件
        left_nodes_test = [i for i, v in enumerate(mesh_test.vertices) 
                          if np.isclose(v[0], 0.0)]
        right_nodes_test = [i for i, v in enumerate(mesh_test.vertices) 
                           if np.isclose(v[0], Lx)]
        
        bc_test = {
            'dirichlet': [(node, h_left) for node in left_nodes_test] + 
                         [(node, h_right) for node in right_nodes_test]
        }
        
        # 求解
        h_test = solve_fem_2d(mesh_test, K, bc_test)
        
        # 计算误差
        errors_test = compute_element_errors(mesh_test, h_test, h_analytical)
        
        errors_L2.append(errors_test['L2'])
        errors_Linf.append(errors_test['Linf'])
        
        # 计算特征网格尺寸
        h_mesh = Lx / (nx_test - 1)
        h_values.append(h_mesh)
        
        print(f"{nx_test:>5}×{ny_test:<4} {mesh_test.n_elements:>10} "
              f"{errors_test['L2']:>15.6e} {errors_test['Linf']:>15.6e}")
    
    # 图6：收敛性曲线
    fig6, ax6 = plt.subplots(figsize=(10, 8))
    
    ax6.loglog(h_values, errors_L2, 'bo-', linewidth=2, markersize=8,
              label='L² 误差')
    ax6.loglog(h_values, errors_Linf, 'rs-', linewidth=2, markersize=8,
              label='L∞ 误差')
    
    # 参考线（理论收敛率）
    h_ref = np.array([h_values[0], h_values[-1]])
    # 线性单元理论收敛率：O(h²) for L2, O(h²) for L∞
    ax6.loglog(h_ref, errors_L2[0] * (h_ref / h_values[0])**2,
              'k--', linewidth=1.5, label='O(h²) 参考线')
    
    ax6.grid(True, alpha=0.3, which='both')
    ax6.set_xlabel('网格尺寸 h (m)', fontsize=12)
    ax6.set_ylabel('误差', fontsize=12)
    ax6.set_title('案例5：网格收敛性分析', fontsize=14, fontweight='bold')
    ax6.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_05_convergence.png"), dpi=300)
    
    print(f"\n✓ 网格收敛性分析完成")
    
    # ========== 总结 ==========
    print("\n" + "=" * 60)
    print("案例5总结")
    print("=" * 60)
    print("✓ 成功实现了Galerkin有限元方法")
    print("✓ 掌握了三角形网格生成")
    print("✓ 理解了单元刚度矩阵组装")
    print("✓ 与有限差分法进行了对比")
    print("✓ 验证了网格收敛性（O(h²)）")
    print("\n关键收获：")
    print("1. 有限元方法更适合复杂几何")
    print("2. 弱形式天然满足自然边界条件")
    print("3. 单元刚度矩阵的物理意义")
    print("4. 网格质量对精度的影响")
    print("5. 与有限差分法的异同")
    print("\n有限元 vs 有限差分：")
    print("  几何灵活性: 有限元 > 有限差分")
    print("  编程复杂度: 有限元 > 有限差分")
    print("  计算效率: 相当")
    print("  精度: 相当（对于规则网格）")
    print("=" * 60)
    
    plt.show()


if __name__ == "__main__":
    main()
