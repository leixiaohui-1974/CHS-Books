"""
空间插值模块
===========

提供各种空间插值方法
"""

from .thiessen import thiessen_polygon, thiessen_weights
from .idw import inverse_distance_weighting
from .kriging import ordinary_kriging, variogram

__all__ = [
    'thiessen_polygon',
    'thiessen_weights',
    'inverse_distance_weighting',
    'ordinary_kriging',
    'variogram',
]
