"""
工具函数模块
===========

提供通用的数据处理、评估指标、绘图等工具函数
"""

from .data_io import *
from .metrics import *
from .time_series import *
from .plotting import *

__all__ = [
    # data_io
    'read_rainfall_data',
    'read_discharge_data',
    'save_results',
    # metrics
    'nash_sutcliffe',
    'rmse',
    'relative_error',
    'peak_error',
    # time_series
    'resample_timeseries',
    'fill_missing_data',
    # plotting
    'plot_hydrograph',
    'plot_scatter',
]
