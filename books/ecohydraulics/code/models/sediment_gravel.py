"""卵石河床补充模型 (案例16)

本模块实现产卵场底质补充设计
"""

import numpy as np
from typing import Dict, Tuple

class GravelSupplementDesign:
    """卵石补充设计模型"""
    
    def __init__(self, target_d50: float = 25.0):
        """
        Parameters:
        -----------
        target_d50 : float
            目标中值粒径 (mm)
        """
        self.target_d50 = target_d50
    
    def critical_velocity(self, d: float) -> float:
        """计算起动流速 (m/s)"""
        # Hjulström公式简化
        return 0.2 * (d / 1000) ** 0.5
    
    def shields_stress(self, d: float, h: float, S: float) -> float:
        """计算Shields应力"""
        rho = 1000.0
        rho_s = 2650.0
        g = 9.81
        tau = rho * g * h * S
        tau_c = (rho_s - rho) * g * d / 1000
        return tau / tau_c
    
    def gravel_size_distribution(self) -> Dict:
        """设计粒径配比"""
        d50 = self.target_d50
        return {
            'd16': d50 * 0.5,
            'd50': d50,
            'd84': d50 * 2.0,
            'd90': d50 * 2.5
        }
    
    def stability_assessment(self, velocity: float, depth: float, slope: float) -> Dict:
        """稳定性评估"""
        d50 = self.target_d50
        v_c = self.critical_velocity(d50)
        theta = self.shields_stress(d50, depth, slope)
        
        if velocity < v_c:
            status = "稳定"
        elif velocity < 1.5 * v_c:
            status = "弱输移"
        else:
            status = "强输移"
        
        return {
            'critical_velocity': v_c,
            'shields_stress': theta,
            'stability_status': status,
            'safety_factor': v_c / velocity if velocity > 0 else 10.0
        }


class EstuaryHydraulics:
    """河口水力学模型 (案例17)"""
    
    def __init__(self, tidal_range: float = 3.0):
        """
        Parameters:
        -----------
        tidal_range : float
            潮差 (m)
        """
        self.tidal_range = tidal_range
    
    def tidal_water_level(self, t: float, period: float = 12.4) -> float:
        """潮汐水位 (m)"""
        return self.tidal_range / 2 * np.sin(2 * np.pi * t / period)
    
    def saltwater_intrusion(self, river_flow: float) -> float:
        """盐水楔侵入距离 (km)"""
        # 简化经验公式
        L = 15 * (self.tidal_range ** 1.5) / (river_flow ** 0.5) if river_flow > 0 else 50
        return min(L, 100)
    
    def ecological_water_requirement(self) -> float:
        """生态需水量 (m³/s)"""
        # 维持咸淡水平衡
        return 100 * (self.tidal_range / 3.0)


class RestorationAssessment:
    """生态修复效果评估模型 (案例18)"""
    
    def __init__(self):
        """初始化"""
        pass
    
    def hydraulic_diversity_change(self, before: np.ndarray, after: np.ndarray) -> Dict:
        """水力多样性变化"""
        H_before = -np.sum(before * np.log(before + 1e-10))
        H_after = -np.sum(after * np.log(after + 1e-10))
        
        change_rate = (H_after - H_before) / H_before * 100 if H_before > 0 else 0
        
        return {
            'shannon_before': H_before,
            'shannon_after': H_after,
            'change_rate': change_rate,
            'improvement': change_rate > 0
        }
    
    def habitat_quality_score(self, velocity: float, depth: float, substrate: str) -> float:
        """栖息地质量评分 (0-1)"""
        # 流速适宜性
        if 0.3 <= velocity <= 0.8:
            v_score = 1.0
        elif velocity < 0.3:
            v_score = velocity / 0.3
        else:
            v_score = max(0.2, 1 - (velocity - 0.8) / 1.2)
        
        # 水深适宜性
        if 0.5 <= depth <= 2.0:
            d_score = 1.0
        elif depth < 0.5:
            d_score = 0.5 + depth
        else:
            d_score = max(0.3, 1 - (depth - 2) / 3)
        
        # 底质适宜性
        substrate_scores = {'砾石': 1.0, '粗砂': 0.8, '细砂': 0.5, '淤泥': 0.2}
        s_score = substrate_scores.get(substrate, 0.5)
        
        return (v_score * 0.4 + d_score * 0.3 + s_score * 0.3)
    
    def comprehensive_evaluation(self, 
                                 hydraulic_improvement: float,
                                 habitat_improvement: float,
                                 biodiversity_improvement: float) -> Dict:
        """综合评价"""
        overall_score = (hydraulic_improvement * 0.3 + 
                        habitat_improvement * 0.4 + 
                        biodiversity_improvement * 0.3)
        
        if overall_score > 30:
            grade = "显著"
        elif overall_score > 15:
            grade = "良好"
        elif overall_score > 5:
            grade = "一般"
        else:
            grade = "较差"
        
        return {
            'overall_score': overall_score,
            'grade': grade,
            'hydraulic_contribution': hydraulic_improvement * 0.3,
            'habitat_contribution': habitat_improvement * 0.4,
            'biodiversity_contribution': biodiversity_improvement * 0.3
        }
