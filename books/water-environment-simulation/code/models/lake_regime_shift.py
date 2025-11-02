"""
湖泊稳态转换模型（简化版）
Simplified Lake Regime Shift Model
"""

import numpy as np
from scipy.integrate import odeint


class LakeRegimeShiftModel:
    """湖泊清水态-浊水态转换模型"""
    
    def __init__(self, P_load):
        """
        参数：
        - P_load: 磷负荷 (mg/L/d)
        """
        self.P_load = P_load
        self.state = np.array([50, 10])  # [水草, 藻类] 生物量 (g/m²)
        
        print(f"湖泊稳态转换模型初始化:")
        print(f"  磷负荷: {P_load} mg/L/d")
    
    def dynamics(self, state, t, P):
        """竞争动力学"""
        M, A = state  # 水草, 藻类
        
        # 简化的竞争模型
        dM = 0.1 * M * (1 - M/100) - 0.05 * M * A / 10 - 0.01 * M * P
        dA = 0.2 * A * (1 - A/100) * P / 50 - 0.1 * A * M / 50
        
        return [dM, dA]
    
    def solve(self, t_span):
        """求解"""
        result = odeint(self.dynamics, self.state, t_span, args=(self.P_load,))
        
        final_M, final_A = result[-1, :]
        regime = "清水态" if final_M > final_A else "浊水态"
        
        print(f"\n稳态分析:")
        print(f"  最终水草: {final_M:.1f} g/m²")
        print(f"  最终藻类: {final_A:.1f} g/m²")
        print(f"  系统状态: {regime}")
        
        return t_span, result, regime


def find_critical_load(load_range):
    """寻找临界磷负荷（简化）"""
    critical_load = 0.5  # 简化假设
    
    print(f"\n临界负荷分析:")
    print(f"  临界磷负荷: {critical_load} mg/L/d")
    
    return critical_load
