"""
全局敏感性分析模块

实现全局敏感性分析方法：
- Sobol敏感性指数
- Morris筛选法
- 参数交互作用分析
"""

import numpy as np
from typing import Callable, Dict, List, Tuple, Optional, Any
from itertools import combinations


def sobol_sequence(n_samples: int, n_params: int) -> np.ndarray:
    """
    生成Sobol准随机序列（简化版）
    
    Parameters
    ----------
    n_samples : int
        样本数
    n_params : int
        参数数
        
    Returns
    -------
    np.ndarray
        Sobol序列 (n_samples × n_params)
        
    Notes
    -----
    这是一个简化的实现。实际应用建议使用scipy.stats.qmc.Sobol
    """
    # 简化：使用分层拉丁超立方采样近似
    samples = np.zeros((n_samples, n_params))
    
    for i in range(n_params):
        # 分层采样
        intervals = np.linspace(0, 1, n_samples + 1)
        for j in range(n_samples):
            samples[j, i] = np.random.uniform(intervals[j], intervals[j + 1])
    
    # 随机置换
    for i in range(n_params):
        samples[:, i] = np.random.permutation(samples[:, i])
    
    return samples


def sample_sobol_matrices(
    n_samples: int,
    n_params: int,
    bounds: List[Tuple[float, float]]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    为Sobol分析生成采样矩阵
    
    Parameters
    ----------
    n_samples : int
        基础样本数
    n_params : int
        参数数
    bounds : list of tuples
        参数边界
        
    Returns
    -------
    A, B : np.ndarray
        两个独立的采样矩阵
        
    Notes
    -----
    Sobol分析需要两个独立的采样矩阵A和B
    """
    # 生成两个独立的样本矩阵
    A = sobol_sequence(n_samples, n_params)
    B = sobol_sequence(n_samples, n_params)
    
    # 缩放到参数范围
    for i, (lower, upper) in enumerate(bounds):
        A[:, i] = lower + A[:, i] * (upper - lower)
        B[:, i] = lower + B[:, i] * (upper - lower)
    
    return A, B


def compute_sobol_indices(
    forward_model: Callable,
    bounds: List[Tuple[float, float]],
    n_samples: int = 1000,
    calc_second_order: bool = False,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    计算Sobol敏感性指数
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    bounds : list of tuples
        参数边界
    n_samples : int
        采样数量
    calc_second_order : bool
        是否计算二阶交互指数
    verbose : bool
        输出详细信息
        
    Returns
    -------
    dict
        包含Sobol指数的字典
        
    Notes
    -----
    一阶指数 S_i: 参数i的主效应
    总效应指数 ST_i: 参数i的总效应（包括交互）
    二阶指数 S_ij: 参数i和j的交互效应
    """
    n_params = len(bounds)
    
    if verbose:
        print(f"计算Sobol敏感性指数...")
        print(f"  参数数: {n_params}")
        print(f"  采样数: {n_samples}")
        print(f"  总模型运行次数: {n_samples * (2 + n_params)}")
    
    # 生成采样矩阵
    A, B = sample_sobol_matrices(n_samples, n_params, bounds)
    
    # 运行模型
    if verbose:
        print(f"\n运行模型...")
    
    f_A = np.array([forward_model(A[i]) for i in range(n_samples)])
    f_B = np.array([forward_model(B[i]) for i in range(n_samples)])
    
    # 如果模型返回多个输出，取第一个或均值
    if len(f_A.shape) > 1:
        f_A = np.mean(f_A, axis=1)
        f_B = np.mean(f_B, axis=1)
    
    # 计算C_i矩阵（第i列从B取，其余从A取）
    f_C = np.zeros((n_samples, n_params))
    for i in range(n_params):
        C_i = A.copy()
        C_i[:, i] = B[:, i]
        f_C[:, i] = np.array([forward_model(C_i[j]) for j in range(n_samples)])
        if len(f_C.shape) > 2:
            f_C[:, i] = np.mean(f_C[:, i], axis=1)
    
    # 计算方差
    f0 = np.mean(np.concatenate([f_A, f_B]))
    V = np.var(np.concatenate([f_A, f_B]))
    
    # 一阶敏感性指数
    S_first = np.zeros(n_params)
    for i in range(n_params):
        S_first[i] = (np.mean(f_B * (f_C[:, i] - f_A))) / V
    
    # 总效应敏感性指数
    S_total = np.zeros(n_params)
    for i in range(n_params):
        S_total[i] = 1 - (np.mean(f_A * (f_C[:, i] - f_B))) / V
    
    result = {
        'S_first': S_first,
        'S_total': S_total,
        'variance': V,
        'mean': f0,
        'n_samples': n_samples,
        'n_params': n_params
    }
    
    # 二阶交互指数（可选）
    if calc_second_order:
        if verbose:
            print(f"\n计算二阶交互指数...")
        
        S_second = np.zeros((n_params, n_params))
        for i, j in combinations(range(n_params), 2):
            C_ij = A.copy()
            C_ij[:, i] = B[:, i]
            C_ij[:, j] = B[:, j]
            f_C_ij = np.array([forward_model(C_ij[k]) for k in range(n_samples)])
            if len(f_C_ij.shape) > 1:
                f_C_ij = np.mean(f_C_ij, axis=1)
            
            S_second[i, j] = (np.mean(f_B * (f_C_ij - f_A))) / V - S_first[i] - S_first[j]
            S_second[j, i] = S_second[i, j]
        
        result['S_second'] = S_second
    
    if verbose:
        print(f"\n一阶指数（主效应）:")
        for i in range(n_params):
            print(f"  S{i+1} = {S_first[i]:.4f}")
        
        print(f"\n总效应指数:")
        for i in range(n_params):
            print(f"  ST{i+1} = {S_total[i]:.4f}")
        
        print(f"\n交互效应指数:")
        for i in range(n_params):
            interaction = S_total[i] - S_first[i]
            print(f"  I{i+1} = ST{i+1} - S{i+1} = {interaction:.4f}")
    
    return result


def morris_screening(
    forward_model: Callable,
    bounds: List[Tuple[float, float]],
    n_trajectories: int = 10,
    n_levels: int = 4,
    delta: float = 0.5,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Morris筛选法（OAT - One-At-a-Time）
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    bounds : list of tuples
        参数边界
    n_trajectories : int
        轨迹数量
    n_levels : int
        每个参数的离散化水平数
    delta : float
        参数扰动步长（相对于范围）
    verbose : bool
        输出详细信息
        
    Returns
    -------
    dict
        Morris分析结果
        
    Notes
    -----
    Morris方法特点：
    - 计算效率高
    - 用于参数筛选
    - 识别重要和不重要参数
    - 检测非线性和交互作用
    
    输出指标：
    - μ: 均值（主效应）
    - μ*: 绝对均值（考虑方向）
    - σ: 标准差（非线性/交互）
    """
    n_params = len(bounds)
    
    if verbose:
        print(f"Morris筛选法...")
        print(f"  参数数: {n_params}")
        print(f"  轨迹数: {n_trajectories}")
        print(f"  水平数: {n_levels}")
        print(f"  总运行次数: {n_trajectories * (n_params + 1)}")
    
    # 存储基本效应
    elementary_effects = np.zeros((n_trajectories, n_params))
    
    for traj in range(n_trajectories):
        # 生成一条随机轨迹
        # 起始点
        x0 = np.array([np.random.choice(np.linspace(lower, upper, n_levels))
                      for lower, upper in bounds])
        
        # 随机排列参数顺序
        param_order = np.random.permutation(n_params)
        
        # 计算基线输出
        y0 = forward_model(x0)
        if hasattr(y0, '__len__'):
            y0 = np.mean(y0)
        
        x_current = x0.copy()
        y_current = y0
        
        # 沿轨迹逐个改变参数
        for i, param_idx in enumerate(param_order):
            # 计算扰动量
            lower, upper = bounds[param_idx]
            delta_abs = delta * (upper - lower)
            
            # 扰动参数
            x_new = x_current.copy()
            # 确保不超出边界
            if x_current[param_idx] + delta_abs <= upper:
                x_new[param_idx] = x_current[param_idx] + delta_abs
            else:
                x_new[param_idx] = x_current[param_idx] - delta_abs
            
            # 计算新输出
            y_new = forward_model(x_new)
            if hasattr(y_new, '__len__'):
                y_new = np.mean(y_new)
            
            # 基本效应
            ee = (y_new - y_current) / delta_abs
            elementary_effects[traj, param_idx] = ee
            
            # 更新当前点
            x_current = x_new
            y_current = y_new
    
    # 计算Morris指标
    mu = np.mean(elementary_effects, axis=0)          # 均值
    mu_star = np.mean(np.abs(elementary_effects), axis=0)  # 绝对均值
    sigma = np.std(elementary_effects, axis=0)        # 标准差
    
    if verbose:
        print(f"\nMorris指标:")
        print(f"{'参数':<10} {'μ':<12} {'μ*':<12} {'σ':<12} {'重要性':<10}")
        print("-" * 60)
        
        for i in range(n_params):
            importance = "高" if mu_star[i] > np.median(mu_star) else "低"
            print(f"参数{i+1:<6} {mu[i]:<12.4f} {mu_star[i]:<12.4f} "
                  f"{sigma[i]:<12.4f} {importance:<10}")
    
    return {
        'mu': mu,
        'mu_star': mu_star,
        'sigma': sigma,
        'elementary_effects': elementary_effects,
        'n_trajectories': n_trajectories,
        'n_params': n_params
    }


def interaction_analysis(
    forward_model: Callable,
    bounds: List[Tuple[float, float]],
    n_samples: int = 100,
    param_pairs: Optional[List[Tuple[int, int]]] = None
) -> Dict[str, Any]:
    """
    参数交互作用分析
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    bounds : list of tuples
        参数边界
    n_samples : int
        每对参数的采样数
    param_pairs : list of tuples, optional
        要分析的参数对索引，默认分析所有对
        
    Returns
    -------
    dict
        交互作用分析结果
    """
    n_params = len(bounds)
    
    if param_pairs is None:
        param_pairs = list(combinations(range(n_params), 2))
    
    interaction_strength = {}
    
    for i, j in param_pairs:
        # 在其他参数中点固定，变化i和j
        base_params = np.array([(lower + upper) / 2 for lower, upper in bounds])
        
        # 创建网格
        p_i = np.linspace(bounds[i][0], bounds[i][1], n_samples)
        p_j = np.linspace(bounds[j][0], bounds[j][1], n_samples)
        
        # 计算四个角点
        corners = []
        for pi in [bounds[i][0], bounds[i][1]]:
            for pj in [bounds[j][0], bounds[j][1]]:
                params = base_params.copy()
                params[i] = pi
                params[j] = pj
                y = forward_model(params)
                if hasattr(y, '__len__'):
                    y = np.mean(y)
                corners.append(y)
        
        # 交互作用强度：(f(1,1) + f(0,0)) - (f(1,0) + f(0,1))
        interaction = (corners[3] + corners[0]) - (corners[2] + corners[1])
        
        interaction_strength[(i, j)] = interaction
    
    return {
        'interaction_strength': interaction_strength,
        'param_pairs': param_pairs
    }


def variance_based_decomposition(
    forward_model: Callable,
    bounds: List[Tuple[float, float]],
    n_samples: int = 1000
) -> Dict[str, float]:
    """
    方差分解（ANOVA分解）
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    bounds : list of tuples
        参数边界
    n_samples : int
        采样数量
        
    Returns
    -------
    dict
        方差贡献
    """
    n_params = len(bounds)
    
    # 拉丁超立方采样
    samples = np.random.rand(n_samples, n_params)
    for i, (lower, upper) in enumerate(bounds):
        samples[:, i] = lower + samples[:, i] * (upper - lower)
    
    # 运行模型
    outputs = np.array([forward_model(samples[i]) for i in range(n_samples)])
    if len(outputs.shape) > 1:
        outputs = np.mean(outputs, axis=1)
    
    # 总方差
    total_var = np.var(outputs)
    
    # 一阶方差贡献（条件期望方差）
    var_contributions = {}
    for i in range(n_params):
        # 简化计算：分组平均
        n_bins = 10
        bins = np.linspace(bounds[i][0], bounds[i][1], n_bins + 1)
        bin_means = []
        
        for b in range(n_bins):
            mask = (samples[:, i] >= bins[b]) & (samples[:, i] < bins[b + 1])
            if np.sum(mask) > 0:
                bin_means.append(np.mean(outputs[mask]))
        
        if len(bin_means) > 0:
            var_contributions[f'param_{i}'] = np.var(bin_means) / total_var
    
    return var_contributions
