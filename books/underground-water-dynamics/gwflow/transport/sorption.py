"""
吸附模型
"""

import numpy as np
from typing import Union


def retardation_factor(
    rho_b: float,
    n: float,
    Kd: float
) -> float:
    """
    阻滞因子（线性吸附）
    
    R = 1 + (ρb/n) * Kd
    
    Parameters
    ----------
    rho_b : float
        土壤干密度 [kg/m³]
    n : float
        孔隙度 [-]
    Kd : float
        分配系数 [m³/kg]
    
    Returns
    -------
    R : float
        阻滞因子 [-]
    
    Notes
    -----
    R > 1: 吸附作用，运移速度减慢
    R = 1: 无吸附（保守物质）
    """
    R = 1 + (rho_b / n) * Kd
    return R


def linear_sorption(
    C: Union[float, np.ndarray],
    Kd: float
) -> Union[float, np.ndarray]:
    """
    线性吸附等温线
    
    S = Kd * C
    
    Parameters
    ----------
    C : float or array
        溶液浓度 [kg/m³]
    Kd : float
        分配系数 [m³/kg]
    
    Returns
    -------
    S : float or array
        吸附量 [kg/kg]
    """
    return Kd * C


def freundlich_sorption(
    C: Union[float, np.ndarray],
    Kf: float,
    n: float
) -> Union[float, np.ndarray]:
    """
    Freundlich非线性吸附
    
    S = Kf * C^n
    
    Parameters
    ----------
    C : float or array
        溶液浓度 [kg/m³]
    Kf : float
        Freundlich系数
    n : float
        Freundlich指数（通常<1）
    
    Returns
    -------
    S : float or array
        吸附量 [kg/kg]
    """
    return Kf * C**n


def langmuir_sorption(
    C: Union[float, np.ndarray],
    Qmax: float,
    b: float
) -> Union[float, np.ndarray]:
    """
    Langmuir吸附等温线
    
    S = (Qmax * b * C) / (1 + b * C)
    
    Parameters
    ----------
    C : float or array
        溶液浓度 [kg/m³]
    Qmax : float
        最大吸附量 [kg/kg]
    b : float
        Langmuir常数 [m³/kg]
    
    Returns
    -------
    S : float or array
        吸附量 [kg/kg]
    """
    return (Qmax * b * C) / (1 + b * C)
