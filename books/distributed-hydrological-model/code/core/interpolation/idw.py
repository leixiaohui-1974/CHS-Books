"""
反距离权重插值 (IDW)
==================

Inverse Distance Weighting
"""

import numpy as np


def inverse_distance_weighting(stations_xy, station_values, target_points,
                               power=2, radius=None, min_stations=1):
    """
    反距离权重插值
    
    IDW公式: Z(x) = Σ[wi * Zi] / Σwi
    权重: wi = 1 / di^p
    
    Parameters
    ----------
    stations_xy : array_like, shape (n, 2)
        站点坐标 [[x1, y1], [x2, y2], ...]
    station_values : array_like, shape (n,)
        站点观测值
    target_points : array_like, shape (m, 2)
        目标点坐标
    power : float
        距离权重指数，默认2
    radius : float, optional
        搜索半径，None表示使用所有站点
    min_stations : int
        最小站点数
        
    Returns
    -------
    interpolated : ndarray, shape (m,)
        插值结果
        
    Examples
    --------
    >>> stations = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    >>> values = np.array([10, 20, 15, 25])
    >>> targets = np.array([[0.5, 0.5], [0.25, 0.25]])
    >>> result = inverse_distance_weighting(stations, values, targets, power=2)
    >>> print(f"插值结果: {result}")
    """
    stations_xy = np.asarray(stations_xy)
    station_values = np.asarray(station_values)
    target_points = np.asarray(target_points)
    
    # 确保target_points是2D数组
    if target_points.ndim == 1:
        target_points = target_points.reshape(1, -1)
    
    n_targets = len(target_points)
    interpolated = np.zeros(n_targets)
    
    for i, target in enumerate(target_points):
        # 计算距离
        distances = np.sqrt(np.sum((stations_xy - target) ** 2, axis=1))
        
        # 处理目标点与站点重合的情况
        if np.min(distances) < 1e-10:
            # 直接使用该站点的值
            idx = np.argmin(distances)
            interpolated[i] = station_values[idx]
            continue
        
        # 应用搜索半径
        if radius is not None:
            mask = distances <= radius
            if np.sum(mask) < min_stations:
                # 如果半径内站点不足，使用最近的min_stations个
                idx = np.argsort(distances)[:min_stations]
                mask = np.zeros(len(distances), dtype=bool)
                mask[idx] = True
        else:
            mask = np.ones(len(distances), dtype=bool)
        
        # 计算权重
        weights = 1.0 / (distances[mask] ** power)
        weights = weights / np.sum(weights)  # 归一化
        
        # 插值
        interpolated[i] = np.sum(weights * station_values[mask])
    
    return interpolated


def idw_grid(stations_xy, station_values, grid_x, grid_y, power=2):
    """
    在规则网格上进行IDW插值
    
    Parameters
    ----------
    stations_xy : array_like, shape (n, 2)
        站点坐标
    station_values : array_like, shape (n,)
        站点观测值
    grid_x : ndarray, shape (ny, nx)
        网格X坐标矩阵
    grid_y : ndarray, shape (ny, nx)
        网格Y坐标矩阵
    power : float
        距离权重指数
        
    Returns
    -------
    grid_values : ndarray, shape (ny, nx)
        网格插值结果
        
    Examples
    --------
    >>> stations = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    >>> values = np.array([10, 20, 15, 25])
    >>> x = np.linspace(0, 1, 11)
    >>> y = np.linspace(0, 1, 11)
    >>> grid_x, grid_y = np.meshgrid(x, y)
    >>> grid_z = idw_grid(stations, values, grid_x, grid_y, power=2)
    >>> print(f"网格形状: {grid_z.shape}")
    """
    # 将网格坐标展平
    target_points = np.column_stack([grid_x.ravel(), grid_y.ravel()])
    
    # 插值
    interpolated = inverse_distance_weighting(stations_xy, station_values, 
                                             target_points, power=power)
    
    # 重塑为网格形状
    grid_values = interpolated.reshape(grid_x.shape)
    
    return grid_values


def cross_validation_idw(stations_xy, station_values, power_range=None):
    """
    交叉验证选择最优power参数
    
    Parameters
    ----------
    stations_xy : array_like
        站点坐标
    station_values : array_like
        站点观测值
    power_range : array_like, optional
        power参数范围，默认[0.5, 1, 1.5, 2, 2.5, 3]
        
    Returns
    -------
    best_power : float
        最优power参数
    rmse_values : dict
        各power对应的RMSE
        
    Examples
    --------
    >>> stations = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    >>> values = np.array([10, 20, 15, 25])
    >>> best_p, rmse_dict = cross_validation_idw(stations, values)
    >>> print(f"最优power: {best_p}, RMSE: {rmse_dict}")
    """
    if power_range is None:
        power_range = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    
    stations_xy = np.asarray(stations_xy)
    station_values = np.asarray(station_values)
    n_stations = len(station_values)
    
    rmse_values = {}
    
    for power in power_range:
        # Leave-One-Out交叉验证
        errors = []
        
        for i in range(n_stations):
            # 去掉第i个站点
            train_xy = np.delete(stations_xy, i, axis=0)
            train_values = np.delete(station_values, i)
            test_xy = stations_xy[i:i+1]
            test_value = station_values[i]
            
            # 插值预测
            pred_value = inverse_distance_weighting(train_xy, train_values, 
                                                   test_xy, power=power)
            
            # 计算误差
            error = test_value - pred_value[0]
            errors.append(error)
        
        # 计算RMSE
        rmse = np.sqrt(np.mean(np.array(errors) ** 2))
        rmse_values[power] = rmse
    
    # 找到最优power
    best_power = min(rmse_values, key=rmse_values.get)
    
    return best_power, rmse_values
