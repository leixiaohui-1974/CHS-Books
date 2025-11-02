"""
污染物运移解析解
"""

import numpy as np
from scipy import special
from typing import Union


def analytical_1d_instantaneous(
    x: Union[float, np.ndarray],
    t: float,
    M: float,
    v: float,
    D: float,
    R: float = 1.0,
    lambda_: float = 0.0
) -> Union[float, np.ndarray]:
    """
    一维瞬时点源解析解
    
    C(x,t) = (M / (n*A*√(4πDt/R))) * exp(-(x-vt/R)² / (4Dt/R)) * exp(-λt)
    
    Parameters
    ----------
    x : float or array
        位置 [m]
    t : float
        时间 [day]
    M : float
        总质量 [kg]
    v : float
        流速 [m/day]
    D : float
        弥散系数 [m²/day]
    R : float, optional
        阻滞因子，默认1
    lambda_ : float, optional
        衰减系数 [1/day]，默认0
    
    Returns
    -------
    C : float or array
        浓度 [kg/m³]
    """
    if t <= 0:
        return np.zeros_like(x)
    
    # 考虑阻滞
    v_eff = v / R
    D_eff = D / R
    
    # 高斯分布
    C = (M / np.sqrt(4 * np.pi * D_eff * t)) * \
        np.exp(-(x - v_eff * t)**2 / (4 * D_eff * t)) * \
        np.exp(-lambda_ * t)
    
    return C


def analytical_1d_continuous(
    x: Union[float, np.ndarray],
    t: float,
    C0: float,
    v: float,
    D: float,
    R: float = 1.0,
    lambda_: float = 0.0
) -> Union[float, np.ndarray]:
    """
    一维连续源解析解（x=0处C=C0）
    
    C(x,t) = (C0/2) * [erfc((x-vt/R)/(2√(Dt/R))) + 
                       exp(vx/D) * erfc((x+vt/R)/(2√(Dt/R)))] * exp(-λt)
    
    Parameters
    ----------
    x : float or array
        位置 [m]
    t : float
        时间 [day]
    C0 : float
        源浓度 [kg/m³]
    v, D, R, lambda_ : float
        运移参数
    
    Returns
    -------
    C : float or array
        浓度 [kg/m³]
    """
    if t <= 0:
        C = np.where(x == 0, C0, 0)
        return C
    
    v_eff = v / R
    D_eff = D / R
    
    term1 = special.erfc((x - v_eff * t) / (2 * np.sqrt(D_eff * t)))
    term2 = np.exp(v * x / D) * special.erfc((x + v_eff * t) / (2 * np.sqrt(D_eff * t)))
    
    C = (C0 / 2) * (term1 + term2) * np.exp(-lambda_ * t)
    
    return C


def analytical_2d_instantaneous(
    x: Union[float, np.ndarray],
    y: Union[float, np.ndarray],
    t: float,
    M: float,
    vx: float,
    vy: float,
    Dx: float,
    Dy: float,
    R: float = 1.0,
    lambda_: float = 0.0
) -> Union[float, np.ndarray]:
    """
    二维瞬时点源解析解
    
    C(x,y,t) = (M / (4πt√(Dx*Dy/R²))) * 
               exp(-((x-vx*t/R)²/(4Dx*t/R) + (y-vy*t/R)²/(4Dy*t/R))) * 
               exp(-λt)
    
    Parameters
    ----------
    x, y : float or array
        位置 [m]
    t : float
        时间 [day]
    M : float
        总质量 [kg]
    vx, vy : float
        流速分量 [m/day]
    Dx, Dy : float
        弥散系数 [m²/day]
    R, lambda_ : float
        阻滞因子和衰减系数
    
    Returns
    -------
    C : float or array
        浓度 [kg/m³]
    """
    if t <= 0:
        return np.zeros_like(x)
    
    vx_eff = vx / R
    vy_eff = vy / R
    Dx_eff = Dx / R
    Dy_eff = Dy / R
    
    C = (M / (4 * np.pi * t * np.sqrt(Dx_eff * Dy_eff))) * \
        np.exp(-((x - vx_eff * t)**2 / (4 * Dx_eff * t) + 
                 (y - vy_eff * t)**2 / (4 * Dy_eff * t))) * \
        np.exp(-lambda_ * t)
    
    return C


def ogata_banks_solution(
    x: Union[float, np.ndarray],
    t: float,
    C0: float,
    v: float,
    D: float,
    R: float = 1.0
) -> Union[float, np.ndarray]:
    """
    Ogata-Banks解（一维，初始C=0，x=0处突然C=C0）
    
    C(x,t) = (C0/2) * [erfc((x-vt/R)/(2√(Dt/R))) + 
                       exp(vx/D) * erfc((x+vt/R)/(2√(Dt/R)))]
    
    Parameters
    ----------
    x : float or array
        位置 [m]
    t : float
        时间 [day]
    C0 : float
        边界浓度 [kg/m³]
    v, D, R : float
        运移参数
    
    Returns
    -------
    C : float or array
        浓度 [kg/m³]
    """
    if t <= 0:
        return np.where(x == 0, C0, 0)
    
    v_eff = v / R
    D_eff = D / R
    
    term1 = special.erfc((x - v_eff * t) / (2 * np.sqrt(D_eff * t)))
    term2 = np.exp(v * x / D) * special.erfc((x + v_eff * t) / (2 * np.sqrt(D_eff * t)))
    
    C = (C0 / 2) * (term1 + term2)
    
    return C
