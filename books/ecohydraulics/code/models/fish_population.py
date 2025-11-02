"""鱼类种群动力学模型

本模块实现鱼类种群动态模拟，包括：
- 种群增长模型
- 洄游通道连通性分析
- 栖息地容量评估
- 种群恢复预测
"""

import numpy as np
from typing import Dict, List, Tuple

class RiverConnectivityIndex:
    """河流连通性指数（DCIp）
    
    评估梯级开发对鱼类洄游的影响
    """
    
    def __init__(self, river_segments: List[float], barriers: List[Dict]):
        """
        Parameters:
        -----------
        river_segments : List[float]
            各河段长度 (km)
        barriers : List[Dict]
            障碍物信息，每个包含 {'position': int, 'passability': float}
        """
        self.river_segments = np.array(river_segments)
        self.barriers = barriers
        self.total_length = np.sum(river_segments)
    
    def calculate_dci(self) -> float:
        """计算河流连通性指数 DCIp
        
        DCIp = Σ(li × lj × pij) / L²
        """
        n = len(self.river_segments)
        L_total = self.total_length
        
        # 构建连通性矩阵
        dci = 0.0
        
        for i in range(n):
            for j in range(n):
                li = self.river_segments[i]
                lj = self.river_segments[j]
                
                # 计算i到j的通过概率
                pij = self._passability(i, j)
                
                dci += li * lj * pij
        
        dci = dci / (L_total ** 2)
        
        return dci
    
    def _passability(self, i: int, j: int) -> float:
        """计算从河段i到河段j的通过概率"""
        if i == j:
            return 1.0
        
        # 找出i和j之间的所有障碍
        start = min(i, j)
        end = max(i, j)
        
        passability = 1.0
        for barrier in self.barriers:
            pos = barrier['position']
            if start <= pos < end:
                passability *= barrier['passability']
        
        return passability


class FishPopulationModel:
    """鱼类种群动力学模型
    
    基于Logistic模型模拟种群动态
    """
    
    def __init__(self, 
                 initial_population: float,
                 carrying_capacity: float,
                 growth_rate: float = 0.5):
        """
        Parameters:
        -----------
        initial_population : float
            初始种群数量
        carrying_capacity : float
            环境容纳量
        growth_rate : float
            内禀增长率
        """
        self.N0 = initial_population
        self.K = carrying_capacity
        self.r = growth_rate
    
    def logistic_growth(self, t: float) -> float:
        """Logistic增长模型
        
        N(t) = K / (1 + ((K-N0)/N0) × exp(-r×t))
        """
        N_t = self.K / (1 + ((self.K - self.N0) / self.N0) * np.exp(-self.r * t))
        return N_t
    
    def simulate_population(self, years: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        """模拟种群动态
        
        Returns:
        --------
        tuple
            (时间数组, 种群数量数组)
        """
        t = np.linspace(0, years, years * 12)  # 月度数据
        N = np.array([self.logistic_growth(ti) for ti in t])
        
        return t, N
    
    def recovery_time(self, target_ratio: float = 0.9) -> float:
        """计算种群恢复时间
        
        Parameters:
        -----------
        target_ratio : float
            目标恢复比例（相对于容纳量）
        
        Returns:
        --------
        float
            恢复所需时间（年）
        """
        target_N = self.K * target_ratio
        
        # 解析解
        if self.N0 >= target_N:
            return 0.0
        
        t_recovery = (1.0 / self.r) * np.log(((self.K - self.N0) * target_ratio) / 
                                             (self.N0 * (1 - target_ratio)))
        
        return max(0, t_recovery)


def create_connectivity_scenario(num_dams: int = 5) -> RiverConnectivityIndex:
    """创建梯级开发场景
    
    Parameters:
    -----------
    num_dams : int
        梯级坝数量
    """
    # 河段长度（均分）
    segments = [100.0] * (num_dams + 1)  # km
    
    # 障碍物（梯级坝）
    barriers = []
    for i in range(num_dams):
        barriers.append({
            'position': i,
            'passability': 0.3  # 30%通过率
        })
    
    return RiverConnectivityIndex(segments, barriers)
