"""竖缝式鱼道水力学模型

本模块实现竖缝式鱼道（Vertical Slot Fishway）的水力计算，包括：
- 池室水深计算
- 流速分布计算
- 能量消散分析
- 体积功率密度验算
- 几何参数优化
"""

import numpy as np
from typing import Dict, Tuple, Optional, List

class VerticalSlotFishway:
    """竖缝式鱼道模型
    
    竖缝式鱼道是最常用的过鱼设施之一，通过竖缝形成连续的水流通道，
    鱼类可以在任何水深层游过，适应性强。
    
    理论基础：
    1. 能量方程：ΔE = Q×g×ΔH
    2. 体积功率密度：P/V = ρ×g×Q×ΔH/V < 150 W/m³
    3. 射流扩散：竖缝射流特性
    4. 回流区：低流速休息区
    """
    
    def __init__(self,
                 pool_length: float,      # 池室长度 (m)
                 pool_width: float,       # 池室宽度 (m)
                 slot_width: float,       # 竖缝宽度 (m)
                 drop_per_pool: float,    # 池间落差 (m)
                 num_pools: int,          # 池室数量
                 slope: float = 0.1):     # 底坡 (无量纲)
        """
        初始化竖缝式鱼道模型
        
        Parameters:
        -----------
        pool_length : float
            池室长度 (m)
        pool_width : float
            池室宽度 (m)
        slot_width : float
            竖缝宽度 (m)
        drop_per_pool : float
            每个池室的水位落差 (m)
        num_pools : int
            池室数量
        slope : float
            鱼道底坡，默认0.1 (即1:10)
        """
        self.pool_length = pool_length
        self.pool_width = pool_width
        self.slot_width = slot_width
        self.drop_per_pool = drop_per_pool
        self.num_pools = num_pools
        self.slope = slope
        
        # 常数
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho = 1000.0  # 水密度 (kg/m³)
        
        # 经验系数
        self.discharge_coef = 0.6  # 竖缝流量系数
        self.contraction_coef = 0.9  # 收缩系数
    
    def pool_volume(self, water_depth: float) -> float:
        """计算池室水体积
        
        Parameters:
        -----------
        water_depth : float
            水深 (m)
        
        Returns:
        --------
        float
            池室水体积 (m³)
        """
        return self.pool_length * self.pool_width * water_depth
    
    def slot_discharge(self, water_depth: float) -> float:
        """计算通过竖缝的流量
        
        使用宽顶堰公式的变形
        
        Parameters:
        -----------
        water_depth : float
            池室水深 (m)
        
        Returns:
        --------
        float
            流量 (m³/s)
        """
        # 竖缝流量公式：Q = C × b × h × sqrt(2×g×ΔH)
        Q = (self.discharge_coef * 
             self.slot_width * 
             water_depth * 
             np.sqrt(2 * self.g * self.drop_per_pool))
        
        return Q
    
    def slot_velocity(self, discharge: float, water_depth: float) -> float:
        """计算竖缝处的平均流速
        
        Parameters:
        -----------
        discharge : float
            流量 (m³/s)
        water_depth : float
            水深 (m)
        
        Returns:
        --------
        float
            竖缝流速 (m/s)
        """
        # 实际过流面积考虑收缩系数
        A_effective = self.slot_width * water_depth * self.contraction_coef
        v = discharge / A_effective
        
        return v
    
    def energy_dissipation(self, discharge: float) -> float:
        """计算能量消散功率
        
        Parameters:
        -----------
        discharge : float
            流量 (m³/s)
        
        Returns:
        --------
        float
            消散功率 (W)
        """
        # 能量消散 = ρ × g × Q × ΔH
        P = self.rho * self.g * discharge * self.drop_per_pool
        
        return P
    
    def volumetric_power_dissipation(self, discharge: float, water_depth: float) -> float:
        """计算体积功率密度（VPD）
        
        体积功率密度是鱼道设计的关键指标，应小于150 W/m³
        
        Parameters:
        -----------
        discharge : float
            流量 (m³/s)
        water_depth : float
            水深 (m)
        
        Returns:
        --------
        float
            体积功率密度 (W/m³)
        """
        P = self.energy_dissipation(discharge)
        V = self.pool_volume(water_depth)
        
        VPD = P / V
        
        return VPD
    
    def design_water_depth(self, target_discharge: float, 
                          max_vpd: float = 150.0) -> Tuple[float, bool]:
        """设计水深，使体积功率密度满足要求
        
        Parameters:
        -----------
        target_discharge : float
            目标流量 (m³/s)
        max_vpd : float
            最大允许体积功率密度 (W/m³)，默认150
        
        Returns:
        --------
        tuple
            (设计水深 (m), 是否满足要求)
        """
        # 从能量消散和最大VPD反推最小水深
        P = self.energy_dissipation(target_discharge)
        V_min = P / max_vpd
        h_min = V_min / (self.pool_length * self.pool_width)
        
        # 迭代求解实际水深（考虑流量-水深关系）
        h = h_min * 1.2  # 初始猜测，比最小值大20%
        
        for _ in range(50):
            Q_calc = self.slot_discharge(h)
            error = (Q_calc - target_discharge) / target_discharge
            
            if abs(error) < 0.01:  # 1%误差
                break
            
            # 调整水深
            h = h * (1.0 - 0.5 * error)
            h = max(0.3, h)  # 确保水深不小于0.3m
        
        # 验证VPD
        vpd_actual = self.volumetric_power_dissipation(target_discharge, h)
        is_acceptable = vpd_actual <= max_vpd
        
        return h, is_acceptable
    
    def velocity_field(self, discharge: float, water_depth: float, 
                      nx: int = 20, ny: int = 15) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """计算池室内的流速场（简化2D模型）
        
        使用射流扩散模型估算流速分布
        
        Parameters:
        -----------
        discharge : float
            流量 (m³/s)
        water_depth : float
            水深 (m)
        nx : int
            x方向网格数
        ny : int
            y方向网格数
        
        Returns:
        --------
        tuple
            (x坐标, y坐标, 流速大小) 均为2D数组
        """
        # 创建网格
        x = np.linspace(0, self.pool_length, nx)
        y = np.linspace(0, self.pool_width, ny)
        X, Y = np.meshgrid(x, y)
        
        # 竖缝位置（假设在x=0处）
        v_slot = self.slot_velocity(discharge, water_depth)
        
        # 射流扩散模型（简化）
        # 流速随距离衰减，横向扩散
        
        # 距竖缝的距离
        dist_from_slot = X
        
        # 射流中心线（简化为y=pool_width/2）
        dist_from_centerline = np.abs(Y - self.pool_width / 2.0)
        
        # 流速衰减（指数衰减）
        decay_length = self.pool_length * 0.5
        v_magnitude = v_slot * np.exp(-dist_from_slot / decay_length)
        
        # 横向扩散（高斯分布）
        spread = 0.3 * dist_from_slot + 0.5  # 扩散宽度随距离增加
        lateral_factor = np.exp(-(dist_from_centerline ** 2) / (2 * spread ** 2))
        
        # 最终流速
        V = v_magnitude * lateral_factor
        
        # 回流区（池室两侧和后部）
        # 在远离射流的区域，流速应该很小
        recirculation_mask = (dist_from_centerline > self.pool_width * 0.3) | (X > self.pool_length * 0.7)
        V[recirculation_mask] *= 0.3  # 回流区流速降低
        
        return X, Y, V
    
    def recirculation_area_ratio(self, discharge: float, water_depth: float,
                                 low_velocity_threshold: float = 0.3) -> float:
        """计算回流区（低流速区）面积比例
        
        Parameters:
        -----------
        discharge : float
            流量 (m³/s)
        water_depth : float
            水深 (m)
        low_velocity_threshold : float
            低流速阈值 (m/s)，默认0.3 m/s
        
        Returns:
        --------
        float
            回流区面积占池室总面积的比例
        """
        X, Y, V = self.velocity_field(discharge, water_depth)
        
        # 统计低流速区域
        low_velocity_area = np.sum(V < low_velocity_threshold)
        total_area = V.size
        
        ratio = low_velocity_area / total_area
        
        return ratio
    
    def total_head_loss(self) -> float:
        """计算总水头损失
        
        Returns:
        --------
        float
            总水头损失 (m)
        """
        return self.drop_per_pool * self.num_pools
    
    def fishway_length(self) -> float:
        """计算鱼道总长度
        
        Returns:
        --------
        float
            鱼道长度 (m)
        """
        return self.pool_length * self.num_pools
    
    def fishway_slope_check(self) -> Tuple[float, bool]:
        """检查鱼道实际坡度
        
        Returns:
        --------
        tuple
            (实际坡度, 是否合理)
        """
        total_drop = self.total_head_loss()
        length = self.fishway_length()
        actual_slope = total_drop / length
        
        # 合理坡度范围：1:10 到 1:20 (0.05 到 0.1)
        is_reasonable = 0.05 <= actual_slope <= 0.15
        
        return actual_slope, is_reasonable
    
    def design_summary(self, discharge: float, water_depth: float) -> Dict:
        """生成设计总结报告
        
        Parameters:
        -----------
        discharge : float
            设计流量 (m³/s)
        water_depth : float
            设计水深 (m)
        
        Returns:
        --------
        dict
            设计参数汇总
        """
        v_slot = self.slot_velocity(discharge, water_depth)
        P = self.energy_dissipation(discharge)
        vpd = self.volumetric_power_dissipation(discharge, water_depth)
        recir_ratio = self.recirculation_area_ratio(discharge, water_depth)
        total_drop = self.total_head_loss()
        length = self.fishway_length()
        actual_slope, slope_ok = self.fishway_slope_check()
        
        summary = {
            # 几何参数
            'pool_length_m': self.pool_length,
            'pool_width_m': self.pool_width,
            'slot_width_m': self.slot_width,
            'drop_per_pool_m': self.drop_per_pool,
            'num_pools': self.num_pools,
            
            # 水力参数
            'discharge_m3s': discharge,
            'water_depth_m': water_depth,
            'slot_velocity_ms': v_slot,
            
            # 能量参数
            'power_dissipation_W': P,
            'volumetric_power_density_Wm3': vpd,
            'vpd_acceptable': vpd <= 150.0,
            
            # 生境参数
            'recirculation_area_ratio': recir_ratio,
            
            # 总体参数
            'total_head_loss_m': total_drop,
            'fishway_length_m': length,
            'actual_slope': actual_slope,
            'slope_reasonable': slope_ok
        }
        
        return summary
    
    def optimize_design(self, target_discharge: float, 
                       dam_height: float,
                       max_vpd: float = 150.0,
                       max_slot_velocity: float = 1.5) -> Dict:
        """优化设计参数
        
        在满足约束条件下，优化鱼道设计
        
        Parameters:
        -----------
        target_discharge : float
            目标流量 (m³/s)
        dam_height : float
            大坝高度 (m)
        max_vpd : float
            最大体积功率密度 (W/m³)
        max_slot_velocity : float
            最大竖缝流速 (m/s)
        
        Returns:
        --------
        dict
            优化后的设计参数
        """
        # 根据大坝高度确定池室数量
        num_pools_needed = int(np.ceil(dam_height / self.drop_per_pool)) + 1
        self.num_pools = num_pools_needed
        
        # 设计水深
        h_design, vpd_ok = self.design_water_depth(target_discharge, max_vpd)
        
        # 检查竖缝流速
        v_slot = self.slot_velocity(target_discharge, h_design)
        velocity_ok = v_slot <= max_slot_velocity
        
        # 生成优化报告
        summary = self.design_summary(target_discharge, h_design)
        summary['optimization_result'] = {
            'vpd_constraint_met': vpd_ok,
            'velocity_constraint_met': velocity_ok,
            'all_constraints_met': vpd_ok and velocity_ok
        }
        
        return summary


def create_standard_fishway(dam_height: float, 
                           target_discharge: float = 1.0) -> VerticalSlotFishway:
    """创建标准竖缝式鱼道
    
    使用常用的几何参数
    
    Parameters:
    -----------
    dam_height : float
        大坝高度 (m)
    target_discharge : float
        目标流量 (m³/s)
    
    Returns:
    --------
    VerticalSlotFishway
        配置好的鱼道模型
    """
    # 标准参数
    pool_length = 3.0  # m
    pool_width = 2.0   # m
    slot_width = 0.3   # m
    drop_per_pool = 0.2  # m
    
    # 根据大坝高度确定池室数量
    num_pools = int(np.ceil(dam_height / drop_per_pool)) + 2
    
    fishway = VerticalSlotFishway(
        pool_length=pool_length,
        pool_width=pool_width,
        slot_width=slot_width,
        drop_per_pool=drop_per_pool,
        num_pools=num_pools
    )
    
    return fishway
