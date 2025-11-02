"""
抽出-处理修复模型
Pump and Treat Remediation Model
"""

import numpy as np


class PumpAndTreat:
    """
    简化的抽出-处理修复模型
    """
    
    def __init__(self, Lx, Ly, nx, ny):
        """
        参数：
        - Lx, Ly: 场地尺寸 (m)
        - nx, ny: 网格数
        """
        self.Lx = Lx
        self.Ly = Ly
        self.nx = nx
        self.ny = ny
        
        self.dx = Lx / (nx - 1)
        self.dy = Ly / (ny - 1)
        
        self.C = np.zeros((ny, nx))
        
        print(f"抽出-处理修复模型初始化:")
        print(f"  场地尺寸: {Lx}m × {Ly}m")
        print(f"  网格: {nx} × {ny}")
    
    def simulate_remediation(self, t_span, pump_x, pump_y, Q_pump, D=5):
        """
        模拟修复过程
        
        参数：
        - t_span: 时间数组 (d)
        - pump_x, pump_y: 抽水井位置 (m)
        - Q_pump: 抽水流量 (m³/d)
        - D: 弥散系数 (m²/d)
        """
        dt = t_span[1] - t_span[0]
        
        ix = int(pump_x / self.dx)
        iy = int(pump_y / self.dy)
        
        C_history = []
        mass_removed = 0
        
        for i, t in enumerate(t_span):
            C_new = self.C.copy()
            
            # 扩散
            for j in range(1, self.ny-1):
                for k in range(1, self.nx-1):
                    d2C = (self.C[j, k+1] - 2*self.C[j, k] + self.C[j, k-1]) / (self.dx**2) + \
                          (self.C[j+1, k] - 2*self.C[j, k] + self.C[j-1, k]) / (self.dy**2)
                    C_new[j, k] = self.C[j, k] + dt * D * d2C
            
            # 抽水去除
            if 0 < ix < self.nx and 0 < iy < self.ny:
                mass_removed += C_new[iy, ix] * Q_pump * dt
                C_new[iy, ix] *= np.exp(-Q_pump * dt / (self.dx * self.dy * 1))  # 简化去除
            
            self.C = np.maximum(C_new, 0)
            
            if i % 10 == 0:
                C_history.append(self.C.copy())
        
        print(f"\n修复模拟完成:")
        print(f"  去除污染物质量: {mass_removed:.1f} mg")
        print(f"  最大剩余浓度: {np.max(self.C):.2f} mg/L")
        
        return t_span, C_history, mass_removed


def optimize_well_location(site_size, contam_center):
    """优化抽水井位置（简化）"""
    # 简单策略：放在污染中心下游
    optimal_x = contam_center[0] + 20
    optimal_y = contam_center[1]
    
    print(f"\n抽水井位置优化:")
    print(f"  污染中心: ({contam_center[0]}, {contam_center[1]}) m")
    print(f"  推荐位置: ({optimal_x}, {optimal_y}) m")
    
    return optimal_x, optimal_y
