"""鱼类行为响应与索饵场模型

本模块实现鱼类索饵场水力-饵料关系分析，包括：
- 饵料生物分布模型
- 鱼类摄食效率计算
- 能量收支分析
- 最优索饵流速
"""

import numpy as np
from typing import Dict, Tuple, Optional

class FeedingGroundModel:
    """鱼类索饵场模型
    
    基于最优觅食理论，分析水力条件对鱼类摄食的影响
    """
    
    def __init__(self, species: str = "草鱼"):
        self.species = species
        self.body_length = 30.0  # cm
        self.body_weight = 270.0  # g
    
    def prey_density_by_velocity(self, velocity: float) -> float:
        """根据流速估算饵料密度
        
        浮游生物和底栖生物密度与流速相关
        """
        # 中等流速饵料密度最高
        optimal_v = 0.5
        density_max = 1000.0  # 个/m³
        
        # 高斯分布
        density = density_max * np.exp(-((velocity - optimal_v) ** 2) / (2 * 0.3 ** 2))
        
        return density
    
    def feeding_efficiency(self, velocity: float, prey_density: float) -> float:
        """计算摄食效率
        
        摄食效率 = 捕获率 × 饵料密度
        """
        # 流速太快或太慢都影响捕获
        if velocity < 0.2:
            capture_rate = 0.3
        elif velocity > 1.5:
            capture_rate = 0.2
        else:
            capture_rate = 0.8 - 0.3 * abs(velocity - 0.6)
        
        efficiency = capture_rate * prey_density
        
        return max(0, efficiency)
    
    def energy_balance(self, velocity: float, feeding_duration: float = 3600.0) -> Dict:
        """计算能量收支平衡
        
        能量收入 = 摄食获得
        能量支出 = 基础代谢 + 游泳消耗
        """
        # 饵料密度
        prey_dens = self.prey_density_by_velocity(velocity)
        
        # 摄食效率
        feed_eff = self.feeding_efficiency(velocity, prey_dens)
        
        # 能量收入（简化，增加能量转化系数）
        energy_gain = feed_eff * feeding_duration * 2.5  # J
        
        # 能量支出
        BMR = 0.3 * (self.body_weight ** 0.8)  # 基础代谢 W
        swimming_cost = BMR * ((velocity / 0.6) ** 2.5)  # 游泳消耗 W
        energy_cost = (BMR + swimming_cost) * feeding_duration  # J
        
        net_energy = energy_gain - energy_cost
        
        return {
            'prey_density': prey_dens,
            'feeding_efficiency': feed_eff,
            'energy_gain_J': energy_gain,
            'energy_cost_J': energy_cost,
            'net_energy_J': net_energy,
            'is_favorable': net_energy > 0
        }
    
    def optimal_feeding_velocity(self) -> float:
        """找到最优索饵流速
        
        使净能量收益最大
        """
        velocities = np.linspace(0.2, 1.5, 50)
        net_energies = []
        
        for v in velocities:
            balance = self.energy_balance(v)
            net_energies.append(balance['net_energy_J'])
        
        # 找到最大净能量对应的流速
        max_idx = np.argmax(net_energies)
        optimal_v = velocities[max_idx]
        
        return optimal_v


def create_grass_carp_feeding_model() -> FeedingGroundModel:
    """创建草鱼索饵模型"""
    return FeedingGroundModel("草鱼")
