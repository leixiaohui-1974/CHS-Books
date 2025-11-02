"""
贝叶斯推断模块

实现贝叶斯参数推断的各种方法：
- Metropolis-Hastings MCMC
- 后验分布估计
- 不确定性量化
- 预测分布
"""

import numpy as np
from typing import Callable, Dict, List, Tuple, Optional, Any
from scipy.stats import norm, multivariate_normal


def log_likelihood(
    observations: np.ndarray,
    simulated: np.ndarray,
    sigma: float
) -> float:
    """
    计算对数似然函数
    
    Parameters
    ----------
    observations : np.ndarray
        观测值
    simulated : np.ndarray
        模拟值
    sigma : float
        观测误差标准差
        
    Returns
    -------
    float
        对数似然值
        
    Notes
    -----
    假设观测误差为独立正态分布：
    L(θ|D) = Π N(h_obs,i | h_sim,i(θ), σ²)
    log L = -n/2 log(2πσ²) - Σ(h_obs - h_sim)²/(2σ²)
    """
    residuals = observations - simulated
    n = len(observations)
    
    # 对数似然
    log_lik = -0.5 * n * np.log(2 * np.pi * sigma**2) - \
              np.sum(residuals**2) / (2 * sigma**2)
    
    return log_lik


def log_prior_uniform(
    parameters: np.ndarray,
    bounds: List[Tuple[float, float]]
) -> float:
    """
    均匀先验的对数概率
    
    Parameters
    ----------
    parameters : np.ndarray
        参数值
    bounds : list of tuples
        参数边界
        
    Returns
    -------
    float
        对数先验概率
        
    Notes
    -----
    均匀先验：p(θ) = 1/(b-a) if a ≤ θ ≤ b, else 0
    """
    for param, (lower, upper) in zip(parameters, bounds):
        if param < lower or param > upper:
            return -np.inf
    
    # 均匀分布的对数概率（常数项）
    log_prob = -np.sum([np.log(upper - lower) for lower, upper in bounds])
    return log_prob


def log_prior_normal(
    parameters: np.ndarray,
    prior_mean: np.ndarray,
    prior_std: np.ndarray
) -> float:
    """
    正态先验的对数概率
    
    Parameters
    ----------
    parameters : np.ndarray
        参数值
    prior_mean : np.ndarray
        先验均值
    prior_std : np.ndarray
        先验标准差
        
    Returns
    -------
    float
        对数先验概率
    """
    log_prob = np.sum(norm.logpdf(parameters, loc=prior_mean, scale=prior_std))
    return log_prob


def log_posterior(
    parameters: np.ndarray,
    forward_model: Callable,
    observations: np.ndarray,
    sigma: float,
    prior_type: str = 'uniform',
    prior_params: Optional[Dict] = None
) -> float:
    """
    计算对数后验概率
    
    Parameters
    ----------
    parameters : np.ndarray
        参数值
    forward_model : callable
        正演模型
    observations : np.ndarray
        观测值
    sigma : float
        观测误差标准差
    prior_type : str
        先验类型：'uniform' 或 'normal'
    prior_params : dict
        先验参数
        
    Returns
    -------
    float
        对数后验概率
        
    Notes
    -----
    贝叶斯定理：
    p(θ|D) ∝ p(D|θ) p(θ)
    log p(θ|D) = log p(D|θ) + log p(θ) + const
    """
    # 计算先验
    if prior_type == 'uniform':
        log_prior = log_prior_uniform(parameters, prior_params['bounds'])
    elif prior_type == 'normal':
        log_prior = log_prior_normal(
            parameters,
            prior_params['mean'],
            prior_params['std']
        )
    else:
        raise ValueError(f"Unknown prior type: {prior_type}")
    
    # 先验为零（参数超出范围），直接返回
    if np.isinf(log_prior):
        return -np.inf
    
    # 计算似然
    try:
        simulated = forward_model(parameters)
        log_lik = log_likelihood(observations, simulated, sigma)
    except Exception as e:
        # 模型运行失败，返回极小概率
        return -np.inf
    
    # 后验 = 似然 + 先验
    log_post = log_lik + log_prior
    
    return log_post


def metropolis_hastings(
    forward_model: Callable,
    initial_params: np.ndarray,
    observations: np.ndarray,
    sigma: float,
    prior_type: str = 'uniform',
    prior_params: Optional[Dict] = None,
    n_iterations: int = 10000,
    proposal_std: Optional[np.ndarray] = None,
    burn_in: int = 1000,
    thin: int = 10,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Metropolis-Hastings MCMC采样
    
    Parameters
    ----------
    forward_model : callable
        正演模型
    initial_params : np.ndarray
        初始参数
    observations : np.ndarray
        观测值
    sigma : float
        观测误差标准差
    prior_type : str
        先验类型
    prior_params : dict
        先验参数
    n_iterations : int
        MCMC迭代次数
    proposal_std : np.ndarray, optional
        提议分布标准差
    burn_in : int
        燃烧期（舍弃前期样本）
    thin : int
        稀疏化（每隔thin个保留一个样本）
    verbose : bool
        输出详细信息
        
    Returns
    -------
    dict
        MCMC结果
        
    Notes
    -----
    Metropolis-Hastings算法：
    1. 从当前θ_t生成候选θ*
    2. 计算接受概率 α = min(1, p(θ*|D)/p(θ_t|D))
    3. 以概率α接受θ*，否则保留θ_t
    """
    n_params = len(initial_params)
    
    # 提议分布标准差（默认为参数初始值的10%）
    if proposal_std is None:
        proposal_std = 0.1 * np.abs(initial_params)
        proposal_std[proposal_std == 0] = 0.1
    
    # 存储MCMC链
    chain = np.zeros((n_iterations, n_params))
    log_posterior_values = np.zeros(n_iterations)
    acceptance_count = 0
    
    # 初始化
    current_params = initial_params.copy()
    current_log_posterior = log_posterior(
        current_params,
        forward_model,
        observations,
        sigma,
        prior_type,
        prior_params
    )
    
    if verbose:
        print(f"开始Metropolis-Hastings MCMC采样")
        print(f"  迭代次数: {n_iterations}")
        print(f"  参数数量: {n_params}")
        print(f"  燃烧期: {burn_in}")
        print(f"  稀疏化: {thin}")
        print(f"  初始对数后验: {current_log_posterior:.4f}")
        print()
    
    # MCMC循环
    for iteration in range(n_iterations):
        # 生成候选参数（正态提议分布）
        proposal_params = current_params + np.random.normal(0, proposal_std, n_params)
        
        # 计算候选的对数后验
        proposal_log_posterior = log_posterior(
            proposal_params,
            forward_model,
            observations,
            sigma,
            prior_type,
            prior_params
        )
        
        # 计算接受概率（对数尺度）
        log_accept_ratio = proposal_log_posterior - current_log_posterior
        
        # Metropolis-Hastings接受准则
        if log_accept_ratio > 0 or np.random.rand() < np.exp(log_accept_ratio):
            # 接受候选
            current_params = proposal_params
            current_log_posterior = proposal_log_posterior
            acceptance_count += 1
        
        # 存储当前状态
        chain[iteration, :] = current_params
        log_posterior_values[iteration] = current_log_posterior
        
        # 输出进度
        if verbose and (iteration + 1) % (n_iterations // 10) == 0:
            acceptance_rate = acceptance_count / (iteration + 1)
            print(f"迭代 {iteration + 1}/{n_iterations}: "
                  f"接受率 = {acceptance_rate:.3f}, "
                  f"对数后验 = {current_log_posterior:.4f}")
    
    # 去除燃烧期和稀疏化
    chain_burned = chain[burn_in::thin, :]
    log_posterior_burned = log_posterior_values[burn_in::thin]
    
    # 计算后验统计量
    posterior_mean = np.mean(chain_burned, axis=0)
    posterior_std = np.std(chain_burned, axis=0)
    posterior_median = np.median(chain_burned, axis=0)
    
    # 95% 置信区间
    posterior_ci_lower = np.percentile(chain_burned, 2.5, axis=0)
    posterior_ci_upper = np.percentile(chain_burned, 97.5, axis=0)
    
    acceptance_rate = acceptance_count / n_iterations
    
    if verbose:
        print(f"\nMCMC采样完成")
        print(f"  总体接受率: {acceptance_rate:.3f}")
        print(f"  有效样本数: {len(chain_burned)}")
        print(f"\n后验统计量:")
        for i in range(n_params):
            print(f"  参数{i+1}: "
                  f"均值={posterior_mean[i]:.4f}, "
                  f"标准差={posterior_std[i]:.4f}, "
                  f"95%CI=[{posterior_ci_lower[i]:.4f}, {posterior_ci_upper[i]:.4f}]")
    
    return {
        'chain': chain,
        'chain_burned': chain_burned,
        'log_posterior': log_posterior_values,
        'log_posterior_burned': log_posterior_burned,
        'posterior_mean': posterior_mean,
        'posterior_std': posterior_std,
        'posterior_median': posterior_median,
        'posterior_ci_lower': posterior_ci_lower,
        'posterior_ci_upper': posterior_ci_upper,
        'acceptance_rate': acceptance_rate,
        'n_iterations': n_iterations,
        'burn_in': burn_in,
        'thin': thin,
        'n_effective_samples': len(chain_burned)
    }


def compute_dic(
    chain: np.ndarray,
    forward_model: Callable,
    observations: np.ndarray,
    sigma: float
) -> Dict[str, float]:
    """
    计算偏差信息准则（DIC）
    
    Parameters
    ----------
    chain : np.ndarray
        MCMC链（后验样本）
    forward_model : callable
        正演模型
    observations : np.ndarray
        观测值
    sigma : float
        观测误差标准差
        
    Returns
    -------
    dict
        DIC及其组成部分
        
    Notes
    -----
    DIC = D_bar + p_D
    其中：
    - D_bar: 后验均值处的偏差
    - p_D: 有效参数数量
    
    用于模型选择，DIC越小越好
    """
    # 后验均值
    posterior_mean = np.mean(chain, axis=0)
    
    # 后验均值处的偏差
    sim_mean = forward_model(posterior_mean)
    D_theta_bar = -2 * log_likelihood(observations, sim_mean, sigma)
    
    # 每个样本的偏差
    D_samples = []
    for params in chain[::10]:  # 稀疏采样以加速
        sim = forward_model(params)
        D = -2 * log_likelihood(observations, sim, sigma)
        D_samples.append(D)
    
    D_bar = np.mean(D_samples)
    
    # 有效参数数量
    p_D = D_bar - D_theta_bar
    
    # DIC
    DIC = D_bar + p_D
    
    return {
        'DIC': DIC,
        'D_bar': D_bar,
        'D_theta_bar': D_theta_bar,
        'p_D': p_D
    }


def predictive_distribution(
    chain: np.ndarray,
    forward_model: Callable,
    sigma: float,
    n_samples: int = 1000
) -> np.ndarray:
    """
    计算预测分布
    
    Parameters
    ----------
    chain : np.ndarray
        后验样本链
    forward_model : callable
        正演模型
    sigma : float
        观测误差标准差
    n_samples : int
        预测样本数
        
    Returns
    -------
    np.ndarray
        预测样本（n_samples × n_observations）
        
    Notes
    -----
    预测分布：
    p(y_new|D) = ∫ p(y_new|θ) p(θ|D) dθ
    
    通过从后验抽样并加入观测噪声来近似
    """
    # 从后验链中随机抽取样本
    indices = np.random.choice(len(chain), n_samples, replace=True)
    
    predictions = []
    for idx in indices:
        params = chain[idx]
        # 模型预测
        y_pred = forward_model(params)
        # 加入观测噪声
        y_pred_noisy = y_pred + np.random.normal(0, sigma, len(y_pred))
        predictions.append(y_pred_noisy)
    
    return np.array(predictions)


def gelman_rubin_diagnostic(
    chains: List[np.ndarray]
) -> np.ndarray:
    """
    Gelman-Rubin收敛诊断（R-hat统计量）
    
    Parameters
    ----------
    chains : list of np.ndarray
        多条独立MCMC链
        
    Returns
    -------
    np.ndarray
        每个参数的R-hat值
        
    Notes
    -----
    R-hat ≈ 1: 收敛良好
    R-hat > 1.1: 未充分收敛
    
    需要至少2条独立链
    """
    if len(chains) < 2:
        raise ValueError("需要至少2条链进行Gelman-Rubin诊断")
    
    n_chains = len(chains)
    n_iterations = chains[0].shape[0]
    n_params = chains[0].shape[1]
    
    # 每条链的均值
    chain_means = np.array([np.mean(chain, axis=0) for chain in chains])
    
    # 总体均值
    overall_mean = np.mean(chain_means, axis=0)
    
    # 链间方差
    B = n_iterations / (n_chains - 1) * np.sum((chain_means - overall_mean)**2, axis=0)
    
    # 链内方差
    chain_vars = np.array([np.var(chain, axis=0, ddof=1) for chain in chains])
    W = np.mean(chain_vars, axis=0)
    
    # 方差估计
    var_plus = (n_iterations - 1) / n_iterations * W + B / n_iterations
    
    # R-hat
    R_hat = np.sqrt(var_plus / W)
    
    return R_hat
