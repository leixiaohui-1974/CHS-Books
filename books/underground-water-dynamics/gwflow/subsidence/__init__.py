"""
gwflow.subsidence - 地面沉降模拟模块

本模块提供地面沉降模拟的完整功能，包括：
- Terzaghi固结理论
- 土层压缩计算
- 沉降预测
- 时间过程模拟
"""

from .consolidation import (
    SoilLayer,
    terzaghi_consolidation_1d,
    consolidation_degree,
    consolidation_settlement,
    compute_settlement_time
)

from .subsidence_model import (
    SubsidenceModel,
    compute_effective_stress_change,
    compute_layer_compression
)

__version__ = '0.6.0'

__all__ = [
    # 土层类
    'SoilLayer',
    
    # 固结理论
    'terzaghi_consolidation_1d',
    'consolidation_degree',
    'consolidation_settlement',
    'compute_settlement_time',
    
    # 沉降模型
    'SubsidenceModel',
    'compute_effective_stress_change',
    'compute_layer_compression',
]
