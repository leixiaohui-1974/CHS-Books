"""
gwflow.coupling.exchange - 地表地下水交换通量计算

本模块提供地表水和地下水之间水量交换的计算方法。

核心概念：
---------
1. 渗漏机制：
   地表水和地下水通过弱透水层（如河床、湖底）进行水量交换。
   交换通量正比于两侧水头差。

2. 水力传导度（Conductance）：
   C = K * A / b
   其中：
   - K: 弱透水层渗透系数 (m/day)
   - A: 交换面积 (m²)
   - b: 弱透水层厚度 (m)

3. 渗漏系数（Leakance）：
   L = K / b (1/day)
   
   与传导度的关系：
   C = L * A

4. 交换通量：
   Q = C * (h_sw - h_gw)
   
   正值表示地表水补给地下水
   负值表示地下水排泄到地表水

参考文献：
---------
1. McDonald & Harbaugh (1988). MODFLOW User Manual, Chapter 6
2. Prudic (1989). Documentation of a computer program to simulate 
   stream-aquifer relations
3. Sophocleous (2002). Interactions between groundwater and surface water: 
   the state of the science. Hydrogeology Journal, 10(1), 52-67

作者: gwflow开发团队
日期: 2025-11-02
"""

import numpy as np
from typing import Union, Optional


def compute_exchange_flux(
    h_gw: Union[float, np.ndarray],
    h_sw: Union[float, np.ndarray],
    conductance: float,
    bed_bottom: Optional[Union[float, np.ndarray]] = None,
    method: str = 'standard'
) -> Union[float, np.ndarray]:
    """
    计算地表水-地下水交换通量
    
    基本公式：
        Q = C * (h_sw - h_gw)
    
    当考虑河床底部时（断开机制）：
        if h_gw > bed_bottom:
            Q = C * (h_sw - h_gw)
        else:
            Q = C * (h_sw - bed_bottom)
    
    Parameters
    ----------
    h_gw : float or array
        地下水水头 (m)
    h_sw : float or array
        地表水水头/水位 (m)
    conductance : float
        水力传导度 (m²/day)
    bed_bottom : float or array, optional
        河床/湖底高程 (m)
        如果提供，将使用断开机制
    method : str, default='standard'
        计算方法：
        - 'standard': 标准方法，Q = C * (h_sw - h_gw)
        - 'disconnected': 断开机制，考虑bed_bottom
    
    Returns
    -------
    Q : float or array
        交换通量 (m³/day)
        正值：地表水补给地下水
        负值：地下水排泄到地表水
    
    Examples
    --------
    >>> # 标准计算
    >>> Q = compute_exchange_flux(h_gw=25.0, h_sw=30.0, conductance=1000.0)
    >>> print(f"交换通量: {Q:.2f} m³/day")
    交换通量: 5000.00 m³/day
    
    >>> # 考虑断开机制
    >>> Q = compute_exchange_flux(
    ...     h_gw=18.0, h_sw=30.0, conductance=1000.0,
    ...     bed_bottom=20.0, method='disconnected'
    ... )
    >>> print(f"交换通量: {Q:.2f} m³/day")
    交换通量: 10000.00 m³/day
    
    Notes
    -----
    1. 断开机制（Disconnection）：
       当地下水位降到河床底部以下时，河流不能继续向下补给。
       此时通量被限制为：Q = C * (h_sw - bed_bottom)
    
    2. 物理意义：
       - 正通量：地表水位高于地下水位，地表水补给地下水
       - 负通量：地下水位高于地表水位，地下水排泄到地表水
       - 零通量：水位相等，无交换
    
    3. 单位转换：
       如果需要转换为源汇项 (1/day)，除以单元体积：
       q = Q / (dx * dy * b)
    """
    if method == 'standard':
        # 标准计算
        Q = conductance * (h_sw - h_gw)
    
    elif method == 'disconnected':
        # 断开机制
        if bed_bottom is None:
            raise ValueError("method='disconnected' requires bed_bottom parameter")
        
        # 确保数组兼容性
        h_gw = np.asarray(h_gw)
        h_sw = np.asarray(h_sw)
        bed_bottom = np.asarray(bed_bottom)
        
        # 计算有效地下水水头
        h_gw_effective = np.maximum(h_gw, bed_bottom)
        
        # 计算交换通量
        Q = conductance * (h_sw - h_gw_effective)
    
    else:
        raise ValueError(f"Unknown method: {method}. Use 'standard' or 'disconnected'")
    
    return Q


def leakance_coefficient(
    K_bed: float,
    b_bed: float
) -> float:
    """
    计算渗漏系数（Leakance Coefficient）
    
    公式：
        L = K_bed / b_bed
    
    Parameters
    ----------
    K_bed : float
        河床/湖底渗透系数 (m/day)
    b_bed : float
        河床/湖底厚度 (m)
    
    Returns
    -------
    L : float
        渗漏系数 (1/day)
    
    Examples
    --------
    >>> L = leakance_coefficient(K_bed=1.0, b_bed=2.0)
    >>> print(f"渗漏系数: {L:.3f} 1/day")
    渗漏系数: 0.500 1/day
    
    Notes
    -----
    渗漏系数表示单位水头差下的渗透能力。
    较大的L值表示较强的水力连接。
    """
    if K_bed <= 0:
        raise ValueError(f"K_bed must be positive, got {K_bed}")
    if b_bed <= 0:
        raise ValueError(f"b_bed must be positive, got {b_bed}")
    
    return K_bed / b_bed


def conductance_from_geometry(
    K_bed: float,
    b_bed: float,
    length: float,
    width: float
) -> float:
    """
    根据几何参数计算水力传导度
    
    公式：
        C = K_bed * L * W / b_bed
    
    其中：
    - L: 河段长度或湖泊长度 (m)
    - W: 河宽或湖泊宽度 (m)
    - A = L * W: 交换面积 (m²)
    
    Parameters
    ----------
    K_bed : float
        河床/湖底渗透系数 (m/day)
    b_bed : float
        河床/湖底厚度 (m)
    length : float
        长度 (m)
    width : float
        宽度 (m)
    
    Returns
    -------
    C : float
        水力传导度 (m²/day)
    
    Examples
    --------
    >>> C = conductance_from_geometry(
    ...     K_bed=1.0, b_bed=2.0, length=100.0, width=50.0
    ... )
    >>> print(f"传导度: {C:.2e} m²/day")
    传导度: 2.50e+03 m²/day
    
    Notes
    -----
    水力传导度是MODFLOW中River包的核心参数。
    单位为 m²/day，表示单位水头差下的体积流量。
    """
    if K_bed <= 0:
        raise ValueError(f"K_bed must be positive, got {K_bed}")
    if b_bed <= 0:
        raise ValueError(f"b_bed must be positive, got {b_bed}")
    if length <= 0:
        raise ValueError(f"length must be positive, got {length}")
    if width <= 0:
        raise ValueError(f"width must be positive, got {width}")
    
    area = length * width
    C = K_bed * area / b_bed
    
    return C


def river_head_gradient(
    river_stage: float,
    river_bottom: float,
    gw_head: float,
    method: str = 'standard'
) -> float:
    """
    计算河流-地下水有效水头梯度
    
    Parameters
    ----------
    river_stage : float
        河流水位 (m)
    river_bottom : float
        河底高程 (m)
    gw_head : float
        地下水水头 (m)
    method : str, default='standard'
        计算方法：
        - 'standard': 标准方法，Δh = river_stage - gw_head
        - 'clamped': 限制在河底以上
        - 'disconnected': 完全断开机制
    
    Returns
    -------
    gradient : float
        有效水头梯度 (m)
    
    Examples
    --------
    >>> # 标准方法
    >>> grad = river_head_gradient(30.0, 20.0, 25.0, method='standard')
    >>> print(f"水头梯度: {grad:.2f} m")
    水头梯度: 5.00 m
    
    >>> # 断开机制
    >>> grad = river_head_gradient(30.0, 20.0, 18.0, method='disconnected')
    >>> print(f"水头梯度: {grad:.2f} m")
    水头梯度: 10.00 m
    
    Notes
    -----
    1. standard方法：
       简单的水头差，不考虑河底
    
    2. clamped方法：
       确保地下水水头不低于河底
       
    3. disconnected方法：
       当地下水位低于河底时，使用河底作为地下水水头
    """
    if method == 'standard':
        return river_stage - gw_head
    
    elif method == 'clamped':
        # 限制地下水水头在河底以上
        effective_gw_head = max(gw_head, river_bottom)
        return river_stage - effective_gw_head
    
    elif method == 'disconnected':
        # 完全断开机制
        if gw_head < river_bottom:
            # 地下水低于河底，河流与地下水断开
            return river_stage - river_bottom
        else:
            # 正常连接
            return river_stage - gw_head
    
    else:
        raise ValueError(
            f"Unknown method: {method}. "
            f"Use 'standard', 'clamped', or 'disconnected'"
        )


def compute_leakage_vertical(
    h_upper: Union[float, np.ndarray],
    h_lower: Union[float, np.ndarray],
    K_aquitard: float,
    b_aquitard: float,
    area: float
) -> Union[float, np.ndarray]:
    """
    计算垂向越流通量（用于多层含水层系统）
    
    公式：
        Q = C_leakage * (h_upper - h_lower)
        C_leakage = K_aquitard * A / b_aquitard
    
    Parameters
    ----------
    h_upper : float or array
        上层含水层水头 (m)
    h_lower : float or array
        下层含水层水头 (m)
    K_aquitard : float
        弱透水层渗透系数 (m/day)
    b_aquitard : float
        弱透水层厚度 (m)
    area : float
        交换面积 (m²)
    
    Returns
    -------
    Q : float or array
        越流通量 (m³/day)
        正值：上层向下层流动
        负值：下层向上层流动
    
    Examples
    --------
    >>> Q = compute_leakage_vertical(
    ...     h_upper=50.0, h_lower=45.0,
    ...     K_aquitard=0.01, b_aquitard=10.0,
    ...     area=1000.0
    ... )
    >>> print(f"越流通量: {Q:.2f} m³/day")
    越流通量: 5.00 m³/day
    
    Notes
    -----
    越流（Leakage）是多层含水层系统中的重要过程。
    通常用于模拟承压含水层之间通过弱透水层的水量交换。
    """
    if K_aquitard <= 0:
        raise ValueError(f"K_aquitard must be positive, got {K_aquitard}")
    if b_aquitard <= 0:
        raise ValueError(f"b_aquitard must be positive, got {b_aquitard}")
    if area <= 0:
        raise ValueError(f"area must be positive, got {area}")
    
    # 计算越流传导度
    C_leakage = K_aquitard * area / b_aquitard
    
    # 计算越流通量
    Q = C_leakage * (h_upper - h_lower)
    
    return Q
