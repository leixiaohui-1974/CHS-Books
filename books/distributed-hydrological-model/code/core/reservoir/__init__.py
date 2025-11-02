"""
水库调度模块
===========

提供水库优化调度功能。

子模块:
- operation_rules: 调度规则库
- optimization: 优化调度算法

作者: CHS-Books项目组
日期: 2025-11-02
"""

from .operation_rules import ReservoirRules, OperationRule
from .optimization import optimize_reservoir_operation

__all__ = [
    'ReservoirRules',
    'OperationRule',
    'optimize_reservoir_operation'
]

__version__ = '0.1.0'
