"""
鲁棒优化

在不确定性下的优化决策
"""

import numpy as np
from typing import Callable, Dict, List, Optional, Tuple
from scipy.optimize import minimize, linprog


class RobustOptimizer:
    """
    鲁棒优化器
    """
    
    def __init__(self, objective: Callable, constraints: Optional[List] = None):
        """
        初始化鲁棒优化器
        
        Parameters
        ----------
        objective : Callable
            目标函数
        constraints : List, optional
            约束列表
        """
        self.objective = objective
        self.constraints = constraints or []
        
        self.solution = None
        self.worst_case_scenarios = []
    
    def optimize_worst_case(
        self,
        scenarios: List[Dict],
        x0: np.ndarray,
        bounds: Optional[List[Tuple]] = None
    ) -> Dict:
        """
        最坏情景优化（Min-Max）
        
        min_x max_s f(x, s)
        
        Parameters
        ----------
        scenarios : List[Dict]
            情景列表
        x0 : np.ndarray
            初始解
        bounds : List[Tuple], optional
            变量边界
        
        Returns
        -------
        Dict
            优化结果
        """
        def worst_case_objective(x):
            # 评估所有情景，取最差
            values = []
            for scenario in scenarios:
                val = self.objective(x, **scenario)
                values.append(val)
            
            return max(values)  # 最坏情景
        
        # 优化
        result = minimize(
            worst_case_objective,
            x0,
            bounds=bounds,
            constraints=self.constraints
        )
        
        self.solution = result.x
        
        return {
            'x': result.x,
            'worst_case_value': result.fun,
            'success': result.success,
            'message': result.message
        }
    
    def optimize_regret(
        self,
        scenarios: List[Dict],
        probabilities: List[float],
        x0: np.ndarray,
        bounds: Optional[List[Tuple]] = None
    ) -> Dict:
        """
        后悔值优化（Min-Max Regret）
        
        min_x max_s [f(x, s) - f^*(s)]
        
        其中f^*(s)是情景s下的最优值
        
        Parameters
        ----------
        scenarios : List[Dict]
            情景列表
        probabilities : List[float]
            情景概率
        x0 : np.ndarray
            初始解
        bounds : List[Tuple], optional
            变量边界
        
        Returns
        -------
        Dict
            优化结果
        """
        # 先计算每个情景的最优值
        optimal_values = []
        for scenario in scenarios:
            def scenario_objective(x):
                return self.objective(x, **scenario)
            
            result = minimize(
                scenario_objective,
                x0,
                bounds=bounds,
                constraints=self.constraints
            )
            optimal_values.append(result.fun)
        
        # 定义后悔值目标
        def regret_objective(x):
            regrets = []
            for i, scenario in enumerate(scenarios):
                val = self.objective(x, **scenario)
                regret = val - optimal_values[i]
                regrets.append(regret)
            
            return max(regrets)  # 最大后悔
        
        # 优化
        result = minimize(
            regret_objective,
            x0,
            bounds=bounds,
            constraints=self.constraints
        )
        
        return {
            'x': result.x,
            'max_regret': result.fun,
            'optimal_values': optimal_values,
            'success': result.success
        }
    
    def optimize_weighted(
        self,
        scenarios: List[Dict],
        probabilities: List[float],
        risk_aversion: float,
        x0: np.ndarray,
        bounds: Optional[List[Tuple]] = None
    ) -> Dict:
        """
        加权鲁棒优化
        
        min_x α*E[f(x,s)] + (1-α)*max_s f(x,s)
        
        Parameters
        ----------
        scenarios : List[Dict]
            情景列表
        probabilities : List[float]
            情景概率
        risk_aversion : float
            风险厌恶系数 [0, 1]
            0: 只考虑期望（风险中性）
            1: 只考虑最坏（完全风险厌恶）
        x0 : np.ndarray
            初始解
        bounds : List[Tuple], optional
            变量边界
        
        Returns
        -------
        Dict
            优化结果
        """
        def weighted_objective(x):
            values = []
            for i, scenario in enumerate(scenarios):
                val = self.objective(x, **scenario)
                values.append((val, probabilities[i]))
            
            # 期望值
            expected = sum(v * p for v, p in values)
            
            # 最坏情景
            worst = max(v for v, _ in values)
            
            # 加权组合
            return (1 - risk_aversion) * expected + risk_aversion * worst
        
        result = minimize(
            weighted_objective,
            x0,
            bounds=bounds,
            constraints=self.constraints
        )
        
        return {
            'x': result.x,
            'weighted_value': result.fun,
            'risk_aversion': risk_aversion,
            'success': result.success
        }
    
    def optimize_cvar(
        self,
        scenarios: List[Dict],
        probabilities: List[float],
        alpha: float,
        x0: np.ndarray,
        bounds: Optional[List[Tuple]] = None
    ) -> Dict:
        """
        CVaR优化
        
        min_x CVaR_α[f(x,s)]
        
        Parameters
        ----------
        scenarios : List[Dict]
            情景列表
        probabilities : List[float]
            情景概率
        alpha : float
            置信水平（如0.95）
        x0 : np.ndarray
            初始解
        bounds : List[Tuple], optional
            变量边界
        
        Returns
        -------
        Dict
            优化结果
        """
        # 使用近似方法：VaR + 期望超过部分
        def cvar_objective(x):
            values = []
            for i, scenario in enumerate(scenarios):
                val = self.objective(x, **scenario)
                values.append((val, probabilities[i]))
            
            # 排序
            sorted_values = sorted(values, key=lambda x: x[0], reverse=True)
            
            # 计算VaR
            cumulative_prob = 0
            var_index = 0
            for i, (val, prob) in enumerate(sorted_values):
                cumulative_prob += prob
                if cumulative_prob >= (1 - alpha):
                    var_index = i
                    break
            
            # CVaR：VaR + 尾部期望
            var = sorted_values[var_index][0]
            tail_values = sorted_values[:var_index+1]
            
            if len(tail_values) == 0:
                cvar = var
            else:
                tail_prob = sum(p for _, p in tail_values)
                if tail_prob > 0:
                    cvar = sum(v * p for v, p in tail_values) / tail_prob
                else:
                    cvar = var
            
            return cvar
        
        result = minimize(
            cvar_objective,
            x0,
            bounds=bounds,
            constraints=self.constraints
        )
        
        return {
            'x': result.x,
            'cvar': result.fun,
            'alpha': alpha,
            'success': result.success
        }
