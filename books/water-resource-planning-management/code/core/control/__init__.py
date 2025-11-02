"""
控制模块

提供实时调度与控制算法：
- PID: 比例-积分-微分控制
- MPC: 模型预测控制
- LQR: 线性二次调节器
- Saint-Venant: 明渠水力学方程求解
"""

from .pid_controller import PIDController
from .mpc_controller import MPCController
from .saint_venant import SaintVenantSolver

__all__ = [
    "PIDController",
    "MPCController",
    "SaintVenantSolver",
]
