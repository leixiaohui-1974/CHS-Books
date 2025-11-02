"""
扩散模型
Diffusion Models

实现Fick扩散定律的1D和2D模型
"""

import numpy as np


class Diffusion1D:
    """
    一维扩散模型
    
    控制方程：
        ∂C/∂t = D * ∂²C/∂x²
    
    其中：
        C: 浓度 (mg/L)
        t: 时间 (s)
        D: 扩散系数 (m²/s)
        x: 空间坐标 (m)
    
    参数:
        L: 空间域长度 (m)
        T: 总模拟时间 (s)
        nx: 空间网格数
        nt: 时间步数
        D: 扩散系数 (m²/s)
    """
    
    def __init__(self, L=10.0, T=100.0, nx=100, nt=1000, D=0.01):
        """初始化扩散模型"""
        self.L = L
        self.T = T
        self.nx = nx
        self.nt = nt
        self.D = D
        
        # 网格参数
        self.dx = L / (nx - 1)
        self.dt = T / nt
        
        # 空间和时间坐标
        self.x = np.linspace(0, L, nx)
        self.t = np.linspace(0, T, nt)
        
        # Fourier数（稳定性条件）
        self.Fo = D * self.dt / self.dx**2
        
        # 浓度场
        self.C = np.zeros((nt, nx))
        
    def set_initial_condition(self, C0):
        """
        设置初始条件
        
        参数:
            C0: 初始浓度分布 (数组或函数)
        """
        if callable(C0):
            self.C[0, :] = C0(self.x)
        else:
            self.C[0, :] = C0
            
    def set_boundary_conditions(self, bc_type='dirichlet', bc_left=0.0, bc_right=0.0):
        """
        设置边界条件
        
        参数:
            bc_type: 边界条件类型 ('dirichlet' 或 'neumann')
            bc_left: 左边界值
            bc_right: 右边界值
        """
        self.bc_type = bc_type
        self.bc_left = bc_left
        self.bc_right = bc_right
        
    def solve_explicit(self):
        """
        显式有限差分求解（FTCS格式）
        
        格式：
            C[n+1,i] = C[n,i] + Fo * (C[n,i+1] - 2*C[n,i] + C[n,i-1])
        
        稳定性条件：
            Fo ≤ 0.5
        """
        if self.Fo > 0.5:
            print(f"警告: Fourier数 = {self.Fo:.3f} > 0.5，可能不稳定！")
            
        for n in range(self.nt - 1):
            # 内部节点
            self.C[n+1, 1:-1] = self.C[n, 1:-1] + self.Fo * (
                self.C[n, 2:] - 2*self.C[n, 1:-1] + self.C[n, :-2]
            )
            
            # 边界条件
            if self.bc_type == 'dirichlet':
                self.C[n+1, 0] = self.bc_left
                self.C[n+1, -1] = self.bc_right
            elif self.bc_type == 'neumann':
                # 零通量边界
                self.C[n+1, 0] = self.C[n+1, 1]
                self.C[n+1, -1] = self.C[n+1, -2]
                
        return self.C
    
    def solve_implicit(self):
        """
        隐式有限差分求解（BTCS格式）
        
        格式：
            -Fo*C[n+1,i-1] + (1+2*Fo)*C[n+1,i] - Fo*C[n+1,i+1] = C[n,i]
        
        无条件稳定
        """
        from scipy.sparse import diags
        from scipy.sparse.linalg import spsolve
        
        # 构造系数矩阵（三对角矩阵）
        main_diag = (1 + 2*self.Fo) * np.ones(self.nx)
        off_diag = -self.Fo * np.ones(self.nx - 1)
        
        # Dirichlet边界条件
        if self.bc_type == 'dirichlet':
            main_diag[0] = 1.0
            main_diag[-1] = 1.0
            off_diag[0] = 0.0
            off_diag[-1] = 0.0
        
        A = diags([off_diag, main_diag, off_diag], [-1, 0, 1], format='csr')
        
        # 时间推进
        for n in range(self.nt - 1):
            b = self.C[n, :].copy()
            
            # 边界条件
            if self.bc_type == 'dirichlet':
                b[0] = self.bc_left
                b[-1] = self.bc_right
            
            self.C[n+1, :] = spsolve(A, b)
            
        return self.C
    
    def solve_crank_nicolson(self):
        """
        Crank-Nicolson格式求解（隐式，二阶精度）
        
        格式：
            (1+Fo)*C[n+1,i] - 0.5*Fo*(C[n+1,i+1]+C[n+1,i-1]) = 
            (1-Fo)*C[n,i] + 0.5*Fo*(C[n,i+1]+C[n,i-1])
        
        无条件稳定，时间和空间都是二阶精度
        """
        from scipy.sparse import diags
        from scipy.sparse.linalg import spsolve
        
        # 左侧矩阵
        main_diag_L = (1 + self.Fo) * np.ones(self.nx)
        off_diag_L = -0.5 * self.Fo * np.ones(self.nx - 1)
        
        if self.bc_type == 'dirichlet':
            main_diag_L[0] = 1.0
            main_diag_L[-1] = 1.0
            off_diag_L[0] = 0.0
            off_diag_L[-1] = 0.0
        
        A = diags([off_diag_L, main_diag_L, off_diag_L], [-1, 0, 1], format='csr')
        
        # 时间推进
        for n in range(self.nt - 1):
            # 右侧向量
            b = np.zeros(self.nx)
            b[1:-1] = (1 - self.Fo) * self.C[n, 1:-1] + 0.5 * self.Fo * (
                self.C[n, 2:] + self.C[n, :-2]
            )
            
            # 边界条件
            if self.bc_type == 'dirichlet':
                b[0] = self.bc_left
                b[-1] = self.bc_right
            else:
                b[0] = (1 - self.Fo) * self.C[n, 0] + 0.5 * self.Fo * (
                    self.C[n, 1] + self.C[n, 1]
                )
                b[-1] = (1 - self.Fo) * self.C[n, -1] + 0.5 * self.Fo * (
                    self.C[n, -2] + self.C[n, -2]
                )
            
            self.C[n+1, :] = spsolve(A, b)
            
        return self.C
    
    def analytical_solution(self, x, t, C0_func, num_terms=100):
        """
        解析解（无限域，初始脉冲）
        
        对于初始条件 C(x,0) = δ(x-x0)（脉冲函数）：
            C(x,t) = M / sqrt(4*π*D*t) * exp(-(x-x0)²/(4*D*t))
        
        参数:
            x: 空间坐标
            t: 时间
            C0_func: 初始条件函数
            num_terms: 级数项数
            
        返回:
            C: 浓度
        """
        # 高斯解（脉冲初始条件）
        if t == 0:
            return C0_func(x)
        
        # 假设初始为中心脉冲
        x0 = self.L / 2
        M = 1.0  # 总质量
        
        C = M / np.sqrt(4 * np.pi * self.D * t) * np.exp(
            -(x - x0)**2 / (4 * self.D * t)
        )
        
        return C


class Diffusion2D:
    """
    二维扩散模型
    
    控制方程：
        ∂C/∂t = Dx * ∂²C/∂x² + Dy * ∂²C/∂y²
    
    参数:
        Lx, Ly: 空间域尺寸 (m)
        T: 总模拟时间 (s)
        nx, ny: 空间网格数
        nt: 时间步数
        Dx, Dy: x和y方向扩散系数 (m²/s)
    """
    
    def __init__(self, Lx=10.0, Ly=10.0, T=100.0, nx=50, ny=50, nt=1000, 
                 Dx=0.01, Dy=0.01):
        """初始化2D扩散模型"""
        self.Lx = Lx
        self.Ly = Ly
        self.T = T
        self.nx = nx
        self.ny = ny
        self.nt = nt
        self.Dx = Dx
        self.Dy = Dy
        
        # 网格参数
        self.dx = Lx / (nx - 1)
        self.dy = Ly / (ny - 1)
        self.dt = T / nt
        
        # 坐标网格
        self.x = np.linspace(0, Lx, nx)
        self.y = np.linspace(0, Ly, ny)
        self.X, self.Y = np.meshgrid(self.x, self.y)
        self.t = np.linspace(0, T, nt)
        
        # Fourier数
        self.Fo_x = Dx * self.dt / self.dx**2
        self.Fo_y = Dy * self.dt / self.dy**2
        
        # 浓度场 (nt, ny, nx)
        self.C = np.zeros((nt, ny, nx))
        
    def set_initial_condition(self, C0):
        """
        设置初始条件
        
        参数:
            C0: 初始浓度分布 (2D数组或函数)
        """
        if callable(C0):
            self.C[0, :, :] = C0(self.X, self.Y)
        else:
            self.C[0, :, :] = C0
            
    def solve_explicit(self):
        """
        显式有限差分求解（2D FTCS格式）
        
        稳定性条件：
            Fo_x + Fo_y ≤ 0.5
        """
        Fo_total = self.Fo_x + self.Fo_y
        if Fo_total > 0.5:
            print(f"警告: Fourier数总和 = {Fo_total:.3f} > 0.5，可能不稳定！")
            
        for n in range(self.nt - 1):
            # 内部节点
            self.C[n+1, 1:-1, 1:-1] = self.C[n, 1:-1, 1:-1] + \
                self.Fo_x * (self.C[n, 1:-1, 2:] - 2*self.C[n, 1:-1, 1:-1] + 
                            self.C[n, 1:-1, :-2]) + \
                self.Fo_y * (self.C[n, 2:, 1:-1] - 2*self.C[n, 1:-1, 1:-1] + 
                            self.C[n, :-2, 1:-1])
            
            # 边界条件（Dirichlet，浓度为0）
            self.C[n+1, 0, :] = 0
            self.C[n+1, -1, :] = 0
            self.C[n+1, :, 0] = 0
            self.C[n+1, :, -1] = 0
            
        return self.C
    
    def analytical_solution_2d(self, x, y, t):
        """
        2D高斯解（点源）
        
        C(x,y,t) = M / (4*π*sqrt(Dx*Dy)*t) * exp(-[(x-x0)²/(4*Dx*t) + (y-y0)²/(4*Dy*t)])
        """
        if t == 0:
            return 0
            
        x0 = self.Lx / 2
        y0 = self.Ly / 2
        M = 1.0
        
        C = M / (4 * np.pi * np.sqrt(self.Dx * self.Dy) * t) * np.exp(
            -(x - x0)**2 / (4 * self.Dx * t) - (y - y0)**2 / (4 * self.Dy * t)
        )
        
        return C
