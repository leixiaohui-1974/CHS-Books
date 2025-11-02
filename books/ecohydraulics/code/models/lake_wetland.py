"""湖泊与湿地生态水力学模型（案例29-33）"""

import numpy as np
from typing import Dict, List, Tuple

class LakeHydrodynamics:
    """湖泊水动力学模型（案例29）
    
    模拟风生流、温度分层和水质输移
    """
    
    def __init__(self, 
                 lake_area: float,
                 average_depth: float,
                 fetch_length: float):
        """
        Parameters:
        -----------
        lake_area : float
            湖泊面积 (km²)
        average_depth : float
            平均水深 (m)
        fetch_length : float
            风区长度 (m)
        """
        self.A = lake_area * 1e6  # 转换为m²
        self.h = average_depth
        self.F = fetch_length
        
        # 物理常数
        self.rho_water = 1000.0  # 水密度 kg/m³
        self.rho_air = 1.225  # 空气密度 kg/m³
        self.g = 9.81  # 重力加速度 m/s²
    
    def wind_stress(self, wind_speed: float) -> float:
        """计算风应力 (Pa)
        
        Parameters:
        -----------
        wind_speed : float
            10m高度风速 (m/s)
        """
        # 拖曳系数（经验公式）
        if wind_speed < 3:
            Cd = 0.0012
        elif wind_speed < 10:
            Cd = (0.49 + 0.065 * wind_speed) * 1e-3
        else:
            Cd = 0.0013
        
        tau = Cd * self.rho_air * wind_speed ** 2
        return tau
    
    def surface_current_velocity(self, wind_speed: float) -> float:
        """表层流速 (m/s)
        
        经验公式：表层流速约为风速的2-3%
        """
        u_surface = 0.03 * wind_speed
        return u_surface
    
    def wind_setup(self, wind_speed: float) -> float:
        """风壅水高度 (m)
        
        风作用下湖泊下风端水位壅高
        """
        tau = self.wind_stress(wind_speed)
        # 简化公式
        delta_h = (tau * self.F) / (self.rho_water * self.g * self.h)
        return delta_h
    
    def wave_parameters(self, wind_speed: float) -> Dict:
        """风浪参数计算
        
        Returns:
        --------
        Dict : 包含波高、波长、周期等参数
        """
        # SMB法简化公式
        g = self.g
        F = self.F / 1000  # km
        U = wind_speed
        
        # 无因次参数
        gF_U2 = g * F * 1000 / (U ** 2)
        
        # 有效波高 (m)
        if gF_U2 < 1000:
            H_s = 0.21 * (U ** 2 / g) * (gF_U2 ** 0.5)
        else:
            H_s = 0.21 * (U ** 2 / g) * (1000 ** 0.5)
        
        # 平均周期 (s)
        if gF_U2 < 1000:
            T_m = 0.67 * (U / g) * (gF_U2 ** 0.33)
        else:
            T_m = 0.67 * (U / g) * (1000 ** 0.33)
        
        # 波长 (m)
        L = (g * T_m ** 2) / (2 * np.pi)
        
        return {
            'significant_wave_height': H_s,
            'mean_period': T_m,
            'wavelength': L,
            'wave_steepness': H_s / L
        }
    
    def thermal_stratification(self, 
                               surface_temp: float,
                               bottom_temp: float) -> Dict:
        """温度分层计算
        
        Parameters:
        -----------
        surface_temp : float
            表层温度 (°C)
        bottom_temp : float
            底层温度 (°C)
        """
        # 温跃层深度估算（夏季典型值）
        thermocline_depth = self.h * 0.4
        
        # 密度差
        def water_density(T):
            """水的密度随温度变化"""
            return 1000 * (1 - (T - 4) ** 2 / 200)
        
        rho_surface = water_density(surface_temp)
        rho_bottom = water_density(bottom_temp)
        
        # 理查森数（分层稳定性指标）
        delta_rho = rho_bottom - rho_surface
        Ri = (self.g * delta_rho * thermocline_depth) / (rho_surface * 0.01 ** 2)
        
        return {
            'thermocline_depth': thermocline_depth,
            'surface_density': rho_surface,
            'bottom_density': rho_bottom,
            'density_difference': delta_rho,
            'richardson_number': Ri,
            'stratification_status': 'strong' if Ri > 10 else ('moderate' if Ri > 1 else 'weak')
        }
    
    def nutrient_mixing(self, 
                       wind_speed: float,
                       surface_conc: float,
                       bottom_conc: float) -> float:
        """营养盐垂向混合
        
        Parameters:
        -----------
        wind_speed : float
            风速 (m/s)
        surface_conc : float
            表层浓度 (mg/L)
        bottom_conc : float
            底层浓度 (mg/L)
        
        Returns:
        --------
        float : 垂向扩散系数 (m²/s)
        """
        # 垂向扩散系数（经验公式）
        u_star = np.sqrt(self.wind_stress(wind_speed) / self.rho_water)
        Kz = 0.01 * u_star * self.h
        
        return Kz
    
    def algae_bloom_risk(self,
                        temperature: float,
                        total_phosphorus: float,
                        total_nitrogen: float,
                        light_extinction: float) -> Dict:
        """藻类水华风险评估
        
        Parameters:
        -----------
        temperature : float
            水温 (°C)
        total_phosphorus : float
            总磷浓度 (mg/L)
        total_nitrogen : float
            总氮浓度 (mg/L)
        light_extinction : float
            光消减系数 (1/m)
        """
        # 温度因子
        if 15 <= temperature <= 30:
            temp_factor = 1.0
        elif temperature < 15:
            temp_factor = 0.5
        else:
            temp_factor = 0.7
        
        # 营养盐因子
        if total_phosphorus > 0.05:
            nutrient_factor = 1.0
        elif total_phosphorus > 0.02:
            nutrient_factor = 0.7
        else:
            nutrient_factor = 0.3
        
        # 光照因子
        euphotic_depth = 4.6 / light_extinction  # 真光层深度
        if euphotic_depth > self.h * 0.5:
            light_factor = 1.0
        else:
            light_factor = euphotic_depth / (self.h * 0.5)
        
        # 综合风险指数
        risk_index = temp_factor * nutrient_factor * light_factor
        
        if risk_index > 0.8:
            risk_level = "高风险"
        elif risk_index > 0.5:
            risk_level = "中风险"
        else:
            risk_level = "低风险"
        
        return {
            'temperature_factor': temp_factor,
            'nutrient_factor': nutrient_factor,
            'light_factor': light_factor,
            'euphotic_depth': euphotic_depth,
            'risk_index': risk_index,
            'risk_level': risk_level
        }


class ConstructedWetland:
    """人工湿地模型（案例30）
    
    水力停留时间（HRT）优化设计
    """
    
    def __init__(self,
                 length: float,
                 width: float,
                 depth: float,
                 porosity: float = 0.4):
        """
        Parameters:
        -----------
        length : float
            湿地长度 (m)
        width : float
            湿地宽度 (m)
        depth : float
            湿地深度 (m)
        porosity : float
            孔隙率（表面流：1.0，潜流：0.3-0.5）
        """
        self.L = length
        self.W = width
        self.h = depth
        self.n = porosity
        
        self.volume = length * width * depth * porosity
    
    def hydraulic_retention_time(self, flow_rate: float) -> float:
        """水力停留时间 (天)
        
        Parameters:
        -----------
        flow_rate : float
            进水流量 (m³/d)
        """
        HRT = self.volume / flow_rate
        return HRT
    
    def effective_volume_ratio(self, 
                              tracer_recovery: np.ndarray,
                              time_steps: np.ndarray) -> float:
        """有效容积比
        
        通过示踪剂试验确定短流和死区
        
        Parameters:
        -----------
        tracer_recovery : np.ndarray
            示踪剂回收曲线
        time_steps : np.ndarray
            时间序列
        """
        # 理论停留时间
        theoretical_HRT = np.sum(time_steps * tracer_recovery) / np.sum(tracer_recovery)
        
        # 峰值时间
        peak_time = time_steps[np.argmax(tracer_recovery)]
        
        # 有效容积比
        e = peak_time / theoretical_HRT
        
        return e
    
    def pollutant_removal(self,
                         inlet_conc: float,
                         HRT: float,
                         pollutant_type: str) -> Dict:
        """污染物去除计算
        
        Parameters:
        -----------
        inlet_conc : float
            进水浓度 (mg/L)
        HRT : float
            水力停留时间 (天)
        pollutant_type : str
            污染物类型：'COD', 'BOD', 'TN', 'TP', 'NH3N'
        """
        # 一级动力学去除系数 (1/d)
        k_values = {
            'COD': 0.5,
            'BOD': 0.7,
            'TN': 0.3,
            'TP': 0.2,
            'NH3N': 0.4
        }
        
        k = k_values.get(pollutant_type, 0.3)
        
        # 出水浓度
        outlet_conc = inlet_conc * np.exp(-k * HRT)
        
        # 去除率
        removal_rate = (inlet_conc - outlet_conc) / inlet_conc * 100
        
        # 去除负荷
        removal_load = (inlet_conc - outlet_conc) * 1e-3  # kg/m³
        
        return {
            'inlet_concentration': inlet_conc,
            'outlet_concentration': outlet_conc,
            'removal_rate': removal_rate,
            'removal_coefficient': k,
            'removal_load': removal_load
        }
    
    def optimal_HRT_design(self,
                          target_removal: float,
                          inlet_conc: float,
                          pollutant_type: str) -> Dict:
        """最优HRT设计
        
        Parameters:
        -----------
        target_removal : float
            目标去除率 (%)
        inlet_conc : float
            进水浓度 (mg/L)
        pollutant_type : str
            污染物类型
        """
        # 一级动力学系数
        k_values = {
            'COD': 0.5,
            'BOD': 0.7,
            'TN': 0.3,
            'TP': 0.2,
            'NH3N': 0.4
        }
        k = k_values.get(pollutant_type, 0.3)
        
        # 所需HRT
        target_conc = inlet_conc * (1 - target_removal / 100)
        HRT_required = -np.log(target_conc / inlet_conc) / k
        
        # 设计流量
        design_flow = self.volume / HRT_required
        
        # 湿地面积负荷
        area = self.L * self.W
        hydraulic_loading = design_flow / area
        
        return {
            'required_HRT': HRT_required,
            'design_flow_rate': design_flow,
            'hydraulic_loading': hydraulic_loading,
            'target_concentration': target_conc,
            'area': area
        }
    
    def aspect_ratio_optimization(self,
                                  target_HRT: float,
                                  total_area: float) -> Dict:
        """长宽比优化
        
        长宽比影响短流和死区
        
        Parameters:
        -----------
        target_HRT : float
            目标停留时间 (天)
        total_area : float
            总面积 (m²)
        """
        # 推荐长宽比范围：3:1 到 10:1
        ratios = np.array([3, 5, 7, 10])
        
        results = []
        for ratio in ratios:
            W = np.sqrt(total_area / ratio)
            L = W * ratio
            
            # 估算有效容积比（经验公式）
            e = 0.5 + 0.4 * (1 - np.exp(-ratio / 5))
            
            # 实际HRT
            actual_HRT = target_HRT / e
            
            results.append({
                'length_width_ratio': ratio,
                'length': L,
                'width': W,
                'effective_volume_ratio': e,
                'actual_HRT': actual_HRT
            })
        
        # 选择最接近目标HRT的方案
        differences = [abs(r['actual_HRT'] - target_HRT) for r in results]
        optimal_idx = np.argmin(differences)
        
        return {
            'all_scenarios': results,
            'optimal_scenario': results[optimal_idx],
            'optimal_ratio': ratios[optimal_idx]
        }


def simulate_lake_wind_event(lake: LakeHydrodynamics,
                             wind_speeds: np.ndarray,
                             duration_hours: int) -> Dict:
    """模拟湖泊风事件
    
    Parameters:
    -----------
    lake : LakeHydrodynamics
        湖泊对象
    wind_speeds : np.ndarray
        风速时间序列 (m/s)
    duration_hours : int
        持续时间 (小时)
    """
    results = {
        'time': np.arange(0, duration_hours, 1),
        'wind_speed': wind_speeds,
        'surface_velocity': [],
        'wind_setup': [],
        'wave_height': []
    }
    
    for U in wind_speeds:
        u_surf = lake.surface_current_velocity(U)
        setup = lake.wind_setup(U)
        waves = lake.wave_parameters(U)
        
        results['surface_velocity'].append(u_surf)
        results['wind_setup'].append(setup)
        results['wave_height'].append(waves['significant_wave_height'])
    
    return results


def design_wetland_system(target_removal_rate: float,
                          inlet_flow: float,
                          inlet_concentration: float,
                          pollutant: str) -> Dict:
    """人工湿地系统设计
    
    Parameters:
    -----------
    target_removal_rate : float
        目标去除率 (%)
    inlet_flow : float
        进水流量 (m³/d)
    inlet_concentration : float
        进水浓度 (mg/L)
    pollutant : str
        污染物类型
    """
    # 初步尺寸估算
    # 假设HRT = 3天，深度 = 0.6m
    HRT_initial = 3.0
    depth = 0.6
    porosity = 0.4
    
    volume = inlet_flow * HRT_initial
    area = volume / (depth * porosity)
    
    # 长宽比取5:1
    width = np.sqrt(area / 5)
    length = width * 5
    
    # 创建湿地对象
    wetland = ConstructedWetland(length, width, depth, porosity)
    
    # 验证去除率
    actual_HRT = wetland.hydraulic_retention_time(inlet_flow)
    removal = wetland.pollutant_removal(inlet_concentration, actual_HRT, pollutant)
    
    # 如果不满足要求，迭代优化
    if removal['removal_rate'] < target_removal_rate:
        optimal_design = wetland.optimal_HRT_design(
            target_removal_rate, inlet_concentration, pollutant
        )
        # 重新计算尺寸
        HRT_required = optimal_design['required_HRT']
        volume = inlet_flow * HRT_required
        area = volume / (depth * porosity)
        width = np.sqrt(area / 5)
        length = width * 5
        
        wetland = ConstructedWetland(length, width, depth, porosity)
    
    return {
        'dimensions': {
            'length': length,
            'width': width,
            'depth': depth,
            'area': area,
            'volume': volume
        },
        'hydraulics': {
            'HRT': wetland.hydraulic_retention_time(inlet_flow),
            'hydraulic_loading': inlet_flow / area
        },
        'performance': wetland.pollutant_removal(
            inlet_concentration,
            wetland.hydraulic_retention_time(inlet_flow),
            pollutant
        )
    }
