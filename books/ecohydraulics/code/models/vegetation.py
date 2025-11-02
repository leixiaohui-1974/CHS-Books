"""
涉水植物水力模型
===============

实现植物-水流相互作用模型
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from .channel import RiverReach


class VegetationType:
    """
    植物类型类
    
    定义不同植物的水力特性
    
    Parameters
    ----------
    name : str
        植物名称
    height : float
        植物高度 (m)
    stem_diameter : float
        茎干直径 (m)
    drag_coefficient : float
        阻力系数 Cd
    density : float
        单位面积植物密度 (stems/m²)
    critical_velocity : float
        临界冲刷流速 (m/s)
    """
    
    def __init__(self, name: str, height: float, stem_diameter: float,
                 drag_coefficient: float, density: float, critical_velocity: float):
        self.name = name
        self.height = height  # m
        self.stem_diameter = stem_diameter  # m
        self.drag_coefficient = drag_coefficient
        self.density = density  # stems/m²
        self.critical_velocity = critical_velocity  # m/s
    
    def frontal_area_per_volume(self) -> float:
        """
        计算单位体积的迎流面积
        
        Returns
        -------
        float
            a = n * d * h，单位: m²/m³
        """
        # n: 密度 (stems/m²)
        # d: 直径 (m)
        # h: 高度 (m)
        # a = n * d (m⁻¹)
        return self.density * self.stem_diameter
    
    def __repr__(self):
        return f"VegetationType({self.name}, h={self.height}m, d={self.stem_diameter}m)"


class VegetatedChannel:
    """
    含植被河道模型
    
    计算植被对水流的影响
    
    Parameters
    ----------
    reach : RiverReach
        基础河段
    vegetation : VegetationType
        植物类型
    coverage : float
        植被覆盖率 (0-1)
    """
    
    def __init__(self, reach: RiverReach, vegetation: VegetationType, coverage: float):
        self.reach = reach
        self.vegetation = vegetation
        self.coverage = coverage  # 0-1
        
        if not 0 <= coverage <= 1:
            raise ValueError("植被覆盖率必须在0-1之间")
    
    def effective_roughness(self, h: float) -> float:
        """
        计算植被影响下的有效糙率
        
        使用综合糙率公式
        
        Parameters
        ----------
        h : float
            水深 (m)
            
        Returns
        -------
        float
            有效Manning糙率
        """
        # 如果植物未淹没
        if h <= self.vegetation.height:
            # 植物完全挺水或部分淹没
            # 使用Cowan公式或经验公式
            n_bare = self.reach.n  # 裸露河床糙率
            
            # 植被增加的糙率
            # 简化公式: n_veg = n_bare * (1 + k * coverage * (hveg/h))
            k = 2.0  # 经验系数
            ratio = min(self.vegetation.height / h, 1.0)
            n_eff = n_bare * (1 + k * self.coverage * ratio)
        else:
            # 植物完全淹没
            # 分层流动：下层有植物，上层无植物
            h_veg = self.vegetation.height
            h_clear = h - h_veg
            
            # 下层（有植物）的糙率
            n_lower = self.reach.n * (1 + 3 * self.coverage)
            
            # 上层（无植物）的糙率
            n_upper = self.reach.n
            
            # 加权平均（按水深加权）
            n_eff = (n_lower * h_veg + n_upper * h_clear) / h
        
        return n_eff
    
    def drag_force(self, h: float, v: float) -> float:
        """
        计算植被阻力
        
        F_d = 0.5 * ρ * Cd * A * v²
        
        Parameters
        ----------
        h : float
            水深 (m)
        v : float
            流速 (m/s)
            
        Returns
        -------
        float
            单位面积阻力 (N/m²)
        """
        rho = 1000  # 水的密度 kg/m³
        
        # 有效植物高度（考虑淹没）
        h_eff = min(h, self.vegetation.height)
        
        # 单位面积的迎流面积
        A_per_area = self.vegetation.density * self.vegetation.stem_diameter * h_eff * self.coverage
        
        # 阻力
        F_d = 0.5 * rho * self.vegetation.drag_coefficient * A_per_area * v**2
        
        return F_d
    
    def velocity_reduction_factor(self, h: float) -> float:
        """
        计算流速衰减因子
        
        有植被时的流速 / 无植被时的流速
        
        Parameters
        ----------
        h : float
            水深 (m)
            
        Returns
        -------
        float
            流速衰减因子 (0-1)
        """
        # 基于有效糙率的比值
        n_veg = self.effective_roughness(h)
        n_bare = self.reach.n
        
        # 从Manning公式: v ∝ n^(-1)
        # 因此 v_veg / v_bare = n_bare / n_veg
        factor = n_bare / n_veg
        
        return factor
    
    def velocity_manning_with_vegetation(self, h: float) -> float:
        """
        计算含植被时的流速
        
        Parameters
        ----------
        h : float
            水深 (m)
            
        Returns
        -------
        float
            流速 (m/s)
        """
        n_eff = self.effective_roughness(h)
        
        # 临时修改河段糙率
        original_n = self.reach.n
        self.reach.n = n_eff
        
        v = self.reach.velocity_manning(h)
        
        # 恢复原糙率
        self.reach.n = original_n
        
        return v
    
    def discharge_with_vegetation(self, h: float) -> float:
        """
        计算含植被时的流量
        
        Parameters
        ----------
        h : float
            水深 (m)
            
        Returns
        -------
        float
            流量 (m³/s)
        """
        A = self.reach.area(h)
        v = self.velocity_manning_with_vegetation(h)
        
        return A * v
    
    def check_stability(self, h: float, Q: float) -> Dict[str, any]:
        """
        检查植物稳定性
        
        判断植物是否会被冲刷
        
        Parameters
        ----------
        h : float
            水深 (m)
        Q : float
            流量 (m³/s)
            
        Returns
        -------
        dict
            稳定性评估结果
        """
        v = self.velocity_manning_with_vegetation(h)
        
        # 安全系数
        safety_factor = self.vegetation.critical_velocity / v if v > 0 else np.inf
        
        # 判断稳定性
        if safety_factor >= 2.0:
            stability = "安全"
        elif safety_factor >= 1.5:
            stability = "基本安全"
        elif safety_factor >= 1.0:
            stability = "临界"
        else:
            stability = "不稳定（可能冲刷）"
        
        return {
            'velocity': v,
            'critical_velocity': self.vegetation.critical_velocity,
            'safety_factor': safety_factor,
            'stability': stability,
            'is_stable': safety_factor >= 1.0
        }


class VegetationGrowthModel:
    """
    植物生长水力条件模型
    
    评估植物生长的水力适宜性
    """
    
    @staticmethod
    def submergence_duration(flow_series: np.ndarray, 
                            dates: np.ndarray,
                            elevation: float,
                            channel_bottom: float,
                            reach: RiverReach) -> Dict[str, float]:
        """
        计算淹水持续时间
        
        Parameters
        ----------
        flow_series : array
            流量时间序列 (m³/s)
        dates : array
            日期序列
        elevation : float
            植物种植高程 (m)
        channel_bottom : float
            河床底高程 (m)
        reach : RiverReach
            河段对象
            
        Returns
        -------
        dict
            淹水特征
        """
        # 计算每个流量对应的水深
        depths = []
        for Q in flow_series:
            h = reach.solve_depth(Q)
            water_surface = channel_bottom + h
            depths.append(water_surface)
        
        depths = np.array(depths)
        
        # 判断是否淹没
        submerged = depths > elevation
        
        # 淹没天数
        total_days = len(flow_series)
        submerged_days = np.sum(submerged)
        submergence_ratio = submerged_days / total_days
        
        # 最大连续淹没天数
        max_consecutive = VegetationGrowthModel._max_consecutive(submerged)
        
        # 年平均淹没深度
        submergence_depths = np.maximum(depths - elevation, 0)
        mean_submergence_depth = np.mean(submergence_depths[submerged]) if np.any(submerged) else 0
        
        return {
            'total_days': total_days,
            'submerged_days': submerged_days,
            'submergence_ratio': submergence_ratio,
            'max_consecutive_days': max_consecutive,
            'mean_submergence_depth': mean_submergence_depth
        }
    
    @staticmethod
    def _max_consecutive(boolean_array: np.ndarray) -> int:
        """计算最大连续True的数量"""
        if len(boolean_array) == 0:
            return 0
        
        max_count = 0
        current_count = 0
        
        for value in boolean_array:
            if value:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        
        return max_count
    
    @staticmethod
    def growth_suitability(submergence_ratio: float,
                          mean_velocity: float,
                          vegetation: VegetationType) -> Dict[str, any]:
        """
        评估植物生长适宜性
        
        Parameters
        ----------
        submergence_ratio : float
            淹水比例 (0-1)
        mean_velocity : float
            平均流速 (m/s)
        vegetation : VegetationType
            植物类型
            
        Returns
        -------
        dict
            适宜性评估
        """
        # 淹水适宜性（不同植物有不同的淹水耐受性）
        # 这里假设挺水植物偏好部分淹没（0.3-0.7）
        if 0.3 <= submergence_ratio <= 0.7:
            submergence_suitability = 1.0
        elif 0.1 <= submergence_ratio < 0.3 or 0.7 < submergence_ratio <= 0.9:
            submergence_suitability = 0.7
        elif submergence_ratio < 0.1 or submergence_ratio > 0.9:
            submergence_suitability = 0.3
        else:
            submergence_suitability = 0.5
        
        # 流速适宜性（不应超过临界流速）
        v_critical = vegetation.critical_velocity
        if mean_velocity < 0.3 * v_critical:
            velocity_suitability = 1.0
        elif mean_velocity < 0.6 * v_critical:
            velocity_suitability = 0.8
        elif mean_velocity < 0.9 * v_critical:
            velocity_suitability = 0.5
        else:
            velocity_suitability = 0.2
        
        # 综合适宜性
        overall_suitability = (submergence_suitability + velocity_suitability) / 2
        
        # 评级
        if overall_suitability >= 0.8:
            grade = "优秀"
        elif overall_suitability >= 0.6:
            grade = "良好"
        elif overall_suitability >= 0.4:
            grade = "一般"
        else:
            grade = "较差"
        
        return {
            'submergence_suitability': submergence_suitability,
            'velocity_suitability': velocity_suitability,
            'overall_suitability': overall_suitability,
            'grade': grade
        }


# 预设植物类型
def create_reed() -> VegetationType:
    """
    创建芦苇（Reed）植物类型
    
    典型的挺水植物
    """
    return VegetationType(
        name="芦苇",
        height=2.0,           # 2米高
        stem_diameter=0.01,   # 1cm直径
        drag_coefficient=1.2,
        density=50,           # 50 stems/m²
        critical_velocity=2.0 # 2 m/s
    )


def create_cattail() -> VegetationType:
    """
    创建香蒲（Cattail）植物类型
    
    挺水植物
    """
    return VegetationType(
        name="香蒲",
        height=1.5,
        stem_diameter=0.015,
        drag_coefficient=1.3,
        density=40,
        critical_velocity=1.5
    )


def create_submerged_plant() -> VegetationType:
    """
    创建沉水植物类型
    
    如金鱼藻等
    """
    return VegetationType(
        name="沉水植物",
        height=0.5,
        stem_diameter=0.005,
        drag_coefficient=1.0,
        density=100,
        critical_velocity=1.0
    )


def create_willow_shrub() -> VegetationType:
    """
    创建柳树灌木类型
    
    岸边灌木
    """
    return VegetationType(
        name="柳树灌木",
        height=3.0,
        stem_diameter=0.05,
        drag_coefficient=1.5,
        density=10,
        critical_velocity=3.0
    )
