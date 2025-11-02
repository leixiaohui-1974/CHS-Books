"""
三维湖泊富营养化模型（简化版）
Simplified 3D Lake Eutrophication Model
"""

import numpy as np


class Lake3DEutrophication:
    """
    简化的3D湖泊富营养化模型
    
    模拟风驱动湖流和藻类空间分布
    """
    
    def __init__(self, Lx, Ly, H, nx, ny, nz):
        """
        参数：
        - Lx, Ly: 湖泊长宽 (m)
        - H: 水深 (m)
        - nx, ny, nz: 网格节点数
        """
        self.Lx = Lx
        self.Ly = Ly
        self.H = H
        self.nx = nx
        self.ny = ny
        self.nz = nz
        
        self.dx = Lx / (nx - 1)
        self.dy = Ly / (ny - 1)
        self.dz = H / (nz - 1)
        
        self.x = np.linspace(0, Lx, nx)
        self.y = np.linspace(0, Ly, ny)
        self.z = np.linspace(0, H, nz)
        
        # 3D场
        self.Chl = np.zeros((nz, ny, nx))  # 叶绿素
        self.N = np.zeros((nz, ny, nx))    # 氮
        self.P = np.zeros((nz, ny, nx))    # 磷
        
        print(f"3D湖泊模型初始化:")
        print(f"  尺寸: {Lx}m × {Ly}m × {H}m")
        print(f"  网格: {nx} × {ny} × {nz}")
    
    def simulate_wind_driven_transport(self, wind_speed, wind_dir, dt, n_steps):
        """
        模拟风驱动输运（简化）
        
        参数：
        - wind_speed: 风速 (m/s)
        - wind_dir: 风向 (度，0=北，90=东)
        - dt: 时间步 (s)
        - n_steps: 步数
        """
        # 风驱动流速（简化）
        u_wind = 0.03 * wind_speed * np.cos(np.radians(wind_dir))
        v_wind = 0.03 * wind_speed * np.sin(np.radians(wind_dir))
        
        for step in range(n_steps):
            # 表层对流（简化）
            Chl_new = self.Chl.copy()
            
            for i in range(1, self.nx-1):
                for j in range(1, self.ny-1):
                    # 表层输运
                    if u_wind > 0:
                        dChl_dx = (self.Chl[0, j, i] - self.Chl[0, j, i-1]) / self.dx
                    else:
                        dChl_dx = (self.Chl[0, j, i+1] - self.Chl[0, j, i]) / self.dx
                    
                    if v_wind > 0:
                        dChl_dy = (self.Chl[0, j, i] - self.Chl[0, j-1, i]) / self.dy
                    else:
                        dChl_dy = (self.Chl[0, j+1, i] - self.Chl[0, j, i]) / self.dy
                    
                    Chl_new[0, j, i] -= dt * (u_wind * dChl_dx + v_wind * dChl_dy)
            
            self.Chl = np.maximum(Chl_new, 0)
        
        print(f"\n风驱动输运模拟完成")
        print(f"  风速: {wind_speed} m/s")
        print(f"  风向: {wind_dir}°")
        print(f"  最大Chl-a: {np.max(self.Chl):.1f} μg/L")
        
        return self.Chl


def calculate_bloom_area(Chl_field, threshold=30):
    """
    计算水华面积
    
    参数：
    - Chl_field: 3D叶绿素场
    - threshold: 水华阈值
    
    返回：
    - area_fraction: 水华面积比例
    """
    bloom_cells = np.sum(Chl_field > threshold)
    total_cells = Chl_field.size
    area_fraction = bloom_cells / total_cells
    
    print(f"\n水华面积计算:")
    print(f"  阈值: {threshold} μg/L")
    print(f"  水华区域: {area_fraction*100:.1f}%")
    
    return area_fraction
