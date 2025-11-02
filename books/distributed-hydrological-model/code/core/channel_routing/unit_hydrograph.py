"""
单元线法河道汇流
==============

单元线（Unit Hydrograph, UH）是指单位时段内单位净雨在流域出口产生的地表径流过程线。

理论基础
--------
1. 线性叠加原理：
   Q(t) = Σ[R(i) × UH(t-i)]
   
2. 时段不变性：
   相同时段的单位净雨产生的UH相同
   
3. 比例性：
   净雨深度加倍，UH纵坐标加倍

常用单元线：
----------
1. Snyder综合单元线
2. SCS无量纲单元线
3. 瞬时单元线（IUH）

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
from typing import Dict, Optional, Tuple


class UnitHydrograph:
    """
    单元线法河道汇流模型
    
    Parameters
    ----------
    unit_hydrograph : ndarray
        单元线序列 (m³/s/mm)，长度为n
    dt : float
        时间步长 (h)
    
    Attributes
    ----------
    uh : ndarray
        单元线
    dt : float
        时间步长
    n : int
        单元线长度
    
    Examples
    --------
    >>> # 创建三角形单元线
    >>> uh = np.array([0, 0.5, 1.0, 0.5, 0])
    >>> model = UnitHydrograph(uh, dt=1.0)
    >>> runoff = np.array([10, 20, 15, 5])  # mm
    >>> results = model.run(runoff)
    """
    
    def __init__(self, unit_hydrograph: np.ndarray, dt: float):
        """初始化单元线模型"""
        self.uh = np.array(unit_hydrograph)
        self.dt = dt
        self.n = len(self.uh)
        
        # 验证
        if self.n == 0:
            raise ValueError("单元线不能为空")
        if self.dt <= 0:
            raise ValueError("时间步长必须为正")
        if np.any(self.uh < 0):
            raise ValueError("单元线值不能为负")
    
    def run(self, runoff: np.ndarray) -> Dict[str, np.ndarray]:
        """
        运行单元线模型
        
        Parameters
        ----------
        runoff : ndarray
            净雨深度序列 (mm)
        
        Returns
        -------
        results : dict
            包含：
            - discharge : ndarray, 流量过程 (m³/s)
        """
        m = len(runoff)
        
        # 输出流量长度
        n_out = m + self.n - 1
        discharge = np.zeros(n_out)
        
        # 卷积计算
        for i in range(m):
            if runoff[i] > 0:
                for j in range(self.n):
                    if i + j < n_out:
                        discharge[i + j] += runoff[i] * self.uh[j]
        
        return {
            'discharge': discharge,
            'time': np.arange(n_out) * self.dt
        }
    
    def validate(self) -> Dict[str, float]:
        """
        验证单元线有效性
        
        Returns
        -------
        validation : dict
            包含验证指标
        """
        # 计算单元线体积（应该等于1 mm）
        volume = np.sum(self.uh) * self.dt * 3600  # m³/s * h * 3600s/h = m³
        # 对于单位面积（1 km² = 1e6 m²），1mm = 1000 m³
        
        # 峰值流量
        peak_uh = np.max(self.uh)
        peak_time = np.argmax(self.uh) * self.dt
        
        # 基流时间
        base_time = self.n * self.dt
        
        return {
            'volume': volume,
            'peak_uh': peak_uh,
            'peak_time': peak_time,
            'base_time': base_time,
            'dt': self.dt
        }


def create_snyder_uh(basin_area: float, main_channel_length: float,
                    centroid_to_outlet: float, ct: float = 2.0,
                    cp: float = 0.6, dt: float = 1.0) -> Tuple[np.ndarray, float]:
    """
    创建Snyder综合单元线
    
    Snyder单元线是基于流域特征综合的单元线，适用于无实测资料的流域。
    
    Parameters
    ----------
    basin_area : float
        流域面积 (km²)
    main_channel_length : float
        主河道长度 (km)
    centroid_to_outlet : float
        流域重心到出口的距离 (km)
    ct : float
        地区综合参数，一般在1.8-2.2
    cp : float
        峰值流量系数，一般在0.4-0.8
    dt : float
        时间步长 (h)
    
    Returns
    -------
    uh : ndarray
        单元线 (m³/s/mm)
    tp : float
        峰现时间 (h)
    
    References
    ----------
    Snyder, F.F. (1938). Synthetic unit-graphs. Transactions, 
    American Geophysical Union, 19, 447-454.
    """
    # 计算滞时
    tp = ct * (main_channel_length * centroid_to_outlet) ** 0.3
    
    # 峰值流量 (m³/s/mm/km²)
    qp = cp * basin_area / tp
    
    # 基流时间
    tb = 3 + tp / 8
    
    # 生成时间序列
    n_steps = int(tb / dt) + 5
    time = np.arange(n_steps) * dt
    
    # Snyder单元线形状（简化的三角形-指数衰减）
    uh = np.zeros(n_steps)
    
    for i, t in enumerate(time):
        if t <= tp:
            # 上升段（抛物线）
            uh[i] = qp * (t / tp) ** 1.5
        else:
            # 下降段（指数衰减）
            uh[i] = qp * np.exp(-2.3 * (t - tp) / tp)
    
    # 归一化（确保体积为1mm）
    volume = np.sum(uh) * dt * 3600 / (basin_area * 1e6)  # mm
    uh = uh / volume
    
    return uh, tp


def create_scs_uh(basin_area: float, tc: float, dt: float = 1.0) -> np.ndarray:
    """
    创建SCS无量纲单元线
    
    SCS（Soil Conservation Service）单元线是美国水土保持局开发的
    标准化单元线，形状固定，只需流域面积和汇流时间。
    
    Parameters
    ----------
    basin_area : float
        流域面积 (km²)
    tc : float
        汇流时间 (h)
    dt : float
        时间步长 (h)
    
    Returns
    -------
    uh : ndarray
        单元线 (m³/s/mm)
    
    Notes
    -----
    SCS无量纲单元线的峰值流量为：
    Qp = 0.208 * A / Tp
    其中 Tp = 0.6 * Tc
    
    References
    ----------
    USDA-SCS (1972). National Engineering Handbook, Section 4: Hydrology.
    """
    # 峰现时间
    tp = 0.6 * tc
    
    # 峰值流量 (m³/s/mm/km²)
    qp = 0.208 * basin_area / tp
    
    # 基流时间
    tb = 2.67 * tp
    
    # 生成时间序列
    n_steps = int(tb / dt) + 5
    time = np.arange(n_steps) * dt
    
    # SCS无量纲单元线（标准形状）
    uh = np.zeros(n_steps)
    
    for i, t in enumerate(time):
        t_ratio = t / tp
        
        if t_ratio <= 1.0:
            # 上升段
            uh[i] = qp * t_ratio ** 2.5
        elif t_ratio <= 1.7:
            # 下降段1
            uh[i] = qp * np.exp(-1.5 * (t_ratio - 1))
        else:
            # 下降段2
            uh[i] = qp * np.exp(-3.0 * (t_ratio - 1.7) - 1.5 * 0.7)
    
    # 归一化
    volume = np.sum(uh) * dt * 3600 / (basin_area * 1e6)
    uh = uh / volume
    
    return uh


def create_triangular_uh(basin_area: float, tp: float, tb: float, 
                        dt: float = 1.0) -> np.ndarray:
    """
    创建三角形单元线
    
    最简单的单元线形状，用于教学演示。
    
    Parameters
    ----------
    basin_area : float
        流域面积 (km²)
    tp : float
        峰现时间 (h)
    tb : float
        基流时间 (h)
    dt : float
        时间步长 (h)
    
    Returns
    -------
    uh : ndarray
        单元线 (m³/s/mm)
    """
    # 峰值流量（根据三角形面积=1mm）
    # 0.5 * tb * qp = 1 mm * A (转换为m³/s)
    qp = 2.0 * basin_area * 1e6 / 1000 / (tb * 3600)  # m³/s/mm
    
    # 生成时间序列
    n_steps = int(tb / dt) + 2
    time = np.arange(n_steps) * dt
    
    uh = np.zeros(n_steps)
    
    for i, t in enumerate(time):
        if t <= tp:
            # 上升段
            uh[i] = qp * t / tp
        elif t <= tb:
            # 下降段
            uh[i] = qp * (tb - t) / (tb - tp)
        else:
            uh[i] = 0
    
    return uh


def convolve_with_losses(uh: np.ndarray, rainfall: np.ndarray, 
                        losses: np.ndarray, dt: float) -> np.ndarray:
    """
    考虑损失的单元线卷积
    
    Parameters
    ----------
    uh : ndarray
        单元线
    rainfall : ndarray
        降雨 (mm)
    losses : ndarray
        损失（入渗+蒸发等） (mm)
    dt : float
        时间步长 (h)
    
    Returns
    -------
    discharge : ndarray
        流量过程 (m³/s)
    """
    # 计算净雨
    runoff = np.maximum(rainfall - losses, 0)
    
    # 创建单元线模型
    model = UnitHydrograph(uh, dt)
    
    # 运行
    results = model.run(runoff)
    
    return results['discharge']


if __name__ == '__main__':
    # 简单测试
    print("单元线法测试")
    print("=" * 50)
    
    # 1. 三角形单元线
    print("\n1. 三角形单元线")
    basin_area = 100  # km²
    tp = 5  # h
    tb = 15  # h
    dt = 1.0  # h
    
    uh_tri = create_triangular_uh(basin_area, tp, tb, dt)
    model = UnitHydrograph(uh_tri, dt)
    
    print(f"   流域面积: {basin_area} km²")
    print(f"   峰现时间: {tp} h")
    print(f"   基流时间: {tb} h")
    
    # 验证
    validation = model.validate()
    print(f"\n   单元线验证:")
    print(f"     峰值: {validation['peak_uh']:.4f} m³/s/mm")
    print(f"     峰现时间: {validation['peak_time']:.1f} h")
    print(f"     基流时间: {validation['base_time']:.1f} h")
    
    # 2. 应用单元线
    print("\n2. 应用单元线")
    runoff = np.array([0, 10, 20, 15, 5, 0, 0])  # mm
    print(f"   净雨: {runoff}")
    
    results = model.run(runoff)
    print(f"   流量过程长度: {len(results['discharge'])}")
    print(f"   峰值流量: {np.max(results['discharge']):.2f} m³/s")
    print(f"   峰现时刻: {np.argmax(results['discharge'])} h")
    
    # 3. Snyder单元线
    print("\n3. Snyder单元线")
    L = 20  # km
    Lc = 10  # km
    uh_snyder, tp_snyder = create_snyder_uh(basin_area, L, Lc, dt=dt)
    print(f"   峰现时间: {tp_snyder:.2f} h")
    print(f"   峰值流量: {np.max(uh_snyder):.4f} m³/s/mm")
    
    # 4. SCS单元线
    print("\n4. SCS单元线")
    tc = 8  # h
    uh_scs = create_scs_uh(basin_area, tc, dt=dt)
    print(f"   汇流时间: {tc} h")
    print(f"   峰值流量: {np.max(uh_scs):.4f} m³/s/mm")
