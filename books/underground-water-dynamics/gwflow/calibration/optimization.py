"""
优化算法模块

实现各种参数率定的优化算法
"""

import numpy as np
from typing import Callable, Dict, List, Tuple, Optional, Any
from scipy.optimize import minimize, least_squares


def compute_objective_function(
    observed: np.ndarray,
    simulated: np.ndarray,
    weights: Optional[np.ndarray] = None
) -> float:
    """
    计算目标函数（加权最小二乘）
    
    Parameters
    ----------
    observed : np.ndarray
        观测值
    simulated : np.ndarray
        模拟值
    weights : np.ndarray, optional
        权重矩阵，默认为均匀权重
        
    Returns
    -------
    float
        目标函数值（加权残差平方和）
        
    Notes
    -----
    目标函数定义为：
    Φ = Σ w_i * (h_obs,i - h_sim,i)²
    """
    residuals = observed - simulated
    
    if weights is None:
        weights = np.ones_like(observed)
    
    objective = np.sum(weights * residuals**2)
    return objective


def compute_jacobian(
    forward_model: Callable,
    parameters: np.ndarray,
    delta: float = 1e-6
) -> np.ndarray:
    """
    使用有限差分计算Jacobian矩阵（敏感性矩阵）
    
    Parameters
    ----------
    forward_model : callable
        正演模型函数，输入参数，返回模拟观测值
    parameters : np.ndarray
        当前参数值
    delta : float
        有限差分步长
        
    Returns
    -------
    np.ndarray
        Jacobian矩阵，形状为 (n_observations, n_parameters)
        
    Notes
    -----
    Jacobian矩阵的第i行第j列元素为：
    J_ij = ∂h_i / ∂p_j
    """
    # 基准模拟
    base_simulation = forward_model(parameters)
    n_obs = len(base_simulation)
    n_params = len(parameters)
    
    jacobian = np.zeros((n_obs, n_params))
    
    # 对每个参数计算偏导数
    for j in range(n_params):
        # 扰动第j个参数
        params_perturbed = parameters.copy()
        delta_p = delta * max(abs(parameters[j]), 1.0)
        params_perturbed[j] += delta_p
        
        # 计算扰动后的模拟
        perturbed_simulation = forward_model(params_perturbed)
        
        # 有限差分近似
        jacobian[:, j] = (perturbed_simulation - base_simulation) / delta_p
    
    return jacobian


def gradient_descent(
    forward_model: Callable,
    initial_params: np.ndarray,
    observed: np.ndarray,
    learning_rate: float = 0.01,
    max_iterations: int = 100,
    tolerance: float = 1e-6,
    weights: Optional[np.ndarray] = None,
    bounds: Optional[List[Tuple[float, float]]] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    梯度下降法参数率定
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    initial_params : np.ndarray
        初始参数值
    observed : np.ndarray
        观测值
    learning_rate : float
        学习率
    max_iterations : int
        最大迭代次数
    tolerance : float
        收敛容差
    weights : np.ndarray, optional
        观测权重
    bounds : list of tuples, optional
        参数边界 [(min1, max1), (min2, max2), ...]
    verbose : bool
        是否输出迭代信息
        
    Returns
    -------
    dict
        包含优化结果的字典：
        - 'parameters': 最优参数
        - 'objective': 目标函数值
        - 'iterations': 迭代次数
        - 'history': 优化历史
    """
    params = initial_params.copy()
    n_params = len(params)
    
    if weights is None:
        weights = np.ones_like(observed)
    
    # 存储优化历史
    history = {
        'parameters': [params.copy()],
        'objective': [],
        'gradient_norm': []
    }
    
    for iteration in range(max_iterations):
        # 正演模拟
        simulated = forward_model(params)
        
        # 计算目标函数
        objective = compute_objective_function(observed, simulated, weights)
        history['objective'].append(objective)
        
        # 计算Jacobian矩阵
        jacobian = compute_jacobian(forward_model, params)
        
        # 计算梯度：∇Φ = -2 * J^T * W * r
        residuals = observed - simulated
        gradient = -2.0 * jacobian.T @ (weights * residuals)
        gradient_norm = np.linalg.norm(gradient)
        history['gradient_norm'].append(gradient_norm)
        
        if verbose and iteration % 10 == 0:
            print(f"Iteration {iteration}: Objective = {objective:.6e}, "
                  f"||Gradient|| = {gradient_norm:.6e}")
        
        # 检查收敛
        if gradient_norm < tolerance:
            if verbose:
                print(f"Converged at iteration {iteration}")
            break
        
        # 更新参数
        params = params - learning_rate * gradient
        
        # 应用边界约束
        if bounds is not None:
            for i, (lower, upper) in enumerate(bounds):
                params[i] = np.clip(params[i], lower, upper)
        
        history['parameters'].append(params.copy())
    
    return {
        'parameters': params,
        'objective': objective,
        'iterations': iteration + 1,
        'history': history,
        'success': gradient_norm < tolerance
    }


def gauss_newton(
    forward_model: Callable,
    initial_params: np.ndarray,
    observed: np.ndarray,
    max_iterations: int = 50,
    tolerance: float = 1e-6,
    weights: Optional[np.ndarray] = None,
    bounds: Optional[List[Tuple[float, float]]] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Gauss-Newton法参数率定
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    initial_params : np.ndarray
        初始参数值
    observed : np.ndarray
        观测值
    max_iterations : int
        最大迭代次数
    tolerance : float
        收敛容差
    weights : np.ndarray, optional
        观测权重
    bounds : list of tuples, optional
        参数边界
    verbose : bool
        是否输出迭代信息
        
    Returns
    -------
    dict
        优化结果
        
    Notes
    -----
    更新公式：
    p_{k+1} = p_k + (J^T W J)^{-1} J^T W r
    """
    params = initial_params.copy()
    
    if weights is None:
        weights = np.ones_like(observed)
    
    # 权重矩阵
    W = np.diag(weights)
    
    history = {
        'parameters': [params.copy()],
        'objective': [],
        'parameter_update_norm': []
    }
    
    for iteration in range(max_iterations):
        # 正演模拟
        simulated = forward_model(params)
        residuals = observed - simulated
        
        # 计算目标函数
        objective = compute_objective_function(observed, simulated, weights)
        history['objective'].append(objective)
        
        # 计算Jacobian矩阵
        J = compute_jacobian(forward_model, params)
        
        # Gauss-Newton方程：(J^T W J) Δp = J^T W r
        JtWJ = J.T @ W @ J
        JtWr = J.T @ W @ residuals
        
        # 求解参数更新（使用正则化避免奇异）
        regularization = 1e-8 * np.eye(len(params))
        try:
            delta_params = np.linalg.solve(JtWJ + regularization, JtWr)
        except np.linalg.LinAlgError:
            if verbose:
                print("Warning: Singular matrix, using pseudo-inverse")
            delta_params = np.linalg.lstsq(JtWJ, JtWr, rcond=None)[0]
        
        param_update_norm = np.linalg.norm(delta_params)
        history['parameter_update_norm'].append(param_update_norm)
        
        if verbose and iteration % 5 == 0:
            print(f"Iteration {iteration}: Objective = {objective:.6e}, "
                  f"||Δp|| = {param_update_norm:.6e}")
        
        # 检查收敛
        if param_update_norm < tolerance:
            if verbose:
                print(f"Converged at iteration {iteration}")
            break
        
        # 更新参数
        params = params + delta_params
        
        # 应用边界约束
        if bounds is not None:
            for i, (lower, upper) in enumerate(bounds):
                params[i] = np.clip(params[i], lower, upper)
        
        history['parameters'].append(params.copy())
    
    return {
        'parameters': params,
        'objective': objective,
        'iterations': iteration + 1,
        'history': history,
        'success': param_update_norm < tolerance
    }


def levenberg_marquardt(
    forward_model: Callable,
    initial_params: np.ndarray,
    observed: np.ndarray,
    max_iterations: int = 50,
    tolerance: float = 1e-6,
    lambda_init: float = 0.01,
    lambda_factor: float = 10.0,
    weights: Optional[np.ndarray] = None,
    bounds: Optional[List[Tuple[float, float]]] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Levenberg-Marquardt算法参数率定
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    initial_params : np.ndarray
        初始参数值
    observed : np.ndarray
        观测值
    max_iterations : int
        最大迭代次数
    tolerance : float
        收敛容差
    lambda_init : float
        初始阻尼因子
    lambda_factor : float
        阻尼因子调整系数
    weights : np.ndarray, optional
        观测权重
    bounds : list of tuples, optional
        参数边界
    verbose : bool
        是否输出迭代信息
        
    Returns
    -------
    dict
        优化结果
        
    Notes
    -----
    L-M算法结合了梯度下降和Gauss-Newton法：
    (J^T W J + λI) Δp = J^T W r
    
    λ大时类似梯度下降（稳定但慢）
    λ小时类似Gauss-Newton（快但可能不稳定）
    """
    params = initial_params.copy()
    lambda_current = lambda_init
    
    if weights is None:
        weights = np.ones_like(observed)
    
    W = np.diag(weights)
    
    history = {
        'parameters': [params.copy()],
        'objective': [],
        'lambda': [lambda_current]
    }
    
    # 初始目标函数
    simulated = forward_model(params)
    objective_current = compute_objective_function(observed, simulated, weights)
    history['objective'].append(objective_current)
    
    for iteration in range(max_iterations):
        residuals = observed - simulated
        
        # 计算Jacobian矩阵
        J = compute_jacobian(forward_model, params)
        
        # L-M方程：(J^T W J + λI) Δp = J^T W r
        JtWJ = J.T @ W @ J
        JtWr = J.T @ W @ residuals
        
        # 求解
        I = np.eye(len(params))
        try:
            delta_params = np.linalg.solve(JtWJ + lambda_current * I, JtWr)
        except np.linalg.LinAlgError:
            delta_params = np.linalg.lstsq(JtWJ + lambda_current * I, JtWr, rcond=None)[0]
        
        # 尝试新参数
        params_new = params + delta_params
        
        # 应用边界约束
        if bounds is not None:
            for i, (lower, upper) in enumerate(bounds):
                params_new[i] = np.clip(params_new[i], lower, upper)
        
        # 计算新的目标函数
        simulated_new = forward_model(params_new)
        objective_new = compute_objective_function(observed, simulated_new, weights)
        
        # 判断是否接受新参数
        if objective_new < objective_current:
            # 接受，减小λ
            params = params_new
            simulated = simulated_new
            objective_current = objective_new
            lambda_current /= lambda_factor
            
            if verbose and iteration % 5 == 0:
                print(f"Iteration {iteration}: Objective = {objective_current:.6e}, "
                      f"λ = {lambda_current:.6e} (decreased)")
        else:
            # 拒绝，增大λ
            lambda_current *= lambda_factor
            
            if verbose and iteration % 5 == 0:
                print(f"Iteration {iteration}: Objective = {objective_current:.6e}, "
                      f"λ = {lambda_current:.6e} (increased)")
        
        history['parameters'].append(params.copy())
        history['objective'].append(objective_current)
        history['lambda'].append(lambda_current)
        
        # 检查收敛
        param_update_norm = np.linalg.norm(delta_params)
        if param_update_norm < tolerance:
            if verbose:
                print(f"Converged at iteration {iteration}")
            break
    
    return {
        'parameters': params,
        'objective': objective_current,
        'iterations': iteration + 1,
        'history': history,
        'success': param_update_norm < tolerance
    }


def calibrate_parameters(
    forward_model: Callable,
    initial_params: np.ndarray,
    observed: np.ndarray,
    method: str = 'levenberg-marquardt',
    **kwargs
) -> Dict[str, Any]:
    """
    参数率定主函数
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    initial_params : np.ndarray
        初始参数值
    observed : np.ndarray
        观测值
    method : str
        优化方法：'gradient-descent', 'gauss-newton', 'levenberg-marquardt'
    **kwargs
        其他优化参数
        
    Returns
    -------
    dict
        优化结果
    """
    method = method.lower()
    
    if method == 'gradient-descent':
        return gradient_descent(forward_model, initial_params, observed, **kwargs)
    elif method == 'gauss-newton':
        return gauss_newton(forward_model, initial_params, observed, **kwargs)
    elif method == 'levenberg-marquardt':
        return levenberg_marquardt(forward_model, initial_params, observed, **kwargs)
    else:
        raise ValueError(f"Unknown method: {method}. "
                        f"Choose from 'gradient-descent', 'gauss-newton', 'levenberg-marquardt'")
