"""鱼类产卵场水力条件模型

本模块实现鱼类产卵场（Spawning Ground）的水力分析，包括：
- 鱼卵沉降速度计算
- 悬浮流速阈值
- 漂流距离估算
- 涨水过程分析
- 底质适宜性评价
- 产卵场水力条件评估
"""

import numpy as np
from typing import Dict, Tuple, Optional, List

class FishEgg:
    """鱼卵模型
    
    描述鱼卵的物理特性和水力学行为
    """
    
    def __init__(self,
                 diameter: float,          # 鱼卵直径 (mm)
                 density: float = 1005.0,  # 鱼卵密度 (kg/m³)
                 species: str = "四大家鱼"):
        """
        初始化鱼卵模型
        
        Parameters:
        -----------
        diameter : float
            鱼卵直径 (mm)
        density : float
            鱼卵密度 (kg/m³)，略大于水的密度
        species : str
            鱼类种类
        """
        self.diameter = diameter  # mm
        self.density = density    # kg/m³
        self.species = species
        
        # 水的物理性质
        self.water_density = 1000.0  # kg/m³
        self.water_viscosity = 1.0e-3  # Pa·s (20°C)
        self.g = 9.81  # m/s²
    
    def settling_velocity(self) -> float:
        """计算鱼卵沉降速度（Stokes公式）
        
        对于球形颗粒在层流中的沉降：
        w_s = (g × (ρ_egg - ρ_water) × d²) / (18 × μ)
        
        Returns:
        --------
        float
            沉降速度 (m/s)
        """
        d = self.diameter / 1000.0  # 转换为 m
        
        # Stokes沉降速度
        w_s = (self.g * (self.density - self.water_density) * d**2) / \
              (18.0 * self.water_viscosity)
        
        return w_s
    
    def reynolds_number(self) -> float:
        """计算鱼卵的雷诺数
        
        Re = ρ × w_s × d / μ
        
        Returns:
        --------
        float
            雷诺数（无量纲）
        """
        w_s = self.settling_velocity()
        d = self.diameter / 1000.0
        
        Re = (self.water_density * w_s * d) / self.water_viscosity
        
        return Re
    
    def suspension_velocity_threshold(self, safety_factor: float = 1.2) -> float:
        """计算维持鱼卵悬浮的最小流速
        
        流速需要产生足够的紊动强度来抵消沉降
        
        Parameters:
        -----------
        safety_factor : float
            安全系数，默认1.2
        
        Returns:
        --------
        float
            最小悬浮流速 (m/s)
        """
        w_s = self.settling_velocity()
        
        # 经验公式：需要的流速约为沉降速度的10-20倍
        # 因为紊动强度与流速平方成正比
        v_min = safety_factor * np.sqrt(w_s * 10.0)
        
        return v_min


class SpawningGround:
    """产卵场模型
    
    评估产卵场的水力条件适宜性
    """
    
    def __init__(self,
                 reach_length: float,      # 河段长度 (m)
                 slope: float,             # 坡度
                 d50: float,               # 底质中值粒径 (mm)
                 egg: FishEgg):            # 鱼卵模型
        """
        初始化产卵场模型
        
        Parameters:
        -----------
        reach_length : float
            河段长度 (m)
        slope : float
            河床坡度（无量纲）
        d50 : float
            底质中值粒径 (mm)
        egg : FishEgg
            鱼卵模型
        """
        self.reach_length = reach_length
        self.slope = slope
        self.d50 = d50
        self.egg = egg
        
        self.g = 9.81
    
    def drift_distance(self, 
                      flow_velocity: float,
                      water_depth: float,
                      hatching_time: float = 24.0) -> float:
        """计算鱼卵漂流距离
        
        漂流距离 = 平均流速 × 孵化时间
        考虑沉降和垂向流速分布
        
        Parameters:
        -----------
        flow_velocity : float
            表层流速 (m/s)
        water_depth : float
            水深 (m)
        hatching_time : float
            孵化时间 (小时)，默认24小时
        
        Returns:
        --------
        float
            漂流距离 (m)
        """
        # 鱼卵主要在中下层，流速约为表层的0.6-0.8倍
        effective_velocity = flow_velocity * 0.7
        
        # 孵化时间转换为秒
        time_seconds = hatching_time * 3600.0
        
        # 漂流距离
        distance = effective_velocity * time_seconds
        
        return distance
    
    def optimal_flow_velocity_range(self) -> Tuple[float, float]:
        """确定最优产卵流速范围
        
        根据鱼卵悬浮要求和鱼类产卵行为
        
        Returns:
        --------
        tuple
            (最小流速, 最大流速) (m/s)
        """
        # 最小流速：维持鱼卵悬浮
        v_min = self.egg.suspension_velocity_threshold()
        
        # 最大流速：不能过大，否则冲走亲鱼
        # 四大家鱼产卵流速一般在0.8-1.5 m/s
        v_max = 1.5
        
        # 确保最小流速不超过最大流速
        v_min = max(0.8, min(v_min, v_max - 0.2))
        
        return v_min, v_max
    
    def substrate_suitability(self) -> Dict:
        """评估底质适宜性
        
        产卵场底质要求：
        - 卵石、砾石底床（d50 = 20-50 mm）
        - 稳定、不淤积
        
        Returns:
        --------
        dict
            底质评价结果
        """
        # 最优粒径范围
        d50_optimal_min = 20.0  # mm
        d50_optimal_max = 50.0  # mm
        
        if d50_optimal_min <= self.d50 <= d50_optimal_max:
            suitability = "优秀"
            score = 1.0
        elif 10.0 <= self.d50 < d50_optimal_min:
            suitability = "较好"
            score = 0.7
        elif d50_optimal_max < self.d50 <= 80.0:
            suitability = "较好"
            score = 0.7
        elif self.d50 < 10.0:
            suitability = "不适宜（过细，易淤积）"
            score = 0.3
        else:
            suitability = "不适宜（过粗）"
            score = 0.3
        
        result = {
            'd50_mm': self.d50,
            'optimal_range': (d50_optimal_min, d50_optimal_max),
            'suitability': suitability,
            'score': score
        }
        
        return result
    
    def water_level_rise_requirement(self, 
                                     flow_increase: float,
                                     channel_width: float,
                                     water_depth: float) -> float:
        """计算涨水幅度
        
        四大家鱼产卵需要涨水刺激
        
        Parameters:
        -----------
        flow_increase : float
            流量增幅 (m³/s)
        channel_width : float
            河道宽度 (m)
        water_depth : float
            原水深 (m)
        
        Returns:
        --------
        float
            水位涨幅 (m)
        """
        # 简化估算：ΔH ≈ ΔQ / (width × velocity_increase)
        # 这里使用更简单的估算
        velocity_increase = 0.2  # m/s，经验值
        delta_h = flow_increase / (channel_width * velocity_increase)
        
        return delta_h
    
    def spawning_condition_assessment(self,
                                      flow_velocity: float,
                                      water_depth: float,
                                      water_level_rise: float,
                                      channel_width: float = 200.0) -> Dict:
        """综合评估产卵场水力条件
        
        Parameters:
        -----------
        flow_velocity : float
            流速 (m/s)
        water_depth : float
            水深 (m)
        water_level_rise : float
            水位涨幅 (m/day)
        channel_width : float
            河道宽度 (m)
        
        Returns:
        --------
        dict
            综合评价结果
        """
        # 1. 流速评价
        v_min, v_max = self.optimal_flow_velocity_range()
        velocity_suitable = v_min <= flow_velocity <= v_max
        velocity_score = 1.0 if velocity_suitable else 0.5
        
        # 2. 水深评价（一般要求 > 2m）
        depth_suitable = water_depth >= 2.0
        depth_score = 1.0 if depth_suitable else 0.7
        
        # 3. 涨水评价（0.5-1.0 m/day）
        rise_suitable = 0.5 <= water_level_rise <= 1.5
        rise_score = 1.0 if rise_suitable else 0.6
        
        # 4. 底质评价
        substrate_result = self.substrate_suitability()
        substrate_score = substrate_result['score']
        
        # 5. 漂流距离评价（50-100 km为宜）
        drift_dist = self.drift_distance(flow_velocity, water_depth)
        drift_dist_km = drift_dist / 1000.0
        drift_suitable = 50.0 <= drift_dist_km <= 150.0
        drift_score = 1.0 if drift_suitable else 0.7
        
        # 综合评分（加权平均）
        weights = [0.25, 0.15, 0.25, 0.20, 0.15]  # 流速、水深、涨水、底质、漂流
        scores = [velocity_score, depth_score, rise_score, substrate_score, drift_score]
        overall_score = sum(w * s for w, s in zip(weights, scores))
        
        # 评级
        if overall_score >= 0.85:
            grade = "优秀"
        elif overall_score >= 0.70:
            grade = "良好"
        elif overall_score >= 0.55:
            grade = "中等"
        else:
            grade = "不适宜"
        
        assessment = {
            'velocity': {
                'value_ms': flow_velocity,
                'optimal_range': (v_min, v_max),
                'suitable': velocity_suitable,
                'score': velocity_score
            },
            'depth': {
                'value_m': water_depth,
                'requirement': '>= 2.0 m',
                'suitable': depth_suitable,
                'score': depth_score
            },
            'water_level_rise': {
                'value_m_per_day': water_level_rise,
                'optimal_range': (0.5, 1.5),
                'suitable': rise_suitable,
                'score': rise_score
            },
            'substrate': substrate_result,
            'drift_distance': {
                'value_km': drift_dist_km,
                'optimal_range': (50, 150),
                'suitable': drift_suitable,
                'score': drift_score
            },
            'overall_score': overall_score,
            'grade': grade
        }
        
        return assessment


def create_chinese_carp_egg(species: str = "草鱼") -> FishEgg:
    """创建四大家鱼鱼卵模型
    
    四大家鱼：青鱼、草鱼、鲢鱼、鳙鱼
    卵径约3-5mm，微粘性
    
    Parameters:
    -----------
    species : str
        鱼类种类
    
    Returns:
    --------
    FishEgg
        鱼卵模型
    """
    # 四大家鱼卵径相近
    diameter = 4.5  # mm
    density = 1005.0  # kg/m³，略大于水
    
    egg = FishEgg(diameter, density, species)
    
    return egg


def create_standard_spawning_ground(reach_length: float = 50000.0,
                                    d50: float = 30.0) -> SpawningGround:
    """创建标准产卵场
    
    Parameters:
    -----------
    reach_length : float
        河段长度 (m)，默认50 km
    d50 : float
        底质中值粒径 (mm)，默认30 mm
    
    Returns:
    --------
    SpawningGround
        产卵场模型
    """
    egg = create_chinese_carp_egg("四大家鱼")
    
    spawning_ground = SpawningGround(
        reach_length=reach_length,
        slope=0.0005,  # 缓坡
        d50=d50,
        egg=egg
    )
    
    return spawning_ground
