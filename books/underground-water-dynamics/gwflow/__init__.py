"""
gwflow - 地下水流动模拟工具包
=====================================

一个用于地下水动力学建模、仿真与智能管理的Python工具包。

主要模块：
- grid: 网格生成（结构化和非结构化）
- solvers: 求解器（稳态、瞬态、有限差分、有限元）
- calibration: 参数率定（优化、PEST、贝叶斯）
- coupling: 耦合模型（地表地下水）
- transport: 运移模拟（污染物、热）
- surrogate: 代理模型（GPR、神经网络、POD-ROM）
- digital_twin: 数字孪生（卡尔曼滤波、虚拟传感器）
- optimization: 优化管理（开采调度、MPC）
- visualization: 可视化工具
- utils: 实用工具函数

示例：
    >>> from gwflow.solvers import solve_1d_steady_gw
    >>> h = solve_1d_steady_gw(K=10.0, L=1000.0, h0=20.0, hL=10.0, nx=50)
"""

__version__ = "0.1.0"
__author__ = "Underground Water Dynamics Team"
__license__ = "MIT"

# 导入核心功能
from gwflow.solvers.steady_state import solve_1d_steady_gw, solve_2d_steady_gw
from gwflow.solvers.transient import solve_2d_transient_gw
from gwflow.grid.structured import create_1d_grid, create_2d_grid

__all__ = [
    "solve_1d_steady_gw",
    "solve_2d_steady_gw",
    "solve_2d_transient_gw",
    "create_1d_grid",
    "create_2d_grid",
]
