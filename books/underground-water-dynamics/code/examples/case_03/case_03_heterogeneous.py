"""
案例3：非均质含水层模拟
=========================

学习目标：
1. 理解非均质性的表征方法
2. 掌握分区参数设置
3. 学习随机场生成方法
4. 分析非均质性对流场的影响
5. 可视化非均质参数场

问题描述：
一个矩形承压含水层，水力传导度空间变化。
比较均质和非均质情况下的流场差异。

场景：
1. 均质含水层（基准）
2. 分区非均质（透镜体）
3. 随机非均质（地质统计）

理论基础：
非均质含水层的二维稳态渗流方程：
    ∂/∂x(K(x,y) * ∂h/∂x) + ∂/∂y(K(x,y) * ∂h/∂y) = 0

其中K(x,y)是空间变化的水力传导度场。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import sys
import os

sys.path.insert(0, os.path.abspath('../../..'))

from gwflow.solvers.steady_state import solve_2d_steady_gw, compute_darcy_velocity
from gwflow.grid.structured import create_2d_grid
from gwflow.visualization.plots import plot_2d_head, plot_2d_velocity


def create_zoned_heterogeneous_K(X: np.ndarray, Y: np.ndarray, K_background: float,
                                  zones: list) -> np.ndarray:
    """
    创建分区非均质水力传导度场
    
    参数：
        X, Y: 网格坐标
        K_background: 背景水力传导度
        zones: 异常区列表，每个元素为字典:
               {'x_range': (x1, x2), 'y_range': (y1, y2), 'K': K_value}
    
    返回：
        K: 水力传导度场
    """
    ny, nx = X.shape
    K = K_background * np.ones((ny, nx))
    
    for zone in zones:
        x1, x2 = zone['x_range']
        y1, y2 = zone['y_range']
        K_zone = zone['K']
        
        # 找到在区域内的网格点
        mask = (X >= x1) & (X <= x2) & (Y >= y1) & (Y <= y2)
        K[mask] = K_zone
    
    return K


def create_random_field(X: np.ndarray, Y: np.ndarray, mean_K: float,
                       variance: float, correlation_length: float,
                       random_seed: int = 42) -> np.ndarray:
    """
    创建随机水力传导度场（对数正态分布）
    
    使用高斯随机场方法和指数协方差函数
    
    参数：
        X, Y: 网格坐标
        mean_K: 几何平均水力传导度
        variance: 对数方差
        correlation_length: 相关长度
        random_seed: 随机种子
    
    返回：
        K: 随机水力传导度场
    """
    from scipy.spatial.distance import cdist
    
    np.random.seed(random_seed)
    
    ny, nx = X.shape
    
    # 获取所有网格点坐标
    coords = np.column_stack([X.ravel(), Y.ravel()])
    n_points = len(coords)
    
    # 构建协方差矩阵（指数型）
    print("  正在生成协方差矩阵...")
    distances = cdist(coords, coords)
    C = variance * np.exp(-distances / correlation_length)
    
    # 添加小的对角项以确保正定性
    C += 1e-6 * np.eye(n_points)
    
    # Cholesky分解
    print("  正在进行Cholesky分解...")
    try:
        L = np.linalg.cholesky(C)
    except np.linalg.LinAlgError:
        print("  警告：Cholesky分解失败，使用特征值分解...")
        eigenvalues, eigenvectors = np.linalg.eigh(C)
        eigenvalues[eigenvalues < 0] = 0
        L = eigenvectors @ np.diag(np.sqrt(eigenvalues))
    
    # 生成标准正态随机数
    z = np.random.randn(n_points)
    
    # 生成相关的随机场（对数空间）
    log_K = np.log(mean_K) + L @ z
    
    # 转换回原空间
    K = np.exp(log_K).reshape((ny, nx))
    
    return K


def plot_K_field(X: np.ndarray, Y: np.ndarray, K: np.ndarray,
                title: str, save_path: str = None) -> plt.Figure:
    """绘制水力传导度场"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 使用对数尺度
    contourf = ax.contourf(X, Y, K, levels=20, cmap='YlOrRd')
    contour = ax.contour(X, Y, K, levels=10, colors='black',
                         linewidths=0.5, alpha=0.4)
    ax.clabel(contour, inline=True, fontsize=8, fmt='%.1f')
    
    cbar = plt.colorbar(contourf, ax=ax, label='水力传导度 K (m/day)')
    
    ax.set_xlabel('x (m)', fontsize=12)
    ax.set_ylabel('y (m)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300)
    
    return fig


def compare_scenarios(X: np.ndarray, Y: np.ndarray, K_scenarios: dict,
                     boundary_conditions: dict, dx: float, dy: float):
    """比较不同非均质场景"""
    
    results = {}
    
    for scenario_name, K in K_scenarios.items():
        print(f"\n正在求解场景: {scenario_name}")
        
        # 求解
        h = solve_2d_steady_gw(K, X[0, -1], Y[-1, 0],
                               X.shape[1], X.shape[0],
                               boundary_conditions)
        
        # 计算流速
        vx, vy = compute_darcy_velocity(h, K, dx, dy)
        
        # 统计信息
        results[scenario_name] = {
            'K': K,
            'h': h,
            'vx': vx,
            'vy': vy,
            'K_mean': K.mean(),
            'K_std': K.std(),
            'K_min': K.min(),
            'K_max': K.max(),
            'h_mean': h.mean(),
            'h_std': h.std()
        }
        
        print(f"  K范围: [{K.min():.2f}, {K.max():.2f}] m/day")
        print(f"  K平均值: {K.mean():.2f} m/day")
        print(f"  水头范围: [{h.min():.2f}, {h.max():.2f}] m")
    
    return results


def main():
    """主函数"""
    print("=" * 60)
    print("案例3：非均质含水层模拟")
    print("=" * 60)
    
    # ========== 第1步：定义问题参数 ==========
    print("\n第1步：定义问题参数")
    print("-" * 60)
    
    Lx = 1000.0    # x方向长度 [m]
    Ly = 800.0     # y方向长度 [m]
    nx = 51        # x方向网格数
    ny = 41        # y方向网格数
    
    K_background = 10.0  # 背景水力传导度
    
    print(f"区域尺寸：Lx = {Lx} m, Ly = {Ly} m")
    print(f"网格数量：nx = {nx}, ny = {ny}")
    print(f"背景水力传导度：K = {K_background} m/day")
    
    # ========== 第2步：创建网格 ==========
    print("\n第2步：创建二维计算网格")
    print("-" * 60)
    
    X, Y, dx, dy = create_2d_grid(Lx, Ly, nx, ny)
    
    print(f"网格间距：dx = {dx:.2f} m, dy = {dy:.2f} m")
    
    # ========== 第3步：定义边界条件 ==========
    print("\n第3步：定义边界条件")
    print("-" * 60)
    
    boundary_conditions = {
        'left': {'type': 'dirichlet', 'value': 20.0},
        'right': {'type': 'dirichlet', 'value': 10.0},
        'bottom': {'type': 'neumann', 'value': 0.0},
        'top': {'type': 'neumann', 'value': 0.0}
    }
    
    print("边界条件：左边h=20m，右边h=10m，上下无流")
    
    # ========== 第4步：场景1 - 均质含水层（基准） ==========
    print("\n第4步：场景1 - 均质含水层（基准）")
    print("-" * 60)
    
    K_homogeneous = K_background * np.ones((ny, nx))
    
    print(f"均质水力传导度：K = {K_background} m/day")
    
    # ========== 第5步：场景2 - 分区非均质（透镜体） ==========
    print("\n第5步：场景2 - 分区非均质（低渗透透镜体）")
    print("-" * 60)
    
    # 定义低渗透透镜体
    zones_low_k = [
        {
            'x_range': (300, 500),
            'y_range': (300, 500),
            'K': 1.0  # 低渗透区
        },
        {
            'x_range': (600, 800),
            'y_range': (200, 400),
            'K': 2.0  # 中等渗透区
        }
    ]
    
    K_zoned_low = create_zoned_heterogeneous_K(X, Y, K_background, zones_low_k)
    
    print("透镜体1: x=[300,500], y=[300,500], K=1.0 m/day")
    print("透镜体2: x=[600,800], y=[200,400], K=2.0 m/day")
    
    # ========== 第6步：场景3 - 分区非均质（高渗透通道） ==========
    print("\n第6步：场景3 - 分区非均质（高渗透通道）")
    print("-" * 60)
    
    # 定义高渗透通道
    zones_high_k = [
        {
            'x_range': (400, 600),
            'y_range': (350, 450),
            'K': 50.0  # 高渗透通道
        }
    ]
    
    K_zoned_high = create_zoned_heterogeneous_K(X, Y, K_background, zones_high_k)
    
    print("高渗透通道: x=[400,600], y=[350,450], K=50.0 m/day")
    
    # ========== 第7步：场景4 - 随机非均质 ==========
    print("\n第7步：场景4 - 随机非均质（地质统计）")
    print("-" * 60)
    
    mean_K = 10.0
    variance = 0.5  # 对数方差
    correlation_length = 200.0  # 相关长度
    
    print(f"几何平均K: {mean_K} m/day")
    print(f"对数方差: {variance}")
    print(f"相关长度: {correlation_length} m")
    
    # 注意：对于大网格，随机场生成可能很慢
    print("警告：随机场生成可能需要较长时间...")
    K_random = create_random_field(X, Y, mean_K, variance, correlation_length)
    
    print(f"✓ 随机场生成完成")
    print(f"  实际K范围: [{K_random.min():.2f}, {K_random.max():.2f}] m/day")
    print(f"  实际K平均: {K_random.mean():.2f} m/day")
    
    # ========== 第8步：比较所有场景 ==========
    print("\n第8步：求解所有场景")
    print("-" * 60)
    
    K_scenarios = {
        '场景1：均质': K_homogeneous,
        '场景2：低渗透透镜体': K_zoned_low,
        '场景3：高渗透通道': K_zoned_high,
        '场景4：随机场': K_random
    }
    
    results = compare_scenarios(X, Y, K_scenarios, boundary_conditions, dx, dy)
    
    # ========== 第9步：可视化水力传导度场 ==========
    print("\n第9步：可视化水力传导度场")
    print("-" * 60)
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 绘制所有K场
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.ravel()
    
    for idx, (name, K) in enumerate(K_scenarios.items()):
        ax = axes[idx]
        contourf = ax.contourf(X, Y, K, levels=20, cmap='YlOrRd')
        ax.set_xlabel('x (m)', fontsize=10)
        ax.set_ylabel('y (m)', fontsize=10)
        ax.set_title(name, fontsize=12, fontweight='bold')
        ax.set_aspect('equal')
        plt.colorbar(contourf, ax=ax, label='K (m/day)')
        
        # 标注透镜体位置
        if '透镜体' in name:
            for zone in (zones_low_k if '低渗透' in name else []):
                x1, x2 = zone['x_range']
                y1, y2 = zone['y_range']
                rect = Rectangle((x1, y1), x2-x1, y2-y1,
                               linewidth=2, edgecolor='blue',
                               facecolor='none', linestyle='--')
                ax.add_patch(rect)
        elif '通道' in name:
            for zone in zones_high_k:
                x1, x2 = zone['x_range']
                y1, y2 = zone['y_range']
                rect = Rectangle((x1, y1), x2-x1, y2-y1,
                               linewidth=2, edgecolor='red',
                               facecolor='none', linestyle='--')
                ax.add_patch(rect)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_03_K_fields.png"), dpi=300)
    
    # ========== 第10步：可视化水头分布 ==========
    print("\n第10步：可视化水头分布")
    print("-" * 60)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.ravel()
    
    for idx, (name, result) in enumerate(results.items()):
        ax = axes[idx]
        h = result['h']
        contourf = ax.contourf(X, Y, h, levels=20, cmap='viridis')
        contour = ax.contour(X, Y, h, levels=10, colors='black',
                           linewidths=0.5, alpha=0.4)
        ax.clabel(contour, inline=True, fontsize=8, fmt='%.1f')
        
        ax.set_xlabel('x (m)', fontsize=10)
        ax.set_ylabel('y (m)', fontsize=10)
        ax.set_title(f"{name} - 水头分布", fontsize=12, fontweight='bold')
        ax.set_aspect('equal')
        plt.colorbar(contourf, ax=ax, label='水头 (m)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_03_head_fields.png"), dpi=300)
    
    # ========== 第11步：对比分析 ==========
    print("\n第11步：对比分析")
    print("-" * 60)
    
    # 提取中心线数据
    y_center = ny // 2
    x_line = X[y_center, :]
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # 子图1：水头对比
    ax1 = axes[0]
    for name, result in results.items():
        h_line = result['h'][y_center, :]
        ax1.plot(x_line, h_line, linewidth=2, marker='o',
                markersize=3, markevery=5, label=name)
    
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('x (m)', fontsize=12)
    ax1.set_ylabel('水头 (m)', fontsize=12)
    ax1.set_title('案例3：不同场景中心线水头对比', fontsize=14, fontweight='bold')
    ax1.legend()
    
    # 子图2：K对比
    ax2 = axes[1]
    for name, result in results.items():
        K_line = result['K'][y_center, :]
        ax2.plot(x_line, K_line, linewidth=2, marker='s',
                markersize=3, markevery=5, label=name)
    
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('x (m)', fontsize=12)
    ax2.set_ylabel('K (m/day)', fontsize=12)
    ax2.set_title('案例3：不同场景中心线水力传导度对比', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.set_yscale('log')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_03_centerline_comparison.png"), dpi=300)
    
    # ========== 第12步：流线图 ==========
    print("\n第12步：绘制流线图")
    print("-" * 60)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.ravel()
    
    for idx, (name, result) in enumerate(results.items()):
        ax = axes[idx]
        h = result['h']
        K = result['K']
        
        # 背景：K场
        contourf = ax.contourf(X, Y, K, levels=20, cmap='YlOrRd', alpha=0.3)
        
        # 流线
        ax.contour(X, Y, h, levels=15, colors='blue', linewidths=1.5, alpha=0.8)
        
        ax.set_xlabel('x (m)', fontsize=10)
        ax.set_ylabel('y (m)', fontsize=10)
        ax.set_title(f"{name} - 流线图", fontsize=12, fontweight='bold')
        ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "case_03_streamlines.png"), dpi=300)
    
    print(f"✓ 图形已保存到 {output_dir}/ 目录")
    
    # ========== 第13步：统计分析 ==========
    print("\n第13步：统计分析")
    print("-" * 60)
    
    print(f"\n{'场景':<25} {'K均值':>10} {'K标准差':>10} {'水头标准差':>12}")
    print("-" * 60)
    for name, result in results.items():
        print(f"{name:<25} {result['K_mean']:>10.2f} {result['K_std']:>10.2f} {result['h_std']:>12.4f}")
    
    # 计算与均质场景的差异
    h_homo = results['场景1：均质']['h']
    
    print(f"\n与均质场景的水头差异（RMSE）:")
    print("-" * 60)
    for name, result in results.items():
        if name == '场景1：均质':
            continue
        rmse = np.sqrt(np.mean((result['h'] - h_homo)**2))
        max_diff = np.abs(result['h'] - h_homo).max()
        print(f"{name:<25} RMSE={rmse:>8.4f} m, 最大差异={max_diff:>8.4f} m")
    
    # ========== 总结 ==========
    print("\n" + "=" * 60)
    print("案例3总结")
    print("=" * 60)
    print("✓ 成功模拟了非均质含水层")
    print("✓ 比较了4种不同非均质场景")
    print("✓ 分析了非均质性对流场的影响")
    print("✓ 生成了随机场（地质统计方法）")
    print("\n关键发现：")
    print("1. 低渗透透镜体会导致流线绕行")
    print("2. 高渗透通道会吸引更多流量")
    print("3. 随机非均质导致水头分布不规则")
    print("4. 非均质性显著影响流场模式")
    print("=" * 60)
    
    plt.show()


if __name__ == "__main__":
    main()
