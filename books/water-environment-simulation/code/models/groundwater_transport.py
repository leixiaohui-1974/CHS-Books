"""
地下水污染物运移模型
Groundwater Solute Transport Model
"""

import numpy as np


class GroundwaterColumn1D:
    """
    一维地下水污染柱模型
    
    控制方程：
    R * ∂C/∂t + v * ∂C/∂x = D * ∂²C/∂x²
    
    阻滞因子：
    R = 1 + ρb*Kd/θ
    """
    
    def __init__(self, L, nx, theta=0.3, rho_b=1.5, Kd=0):
        """
        参数：
        - L: 土柱长度 (m)
        - nx: 网格节点数
        - theta: 孔隙度
        - rho_b: 干容重 (g/cm³)
        - Kd: 分配系数 (cm³/g)
        """
        self.L = L
        self.nx = nx
        self.dx = L / (nx - 1)
        self.x = np.linspace(0, L, nx)
        
        self.theta = theta
        self.rho_b = rho_b
        self.Kd = Kd
        
        # 阻滞因子
        self.R = 1 + rho_b * Kd / theta
        
        self.C = np.zeros(nx)
        
        print(f"地下水污染柱模型初始化:")
        print(f"  土柱长度: {L} m")
        print(f"  网格数: {nx}")
        print(f"  孔隙度: {theta}")
        print(f"  分配系数: {Kd} cm³/g")
        print(f"  阻滞因子: {self.R:.2f}")
    
    def solve(self, t_span, v, D, C_in):
        """
        求解对流-弥散-吸附方程
        
        参数：
        - t_span: 时间数组 (d)
        - v: 渗流速度 (m/d)
        - D: 弥散系数 (m²/d)
        - C_in: 入口浓度 (mg/L)
        """
        dt = t_span[1] - t_span[0]
        
        # Courant数和Fourier数
        Cr = v * dt / self.dx
        Fo = D * dt / (self.dx ** 2)
        
        print(f"\n数值参数:")
        print(f"  Courant数: {Cr:.3f}")
        print(f"  Fourier数: {Fo:.3f}")
        print(f"  稳定性: ", end="")
        if Cr <= 1 and Fo <= 0.5 / self.R:
            print("✓ 稳定")
        else:
            print("⚠ 可能不稳定")
        
        C_history = np.zeros((len(t_span), self.nx))
        C_history[0, :] = self.C.copy()
        
        for i, t in enumerate(t_span[1:], 1):
            C_new = self.C.copy()
            
            # 内部节点（显式格式）
            for j in range(1, self.nx-1):
                dC_dx = (self.C[j+1] - self.C[j-1]) / (2 * self.dx)
                d2C_dx2 = (self.C[j+1] - 2*self.C[j] + self.C[j-1]) / (self.dx ** 2)
                
                C_new[j] = self.C[j] + dt / self.R * (-v * dC_dx + D * d2C_dx2)
            
            # 边界条件
            C_new[0] = C_in  # 入口恒定浓度
            C_new[-1] = C_new[-2]  # 出口零梯度
            
            self.C = np.maximum(C_new, 0)
            C_history[i, :] = self.C.copy()
        
        print(f"\n模拟完成:")
        print(f"  出口浓度: {self.C[-1]:.2f} mg/L")
        print(f"  穿透率: {self.C[-1]/C_in*100:.1f}%")
        
        return t_span, self.x, C_history


def calculate_retardation_factor(theta, rho_b, Kd):
    """
    计算阻滞因子
    
    R = 1 + ρb*Kd/θ
    """
    R = 1 + rho_b * Kd / theta
    print(f"\n阻滞因子计算:")
    print(f"  孔隙度 θ = {theta}")
    print(f"  干容重 ρb = {rho_b} g/cm³")
    print(f"  分配系数 Kd = {Kd} cm³/g")
    print(f"  阻滞因子 R = {R:.2f}")
    return R


def calculate_breakthrough_time(L, v, R):
    """
    计算穿透时间
    
    t = R * L / v
    """
    t = R * L / v
    print(f"\n穿透时间计算:")
    print(f"  土柱长度 L = {L} m")
    print(f"  渗流速度 v = {v} m/d")
    print(f"  阻滞因子 R = {R:.2f}")
    print(f"  穿透时间 t = {t:.1f} d")
    return t
