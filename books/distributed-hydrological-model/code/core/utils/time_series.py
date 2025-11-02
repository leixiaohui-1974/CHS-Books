"""
时间序列处理模块
=============

提供时间序列数据处理功能
"""

import numpy as np
import pandas as pd


def resample_timeseries(data, freq='D'):
    """
    重采样时间序列
    
    Parameters
    ----------
    data : pd.DataFrame
        时间序列数据
    freq : str
        重采样频率 ('H'=小时, 'D'=天, 'M'=月)
        
    Returns
    -------
    resampled : pd.DataFrame
        重采样后的数据
    """
    return data.resample(freq).mean()


def fill_missing_data(data, method='linear'):
    """
    填充缺失数据
    
    Parameters
    ----------
    data : pd.Series or pd.DataFrame
        含缺失值的数据
    method : str
        填充方法 ('linear', 'ffill', 'bfill', 'mean')
        
    Returns
    -------
    filled : pd.Series or pd.DataFrame
        填充后的数据
    """
    if method == 'linear':
        return data.interpolate(method='linear')
    elif method == 'ffill':
        return data.fillna(method='ffill')
    elif method == 'bfill':
        return data.fillna(method='bfill')
    elif method == 'mean':
        return data.fillna(data.mean())
    else:
        return data
