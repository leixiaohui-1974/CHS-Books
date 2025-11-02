"""丹尼尔式鱼道设计模型（案例9）"""

import numpy as np
from typing import Dict, Tuple

class DenilFishway:
    """丹尼尔式鱼道水力设计模型
    
    丹尼尔鱼道是一种倾斜槽式鱼道，通过槽底的挡板产生紊流
    消能，适用于中小型鱼类。
    """
    
    def __init__(self, 
                 channel_width: float,
                 channel_length: float,
                 slope: float,
                 baffle_spacing: float = 0.4):
        """
        Parameters:
        -----------
        channel_width : float
            槽道宽度 (m)
        channel_length : float
            槽道总长度 (m)
        slope : float
            底坡 (1:n, 例如1:8表示slope=8)
        baffle_spacing : float
            挡板间距 (m), 默认0.4m
        """
        self.B = channel_width
        self.L = channel_length
        self.slope = slope
        self.s = baffle_spacing
        
        # 标准挡板参数（基于经典丹尼尔设计）
        self.baffle_height = 0.15  # 挡板高度 (m)
        self.baffle_angle = 45  # 挡板倾角 (度)
    
    def water_depth(self, discharge: float) -> float:
        """计算槽内水深 (m)
        
        基于经验公式: h = C * Q^0.4 * B^(-0.3)
        """
        C = 0.5 + 0.05 / self.slope  # 经验系数
        h = C * (discharge ** 0.4) * (self.B ** (-0.3))
        return h
    
    def flow_velocity(self, discharge: float) -> float:
        """计算平均流速 (m/s)"""
        h = self.water_depth(discharge)
        A = self.B * h
        v = discharge / A if A > 0 else 0
        return v
    
    def energy_dissipation_rate(self) -> float:
        """单位长度能量耗散率 (m/m)
        
        丹尼尔鱼道的关键设计参数
        """
        # 基于底坡和挡板配置
        theta = np.radians(self.baffle_angle)
        epsilon = (1 / self.slope) * (1 + 0.5 * np.sin(theta))
        return epsilon
    
    def hydraulic_conditions(self, discharge: float) -> Dict:
        """计算水力条件"""
        h = self.water_depth(discharge)
        v = self.flow_velocity(discharge)
        Fr = v / np.sqrt(9.81 * h)  # 弗劳德数
        
        # 单位功率（用于评估鱼类通过难度）
        P_unit = 9810 * discharge * (1 / self.slope) / (self.B * self.L)  # W/m²
        
        return {
            'discharge': discharge,
            'water_depth': h,
            'velocity': v,
            'froude_number': Fr,
            'unit_power': P_unit,
            'energy_dissipation': self.energy_dissipation_rate()
        }
    
    def fish_passage_capacity(self, discharge: float, 
                             fish_species: str = 'cyprinid') -> Dict:
        """鱼类通过能力评估
        
        Parameters:
        -----------
        fish_species : str
            鱼类类型: 'cyprinid'(鲤科), 'salmonid'(鲑科)
        """
        conditions = self.hydraulic_conditions(discharge)
        v = conditions['velocity']
        P_unit = conditions['unit_power']
        
        # 不同鱼类的临界参数
        if fish_species == 'cyprinid':
            v_crit = 2.0  # m/s
            P_crit = 200  # W/m²
        else:  # salmonid
            v_crit = 3.0
            P_crit = 300
        
        # 适宜性评分
        if v < v_crit * 0.8 and P_unit < P_crit * 0.8:
            suitability = "优秀"
            score = 1.0
        elif v < v_crit and P_unit < P_crit:
            suitability = "良好"
            score = 0.8
        elif v < v_crit * 1.2 and P_unit < P_crit * 1.2:
            suitability = "可接受"
            score = 0.6
        else:
            suitability = "不适宜"
            score = 0.3
        
        return {
            'fish_species': fish_species,
            'velocity': v,
            'critical_velocity': v_crit,
            'unit_power': P_unit,
            'critical_power': P_crit,
            'suitability': suitability,
            'score': score
        }
    
    def design_optimization(self, 
                          target_discharge: float,
                          target_species: str = 'cyprinid') -> Dict:
        """优化设计参数"""
        # 尝试不同的底坡
        slopes = np.array([6, 8, 10, 12, 15])
        results = []
        
        for s in slopes:
            self.slope = s
            passage = self.fish_passage_capacity(target_discharge, target_species)
            results.append({
                'slope': s,
                'score': passage['score'],
                'velocity': passage['velocity'],
                'unit_power': passage['unit_power'],
                'suitability': passage['suitability']
            })
        
        # 找到最优方案
        scores = [r['score'] for r in results]
        best_idx = np.argmax(scores)
        
        return {
            'optimal_slope': results[best_idx]['slope'],
            'all_results': results,
            'recommendation': results[best_idx]
        }
    
    def baffle_configuration(self) -> Dict:
        """挡板配置参数"""
        n_baffles = int(self.L / self.s)
        
        return {
            'baffle_spacing': self.s,
            'baffle_height': self.baffle_height,
            'baffle_angle': self.baffle_angle,
            'number_of_baffles': n_baffles,
            'total_length': self.L
        }


def create_denil_design(dam_height: float,
                       design_discharge: float,
                       fish_species: str = 'cyprinid') -> Dict:
    """创建标准丹尼尔鱼道设计
    
    Parameters:
    -----------
    dam_height : float
        坝高 (m)
    design_discharge : float
        设计流量 (m³/s)
    fish_species : str
        目标鱼类
    
    Returns:
    --------
    Dict : 完整的设计方案
    """
    # 标准设计参数
    width = 1.0  # 标准槽宽1m
    
    # 根据坝高确定长度（坡度1:10左右）
    slope_estimate = 10
    length = dam_height * slope_estimate
    
    # 创建鱼道
    fishway = DenilFishway(width, length, slope_estimate)
    
    # 优化设计
    optimization = fishway.design_optimization(design_discharge, fish_species)
    
    # 使用最优坡度
    optimal_slope = optimization['optimal_slope']
    fishway = DenilFishway(width, dam_height * optimal_slope, optimal_slope)
    
    # 最终设计参数
    conditions = fishway.hydraulic_conditions(design_discharge)
    passage = fishway.fish_passage_capacity(design_discharge, fish_species)
    baffles = fishway.baffle_configuration()
    
    return {
        'dam_height': dam_height,
        'design_discharge': design_discharge,
        'channel_width': width,
        'channel_length': fishway.L,
        'slope': optimal_slope,
        'hydraulic_conditions': conditions,
        'fish_passage': passage,
        'baffle_config': baffles,
        'optimization_results': optimization
    }
