"""
gwflow.coupling.river_package - MODFLOW River包实现

本模块实现完整的MODFLOW River包功能，用于模拟河流网络与地下水的相互作用。

MODFLOW River包是地下水建模中最常用的边界条件之一，用于处理河流-地下水交互。

核心功能：
---------
1. RiverPackage类：管理河流网络
2. 河流单元（River Cell）管理
3. 多河段处理
4. 断开机制
5. 通量计算与统计

MODFLOW River包参数：
--------------------
对于每个河流单元，需要以下参数：
- STAGE: 河流水位 (m)
- COND: 水力传导度 (m²/day)
- RBOT: 河底高程 (m)
- Layer, Row, Col: 单元位置

参考文献：
---------
1. Prudic (1989). Documentation of a computer program to simulate 
   stream-aquifer relations
2. Harbaugh (2005). MODFLOW-2005, The U.S. Geological Survey modular 
   ground-water model

作者: gwflow开发团队
日期: 2025-11-02
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class RiverCell:
    """
    河流单元数据结构
    
    存储单个河流单元的所有参数，对应MODFLOW River包的一行数据。
    
    Attributes
    ----------
    layer : int
        层号（对于二维模型，通常为0）
    row : int
        行号
    col : int
        列号
    stage : float
        河流水位 (m)
    conductance : float
        水力传导度 (m²/day)
    bottom : float
        河底高程 (m)
    segment_id : int, optional
        河段编号，用于分组统计
    reach_id : int, optional
        河道段编号
    
    Examples
    --------
    >>> cell = RiverCell(
    ...     layer=0, row=5, col=10,
    ...     stage=30.0,
    ...     conductance=1000.0,
    ...     bottom=20.0,
    ...     segment_id=1
    ... )
    """
    layer: int
    row: int
    col: int
    stage: float
    conductance: float
    bottom: float
    segment_id: Optional[int] = None
    reach_id: Optional[int] = None
    
    def __post_init__(self):
        """验证参数"""
        if self.stage < self.bottom:
            raise ValueError(
                f"stage ({self.stage}) must be >= bottom ({self.bottom})"
            )
        if self.conductance < 0:
            raise ValueError(f"conductance must be non-negative")


class RiverPackage:
    """
    MODFLOW River包
    
    管理河流网络，计算河流与地下水的交换通量。
    
    Parameters
    ----------
    name : str, default='RIV'
        River包名称
    
    Attributes
    ----------
    river_cells : list of RiverCell
        所有河流单元列表
    n_cells : int
        河流单元总数
    
    Methods
    -------
    add_river_cell : 添加单个河流单元
    add_river_segment : 添加河流河段
    compute_flux : 计算所有单元的交换通量
    get_segment_flux : 获取指定河段的总通量
    update_stage : 更新河流水位
    
    Examples
    --------
    >>> # 创建River包
    >>> riv = RiverPackage(name='MainRiver')
    >>> 
    >>> # 添加河流单元
    >>> riv.add_river_cell(
    ...     layer=0, row=5, col=10,
    ...     stage=30.0, conductance=1000.0, bottom=20.0
    ... )
    >>> 
    >>> # 计算通量
    >>> h_gw = np.ones((10, 20)) * 25.0
    >>> fluxes = riv.compute_flux(h_gw)
    >>> 
    >>> # 获取总通量
    >>> total_flux = riv.get_total_flux(h_gw)
    >>> print(f"Total river flux: {total_flux:.2f} m³/day")
    
    Notes
    -----
    River包使用第三类边界条件（Cauchy边界），通量正比于水头差。
    
    断开机制确保当地下水位降到河底以下时，通量不会继续线性增大。
    """
    
    def __init__(self, name: str = 'RIV'):
        self.name = name
        self.river_cells: List[RiverCell] = []
    
    @property
    def n_cells(self) -> int:
        """河流单元总数"""
        return len(self.river_cells)
    
    def add_river_cell(
        self,
        layer: int,
        row: int,
        col: int,
        stage: float,
        conductance: float,
        bottom: float,
        segment_id: Optional[int] = None,
        reach_id: Optional[int] = None
    ) -> None:
        """
        添加单个河流单元
        
        Parameters
        ----------
        layer : int
            层号
        row : int
            行号
        col : int
            列号
        stage : float
            河流水位 (m)
        conductance : float
            水力传导度 (m²/day)
        bottom : float
            河底高程 (m)
        segment_id : int, optional
            河段编号
        reach_id : int, optional
            河道段编号
        
        Examples
        --------
        >>> riv = RiverPackage()
        >>> riv.add_river_cell(0, 5, 10, 30.0, 1000.0, 20.0, segment_id=1)
        """
        cell = RiverCell(
            layer=layer,
            row=row,
            col=col,
            stage=stage,
            conductance=conductance,
            bottom=bottom,
            segment_id=segment_id,
            reach_id=reach_id
        )
        self.river_cells.append(cell)
    
    def add_river_segment(
        self,
        cells: List[Tuple[int, int]],
        stage_start: float,
        stage_end: float,
        conductance: float,
        bottom: float,
        segment_id: int,
        layer: int = 0
    ) -> None:
        """
        添加河流河段（多个连续单元）
        
        河段的水位线性插值，从起点到终点。
        
        Parameters
        ----------
        cells : list of tuple
            单元坐标列表 [(row1, col1), (row2, col2), ...]
        stage_start : float
            起点水位 (m)
        stage_end : float
            终点水位 (m)
        conductance : float
            水力传导度 (m²/day)，所有单元相同
        bottom : float
            河底高程 (m)，所有单元相同
        segment_id : int
            河段编号
        layer : int, default=0
            层号
        
        Examples
        --------
        >>> riv = RiverPackage()
        >>> # 添加从(5,10)到(5,15)的河段
        >>> cells = [(5, 10), (5, 11), (5, 12), (5, 13), (5, 14), (5, 15)]
        >>> riv.add_river_segment(
        ...     cells=cells,
        ...     stage_start=30.0,
        ...     stage_end=28.0,
        ...     conductance=1000.0,
        ...     bottom=20.0,
        ...     segment_id=1
        ... )
        """
        n = len(cells)
        if n == 0:
            return
        
        # 线性插值水位
        if n == 1:
            stages = [stage_start]
        else:
            stages = np.linspace(stage_start, stage_end, n)
        
        # 添加每个单元
        for i, (row, col) in enumerate(cells):
            self.add_river_cell(
                layer=layer,
                row=row,
                col=col,
                stage=stages[i],
                conductance=conductance,
                bottom=bottom,
                segment_id=segment_id,
                reach_id=i
            )
    
    def compute_flux(
        self,
        head: np.ndarray,
        use_disconnection: bool = True
    ) -> np.ndarray:
        """
        计算所有河流单元的交换通量
        
        Parameters
        ----------
        head : array
            地下水水头，shape可以是：
            - (nrow, ncol) 对于二维模型
            - (nlay, nrow, ncol) 对于三维模型
        use_disconnection : bool, default=True
            是否使用断开机制
        
        Returns
        -------
        fluxes : array, shape (n_cells,)
            每个河流单元的交换通量 (m³/day)
            正值：河流补给地下水
            负值：地下水排泄到河流
        
        Examples
        --------
        >>> riv = RiverPackage()
        >>> # ... 添加河流单元 ...
        >>> h_gw = np.ones((10, 20)) * 25.0
        >>> fluxes = riv.compute_flux(h_gw)
        >>> print(f"Total flux: {np.sum(fluxes):.2f} m³/day")
        """
        fluxes = np.zeros(self.n_cells)
        
        for i, cell in enumerate(self.river_cells):
            # 获取地下水水头
            if head.ndim == 2:
                # 二维模型
                h_gw = head[cell.row, cell.col]
            elif head.ndim == 3:
                # 三维模型
                h_gw = head[cell.layer, cell.row, cell.col]
            else:
                raise ValueError(f"head must be 2D or 3D array, got shape {head.shape}")
            
            # 计算通量
            if use_disconnection:
                # 断开机制
                if h_gw > cell.bottom:
                    # 正常连接
                    flux = cell.conductance * (cell.stage - h_gw)
                else:
                    # 断开，限制通量
                    flux = cell.conductance * (cell.stage - cell.bottom)
            else:
                # 标准计算
                flux = cell.conductance * (cell.stage - h_gw)
            
            fluxes[i] = flux
        
        return fluxes
    
    def get_total_flux(
        self,
        head: np.ndarray,
        use_disconnection: bool = True
    ) -> float:
        """
        获取河流系统的总交换通量
        
        Parameters
        ----------
        head : array
            地下水水头
        use_disconnection : bool, default=True
            是否使用断开机制
        
        Returns
        -------
        total_flux : float
            总交换通量 (m³/day)
        """
        fluxes = self.compute_flux(head, use_disconnection)
        return np.sum(fluxes)
    
    def get_segment_flux(
        self,
        segment_id: int,
        head: np.ndarray,
        use_disconnection: bool = True
    ) -> float:
        """
        获取指定河段的总通量
        
        Parameters
        ----------
        segment_id : int
            河段编号
        head : array
            地下水水头
        use_disconnection : bool, default=True
            是否使用断开机制
        
        Returns
        -------
        segment_flux : float
            河段总通量 (m³/day)
        """
        fluxes = self.compute_flux(head, use_disconnection)
        
        segment_flux = 0.0
        for i, cell in enumerate(self.river_cells):
            if cell.segment_id == segment_id:
                segment_flux += fluxes[i]
        
        return segment_flux
    
    def get_segment_statistics(
        self,
        head: np.ndarray,
        use_disconnection: bool = True
    ) -> Dict[int, Dict[str, float]]:
        """
        获取各河段的统计信息
        
        Parameters
        ----------
        head : array
            地下水水头
        use_disconnection : bool, default=True
            是否使用断开机制
        
        Returns
        -------
        stats : dict
            字典，键为segment_id，值为统计信息：
            - 'total_flux': 总通量 (m³/day)
            - 'n_cells': 单元数
            - 'avg_flux': 平均通量 (m³/day/cell)
            - 'max_flux': 最大通量 (m³/day)
            - 'min_flux': 最小通量 (m³/day)
        
        Examples
        --------
        >>> stats = riv.get_segment_statistics(h_gw)
        >>> for seg_id, info in stats.items():
        ...     print(f"Segment {seg_id}: {info['total_flux']:.2f} m³/day")
        """
        fluxes = self.compute_flux(head, use_disconnection)
        
        # 按河段分组
        segment_fluxes: Dict[int, List[float]] = {}
        for i, cell in enumerate(self.river_cells):
            seg_id = cell.segment_id
            if seg_id is None:
                seg_id = -1  # 未分配河段的单元
            
            if seg_id not in segment_fluxes:
                segment_fluxes[seg_id] = []
            segment_fluxes[seg_id].append(fluxes[i])
        
        # 计算统计
        stats = {}
        for seg_id, flux_list in segment_fluxes.items():
            flux_array = np.array(flux_list)
            stats[seg_id] = {
                'total_flux': np.sum(flux_array),
                'n_cells': len(flux_list),
                'avg_flux': np.mean(flux_array),
                'max_flux': np.max(flux_array),
                'min_flux': np.min(flux_array)
            }
        
        return stats
    
    def update_stage(
        self,
        new_stage: float,
        segment_id: Optional[int] = None
    ) -> None:
        """
        更新河流水位
        
        Parameters
        ----------
        new_stage : float
            新的河流水位 (m)
        segment_id : int, optional
            如果指定，只更新该河段
            如果为None，更新所有单元
        
        Examples
        --------
        >>> # 更新所有单元
        >>> riv.update_stage(32.0)
        >>> 
        >>> # 只更新河段1
        >>> riv.update_stage(32.0, segment_id=1)
        """
        for cell in self.river_cells:
            if segment_id is None or cell.segment_id == segment_id:
                if new_stage < cell.bottom:
                    raise ValueError(
                        f"new_stage ({new_stage}) must be >= bottom ({cell.bottom})"
                    )
                cell.stage = new_stage
    
    def apply_flux_to_source(
        self,
        head: np.ndarray,
        cell_volume: np.ndarray,
        use_disconnection: bool = True
    ) -> np.ndarray:
        """
        将河流通量应用为源汇项
        
        Parameters
        ----------
        head : array
            地下水水头
        cell_volume : array
            单元体积 (m³)，与head相同shape
        use_disconnection : bool, default=True
            是否使用断开机制
        
        Returns
        -------
        source : array
            源汇项 (1/day)，与head相同shape
        
        Notes
        -----
        源汇项定义为：q = Q / V
        其中 Q 是体积通量 (m³/day)，V 是单元体积 (m³)
        """
        source = np.zeros_like(head)
        fluxes = self.compute_flux(head, use_disconnection)
        
        for i, cell in enumerate(self.river_cells):
            if head.ndim == 2:
                vol = cell_volume[cell.row, cell.col]
                source[cell.row, cell.col] += fluxes[i] / vol
            elif head.ndim == 3:
                vol = cell_volume[cell.layer, cell.row, cell.col]
                source[cell.layer, cell.row, cell.col] += fluxes[i] / vol
        
        return source
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取River包摘要信息
        
        Returns
        -------
        summary : dict
            摘要信息
        """
        segments = set(cell.segment_id for cell in self.river_cells 
                      if cell.segment_id is not None)
        
        stages = [cell.stage for cell in self.river_cells]
        conductances = [cell.conductance for cell in self.river_cells]
        
        return {
            'name': self.name,
            'n_cells': self.n_cells,
            'n_segments': len(segments),
            'stage_range': (np.min(stages), np.max(stages)) if stages else (None, None),
            'conductance_range': (np.min(conductances), np.max(conductances)) if conductances else (None, None)
        }
    
    def __repr__(self) -> str:
        return f"RiverPackage(name='{self.name}', n_cells={self.n_cells})"
