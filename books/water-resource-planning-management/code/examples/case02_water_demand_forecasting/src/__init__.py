"""
案例1.2：城市需水预测 - 源代码模块
"""

from .quota_method import QuotaForecaster
from .trend_analysis import TrendForecaster
from .grey_model import GreyForecaster

__all__ = [
    "QuotaForecaster",
    "TrendForecaster",
    "GreyForecaster",
]
