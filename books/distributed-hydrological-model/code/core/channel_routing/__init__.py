"""
河道汇流模块
==========

本模块提供河道汇流计算方法。

可用模块：
---------
- unit_hydrograph : 单元线法
- muskingum : Muskingum法
- kinematic_wave_channel : 运动波法

作者: CHS-Books项目组
"""

from .unit_hydrograph import UnitHydrograph, create_snyder_uh, create_scs_uh
from .muskingum import MuskingumChannel

__all__ = [
    'UnitHydrograph',
    'create_snyder_uh',
    'create_scs_uh',
    'MuskingumChannel',
]
