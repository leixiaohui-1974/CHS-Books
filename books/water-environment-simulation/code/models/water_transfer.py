"""
跨流域调水模型（简化版）
Simplified Inter-Basin Water Transfer Model
"""

import numpy as np


class WaterTransferModel:
    """跨流域调水水质风险评估模型"""
    
    def __init__(self, channel_length, flow_rate):
        """
        参数：
        - channel_length: 渠道长度 (km)
        - flow_rate: 输水流量 (m³/s)
        """
        self.channel_length = channel_length
        self.flow_rate = flow_rate
        self.residence_time = channel_length * 1000 / (flow_rate / 10) / 86400  # days
        
        print(f"调水模型初始化:")
        print(f"  渠道长度: {channel_length} km")
        print(f"  输水流量: {flow_rate} m³/s")
        print(f"  停留时间: {self.residence_time:.1f} d")
    
    def simulate_algae_growth_risk(self, initial_Chl, light_intensity):
        """
        评估藻类生长风险
        
        参数：
        - initial_Chl: 初始叶绿素 (μg/L)
        - light_intensity: 光照强度 (W/m²)
        """
        # 简化生长模型
        growth_rate = 0.5 * min(1, light_intensity / 200)
        final_Chl = initial_Chl * np.exp(growth_rate * self.residence_time)
        
        risk = "高" if final_Chl > 30 else ("中" if final_Chl > 10 else "低")
        
        print(f"\n藻类生长风险:")
        print(f"  初始叶绿素: {initial_Chl} μg/L")
        print(f"  最终叶绿素: {final_Chl:.1f} μg/L")
        print(f"  风险等级: {risk}")
        
        return final_Chl, risk


def assess_mixing_quality(source1_quality, source2_quality, ratio):
    """评估多水源混合水质"""
    mixed_quality = source1_quality * ratio + source2_quality * (1 - ratio)
    
    print(f"\n水源混合:")
    print(f"  水源1水质: {source1_quality} mg/L")
    print(f"  水源2水质: {source2_quality} mg/L")
    print(f"  混合比例: {ratio*100:.0f}:{(1-ratio)*100:.0f}")
    print(f"  混合后水质: {mixed_quality:.1f} mg/L")
    
    return mixed_quality
