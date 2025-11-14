"""
案例6：分布式产流网格模型

本案例演示如何构建分布式产流模型：
1. 将流域划分为规则网格
2. 对每个网格进行降雨插值
3. 对每个网格独立计算产流
4. 汇总得到流域总产流
5. 可视化空间分布

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap
import os
import sys
from pathlib import Path

# 添加code目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.interpolation import inverse_distance_weighting, ordinary_kriging
from core.runoff_generation import XinAnJiangModel, create_default_xaj_params

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def create_basin_grid(nx=20, ny=20, dx=100, dy=100):
    """
    创建流域网格
    
    参数:
    ----
    nx : int
        x方向网格数
    ny : int
        y方向网格数
    dx : float
        x方向网格大小(m)
    dy : float
        y方向网格大小(m)
    
    返回:
    ----
    grid_x : ndarray, shape (ny, nx)
        网格中心x坐标
    grid_y : ndarray, shape (ny, nx)
        网格中心y坐标
    """
    x = np.arange(0, nx * dx, dx) + dx / 2
    y = np.arange(0, ny * dy, dy) + dy / 2
    grid_x, grid_y = np.meshgrid(x, y)
    
    return grid_x, grid_y


def create_circular_basin(grid_x, grid_y, center_x=1000, center_y=1000, radius=800):
    """
    创建圆形流域边界
    
    参数:
    ----
    grid_x, grid_y : ndarray
        网格坐标
    center_x, center_y : float
        流域中心坐标
    radius : float
        流域半径(m)
    
    返回:
    ----
    mask : ndarray, bool
        True表示网格在流域内
    """
    distance = np.sqrt((grid_x - center_x)**2 + (grid_y - center_y)**2)
    mask = distance <= radius
    
    return mask


def generate_rainfall_stations(n_stations=5, x_range=(0, 2000), y_range=(0, 2000), seed=42):
    """
    生成雨量站位置和降雨数据
    
    参数:
    ----
    n_stations : int
        雨量站数量
    x_range, y_range : tuple
        坐标范围
    seed : int
        随机种子
    
    返回:
    ----
    stations_xy : ndarray, shape (n_stations, 2)
        站点坐标
    rainfall : ndarray, shape (n_stations, n_time)
        降雨时间序列(mm/h)
    """
    np.random.seed(seed)
    
    # 生成站点位置
    x = np.random.uniform(x_range[0], x_range[1], n_stations)
    y = np.random.uniform(y_range[0], y_range[1], n_stations)
    stations_xy = np.column_stack([x, y])
    
    # 生成24小时降雨过程（设计暴雨）
    n_time = 24
    time = np.arange(n_time)
    
    # 芝加哥雨型
    r = 0.4  # 峰值位置系数
    peak_time = int(n_time * r)
    
    # 基础雨型
    rainfall_pattern = np.zeros(n_time)
    for i in range(n_time):
        if i <= peak_time:
            rainfall_pattern[i] = (i / peak_time) ** 2
        else:
            rainfall_pattern[i] = np.exp(-0.3 * (i - peak_time))
    
    # 归一化并缩放到总雨量100mm
    rainfall_pattern = rainfall_pattern / rainfall_pattern.sum() * 100
    
    # 为每个站点添加空间变异性
    rainfall = np.zeros((n_stations, n_time))
    for i in range(n_stations):
        # 空间系数（0.8-1.2）
        spatial_factor = 0.8 + 0.4 * np.random.rand()
        rainfall[i, :] = rainfall_pattern * spatial_factor
    
    return stations_xy, rainfall


def interpolate_rainfall_to_grid(grid_x, grid_y, basin_mask, stations_xy, rainfall_t, method='idw'):
    """
    将站点降雨插值到网格
    
    参数:
    ----
    grid_x, grid_y : ndarray
        网格坐标
    basin_mask : ndarray, bool
        流域掩膜
    stations_xy : ndarray
        站点坐标
    rainfall_t : ndarray
        某时刻的站点降雨
    method : str
        插值方法 ('idw' 或 'kriging')
    
    返回:
    ----
    grid_rainfall : ndarray
        网格降雨(mm/h)，流域外为NaN
    """
    ny, nx = grid_x.shape
    grid_rainfall = np.full((ny, nx), np.nan)
    
    # 只对流域内的网格插值
    valid_points = []
    for i in range(ny):
        for j in range(nx):
            if basin_mask[i, j]:
                valid_points.append([grid_x[i, j], grid_y[i, j]])
    
    valid_points = np.array(valid_points)
    
    if len(valid_points) == 0:
        return grid_rainfall
    
    # 插值
    if method == 'idw':
        interpolated = inverse_distance_weighting(
            stations_xy, rainfall_t, valid_points, power=2.0
        )
    elif method == 'kriging':
        interpolated = ordinary_kriging(
            stations_xy, rainfall_t, valid_points,
            variogram_model='spherical', nugget=0.1, sill=1.0, range_param=800
        )
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # 填充回网格
    idx = 0
    for i in range(ny):
        for j in range(nx):
            if basin_mask[i, j]:
                grid_rainfall[i, j] = interpolated[idx]
                idx += 1
    
    return grid_rainfall


def create_parameter_field(grid_x, grid_y, basin_mask, param_name='WM', 
                           base_value=120, variability=0.2, seed=42):
    """
    创建参数空间分布场
    
    参数:
    ----
    grid_x, grid_y : ndarray
        网格坐标
    basin_mask : ndarray
        流域掩膜
    param_name : str
        参数名称
    base_value : float
        基础值
    variability : float
        空间变异系数
    seed : int
        随机种子
    
    返回:
    ----
    param_field : ndarray
        参数空间场
    """
    np.random.seed(seed)
    ny, nx = grid_x.shape
    param_field = np.full((ny, nx), np.nan)
    
    # 添加空间趋势（从上游到下游）
    trend = (grid_y - grid_y.min()) / (grid_y.max() - grid_y.min())
    
    # 添加随机扰动
    for i in range(ny):
        for j in range(nx):
            if basin_mask[i, j]:
                random_factor = 1.0 + variability * (2 * np.random.rand() - 1)
                trend_factor = 0.9 + 0.2 * trend[i, j]  # 0.9-1.1
                param_field[i, j] = base_value * random_factor * trend_factor
    
    return param_field


def run_distributed_runoff_model(grid_x, grid_y, basin_mask, rainfall_grid, 
                                  param_fields, model_type='xaj'):
    """
    运行分布式产流模型
    
    参数:
    ----
    grid_x, grid_y : ndarray
        网格坐标
    basin_mask : ndarray
        流域掩膜
    rainfall_grid : ndarray, shape (n_time, ny, nx)
        网格降雨时间序列
    param_fields : dict
        参数空间场字典
    model_type : str
        模型类型 ('xaj')
    
    返回:
    ----
    runoff_grid : ndarray, shape (n_time, ny, nx)
        网格产流(mm/h)
    total_runoff : ndarray, shape (n_time,)
        流域总产流(mm/h)
    """
    n_time, ny, nx = rainfall_grid.shape
    runoff_grid = np.zeros((n_time, ny, nx))
    
    # 为每个网格创建模型实例
    models = {}
    
    for i in range(ny):
        for j in range(nx):
            if basin_mask[i, j]:
                # 为该网格创建参数
                if model_type == 'xaj':
                    params = create_default_xaj_params()
                    # 更新为空间分布参数
                    for param_name, param_field in param_fields.items():
                        if not np.isnan(param_field[i, j]):
                            params[param_name] = param_field[i, j]
                    
                    models[(i, j)] = XinAnJiangModel(params)
                else:
                    raise ValueError(f"Unknown model type: {model_type}")
    
    # 时间循环
    for t in range(n_time):
        for i in range(ny):
            for j in range(nx):
                if basin_mask[i, j] and (i, j) in models:
                    P = rainfall_grid[t, i, j]
                    if not np.isnan(P):
                        # 运行模型（即使P=0也运行，因为模型有状态）
                        model = models[(i, j)]
                        results = model.run(np.array([P]), np.array([0.0]))
                        runoff_grid[t, i, j] = results['R'][0]  # 总径流深
    
    # 计算流域总产流（面积加权平均）
    n_valid_grids = np.sum(basin_mask)
    total_runoff = np.zeros(n_time)
    for t in range(n_time):
        valid_runoff = runoff_grid[t][basin_mask]
        # 过滤掉0值和nan值
        valid_runoff = valid_runoff[~np.isnan(valid_runoff)]
        total_runoff[t] = np.mean(valid_runoff) if len(valid_runoff) > 0 else 0.0
    
    return runoff_grid, total_runoff


def plot_basin_setup(grid_x, grid_y, basin_mask, stations_xy, save_path=None):
    """
    绘制流域设置图
    """
    fig, ax = plt.subplots(figsize=(10, 9))
    
    # 绘制网格
    ny, nx = grid_x.shape
    dx = grid_x[0, 1] - grid_x[0, 0]
    dy = grid_y[1, 0] - grid_y[0, 0]
    
    for i in range(ny):
        for j in range(nx):
            if basin_mask[i, j]:
                rect = Rectangle(
                    (grid_x[i, j] - dx/2, grid_y[i, j] - dy/2),
                    dx, dy, 
                    facecolor='lightblue', 
                    edgecolor='gray', 
                    linewidth=0.5, 
                    alpha=0.5
                )
                ax.add_patch(rect)
    
    # 绘制流域边界
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch
    # 简化：绘制圆形边界
    theta = np.linspace(0, 2*np.pi, 100)
    center_x, center_y = 1000, 1000
    radius = 800
    x_boundary = center_x + radius * np.cos(theta)
    y_boundary = center_y + radius * np.sin(theta)
    ax.plot(x_boundary, y_boundary, 'b-', linewidth=2, label='流域边界')
    
    # 绘制雨量站
    ax.scatter(stations_xy[:, 0], stations_xy[:, 1], 
               c='red', s=100, marker='^', 
               edgecolors='black', linewidths=1.5,
               label=f'雨量站 (n={len(stations_xy)})', 
               zorder=5)
    
    # 标注站点编号
    for idx, (x, y) in enumerate(stations_xy):
        ax.text(x, y + 50, f'S{idx+1}', 
                fontsize=9, ha='center', fontweight='bold')
    
    ax.set_xlabel('X坐标 (m)', fontsize=12)
    ax.set_ylabel('Y坐标 (m)', fontsize=12)
    ax.set_title('流域网格划分与雨量站分布', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    ax.set_xlim(-100, 2100)
    ax.set_ylim(-100, 2100)
    
    # 添加统计信息
    n_grids = np.sum(basin_mask)
    area = n_grids * dx * dy / 1e6  # km^2
    info_text = f'网格数: {n_grids}\n流域面积: {area:.2f} km²\n网格大小: {dx}m × {dy}m'
    ax.text(0.02, 0.98, info_text, 
            transform=ax.transAxes, 
            fontsize=10, 
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def plot_rainfall_interpolation(grid_x, grid_y, basin_mask, stations_xy, 
                                 rainfall_station, rainfall_grid, time_idx=10, 
                                 save_path=None):
    """
    绘制降雨插值结果
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # 创建自定义颜色映射
    colors = ['white', 'lightblue', 'blue', 'darkblue']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('rainfall', colors, N=n_bins)
    
    # 子图1: IDW插值
    ax = axes[0]
    rainfall_plot = np.where(basin_mask, rainfall_grid, np.nan)
    im = ax.contourf(grid_x, grid_y, rainfall_plot, 
                     levels=15, cmap=cmap, alpha=0.8)
    ax.scatter(stations_xy[:, 0], stations_xy[:, 1], 
               c=rainfall_station, s=150, cmap=cmap,
               edgecolors='black', linewidths=2, zorder=5)
    
    # 标注站点降雨值
    for idx, (x, y, r) in enumerate(zip(stations_xy[:, 0], stations_xy[:, 1], rainfall_station)):
        ax.text(x, y + 100, f'{r:.1f}', 
                fontsize=9, ha='center', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('降雨强度 (mm/h)', fontsize=11)
    ax.set_xlabel('X坐标 (m)', fontsize=12)
    ax.set_ylabel('Y坐标 (m)', fontsize=12)
    ax.set_title(f'IDW插值结果 (t={time_idx}h)', fontsize=13, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    # 子图2: 降雨统计
    ax = axes[1]
    valid_rainfall = rainfall_grid[~np.isnan(rainfall_grid)]
    ax.hist(valid_rainfall, bins=20, color='steelblue', alpha=0.7, edgecolor='black')
    ax.axvline(np.mean(valid_rainfall), color='red', linestyle='--', 
               linewidth=2, label=f'平均值: {np.mean(valid_rainfall):.2f} mm/h')
    ax.axvline(np.median(valid_rainfall), color='orange', linestyle='--', 
               linewidth=2, label=f'中位数: {np.median(valid_rainfall):.2f} mm/h')
    
    ax.set_xlabel('降雨强度 (mm/h)', fontsize=12)
    ax.set_ylabel('网格数量', fontsize=12)
    ax.set_title('网格降雨分布统计', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # 添加统计信息
    stats_text = f'最小值: {np.min(valid_rainfall):.2f} mm/h\n'
    stats_text += f'最大值: {np.max(valid_rainfall):.2f} mm/h\n'
    stats_text += f'标准差: {np.std(valid_rainfall):.2f} mm/h\n'
    stats_text += f'变异系数: {np.std(valid_rainfall)/np.mean(valid_rainfall):.2f}'
    ax.text(0.98, 0.98, stats_text, 
            transform=ax.transAxes, 
            fontsize=10, 
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def plot_runoff_spatial_distribution(grid_x, grid_y, basin_mask, runoff_grid, 
                                      time_idx=10, save_path=None):
    """
    绘制产流空间分布
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # 创建自定义颜色映射
    colors = ['white', 'yellow', 'orange', 'red', 'darkred']
    cmap = LinearSegmentedColormap.from_list('runoff', colors, N=100)
    
    # 子图1: 产流空间分布
    ax = axes[0]
    runoff_plot = np.where(basin_mask, runoff_grid, np.nan)
    im = ax.contourf(grid_x, grid_y, runoff_plot, 
                     levels=15, cmap=cmap, alpha=0.8)
    
    # 叠加网格
    ny, nx = grid_x.shape
    dx = grid_x[0, 1] - grid_x[0, 0]
    for i in range(ny):
        for j in range(nx):
            if basin_mask[i, j]:
                rect = Rectangle(
                    (grid_x[i, j] - dx/2, grid_y[i, j] - dx/2),
                    dx, dx, 
                    facecolor='none', 
                    edgecolor='gray', 
                    linewidth=0.3, 
                    alpha=0.5
                )
                ax.add_patch(rect)
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('产流深 (mm/h)', fontsize=11)
    ax.set_xlabel('X坐标 (m)', fontsize=12)
    ax.set_ylabel('Y坐标 (m)', fontsize=12)
    ax.set_title(f'产流空间分布 (t={time_idx}h)', fontsize=13, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    # 子图2: 产流统计
    ax = axes[1]
    valid_runoff = runoff_grid[~np.isnan(runoff_grid)]
    valid_runoff = valid_runoff[valid_runoff > 0]  # 只统计有产流的网格
    
    if len(valid_runoff) > 0:
        ax.hist(valid_runoff, bins=20, color='coral', alpha=0.7, edgecolor='black')
        ax.axvline(np.mean(valid_runoff), color='red', linestyle='--', 
                   linewidth=2, label=f'平均值: {np.mean(valid_runoff):.2f} mm/h')
        
        ax.set_xlabel('产流深 (mm/h)', fontsize=12)
        ax.set_ylabel('网格数量', fontsize=12)
        ax.set_title('网格产流分布统计', fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # 统计信息
        n_runoff_grids = len(valid_runoff)
        n_total_grids = np.sum(basin_mask)
        runoff_ratio = n_runoff_grids / n_total_grids * 100
        
        stats_text = f'产流网格数: {n_runoff_grids}/{n_total_grids} ({runoff_ratio:.1f}%)\n'
        stats_text += f'平均产流: {np.mean(valid_runoff):.2f} mm/h\n'
        stats_text += f'最大产流: {np.max(valid_runoff):.2f} mm/h\n'
        stats_text += f'标准差: {np.std(valid_runoff):.2f} mm/h'
        ax.text(0.98, 0.98, stats_text, 
                transform=ax.transAxes, 
                fontsize=10, 
                verticalalignment='top',
                horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    else:
        ax.text(0.5, 0.5, '该时刻无产流', 
                ha='center', va='center', 
                transform=ax.transAxes, 
                fontsize=14)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def plot_runoff_time_series(time, total_runoff, rainfall_mean, save_path=None):
    """
    绘制产流过程线
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # 子图1: 降雨过程
    ax = axes[0]
    ax.bar(time, rainfall_mean, color='steelblue', alpha=0.7, label='平均降雨')
    ax.set_ylabel('降雨强度 (mm/h)', fontsize=12)
    ax.set_title('流域平均降雨过程', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.invert_yaxis()  # 降雨倒置
    
    # 子图2: 产流过程
    ax = axes[1]
    ax.plot(time, total_runoff, 'ro-', linewidth=2, markersize=6, label='流域总产流')
    ax.fill_between(time, 0, total_runoff, alpha=0.3, color='red')
    
    # 标注峰值
    peak_idx = np.argmax(total_runoff)
    peak_runoff = total_runoff[peak_idx]
    peak_time = time[peak_idx]
    ax.plot(peak_time, peak_runoff, 'r*', markersize=15, zorder=5)
    ax.annotate(f'峰值: {peak_runoff:.2f} mm/h\n时间: {peak_time}h',
                xy=(peak_time, peak_runoff),
                xytext=(peak_time + 3, peak_runoff * 0.8),
                fontsize=10,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    ax.set_xlabel('时间 (h)', fontsize=12)
    ax.set_ylabel('产流深 (mm/h)', fontsize=12)
    ax.set_title('流域产流过程线', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # 累计产流
    cumulative_runoff = np.cumsum(total_runoff)
    cumulative_rainfall = np.cumsum(rainfall_mean)
    runoff_coefficient = cumulative_runoff[-1] / cumulative_rainfall[-1] if cumulative_rainfall[-1] > 0 else 0
    
    info_text = f'累计降雨: {cumulative_rainfall[-1]:.1f} mm\n'
    info_text += f'累计产流: {cumulative_runoff[-1]:.1f} mm\n'
    info_text += f'产流系数: {runoff_coefficient:.3f}'
    ax.text(0.02, 0.98, info_text, 
            transform=ax.transAxes, 
            fontsize=10, 
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    plt.close()


def main():
    """主函数"""
    print("=" * 70)
    print("案例6：分布式产流网格模型")
    print("=" * 70)
    
    # 创建输出目录
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 创建流域网格
    print("\n1. 创建流域网格...")
    nx, ny = 20, 20  # 20×20网格
    dx, dy = 100, 100  # 100m×100m
    grid_x, grid_y = create_basin_grid(nx, ny, dx, dy)
    basin_mask = create_circular_basin(grid_x, grid_y)
    
    n_grids = np.sum(basin_mask)
    area_km2 = n_grids * dx * dy / 1e6
    print(f"   网格数量: {n_grids}")
    print(f"   流域面积: {area_km2:.2f} km²")
    
    # 2. 生成雨量站数据
    print("\n2. 生成雨量站数据...")
    stations_xy, rainfall_stations = generate_rainfall_stations(n_stations=5)
    n_time = rainfall_stations.shape[1]
    print(f"   雨量站数量: {len(stations_xy)}")
    print(f"   时间步数: {n_time} 小时")
    
    # 绘制流域设置
    plot_basin_setup(grid_x, grid_y, basin_mask, stations_xy, 
                     save_path=f'{output_dir}/basin_setup.png')
    
    # 3. 降雨空间插值
    print("\n3. 进行降雨空间插值...")
    rainfall_grids = np.zeros((n_time, ny, nx))
    
    for t in range(n_time):
        rainfall_grids[t] = interpolate_rainfall_to_grid(
            grid_x, grid_y, basin_mask, 
            stations_xy, rainfall_stations[:, t], 
            method='idw'
        )
    
    # 绘制插值结果（峰值时刻）
    peak_time_idx = 10
    plot_rainfall_interpolation(
        grid_x, grid_y, basin_mask, stations_xy,
        rainfall_stations[:, peak_time_idx],
        rainfall_grids[peak_time_idx],
        time_idx=peak_time_idx,
        save_path=f'{output_dir}/rainfall_interpolation.png'
    )
    
    # 4. 创建参数空间场
    print("\n4. 创建参数空间分布...")
    param_fields = {
        'WM': create_parameter_field(grid_x, grid_y, basin_mask, 'WM', 120, 0.2),
        'B': create_parameter_field(grid_x, grid_y, basin_mask, 'B', 0.3, 0.15),
        'SM': create_parameter_field(grid_x, grid_y, basin_mask, 'SM', 30, 0.2)
    }
    print(f"   参数场数量: {len(param_fields)}")
    
    # 5. 运行分布式产流模型
    print("\n5. 运行分布式产流模型...")
    runoff_grids, total_runoff = run_distributed_runoff_model(
        grid_x, grid_y, basin_mask, 
        rainfall_grids, param_fields, 
        model_type='xaj'
    )
    print("   模拟完成！")
    
    # 6. 可视化结果
    print("\n6. 生成可视化图表...")
    
    # 产流空间分布（峰值时刻）
    plot_runoff_spatial_distribution(
        grid_x, grid_y, basin_mask, 
        runoff_grids[peak_time_idx],
        time_idx=peak_time_idx,
        save_path=f'{output_dir}/runoff_spatial.png'
    )
    
    # 产流时间过程
    rainfall_mean = np.array([np.nanmean(rainfall_grids[t, basin_mask]) 
                              for t in range(n_time)])
    time = np.arange(n_time)
    plot_runoff_time_series(
        time, total_runoff, rainfall_mean,
        save_path=f'{output_dir}/runoff_time_series.png'
    )
    
    # 7. 输出统计结果
    print("\n" + "=" * 70)
    print("模拟结果统计")
    print("=" * 70)
    
    cumulative_rainfall = np.sum(rainfall_mean)
    cumulative_runoff = np.sum(total_runoff)
    runoff_coefficient = cumulative_runoff / cumulative_rainfall if cumulative_rainfall > 0 else 0
    peak_runoff = np.max(total_runoff)
    peak_time = np.argmax(total_runoff)
    
    print(f"累计降雨: {cumulative_rainfall:.2f} mm")
    print(f"累计产流: {cumulative_runoff:.2f} mm")
    print(f"产流系数: {runoff_coefficient:.3f}")
    print(f"峰值产流: {peak_runoff:.2f} mm/h")
    print(f"峰现时间: {peak_time} h")
    print(f"流域面积: {area_km2:.2f} km²")
    print(f"网格数量: {n_grids}")
    
    print("\n所有图表已保存到 outputs/ 目录")
    print("=" * 70)


if __name__ == '__main__':
    main()
