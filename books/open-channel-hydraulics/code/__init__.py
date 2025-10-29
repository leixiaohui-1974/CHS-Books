"""
明渠水力学计算代码库
Open Channel Hydraulics Computation Library

本模块提供明渠水力学计算的完整实现，包括：
- 恒定流计算（均匀流、非均匀流）
- 非恒定流计算（圣维南方程求解）
- 水工建筑物计算
- 管道水力学计算
- 混合系统计算

作者：CHS-Books项目
版本：v1.0
"""

__version__ = "1.0.0"
__author__ = "CHS-Books Project"

# 模块导出
__all__ = [
    "models",
    "solvers",
    "utils",
]
