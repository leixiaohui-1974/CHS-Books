"""
不确定性量化模块

实现不确定性量化的各种方法：
- Monte Carlo方法
- GLUE方法
- 置信区间估计
- 不确定性传播
"""

import numpy as np
from typing import Callable, Dict, List, Tuple, Optional, Any


def monte_carlo_uncertainty(
    forward_model: Callable,
    param_distributions: List[Tuple[str, Any]],
    n_samples: int = 1000,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Monte Carlo不确定性分析
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    param_distributions : list of tuples
        参数分布列表，格式：[('uniform', (min, max)), ('normal', (mean, std)), ...]
    n_samples : int
        Monte Carlo采样数
    verbose : bool
        输出详细信息
        
    Returns
    -------
    dict
        不确定性分析结果
    """
    n_params = len(param_distributions)
    
    if verbose:
        print(f"Monte Carlo不确定性分析...")
        print(f"  参数数: {n_params}")
        print(f"  采样数: {n_samples}")
    
    # 采样参数
    param_samples = np.zeros((n_samples, n_params))
    
    for i, (dist_type, dist_params) in enumerate(param_distributions):
        if dist_type == 'uniform':
            lower, upper = dist_params
            param_samples[:, i] = np.random.uniform(lower, upper, n_samples)
        elif dist_type == 'normal':
            mean, std = dist_params
            param_samples[:, i] = np.random.normal(mean, std, n_samples)
        elif dist_type == 'lognormal':
            mean, std = dist_params
            param_samples[:, i] = np.random.lognormal(np.log(mean), std, n_samples)
        else:
            raise ValueError(f"Unknown distribution type: {dist_type}")
    
    # 运行模型
    if verbose:
        print(f"  运行模型...")
    
    outputs = []
    for i in range(n_samples):
        try:
            output = forward_model(param_samples[i])
            outputs.append(output)
        except:
            # 模型运行失败，跳过
            outputs.append(np.nan)
    
    outputs = np.array(outputs)
    
    # 移除失败的运行
    valid_mask = ~np.isnan(outputs).any(axis=1) if len(outputs.shape) > 1 else ~np.isnan(outputs)
    outputs_valid = outputs[valid_mask]
    param_samples_valid = param_samples[valid_mask]
    
    n_valid = len(outputs_valid)
    
    if verbose:
        print(f"  有效运行: {n_valid}/{n_samples}")
    
    # 计算统计量
    if len(outputs_valid.shape) > 1:
        # 多输出
        output_mean = np.mean(outputs_valid, axis=0)
        output_std = np.std(outputs_valid, axis=0)
        output_ci_lower = np.percentile(outputs_valid, 2.5, axis=0)
        output_ci_upper = np.percentile(outputs_valid, 97.5, axis=0)
    else:
        # 单输出
        output_mean = np.mean(outputs_valid)
        output_std = np.std(outputs_valid)
        output_ci_lower = np.percentile(outputs_valid, 2.5)
        output_ci_upper = np.percentile(outputs_valid, 97.5)
    
    return {
        'param_samples': param_samples_valid,
        'outputs': outputs_valid,
        'output_mean': output_mean,
        'output_std': output_std,
        'output_ci_lower': output_ci_lower,
        'output_ci_upper': output_ci_upper,
        'n_samples': n_samples,
        'n_valid': n_valid
    }


def glue_analysis(
    forward_model: Callable,
    observations: np.ndarray,
    param_bounds: List[Tuple[float, float]],
    n_samples: int = 10000,
    likelihood_threshold: float = 0.1,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    GLUE (Generalized Likelihood Uncertainty Estimation) 分析
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    observations : np.ndarray
        观测数据
    param_bounds : list of tuples
        参数边界
    n_samples : int
        采样数
    likelihood_threshold : float
        似然函数阈值（接受行为参数集）
    verbose : bool
        输出详细信息
        
    Returns
    -------
    dict
        GLUE分析结果
        
    Notes
    -----
    GLUE步骤：
    1. 大量随机采样参数
    2. 运行模型计算似然
    3. 根据阈值接受/拒绝参数集
    4. 用接受的参数集估计不确定性
    """
    n_params = len(param_bounds)
    
    if verbose:
        print(f"GLUE分析...")
        print(f"  参数数: {n_params}")
        print(f"  采样数: {n_samples}")
        print(f"  似然阈值: {likelihood_threshold}")
    
    # 随机采样参数
    param_samples = np.random.rand(n_samples, n_params)
    for i, (lower, upper) in enumerate(param_bounds):
        param_samples[:, i] = lower + param_samples[:, i] * (upper - lower)
    
    # 计算似然
    likelihoods = np.zeros(n_samples)
    simulations = []
    
    if verbose:
        print(f"  运行模型并计算似然...")
    
    for i in range(n_samples):
        try:
            sim = forward_model(param_samples[i])
            simulations.append(sim)
            
            # Nash-Sutcliffe效率作为似然
            nse = 1 - np.sum((observations - sim)**2) / np.sum((observations - np.mean(observations))**2)
            likelihoods[i] = max(0, nse)  # 限制在[0, 1]
        except:
            simulations.append(np.nan * np.ones_like(observations))
            likelihoods[i] = 0
    
    simulations = np.array(simulations)
    
    # 识别行为参数集
    behavioral_mask = likelihoods >= likelihood_threshold
    n_behavioral = np.sum(behavioral_mask)
    
    if verbose:
        print(f"  行为参数集: {n_behavioral}/{n_samples} ({n_behavioral/n_samples*100:.1f}%)")
    
    if n_behavioral == 0:
        raise ValueError("没有找到行为参数集，尝试降低阈值或增加采样数")
    
    # 行为参数集
    behavioral_params = param_samples[behavioral_mask]
    behavioral_sims = simulations[behavioral_mask]
    behavioral_likes = likelihoods[behavioral_mask]
    
    # 加权统计量
    weights = behavioral_likes / np.sum(behavioral_likes)
    
    # 加权输出
    weighted_mean = np.average(behavioral_sims, weights=weights, axis=0)
    
    # 置信区间（基于行为参数集）
    ci_lower = np.percentile(behavioral_sims, 2.5, axis=0)
    ci_upper = np.percentile(behavioral_sims, 97.5, axis=0)
    
    return {
        'behavioral_params': behavioral_params,
        'behavioral_simulations': behavioral_sims,
        'behavioral_likelihoods': behavioral_likes,
        'weights': weights,
        'weighted_mean': weighted_mean,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'n_behavioral': n_behavioral,
        'n_total': n_samples,
        'acceptance_rate': n_behavioral / n_samples
    }


def bootstrap_uncertainty(
    forward_model: Callable,
    observations: np.ndarray,
    calibrated_params: np.ndarray,
    n_bootstrap: int = 1000,
    noise_std: Optional[float] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Bootstrap不确定性估计
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    observations : np.ndarray
        观测数据
    calibrated_params : np.ndarray
        率定后的参数
    n_bootstrap : int
        Bootstrap样本数
    noise_std : float, optional
        观测误差标准差，如果未提供则从残差估计
    verbose : bool
        输出详细信息
        
    Returns
    -------
    dict
        Bootstrap不确定性结果
    """
    if verbose:
        print(f"Bootstrap不确定性分析...")
        print(f"  Bootstrap样本数: {n_bootstrap}")
    
    # 计算残差
    sim_base = forward_model(calibrated_params)
    residuals = observations - sim_base
    
    if noise_std is None:
        noise_std = np.std(residuals)
        if verbose:
            print(f"  估计噪声标准差: {noise_std:.4f}")
    
    # Bootstrap重采样
    bootstrap_outputs = []
    
    for i in range(n_bootstrap):
        # 生成Bootstrap样本（残差重采样）
        bootstrap_residuals = np.random.choice(residuals, size=len(residuals), replace=True)
        bootstrap_obs = sim_base + bootstrap_residuals
        
        # 可以在此基础上重新率定，这里简化为直接使用
        bootstrap_outputs.append(bootstrap_obs)
    
    bootstrap_outputs = np.array(bootstrap_outputs)
    
    # 统计量
    output_mean = np.mean(bootstrap_outputs, axis=0)
    output_std = np.std(bootstrap_outputs, axis=0)
    ci_lower = np.percentile(bootstrap_outputs, 2.5, axis=0)
    ci_upper = np.percentile(bootstrap_outputs, 97.5, axis=0)
    
    return {
        'bootstrap_outputs': bootstrap_outputs,
        'output_mean': output_mean,
        'output_std': output_std,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'n_bootstrap': n_bootstrap,
        'noise_std': noise_std
    }


def propagate_uncertainty(
    forward_model: Callable,
    params_mean: np.ndarray,
    params_cov: np.ndarray,
    n_samples: int = 1000
) -> Dict[str, Any]:
    """
    不确定性传播（线性近似）
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    params_mean : np.ndarray
        参数均值
    params_cov : np.ndarray
        参数协方差矩阵
    n_samples : int
        Monte Carlo采样数
        
    Returns
    -------
    dict
        不确定性传播结果
        
    Notes
    -----
    从参数的多元正态分布采样，传播到输出
    """
    n_params = len(params_mean)
    
    # 从多元正态分布采样
    param_samples = np.random.multivariate_normal(params_mean, params_cov, n_samples)
    
    # 传播到输出
    outputs = np.array([forward_model(param_samples[i]) for i in range(n_samples)])
    
    # 统计量
    if len(outputs.shape) > 1:
        output_mean = np.mean(outputs, axis=0)
        output_cov = np.cov(outputs.T)
        output_std = np.std(outputs, axis=0)
    else:
        output_mean = np.mean(outputs)
        output_cov = np.var(outputs)
        output_std = np.std(outputs)
    
    return {
        'output_samples': outputs,
        'output_mean': output_mean,
        'output_cov': output_cov,
        'output_std': output_std
    }


def prediction_interval(
    predictions: np.ndarray,
    confidence_level: float = 0.95
) -> Tuple[np.ndarray, np.ndarray]:
    """
    计算预测区间
    
    Parameters
    ----------
    predictions : np.ndarray
        预测样本 (n_samples × n_predictions)
    confidence_level : float
        置信水平
        
    Returns
    -------
    lower, upper : np.ndarray
        预测区间下界和上界
    """
    alpha = 1 - confidence_level
    lower_percentile = 100 * alpha / 2
    upper_percentile = 100 * (1 - alpha / 2)
    
    lower = np.percentile(predictions, lower_percentile, axis=0)
    upper = np.percentile(predictions, upper_percentile, axis=0)
    
    return lower, upper


def uncertainty_decomposition(
    param_uncertainty_contribution: np.ndarray,
    obs_noise_std: float,
    model_outputs: np.ndarray
) -> Dict[str, float]:
    """
    不确定性分解
    
    Parameters
    ----------
    param_uncertainty_contribution : np.ndarray
        参数不确定性对输出的贡献
    obs_noise_std : float
        观测噪声标准差
    model_outputs : np.ndarray
        模型输出
        
    Returns
    -------
    dict
        不确定性分量
        
    Notes
    -----
    总不确定性 = 参数不确定性 + 观测误差 + 模型误差
    """
    # 参数不确定性
    param_var = np.var(param_uncertainty_contribution)
    
    # 观测误差
    obs_var = obs_noise_std**2
    
    # 总方差
    total_var = np.var(model_outputs)
    
    # 模型误差（残差）
    model_var = max(0, total_var - param_var - obs_var)
    
    return {
        'parameter_uncertainty': param_var,
        'observation_uncertainty': obs_var,
        'model_uncertainty': model_var,
        'total_uncertainty': total_var,
        'param_fraction': param_var / total_var if total_var > 0 else 0,
        'obs_fraction': obs_var / total_var if total_var > 0 else 0,
        'model_fraction': model_var / total_var if total_var > 0 else 0
    }
