"""
熵权法

客观赋权方法，基于信息熵确定指标权重
"""

import numpy as np
from typing import Optional


class EntropyWeight:
    """
    熵权法
    
    根据数据的离散程度客观确定权重
    
    基本思想：信息熵越小，指标的变异程度越大，权重应该越大
    
    Examples
    --------
    >>> # 数据矩阵 (4个样本, 3个指标)
    >>> data = np.array([
    ...     [90, 80, 70],
    ...     [85, 85, 80],
    ...     [88, 82, 75],
    ...     [92, 78, 68]
    ... ])
    >>> 
    >>> # 计算权重
    >>> ew = EntropyWeight()
    >>> weights = ew.calculate_weights(data)
    >>> print(f"权重: {weights}")
    """
    
    def __init__(self):
        """初始化"""
        self.data = None
        self.normalized_data = None
        self.entropy = None
        self.weights = None
    
    def calculate_weights(
        self,
        data: np.ndarray,
        normalize_method: str = "minmax"
    ) -> np.ndarray:
        """
        计算熵权
        
        Parameters
        ----------
        data : np.ndarray
            数据矩阵 (m×n)，m个样本，n个指标
        normalize_method : str, optional
            归一化方法：'minmax'（默认）, 'zscore'
        
        Returns
        -------
        np.ndarray
            权重向量 (n,)
        """
        self.data = np.array(data, dtype=float)
        m, n = self.data.shape
        
        # 1. 数据归一化（0-1）
        self.normalized_data = self._normalize(normalize_method)
        
        # 2. 计算比重
        # 加上一个小值避免log(0)
        P = self.normalized_data / (np.sum(self.normalized_data, axis=0) + 1e-10)
        P = np.where(P == 0, 1e-10, P)  # 避免log(0)
        
        # 3. 计算信息熵
        k = 1.0 / np.log(m)  # 常数
        self.entropy = -k * np.sum(P * np.log(P), axis=0)
        
        # 4. 计算信息效用值
        d = 1 - self.entropy
        
        # 5. 计算权重
        self.weights = d / np.sum(d)
        
        return self.weights
    
    def _normalize(self, method: str = "minmax") -> np.ndarray:
        """
        归一化数据
        
        Parameters
        ----------
        method : str
            归一化方法
        
        Returns
        -------
        np.ndarray
            归一化后的数据
        """
        if method == "minmax":
            # 0-1归一化
            min_vals = np.min(self.data, axis=0)
            max_vals = np.max(self.data, axis=0)
            range_vals = max_vals - min_vals
            
            # 避免除以0
            range_vals = np.where(range_vals == 0, 1, range_vals)
            
            return (self.data - min_vals) / range_vals
        
        elif method == "zscore":
            # Z-score标准化
            mean_vals = np.mean(self.data, axis=0)
            std_vals = np.std(self.data, axis=0)
            
            # 避免除以0
            std_vals = np.where(std_vals == 0, 1, std_vals)
            
            # 标准化后再映射到[0,1]
            z_scores = (self.data - mean_vals) / std_vals
            min_z = np.min(z_scores, axis=0)
            max_z = np.max(z_scores, axis=0)
            range_z = max_z - min_z
            range_z = np.where(range_z == 0, 1, range_z)
            
            return (z_scores - min_z) / range_z
        
        else:
            raise ValueError(f"不支持的归一化方法: {method}")
    
    def get_results(self) -> dict:
        """
        获取完整结果
        
        Returns
        -------
        dict
            包含权重、熵值等信息的字典
        """
        if self.weights is None:
            raise ValueError("请先调用calculate_weights()方法")
        
        return {
            "weights": self.weights,
            "entropy": self.entropy,
            "information_utility": 1 - self.entropy
        }


def calculate_entropy_weights(data: np.ndarray) -> np.ndarray:
    """
    计算熵权的便捷函数
    
    Parameters
    ----------
    data : np.ndarray
        数据矩阵 (m×n)
    
    Returns
    -------
    np.ndarray
        权重向量 (n,)
    
    Examples
    --------
    >>> data = np.array([[90, 80], [85, 85], [88, 82]])
    >>> weights = calculate_entropy_weights(data)
    >>> print(f"权重: {weights}")
    """
    ew = EntropyWeight()
    return ew.calculate_weights(data)
