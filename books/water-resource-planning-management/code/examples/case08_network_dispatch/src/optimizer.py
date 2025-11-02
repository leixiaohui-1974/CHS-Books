"""
管网优化调度器

使用LP、NLP和MPC方法进行优化调度
"""

import numpy as np
from typing import Dict, List
from scipy.optimize import linprog, minimize
from .network_model import WaterNetwork
from .hydraulic_solver import HydraulicSolver


class NetworkOptimizer:
    """管网优化调度器"""
    
    def __init__(self, network: WaterNetwork, solver: HydraulicSolver):
        self.network = network
        self.solver = solver
    
    def optimize_lp(self, total_demand: float, power_costs: Dict[str, float]) -> Dict[str, float]:
        """
        线性规划优化（简化模型）
        
        min Σ c_i * Q_i
        s.t. Σ Q_i >= D_total
             Q_min,i <= Q_i <= Q_max,i
        
        Parameters
        ----------
        total_demand : float
            总需水量 (m³/h)
        power_costs : Dict[str, float]
            各泵站单位流量成本
        
        Returns
        -------
        Dict[str, float]
            各泵站最优流量
        """
        pumps = list(self.network.pumps.values())
        n = len(pumps)
        
        # 目标函数系数（近似线性化）
        c = np.array([power_costs.get(pump.id, 1.0) for pump in pumps])
        
        # 约束：Σ Q_i >= D_total  =>  -Σ Q_i <= -D_total
        A_ub = -np.ones((1, n))
        b_ub = np.array([-total_demand])
        
        # 变量界限
        bounds = [(pump.min_flow, pump.max_flow) for pump in pumps]
        
        # 求解
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        
        if result.success:
            flows = {}
            for i, pump in enumerate(pumps):
                flows[pump.id] = result.x[i]
            return flows
        else:
            # 失败时返回均匀分配
            avg_flow = total_demand / n
            return {pump.id: np.clip(avg_flow, pump.min_flow, pump.max_flow) 
                   for pump in pumps}
    
    def optimize_nlp(self, demands: Dict[str, float], power_cost: float = 0.8) -> Dict:
        """
        非线性规划优化
        
        min Σ P_i(Q_i) * cost
        s.t. 流量平衡
             压力约束
             泵站容量约束
        
        Parameters
        ----------
        demands : Dict[str, float]
            各节点需水量
        power_cost : float
            电价 (元/kWh)
        
        Returns
        -------
        Dict
            优化结果
        """
        pumps = list(self.network.pumps.values())
        n = len(pumps)
        
        # 更新节点需水量
        for node_id, demand in demands.items():
            if node_id in self.network.nodes:
                self.network.nodes[node_id].demand = demand
        
        total_demand = sum(demands.values())
        
        # 目标函数：最小化能耗成本
        def objective(Q):
            total_cost = 0.0
            for i, pump in enumerate(pumps):
                power = pump.calculate_power(Q[i])
                total_cost += power * power_cost
            return total_cost
        
        # 约束
        def constraint_flow_balance(Q):
            # 供给量 >= 需求量
            return np.sum(Q) - total_demand
        
        def constraint_pressure(Q):
            # 更新泵站流量并求解水力
            pump_flows = {pump.id: Q[i] for i, pump in enumerate(pumps)}
            self.solver.solve(pump_flows)
            
            # 计算压力违约量（负值表示不满足）
            violation = 0.0
            for node in self.network.nodes.values():
                if node.type == 'junction' and node.pressure is not None:
                    if node.pressure < node.min_pressure:
                        violation += (node.min_pressure - node.pressure)
            
            # 返回负值表示违约（约束函数 >= 0）
            return -violation
        
        # 约束定义
        constraints = [
            {'type': 'ineq', 'fun': constraint_flow_balance},
            {'type': 'ineq', 'fun': constraint_pressure}
        ]
        
        # 变量界限
        bounds = [(pump.min_flow, pump.max_flow) for pump in pumps]
        
        # 初始猜测（均匀分配）
        x0 = np.array([total_demand / n for _ in range(n)])
        x0 = np.clip(x0, [b[0] for b in bounds], [b[1] for b in bounds])
        
        # 求解
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 100}
        )
        
        # 提取结果
        if result.success:
            flows = {pump.id: result.x[i] for i, pump in enumerate(pumps)}
        else:
            # 使用LP结果作为备选
            flows = self.optimize_lp(total_demand, {p.id: 1.0 for p in pumps})
        
        # 求解水力
        self.solver.solve(flows)
        
        return {
            'flows': flows,
            'cost': result.fun if result.success else objective(np.array(list(flows.values()))),
            'power': self.network.get_total_power(),
            'pressure_ok': all(self.network.check_pressure_constraints().values()),
            'success': result.success
        }
    
    def optimize_mpc(
        self,
        demand_forecast: List[Dict[str, float]],
        horizon: int,
        power_cost: float = 0.8
    ) -> List[Dict[str, float]]:
        """
        MPC优化调度
        
        滚动优化未来horizon个时段
        
        Parameters
        ----------
        demand_forecast : List[Dict]
            需水预测序列
        horizon : int
            预测时域
        power_cost : float
            电价
        
        Returns
        -------
        List[Dict]
            各时段最优流量
        """
        n_periods = len(demand_forecast)
        all_flows = []
        
        for t in range(n_periods):
            # 当前时段的需水
            current_demand = demand_forecast[t]
            
            # MPC: 考虑未来horizon个时段（简化为只优化当前时段）
            result = self.optimize_nlp(current_demand, power_cost)
            
            all_flows.append(result['flows'])
        
        return all_flows
