"""
供水管网模型

定义管网的拓扑结构、节点、管道和泵站
"""

import numpy as np
from typing import List, Dict, Optional


class Node:
    """管网节点"""
    
    def __init__(
        self,
        node_id: str,
        node_type: str,
        elevation: float = 0.0,
        demand: float = 0.0,
        min_pressure: float = 0.0
    ):
        """
        Parameters
        ----------
        node_id : str
            节点ID
        node_type : str
            节点类型：'source', 'junction', 'tank'
        elevation : float
            地面高程 (m)
        demand : float
            需水量 (m³/h)
        min_pressure : float
            最小压力要求 (m)
        """
        self.id = node_id
        self.type = node_type
        self.elevation = elevation
        self.demand = demand
        self.min_pressure = min_pressure
        
        # 计算结果
        self.head = None  # 水头 (m)
        self.pressure = None  # 压力 (m)


class Pipe:
    """管道"""
    
    def __init__(
        self,
        pipe_id: str,
        from_node: str,
        to_node: str,
        length: float,
        diameter: float,
        roughness: float = 0.012
    ):
        """
        Parameters
        ----------
        pipe_id : str
            管道ID
        from_node, to_node : str
            起止节点ID
        length : float
            长度 (m)
        diameter : float
            直径 (mm)
        roughness : float
            粗糙系数
        """
        self.id = pipe_id
        self.from_node = from_node
        self.to_node = to_node
        self.length = length
        self.diameter = diameter / 1000  # 转换为米
        self.roughness = roughness
        
        # 计算结果
        self.flow = 0.0  # 流量 (m³/h)
        self.velocity = 0.0  # 流速 (m/s)
        self.head_loss = 0.0  # 水头损失 (m)
    
    def calculate_head_loss(self, flow: float) -> float:
        """
        计算水头损失（Hazen-Williams公式）
        
        h_f = 10.67 * L * Q^1.852 / (C^1.852 * D^4.87)
        
        Parameters
        ----------
        flow : float
            流量 (m³/h)
        
        Returns
        -------
        float
            水头损失 (m)
        """
        if abs(flow) < 1e-6:
            return 0.0
        
        # Hazen-Williams系数
        C = 130 * (1 - self.roughness * 10)
        
        # 流量单位转换 m³/h -> m³/s
        Q = abs(flow) / 3600
        
        # 水头损失
        h_f = 10.67 * self.length * (Q ** 1.852) / (C ** 1.852 * self.diameter ** 4.87)
        
        return h_f if flow > 0 else -h_f


class PumpStation:
    """泵站"""
    
    def __init__(
        self,
        pump_id: str,
        capacity_range: tuple,
        efficiency: float,
        head_curve: Dict[str, float]
    ):
        """
        Parameters
        ----------
        pump_id : str
            泵站ID
        capacity_range : tuple
            流量范围 (m³/h)
        efficiency : float
            效率
        head_curve : Dict
            扬程曲线参数 {'a': float, 'b': float}
            H = a - b*Q^2
        """
        self.id = pump_id
        self.min_flow = capacity_range[0]
        self.max_flow = capacity_range[1]
        self.efficiency = efficiency
        self.head_a = head_curve['a']
        self.head_b = head_curve['b']
        
        # 运行状态
        self.flow = 0.0  # 当前流量
        self.head = 0.0  # 当前扬程
        self.power = 0.0  # 当前功率 (kW)
    
    def calculate_head(self, flow: float) -> float:
        """
        计算扬程
        
        Parameters
        ----------
        flow : float
            流量 (m³/h)
        
        Returns
        -------
        float
            扬程 (m)
        """
        return self.head_a - self.head_b * (flow ** 2)
    
    def calculate_power(self, flow: float) -> float:
        """
        计算功率
        
        P = ρ·g·Q·H / (η·3600)
        
        Parameters
        ----------
        flow : float
            流量 (m³/h)
        
        Returns
        -------
        float
            功率 (kW)
        """
        if flow < 1e-6:
            return 0.0
        
        head = self.calculate_head(flow)
        
        # Q单位转换 m³/h -> m³/s
        Q = flow / 3600
        
        # 功率 (kW)
        power = 1000 * 9.81 * Q * head / (self.efficiency * 1000)
        
        return power


class WaterNetwork:
    """供水管网"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.pipes: Dict[str, Pipe] = {}
        self.pumps: Dict[str, PumpStation] = {}
    
    def add_node(self, node: Node):
        """添加节点"""
        self.nodes[node.id] = node
    
    def add_pipe(self, pipe: Pipe):
        """添加管道"""
        self.pipes[pipe.id] = pipe
    
    def add_pump(self, pump: PumpStation):
        """添加泵站"""
        self.pumps[pump.id] = pump
    
    def get_total_demand(self) -> float:
        """获取总需水量"""
        return sum(node.demand for node in self.nodes.values())
    
    def get_total_power(self) -> float:
        """获取总功率"""
        return sum(pump.power for pump in self.pumps.values())
    
    def check_pressure_constraints(self) -> Dict[str, bool]:
        """检查压力约束"""
        results = {}
        for node_id, node in self.nodes.items():
            if node.type == 'junction' and node.pressure is not None:
                results[node_id] = node.pressure >= node.min_pressure
        return results
    
    def get_pressure_violation(self) -> float:
        """获取压力违约量"""
        violation = 0.0
        for node in self.nodes.values():
            if node.type == 'junction' and node.pressure is not None:
                if node.pressure < node.min_pressure:
                    violation += (node.min_pressure - node.pressure)
        return violation
