"""
两阶段随机规划

实现样本平均近似（SAA）方法
"""

import numpy as np
from typing import List, Tuple, Dict
from scipy.optimize import linprog


def generate_scenarios(
    config: Dict,
    n_samples: int = 1000,
    seed: int = 42
) -> List[Dict]:
    """
    生成不确定性情景
    
    Parameters
    ----------
    config : Dict
        不确定性参数配置
    n_samples : int
        采样数量
    seed : int
        随机种子
    
    Returns
    -------
    List[Dict]
        情景列表
    """
    np.random.seed(seed)
    scenarios = []
    
    runoff_config = config['runoff_uncertainty']
    demand_scenarios = config['demand_scenarios']
    
    for i in range(n_samples):
        scenario = {'id': i}
        
        # 径流采样（正态分布）
        scenario['runoff'] = {}
        for source_id, params in runoff_config.items():
            if params['std'] > 0:
                value = np.random.normal(params['mean'], params['std'])
                value = np.clip(value, params['min'], params['max'])
            else:
                value = params['mean']
            scenario['runoff'][source_id] = value
        
        # 需水采样（离散分布）
        probs = [s['probability'] for s in demand_scenarios]
        idx = np.random.choice(len(demand_scenarios), p=probs)
        scenario['demand_multiplier'] = demand_scenarios[idx]['multiplier']
        scenario['demand_scenario'] = demand_scenarios[idx]['name']
        
        # 概率（假设均等）
        scenario['probability'] = 1.0 / n_samples
        
        scenarios.append(scenario)
    
    return scenarios


class TwoStageSP:
    """
    两阶段随机规划求解器
    
    第一阶段：确定配置容量
    第二阶段：根据实际情况调度
    """
    
    def __init__(self, base_config: Dict):
        """
        初始化
        
        Parameters
        ----------
        base_config : Dict
            基础配置参数
        """
        self.config = base_config
        self.n_sources = len(base_config['sources'])
        self.n_users = len(base_config['users'])
        
        # 提取基础参数
        self.benefits = np.array([u['benefit'] for u in base_config['users']])
        self.base_demands = np.array([u['base_demand'] for u in base_config['users']])
        self.base_costs = np.array([s['base_cost'] for s in base_config['sources']])
        self.transport_costs = np.array(base_config['transport_costs'])
    
    def solve_first_stage(
        self,
        scenarios: List[Dict],
        capacity_cost: float = 10.0
    ) -> np.ndarray:
        """
        求解第一阶段（简化：固定容量）
        
        Parameters
        ----------
        scenarios : List[Dict]
            情景列表
        capacity_cost : float
            容量建设成本
        
        Returns
        -------
        np.ndarray
            配置容量
        """
        # 简化：使用平均径流作为容量
        avg_runoff = {}
        for source_key in scenarios[0]['runoff'].keys():
            avg_runoff[source_key] = np.mean([s['runoff'][source_key] for s in scenarios])
        
        capacities = np.array([
            avg_runoff['source_1'],
            avg_runoff['source_2'],
            avg_runoff['source_3']
        ])
        
        return capacities
    
    def solve_second_stage(
        self,
        capacities: np.ndarray,
        scenario: Dict
    ) -> Tuple[np.ndarray, float]:
        """
        求解第二阶段（实际调度）
        
        Parameters
        ----------
        capacities : np.ndarray
            第一阶段确定的容量
        scenario : Dict
            具体情景
        
        Returns
        -------
        Tuple[np.ndarray, float]
            (配水方案, 目标值)
        """
        # 构造线性规划
        n_vars = self.n_sources * self.n_users
        
        # 目标函数：最大化净效益
        c = []
        for i in range(self.n_sources):
            for j in range(self.n_users):
                net_benefit = self.benefits[j] - self.base_costs[i] - self.transport_costs[i, j]
                c.append(-net_benefit)  # 转为最小化
        c = np.array(c)
        
        # 约束1：水源容量（考虑实际径流）
        actual_capacities = np.array([
            scenario['runoff']['source_1'],
            scenario['runoff']['source_2'],
            scenario['runoff']['source_3']
        ])
        # 不超过设计容量和实际径流的较小值
        effective_capacities = np.minimum(capacities, actual_capacities)
        
        A_ub_cap = np.zeros((self.n_sources, n_vars))
        for i in range(self.n_sources):
            for j in range(self.n_users):
                idx = i * self.n_users + j
                A_ub_cap[i, idx] = 1
        b_ub_cap = effective_capacities
        
        # 约束2：需水满足（考虑实际需水）
        actual_demands = self.base_demands * scenario['demand_multiplier']
        
        A_ub_dem = np.zeros((self.n_users, n_vars))
        for j in range(self.n_users):
            for i in range(self.n_sources):
                idx = i * self.n_users + j
                A_ub_dem[j, idx] = -1
        b_ub_dem = -actual_demands * 0.9  # 至少满足90%
        
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
            return result.x, -result.fun
        else:
            return np.zeros(n_vars), 0
    
    def solve(
        self,
        scenarios: List[Dict]
    ) -> Dict:
        """
        求解两阶段随机规划
        
        Parameters
        ----------
        scenarios : List[Dict]
            情景列表
        
        Returns
        -------
        Dict
            求解结果
        """
        # 第一阶段：确定容量
        capacities = self.solve_first_stage(scenarios)
        
        # 第二阶段：对所有情景求解
        scenario_results = []
        total_expected_value = 0
        
        for scenario in scenarios:
            allocation, value = self.solve_second_stage(capacities, scenario)
            
            scenario_results.append({
                'scenario_id': scenario['id'],
                'allocation': allocation,
                'value': value,
                'probability': scenario['probability']
            })
            
            total_expected_value += scenario['probability'] * value
        
        return {
            'capacities': capacities,
            'expected_value': total_expected_value,
            'scenario_results': scenario_results
        }
