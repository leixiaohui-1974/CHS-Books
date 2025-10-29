"""
水箱模型库 - 教学专用

包含：
- SingleTank: 单水箱模型（一阶系统）
- DoubleTank: 双水箱串联模型（二阶系统）
- MultiTank: 多水箱网络模型（MIMO系统）
"""

from .single_tank import SingleTank
from .double_tank import DoubleTank

__all__ = ['SingleTank', 'DoubleTank']
__version__ = '1.1.0'
