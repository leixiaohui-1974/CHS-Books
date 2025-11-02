"""
多目标优化模块 (Multi-Objective Optimization Module)

提供多种多目标优化方法和帕累托前沿分析工具。

主要组件:
---------
- weighted_sum_method: 加权和法
- epsilon_constraint_method: ε-约束法
- identify_pareto_front: 帕累托前沿识别
- generate_pareto_front_weighted_sum: 生成帕累托前沿
- SimpleNSGAII: 简化NSGA-II算法
- plot_pareto_front_2d: 可视化帕累托前沿

Examples
--------
>>> from gwflow.optimization import SimpleNSGAII
>>> def f1(x): return x[0]**2 + x[1]**2
>>> def f2(x): return (x[0]-1)**2 + (x[1]-1)**2
>>> nsga = SimpleNSGAII([f1, f2], [(-5, 5), (-5, 5)])
>>> solutions, objectives = nsga.run()
"""

from .multi_objective import (
    weighted_sum_method,
    epsilon_constraint_method,
    is_pareto_dominated,
    identify_pareto_front,
    generate_pareto_front_weighted_sum,
    SimpleNSGAII,
    plot_pareto_front_2d
)

__all__ = [
    'weighted_sum_method',
    'epsilon_constraint_method',
    'is_pareto_dominated',
    'identify_pareto_front',
    'generate_pareto_front_weighted_sum',
    'SimpleNSGAII',
    'plot_pareto_front_2d',
]
