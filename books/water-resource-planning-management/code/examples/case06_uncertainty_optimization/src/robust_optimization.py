"""
鲁棒优化

考虑最坏情况的优化方法
"""

import numpy as np
from typing import Dict, Tuple
from scipy.optimize import linprog


class RobustOptimizer:
    """
    鲁棒优化求解器
    
    考虑不确定性集合，求解min-max问题
    """
    
    def __init__(self, base_config: Dict, uncertainty_config: Dict):
        """
        初始化
        
        Parameters
        ----------
        base_config : Dict
            基础配置
        uncertainty_config : Dict
            不确定性配置
        """
        self.base_config = base_config
        self.uncertainty_config = uncertainty_config
        
        self.n_sources = len(base_config['sources'])
        self.n_users = len(base_config['users'])
        
        # 提取参数
        self.benefits = np.array([u['benefit'] for u in base_config['users']])
        self.base_demands = np.array([u['base_demand'] for u in base_config['users']])
        self.base_costs = np.array([s['base_cost'] for s in base_config['sources']])
        self.transport_costs = np.array(base_config['transport_costs'])
    
    def generate_worst_case_scenario(
        self,
        uncertainty_level: float = 1.5
    ) -> Dict:
        """
        生成最坏情况情景
        
        Parameters
        ----------
        uncertainty_level : float
            不确定性水平（标准差的倍数）
        
        Returns
        -------
        Dict
            最坏情况情景
        """
        runoff_config = self.uncertainty_config['runoff_uncertainty']
        
        # 径流：均值 - uncertainty_level × 标准差
        worst_runoff = {}
        for source_id, params in runoff_config.items():
            worst_value = params['mean'] - uncertainty_level * params['std']
            worst_value = max(worst_value, params['min'])
            worst_runoff[source_id] = worst_value
        
        # 需水：最大需水
        demand_scenarios = self.uncertainty_config['demand_scenarios']
        max_multiplier = max([s['multiplier'] for s in demand_scenarios])
        
        return {
            'runoff': worst_runoff,
            'demand_multiplier': max_multiplier
        }
    
    def solve(
        self,
        uncertainty_level: float = 1.5
    ) -> Dict:
        """
        求解鲁棒优化问题
        
        Parameters
        ----------
        uncertainty_level : float
            不确定性水平
        
        Returns
        -------
        Dict
            鲁棒方案
        """
        # 生成最坏情况
        worst_scenario = self.generate_worst_case_scenario(uncertainty_level)
        
        # 构造线性规划（针对最坏情况）
        n_vars = self.n_sources * self.n_users
        
        # 目标函数
        c = []
        for i in range(self.n_sources):
            for j in range(self.n_users):
                net_benefit = self.benefits[j] - self.base_costs[i] - self.transport_costs[i, j]
                c.append(-net_benefit)
        c = np.array(c)
        
        # 约束1：最坏情况的水源容量
        worst_capacities = np.array([
            worst_scenario['runoff']['source_1'],
            worst_scenario['runoff']['source_2'],
            worst_scenario['runoff']['source_3']
        ])
        
        A_ub_cap = np.zeros((self.n_sources, n_vars))
        for i in range(self.n_sources):
            for j in range(self.n_users):
                idx = i * self.n_users + j
                A_ub_cap[i, idx] = 1
        b_ub_cap = worst_capacities
        
        # 约束2：最坏情况的需水
        worst_demands = self.base_demands * worst_scenario['demand_multiplier']
        
        A_ub_dem = np.zeros((self.n_users, n_vars))
        for j in range(self.n_users):
            for i in range(self.n_sources):
                idx = i * self.n_users + j
                A_ub_dem[j, idx] = -1
        b_ub_dem = -worst_demands * 0.85  # 鲁棒方案允许略低的保证率
        
        # 合并约束
        A_ub = np.vstack([A_ub_cap, A_ub_dem])
        b_ub = np.concatenate([b_ub_cap, b_ub_dem])
        
        # 求解
        result = linprog(
            c, A_ub=A_ub, b_ub=b_ub,
            bounds=[(0, None)] * n_vars,
            method='highs'
        )
        
        if result.success:
            return {
                'allocation': result.x,
                'worst_case_value': -result.fun,
                'worst_scenario': worst_scenario
            }
        else:
            return {
                'allocation': np.zeros(n_vars),
                'worst_case_value': 0,
                'worst_scenario': worst_scenario
            }
