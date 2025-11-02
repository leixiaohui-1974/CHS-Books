"""
流域水文-水质耦合模型（简化版）
Simplified Watershed Hydrological-Water Quality Model
"""

import numpy as np


class WatershedModel:
    """简化的流域水文-水质耦合模型"""
    
    def __init__(self, area, n_subbasins=5):
        """
        参数：
        - area: 流域面积 (km²)
        - n_subbasins: 子流域数量
        """
        self.area = area
        self.n_subbasins = n_subbasins
        self.subbasin_area = area / n_subbasins
        
        print(f"流域模型初始化:")
        print(f"  流域面积: {area} km²")
        print(f"  子流域数: {n_subbasins}")
    
    def simulate_runoff(self, rainfall, CN=75):
        """
        模拟径流（SCS-CN方法）
        
        参数：
        - rainfall: 降雨量 (mm)
        - CN: 径流曲线数
        """
        S = 25400 / CN - 254  # 最大潜在滞留量 (mm)
        if rainfall > 0.2 * S:
            runoff = (rainfall - 0.2*S)**2 / (rainfall + 0.8*S)
        else:
            runoff = 0
        
        print(f"\n径流计算:")
        print(f"  降雨: {rainfall} mm")
        print(f"  径流: {runoff:.1f} mm")
        
        return runoff
    
    def calculate_pollutant_load(self, runoff, EMC):
        """
        计算污染物负荷
        
        参数：
        - runoff: 径流量 (mm)
        - EMC: 事件平均浓度 (mg/L)
        """
        volume = runoff * self.area * 1000  # m³
        load = volume * EMC / 1000  # kg
        
        print(f"\n污染负荷:")
        print(f"  径流体积: {volume:.0f} m³")
        print(f"  污染负荷: {load:.1f} kg")
        
        return load


def assess_land_use_impact(agricultural_ratio, urban_ratio):
    """评估土地利用影响"""
    impact_score = agricultural_ratio * 0.6 + urban_ratio * 0.9
    
    print(f"\n土地利用影响:")
    print(f"  农业用地比例: {agricultural_ratio*100:.1f}%")
    print(f"  城市用地比例: {urban_ratio*100:.1f}%")
    print(f"  综合影响分数: {impact_score:.2f}")
    
    return impact_score
