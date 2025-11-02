"""生态护岸水力设计模型

本模块实现生态护岸水力特性计算，包括：
- 护岸前流速分布
- 植被护岸阻力
- 庇护所评估
- 稳定性验算
"""

import numpy as np
from typing import Dict, List, Tuple, Optional


class EcologicalRevetment:
    """生态护岸模型
    
    计算不同类型生态护岸的水力特性
    """
    
    def __init__(self,
                 revetment_type: str,
                 height: float,
                 width: float,
                 porosity: float = 0.4):
        """
        Parameters:
        -----------
        revetment_type : str
            护岸类型（'植被护坡', '石笼', '生态袋', '格宾'）
        height : float
            护岸高度 (m)
        width : float
            护岸宽度/厚度 (m)
        porosity : float
            孔隙率（0-1）
        """
        self.type = revetment_type
        self.height = height
        self.width = width
        self.porosity = porosity
    
    def roughness_coefficient(self) -> float:
        """计算护岸粗糙系数（Manning n）"""
        # 不同护岸类型的粗糙系数
        roughness_dict = {
            '植被护坡': 0.060,  # 草皮护坡
            '石笼': 0.045,      # 石笼网
            '生态袋': 0.035,    # 植生袋
            '格宾': 0.040,      # 格宾网箱
            '混凝土': 0.015     # 对比
        }
        
        return roughness_dict.get(self.type, 0.035)
    
    def velocity_reduction_factor(self) -> float:
        """计算流速削减系数
        
        护岸前流速 = 削减系数 × 主流流速
        """
        # 基于孔隙率和粗糙度
        n = self.roughness_coefficient()
        
        # 经验公式
        reduction = 0.3 + 0.4 * self.porosity + 0.3 * (0.06 - n) / 0.06
        
        return max(0.2, min(reduction, 0.8))
    
    def drag_coefficient(self) -> float:
        """计算阻力系数"""
        # 多孔介质阻力
        if self.porosity > 0.3:
            Cd = 1.2 * (1 - self.porosity) ** 2
        else:
            Cd = 2.0
        
        return Cd
    
    def shelter_area_ratio(self, channel_width: float) -> float:
        """计算庇护所面积比例
        
        Parameters:
        -----------
        channel_width : float
            河道宽度 (m)
        """
        # 护岸前低流速区宽度
        shelter_width = self.width * (1 + 0.5 * self.porosity)
        
        # 庇护所占河道比例
        ratio = shelter_width / channel_width
        
        return min(ratio, 0.3)  # 最大30%


class VegetatedRevetment(EcologicalRevetment):
    """植被护岸模型
    
    考虑植被-水流相互作用
    """
    
    def __init__(self,
                 height: float,
                 coverage: float,
                 stem_diameter: float = 0.005,
                 stem_density: float = 1000.0):
        """
        Parameters:
        -----------
        height : float
            植被高度 (m)
        coverage : float
            植被覆盖度（0-1）
        stem_diameter : float
            茎秆直径 (m)
        stem_density : float
            茎秆密度 (根/m²)
        """
        super().__init__('植被护坡', height, 2.0, porosity=1-coverage)
        self.coverage = coverage
        self.d = stem_diameter
        self.m = stem_density
    
    def vegetation_drag_coefficient(self) -> float:
        """植被阻力系数"""
        # Kouwen-Unny公式
        Cd_veg = 2.0 + 3.0 * self.coverage
        
        return Cd_veg
    
    def effective_roughness(self, water_depth: float, velocity: float) -> float:
        """计算植被有效糙率
        
        Parameters:
        -----------
        water_depth : float
            水深 (m)
        velocity : float
            流速 (m/s)
        """
        # 植被淹没比
        submergence = self.height / water_depth
        
        if submergence >= 1.0:  # 非淹没
            # Manning-Strickler公式修正
            n_veg = 0.06 * (1 + 2 * self.coverage)
        else:  # 淹没
            # 部分淹没，阻力减小
            n_veg = 0.035 * (1 + self.coverage * submergence)
        
        return n_veg
    
    def root_reinforcement(self, soil_cohesion: float = 10.0) -> float:
        """估算根系加固效果
        
        Parameters:
        -----------
        soil_cohesion : float
            土壤粘聚力 (kPa)
        
        Returns:
        --------
        float
            加固后粘聚力 (kPa)
        """
        # 根系贡献的附加粘聚力
        root_contribution = 5.0 * self.coverage  # 简化公式
        
        return soil_cohesion + root_contribution


class RevetmentStability:
    """护岸稳定性分析"""
    
    def __init__(self,
                 revetment: EcologicalRevetment,
                 slope_angle: float,
                 water_depth: float,
                 velocity: float):
        """
        Parameters:
        -----------
        revetment : EcologicalRevetment
            护岸对象
        slope_angle : float
            边坡角度（度）
        water_depth : float
            水深 (m)
        velocity : float
            流速 (m/s)
        """
        self.revetment = revetment
        self.slope = np.deg2rad(slope_angle)
        self.h = water_depth
        self.v = velocity
    
    def shear_stress(self) -> float:
        """计算护岸表面剪应力
        
        Returns:
        --------
        float
            剪应力 (Pa)
        """
        rho = 1000.0  # 水密度
        Cd = self.revetment.drag_coefficient()
        
        # 护岸前流速
        v_local = self.v * self.revetment.velocity_reduction_factor()
        
        # 剪应力
        tau = 0.5 * rho * Cd * v_local ** 2
        
        return tau
    
    def critical_velocity(self, particle_size: float = 0.02) -> float:
        """计算临界冲刷流速
        
        Parameters:
        -----------
        particle_size : float
            护岸材料粒径 (m)
        """
        # Shields-Lane公式简化
        rho = 1000.0
        rho_s = 2650.0
        g = 9.81
        
        # 临界剪应力
        tau_c = 0.05 * (rho_s - rho) * g * particle_size
        
        # 临界流速
        v_c = np.sqrt(2 * tau_c / (rho * self.revetment.drag_coefficient()))
        
        return v_c
    
    def stability_factor(self, particle_size: float = 0.02) -> float:
        """计算稳定安全系数
        
        安全系数 = 临界流速 / 实际流速
        """
        v_c = self.critical_velocity(particle_size)
        v_actual = self.v * self.revetment.velocity_reduction_factor()
        
        SF = v_c / v_actual if v_actual > 0 else 10.0
        
        return SF
    
    def slope_stability_assessment(self) -> Dict:
        """边坡稳定性综合评价"""
        tau = self.shear_stress()
        SF = self.stability_factor()
        
        # 稳定性评级
        if SF > 2.0:
            stability = "安全"
            risk = "低"
        elif SF > 1.5:
            stability = "基本安全"
            risk = "中"
        else:
            stability = "不安全"
            risk = "高"
        
        # 边坡角度评价
        slope_deg = np.rad2deg(self.slope)
        if slope_deg < 30:
            slope_status = "缓坡"
        elif slope_deg < 45:
            slope_status = "中等"
        else:
            slope_status = "陡坡"
        
        return {
            'shear_stress': tau,
            'safety_factor': SF,
            'stability': stability,
            'erosion_risk': risk,
            'slope_angle': slope_deg,
            'slope_status': slope_status
        }


def design_ecological_revetment(channel_width: float,
                                water_depth: float,
                                velocity: float,
                                slope_angle: float,
                                revetment_type: str = '植被护坡') -> Dict:
    """生态护岸综合设计
    
    Parameters:
    -----------
    channel_width : float
        河道宽度 (m)
    water_depth : float
        设计水深 (m)
    velocity : float
        设计流速 (m/s)
    slope_angle : float
        边坡角度（度）
    revetment_type : str
        护岸类型
    
    Returns:
    --------
    dict
        设计成果
    """
    # 创建护岸对象
    if revetment_type == '植被护坡':
        revetment = VegetatedRevetment(
            height=0.5,
            coverage=0.7,
            stem_diameter=0.005,
            stem_density=1000.0
        )
        n_eff = revetment.effective_roughness(water_depth, velocity)
        root_cohesion = revetment.root_reinforcement()
    else:
        revetment = EcologicalRevetment(
            revetment_type=revetment_type,
            height=1.0,
            width=0.5,
            porosity=0.4
        )
        n_eff = revetment.roughness_coefficient()
        root_cohesion = None
    
    # 稳定性分析
    stability = RevetmentStability(revetment, slope_angle, water_depth, velocity)
    stab_result = stability.slope_stability_assessment()
    
    # 水力特性
    v_reduction = revetment.velocity_reduction_factor()
    shelter_ratio = revetment.shelter_area_ratio(channel_width)
    
    # 庇护所面积
    shelter_area = shelter_ratio * channel_width * 100  # 每100m河段
    
    result = {
        'revetment_type': revetment_type,
        'roughness': n_eff,
        'velocity_reduction': v_reduction,
        'shelter_ratio': shelter_ratio,
        'shelter_area_per_100m': shelter_area,
        'stability': stab_result
    }
    
    if root_cohesion is not None:
        result['root_reinforcement'] = root_cohesion
    
    return result
