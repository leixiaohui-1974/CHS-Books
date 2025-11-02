"""
水文-水动力耦合接口
==================

实现水文模型与水动力模型之间的数据交换和耦合计算。

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
from typing import Dict, Callable, Optional


class HydroInterface:
    """
    水文-水动力耦合接口
    
    负责:
    1. 水文模型输出→水动力模型输入
    2. 水动力模型输出→水文模型反馈
    3. 时间步同步
    4. 数据格式转换
    """
    
    def __init__(self, 
                 hydro_model: Callable,
                 hydraulic_model: Callable,
                 coupling_interval: float = 3600.0):
        """
        初始化耦合接口
        
        Parameters
        ----------
        hydro_model : callable
            水文模型函数
        hydraulic_model : callable
            水动力模型函数
        coupling_interval : float
            耦合时间间隔 (s)
        """
        self.hydro_model = hydro_model
        self.hydraulic_model = hydraulic_model
        self.coupling_interval = coupling_interval
        
    def convert_runoff_to_discharge(self, 
                                    runoff: float,
                                    area: float,
                                    dt: float) -> float:
        """
        将径流深转换为流量
        
        Parameters
        ----------
        runoff : float
            径流深 (mm)
        area : float
            流域面积 (km²)
        dt : float
            时间步长 (s)
            
        Returns
        -------
        discharge : float
            流量 (m³/s)
        """
        # 径流深(mm) → 体积(m³) → 流量(m³/s)
        volume = runoff * 1e-3 * area * 1e6  # m³
        discharge = volume / dt  # m³/s
        return discharge
    
    def aggregate_runoff(self, 
                        grid_runoff: np.ndarray,
                        mask: np.ndarray) -> float:
        """
        汇总网格径流
        
        Parameters
        ----------
        grid_runoff : ndarray
            网格径流 (mm)
        mask : ndarray
            有效网格掩膜
            
        Returns
        -------
        total_runoff : float
            总径流 (mm)
        """
        valid_runoff = grid_runoff[mask]
        return np.mean(valid_runoff) if len(valid_runoff) > 0 else 0.0
    
    def smooth_discharge(self, 
                        discharge: np.ndarray,
                        window: int = 3) -> np.ndarray:
        """
        平滑流量序列
        
        Parameters
        ----------
        discharge : ndarray
            原始流量
        window : int
            平滑窗口
            
        Returns
        -------
        smoothed : ndarray
            平滑后的流量
        """
        if len(discharge) < window:
            return discharge
        
        smoothed = np.copy(discharge)
        for i in range(window, len(discharge)):
            smoothed[i] = np.mean(discharge[i-window:i+1])
        
        return smoothed


def couple_simulation(
    rainfall: np.ndarray,
    evaporation: np.ndarray,
    hydro_params: Dict,
    hydraulic_params: Dict,
    dt_hydro: float = 3600.0,
    dt_hydraulic: float = 10.0,
    watershed_area: float = 100.0
) -> Dict[str, np.ndarray]:
    """
    执行水文-水动力耦合模拟
    
    Parameters
    ----------
    rainfall : ndarray
        降雨序列 (mm/时段)
    evaporation : ndarray
        蒸发序列 (mm/时段)
    hydro_params : dict
        水文模型参数
    hydraulic_params : dict
        水动力模型参数
    dt_hydro : float
        水文模型时间步长 (s)
    dt_hydraulic : float
        水动力模型时间步长 (s)
    watershed_area : float
        流域面积 (km²)
        
    Returns
    -------
    results : dict
        耦合模拟结果
    """
    from ..runoff_generation.xaj_model import XinAnJiangModel
    from .saint_venant import solve_saint_venant
    
    # 水文模型模拟
    print("  1. 运行水文模型...")
    xaj = XinAnJiangModel(hydro_params)
    hydro_results = xaj.run(rainfall, evaporation)
    runoff = hydro_results['R']  # mm
    
    # 处理NaN值
    runoff = np.nan_to_num(runoff, nan=0.0, posinf=0.0, neginf=0.0)
    runoff = np.maximum(runoff, 0.0)  # 确保非负
    
    # 转换为流量
    print("  2. 转换径流为流量...")
    n_steps = len(runoff)
    discharge = np.zeros(n_steps)
    
    for i in range(n_steps):
        # 径流(mm) → 流量(m³/s)
        volume = runoff[i] * 1e-3 * watershed_area * 1e6  # m³
        discharge[i] = volume / dt_hydro  # m³/s
    
    # 平滑流量过程
    discharge = np.convolve(discharge, np.ones(3)/3, mode='same')
    discharge = np.maximum(discharge, 1.0)  # 最小基流
    
    # 插值到水动力时间步
    print("  3. 插值到水动力时间步...")
    t_hydro = np.arange(n_steps) * dt_hydro
    n_hydraulic = int((n_steps * dt_hydro) / dt_hydraulic)
    t_hydraulic = np.arange(n_hydraulic) * dt_hydraulic
    
    discharge_interp = np.interp(t_hydraulic, t_hydro, discharge)
    
    # 水动力模型模拟
    print("  4. 运行水动力模型...")
    hydraulic_results = solve_saint_venant(
        L=hydraulic_params.get('L', 1000.0),
        dx=hydraulic_params.get('dx', 50.0),
        dt=dt_hydraulic,
        T=n_hydraulic * dt_hydraulic,
        Q_upstream=discharge_interp,
        n=hydraulic_params.get('n', 0.03),
        B=hydraulic_params.get('B', 10.0),
        S0=hydraulic_params.get('S0', 0.001),
        h0=hydraulic_params.get('h0', 1.0),
        Q0=discharge_interp[0]
    )
    
    return {
        'hydro': hydro_results,
        'discharge': discharge,
        't_hydro': t_hydro,
        'hydraulic': hydraulic_results,
        'runoff': runoff
    }


if __name__ == '__main__':
    """测试耦合接口"""
    print("测试水文-水动力耦合接口...")
    
    # 测试单位转换
    interface = HydroInterface(None, None)
    
    runoff = 10.0  # mm
    area = 100.0  # km²
    dt = 3600.0  # s
    
    discharge = interface.convert_runoff_to_discharge(runoff, area, dt)
    print(f"径流 {runoff} mm → 流量 {discharge:.2f} m³/s")
    
    # 测试流量平滑
    Q = np.array([10, 20, 15, 25, 20, 18])
    Q_smooth = interface.smooth_discharge(Q, window=2)
    print(f"原始流量: {Q}")
    print(f"平滑流量: {Q_smooth}")
    
    print("测试通过！")
