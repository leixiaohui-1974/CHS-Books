"""
河网水系连通模型（简化版）
Simplified River Network Connectivity Model
"""

import numpy as np


class RiverNetworkModel:
    """河网水系连通模型"""
    
    def __init__(self, n_nodes, n_gates):
        """
        参数：
        - n_nodes: 节点数
        - n_gates: 闸门数
        """
        self.n_nodes = n_nodes
        self.n_gates = n_gates
        self.flow_matrix = np.zeros((n_nodes, n_nodes))
        
        print(f"河网模型初始化:")
        print(f"  节点数: {n_nodes}")
        print(f"  闸门数: {n_gates}")
    
    def simulate_gate_operation(self, gate_opening, inflow):
        """
        模拟闸门调度
        
        参数：
        - gate_opening: 闸门开度 (0-1)
        - inflow: 入流流量 (m³/s)
        """
        outflow = gate_opening * inflow
        
        print(f"\n闸门调度:")
        print(f"  开度: {gate_opening*100:.0f}%")
        print(f"  入流: {inflow:.1f} m³/s")
        print(f"  出流: {outflow:.1f} m³/s")
        
        return outflow
    
    def calculate_water_exchange_time(self, volume, flow_rate):
        """
        计算换水周期
        
        参数：
        - volume: 水体体积 (m³)
        - flow_rate: 流量 (m³/s)
        """
        time = volume / flow_rate / 86400  # days
        
        print(f"\n换水周期:")
        print(f"  水体体积: {volume:.0f} m³")
        print(f"  流量: {flow_rate:.1f} m³/s")
        print(f"  换水周期: {time:.1f} d")
        
        return time


def optimize_gate_schedule(target_quality, current_quality):
    """优化闸门调度策略（简化）"""
    if current_quality < target_quality:
        recommended_opening = 0.8  # 加大换水
    else:
        recommended_opening = 0.3  # 正常运行
    
    print(f"\n调度优化:")
    print(f"  目标水质: {target_quality} mg/L")
    print(f"  当前水质: {current_quality} mg/L")
    print(f"  推荐开度: {recommended_opening*100:.0f}%")
    
    return recommended_opening
