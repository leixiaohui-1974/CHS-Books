"""
核心模块包
=========

包含所有核心功能模块
"""

# 移除自动导入以避免循环依赖
# 用户需要显式导入所需模块
# 例如: from core.interpolation import thiessen_polygon

__all__ = [
    'basin',
    'interpolation',
    'runoff_generation',
    'utils',
]
