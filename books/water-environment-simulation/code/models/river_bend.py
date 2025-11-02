"""
河流弯道水质模拟模型
River Bend Water Quality Model

包括：
1. 弯道二次流模拟
2. 增强横向混合
3. 浓度偏向效应
4. 弯道系数计算
"""

import numpy as np


class RiverBend2D:
    """
    河流弯道二维水质模型
    
    考虑弯道二次流对污染物横向分布的影响
    
    特点：
    - 横向环流增强混合
    - 浓度偏向凹岸
    - 有效扩散系数增大
    
    参数：
        L: 纵向长度 (m)
        B: 河宽 (m)
        nx: 纵向节点数
        ny: 横向节点数
        u: 纵向平均流速 (m/s)
        Ey_straight: 直道横向扩散系数 (m²/s)
        R: 弯道曲率半径 (m)
        bend_angle: 弯道转角 (度)
    """
    
    def __init__(self, L, B, nx, ny, u, Ey_straight, R, bend_angle):
        """初始化河流弯道模型"""
        self.L = L
        self.B = B
        self.nx = nx
        self.ny = ny
        self.u = u
        self.Ey_straight = Ey_straight
        self.R = R
        self.bend_angle = bend_angle
        
        # 计算弯道增强系数
        self.K_bend = self.calculate_bend_enhancement_factor()
        
        # 有效横向扩散系数（弯道增强）
        self.Ey_effective = Ey_straight * self.K_bend
        
        # 空间离散
        self.x = np.linspace(0, L, nx)
        self.y = np.linspace(0, B, ny)
        self.dx = L / (nx - 1)
        self.dy = B / (ny - 1)
        
        # 浓度场
        self.C = np.zeros((ny, nx))
        
        # 排放源
        self.sources = []
        
        print(f"河流弯道模型初始化:")
        print(f"  计算域: {L}m × {B}m")
        print(f"  网格: {nx} × {ny}")
        print(f"  流速 u = {u} m/s")
        print(f"  曲率半径 R = {R} m")
        print(f"  弯道转角 = {bend_angle}°")
        print(f"  直道Ey = {Ey_straight:.4f} m²/s")
        print(f"  弯道增强系数 K = {self.K_bend:.2f}")
        print(f"  有效Ey = {self.Ey_effective:.4f} m²/s")
    
    def calculate_bend_enhancement_factor(self):
        """
        计算弯道对横向混合的增强系数
        
        基于经验公式：
        K_bend = 1 + C * (B/R)^n
        
        其中：
        - C: 经验系数（通常1.5-3.0）
        - n: 指数（通常1.0-1.5）
        - B/R: 宽深比
        
        返回：
            K_bend: 弯道增强系数（>1）
        """
        # 宽曲比
        width_curvature_ratio = self.B / self.R
        
        # 经验公式（Rutherford, 1994）
        C = 2.0
        n = 1.0
        K_bend = 1.0 + C * (width_curvature_ratio ** n)
        
        # 限制最大增强系数（避免不合理值）
        K_bend = min(K_bend, 5.0)
        
        return K_bend
    
    def add_source(self, x, y, Q_discharge, C_discharge, Q_river):
        """
        添加排放源
        
        参数：
            x: 排放位置x坐标 (m)
            y: 排放位置y坐标 (m)
            Q_discharge: 排放流量 (m³/s)
            C_discharge: 排放浓度 (mg/L)
            Q_river: 河流流量 (m³/s)
        """
        source = {
            'x': x,
            'y': y,
            'Q': Q_discharge,
            'C': C_discharge,
            'Q_river': Q_river
        }
        self.sources.append(source)
        
        print(f"\n添加排放源:")
        print(f"  位置: ({x}, {y}) m")
        print(f"  排放流量: {Q_discharge} m³/s")
        print(f"  排放浓度: {C_discharge} mg/L")
    
    def calculate_secondary_flow_velocity(self, y):
        """
        计算弯道二次流横向速度分量
        
        二次流特征：
        - 表层水流向凹岸（外岸）
        - 底层水流向凸岸（内岸）
        - 形成横向环流
        
        简化模型：
        v(y) = v_max * sin(π*y/B)
        
        其中v_max与流速和曲率有关
        
        参数：
            y: 横向坐标 (m)
            
        返回：
            v: 横向流速 (m/s)
        """
        # 最大横向流速（经验估算）
        # v_max ≈ 0.1 * u * (B/R)
        v_max = 0.1 * self.u * (self.B / self.R)
        
        # 正弦分布（简化）
        v = v_max * np.sin(np.pi * y / self.B)
        
        return v
    
    def solve_with_secondary_flow(self):
        """
        求解考虑二次流的浓度场
        
        方法：
        1. 使用增强的横向扩散系数
        2. 叠加横向对流效应
        3. 浓度偏向凹岸
        """
        print(f"\n求解考虑二次流的浓度场...")
        
        # 初始化
        C = np.zeros((self.ny, self.nx))
        
        # 设置排放源
        for source in self.sources:
            ix = np.argmin(np.abs(self.x - source['x']))
            iy = np.argmin(np.abs(self.y - source['y']))
            C[iy, ix] = source['C']
        
        # 从上游向下游逐列求解
        for i in range(1, self.nx):
            C_prev = C[:, i-1].copy()
            
            # 伪时间步进
            dt = 0.5 * self.dy**2 / self.Ey_effective
            travel_time = self.dx / self.u
            n_steps = max(int(travel_time / dt), 10)
            
            C_new = C_prev.copy()
            for _ in range(n_steps):
                C_temp = C_new.copy()
                
                # 横向扩散（增强）
                for j in range(1, self.ny-1):
                    d2C_dy2 = (C_new[j+1] - 2*C_new[j] + C_new[j-1]) / self.dy**2
                    C_temp[j] = C_new[j] + dt * self.Ey_effective * d2C_dy2
                    
                    # 二次流横向对流（可选）
                    if j > 0 and j < self.ny - 1:
                        v_secondary = self.calculate_secondary_flow_velocity(self.y[j])
                        if v_secondary > 0:  # 向外岸
                            dC_dy = (C_new[j+1] - C_new[j]) / self.dy
                        else:  # 向内岸
                            dC_dy = (C_new[j] - C_new[j-1]) / self.dy
                        
                        # 二次流对流项
                        C_temp[j] -= dt * v_secondary * dC_dy
                
                # 边界条件：零通量
                C_temp[0] = C_temp[1]
                C_temp[-1] = C_temp[-2]
                
                C_new = C_temp
            
            C[:, i] = C_new
        
        self.C = C
        
        print(f"求解完成！")
        print(f"  最大浓度: {np.max(C):.2f} mg/L")
        
        return self.x, self.y, self.C
    
    def calculate_concentration_shift(self):
        """
        计算浓度偏向（凹岸侧浓度高于凸岸侧）
        
        返回：
            shift_ratio: 浓度偏向比（凹岸/凸岸）
        """
        if self.C is None:
            raise ValueError("请先求解浓度场")
        
        # 在下游某断面计算
        ix = self.nx // 2
        C_section = self.C[:, ix]
        
        # 凹岸侧（假设在y=B侧）
        C_outer = np.mean(C_section[self.ny*3//4:])
        
        # 凸岸侧（假设在y=0侧）
        C_inner = np.mean(C_section[:self.ny//4])
        
        if C_inner > 0:
            shift_ratio = C_outer / C_inner
        else:
            shift_ratio = 1.0
        
        print(f"\n浓度偏向分析:")
        print(f"  凹岸侧平均浓度: {C_outer:.2f} mg/L")
        print(f"  凸岸侧平均浓度: {C_inner:.2f} mg/L")
        print(f"  偏向比: {shift_ratio:.2f}")
        
        return shift_ratio


def calculate_bend_mixing_length(B, u, Ey_straight, K_bend):
    """
    计算弯道混合长度
    
    弯道混合长度 = 直道混合长度 / K_bend
    
    参数：
        B: 河宽 (m)
        u: 流速 (m/s)
        Ey_straight: 直道横向扩散系数 (m²/s)
        K_bend: 弯道增强系数
        
    返回：
        L_mix_bend: 弯道混合长度 (m)
        L_mix_straight: 直道混合长度 (m)
    """
    # 直道混合长度
    L_mix_straight = 0.4 * u * B**2 / Ey_straight
    
    # 弯道混合长度（缩短）
    L_mix_bend = L_mix_straight / K_bend
    
    print(f"混合长度对比:")
    print(f"  直道混合长度: {L_mix_straight/1000:.2f} km")
    print(f"  弯道混合长度: {L_mix_bend/1000:.2f} km")
    print(f"  缩短比例: {(1 - L_mix_bend/L_mix_straight)*100:.0f}%")
    
    return L_mix_bend, L_mix_straight


def calculate_curvature_radius(bend_length, bend_angle):
    """
    根据弯道长度和转角计算曲率半径
    
    R = L / θ (θ为弧度)
    
    参数：
        bend_length: 弯道长度 (m)
        bend_angle: 弯道转角 (度)
        
    返回：
        R: 曲率半径 (m)
    """
    # 转换为弧度
    theta_rad = np.deg2rad(bend_angle)
    
    # 计算曲率半径
    R = bend_length / theta_rad
    
    print(f"弯道几何参数:")
    print(f"  弯道长度: {bend_length} m")
    print(f"  转角: {bend_angle}°")
    print(f"  曲率半径: {R:.0f} m")
    
    return R


def calculate_secondary_flow_strength(u, R, B, H):
    """
    计算二次流强度
    
    二次流强度与以下因素有关：
    - 流速u
    - 曲率半径R
    - 河宽B
    - 水深H
    
    参数：
        u: 流速 (m/s)
        R: 曲率半径 (m)
        B: 河宽 (m)
        H: 水深 (m)
        
    返回：
        v_max: 最大横向流速 (m/s)
        Fr: Froude数
    """
    # Froude数
    g = 9.81
    Fr = u / np.sqrt(g * H)
    
    # 最大横向流速（经验公式）
    v_max = 0.1 * u * (B / R)
    
    # 横向流速与纵向流速比
    v_u_ratio = v_max / u
    
    print(f"二次流特征:")
    print(f"  Froude数: {Fr:.3f}")
    print(f"  最大横向流速: {v_max:.4f} m/s")
    print(f"  横纵流速比: {v_u_ratio:.3f}")
    
    return v_max, Fr
