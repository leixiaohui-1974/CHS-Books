"""
gwflow.pumping - 抽水井模拟与优化模块

本模块提供抽水井模拟的完整功能，包括：
- 解析解（Theis, Cooper-Jacob, Thiem）
- 多井系统叠加
- 开采优化
"""

from .wells import (
    PumpingWell,
    WellField
)

from .analytical import (
    theis_well_function,
    theis_solution,
    cooper_jacob_solution,
    thiem_solution,
    superposition_principle,
    distance_drawdown_curve,
    time_drawdown_curve
)

from .optimization import (
    optimize_pumping_rates,
    optimize_well_locations,
    compute_feasible_region
)

__version__ = '0.6.0'

__all__ = [
    # 井类
    'PumpingWell',
    'WellField',
    
    # 解析解
    'theis_well_function',
    'theis_solution',
    'cooper_jacob_solution',
    'thiem_solution',
    'superposition_principle',
    'distance_drawdown_curve',
    'time_drawdown_curve',
    
    # 优化
    'optimize_pumping_rates',
    'optimize_well_locations',
    'compute_feasible_region',
]
