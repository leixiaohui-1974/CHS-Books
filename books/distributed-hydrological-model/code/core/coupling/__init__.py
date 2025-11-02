"""
耦合模拟模块
===========

提供水文-水动力耦合模拟功能。

子模块:
- saint_venant: 一维Saint-Venant方程求解
- hydro_interface: 水文与水动力接口

作者: CHS-Books项目组
日期: 2025-11-02
"""

from .saint_venant import SaintVenant1D, solve_saint_venant
from .hydro_interface import HydroInterface, couple_simulation

__all__ = [
    'SaintVenant1D',
    'solve_saint_venant',
    'HydroInterface',
    'couple_simulation'
]

__version__ = '0.1.0'
