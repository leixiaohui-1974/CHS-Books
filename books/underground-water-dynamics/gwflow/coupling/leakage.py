"""
gwflow.coupling.leakage - 多层含水层越流模拟

本模块提供多层含水层系统中垂向越流的计算方法。

越流（Leakage）是指水量通过弱透水层在不同含水层之间的垂向流动。
这是多层含水层系统中水量交换的重要机制。

核心概念：
---------
1. 弱透水层（Aquitard）：
   - 渗透系数很小的地层
   - 阻碍垂向流动
   - 但仍允许缓慢的水量交换

2. 越流系数（Leakance）：
   L = K_aquitard / b_aquitard  (1/day)
   表示单位水头差下的越流能力

3. 越流通量：
   Q = C * (h_upper - h_lower)
   C = K_aquitard * A / b_aquitard  (m²/day)

4. 多层系统：
   Layer 1 (Confined)
       ↕ Leakage_1
   Aquitard_1
       ↕ Leakage_2
   Layer 2 (Confined)
       ↕ Leakage_3
   Aquitard_2
       ↕
   Layer 3 (Confined)

参考文献：
---------
1. McDonald & Harbaugh (1988). MODFLOW User Manual
2. Hantush (1960). Modification of the theory of leaky aquifers
3. Neuman & Witherspoon (1969). Theory of flow in a confined two aquifer system

作者: gwflow开发团队
日期: 2025-11-02
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class AquitardLayer:
    """
    弱透水层参数
    
    Attributes
    ----------
    top_elevation : float
        顶板高程 (m)
    bottom_elevation : float
        底板高程 (m)
    K_vertical : float
        垂向渗透系数 (m/day)
    storage : float, optional
        储水系数（瞬态模拟用）
    
    Properties
    ----------
    thickness : float
        厚度 (m)
    leakance : float
        渗漏系数 (1/day)
    """
    top_elevation: float
    bottom_elevation: float
    K_vertical: float
    storage: Optional[float] = None
    
    @property
    def thickness(self) -> float:
        """弱透水层厚度"""
        return self.top_elevation - self.bottom_elevation
    
    @property
    def leakance(self) -> float:
        """渗漏系数 L = K / b"""
        return self.K_vertical / self.thickness
    
    def __post_init__(self):
        if self.top_elevation <= self.bottom_elevation:
            raise ValueError("top_elevation must be > bottom_elevation")
        if self.K_vertical <= 0:
            raise ValueError("K_vertical must be positive")


@dataclass
class AquiferLayer:
    """
    含水层参数
    
    Attributes
    ----------
    layer_id : int
        层编号（从上到下：0, 1, 2, ...）
    top_elevation : float
        顶板高程 (m)
    bottom_elevation : float
        底板高程 (m)
    K_horizontal : float
        水平渗透系数 (m/day)
    storage : float
        储水系数（承压：储水系数；无压：给水度）
    is_confined : bool
        是否承压
    
    Properties
    ----------
    thickness : float
        厚度 (m)
    transmissivity : float
        导水系数 T = K * b (m²/day)
    """
    layer_id: int
    top_elevation: float
    bottom_elevation: float
    K_horizontal: float
    storage: float
    is_confined: bool = True
    
    @property
    def thickness(self) -> float:
        """含水层厚度"""
        return self.top_elevation - self.bottom_elevation
    
    @property
    def transmissivity(self) -> float:
        """导水系数"""
        return self.K_horizontal * self.thickness
    
    def __post_init__(self):
        if self.top_elevation <= self.bottom_elevation:
            raise ValueError("top_elevation must be > bottom_elevation")
        if self.K_horizontal <= 0:
            raise ValueError("K_horizontal must be positive")
        if self.storage <= 0:
            raise ValueError("storage must be positive")


class MultiLayerSystem:
    """
    多层含水层系统
    
    管理多层含水层和弱透水层，计算层间越流。
    
    Parameters
    ----------
    name : str
        系统名称
    
    Attributes
    ----------
    aquifer_layers : list of AquiferLayer
        含水层列表
    aquitard_layers : list of AquitardLayer
        弱透水层列表
    n_layers : int
        含水层数量
    
    Methods
    -------
    add_aquifer_layer : 添加含水层
    add_aquitard_layer : 添加弱透水层
    compute_leakage : 计算越流通量
    setup_from_arrays : 从数组批量设置
    
    Examples
    --------
    >>> # 创建三层系统
    >>> system = MultiLayerSystem(name='ThreeLayerSystem')
    >>> 
    >>> # 添加第一层含水层
    >>> system.add_aquifer_layer(
    ...     layer_id=0,
    ...     top_elevation=100.0,
    ...     bottom_elevation=80.0,
    ...     K_horizontal=20.0,
    ...     storage=0.0001
    ... )
    >>> 
    >>> # 添加第一个弱透水层
    >>> system.add_aquitard_layer(
    ...     top_elevation=80.0,
    ...     bottom_elevation=75.0,
    ...     K_vertical=0.01
    ... )
    >>> 
    >>> # 添加第二层含水层
    >>> system.add_aquifer_layer(...)
    >>> 
    >>> # 计算越流
    >>> heads = [np.array(...), np.array(...), np.array(...)]
    >>> leakage = system.compute_leakage(heads)
    """
    
    def __init__(self, name: str = 'MultiLayerSystem'):
        self.name = name
        self.aquifer_layers: List[AquiferLayer] = []
        self.aquitard_layers: List[AquitardLayer] = []
    
    @property
    def n_layers(self) -> int:
        """含水层数量"""
        return len(self.aquifer_layers)
    
    @property
    def n_aquitards(self) -> int:
        """弱透水层数量"""
        return len(self.aquitard_layers)
    
    def add_aquifer_layer(
        self,
        layer_id: int,
        top_elevation: float,
        bottom_elevation: float,
        K_horizontal: float,
        storage: float,
        is_confined: bool = True
    ) -> None:
        """
        添加含水层
        
        Parameters
        ----------
        layer_id : int
            层编号
        top_elevation : float
            顶板高程 (m)
        bottom_elevation : float
            底板高程 (m)
        K_horizontal : float
            水平渗透系数 (m/day)
        storage : float
            储水系数
        is_confined : bool
            是否承压
        """
        layer = AquiferLayer(
            layer_id=layer_id,
            top_elevation=top_elevation,
            bottom_elevation=bottom_elevation,
            K_horizontal=K_horizontal,
            storage=storage,
            is_confined=is_confined
        )
        self.aquifer_layers.append(layer)
        self.aquifer_layers.sort(key=lambda x: x.layer_id)
    
    def add_aquitard_layer(
        self,
        top_elevation: float,
        bottom_elevation: float,
        K_vertical: float,
        storage: Optional[float] = None
    ) -> None:
        """
        添加弱透水层
        
        Parameters
        ----------
        top_elevation : float
            顶板高程 (m)
        bottom_elevation : float
            底板高程 (m)
        K_vertical : float
            垂向渗透系数 (m/day)
        storage : float, optional
            储水系数
        """
        aquitard = AquitardLayer(
            top_elevation=top_elevation,
            bottom_elevation=bottom_elevation,
            K_vertical=K_vertical,
            storage=storage
        )
        self.aquitard_layers.append(aquitard)
    
    def compute_leakage(
        self,
        heads: List[np.ndarray],
        cell_area: float
    ) -> List[np.ndarray]:
        """
        计算各层的越流通量
        
        Parameters
        ----------
        heads : list of array
            各层水头，heads[i] 是第 i 层的水头数组
        cell_area : float
            单元面积 (m²)
        
        Returns
        -------
        leakage_fluxes : list of array
            各层的越流通量 (m³/day)
            leakage_fluxes[i] 是第 i 层的净越流
            正值：向下流动（流出该层）
            负值：向上流动（流入该层）
        
        Notes
        -----
        对于第 i 层：
        - 来自上层的越流：Q_from_above = C_i-1 * (h[i-1] - h[i])
        - 向下层的越流：Q_to_below = C_i * (h[i] - h[i+1])
        - 净越流：Q_net[i] = Q_to_below - Q_from_above
        
        边界层：
        - 第0层（最上层）：只有向下越流
        - 第n-1层（最下层）：只有来自上层的越流
        """
        n_layers = len(heads)
        if n_layers != self.n_layers:
            raise ValueError(
                f"Number of head arrays ({n_layers}) must match "
                f"number of aquifer layers ({self.n_layers})"
            )
        
        # 检查弱透水层数量
        expected_aquitards = n_layers - 1
        if self.n_aquitards != expected_aquitards:
            raise ValueError(
                f"Expected {expected_aquitards} aquitards for {n_layers} layers, "
                f"got {self.n_aquitards}"
            )
        
        leakage_fluxes = []
        
        for i in range(n_layers):
            shape = heads[i].shape
            net_leakage = np.zeros(shape)
            
            # 来自上层的越流（流入）
            if i > 0:
                aquitard = self.aquitard_layers[i-1]
                conductance = aquitard.K_vertical * cell_area / aquitard.thickness
                Q_from_above = conductance * (heads[i-1] - heads[i])
                net_leakage -= Q_from_above  # 流入为负
            
            # 向下层的越流（流出）
            if i < n_layers - 1:
                aquitard = self.aquitard_layers[i]
                conductance = aquitard.K_vertical * cell_area / aquitard.thickness
                Q_to_below = conductance * (heads[i] - heads[i+1])
                net_leakage += Q_to_below  # 流出为正
            
            leakage_fluxes.append(net_leakage)
        
        return leakage_fluxes
    
    def compute_leakage_as_source(
        self,
        heads: List[np.ndarray],
        cell_volumes: List[np.ndarray]
    ) -> List[np.ndarray]:
        """
        将越流转换为源汇项
        
        Parameters
        ----------
        heads : list of array
            各层水头
        cell_volumes : list of array
            各层单元体积 (m³)
        
        Returns
        -------
        source_terms : list of array
            各层源汇项 (1/day)
            source[i] = -Q_net[i] / V[i]
            负号：因为流出为正通量，但对该层是消耗（负源）
        """
        # 计算通量
        cell_area = cell_volumes[0].flatten()[0] / self.aquifer_layers[0].thickness
        leakage_fluxes = self.compute_leakage(heads, cell_area)
        
        source_terms = []
        for i in range(len(heads)):
            source = -leakage_fluxes[i] / cell_volumes[i]
            source_terms.append(source)
        
        return source_terms
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取系统摘要信息
        
        Returns
        -------
        summary : dict
            系统信息
        """
        aquifer_info = []
        for layer in self.aquifer_layers:
            aquifer_info.append({
                'layer_id': layer.layer_id,
                'thickness': layer.thickness,
                'K': layer.K_horizontal,
                'T': layer.transmissivity,
                'type': 'Confined' if layer.is_confined else 'Unconfined'
            })
        
        aquitard_info = []
        for i, aquitard in enumerate(self.aquitard_layers):
            aquitard_info.append({
                'position': f'Between Layer {i} and {i+1}',
                'thickness': aquitard.thickness,
                'K_vertical': aquitard.K_vertical,
                'leakance': aquitard.leakance
            })
        
        return {
            'name': self.name,
            'n_layers': self.n_layers,
            'n_aquitards': self.n_aquitards,
            'aquifer_layers': aquifer_info,
            'aquitard_layers': aquitard_info
        }
    
    def __repr__(self) -> str:
        return (
            f"MultiLayerSystem(name='{self.name}', "
            f"n_layers={self.n_layers}, "
            f"n_aquitards={self.n_aquitards})"
        )


def compute_steady_leakage_1d(
    h_upper: float,
    h_lower: float,
    K_aquitard: float,
    b_aquitard: float,
    area: float
) -> float:
    """
    计算稳态越流通量（单个位置）
    
    Parameters
    ----------
    h_upper : float
        上层含水层水头 (m)
    h_lower : float
        下层含水层水头 (m)
    K_aquitard : float
        弱透水层垂向渗透系数 (m/day)
    b_aquitard : float
        弱透水层厚度 (m)
    area : float
        交换面积 (m²)
    
    Returns
    -------
    Q : float
        越流通量 (m³/day)
        正值：向下流动
        负值：向上流动
    
    Examples
    --------
    >>> Q = compute_steady_leakage_1d(
    ...     h_upper=50.0,
    ...     h_lower=45.0,
    ...     K_aquitard=0.01,
    ...     b_aquitard=10.0,
    ...     area=1000.0
    ... )
    >>> print(f"Leakage: {Q:.2f} m³/day")
    """
    if K_aquitard <= 0:
        raise ValueError("K_aquitard must be positive")
    if b_aquitard <= 0:
        raise ValueError("b_aquitard must be positive")
    if area <= 0:
        raise ValueError("area must be positive")
    
    # 计算传导度
    conductance = K_aquitard * area / b_aquitard
    
    # 计算越流
    Q = conductance * (h_upper - h_lower)
    
    return Q


def hantush_jacob_solution(
    r: np.ndarray,
    t: float,
    Q_well: float,
    T: float,
    S: float,
    leakance: float
) -> np.ndarray:
    """
    Hantush-Jacob解：考虑越流的承压含水层抽水解析解
    
    这是经典的Theis解的扩展，考虑了来自相邻含水层的越流补给。
    
    Parameters
    ----------
    r : array
        径向距离 (m)
    t : float
        时间 (day)
    Q_well : float
        抽水井流量 (m³/day)
    T : float
        导水系数 (m²/day)
    S : float
        储水系数
    leakance : float
        渗漏系数 (1/day), L = K_aquitard / b_aquitard
    
    Returns
    -------
    s : array
        水位降深 (m)
    
    Notes
    -----
    Hantush-Jacob公式：
    s = (Q / 4πT) * W(u, r/B)
    
    其中：
    - u = r²S / (4Tt)
    - B = sqrt(T / L)  渗漏因子 (m)
    - W(u, r/B) 是Hantush井函数
    
    当 L → 0 时，退化为Theis解（无越流）
    
    References
    ----------
    Hantush & Jacob (1955). Non-steady radial flow in an infinite 
    leaky aquifer. Transactions, American Geophysical Union, 36(1), 95-100.
    """
    from scipy.special import exp1  # 指数积分函数
    
    # 参数验证
    if np.any(r <= 0):
        raise ValueError("r must be positive")
    if t <= 0:
        raise ValueError("t must be positive")
    if T <= 0:
        raise ValueError("T must be positive")
    if S <= 0:
        raise ValueError("S must be positive")
    if leakance < 0:
        raise ValueError("leakance must be non-negative")
    
    # 计算参数
    u = r**2 * S / (4 * T * t)
    
    if leakance == 0:
        # 无越流，使用Theis解
        W = exp1(u)
    else:
        # 有越流，使用Hantush-Jacob解
        B = np.sqrt(T / leakance)  # 渗漏因子
        beta = r / B
        
        # Hantush井函数的近似（对于小u和适中的beta）
        # 完整实现需要数值积分，这里使用简化公式
        W = exp1(u) * np.exp(-beta)  # 简化近似
    
    # 计算降深
    s = Q_well / (4 * np.pi * T) * W
    
    return s


def estimate_leakage_factor(
    T: float,
    leakance: float
) -> float:
    """
    估算渗漏因子（Leakage Factor）
    
    渗漏因子 B 表示越流影响的特征距离。
    
    Parameters
    ----------
    T : float
        导水系数 (m²/day)
    leakance : float
        渗漏系数 (1/day)
    
    Returns
    -------
    B : float
        渗漏因子 (m)
    
    Notes
    -----
    B = sqrt(T / L)
    
    物理意义：
    - B 大：越流弱，影响范围广
    - B 小：越流强，影响范围窄
    
    典型值：
    - 弱越流：B > 1000m
    - 中等越流：100m < B < 1000m
    - 强越流：B < 100m
    
    Examples
    --------
    >>> B = estimate_leakage_factor(T=1000.0, leakance=0.001)
    >>> print(f"Leakage factor: {B:.1f} m")
    Leakage factor: 1000.0 m
    """
    if T <= 0:
        raise ValueError("T must be positive")
    if leakance < 0:
        raise ValueError("leakance must be non-negative")
    
    if leakance == 0:
        return np.inf  # 无越流
    
    B = np.sqrt(T / leakance)
    return B
