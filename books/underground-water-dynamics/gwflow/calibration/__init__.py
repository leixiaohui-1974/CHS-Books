"""
参数率定模块

提供地下水模型参数率定的各种方法，包括：
- 优化算法（梯度下降、牛顿法、L-M算法）
- 目标函数定义
- 敏感性分析
- 不确定性量化
"""

from .optimization import (
    calibrate_parameters,
    compute_objective_function,
    compute_jacobian,
    gradient_descent,
    levenberg_marquardt,
    gauss_newton
)

from .sensitivity import (
    compute_sensitivity_matrix,
    forward_difference_sensitivity,
    relative_sensitivity_coefficient
)

__all__ = [
    'calibrate_parameters',
    'compute_objective_function',
    'compute_jacobian',
    'gradient_descent',
    'levenberg_marquardt',
    'gauss_newton',
    'compute_sensitivity_matrix',
    'forward_difference_sensitivity',
    'relative_sensitivity_coefficient',
]
