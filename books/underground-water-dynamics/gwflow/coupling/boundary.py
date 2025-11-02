"""
gwflow.coupling.boundary - 耦合边界条件类

本模块提供地表地下水耦合的边界条件类，包括：
- RiverBoundary: 河流边界
- LakeBoundary: 湖泊边界  
- ETBoundary: 蒸散发边界

这些类封装了边界条件的参数和计算方法，便于在耦合模型中使用。

作者: gwflow开发团队
日期: 2025-11-02
"""

import numpy as np
from typing import Optional, Union


class RiverBoundary:
    """
    河流边界条件
    
    模拟河流与地下水的相互作用，基于MODFLOW River包的原理。
    
    核心公式：
        Q = C * (H_river - h_gw)  当 h_gw > river_bottom
        Q = C * (H_river - river_bottom)  当 h_gw <= river_bottom
    
    其中：
    - Q: 交换通量 (m³/day)
    - C: 水力传导度 (m²/day)
    - H_river: 河流水位 (m)
    - h_gw: 地下水水头 (m)
    - river_bottom: 河底高程 (m)
    
    Parameters
    ----------
    river_stage : float
        河流水位 (m)
    river_bottom : float
        河底高程 (m)
    river_bed_K : float
        河床渗透系数 (m/day)
    river_bed_thickness : float
        河床厚度 (m)
    river_width : float
        河宽 (m)
    river_length : float
        河段长度 (m)
    
    Attributes
    ----------
    conductance : float
        水力传导度 (m²/day)，自动计算
    leakance : float
        渗漏系数 (1/day)，自动计算
    
    Examples
    --------
    >>> river = RiverBoundary(
    ...     river_stage=30.0,
    ...     river_bottom=20.0,
    ...     river_bed_K=1.0,
    ...     river_bed_thickness=2.0,
    ...     river_width=50.0,
    ...     river_length=100.0
    ... )
    >>> 
    >>> # 计算交换通量
    >>> flux = river.compute_flux(gw_head=25.0)
    >>> print(f"交换通量: {flux:.2f} m³/day")
    >>> 
    >>> # 更新河流水位
    >>> river.update_stage(32.0)
    
    References
    ----------
    1. McDonald & Harbaugh (1988). MODFLOW User Manual
    2. Prudic (1989). Documentation of River Package
    """
    
    def __init__(
        self,
        river_stage: float,
        river_bottom: float,
        river_bed_K: float,
        river_bed_thickness: float,
        river_width: float,
        river_length: float
    ):
        # 验证输入
        if river_stage < river_bottom:
            raise ValueError(
                f"river_stage ({river_stage}) must be >= river_bottom ({river_bottom})"
            )
        if river_bed_K <= 0:
            raise ValueError(f"river_bed_K must be positive, got {river_bed_K}")
        if river_bed_thickness <= 0:
            raise ValueError(f"river_bed_thickness must be positive")
        if river_width <= 0:
            raise ValueError(f"river_width must be positive")
        if river_length <= 0:
            raise ValueError(f"river_length must be positive")
        
        # 存储参数
        self.river_stage = river_stage
        self.river_bottom = river_bottom
        self.river_bed_K = river_bed_K
        self.river_bed_thickness = river_bed_thickness
        self.river_width = river_width
        self.river_length = river_length
        
        # 计算派生参数
        self.area = river_width * river_length
        self.conductance = (
            river_bed_K * self.area / river_bed_thickness
        )
        self.leakance = river_bed_K / river_bed_thickness
    
    def compute_flux(
        self,
        gw_head: Union[float, np.ndarray],
        method: str = 'standard'
    ) -> Union[float, np.ndarray]:
        """
        计算河流-地下水交换通量
        
        Parameters
        ----------
        gw_head : float or array
            地下水水头 (m)
        method : str, default='standard'
            计算方法：
            - 'standard': 标准方法，不考虑断开
            - 'disconnected': 考虑河流断开机制
        
        Returns
        -------
        flux : float or array
            交换通量 (m³/day)
            正值：河流补给地下水
            负值：地下水排泄到河流
        """
        if method == 'standard':
            # 标准计算
            flux = self.conductance * (self.river_stage - gw_head)
        
        elif method == 'disconnected':
            # 断开机制
            gw_head = np.asarray(gw_head)
            
            # 当地下水位低于河底时，河流不能继续向下补给
            # 此时通量被限制为 C * (H_river - river_bottom)
            gw_head_effective = np.maximum(gw_head, self.river_bottom)
            
            flux = self.conductance * (self.river_stage - gw_head_effective)
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return flux
    
    def update_stage(self, new_stage: float):
        """
        更新河流水位
        
        Parameters
        ----------
        new_stage : float
            新的河流水位 (m)
        """
        if new_stage < self.river_bottom:
            raise ValueError(
                f"new_stage ({new_stage}) must be >= river_bottom ({self.river_bottom})"
            )
        self.river_stage = new_stage
    
    def update_bottom(self, new_bottom: float):
        """
        更新河底高程
        
        Parameters
        ----------
        new_bottom : float
            新的河底高程 (m)
        """
        if new_bottom > self.river_stage:
            raise ValueError(
                f"new_bottom ({new_bottom}) must be <= river_stage ({self.river_stage})"
            )
        self.river_bottom = new_bottom
    
    def __repr__(self) -> str:
        return (
            f"RiverBoundary("
            f"stage={self.river_stage:.2f}m, "
            f"bottom={self.river_bottom:.2f}m, "
            f"C={self.conductance:.2e}m²/day)"
        )


class LakeBoundary:
    """
    湖泊边界条件
    
    模拟湖泊与地下水的相互作用。
    与河流边界类似，但通常面积更大，可能不考虑断开机制。
    
    核心公式：
        Q = C * (H_lake - h_gw)
        C = K_bed * A / b_bed
    
    Parameters
    ----------
    lake_stage : float
        湖泊水位 (m)
    lake_bottom : float
        湖底高程 (m)
    lake_bed_K : float
        湖底渗透系数 (m/day)
    lake_bed_thickness : float
        湖底厚度 (m)
    lake_area : float
        湖泊面积 (m²)
    
    Examples
    --------
    >>> lake = LakeBoundary(
    ...     lake_stage=50.0,
    ...     lake_bottom=45.0,
    ...     lake_bed_K=0.5,
    ...     lake_bed_thickness=3.0,
    ...     lake_area=10000.0
    ... )
    >>> 
    >>> flux = lake.compute_flux(gw_head=48.0)
    >>> print(f"交换通量: {flux:.2f} m³/day")
    """
    
    def __init__(
        self,
        lake_stage: float,
        lake_bottom: float,
        lake_bed_K: float,
        lake_bed_thickness: float,
        lake_area: float
    ):
        # 验证输入
        if lake_stage < lake_bottom:
            raise ValueError("lake_stage must be >= lake_bottom")
        if lake_bed_K <= 0:
            raise ValueError("lake_bed_K must be positive")
        if lake_bed_thickness <= 0:
            raise ValueError("lake_bed_thickness must be positive")
        if lake_area <= 0:
            raise ValueError("lake_area must be positive")
        
        # 存储参数
        self.lake_stage = lake_stage
        self.lake_bottom = lake_bottom
        self.lake_bed_K = lake_bed_K
        self.lake_bed_thickness = lake_bed_thickness
        self.lake_area = lake_area
        
        # 计算传导度
        self.conductance = lake_bed_K * lake_area / lake_bed_thickness
        self.leakance = lake_bed_K / lake_bed_thickness
    
    def compute_flux(
        self,
        gw_head: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        计算湖泊-地下水交换通量
        
        Parameters
        ----------
        gw_head : float or array
            地下水水头 (m)
        
        Returns
        -------
        flux : float or array
            交换通量 (m³/day)
            正值：湖泊补给地下水
            负值：地下水排泄到湖泊
        """
        return self.conductance * (self.lake_stage - gw_head)
    
    def update_stage(self, new_stage: float):
        """更新湖泊水位"""
        if new_stage < self.lake_bottom:
            raise ValueError("new_stage must be >= lake_bottom")
        self.lake_stage = new_stage
    
    def __repr__(self) -> str:
        return (
            f"LakeBoundary("
            f"stage={self.lake_stage:.2f}m, "
            f"area={self.lake_area:.2e}m², "
            f"C={self.conductance:.2e}m²/day)"
        )


class ETBoundary:
    """
    蒸散发边界条件
    
    模拟地下水的蒸散发过程。
    蒸散发率取决于地下水位深度。
    
    核心公式：
        当 h >= z_surface: ET = ET_max
        当 h <= z_surface - d: ET = 0
        其他情况: ET = ET_max * (h - (z_surface - d)) / d
    
    其中：
    - h: 地下水水头
    - z_surface: 地表高程
    - d: 消退深度（extinction depth）
    - ET_max: 最大蒸散发率
    
    Parameters
    ----------
    et_max : float
        最大蒸散发率 (m/day)
    extinction_depth : float
        蒸散发消退深度 (m)
    land_surface_elevation : float
        地表高程 (m)
    
    Examples
    --------
    >>> et = ETBoundary(
    ...     et_max=0.005,
    ...     extinction_depth=3.0,
    ...     land_surface_elevation=50.0
    ... )
    >>> 
    >>> # 地下水位在地表以下1m
    >>> et_rate = et.compute_et(gw_head=49.0)
    >>> print(f"ET率: {et_rate:.5f} m/day")
    
    Notes
    -----
    蒸散发是地下水的重要消耗项，特别是在：
    - 浅层地下水区域
    - 植被覆盖区域
    - 蒸发潜力大的干旱区
    
    References
    ----------
    1. Banta (2000). MODFLOW-2000, the Evapotranspiration Package
    """
    
    def __init__(
        self,
        et_max: float,
        extinction_depth: float,
        land_surface_elevation: float
    ):
        # 验证输入
        if et_max < 0:
            raise ValueError(f"et_max must be non-negative, got {et_max}")
        if extinction_depth <= 0:
            raise ValueError(f"extinction_depth must be positive")
        
        # 存储参数
        self.et_max = et_max
        self.extinction_depth = extinction_depth
        self.land_surface_elevation = land_surface_elevation
    
    def compute_et(
        self,
        gw_head: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """
        计算实际蒸散发率
        
        Parameters
        ----------
        gw_head : float or array
            地下水水头 (m)
        
        Returns
        -------
        et : float or array
            实际蒸散发率 (m/day)
        """
        gw_head = np.asarray(gw_head)
        
        # 计算地下水位深度（地表以下的深度）
        depth_below_surface = self.land_surface_elevation - gw_head
        
        # 初始化ET数组
        et = np.zeros_like(gw_head, dtype=float)
        
        # 情况1: 地下水位在地表以上或地表处
        mask1 = depth_below_surface <= 0
        et[mask1] = self.et_max
        
        # 情况2: 地下水位在消退深度以内
        mask2 = (depth_below_surface > 0) & (depth_below_surface < self.extinction_depth)
        ratio = 1.0 - depth_below_surface[mask2] / self.extinction_depth
        et[mask2] = self.et_max * ratio
        
        # 情况3: 地下水位超过消退深度
        # et = 0 (已初始化)
        
        # 如果输入是标量，返回标量
        if np.ndim(gw_head) == 0:
            return float(et)
        
        return et
    
    def compute_et_flux(
        self,
        gw_head: Union[float, np.ndarray],
        area: float
    ) -> Union[float, np.ndarray]:
        """
        计算蒸散发体积通量
        
        Parameters
        ----------
        gw_head : float or array
            地下水水头 (m)
        area : float
            单元面积 (m²)
        
        Returns
        -------
        flux : float or array
            蒸散发体积通量 (m³/day)，为负值（消耗）
        """
        et_rate = self.compute_et(gw_head)
        return -et_rate * area  # 负值表示消耗
    
    def update_et_max(self, new_et_max: float):
        """更新最大蒸散发率"""
        if new_et_max < 0:
            raise ValueError("new_et_max must be non-negative")
        self.et_max = new_et_max
    
    def __repr__(self) -> str:
        return (
            f"ETBoundary("
            f"ET_max={self.et_max:.5f}m/day, "
            f"extinction_depth={self.extinction_depth:.2f}m, "
            f"surface_elev={self.land_surface_elevation:.2f}m)"
        )
