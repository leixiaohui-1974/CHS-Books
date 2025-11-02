"""
线性水库坡面汇流模型
==================

线性水库模型是最简单的汇流模型，假设出流量与蓄水量成正比。

理论基础
--------
1. 水量平衡方程：
   dS/dt = I(t) - Q(t)
   
2. 线性储蓄关系：
   S(t) = K × Q(t)
   
3. 结合得到：
   K × dQ/dt + Q = I(t)
   
   其中：
   - S: 蓄水量 (m³)
   - Q: 出流量 (m³/s)
   - I: 入流量 (m³/s)
   - K: 调蓄系数 (s)

4. 解析解：
   Q(t+Δt) = C1 × I(t) + C2 × Q(t)
   
   其中：
   C1 = Δt / (K + 0.5×Δt)
   C2 = (K - 0.5×Δt) / (K + 0.5×Δt)

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
from typing import Dict


class LinearReservoirSlope:
    """
    线性水库坡面汇流模型
    
    Parameters
    ----------
    params : dict
        模型参数：
        - area : float, 坡面面积 (m²)
        - K : float, 调蓄系数 (s)
        - dt : float, 时间步长 (s)
    
    Examples
    --------
    >>> params = {
    ...     'area': 5000,   # m²
    ...     'K': 300,       # s
    ...     'dt': 60        # s
    ... }
    >>> model = LinearReservoirSlope(params)
    >>> runoff = np.array([10, 20, 30, 20, 10])  # mm/h
    >>> results = model.run(runoff)
    """
    
    def __init__(self, params: Dict[str, float]):
        """初始化线性水库模型"""
        # 验证必需参数
        required = ['area', 'K', 'dt']
        for param in required:
            if param not in params:
                raise ValueError(f"缺少必需参数: {param}")
        
        # 参数
        self.area = params['area']  # 坡面面积 (m²)
        self.K = params['K']        # 调蓄系数 (s)
        self.dt = params['dt']      # 时间步长 (s)
        
        # 参数检查
        if self.area <= 0:
            raise ValueError("坡面面积必须为正")
        if self.K <= 0:
            raise ValueError("调蓄系数必须为正")
        if self.dt <= 0:
            raise ValueError("时间步长必须为正")
        
        # 计算汇流系数
        self.C1 = self.dt / (self.K + 0.5 * self.dt)
        self.C2 = (self.K - 0.5 * self.dt) / (self.K + 0.5 * self.dt)
        
        # 状态变量
        self.Q = 0.0  # 出流量 (m³/s)
        self.S = 0.0  # 蓄水量 (m³)
    
    def run(self, runoff: np.ndarray) -> Dict[str, np.ndarray]:
        """
        运行线性水库模型
        
        Parameters
        ----------
        runoff : ndarray
            净雨强度序列 (mm/h)
        
        Returns
        -------
        results : dict
            包含：
            - discharge : ndarray, 出流量 (m³/s)
            - storage : ndarray, 蓄水量 (m³)
        """
        n_steps = len(runoff)
        
        # 转换净雨强度: mm/h -> m³/s
        inflow = runoff / 1000.0 / 3600.0 * self.area
        
        # 初始化结果
        discharge = np.zeros(n_steps)
        storage = np.zeros(n_steps)
        
        # 重置状态
        self.reset()
        
        # 时间步进
        for t in range(n_steps):
            # 计算出流量
            self.Q = self.C1 * inflow[t] + self.C2 * self.Q
            
            # 确保非负
            self.Q = max(self.Q, 0)
            
            # 计算蓄水量
            self.S = self.K * self.Q
            
            # 保存结果
            discharge[t] = self.Q
            storage[t] = self.S
        
        return {
            'discharge': discharge,
            'storage': storage
        }
    
    def reset(self):
        """重置模型状态"""
        self.Q = 0.0
        self.S = 0.0
    
    def get_state(self) -> Dict[str, float]:
        """获取当前状态"""
        return {
            'Q': self.Q,
            'S': self.S
        }
    
    def set_state(self, state: Dict[str, float]):
        """设置模型状态"""
        if 'Q' in state:
            self.Q = state['Q']
        if 'S' in state:
            self.S = state['S']


class NashCascade:
    """
    纳什瀑布模型（多个线性水库串联）
    
    Parameters
    ----------
    params : dict
        模型参数：
        - area : float, 汇水面积 (m²)
        - K : float, 单个水库调蓄系数 (s)
        - n : int, 水库个数
        - dt : float, 时间步长 (s)
    
    Notes
    -----
    纳什瀑布模型是n个相同的线性水库串联，
    可以模拟更真实的汇流过程。
    
    Examples
    --------
    >>> params = {
    ...     'area': 5000,
    ...     'K': 100,
    ...     'n': 3,
    ...     'dt': 60
    ... }
    >>> model = NashCascade(params)
    """
    
    def __init__(self, params: Dict):
        """初始化纳什瀑布模型"""
        # 验证参数
        required = ['area', 'K', 'n', 'dt']
        for param in required:
            if param not in params:
                raise ValueError(f"缺少必需参数: {param}")
        
        self.area = params['area']
        self.K = params['K']
        self.n = int(params['n'])
        self.dt = params['dt']
        
        if self.n <= 0:
            raise ValueError("水库个数必须为正整数")
        
        # 创建n个线性水库
        self.reservoirs = []
        for i in range(self.n):
            res_params = {
                'area': self.area if i == 0 else 1,  # 只有第一个水库接收净雨
                'K': self.K,
                'dt': self.dt
            }
            self.reservoirs.append(LinearReservoirSlope(res_params))
    
    def run(self, runoff: np.ndarray) -> Dict[str, np.ndarray]:
        """
        运行纳什瀑布模型
        
        Parameters
        ----------
        runoff : ndarray
            净雨强度序列 (mm/h)
        
        Returns
        -------
        results : dict
            包含：
            - discharge : ndarray, 最终出流量 (m³/s)
            - intermediate_discharge : list of ndarray, 各级出流量
        """
        n_steps = len(runoff)
        
        # 重置所有水库
        for res in self.reservoirs:
            res.reset()
        
        # 第一级：输入为净雨
        results_1 = self.reservoirs[0].run(runoff)
        intermediate_discharge = [results_1['discharge']]
        
        # 后续各级：输入为上一级的出流
        for i in range(1, self.n):
            # 将上一级出流转换为等效净雨强度
            inflow_mm_h = intermediate_discharge[-1] / self.area * 1000 * 3600
            
            # 运行当前水库
            results_i = self.reservoirs[i].run(inflow_mm_h)
            intermediate_discharge.append(results_i['discharge'])
        
        return {
            'discharge': intermediate_discharge[-1],
            'intermediate_discharge': intermediate_discharge
        }
    
    def reset(self):
        """重置所有水库"""
        for res in self.reservoirs:
            res.reset()


def estimate_K_from_tc(tc: float, n: int = 3) -> float:
    """
    根据汇流时间和水库个数估算调蓄系数K
    
    对于纳什瀑布模型:
    tc ≈ n × K
    
    Parameters
    ----------
    tc : float
        汇流时间 (s)
    n : int
        水库个数
    
    Returns
    -------
    K : float
        调蓄系数 (s)
    """
    return tc / n


if __name__ == '__main__':
    # 简单测试
    print("线性水库坡面汇流模型测试")
    print("=" * 50)
    
    # 单个线性水库
    params = {
        'area': 5000,   # m²
        'K': 300,       # s (5分钟)
        'dt': 60        # s (1分钟)
    }
    
    print("单个线性水库:")
    print(f"  面积: {params['area']} m²")
    print(f"  调蓄系数: {params['K']} s ({params['K']/60:.1f} 分钟)")
    print()
    
    model = LinearReservoirSlope(params)
    
    # 模拟净雨（三角形）
    duration_minutes = 30
    n_steps = duration_minutes
    runoff = np.zeros(n_steps)
    runoff[5:15] = np.linspace(0, 30, 10)  # 上升段
    runoff[15:25] = np.linspace(30, 0, 10)  # 下降段
    
    results = model.run(runoff)
    
    print("模拟结果:")
    print(f"  峰值流量: {np.max(results['discharge']):.4f} m³/s")
    print(f"  峰现时间: {np.argmax(results['discharge'])} 分钟")
    print()
    
    # 纳什瀑布
    print("纳什瀑布模型 (n=3):")
    nash_params = {
        'area': 5000,
        'K': 100,
        'n': 3,
        'dt': 60
    }
    nash = NashCascade(nash_params)
    nash_results = nash.run(runoff)
    
    print(f"  峰值流量: {np.max(nash_results['discharge']):.4f} m³/s")
    print(f"  峰现时间: {np.argmax(nash_results['discharge'])} 分钟")
