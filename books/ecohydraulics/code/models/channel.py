"""
河道模型类
==========

定义河道几何和水力特性
"""

import numpy as np
from typing import Optional, Dict, Any


class RiverReach:
    """
    河段类
    
    表示河流中的一个河段，包含几何参数和水力特性。
    
    Parameters
    ----------
    length : float
        河段长度 (m)
    width : float
        河道平均宽度 (m)
    slope : float
        河床坡度 (无量纲)
    roughness : float
        Manning糙率系数 (s/m^(1/3))
    side_slope : float, optional
        边坡系数 m (水平:垂直), 默认为2.0
    """
    
    def __init__(self, 
                 length: float,
                 width: float,
                 slope: float,
                 roughness: float,
                 side_slope: float = 2.0):
        self.length = length
        self.b = width  # 底宽
        self.S0 = slope  # 底坡
        self.n = roughness  # 糙率
        self.m = side_slope  # 边坡系数
        
    def area(self, h: float) -> float:
        """
        计算过水断面面积
        
        Parameters
        ----------
        h : float
            水深 (m)
            
        Returns
        -------
        float
            断面面积 (m²)
        """
        return (self.b + self.m * h) * h
    
    def wetted_perimeter(self, h: float) -> float:
        """
        计算湿周
        
        Parameters
        ----------
        h : float
            水深 (m)
            
        Returns
        -------
        float
            湿周 (m)
        """
        return self.b + 2 * h * np.sqrt(1 + self.m**2)
    
    def hydraulic_radius(self, h: float) -> float:
        """
        计算水力半径
        
        Parameters
        ----------
        h : float
            水深 (m)
            
        Returns
        -------
        float
            水力半径 (m)
        """
        A = self.area(h)
        chi = self.wetted_perimeter(h)
        return A / chi if chi > 0 else 0.0
    
    def top_width(self, h: float) -> float:
        """
        计算水面宽度
        
        Parameters
        ----------
        h : float
            水深 (m)
            
        Returns
        -------
        float
            水面宽度 (m)
        """
        return self.b + 2 * self.m * h
    
    def velocity_manning(self, h: float) -> float:
        """
        使用Manning公式计算流速
        
        v = (1/n) * R^(2/3) * S0^(1/2)
        
        Parameters
        ----------
        h : float
            水深 (m)
            
        Returns
        -------
        float
            流速 (m/s)
        """
        R = self.hydraulic_radius(h)
        return (1.0 / self.n) * R**(2/3) * self.S0**0.5
    
    def discharge_manning(self, h: float) -> float:
        """
        计算流量
        
        Q = A * v
        
        Parameters
        ----------
        h : float
            水深 (m)
            
        Returns
        -------
        float
            流量 (m³/s)
        """
        A = self.area(h)
        v = self.velocity_manning(h)
        return A * v
    
    def solve_depth(self, Q: float, tol: float = 1e-6, max_iter: int = 100) -> float:
        """
        已知流量求解水深（均匀流）
        
        使用牛顿迭代法求解非线性方程
        
        Parameters
        ----------
        Q : float
            流量 (m³/s)
        tol : float
            收敛容差
        max_iter : int
            最大迭代次数
            
        Returns
        -------
        float
            水深 (m)
        """
        # 初始猜测
        h = (Q * self.n / (self.b * self.S0**0.5))**0.6
        
        for i in range(max_iter):
            # 计算函数值
            f = self.discharge_manning(h) - Q
            
            # 数值计算导数
            dh = 1e-6
            f_dh = self.discharge_manning(h + dh) - Q
            df = (f_dh - f) / dh
            
            # 牛顿迭代
            if abs(df) < 1e-12:
                break
            h_new = h - f / df
            
            # 确保水深为正
            h_new = max(0.01, h_new)
            
            # 检查收敛
            if abs(h_new - h) < tol:
                return h_new
            
            h = h_new
        
        raise ValueError(f"水深求解未收敛: Q={Q} m³/s")
    
    def get_hydraulic_properties(self, h: float) -> Dict[str, float]:
        """
        获取所有水力要素
        
        Parameters
        ----------
        h : float
            水深 (m)
            
        Returns
        -------
        dict
            包含所有水力要素的字典
        """
        A = self.area(h)
        chi = self.wetted_perimeter(h)
        R = self.hydraulic_radius(h)
        B = self.top_width(h)
        v = self.velocity_manning(h)
        Q = self.discharge_manning(h)
        
        return {
            'depth': h,
            'area': A,
            'wetted_perimeter': chi,
            'hydraulic_radius': R,
            'top_width': B,
            'velocity': v,
            'discharge': Q
        }


class River:
    """
    河流类
    
    表示一条完整的河流，可包含多个河段。
    
    Parameters
    ----------
    name : str
        河流名称
    mean_annual_flow : float
        多年平均流量 (m³/s)
    """
    
    def __init__(self, name: str, mean_annual_flow: float):
        self.name = name
        self.Q_maf = mean_annual_flow  # 多年平均流量
        self.reaches = []
        
    def add_reach(self, reach: RiverReach):
        """添加河段"""
        self.reaches.append(reach)
        
    def total_length(self) -> float:
        """计算河流总长度"""
        return sum(reach.length for reach in self.reaches)
    
    def average_wetted_perimeter(self, Q: float) -> float:
        """
        计算给定流量下的平均湿周
        
        Parameters
        ----------
        Q : float
            流量 (m³/s)
            
        Returns
        -------
        float
            平均湿周 (m)
        """
        if not self.reaches:
            raise ValueError("河流中没有河段")
        
        total_wp = 0.0
        total_length = 0.0
        
        for reach in self.reaches:
            h = reach.solve_depth(Q)
            wp = reach.wetted_perimeter(h)
            total_wp += wp * reach.length
            total_length += reach.length
        
        return total_wp / total_length if total_length > 0 else 0.0
    
    def __repr__(self):
        return f"River(name='{self.name}', Q_maf={self.Q_maf} m³/s, reaches={len(self.reaches)})"
