"""河口海岸生态系统模型

本模块包含河口海岸生态系统相关模型：
- SaltWedge: 河口盐水楔三维模拟
- MangroveHydrodynamics: 红树林湿地水动力
- EcologicalRevetment: 海岸带生态护岸
- EstuarineWetlandCarbon: 河口湿地碳汇功能
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class SaltWedge:
    """河口盐水楔三维模拟模型（案例38）
    
    模拟河口区域淡水与海水的混合过程
    """
    
    def __init__(self,
                 estuary_depth: float,
                 estuary_width: float,
                 river_discharge: float):
        """
        Parameters:
        -----------
        estuary_depth : float
            河口平均水深 (m)
        estuary_width : float
            河口宽度 (m)
        river_discharge : float
            径流量 (m³/s)
        """
        self.h = estuary_depth
        self.W = estuary_width
        self.Q_r = river_discharge
        self.g = 9.81
        self.rho_f = 1000.0  # 淡水密度 kg/m³
        self.rho_s = 1025.0  # 海水密度 kg/m³
    
    def densimetric_froude_number(self) -> float:
        """密度弗劳德数
        
        判断河口混合类型的关键参数
        """
        delta_rho = self.rho_s - self.rho_f
        g_prime = self.g * delta_rho / self.rho_f
        
        # 淡水流速
        u_f = self.Q_r / (self.W * self.h)
        
        # 密度弗劳德数
        Fr = u_f / np.sqrt(g_prime * self.h)
        
        return Fr
    
    def mixing_type_classification(self) -> Dict:
        """河口混合类型分类"""
        Fr = self.densimetric_froude_number()
        
        if Fr > 1.0:
            mixing_type = "高度混合型"
            description = "淡水动能大，垂向混合充分"
        elif Fr > 0.08:
            mixing_type = "部分混合型"
            description = "存在一定垂向分层"
        else:
            mixing_type = "盐水楔型"
            description = "明显的淡水-海水界面"
        
        return {
            'froude_number': Fr,
            'mixing_type': mixing_type,
            'description': description
        }
    
    def salt_wedge_length(self,
                         tidal_range: float = 2.0) -> float:
        """盐水楔长度估算 (km)
        
        Parameters:
        -----------
        tidal_range : float
            潮差 (m)
        """
        Fr = self.densimetric_froude_number()
        
        # 经验公式（基于Hansen-Rattray）
        if Fr < 0.08:
            # 盐水楔型
            L = self.h * 100 / np.sqrt(Fr)  # m
        else:
            # 混合型
            L = self.h * 50
        
        # 潮汐影响
        L = L * (1 + 0.5 * tidal_range / self.h)
        
        return L / 1000  # 转换为km
    
    def salinity_distribution(self,
                             distance: np.ndarray,
                             depth_fraction: float) -> np.ndarray:
        """盐度分布 (ppt)
        
        Parameters:
        -----------
        distance : np.ndarray
            距河口距离 (km)
        depth_fraction : float
            相对水深 (0=表层, 1=底层)
        """
        L = self.salt_wedge_length()
        
        # 简化的盐度模型
        # 表层（淡水影响大）
        S_surface = 35 * (1 - np.exp(-distance / L))
        
        # 底层（海水影响大）
        S_bottom = 35 * (1 - 0.5 * np.exp(-distance / (0.5 * L)))
        
        # 线性插值
        S = S_surface + depth_fraction * (S_bottom - S_surface)
        
        return S
    
    def stratification_parameter(self,
                                surface_salinity: float,
                                bottom_salinity: float) -> float:
        """分层参数
        
        Parameters:
        -----------
        surface_salinity : float
            表层盐度 (ppt)
        bottom_salinity : float
            底层盐度 (ppt)
        """
        delta_S = bottom_salinity - surface_salinity
        S_avg = (surface_salinity + bottom_salinity) / 2
        
        # 分层参数（0=完全混合，1=强分层）
        if S_avg > 0:
            alpha = delta_S / S_avg
        else:
            alpha = 0
        
        return alpha
    
    def residence_time(self,
                      estuary_length: float) -> float:
        """河口水体停留时间 (天)
        
        Parameters:
        -----------
        estuary_length : float
            河口段长度 (km)
        """
        # 河口容积
        V = estuary_length * 1000 * self.W * self.h  # m³
        
        # 停留时间
        T = V / self.Q_r / 86400  # 天
        
        return T
    
    def ecological_impact_assessment(self,
                                    avg_salinity: float) -> Dict:
        """生态影响评估
        
        Parameters:
        -----------
        avg_salinity : float
            平均盐度 (ppt)
        """
        # 根据盐度判断生态类型
        if avg_salinity < 0.5:
            zone = "淡水区"
            species = ["淡水鱼类", "淡水植物"]
            biodiversity = "低"
        elif avg_salinity < 5:
            zone = "低盐区"
            species = ["广盐性鱼类", "芦苇", "香蒲"]
            biodiversity = "高"
        elif avg_salinity < 18:
            zone = "半咸水区"
            species = ["河口鱼类", "海三棱藨草"]
            biodiversity = "最高"
        else:
            zone = "高盐区"
            species = ["海水鱼类", "海草"]
            biodiversity = "中"
        
        return {
            'salinity': avg_salinity,
            'ecological_zone': zone,
            'typical_species': species,
            'biodiversity': biodiversity
        }


class MangroveHydrodynamics:
    """红树林湿地水动力模型（案例39）
    
    分析红树林对波浪、潮流的消减作用
    """
    
    def __init__(self,
                 forest_width: float,
                 tree_density: float,
                 tree_diameter: float):
        """
        Parameters:
        -----------
        forest_width : float
            红树林带宽度 (m)
        tree_density : float
            树木密度 (株/m²)
        tree_diameter : float
            平均树干直径 (m)
        """
        self.W = forest_width
        self.n = tree_density
        self.d = tree_diameter
        self.g = 9.81
    
    def drag_coefficient(self,
                        velocity: float) -> float:
        """红树林阻力系数
        
        Parameters:
        -----------
        velocity : float
            流速 (m/s)
        """
        # Reynolds数
        nu = 1e-6  # 运动粘度
        Re = velocity * self.d / nu
        
        # 阻力系数（经验公式）
        if Re < 1e5:
            Cd = 1.2
        else:
            Cd = 0.8 + 0.4 * np.exp(-Re / 1e5)
        
        return Cd
    
    def wave_attenuation(self,
                        incident_wave_height: float,
                        wave_period: float,
                        water_depth: float) -> Dict:
        """波浪消减
        
        Parameters:
        -----------
        incident_wave_height : float
            入射波高 (m)
        wave_period : float
            波周期 (s)
        water_depth : float
            水深 (m)
        """
        # 波长（浅水波）
        L = self.g * wave_period**2 / (2 * np.pi) * np.tanh(2 * np.pi * water_depth / 10)
        
        # 波速
        c = L / wave_period
        
        # 红树林引起的消减系数（经验公式）
        # 基于Mazda et al. (1997)
        alpha = 0.002 * self.n * self.d * incident_wave_height / water_depth
        
        # 透射波高
        transmitted_wave_height = incident_wave_height * np.exp(-alpha * self.W)
        
        # 消减率
        attenuation_rate = (1 - transmitted_wave_height / incident_wave_height) * 100
        
        return {
            'incident_height': incident_wave_height,
            'transmitted_height': transmitted_wave_height,
            'attenuation_rate': attenuation_rate,
            'wavelength': L,
            'wave_celerity': c
        }
    
    def current_reduction(self,
                         inlet_velocity: float,
                         water_depth: float) -> Dict:
        """潮流消减
        
        Parameters:
        -----------
        inlet_velocity : float
            入流流速 (m/s)
        water_depth : float
            水深 (m)
        """
        Cd = self.drag_coefficient(inlet_velocity)
        
        # 植被阻力参数
        a = self.n * self.d  # 单位体积植被面积
        
        # 动量方程求解（简化）
        # du/dx = -Cd * a * u^2 / h
        
        # 数值积分
        dx = 1.0  # m
        n_steps = int(self.W / dx)
        u = inlet_velocity
        
        velocities = [u]
        distances = [0]
        
        for i in range(n_steps):
            du = -Cd * a * u**2 / water_depth * dx
            u = max(u + du, 0.01)  # 防止负速度
            velocities.append(u)
            distances.append((i + 1) * dx)
        
        outlet_velocity = velocities[-1]
        reduction_rate = (1 - outlet_velocity / inlet_velocity) * 100
        
        return {
            'inlet_velocity': inlet_velocity,
            'outlet_velocity': outlet_velocity,
            'reduction_rate': reduction_rate,
            'velocity_profile': np.array(velocities),
            'distances': np.array(distances)
        }
    
    def sediment_trapping_efficiency(self,
                                    inlet_ssc: float,
                                    current_velocity: float) -> float:
        """泥沙捕获效率
        
        Parameters:
        -----------
        inlet_ssc : float
            入流悬沙浓度 (mg/L)
        current_velocity : float
            流速 (m/s)
        """
        # 沉降速度（假设细颗粒）
        w_s = 0.001  # m/s
        
        # 停留时间
        residence_time = self.W / current_velocity  # s
        
        # 捕获效率
        eta = 1 - np.exp(-w_s * residence_time / 1.0)  # 简化
        eta = min(eta, 0.95)  # 最大95%
        
        return eta * 100
    
    def coastal_protection_value(self,
                                storm_wave_height: float,
                                protected_area: float) -> Dict:
        """海岸防护价值评估
        
        Parameters:
        -----------
        storm_wave_height : float
            风暴波高 (m)
        protected_area : float
            防护面积 (ha)
        """
        # 波浪消减
        attenuation = self.wave_attenuation(storm_wave_height, 8.0, 2.0)
        
        # 减少的波浪能量
        E_reduced = 1000 * self.g * (storm_wave_height**2 - 
                                     attenuation['transmitted_height']**2) / 8
        
        # 经济价值估算（避免的防波堤建设）
        dike_cost_per_meter = 5000  # 元/m
        equivalent_length = protected_area * 1e4 / 100  # m
        
        protection_value = E_reduced / 1000 * equivalent_length * dike_cost_per_meter
        
        return {
            'wave_attenuation': attenuation['attenuation_rate'],
            'energy_reduction': E_reduced,
            'protection_value': protection_value / 1e4,  # 万元
            'protected_area': protected_area
        }


class EcologicalRevetment:
    """海岸带生态护岸模型（案例40）
    
    设计和评估生态护岸工程
    """
    
    def __init__(self,
                 revetment_length: float,
                 slope_angle: float,
                 design_wave_height: float):
        """
        Parameters:
        -----------
        revetment_length : float
            护岸长度 (m)
        slope_angle : float
            坡度角 (度)
        design_wave_height : float
            设计波高 (m)
        """
        self.L = revetment_length
        self.alpha = slope_angle
        self.H_design = design_wave_height
        self.g = 9.81
    
    def wave_runup(self,
                   wave_height: float,
                   wave_period: float) -> float:
        """波浪爬高 (m)
        
        Parameters:
        -----------
        wave_height : float
            波高 (m)
        wave_period : float
            周期 (s)
        """
        # 波陡
        s = wave_height / (self.g * wave_period**2 / (2 * np.pi))
        
        # 坡度因子
        tan_alpha = np.tan(np.radians(self.alpha))
        xi = tan_alpha / np.sqrt(s)
        
        # Hunt公式
        if xi < 3:
            R = wave_height * 1.5 * xi
        else:
            R = wave_height * 4.0
        
        return R
    
    def stability_analysis(self,
                          stone_size: float,
                          stone_density: float = 2650) -> Dict:
        """稳定性分析
        
        Parameters:
        -----------
        stone_size : float
            块石粒径 (m)
        stone_density : float
            块石密度 (kg/m³)
        """
        # Hudson公式
        rho_w = 1025  # 海水密度
        K_D = 2.0  # 稳定系数（抛石）
        
        # 所需块石重量
        W_required = (rho_w * self.g * self.H_design**3) / \
                     (K_D * (stone_density / rho_w - 1)**3 * 
                      np.sin(np.radians(self.alpha))**3)
        
        # 实际块石重量
        W_actual = stone_density * (4/3) * np.pi * (stone_size/2)**3
        
        # 安全系数
        safety_factor = W_actual / W_required
        
        # 稳定性评价
        if safety_factor >= 1.5:
            stability = "安全"
        elif safety_factor >= 1.0:
            stability = "基本安全"
        else:
            stability = "不安全"
        
        return {
            'required_weight': W_required,
            'actual_weight': W_actual,
            'safety_factor': safety_factor,
            'stability': stability
        }
    
    def vegetation_design(self,
                         tidal_zone: str) -> Dict:
        """植被配置设计
        
        Parameters:
        -----------
        tidal_zone : str
            潮区类型: 'high', 'middle', 'low'
        """
        # 不同潮区的植被配置
        vegetation_schemes = {
            'high': {
                'species': ['海滨木槿', '厚藤', '黄槿'],
                'density': 4,  # 株/m²
                'root_depth': 1.5,
                'wave_resistance': '高'
            },
            'middle': {
                'species': ['芦苇', '海三棱藨草', '盐地碱蓬'],
                'density': 16,
                'root_depth': 0.8,
                'wave_resistance': '中'
            },
            'low': {
                'species': ['海草床', '大叶藻'],
                'density': 100,
                'root_depth': 0.3,
                'wave_resistance': '低'
            }
        }
        
        scheme = vegetation_schemes.get(tidal_zone, vegetation_schemes['middle'])
        
        # 计算护岸面积（斜坡）
        slope_length = 10  # m（假设）
        area = self.L * slope_length
        
        # 所需植株数
        total_plants = int(area * scheme['density'])
        
        return {
            'tidal_zone': tidal_zone,
            'species': scheme['species'],
            'planting_density': scheme['density'],
            'total_plants': total_plants,
            'root_depth': scheme['root_depth'],
            'wave_resistance': scheme['wave_resistance']
        }
    
    def ecological_function_assessment(self) -> Dict:
        """生态功能评估"""
        # 生境提供
        habitat_area = self.L * 5  # m²（假设5m宽度）
        
        # 生物多样性评分（0-100）
        biodiversity_score = 75
        
        # 水质净化能力
        filtration_rate = habitat_area * 0.1  # m³/d
        
        # 景观价值
        landscape_score = 85
        
        return {
            'habitat_area': habitat_area,
            'biodiversity_score': biodiversity_score,
            'filtration_rate': filtration_rate,
            'landscape_score': landscape_score,
            'overall_score': (biodiversity_score + landscape_score) / 2
        }
    
    def cost_comparison(self,
                       traditional_cost_per_m: float = 5000) -> Dict:
        """成本对比分析
        
        Parameters:
        -----------
        traditional_cost_per_m : float
            传统护岸成本 (元/m)
        """
        # 生态护岸成本组成
        stone_cost = self.L * 2000  # 元
        vegetation_cost = self.L * 500
        construction_cost = self.L * 1000
        
        ecological_total = stone_cost + vegetation_cost + construction_cost
        traditional_total = self.L * traditional_cost_per_m
        
        # 生命周期成本（20年）
        maintenance_eco = ecological_total * 0.02 * 20  # 年维护2%
        maintenance_trad = traditional_total * 0.05 * 20  # 年维护5%
        
        lifecycle_eco = ecological_total + maintenance_eco
        lifecycle_trad = traditional_total + maintenance_trad
        
        savings = lifecycle_trad - lifecycle_eco
        
        return {
            'ecological_initial': ecological_total / 1e4,
            'traditional_initial': traditional_total / 1e4,
            'ecological_lifecycle': lifecycle_eco / 1e4,
            'traditional_lifecycle': lifecycle_trad / 1e4,
            'lifecycle_savings': savings / 1e4,
            'cost_ratio': ecological_total / traditional_total
        }


class EstuarineWetlandCarbon:
    """河口湿地碳汇功能模型（案例41）
    
    评估河口湿地的固碳能力
    """
    
    def __init__(self,
                 wetland_area: float,
                 vegetation_type: str):
        """
        Parameters:
        -----------
        wetland_area : float
            湿地面积 (ha)
        vegetation_type : str
            植被类型: 'mangrove', 'salt_marsh', 'seagrass'
        """
        self.A = wetland_area * 1e4  # m²
        self.veg_type = vegetation_type
    
    def net_primary_production(self) -> float:
        """净初级生产力 (gC/m²/year)"""
        # 不同植被类型的NPP
        npp_values = {
            'mangrove': 800,
            'salt_marsh': 600,
            'seagrass': 400,
            'mudflat': 50
        }
        
        npp = npp_values.get(self.veg_type, 500)
        return npp
    
    def carbon_sequestration_rate(self) -> Dict:
        """碳固定速率
        
        Returns:
        --------
        Dict with various carbon sequestration metrics
        """
        npp = self.net_primary_production()
        
        # 碳固定效率（NPP转化为长期储存）
        burial_efficiency = {
            'mangrove': 0.35,
            'salt_marsh': 0.25,
            'seagrass': 0.20
        }
        
        eff = burial_efficiency.get(self.veg_type, 0.25)
        
        # 年碳埋藏速率
        burial_rate = npp * eff  # gC/m²/year
        
        # 总碳固定量
        total_sequestration = burial_rate * self.A / 1e6  # tC/year
        
        # CO2当量
        co2_equivalent = total_sequestration * 44 / 12  # tCO2/year
        
        return {
            'npp': npp,
            'burial_efficiency': eff * 100,
            'burial_rate': burial_rate,
            'total_sequestration': total_sequestration,
            'co2_equivalent': co2_equivalent
        }
    
    def soil_carbon_stock(self,
                         soil_depth: float = 1.0) -> float:
        """土壤碳储量 (tC/ha)
        
        Parameters:
        -----------
        soil_depth : float
            土壤深度 (m)
        """
        # 不同湿地类型的土壤碳密度
        soil_c_density = {
            'mangrove': 250,  # tC/ha/m
            'salt_marsh': 180,
            'seagrass': 120
        }
        
        density = soil_c_density.get(self.veg_type, 180)
        stock = density * soil_depth
        
        return stock
    
    def carbon_accumulation_rate(self) -> float:
        """碳累积速率 (mm/year)
        
        沉积物垂直累积速率
        """
        rates = {
            'mangrove': 5.0,
            'salt_marsh': 3.0,
            'seagrass': 2.0
        }
        
        return rates.get(self.veg_type, 3.0)
    
    def blue_carbon_potential(self,
                             project_lifetime: int = 20) -> Dict:
        """蓝碳项目潜力评估
        
        Parameters:
        -----------
        project_lifetime : int
            项目周期 (年)
        """
        seq = self.carbon_sequestration_rate()
        
        # 总固碳量
        total_carbon = seq['total_sequestration'] * project_lifetime
        total_co2 = seq['co2_equivalent'] * project_lifetime
        
        # 碳价格（假设）
        carbon_price = 50  # 元/tCO2
        
        # 经济价值
        economic_value = total_co2 * carbon_price
        
        # 附加生态服务价值
        biodiversity_value = self.A / 1e4 * 2000 * project_lifetime  # 元
        water_purification_value = self.A / 1e4 * 1500 * project_lifetime
        
        total_ecosystem_value = (economic_value + biodiversity_value + 
                                water_purification_value)
        
        return {
            'project_lifetime': project_lifetime,
            'total_carbon_sequestration': total_carbon,
            'total_co2_equivalent': total_co2,
            'carbon_credit_value': economic_value / 1e4,  # 万元
            'biodiversity_value': biodiversity_value / 1e4,
            'water_purification_value': water_purification_value / 1e4,
            'total_ecosystem_value': total_ecosystem_value / 1e4,
            'annual_value_per_ha': total_ecosystem_value / project_lifetime / (self.A / 1e4) / 1e4
        }
    
    def greenhouse_gas_emissions(self,
                                 soil_organic_carbon: float) -> Dict:
        """温室气体排放评估
        
        Parameters:
        -----------
        soil_organic_carbon : float
            土壤有机碳含量 (%)
        """
        # CH4排放（厌氧条件）
        # 简化模型
        if self.veg_type == 'mangrove':
            ch4_flux = 15  # mgCH4/m²/day
        elif self.veg_type == 'salt_marsh':
            ch4_flux = 5
        else:
            ch4_flux = 2
        
        # N2O排放
        n2o_flux = 0.1  # mgN2O/m²/day
        
        # 年总排放
        annual_ch4 = ch4_flux * 365 * self.A / 1e9  # tCH4/year
        annual_n2o = n2o_flux * 365 * self.A / 1e9  # tN2O/year
        
        # CO2当量（CH4的GWP=25, N2O的GWP=298）
        ch4_co2eq = annual_ch4 * 25
        n2o_co2eq = annual_n2o * 298
        
        # 净碳平衡
        seq = self.carbon_sequestration_rate()
        net_balance = seq['co2_equivalent'] - ch4_co2eq - n2o_co2eq
        
        return {
            'ch4_emission': annual_ch4,
            'n2o_emission': annual_n2o,
            'ch4_co2_equivalent': ch4_co2eq,
            'n2o_co2_equivalent': n2o_co2eq,
            'total_ghg_emission': ch4_co2eq + n2o_co2eq,
            'carbon_sequestration': seq['co2_equivalent'],
            'net_carbon_balance': net_balance,
            'is_carbon_sink': net_balance > 0
        }


def simulate_storm_surge_protection(mangrove_width: float,
                                    surge_height: float,
                                    tree_density: float) -> Dict:
    """模拟红树林对风暴潮的防护
    
    Parameters:
    -----------
    mangrove_width : float
        红树林带宽度 (m)
    surge_height : float
        风暴潮高度 (m)
    tree_density : float
        树木密度 (株/m²)
    """
    mangrove = MangroveHydrodynamics(mangrove_width, tree_density, 0.15)
    
    # 风暴波浪消减
    wave_result = mangrove.wave_attenuation(surge_height * 0.5, 10.0, surge_height)
    
    # 风暴流速消减
    current_result = mangrove.current_reduction(2.0, surge_height)
    
    # 综合防护效果
    protection_score = (wave_result['attenuation_rate'] + 
                       current_result['reduction_rate']) / 2
    
    return {
        'wave_attenuation': wave_result,
        'current_reduction': current_result,
        'protection_score': protection_score,
        'risk_level': 'low' if protection_score > 50 else 'high'
    }
