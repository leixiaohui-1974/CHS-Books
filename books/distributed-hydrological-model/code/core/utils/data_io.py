"""
数据输入输出模块
=============

提供数据读写功能
"""

import numpy as np
import pandas as pd
from pathlib import Path


def read_rainfall_data(file_path, delimiter=',', time_col=0, value_col=1):
    """
    读取降雨数据
    
    Parameters
    ----------
    file_path : str
        文件路径
    delimiter : str
        分隔符
    time_col : int
        时间列索引
    value_col : int
        降雨量列索引
        
    Returns
    -------
    df : pd.DataFrame
        降雨数据框
    """
    df = pd.read_csv(file_path, delimiter=delimiter)
    return df


def read_discharge_data(file_path, delimiter=','):
    """
    读取流量数据
    
    Parameters
    ----------
    file_path : str
        文件路径
    delimiter : str
        分隔符
        
    Returns
    -------
    df : pd.DataFrame
        流量数据框
    """
    df = pd.read_csv(file_path, delimiter=delimiter)
    return df


def save_results(data, file_path, format='csv'):
    """
    保存结果数据
    
    Parameters
    ----------
    data : dict or pd.DataFrame
        要保存的数据
    file_path : str
        保存路径
    format : str
        保存格式 ('csv', 'json', 'excel')
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    if isinstance(data, dict):
        data = pd.DataFrame(data)
    
    if format == 'csv':
        data.to_csv(file_path, index=False)
    elif format == 'json':
        data.to_json(file_path, orient='records', indent=2)
    elif format == 'excel':
        data.to_excel(file_path, index=False)
    
    print(f"结果已保存至: {file_path}")
