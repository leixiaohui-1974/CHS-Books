"""洪泛区湿地模型

本模块实现河流-洪泛区水力连通性分析，包括：
- 漫滩水力学
- 湿地淹没频率
- 幼鱼生长适宜性
- 生态调度方案
"""

import numpy as np
from typing import Dict, List, Tuple, Optional


class FloodplainHydraulics:
    """漫滩水力学模型
    
    计算不同流量下的漫滩范围和水深
    """
    
    def __init__(self,
                 channel_width: float,
                 channel_depth: float,
                 floodplain_width: float,
                 floodplain_elevation: float,
                 slope: float):
        """
        Parameters:
        -----------
        channel_width : float
            主河道宽度 (m)
        channel_depth : float
            主河道深度 (m)
        floodplain_width : float
            洪泛区总宽度 (m)
        floodplain_elevation : float
            洪泛区高程（相对河床） (m)
        slope : float
            河道坡度
        """
        self.Bc = channel_width
        self.Hc = channel_depth
        self.Bf = floodplain_width
        self.Hf = floodplain_elevation
        self.S = slope
    
    def inundation_area(self, discharge: float, manning_n: float = 0.035) -> Dict:
        """计算淹没面积
        
        Parameters:
        -----------
        discharge : float
            流量 (m³/s)
        manning_n : float
            Manning粗糙系数
        
        Returns:
        --------
        dict
            淹没信息
        """
        # 估算水深（简化为复式断面）
        h = self._calculate_water_depth(discharge, manning_n)
        
        # 判断是否漫滩
        if h <= self.Hf:
            # 未漫滩
            inundated_width = self.Bc
            inundated_area = self.Bc * 100  # 每100m河段
            is_overbank = False
        else:
            # 已漫滩
            overbank_depth = h - self.Hf
            inundated_width = self.Bc + self.Bf
            inundated_area = (self.Bc + self.Bf) * 100
            is_overbank = True
        
        return {
            'discharge': discharge,
            'water_depth': h,
            'inundated_width': inundated_width,
            'inundated_area': inundated_area,
            'is_overbank': is_overbank,
            'overbank_depth': h - self.Hf if is_overbank else 0.0
        }
    
    def _calculate_water_depth(self, Q: float, n: float) -> float:
        """估算水深（Manning公式迭代）"""
        # 简化计算：假设宽浅河道
        h_guess = (Q * n / (self.Bc * np.sqrt(self.S))) ** (3.0/5.0)
        
        return h_guess
    
    def overbank_threshold_discharge(self, manning_n: float = 0.035) -> float:
        """计算漫滩临界流量"""
        # 主河道满槽流量
        A = self.Bc * self.Hf
        R = A / (self.Bc + 2 * self.Hf)
        Q_threshold = (1.0 / manning_n) * A * R ** (2.0/3.0) * np.sqrt(self.S)
        
        return Q_threshold


class WetlandConnectivity:
    """湿地连通性分析
    
    评估湿地与河流的水文连通性
    """
    
    def __init__(self,
                 wetland_elevation: float,
                 wetland_area: float):
        """
        Parameters:
        -----------
        wetland_elevation : float
            湿地底部高程（相对河床） (m)
        wetland_area : float
            湿地面积 (ha)
        """
        self.elevation = wetland_elevation
        self.area = wetland_area
    
    def inundation_frequency(self, 
                            water_depths: np.ndarray,
                            days_per_year: int = 365) -> Dict:
        """计算淹没频率
        
        Parameters:
        -----------
        water_depths : np.ndarray
            全年日平均水深序列 (m)
        days_per_year : int
            天数
        
        Returns:
        --------
        dict
            淹没频率统计
        """
        # 判断淹没
        inundated = water_depths > self.elevation
        
        # 统计
        inundation_days = np.sum(inundated)
        inundation_freq = inundation_days / days_per_year
        
        # 淹没历时
        if inundation_days > 0:
            avg_depth = np.mean(water_depths[inundated] - self.elevation)
            max_depth = np.max(water_depths[inundated] - self.elevation)
        else:
            avg_depth = 0.0
            max_depth = 0.0
        
        return {
            'inundation_days': inundation_days,
            'inundation_frequency': inundation_freq,
            'avg_inundation_depth': avg_depth,
            'max_inundation_depth': max_depth
        }
    
    def connectivity_index(self, inundation_freq: float) -> float:
        """计算连通性指数
        
        基于淹没频率
        """
        # 连通性指数：0-1
        # 理想：20-40% 淹没频率
        if inundation_freq < 0.1:
            CI = inundation_freq / 0.1
        elif inundation_freq < 0.4:
            CI = 1.0
        else:
            CI = max(0.5, 1.0 - (inundation_freq - 0.4) / 0.6)
        
        return CI


class JuvenileFishGrowth:
    """幼鱼生长模型
    
    评估湿地作为幼鱼育肥场的适宜性
    """
    
    def __init__(self,
                 species: str = "四大家鱼",
                 initial_length: float = 1.0):
        """
        Parameters:
        -----------
        species : str
            鱼类种类
        initial_length : float
            初始体长 (cm)
        """
        self.species = species
        self.L0 = initial_length
    
    def growth_rate(self, 
                   temperature: float,
                   food_abundance: float) -> float:
        """计算生长率
        
        Parameters:
        -----------
        temperature : float
            水温 (°C)
        food_abundance : float
            饵料丰度（0-1）
        
        Returns:
        --------
        float
            日生长率 (cm/day)
        """
        # 温度影响（Q10模型）
        T_opt = 25.0  # 最适温度
        if temperature < 15:
            temp_factor = 0.3
        elif temperature < T_opt:
            temp_factor = 0.3 + 0.7 * (temperature - 15) / (T_opt - 15)
        elif temperature < 32:
            temp_factor = 1.0 - 0.5 * (temperature - T_opt) / (32 - T_opt)
        else:
            temp_factor = 0.5
        
        # 饵料影响
        food_factor = food_abundance
        
        # 基础生长率
        base_rate = 0.2  # cm/day (最优条件)
        
        growth = base_rate * temp_factor * food_factor
        
        return growth
    
    def simulate_growth(self,
                       days: int,
                       temperature: float,
                       food_abundance: float) -> Tuple[np.ndarray, np.ndarray]:
        """模拟生长过程
        
        Returns:
        --------
        tuple
            (时间数组, 体长数组)
        """
        t = np.arange(days)
        L = np.zeros(days)
        L[0] = self.L0
        
        daily_growth = self.growth_rate(temperature, food_abundance)
        
        for i in range(1, days):
            L[i] = L[i-1] + daily_growth
        
        return t, L
    
    def wetland_suitability(self,
                           water_depth: float,
                           temperature: float,
                           vegetation_coverage: float) -> Dict:
        """评估湿地适宜性
        
        Parameters:
        -----------
        water_depth : float
            水深 (m)
        temperature : float
            水温 (°C)
        vegetation_coverage : float
            植被覆盖度（0-1）
        """
        # 水深适宜性（0.5-2.0m为佳）
        if water_depth < 0.3:
            depth_suit = 0.2
        elif water_depth < 0.5:
            depth_suit = 0.6
        elif water_depth <= 2.0:
            depth_suit = 1.0
        else:
            depth_suit = 0.7
        
        # 温度适宜性
        if 20 <= temperature <= 28:
            temp_suit = 1.0
        elif 15 <= temperature < 20:
            temp_suit = 0.6 + 0.4 * (temperature - 15) / 5
        elif 28 < temperature <= 32:
            temp_suit = 1.0 - 0.5 * (temperature - 28) / 4
        else:
            temp_suit = 0.3
        
        # 植被适宜性（提供隐蔽和饵料）
        if 0.3 <= vegetation_coverage <= 0.7:
            veg_suit = 1.0
        elif vegetation_coverage < 0.3:
            veg_suit = 0.5 + vegetation_coverage / 0.6
        else:
            veg_suit = 1.0 - 0.5 * (vegetation_coverage - 0.7) / 0.3
        
        # 综合适宜性
        overall = (depth_suit * 0.4 + temp_suit * 0.4 + veg_suit * 0.2)
        
        # 等级
        if overall > 0.8:
            grade = "优秀"
        elif overall > 0.6:
            grade = "良好"
        elif overall > 0.4:
            grade = "一般"
        else:
            grade = "较差"
        
        return {
            'depth_suitability': depth_suit,
            'temperature_suitability': temp_suit,
            'vegetation_suitability': veg_suit,
            'overall_suitability': overall,
            'grade': grade
        }


def design_ecological_gate_operation(
    monthly_flows: np.ndarray,
    wetland_elevation: float,
    target_inundation_freq: float = 0.3) -> Dict:
    """设计生态水闸调度方案
    
    Parameters:
    -----------
    monthly_flows : np.ndarray
        月平均流量 (m³/s)
    wetland_elevation : float
        湿地高程 (m)
    target_inundation_freq : float
        目标淹没频率
    
    Returns:
    --------
    dict
        调度方案
    """
    # 简化：根据月流量确定是否开闸
    months = len(monthly_flows)
    gate_operations = []
    
    # 按流量排序，确定开闸阈值
    sorted_flows = np.sort(monthly_flows)
    threshold_idx = int((1 - target_inundation_freq) * months)
    flow_threshold = sorted_flows[threshold_idx]
    
    for i, flow in enumerate(monthly_flows):
        if flow >= flow_threshold:
            operation = "开闸"
            effect = "淹没湿地，促进鱼类繁殖和幼鱼生长"
        else:
            operation = "关闸"
            effect = "维持主河道流量"
        
        gate_operations.append({
            'month': i + 1,
            'flow': flow,
            'operation': operation,
            'effect': effect
        })
    
    return {
        'flow_threshold': flow_threshold,
        'operations': gate_operations,
        'expected_frequency': target_inundation_freq
    }
