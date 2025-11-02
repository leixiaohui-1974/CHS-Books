"""
gwflow.transport - 污染物运移模拟模块

本模块提供地下水污染物运移模拟的完整功能，包括：
- 对流-弥散方程（ADE）求解
- 解析解
- 吸附模型
- 衰减动力学
"""

from .advection_dispersion import (
    ADESolver1D,
    ADESolver2D,
    solve_ade_1d_implicit,
    solve_ade_2d_implicit
)

from .analytical import (
    analytical_1d_instantaneous,
    analytical_1d_continuous,
    analytical_2d_instantaneous,
    ogata_banks_solution
)

from .sorption import (
    retardation_factor,
    linear_sorption,
    freundlich_sorption,
    langmuir_sorption
)

__version__ = '0.6.0'

__all__ = [
    # 数值求解器
    'ADESolver1D',
    'ADESolver2D',
    'solve_ade_1d_implicit',
    'solve_ade_2d_implicit',
    
    # 解析解
    'analytical_1d_instantaneous',
    'analytical_1d_continuous',
    'analytical_2d_instantaneous',
    'ogata_banks_solution',
    
    # 吸附模型
    'retardation_factor',
    'linear_sorption',
    'freundlich_sorption',
    'langmuir_sorption',
]
