"""
水力学模型模块
包含各种渠道、管道和水工建筑物的模型
"""

from .channel import TrapezoidalChannel, RectangularChannel, CircularChannel

__all__ = [
    "TrapezoidalChannel",
    "RectangularChannel",
    "CircularChannel",
]
