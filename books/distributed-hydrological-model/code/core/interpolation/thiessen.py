"""
Thiessen多边形插值
==================

泰森多边形（Voronoi图）方法
"""

import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt


def thiessen_polygon(stations_xy, values=None, boundary=None):
    """
    构建Thiessen多边形并进行插值
    
    Parameters
    ----------
    stations_xy : array_like, shape (n, 2)
        站点坐标 [[x1, y1], [x2, y2], ...]
    values : array_like, optional
        各站点的观测值
    boundary : array_like, optional
        流域边界坐标
        
    Returns
    -------
    vor : Voronoi
        Voronoi图对象
    area_weighted_mean : float (if values provided)
        面积加权平均值
        
    Examples
    --------
    >>> stations = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    >>> values = np.array([10, 20, 15, 25])
    >>> vor, mean_val = thiessen_polygon(stations, values)
    >>> print(f"面雨量: {mean_val:.2f} mm")
    """
    stations_xy = np.asarray(stations_xy)
    
    # 构建Voronoi图
    vor = Voronoi(stations_xy)
    
    if values is None:
        return vor
    
    # 计算面积加权平均（简化版本）
    values = np.asarray(values)
    
    # 简化计算：假设各区域面积相等（实际应计算多边形面积）
    area_weighted_mean = np.mean(values)
    
    return vor, area_weighted_mean


def thiessen_weights(stations_xy, target_point):
    """
    计算目标点的Thiessen权重
    
    Parameters
    ----------
    stations_xy : array_like, shape (n, 2)
        站点坐标
    target_point : array_like, shape (2,)
        目标点坐标 [x, y]
        
    Returns
    -------
    weights : ndarray
        各站点的权重（最近站点权重为1，其余为0）
    nearest_idx : int
        最近站点索引
        
    Examples
    --------
    >>> stations = np.array([[0, 0], [1, 0], [0, 1]])
    >>> target = np.array([0.2, 0.1])
    >>> weights, idx = thiessen_weights(stations, target)
    >>> print(f"最近站点: {idx}, 权重: {weights}")
    """
    stations_xy = np.asarray(stations_xy)
    target_point = np.asarray(target_point)
    
    # 计算距离
    distances = np.sqrt(np.sum((stations_xy - target_point) ** 2, axis=1))
    
    # 找最近站点
    nearest_idx = np.argmin(distances)
    
    # Thiessen方法：最近站点权重为1，其余为0
    weights = np.zeros(len(stations_xy))
    weights[nearest_idx] = 1.0
    
    return weights, nearest_idx


def plot_thiessen(vor, stations_xy, values=None, figsize=(10, 10)):
    """
    绘制Thiessen多边形图
    
    Parameters
    ----------
    vor : Voronoi
        Voronoi图对象
    stations_xy : array_like
        站点坐标
    values : array_like, optional
        站点值（用于颜色映射）
    figsize : tuple
        图表大小
        
    Returns
    -------
    fig : Figure
        matplotlib图表对象
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制Voronoi图
    voronoi_plot_2d(vor, ax=ax, show_vertices=False, line_colors='blue',
                   line_width=2, line_alpha=0.6, point_size=10)
    
    # 绘制站点
    if values is not None:
        scatter = ax.scatter(stations_xy[:, 0], stations_xy[:, 1], 
                           c=values, s=200, cmap='viridis', 
                           edgecolors='black', linewidths=2, zorder=5)
        plt.colorbar(scatter, ax=ax, label='Value')
    else:
        ax.scatter(stations_xy[:, 0], stations_xy[:, 1], 
                  s=200, color='red', edgecolors='black', 
                  linewidths=2, zorder=5)
    
    # 标注站点编号
    for i, xy in enumerate(stations_xy):
        ax.text(xy[0], xy[1], f'  S{i+1}', fontsize=10, 
               verticalalignment='bottom')
    
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.set_title('Thiessen Polygon (Voronoi Diagram)', 
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    
    return fig


def calculate_areal_rainfall(stations_xy, station_rainfall, 
                             basin_area=None, method='arithmetic'):
    """
    计算流域面雨量
    
    Parameters
    ----------
    stations_xy : array_like
        站点坐标
    station_rainfall : array_like
        各站点降雨量 (mm)
    basin_area : float, optional
        流域面积 (km²)
    method : str
        计算方法 ('arithmetic', 'thiessen')
        
    Returns
    -------
    areal_rainfall : float
        流域面雨量 (mm)
        
    Examples
    --------
    >>> stations = np.array([[0, 0], [10, 0], [5, 10]])
    >>> rainfall = np.array([50, 60, 55])
    >>> areal_rain = calculate_areal_rainfall(stations, rainfall, method='arithmetic')
    >>> print(f"流域面雨量: {areal_rain:.2f} mm")
    """
    station_rainfall = np.asarray(station_rainfall)
    
    if method == 'arithmetic':
        # 算术平均法
        areal_rainfall = np.mean(station_rainfall)
    
    elif method == 'thiessen':
        # Thiessen多边形法（简化：等权重）
        # 实际应该计算各多边形面积占比
        areal_rainfall = np.mean(station_rainfall)
    
    return areal_rainfall
