"""
决策支持模块

提供多准则决策分析方法：
- AHP: 层次分析法
- TOPSIS: 理想解法
- 熵权法: 客观赋权
- 模糊综合评价
"""

from .ahp import AHP, calculate_consistency_ratio
from .topsis import TOPSIS
from .entropy_weight import EntropyWeight
from .fuzzy_evaluation import FuzzyEvaluation

__all__ = [
    "AHP",
    "calculate_consistency_ratio",
    "TOPSIS",
    "EntropyWeight",
    "FuzzyEvaluation",
]
