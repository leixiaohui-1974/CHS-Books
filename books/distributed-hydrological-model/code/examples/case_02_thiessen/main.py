"""
案例2：Thiessen多边形降雨插值
============================

演示Thiessen多边形法计算流域面雨量

作者: CHS-Books项目组
日期: 2025-11-02
"""

import sys
sys.path.insert(0, '../../..')

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.spatial import Voronoi, voronoi_plot_2d

from code.core.interpolation import (
    thiessen_polygon, thiessen_weights, calculate_areal_rainfall
)
from code.core.interpolation.idw import inverse_distance_weighting

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建输出目录
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)


def generate_station_data(n_stations=5, basin_size=20):
    """
    生成模拟的雨量站数据
    
    Parameters
    ----------
    n_stations : int
        站点数量
    basin_size : float
        流域大小 (km)
        
    Returns
    -------
    stations_xy : ndarray
        站点坐标
    rainfall : ndarray
        各站点降雨量
    """
    np.random.seed(42)
    
    # 生成站点坐标（均匀分布）
    if n_stations == 3:
        # 三角形布局
        stations_xy = np.array([
            [5, 5],
            [15, 5],
            [10, 15]
        ])
    elif n_stations == 5:
        # 五点布局（四角+中心）
        stations_xy = np.array([
            [3, 3],
            [17, 3],
            [3, 17],
            [17, 17],
            [10, 10]
        ])
    elif n_stations == 8:
        # 8点均匀布局
        stations_xy = np.array([
            [3, 3], [10, 3], [17, 3],
            [3, 10], [17, 10],
            [3, 17], [10, 17], [17, 17]
        ])
    else:
        # 随机布局
        stations_xy = np.random.rand(n_stations, 2) * basin_size
    
    # 生成降雨量（模拟一场暴雨）
    # 假设降雨中心在(12, 12)，呈高斯分布
    center = np.array([12, 12])
    distances = np.sqrt(np.sum((stations_xy - center) ** 2, axis=1))
    
    # 基础降雨 + 距离衰减
    base_rainfall = 50  # mm
    rainfall = base_rainfall - distances * 1.5 + np.random.randn(n_stations) * 3
    rainfall = np.maximum(rainfall, 20)  # 最小20mm
    
    return stations_xy, rainfall


def plot_thiessen_rainfall(stations_xy, rainfall, basin_size=20, save_path=None):
    """绘制Thiessen多边形降雨图"""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 构建Voronoi图
    vor = Voronoi(stations_xy)
    
    # 绘制Voronoi图
    voronoi_plot_2d(vor, ax=ax, show_vertices=False, 
                   line_colors='blue', line_width=2, 
                   line_alpha=0.8, point_size=0)
    
    # 绘制站点（按降雨量大小着色）
    scatter = ax.scatter(stations_xy[:, 0], stations_xy[:, 1],
                        c=rainfall, s=400, cmap='RdYlBu_r',
                        edgecolors='black', linewidths=3, zorder=5,
                        vmin=rainfall.min(), vmax=rainfall.max())
    
    # 标注站点编号和降雨量
    for i, (xy, r) in enumerate(zip(stations_xy, rainfall)):
        ax.text(xy[0], xy[1], f'S{i+1}\n{r:.1f}mm',
               ha='center', va='center', fontsize=10,
               fontweight='bold', color='white',
               bbox=dict(boxstyle='round', facecolor='black', alpha=0.6))
    
    # 流域边界
    ax.plot([0, basin_size, basin_size, 0, 0],
           [0, 0, basin_size, basin_size, 0],
           'k-', linewidth=3, label='流域边界')
    
    # 颜色条
    cbar = plt.colorbar(scatter, ax=ax, label='降雨量 (mm)')
    cbar.ax.tick_params(labelsize=11)
    
    ax.set_xlabel('X坐标 (km)', fontsize=13)
    ax.set_ylabel('Y坐标 (km)', fontsize=13)
    ax.set_title('Thiessen多边形降雨分布', fontsize=15, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-1, basin_size + 1)
    ax.set_ylim(-1, basin_size + 1)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def compare_methods(stations_xy, rainfall, basin_size=20, save_path=None):
    """对比不同插值方法"""
    # 创建网格
    x = np.linspace(0, basin_size, 50)
    y = np.linspace(0, basin_size, 50)
    grid_x, grid_y = np.meshgrid(x, y)
    
    # 1. Thiessen方法（简化：使用最近邻）
    target_points = np.column_stack([grid_x.ravel(), grid_y.ravel()])
    thiessen_result = np.zeros(len(target_points))
    for i, point in enumerate(target_points):
        _, nearest_idx = thiessen_weights(stations_xy, point)
        thiessen_result[i] = rainfall[nearest_idx]
    thiessen_grid = thiessen_result.reshape(grid_x.shape)
    
    # 2. IDW方法
    idw_result = inverse_distance_weighting(stations_xy, rainfall, 
                                           target_points, power=2)
    idw_grid = idw_result.reshape(grid_x.shape)
    
    # 3. 算术平均
    arithmetic_mean = np.mean(rainfall)
    
    # 绘图
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Thiessen
    im1 = axes[0].contourf(grid_x, grid_y, thiessen_grid, 
                           levels=15, cmap='RdYlBu_r')
    axes[0].scatter(stations_xy[:, 0], stations_xy[:, 1], 
                   c='red', s=100, edgecolors='black', linewidths=2, zorder=5)
    axes[0].set_title(f'Thiessen多边形法\n面雨量: {np.mean(thiessen_grid):.1f} mm',
                     fontsize=13, fontweight='bold')
    axes[0].set_xlabel('X (km)', fontsize=11)
    axes[0].set_ylabel('Y (km)', fontsize=11)
    axes[0].set_aspect('equal')
    plt.colorbar(im1, ax=axes[0], label='降雨量 (mm)')
    
    # IDW
    im2 = axes[1].contourf(grid_x, grid_y, idw_grid, 
                           levels=15, cmap='RdYlBu_r')
    axes[1].scatter(stations_xy[:, 0], stations_xy[:, 1], 
                   c='red', s=100, edgecolors='black', linewidths=2, zorder=5)
    axes[1].set_title(f'IDW方法 (power=2)\n面雨量: {np.mean(idw_grid):.1f} mm',
                     fontsize=13, fontweight='bold')
    axes[1].set_xlabel('X (km)', fontsize=11)
    axes[1].set_aspect('equal')
    plt.colorbar(im2, ax=axes[1], label='降雨量 (mm)')
    
    # 对比柱状图
    methods = ['算术平均', 'Thiessen', 'IDW']
    values = [arithmetic_mean, np.mean(thiessen_grid), np.mean(idw_grid)]
    colors = ['skyblue', 'orange', 'lightgreen']
    
    bars = axes[2].bar(methods, values, color=colors, edgecolor='black', linewidth=2)
    axes[2].set_ylabel('流域平均降雨量 (mm)', fontsize=12)
    axes[2].set_title('不同方法对比', fontsize=13, fontweight='bold')
    axes[2].grid(True, alpha=0.3, axis='y')
    
    # 标注数值
    for bar, val in zip(bars, values):
        height = bar.get_height()
        axes[2].text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f} mm',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig, values


def sensitivity_to_station_number(basin_size=20, save_path=None):
    """站点数量敏感性分析"""
    station_numbers = [3, 5, 8, 10, 15]
    thiessen_means = []
    arithmetic_means = []
    idw_means = []
    
    for n in station_numbers:
        stations_xy, rainfall = generate_station_data(n, basin_size)
        
        # 算术平均
        arithmetic_means.append(np.mean(rainfall))
        
        # Thiessen（简化计算）
        thiessen_means.append(calculate_areal_rainfall(
            stations_xy, rainfall, method='thiessen'
        ))
        
        # IDW
        grid_points = np.random.rand(1000, 2) * basin_size
        idw_result = inverse_distance_weighting(
            stations_xy, rainfall, grid_points, power=2
        )
        idw_means.append(np.mean(idw_result))
    
    # 绘图
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.plot(station_numbers, arithmetic_means, 'o-', 
           linewidth=2.5, markersize=10, label='算术平均', color='blue')
    ax.plot(station_numbers, thiessen_means, 's-', 
           linewidth=2.5, markersize=10, label='Thiessen', color='orange')
    ax.plot(station_numbers, idw_means, '^-', 
           linewidth=2.5, markersize=10, label='IDW', color='green')
    
    ax.set_xlabel('站点数量', fontsize=13)
    ax.set_ylabel('流域平均降雨量 (mm)', fontsize=13)
    ax.set_title('站点数量对面雨量计算的影响', fontsize=15, fontweight='bold')
    ax.legend(fontsize=12, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(station_numbers)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    return fig


def main():
    """主函数"""
    print("=" * 70)
    print("案例2：Thiessen多边形降雨插值")
    print("=" * 70)
    print()
    
    basin_size = 20  # km
    
    # 1. 生成站点数据
    print("1. 生成雨量站数据...")
    stations_xy, rainfall = generate_station_data(n_stations=5, basin_size=basin_size)
    
    print(f"   站点数量: {len(stations_xy)}")
    print(f"   流域大小: {basin_size} × {basin_size} km²")
    print()
    print("   站点信息:")
    for i, (xy, r) in enumerate(zip(stations_xy, rainfall)):
        print(f"     站点{i+1}: 坐标({xy[0]:.1f}, {xy[1]:.1f}), 降雨量{r:.1f} mm")
    print()
    
    # 2. 计算面雨量
    print("2. 计算流域面雨量...")
    
    # 算术平均
    arithmetic_mean = np.mean(rainfall)
    print(f"   算术平均法: {arithmetic_mean:.2f} mm")
    
    # Thiessen多边形法
    vor, thiessen_mean = thiessen_polygon(stations_xy, rainfall)
    print(f"   Thiessen法: {thiessen_mean:.2f} mm")
    
    # 差异
    diff = abs(thiessen_mean - arithmetic_mean)
    print(f"   差异: {diff:.2f} mm ({diff/arithmetic_mean*100:.2f}%)")
    print()
    
    # 3. 绘制Thiessen多边形
    print("3. 绘制Thiessen多边形图...")
    fig1 = plot_thiessen_rainfall(stations_xy, rainfall, basin_size,
                                  save_path=output_dir / 'thiessen_polygon.png')
    plt.close(fig1)
    
    # 4. 对比不同方法
    print("4. 对比不同插值方法...")
    fig2, method_values = compare_methods(stations_xy, rainfall, basin_size,
                                         save_path=output_dir / 'methods_comparison.png')
    plt.close(fig2)
    
    print(f"   算术平均: {method_values[0]:.2f} mm")
    print(f"   Thiessen: {method_values[1]:.2f} mm")
    print(f"   IDW: {method_values[2]:.2f} mm")
    print()
    
    # 5. 站点数量敏感性分析
    print("5. 站点数量敏感性分析...")
    fig3 = sensitivity_to_station_number(basin_size,
                                        save_path=output_dir / 'sensitivity_stations.png')
    plt.close(fig3)
    print("   分析完成")
    print()
    
    # 6. 总结
    print("=" * 70)
    print("分析完成！")
    print("=" * 70)
    print()
    print("生成的文件:")
    print("  - outputs/thiessen_polygon.png       : Thiessen多边形图")
    print("  - outputs/methods_comparison.png     : 方法对比图")
    print("  - outputs/sensitivity_stations.png   : 站点数量敏感性")
    print()
    print("关键发现:")
    print(f"  1. Thiessen法与算术平均法差异: {diff:.2f} mm ({diff/arithmetic_mean*100:.2f}%)")
    print(f"  2. 站点数量影响显著，建议至少5个站点")
    print(f"  3. Thiessen法适合站点分布均匀的情况")
    print(f"  4. IDW法结果更平滑，但计算略复杂")
    print()


if __name__ == '__main__':
    main()
