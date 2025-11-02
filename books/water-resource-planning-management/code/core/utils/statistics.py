"""
统计分析工具

提供水文统计分析的常用函数
"""

import numpy as np
from scipy import stats, optimize
from typing import Dict, Tuple, Optional
import warnings


def calculate_statistics(data: np.ndarray) -> Dict[str, float]:
    """
    计算基本统计量
    
    Parameters
    ----------
    data : np.ndarray
        数据序列
    
    Returns
    -------
    Dict[str, float]
        统计量字典，包含：
        - mean: 均值
        - std: 标准差
        - cv: 变差系数
        - cs: 偏态系数
        - min: 最小值
        - max: 最大值
        - median: 中位数
    
    Examples
    --------
    >>> data = np.array([100, 120, 90, 110, 95])
    >>> stats = calculate_statistics(data)
    >>> print(f"均值: {stats['mean']:.2f}")
    """
    data = np.array(data)
    data = data[~np.isnan(data)]  # 移除NaN值
    
    if len(data) == 0:
        raise ValueError("数据为空")
    
    mean_val = np.mean(data)
    std_val = np.std(data, ddof=1)  # 样本标准差
    
    return {
        "mean": mean_val,
        "std": std_val,
        "cv": std_val / mean_val if mean_val != 0 else 0,  # 变差系数
        "cs": stats.skew(data, bias=False),  # 偏态系数
        "min": np.min(data),
        "max": np.max(data),
        "median": np.median(data),
        "q25": np.percentile(data, 25),
        "q75": np.percentile(data, 75),
    }


def pearson_iii_distribution(
    data: np.ndarray,
) -> Tuple[float, float, float]:
    """
    拟合Pearson III型分布（P-III）
    
    在水文频率分析中广泛应用
    
    Parameters
    ----------
    data : np.ndarray
        数据序列
    
    Returns
    -------
    Tuple[float, float, float]
        (均值, 变差系数Cv, 偏态系数Cs)
    
    Examples
    --------
    >>> data = np.array([100, 120, 90, 110, 95, 105, 115])
    >>> mean, cv, cs = pearson_iii_distribution(data)
    >>> print(f"均值={mean:.2f}, Cv={cv:.3f}, Cs={cs:.3f}")
    """
    data = np.array(data)
    data = data[~np.isnan(data)]
    
    if len(data) < 3:
        raise ValueError("数据点数不足，至少需要3个数据点")
    
    # 计算统计参数
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    cv = std / mean
    cs = stats.skew(data, bias=False)
    
    return mean, cv, cs


def frequency_analysis(
    data: np.ndarray,
    probabilities: Optional[np.ndarray] = None,
    distribution: str = "pearson3"
) -> Tuple[np.ndarray, np.ndarray]:
    """
    频率分析
    
    Parameters
    ----------
    data : np.ndarray
        数据序列
    probabilities : np.ndarray, optional
        超过概率序列，如[0.01, 0.05, 0.10, 0.20, 0.50, 0.75, 0.90, 0.95, 0.99]
        如果为None，则使用默认值
    distribution : str, optional
        分布类型，默认为'pearson3'（P-III型）
        支持：'pearson3', 'lognorm', 'gamma'
    
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (超过概率, 对应的设计值)
    
    Examples
    --------
    >>> data = np.random.lognormal(4.5, 0.5, 50)  # 模拟50年径流数据
    >>> p, q = frequency_analysis(data, probabilities=[0.5, 0.75, 0.95])
    >>> for pi, qi in zip(p, q):
    ...     print(f"P={pi*100:.0f}%: Q={qi:.2f}")
    """
    data = np.array(data)
    data = data[~np.isnan(data)]
    
    if probabilities is None:
        # 默认的超过概率
        probabilities = np.array([0.01, 0.05, 0.10, 0.20, 0.50, 0.75, 0.90, 0.95, 0.99])
    else:
        probabilities = np.array(probabilities)
    
    # 拟合分布
    if distribution == "pearson3":
        # Pearson III型分布
        mean, cv, cs = pearson_iii_distribution(data)
        
        # 计算设计值
        design_values = []
        for p in probabilities:
            # 使用Pearson III型的分位数计算
            # 这里使用gamma分布近似（Pearson III是gamma的推广）
            if cs > 0:
                # 正偏
                shape = 4 / cs ** 2
                scale = mean * cs ** 2 / 2
                loc = mean * (1 - 2 / cs ** 2)
                design_value = stats.gamma.ppf(1 - p, shape, loc=loc, scale=scale)
            else:
                # 使用正态分布近似
                design_value = stats.norm.ppf(1 - p, loc=mean, scale=mean * cv)
            
            design_values.append(design_value)
        
        design_values = np.array(design_values)
    
    elif distribution == "lognorm":
        # 对数正态分布
        shape, loc, scale = stats.lognorm.fit(data, floc=0)
        design_values = stats.lognorm.ppf(1 - probabilities, shape, loc=loc, scale=scale)
    
    elif distribution == "gamma":
        # Gamma分布
        shape, loc, scale = stats.gamma.fit(data)
        design_values = stats.gamma.ppf(1 - probabilities, shape, loc=loc, scale=scale)
    
    else:
        raise ValueError(f"不支持的分布类型: {distribution}")
    
    return probabilities, design_values


def calculate_exceedance_probability(
    data: np.ndarray,
    method: str = "weibull"
) -> Tuple[np.ndarray, np.ndarray]:
    """
    计算经验超过概率
    
    Parameters
    ----------
    data : np.ndarray
        数据序列
    method : str, optional
        计算方法，默认为'weibull'
        支持：'weibull', 'hazen', 'california'
    
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (排序后的数据, 对应的超过概率)
    
    Examples
    --------
    >>> data = np.array([100, 120, 90, 110, 95])
    >>> sorted_data, probs = calculate_exceedance_probability(data)
    >>> for x, p in zip(sorted_data, probs):
    ...     print(f"X={x:.1f}, P={p:.3f}")
    """
    data = np.array(data)
    data = data[~np.isnan(data)]
    
    # 从大到小排序
    sorted_data = np.sort(data)[::-1]
    n = len(sorted_data)
    
    if method == "weibull":
        # Weibull公式: P = m / (n + 1)
        probs = np.arange(1, n + 1) / (n + 1)
    
    elif method == "hazen":
        # Hazen公式: P = (m - 0.5) / n
        probs = (np.arange(1, n + 1) - 0.5) / n
    
    elif method == "california":
        # California公式: P = m / n
        probs = np.arange(1, n + 1) / n
    
    else:
        raise ValueError(f"不支持的方法: {method}")
    
    return sorted_data, probs


def moving_average(
    data: np.ndarray,
    window: int
) -> np.ndarray:
    """
    移动平均
    
    Parameters
    ----------
    data : np.ndarray
        数据序列
    window : int
        窗口大小
    
    Returns
    -------
    np.ndarray
        移动平均序列
    
    Examples
    --------
    >>> data = np.array([1, 2, 3, 4, 5])
    >>> ma = moving_average(data, window=3)
    >>> print(ma)
    """
    if window < 1:
        raise ValueError("窗口大小必须大于0")
    
    if window > len(data):
        warnings.warn("窗口大小大于数据长度，返回全局平均值")
        return np.full_like(data, np.mean(data), dtype=float)
    
    # 使用卷积计算移动平均
    weights = np.ones(window) / window
    ma = np.convolve(data, weights, mode='valid')
    
    # 填充前后的值
    result = np.full_like(data, np.nan, dtype=float)
    start_idx = (window - 1) // 2
    result[start_idx:start_idx + len(ma)] = ma
    
    return result
