"""
电网支撑与辅助服务模块

包含:
1. 一次调频
2. 二次调频（AGC）
3. 无功电压控制
4. 黑启动
5. 惯量支撑

作者: CHS Books
"""

import numpy as np
from typing import Dict, List


class PrimaryFrequencyControl:
    """
    一次调频
    
    频率下降 → 自动增加出力
    """
    
    def __init__(
        self,
        droop: float = 0.05,  # 5% droop
        deadband: float = 0.05,  # ±0.05 Hz
        P_rated: float = 100,  # MW
        name: str = "PrimaryFreqControl"
    ):
        """
        初始化一次调频
        
        Args:
            droop: 下垂系数
            deadband: 死区
            P_rated: 额定功率
        """
        self.name = name
        self.droop = droop
        self.deadband = deadband
        self.P_rated = P_rated
    
    def compute_response(
        self,
        delta_f: float,  # 频率偏差 (Hz)
        f_rated: float = 50.0  # 额定频率 (Hz)
    ) -> float:
        """
        计算一次调频响应
        
        ΔP = -(1/R) * (Δf / f_rated) * P_rated
        
        Args:
            delta_f: 频率偏差
            f_rated: 额定频率
            
        Returns:
            功率增量 (MW)
        """
        # 死区
        if abs(delta_f) < self.deadband:
            return 0
        
        # 下垂控制
        delta_P = -(1 / self.droop) * (delta_f / f_rated) * self.P_rated
        
        # 限幅
        delta_P = np.clip(delta_P, -self.P_rated * 0.1, self.P_rated * 0.1)
        
        return delta_P


class SecondaryFrequencyControl:
    """
    二次调频（AGC）
    
    ACE = ΔPtie + β * Δf
    """
    
    def __init__(
        self,
        beta: float = 20.0,  # MW/0.1Hz
        Kp: float = 0.5,
        Ki: float = 0.1,
        name: str = "AGC"
    ):
        """
        初始化AGC
        
        Args:
            beta: 频率偏差系数
            Kp, Ki: PI控制参数
        """
        self.name = name
        self.beta = beta
        self.Kp = Kp
        self.Ki = Ki
        
        self.ACE_integral = 0
    
    def compute_ACE(
        self,
        delta_f: float,
        delta_Ptie: float
    ) -> float:
        """
        计算区域控制偏差
        
        ACE = ΔPtie + β * Δf
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
            delta_f: 频率偏差 (Hz)
            delta_Ptie: 联络线偏差 (MW)
            dt: 时间步长 (s)
            
        Returns:
            控制指令 (MW)
        """
        ACE = self.compute_ACE(delta_f, delta_Ptie)
        
        # PI控制
        self.ACE_integral += ACE * dt
        
        P_agc = -(self.Kp * ACE + self.Ki * self.ACE_integral)
        
        return P_agc
    
    def evaluate_CPS(
        self,
        ACE_series: np.ndarray,
        epsilon: float = 0.0002  # 控制性能标准
    ) -> float:
        """
        评估CPS1（控制性能标准1）
        
        CPS1 = (2 - CF) × 100%
        CF = AVG[(ACE/10)² / ε²]
        
        Args:
            ACE_series: ACE时间序列
            epsilon: 标准参数
            
        Returns:
            CPS1 (%)
        """
        CF = np.mean((ACE_series / 10)**2) / epsilon**2
        CPS1 = (2 - CF) * 100
        CPS1 = np.clip(CPS1, 0, 200)
        
        return CPS1


class ReactiveVoltageControl:
    """
    无功电压控制
    """
    
    def __init__(
        self,
        V_rated: float = 10.5,  # kV
        Q_max: float = 50,  # Mvar
        Kq: float = 2.0,
        name: str = "VoltageControl"
    ):
        """
        初始化无功电压控制
        
        Args:
            V_rated: 额定电压
            Q_max: 最大无功容量
            Kq: 控制增益
        """
        self.name = name
        self.V_rated = V_rated
        self.Q_max = Q_max
        self.Kq = Kq
    
    def compute_reactive_power(
        self,
        V_actual: float,  # 实际电压 (kV)
        V_ref: float = None  # 参考电压 (kV)
    ) -> float:
        """
        计算无功功率指令
        
        Q = Kq * (V_ref - V_actual)
        
        Args:
            V_actual: 实际电压
            V_ref: 参考电压（None则使用额定值）
            
        Returns:
            无功功率 (Mvar)
        """
        if V_ref is None:
            V_ref = self.V_rated
        
        delta_V = V_ref - V_actual
        Q = self.Kq * delta_V
        
        Q = np.clip(Q, -self.Q_max, self.Q_max)
        
        return Q
    
    def voltage_stability_index(
        self,
        V: float,
        V_min: float = 0.95,
        V_max: float = 1.05
    ) -> float:
        """
        电压稳定性指标
        
        Args:
            V: 电压标幺值
            V_min, V_max: 电压限制
            
        Returns:
            稳定性指标 [0, 1]
        """
        if V < V_min:
            index = (V - V_min) / V_min + 1
        elif V > V_max:
            index = (V_max - V) / (V - V_max) + 1
        else:
            index = 1.0
        
        index = np.clip(index, 0, 1)
        
        return index


class BlackStartController:
    """
    黑启动控制
    
    系统停电后的恢复启动
    """
    
    def __init__(self, name: str = "BlackStart"):
        self.name = name
        self.stage = 0
    
    def plan_sequence(
        self,
        units_available: List[Dict]
    ) -> List[Dict]:
        """
        规划黑启动序列
        
        Args:
            units_available: 可用机组列表
            
        Returns:
            启动序列
        """
        sequence = []
        
        # 第1步：启动黑启动电源（水电、燃气）
        for unit in units_available:
            if unit['type'] in ['hydro', 'gas']:
                sequence.append({
                    'step': 1,
                    'unit': unit['name'],
                    'action': 'start',
                    'duration': 0.5,  # hours
                })
        
        # 第2步：逐步启动火电机组
        thermal_units = [u for u in units_available if u['type'] == 'thermal']
        for i, unit in enumerate(thermal_units):
            sequence.append({
                'step': 2 + i,
                'unit': unit['name'],
                'action': 'start',
                'duration': unit.get('startup_time', 4),
            })
        
        # 第3步：带负荷
        sequence.append({
            'step': len(sequence) + 1,
            'action': 'load',
            'duration': 1,
        })
        
        return sequence
    
    def voltage_ramp(
        self,
        t: float,
        V_target: float = 1.0,
        ramp_rate: float = 0.1  # pu/s
    ) -> float:
        """
        电压爬坡
        
        Args:
            t: 时间 (s)
            V_target: 目标电压 (pu)
            ramp_rate: 爬坡速率
            
        Returns:
            电压设定值 (pu)
        """
        V_setpoint = min(ramp_rate * t, V_target)
        return V_setpoint
    
    def frequency_ramp(
        self,
        t: float,
        f_target: float = 50.0,
        ramp_rate: float = 0.5  # Hz/s
    ) -> float:
        """
        频率爬坡
        
        Args:
            t: 时间 (s)
            f_target: 目标频率 (Hz)
            ramp_rate: 爬坡速率
            
        Returns:
            频率设定值 (Hz)
        """
        f_setpoint = min(ramp_rate * t, f_target)
        return f_setpoint


class VirtualInertiaControl:
    """
    惯量支撑（VSG）
    
    提供虚拟惯量以稳定频率
    """
    
    def __init__(
        self,
        J_virtual: float = 10.0,  # 虚拟转动惯量 (kg·m²)
        D_damping: float = 100.0,  # 阻尼系数
        P_rated: float = 50,  # MW
        name: str = "VSG"
    ):
        """
        初始化VSG
        
        Args:
            J_virtual: 虚拟惯量
            D_damping: 阻尼系数
            P_rated: 额定功率
        """
        self.name = name
        self.J = J_virtual
        self.D = D_damping
        self.P_rated = P_rated
        
        self.omega = 2 * np.pi * 50  # 额定角频率 (rad/s)
    
    def compute_inertia_response(
        self,
        df_dt: float,  # 频率变化率 (Hz/s)
        delta_f: float  # 频率偏差 (Hz)
    ) -> float:
        """
        计算惯量响应
        
        P = -J * (dω/dt) - D * Δω
          = -J * 2π * (df/dt) - D * 2π * Δf
        
        Args:
            df_dt: 频率变化率
            delta_f: 频率偏差
            
        Returns:
            功率响应 (MW)
        """
        d_omega_dt = 2 * np.pi * df_dt
        delta_omega = 2 * np.pi * delta_f
        
        P_inertia = -self.J * d_omega_dt - self.D * delta_omega
        
        # 转换为MW并限幅
        P_inertia = P_inertia / 1e6
        P_inertia = np.clip(P_inertia, -self.P_rated * 0.2, self.P_rated * 0.2)
        
        return P_inertia
    
    def frequency_nadir_improvement(
        self,
        P_disturbance: float,  # 扰动功率 (MW)
        H_system: float = 5.0,  # 系统惯量常数 (s)
        S_base: float = 1000  # 基准容量 (MVA)
    ) -> Dict:
        """
        评估频率最低点改善效果
        
        Args:
            P_disturbance: 扰动功率
            H_system: 系统惯量常数
            S_base: 基准容量
            
        Returns:
            评估结果
        """
        # 无VSG时的频率最低点
        f_nadir_without = -P_disturbance / (2 * H_system * S_base / 50)
        
        # 有VSG时（简化）
        H_total = H_system + self.J / (2 * S_base / (2 * np.pi * 50)**2)
        f_nadir_with = -P_disturbance / (2 * H_total * S_base / 50)
        
        improvement = f_nadir_without - f_nadir_with
        
        return {
            'f_nadir_without_VSG': f_nadir_without,
            'f_nadir_with_VSG': f_nadir_with,
            'improvement': improvement,
            'improvement_ratio': improvement / abs(f_nadir_without),
        }


class AncillaryServiceCoordination:
    """
    辅助服务协调
    
    多种电源协调提供辅助服务
    """
    
    def __init__(self, name: str = "AncillaryService"):
        self.name = name
    
    def allocate_frequency_regulation(
        self,
        P_total: float,
        units: List[Dict]
    ) -> Dict:
        """
        分配调频任务
        
        Args:
            P_total: 总调频需求 (MW)
            units: 机组列表
            
        Returns:
            分配方案
        """
        allocation = {}
        
        # 计算调频能力
        total_capability = sum(u.get('regulation_capability', 0) for u in units)
        
        if total_capability == 0:
            return allocation
        
        # 按能力比例分配
        for unit in units:
            capability = unit.get('regulation_capability', 0)
            allocation[unit['name']] = P_total * (capability / total_capability)
        
        return allocation
    
    def compute_service_cost(
        self,
        service_type: str,
        capacity: float,  # MW
        energy: float,  # MWh
        price_capacity: float = 100,  # 元/MW/day
        price_energy: float = 500  # 元/MWh
    ) -> float:
        """
        计算辅助服务成本
        
        Args:
            service_type: 服务类型
            capacity: 容量
            energy: 电量
            price_capacity: 容量价格
            price_energy: 电量价格
            
        Returns:
            成本 (元)
        """
        cost = capacity * price_capacity + energy * price_energy
        return cost
    
    def evaluate_service_value(
        self,
        service_provision: Dict,
        market_prices: Dict
    ) -> Dict:
        """
        评估辅助服务价值
        
        Args:
            service_provision: 提供的服务
            market_prices: 市场价格
            
        Returns:
            价值评估
        """
        total_value = 0
        breakdown = {}
        
        for service, amount in service_provision.items():
            price = market_prices.get(service, 0)
            value = amount * price
            breakdown[service] = value
            total_value += value
        
        return {
            'total_value': total_value,
            'breakdown': breakdown,
        }
