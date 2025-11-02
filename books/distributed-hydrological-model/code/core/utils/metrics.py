"""
评估指标模块
===========

提供常用的水文模型评估指标
"""

import numpy as np


def nash_sutcliffe(observed, simulated):
    """
    Nash-Sutcliffe效率系数 (NSE)
    
    NSE = 1 - Σ(Qo - Qs)² / Σ(Qo - Qo_mean)²
    
    范围: (-∞, 1]，1为最优
    
    Parameters
    ----------
    observed : array_like
        观测值序列
    simulated : array_like
        模拟值序列
        
    Returns
    -------
    nse : float
        Nash-Sutcliffe效率系数
        
    Examples
    --------
    >>> obs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    >>> sim = np.array([1.1, 2.1, 2.9, 4.2, 4.8])
    >>> nse = nash_sutcliffe(obs, sim)
    >>> print(f"NSE = {nse:.4f}")
    """
    observed = np.asarray(observed)
    simulated = np.asarray(simulated)
    
    # 移除NaN值
    mask = ~(np.isnan(observed) | np.isnan(simulated))
    observed = observed[mask]
    simulated = simulated[mask]
    
    if len(observed) == 0:
        return np.nan
    
    # 计算NSE
    numerator = np.sum((observed - simulated) ** 2)
    denominator = np.sum((observed - np.mean(observed)) ** 2)
    
    if denominator == 0:
        return np.nan
    
    nse = 1 - numerator / denominator
    
    return nse


def rmse(observed, simulated):
    """
    均方根误差 (RMSE)
    
    RMSE = sqrt(mean((Qo - Qs)²))
    
    Parameters
    ----------
    observed : array_like
        观测值序列
    simulated : array_like
        模拟值序列
        
    Returns
    -------
    rmse_value : float
        均方根误差
        
    Examples
    --------
    >>> obs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    >>> sim = np.array([1.1, 2.1, 2.9, 4.2, 4.8])
    >>> error = rmse(obs, sim)
    >>> print(f"RMSE = {error:.4f}")
    """
    observed = np.asarray(observed)
    simulated = np.asarray(simulated)
    
    # 移除NaN值
    mask = ~(np.isnan(observed) | np.isnan(simulated))
    observed = observed[mask]
    simulated = simulated[mask]
    
    if len(observed) == 0:
        return np.nan
    
    rmse_value = np.sqrt(np.mean((observed - simulated) ** 2))
    
    return rmse_value


def relative_error(observed, simulated):
    """
    相对误差 (RE)
    
    RE = (Qs_total - Qo_total) / Qo_total × 100%
    
    Parameters
    ----------
    observed : array_like
        观测值序列
    simulated : array_like
        模拟值序列
        
    Returns
    -------
    re : float
        相对误差 (%)
        
    Examples
    --------
    >>> obs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    >>> sim = np.array([1.1, 2.1, 2.9, 4.2, 4.8])
    >>> error = relative_error(obs, sim)
    >>> print(f"RE = {error:.2f}%")
    """
    observed = np.asarray(observed)
    simulated = np.asarray(simulated)
    
    # 移除NaN值
    mask = ~(np.isnan(observed) | np.isnan(simulated))
    observed = observed[mask]
    simulated = simulated[mask]
    
    if len(observed) == 0:
        return np.nan
    
    obs_total = np.sum(observed)
    sim_total = np.sum(simulated)
    
    if obs_total == 0:
        return np.nan
    
    re = (sim_total - obs_total) / obs_total * 100
    
    return re


def peak_error(observed, simulated):
    """
    洪峰相对误差
    
    PE = (Qp_sim - Qp_obs) / Qp_obs × 100%
    
    Parameters
    ----------
    observed : array_like
        观测值序列
    simulated : array_like
        模拟值序列
        
    Returns
    -------
    pe : float
        洪峰相对误差 (%)
        
    Examples
    --------
    >>> obs = np.array([1.0, 2.0, 5.0, 3.0, 2.0])
    >>> sim = np.array([1.1, 2.1, 5.5, 3.1, 2.1])
    >>> error = peak_error(obs, sim)
    >>> print(f"Peak Error = {error:.2f}%")
    """
    observed = np.asarray(observed)
    simulated = np.asarray(simulated)
    
    # 移除NaN值
    mask = ~(np.isnan(observed) | np.isnan(simulated))
    observed = observed[mask]
    simulated = simulated[mask]
    
    if len(observed) == 0:
        return np.nan
    
    peak_obs = np.max(observed)
    peak_sim = np.max(simulated)
    
    if peak_obs == 0:
        return np.nan
    
    pe = (peak_sim - peak_obs) / peak_obs * 100
    
    return pe


def correlation_coefficient(observed, simulated):
    """
    相关系数 (R)
    
    Parameters
    ----------
    observed : array_like
        观测值序列
    simulated : array_like
        模拟值序列
        
    Returns
    -------
    r : float
        相关系数
    """
    observed = np.asarray(observed)
    simulated = np.asarray(simulated)
    
    # 移除NaN值
    mask = ~(np.isnan(observed) | np.isnan(simulated))
    observed = observed[mask]
    simulated = simulated[mask]
    
    if len(observed) < 2:
        return np.nan
    
    r = np.corrcoef(observed, simulated)[0, 1]
    
    return r


def evaluate_model(observed, simulated, metrics=None):
    """
    综合评估模型性能
    
    Parameters
    ----------
    observed : array_like
        观测值序列
    simulated : array_like
        模拟值序列
    metrics : list, optional
        要计算的指标列表，默认计算所有指标
        
    Returns
    -------
    results : dict
        评估指标字典
        
    Examples
    --------
    >>> obs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    >>> sim = np.array([1.1, 2.1, 2.9, 4.2, 4.8])
    >>> results = evaluate_model(obs, sim)
    >>> for key, value in results.items():
    ...     print(f"{key}: {value:.4f}")
    """
    if metrics is None:
        metrics = ['NSE', 'RMSE', 'RE', 'PE', 'R']
    
    results = {}
    
    metric_functions = {
        'NSE': nash_sutcliffe,
        'RMSE': rmse,
        'RE': relative_error,
        'PE': peak_error,
        'R': correlation_coefficient,
    }
    
    for metric in metrics:
        if metric in metric_functions:
            results[metric] = metric_functions[metric](observed, simulated)
    
    return results
