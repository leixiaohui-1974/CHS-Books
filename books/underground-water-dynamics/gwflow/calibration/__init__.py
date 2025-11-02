"""
参数率定模块

提供地下水模型参数率定的各种方法，包括：
- 优化算法（梯度下降、牛顿法、L-M算法）
- 目标函数定义
- 敏感性分析（局部和全局）
- 不确定性量化
- 贝叶斯推断
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

from .global_sensitivity import (
    compute_sobol_indices,
    morris_screening,
    interaction_analysis
)

from .bayesian import (
    metropolis_hastings,
    log_posterior,
    compute_dic,
    predictive_distribution
)

from .uncertainty import (
    monte_carlo_uncertainty,
    glue_analysis,
    bootstrap_uncertainty,
    propagate_uncertainty
)

__all__ = [
    # Optimization
    'calibrate_parameters',
    'compute_objective_function',
    'compute_jacobian',
    'gradient_descent',
    'levenberg_marquardt',
    'gauss_newton',
    # Local sensitivity
    'compute_sensitivity_matrix',
    'forward_difference_sensitivity',
    'relative_sensitivity_coefficient',
    # Global sensitivity
    'compute_sobol_indices',
    'morris_screening',
    'interaction_analysis',
    # Bayesian
    'metropolis_hastings',
    'log_posterior',
    'compute_dic',
    'predictive_distribution',
    # Uncertainty
    'monte_carlo_uncertainty',
    'glue_analysis',
    'bootstrap_uncertainty',
    'propagate_uncertainty',
]
