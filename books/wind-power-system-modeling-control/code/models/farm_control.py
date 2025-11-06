"""
风电场协调控制模块

包含:
1. 有功功率控制
2. 无功电压控制
3. 负荷分配
4. 风储联合控制
5. 尾流优化控制
6. 虚拟惯量控制

作者: CHS Books
"""

import numpy as np
from typing import Dict, List, Tuple
from .control import PIDController


class ActivePowerController:
    """
    风电场有功功率控制
    
    集中控制器，将场级功率指令分配给各机组
    """
    
    def __init__(
        self,
        n_turbines: int,
        P_rated_total: float = 100e6,
        Kp: float = 0.1,
        Ki: float = 1.0,
        name: str = "Farm_P_Control"
    ):
        """
        初始化有功功率控制器
        
        Args:
            n_turbines: 机组数量
            P_rated_total: 总额定功率
            Kp, Ki: PI参数
        """
        self.name = name
        self.n_turbines = n_turbines
        self.P_rated_total = P_rated_total
        
        # PI控制器
        self.pi = PIDController(Kp=Kp, Ki=Ki, Kd=0)
    
    def proportional_dispatch(
        self,
        P_ref_total: float,
        P_available: List[float]
    ) -> List[float]:
        """
        比例分配策略
        
        Args:
            P_ref_total: 场级功率指令
            P_available: 各机组可用功率
            
        Returns:
            各机组功率指令
        """
        P_available_total = sum(P_available)
        
        if P_available_total == 0:
            return [0] * self.n_turbines
        
        # 比例分配
        ratio = min(1.0, P_ref_total / P_available_total)
        P_refs = [P_avail * ratio for P_avail in P_available]
        
        return P_refs
    
    def optimal_dispatch(
        self,
        P_ref_total: float,
        efficiencies: List[float],
        P_max: List[float]
    ) -> List[float]:
        """
        最优分配策略（等微增率法）
        
        Args:
            P_ref_total: 场级功率指令
            efficiencies: 各机组效率
            P_max: 各机组最大功率
            
        Returns:
            各机组功率指令
        """
        # 简化：按效率加权分配
        eff_sum = sum(efficiencies)
        if eff_sum == 0:
            return [0] * self.n_turbines
        
        P_refs = []
        for eff, P_m in zip(efficiencies, P_max):
            P_i = P_ref_total * (eff / eff_sum)
            P_refs.append(min(P_i, P_m))
        
        return P_refs


class ReactivePowerController:
    """
    风电场无功电压控制
    
    维持并网点电压稳定
    """
    
    def __init__(
        self,
        V_ref: float = 1.0,
        Kp: float = 100.0,
        Ki: float = 10.0,
        Q_max: float = 50e6,
        name: str = "Farm_Q_Control"
    ):
        """
        初始化无功电压控制器
        
        Args:
            V_ref: 参考电压（pu）
            Kp, Ki: PI参数
            Q_max: 最大无功功率
        """
        self.name = name
        self.V_ref = V_ref
        self.Q_max = Q_max
        
        # PI控制器
        self.pi = PIDController(Kp=Kp, Ki=Ki, Kd=0, output_limits=(-Q_max, Q_max))
    
    def compute_Q_ref(self, V_pcc: float, dt: float) -> float:
        """
        计算场级无功功率指令
        
        Args:
            V_pcc: 并网点电压（pu）
            dt: 时间步长
            
        Returns:
            无功功率指令
        """
        Q_ref = self.pi.compute(self.V_ref, V_pcc, dt)
        return Q_ref
    
    def distribute_Q(
        self,
        Q_ref_total: float,
        Q_capacities: List[float]
    ) -> List[float]:
        """
        无功功率分配
        
        Args:
            Q_ref_total: 场级无功指令
            Q_capacities: 各机组无功容量
            
        Returns:
            各机组无功指令
        """
        Q_cap_total = sum(Q_capacities)
        if Q_cap_total == 0:
            return [0] * len(Q_capacities)
        
        # 按容量比例分配
        Q_refs = [Q_ref_total * (Q_cap / Q_cap_total) for Q_cap in Q_capacities]
        
        return Q_refs


class WindStorageCoordination:
    """
    风储联合控制
    
    协调风电和储能，平抑功率波动
    """
    
    def __init__(
        self,
        P_wind_rated: float = 100e6,
        P_storage_rated: float = 20e6,
        E_storage_capacity: float = 40e6,  # Wh
        SOC_min: float = 0.2,
        SOC_max: float = 0.9,
        name: str = "WindStorage"
    ):
        """
        初始化风储协调控制器
        
        Args:
            P_wind_rated: 风电额定功率
            P_storage_rated: 储能额定功率
            E_storage_capacity: 储能容量
            SOC_min, SOC_max: SOC限制
        """
        self.name = name
        self.P_wind_rated = P_wind_rated
        self.P_storage_rated = P_storage_rated
        self.E_storage_capacity = E_storage_capacity
        self.SOC_min = SOC_min
        self.SOC_max = SOC_max
        
        # SOC状态
        self.SOC = 0.5
    
    def power_smoothing(
        self,
        P_wind: float,
        P_ref: float,
        dt: float
    ) -> Dict:
        """
        功率平滑控制
        
        Args:
            P_wind: 风电实际功率
            P_ref: 并网功率指令
            dt: 时间步长
            
        Returns:
            控制结果
        """
        # 功率差值由储能补偿
        P_diff = P_ref - P_wind
        
        # 储能功率限制
        P_storage_max = min(self.P_storage_rated, 
                           (self.SOC_max - self.SOC) * self.E_storage_capacity / dt)
        P_storage_min = max(-self.P_storage_rated,
                           (self.SOC_min - self.SOC) * self.E_storage_capacity / dt)
        
        P_storage = np.clip(P_diff, P_storage_min, P_storage_max)
        
        # 更新SOC
        self.SOC += P_storage * dt / self.E_storage_capacity
        self.SOC = np.clip(self.SOC, 0, 1)
        
        # 实际并网功率
        P_grid = P_wind + P_storage
        
        return {
            'P_wind': P_wind,
            'P_storage': P_storage,
            'P_grid': P_grid,
            'SOC': self.SOC,
        }


class WakeOptimization:
    """
    尾流优化控制
    
    通过调整上游机组功率，优化场级总功率
    """
    
    def __init__(
        self,
        n_turbines: int,
        wake_matrix: np.ndarray = None,
        name: str = "WakeOpt"
    ):
        """
        初始化尾流优化控制器
        
        Args:
            n_turbines: 机组数量
            wake_matrix: 尾流影响矩阵 [n x n]
        """
        self.name = name
        self.n_turbines = n_turbines
        
        # 尾流影响矩阵（简化）
        if wake_matrix is None:
            self.wake_matrix = np.eye(n_turbines)
            for i in range(n_turbines - 1):
                self.wake_matrix[i+1, i] = 0.8  # 下游机组受上游影响
        else:
            self.wake_matrix = wake_matrix
    
    def optimize_setpoints(
        self,
        v_winds: List[float],
        derating_factors: List[float] = None
    ) -> List[float]:
        """
        优化各机组工作点
        
        Args:
            v_winds: 各机组风速
            derating_factors: 降额系数（0-1）
            
        Returns:
            各机组功率指令
        """
        if derating_factors is None:
            derating_factors = [1.0] * self.n_turbines
        
        # 简化优化：贪心算法
        P_refs = []
        for i in range(self.n_turbines):
            # 考虑上游影响
            v_eff = v_winds[i]
            for j in range(i):
                if self.wake_matrix[i, j] < 1.0:
                    v_eff *= self.wake_matrix[i, j]
            
            # 功率计算（简化）
            P_i = 0.5 * 1.225 * np.pi * 40**2 * v_eff**3 * 0.4 * derating_factors[i]
            P_refs.append(P_i)
        
        return P_refs


class VirtualInertiaController:
    """
    虚拟惯量控制
    
    模拟同步机惯量响应，提供频率支撑
    """
    
    def __init__(
        self,
        H_virtual: float = 5.0,
        K_droop: float = 20.0,
        df_deadband: float = 0.01,
        name: str = "VirtualInertia"
    ):
        """
        初始化虚拟惯量控制器
        
        Args:
            H_virtual: 虚拟惯量常数（秒）
            K_droop: 下垂系数（MW/Hz）
            df_deadband: 频率死区（Hz）
        """
        self.name = name
        self.H_virtual = H_virtual
        self.K_droop = K_droop
        self.df_deadband = df_deadband
        
        # 状态变量
        self.f_prev = 50.0
    
    def compute_inertia_response(
        self,
        f_grid: float,
        f_nom: float,
        P_base: float,
        dt: float
    ) -> Dict:
        """
        计算惯量响应功率
        
        Args:
            f_grid: 电网频率（Hz）
            f_nom: 额定频率（Hz）
            P_base: 基准功率（W）
            dt: 时间步长
            
        Returns:
            控制结果
        """
        # 频率偏差
        df = f_grid - f_nom
        
        # 频率变化率
        df_dt = (f_grid - self.f_prev) / dt if dt > 0 else 0
        self.f_prev = f_grid
        
        # 惯量响应（模拟 dP/dt = -2H * df/dt）
        if abs(df) > self.df_deadband:
            P_inertia = -2 * self.H_virtual * P_base * df_dt / f_nom
            
            # 下垂响应
            P_droop = -self.K_droop * df * 1e6  # Hz → W
            
            # 总附加功率
            P_additional = P_inertia + P_droop
        else:
            P_additional = 0
            P_inertia = 0
            P_droop = 0
        
        return {
            'P_additional': P_additional,
            'P_inertia': P_inertia,
            'P_droop': P_droop,
            'df': df,
            'df_dt': df_dt,
        }


class FarmCentralController:
    """
    风电场集中控制器
    
    综合协调有功、无功、储能等子系统
    """
    
    def __init__(
        self,
        n_turbines: int,
        P_rated_total: float = 100e6,
        with_storage: bool = False,
        name: str = "FarmCentral"
    ):
        """
        初始化集中控制器
        
        Args:
            n_turbines: 机组数量
            P_rated_total: 总额定功率
            with_storage: 是否含储能
        """
        self.name = name
        self.n_turbines = n_turbines
        self.P_rated_total = P_rated_total
        self.with_storage = with_storage
        
        # 子控制器
        self.P_ctrl = ActivePowerController(n_turbines, P_rated_total)
        self.Q_ctrl = ReactivePowerController()
        
        if with_storage:
            self.storage_ctrl = WindStorageCoordination(P_wind_rated=P_rated_total)
    
    def coordinate_control(
        self,
        P_ref_total: float,
        V_pcc: float,
        P_turbines: List[float],
        dt: float
    ) -> Dict:
        """
        协调控制
        
        Args:
            P_ref_total: 场级功率指令
            V_pcc: 并网点电压
            P_turbines: 各机组功率
            dt: 时间步长
            
        Returns:
            控制结果
        """
        # 有功功率分配
        P_refs = self.P_ctrl.proportional_dispatch(P_ref_total, P_turbines)
        
        # 无功电压控制
        Q_ref_total = self.Q_ctrl.compute_Q_ref(V_pcc, dt)
        Q_capacities = [10e6] * self.n_turbines  # 简化
        Q_refs = self.Q_ctrl.distribute_Q(Q_ref_total, Q_capacities)
        
        # 储能协调（如果有）
        if self.with_storage:
            P_wind_total = sum(P_turbines)
            storage_result = self.storage_ctrl.power_smoothing(P_wind_total, P_ref_total, dt)
        else:
            storage_result = None
        
        return {
            'P_refs': P_refs,
            'Q_refs': Q_refs,
            'Q_ref_total': Q_ref_total,
            'storage': storage_result,
        }
