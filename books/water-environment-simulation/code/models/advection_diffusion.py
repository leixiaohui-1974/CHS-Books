"""
对流-扩散模型
Advection-Diffusion Model

实现1D对流-扩散方程的不同数值格式
"""

import numpy as np


class AdvectionDiffusion1D:
    """
    一维对流-扩散模型
    
    控制方程：
        ∂C/∂t + u * ∂C/∂x = D * ∂²C/∂x²
    
    其中：
        C: 浓度 (mg/L)
        t: 时间 (s)
        u: 流速 (m/s)
        D: 扩散系数 (m²/s)
        x: 空间坐标 (m)
    
    无量纲数：
        Pe = u*L/D  (Peclet数，对流与扩散的比值)
        Cr = u*dt/dx (Courant数，CFL条件)
        
    参数:
        L: 空间域长度 (m)
        T: 总模拟时间 (s)
        nx: 空间网格数
        nt: 时间步数
        u: 流速 (m/s)
        D: 扩散系数 (m²/s)
    """
    
    def __init__(self, L=100.0, T=200.0, nx=200, nt=2000, u=0.5, D=0.1):
        """初始化对流-扩散模型"""
        self.L = L
        self.T = T
        self.nx = nx
        self.nt = nt
        self.u = u
        self.D = D
        
        # 网格参数
        self.dx = L / (nx - 1)
        self.dt = T / nt
        
        # 坐标
        self.x = np.linspace(0, L, nx)
        self.t = np.linspace(0, T, nt)
        
        # 无量纲数
        self.Pe = u * L / D if D > 0 else float('inf')  # Peclet数
        self.Cr = u * self.dt / self.dx  # Courant数
        self.Fo = D * self.dt / self.dx**2  # Fourier数
        
        # 浓度场
        self.C = np.zeros((nt, nx))
        
        print(f"Pe = {self.Pe:.2f}, Cr = {self.Cr:.3f}, Fo = {self.Fo:.3f}")
        
    def set_initial_condition(self, C0):
        """设置初始条件"""
        if callable(C0):
            self.C[0, :] = C0(self.x)
        else:
            self.C[0, :] = C0
            
    def set_boundary_conditions(self, bc_left=None, bc_right=None):
        """
        设置边界条件
        
        参数:
            bc_left: 左边界值或函数
            bc_right: 右边界值或函数
        """
        self.bc_left = bc_left
        self.bc_right = bc_right
        
    def solve_upwind(self):
        """
        迎风格式（Upwind Scheme）
        
        对流项使用一阶迎风差分：
            ∂C/∂x ≈ (C[i] - C[i-1]) / dx  (u > 0)
            
        扩散项使用中心差分：
            ∂²C/∂x² ≈ (C[i+1] - 2*C[i] + C[i-1]) / dx²
        
        优点：稳定性好
        缺点：数值耗散大（一阶精度）
        
        稳定性条件：
            Cr ≤ 1
            2*Fo + Cr ≤ 1
        """
        if self.Cr > 1:
            print(f"警告: Courant数 = {self.Cr:.3f} > 1，可能不稳定！")
        
        for n in range(self.nt - 1):
            # 内部节点（假设u > 0）
            self.C[n+1, 1:-1] = self.C[n, 1:-1] - \
                self.Cr * (self.C[n, 1:-1] - self.C[n, :-2]) + \
                self.Fo * (self.C[n, 2:] - 2*self.C[n, 1:-1] + self.C[n, :-2])
            
            # 边界条件
            if self.bc_left is not None:
                if callable(self.bc_left):
                    self.C[n+1, 0] = self.bc_left(self.t[n+1])
                else:
                    self.C[n+1, 0] = self.bc_left
            else:
                self.C[n+1, 0] = self.C[n, 0]
                
            if self.bc_right is not None:
                self.C[n+1, -1] = self.bc_right
            else:
                # 出流边界（零梯度）
                self.C[n+1, -1] = self.C[n+1, -2]
                
        return self.C
    
    def solve_central(self):
        """
        中心差分格式
        
        对流项使用中心差分：
            ∂C/∂x ≈ (C[i+1] - C[i-1]) / (2*dx)
        
        优点：二阶精度
        缺点：容易产生非物理振荡（Pe > 2）
        
        稳定性条件：
            Cr ≤ 2*Fo
        """
        if self.Cr > 2 * self.Fo:
            print(f"警告: Cr = {self.Cr:.3f} > 2*Fo = {2*self.Fo:.3f}，可能不稳定！")
        
        if self.Pe > 2:
            print(f"警告: Pe = {self.Pe:.2f} > 2，可能产生振荡！")
        
        for n in range(self.nt - 1):
            # 内部节点
            self.C[n+1, 1:-1] = self.C[n, 1:-1] - \
                0.5 * self.Cr * (self.C[n, 2:] - self.C[n, :-2]) + \
                self.Fo * (self.C[n, 2:] - 2*self.C[n, 1:-1] + self.C[n, :-2])
            
            # 边界条件
            if self.bc_left is not None:
                if callable(self.bc_left):
                    self.C[n+1, 0] = self.bc_left(self.t[n+1])
                else:
                    self.C[n+1, 0] = self.bc_left
            else:
                self.C[n+1, 0] = self.C[n, 0]
                
            if self.bc_right is not None:
                self.C[n+1, -1] = self.bc_right
            else:
                self.C[n+1, -1] = self.C[n+1, -2]
                
        return self.C
    
    def solve_quick(self):
        """
        QUICK格式（Quadratic Upstream Interpolation for Convective Kinematics）
        
        对流项使用三点上游插值：
            使用三个点（上游两个，下游一个）进行二次插值
        
        优点：三阶精度，数值耗散小
        缺点：需要更多边界点处理
        """
        for n in range(self.nt - 1):
            # 内部节点（需要至少3个上游点）
            for i in range(2, self.nx - 1):
                # 对流项（QUICK格式）
                if self.u > 0:
                    # 三点上游插值
                    C_face = (3*self.C[n, i] + 6*self.C[n, i-1] - self.C[n, i-2]) / 8
                    adv_term = -self.u * (C_face - self.C[n, i-1]) / self.dx
                else:
                    C_face = (3*self.C[n, i] + 6*self.C[n, i+1] - self.C[n, i+2]) / 8
                    adv_term = -self.u * (self.C[n, i+1] - C_face) / self.dx
                
                # 扩散项（中心差分）
                diff_term = self.D * (self.C[n, i+1] - 2*self.C[n, i] + self.C[n, i-1]) / self.dx**2
                
                self.C[n+1, i] = self.C[n, i] + self.dt * (adv_term + diff_term)
            
            # 边界和近边界节点使用迎风格式
            self.C[n+1, 1] = self.C[n, 1] - \
                self.Cr * (self.C[n, 1] - self.C[n, 0]) + \
                self.Fo * (self.C[n, 2] - 2*self.C[n, 1] + self.C[n, 0])
            
            # 边界条件
            if self.bc_left is not None:
                if callable(self.bc_left):
                    self.C[n+1, 0] = self.bc_left(self.t[n+1])
                else:
                    self.C[n+1, 0] = self.bc_left
            else:
                self.C[n+1, 0] = self.C[n, 0]
                
            if self.bc_right is not None:
                self.C[n+1, -1] = self.bc_right
            else:
                self.C[n+1, -1] = self.C[n+1, -2]
                
        return self.C
    
    def solve_lax_wendroff(self):
        """
        Lax-Wendroff格式
        
        二阶精度格式，基于Taylor展开
        
        稳定性条件：
            Cr² ≤ 2*Fo
        """
        for n in range(self.nt - 1):
            # 内部节点
            self.C[n+1, 1:-1] = self.C[n, 1:-1] - \
                0.5 * self.Cr * (self.C[n, 2:] - self.C[n, :-2]) + \
                0.5 * self.Cr**2 * (self.C[n, 2:] - 2*self.C[n, 1:-1] + self.C[n, :-2]) + \
                self.Fo * (self.C[n, 2:] - 2*self.C[n, 1:-1] + self.C[n, :-2])
            
            # 边界条件
            if self.bc_left is not None:
                if callable(self.bc_left):
                    self.C[n+1, 0] = self.bc_left(self.t[n+1])
                else:
                    self.C[n+1, 0] = self.bc_left
            else:
                self.C[n+1, 0] = self.C[n, 0]
                
            if self.bc_right is not None:
                self.C[n+1, -1] = self.bc_right
            else:
                self.C[n+1, -1] = self.C[n+1, -2]
                
        return self.C
    
    def analytical_solution_steady(self, x):
        """
        稳态解析解（无源项）
        
        对于边界条件 C(0) = C0, C(L) = 0：
            C(x) = C0 * [exp(Pe*x/L) - 1] / [exp(Pe) - 1]
        
        参数:
            x: 空间坐标
            
        返回:
            C: 浓度
        """
        if self.bc_left is None:
            C0 = 1.0
        else:
            C0 = self.bc_left if not callable(self.bc_left) else 1.0
        
        C = C0 * (np.exp(self.Pe * x / self.L) - 1) / (np.exp(self.Pe) - 1)
        
        return C
