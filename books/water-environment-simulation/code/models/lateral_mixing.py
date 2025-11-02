"""
河流横向混合模型
Lateral Mixing in Rivers

包括：
1. 二维对流-扩散模型
2. 侧向排放源处理
3. 横向混合长度计算
4. 完全混合判断
"""

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve


class LateralMixing2D:
    """
    二维河流横向混合模型
    
    适用于侧向排放污染物在河流中的横向扩散混合过程
    
    控制方程：
    ∂C/∂t + u*∂C/∂x = Ex*∂²C/∂x² + Ey*∂²C/∂y²
    
    其中：
    - C: 浓度 (mg/L)
    - u: 纵向流速 (m/s)
    - Ex: 纵向扩散系数 (m²/s)
    - Ey: 横向扩散系数 (m²/s)
    - x: 纵向坐标 (m)
    - y: 横向坐标 (m)
    
    参数：
        L: 纵向长度 (m)
        B: 河宽 (m)
        nx: 纵向节点数
        ny: 横向节点数
        u: 纵向流速 (m/s)
        Ex: 纵向扩散系数 (m²/s)
        Ey: 横向扩散系数 (m²/s)
    """
    
    def __init__(self, L, B, nx, ny, u, Ex, Ey):
        """初始化二维横向混合模型"""
        self.L = L
        self.B = B
        self.nx = nx
        self.ny = ny
        self.u = u
        self.Ex = Ex
        self.Ey = Ey
        
        # 空间离散
        self.x = np.linspace(0, L, nx)
        self.y = np.linspace(0, B, ny)
        self.dx = L / (nx - 1)
        self.dy = B / (ny - 1)
        
        # 浓度场
        self.C = np.zeros((ny, nx))
        
        # 排放源
        self.sources = []
        
        print(f"二维横向混合模型初始化:")
        print(f"  计算域: {L}m × {B}m")
        print(f"  网格: {nx} × {ny}")
        print(f"  流速 u = {u} m/s")
        print(f"  Ex = {Ex} m²/s, Ey = {Ey} m²/s")
    
    def add_source(self, x, y, Q_discharge, C_discharge, Q_river):
        """
        添加侧向排放源
        
        参数：
            x: 排放位置x坐标 (m)
            y: 排放位置y坐标 (m)
            Q_discharge: 排放流量 (m³/s)
            C_discharge: 排放浓度 (mg/L)
            Q_river: 河流流量 (m³/s)
        """
        source = {
            'x': x,
            'y': y,
            'Q': Q_discharge,
            'C': C_discharge,
            'Q_river': Q_river
        }
        self.sources.append(source)
        
        print(f"\n添加侧向排放源:")
        print(f"  位置: ({x}, {y}) m")
        print(f"  排放流量: {Q_discharge} m³/s")
        print(f"  排放浓度: {C_discharge} mg/L")
        print(f"  河流流量: {Q_river} m³/s")
    
    def solve_steady_state(self, method='explicit'):
        """
        求解稳态浓度场
        
        参数：
            method: 求解方法 ('explicit' 或 'implicit')
            
        返回：
            x, y, C: 坐标和浓度场
        """
        print(f"\n求解稳态浓度场（{method}）...")
        
        if method == 'explicit':
            self._solve_explicit()
        elif method == 'implicit':
            self._solve_implicit()
        else:
            raise ValueError(f"未知求解方法: {method}")
        
        print(f"求解完成！")
        print(f"  最大浓度: {np.max(self.C):.2f} mg/L")
        
        return self.x, self.y, self.C
    
    def _solve_explicit(self):
        """显式求解稳态浓度场"""
        # 初始化
        C = np.zeros((self.ny, self.nx))
        
        # 设置排放源
        for source in self.sources:
            ix = np.argmin(np.abs(self.x - source['x']))
            iy = np.argmin(np.abs(self.y - source['y']))
            
            # 排放源处初始浓度（考虑瞬时混合）
            C[iy, ix] = source['C']
        
        # 从上游向下游逐列求解
        for i in range(1, self.nx):
            # 对每个横断面，求解横向扩散方程
            # ∂C/∂t = Ey*∂²C/∂y²
            
            # 使用上一个断面作为初始值
            C_prev = C[:, i-1].copy()
            
            # 伪时间步进（达到稳态）
            dt = 0.5 * self.dy**2 / self.Ey  # CFL条件
            n_steps = int(self.dx / (self.u * dt))
            
            for _ in range(n_steps):
                # 横向扩散（显式格式）
                C_new = C_prev.copy()
                for j in range(1, self.ny-1):
                    d2C_dy2 = (C_prev[j+1] - 2*C_prev[j] + C_prev[j-1]) / self.dy**2
                    C_new[j] = C_prev[j] + dt * self.Ey * d2C_dy2
                
                # 边界条件：零通量
                C_new[0] = C_new[1]
                C_new[-1] = C_new[-2]
                
                C_prev = C_new
            
            C[:, i] = C_new
        
        self.C = C
    
    def _solve_implicit(self):
        """隐式求解稳态浓度场"""
        # 初始化
        C = np.zeros((self.ny, self.nx))
        
        # 设置排放源
        for source in self.sources:
            ix = np.argmin(np.abs(self.x - source['x']))
            iy = np.argmin(np.abs(self.y - source['y']))
            C[iy, ix] = source['C']
        
        # 从上游向下游逐列求解
        for i in range(1, self.nx):
            # 构建隐式求解矩阵
            # (I - dt*Ey*D2y) * C_new = C_prev
            
            dt = self.dx / self.u
            alpha = self.Ey * dt / self.dy**2
            
            # 三对角矩阵
            main_diag = np.ones(self.ny) * (1 + 2*alpha)
            off_diag = np.ones(self.ny-1) * (-alpha)
            
            # 边界条件：零通量
            main_diag[0] = 1
            main_diag[-1] = 1
            off_diag[0] = -1
            off_diag[-1] = -1
            
            # 构建稀疏矩阵
            A = diags([off_diag, main_diag, off_diag], [-1, 0, 1], 
                     shape=(self.ny, self.ny), format='csr')
            
            # 右端项
            b = C[:, i-1].copy()
            b[0] = 0  # 边界条件
            b[-1] = 0
            
            # 求解
            C[:, i] = spsolve(A, b)
        
        self.C = C
    
    def calculate_mixing_length(self, threshold=0.95):
        """
        计算横向混合长度
        
        混合长度：从排放点到横断面浓度达到均匀分布的距离
        
        参数：
            threshold: 混合均匀度阈值（默认0.95，表示95%均匀）
            
        返回：
            L_mix: 混合长度 (m)
        """
        if self.C is None or len(self.sources) == 0:
            raise ValueError("请先求解浓度场并添加排放源")
        
        source = self.sources[0]
        ix_source = np.argmin(np.abs(self.x - source['x']))
        
        # 从排放点开始搜索
        for i in range(ix_source, self.nx):
            C_section = self.C[:, i]
            
            # 计算横断面浓度的变异系数
            C_mean = np.mean(C_section)
            if C_mean > 0:
                C_cv = np.std(C_section) / C_mean
                uniformity = 1 - C_cv
                
                if uniformity >= threshold:
                    L_mix = self.x[i] - source['x']
                    print(f"\n横向混合长度:")
                    print(f"  L_mix = {L_mix:.0f} m")
                    print(f"  均匀度: {uniformity:.2%}")
                    return L_mix
        
        # 未达到完全混合
        L_mix = self.L - source['x']
        print(f"\n未完全混合:")
        print(f"  计算域长度: {L_mix:.0f} m")
        return L_mix
    
    def calculate_lateral_dispersion_coefficient(self, H, u_star, B):
        """
        计算横向扩散系数（经验公式）
        
        Elder公式（1959）:
        Ey = 0.23 * H * u_star
        
        Fischer公式（1979）:
        Ey = 0.15 * H * u_star
        
        参数：
            H: 水深 (m)
            u_star: 摩阻流速 (m/s)
            B: 河宽 (m)
            
        返回：
            Ey: 横向扩散系数 (m²/s)
        """
        # Elder公式
        Ey_elder = 0.23 * H * u_star
        
        # Fischer公式
        Ey_fischer = 0.15 * H * u_star
        
        # 推荐值（取平均）
        Ey = (Ey_elder + Ey_fischer) / 2
        
        print(f"\n横向扩散系数计算:")
        print(f"  Elder公式: Ey = {Ey_elder:.3f} m²/s")
        print(f"  Fischer公式: Ey = {Ey_fischer:.3f} m²/s")
        print(f"  推荐值: Ey = {Ey:.3f} m²/s")
        
        return Ey


def calculate_mixing_time(B, Ey):
    """
    计算横向混合时间
    
    T_mix ≈ B² / (6 * Ey)
    
    参数：
        B: 河宽 (m)
        Ey: 横向扩散系数 (m²/s)
        
    返回：
        T_mix: 混合时间 (s)
    """
    T_mix = B**2 / (6 * Ey)
    
    print(f"横向混合时间:")
    print(f"  T_mix = {T_mix:.0f} s ({T_mix/3600:.2f} hour)")
    
    return T_mix


def calculate_complete_mixing_distance(B, u, Ey):
    """
    计算完全混合距离
    
    L_mix ≈ u * T_mix = u * B² / (6 * Ey)
    
    参数：
        B: 河宽 (m)
        u: 流速 (m/s)
        Ey: 横向扩散系数 (m²/s)
        
    返回：
        L_mix: 完全混合距离 (m)
    """
    T_mix = B**2 / (6 * Ey)
    L_mix = u * T_mix
    
    print(f"完全混合距离:")
    print(f"  L_mix = {L_mix:.0f} m ({L_mix/1000:.2f} km)")
    print(f"  = {L_mix/B:.1f} × B (河宽)")
    
    return L_mix


def calculate_concentration_at_bank(C0, y, B, x, Ey, u):
    """
    计算岸边浓度（解析解）
    
    对于侧向点源排放，岸边浓度为：
    C(x,y=B) = C0 * exp(-π²*Ey*x/(u*B²))
    
    参数：
        C0: 排放浓度 (mg/L)
        y: 排放位置横坐标 (m)
        B: 河宽 (m)
        x: 纵向距离 (m)
        Ey: 横向扩散系数 (m²/s)
        u: 流速 (m/s)
        
    返回：
        C_bank: 岸边浓度 (mg/L)
    """
    # 简化解析解（假设侧岸排放）
    decay_factor = np.exp(-np.pi**2 * Ey * x / (u * B**2))
    C_bank = C0 * decay_factor
    
    return C_bank
