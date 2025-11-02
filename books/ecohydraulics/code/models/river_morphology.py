"""河流形态多样性设计模型

本模块实现河流形态设计，包括：
- 深潭-浅滩序列设计
- 弯道水流计算
- 河床稳定性分析
- 水力多样性评价
"""

import numpy as np
from typing import Dict, List, Tuple, Optional


class PoolRiffleSequence:
    """深潭-浅滩序列设计模型
    
    基于自然河道形态特征，设计深潭-浅滩交替序列
    """
    
    def __init__(self, 
                 channel_width: float,
                 average_depth: float,
                 slope: float,
                 discharge: float):
        """
        Parameters:
        -----------
        channel_width : float
            河道宽度 (m)
        average_depth : float
            平均水深 (m)
        slope : float
            河道坡度
        discharge : float
            设计流量 (m³/s)
        """
        self.width = channel_width
        self.h_avg = average_depth
        self.slope = slope
        self.Q = discharge
    
    def pool_spacing(self) -> float:
        """计算深潭间距
        
        经验公式：间距 = 5-7倍河宽
        """
        return 6.0 * self.width  # 取中值
    
    def pool_depth(self) -> float:
        """计算深潭设计水深
        
        经验：深潭深度 = 1.5-2倍平均水深
        """
        return 1.75 * self.h_avg  # 取中值
    
    def riffle_depth(self) -> float:
        """计算浅滩水深
        
        浅滩深度 = 0.5-0.8倍平均水深
        """
        return 0.65 * self.h_avg
    
    def design_profile(self, reach_length: float) -> Tuple[np.ndarray, np.ndarray]:
        """设计深潭-浅滩纵剖面
        
        Parameters:
        -----------
        reach_length : float
            河段长度 (m)
        
        Returns:
        --------
        tuple
            (距离数组, 水深数组)
        """
        spacing = self.pool_spacing()
        n_pools = int(reach_length / spacing)
        
        # 生成距离点
        x = np.linspace(0, reach_length, n_pools * 20)
        
        # 深潭和浅滩深度
        h_pool = self.pool_depth()
        h_riffle = self.riffle_depth()
        
        # 生成正弦曲线模拟深潭-浅滩序列
        h = self.h_avg + 0.5 * (h_pool - h_riffle) * np.sin(2 * np.pi * x / spacing)
        
        return x, h
    
    def velocity_distribution(self, x: np.ndarray, h: np.ndarray) -> np.ndarray:
        """计算流速分布
        
        使用连续性方程：Q = v * A
        """
        A = self.width * h
        v = self.Q / A
        
        return v
    
    def hydraulic_diversity(self, velocities: np.ndarray) -> Dict:
        """计算水力多样性指数
        
        使用Shannon多样性指数
        """
        # 将流速分为5个等级
        bins = np.linspace(velocities.min(), velocities.max(), 6)
        hist, _ = np.histogram(velocities, bins=bins)
        
        # 计算概率
        p = hist / np.sum(hist)
        p = p[p > 0]  # 移除0值
        
        # Shannon指数
        shannon = -np.sum(p * np.log(p))
        
        # Simpson指数
        simpson = 1 - np.sum(p ** 2)
        
        return {
            'shannon_index': shannon,
            'simpson_index': simpson,
            'velocity_range': velocities.max() - velocities.min(),
            'velocity_cv': np.std(velocities) / np.mean(velocities)
        }


class MeanderChannel:
    """弯道河流模型
    
    计算弯道水流特性和环流
    """
    
    def __init__(self,
                 channel_width: float,
                 meander_radius: float,
                 water_depth: float,
                 slope: float):
        """
        Parameters:
        -----------
        channel_width : float
            河道宽度 (m)
        meander_radius : float
            弯道半径 (m)
        water_depth : float
            水深 (m)
        slope : float
            河道坡度
        """
        self.B = channel_width
        self.R = meander_radius
        self.h = water_depth
        self.S = slope
    
    def velocity_ratio(self) -> float:
        """计算弯道内外岸流速比
        
        经验公式
        """
        # 弯道影响系数
        k = self.B / self.R
        
        # 外岸流速 / 内岸流速
        ratio = 1 + 0.5 * k
        
        return ratio
    
    def secondary_flow_strength(self) -> float:
        """计算次生环流强度
        
        Returns:
        --------
        float
            环流强度系数（无量纲）
        """
        # Rozovskii公式
        k = self.B / self.R
        Fr = self.froude_number()
        
        # 环流强度
        circulation = 7.0 * k * np.sqrt(Fr)
        
        return min(circulation, 1.0)  # 限制最大值
    
    def froude_number(self) -> float:
        """计算Froude数"""
        g = 9.81
        v = np.sqrt(g * self.h * self.S)  # 估算平均流速
        Fr = v / np.sqrt(g * self.h)
        
        return Fr
    
    def bend_scour_depth(self) -> float:
        """计算弯道冲刷深度
        
        外岸冲刷深度估算
        """
        # 经验公式：冲刷深度 = (1.5-2.0) × 平均水深
        scour_factor = 1.75 + 0.5 * (self.B / self.R)
        
        return min(scour_factor * self.h, 3.0 * self.h)


class BedStability:
    """河床稳定性分析
    
    评估河床在设计流量下的稳定性
    """
    
    def __init__(self,
                 bed_material_d50: float,
                 water_depth: float,
                 slope: float,
                 velocity: float):
        """
        Parameters:
        -----------
        bed_material_d50 : float
            床沙中值粒径 (mm)
        water_depth : float
            水深 (m)
        slope : float
            河道坡度
        velocity : float
            流速 (m/s)
        """
        self.d50 = bed_material_d50 / 1000.0  # 转换为m
        self.h = water_depth
        self.S = slope
        self.v = velocity
    
    def shields_stress(self) -> float:
        """计算Shields应力参数"""
        rho = 1000.0  # 水密度
        rho_s = 2650.0  # 泥沙密度
        g = 9.81
        
        tau = rho * g * self.h * self.S  # 床面剪应力
        tau_c = (rho_s - rho) * g * self.d50  # 临界剪应力
        
        theta = tau / tau_c
        
        return theta
    
    def critical_velocity(self) -> float:
        """计算起动流速
        
        使用Hjulström曲线简化公式
        """
        # 经验公式（适用于粗砂和砾石）
        v_c = 0.2 * (self.d50 * 1000) ** 0.5  # d50单位mm
        
        return v_c
    
    def stability_assessment(self) -> Dict:
        """综合稳定性评价"""
        theta = self.shields_stress()
        v_c = self.critical_velocity()
        
        # 稳定性判断
        if theta < 0.03:
            stability = "稳定"
            risk = "低"
        elif theta < 0.06:
            stability = "基本稳定"
            risk = "中"
        else:
            stability = "不稳定"
            risk = "高"
        
        # 流速判断
        if self.v < v_c:
            velocity_status = "不起动"
        elif self.v < 1.5 * v_c:
            velocity_status = "弱输移"
        else:
            velocity_status = "强输移"
        
        return {
            'shields_stress': theta,
            'critical_velocity': v_c,
            'actual_velocity': self.v,
            'stability': stability,
            'erosion_risk': risk,
            'transport_status': velocity_status
        }


def design_naturalized_channel(width: float,
                               length: float,
                               slope: float,
                               discharge: float,
                               d50: float) -> Dict:
    """近自然河道综合设计
    
    Parameters:
    -----------
    width : float
        河道宽度 (m)
    length : float
        河段长度 (m)
    slope : float
        河道坡度
    discharge : float
        设计流量 (m³/s)
    d50 : float
        床沙中值粒径 (mm)
    
    Returns:
    --------
    dict
        设计成果
    """
    # 估算平均水深
    h_avg = (discharge / (width * np.sqrt(9.81 * slope))) ** (2.0/3.0)
    
    # 深潭-浅滩设计
    pr_seq = PoolRiffleSequence(width, h_avg, slope, discharge)
    x, h = pr_seq.design_profile(length)
    v = pr_seq.velocity_distribution(x, h)
    diversity = pr_seq.hydraulic_diversity(v)
    
    # 弯道设计
    meander_r = 2.5 * width
    meander = MeanderChannel(width, meander_r, h_avg, slope)
    
    # 稳定性分析
    stability = BedStability(d50, h_avg, slope, np.mean(v))
    stability_result = stability.stability_assessment()
    
    return {
        'pool_spacing': pr_seq.pool_spacing(),
        'pool_depth': pr_seq.pool_depth(),
        'riffle_depth': pr_seq.riffle_depth(),
        'profile': (x, h, v),
        'hydraulic_diversity': diversity,
        'meander_radius': meander_r,
        'velocity_ratio': meander.velocity_ratio(),
        'secondary_flow': meander.secondary_flow_strength(),
        'bend_scour': meander.bend_scour_depth(),
        'stability': stability_result
    }
