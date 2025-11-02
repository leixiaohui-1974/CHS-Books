"""
二维含水层污染羽迁移模型
2D Aquifer Contaminant Plume Transport Model
"""

import numpy as np


class Aquifer2D:
    """
    二维含水层地下水流和溶质运移模型
    
    地下水流：简化稳态流场
    溶质运移：∂C/∂t + v·∇C = ∇·(D∇C) - λC
    """
    
    def __init__(self, Lx, Ly, nx, ny):
        """
        参数：
        - Lx, Ly: 含水层长宽 (m)
        - nx, ny: 网格节点数
        """
        self.Lx = Lx
        self.Ly = Ly
        self.nx = nx
        self.ny = ny
        
        self.dx = Lx / (nx - 1)
        self.dy = Ly / (ny - 1)
        
        self.x = np.linspace(0, Lx, nx)
        self.y = np.linspace(0, Ly, ny)
        
        self.C = np.zeros((ny, nx))
        
        print(f"二维含水层模型初始化:")
        print(f"  尺寸: {Lx}m × {Ly}m")
        print(f"  网格: {nx} × {ny}")
    
    def solve_transport(self, t_span, vx, vy, Dx, Dy, decay=0, source_x=None, source_y=None, source_C=100):
        """
        求解溶质运移
        
        参数：
        - t_span: 时间数组 (d)
        - vx, vy: 流速 (m/d)
        - Dx, Dy: 弥散系数 (m²/d)
        - decay: 衰减系数 (1/d)
        - source_x, source_y: 源位置
        - source_C: 源浓度 (mg/L)
        """
        dt = t_span[1] - t_span[0]
        
        # 设置源
        if source_x is not None and source_y is not None:
            ix = int(source_x / self.dx)
            iy = int(source_y / self.dy)
        
        print(f"\n数值参数:")
        print(f"  时间步: {dt:.3f} d")
        print(f"  流速: vx={vx:.3f}, vy={vy:.3f} m/d")
        print(f"  弥散系数: Dx={Dx:.3f}, Dy={Dy:.3f} m²/d")
        
        C_history = []
        
        for i, t in enumerate(t_span):
            C_new = self.C.copy()
            
            # 内部节点
            for j in range(1, self.ny-1):
                for k in range(1, self.nx-1):
                    # 对流项（upwind）
                    if vx > 0:
                        dC_dx = (self.C[j, k] - self.C[j, k-1]) / self.dx
                    else:
                        dC_dx = (self.C[j, k+1] - self.C[j, k]) / self.dx
                    
                    if vy > 0:
                        dC_dy = (self.C[j, k] - self.C[j-1, k]) / self.dy
                    else:
                        dC_dy = (self.C[j+1, k] - self.C[j, k]) / self.dy
                    
                    # 弥散项
                    d2C_dx2 = (self.C[j, k+1] - 2*self.C[j, k] + self.C[j, k-1]) / (self.dx**2)
                    d2C_dy2 = (self.C[j+1, k] - 2*self.C[j, k] + self.C[j-1, k]) / (self.dy**2)
                    
                    C_new[j, k] = self.C[j, k] + dt * (
                        -vx * dC_dx - vy * dC_dy + 
                        Dx * d2C_dx2 + Dy * d2C_dy2 - 
                        decay * self.C[j, k]
                    )
            
            # 边界条件（零梯度）
            C_new[0, :] = C_new[1, :]
            C_new[-1, :] = C_new[-2, :]
            C_new[:, 0] = C_new[:, 1]
            C_new[:, -1] = C_new[:, -2]
            
            # 源项
            if source_x is not None:
                C_new[iy, ix] = source_C
            
            self.C = np.maximum(C_new, 0)
            
            if i % 10 == 0:
                C_history.append(self.C.copy())
        
        print(f"\n模拟完成:")
        print(f"  最大浓度: {np.max(self.C):.2f} mg/L")
        print(f"  污染羽面积: {np.sum(self.C > 1) * self.dx * self.dy:.1f} m²")
        
        return t_span, C_history


def assess_well_risk(C_field, well_x, well_y, Lx, Ly, threshold=10):
    """
    评估水井污染风险
    
    参数：
    - C_field: 浓度场
    - well_x, well_y: 水井位置 (m)
    - Lx, Ly: 含水层尺寸 (m)
    - threshold: 风险阈值 (mg/L)
    
    返回：
    - at_risk: 是否有风险
    - concentration: 水井处浓度
    """
    ny, nx = C_field.shape
    ix = int(well_x / Lx * (nx - 1))
    iy = int(well_y / Ly * (ny - 1))
    
    concentration = C_field[iy, ix]
    at_risk = concentration > threshold
    
    print(f"\n水井风险评估:")
    print(f"  水井位置: ({well_x}, {well_y}) m")
    print(f"  浓度: {concentration:.2f} mg/L")
    print(f"  阈值: {threshold} mg/L")
    print(f"  风险: {'⚠ 是' if at_risk else '✓ 否'}")
    
    return at_risk, concentration
