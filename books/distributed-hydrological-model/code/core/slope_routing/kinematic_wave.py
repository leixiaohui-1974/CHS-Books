"""
运动波坡面汇流模型
================

运动波理论是描述浅水流动的简化模型，忽略惯性项和压力项。

理论基础
--------
1. 连续性方程：
   ∂h/∂t + ∂q/∂x = r(x,t)
   
2. 运动波简化：
   q = α × h^m
   
   其中：
   - h: 水深 (m)
   - q: 单宽流量 (m²/s)
   - r: 净雨强度 (m/s)
   - α, m: 参数（与曼宁公式相关）

3. Manning公式关系：
   α = (1/n) × S^0.5
   m = 5/3
   
   其中：
   - n: 曼宁糙率
   - S: 坡度

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
from typing import Dict, Tuple


class KinematicWaveSlope:
    """
    运动波坡面汇流模型
    
    Parameters
    ----------
    params : dict
        模型参数：
        - length : float, 坡面长度 (m)
        - width : float, 坡面宽度 (m)
        - slope : float, 坡度 (-)
        - manning_n : float, 曼宁糙率系数
        - dx : float, 空间步长 (m)
        - dt : float, 时间步长 (s)
    
    Examples
    --------
    >>> params = {
    ...     'length': 100,  # m
    ...     'width': 50,    # m
    ...     'slope': 0.01,  # 1%坡度
    ...     'manning_n': 0.15,
    ...     'dx': 5,        # m
    ...     'dt': 60        # s
    ... }
    >>> model = KinematicWaveSlope(params)
    >>> runoff = np.array([10, 20, 30, 20, 10])  # mm/h
    >>> results = model.run(runoff)
    """
    
    def __init__(self, params: Dict[str, float]):
        """初始化运动波模型"""
        # 验证必需参数
        required = ['length', 'width', 'slope', 'manning_n', 'dx', 'dt']
        for param in required:
            if param not in params:
                raise ValueError(f"缺少必需参数: {param}")
        
        # 几何参数
        self.L = params['length']      # 坡面长度 (m)
        self.W = params['width']       # 坡面宽度 (m)
        self.S = params['slope']       # 坡度 (-)
        self.n = params['manning_n']   # 曼宁糙率
        
        # 数值参数
        self.dx = params['dx']  # 空间步长 (m)
        self.dt = params['dt']  # 时间步长 (s)
        
        # 参数检查
        if self.L <= 0 or self.W <= 0:
            raise ValueError("坡面长度和宽度必须为正")
        if self.S <= 0:
            raise ValueError("坡度必须为正")
        if self.n <= 0:
            raise ValueError("曼宁糙率必须为正")
        if self.dx <= 0 or self.dx > self.L:
            raise ValueError("空间步长必须在(0, L]范围内")
        if self.dt <= 0:
            raise ValueError("时间步长必须为正")
        
        # 网格设置
        self.nx = int(self.L / self.dx) + 1  # 空间节点数
        self.x = np.linspace(0, self.L, self.nx)  # 空间坐标
        
        # 运动波参数
        self.alpha = (1 / self.n) * (self.S ** 0.5)  # α参数
        self.m = 5.0 / 3.0                           # m参数
        
        # 状态变量
        self.h = np.zeros(self.nx)  # 水深 (m)
        
        # Courant数检查
        self._check_courant_condition()
    
    def _check_courant_condition(self):
        """检查Courant条件"""
        # 估计最大流速（假设最大水深0.1m）
        h_max = 0.1  # m
        v_max = self.alpha * (h_max ** (self.m - 1))
        
        courant = v_max * self.dt / self.dx
        
        if courant > 1:
            import warnings
            warnings.warn(
                f"Courant数 = {courant:.2f} > 1，可能导致数值不稳定。"
                f"建议减小dt或增大dx。",
                UserWarning
            )
    
    def _flux(self, h: np.ndarray) -> np.ndarray:
        """
        计算单宽流量
        
        q = α × h^m
        """
        return self.alpha * np.power(np.maximum(h, 1e-10), self.m)
    
    def run(self, runoff: np.ndarray) -> Dict[str, np.ndarray]:
        """
        运行运动波模型
        
        Parameters
        ----------
        runoff : ndarray
            净雨强度序列 (mm/h)
        
        Returns
        -------
        results : dict
            包含：
            - outlet_discharge : ndarray, 出口流量 (m³/s)
            - water_depth : ndarray, 水深分布 (m)
        """
        n_steps = len(runoff)
        
        # 转换净雨强度单位: mm/h -> m/s
        r = runoff / 1000.0 / 3600.0  # m/s
        
        # 初始化结果
        outlet_discharge = np.zeros(n_steps)
        water_depth_series = []
        
        # 重置状态
        self.reset()
        
        # 时间步进
        for t in range(n_steps):
            # 更新水深（使用显式差分格式）
            h_new = self.h.copy()
            
            # 计算流量
            q = self._flux(self.h)
            
            # 更新内部节点
            for i in range(1, self.nx):
                # 上游流量
                q_in = q[i-1]
                # 下游流量
                q_out = q[i]
                # 侧向入流
                lateral_inflow = r[t]
                
                # 水深变化
                dh_dt = (q_in - q_out) / self.dx + lateral_inflow
                
                # 更新水深
                h_new[i] = self.h[i] + dh_dt * self.dt
                
                # 非负约束
                h_new[i] = max(h_new[i], 0)
            
            # 上边界（山顶）：只有侧向入流
            h_new[0] = self.h[0] + r[t] * self.dt
            h_new[0] = max(h_new[0], 0)
            
            # 更新状态
            self.h = h_new
            
            # 出口流量
            q_outlet = self._flux(self.h[-1])  # 单宽流量 (m²/s)
            Q_outlet = q_outlet * self.W       # 总流量 (m³/s)
            
            outlet_discharge[t] = Q_outlet
            water_depth_series.append(self.h.copy())
        
        return {
            'outlet_discharge': outlet_discharge,
            'water_depth': np.array(water_depth_series),
            'x': self.x
        }
    
    def reset(self):
        """重置模型状态"""
        self.h = np.zeros(self.nx)
    
    def get_state(self) -> Dict[str, np.ndarray]:
        """获取当前状态"""
        return {'h': self.h.copy()}
    
    def set_state(self, state: Dict[str, np.ndarray]):
        """设置模型状态"""
        if 'h' in state:
            self.h = state['h'].copy()


def estimate_time_of_concentration(length: float, slope: float, 
                                  manning_n: float) -> float:
    """
    估算坡面汇流时间
    
    使用运动波理论的近似公式：
    tc = (L × n / (S^0.5))^0.6 / (0.6)
    
    Parameters
    ----------
    length : float
        坡面长度 (m)
    slope : float
        坡度 (-)
    manning_n : float
        曼宁糙率
    
    Returns
    -------
    tc : float
        汇流时间 (s)
    """
    # 近似公式
    tc = ((length * manning_n) / (slope ** 0.5)) ** 0.6 / 0.6
    
    return tc


if __name__ == '__main__':
    # 简单测试
    print("运动波坡面汇流模型测试")
    print("=" * 50)
    
    params = {
        'length': 100,      # m
        'width': 50,        # m
        'slope': 0.01,      # 1%坡度
        'manning_n': 0.15,
        'dx': 10,           # m
        'dt': 60            # s
    }
    
    print(f"坡面参数:")
    print(f"  长度: {params['length']} m")
    print(f"  宽度: {params['width']} m")
    print(f"  坡度: {params['slope']*100:.1f}%")
    print(f"  糙率: {params['manning_n']}")
    print()
    
    # 估算汇流时间
    tc = estimate_time_of_concentration(
        params['length'], params['slope'], params['manning_n']
    )
    print(f"估算汇流时间: {tc/60:.1f} 分钟")
    print()
    
    model = KinematicWaveSlope(params)
    
    # 模拟净雨过程（矩形）
    duration_minutes = 30
    n_steps = duration_minutes
    runoff = np.zeros(n_steps)
    runoff[5:20] = 30  # mm/h，持续15分钟
    
    print(f"净雨过程: 30 mm/h，持续15分钟")
    print()
    
    results = model.run(runoff)
    
    print("模拟结果:")
    print(f"  峰值流量: {np.max(results['outlet_discharge']):.4f} m³/s")
    print(f"  峰现时间: {np.argmax(results['outlet_discharge'])} 分钟")
    print(f"  总出流量: {np.sum(results['outlet_discharge']) * params['dt']:.2f} m³")
    print(f"  总净雨量: {np.sum(runoff/60) * params['length'] * params['width'] / 1000:.2f} m³")
