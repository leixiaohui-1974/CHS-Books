"""水工建筑物生态化设计模型（案例19-22）"""

import numpy as np
from typing import Dict, Tuple, List

class EcologicalWeir:
    """生态堰设计模型（案例19）"""
    
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    
    def discharge_capacity(self, gate_opening: float, upstream_depth: float) -> float:
        """过流能力 (m³/s)"""
        # 堰流公式
        m = 0.40  # 流量系数
        g = 9.81
        Q = m * self.width * gate_opening * np.sqrt(2 * g * upstream_depth)
        return Q
    
    def fish_passage_velocity(self, discharge: float) -> float:
        """鱼类通过流速 (m/s)"""
        A = self.width * self.height * 0.3  # 通道面积
        v = discharge / A if A > 0 else 0
        return v
    
    def suitability_assessment(self, velocity: float) -> str:
        """适宜性评价"""
        if velocity < 0.8:
            return "适宜"
        elif velocity < 1.5:
            return "基本适宜"
        else:
            return "不适宜"


class StockingArea:
    """增殖放流区设计（案例20）"""
    
    def __init__(self, area: float = 1000.0):
        self.area = area
    
    def acclimation_velocity(self, stage: int) -> float:
        """驯化流速 (m/s)"""
        # 3阶段驯化
        stages = {1: 0.1, 2: 0.3, 3: 0.5}
        return stages.get(stage, 0.2)
    
    def optimal_release_flow(self, fish_length: float) -> float:
        """最优放流流量 (m³/s)"""
        # 基于鱼体长
        Q_optimal = 50 + fish_length * 10
        return Q_optimal
    
    def survival_rate_estimate(self, flow: float, temperature: float) -> float:
        """存活率估算"""
        # 简化模型
        if 15 <= temperature <= 25:
            temp_factor = 1.0
        else:
            temp_factor = 0.7
        
        if 50 <= flow <= 200:
            flow_factor = 1.0
        else:
            flow_factor = 0.8
        
        return 0.7 * temp_factor * flow_factor


class HydropowerScheduling:
    """水电站生态调度（案例21）"""
    
    def __init__(self, capacity_MW: float, ecological_flow: float):
        self.capacity = capacity_MW
        self.Q_eco = ecological_flow
    
    def power_generation(self, discharge: float, head: float) -> float:
        """发电量 (MW)"""
        efficiency = 0.85
        g = 9.81
        rho = 1000.0
        P = efficiency * rho * g * discharge * head / 1e6
        return min(P, self.capacity)
    
    def ecological_benefit(self, discharge: float) -> float:
        """生态效益评分 (0-100)"""
        if discharge >= self.Q_eco:
            return 100 * (1 - np.exp(-(discharge - self.Q_eco) / self.Q_eco))
        else:
            return 50 * (discharge / self.Q_eco)
    
    def multi_objective_optimization(self, discharges: np.ndarray, head: float) -> Dict:
        """多目标优化"""
        powers = []
        eco_benefits = []
        
        for Q in discharges:
            P = self.power_generation(Q, head)
            E = self.ecological_benefit(Q)
            powers.append(P)
            eco_benefits.append(E)
        
        # 找到Pareto前沿
        pareto_indices = []
        for i in range(len(discharges)):
            is_pareto = True
            for j in range(len(discharges)):
                if i != j:
                    if powers[j] >= powers[i] and eco_benefits[j] >= eco_benefits[i]:
                        if powers[j] > powers[i] or eco_benefits[j] > eco_benefits[i]:
                            is_pareto = False
                            break
            if is_pareto:
                pareto_indices.append(i)
        
        return {
            'discharges': discharges,
            'powers': np.array(powers),
            'eco_benefits': np.array(eco_benefits),
            'pareto_indices': pareto_indices
        }


class DamSprayImpact:
    """大坝泄洪雾化影响（案例22）"""
    
    def __init__(self, dam_height: float):
        self.H = dam_height
    
    def spray_intensity(self, discharge: float, distance: float) -> float:
        """雾化强度 (mm/h)"""
        # 经验公式
        I_max = 0.5 * (discharge / 100) * np.sqrt(self.H)
        I = I_max * np.exp(-distance / 100)
        return I
    
    def vegetation_impact_zone(self, discharge: float) -> float:
        """植被影响范围 (m)"""
        # 雾化范围
        return 50 * np.sqrt(discharge * self.H / 100)
    
    def mitigation_measures(self) -> List[str]:
        """缓解措施"""
        return [
            "优化泄洪方式（分散泄洪）",
            "设置导流设施",
            "种植耐雾化植物",
            "建立监测预警系统"
        ]
