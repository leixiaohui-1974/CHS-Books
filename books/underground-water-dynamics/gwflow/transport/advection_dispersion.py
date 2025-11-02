"""
对流-弥散方程数值求解器
"""

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from typing import Tuple, Optional


def solve_ade_1d_implicit(
    C0: np.ndarray,
    dx: float,
    dt: float,
    n_steps: int,
    v: float,
    D: float,
    R: float = 1.0,
    lambda_: float = 0.0,
    source: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    一维对流-弥散方程隐式求解
    
    ∂C/∂t = D∂²C/∂x² - v∂C/∂x - λC + S/R
    
    使用Crank-Nicolson格式
    
    Parameters
    ----------
    C0 : ndarray
        初始浓度 [kg/m³]
    dx : float
        空间步长 [m]
    dt : float
        时间步长 [day]
    n_steps : int
        时间步数
    v : float
        流速 [m/day]
    D : float
        弥散系数 [m²/day]
    R : float, optional
        阻滞因子
    lambda_ : float, optional
        衰减系数 [1/day]
    source : ndarray, optional
        源项 [kg/m³/day]
    
    Returns
    -------
    C_history : ndarray, shape (n_steps+1, nx)
        浓度历史
    """
    nx = len(C0)
    C_history = np.zeros((n_steps + 1, nx))
    C_history[0, :] = C0
    
    C = C0.copy()
    
    # Courant数
    Cr = v * dt / dx  # 对流
    Cd = D * dt / dx**2  # 弥散
    
    # 稳定性检查
    if Cd > 0.5:
        print(f"Warning: Cd={Cd:.3f} > 0.5, may be unstable")
    
    for step in range(n_steps):
        # 构建系数矩阵（隐式，Crank-Nicolson）
        # 对流项用中心差分，弥散项用中心差分
        
        # 主对角线
        diag = np.ones(nx) * (R + Cd + lambda_ * dt / 2)
        
        # 上下对角线
        upper = -np.ones(nx - 1) * (Cd / 2 + Cr / 4)
        lower = -np.ones(nx - 1) * (Cd / 2 - Cr / 4)
        
        # 构建稀疏矩阵
        A = sparse.diags([lower, diag, upper], [-1, 0, 1], format='csr')
        
        # 右端项
        b = C.copy() * (R - Cd - lambda_ * dt / 2)
        
        # 添加源项
        if source is not None:
            b += dt * source
        
        # 边界条件（零浓度）
        A = A.tolil()
        A[0, :] = 0
        A[0, 0] = 1
        A[-1, :] = 0
        A[-1, -1] = 1
        A = A.tocsr()
        
        b[0] = 0
        b[-1] = 0
        
        # 求解
        C = spsolve(A, b)
        C = np.maximum(C, 0)  # 确保非负
        
        C_history[step + 1, :] = C
    
    return C_history


def solve_ade_2d_implicit(
    C0: np.ndarray,
    dx: float,
    dy: float,
    dt: float,
    n_steps: int,
    vx: float,
    vy: float,
    Dx: float,
    Dy: float,
    R: float = 1.0,
    lambda_: float = 0.0,
    source: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    二维对流-弥散方程简化求解
    
    使用算子分裂法（ADI）
    
    Parameters
    ----------
    C0 : ndarray, shape (ny, nx)
        初始浓度
    dx, dy : float
        空间步长
    dt : float
        时间步长
    n_steps : int
        时间步数
    vx, vy : float
        流速分量
    Dx, Dy : float
        弥散系数
    R, lambda_ : float
        阻滞和衰减
    source : ndarray, optional
        源项
    
    Returns
    -------
    C_history : ndarray, shape (n_steps+1, ny, nx)
        浓度历史
    """
    ny, nx = C0.shape
    C_history = np.zeros((n_steps + 1, ny, nx))
    C_history[0, :, :] = C0
    
    C = C0.copy()
    
    for step in range(n_steps):
        # 简化：显式求解（实际应用中应使用ADI）
        C_new = C.copy()
        
        for i in range(1, ny - 1):
            for j in range(1, nx - 1):
                # 对流项
                conv_x = -vx * (C[i, j+1] - C[i, j-1]) / (2 * dx)
                conv_y = -vy * (C[i+1, j] - C[i-1, j]) / (2 * dy)
                
                # 弥散项
                disp_x = Dx * (C[i, j+1] - 2*C[i, j] + C[i, j-1]) / dx**2
                disp_y = Dy * (C[i+1, j] - 2*C[i, j] + C[i-1, j]) / dy**2
                
                # 衰减
                decay = -lambda_ * C[i, j]
                
                # 源项
                src = source[i, j] if source is not None else 0
                
                # 更新
                dC = (conv_x + conv_y + disp_x + disp_y + decay + src / R) * dt / R
                C_new[i, j] = C[i, j] + dC
        
        C = np.maximum(C_new, 0)
        C_history[step + 1, :, :] = C
    
    return C_history


class ADESolver1D:
    """一维对流-弥散求解器"""
    
    def __init__(
        self,
        x: np.ndarray,
        v: float,
        D: float,
        R: float = 1.0,
        lambda_: float = 0.0
    ):
        self.x = x
        self.v = v
        self.D = D
        self.R = R
        self.lambda_ = lambda_
        self.dx = x[1] - x[0]
    
    def solve(
        self,
        C0: np.ndarray,
        dt: float,
        n_steps: int,
        source: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """求解"""
        return solve_ade_1d_implicit(
            C0, self.dx, dt, n_steps,
            self.v, self.D, self.R, self.lambda_, source
        )


class ADESolver2D:
    """二维对流-弥散求解器"""
    
    def __init__(
        self,
        x: np.ndarray,
        y: np.ndarray,
        vx: float,
        vy: float,
        Dx: float,
        Dy: float,
        R: float = 1.0,
        lambda_: float = 0.0
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.Dx = Dx
        self.Dy = Dy
        self.R = R
        self.lambda_ = lambda_
        self.dx = x[1] - x[0]
        self.dy = y[1] - y[0]
    
    def solve(
        self,
        C0: np.ndarray,
        dt: float,
        n_steps: int,
        source: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """求解"""
        return solve_ade_2d_implicit(
            C0, self.dx, self.dy, dt, n_steps,
            self.vx, self.vy, self.Dx, self.Dy,
            self.R, self.lambda_, source
        )
