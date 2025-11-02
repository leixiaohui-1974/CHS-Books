"""
时间序列处理工具
"""

import numpy as np
import pandas as pd
from typing import Optional, Union


def resample_series(
    series: pd.Series,
    freq: str,
    method: str = "mean"
) -> pd.Series:
    """
    重采样时间序列
    
    Parameters
    ----------
    series : pd.Series
        时间序列，索引必须是DatetimeIndex
    freq : str
        目标频率，如'D'(日), 'M'(月), 'Y'(年)
    method : str, optional
        聚合方法：'mean', 'sum', 'max', 'min'
    
    Returns
    -------
    pd.Series
        重采样后的序列
    
    Examples
    --------
    >>> dates = pd.date_range('2020-01-01', periods=365, freq='D')
    >>> series = pd.Series(np.random.randn(365), index=dates)
    >>> monthly = resample_series(series, 'M', method='mean')
    """
    if not isinstance(series.index, pd.DatetimeIndex):
        raise TypeError("序列索引必须是DatetimeIndex类型")
    
    resampler = series.resample(freq)
    
    if method == "mean":
        return resampler.mean()
    elif method == "sum":
        return resampler.sum()
    elif method == "max":
        return resampler.max()
    elif method == "min":
        return resampler.min()
    else:
        raise ValueError(f"不支持的聚合方法: {method}")


def fill_missing_values(
    series: Union[pd.Series, np.ndarray],
    method: str = "linear"
) -> Union[pd.Series, np.ndarray]:
    """
    填补缺失值
    
    Parameters
    ----------
    series : pd.Series or np.ndarray
        数据序列
    method : str, optional
        填补方法：
        - 'linear': 线性插值
        - 'forward': 前向填充
        - 'backward': 后向填充
        - 'mean': 均值填充
    
    Returns
    -------
    pd.Series or np.ndarray
        填补后的序列
    
    Examples
    --------
    >>> data = pd.Series([1, np.nan, 3, np.nan, 5])
    >>> filled = fill_missing_values(data, method='linear')
    >>> print(filled.values)
    """
    if isinstance(series, np.ndarray):
        series = pd.Series(series)
        return_array = True
    else:
        return_array = False
    
    if method == "linear":
        result = series.interpolate(method='linear')
    elif method == "forward":
        result = series.fillna(method='ffill')
    elif method == "backward":
        result = series.fillna(method='bfill')
    elif method == "mean":
        result = series.fillna(series.mean())
    else:
        raise ValueError(f"不支持的填补方法: {method}")
    
    if return_array:
        return result.values
    else:
        return result


def detect_outliers(
    data: np.ndarray,
    method: str = "iqr",
    threshold: float = 1.5
) -> np.ndarray:
    """
    检测异常值
    
    Parameters
    ----------
    data : np.ndarray
        数据序列
    method : str, optional
        检测方法：
        - 'iqr': 四分位距法
        - 'zscore': Z分数法
    threshold : float, optional
        阈值参数
    
    Returns
    -------
    np.ndarray
        布尔数组，True表示异常值
    
    Examples
    --------
    >>> data = np.array([1, 2, 3, 100, 4, 5])
    >>> outliers = detect_outliers(data, method='iqr')
    >>> print(data[outliers])  # [100]
    """
    data = np.array(data)
    
    if method == "iqr":
        # 四分位距法
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        return (data < lower_bound) | (data > upper_bound)
    
    elif method == "zscore":
        # Z分数法
        mean = np.mean(data)
        std = np.std(data)
        z_scores = np.abs((data - mean) / std)
        return z_scores > threshold
    
    else:
        raise ValueError(f"不支持的检测方法: {method}")


def detrend(
    series: np.ndarray,
    method: str = "linear"
) -> np.ndarray:
    """
    去除趋势
    
    Parameters
    ----------
    series : np.ndarray
        数据序列
    method : str, optional
        去趋势方法：'linear', 'constant'
    
    Returns
    -------
    np.ndarray
        去趋势后的序列
    """
    from scipy import signal
    return signal.detrend(series, type=method)
