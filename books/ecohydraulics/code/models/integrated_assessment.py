"""综合评估与管理模型（案例23-28）"""

import numpy as np
from typing import Dict, List

class WatershedEcohydrology:
    """流域生态水文模型（案例23-25）"""
    
    def __init__(self, watershed_area: float):
        self.area = watershed_area  # km²
    
    def water_balance(self, precipitation: float, evapotranspiration: float) -> Dict:
        """水量平衡 (mm)"""
        runoff = precipitation - evapotranspiration
        infiltration = precipitation * 0.3
        
        return {
            'precipitation': precipitation,
            'evapotranspiration': evapotranspiration,
            'runoff': runoff,
            'infiltration': infiltration
        }
    
    def ecological_flow_regime(self, monthly_flows: np.ndarray) -> Dict:
        """生态流量过程"""
        return {
            'mean': np.mean(monthly_flows),
            'cv': np.std(monthly_flows) / np.mean(monthly_flows),
            'min': np.min(monthly_flows),
            'max': np.max(monthly_flows)
        }


class ClimateChangeImpact:
    """气候变化影响模型（案例26）"""
    
    def __init__(self):
        pass
    
    def temperature_change_impact(self, delta_T: float) -> Dict:
        """温度变化影响"""
        # 简化：温升对生态的影响
        flow_change = -5 * delta_T  # 流量变化%
        habitat_loss = 10 * delta_T  # 栖息地损失%
        
        return {
            'temperature_change': delta_T,
            'flow_change_percent': flow_change,
            'habitat_loss_percent': habitat_loss,
            'adaptation_needed': delta_T > 2.0
        }


class RiverHealthAssessment:
    """河流健康评估（案例27）"""
    
    def __init__(self):
        pass
    
    def calculate_rhi(self, 
                     hydrology_score: float,
                     habitat_score: float,
                     biodiversity_score: float,
                     water_quality_score: float) -> Dict:
        """河流健康指数 (RHI)"""
        # 权重
        weights = [0.25, 0.30, 0.30, 0.15]
        scores = [hydrology_score, habitat_score, biodiversity_score, water_quality_score]
        
        rhi = sum(w * s for w, s in zip(weights, scores))
        
        if rhi >= 80:
            grade = "健康"
        elif rhi >= 60:
            grade = "亚健康"
        elif rhi >= 40:
            grade = "不健康"
        else:
            grade = "病态"
        
        return {
            'rhi': rhi,
            'grade': grade,
            'hydrology': hydrology_score,
            'habitat': habitat_score,
            'biodiversity': biodiversity_score,
            'water_quality': water_quality_score
        }


class IntegratedManagement:
    """综合管理模型（案例28）"""
    
    def __init__(self):
        pass
    
    def multi_stakeholder_benefit(self,
                                  water_allocation: Dict[str, float]) -> Dict:
        """多方利益平衡"""
        total = sum(water_allocation.values())
        
        benefits = {}
        for user, volume in water_allocation.items():
            benefits[user] = volume / total * 100
        
        # 公平性指标（基尼系数简化）
        values = list(water_allocation.values())
        gini = (np.sum(np.abs(np.subtract.outer(values, values)))) / (2 * len(values) * np.sum(values))
        
        return {
            'allocation': water_allocation,
            'benefits': benefits,
            'gini_coefficient': gini,
            'equity': '公平' if gini < 0.3 else '不均衡'
        }
    
    def adaptive_management_framework(self, 
                                     monitoring_data: np.ndarray) -> Dict:
        """适应性管理"""
        trend = np.polyfit(range(len(monitoring_data)), monitoring_data, 1)[0]
        
        if trend > 0.1:
            recommendation = "生态状况改善，继续当前措施"
        elif trend < -0.1:
            recommendation = "生态状况恶化，需调整管理策略"
        else:
            recommendation = "生态状况稳定，保持监测"
        
        return {
            'trend': trend,
            'recommendation': recommendation,
            'mean_value': np.mean(monitoring_data)
        }
