"""
多层含水层垂向迁移模型
Multilayer Aquifer Vertical Transport Model
"""

import numpy as np


class MultilayerAquifer:
    """
    简化的多层含水层垂向迁移模型
    """
    
    def __init__(self, layers, dz):
        """
        参数：
        - layers: 层数
        - dz: 垂向网格间距 (m)
        """
        self.layers = layers
        self.dz = dz
        self.z = np.arange(0, layers * dz, dz)
        
        self.C = np.zeros(layers)
        
        print(f"多层含水层模型初始化:")
        print(f"  层数: {layers}")
        print(f"  垂向间距: {dz} m")
    
    def solve(self, t_span, Kz, theta=0.3):
        """
        求解垂向扩散
        
        参数：
        - t_span: 时间数组 (d)
        - Kz: 垂向弥散系数 (m²/d)
        - theta: 孔隙度
        """
        dt = t_span[1] - t_span[0]
        
        C_history = np.zeros((len(t_span), self.layers))
        C_history[0, :] = self.C.copy()
        
        for i in range(1, len(t_span)):
            C_new = self.C.copy()
            
            for j in range(1, self.layers-1):
                d2C_dz2 = (self.C[j+1] - 2*self.C[j] + self.C[j-1]) / (self.dz**2)
                C_new[j] = self.C[j] + dt * Kz * d2C_dz2 / theta
            
            self.C = np.maximum(C_new, 0)
            C_history[i, :] = self.C.copy()
        
        print(f"\n模拟完成:")
        print(f"  底层浓度: {self.C[-1]:.2f} mg/L")
        
        return t_span, self.z, C_history


def assess_aquitard_protection(C_above, C_below):
    """评估隔水层保护效果"""
    protection = (C_above - C_below) / C_above * 100 if C_above > 0 else 100
    print(f"\n隔水层保护评估:")
    print(f"  上层浓度: {C_above:.2f} mg/L")
    print(f"  下层浓度: {C_below:.2f} mg/L")
    print(f"  保护效果: {protection:.1f}%")
    return protection
