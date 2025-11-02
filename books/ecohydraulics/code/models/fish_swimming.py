"""鱼类游泳能力模型

本模块实现鱼类游泳生物力学计算，包括：
- 持续游泳速度（Sustained swimming speed）
- 爆发游泳速度（Burst swimming speed）
- 临界游泳速度（Critical swimming speed, Ucrit）
- 耐力时间（Endurance time）
- 能量消耗（Energy expenditure）
"""

import numpy as np
from typing import Dict, Tuple, Optional

class FishSwimmingModel:
    """鱼类游泳能力模型
    
    基于鱼类生物力学原理，计算不同游泳模式的速度和耐力。
    
    理论基础：
    1. 持续游速 = k1 * BL (body length/s)
    2. 爆发游速 = k2 * BL
    3. Ucrit = 临界游泳速度测试
    4. 耐力时间与速度的幂函数关系
    """
    
    def __init__(self, 
                 species: str,
                 body_length: float,  # 体长 (cm)
                 body_weight: Optional[float] = None,  # 体重 (g)
                 temperature: float = 20.0):  # 水温 (°C)
        """
        初始化鱼类游泳模型
        
        Parameters:
        -----------
        species : str
            鱼类种类
        body_length : float
            体长 (cm)
        body_weight : float, optional
            体重 (g)，如不提供则根据体长估算
        temperature : float
            水温 (°C)，影响游泳能力
        """
        self.species = species
        self.body_length = body_length  # cm
        self.temperature = temperature
        
        # 如果未提供体重，使用体长-体重关系估算
        if body_weight is None:
            self.body_weight = self.estimate_weight(body_length)
        else:
            self.body_weight = body_weight
        
        # 游泳能力系数（不同鱼类不同）
        self.sustained_coef = 2.0  # 持续游速系数 (BL/s)
        self.burst_coef = 10.0     # 爆发游速系数 (BL/s)
        self.ucrit_coef = 5.0      # Ucrit系数 (BL/s)
    
    @staticmethod
    def estimate_weight(length: float) -> float:
        """根据体长估算体重
        
        使用常见的体长-体重关系: W = a * L^b
        对于鲤科鱼类: a ≈ 0.01, b ≈ 3
        
        Parameters:
        -----------
        length : float
            体长 (cm)
        
        Returns:
        --------
        float
            估算体重 (g)
        """
        a = 0.01
        b = 3.0
        return a * (length ** b)
    
    def sustained_speed(self) -> float:
        """计算持续游泳速度（可长时间维持）
        
        持续游速通常为 1.5-2.5 BL/s
        
        Returns:
        --------
        float
            持续游速 (m/s)
        """
        # 温度修正系数（20°C为基准）
        temp_factor = 1.0 + 0.02 * (self.temperature - 20.0)
        temp_factor = max(0.5, min(1.5, temp_factor))
        
        # 持续游速 (BL/s -> m/s)
        speed_bl = self.sustained_coef * temp_factor
        speed_ms = speed_bl * (self.body_length / 100.0)
        
        return speed_ms
    
    def burst_speed(self) -> float:
        """计算爆发游泳速度（短时间冲刺）
        
        爆发游速通常为 8-12 BL/s
        可维持时间很短（秒级）
        
        Returns:
        --------
        float
            爆发游速 (m/s)
        """
        # 温度修正
        temp_factor = 1.0 + 0.02 * (self.temperature - 20.0)
        temp_factor = max(0.5, min(1.5, temp_factor))
        
        # 爆发游速
        speed_bl = self.burst_coef * temp_factor
        speed_ms = speed_bl * (self.body_length / 100.0)
        
        return speed_ms
    
    def critical_speed(self) -> float:
        """计算临界游泳速度（Ucrit）
        
        Ucrit是标准测试方法得到的临界速度
        通常在持续游速和爆发游速之间
        
        Returns:
        --------
        float
            临界游速 (m/s)
        """
        temp_factor = 1.0 + 0.02 * (self.temperature - 20.0)
        temp_factor = max(0.5, min(1.5, temp_factor))
        
        speed_bl = self.ucrit_coef * temp_factor
        speed_ms = speed_bl * (self.body_length / 100.0)
        
        return speed_ms
    
    def endurance_time(self, swimming_speed: float) -> float:
        """计算给定速度下的耐力时间
        
        耐力时间与速度呈幂函数关系：
        t = a * v^(-b)
        
        Parameters:
        -----------
        swimming_speed : float
            游泳速度 (m/s)
        
        Returns:
        --------
        float
            耐力时间 (s)，如果速度过低返回inf
        """
        sustained = self.sustained_speed()
        
        # 如果速度低于持续游速，可以无限时间维持
        if swimming_speed <= sustained:
            return np.inf
        
        # 如果速度高于爆发游速，无法维持
        burst = self.burst_speed()
        if swimming_speed >= burst:
            return 0.0
        
        # 耐力时间计算（幂函数）
        # 在持续游速时: t = inf
        # 在爆发游速时: t = 0
        # 中间区域: 指数衰减
        
        v_norm = (swimming_speed - sustained) / (burst - sustained)
        t = 3600.0 * np.exp(-5.0 * v_norm)  # 秒
        
        return t
    
    def energy_expenditure(self, swimming_speed: float, duration: float) -> float:
        """计算能量消耗
        
        能量消耗与速度的立方成正比
        
        Parameters:
        -----------
        swimming_speed : float
            游泳速度 (m/s)
        duration : float
            游泳时间 (s)
        
        Returns:
        --------
        float
            能量消耗 (J)
        """
        # 基础代谢率（与体重相关）
        BMR = 0.5 * (self.body_weight ** 0.8)  # W
        
        # 游泳能量消耗与速度立方成正比
        sustained = self.sustained_speed()
        speed_factor = (swimming_speed / sustained) ** 3
        
        # 总功率
        power = BMR * (1.0 + speed_factor)  # W
        
        # 总能量
        energy = power * duration  # J
        
        return energy
    
    def swimming_performance_summary(self) -> Dict:
        """生成游泳能力汇总
        
        Returns:
        --------
        dict
            包含各种游泳参数的字典
        """
        sustained = self.sustained_speed()
        burst = self.burst_speed()
        ucrit = self.critical_speed()
        
        # 计算不同速度下的耐力
        speeds = np.linspace(sustained, burst, 5)
        endurances = [self.endurance_time(v) for v in speeds]
        
        summary = {
            'species': self.species,
            'body_length_cm': self.body_length,
            'body_weight_g': self.body_weight,
            'temperature_C': self.temperature,
            'sustained_speed_ms': sustained,
            'sustained_speed_BLs': sustained / (self.body_length / 100.0),
            'burst_speed_ms': burst,
            'burst_speed_BLs': burst / (self.body_length / 100.0),
            'critical_speed_ms': ucrit,
            'critical_speed_BLs': ucrit / (self.body_length / 100.0),
            'speed_endurance_pairs': list(zip(speeds, endurances))
        }
        
        return summary
    
    def design_flow_velocity(self, safety_factor: float = 0.8) -> Tuple[float, str]:
        """确定鱼道设计流速
        
        设计流速应低于持续游速，确保鱼类能够通过
        
        Parameters:
        -----------
        safety_factor : float
            安全系数，默认0.8
        
        Returns:
        --------
        tuple
            (设计流速 (m/s), 建议说明)
        """
        sustained = self.sustained_speed()
        design_v = sustained * safety_factor
        
        recommendation = f"""
        鱼道设计流速建议：
        - 持续游速: {sustained:.2f} m/s
        - 设计流速: {design_v:.2f} m/s（持续游速的{safety_factor*100:.0f}%）
        - 说明: 设计流速应确保{self.species}（体长{self.body_length:.0f}cm）
                能够长时间游动而不疲劳
        """
        
        return design_v, recommendation
    
    def can_pass_velocity(self, flow_velocity: float, passage_length: float) -> Tuple[bool, float, str]:
        """判断鱼类能否通过给定流速的通道
        
        Parameters:
        -----------
        flow_velocity : float
            通道流速 (m/s)
        passage_length : float
            通道长度 (m)
        
        Returns:
        --------
        tuple
            (能否通过, 需要时间(s), 说明)
        """
        sustained = self.sustained_speed()
        endurance = self.endurance_time(flow_velocity)
        
        # 相对游速（鱼类游速减去水流速度）
        relative_speed = self.sustained_speed()
        
        if flow_velocity > self.burst_speed():
            return False, 0, "流速超过爆发游速，无法通过"
        
        if flow_velocity <= sustained:
            time_needed = passage_length / relative_speed
            return True, time_needed, f"可以轻松通过，需要时间{time_needed:.1f}秒"
        
        # 需要高于持续游速的速度
        time_needed = passage_length / (relative_speed * 1.5)
        
        if time_needed <= endurance:
            return True, time_needed, f"可以通过，需要时间{time_needed:.1f}秒（耐力{endurance:.1f}秒）"
        else:
            return False, time_needed, f"无法通过，需要时间{time_needed:.1f}秒，但耐力只有{endurance:.1f}秒"


def create_grass_carp(body_length: float = 30.0, temperature: float = 20.0) -> FishSwimmingModel:
    """创建草鱼模型
    
    草鱼（Ctenopharyngodon idella）是重要的经济鱼类
    游泳能力中等
    """
    fish = FishSwimmingModel("草鱼", body_length, temperature=temperature)
    fish.sustained_coef = 2.0
    fish.burst_coef = 10.0
    fish.ucrit_coef = 5.0
    return fish


def create_black_carp(body_length: float = 40.0, temperature: float = 20.0) -> FishSwimmingModel:
    """创建青鱼模型
    
    青鱼（Mylopharyngodon piceus）体型较大
    游泳能力较强
    """
    fish = FishSwimmingModel("青鱼", body_length, temperature=temperature)
    fish.sustained_coef = 2.2
    fish.burst_coef = 11.0
    fish.ucrit_coef = 5.5
    return fish


def create_common_carp(body_length: float = 25.0, temperature: float = 20.0) -> FishSwimmingModel:
    """创建鲤鱼模型
    
    鲤鱼（Cyprinus carpio）适应力强
    游泳能力中等偏下
    """
    fish = FishSwimmingModel("鲤鱼", body_length, temperature=temperature)
    fish.sustained_coef = 1.8
    fish.burst_coef = 9.0
    fish.ucrit_coef = 4.5
    return fish


def create_silver_carp(body_length: float = 35.0, temperature: float = 20.0) -> FishSwimmingModel:
    """创建鲢鱼模型
    
    鲢鱼（Hypophthalmichthys molitrix）滤食性鱼类
    游泳能力中等
    """
    fish = FishSwimmingModel("鲢鱼", body_length, temperature=temperature)
    fish.sustained_coef = 1.9
    fish.burst_coef = 9.5
    fish.ucrit_coef = 4.8
    return fish
