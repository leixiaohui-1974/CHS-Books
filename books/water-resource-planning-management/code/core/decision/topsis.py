"""
TOPSIS法 (Technique for Order Preference by Similarity to an Ideal Solution)

逼近理想解排序法，用于多准则决策
"""

import numpy as np
from typing import List, Optional, Tuple


class TOPSIS:
    """
    TOPSIS多准则决策方法
    
    基本思想：选择的方案应该离正理想解最近，离负理想解最远
    
    Examples
    --------
    >>> # 决策矩阵 (4个方案, 3个指标)
    >>> matrix = np.array([
    ...     [90, 80, 70],
    ...     [85, 85, 80],
    ...     [88, 82, 75],
    ...     [92, 78, 68]
    ... ])
    >>> 
    >>> # 权重
    >>> weights = np.array([0.4, 0.3, 0.3])
    >>> 
    >>> # 指标类型 (True=效益型, False=成本型)
    >>> is_benefit = [True, True, False]
    >>> 
    >>> # 计算
    >>> topsis = TOPSIS()
    >>> scores = topsis.calculate(matrix, weights, is_benefit)
    >>> print(f"综合得分: {scores}")
    """
    
    def __init__(self):
        """初始化"""
        self.matrix = None
        self.normalized_matrix = None
        self.weighted_matrix = None
        self.positive_ideal = None
        self.negative_ideal = None
        self.scores = None
    
    def calculate(
        self,
        matrix: np.ndarray,
        weights: np.ndarray,
        is_benefit: Optional[List[bool]] = None,
        normalize_method: str = "vector"
    ) -> np.ndarray:
        """
        计算TOPSIS得分
        
        Parameters
        ----------
        matrix : np.ndarray
            决策矩阵 (m×n)，m个方案，n个指标
        weights : np.ndarray
            权重向量 (n,)
        is_benefit : List[bool], optional
            指标类型列表，True表示效益型，False表示成本型
            如果为None，则假设全部为效益型
        normalize_method : str, optional
            归一化方法：'vector'（向量归一化）, 'minmax'（0-1归一化）
        
        Returns
        -------
        np.ndarray
            综合得分 (m,)，范围0-1，越大越好
        """
        self.matrix = np.array(matrix, dtype=float)
        m, n = self.matrix.shape
        
        # 检查权重
        if len(weights) != n:
            raise ValueError("权重维度与指标数量不匹配")
        
        # 默认全部为效益型指标
        if is_benefit is None:
            is_benefit = [True] * n
        
        # 1. 归一化
        self.normalized_matrix = self._normalize(normalize_method)
        
        # 2. 将成本型指标转换为效益型
        for j, is_ben in enumerate(is_benefit):
            if not is_ben:
                # 成本型：取倒数
                self.normalized_matrix[:, j] = 1.0 / (self.normalized_matrix[:, j] + 1e-10)
        
        # 3. 加权
        self.weighted_matrix = self.normalized_matrix * weights
        
        # 4. 确定正理想解和负理想解
        self.positive_ideal = np.max(self.weighted_matrix, axis=0)
        self.negative_ideal = np.min(self.weighted_matrix, axis=0)
        
        # 5. 计算距离
        d_positive = np.sqrt(np.sum((self.weighted_matrix - self.positive_ideal) ** 2, axis=1))
        d_negative = np.sqrt(np.sum((self.weighted_matrix - self.negative_ideal) ** 2, axis=1))
        
        # 6. 计算综合得分
        self.scores = d_negative / (d_positive + d_negative + 1e-10)
        
        return self.scores
    
    def _normalize(self, method: str = "vector") -> np.ndarray:
        """
        归一化决策矩阵
        
        Parameters
        ----------
        method : str
            归一化方法
        
        Returns
        -------
        np.ndarray
            归一化后的矩阵
        """
        if method == "vector":
            # 向量归一化
            norms = np.sqrt(np.sum(self.matrix ** 2, axis=0))
            return self.matrix / (norms + 1e-10)
        
        elif method == "minmax":
            # 0-1归一化
            min_vals = np.min(self.matrix, axis=0)
            max_vals = np.max(self.matrix, axis=0)
            return (self.matrix - min_vals) / (max_vals - min_vals + 1e-10)
        
        else:
            raise ValueError(f"不支持的归一化方法: {method}")
    
    def rank(self) -> np.ndarray:
        """
        获取排名
        
        Returns
        -------
        np.ndarray
            排名（从1开始，1表示最好）
        """
        if self.scores is None:
            raise ValueError("请先调用calculate()方法")
        
        # argsort返回从小到大的索引，我们要从大到小
        sorted_indices = np.argsort(-self.scores)
        
        # 创建排名数组
        ranks = np.empty(len(self.scores), dtype=int)
        ranks[sorted_indices] = np.arange(1, len(self.scores) + 1)
        
        return ranks
    
    def get_results(self) -> dict:
        """
        获取完整结果
        
        Returns
        -------
        dict
            包含得分、排名等信息的字典
        """
        if self.scores is None:
            raise ValueError("请先调用calculate()方法")
        
        return {
            "scores": self.scores,
            "ranks": self.rank(),
            "positive_ideal": self.positive_ideal,
            "negative_ideal": self.negative_ideal
        }


def topsis_rank(
    matrix: np.ndarray,
    weights: np.ndarray,
    is_benefit: Optional[List[bool]] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    TOPSIS排序的便捷函数
    
    Parameters
    ----------
    matrix : np.ndarray
        决策矩阵
    weights : np.ndarray
        权重
    is_benefit : List[bool], optional
        指标类型
    
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (得分, 排名)
    
    Examples
    --------
    >>> matrix = np.array([[90, 80], [85, 85], [88, 82]])
    >>> weights = np.array([0.6, 0.4])
    >>> scores, ranks = topsis_rank(matrix, weights)
    """
    topsis = TOPSIS()
    scores = topsis.calculate(matrix, weights, is_benefit)
    ranks = topsis.rank()
    return scores, ranks
