"""
动态规划算法

用于梯级水库优化调度
"""

import numpy as np
from typing import List, Dict, Tuple
from .reservoir_model import Reservoir, CascadeSystem


class DynamicProgramming:
    """
    动态规划求解器
    
    使用逆序递推求解水库优化调度问题
    """
    
    def __init__(
        self,
        reservoir: Reservoir,
        n_states: int = 10,
        n_decisions: int = 8
    ):
        """
        初始化
        
        Parameters
        ----------
        reservoir : Reservoir
            水库对象
        n_states : int
            状态离散数
        n_decisions : int
            决策离散数
        """
        self.reservoir = reservoir
        self.n_states = n_states
        self.n_decisions = n_decisions
        
        # 离散化状态空间（库容）
        self.states = np.linspace(
            reservoir.level_to_storage(reservoir.dead_level),
            reservoir.max_capacity,
            n_states
        )
        
        # 记录最优值函数和决策
        self.value_function = None
        self.optimal_decisions = None
    
    def discretize_decisions(
        self,
        storage: float,
        inflow: float,
        min_discharge: float = 50,
        max_discharge: float = 3000
    ) -> np.ndarray:
        """
        离散化决策空间（出库流量）
        
        Parameters
        ----------
        storage : float
            当前库容
        inflow : float
            入流
        min_discharge : float
            最小出库流量
        max_discharge : float
            最大出库流量
        
        Returns
        -------
        np.ndarray
            可行的出库流量决策
        """
        # 考虑水量平衡约束
        # 最大出库：不能使库容降到死水位以下
        max_possible = (storage - self.states[0]) * 1e8 / 864000 + inflow
        max_possible = min(max_possible, max_discharge)
        
        # 最小出库：不能使库容超过最大库容
        min_possible = max(min_discharge, 0)
        
        if max_possible < min_possible:
            return np.array([inflow])
        
        return np.linspace(min_possible, max_possible, self.n_decisions)
    
    def backward_recursion(
        self,
        inflows: List[float],
        initial_storage: float,
        delta_t: float = 864000
    ) -> Tuple[float, List[float]]:
        """
        逆序递推
        
        Parameters
        ----------
        inflows : List[float]
            各时段入流
        initial_storage : float
            初始库容
        delta_t : float
            时段长度 (秒)
        
        Returns
        -------
        Tuple[float, List[float]]
            (最大发电量, 最优出库流量序列)
        """
        n_periods = len(inflows)
        
        # 初始化值函数和决策表
        self.value_function = np.zeros((n_periods + 1, self.n_states))
        self.optimal_decisions = np.zeros((n_periods, self.n_states))
        
        # 逆序递推
        for t in range(n_periods - 1, -1, -1):
            inflow = inflows[t]
            
            for i, storage in enumerate(self.states):
                # 可行决策
                decisions = self.discretize_decisions(storage, inflow)
                
                max_value = -np.inf
                best_decision = decisions[0]
                
                for discharge in decisions:
                    # 状态转移
                    next_storage = self.reservoir.water_balance(
                        storage, inflow, discharge, delta_t
                    )
                    
                    # 当前阶段收益（发电量）
                    power = self.reservoir.calculate_power(
                        storage, discharge, next_storage
                    )
                    immediate_reward = power * delta_t / 3600  # MWh
                    
                    # 下一阶段值函数（插值）
                    future_value = np.interp(
                        next_storage,
                        self.states,
                        self.value_function[t + 1, :]
                    )
                    
                    # 总价值
                    total_value = immediate_reward + future_value
                    
                    if total_value > max_value:
                        max_value = total_value
                        best_decision = discharge
                
                self.value_function[t, i] = max_value
                self.optimal_decisions[t, i] = best_decision
        
        # 前向追溯最优策略
        optimal_discharges = []
        current_storage = initial_storage
        
        for t in range(n_periods):
            # 插值找到最优决策
            optimal_discharge = np.interp(
                current_storage,
                self.states,
                self.optimal_decisions[t, :]
            )
            optimal_discharges.append(optimal_discharge)
            
            # 状态转移
            current_storage = self.reservoir.water_balance(
                current_storage,
                inflows[t],
                optimal_discharge,
                delta_t
            )
        
        # 计算最大发电量
        max_energy = np.interp(
            initial_storage,
            self.states,
            self.value_function[0, :]
        )
        
        return max_energy, optimal_discharges
