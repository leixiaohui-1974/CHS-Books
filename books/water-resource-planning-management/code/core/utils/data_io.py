"""
数据输入输出工具

提供CSV、YAML、Excel等格式的读写功能
"""

import os
from typing import Any, Dict, Optional, Union
import pandas as pd
import yaml


def load_csv(
    filepath: str, encoding: str = "utf-8", **kwargs
) -> pd.DataFrame:
    """
    读取CSV文件
    
    Parameters
    ----------
    filepath : str
        文件路径
    encoding : str, optional
        文件编码，默认为'utf-8'
    **kwargs
        传递给pandas.read_csv的其他参数
    
    Returns
    -------
    pd.DataFrame
        数据框
    
    Examples
    --------
    >>> df = load_csv('data/runoff.csv')
    >>> print(df.head())
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    return pd.read_csv(filepath, encoding=encoding, **kwargs)


def save_csv(
    data: pd.DataFrame,
    filepath: str,
    encoding: str = "utf-8",
    index: bool = False,
    **kwargs
) -> None:
    """
    保存数据到CSV文件
    
    Parameters
    ----------
    data : pd.DataFrame
        要保存的数据
    filepath : str
        保存路径
    encoding : str, optional
        文件编码
    index : bool, optional
        是否保存索引
    **kwargs
        传递给pandas.to_csv的其他参数
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    
    data.to_csv(filepath, encoding=encoding, index=index, **kwargs)
    print(f"数据已保存到: {filepath}")


def load_yaml(filepath: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """
    读取YAML配置文件
    
    Parameters
    ----------
    filepath : str
        文件路径
    encoding : str, optional
        文件编码
    
    Returns
    -------
    Dict[str, Any]
        配置字典
    
    Examples
    --------
    >>> config = load_yaml('config.yaml')
    >>> print(config['parameters'])
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    with open(filepath, "r", encoding=encoding) as f:
        return yaml.safe_load(f)


def save_yaml(
    data: Dict[str, Any],
    filepath: str,
    encoding: str = "utf-8"
) -> None:
    """
    保存数据到YAML文件
    
    Parameters
    ----------
    data : Dict[str, Any]
        要保存的数据
    filepath : str
        保存路径
    encoding : str, optional
        文件编码
    """
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    
    with open(filepath, "w", encoding=encoding) as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    print(f"数据已保存到: {filepath}")


def load_excel(
    filepath: str,
    sheet_name: Union[str, int] = 0,
    **kwargs
) -> pd.DataFrame:
    """
    读取Excel文件
    
    Parameters
    ----------
    filepath : str
        文件路径
    sheet_name : str or int, optional
        工作表名称或索引
    **kwargs
        传递给pandas.read_excel的其他参数
    
    Returns
    -------
    pd.DataFrame
        数据框
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    return pd.read_excel(filepath, sheet_name=sheet_name, **kwargs)


def save_excel(
    data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
    filepath: str,
    **kwargs
) -> None:
    """
    保存数据到Excel文件
    
    Parameters
    ----------
    data : pd.DataFrame or Dict[str, pd.DataFrame]
        要保存的数据，可以是单个DataFrame或多个工作表的字典
    filepath : str
        保存路径
    **kwargs
        传递给pandas.to_excel的其他参数
    """
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    
    if isinstance(data, dict):
        with pd.ExcelWriter(filepath) as writer:
            for sheet_name, df in data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False, **kwargs)
    else:
        data.to_excel(filepath, index=False, **kwargs)
    
    print(f"数据已保存到: {filepath}")
