"""
数据同化模块
============

本模块提供多种数据同化方法。

主要功能：
- 集合卡尔曼滤波（EnKF）
- 粒子滤波（PF）
- 变分同化（4D-Var）

作者: CHS-Books项目组
日期: 2025-11-02
"""

from .enkf import EnKF, enkf_assimilation

__all__ = [
    'EnKF',
    'enkf_assimilation'
]

__version__ = '0.1.0'
