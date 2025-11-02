"""
units.py - 单位转换工具
========================
"""

from typing import Union
import numpy as np


def convert_units(
    value: Union[float, np.ndarray],
    from_unit: str,
    to_unit: str
) -> Union[float, np.ndarray]:
    """
    单位转换
    
    支持的单位：
    - 长度：m, cm, mm, km
    - 时间：s, min, h, day, year
    - 水力传导度：m/s, m/day, cm/s
    
    参数：
        value: 数值
        from_unit: 原始单位
        to_unit: 目标单位
    
    返回：
        转换后的数值
    """
    # 长度转换（全部转换为m）
    length_factors = {
        'm': 1.0,
        'cm': 0.01,
        'mm': 0.001,
        'km': 1000.0
    }
    
    # 时间转换（全部转换为day）
    time_factors = {
        's': 1.0 / 86400,
        'min': 1.0 / 1440,
        'h': 1.0 / 24,
        'day': 1.0,
        'year': 365.25
    }
    
    # 水力传导度转换
    if '/' in from_unit and '/' in to_unit:
        from_length, from_time = from_unit.split('/')
        to_length, to_time = to_unit.split('/')
        
        # 转换长度
        value_m = value * length_factors[from_length]
        # 转换时间
        value_m_day = value_m / time_factors[from_time]
        # 转换到目标单位
        result = value_m_day * time_factors[to_time] / length_factors[to_length]
        
        return result
    
    # 长度转换
    if from_unit in length_factors and to_unit in length_factors:
        return value * length_factors[from_unit] / length_factors[to_unit]
    
    # 时间转换
    if from_unit in time_factors and to_unit in time_factors:
        return value * time_factors[from_unit] / time_factors[to_unit]
    
    raise ValueError(f"不支持的单位转换: {from_unit} -> {to_unit}")
