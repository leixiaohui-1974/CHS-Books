"""
储能系统应用模块

包含:
1. 削峰填谷
2. 平滑新能源出力
3. 调频辅助服务
4. 微网储能优化配置
5. V2G双向互动
6. 飞轮储能

作者: CHS Books
"""

import numpy as np
from typing import Dict, List
from scipy.optimize import minimize


class PeakShavingValleyFilling:
    """
    削峰填谷应用
    
    利用峰谷电价差套利
    """
    
    def __init__(
        self,
        P_rated: float = 1000e3,  # W
        E_capacity: float = 2000e3,  # Wh
        efficiency: float = 0.9,
        soc_min: float = 0.2,
        soc_max: float = 0.9,
        name: str = "PeakShaving"
    ):
        """
        初始化削峰填谷控制器
        
        Args:
            P_rated: 额定功率
            E_capacity: 储能容量
            efficiency: 充放电效率
            soc_min, soc_max: SOC限制
        """
        self.name = name
        self.P_rated = P_rated
        self.E_capacity = E_capacity
        self.efficiency = efficiency
        self.soc_min = soc_min
        self.soc_max = soc_max
        
        # 状态
        self.soc = 0.5
    
    def optimize_daily_schedule(
        self,
        load_profile: np.ndarray,
        price_profile: np.ndarray
    ) -> np.ndarray:
        """
        优化日调度计划
        
        Args:
            load_profile: 24小时负荷曲线 (W)
            price_profile: 24小时电价曲线 (元/kWh)
            
        Returns:
            储能功率计划 (W), 充电为正
        """
        n_hours = len(load_profile)
        P_storage = np.zeros(n_hours)
        
        # 简化策略：谷时充电，峰时放电
        price_threshold_high = np.percentile(price_profile, 75)
        price_threshold_low = np.percentile(price_profile, 25)
        
        for i in range(n_hours):
            if price_profile[i] < price_threshold_low and self.soc < self.soc_max:
                # 谷时充电
                P_storage[i] = self.P_rated
            elif price_profile[i] > price_threshold_high and self.soc > self.soc_min:
                # 峰时放电
                P_storage[i] = -self.P_rated
            else:
                P_storage[i] = 0
        
        return P_storage
    
    def compute_cost_benefit(
        self,
        P_storage: np.ndarray,
        price_profile: np.ndarray,
        dt: float = 3600.0
    ) -> Dict:
        """
        计算成本效益
        
        Args:
            P_storage: 储能功率曲线 (W)
            price_profile: 电价曲线 (元/kWh)
            dt: 时间步长 (s)
            
        Returns:
            成本效益分析结果
        """
        # 充电成本
        P_charge = np.maximum(P_storage, 0)
        E_charge = P_charge * dt / 3600 / 1000  # kWh
        cost_charge = np.sum(E_charge * price_profile)
        
        # 放电收益
        P_discharge = np.abs(np.minimum(P_storage, 0))
        E_discharge = P_discharge * dt / 3600 / 1000  # kWh
        revenue_discharge = np.sum(E_discharge * price_profile)
        
        # 净收益
        net_profit = revenue_discharge - cost_charge
        
        return {
            'cost_charge': cost_charge,
            'revenue_discharge': revenue_discharge,
            'net_profit': net_profit,
            'E_charge_total': np.sum(E_charge),
            'E_discharge_total': np.sum(E_discharge),
        }


class RenewableSmoothingControl:
    """
    平滑新能源出力
    
    降低风光出力波动
    """
    
    def __init__(
        self,
        P_storage_rated: float = 500e3,  # W
        filter_time_constant: float = 600.0,  # s, 滤波时间常数
        name: str = "RenewableSmoothing"
    ):
        """
        初始化平滑控制器
        
        Args:
            P_storage_rated: 储能额定功率
            filter_time_constant: 一阶滤波时间常数
        """
        self.name = name
        self.P_rated = P_storage_rated
        self.tau = filter_time_constant
        
        # 滤波器状态
        self.P_filtered = 0.0
    
    def low_pass_filter(self, P_renewable: float, dt: float) -> float:
        """
        一阶低通滤波
        
        Args:
            P_renewable: 新能源实际功率 (W)
            dt: 时间步长 (s)
            
        Returns:
            滤波后的功率 (W)
        """
        alpha = dt / (self.tau + dt)
        self.P_filtered = alpha * P_renewable + (1 - alpha) * self.P_filtered
        return self.P_filtered
    
    def compute_storage_power(
        self,
        P_renewable: float,
        dt: float
    ) -> Dict:
        """
        计算储能功率指令
        
        Args:
            P_renewable: 新能源实际功率 (W)
            dt: 时间步长 (s)
            
        Returns:
            控制结果
        """
        # 滤波得到并网功率参考
        P_grid_ref = self.low_pass_filter(P_renewable, dt)
        
        # 储能功率 = 新能源功率 - 并网功率参考
        P_storage = P_renewable - P_grid_ref
        P_storage = np.clip(P_storage, -self.P_rated, self.P_rated)
        
        # 实际并网功率
        P_grid_actual = P_renewable - P_storage
        
        return {
            'P_renewable': P_renewable,
            'P_grid_ref': P_grid_ref,
            'P_storage': P_storage,
            'P_grid_actual': P_grid_actual,
        }
    
    def compute_smoothing_effect(
        self,
        P_renewable_profile: np.ndarray,
        dt: float
    ) -> Dict:
        """
        评估平滑效果
        
        Args:
            P_renewable_profile: 新能源功率时间序列
            dt: 时间步长
            
        Returns:
            平滑效果指标
        """
        n = len(P_renewable_profile)
        P_grid = np.zeros(n)
        
        for i in range(n):
            result = self.compute_storage_power(P_renewable_profile[i], dt)
            P_grid[i] = result['P_grid_actual']
        
        # 计算波动率
        std_original = np.std(P_renewable_profile)
        std_smoothed = np.std(P_grid)
        smoothing_ratio = (std_original - std_smoothed) / std_original
        
        return {
            'std_original': std_original,
            'std_smoothed': std_smoothed,
            'smoothing_ratio': smoothing_ratio,
            'P_grid_profile': P_grid,
        }


class FrequencyRegulationService:
    """
    调频辅助服务
    
    一次/二次调频
    """
    
    def __init__(
        self,
        P_rated: float = 1000e3,  # W
        response_time: float = 1.0,  # s
        dead_band: float = 0.033,  # Hz
        droop: float = 0.05,  # 5% droop
        name: str = "FreqRegulation"
    ):
        """
        初始化调频控制器
        
        Args:
            P_rated: 额定功率
            response_time: 响应时间
            dead_band: 频率死区
            droop: 下垂系数
        """
        self.name = name
        self.P_rated = P_rated
        self.response_time = response_time
        self.dead_band = dead_band
        self.droop = droop
        self.f_nom = 50.0  # Hz
    
    def primary_frequency_control(self, f_grid: float) -> float:
        """
        一次调频控制
        
        P = -K_droop * Δf
        
        Args:
            f_grid: 电网频率 (Hz)
            
        Returns:
            功率指令 (W)
        """
        df = f_grid - self.f_nom
        
        # 死区
        if abs(df) < self.dead_band:
            return 0.0
        
        # 下垂控制
        K_droop = self.P_rated / (self.droop * self.f_nom)
        P_ref = -K_droop * df
        P_ref = np.clip(P_ref, -self.P_rated, self.P_rated)
        
        return P_ref
    
    def compute_regulation_revenue(
        self,
        capacity_payment: float,  # 元/MW/月
        energy_payment: float,  # 元/MWh
        P_capacity: float,  # MW, 申报容量
        E_regulated: float,  # MWh, 月调节电量
        performance_score: float = 1.0  # 性能考核得分
    ) -> float:
        """
        计算调频收益
        
        Args:
            capacity_payment: 容量补偿价格
            energy_payment: 电量补偿价格
            P_capacity: 申报调频容量
            E_regulated: 月调节电量
            performance_score: 性能得分 (0-1)
            
        Returns:
            月收益 (元)
        """
        revenue_capacity = capacity_payment * P_capacity * performance_score
        revenue_energy = energy_payment * E_regulated * performance_score
        total_revenue = revenue_capacity + revenue_energy
        
        return total_revenue


class MicrogridStorageOptimization:
    """
    微网储能优化配置
    
    优化储能容量和功率
    """
    
    def __init__(
        self,
        load_profile: np.ndarray,  # 负荷曲线
        renewable_profile: np.ndarray,  # 新能源曲线
        cost_per_kwh: float = 1500.0,  # 元/kWh, 储能成本
        cost_per_kw: float = 800.0,  # 元/kW, 功率成本
        name: str = "MicrogridOptimization"
    ):
        """
        初始化微网优化
        
        Args:
            load_profile: 负荷曲线 (W)
            renewable_profile: 新能源曲线 (W)
            cost_per_kwh: 储能容量成本
            cost_per_kw: 储能功率成本
        """
        self.name = name
        self.load = load_profile
        self.renewable = renewable_profile
        self.cost_kwh = cost_per_kwh
        self.cost_kw = cost_per_kw
    
    def optimize_capacity(self) -> Dict:
        """
        优化储能容量配置
        
        目标: 最小化 储能投资成本 + 负荷缺额成本
        
        Returns:
            优化结果
        """
        # 净负荷
        net_load = self.load - self.renewable
        
        # 需要储能支撑的最大功率
        P_storage_max = np.max(net_load[net_load > 0])
        
        # 需要储能吸收的最大能量
        surplus_energy = -np.sum(net_load[net_load < 0]) / 3600 / 1000  # kWh
        deficit_energy = np.sum(net_load[net_load > 0]) / 3600 / 1000  # kWh
        
        # 简化：储能容量取缺额和盈余的平均
        E_storage_optimal = min(surplus_energy, deficit_energy)
        
        # 功率取最大净负荷
        P_storage_optimal = P_storage_max
        
        # 成本
        cost_total = (E_storage_optimal * self.cost_kwh + 
                     P_storage_optimal / 1000 * self.cost_kw)
        
        return {
            'P_storage_optimal': P_storage_optimal,
            'E_storage_optimal': E_storage_optimal,
            'cost_total': cost_total,
            'surplus_energy': surplus_energy,
            'deficit_energy': deficit_energy,
        }


class V2GController:
    """
    Vehicle-to-Grid (V2G) 控制器
    
    电动汽车双向充放电
    """
    
    def __init__(
        self,
        n_vehicles: int = 100,
        battery_capacity: float = 60.0,  # kWh
        charge_power_max: float = 7.0,  # kW
        soc_min: float = 0.2,
        soc_max: float = 0.9,
        name: str = "V2G"
    ):
        """
        初始化V2G控制器
        
        Args:
            n_vehicles: 车辆数量
            battery_capacity: 单车电池容量
            charge_power_max: 单车最大充电功率
            soc_min, soc_max: SOC限制
        """
        self.name = name
        self.n_vehicles = n_vehicles
        self.battery_capacity = battery_capacity
        self.P_max = charge_power_max
        self.soc_min = soc_min
        self.soc_max = soc_max
        
        # 车辆SOC（随机初始化）
        self.vehicle_soc = np.random.uniform(0.3, 0.8, n_vehicles)
    
    def aggregate_capacity(self) -> Dict:
        """
        聚合容量计算
        
        Returns:
            聚合容量信息
        """
        # 可充电容量
        E_charge_available = np.sum(
            (self.soc_max - self.vehicle_soc) * self.battery_capacity
        )
        
        # 可放电容量
        E_discharge_available = np.sum(
            (self.vehicle_soc - self.soc_min) * self.battery_capacity
        )
        
        # 聚合功率
        P_charge_total = self.n_vehicles * self.P_max
        P_discharge_total = self.n_vehicles * self.P_max
        
        return {
            'E_charge_available': E_charge_available,
            'E_discharge_available': E_discharge_available,
            'P_charge_total': P_charge_total,
            'P_discharge_total': P_discharge_total,
        }
    
    def dispatch_power(
        self,
        P_grid_request: float,  # kW, 电网请求功率
        dt: float = 3600.0  # s
    ) -> float:
        """
        功率调度
        
        Args:
            P_grid_request: 电网请求功率 (kW), 充电为正
            dt: 时间步长 (s)
            
        Returns:
            实际功率 (kW)
        """
        # 简化：均匀分配给所有车辆
        P_per_vehicle = P_grid_request / self.n_vehicles
        P_per_vehicle = np.clip(P_per_vehicle, -self.P_max, self.P_max)
        
        # 更新车辆SOC
        for i in range(self.n_vehicles):
            delta_soc = P_per_vehicle * dt / 3600 / self.battery_capacity
            self.vehicle_soc[i] += delta_soc
            self.vehicle_soc[i] = np.clip(self.vehicle_soc[i], self.soc_min, self.soc_max)
        
        P_actual = P_per_vehicle * self.n_vehicles
        return P_actual


class FlywheelEnergyStorage:
    """
    飞轮储能系统
    
    高功率密度、快速响应
    """
    
    def __init__(
        self,
        J_flywheel: float = 50.0,  # kg·m², 转动惯量
        omega_max: float = 3000.0,  # rad/s, 最大角速度
        omega_min: float = 1000.0,  # rad/s, 最小角速度
        efficiency: float = 0.9,
        name: str = "Flywheel"
    ):
        """
        初始化飞轮储能
        
        Args:
            J_flywheel: 转动惯量
            omega_max: 最大角速度
            omega_min: 最小角速度
            efficiency: 充放电效率
        """
        self.name = name
        self.J = J_flywheel
        self.omega_max = omega_max
        self.omega_min = omega_min
        self.efficiency = efficiency
        
        # 状态
        self.omega = (omega_max + omega_min) / 2
    
    def get_stored_energy(self) -> float:
        """
        计算存储能量
        
        E = 0.5 * J * ω²
        
        Returns:
            能量 (J)
        """
        return 0.5 * self.J * self.omega**2
    
    def get_soc(self) -> float:
        """
        计算SOC
        
        Returns:
            SOC (0-1)
        """
        E_current = self.get_stored_energy()
        E_max = 0.5 * self.J * self.omega_max**2
        E_min = 0.5 * self.J * self.omega_min**2
        
        soc = (E_current - E_min) / (E_max - E_min)
        return np.clip(soc, 0, 1)
    
    def charge_discharge(self, P: float, dt: float):
        """
        充放电
        
        Args:
            P: 功率 (W), 充电为正
            dt: 时间步长 (s)
        """
        # 能量变化
        delta_E = P * self.efficiency * dt
        
        # 当前能量
        E_current = self.get_stored_energy()
        E_new = E_current + delta_E
        
        # 反算角速度
        self.omega = np.sqrt(2 * E_new / self.J)
        self.omega = np.clip(self.omega, self.omega_min, self.omega_max)
