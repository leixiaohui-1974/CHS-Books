"""
采样方法模块

提供多种空间填充设计（Space-Filling Design）方法用于生成训练数据。

采样方法对比:
-----------
1. 随机采样: 简单但可能分布不均
2. 均匀网格: 覆盖完整但维度灾难
3. 拉丁超立方 (LHS): 平衡覆盖与样本量
4. Sobol序列: 低差异序列，分布均匀

本模块实现LHS和Sobol采样，适用于代理模型训练数据生成。
"""

import numpy as np
from typing import Tuple, Union, List
from scipy.stats import qmc


def latin_hypercube_sampling(
    n_samples: int,
    n_dims: int,
    bounds: Union[np.ndarray, List[Tuple[float, float]]],
    seed: int = 42
) -> np.ndarray:
    """
    拉丁超立方采样 (Latin Hypercube Sampling, LHS)
    
    LHS确保每个输入维度被均匀采样，避免采样空洞。
    
    Parameters
    ----------
    n_samples : int
        采样点数
    n_dims : int
        维度数
    bounds : array-like
        每个维度的边界 [(min1, max1), (min2, max2), ...]
    seed : int
        随机种子
    
    Returns
    -------
    samples : np.ndarray
        采样点 (n_samples × n_dims)
    
    Examples
    --------
    >>> bounds = [(0, 1), (0, 10), (5, 15)]
    >>> samples = latin_hypercube_sampling(100, 3, bounds)
    >>> samples.shape
    (100, 3)
    """
    # 转换bounds
    bounds = np.array(bounds)
    lower_bounds = bounds[:, 0]
    upper_bounds = bounds[:, 1]
    
    # 使用scipy的LHS
    sampler = qmc.LatinHypercube(d=n_dims, seed=seed)
    samples_unit = sampler.random(n=n_samples)
    
    # 缩放到实际范围
    samples = qmc.scale(samples_unit, lower_bounds, upper_bounds)
    
    return samples


def sobol_sampling(
    n_samples: int,
    n_dims: int,
    bounds: Union[np.ndarray, List[Tuple[float, float]]],
    seed: int = 42
) -> np.ndarray:
    """
    Sobol序列采样
    
    Sobol序列是一种低差异序列（Low-Discrepancy Sequence），
    比随机采样更均匀地覆盖空间。
    
    Parameters
    ----------
    n_samples : int
        采样点数
    n_dims : int
        维度数
    bounds : array-like
        每个维度的边界
    seed : int
        随机种子
    
    Returns
    -------
    samples : np.ndarray
        采样点 (n_samples × n_dims)
    
    Examples
    --------
    >>> bounds = [(0, 1), (0, 10)]
    >>> samples = sobol_sampling(128, 2, bounds)
    >>> samples.shape
    (128, 2)
    
    Notes
    -----
    Sobol序列最好使用2的幂次方个样本点 (如64, 128, 256)。
    """
    # 转换bounds
    bounds = np.array(bounds)
    lower_bounds = bounds[:, 0]
    upper_bounds = bounds[:, 1]
    
    # 使用scipy的Sobol
    sampler = qmc.Sobol(d=n_dims, seed=seed)
    samples_unit = sampler.random(n=n_samples)
    
    # 缩放到实际范围
    samples = qmc.scale(samples_unit, lower_bounds, upper_bounds)
    
    return samples


def random_sampling(
    n_samples: int,
    n_dims: int,
    bounds: Union[np.ndarray, List[Tuple[float, float]]],
    seed: int = 42
) -> np.ndarray:
    """
    均匀随机采样
    
    Parameters
    ----------
    n_samples : int
        采样点数
    n_dims : int
        维度数
    bounds : array-like
        每个维度的边界
    seed : int
        随机种子
    
    Returns
    -------
    samples : np.ndarray
        采样点 (n_samples × n_dims)
    """
    np.random.seed(seed)
    
    bounds = np.array(bounds)
    lower_bounds = bounds[:, 0]
    upper_bounds = bounds[:, 1]
    
    samples = np.random.uniform(
        low=lower_bounds,
        high=upper_bounds,
        size=(n_samples, n_dims)
    )
    
    return samples


def plot_sampling_comparison(
    methods: List[str],
    n_samples: int = 100,
    bounds: List[Tuple[float, float]] = [(0, 1), (0, 1)],
    seed: int = 42
):
    """
    可视化不同采样方法的对比
    
    Parameters
    ----------
    methods : List[str]
        采样方法列表，如['random', 'lhs', 'sobol']
    n_samples : int
        每种方法的采样点数
    bounds : List[Tuple]
        采样边界（2D）
    seed : int
        随机种子
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        图形对象
    """
    import matplotlib.pyplot as plt
    
    n_methods = len(methods)
    fig, axes = plt.subplots(1, n_methods, figsize=(6*n_methods, 5))
    if n_methods == 1:
        axes = [axes]
    
    for ax, method in zip(axes, methods):
        if method == 'random':
            samples = random_sampling(n_samples, 2, bounds, seed)
            title = '随机采样'
        elif method == 'lhs':
            samples = latin_hypercube_sampling(n_samples, 2, bounds, seed)
            title = '拉丁超立方采样 (LHS)'
        elif method == 'sobol':
            samples = sobol_sampling(n_samples, 2, bounds, seed)
            title = 'Sobol序列采样'
        else:
            raise ValueError(f"未知方法: {method}")
        
        ax.scatter(samples[:, 0], samples[:, 1], alpha=0.6, 
                  edgecolors='k', linewidths=0.5, s=30)
        ax.set_xlabel('维度 1')
        ax.set_ylabel('维度 2')
        ax.set_title(f'{title}\n({n_samples} 个样本点)')
        ax.set_xlim(bounds[0])
        ax.set_ylim(bounds[1])
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def compute_discrepancy(samples: np.ndarray) -> float:
    """
    计算采样点的差异度（Discrepancy）
    
    差异度衡量采样点分布的均匀性，越小越好。
    
    Parameters
    ----------
    samples : np.ndarray
        采样点 (n_samples × n_dims)，应在[0, 1]^d单位超立方体中
    
    Returns
    -------
    discrepancy : float
        星形差异度 (Star Discrepancy)
    
    Notes
    -----
    使用Wrap-around L2-discrepancy的简化估计。
    """
    n_samples, n_dims = samples.shape
    
    # 计算所有样本对之间的距离
    pairwise_prod = np.prod(
        1 + 0.5 * np.abs(samples[:, None, :] - 0.5) +
        0.5 * np.abs(samples[None, :, :] - 0.5) -
        0.5 * np.abs(samples[:, None, :] - samples[None, :, :]),
        axis=2
    )
    
    term1 = (13/12) ** n_dims
    term2 = (2 / n_samples) * np.sum(
        np.prod(1 + 0.5 * np.abs(samples - 0.5), axis=1)
    )
    term3 = (1 / n_samples**2) * np.sum(pairwise_prod)
    
    discrepancy = np.sqrt(term1 - term2 + term3)
    
    return discrepancy
