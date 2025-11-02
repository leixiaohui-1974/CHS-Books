"""
敏感性分析模块

提供参数敏感性分析的各种方法
"""

import numpy as np
from typing import Callable, Dict, List, Optional, Any


def forward_difference_sensitivity(
    forward_model: Callable,
    parameters: np.ndarray,
    delta: float = 1e-6
) -> np.ndarray:
    """
    使用前向差分计算敏感性矩阵
    
    Parameters
    ----------
    forward_model : callable
        正演模型，输入参数，返回模拟值
    parameters : np.ndarray
        参数值
    delta : float
        差分步长
        
    Returns
    -------
    np.ndarray
        敏感性矩阵，形状为 (n_observations, n_parameters)
    """
    base_simulation = forward_model(parameters)
    n_obs = len(base_simulation)
    n_params = len(parameters)
    
    sensitivity = np.zeros((n_obs, n_params))
    
    for j in range(n_params):
        params_perturbed = parameters.copy()
        delta_p = delta * max(abs(parameters[j]), 1.0)
        params_perturbed[j] += delta_p
        
        perturbed_simulation = forward_model(params_perturbed)
        sensitivity[:, j] = (perturbed_simulation - base_simulation) / delta_p
    
    return sensitivity


def relative_sensitivity_coefficient(
    forward_model: Callable,
    parameters: np.ndarray,
    param_index: int,
    delta: float = 0.01
) -> np.ndarray:
    """
    计算相对敏感性系数
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    parameters : np.ndarray
        参数值
    param_index : int
        参数索引
    delta : float
        相对扰动量（默认1%）
        
    Returns
    -------
    np.ndarray
        相对敏感性系数
        
    Notes
    -----
    相对敏感性系数定义为：
    RSS_i = (∂h_i / ∂p) * (p / h_i)
    """
    base_simulation = forward_model(parameters)
    
    params_perturbed = parameters.copy()
    delta_p = delta * parameters[param_index]
    params_perturbed[param_index] += delta_p
    
    perturbed_simulation = forward_model(params_perturbed)
    
    # 相对敏感性
    with np.errstate(divide='ignore', invalid='ignore'):
        rss = ((perturbed_simulation - base_simulation) / delta_p) * \
              (parameters[param_index] / base_simulation)
        rss = np.nan_to_num(rss, 0.0)
    
    return rss


def compute_sensitivity_matrix(
    forward_model: Callable,
    parameters: np.ndarray,
    method: str = 'forward',
    delta: float = 1e-6
) -> np.ndarray:
    """
    计算敏感性矩阵
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    parameters : np.ndarray
        参数值
    method : str
        方法：'forward' (前向差分), 'central' (中心差分)
    delta : float
        差分步长
        
    Returns
    -------
    np.ndarray
        敏感性矩阵
    """
    if method == 'forward':
        return forward_difference_sensitivity(forward_model, parameters, delta)
    elif method == 'central':
        return central_difference_sensitivity(forward_model, parameters, delta)
    else:
        raise ValueError(f"Unknown method: {method}")


def central_difference_sensitivity(
    forward_model: Callable,
    parameters: np.ndarray,
    delta: float = 1e-6
) -> np.ndarray:
    """
    使用中心差分计算敏感性矩阵（更精确）
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    parameters : np.ndarray
        参数值
    delta : float
        差分步长
        
    Returns
    -------
    np.ndarray
        敏感性矩阵
        
    Notes
    -----
    中心差分：∂h/∂p ≈ [h(p+δ) - h(p-δ)] / (2δ)
    精度为O(δ²)，优于前向差分的O(δ)
    """
    base_simulation = forward_model(parameters)
    n_obs = len(base_simulation)
    n_params = len(parameters)
    
    sensitivity = np.zeros((n_obs, n_params))
    
    for j in range(n_params):
        delta_p = delta * max(abs(parameters[j]), 1.0)
        
        # 正向扰动
        params_plus = parameters.copy()
        params_plus[j] += delta_p
        sim_plus = forward_model(params_plus)
        
        # 负向扰动
        params_minus = parameters.copy()
        params_minus[j] -= delta_p
        sim_minus = forward_model(params_minus)
        
        # 中心差分
        sensitivity[:, j] = (sim_plus - sim_minus) / (2.0 * delta_p)
    
    return sensitivity


def compute_composite_sensitivity(
    sensitivity_matrix: np.ndarray,
    weights: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    计算复合敏感性（每个参数的总敏感性）
    
    Parameters
    ----------
    sensitivity_matrix : np.ndarray
        敏感性矩阵
    weights : np.ndarray, optional
        观测权重
        
    Returns
    -------
    np.ndarray
        每个参数的复合敏感性
        
    Notes
    -----
    复合敏感性定义为：
    CSS_j = sqrt(Σ w_i * (∂h_i/∂p_j)²)
    """
    if weights is None:
        weights = np.ones(sensitivity_matrix.shape[0])
    
    composite = np.sqrt(np.sum(weights[:, np.newaxis] * sensitivity_matrix**2, axis=0))
    return composite


def compute_parameter_correlation(
    sensitivity_matrix: np.ndarray,
    weights: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    计算参数相关性矩阵
    
    Parameters
    ----------
    sensitivity_matrix : np.ndarray
        敏感性矩阵
    weights : np.ndarray, optional
        观测权重
        
    Returns
    -------
    np.ndarray
        参数相关性矩阵
        
    Notes
    -----
    高相关性表示参数之间难以独立率定
    """
    if weights is None:
        W = np.eye(sensitivity_matrix.shape[0])
    else:
        W = np.diag(weights)
    
    J = sensitivity_matrix
    JtWJ = J.T @ W @ J
    
    # 标准化得到相关性矩阵
    d = np.sqrt(np.diag(JtWJ))
    correlation = JtWJ / np.outer(d, d)
    
    return correlation
