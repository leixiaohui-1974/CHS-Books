"""
管网水力计算求解器

使用简化的迭代方法求解管网水力方程
"""

import numpy as np
from typing import Dict
from .network_model import WaterNetwork


class HydraulicSolver:
    """管网水力求解器"""
    
    def __init__(self, network: WaterNetwork):
        self.network = network
        self.max_iterations = 100
        self.tolerance = 0.01  # m
    
    def solve(self, pump_flows: Dict[str, float]) -> bool:
        """
        求解管网水力
        
        简化假设：
        1. 泵站直接供给用户区
        2. 忽略管道阻力的耦合影响
        3. 逐个计算各支路
        
        Parameters
        ----------
        pump_flows : Dict[str, float]
            各泵站流量 (m³/h)
        
        Returns
        -------
        bool
            是否收敛
        """
        # 更新泵站流量
        for pump_id, flow in pump_flows.items():
            if pump_id in self.network.pumps:
                pump = self.network.pumps[pump_id]
                pump.flow = flow
                pump.head = pump.calculate_head(flow)
                pump.power = pump.calculate_power(flow)
        
        # 简化计算：泵站压力 - 管道损失
        for node_id, node in self.network.nodes.items():
            if node.type == 'junction':
                # 找到供给该节点的泵站
                supplying_pump = self._find_supplying_pump(node_id)
                
                if supplying_pump:
                    # 泵站扬程
                    pump_head = supplying_pump.head
                    
                    # 管道水头损失
                    pipe_loss = self._calculate_pipe_loss(supplying_pump.id, node_id, supplying_pump.flow)
                    
                    # 节点水头 = 泵站扬程 - 管道损失
                    node.head = pump_head - pipe_loss
                    
                    # 节点压力 = 水头 - 地面高程
                    node.pressure = node.head - node.elevation
                else:
                    # 未供水节点
                    node.head = 0.0
                    node.pressure = 0.0
        
        return True
    
    def _find_supplying_pump(self, node_id: str):
        """查找供给该节点的泵站"""
        # 简化：根据管道连接关系查找
        for pipe in self.network.pipes.values():
            if pipe.to_node == node_id:
                # 查找连接到该管道起点的泵站
                for pump in self.network.pumps.values():
                    if pump.id == pipe.from_node:
                        return pump
        return None
    
    def _calculate_pipe_loss(self, from_node: str, to_node: str, flow: float) -> float:
        """计算管道水头损失"""
        for pipe in self.network.pipes.values():
            if pipe.from_node == from_node and pipe.to_node == to_node:
                return pipe.calculate_head_loss(flow)
        return 0.0
    
    def solve_iterative(self, pump_flows: Dict[str, float], max_iter: int = 50) -> bool:
        """
        迭代求解管网水力（更精确）
        
        Parameters
        ----------
        pump_flows : Dict[str, float]
            各泵站流量
        max_iter : int
            最大迭代次数
        
        Returns
        -------
        bool
            是否收敛
        """
        for iteration in range(max_iter):
            # 保存上一次的压力
            old_pressures = {node_id: node.pressure if node.pressure else 0.0 
                           for node_id, node in self.network.nodes.items()}
            
            # 求解一次
            self.solve(pump_flows)
            
            # 检查收敛
            converged = True
            for node_id, node in self.network.nodes.items():
                if node.type == 'junction':
                    pressure_change = abs((node.pressure if node.pressure else 0.0) - old_pressures[node_id])
                    if pressure_change > self.tolerance:
                        converged = False
                        break
            
            if converged:
                return True
        
        return False
