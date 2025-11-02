"""
湖泊藻类生长动力学模型
Lake Algae Growth Dynamics Model
"""

import numpy as np
from scipy.integrate import odeint


class AlgaeGrowthModel:
    """
    藻类-营养盐-DO耦合模型
    
    dChl/dt = (μ - r - m) * Chl
    dN/dt = -aN * μ * Chl
    dP/dt = -aP * μ * Chl
    dDO/dt = aO * μ * Chl - rO * r * Chl
    """
    
    def __init__(self, Chl0=5, N0=500, P0=50, DO0=8):
        """
        参数：
        - Chl0: 初始叶绿素a (μg/L)
        - N0: 初始氮 (μg/L)
        - P0: 初始磷 (μg/L)
        - DO0: 初始DO (mg/L)
        """
        self.state = np.array([Chl0, N0, P0, DO0])
        
        # 参数
        self.mu_max = 2.0  # 最大生长速率 (1/d)
        self.r = 0.1  # 呼吸速率 (1/d)
        self.m = 0.05  # 死亡速率 (1/d)
        self.K_N = 50  # 氮半饱和常数 (μg/L)
        self.K_P = 5   # 磷半饱和常数 (μg/L)
        self.I_opt = 200  # 最适光照 (W/m²)
        self.T_opt = 25  # 最适温度 (°C)
        
        print(f"藻类生长模型初始化:")
        print(f"  初始叶绿素: {Chl0} μg/L")
        print(f"  初始氮: {N0} μg/L")
        print(f"  初始磷: {P0} μg/L")
        print(f"  最大生长速率: {self.mu_max} 1/d")
    
    def growth_rate(self, N, P, I, T):
        """
        计算藻类生长速率
        
        μ = μ_max * f_N * f_P * f_I * f_T
        """
        # 营养盐限制（Monod）
        f_N = N / (self.K_N + N)
        f_P = P / (self.K_P + P)
        
        # 光照限制（Steele）
        f_I = (I / self.I_opt) * np.exp(1 - I / self.I_opt)
        
        # 温度影响（简化）
        f_T = np.exp(-((T - self.T_opt) / 10)**2)
        
        mu = self.mu_max * min(f_N, f_P) * f_I * f_T
        
        return mu
    
    def dynamics(self, state, t, I, T):
        """系统动力学"""
        Chl, N, P, DO = state
        
        mu = self.growth_rate(N, P, I, T)
        
        dChl = (mu - self.r - self.m) * Chl
        dN = -0.15 * mu * Chl  # N/Chl比约15
        dP = -0.01 * mu * Chl  # P/Chl比约1
        dDO = 0.3 * mu * Chl - 0.2 * self.r * Chl  # 光合产氧-呼吸耗氧
        
        return [dChl, dN, dP, dDO]
    
    def solve(self, t_span, I=200, T=25):
        """求解"""
        result = odeint(self.dynamics, self.state, t_span, args=(I, T))
        
        self.state = result[-1, :]
        
        print(f"\n模拟完成:")
        print(f"  最终Chl-a: {self.state[0]:.1f} μg/L")
        print(f"  最终N: {self.state[1]:.1f} μg/L")
        print(f"  最终P: {self.state[2]:.1f} μg/L")
        print(f"  最终DO: {self.state[3]:.1f} mg/L")
        
        return t_span, result


def assess_bloom_risk(Chl):
    """
    评估水华风险
    
    Chl-a阈值：
    - <10: 正常
    - 10-30: 警戒
    - >30: 水华
    """
    if Chl < 10:
        return "Normal", 0
    elif Chl < 30:
        return "Warning", 1
    else:
        return "Bloom", 2
