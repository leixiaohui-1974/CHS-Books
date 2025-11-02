"""
河流生态系统模型（简化版）
Simplified River Ecosystem Model
"""

import numpy as np
from scipy.integrate import odeint


class RiverEcosystemModel:
    """河流生态系统模型（藻类-浮游动物-鱼类）"""
    
    def __init__(self):
        """初始化"""
        self.state = np.array([10, 5, 2])  # [藻类, 浮游动物, 鱼类]
        
        print(f"河流生态系统模型初始化")
        print(f"  初始藻类: {self.state[0]} mg/L")
        print(f"  初始浮游动物: {self.state[1]} mg/L")
        print(f"  初始鱼类: {self.state[2]} mg/L")
    
    def ecosystem_dynamics(self, state, t):
        """生态系统动力学方程"""
        A, Z, F = state  # 藻类, 浮游动物, 鱼类
        
        # 简化的Lotka-Volterra方程
        dA = 0.5 * A - 0.1 * A * Z
        dZ = 0.05 * A * Z - 0.2 * Z - 0.1 * Z * F
        dF = 0.02 * Z * F - 0.1 * F
        
        return [dA, dZ, dF]
    
    def solve(self, t_span):
        """求解"""
        result = odeint(self.ecosystem_dynamics, self.state, t_span)
        
        print(f"\n生态模拟完成:")
        print(f"  最终藻类: {result[-1, 0]:.1f} mg/L")
        print(f"  最终浮游动物: {result[-1, 1]:.1f} mg/L")
        print(f"  最终鱼类: {result[-1, 2]:.1f} mg/L")
        
        return t_span, result


def calculate_biodiversity_index(species_abundance):
    """计算生物多样性指数（Shannon指数）"""
    total = np.sum(species_abundance)
    proportions = species_abundance / total
    proportions = proportions[proportions > 0]
    H = -np.sum(proportions * np.log(proportions))
    
    print(f"\n生物多样性:")
    print(f"  Shannon指数: {H:.2f}")
    
    return H
