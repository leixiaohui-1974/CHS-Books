"""
栖息地适宜性模型
===============

实现鱼类栖息地适宜性评价方法（PHABSIM）
"""

import numpy as np
from typing import Dict, List, Tuple, Callable, Optional
from .channel import RiverReach


class SuitabilityCurve:
    """
    适宜性曲线类
    
    定义生物对某一环境因子（如水深、流速）的适宜性偏好
    
    Parameters
    ----------
    variable_name : str
        环境因子名称（如'depth', 'velocity'）
    points : list of tuples
        (变量值, 适宜性指数)对列表
        适宜性指数范围：0-1
    """
    
    def __init__(self, variable_name: str, points: List[Tuple[float, float]]):
        self.variable_name = variable_name
        self.points = sorted(points, key=lambda x: x[0])  # 按变量值排序
        
        # 提取x和y值
        self.x_values = np.array([p[0] for p in self.points])
        self.y_values = np.array([p[1] for p in self.points])
        
        # 验证适宜性指数在0-1范围内
        if np.any(self.y_values < 0) or np.any(self.y_values > 1):
            raise ValueError("适宜性指数必须在0-1范围内")
    
    def evaluate(self, value: float) -> float:
        """
        计算给定变量值的适宜性指数
        
        使用线性插值
        
        Parameters
        ----------
        value : float
            环境因子的值
            
        Returns
        -------
        float
            适宜性指数 (0-1)
        """
        # 边界处理
        if value <= self.x_values[0]:
            return self.y_values[0]
        if value >= self.x_values[-1]:
            return self.y_values[-1]
        
        # 线性插值
        return np.interp(value, self.x_values, self.y_values)
    
    def plot_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """返回用于绘图的数据"""
        # 生成平滑曲线
        x_smooth = np.linspace(self.x_values[0], self.x_values[-1], 100)
        y_smooth = np.interp(x_smooth, self.x_values, self.y_values)
        return x_smooth, y_smooth


class HabitatSuitabilityModel:
    """
    栖息地适宜性模型
    
    实现PHABSIM（Physical Habitat Simulation）方法
    
    Parameters
    ----------
    species_name : str
        物种名称
    life_stage : str
        生活史阶段（如'adult', 'juvenile', 'spawning'）
    """
    
    def __init__(self, species_name: str, life_stage: str):
        self.species_name = species_name
        self.life_stage = life_stage
        self.curves = {}  # 存储各因子的适宜性曲线
        
    def add_suitability_curve(self, variable: str, curve: SuitabilityCurve):
        """添加适宜性曲线"""
        self.curves[variable] = curve
    
    def calculate_csi(self, depth: float, velocity: float, 
                     substrate: Optional[float] = None) -> float:
        """
        计算综合适宜性指数（Composite Suitability Index, CSI）
        
        CSI = HSI_depth × HSI_velocity × HSI_substrate
        
        Parameters
        ----------
        depth : float
            水深 (m)
        velocity : float
            流速 (m/s)
        substrate : float, optional
            底质指数
            
        Returns
        -------
        float
            综合适宜性指数 (0-1)
        """
        csi = 1.0
        
        # 水深适宜性
        if 'depth' in self.curves:
            si_depth = self.curves['depth'].evaluate(depth)
            csi *= si_depth
        
        # 流速适宜性
        if 'velocity' in self.curves:
            si_velocity = self.curves['velocity'].evaluate(velocity)
            csi *= si_velocity
        
        # 底质适宜性
        if substrate is not None and 'substrate' in self.curves:
            si_substrate = self.curves['substrate'].evaluate(substrate)
            csi *= si_substrate
        
        return csi
    
    def calculate_wua(self, reach: RiverReach, Q: float, 
                     n_cells: int = 50) -> Dict[str, float]:
        """
        计算加权可利用面积（Weighted Usable Area, WUA）
        
        WUA = Σ(CSI_i × A_i)
        
        Parameters
        ----------
        reach : RiverReach
            河段对象
        Q : float
            流量 (m³/s)
        n_cells : int
            横断面网格数
            
        Returns
        -------
        dict
            包含WUA及相关信息
        """
        # 求解水深
        h = reach.solve_depth(Q)
        v_avg = reach.velocity_manning(h)
        
        # 横向分割河道
        B = reach.top_width(h)
        cell_width = B / n_cells
        
        total_wua = 0.0
        cell_areas = []
        cell_csi = []
        cell_positions = []
        
        for i in range(n_cells):
            # 横向位置（从左岸到右岸）
            y = (i + 0.5) * cell_width - B / 2
            
            # 计算该位置的水深（考虑河道断面形状）
            # 简化假设：梯形断面，从中心向两侧水深线性减小
            if reach.m > 0:  # 梯形断面
                # 计算该位置的局部水深
                edge_distance = abs(y)
                b_half = reach.b / 2
                
                if edge_distance <= b_half:
                    # 在底部平坦区域
                    local_depth = h
                else:
                    # 在边坡上
                    slope_distance = edge_distance - b_half
                    local_depth = max(0, h - slope_distance / reach.m)
            else:
                # 矩形断面
                local_depth = h if abs(y) <= reach.b / 2 else 0
            
            if local_depth <= 0:
                continue
            
            # 估算局部流速（简化：使用平均流速）
            # 实际应用中可用更复杂的流速分布模型
            local_velocity = v_avg
            
            # 计算适宜性指数
            csi = self.calculate_csi(local_depth, local_velocity)
            
            # 计算单元面积
            cell_area = cell_width * reach.length
            
            # 累加WUA
            wua_contribution = csi * cell_area
            total_wua += wua_contribution
            
            # 记录数据
            cell_areas.append(cell_area)
            cell_csi.append(csi)
            cell_positions.append(y)
        
        # 总面积
        total_area = reach.area(h) * reach.length / h  # 河床面积近似
        
        return {
            'wua': total_wua,  # m²
            'total_area': total_area,
            'habitat_quality': total_wua / total_area if total_area > 0 else 0,
            'flow': Q,
            'depth': h,
            'velocity': v_avg,
            'cell_positions': np.array(cell_positions),
            'cell_csi': np.array(cell_csi),
            'cell_areas': np.array(cell_areas),
            'n_cells': n_cells
        }
    
    def calculate_wua_vs_flow(self, reach: RiverReach, 
                             flow_range: Tuple[float, float],
                             n_flows: int = 20) -> Dict[str, np.ndarray]:
        """
        计算WUA随流量变化的关系
        
        Parameters
        ----------
        reach : RiverReach
            河段对象
        flow_range : tuple
            流量范围 (Q_min, Q_max)
        n_flows : int
            流量点数
            
        Returns
        -------
        dict
            包含流量和WUA数组
        """
        Q_min, Q_max = flow_range
        flows = np.linspace(Q_min, Q_max, n_flows)
        
        wua_values = []
        habitat_quality = []
        
        for Q in flows:
            result = self.calculate_wua(reach, Q)
            wua_values.append(result['wua'])
            habitat_quality.append(result['habitat_quality'])
        
        return {
            'flows': flows,
            'wua': np.array(wua_values),
            'habitat_quality': np.array(habitat_quality)
        }
    
    def find_optimal_flow(self, reach: RiverReach,
                         flow_range: Tuple[float, float],
                         n_flows: int = 50) -> Dict[str, float]:
        """
        找到WUA最大时的最优流量
        
        Parameters
        ----------
        reach : RiverReach
            河段对象
        flow_range : tuple
            流量范围
        n_flows : int
            搜索点数
            
        Returns
        -------
        dict
            最优流量及对应的WUA
        """
        result = self.calculate_wua_vs_flow(reach, flow_range, n_flows)
        
        # 找到WUA最大值的索引
        max_idx = np.argmax(result['wua'])
        
        return {
            'optimal_flow': result['flows'][max_idx],
            'max_wua': result['wua'][max_idx],
            'habitat_quality': result['habitat_quality'][max_idx]
        }


def create_carp_adult_model() -> HabitatSuitabilityModel:
    """
    创建鲤鱼成鱼栖息地适宜性模型
    
    基于文献数据和专家经验
    
    Returns
    -------
    HabitatSuitabilityModel
        鲤鱼成鱼模型
    """
    model = HabitatSuitabilityModel(
        species_name="鲤鱼",
        life_stage="成鱼"
    )
    
    # 水深适宜性曲线
    # 鲤鱼偏好中等水深，0.5-2.0m最适宜
    depth_curve = SuitabilityCurve(
        variable_name='depth',
        points=[
            (0.0, 0.0),    # 太浅不适宜
            (0.2, 0.3),
            (0.5, 0.8),
            (1.0, 1.0),    # 最适水深
            (1.5, 1.0),
            (2.0, 0.9),
            (3.0, 0.6),
            (5.0, 0.2)     # 太深不适宜
        ]
    )
    model.add_suitability_curve('depth', depth_curve)
    
    # 流速适宜性曲线
    # 鲤鱼偏好缓流，0.2-0.6 m/s最适宜
    velocity_curve = SuitabilityCurve(
        variable_name='velocity',
        points=[
            (0.0, 0.2),    # 静水不太适宜
            (0.1, 0.5),
            (0.2, 0.9),
            (0.4, 1.0),    # 最适流速
            (0.6, 1.0),
            (0.8, 0.7),
            (1.0, 0.4),
            (1.5, 0.1),    # 急流不适宜
            (2.0, 0.0)
        ]
    )
    model.add_suitability_curve('velocity', velocity_curve)
    
    return model


def create_carp_juvenile_model() -> HabitatSuitabilityModel:
    """
    创建鲤鱼幼鱼栖息地适宜性模型
    
    幼鱼偏好更浅和更缓的水流
    
    Returns
    -------
    HabitatSuitabilityModel
        鲤鱼幼鱼模型
    """
    model = HabitatSuitabilityModel(
        species_name="鲤鱼",
        life_stage="幼鱼"
    )
    
    # 水深适宜性曲线（偏好浅水）
    depth_curve = SuitabilityCurve(
        variable_name='depth',
        points=[
            (0.0, 0.0),
            (0.1, 0.4),
            (0.2, 0.8),
            (0.4, 1.0),    # 最适水深
            (0.6, 1.0),
            (1.0, 0.7),
            (1.5, 0.4),
            (2.0, 0.1)
        ]
    )
    model.add_suitability_curve('depth', depth_curve)
    
    # 流速适宜性曲线（偏好更缓流速）
    velocity_curve = SuitabilityCurve(
        variable_name='velocity',
        points=[
            (0.0, 0.3),
            (0.05, 0.7),
            (0.1, 1.0),    # 最适流速
            (0.2, 1.0),
            (0.3, 0.8),
            (0.5, 0.4),
            (0.8, 0.1),
            (1.0, 0.0)
        ]
    )
    model.add_suitability_curve('velocity', velocity_curve)
    
    return model
