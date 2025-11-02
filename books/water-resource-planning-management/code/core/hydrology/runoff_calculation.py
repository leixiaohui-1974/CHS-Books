"""
径流计算模块

提供各种径流计算方法
"""

import numpy as np
from typing import Tuple, Optional


def calculate_runoff_coefficient(
    runoff: float,
    precipitation: float
) -> float:
    """
    计算径流系数
    
    径流系数 α = R / P
    
    Parameters
    ----------
    runoff : float
        径流深 (mm)
    precipitation : float
        降水量 (mm)
    
    Returns
    -------
    float
        径流系数
    
    Examples
    --------
    >>> alpha = calculate_runoff_coefficient(runoff=300, precipitation=500)
    >>> print(f"径流系数: {alpha:.3f}")
    """
    if precipitation == 0:
        return 0.0
    
    return runoff / precipitation


def estimate_annual_runoff(
    area: float,
    precipitation: float,
    runoff_coefficient: Optional[float] = None,
    evaporation: Optional[float] = None
) -> float:
    """
    估算年径流量
    
    两种方法：
    1. 径流系数法：R = α * P * A
    2. 水量平衡法：R = (P - E) * A
    
    Parameters
    ----------
    area : float
        流域面积 (km²)
    precipitation : float
        年降水量 (mm)
    runoff_coefficient : float, optional
        径流系数，如果提供则使用径流系数法
    evaporation : float, optional
        年蒸发量 (mm)，如果提供则使用水量平衡法
    
    Returns
    -------
    float
        年径流量 (亿m³)
    
    Examples
    --------
    >>> # 方法1: 径流系数法
    >>> runoff1 = estimate_annual_runoff(
    ...     area=5000,
    ...     precipitation=800,
    ...     runoff_coefficient=0.6
    ... )
    >>> print(f"年径流量: {runoff1:.2f} 亿m³")
    >>> 
    >>> # 方法2: 水量平衡法
    >>> runoff2 = estimate_annual_runoff(
    ...     area=5000,
    ...     precipitation=800,
    ...     evaporation=400
    ... )
    >>> print(f"年径流量: {runoff2:.2f} 亿m³")
    """
    if runoff_coefficient is not None:
        # 径流系数法
        runoff_depth = runoff_coefficient * precipitation  # mm
    elif evaporation is not None:
        # 水量平衡法
        runoff_depth = precipitation - evaporation  # mm
    else:
        raise ValueError("必须提供 runoff_coefficient 或 evaporation 参数")
    
    # 转换为体积
    # mm * km² = 1000 m³ = 0.0001 亿m³
    runoff_volume = runoff_depth * area * 0.0001  # 亿m³
    
    return runoff_volume


def calculate_design_flood(
    area: float,
    precipitation: float,
    duration: float,
    runoff_coefficient: float = 0.6,
    concentration_time: Optional[float] = None
) -> Tuple[float, float]:
    """
    计算设计洪水
    
    使用推理公式法
    
    Parameters
    ----------
    area : float
        流域面积 (km²)
    precipitation : float
        设计雨量 (mm)
    duration : float
        降雨历时 (h)
    runoff_coefficient : float, optional
        径流系数，默认0.6
    concentration_time : float, optional
        汇流时间 (h)，如果不提供则使用经验公式估算
    
    Returns
    -------
    Tuple[float, float]
        (设计洪峰流量 m³/s, 洪水总量 万m³)
    
    Examples
    --------
    >>> peak_flow, total_volume = calculate_design_flood(
    ...     area=500,
    ...     precipitation=120,
    ...     duration=6,
    ...     runoff_coefficient=0.7
    ... )
    >>> print(f"洪峰流量: {peak_flow:.2f} m³/s")
    >>> print(f"洪水总量: {total_volume:.2f} 万m³")
    """
    # 估算汇流时间（如果未提供）
    if concentration_time is None:
        # 经验公式：τ = 0.278 * L^0.6 / J^0.3
        # 这里用简化公式：τ = 0.5 * A^0.3 (小时)
        concentration_time = 0.5 * (area ** 0.3)
    
    # 计算径流深 (mm)
    runoff_depth = runoff_coefficient * precipitation
    
    # 计算洪水总量 (万m³)
    # mm * km² * 100 = 万m³
    total_volume = runoff_depth * area * 100
    
    # 计算洪峰流量 (m³/s)
    # 使用简化的三角形洪水过程线
    # Q = (R * A) / (3.6 * τ)
    # 其中 R 单位为mm, A 单位为km², τ 单位为h
    peak_flow = (runoff_depth * area) / (3.6 * concentration_time)
    
    return peak_flow, total_volume


def calculate_baseflow_separation(
    discharge: np.ndarray,
    method: str = "constant_slope"
) -> Tuple[np.ndarray, np.ndarray]:
    """
    基流分割
    
    Parameters
    ----------
    discharge : np.ndarray
        流量过程 (m³/s)
    method : str, optional
        分割方法：
        - 'constant_slope': 恒定斜率法
        - 'fixed_ratio': 固定比例法
    
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (基流, 地表径流)
    
    Examples
    --------
    >>> discharge = np.array([10, 50, 100, 80, 50, 30, 20, 15])
    >>> baseflow, surface_flow = calculate_baseflow_separation(discharge)
    >>> print(f"基流: {baseflow}")
    >>> print(f"地表径流: {surface_flow}")
    """
    n = len(discharge)
    
    if method == "constant_slope":
        # 恒定斜率法
        # 找到局部最小值作为基流点
        baseflow = np.zeros(n)
        
        # 简化实现：使用移动窗口的最小值
        window = min(5, n)
        for i in range(n):
            start = max(0, i - window // 2)
            end = min(n, i + window // 2 + 1)
            baseflow[i] = np.min(discharge[start:end])
        
        # 平滑基流线
        if n > 3:
            baseflow = np.convolve(baseflow, np.ones(3) / 3, mode='same')
    
    elif method == "fixed_ratio":
        # 固定比例法：假设基流占总流量的20-30%
        baseflow = discharge * 0.25
    
    else:
        raise ValueError(f"不支持的方法: {method}")
    
    # 计算地表径流
    surface_flow = discharge - baseflow
    surface_flow = np.maximum(surface_flow, 0)  # 确保非负
    
    return baseflow, surface_flow
