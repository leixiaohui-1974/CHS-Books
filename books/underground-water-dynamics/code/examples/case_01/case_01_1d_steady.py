"""
案例1：一维稳态地下水流动
===========================

学习目标：
1. 理解达西定律和一维稳态渗流方程
2. 掌握有限差分法离散
3. 学习边界条件的处理
4. 进行手工计算验证

问题描述：
一个一维承压含水层，长度L=1000m，水力传导度K=10 m/day。
左边界水头h0=20m，右边界水头hL=10m。
求解稳态水头分布。

理论基础：
一维稳态渗流方程：
    d/dx(K * dh/dx) = 0

对于均质含水层（K为常数）：
    d²h/dx² = 0

解析解：
    h(x) = h0 + (hL - h0) * x / L
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('../../..'))

from gwflow.solvers.steady_state import solve_1d_steady_gw
from gwflow.grid.structured import create_1d_grid
from gwflow.visualization.plots import plot_1d_head, plot_comparison


def analytical_solution(x: np.ndarray, h0: float, hL: float, L: float) -> np.ndarray:
    """
    一维稳态流动的解析解（线性分布）
    
    参数：
        x: 位置坐标
        h0: 左边界水头
        hL: 右边界水头
        L: 含水层长度
    
    返回：
        h: 解析解
    """
    return h0 + (hL - h0) * x / L


def main():
    """主函数"""
    print("=" * 60)
    print("案例1：一维稳态地下水流动")
    print("=" * 60)
    
    # ========== 第1步：定义问题参数 ==========
    print("\n第1步：定义问题参数")
    print("-" * 60)
    
    K = 10.0      # 水力传导度 [m/day]
    L = 1000.0    # 含水层长度 [m]
    h0 = 20.0     # 左边界水头 [m]
    hL = 10.0     # 右边界水头 [m]
    nx = 51       # 网格数量
    
    print(f"水力传导度 K = {K} m/day")
    print(f"含水层长度 L = {L} m")
    print(f"左边界水头 h0 = {h0} m")
    print(f"右边界水头 hL = {hL} m")
    print(f"网格数量 nx = {nx}")
    
    # ========== 第2步：创建网格 ==========
    print("\n第2步：创建计算网格")
    print("-" * 60)
    
    x, dx = create_1d_grid(L, nx)
    
    print(f"网格间距 dx = {dx:.2f} m")
    print(f"网格节点数 = {len(x)}")
    
    # ========== 第3步：手工计算（解析解） ==========
    print("\n第3步：手工计算（解析解）")
    print("-" * 60)
    
    h_analytical = analytical_solution(x, h0, hL, L)
    
    print("解析解公式：h(x) = h0 + (hL - h0) * x / L")
    print(f"x=0处水头（理论）：{h_analytical[0]:.4f} m")
    print(f"x=L处水头（理论）：{h_analytical[-1]:.4f} m")
    print(f"x=L/2处水头（理论）：{h_analytical[nx//2]:.4f} m")
    
    # ========== 第4步：数值求解 ==========
    print("\n第4步：数值求解（有限差分法）")
    print("-" * 60)
    
    h_numerical = solve_1d_steady_gw(K, L, h0, hL, nx)
    
    print(f"x=0处水头（数值）：{h_numerical[0]:.4f} m")
    print(f"x=L处水头（数值）：{h_numerical[-1]:.4f} m")
    print(f"x=L/2处水头（数值）：{h_numerical[nx//2]:.4f} m")
    
    # ========== 第5步：误差分析 ==========
    print("\n第5步：误差分析")
    print("-" * 60)
    
    error = np.abs(h_numerical - h_analytical)
    rmse = np.sqrt(np.mean(error**2))
    max_error = np.max(error)
    
    print(f"均方根误差 RMSE = {rmse:.6e} m")
    print(f"最大误差 = {max_error:.6e} m")
    print(f"相对误差 = {max_error / (h0 - hL) * 100:.6f} %")
    
    if rmse < 1e-10:
        print("✓ 数值解与解析解高度吻合！")
    
    # ========== 第6步：计算流速（达西速度） ==========
    print("\n第6步：计算达西速度")
    print("-" * 60)
    
    # 使用中心差分计算梯度
    dh_dx = np.gradient(h_numerical, dx)
    
    # 达西定律：v = -K * dh/dx
    v = -K * dh_dx
    
    print(f"平均流速 = {np.mean(v):.6f} m/day")
    print(f"理论流速（均质层）= {-K * (hL - h0) / L:.6f} m/day")
    
    # ========== 第7步：可视化 ==========
    print("\n第7步：可视化结果")
    print("-" * 60)
    
    # 创建输出目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 图1：数值解与解析解对比
    fig1 = plot_comparison(
        x, h_numerical, h_analytical,
        title="案例1：一维稳态地下水流动 - 数值解与解析解对比",
        save_path=os.path.join(output_dir, "case_01_comparison.png")
    )
    
    # 图2：流速分布
    fig2, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, v, 'g-', linewidth=2, marker='s', markersize=4, markevery=5)
    ax.axhline(y=np.mean(v), color='r', linestyle='--', label='平均流速')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('距离 (m)', fontsize=12)
    ax.set_ylabel('达西速度 (m/day)', fontsize=12)
    ax.set_title('案例1：达西速度分布', fontsize=14, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_01_velocity.png"), dpi=300)
    
    print(f"✓ 图形已保存到 {output_dir}/ 目录")
    
    # ========== 第8步：网格收敛性测试 ==========
    print("\n第8步：网格收敛性测试")
    print("-" * 60)
    
    grid_sizes = [11, 21, 51, 101, 201]
    errors = []
    
    print(f"{'网格数':>10} {'网格间距(m)':>15} {'RMSE':>15}")
    print("-" * 42)
    
    for n in grid_sizes:
        x_test, dx_test = create_1d_grid(L, n)
        h_num = solve_1d_steady_gw(K, L, h0, hL, n)
        h_ana = analytical_solution(x_test, h0, hL, L)
        rmse_test = np.sqrt(np.mean((h_num - h_ana)**2))
        errors.append(rmse_test)
        print(f"{n:>10} {dx_test:>15.2f} {rmse_test:>15.6e}")
    
    # 图3：收敛性分析
    fig3, ax = plt.subplots(figsize=(10, 6))
    ax.loglog([L/(n-1) for n in grid_sizes], errors, 'bo-', linewidth=2,
              markersize=8, label='RMSE')
    ax.grid(True, alpha=0.3, which='both')
    ax.set_xlabel('网格间距 dx (m)', fontsize=12)
    ax.set_ylabel('均方根误差 RMSE (m)', fontsize=12)
    ax.set_title('案例1：网格收敛性分析', fontsize=14, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_01_convergence.png"), dpi=300)
    
    print(f"\n✓ 网格收敛性分析完成")
    
    # ========== 总结 ==========
    print("\n" + "=" * 60)
    print("案例1总结")
    print("=" * 60)
    print("✓ 成功求解一维稳态地下水流动问题")
    print("✓ 数值解与解析解高度吻合")
    print("✓ 验证了有限差分法的正确性")
    print("✓ 完成了网格收敛性分析")
    print("\n关键收获：")
    print("1. 掌握了达西定律的应用")
    print("2. 理解了有限差分法的离散过程")
    print("3. 学会了边界条件的处理")
    print("4. 掌握了误差分析和网格收敛性检验")
    print("=" * 60)
    
    plt.show()


if __name__ == "__main__":
    main()
