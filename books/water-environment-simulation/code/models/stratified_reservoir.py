"""
水库温度分层与水质模拟（1D垂向模型）
Stratified Reservoir Temperature and Water Quality Model

用于模拟深水水库的温度分层和溶解氧垂向分布
"""

import numpy as np
from scipy.integrate import odeint


class StratifiedReservoir1D:
    """
    1D垂向分层水库模型
    
    控制方程：
    ∂T/∂t = ∂/∂z(Kz * ∂T/∂z) + Q_heat
    ∂DO/∂t = ∂/∂z(Kz * ∂DO/∂z) + Source - Sink
    
    其中：
    - T: 温度 (°C)
    - DO: 溶解氧 (mg/L)
    - Kz: 垂向扩散系数 (m²/d)
    - Q_heat: 热源项 (°C/d)
    - Source: DO产生（光合作用）
    - Sink: DO消耗（呼吸、SOD）
    """
    
    def __init__(self, H, nz, T_init=None, DO_init=None):
        """
        初始化分层水库模型
        
        参数：
        - H: 水深 (m)
        - nz: 垂向节点数
        - T_init: 初始温度分布 (°C)
        - DO_init: 初始DO分布 (mg/L)
        """
        self.H = H
        self.nz = nz
        self.dz = H / (nz - 1)
        self.z = np.linspace(0, H, nz)  # 0=表层, H=底层
        
        # 初始化温度和DO
        if T_init is None:
            self.T = np.ones(nz) * 20  # 初始均匀20°C
        else:
            self.T = T_init
        
        if DO_init is None:
            self.DO = np.ones(nz) * 8  # 初始均匀8 mg/L
        else:
            self.DO = DO_init
        
        # 参数
        self.Kz = 1e-5 * np.ones(nz)  # 垂向扩散系数 (m²/d)，默认强分层
        self.SOD = 0.5  # 沉积物耗氧速率 (g/m²/d)
        
        print(f"分层水库模型初始化:")
        print(f"  水深: {self.H} m")
        print(f"  节点数: {self.nz}")
        print(f"  垂向分辨率: {self.dz:.2f} m")
        print(f"  初始温度: {self.T[0]:.1f}°C (表层) - {self.T[-1]:.1f}°C (底层)")
        print(f"  初始DO: {self.DO[0]:.1f} mg/L (表层) - {self.DO[-1]:.1f} mg/L (底层)")
    
    def set_vertical_diffusivity(self, Kz):
        """
        设置垂向扩散系数
        
        参数：
        - Kz: 扩散系数 (m²/d) 或数组
        
        典型值：
        - 强分层（夏季温跃层）: 1e-6 - 1e-5 m²/d
        - 弱分层: 1e-4 - 1e-3 m²/d
        - 完全混合: > 1e-2 m²/d
        """
        if np.isscalar(Kz):
            self.Kz = Kz * np.ones(self.nz)
        else:
            self.Kz = Kz
        
        print(f"\n垂向扩散系数设置:")
        print(f"  表层: {self.Kz[0]:.2e} m²/d")
        print(f"  底层: {self.Kz[-1]:.2e} m²/d")
    
    def calculate_thermocline_depth(self):
        """
        计算温跃层深度
        
        温跃层定义为温度梯度最大的位置
        
        返回：
        - z_thermocline: 温跃层深度 (m)
        - dT_dz_max: 最大温度梯度 (°C/m)
        """
        dT_dz = np.diff(self.T) / self.dz
        idx_max = np.argmax(np.abs(dT_dz))
        z_thermocline = self.z[idx_max]
        dT_dz_max = dT_dz[idx_max]
        
        print(f"\n温跃层计算:")
        print(f"  温跃层深度: {z_thermocline:.1f} m")
        print(f"  最大温度梯度: {dT_dz_max:.2f} °C/m")
        
        return z_thermocline, dT_dz_max
    
    def solve_temperature_1d(self, t_span, T_surface=None, Q_bottom=0):
        """
        求解1D垂向温度扩散
        
        参数：
        - t_span: 时间数组 (d)
        - T_surface: 表层温度函数 T(t) 或常数
        - Q_bottom: 底层热通量 (W/m²)
        
        返回：
        - t: 时间数组
        - T: 温度场 (nz, nt)
        """
        if T_surface is None:
            T_surface = lambda t: self.T[0]
        elif np.isscalar(T_surface):
            T_surf_const = T_surface
            T_surface = lambda t: T_surf_const
        
        def dT_dt(T, t):
            dT = np.zeros_like(T)
            
            # 内部节点：扩散
            for i in range(1, self.nz-1):
                Kz_up = (self.Kz[i] + self.Kz[i-1]) / 2
                Kz_down = (self.Kz[i] + self.Kz[i+1]) / 2
                
                d2T_dz2 = (Kz_down * (T[i+1] - T[i]) - Kz_up * (T[i] - T[i-1])) / self.dz**2
                dT[i] = d2T_dz2
            
            # 边界：表层固定温度
            dT[0] = (T_surface(t) - T[0]) / 0.1  # 松弛到表层温度
            
            # 边界：底层零通量或固定通量
            dT[-1] = dT[-2]  # 零梯度
            
            return dT
        
        # 求解
        T_result = odeint(dT_dt, self.T, t_span)
        
        self.T = T_result[-1, :]  # 更新为最终状态
        
        print(f"\n温度场求解完成:")
        print(f"  时间范围: {t_span[0]:.1f} - {t_span[-1]:.1f} d")
        print(f"  最终表层温度: {self.T[0]:.1f}°C")
        print(f"  最终底层温度: {self.T[-1]:.1f}°C")
        
        return t_span, T_result.T
    
    def solve_do_1d(self, t_span, DO_surface=None, photosynthesis=True):
        """
        求解1D垂向DO分布
        
        参数：
        - t_span: 时间数组 (d)
        - DO_surface: 表层DO (mg/L)，None则为饱和
        - photosynthesis: 是否考虑光合作用
        
        返回：
        - t: 时间数组
        - DO: DO场 (nz, nt)
        """
        def calculate_DO_saturation(T):
            """计算饱和DO (Benson-Krause方程)"""
            return 14.652 - 0.41022*T + 0.007991*T**2 - 0.000077774*T**3
        
        if DO_surface is None:
            DO_surface = calculate_DO_saturation(self.T[0])
        
        def dDO_dt(DO, t):
            dDO = np.zeros_like(DO)
            
            # 内部节点：扩散 + 反应
            for i in range(1, self.nz-1):
                Kz_up = (self.Kz[i] + self.Kz[i-1]) / 2
                Kz_down = (self.Kz[i] + self.Kz[i+1]) / 2
                
                # 扩散项
                d2DO_dz2 = (Kz_down * (DO[i+1] - DO[i]) - Kz_up * (DO[i] - DO[i-1])) / self.dz**2
                
                # 反应项
                reaction = 0
                
                # 光合作用（仅表层光照区）
                if photosynthesis and self.z[i] < 10:  # 透光层10m
                    light_factor = np.exp(-0.3 * self.z[i])  # 光衰减
                    photosynthesis_rate = 2.0 * light_factor  # mg/L/d
                    reaction += photosynthesis_rate
                
                # 呼吸消耗
                respiration = 0.5  # mg/L/d
                reaction -= respiration
                
                dDO[i] = d2DO_dz2 + reaction
            
            # 边界：表层DO
            dDO[0] = (DO_surface - DO[0]) / 0.1
            
            # 边界：底层SOD
            SOD_flux = self.SOD / self.dz  # mg/L/d
            dDO[-1] = dDO[-2] - SOD_flux
            
            return dDO
        
        # 求解
        DO_result = odeint(dDO_dt, self.DO, t_span)
        
        self.DO = DO_result[-1, :]  # 更新
        
        print(f"\nDO场求解完成:")
        print(f"  时间范围: {t_span[0]:.1f} - {t_span[-1]:.1f} d")
        print(f"  最终表层DO: {self.DO[0]:.1f} mg/L")
        print(f"  最终底层DO: {self.DO[-1]:.1f} mg/L")
        
        return t_span, DO_result.T
    
    def assess_anoxia_risk(self, DO_threshold=2.0):
        """
        评估缺氧风险
        
        参数：
        - DO_threshold: 缺氧阈值 (mg/L)
        
        返回：
        - anoxic_depth: 缺氧层深度 (m)
        - anoxic_volume_fraction: 缺氧水体比例
        """
        anoxic_mask = self.DO < DO_threshold
        
        if np.any(anoxic_mask):
            anoxic_depth = self.z[np.where(anoxic_mask)[0][0]]
            anoxic_volume_fraction = np.sum(anoxic_mask) / self.nz
        else:
            anoxic_depth = None
            anoxic_volume_fraction = 0
        
        print(f"\n缺氧风险评估:")
        print(f"  缺氧阈值: {DO_threshold} mg/L")
        if anoxic_depth is not None:
            print(f"  缺氧层起始深度: {anoxic_depth:.1f} m")
            print(f"  缺氧水体比例: {anoxic_volume_fraction*100:.1f}%")
            print(f"  ⚠️  存在缺氧风险")
        else:
            print(f"  ✓ 无缺氧风险")
        
        return anoxic_depth, anoxic_volume_fraction


def calculate_buoyancy_frequency(T, z):
    """
    计算浮力频率（Brunt-Väisälä频率）
    
    N² = -(g/ρ) * dρ/dz ≈ -(g/ρ) * α * dT/dz
    
    其中α是热膨胀系数 ≈ 2e-4 /°C
    
    参数：
    - T: 温度分布 (°C)
    - z: 深度数组 (m)
    
    返回：
    - N2: 浮力频率平方 (1/s²)
    """
    g = 9.81  # m/s²
    alpha = 2e-4  # /°C
    
    dT_dz = np.gradient(T, z)
    N2 = -g * alpha * dT_dz
    
    return N2


def calculate_richardson_number(T, z, u=0.01):
    """
    计算Richardson数（分层稳定性）
    
    Ri = N²/(du/dz)²
    
    Ri > 1: 强分层
    Ri < 0.25: 弱分层，易混合
    
    参数：
    - T: 温度分布
    - z: 深度
    - u: 流速尺度 (m/s)
    
    返回：
    - Ri: Richardson数
    """
    N2 = calculate_buoyancy_frequency(T, z)
    du_dz = u / (z[-1] - z[0])  # 简化
    
    Ri = N2 / (du_dz**2 + 1e-10)
    
    return Ri


def estimate_mixing_depth(T, z, dT_threshold=0.5):
    """
    估算混合层深度
    
    定义为表层温度变化小于阈值的深度
    
    参数：
    - T: 温度分布
    - z: 深度
    - dT_threshold: 温差阈值 (°C)
    
    返回：
    - h_mix: 混合层深度 (m)
    """
    T_surface = T[0]
    dT = np.abs(T - T_surface)
    
    idx = np.where(dT > dT_threshold)[0]
    if len(idx) > 0:
        h_mix = z[idx[0]]
    else:
        h_mix = z[-1]  # 完全混合
    
    print(f"\n混合层深度估算:")
    print(f"  表层温度: {T_surface:.1f}°C")
    print(f"  温差阈值: {dT_threshold}°C")
    print(f"  混合层深度: {h_mix:.1f} m")
    
    return h_mix
