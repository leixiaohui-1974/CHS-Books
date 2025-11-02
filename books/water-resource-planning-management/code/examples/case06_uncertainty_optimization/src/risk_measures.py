"""
风险度量

VaR和CVaR计算
"""

import numpy as np
from typing import List, Tuple


def calculate_var(
    values: np.ndarray,
    confidence_level: float = 0.95
) -> float:
    """
    计算VaR（在险价值）
    
    Parameters
    ----------
    values : np.ndarray
        样本值（损失或收益）
    confidence_level : float
        置信水平
    
    Returns
    -------
    float
        VaR值
    """
    # 对于损失，VaR是分位数
    # 对于收益，VaR是(1-α)分位数
    return np.percentile(values, (1 - confidence_level) * 100)


def calculate_cvar(
    values: np.ndarray,
    confidence_level: float = 0.95
) -> Tuple[float, float]:
    """
    计算CVaR（条件风险价值）
    
    Parameters
    ----------
    values : np.ndarray
        样本值
    confidence_level : float
        置信水平
    
    Returns
    -------
    Tuple[float, float]
        (VaR, CVaR)
    """
    # 计算VaR
    var = calculate_var(values, confidence_level)
    
    # CVaR：超过VaR的值的平均
    tail_values = values[values <= var]
    
    if len(tail_values) > 0:
        cvar = np.mean(tail_values)
    else:
        cvar = var
    
    return var, cvar


def calculate_expected_shortfall(
    values: np.ndarray,
    threshold: float
) -> float:
    """
    计算期望短缺
    
    Parameters
    ----------
    values : np.ndarray
        样本值
    threshold : float
        阈值
    
    Returns
    -------
    float
        期望短缺
    """
    shortfalls = np.maximum(threshold - values, 0)
    return np.mean(shortfalls)


def calculate_downside_risk(
    values: np.ndarray,
    target: float
) -> float:
    """
    计算下行风险
    
    Parameters
    ----------
    values : np.ndarray
        样本值
    target : float
        目标值
    
    Returns
    -------
    float
        下行风险（半方差）
    """
    deviations = np.minimum(values - target, 0)
    return np.sqrt(np.mean(deviations ** 2))


def calculate_risk_metrics(
    values: np.ndarray,
    target: float = None,
    confidence_level: float = 0.95
) -> dict:
    """
    计算综合风险指标
    
    Parameters
    ----------
    values : np.ndarray
        样本值
    target : float, optional
        目标值
    confidence_level : float
        置信水平
    
    Returns
    -------
    dict
        风险指标字典
    """
    metrics = {}
    
    # 基本统计
    metrics['mean'] = np.mean(values)
    metrics['std'] = np.std(values)
    metrics['min'] = np.min(values)
    metrics['max'] = np.max(values)
    
    # VaR和CVaR
    var, cvar = calculate_cvar(values, confidence_level)
    metrics['var'] = var
    metrics['cvar'] = cvar
    
    # 下行风险
    if target is not None:
        metrics['downside_risk'] = calculate_downside_risk(values, target)
        metrics['expected_shortfall'] = calculate_expected_shortfall(values, target)
    
    # 变异系数
    metrics['coefficient_of_variation'] = metrics['std'] / (metrics['mean'] + 1e-10)
    
    return metrics
