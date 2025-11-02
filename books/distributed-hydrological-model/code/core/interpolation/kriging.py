"""
克里金插值 (Kriging)
==================

Ordinary Kriging - 普通克里金插值
"""

import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import minimize


def variogram(distances, semivariances, model='spherical', 
             nugget=0, sill=None, range_param=None):
    """
    变异函数模型
    
    Parameters
    ----------
    distances : array_like
        距离数组
    semivariances : array_like
        半方差数组
    model : str
        模型类型 ('spherical', 'exponential', 'gaussian')
    nugget : float
        块金效应
    sill : float
        基台值
    range_param : float
        变程
        
    Returns
    -------
    fitted_params : dict
        拟合的参数
    """
    # 简化实现：返回理论参数
    if sill is None:
        sill = np.max(semivariances)
    if range_param is None:
        range_param = np.max(distances) / 3
    
    return {
        'model': model,
        'nugget': nugget,
        'sill': sill,
        'range': range_param
    }


def spherical_variogram(h, nugget, sill, range_param):
    """
    球状变异函数模型
    
    γ(h) = nugget + (sill - nugget) * [1.5*h/a - 0.5*(h/a)³]  for h <= a
    γ(h) = sill                                                for h > a
    
    Parameters
    ----------
    h : float or ndarray
        距离
    nugget : float
        块金效应
    sill : float
        基台值
    range_param : float
        变程
        
    Returns
    -------
    gamma : float or ndarray
        半方差值
    """
    h = np.asarray(h)
    gamma = np.zeros_like(h, dtype=float)
    
    # h <= range
    mask1 = h <= range_param
    if np.any(mask1):
        ratio = h[mask1] / range_param
        gamma[mask1] = nugget + (sill - nugget) * (1.5 * ratio - 0.5 * ratio**3)
    
    # h > range
    mask2 = h > range_param
    if np.any(mask2):
        gamma[mask2] = sill
    
    return gamma


def ordinary_kriging(stations_xy, station_values, target_points,
                    variogram_params=None):
    """
    普通克里金插值
    
    Parameters
    ----------
    stations_xy : array_like, shape (n, 2)
        站点坐标
    station_values : array_like, shape (n,)
        站点观测值
    target_points : array_like, shape (m, 2)
        目标点坐标
    variogram_params : dict, optional
        变异函数参数，包含 'nugget', 'sill', 'range', 'model'
        
    Returns
    -------
    interpolated : ndarray, shape (m,)
        插值结果
    variances : ndarray, shape (m,)
        插值方差（不确定性）
        
    Examples
    --------
    >>> stations = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    >>> values = np.array([10, 20, 15, 25])
    >>> targets = np.array([[0.5, 0.5]])
    >>> result, var = ordinary_kriging(stations, values, targets)
    >>> print(f"插值结果: {result[0]:.2f}, 方差: {var[0]:.2f}")
    """
    stations_xy = np.asarray(stations_xy)
    station_values = np.asarray(station_values)
    target_points = np.asarray(target_points)
    
    if target_points.ndim == 1:
        target_points = target_points.reshape(1, -1)
    
    n_stations = len(stations_xy)
    n_targets = len(target_points)
    
    # 默认变异函数参数
    if variogram_params is None:
        # 计算站点间距离
        distances = cdist(stations_xy, stations_xy)
        max_dist = np.max(distances)
        semivar = np.var(station_values)
        
        variogram_params = {
            'model': 'spherical',
            'nugget': 0.0,
            'sill': semivar,
            'range': max_dist / 3
        }
    
    # 构建站点间的半方差矩阵
    distances_stations = cdist(stations_xy, stations_xy)
    gamma_matrix = spherical_variogram(distances_stations, 
                                      variogram_params['nugget'],
                                      variogram_params['sill'],
                                      variogram_params['range'])
    
    # 构建克里金方程组矩阵 (n+1)×(n+1)
    K = np.zeros((n_stations + 1, n_stations + 1))
    K[:n_stations, :n_stations] = gamma_matrix
    K[n_stations, :n_stations] = 1
    K[:n_stations, n_stations] = 1
    K[n_stations, n_stations] = 0
    
    # 插值
    interpolated = np.zeros(n_targets)
    variances = np.zeros(n_targets)
    
    for i, target in enumerate(target_points):
        # 计算目标点到各站点的距离
        distances_target = np.sqrt(np.sum((stations_xy - target) ** 2, axis=1))
        
        # 计算目标点的半方差向量
        gamma_vector = spherical_variogram(distances_target,
                                          variogram_params['nugget'],
                                          variogram_params['sill'],
                                          variogram_params['range'])
        
        # 构建右侧向量
        b = np.zeros(n_stations + 1)
        b[:n_stations] = gamma_vector
        b[n_stations] = 1
        
        # 求解克里金方程组
        try:
            weights = np.linalg.solve(K, b)
            
            # 插值
            interpolated[i] = np.sum(weights[:n_stations] * station_values)
            
            # 插值方差
            variances[i] = np.sum(weights[:n_stations] * gamma_vector) + weights[n_stations]
        except np.linalg.LinAlgError:
            # 矩阵奇异，使用简单平均
            interpolated[i] = np.mean(station_values)
            variances[i] = np.var(station_values)
    
    return interpolated, variances


def experimental_variogram(stations_xy, station_values, n_lags=10):
    """
    计算实验变异函数
    
    Parameters
    ----------
    stations_xy : array_like
        站点坐标
    station_values : array_like
        站点观测值
    n_lags : int
        滞后数
        
    Returns
    -------
    lag_distances : ndarray
        滞后距离
    semivariances : ndarray
        半方差
    """
    stations_xy = np.asarray(stations_xy)
    station_values = np.asarray(station_values)
    
    # 计算所有站点对之间的距离和半方差
    n = len(stations_xy)
    distances = []
    semivar = []
    
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt(np.sum((stations_xy[i] - stations_xy[j]) ** 2))
            semi = 0.5 * (station_values[i] - station_values[j]) ** 2
            distances.append(dist)
            semivar.append(semi)
    
    distances = np.array(distances)
    semivar = np.array(semivar)
    
    # 分箱统计
    max_dist = np.max(distances)
    lag_width = max_dist / n_lags
    
    lag_distances = []
    semivariances = []
    
    for i in range(n_lags):
        lag_min = i * lag_width
        lag_max = (i + 1) * lag_width
        
        mask = (distances >= lag_min) & (distances < lag_max)
        
        if np.sum(mask) > 0:
            lag_distances.append((lag_min + lag_max) / 2)
            semivariances.append(np.mean(semivar[mask]))
    
    return np.array(lag_distances), np.array(semivariances)
