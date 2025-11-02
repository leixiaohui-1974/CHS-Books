"""
抽水井解析解模块

提供经典的井流解析解：
- Theis解（非稳定流）
- Cooper-Jacob近似
- Thiem解（稳态流）
- 叠加原理
"""

import numpy as np
from scipy import special
from typing import Union, List, Tuple, Optional


def theis_well_function(u: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Theis井函数 W(u)
    
    W(u) = ∫[u,∞] (e^(-x) / x) dx
    
    Parameters
    ----------
    u : float or array
        井函数参数 u = r²S / (4Tt)
    
    Returns
    -------
    W_u : float or array
        井函数值
    
    Notes
    -----
    使用指数积分函数 E1(u) 计算，W(u) = E1(u)
    """
    return special.exp1(u)


def theis_solution(
    r: Union[float, np.ndarray],
    t: Union[float, np.ndarray],
    Q: float,
    T: float,
    S: float
) -> Union[float, np.ndarray]:
    """
    Theis非稳定流井流解析解
    
    s(r,t) = (Q / 4πT) * W(u)
    u = r²S / (4Tt)
    
    Parameters
    ----------
    r : float or array
        到井的径向距离 [m]
    t : float or array
        时间 [day]
    Q : float
        抽水流量 [m³/day]
    T : float
        导水系数 [m²/day]
    S : float
        贮水系数 [-]
    
    Returns
    -------
    s : float or array
        降深 [m]
    
    Examples
    --------
    >>> s = theis_solution(r=100, t=1, Q=1000, T=500, S=0.0002)
    >>> print(f"降深: {s:.2f} m")
    
    References
    ----------
    Theis, C.V. (1935). "The relation between the lowering of the piezometric 
    surface and the rate and duration of discharge of a well using ground-water 
    storage". Transactions, American Geophysical Union, 16: 519–524.
    """
    # 计算u
    u = (r**2 * S) / (4 * T * t)
    
    # 计算W(u)
    W_u = theis_well_function(u)
    
    # 计算降深
    s = (Q / (4 * np.pi * T)) * W_u
    
    return s


def cooper_jacob_solution(
    r: Union[float, np.ndarray],
    t: Union[float, np.ndarray],
    Q: float,
    T: float,
    S: float
) -> Union[float, np.ndarray]:
    """
    Cooper-Jacob近似解
    
    当 u < 0.01 时（大时间或小距离），W(u) 可近似为：
    W(u) ≈ -0.5772 - ln(u) = ln(2.25Tt / r²S)
    
    s(r,t) = (Q / 4πT) * ln(2.25Tt / r²S)
    
    Parameters
    ----------
    r : float or array
        径向距离 [m]
    t : float or array
        时间 [day]
    Q : float
        抽水流量 [m³/day]
    T : float
        导水系数 [m²/day]
    S : float
        贮水系数 [-]
    
    Returns
    -------
    s : float or array
        降深 [m]
    
    Notes
    -----
    适用条件：u < 0.01，即 r²S / (4Tt) < 0.01
    通常要求 t > 25r²S / T
    
    References
    ----------
    Cooper, H.H. and Jacob, C.E. (1946). "A generalized graphical method for 
    evaluating formation constants and summarizing well field history". 
    Transactions, American Geophysical Union, 27: 526–534.
    """
    # 计算降深
    s = (Q / (4 * np.pi * T)) * np.log(2.25 * T * t / (r**2 * S))
    
    return s


def thiem_solution(
    r: Union[float, np.ndarray],
    Q: float,
    T: float,
    R: float,
    h0: Optional[float] = None
) -> Union[float, np.ndarray]:
    """
    Thiem稳态流井流解析解
    
    s(r) = (Q / 2πT) * ln(R / r)
    或
    h(r) = h0 - (Q / 2πT) * ln(R / r)
    
    Parameters
    ----------
    r : float or array
        径向距离 [m]
    Q : float
        抽水流量 [m³/day]
    T : float
        导水系数 [m²/day]
    R : float
        影响半径 [m]，s(R) = 0 处的距离
    h0 : float, optional
        初始水头 [m]，如果提供则返回水头而非降深
    
    Returns
    -------
    s or h : float or array
        降深 [m] 或水头 [m]
    
    Notes
    -----
    适用于稳定流井流，即 ∂h/∂t = 0
    
    References
    ----------
    Thiem, G. (1906). Hydrologische Methoden. Leipzig: Gebhardt. 56 pp.
    """
    # 确保r不等于0（避免除以零）
    r = np.maximum(r, 1e-10)
    
    # 计算降深
    s = (Q / (2 * np.pi * T)) * np.log(R / r)
    
    # 如果提供了初始水头，返回水头
    if h0 is not None:
        return h0 - s
    else:
        return s


def superposition_principle(
    wells: List[Tuple[float, float, float]],
    x: Union[float, np.ndarray],
    y: Union[float, np.ndarray],
    t: float,
    T: float,
    S: float,
    method: str = 'theis'
) -> Union[float, np.ndarray]:
    """
    叠加原理计算多井系统的总降深
    
    s_total(x,y,t) = Σ s_i(x,y,t)
    
    Parameters
    ----------
    wells : list of tuples
        井的列表，每个井为 (x_well, y_well, Q_well)
    x, y : float or array
        观测点坐标 [m]
    t : float
        时间 [day]
    T : float
        导水系数 [m²/day]
    S : float
        贮水系数 [-]
    method : str, optional
        计算方法，'theis' 或 'cooper_jacob'，默认 'theis'
    
    Returns
    -------
    s_total : float or array
        总降深 [m]
    
    Examples
    --------
    >>> wells = [(0, 0, 1000), (500, 0, 800)]  # 两口井
    >>> s = superposition_principle(wells, x=250, y=0, t=10, T=500, S=0.0002)
    """
    s_total = np.zeros_like(x, dtype=float)
    
    for x_well, y_well, Q_well in wells:
        # 计算距离
        r = np.sqrt((x - x_well)**2 + (y - y_well)**2)
        
        # 避免r=0
        r = np.maximum(r, 0.1)  # 井半径约0.1m
        
        # 根据方法选择
        if method == 'theis':
            s_well = theis_solution(r, t, Q_well, T, S)
        elif method == 'cooper_jacob':
            s_well = cooper_jacob_solution(r, t, Q_well, T, S)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        s_total += s_well
    
    return s_total


def compute_influence_radius(
    Q: float,
    T: float,
    S: float,
    t: float,
    s_threshold: float = 0.01
) -> float:
    """
    计算影响半径
    
    影响半径定义为降深小于阈值处的距离
    
    Parameters
    ----------
    Q : float
        抽水流量 [m³/day]
    T : float
        导水系数 [m²/day]
    S : float
        贮水系数 [-]
    t : float
        时间 [day]
    s_threshold : float, optional
        降深阈值 [m]，默认0.01m
    
    Returns
    -------
    R : float
        影响半径 [m]
    
    Notes
    -----
    使用Cooper-Jacob公式反推：
    s = (Q / 4πT) * ln(2.25Tt / r²S) = s_threshold
    → r = √(2.25Tt / S * exp(-4πTs_threshold / Q))
    """
    # 避免负数
    arg = 2.25 * T * t / S * np.exp(-4 * np.pi * T * s_threshold / Q)
    R = np.sqrt(max(arg, 1.0))
    
    return R


def distance_drawdown_curve(
    Q: float,
    T: float,
    S: float,
    t: float,
    r_range: Tuple[float, float] = (1, 1000),
    n_points: int = 100
) -> Tuple[np.ndarray, np.ndarray]:
    """
    生成距离-降深曲线
    
    Parameters
    ----------
    Q : float
        抽水流量 [m³/day]
    T : float
        导水系数 [m²/day]
    S : float
        贮水系数 [-]
    t : float
        时间 [day]
    r_range : tuple, optional
        距离范围 [m]，默认 (1, 1000)
    n_points : int, optional
        点数，默认100
    
    Returns
    -------
    r : ndarray
        距离数组 [m]
    s : ndarray
        降深数组 [m]
    """
    r = np.logspace(np.log10(r_range[0]), np.log10(r_range[1]), n_points)
    s = theis_solution(r, t, Q, T, S)
    
    return r, s


def time_drawdown_curve(
    r: float,
    Q: float,
    T: float,
    S: float,
    t_range: Tuple[float, float] = (0.01, 100),
    n_points: int = 100
) -> Tuple[np.ndarray, np.ndarray]:
    """
    生成时间-降深曲线
    
    Parameters
    ----------
    r : float
        观测距离 [m]
    Q : float
        抽水流量 [m³/day]
    T : float
        导水系数 [m²/day]
    S : float
        贮水系数 [-]
    t_range : tuple, optional
        时间范围 [day]，默认 (0.01, 100)
    n_points : int, optional
        点数，默认100
    
    Returns
    -------
    t : ndarray
        时间数组 [day]
    s : ndarray
        降深数组 [m]
    """
    t = np.logspace(np.log10(t_range[0]), np.log10(t_range[1]), n_points)
    s = theis_solution(r, t, Q, T, S)
    
    return t, s
