"""
PEST风格参数率定模块

实现类似PEST（Parameter ESTimation）的率定框架
包括：
- 参数组管理
- 观测组管理
- SVD辅助参数估计
- Tikhonov正则化
"""

import numpy as np
from typing import Callable, Dict, List, Tuple, Optional, Any
from scipy.linalg import svd


class ParameterGroup:
    """参数组类"""
    
    def __init__(
        self,
        name: str,
        parameters: List[str],
        initial_values: np.ndarray,
        lower_bounds: np.ndarray,
        upper_bounds: np.ndarray,
        transform: str = 'none',
        scale_factor: float = 1.0
    ):
        """
        初始化参数组
        
        Parameters
        ----------
        name : str
            参数组名称
        parameters : list of str
            参数名称列表
        initial_values : np.ndarray
            初始值
        lower_bounds : np.ndarray
            下界
        upper_bounds : np.ndarray
            上界
        transform : str
            变换类型：'none', 'log', 'fixed'
        scale_factor : float
            缩放因子
        """
        self.name = name
        self.parameters = parameters
        self.initial_values = initial_values.copy()
        self.lower_bounds = lower_bounds.copy()
        self.upper_bounds = upper_bounds.copy()
        self.transform = transform
        self.scale_factor = scale_factor
        self.n_params = len(parameters)
        
    def to_model_space(self, transformed_values: np.ndarray) -> np.ndarray:
        """从变换空间到模型空间"""
        if self.transform == 'log':
            return np.exp(transformed_values)
        elif self.transform == 'none':
            return transformed_values
        elif self.transform == 'fixed':
            return self.initial_values
        else:
            return transformed_values
    
    def to_transform_space(self, model_values: np.ndarray) -> np.ndarray:
        """从模型空间到变换空间"""
        if self.transform == 'log':
            return np.log(model_values)
        elif self.transform == 'none':
            return model_values
        elif self.transform == 'fixed':
            return self.initial_values
        else:
            return model_values


class ObservationGroup:
    """观测组类"""
    
    def __init__(
        self,
        name: str,
        observations: np.ndarray,
        weights: Optional[np.ndarray] = None,
        group_weight: float = 1.0
    ):
        """
        初始化观测组
        
        Parameters
        ----------
        name : str
            观测组名称
        observations : np.ndarray
            观测值
        weights : np.ndarray, optional
            观测权重
        group_weight : float
            组权重
        """
        self.name = name
        self.observations = observations.copy()
        self.n_obs = len(observations)
        
        if weights is None:
            self.weights = np.ones(self.n_obs) * group_weight
        else:
            self.weights = weights * group_weight


def svd_assist(
    jacobian: np.ndarray,
    residuals: np.ndarray,
    weights: np.ndarray,
    n_components: Optional[int] = None,
    eigenvalue_threshold: float = 1e-6
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    SVD辅助参数估计
    
    Parameters
    ----------
    jacobian : np.ndarray
        Jacobian矩阵
    residuals : np.ndarray
        残差向量
    weights : np.ndarray
        权重
    n_components : int, optional
        保留的奇异值数量
    eigenvalue_threshold : float
        特征值阈值
        
    Returns
    -------
    delta_params : np.ndarray
        参数更新
    info : dict
        SVD信息
        
    Notes
    -----
    SVD分解：J = U Σ V^T
    参数更新：Δp = V Σ^{-1} U^T W r
    
    保留主要奇异值，避免小特征值引起的不稳定
    """
    # 加权Jacobian矩阵
    W_sqrt = np.diag(np.sqrt(weights))
    J_weighted = W_sqrt @ jacobian
    r_weighted = W_sqrt @ residuals
    
    # SVD分解
    U, s, Vt = svd(J_weighted, full_matrices=False)
    
    # 确定保留的奇异值数量
    if n_components is None:
        # 基于阈值自动确定
        n_components = np.sum(s > eigenvalue_threshold * s[0])
    
    n_components = min(n_components, len(s))
    
    # 保留主要成分
    U_trunc = U[:, :n_components]
    s_trunc = s[:n_components]
    Vt_trunc = Vt[:n_components, :]
    
    # 计算参数更新
    s_inv = 1.0 / s_trunc
    delta_params = Vt_trunc.T @ (s_inv * (U_trunc.T @ r_weighted))
    
    # 计算条件数
    condition_number = s[0] / s[-1] if len(s) > 0 else np.inf
    condition_number_truncated = s_trunc[0] / s_trunc[-1] if len(s_trunc) > 0 else np.inf
    
    info = {
        'singular_values': s,
        'n_components': n_components,
        'condition_number': condition_number,
        'condition_number_truncated': condition_number_truncated,
        'explained_variance_ratio': np.sum(s_trunc**2) / np.sum(s**2)
    }
    
    return delta_params, info


def tikhonov_regularization(
    jacobian: np.ndarray,
    residuals: np.ndarray,
    weights: np.ndarray,
    alpha: float = 0.01,
    prior_params: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Tikhonov正则化
    
    Parameters
    ----------
    jacobian : np.ndarray
        Jacobian矩阵
    residuals : np.ndarray
        残差向量
    weights : np.ndarray
        权重
    alpha : float
        正则化参数
    prior_params : np.ndarray, optional
        先验参数值
        
    Returns
    -------
    np.ndarray
        参数更新
        
    Notes
    -----
    正则化目标函数：
    Φ_reg = ||W^{1/2}(h_obs - h_sim)||² + α²||p - p_prior||²
    
    正规方程：
    (J^T W J + α²I) Δp = J^T W r + α²(p_prior - p_current)
    """
    W = np.diag(weights)
    JtWJ = jacobian.T @ W @ jacobian
    JtWr = jacobian.T @ W @ residuals
    
    n_params = jacobian.shape[1]
    I = np.eye(n_params)
    
    # Tikhonov矩阵
    A = JtWJ + alpha**2 * I
    
    # 右端项
    if prior_params is not None:
        # 假设当前参数为0（相对更新）
        b = JtWr + alpha**2 * prior_params
    else:
        b = JtWr
    
    # 求解
    try:
        delta_params = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        delta_params = np.linalg.lstsq(A, b, rcond=None)[0]
    
    return delta_params


def pest_calibrate(
    forward_model: Callable,
    param_groups: List[ParameterGroup],
    obs_groups: List[ObservationGroup],
    method: str = 'svd',
    max_iterations: int = 30,
    tolerance: float = 1e-4,
    svd_components: Optional[int] = None,
    regularization_alpha: float = 0.0,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    PEST风格参数率定
    
    Parameters
    ----------
    forward_model : callable
        正演模型，输入参数字典，返回模拟观测字典
    param_groups : list of ParameterGroup
        参数组列表
    obs_groups : list of ObservationGroup
        观测组列表
    method : str
        方法：'svd'（SVD辅助）或 'lm'（Levenberg-Marquardt）
    max_iterations : int
        最大迭代次数
    tolerance : float
        收敛容差
    svd_components : int, optional
        SVD保留的成分数
    regularization_alpha : float
        正则化参数
    verbose : bool
        输出详细信息
        
    Returns
    -------
    dict
        率定结果
    """
    # 初始化参数
    all_params = []
    param_names = []
    for group in param_groups:
        all_params.extend(group.initial_values)
        param_names.extend(group.parameters)
    
    params = np.array(all_params)
    n_params = len(params)
    
    # 收集所有观测
    all_observations = []
    all_weights = []
    for group in obs_groups:
        all_observations.extend(group.observations)
        all_weights.extend(group.weights)
    
    observations = np.array(all_observations)
    weights = np.array(all_weights)
    n_obs = len(observations)
    
    # 优化历史
    history = {
        'parameters': [params.copy()],
        'objective': [],
        'svd_info': [] if method == 'svd' else None
    }
    
    # Levenberg-Marquardt参数
    lambda_lm = 0.01 if method == 'lm' else None
    
    if verbose:
        print(f"开始PEST率定")
        print(f"  参数数量: {n_params}")
        print(f"  观测数量: {n_obs}")
        print(f"  方法: {method.upper()}")
        print(f"  正则化: {'是' if regularization_alpha > 0 else '否'}")
        print()
    
    for iteration in range(max_iterations):
        # 正演模拟
        simulated = forward_model(params)
        residuals = observations - simulated
        
        # 计算目标函数
        objective = np.sum(weights * residuals**2)
        history['objective'].append(objective)
        
        if verbose and iteration % 5 == 0:
            rmse = np.sqrt(objective / n_obs)
            print(f"迭代 {iteration}: Φ = {objective:.6e}, RMSE = {rmse:.6e}")
        
        # 计算Jacobian矩阵（有限差分）
        jacobian = np.zeros((n_obs, n_params))
        delta = 1e-6
        
        for j in range(n_params):
            params_perturbed = params.copy()
            delta_p = delta * max(abs(params[j]), 1.0)
            params_perturbed[j] += delta_p
            
            sim_perturbed = forward_model(params_perturbed)
            jacobian[:, j] = (sim_perturbed - simulated) / delta_p
        
        # 计算参数更新
        if method == 'svd':
            # SVD辅助方法
            if regularization_alpha > 0:
                delta_params = tikhonov_regularization(
                    jacobian, residuals, weights, regularization_alpha
                )
                svd_info = {'method': 'tikhonov'}
            else:
                delta_params, svd_info = svd_assist(
                    jacobian, residuals, weights,
                    n_components=svd_components
                )
                history['svd_info'].append(svd_info)
                
                if verbose and iteration % 5 == 0:
                    print(f"  SVD成分: {svd_info['n_components']}, "
                          f"条件数: {svd_info['condition_number_truncated']:.2e}")
        
        elif method == 'lm':
            # Levenberg-Marquardt方法
            W = np.diag(weights)
            JtWJ = jacobian.T @ W @ jacobian
            JtWr = jacobian.T @ W @ residuals
            
            I = np.eye(n_params)
            try:
                delta_params = np.linalg.solve(JtWJ + lambda_lm * I, JtWr)
            except np.linalg.LinAlgError:
                delta_params = np.linalg.lstsq(JtWJ + lambda_lm * I, JtWr, rcond=None)[0]
            
            # 尝试新参数
            params_new = params + delta_params
            sim_new = forward_model(params_new)
            obj_new = np.sum(weights * (observations - sim_new)**2)
            
            if obj_new < objective:
                lambda_lm /= 10.0
            else:
                lambda_lm *= 10.0
                delta_params = np.zeros_like(delta_params)  # 拒绝更新
        
        # 检查收敛
        param_update_norm = np.linalg.norm(delta_params) / max(np.linalg.norm(params), 1.0)
        if param_update_norm < tolerance:
            if verbose:
                print(f"\n收敛于迭代 {iteration}")
            break
        
        # 更新参数
        params = params + delta_params
        
        # 应用边界约束
        idx = 0
        for group in param_groups:
            for i in range(group.n_params):
                params[idx] = np.clip(
                    params[idx],
                    group.lower_bounds[i],
                    group.upper_bounds[i]
                )
                idx += 1
        
        history['parameters'].append(params.copy())
    
    # 构建结果字典
    results = {}
    idx = 0
    for group in param_groups:
        group_params = {}
        for i, pname in enumerate(group.parameters):
            group_params[pname] = params[idx]
            idx += 1
        results[group.name] = group_params
    
    return {
        'parameters': results,
        'parameter_vector': params,
        'objective': objective,
        'iterations': iteration + 1,
        'history': history,
        'success': param_update_norm < tolerance,
        'n_parameters': n_params,
        'n_observations': n_obs
    }
