"""城市水生态系统模型

本模块包含城市水生态系统相关模型：
- SpongeCityDesign: 海绵城市雨洪管理
- UrbanRiverRestoration: 城市河道生态修复
- RainGarden: 雨水花园/生物滞留系统
- UrbanFloodControl: 城市内涝生态化防治
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class SpongeCityDesign:
    """海绵城市雨洪管理模型（案例34）
    
    设计海绵城市设施，实现雨水源头控制和资源化利用
    """
    
    def __init__(self,
                 catchment_area: float,
                 imperviousness: float):
        """
        Parameters:
        -----------
        catchment_area : float
            汇水面积 (ha)
        imperviousness : float
            不透水率 (0-1)
        """
        self.A = catchment_area * 1e4  # m²
        self.imp = imperviousness
    
    def runoff_volume(self,
                     rainfall: float,
                     initial_loss: float = 2.0) -> Dict:
        """径流量计算
        
        Parameters:
        -----------
        rainfall : float
            降雨量 (mm)
        initial_loss : float
            初损 (mm)
        """
        # SCS-CN方法简化
        effective_rain = max(rainfall - initial_loss, 0)
        
        # 不同下垫面径流系数
        runoff_coef_imp = 0.9  # 不透水面
        runoff_coef_per = 0.1  # 透水面
        
        # 总径流系数
        runoff_coef = self.imp * runoff_coef_imp + (1 - self.imp) * runoff_coef_per
        
        # 径流量
        runoff_depth = effective_rain * runoff_coef  # mm
        runoff_volume = runoff_depth * self.A / 1000  # m³
        
        return {
            'rainfall': rainfall,
            'effective_rainfall': effective_rain,
            'runoff_coefficient': runoff_coef,
            'runoff_depth': runoff_depth,
            'runoff_volume': runoff_volume
        }
    
    def lid_facility_sizing(self,
                           design_rainfall: float,
                           facility_type: str) -> Dict:
        """LID设施规模设计
        
        Parameters:
        -----------
        design_rainfall : float
            设计降雨 (mm)
        facility_type : str
            设施类型: 'bioretention', 'permeable', 'green_roof', 'rain_barrel'
        """
        runoff = self.runoff_volume(design_rainfall)
        target_volume = runoff['runoff_volume']
        
        # 不同LID设施的参数
        facilities = {
            'bioretention': {
                'depth': 0.5,  # m
                'area_ratio': 0.05,  # 占汇水面积比例
                'retention': 20  # mm
            },
            'permeable': {
                'depth': 0.3,
                'area_ratio': 0.15,
                'retention': 15
            },
            'green_roof': {
                'depth': 0.15,
                'area_ratio': 0.3,
                'retention': 25
            },
            'rain_barrel': {
                'depth': 1.5,
                'area_ratio': 0.001,
                'retention': 50
            }
        }
        
        params = facilities.get(facility_type, facilities['bioretention'])
        
        # 设施面积
        facility_area = self.A * params['area_ratio']
        
        # 调蓄容积
        storage_volume = facility_area * params['depth']
        
        # 削减径流量
        reduction_volume = min(storage_volume, target_volume * 0.8)
        reduction_rate = reduction_volume / target_volume * 100
        
        return {
            'facility_type': facility_type,
            'facility_area': facility_area,
            'storage_depth': params['depth'],
            'storage_volume': storage_volume,
            'runoff_reduction': reduction_volume,
            'reduction_rate': reduction_rate,
            'cost_estimate': facility_area * 300  # 元/m²
        }
    
    def annual_control_rate(self,
                           rainfall_series: np.ndarray) -> Dict:
        """年径流总量控制率
        
        Parameters:
        -----------
        rainfall_series : np.ndarray
            年降雨序列 (mm)
        """
        n_events = len(rainfall_series)
        controlled_count = 0
        total_runoff = 0
        controlled_runoff = 0
        
        # 假设生物滞留设施
        facility = self.lid_facility_sizing(25, 'bioretention')
        storage_capacity = facility['storage_volume']
        
        for rain in rainfall_series:
            runoff = self.runoff_volume(rain)
            volume = runoff['runoff_volume']
            total_runoff += volume
            
            if volume <= storage_capacity:
                controlled_count += 1
                controlled_runoff += volume
            else:
                controlled_runoff += storage_capacity
        
        control_rate_count = controlled_count / n_events * 100
        control_rate_volume = controlled_runoff / total_runoff * 100
        
        return {
            'total_events': n_events,
            'controlled_events': controlled_count,
            'control_rate_count': control_rate_count,
            'total_runoff': total_runoff,
            'controlled_runoff': controlled_runoff,
            'control_rate_volume': control_rate_volume
        }
    
    def water_quality_improvement(self,
                                 inlet_concentration: Dict[str, float]) -> Dict:
        """水质改善效果
        
        Parameters:
        -----------
        inlet_concentration : Dict[str, float]
            入流浓度 {'TSS': xx, 'TN': xx, 'TP': xx, 'COD': xx}
        """
        # LID设施典型去除率（基于文献）
        removal_rates = {
            'TSS': 0.85,
            'TN': 0.45,
            'TP': 0.60,
            'COD': 0.55,
            'Cu': 0.70,
            'Zn': 0.75
        }
        
        outlet_conc = {}
        removal_mass = {}
        
        for pollutant, conc_in in inlet_concentration.items():
            removal_rate = removal_rates.get(pollutant, 0.5)
            conc_out = conc_in * (1 - removal_rate)
            outlet_conc[pollutant] = conc_out
            removal_mass[pollutant] = (conc_in - conc_out) * 1e-3  # kg/m³
        
        return {
            'inlet_concentration': inlet_concentration,
            'outlet_concentration': outlet_conc,
            'removal_rates': {k: removal_rates.get(k, 0.5) * 100 for k in inlet_concentration.keys()},
            'removal_mass': removal_mass
        }


class UrbanRiverRestoration:
    """城市河道生态修复模型（案例35）
    
    评估和设计城市河道生态修复方案
    """
    
    def __init__(self,
                 river_length: float,
                 channel_width: float,
                 average_depth: float):
        """
        Parameters:
        -----------
        river_length : float
            河道长度 (km)
        channel_width : float
            河道宽度 (m)
        average_depth : float
            平均水深 (m)
        """
        self.L = river_length * 1000  # m
        self.W = channel_width
        self.H = average_depth
        self.A_surface = self.L * self.W  # 水面面积
    
    def hydraulic_diversity_index(self,
                                  velocity_data: np.ndarray,
                                  depth_data: np.ndarray) -> float:
        """水力多样性指数
        
        Parameters:
        -----------
        velocity_data : np.ndarray
            流速数据 (m/s)
        depth_data : np.ndarray
            水深数据 (m)
        """
        # 计算Shannon多样性指数
        # 将流速和水深分组
        v_bins = np.histogram(velocity_data, bins=5)[0]
        d_bins = np.histogram(depth_data, bins=5)[0]
        
        # 计算概率
        v_prob = v_bins / np.sum(v_bins)
        d_prob = d_bins / np.sum(d_bins)
        
        # Shannon指数
        H_v = -np.sum(v_prob[v_prob > 0] * np.log(v_prob[v_prob > 0]))
        H_d = -np.sum(d_prob[d_prob > 0] * np.log(d_prob[d_prob > 0]))
        
        # 综合指数
        HDI = (H_v + H_d) / 2
        
        return HDI
    
    def habitat_suitability_index(self,
                                  velocity: float,
                                  depth: float,
                                  substrate_type: str) -> float:
        """生境适宜性指数
        
        Parameters:
        -----------
        velocity : float
            流速 (m/s)
        depth : float
            水深 (m)
        substrate_type : str
            底质类型: 'sand', 'gravel', 'cobble', 'boulder'
        """
        # 流速适宜性
        if velocity < 0.1:
            SI_v = 0.3
        elif velocity < 0.5:
            SI_v = 0.8 + 0.4 * (velocity - 0.1) / 0.4
        elif velocity < 1.0:
            SI_v = 1.0
        elif velocity < 1.5:
            SI_v = 1.0 - 0.6 * (velocity - 1.0) / 0.5
        else:
            SI_v = 0.4
        
        # 水深适宜性
        if depth < 0.2:
            SI_d = 0.2
        elif depth < 0.8:
            SI_d = 0.2 + 0.8 * (depth - 0.2) / 0.6
        elif depth < 2.0:
            SI_d = 1.0
        else:
            SI_d = 1.0 - 0.3 * min((depth - 2.0) / 2.0, 1.0)
        
        # 底质适宜性
        substrate_scores = {
            'sand': 0.4,
            'gravel': 0.8,
            'cobble': 1.0,
            'boulder': 0.7
        }
        SI_s = substrate_scores.get(substrate_type, 0.5)
        
        # 综合适宜性
        HSI = (SI_v * SI_d * SI_s) ** (1/3)
        
        return HSI
    
    def ecological_flow_requirement(self,
                                   base_flow: float) -> Dict:
        """生态流量需求
        
        Parameters:
        -----------
        base_flow : float
            基流 (m³/s)
        """
        # Tennant法
        flow_levels = {
            'optimal': base_flow * 0.60,
            'outstanding': base_flow * 0.40,
            'excellent': base_flow * 0.30,
            'good': base_flow * 0.20,
            'fair': base_flow * 0.10,
            'poor': base_flow * 0.10,
            'minimum': base_flow * 0.10
        }
        
        return flow_levels
    
    def riparian_vegetation_design(self,
                                  bank_slope: float,
                                  soil_type: str) -> Dict:
        """滨岸植被设计
        
        Parameters:
        -----------
        bank_slope : float
            岸坡坡度 (度)
        soil_type : str
            土壤类型: 'clay', 'loam', 'sand'
        """
        # 植被配置建议
        if bank_slope < 15:
            zone_config = {
                'water_edge': ['芦苇', '香蒲', '千屈菜'],
                'middle': ['狗牙根', '高羊茅', '早熟禾'],
                'upland': ['垂柳', '水杉', '池杉']
            }
            stability = '高'
        elif bank_slope < 30:
            zone_config = {
                'water_edge': ['芦苇', '水葱'],
                'middle': ['狗牙根', '黑麦草'],
                'upland': ['垂柳', '柽柳']
            }
            stability = '中'
        else:
            zone_config = {
                'water_edge': ['芦苇'],
                'middle': ['狗牙根'],
                'upland': ['柽柳', '沙棘']
            }
            stability = '低'
        
        return {
            'slope': bank_slope,
            'stability': stability,
            'vegetation_zones': zone_config,
            'maintenance': '中等' if bank_slope < 20 else '高'
        }
    
    def self_purification_capacity(self,
                                   flow_rate: float,
                                   temperature: float) -> Dict:
        """河流自净能力
        
        Parameters:
        -----------
        flow_rate : float
            流量 (m³/s)
        temperature : float
            水温 (°C)
        """
        # 复氧系数（基于经验公式）
        velocity = flow_rate / (self.W * self.H)
        K2_20 = 3.9 * velocity ** 0.5 / self.H ** 0.5  # 1/d @ 20°C
        K2 = K2_20 * 1.024 ** (temperature - 20)
        
        # 耗氧系数
        K1_20 = 0.1  # 1/d @ 20°C
        K1 = K1_20 * 1.047 ** (temperature - 20)
        
        # 饱和溶解氧
        DO_sat = 14.652 - 0.41022 * temperature + 0.007991 * temperature**2
        
        return {
            'reaeration_rate': K2,
            'deoxygenation_rate': K1,
            'saturated_DO': DO_sat,
            'self_purification': 'strong' if K2 > K1 * 2 else 'weak'
        }


class RainGarden:
    """雨水花园/生物滞留系统（案例36）
    
    设计和评估雨水花园的水文和水质功能
    """
    
    def __init__(self,
                 garden_area: float,
                 media_depth: float,
                 ponding_depth: float):
        """
        Parameters:
        -----------
        garden_area : float
            花园面积 (m²)
        media_depth : float
            介质层深度 (m)
        ponding_depth : float
            蓄水层深度 (m)
        """
        self.A = garden_area
        self.d_media = media_depth
        self.d_pond = ponding_depth
    
    def infiltration_rate(self,
                         soil_type: str = 'loam') -> float:
        """渗透速率
        
        Parameters:
        -----------
        soil_type : str
            介质类型: 'sand', 'loam', 'clay'
        """
        # 典型渗透速率 (mm/hr)
        rates = {
            'sand': 50,
            'loam': 25,
            'sandy_loam': 30,
            'clay': 5
        }
        return rates.get(soil_type, 25)
    
    def storage_capacity(self,
                        porosity: float = 0.4) -> Dict:
        """调蓄容量
        
        Parameters:
        -----------
        porosity : float
            孔隙率
        """
        # 表面蓄水容量
        surface_storage = self.A * self.d_pond
        
        # 介质层调蓄容量
        media_storage = self.A * self.d_media * porosity
        
        # 总容量
        total_storage = surface_storage + media_storage
        
        return {
            'surface_storage': surface_storage,
            'media_storage': media_storage,
            'total_storage': total_storage,
            'storage_depth': (total_storage / self.A) * 1000  # mm
        }
    
    def drawdown_time(self,
                     infiltration_rate: float) -> float:
        """排空时间 (小时)
        
        Parameters:
        -----------
        infiltration_rate : float
            渗透速率 (mm/hr)
        """
        storage = self.storage_capacity()
        total_depth = storage['storage_depth']  # mm
        
        time = total_depth / infiltration_rate
        return time
    
    def pollutant_removal_efficiency(self,
                                    inlet_load: Dict[str, float]) -> Dict:
        """污染物去除效率
        
        Parameters:
        -----------
        inlet_load : Dict[str, float]
            入流负荷 (kg/year)
        """
        # 雨水花园典型去除率
        removal_rates = {
            'TSS': 0.90,
            'TN': 0.50,
            'TP': 0.70,
            'Metals': 0.80,
            'Bacteria': 0.85
        }
        
        outlet_load = {}
        removal_amount = {}
        
        for pollutant, load in inlet_load.items():
            rate = removal_rates.get(pollutant, 0.6)
            outlet_load[pollutant] = load * (1 - rate)
            removal_amount[pollutant] = load * rate
        
        return {
            'removal_rates': {k: removal_rates.get(k, 0.6) * 100 for k in inlet_load.keys()},
            'inlet_load': inlet_load,
            'outlet_load': outlet_load,
            'removal_amount': removal_amount
        }
    
    def plant_selection(self,
                       water_tolerance: str,
                       sunlight: str) -> List[str]:
        """植物选择
        
        Parameters:
        -----------
        water_tolerance : str
            耐水性: 'high', 'medium', 'low'
        sunlight : str
            光照: 'full', 'partial', 'shade'
        """
        # 植物数据库（简化）
        plants = {
            'high': {
                'full': ['鸢尾', '千屈菜', '水葱', '黄菖蒲'],
                'partial': ['玉簪', '麦冬', '吉祥草'],
                'shade': ['蕨类', '常春藤']
            },
            'medium': {
                'full': ['萱草', '鼠尾草', '薰衣草'],
                'partial': ['八宝景天', '金娃娃萱草'],
                'shade': ['玉簪', '矾根']
            },
            'low': {
                'full': ['石竹', '矢车菊'],
                'partial': ['金鸡菊'],
                'shade': ['常春藤']
            }
        }
        
        return plants.get(water_tolerance, {}).get(sunlight, [])
    
    def cost_benefit_analysis(self,
                             construction_cost_per_m2: float,
                             annual_runoff_reduction: float) -> Dict:
        """成本效益分析
        
        Parameters:
        -----------
        construction_cost_per_m2 : float
            建设成本 (元/m²)
        annual_runoff_reduction : float
            年径流削减量 (m³)
        """
        # 建设成本
        construction_cost = self.A * construction_cost_per_m2
        
        # 维护成本（年）
        annual_maintenance = construction_cost * 0.03
        
        # 效益（避免的雨水处理费用）
        water_treatment_cost = 2.0  # 元/m³
        annual_benefit = annual_runoff_reduction * water_treatment_cost
        
        # 生态系统服务价值
        ecosystem_value = self.A * 50  # 元/m²/年
        total_annual_benefit = annual_benefit + ecosystem_value
        
        # 投资回收期
        payback = construction_cost / (total_annual_benefit - annual_maintenance)
        
        return {
            'construction_cost': construction_cost,
            'annual_maintenance': annual_maintenance,
            'annual_benefit': total_annual_benefit,
            'payback_period': payback,
            'npv_20years': -construction_cost + total_annual_benefit * 15  # 简化NPV
        }


class UrbanFloodControl:
    """城市内涝生态化防治模型（案例37）
    
    评估和设计城市内涝生态防治方案
    """
    
    def __init__(self,
                 district_area: float,
                 design_return_period: int):
        """
        Parameters:
        -----------
        district_area : float
            区域面积 (km²)
        design_return_period : int
            设计重现期 (年)
        """
        self.A = district_area * 1e6  # m²
        self.T = design_return_period
    
    def design_rainfall_intensity(self,
                                  duration: float,
                                  location: str = 'beijing') -> float:
        """设计暴雨强度 (mm/h)
        
        Parameters:
        -----------
        duration : float
            降雨历时 (min)
        location : str
            城市位置
        """
        # 暴雨强度公式（北京）
        if location == 'beijing':
            i = 2989 * (1 + 0.723 * np.log(self.T)) / (duration + 13.1) ** 0.886
        elif location == 'shanghai':
            i = 3449 * (1 + 0.902 * np.log(self.T)) / (duration + 15.9) ** 0.916
        else:  # 默认使用通用公式
            i = 3000 * (1 + 0.8 * np.log(self.T)) / (duration + 15) ** 0.9
        
        return i
    
    def runoff_calculation(self,
                          rainfall_intensity: float,
                          imperviousness: float) -> Dict:
        """径流计算
        
        Parameters:
        -----------
        rainfall_intensity : float
            降雨强度 (mm/h)
        imperviousness : float
            不透水率 (0-1)
        """
        # 径流系数
        psi = 0.9 * imperviousness + 0.1 * (1 - imperviousness)
        
        # 径流流量
        Q = psi * rainfall_intensity * self.A / 1000 / 3600  # m³/s
        
        # 峰值流量
        Q_peak = Q * 1.2
        
        return {
            'runoff_coefficient': psi,
            'rainfall_intensity': rainfall_intensity,
            'runoff_flow': Q,
            'peak_flow': Q_peak
        }
    
    def detention_basin_design(self,
                              inflow_volume: float,
                              outlet_capacity: float) -> Dict:
        """调蓄池设计
        
        Parameters:
        -----------
        inflow_volume : float
            入流总量 (m³)
        outlet_capacity : float
            出流能力 (m³/s)
        """
        # 调蓄容积（简化计算）
        storage_volume = inflow_volume * 0.5  # 削减50%峰值
        
        # 调蓄池尺寸
        depth = 3.0  # m（典型深度）
        area = storage_volume / depth
        
        # 排空时间
        drawdown_time = storage_volume / outlet_capacity / 3600  # hours
        
        return {
            'storage_volume': storage_volume,
            'basin_depth': depth,
            'basin_area': area,
            'outlet_capacity': outlet_capacity,
            'drawdown_time': drawdown_time
        }
    
    def green_infrastructure_effectiveness(self,
                                          lid_coverage: float) -> Dict:
        """绿色基础设施效能
        
        Parameters:
        -----------
        lid_coverage : float
            LID设施覆盖率 (%)
        """
        # 径流削减率（基于实测数据）
        runoff_reduction = 0.4 * (lid_coverage / 100) + 0.1 * (lid_coverage / 100) ** 2
        runoff_reduction = min(runoff_reduction, 0.6)  # 最大60%
        
        # 峰值削减
        peak_reduction = runoff_reduction * 1.2
        peak_reduction = min(peak_reduction, 0.7)
        
        # 水质改善
        pollutant_reduction = runoff_reduction * 0.8
        
        return {
            'lid_coverage': lid_coverage,
            'runoff_reduction': runoff_reduction * 100,
            'peak_reduction': peak_reduction * 100,
            'pollutant_reduction': pollutant_reduction * 100,
            'flood_risk_level': self._assess_flood_risk(peak_reduction)
        }
    
    def _assess_flood_risk(self, peak_reduction: float) -> str:
        """评估内涝风险等级"""
        if peak_reduction > 0.5:
            return '低风险'
        elif peak_reduction > 0.3:
            return '中风险'
        else:
            return '高风险'
    
    def integrated_management_strategy(self,
                                      budget: float) -> Dict:
        """综合管理策略
        
        Parameters:
        -----------
        budget : float
            预算 (万元)
        """
        # 不同措施的成本和效果
        measures = {
            '生物滞留': {'cost_per_m2': 300, 'effectiveness': 0.8},
            '透水铺装': {'cost_per_m2': 200, 'effectiveness': 0.5},
            '绿色屋顶': {'cost_per_m2': 400, 'effectiveness': 0.7},
            '调蓄池': {'cost_per_m3': 800, 'effectiveness': 0.9},
            '植草沟': {'cost_per_m': 150, 'effectiveness': 0.4}
        }
        
        # 优化配置（简化）
        total_cost = budget * 1e4  # 元
        
        # 分配预算
        allocation = {
            '生物滞留': 0.30,
            '透水铺装': 0.25,
            '绿色屋顶': 0.15,
            '调蓄池': 0.20,
            '植草沟': 0.10
        }
        
        # 计算综合效果
        total_effectiveness = 0
        for measure, ratio in allocation.items():
            total_effectiveness += measures[measure]['effectiveness'] * ratio
        
        return {
            'budget': budget,
            'allocation': allocation,
            'total_effectiveness': total_effectiveness * 100,
            'expected_reduction': total_effectiveness * 60  # 预期削减率
        }


def design_sponge_city_system(catchment_area: float,
                              imperviousness: float,
                              target_control_rate: float) -> Dict:
    """海绵城市系统集成设计
    
    Parameters:
    -----------
    catchment_area : float
        汇水面积 (ha)
    imperviousness : float
        不透水率 (0-1)
    target_control_rate : float
        目标控制率 (%)
    """
    sponge = SpongeCityDesign(catchment_area, imperviousness)
    
    # 年降雨序列（简化）
    rainfall_series = np.random.exponential(15, 365)
    
    # 计算年控制率
    result = sponge.annual_control_rate(rainfall_series)
    
    # 如果未达标，增加设施
    if result['control_rate_volume'] < target_control_rate:
        deficit = target_control_rate - result['control_rate_volume']
        additional_facilities = {
            'bioretention_area': catchment_area * 1e4 * 0.02,
            'permeable_pavement': catchment_area * 1e4 * 0.10,
            'green_roof': catchment_area * 1e4 * 0.05
        }
    else:
        additional_facilities = {}
    
    return {
        'catchment_area': catchment_area,
        'current_control_rate': result['control_rate_volume'],
        'target_control_rate': target_control_rate,
        'gap': max(target_control_rate - result['control_rate_volume'], 0),
        'additional_facilities': additional_facilities,
        'total_cost': sum(additional_facilities.values()) * 300 if additional_facilities else 0
    }
