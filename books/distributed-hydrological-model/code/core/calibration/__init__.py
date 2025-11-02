"""
参数率定模块
============

本模块提供多种参数率定和优化算法。

主要功能：
- SCE-UA算法（Shuffled Complex Evolution）
- 遗传算法（Genetic Algorithm）
- 粒子群优化（Particle Swarm Optimization）
- 目标函数计算
- 参数约束处理

作者: CHS-Books项目组
日期: 2025-11-02
"""

from .sce_ua import SCEUA, optimize_sce_ua
from .objective import (
    ObjectiveFunction,
    nash_sutcliffe_objective,
    rmse_objective,
    multi_objective
)

__all__ = [
    'SCEUA',
    'optimize_sce_ua',
    'ObjectiveFunction',
    'nash_sutcliffe_objective',
    'rmse_objective',
    'multi_objective'
]

__version__ = '0.1.0'
