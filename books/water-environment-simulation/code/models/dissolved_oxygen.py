"""
溶解氧模型
Dissolved Oxygen (DO) Model

包括：
1. Streeter-Phelps模型（经典DO-BOD模型）
2. 复氧过程（大气复氧）
3. BOD降解过程
4. 氧垂曲线（Oxygen Sag Curve）
5. 临界点计算
"""

import numpy as np
from scipy.integrate import odeint
from scipy.optimize import fsolve


class StreeterPhelps:
    """
    Streeter-Phelps溶解氧模型
    
    描述河流中BOD降解和DO变化的经典模型
    
    控制方程：
        dL/dt = -kd * L
        dD/dt = kd * L - ka * D
    
    其中：
        L: BOD浓度 (mg/L)
        D: DO亏损 (mg/L)
        kd: BOD降解系数 (day^-1)
        ka: 复氧系数 (day^-1)
    
    参数：
        L0: 初始BOD (mg/L)
        D0: 初始DO亏损 (mg/L)
        kd: BOD降解系数 (day^-1)
        ka: 复氧系数 (day^-1)
        T: 模拟时间 (day)
        nt: 时间步数
    """
    
    def __init__(self, L0, D0, kd, ka, T=10.0, nt=1000):
        """
        初始化S-P模型
        
        参数：
            L0: 初始BOD (mg/L)
            D0: 初始DO亏损 (mg/L)
            kd: BOD降解系数 (day^-1)
            ka: 复氧系数 (day^-1)
            T: 模拟时间 (day)
            nt: 时间步数
        """
        self.L0 = L0
        self.D0 = D0
        self.kd = kd
        self.ka = ka
        self.T = T
        self.nt = nt
        
        # 时间数组
        self.t = np.linspace(0, T, nt)
        self.dt = T / (nt - 1)
        
        # 结果数组
        self.L = np.zeros(nt)  # BOD
        self.D = np.zeros(nt)  # DO亏损
        self.DO = np.zeros(nt) # DO浓度
        
        # 饱和溶解氧（默认20°C，9.09 mg/L）
        self.DOs = 9.09
        
        # 临界点
        self.tc = None  # 临界时间
        self.Dc = None  # 临界亏损
        self.DOc = None # 临界DO
    
    def set_saturation_do(self, DOs):
        """设置饱和溶解氧"""
        self.DOs = DOs
    
    def calculate_saturation_do(self, T_water):
        """
        计算饱和溶解氧
        
        使用经验公式（适用于淡水，0-30°C）：
        DOs = 14.652 - 0.41022*T + 0.007991*T^2 - 0.000077774*T^3
        
        参数：
            T_water: 水温 (°C)
            
        返回：
            DOs: 饱和溶解氧 (mg/L)
        """
        T = T_water
        DOs = 14.652 - 0.41022*T + 0.007991*T**2 - 0.000077774*T**3
        self.DOs = DOs
        return DOs
    
    def analytical_solution(self, t=None):
        """
        S-P方程解析解
        
        L(t) = L0 * exp(-kd * t)
        D(t) = (kd*L0/(ka-kd)) * (exp(-kd*t) - exp(-ka*t)) + D0*exp(-ka*t)
        
        参数：
            t: 时间数组（如果为None，使用self.t）
            
        返回：
            L, D, DO: BOD、DO亏损、DO浓度
        """
        if t is None:
            t = self.t
        
        # BOD降解
        L = self.L0 * np.exp(-self.kd * t)
        
        # DO亏损
        if np.abs(self.ka - self.kd) < 1e-10:
            # 当ka ≈ kd时的特殊情况
            D = self.kd * self.L0 * t * np.exp(-self.kd * t) + self.D0 * np.exp(-self.ka * t)
        else:
            # 一般情况
            D = (self.kd * self.L0 / (self.ka - self.kd)) * \
                (np.exp(-self.kd * t) - np.exp(-self.ka * t)) + \
                self.D0 * np.exp(-self.ka * t)
        
        # DO浓度
        DO = self.DOs - D
        
        return L, D, DO
    
    def solve(self):
        """
        求解S-P方程（使用解析解）
        
        返回：
            L, D, DO: BOD、DO亏损、DO浓度数组
        """
        self.L, self.D, self.DO = self.analytical_solution(self.t)
        return self.L, self.D, self.DO
    
    def calculate_critical_point(self):
        """
        计算临界点（氧垂曲线最低点）
        
        临界时间：tc = ln(ka/kd * (1 - D0*(ka-kd)/(kd*L0))) / (ka - kd)
        临界亏损：Dc = kd*L0/ka * exp(-kd*tc)
        
        返回：
            tc: 临界时间 (day)
            Dc: 临界DO亏损 (mg/L)
            DOc: 临界DO浓度 (mg/L)
        """
        if np.abs(self.ka - self.kd) < 1e-10:
            # ka ≈ kd的特殊情况
            self.tc = self.D0 / (self.kd * self.L0)
            self.Dc = self.kd * self.L0 * self.tc * np.exp(-self.kd * self.tc)
        else:
            # 一般情况
            # 临界点条件：dD/dt = 0
            # => kd*L - ka*D = 0
            # => tc = ln(ka/kd * (1 - D0*(ka-kd)/(kd*L0))) / (ka - kd)
            
            factor = self.ka / self.kd * (1.0 - self.D0 * (self.ka - self.kd) / (self.kd * self.L0))
            
            if factor <= 0:
                # 没有临界点（DO一直恢复）
                self.tc = 0.0
                self.Dc = self.D0
            else:
                self.tc = np.log(factor) / (self.ka - self.kd)
                
                # 临界亏损
                _, D_critical, _ = self.analytical_solution(np.array([self.tc]))
                self.Dc = D_critical[0]
        
        # 临界DO浓度
        self.DOc = self.DOs - self.Dc
        
        return self.tc, self.Dc, self.DOc
    
    def temperature_correction(self, kd_20, ka_20, T):
        """
        温度校正
        
        kd(T) = kd(20) * theta_d^(T-20)
        ka(T) = ka(20) * theta_a^(T-20)
        
        参数：
            kd_20: 20°C时的kd (day^-1)
            ka_20: 20°C时的ka (day^-1)
            T: 水温 (°C)
            
        返回：
            kd_T, ka_T: 温度T时的系数
        """
        theta_d = 1.047  # BOD降解温度系数
        theta_a = 1.024  # 复氧温度系数
        
        kd_T = kd_20 * theta_d**(T - 20)
        ka_T = ka_20 * theta_a**(T - 20)
        
        print(f"温度校正 (T = {T}°C):")
        print(f"  kd({T}°C) = {kd_T:.4f} day⁻¹")
        print(f"  ka({T}°C) = {ka_T:.4f} day⁻¹")
        
        return kd_T, ka_T


class DOBODCoupled:
    """
    DO-BOD耦合模型（空间分布）
    
    考虑河流中的对流-扩散-反应过程：
        ∂L/∂t + u*∂L/∂x = D*∂²L/∂x² - kd*L
        ∂DO/∂t + u*∂DO/∂x = D*∂²DO/∂x² + ka*(DOs-DO) - kd*L
    
    参数：
        L: 河段长度 (m)
        T: 模拟时间 (day)
        nx: 空间网格数
        nt: 时间步数
        u: 流速 (m/s)
        D: 扩散系数 (m²/s)
        kd: BOD降解系数 (day^-1)
        ka: 复氧系数 (day^-1)
        DOs: 饱和溶解氧 (mg/L)
    """
    
    def __init__(self, L, T, nx, nt, u, D_coef, kd, ka, DOs):
        """初始化耦合模型"""
        self.L_length = L
        self.T = T
        self.nx = nx
        self.nt = nt
        self.u = u
        self.D_coef = D_coef
        self.kd_day = kd  # day^-1
        self.ka_day = ka  # day^-1
        self.DOs = DOs
        
        # 转换单位
        self.kd = kd / 86400  # 转换为 s^-1
        self.ka = ka / 86400  # 转换为 s^-1
        
        # 网格
        self.x = np.linspace(0, L, nx)
        self.t = np.linspace(0, T * 86400, nt)  # 转换为秒
        self.dx = L / (nx - 1)
        self.dt = T * 86400 / (nt - 1)
        
        # 结果数组
        self.BOD = np.zeros((nt, nx))
        self.DO = np.zeros((nt, nx))
        
    def set_initial_conditions(self, BOD0, DO0):
        """
        设置初始条件
        
        参数：
            BOD0: 初始BOD分布（可以是常数或函数）
            DO0: 初始DO分布（可以是常数或函数）
        """
        if callable(BOD0):
            self.BOD[0, :] = BOD0(self.x)
        else:
            self.BOD[0, :] = BOD0
        
        if callable(DO0):
            self.DO[0, :] = DO0(self.x)
        else:
            self.DO[0, :] = DO0
    
    def set_boundary_conditions(self, BOD_left, DO_left):
        """
        设置边界条件（左侧流入）
        
        参数：
            BOD_left: 左侧BOD边界值
            DO_left: 左侧DO边界值
        """
        self.BOD_bc = BOD_left
        self.DO_bc = DO_left
    
    def solve(self, method='upwind'):
        """
        求解耦合方程
        
        参数：
            method: 数值格式（'upwind'）
            
        返回：
            BOD, DO: BOD和DO浓度场
        """
        if method == 'upwind':
            return self._solve_upwind()
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _solve_upwind(self):
        """使用迎风格式求解"""
        Cr = self.u * self.dt / self.dx
        Fo = self.D_coef * self.dt / self.dx**2
        
        for n in range(self.nt - 1):
            # BOD方程
            for i in range(1, self.nx - 1):
                advection = -self.u * (self.BOD[n, i] - self.BOD[n, i-1]) / self.dx
                diffusion = self.D_coef * (self.BOD[n, i+1] - 2*self.BOD[n, i] + self.BOD[n, i-1]) / self.dx**2
                reaction = -self.kd * self.BOD[n, i]
                
                self.BOD[n+1, i] = self.BOD[n, i] + self.dt * (advection + diffusion + reaction)
            
            # 边界条件
            self.BOD[n+1, 0] = self.BOD_bc
            self.BOD[n+1, -1] = self.BOD[n+1, -2]
            
            # DO方程
            for i in range(1, self.nx - 1):
                advection = -self.u * (self.DO[n, i] - self.DO[n, i-1]) / self.dx
                diffusion = self.D_coef * (self.DO[n, i+1] - 2*self.DO[n, i] + self.DO[n, i-1]) / self.dx**2
                reaeration = self.ka * (self.DOs - self.DO[n, i])
                consumption = -self.kd * self.BOD[n, i]
                
                self.DO[n+1, i] = self.DO[n, i] + self.dt * (advection + diffusion + reaeration + consumption)
            
            # 边界条件
            self.DO[n+1, 0] = self.DO_bc
            self.DO[n+1, -1] = self.DO[n+1, -2]
        
        return self.BOD, self.DO


def calculate_reaeration_coefficient(u, H, formula='Owens'):
    """
    计算复氧系数ka
    
    参数：
        u: 流速 (m/s)
        H: 水深 (m)
        formula: 经验公式选择
            - 'Owens': ka = 5.32*u^0.67 / H^1.85 (浅水河流)
            - 'Churchill': ka = 5.026*u / H^1.673 (大河)
            - 'O\'Connor-Dobbins': ka = 3.93*u^0.5 / H^1.5 (深水河流)
    
    返回：
        ka: 复氧系数 (day^-1, 20°C)
    """
    if formula == 'Owens':
        ka = 5.32 * u**0.67 / H**1.85
    elif formula == 'Churchill':
        ka = 5.026 * u / H**1.673
    elif formula == 'OConnor-Dobbins' or formula == 'O\'Connor-Dobbins':
        ka = 3.93 * u**0.5 / H**1.5
    else:
        raise ValueError(f"Unknown formula: {formula}")
    
    print(f"复氧系数计算 ({formula}公式):")
    print(f"  流速 u = {u:.2f} m/s")
    print(f"  水深 H = {H:.2f} m")
    print(f"  ka = {ka:.4f} day⁻¹ (20°C)")
    
    return ka
