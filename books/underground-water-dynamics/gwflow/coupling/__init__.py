"""
gwflow.coupling - 地表地下水耦合模块

本模块提供地表水和地下水相互作用的建模工具，包括：
- 水量交换计算
- 耦合求解器
- 边界条件处理
- River包实现
- 越流模拟

主要功能：
-----------
1. 水量交换：
   - compute_exchange_flux: 计算地表地下水交换通量
   - leakance_coefficient: 计算渗漏系数
   - river_head_gradient: 计算河流-地下水水头梯度

2. 耦合求解器：
   - solve_coupled_weak: 弱耦合迭代求解
   - solve_coupled_strong: 强耦合联合求解
   - solve_sequential: 顺序耦合求解

3. 边界条件：
   - RiverBoundary: 河流边界条件类
   - LakeBoundary: 湖泊边界条件类
   - ETBoundary: 蒸散发边界条件类

使用示例：
---------
>>> from gwflow.coupling import RiverBoundary, compute_exchange_flux
>>> 
>>> # 创建河流边界
>>> river = RiverBoundary(
...     river_stage=30.0,
...     river_bottom=20.0,
...     river_bed_K=1.0,
...     river_bed_thickness=2.0,
...     river_width=50.0,
...     river_length=100.0
... )
>>> 
>>> # 计算河流与地下水交换通量
>>> flux = river.compute_flux(gw_head=25.0)
>>> print(f"交换通量: {flux:.2f} m³/day")

参考文献：
---------
1. McDonald & Harbaugh (1988). MODFLOW User Manual
2. Harbaugh (2005). MODFLOW-2005 Documentation
3. Sophocleous (2002). Interactions between groundwater and surface water

作者: gwflow开发团队
日期: 2025-11-02
版本: 0.5.0
"""

from .exchange import (
    compute_exchange_flux,
    leakance_coefficient,
    river_head_gradient,
    conductance_from_geometry
)

from .solver import (
    solve_coupled_weak,
    solve_sequential
)

from .boundary import (
    RiverBoundary,
    LakeBoundary,
    ETBoundary
)

from .river_package import (
    RiverPackage,
    RiverCell
)

from .leakage import (
    MultiLayerSystem,
    AquiferLayer,
    AquitardLayer,
    compute_steady_leakage_1d,
    hantush_jacob_solution,
    estimate_leakage_factor
)

__version__ = '0.5.0'

__all__ = [
    # 水量交换
    'compute_exchange_flux',
    'leakance_coefficient',
    'river_head_gradient',
    'conductance_from_geometry',
    
    # 耦合求解器
    'solve_coupled_weak',
    'solve_sequential',
    
    # 边界条件
    'RiverBoundary',
    'LakeBoundary',
    'ETBoundary',
    
    # River包
    'RiverPackage',
    'RiverCell',
    
    # 越流/多层系统
    'MultiLayerSystem',
    'AquiferLayer',
    'AquitardLayer',
    'compute_steady_leakage_1d',
    'hantush_jacob_solution',
    'estimate_leakage_factor',
]
