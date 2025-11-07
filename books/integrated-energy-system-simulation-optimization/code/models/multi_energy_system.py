"""
多能源系统建模模块

包含:
1. 水电站模型
2. 火电机组模型
3. 负荷模型
4. 系统互补特性分析

作者: CHS Books
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


class HydropowerPlant:
    """
    水电站模型
    
    核心方程: P = η * ρ * g * Q * H
    """
    
    def __init__(
        self,
        reservoir_capacity: float = 1000e6,  # m³
        H_rated: float = 100,  # 额定水头 (m)
        Q_max: float = 1000,  # 最大流量 (m³/s)
        efficiency: float = 0.9,
        P_rated: float = 300,  # MW
        name: str = "Hydro"
    ):
        """
        初始化水电站
        
        Args:
            reservoir_capacity: 水库容量
            H_rated: 额定水头
            Q_max: 最大流量
            efficiency: 效率
            P_rated: 额定功率
        """
        self.name = name
        self.V_capacity = reservoir_capacity
        self.H_rated = H_rated
        self.Q_max = Q_max
        self.efficiency = efficiency
        self.P_rated = P_rated
        
        # 状态
        self.V = reservoir_capacity * 0.5  # 初始库容
        
        # 物理常数
        self.rho = 1000  # kg/m³
        self.g = 9.81  # m/s²
    
    def compute_power(
        self,
        Q: float,  # m³/s
        H: float = None  # m
    ) -> float:
        """
        计算发电功率
        
        P = η * ρ * g * Q * H / 1e6
        
        Args:
            Q: 流量
            H: 水头（None则使用额定值）
            
        Returns:
            功率 (MW)
        """
        if H is None:
            H = self.H_rated
        
        P = self.efficiency * self.rho * self.g * Q * H / 1e6
        P = np.clip(P, 0, self.P_rated)
        
        return P
    
    def update_reservoir(
        self,
        Q_in: float,  # 入库流量 (m³/s)
        Q_out: float,  # 出库流量 (m³/s)
        dt: float  # 时间步长 (s)
    ):
        """
        更新水库状态
        
        dV/dt = Q_in - Q_out
        
        Args:
            Q_in: 入库流量
            Q_out: 出库流量
            dt: 时间步长
        """
        dV = (Q_in - Q_out) * dt
        self.V = np.clip(self.V + dV, 0, self.V_capacity)
    
    def get_head(self) -> float:
        """
        根据库容计算水头
        
        简化：线性关系
        """
        V_ratio = self.V / self.V_capacity
        H = self.H_rated * (0.7 + 0.3 * V_ratio)  # 水头随库容变化
        return H
    
    def simulate_daily_operation(
        self,
        inflow_profile: np.ndarray,  # [T] m³/s
        power_target: np.ndarray,  # [T] MW
        dt: float = 900  # 15min
    ) -> Dict:
        """
        日运行仿真
        
        Args:
            inflow_profile: 入库流量曲线
            power_target: 目标功率曲线
            dt: 时间步长
            
        Returns:
            仿真结果
        """
        T = len(inflow_profile)
        
        P_actual = np.zeros(T)
        Q_out = np.zeros(T)
        V_trajectory = np.zeros(T)
        H_trajectory = np.zeros(T)
        
        for t in range(T):
            Q_in = inflow_profile[t]
            H = self.get_head()
            
            # 根据目标功率计算所需流量
            P_target = power_target[t]
            Q_required = P_target * 1e6 / (self.efficiency * self.rho * self.g * H)
            Q_required = np.clip(Q_required, 0, self.Q_max)
            
            # 检查库容约束
            V_after = self.V - Q_required * dt
            if V_after < 0:
                Q_required = self.V / dt
            
            Q_out[t] = Q_required
            P_actual[t] = self.compute_power(Q_required, H)
            
            self.update_reservoir(Q_in, Q_required, dt)
            
            V_trajectory[t] = self.V
            H_trajectory[t] = H
        
        return {
            'P': P_actual,
            'Q_out': Q_out,
            'V': V_trajectory,
            'H': H_trajectory,
        }


class ThermalUnit:
    """
    火电机组模型
    
    特性: 启停时间、爬坡约束、燃料消耗
    """
    
    def __init__(
        self,
        P_rated: float = 600,  # MW
        P_min: float = 200,  # MW
        ramp_rate: float = 10,  # MW/min
        startup_time: float = 4,  # hours
        shutdown_time: float = 2,  # hours
        cost_coef: Tuple[float, float, float] = (1000, 50, 0.01),  # a, b, c
        emission_factor: float = 0.8,  # tCO2/MWh
        name: str = "Thermal"
    ):
        """
        初始化火电机组
        
        Args:
            P_rated: 额定功率
            P_min: 最小出力
            ramp_rate: 爬坡速率
            startup_time: 启动时间
            shutdown_time: 停机时间
            cost_coef: 成本系数 F(P) = a + bP + cP²
            emission_factor: 排放因子
        """
        self.name = name
        self.P_rated = P_rated
        self.P_min = P_min
        self.ramp_rate = ramp_rate
        self.t_startup = startup_time
        self.t_shutdown = shutdown_time
        self.a, self.b, self.c = cost_coef
        self.emission_factor = emission_factor
        
        # 状态
        self.status = True  # True=运行, False=停机
        self.P = P_min
    
    def fuel_cost(self, P: float, dt: float = 1.0) -> float:
        """
        计算燃料成本
        
        F(P) = a + b*P + c*P² (元/小时)
        
        Args:
            P: 功率 (MW)
            dt: 时间 (小时)
            
        Returns:
            成本 (元)
        """
        cost = (self.a + self.b * P + self.c * P**2) * dt
        return cost
    
    def emission(self, P: float, dt: float = 1.0) -> float:
        """
        计算排放量
        
        Args:
            P: 功率 (MW)
            dt: 时间 (小时)
            
        Returns:
            CO2排放量 (tCO2)
        """
        emission = self.emission_factor * P * dt
        return emission
    
    def set_power(self, P_target: float, dt: float = 1.0) -> float:
        """
        设定功率（考虑爬坡约束）
        
        Args:
            P_target: 目标功率
            dt: 时间步长 (分钟)
            
        Returns:
            实际功率
        """
        if not self.status:
            return 0
        
        # 爬坡约束
        delta_P_max = self.ramp_rate * dt
        delta_P = P_target - self.P
        
        if abs(delta_P) <= delta_P_max:
            self.P = P_target
        else:
            self.P += np.sign(delta_P) * delta_P_max
        
        # 功率限制
        self.P = np.clip(self.P, self.P_min if self.status else 0, self.P_rated)
        
        return self.P
    
    def startup(self) -> Dict:
        """
        启动机组
        
        Returns:
            启动信息
        """
        if self.status:
            return {'success': False, 'message': 'Already running'}
        
        startup_cost = 10000  # 启动成本 (元)
        
        self.status = True
        self.P = self.P_min
        
        return {
            'success': True,
            'cost': startup_cost,
            'time': self.t_startup,
        }
    
    def shutdown(self):
        """停机"""
        self.status = False
        self.P = 0


class LoadModel:
    """
    负荷模型
    
    包括刚性负荷和可调节负荷
    """
    
    def __init__(self, name: str = "Load"):
        self.name = name
    
    def generate_daily_load(
        self,
        P_base: float = 1000,  # MW
        peak_ratio: float = 1.3,
        valley_ratio: float = 0.7,
        n_points: int = 96  # 15min x 96 = 24h
    ) -> np.ndarray:
        """
        生成日负荷曲线
        
        典型双峰曲线
        
        Args:
            P_base: 基准负荷
            peak_ratio: 峰值比例
            valley_ratio: 谷值比例
            n_points: 点数
            
        Returns:
            负荷曲线 [n_points]
        """
        t = np.linspace(0, 24, n_points)
        
        # 双峰模型：10:00和19:00峰值
        morning_peak = 10
        evening_peak = 19
        
        load = P_base * (
            1 + 
            (peak_ratio - 1) * np.exp(-((t - morning_peak)**2) / 8) +
            (peak_ratio - 1) * np.exp(-((t - evening_peak)**2) / 8) +
            (valley_ratio - 1) * np.exp(-((t - 3)**2) / 8)
        )
        
        return load
    
    def add_flexible_load(
        self,
        rigid_load: np.ndarray,
        flexible_ratio: float = 0.1
    ) -> Dict:
        """
        添加可调节负荷
        
        Args:
            rigid_load: 刚性负荷
            flexible_ratio: 可调节比例
            
        Returns:
            负荷组成
        """
        total = rigid_load
        flexible = total * flexible_ratio
        rigid = total - flexible
        
        return {
            'total': total,
            'rigid': rigid,
            'flexible': flexible,
        }


class ComplementarityAnalysis:
    """
    多能互补特性分析
    """
    
    def __init__(self, name: str = "Complementarity"):
        self.name = name
    
    def correlation_coefficient(
        self,
        series1: np.ndarray,
        series2: np.ndarray
    ) -> float:
        """
        计算相关系数
        
        Args:
            series1, series2: 时间序列
            
        Returns:
            相关系数 [-1, 1]
        """
        corr = np.corrcoef(series1, series2)[0, 1]
        return corr
    
    def complementarity_coefficient(
        self,
        P_wind: np.ndarray,
        P_solar: np.ndarray
    ) -> float:
        """
        互补系数
        
        C = 1 - σ(P_wind + P_solar) / (σ(P_wind) + σ(P_solar))
        
        C越大，互补性越好
        
        Args:
            P_wind: 风电功率序列
            P_solar: 光伏功率序列
            
        Returns:
            互补系数 [0, 1]
        """
        P_combined = P_wind + P_solar
        
        sigma_combined = np.std(P_combined)
        sigma_wind = np.std(P_wind)
        sigma_solar = np.std(P_solar)
        
        C = 1 - sigma_combined / (sigma_wind + sigma_solar)
        
        return C
    
    def fluctuation_reduction(
        self,
        P_renewable: np.ndarray,
        P_hydro: np.ndarray
    ) -> Dict:
        """
        水电平抑波动效果
        
        Args:
            P_renewable: 新能源功率序列
            P_hydro: 水电调节功率序列
            
        Returns:
            平抑效果评估
        """
        P_combined = P_renewable + P_hydro
        
        # 波动指标
        std_renewable = np.std(P_renewable)
        std_combined = np.std(P_combined)
        
        reduction_ratio = (std_renewable - std_combined) / std_renewable
        
        # 最大爬坡
        ramp_renewable = np.max(np.abs(np.diff(P_renewable)))
        ramp_combined = np.max(np.abs(np.diff(P_combined)))
        
        ramp_reduction = (ramp_renewable - ramp_combined) / ramp_renewable
        
        return {
            'std_reduction': reduction_ratio,
            'ramp_reduction': ramp_reduction,
            'std_before': std_renewable,
            'std_after': std_combined,
        }
    
    def seasonal_complementarity(
        self,
        P_wind_monthly: np.ndarray,  # [12]
        P_solar_monthly: np.ndarray,  # [12]
        inflow_monthly: np.ndarray  # [12]
    ) -> Dict:
        """
        季节互补特性分析
        
        Args:
            P_wind_monthly: 风电月均功率
            P_solar_monthly: 光伏月均功率
            inflow_monthly: 月均来水
            
        Returns:
            季节互补分析
        """
        # 标准化
        wind_norm = P_wind_monthly / np.mean(P_wind_monthly)
        solar_norm = P_solar_monthly / np.mean(P_solar_monthly)
        inflow_norm = inflow_monthly / np.mean(inflow_monthly)
        
        # 相关系数
        corr_wind_solar = self.correlation_coefficient(wind_norm, solar_norm)
        corr_wind_inflow = self.correlation_coefficient(wind_norm, inflow_norm)
        corr_solar_inflow = self.correlation_coefficient(solar_norm, inflow_norm)
        
        return {
            'wind_solar_corr': corr_wind_solar,
            'wind_inflow_corr': corr_wind_inflow,
            'solar_inflow_corr': corr_solar_inflow,
            'wind_monthly': wind_norm,
            'solar_monthly': solar_norm,
            'inflow_monthly': inflow_norm,
        }


class IntegratedEnergySystem:
    """
    综合能源系统
    
    整合水火风光储
    """
    
    def __init__(
        self,
        hydro: HydropowerPlant,
        thermal_units: List[ThermalUnit],
        P_wind_rated: float = 200,
        P_solar_rated: float = 150,
        P_storage_rated: float = 50,
        name: str = "IntegratedSystem"
    ):
        """
        初始化综合能源系统
        
        Args:
            hydro: 水电站
            thermal_units: 火电机组列表
            P_wind_rated: 风电装机
            P_solar_rated: 光伏装机
            P_storage_rated: 储能装机
        """
        self.name = name
        self.hydro = hydro
        self.thermal_units = thermal_units
        self.P_wind_rated = P_wind_rated
        self.P_solar_rated = P_solar_rated
        self.P_storage_rated = P_storage_rated
    
    def compute_total_capacity(self) -> Dict:
        """
        计算总装机容量
        """
        P_hydro = self.hydro.P_rated
        P_thermal = sum(u.P_rated for u in self.thermal_units)
        P_wind = self.P_wind_rated
        P_solar = self.P_solar_rated
        P_storage = self.P_storage_rated
        
        P_total = P_hydro + P_thermal + P_wind + P_solar + P_storage
        
        return {
            'hydro': P_hydro,
            'thermal': P_thermal,
            'wind': P_wind,
            'solar': P_solar,
            'storage': P_storage,
            'total': P_total,
        }
    
    def simulate_operation(
        self,
        load: np.ndarray,
        P_wind: np.ndarray,
        P_solar: np.ndarray,
        inflow: np.ndarray,
        dt: float = 900  # 15min
    ) -> Dict:
        """
        系统运行仿真
        
        Args:
            load: 负荷曲线
            P_wind: 风电出力
            P_solar: 光伏出力
            inflow: 水电入库流量
            dt: 时间步长
            
        Returns:
            仿真结果
        """
        T = len(load)
        
        # 初始化
        P_hydro = np.zeros(T)
        P_thermal = np.zeros(T)
        P_renewable = P_wind + P_solar
        
        for t in range(T):
            # 净负荷
            net_load = load[t] - P_renewable[t]
            
            # 水电跟踪
            P_hydro_target = min(net_load * 0.3, self.hydro.P_rated)
            P_hydro[t] = self.hydro.compute_power(P_hydro_target / 100 * 10)
            
            # 火电平衡
            P_thermal[t] = net_load - P_hydro[t]
            P_thermal[t] = np.clip(P_thermal[t], 0, sum(u.P_rated for u in self.thermal_units))
        
        return {
            'P_hydro': P_hydro,
            'P_thermal': P_thermal,
            'P_wind': P_wind,
            'P_solar': P_solar,
            'P_renewable': P_renewable,
            'load': load,
        }
