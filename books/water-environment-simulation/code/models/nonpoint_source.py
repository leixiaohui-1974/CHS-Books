"""
非点源污染模拟模型
Non-Point Source Pollution Model

包括：
1. SCS-CN径流计算
2. EMC污染负荷估算
3. 分布式源项模拟
4. 降雨-径流-污染耦合
"""

import numpy as np


class SCSCurveNumber:
    """
    SCS-CN径流计算模型
    
    SCS (Soil Conservation Service) 曲线数法
    用于计算降雨产流
    
    基本方程：
    Q = (P - Ia)² / (P - Ia + S)
    其中：
    - Q: 径流深 (mm)
    - P: 降雨量 (mm)
    - Ia: 初损 (mm), Ia = 0.2*S
    - S: 最大潜在滞留量 (mm), S = 25400/CN - 254
    - CN: 曲线数 (30-100)
    
    参数：
        CN: 曲线数 (dimensionless, 30-100)
        area: 汇水面积 (km²)
    """
    
    def __init__(self, CN, area):
        """初始化SCS-CN模型"""
        self.CN = CN
        self.area = area
        
        # 计算最大滞留量
        self.S = 25400.0 / CN - 254.0  # mm
        
        # 初损（经验值：0.2*S）
        self.Ia = 0.2 * self.S  # mm
        
        print(f"SCS-CN模型初始化:")
        print(f"  曲线数 CN = {CN}")
        print(f"  汇水面积 = {area} km²")
        print(f"  最大滞留量 S = {self.S:.1f} mm")
        print(f"  初损 Ia = {self.Ia:.1f} mm")
    
    def calculate_runoff(self, P):
        """
        计算径流深
        
        参数：
            P: 降雨量 (mm)
            
        返回：
            Q: 径流深 (mm)
            runoff_coefficient: 径流系数
        """
        if P <= self.Ia:
            Q = 0
            runoff_coefficient = 0
        else:
            Q = (P - self.Ia)**2 / (P - self.Ia + self.S)
            runoff_coefficient = Q / P
        
        return Q, runoff_coefficient
    
    def calculate_runoff_volume(self, P):
        """
        计算径流量
        
        参数：
            P: 降雨量 (mm)
            
        返回：
            V: 径流量 (m³)
        """
        Q, _ = self.calculate_runoff(P)
        
        # 转换为体积 (mm * km² = 1000 m³)
        V = Q * self.area * 1000
        
        return V
    
    @staticmethod
    def get_CN_from_landuse(landuse_type, soil_type='B', AMC='II'):
        """
        根据土地利用类型和土壤类型查表获取CN值
        
        参数：
            landuse_type: 土地利用类型
            soil_type: 土壤类型 (A, B, C, D)
            AMC: 前期土壤湿度条件 (I, II, III)
            
        返回：
            CN: 曲线数
        """
        # CN值查找表（AMC-II条件）
        CN_table = {
            'urban_residential': {'A': 77, 'B': 85, 'C': 90, 'D': 92},
            'urban_commercial': {'A': 89, 'B': 92, 'C': 94, 'D': 95},
            'urban_industrial': {'A': 81, 'B': 88, 'C': 91, 'D': 93},
            'agricultural_row_crops': {'A': 67, 'B': 78, 'C': 85, 'D': 89},
            'agricultural_pasture': {'A': 49, 'B': 69, 'C': 79, 'D': 84},
            'forest': {'A': 30, 'B': 55, 'C': 70, 'D': 77},
            'meadow': {'A': 30, 'B': 58, 'C': 71, 'D': 78},
            'water': {'A': 100, 'B': 100, 'C': 100, 'D': 100},
        }
        
        CN_II = CN_table.get(landuse_type, {}).get(soil_type, 75)
        
        # AMC条件校正
        if AMC == 'I':  # 干燥条件
            CN = CN_II / (2.281 - 0.01281 * CN_II)
        elif AMC == 'III':  # 湿润条件
            CN = CN_II / (0.427 + 0.00573 * CN_II)
        else:  # AMC-II
            CN = CN_II
        
        return CN


class EventMeanConcentration:
    """
    事件平均浓度（EMC）法
    
    用于估算非点源污染负荷
    
    基本方程：
    L = C * V * 10⁻⁶
    其中：
    - L: 污染负荷 (kg)
    - C: 事件平均浓度 (mg/L)
    - V: 径流量 (m³)
    
    参数：
        EMC_dict: 各污染物的EMC值字典 (mg/L)
    """
    
    def __init__(self, EMC_dict):
        """初始化EMC模型"""
        self.EMC_dict = EMC_dict
        
        print(f"EMC模型初始化:")
        for pollutant, emc in EMC_dict.items():
            print(f"  {pollutant}: EMC = {emc} mg/L")
    
    def calculate_load(self, V_runoff):
        """
        计算污染负荷
        
        参数：
            V_runoff: 径流量 (m³)
            
        返回：
            loads: 污染负荷字典 (kg)
        """
        loads = {}
        
        for pollutant, emc in self.EMC_dict.items():
            # L = C * V * 10⁻⁶ (mg/L * m³ → kg)
            L = emc * V_runoff * 1e-6
            loads[pollutant] = L
        
        return loads
    
    @staticmethod
    def get_typical_EMC(landuse_type, pollutant):
        """
        获取典型EMC值
        
        参数：
            landuse_type: 土地利用类型
            pollutant: 污染物类型
            
        返回：
            EMC: 事件平均浓度 (mg/L)
        """
        # 典型EMC值表
        EMC_table = {
            'urban_residential': {
                'TSS': 150, 'COD': 90, 'BOD': 15,
                'TN': 2.5, 'TP': 0.4, 'NH3-N': 1.2
            },
            'urban_commercial': {
                'TSS': 200, 'COD': 120, 'BOD': 18,
                'TN': 3.0, 'TP': 0.5, 'NH3-N': 1.5
            },
            'urban_industrial': {
                'TSS': 300, 'COD': 180, 'BOD': 25,
                'TN': 4.0, 'TP': 0.7, 'NH3-N': 2.0
            },
            'agricultural_row_crops': {
                'TSS': 500, 'COD': 80, 'BOD': 12,
                'TN': 5.0, 'TP': 1.2, 'NH3-N': 1.0
            },
            'agricultural_pasture': {
                'TSS': 300, 'COD': 60, 'BOD': 10,
                'TN': 3.5, 'TP': 0.8, 'NH3-N': 0.8
            },
        }
        
        return EMC_table.get(landuse_type, {}).get(pollutant, 0)


class NonPointSourceRiver1D:
    """
    非点源污染河流模拟
    
    耦合点源和非点源污染
    
    控制方程：
    u * ∂C/∂x = D * ∂²C/∂x² - k * C + S_nps(x)
    
    其中：
    - S_nps(x): 非点源源项 (kg/m/s)
    
    参数：
        L: 河段长度 (m)
        nx: 空间节点数
        u: 流速 (m/s)
        D: 扩散系数 (m²/s)
        k: 降解系数 (1/s)
        Q_river: 河流流量 (m³/s)
        C0: 上游本底浓度 (mg/L)
    """
    
    def __init__(self, L, nx, u, D, k, Q_river, C0=0):
        """初始化非点源河流模型"""
        self.L = L
        self.nx = nx
        self.u = u
        self.D = D
        self.k = k
        self.Q_river = Q_river
        self.C0 = C0
        
        # 空间离散
        self.x = np.linspace(0, L, nx)
        self.dx = L / (nx - 1)
        
        # 非点源源项（初始为0）
        self.S_nps = np.zeros(nx)  # kg/m/s
        
        # 结果
        self.C = None
        
        print(f"非点源河流模型初始化:")
        print(f"  河段长度 L = {L/1000} km")
        print(f"  流速 u = {u} m/s")
        print(f"  河流流量 Q = {Q_river} m³/s")
    
    def add_distributed_source(self, x_start, x_end, load_rate):
        """
        添加分布式非点源
        
        参数：
            x_start: 起点位置 (m)
            x_end: 终点位置 (m)
            load_rate: 单位长度污染负荷 (kg/m/day)
        """
        # 转换为 kg/m/s
        load_rate_s = load_rate / 86400
        
        # 找到对应的节点范围
        mask = (self.x >= x_start) & (self.x <= x_end)
        self.S_nps[mask] += load_rate_s
        
        total_load = load_rate * (x_end - x_start)
        print(f"添加分布式源项:")
        print(f"  位置: {x_start/1000:.1f} - {x_end/1000:.1f} km")
        print(f"  单位负荷: {load_rate:.3f} kg/m/day")
        print(f"  总负荷: {total_load:.1f} kg/day")
    
    def add_rainfall_runoff_source(self, x_start, x_end, V_runoff, C_runoff, duration):
        """
        添加降雨径流非点源
        
        参数：
            x_start: 起点位置 (m)
            x_end: 终点位置 (m)
            V_runoff: 总径流量 (m³)
            C_runoff: 径流浓度 (mg/L)
            duration: 径流持续时间 (hour)
        """
        # 计算总负荷 (kg)
        total_load = V_runoff * C_runoff * 1e-6
        
        # 转换为单位长度负荷率 (kg/m/s)
        length = x_end - x_start
        duration_s = duration * 3600
        load_rate_s = total_load / length / duration_s
        
        # 添加到源项
        mask = (self.x >= x_start) & (self.x <= x_end)
        self.S_nps[mask] += load_rate_s
        
        print(f"添加降雨径流源项:")
        print(f"  位置: {x_start/1000:.1f} - {x_end/1000:.1f} km")
        print(f"  径流量: {V_runoff:.0f} m³")
        print(f"  径流浓度: {C_runoff:.1f} mg/L")
        print(f"  总负荷: {total_load:.1f} kg")
        print(f"  持续时间: {duration} hour")
    
    def solve(self):
        """
        求解非点源河流水质
        
        使用有限差分法求解稳态方程
        简化：使用解析解 + 源项叠加
        """
        print("\n" + "="*70)
        print("求解非点源河流水质模拟")
        print("="*70)
        
        C = np.zeros(self.nx)
        C[0] = self.C0
        
        # 逐点求解
        for i in range(1, self.nx):
            dx = self.x[i] - self.x[i-1]
            
            # 对流-扩散-反应（简化：忽略扩散）
            # C(i) = C(i-1) * exp(-k*dx/u) + S_nps(i) * dx / (Q * u)
            
            decay_factor = np.exp(-self.k * dx / self.u) if self.k > 0 else 1.0
            C[i] = C[i-1] * decay_factor
            
            # 添加非点源贡献
            if self.S_nps[i] > 0:
                # S_nps单位: kg/m/s
                # 转换为浓度增量: ΔC = S * dx / Q (mg/L)
                delta_C = self.S_nps[i] * dx / self.Q_river * 1e6
                C[i] += delta_C
        
        self.C = C
        
        print(f"\n求解完成！")
        print(f"  最大浓度: {np.max(C):.2f} mg/L")
        print(f"  最小浓度: {np.min(C):.2f} mg/L")
        
        return self.x, self.C
    
    def calculate_total_load(self):
        """
        计算总污染负荷
        
        返回：
            total_load: 总负荷 (kg/day)
        """
        # 积分源项
        total_load_s = np.trapz(self.S_nps, self.x)  # kg/s
        total_load = total_load_s * 86400  # kg/day
        
        return total_load


def calculate_first_flush_factor(rainfall_duration, V_initial_fraction=0.3):
    """
    计算初期冲刷系数
    
    初期冲刷现象：降雨初期污染物浓度高
    
    参数：
        rainfall_duration: 降雨持续时间 (hour)
        V_initial_fraction: 初期径流占比（默认30%）
        
    返回：
        ff_factor: 初期冲刷系数
    """
    # 简化模型：初期30%径流携带60-80%污染物
    if rainfall_duration < 2:
        ff_factor = 2.5  # 短时强降雨，初期冲刷强
    elif rainfall_duration < 6:
        ff_factor = 2.0  # 中等降雨
    else:
        ff_factor = 1.5  # 长时降雨，初期冲刷弱
    
    print(f"初期冲刷系数: {ff_factor:.1f}")
    
    return ff_factor


def calculate_buildup_washoff(days_since_last_rain, rainfall_intensity):
    """
    计算累积-冲刷负荷
    
    累积-冲刷模型：
    - 累积期：污染物在地表累积
    - 冲刷期：降雨冲刷地表污染物
    
    参数：
        days_since_last_rain: 距上次降雨天数
        rainfall_intensity: 降雨强度 (mm/hr)
        
    返回：
        washoff_factor: 冲刷系数
    """
    # 累积量（指数累积）
    buildup = 1 - np.exp(-0.3 * days_since_last_rain)
    
    # 冲刷效率（与降雨强度相关）
    if rainfall_intensity < 5:
        washoff_efficiency = 0.3
    elif rainfall_intensity < 20:
        washoff_efficiency = 0.6
    else:
        washoff_efficiency = 0.9
    
    washoff_factor = buildup * washoff_efficiency
    
    print(f"累积-冲刷系数:")
    print(f"  累积: {buildup:.2f}")
    print(f"  冲刷效率: {washoff_efficiency:.2f}")
    print(f"  → 冲刷系数: {washoff_factor:.2f}")
    
    return washoff_factor
