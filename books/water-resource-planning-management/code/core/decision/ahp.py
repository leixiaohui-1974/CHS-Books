"""
AHP层次分析法 (Analytic Hierarchy Process)

用于多准则决策问题的权重确定
"""

import numpy as np
from typing import Tuple, Optional


# RI表：随机一致性指标
RI_TABLE = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
    11: 1.51,
    12: 1.48,
    13: 1.56,
    14: 1.57,
    15: 1.59,
}


class AHP:
    """
    层次分析法
    
    用于确定指标权重
    
    Examples
    --------
    >>> # 构造判断矩阵
    >>> matrix = np.array([
    ...     [1,   2,   5],
    ...     [0.5, 1,   3],
    ...     [0.2, 0.33, 1]
    ... ])
    >>> 
    >>> # 计算权重
    >>> ahp = AHP()
    >>> weights, CR = ahp.calculate_weights(matrix)
    >>> print(f"权重: {weights}")
    >>> print(f"一致性比率 CR: {CR:.4f}")
    """
    
    def __init__(self):
        """初始化"""
        self.matrix = None
        self.weights = None
        self.lambda_max = None
        self.CI = None
        self.CR = None
    
    def calculate_weights(
        self,
        matrix: np.ndarray,
        method: str = "eigenvalue"
    ) -> Tuple[np.ndarray, float]:
        """
        计算权重向量
        
        Parameters
        ----------
        matrix : np.ndarray
            判断矩阵 (n×n)
        method : str, optional
            计算方法：'eigenvalue'（特征值法）, 'geometric_mean'（几何平均法）
        
        Returns
        -------
        Tuple[np.ndarray, float]
            (权重向量, 一致性比率CR)
        
        Raises
        ------
        ValueError
            如果矩阵不是方阵或一致性检验不通过
        """
        self.matrix = np.array(matrix, dtype=float)
        n = self.matrix.shape[0]
        
        if self.matrix.shape[0] != self.matrix.shape[1]:
            raise ValueError("判断矩阵必须是方阵")
        
        # 计算权重
        if method == "eigenvalue":
            self.weights = self._eigenvalue_method()
        elif method == "geometric_mean":
            self.weights = self._geometric_mean_method()
        else:
            raise ValueError(f"不支持的方法: {method}")
        
        # 一致性检验
        self._consistency_test()
        
        return self.weights, self.CR
    
    def _eigenvalue_method(self) -> np.ndarray:
        """
        特征值法计算权重
        
        Returns
        -------
        np.ndarray
            权重向量
        """
        # 计算特征值和特征向量
        eigenvalues, eigenvectors = np.linalg.eig(self.matrix)
        
        # 找到最大特征值的索引
        max_index = np.argmax(eigenvalues.real)
        
        # 最大特征值
        self.lambda_max = eigenvalues[max_index].real
        
        # 对应的特征向量
        max_eigenvector = eigenvectors[:, max_index].real
        
        # 归一化得到权重
        weights = max_eigenvector / np.sum(max_eigenvector)
        
        return weights
    
    def _geometric_mean_method(self) -> np.ndarray:
        """
        几何平均法计算权重
        
        Returns
        -------
        np.ndarray
            权重向量
        """
        n = self.matrix.shape[0]
        
        # 计算每行元素的几何平均
        geometric_means = np.prod(self.matrix, axis=1) ** (1.0 / n)
        
        # 归一化
        weights = geometric_means / np.sum(geometric_means)
        
        # 计算最大特征值（用于一致性检验）
        AW = self.matrix @ weights
        self.lambda_max = np.mean(AW / weights)
        
        return weights
    
    def _consistency_test(self) -> None:
        """
        一致性检验
        
        计算CI和CR
        """
        n = self.matrix.shape[0]
        
        # 一致性指标 CI
        self.CI = (self.lambda_max - n) / (n - 1)
        
        # 随机一致性指标 RI
        RI = RI_TABLE.get(n, 1.59)
        
        # 一致性比率 CR
        self.CR = self.CI / RI if RI != 0 else 0
    
    def is_consistent(self, threshold: float = 0.10) -> bool:
        """
        判断是否通过一致性检验
        
        Parameters
        ----------
        threshold : float, optional
            一致性阈值，默认0.10
        
        Returns
        -------
        bool
            是否通过一致性检验
        """
        if self.CR is None:
            raise ValueError("请先计算权重")
        
        return self.CR < threshold
    
    def get_results(self) -> dict:
        """
        获取完整结果
        
        Returns
        -------
        dict
            包含权重、特征值、一致性指标的字典
        """
        if self.weights is None:
            raise ValueError("请先计算权重")
        
        return {
            "weights": self.weights,
            "lambda_max": self.lambda_max,
            "CI": self.CI,
            "CR": self.CR,
            "is_consistent": self.is_consistent()
        }


def calculate_consistency_ratio(matrix: np.ndarray) -> float:
    """
    计算一致性比率的便捷函数
    
    Parameters
    ----------
    matrix : np.ndarray
        判断矩阵
    
    Returns
    -------
    float
        一致性比率CR
    
    Examples
    --------
    >>> matrix = np.array([[1, 2], [0.5, 1]])
    >>> CR = calculate_consistency_ratio(matrix)
    >>> print(f"CR = {CR:.4f}")
    """
    ahp = AHP()
    _, CR = ahp.calculate_weights(matrix)
    return CR


def create_judgment_matrix_from_scores(
    scores: np.ndarray,
    scale: int = 9
) -> np.ndarray:
    """
    根据专家打分创建判断矩阵
    
    Parameters
    ----------
    scores : np.ndarray
        专家打分 (n,)
    scale : int, optional
        标度范围，默认9
    
    Returns
    -------
    np.ndarray
        判断矩阵 (n×n)
    
    Examples
    --------
    >>> scores = np.array([90, 80, 70])
    >>> matrix = create_judgment_matrix_from_scores(scores)
    """
    n = len(scores)
    matrix = np.ones((n, n))
    
    for i in range(n):
        for j in range(i + 1, n):
            if scores[i] > scores[j]:
                # 标度：1-9
                ratio = scores[i] / scores[j]
                matrix[i, j] = min(ratio, scale)
                matrix[j, i] = 1.0 / matrix[i, j]
            else:
                ratio = scores[j] / scores[i]
                matrix[j, i] = min(ratio, scale)
                matrix[i, j] = 1.0 / matrix[j, i]
    
    return matrix
