"""
visualization - 可视化模块
=========================

提供地下水模拟结果的可视化功能。
"""

from gwflow.visualization.plots import (
    plot_1d_head,
    plot_2d_head,
    plot_2d_velocity,
    plot_transient_animation
)

# Aliases for backward compatibility
plot_2d_contour = plot_2d_head

__all__ = [
    "plot_1d_head",
    "plot_2d_head",
    "plot_2d_velocity",
    "plot_transient_animation",
    "plot_2d_contour",  # alias
]
