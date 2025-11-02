"""
反应动力学模型
Reaction Kinetics Models

实现不同反应级数的动力学模型
"""

import numpy as np
from scipy.optimize import curve_fit, minimize


class ReactionKinetics:
    """
    反应动力学模型
    
    控制方程：
        dC/dt = -k * C^n + S
    
    其中：
        C: 浓度 (mg/L)
        t: 时间 (s或d)
        k: 反应速率常数
        n: 反应级数（0, 1, 2）
        S: 源项 (mg/L/s)
    
    参数:
        T: 总模拟时间
        nt: 时间步数
        k: 反应速率常数
        n: 反应级数
    """
    
    def __init__(self, T=100.0, nt=1000, k=0.1, n=1):
        """初始化反应动力学模型"""
        self.T = T
        self.nt = nt
        self.k = k
        self.n = n
        
        self.dt = T / nt
        self.t = np.linspace(0, T, nt)
        self.C = np.zeros(nt)
        
    def set_initial_condition(self, C0):
        """设置初始浓度"""
        self.C[0] = C0
        self.C0 = C0
        
    def solve_zero_order(self):
        """
        零阶反应：dC/dt = -k
        
        解析解：C(t) = C0 - k*t
        
        特点：反应速率恒定，与浓度无关
        """
        for n in range(self.nt - 1):
            self.C[n+1] = self.C[n] - self.k * self.dt
            # 浓度不能为负
            self.C[n+1] = max(0, self.C[n+1])
        
        return self.C
    
    def solve_first_order(self):
        """
        一阶反应：dC/dt = -k*C
        
        解析解：C(t) = C0 * exp(-k*t)
        
        特点：最常见的反应级数，半衰期恒定
        """
        for n in range(self.nt - 1):
            self.C[n+1] = self.C[n] * (1 - self.k * self.dt)
            self.C[n+1] = max(0, self.C[n+1])
        
        return self.C
    
    def solve_second_order(self):
        """
        二阶反应：dC/dt = -k*C²
        
        解析解：C(t) = C0 / (1 + k*C0*t)
        
        特点：浓度高时反应快，浓度低时反应慢
        """
        for n in range(self.nt - 1):
            dC = -self.k * self.C[n]**2 * self.dt
            self.C[n+1] = self.C[n] + dC
            self.C[n+1] = max(0, self.C[n+1])
        
        return self.C
    
    def solve_monod(self, K_s=1.0):
        """
        Monod动力学：dC/dt = -k_max * C / (K_s + C)
        
        参数：
            K_s: 半饱和常数 (mg/L)
            
        特点：低浓度时近似一阶，高浓度时近似零阶
        """
        k_max = self.k
        
        for n in range(self.nt - 1):
            rate = k_max * self.C[n] / (K_s + self.C[n])
            self.C[n+1] = self.C[n] - rate * self.dt
            self.C[n+1] = max(0, self.C[n+1])
        
        return self.C
    
    def analytical_zero_order(self, t):
        """零阶反应解析解"""
        C = self.C0 - self.k * t
        return np.maximum(0, C)
    
    def analytical_first_order(self, t):
        """一阶反应解析解"""
        return self.C0 * np.exp(-self.k * t)
    
    def analytical_second_order(self, t):
        """二阶反应解析解"""
        return self.C0 / (1 + self.k * self.C0 * t)
    
    def fit_first_order(self, t_data, C_data):
        """
        从实验数据拟合一阶反应速率常数
        
        方法：线性回归 ln(C) vs t
            ln(C) = ln(C0) - k*t
        
        参数:
            t_data: 时间数据
            C_data: 浓度数据
            
        返回:
            k: 反应速率常数
            R2: 拟合优度
        """
        # 去除零值或负值
        mask = C_data > 0
        t_fit = t_data[mask]
        C_fit = C_data[mask]
        
        # 线性回归
        ln_C = np.log(C_fit)
        coeffs = np.polyfit(t_fit, ln_C, 1)
        k = -coeffs[0]
        C0_fit = np.exp(coeffs[1])
        
        # 计算R²
        ln_C_pred = coeffs[1] + coeffs[0] * t_fit
        ss_res = np.sum((ln_C - ln_C_pred)**2)
        ss_tot = np.sum((ln_C - np.mean(ln_C))**2)
        R2 = 1 - ss_res / ss_tot
        
        print(f"拟合结果：")
        print(f"  k = {k:.6f} d⁻¹")
        print(f"  C0 = {C0_fit:.2f} mg/L")
        print(f"  R² = {R2:.4f}")
        print(f"  半衰期 = {np.log(2)/k:.2f} d")
        
        return k, C0_fit, R2
    
    def temperature_correction(self, k_20, T, theta=1.047):
        """
        温度校正（Arrhenius方程的简化形式）
        
        k(T) = k(20°C) * θ^(T-20)
        
        参数:
            k_20: 20°C时的反应速率常数
            T: 实际温度 (°C)
            theta: 温度系数（典型值1.047）
            
        返回:
            k_T: T°C时的反应速率常数
        """
        k_T = k_20 * theta**(T - 20)
        
        print(f"温度校正：")
        print(f"  k(20°C) = {k_20:.6f}")
        print(f"  温度 = {T}°C")
        print(f"  θ = {theta}")
        print(f"  k({T}°C) = {k_T:.6f}")
        
        return k_T


class ReactionTransport1D:
    """
    反应-迁移耦合模型（1D）
    
    控制方程：
        ∂C/∂t + u * ∂C/∂x = D * ∂²C/∂x² - k*C^n
        
    耦合对流-扩散和反应过程
    """
    
    def __init__(self, L=100.0, T=200.0, nx=200, nt=2000, 
                 u=0.5, D=0.1, k=0.01, n=1):
        """初始化反应-迁移模型"""
        self.L = L
        self.T = T
        self.nx = nx
        self.nt = nt
        self.u = u
        self.D = D
        self.k = k
        self.n = n
        
        self.dx = L / (nx - 1)
        self.dt = T / nt
        
        self.x = np.linspace(0, L, nx)
        self.t = np.linspace(0, T, nt)
        
        self.Cr = u * self.dt / self.dx
        self.Fo = D * self.dt / self.dx**2
        
        self.C = np.zeros((nt, nx))
        
    def set_initial_condition(self, C0):
        """设置初始条件"""
        if callable(C0):
            self.C[0, :] = C0(self.x)
        else:
            self.C[0, :] = C0
            
    def solve(self, method='upwind'):
        """
        求解反应-迁移方程
        
        使用算子分裂方法：
            1. 迁移步（对流-扩散）
            2. 反应步（反应动力学）
        
        参数:
            method: 迁移步的数值格式
        """
        for n in range(self.nt - 1):
            # Step 1: 迁移步（对流-扩散）
            C_temp = self.C[n, :].copy()
            
            if method == 'upwind':
                C_temp[1:-1] = C_temp[1:-1] - \
                    self.Cr * (C_temp[1:-1] - C_temp[:-2]) + \
                    self.Fo * (C_temp[2:] - 2*C_temp[1:-1] + C_temp[:-2])
            
            # 边界条件
            C_temp[0] = C_temp[1]
            C_temp[-1] = C_temp[-2]
            
            # Step 2: 反应步
            if self.n == 1:
                # 一阶反应
                C_temp = C_temp * np.exp(-self.k * self.dt)
            elif self.n == 0:
                # 零阶反应
                C_temp = C_temp - self.k * self.dt
            elif self.n == 2:
                # 二阶反应（隐式求解避免不稳定）
                C_temp = C_temp / (1 + self.k * C_temp * self.dt)
            
            # 确保浓度非负
            C_temp = np.maximum(0, C_temp)
            
            self.C[n+1, :] = C_temp
        
        return self.C
