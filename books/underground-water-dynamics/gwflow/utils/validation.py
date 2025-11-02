"""
validation.py - 参数验证工具
=============================
"""

import numpy as np
from typing import Any, Optional


def validate_parameters(
    K: Any,
    S: Optional[Any] = None,
    h: Optional[Any] = None,
    nx: Optional[int] = None,
    ny: Optional[int] = None
) -> None:
    """
    验证模型参数的合理性
    
    参数：
        K: 水力传导度
        S: 储水系数
        h: 水头
        nx: x方向网格数
        ny: y方向网格数
    """
    # 验证K
    if K is not None:
        if np.isscalar(K):
            if K <= 0:
                raise ValueError("水力传导度必须大于0")
        else:
            K = np.asarray(K)
            if np.any(K <= 0):
                raise ValueError("水力传导度必须全部大于0")
    
    # 验证S
    if S is not None:
        if np.isscalar(S):
            if S <= 0:
                raise ValueError("储水系数必须大于0")
        else:
            S = np.asarray(S)
            if np.any(S <= 0):
                raise ValueError("储水系数必须全部大于0")
    
    # 验证网格数
    if nx is not None and nx < 2:
        raise ValueError("x方向网格数必须至少为2")
    if ny is not None and ny < 2:
        raise ValueError("y方向网格数必须至少为2")
