"""
优化调度模块

包含:
1. 日前调度优化（单/多目标）
2. 日内滚动调度
3. 实时调度（AGC）
4. 随机优化
5. 中长期调度

作者: CHS Books
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class PowerSource:
    """电源单元"""
    name: str
    type: str  # 'hydro', 'thermal', 'wind', 'solar', 'storage'
    P_rated: float  # 额定功率 (MW)
    P_min: float  # 最小出力 (MW)
    P_max: float  # 最大出力 (MW)
    ramp_rate: float  # 爬坡速率 (MW/min)
    cost_coef: Tuple[float, float, float] = (0, 0, 0)  # 成本系数 (a, b, c)
    emission_coef: float = 0  # 排放系数 (kg CO2/MWh)


class DayAheadOptimization:
    """
    日前调度优化
    
    目标：最小化总成本
    约束：功率平衡、机组约束
    """
    
    def __init__(
        self,
        sources: List[PowerSource],
        time_horizon: int = 96,  # 15min x 96 = 24h
        dt: float = 0.25,  # 小时
        name: str = "DayAhead"
    ):
        """
        初始化日前优化
        
        Args:
            sources: 电源列表
            time_horizon: 时间步数
            dt: 时间步长 (小时)
        """
        self.name = name
        self.sources = sources
        self.T = time_horizon
        self.dt = dt
    
    def formulate_problem(
        self,
        load_forecast: np.ndarray,
        renewable_forecast: Dict[str, np.ndarray]
    ) -> Dict:
        """
        建立优化问题
        
        Args:
            load_forecast: 负荷预测 [T] (MW)
            renewable_forecast: 新能源预测 {'wind': [T], 'solar': [T]}
            
        Returns:
            优化问题参数
        """
        # 净负荷
        net_load = load_forecast.copy()
        for source_name, forecast in renewable_forecast.items():
            net_load -= forecast
        
        return {
            'net_load': net_load,
            'n_sources': len(self.sources),
            'T': self.T,
        }
    
    def solve_single_objective(
        self,
        net_load: np.ndarray
    ) -> Dict:
        """
        单目标优化：最小化成本
        
        简化求解（启发式）
        
        Args:
            net_load: 净负荷 [T]
            
        Returns:
            调度方案
        """
        T = len(net_load)
        n_sources = len(self.sources)
        
        # 初始化功率分配
        P_schedule = np.zeros((T, n_sources))
        
        # 简化策略：按成本排序分配
        # 按边际成本排序
        thermal_sources = [(i, s) for i, s in enumerate(self.sources) if s.type == 'thermal']
        thermal_sources_sorted = sorted(thermal_sources, key=lambda x: x[1].cost_coef[1])
        
        for t in range(T):
            remaining_load = net_load[t]
            
            # 按成本从低到高分配
            for idx, source in thermal_sources_sorted:
                if remaining_load > 0:
                    P_alloc = min(remaining_load, source.P_max)
                    P_schedule[t, idx] = P_alloc
                    remaining_load -= P_alloc
        
        # 计算成本
        total_cost = 0
        for i, source in enumerate(self.sources):
            a, b, c = source.cost_coef
            for t in range(T):
                P = P_schedule[t, i]
                cost = (a + b * P + c * P**2) * self.dt
                total_cost += cost
        
        return {
            'P_schedule': P_schedule,
            'total_cost': total_cost,
        }


class ModelPredictiveControl:
    """
    模型预测控制（MPC）
    
    用于日内滚动调度
    """
    
    def __init__(
        self,
        prediction_horizon: int = 16,  # 4小时
        control_horizon: int = 4,  # 1小时
        dt: float = 0.25,
        name: str = "MPC"
    ):
        """
        初始化MPC
        
        Args:
            prediction_horizon: 预测时域
            control_horizon: 控制时域
            dt: 时间步长
        """
        self.name = name
        self.Np = prediction_horizon
        self.Nc = control_horizon
        self.dt = dt
    
    def optimize_step(
        self,
        current_state: Dict,
        forecast: np.ndarray,
        reference: np.ndarray
    ) -> np.ndarray:
        """
        单步优化
        
        Args:
            current_state: 当前状态
            forecast: 预测值 [Np]
            reference: 参考轨迹 [Np]
            
        Returns:
            控制序列 [Nc]
        """
        # 简化：二次规划
        # min Σ (P_pred - P_ref)² + λ * Σ ΔP²
        
        # 简化求解：跟踪参考
        control_sequence = reference[:self.Nc] - forecast[:self.Nc]
        
        return control_sequence


class AGCController:
    """
    自动发电控制（AGC）
    
    实时频率调节
    """
    
    def __init__(
        self,
        beta: float = 20.0,  # 频率偏差系数 (MW/0.1Hz)
        Kp: float = 0.5,
        Ki: float = 0.1,
        name: str = "AGC"
    ):
        """
        初始化AGC控制器
        
        Args:
            beta: 频率偏差系数
            Kp, Ki: PI参数
        """
        self.name = name
        self.beta = beta
        self.Kp = Kp
        self.Ki = Ki
        
        self.ACE_integral = 0
    
    def compute_ACE(
        self,
        delta_f: float,  # 频率偏差 (Hz)
        delta_Ptie: float = 0  # 联络线功率偏差 (MW)
    ) -> float:
        """
        计算区域控制偏差（ACE）
        
        ACE = ΔPtie + β * Δf
        
        Args:
            delta_f: 频率偏差
            delta_Ptie: 联络线功率偏差
            
        Returns:
            ACE值
        """
        ACE = delta_Ptie + self.beta * delta_f
        return ACE
    
    def compute_control(
        self,
        delta_f: float,
        delta_Ptie: float,
        dt: float
    ) -> float:
        """
        计算AGC控制指令
        
        Args:
            delta_f: 频率偏差
            delta_Ptie: 联络线偏差
            dt: 时间步长
            
        Returns:
            功率调节指令 (MW)
        """
        ACE = self.compute_ACE(delta_f, delta_Ptie)
        
        # PI控制
        self.ACE_integral += ACE * dt
        
        P_control = -(self.Kp * ACE + self.Ki * self.ACE_integral)
        
        return P_control
    
    def allocate_to_units(
        self,
        P_control: float,
        units_available: List[PowerSource]
    ) -> Dict[str, float]:
        """
        将AGC指令分配给机组
        
        Args:
            P_control: 总控制指令 (MW)
            units_available: 可调节机组列表
            
        Returns:
            各机组分配
        """
        allocation = {}
        
        # 简化：按容量比例分配
        total_capacity = sum(u.P_rated for u in units_available)
        
        for unit in units_available:
            if total_capacity > 0:
                allocation[unit.name] = P_control * (unit.P_rated / total_capacity)
            else:
                allocation[unit.name] = 0
        
        return allocation


class StochasticOptimization:
    """
    随机优化
    
    考虑新能源预测不确定性
    """
    
    def __init__(
        self,
        n_scenarios: int = 100,
        confidence_level: float = 0.95,
        name: str = "StochasticOpt"
    ):
        """
        初始化随机优化
        
        Args:
            n_scenarios: 场景数量
            confidence_level: 置信水平
        """
        self.name = name
        self.n_scenarios = n_scenarios
        self.confidence_level = confidence_level
    
    def generate_scenarios(
        self,
        forecast_mean: np.ndarray,
        forecast_std: np.ndarray
    ) -> np.ndarray:
        """
        生成场景
        
        Args:
            forecast_mean: 预测均值 [T]
            forecast_std: 预测标准差 [T]
            
        Returns:
            场景 [n_scenarios, T]
        """
        T = len(forecast_mean)
        scenarios = np.zeros((self.n_scenarios, T))
        
        for s in range(self.n_scenarios):
            scenarios[s] = np.random.normal(forecast_mean, forecast_std)
            scenarios[s] = np.clip(scenarios[s], 0, None)
        
        return scenarios
    
    def scenario_reduction(
        self,
        scenarios: np.ndarray,
        n_reduced: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        场景削减
        
        Args:
            scenarios: 原始场景 [n, T]
            n_reduced: 削减后场景数
            
        Returns:
            削减后场景, 概率
        """
        # 简化：K-means聚类
        n_scenarios, T = scenarios.shape
        
        # 随机选择代表性场景
        indices = np.random.choice(n_scenarios, n_reduced, replace=False)
        reduced_scenarios = scenarios[indices]
        probabilities = np.ones(n_reduced) / n_reduced
        
        return reduced_scenarios, probabilities
    
    def solve_two_stage(
        self,
        scenarios: np.ndarray,
        probabilities: np.ndarray,
        first_stage_cost_func,
        second_stage_cost_func
    ) -> Dict:
        """
        两阶段随机优化
        
        min E[Cost] = Cost_1st + Σ p_s * Cost_2nd(s)
        
        Args:
            scenarios: 场景
            probabilities: 概率
            first_stage_cost_func: 第一阶段成本函数
            second_stage_cost_func: 第二阶段成本函数
            
        Returns:
            优化结果
        """
        # 简化实现
        expected_cost = 0
        
        # 第一阶段决策（示例）
        first_stage_decision = {'P_schedule': np.zeros(24)}
        first_stage_cost = first_stage_cost_func(first_stage_decision)
        
        # 第二阶段期望成本
        second_stage_cost = 0
        for s, prob in enumerate(probabilities):
            scenario_cost = second_stage_cost_func(scenarios[s], first_stage_decision)
            second_stage_cost += prob * scenario_cost
        
        expected_cost = first_stage_cost + second_stage_cost
        
        return {
            'expected_cost': expected_cost,
            'first_stage_decision': first_stage_decision,
        }


class LongTermOptimization:
    """
    中长期优化
    
    周/月/年调度
    """
    
    def __init__(
        self,
        reservoir_capacity: float = 1000e6,  # m³
        efficiency: float = 0.9,
        name: str = "LongTermOpt"
    ):
        """
        初始化长期优化
        
        Args:
            reservoir_capacity: 水库容量
            efficiency: 水电效率
        """
        self.name = name
        self.V_capacity = reservoir_capacity
        self.efficiency = efficiency
    
    def dynamic_programming(
        self,
        inflow_scenarios: np.ndarray,  # [n_periods]
        load_profile: np.ndarray,
        V_init: float,
        V_target: float
    ) -> Dict:
        """
        动态规划求解
        
        Args:
            inflow_scenarios: 来水场景
            load_profile: 负荷曲线
            V_init: 初始库容
            V_target: 目标库容
            
        Returns:
            优化结果
        """
        T = len(inflow_scenarios)
        
        # 简化DP：离散化状态和决策
        n_states = 10
        V_states = np.linspace(0, self.V_capacity, n_states)
        
        # 价值函数
        V_function = np.zeros((T+1, n_states))
        policy = np.zeros((T, n_states))
        
        # 终端条件
        for i, V in enumerate(V_states):
            V_function[T, i] = -abs(V - V_target) * 1000  # 惩罚偏离
        
        # 倒推
        for t in range(T-1, -1, -1):
            inflow = inflow_scenarios[t]
            for i, V_curr in enumerate(V_states):
                best_value = -np.inf
                best_action = 0
                
                # 尝试不同放水量
                Q_max = min(V_curr / 3600, 1000)  # m³/s
                for Q in np.linspace(0, Q_max, 5):
                    V_next = V_curr + (inflow - Q) * 3600
                    V_next = np.clip(V_next, 0, self.V_capacity)
                    
                    # 发电功率 P = ηρgQH (简化H为常数)
                    P = self.efficiency * 1000 * 9.81 * Q * 50 / 1e6  # MW
                    
                    # 即时收益（满足负荷）
                    revenue = -abs(P - load_profile[t]) * 100
                    
                    # 未来价值（插值）
                    future_value = np.interp(V_next, V_states, V_function[t+1])
                    
                    total_value = revenue + future_value
                    
                    if total_value > best_value:
                        best_value = total_value
                        best_action = Q
                
                V_function[t, i] = best_value
                policy[t, i] = best_action
        
        return {
            'policy': policy,
            'V_function': V_function,
        }


class MultiObjectiveOptimization:
    """
    多目标优化
    
    成本、排放、消纳等多目标
    """
    
    def __init__(self, name: str = "MultiObjective"):
        self.name = name
    
    def weighted_sum_method(
        self,
        objectives: List,
        weights: List[float]
    ) -> float:
        """
        权重法
        
        min Σ w_i * f_i(x)
        
        Args:
            objectives: 目标函数值列表
            weights: 权重
            
        Returns:
            加权和
        """
        return sum(w * f for w, f in zip(weights, objectives))
    
    def epsilon_constraint_method(
        self,
        primary_objective,
        secondary_objectives: List,
        epsilons: List[float]
    ):
        """
        ε-约束法
        
        min f_1(x)
        s.t. f_i(x) ≤ ε_i, i = 2, ..., k
        
        Args:
            primary_objective: 主要目标
            secondary_objectives: 次要目标列表
            epsilons: 约束上限
        """
        # 检查次要目标约束
        feasible = all(f <= eps for f, eps in zip(secondary_objectives, epsilons))
        
        if feasible:
            return primary_objective
        else:
            return np.inf  # 不可行
