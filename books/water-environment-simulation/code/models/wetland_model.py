"""
湿地净化功能模型（简化版）
Simplified Wetland Treatment Model
"""

import numpy as np


class WetlandModel:
    """人工湿地净化模型"""
    
    def __init__(self, area, depth, porosity=0.4):
        """
        参数：
        - area: 湿地面积 (m²)
        - depth: 水深 (m)
        - porosity: 孔隙率
        """
        self.area = area
        self.depth = depth
        self.porosity = porosity
        self.volume = area * depth * porosity
        
        print(f"湿地模型初始化:")
        print(f"  面积: {area} m²")
        print(f"  水深: {depth} m")
        print(f"  有效体积: {self.volume:.0f} m³")
    
    def calculate_removal(self, C_in, HRT, k_removal):
        """
        计算去除效率
        
        参数：
        - C_in: 进水浓度 (mg/L)
        - HRT: 水力停留时间 (d)
        - k_removal: 去除速率常数 (1/d)
        """
        C_out = C_in * np.exp(-k_removal * HRT)
        efficiency = (C_in - C_out) / C_in * 100
        
        print(f"\n去除效果:")
        print(f"  进水浓度: {C_in} mg/L")
        print(f"  出水浓度: {C_out:.1f} mg/L")
        print(f"  去除效率: {efficiency:.1f}%")
        
        return C_out, efficiency
    
    def optimize_design(self, target_efficiency, C_in, k_removal):
        """优化设计参数"""
        required_HRT = -np.log(1 - target_efficiency/100) / k_removal
        required_area = self.volume / (self.depth * self.porosity) * required_HRT
        
        print(f"\n设计优化:")
        print(f"  目标去除率: {target_efficiency}%")
        print(f"  所需HRT: {required_HRT:.1f} d")
        print(f"  建议面积: {required_area:.0f} m²")
        
        return required_HRT, required_area


def assess_seasonal_variation(summer_temp, winter_temp):
    """评估季节变化影响"""
    summer_k = 0.5
    winter_k = 0.2
    
    print(f"\n季节变化:")
    print(f"  夏季去除速率: {summer_k} 1/d")
    print(f"  冬季去除速率: {winter_k} 1/d")
    
    return summer_k, winter_k
