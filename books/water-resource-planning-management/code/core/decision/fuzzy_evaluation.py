"""
模糊综合评价

用于处理不确定性和模糊性的综合评价方法
"""

import numpy as np
from typing import List, Optional


class FuzzyEvaluation:
    """
    模糊综合评价
    
    基本步骤：
    1. 确定评价因素集
    2. 确定评价等级集
    3. 建立模糊关系矩阵
    4. 确定权重向量
    5. 模糊合成
    6. 综合评判
    
    Examples
    --------
    >>> # 模糊关系矩阵 (3个指标, 5个等级)
    >>> R = np.array([
    ...     [0.1, 0.2, 0.4, 0.2, 0.1],  # 指标1对各等级的隶属度
    ...     [0.0, 0.1, 0.3, 0.4, 0.2],  # 指标2
    ...     [0.2, 0.3, 0.3, 0.1, 0.1]   # 指标3
    ... ])
    >>> 
    >>> # 权重
    >>> weights = np.array([0.4, 0.3, 0.3])
    >>> 
    >>> # 评价
    >>> fuzzy = FuzzyEvaluation()
    >>> result = fuzzy.evaluate(R, weights)
    >>> print(f"综合评价向量: {result}")
    """
    
    def __init__(self):
        """初始化"""
        self.R = None
        self.weights = None
        self.result = None
    
    def evaluate(
        self,
        R: np.ndarray,
        weights: np.ndarray,
        operator: str = "weighted_average"
    ) -> np.ndarray:
        """
        模糊综合评价
        
        Parameters
        ----------
        R : np.ndarray
            模糊关系矩阵 (n×m)，n个指标，m个评价等级
        weights : np.ndarray
            权重向量 (n,)
        operator : str, optional
            合成算子：
            - 'weighted_average': 加权平均型 M(·,⊕)
            - 'min_max': 主因素突出型 M(∧,∨)
            - 'main_factor': 主因素决定型 M(∧,·)
        
        Returns
        -------
        np.ndarray
            综合评价向量 (m,)
        """
        self.R = np.array(R, dtype=float)
        self.weights = np.array(weights, dtype=float)
        
        n, m = self.R.shape
        
        if len(self.weights) != n:
            raise ValueError("权重维度与指标数量不匹配")
        
        # 归一化权重
        self.weights = self.weights / np.sum(self.weights)
        
        # 模糊合成
        if operator == "weighted_average":
            # 加权平均型：B = W·R
            self.result = self.weights @ self.R
        
        elif operator == "min_max":
            # 主因素突出型：bj = max(min(wi, rij))
            self.result = np.zeros(m)
            for j in range(m):
                self.result[j] = np.max(np.minimum(self.weights, self.R[:, j]))
        
        elif operator == "main_factor":
            # 主因素决定型：bj = max(wi ∧ rij)
            self.result = np.zeros(m)
            for j in range(m):
                self.result[j] = np.max(self.weights * self.R[:, j])
        
        else:
            raise ValueError(f"不支持的合成算子: {operator}")
        
        # 归一化
        self.result = self.result / np.sum(self.result)
        
        return self.result
    
    def get_grade(
        self,
        grades: Optional[List[str]] = None,
        method: str = "max_membership"
    ) -> str:
        """
        确定评价等级
        
        Parameters
        ----------
        grades : List[str], optional
            等级名称列表，如['优', '良', '中', '差', '劣']
        method : str, optional
            判定方法：
            - 'max_membership': 最大隶属度原则
            - 'weighted_average': 加权平均
        
        Returns
        -------
        str
            评价等级
        """
        if self.result is None:
            raise ValueError("请先调用evaluate()方法")
        
        if grades is None:
            grades = [f"等级{i+1}" for i in range(len(self.result))]
        
        if method == "max_membership":
            # 最大隶属度原则
            index = np.argmax(self.result)
            return grades[index]
        
        elif method == "weighted_average":
            # 加权平均（假设等级对应分数1,2,3,...）
            scores = np.arange(1, len(self.result) + 1)
            avg_score = np.sum(self.result * scores)
            # 四舍五入到最近的等级
            index = int(round(avg_score)) - 1
            index = np.clip(index, 0, len(grades) - 1)
            return grades[index]
        
        else:
            raise ValueError(f"不支持的判定方法: {method}")
    
    def get_score(self, grade_scores: Optional[np.ndarray] = None) -> float:
        """
        计算综合得分
        
        Parameters
        ----------
        grade_scores : np.ndarray, optional
            各等级对应的分数，如[100, 80, 60, 40, 20]
            如果为None，则使用等差数列
        
        Returns
        -------
        float
            综合得分
        """
        if self.result is None:
            raise ValueError("请先调用evaluate()方法")
        
        if grade_scores is None:
            # 默认使用100到0的等差数列
            m = len(self.result)
            grade_scores = np.linspace(100, 0, m)
        
        return np.sum(self.result * grade_scores)
    
    def get_results(self) -> dict:
        """
        获取完整结果
        
        Returns
        -------
        dict
            包含评价向量、等级、得分等信息的字典
        """
        if self.result is None:
            raise ValueError("请先调用evaluate()方法")
        
        return {
            "evaluation_vector": self.result,
            "grade": self.get_grade(),
            "score": self.get_score()
        }


def build_membership_matrix(
    data: np.ndarray,
    grade_ranges: List[tuple]
) -> np.ndarray:
    """
    构建模糊关系矩阵（隶属度矩阵）
    
    Parameters
    ----------
    data : np.ndarray
        数据矩阵 (n,)，n个指标的值
    grade_ranges : List[tuple]
        各等级的范围，如[(90, 100), (80, 90), (70, 80), (60, 70), (0, 60)]
    
    Returns
    -------
    np.ndarray
        模糊关系矩阵 (n×m)
    
    Examples
    --------
    >>> data = np.array([85, 92, 78])
    >>> ranges = [(90, 100), (80, 90), (70, 80), (60, 70), (0, 60)]
    >>> R = build_membership_matrix(data, ranges)
    """
    n = len(data)
    m = len(grade_ranges)
    R = np.zeros((n, m))
    
    for i, value in enumerate(data):
        for j, (low, high) in enumerate(grade_ranges):
            if low <= value < high:
                # 线性隶属度函数
                if value == low:
                    R[i, j] = 0
                elif value == high:
                    R[i, j] = 1
                else:
                    R[i, j] = (value - low) / (high - low)
                
                # 相邻等级也有一定隶属度
                if j > 0:
                    R[i, j-1] = 1 - R[i, j]
                break
    
    # 归一化每行
    row_sums = np.sum(R, axis=1, keepdims=True)
    R = R / (row_sums + 1e-10)
    
    return R
