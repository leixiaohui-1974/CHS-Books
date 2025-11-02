"""
逐次逼近法 (Progressive Optimality Algorithm, POA)

用于求解梯级水库优化调度问题
"""

import numpy as np
from typing import List, Dict, Tuple
from .reservoir_model import Reservoir, CascadeSystem
from .dynamic_programming import DynamicProgramming


class ProgressiveOptimalityAlgorithm:
    """
    逐次逼近法
    
    将多库问题分解为多个单库子问题，迭代求解
    """
    
    def __init__(
        self,
        cascade_system: CascadeSystem,
        max_iterations: int = 20,
        tolerance: float = 0.001
    ):
        """
        初始化
        
        Parameters
        ----------
        cascade_system : CascadeSystem
            梯级系统
        max_iterations : int
            最大迭代次数
        tolerance : float
            收敛容差
        """
        self.cascade = cascade_system
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        
        # 为每个水库创建DP求解器
        self.dp_solvers = {}
        for res_id, reservoir in cascade_system.reservoirs.items():
            self.dp_solvers[res_id] = DynamicProgramming(
                reservoir,
                n_states=10,
                n_decisions=8
            )
    
    def initialize_solution(
        self,
        inflows: Dict[int, List[float]]
    ) -> Dict[int, List[float]]:
        """
        初始化调度方案（简单策略：出库=入流）
        
        Parameters
        ----------
        inflows : Dict[int, List[float]]
            各水库区间入流
        
        Returns
        -------
        Dict[int, List[float]]
            初始调度方案
        """
        discharges = {}
        for res_id, inflow_series in inflows.items():
            # 简单策略：出库=入流
            discharges[res_id] = inflow_series.copy()
        
        return discharges
    
    def optimize_single_reservoir(
        self,
        reservoir_id: int,
        inflows: Dict[int, List[float]],
        other_discharges: Dict[int, List[float]],
        initial_storages: Dict[int, float]
    ) -> List[float]:
        """
        优化单个水库（固定其他水库）
        
        Parameters
        ----------
        reservoir_id : int
            待优化水库ID
        inflows : Dict[int, List[float]]
            区间入流
        other_discharges : Dict[int, List[float]]
            其他水库的出库流量
        initial_storages : Dict[int, float]
            初始库容
        
        Returns
        -------
        List[float]
            最优出库流量
        """
        # 计算该水库的总入流（区间入流 + 上游来水）
        total_inflows = []
        n_periods = len(inflows[reservoir_id])
        
        for t in range(n_periods):
            total_inflow = inflows[reservoir_id][t]
            
            # 加上上游来水
            for rel in self.cascade.cascade_relations:
                if rel['downstream'] == reservoir_id:
                    upstream_id = rel['upstream']
                    if upstream_id in other_discharges:
                        total_inflow += other_discharges[upstream_id][t]
            
            total_inflows.append(total_inflow)
        
        # 用DP优化该水库
        dp = self.dp_solvers[reservoir_id]
        _, optimal_discharges = dp.backward_recursion(
            total_inflows,
            initial_storages[reservoir_id]
        )
        
        return optimal_discharges
    
    def optimize(
        self,
        inflows: Dict[int, List[float]],
        initial_storages: Dict[int, float],
        verbose: bool = False
    ) -> Tuple[Dict[int, List[float]], List[float]]:
        """
        POA迭代优化
        
        Parameters
        ----------
        inflows : Dict[int, List[float]]
            区间入流
        initial_storages : Dict[int, float]
            初始库容
        verbose : bool
            是否输出进度
        
        Returns
        -------
        Tuple[Dict[int, List[float]], List[float]]
            (最优调度方案, 目标函数历史)
        """
        # 初始化
        discharges = self.initialize_solution(inflows)
        obj_history = []
        
        for iteration in range(self.max_iterations):
            # 计算当前目标函数
            _, total_energy = self.cascade.simulate(
                initial_storages,
                discharges,
                inflows
            )
            obj_history.append(total_energy)
            
            if verbose:
                print(f"迭代 {iteration + 1}: 发电量 = {total_energy:.2f} MWh")
            
            # 收敛判定
            if iteration > 0:
                improvement = abs(obj_history[-1] - obj_history[-2]) / obj_history[-2]
                if improvement < self.tolerance:
                    if verbose:
                        print(f"收敛！改进 < {self.tolerance}")
                    break
            
            # 逐个优化每个水库
            new_discharges = {}
            for res_id in sorted(self.cascade.reservoirs.keys()):
                # 固定其他水库，优化当前水库
                other_discharges = {
                    rid: discharges[rid]
                    for rid in self.cascade.reservoirs
                    if rid != res_id
                }
                
                optimal_discharge = self.optimize_single_reservoir(
                    res_id,
                    inflows,
                    other_discharges,
                    initial_storages
                )
                
                new_discharges[res_id] = optimal_discharge
            
            discharges = new_discharges
        
        return discharges, obj_history
