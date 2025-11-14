#!/usr/bin/env python3
"""
case_11_sce_calibration - 工具函数模块
Book: 分布式水文模型
"""

import numpy as np
from typing import Union, List, Tuple, Optional

def validate_parameters(**kwargs) -> bool:
    """
    验证输入参数的有效性

    Args:
        **kwargs: 待验证的参数字典

    Returns:
        bool: 参数是否有效
    """
    for key, value in kwargs.items():
        if value is None:
            print(f"警告: 参数 {key} 为空")
            return False
        if isinstance(value, (int, float)) and value < 0:
            print(f"警告: 参数 {key} 不应为负值")
            return False
    return True


def calculate_statistics(data: Union[List, np.ndarray]) -> dict:
    """
    计算数据的统计特征

    Args:
        data: 输入数据数组

    Returns:
        dict: 包含均值、标准差、最值等统计信息
    """
    data = np.array(data)

    return {
        'mean': float(np.mean(data)),
        'std': float(np.std(data)),
        'min': float(np.min(data)),
        'max': float(np.max(data)),
        'median': float(np.median(data)),
        'count': len(data)
    }


def interpolate_data(x: np.ndarray, y: np.ndarray, x_new: np.ndarray) -> np.ndarray:
    """
    对数据进行线性插值

    Args:
        x: 原始x坐标
        y: 原始y值
        x_new: 新的x坐标

    Returns:
        np.ndarray: 插值后的y值
    """
    return np.interp(x_new, x, y)


def format_results(results: dict) -> str:
    """
    格式化输出结果

    Args:
        results: 结果字典

    Returns:
        str: 格式化后的字符串
    """
    output = []
    output.append("=" * 60)
    output.append("计算结果")
    output.append("=" * 60)

    for key, value in results.items():
        if isinstance(value, float):
            output.append(f"{key}: {value:.4f}")
        else:
            output.append(f"{key}: {value}")

    output.append("=" * 60)
    return "\n".join(output)


def save_to_json(data: dict, filename: str) -> None:
    """
    将数据保存为JSON文件

    Args:
        data: 待保存的数据
        filename: 文件名
    """
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到: {filename}")


def load_from_json(filename: str) -> dict:
    """
    从JSON文件加载数据

    Args:
        filename: 文件名

    Returns:
        dict: 加载的数据
    """
    import json
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"数据已加载: {filename}")
    return data
