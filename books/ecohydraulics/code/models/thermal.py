"""
水温分层与溶解氧模型
===================

实现水库热分层和DO动力学模型
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.integrate import odeint


class ThermalStratificationModel:
    """
    水温分层模型
    
    模拟水库垂向水温分布
    
    Parameters
    ----------
    depth : float
        水深 (m)
    n_layers : int
        垂向分层数
    """
    
    def __init__(self, depth: float, n_layers: int = 20):
        self.depth = depth
        self.n_layers = n_layers
        self.dz = depth / n_layers
        
        # 分层中心深度
        self.z = np.array([(i + 0.5) * self.dz for i in range(n_layers)])
        
        # 初始温度（均匀分布）
        self.temperature = np.ones(n_layers) * 20.0  # °C
    
    def set_initial_temperature(self, temp_profile: np.ndarray):
        """设置初始温度剖面"""
        if len(temp_profile) != self.n_layers:
            raise ValueError(f"温度剖面长度必须为{self.n_layers}")
        self.temperature = np.array(temp_profile)
    
    def water_density(self, T: float) -> float:
        """
        计算水的密度
        
        使用经验公式（适用于0-30°C）
        
        Parameters
        ----------
        T : float
            温度 (°C)
            
        Returns
        -------
        float
            密度 (kg/m³)
        """
        # 简化公式
        rho = 1000 * (1 - (T - 4)**2 / 100000)
        return rho
    
    def schmidt_stability(self) -> float:
        """
        计算Schmidt稳定度
        
        反映水体分层的稳定程度
        
        Returns
        -------
        float
            稳定度 (J/m²)
        """
        # 计算各层密度
        rho = np.array([self.water_density(T) for T in self.temperature])
        
        # 计算平均密度
        rho_mean = np.mean(rho)
        
        # Schmidt稳定度
        g = 9.81  # 重力加速度
        A = 1.0   # 假设单位面积
        
        S = 0
        for i in range(self.n_layers):
            S += g * A * self.dz * (self.z[i] - self.depth/2) * (rho[i] - rho_mean)
        
        return abs(S)
    
    def thermocline_depth(self) -> float:
        """
        计算温跃层深度
        
        定义为温度梯度最大处
        
        Returns
        -------
        float
            温跃层深度 (m)
        """
        # 计算温度梯度
        dT_dz = np.gradient(self.temperature, self.dz)
        
        # 找到梯度最大（绝对值）的位置
        max_gradient_idx = np.argmax(np.abs(dT_dz))
        
        return self.z[max_gradient_idx]
    
    def epilimnion_thickness(self) -> float:
        """计算表温层厚度"""
        thermocline_z = self.thermocline_depth()
        return thermocline_z
    
    def hypolimnion_thickness(self) -> float:
        """计算底温层厚度"""
        thermocline_z = self.thermocline_depth()
        return self.depth - thermocline_z


class DissolvedOxygenModel:
    """
    溶解氧动力学模型
    
    Parameters
    ----------
    depth : float
        水深 (m)
    n_layers : int
        垂向分层数
    """
    
    def __init__(self, depth: float, n_layers: int = 20):
        self.depth = depth
        self.n_layers = n_layers
        self.dz = depth / n_layers
        
        # 分层中心深度
        self.z = np.array([(i + 0.5) * self.dz for i in range(n_layers)])
        
        # 初始DO浓度（饱和）
        self.DO = np.ones(n_layers) * 8.0  # mg/L
        
        # 温度（关联到热分层模型）
        self.temperature = np.ones(n_layers) * 20.0
    
    def set_temperature(self, temp_profile: np.ndarray):
        """设置温度剖面"""
        self.temperature = temp_profile
    
    def DO_saturation(self, T: float, altitude: float = 0) -> float:
        """
        计算DO饱和浓度
        
        使用经验公式
        
        Parameters
        ----------
        T : float
            温度 (°C)
        altitude : float
            海拔高度 (m)
            
        Returns
        -------
        float
            饱和浓度 (mg/L)
        """
        # 标准大气压下的饱和浓度（Elmore and Hayes, 1960）
        DO_sat = 14.652 - 0.41022*T + 0.007991*T**2 - 0.000077774*T**3
        
        # 海拔修正（简化）
        if altitude > 0:
            pressure_correction = np.exp(-altitude / 8000)
            DO_sat *= pressure_correction
        
        return DO_sat
    
    def reaeration_rate(self, wind_speed: float = 3.0, temperature: float = 20.0) -> float:
        """
        计算复氧系数
        
        使用O'Connor-Dobbins公式
        
        Parameters
        ----------
        wind_speed : float
            风速 (m/s)
        temperature : float
            温度 (°C)
            
        Returns
        -------
        float
            复氧系数 (1/day)
        """
        # 简化模型：K_a ∝ wind_speed
        K_a_20 = 0.5 + 0.2 * wind_speed  # 20°C时的系数
        
        # 温度修正
        K_a = K_a_20 * 1.024**(temperature - 20)
        
        return K_a
    
    def oxygen_consumption_rate(self, depth: float) -> float:
        """
        计算耗氧速率
        
        Parameters
        ----------
        depth : float
            深度 (m)
            
        Returns
        -------
        float
            耗氧速率 (mg/L/day)
        """
        # 表层：藻类呼吸 + 有机物分解
        # 底层：底泥耗氧
        
        if depth < self.depth * 0.3:  # 表温层
            R = 0.5  # 较小的耗氧
        else:  # 底温层
            R = 2.0  # 较大的耗氧（底泥耗氧）
        
        return R
    
    def simulate_DO_profile(self, time_days: float = 30, wind_speed: float = 3.0) -> np.ndarray:
        """
        模拟DO剖面演变
        
        简化的DO动力学方程：
        dDO/dt = K_a(DO_sat - DO) - R
        
        Parameters
        ----------
        time_days : float
            模拟时间 (天)
        wind_speed : float
            风速 (m/s)
            
        Returns
        -------
        array
            最终DO剖面
        """
        dt = 1.0  # 时间步长（天）
        n_steps = int(time_days / dt)
        
        DO = self.DO.copy()
        
        for step in range(n_steps):
            # 对每一层
            for i in range(self.n_layers):
                T = self.temperature[i]
                z = self.z[i]
                
                # 饱和浓度
                DO_sat = self.DO_saturation(T)
                
                # 复氧系数（表层）
                if i == 0:  # 表层
                    K_a = self.reaeration_rate(wind_speed, T)
                    reaeration = K_a * (DO_sat - DO[i])
                else:
                    reaeration = 0
                
                # 耗氧速率
                R = self.oxygen_consumption_rate(z)
                
                # 更新DO
                dDO_dt = reaeration - R
                DO[i] += dDO_dt * dt
                
                # 确保DO不为负
                DO[i] = max(DO[i], 0)
        
        self.DO = DO
        return DO


class ReservoirStratificationAnalyzer:
    """
    水库分层分析器
    
    综合分析水温和DO
    """
    
    @staticmethod
    def classify_layers(thermal_model: ThermalStratificationModel,
                       do_model: DissolvedOxygenModel) -> Dict[str, Dict]:
        """
        划分水层
        
        Returns
        -------
        dict
            各层信息
        """
        thermocline_z = thermal_model.thermocline_depth()
        
        # 表温层
        epilimnion_mask = thermal_model.z < thermocline_z
        # 温跃层（thermocline前后2m）
        thermocline_mask = np.abs(thermal_model.z - thermocline_z) < 2.0
        # 底温层
        hypolimnion_mask = thermal_model.z > (thermocline_z + 2.0)
        
        result = {
            'epilimnion': {
                'depth_range': (0, thermocline_z),
                'mean_temp': np.mean(thermal_model.temperature[epilimnion_mask]) if np.any(epilimnion_mask) else 0,
                'mean_DO': np.mean(do_model.DO[epilimnion_mask]) if np.any(epilimnion_mask) else 0,
                'thickness': thermocline_z
            },
            'thermocline': {
                'depth': thermocline_z,
                'temp_gradient': np.max(np.abs(np.gradient(thermal_model.temperature, thermal_model.dz)))
            },
            'hypolimnion': {
                'depth_range': (thermocline_z + 2.0, thermal_model.depth),
                'mean_temp': np.mean(thermal_model.temperature[hypolimnion_mask]) if np.any(hypolimnion_mask) else 0,
                'mean_DO': np.mean(do_model.DO[hypolimnion_mask]) if np.any(hypolimnion_mask) else 0,
                'thickness': thermal_model.depth - thermocline_z - 2.0
            }
        }
        
        return result
    
    @staticmethod
    def fish_habitat_assessment(do_model: DissolvedOxygenModel,
                                min_DO_requirement: float = 4.0) -> Dict[str, float]:
        """
        评估鱼类可利用水层
        
        Parameters
        ----------
        do_model : DissolvedOxygenModel
            DO模型
        min_DO_requirement : float
            最低DO需求 (mg/L)
            
        Returns
        -------
        dict
            评估结果
        """
        # 找到满足DO要求的水层
        suitable_mask = do_model.DO >= min_DO_requirement
        
        if not np.any(suitable_mask):
            return {
                'suitable_thickness': 0,
                'suitable_ratio': 0,
                'status': '严重缺氧'
            }
        
        suitable_thickness = np.sum(suitable_mask) * do_model.dz
        suitable_ratio = suitable_thickness / do_model.depth
        
        if suitable_ratio > 0.8:
            status = '优秀'
        elif suitable_ratio > 0.6:
            status = '良好'
        elif suitable_ratio > 0.4:
            status = '一般'
        else:
            status = '较差'
        
        return {
            'suitable_thickness': suitable_thickness,
            'suitable_ratio': suitable_ratio,
            'min_DO': np.min(do_model.DO),
            'mean_DO': np.mean(do_model.DO),
            'status': status
        }


def create_summer_stratification(depth: float, n_layers: int = 20) -> ThermalStratificationModel:
    """
    创建典型夏季分层
    
    表层高温，底层低温
    """
    model = ThermalStratificationModel(depth, n_layers)
    
    # 生成温度剖面
    z_norm = model.z / depth  # 归一化深度
    
    # 表层28°C，底层8°C，中间过渡
    T_surface = 28.0
    T_bottom = 8.0
    
    # S型曲线
    temp_profile = T_bottom + (T_surface - T_bottom) / (1 + np.exp(20*(z_norm - 0.3)))
    
    model.set_initial_temperature(temp_profile)
    
    return model


def create_winter_stratification(depth: float, n_layers: int = 20) -> ThermalStratificationModel:
    """
    创建典型冬季分层
    
    温度相对均匀
    """
    model = ThermalStratificationModel(depth, n_layers)
    
    # 冬季温度较低且均匀
    z_norm = model.z / depth
    
    T_surface = 6.0
    T_bottom = 4.0
    
    # 微弱分层
    temp_profile = T_bottom + (T_surface - T_bottom) * (1 - z_norm)**2
    
    model.set_initial_temperature(temp_profile)
    
    return model
