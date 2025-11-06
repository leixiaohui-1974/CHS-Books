"""
混合储能系统模块

包含:
1. 锂电池+超级电容混合储能
2. 功率型/能量型分层控制
3. 氢储能系统
4. 压缩空气储能

作者: CHS Books
"""

import numpy as np
from typing import Dict


class HybridBatterySupercap:
    """
    锂电池+超级电容混合储能
    
    电池提供能量，超级电容提供功率
    """
    
    def __init__(
        self,
        battery_capacity: float = 100e3,  # Wh
        battery_power: float = 50e3,  # W
        supercap_energy: float = 5e3,  # Wh
        supercap_power: float = 200e3,  # W
        filter_cutoff: float = 0.1,  # Hz, 功率分配截止频率
        name: str = "HybridBatterySC"
    ):
        """
        初始化混合储能系统
        
        Args:
            battery_capacity: 电池容量
            battery_power: 电池功率
            supercap_energy: 超级电容能量
            supercap_power: 超级电容功率
            filter_cutoff: 低通滤波截止频率
        """
        self.name = name
        self.E_battery = battery_capacity
        self.P_battery_max = battery_power
        self.E_supercap = supercap_energy
        self.P_supercap_max = supercap_power
        self.fc = filter_cutoff
        
        # 状态
        self.soc_battery = 0.5
        self.soc_supercap = 0.5
        
        # 滤波器状态
        self.P_battery_filtered = 0.0
    
    def power_allocation(
        self,
        P_total_demand: float,
        dt: float
    ) -> Dict:
        """
        功率分配策略
        
        低频分量 → 电池
        高频分量 → 超级电容
        
        Args:
            P_total_demand: 总功率需求 (W)
            dt: 时间步长 (s)
            
        Returns:
            功率分配结果
        """
        # 一阶低通滤波
        tau = 1 / (2 * np.pi * self.fc)
        alpha = dt / (tau + dt)
        
        self.P_battery_filtered = (
            alpha * P_total_demand + 
            (1 - alpha) * self.P_battery_filtered
        )
        
        # 电池承担低频分量
        P_battery = self.P_battery_filtered
        P_battery = np.clip(P_battery, -self.P_battery_max, self.P_battery_max)
        
        # 超级电容承担高频分量
        P_supercap = P_total_demand - P_battery
        P_supercap = np.clip(P_supercap, -self.P_supercap_max, self.P_supercap_max)
        
        # 实际总功率
        P_actual = P_battery + P_supercap
        
        # 更新SOC
        self.soc_battery += P_battery * dt / (self.E_battery * 3600)
        self.soc_battery = np.clip(self.soc_battery, 0, 1)
        
        self.soc_supercap += P_supercap * dt / (self.E_supercap * 3600)
        self.soc_supercap = np.clip(self.soc_supercap, 0, 1)
        
        return {
            'P_total_demand': P_total_demand,
            'P_battery': P_battery,
            'P_supercap': P_supercap,
            'P_actual': P_actual,
            'soc_battery': self.soc_battery,
            'soc_supercap': self.soc_supercap,
        }


class HierarchicalStorageControl:
    """
    功率型/能量型分层控制
    
    协调不同时间尺度的储能
    """
    
    def __init__(
        self,
        power_storage_rating: float = 100e3,  # W, 功率型
        energy_storage_rating: float = 50e3,  # W, 能量型
        power_storage_duration: float = 60.0,  # s, 功率型持续时间
        energy_storage_duration: float = 7200.0,  # s, 能量型持续时间
        name: str = "HierarchicalControl"
    ):
        """
        初始化分层控制
        
        Args:
            power_storage_rating: 功率型额定功率
            energy_storage_rating: 能量型额定功率
            power_storage_duration: 功率型持续时间
            energy_storage_duration: 能量型持续时间
        """
        self.name = name
        self.P_power = power_storage_rating
        self.P_energy = energy_storage_rating
        self.t_power = power_storage_duration
        self.t_energy = energy_storage_duration
        
        # SOC状态
        self.soc_power = 0.5
        self.soc_energy = 0.5
    
    def coordinate_control(
        self,
        P_demand: float,
        time_scale: str,
        dt: float
    ) -> Dict:
        """
        协调控制
        
        Args:
            P_demand: 功率需求 (W)
            time_scale: 'fast' or 'slow'
            dt: 时间步长 (s)
            
        Returns:
            控制结果
        """
        if time_scale == 'fast':
            # 快速响应由功率型承担
            P_power_storage = np.clip(P_demand, -self.P_power, self.P_power)
            P_energy_storage = 0
        else:
            # 慢速响应由能量型承担
            P_energy_storage = np.clip(P_demand, -self.P_energy, self.P_energy)
            P_power_storage = 0
        
        # 更新SOC
        E_power = self.P_power * self.t_power / 3600  # Wh
        E_energy = self.P_energy * self.t_energy / 3600  # Wh
        
        self.soc_power += P_power_storage * dt / (E_power * 3600)
        self.soc_power = np.clip(self.soc_power, 0, 1)
        
        self.soc_energy += P_energy_storage * dt / (E_energy * 3600)
        self.soc_energy = np.clip(self.soc_energy, 0, 1)
        
        return {
            'P_power_storage': P_power_storage,
            'P_energy_storage': P_energy_storage,
            'soc_power': self.soc_power,
            'soc_energy': self.soc_energy,
        }


class HydrogenEnergyStorage:
    """
    氢储能系统
    
    电解槽 + 燃料电池
    """
    
    def __init__(
        self,
        electrolyzer_power: float = 1000e3,  # W
        fuel_cell_power: float = 800e3,  # W
        h2_storage_capacity: float = 100.0,  # kg
        electrolyzer_efficiency: float = 0.7,
        fuel_cell_efficiency: float = 0.5,
        name: str = "HydrogenStorage"
    ):
        """
        初始化氢储能系统
        
        Args:
            electrolyzer_power: 电解槽功率
            fuel_cell_power: 燃料电池功率
            h2_storage_capacity: 氢气储存容量
            electrolyzer_efficiency: 电解槽效率
            fuel_cell_efficiency: 燃料电池效率
        """
        self.name = name
        self.P_electrolyzer = electrolyzer_power
        self.P_fuel_cell = fuel_cell_power
        self.H2_capacity = h2_storage_capacity
        self.eta_electrolyzer = electrolyzer_efficiency
        self.eta_fuel_cell = fuel_cell_efficiency
        
        # 氢气存储量
        self.H2_stored = h2_storage_capacity / 2  # kg
        
        # 氢气高位热值：33.3 kWh/kg
        self.H2_HHV = 33.3 * 3600 * 1000  # J/kg
    
    def electrolyzer_operation(self, P_input: float, dt: float):
        """
        电解槽运行（电→氢）
        
        Args:
            P_input: 输入功率 (W)
            dt: 时间步长 (s)
        """
        P_input = min(P_input, self.P_electrolyzer)
        
        # 产氢量
        E_input = P_input * dt  # J
        m_H2_produced = E_input * self.eta_electrolyzer / self.H2_HHV  # kg
        
        self.H2_stored += m_H2_produced
        self.H2_stored = min(self.H2_stored, self.H2_capacity)
    
    def fuel_cell_operation(self, P_demand: float, dt: float) -> float:
        """
        燃料电池运行（氢→电）
        
        Args:
            P_demand: 需求功率 (W)
            dt: 时间步长 (s)
            
        Returns:
            实际输出功率 (W)
        """
        P_demand = min(P_demand, self.P_fuel_cell)
        
        # 需要的氢气量
        E_demand = P_demand * dt  # J
        m_H2_required = E_demand / (self.eta_fuel_cell * self.H2_HHV)  # kg
        
        if self.H2_stored >= m_H2_required:
            self.H2_stored -= m_H2_required
            return P_demand
        else:
            # 氢气不足
            P_actual = self.H2_stored * self.H2_HHV * self.eta_fuel_cell / dt
            self.H2_stored = 0
            return P_actual
    
    def get_soc(self) -> float:
        """计算SOC"""
        return self.H2_stored / self.H2_capacity


class CompressedAirEnergyStorage:
    """
    压缩空气储能 (CAES)
    
    简化热力学模型
    """
    
    def __init__(
        self,
        compressor_power: float = 50e6,  # W
        turbine_power: float = 40e6,  # W
        storage_volume: float = 100000.0,  # m³
        pressure_max: float = 70e5,  # Pa
        pressure_min: float = 40e5,  # Pa
        efficiency_compression: float = 0.8,
        efficiency_expansion: float = 0.85,
        name: str = "CAES"
    ):
        """
        初始化压缩空气储能
        
        Args:
            compressor_power: 压缩机功率
            turbine_power: 透平功率
            storage_volume: 储气容积
            pressure_max: 最大压力
            pressure_min: 最小压力
            efficiency_compression: 压缩效率
            efficiency_expansion: 膨胀效率
        """
        self.name = name
        self.P_compressor = compressor_power
        self.P_turbine = turbine_power
        self.V = storage_volume
        self.p_max = pressure_max
        self.p_min = pressure_min
        self.eta_comp = efficiency_compression
        self.eta_exp = efficiency_expansion
        
        # 当前压力
        self.p = (pressure_max + pressure_min) / 2
        
        # 气体常数（空气）
        self.R = 287.0  # J/(kg·K)
        self.T = 300.0  # K
    
    def compression(self, P_input: float, dt: float):
        """
        压缩空气（充能）
        
        Args:
            P_input: 输入功率 (W)
            dt: 时间步长 (s)
        """
        P_input = min(P_input, self.P_compressor)
        
        # 简化：能量存储为压力增加
        # E = ∫PdV ≈ p·V·ln(p2/p1)
        E_input = P_input * self.eta_comp * dt
        
        # 压力变化（简化）
        delta_p = E_input / (self.V * 2.5)  # 简化系数
        self.p += delta_p
        self.p = min(self.p, self.p_max)
    
    def expansion(self, P_demand: float, dt: float) -> float:
        """
        膨胀发电（释能）
        
        Args:
            P_demand: 需求功率 (W)
            dt: 时间步长 (s)
            
        Returns:
            实际输出功率 (W)
        """
        P_demand = min(P_demand, self.P_turbine)
        
        # 可释放能量
        E_available = self.V * (self.p - self.p_min) * 2.5
        P_available = E_available / dt * self.eta_exp
        
        if P_available >= P_demand:
            # 压力下降
            E_output = P_demand * dt / self.eta_exp
            delta_p = E_output / (self.V * 2.5)
            self.p -= delta_p
            self.p = max(self.p, self.p_min)
            return P_demand
        else:
            # 能量不足
            self.p = self.p_min
            return P_available
    
    def get_soc(self) -> float:
        """计算SOC"""
        return (self.p - self.p_min) / (self.p_max - self.p_min)
