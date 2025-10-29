"""
求解器模块
包含恒定流和非恒定流的各种求解器
"""

from .steady.uniform_flow import UniformFlowSolver

__all__ = [
    "UniformFlowSolver",
]
