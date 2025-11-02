"""
河口盐水入侵与水质模拟模型
Estuary Saltwater Intrusion and Water Quality Model

包括：
1. 盐水入侵模拟
2. 盐淡水混合
3. 往复流动
4. 密度流效应
"""

import numpy as np


class EstuarySaltIntrusion1D:
    """
    一维河口盐水入侵模型
    
    考虑潮汐作用下的盐水入侵和水质变化
    
    特点：
    - 潮汐往复流动
    - 盐淡水密度差
    - 分层混合
    
    参数：
        L: 河口长度 (m)
        nx: 节点数
        H: 平均水深 (m)
        Q_river: 河流流量 (m³/s)
        tidal_range: 潮差 (m)
        tidal_period: 潮汐周期 (s)
    """
    
    def __init__(self, L, nx, H, Q_river, tidal_range, tidal_period):
        """初始化河口盐水入侵模型"""
        self.L = L
        self.nx = nx
        self.H = H
        self.Q_river = Q_river
        self.tidal_range = tidal_range
        self.tidal_period = tidal_period
        
        # 空间离散
        self.x = np.linspace(0, L, nx)
        self.dx = L / (nx - 1)
        
        # 盐度场（初始化）
        self.S = np.zeros(nx)
        
        # 流速场（初始化）
        self.u = np.zeros(nx)
        
        # 水质浓度场
        self.C = np.zeros(nx)
        
        print(f"河口盐水入侵模型初始化:")
        print(f"  河口长度: {L/1000:.1f} km")
        print(f"  节点数: {nx}")
        print(f"  水深: {H} m")
        print(f"  河流流量: {Q_river} m³/s")
        print(f"  潮差: {tidal_range} m")
        print(f"  潮汐周期: {tidal_period/3600:.1f} hour")
    
    def set_initial_salinity(self, S_sea, S_river=0):
        """
        设置初始盐度分布
        
        参数：
            S_sea: 海水盐度 (ppt)
            S_river: 河水盐度 (ppt, 默认0)
        """
        # 线性分布作为初始条件
        for i in range(self.nx):
            # 从上游（河水）到下游（海水）
            ratio = self.x[i] / self.L
            self.S[i] = S_river + (S_sea - S_river) * ratio
        
        print(f"\n初始盐度设置:")
        print(f"  河水盐度: {S_river} ppt")
        print(f"  海水盐度: {S_sea} ppt")
    
    def calculate_tidal_velocity(self, t):
        """
        计算潮汐流速
        
        简化正弦模型：
        u(t) = u_tide * sin(2π*t/T)
        
        正值：涨潮（向陆）
        负值：落潮（向海）
        
        参数：
            t: 时间 (s)
            
        返回：
            u_tide: 潮汐流速 (m/s)
        """
        # 潮汐流速幅值（经验公式）
        # 基于潮差和周期
        u_tide_max = (self.tidal_range * np.pi) / self.tidal_period
        
        # 正弦变化
        omega = 2 * np.pi / self.tidal_period
        u_tide = u_tide_max * np.sin(omega * t)
        
        return u_tide
    
    def calculate_density_driven_flow(self, S):
        """
        计算密度流（重力环流）
        
        盐度梯度引起的密度流：
        u_density = -g * β * H² * dS/dx / (48 * ν)
        
        简化：
        u_density ∝ -dS/dx
        
        参数：
            S: 盐度场 (ppt)
            
        返回：
            u_density: 密度流速 (m/s)
        """
        u_density = np.zeros(self.nx)
        
        # 计算盐度梯度
        for i in range(1, self.nx-1):
            dS_dx = (S[i+1] - S[i-1]) / (2 * self.dx)
            
            # 密度流速（简化）
            # β ≈ 0.0008 (kg/m³)/ppt
            # g = 9.81 m/s²
            beta = 0.0008
            g = 9.81
            
            # 简化公式（忽略摩擦）
            u_density[i] = -0.01 * beta * g * self.H * dS_dx
        
        # 边界条件
        u_density[0] = u_density[1]
        u_density[-1] = u_density[-2]
        
        return u_density
    
    def solve_salinity_transport(self, t, dt, K_x=100):
        """
        求解盐度输运方程
        
        ∂S/∂t + u*∂S/∂x = Kx*∂²S/∂x²
        
        参数：
            t: 当前时间 (s)
            dt: 时间步长 (s)
            K_x: 纵向扩散系数 (m²/s)
        """
        # 计算总流速
        u_tide = self.calculate_tidal_velocity(t)
        u_density = self.calculate_density_driven_flow(self.S)
        
        # 河流流速（平均）
        B = 500  # 假设河宽 (m)
        u_river = self.Q_river / (B * self.H)
        
        # 总流速 = 河流流 + 潮汐流 + 密度流
        self.u = u_river + u_tide + u_density
        
        # 更新盐度（显式格式）
        S_new = self.S.copy()
        
        for i in range(1, self.nx-1):
            # 对流项（迎风格式）
            if self.u[i] > 0:
                dS_dx = (self.S[i] - self.S[i-1]) / self.dx
            else:
                dS_dx = (self.S[i+1] - self.S[i]) / self.dx
            
            # 扩散项
            d2S_dx2 = (self.S[i+1] - 2*self.S[i] + self.S[i-1]) / self.dx**2
            
            # 更新
            S_new[i] = self.S[i] - dt * self.u[i] * dS_dx + dt * K_x * d2S_dx2
        
        # 边界条件
        S_new[0] = 0     # 上游：淡水
        S_new[-1] = 30   # 下游：海水
        
        self.S = S_new
    
    def calculate_intrusion_length(self, S_threshold=2.0):
        """
        计算盐水入侵长度
        
        定义：从河口向上游，盐度超过阈值的最远距离
        
        参数：
            S_threshold: 盐度阈值 (ppt, 默认2.0)
            
        返回：
            L_intrusion: 入侵长度 (m)
        """
        # 从下游向上游搜索
        for i in range(self.nx-1, -1, -1):
            if self.S[i] >= S_threshold:
                L_intrusion = self.L - self.x[i]
                
                print(f"\n盐水入侵长度:")
                print(f"  阈值: {S_threshold} ppt")
                print(f"  入侵长度: {L_intrusion/1000:.2f} km")
                
                return L_intrusion
        
        # 未入侵
        return 0
    
    def solve_water_quality(self, C_source, x_source, decay_rate=0):
        """
        求解水质浓度（考虑盐度影响）
        
        某些污染物在高盐度下行为不同：
        - 絮凝沉降
        - 生物降解变化
        - 化学反应变化
        
        参数：
            C_source: 源浓度 (mg/L)
            x_source: 源位置 (m)
            decay_rate: 降解速率 (1/day)
        """
        # 初始化浓度
        self.C = np.zeros(self.nx)
        
        # 设置排放源
        ix_source = np.argmin(np.abs(self.x - x_source))
        self.C[ix_source] = C_source
        
        # 简化稳态解（考虑平均流速）
        u_avg = self.Q_river / (500 * self.H)  # 平均流速
        
        for i in range(ix_source+1, self.nx):
            distance = self.x[i] - x_source
            
            # 考虑降解
            k = decay_rate / 86400  # 转换为 1/s
            
            # 一维解析解
            self.C[i] = C_source * np.exp(-k * distance / u_avg)
            
            # 盐度影响因子（简化）
            # 高盐度下，某些污染物沉降增加
            salinity_factor = 1.0 / (1.0 + 0.02 * self.S[i])
            self.C[i] *= salinity_factor
        
        print(f"\n水质浓度计算:")
        print(f"  源位置: {x_source/1000:.1f} km")
        print(f"  源浓度: {C_source} mg/L")


def calculate_stratification_parameter(delta_rho, H, u):
    """
    计算分层参数（Richardson数）
    
    Ri = (g * Δρ * H) / (ρ * u²)
    
    Ri > 1: 强分层
    Ri < 0.25: 充分混合
    
    参数：
        delta_rho: 密度差 (kg/m³)
        H: 水深 (m)
        u: 流速 (m/s)
        
    返回：
        Ri: Richardson数
    """
    g = 9.81
    rho = 1025  # 海水密度
    
    if u > 0:
        Ri = (g * delta_rho * H) / (rho * u**2)
    else:
        Ri = 999  # 无流动，强分层
    
    print(f"分层参数:")
    print(f"  Richardson数: {Ri:.2f}")
    if Ri > 1:
        print(f"  状态: 强分层")
    elif Ri < 0.25:
        print(f"  状态: 充分混合")
    else:
        print(f"  状态: 部分混合")
    
    return Ri


def calculate_mixing_parameter(u, H, du_dz):
    """
    计算混合参数
    
    基于剪切流的混合强度
    
    参数：
        u: 流速 (m/s)
        H: 水深 (m)
        du_dz: 垂向速度梯度 (1/s)
        
    返回：
        mixing_intensity: 混合强度
    """
    # 简化估算
    mixing_intensity = abs(du_dz) * H
    
    print(f"混合强度: {mixing_intensity:.4f}")
    
    return mixing_intensity


def calculate_salt_wedge_length(Q_river, B, H, rho_fresh, rho_salt):
    """
    计算盐水楔长度（简化公式）
    
    基于Keulegan公式（简化）：
    L ∝ Q^(2/3)
    
    参数：
        Q_river: 河流流量 (m³/s)
        B: 河宽 (m)
        H: 水深 (m)
        rho_fresh: 淡水密度 (kg/m³)
        rho_salt: 盐水密度 (kg/m³)
        
    返回：
        L_wedge: 盐水楔长度 (m)
    """
    # 简化Keulegan公式
    g = 9.81
    delta_rho = rho_salt - rho_fresh
    
    # 无量纲参数
    Fr = Q_river / (B * np.sqrt(g * delta_rho / rho_fresh * H**3))
    
    # 入侵长度（经验公式）
    L_wedge = 50 * H * Fr**(-2/3) if Fr > 0 else 0
    
    print(f"盐水楔长度估算:")
    print(f"  Froude数: {Fr:.4f}")
    print(f"  楔长: {L_wedge/1000:.2f} km")
    
    return L_wedge


def estimate_intake_risk(S, x_intake, S_max=0.5):
    """
    评估取水口盐度风险
    
    参数：
        S: 盐度场 (ppt)
        x_intake: 取水口位置 (从0到L的数组索引或距离)
        S_max: 最大允许盐度 (ppt)
        
    返回：
        risk_level: 风险等级 (0-1)
        is_safe: 是否安全
    """
    if isinstance(x_intake, (int, np.integer)):
        S_intake = S[x_intake]
    else:
        # 插值
        S_intake = np.interp(x_intake, range(len(S)), S)
    
    risk_level = S_intake / S_max
    is_safe = S_intake < S_max
    
    print(f"取水口风险评估:")
    print(f"  取水口盐度: {S_intake:.2f} ppt")
    print(f"  安全标准: {S_max} ppt")
    print(f"  风险等级: {risk_level:.2%}")
    print(f"  状态: {'安全' if is_safe else '超标'}")
    
    return risk_level, is_safe
