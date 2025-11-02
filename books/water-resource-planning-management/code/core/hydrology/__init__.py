"""
水文计算模块

提供水文分析的核心功能：
- water_balance: 水量平衡计算
- frequency_analysis: 频率分析
- runoff_model: 径流模型
- forecast: 水文预报
"""

from .water_balance import calculate_water_balance, WaterBalanceModel
from .runoff_calculation import (
    calculate_runoff_coefficient,
    calculate_design_flood,
    estimate_annual_runoff,
)

__all__ = [
    "calculate_water_balance",
    "WaterBalanceModel",
    "calculate_runoff_coefficient",
    "calculate_design_flood",
    "estimate_annual_runoff",
]
