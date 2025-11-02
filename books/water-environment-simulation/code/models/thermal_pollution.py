"""
热污染扩散模型
Thermal Pollution Model

包括：
1. 温排水扩散模拟
2. 温度场计算
3. 混合区评估
4. 热冲击影响
"""

import numpy as np


class ThermalPlume2D:
    """
    二维温排水羽流模型
    
    适用于侧向排放的温排水扩散
    
    控制方程：
    ∂T/∂t + u*∂T/∂x + v*∂T/∂y = Kx*∂²T/∂x² + Ky*∂²T/∂y² - λ*(T-Ta)
    
    其中：
    - T: 温度 (°C)
    - u, v: 流速分量 (m/s)
    - Kx, Ky: 扩散系数 (m²/s)
    - λ: 表面热交换系数 (1/s)
    - Ta: 环境温度 (°C)
    
    参数：
        Lx: x方向长度 (m)
        Ly: y方向宽度 (m)
        nx: x方向节点数
        ny: y方向节点数
        u: x方向流速 (m/s)
        Kx: x方向扩散系数 (m²/s)
        Ky: y方向扩散系数 (m²/s)
        lambda_surface: 表面热交换系数 (1/day)
        T_ambient: 环境温度 (°C)
    """
    
    def __init__(self, Lx, Ly, nx, ny, u, Kx, Ky, lambda_surface, T_ambient):
        """初始化二维温排水模型"""
        self.Lx = Lx
        self.Ly = Ly
        self.nx = nx
        self.ny = ny
        self.u = u
        self.Kx = Kx
        self.Ky = Ky
        self.lambda_s = lambda_surface / 86400  # 转换为1/s
        self.T_ambient = T_ambient
        
        # 空间离散
        self.x = np.linspace(0, Lx, nx)
        self.y = np.linspace(-Ly/2, Ly/2, ny)
        self.dx = Lx / (nx - 1)
        self.dy = Ly / (ny - 1)
        
        # 温度场
        self.T = None
        
        # 排放源
        self.source_x = 0
        self.source_y = 0
        self.Q_thermal = 0  # 热排放量 (MW)
        self.T_discharge = T_ambient
        
        print(f"二维温排水模型初始化:")
        print(f"  计算域: {Lx}m × {Ly}m")
        print(f"  网格: {nx} × {ny}")
        print(f"  流速 u = {u} m/s")
        print(f"  环境温度 = {T_ambient}°C")
    
    def set_discharge(self, x, y, Q_discharge, T_discharge, Q_river):
        """
        设置温排水源
        
        参数：
            x: 排放口x坐标 (m)
            y: 排放口y坐标 (m)
            Q_discharge: 排放流量 (m³/s)
            T_discharge: 排放温度 (°C)
            Q_river: 河流流量 (m³/s)
        """
        self.source_x = x
        self.source_y = y
        self.T_discharge = T_discharge
        
        # 计算热排放量 (MW)
        # Q = ρ * Cp * Q * ΔT
        # ρ*Cp ≈ 4.18 MJ/m³/°C
        self.Q_thermal = 4.18 * Q_discharge * (T_discharge - self.T_ambient)
        
        print(f"\n温排水源设置:")
        print(f"  位置: ({x}, {y}) m")
        print(f"  排放流量: {Q_discharge} m³/s")
        print(f"  排放温度: {T_discharge}°C")
        print(f"  温升: {T_discharge - self.T_ambient}°C")
        print(f"  热排放量: {self.Q_thermal:.2f} MW")
    
    def solve_steady_state(self):
        """
        求解稳态温度场
        
        使用解析解（简化羽流模型）
        """
        print("\n求解稳态温度场...")
        
        # 初始化温度场
        T = np.ones((self.ny, self.nx)) * self.T_ambient
        
        # 找到源点位置
        ix = np.argmin(np.abs(self.x - self.source_x))
        iy = np.argmin(np.abs(self.y - self.source_y))
        
        # 简化解析解（高斯羽流模型）
        for i in range(self.nx):
            for j in range(self.ny):
                x_dist = self.x[i] - self.source_x
                y_dist = self.y[j] - self.source_y
                
                if x_dist > 0:
                    # 纵向扩散宽度
                    sigma_y = np.sqrt(2 * self.Ky * x_dist / self.u)
                    
                    # 高斯分布
                    if sigma_y > 0:
                        gauss_factor = np.exp(-y_dist**2 / (2 * sigma_y**2))
                        
                        # 考虑表面热交换的衰减
                        decay_factor = np.exp(-self.lambda_s * x_dist / self.u)
                        
                        # 温升
                        delta_T = (self.T_discharge - self.T_ambient) * gauss_factor * decay_factor
                        T[j, i] = self.T_ambient + delta_T
        
        self.T = T
        
        print(f"求解完成！")
        print(f"  最高温度: {np.max(T):.2f}°C")
        print(f"  最大温升: {np.max(T) - self.T_ambient:.2f}°C")
        
        return self.x, self.y, self.T
    
    def calculate_mixing_zone(self, T_standard):
        """
        计算混合区
        
        混合区：温升超过标准的区域
        
        参数：
            T_standard: 温度标准 (°C)
            
        返回：
            area: 混合区面积 (m²)
            length: 混合区长度 (m)
            width: 混合区宽度 (m)
        """
        if self.T is None:
            raise ValueError("请先求解温度场")
        
        # 超标区域
        exceed_mask = self.T > T_standard
        
        # 计算面积
        area = np.sum(exceed_mask) * self.dx * self.dy
        
        # 计算长度（x方向最大范围）
        exceed_x = np.any(exceed_mask, axis=0)
        if np.any(exceed_x):
            x_indices = np.where(exceed_x)[0]
            length = (x_indices[-1] - x_indices[0]) * self.dx
        else:
            length = 0
        
        # 计算宽度（y方向最大范围）
        exceed_y = np.any(exceed_mask, axis=1)
        if np.any(exceed_y):
            y_indices = np.where(exceed_y)[0]
            width = (y_indices[-1] - y_indices[0]) * self.dy
        else:
            width = 0
        
        print(f"\n混合区评估（标准: {T_standard}°C）:")
        print(f"  面积: {area:.0f} m²")
        print(f"  长度: {length:.0f} m")
        print(f"  宽度: {width:.0f} m")
        
        return area, length, width
    
    def calculate_thermal_impact(self, T_critical):
        """
        计算热冲击影响范围
        
        参数：
            T_critical: 临界温度 (°C)
            
        返回：
            impact_area: 影响区域面积 (m²)
            max_delta_T: 最大温升 (°C)
        """
        if self.T is None:
            raise ValueError("请先求解温度场")
        
        # 超过临界温度的区域
        impact_mask = self.T > T_critical
        impact_area = np.sum(impact_mask) * self.dx * self.dy
        
        # 最大温升
        max_delta_T = np.max(self.T) - self.T_ambient
        
        print(f"\n热冲击影响评估（临界温度: {T_critical}°C）:")
        print(f"  影响面积: {impact_area:.0f} m²")
        print(f"  最大温升: {max_delta_T:.2f}°C")
        
        return impact_area, max_delta_T


def calculate_surface_heat_exchange(T_water, T_air, wind_speed, solar_radiation=0):
    """
    计算水面热交换系数
    
    水面热交换包括：
    1. 蒸发散热
    2. 对流散热
    3. 辐射散热
    4. 太阳辐射加热
    
    参数：
        T_water: 水温 (°C)
        T_air: 气温 (°C)
        wind_speed: 风速 (m/s)
        solar_radiation: 太阳辐射 (W/m²)
        
    返回：
        lambda_s: 表面热交换系数 (1/day)
        Q_net: 净热通量 (W/m²)
    """
    # 蒸发散热系数（经验公式）
    # He = f(u) * (es - ea)
    # f(u) ≈ 9.2 + 0.46 * u² (Brady公式)
    f_u = 9.2 + 0.46 * wind_speed**2
    
    # 饱和蒸汽压（Magnus公式，简化）
    es = 611 * np.exp(17.27 * T_water / (T_water + 237.3))  # Pa
    ea = 611 * np.exp(17.27 * T_air / (T_air + 237.3)) * 0.7  # 假设相对湿度70%
    
    # 蒸发散热 (W/m²)
    Q_evap = f_u * (es - ea) / 1000
    
    # 对流散热（简化）
    # Hc ≈ 4.5 * (1 + 0.2*u) * (Tw - Ta)
    Q_conv = 4.5 * (1 + 0.2 * wind_speed) * (T_water - T_air)
    
    # 辐射散热（简化）
    # Hr ≈ 5.5 * (Tw - Ta)
    Q_rad = 5.5 * (T_water - T_air)
    
    # 净热通量
    Q_net = -(Q_evap + Q_conv + Q_rad) + solar_radiation
    
    # 转换为热交换系数
    # λ = Q / (ρ * Cp * H * ΔT)
    # 假设平均水深H=2m, ρ*Cp=4.18MJ/m³/°C
    if T_water > T_air:
        lambda_s = abs(Q_net) / (4.18e6 * 2.0 * (T_water - T_air)) * 86400  # 1/day
    else:
        lambda_s = 0.05  # 默认值
    
    print(f"水面热交换:")
    print(f"  蒸发散热: {Q_evap:.1f} W/m²")
    print(f"  对流散热: {Q_conv:.1f} W/m²")
    print(f"  辐射散热: {Q_rad:.1f} W/m²")
    print(f"  太阳辐射: {solar_radiation:.1f} W/m²")
    print(f"  净热通量: {Q_net:.1f} W/m²")
    print(f"  热交换系数: {lambda_s:.3f} day⁻¹")
    
    return lambda_s, Q_net


def calculate_thermal_tolerance(species, T_base, duration):
    """
    计算生物热耐受性
    
    不同物种对温度升高的耐受性不同
    
    参数：
        species: 物种类型
        T_base: 基准温度 (°C)
        duration: 暴露时间 (hour)
        
    返回：
        T_lethal: 致死温度 (°C)
        T_stress: 胁迫温度 (°C)
    """
    # 典型物种热耐受性（简化）
    thermal_tolerance = {
        'cold_water_fish': {  # 冷水鱼（如鲑鱼）
            'T_optimal': (10, 15),
            'T_stress': 20,
            'T_lethal': 24
        },
        'warm_water_fish': {  # 温水鱼（如鲤鱼）
            'T_optimal': (20, 28),
            'T_stress': 32,
            'T_lethal': 35
        },
        'invertebrates': {  # 无脊椎动物
            'T_optimal': (15, 25),
            'T_stress': 28,
            'T_lethal': 32
        },
        'algae': {  # 藻类
            'T_optimal': (20, 30),
            'T_stress': 35,
            'T_lethal': 40
        }
    }
    
    tolerance = thermal_tolerance.get(species, thermal_tolerance['warm_water_fish'])
    
    # 考虑暴露时间的修正（长时间暴露降低耐受性）
    time_factor = 1.0
    if duration > 24:
        time_factor = 0.9
    elif duration > 48:
        time_factor = 0.8
    
    T_stress = tolerance['T_stress'] * time_factor
    T_lethal = tolerance['T_lethal'] * time_factor
    
    print(f"\n{species}热耐受性:")
    print(f"  最适温度: {tolerance['T_optimal'][0]}-{tolerance['T_optimal'][1]}°C")
    print(f"  胁迫温度: {T_stress:.1f}°C")
    print(f"  致死温度: {T_lethal:.1f}°C")
    print(f"  (暴露时间: {duration} hour, 修正系数: {time_factor})")
    
    return T_lethal, T_stress


def calculate_cooling_efficiency(T_in, T_out, T_ambient, Q_cooling):
    """
    计算冷却效率
    
    参数：
        T_in: 进水温度 (°C)
        T_out: 出水温度 (°C)
        T_ambient: 环境温度 (°C)
        Q_cooling: 冷却水流量 (m³/s)
        
    返回：
        efficiency: 冷却效率
        Q_removed: 移除热量 (MW)
    """
    # 实际温降
    delta_T_actual = T_in - T_out
    
    # 理论最大温降
    delta_T_max = T_in - T_ambient
    
    # 冷却效率
    if delta_T_max > 0:
        efficiency = delta_T_actual / delta_T_max
    else:
        efficiency = 0
    
    # 移除热量
    Q_removed = 4.18 * Q_cooling * delta_T_actual  # MW
    
    print(f"冷却效率评估:")
    print(f"  进水温度: {T_in}°C")
    print(f"  出水温度: {T_out}°C")
    print(f"  实际温降: {delta_T_actual}°C")
    print(f"  理论温降: {delta_T_max}°C")
    print(f"  冷却效率: {efficiency:.1%}")
    print(f"  移除热量: {Q_removed:.2f} MW")
    
    return efficiency, Q_removed
