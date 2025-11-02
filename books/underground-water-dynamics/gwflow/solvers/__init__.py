"""
solvers - 求解器模块
===================

提供稳态和瞬态地下水流动求解器。
"""

from gwflow.solvers.steady_state import solve_1d_steady_gw, solve_2d_steady_gw
from gwflow.solvers.transient import solve_2d_transient_gw

__all__ = [
    "solve_1d_steady_gw",
    "solve_2d_steady_gw",
    "solve_2d_transient_gw",
]
