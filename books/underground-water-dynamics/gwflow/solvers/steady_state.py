"""
steady_state.py - 稳态地下水流动求解器
========================================

提供一维和二维稳态地下水流动的有限差分求解器。
"""

import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve
from typing import Optional, Callable, Dict, Any


def solve_1d_steady_gw(
    K: float,
    L: float,
    h0: float,
    hL: float,
    nx: int,
    source: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    求解一维稳态地下水流动问题
    
    控制方程：
        d/dx(K * dh/dx) = Q(x)
    
    边界条件：
        h(0) = h0  （第一类边界条件）
        h(L) = hL  （第一类边界条件）
    
    参数：
        K: float
            水力传导度 [m/day]
        L: float
            含水层长度 [m]
        h0: float
            左边界水头 [m]
        hL: float
            右边界水头 [m]
        nx: int
            网格数量
        source: np.ndarray, optional
            源汇项 [m/day]，形状为 (nx,)
            正值表示补给，负值表示抽水
    
    返回：
        h: np.ndarray
            水头分布 [m]，形状为 (nx,)
    
    示例：
        >>> h = solve_1d_steady_gw(K=10.0, L=1000.0, h0=20.0, hL=10.0, nx=50)
        >>> print(f"最大水头: {h.max():.2f} m")
    """
    if K <= 0:
        raise ValueError("水力传导度必须大于0")
    if nx < 2:
        raise ValueError("网格数量必须至少为2")
    if L <= 0:
        raise ValueError("区域长度必须大于0")
    
    dx = L / (nx - 1)
    
    # 构建系数矩阵
    A = np.zeros((nx, nx))
    b = np.zeros(nx)
    
    # 边界条件（第一类边界条件）
    A[0, 0] = 1.0
    b[0] = h0
    
    A[-1, -1] = 1.0
    b[-1] = hL
    
    # 内部节点（有限差分法）
    # K * (h[i+1] - 2*h[i] + h[i-1]) / dx^2 = Q[i]
    for i in range(1, nx - 1):
        A[i, i - 1] = K / dx**2
        A[i, i] = -2 * K / dx**2
        A[i, i + 1] = K / dx**2
        
        if source is not None:
            b[i] = source[i]
        else:
            b[i] = 0.0
    
    # 求解线性方程组
    h = np.linalg.solve(A, b)
    
    return h


def solve_2d_steady_gw(
    K: np.ndarray,
    Lx: float,
    Ly: float,
    nx: int,
    ny: int,
    boundary_conditions: Dict[str, Any],
    source: Optional[np.ndarray] = None,
    tolerance: float = 1e-6,
    max_iterations: int = 10000
) -> np.ndarray:
    """
    求解二维稳态地下水流动问题
    
    控制方程：
        ∂/∂x(K * ∂h/∂x) + ∂/∂y(K * ∂h/∂y) = Q(x,y)
    
    参数：
        K: np.ndarray
            水力传导度场 [m/day]，形状为 (ny, nx) 或标量
        Lx: float
            x方向区域长度 [m]
        Ly: float
            y方向区域长度 [m]
        nx: int
            x方向网格数量
        ny: int
            y方向网格数量
        boundary_conditions: dict
            边界条件字典，包含：
            - 'left': {'type': 'dirichlet', 'value': 常数或数组}
            - 'right': {'type': 'dirichlet', 'value': 常数或数组}
            - 'bottom': {'type': 'dirichlet', 'value': 常数或数组}
            - 'top': {'type': 'dirichlet', 'value': 常数或数组}
        source: np.ndarray, optional
            源汇项 [m/day]，形状为 (ny, nx)
        tolerance: float
            收敛容差
        max_iterations: int
            最大迭代次数
    
    返回：
        h: np.ndarray
            水头分布 [m]，形状为 (ny, nx)
    
    示例：
        >>> K = 10.0 * np.ones((40, 50))
        >>> bc = {
        ...     'left': {'type': 'dirichlet', 'value': 20.0},
        ...     'right': {'type': 'dirichlet', 'value': 10.0},
        ...     'bottom': {'type': 'neumann', 'value': 0.0},
        ...     'top': {'type': 'neumann', 'value': 0.0}
        ... }
        >>> h = solve_2d_steady_gw(K, 1000.0, 800.0, 50, 40, bc)
    """
    if nx < 2 or ny < 2:
        raise ValueError("网格数量必须至少为2")
    if Lx <= 0 or Ly <= 0:
        raise ValueError("区域尺寸必须大于0")
    
    # 处理K为标量的情况
    if np.isscalar(K):
        K = K * np.ones((ny, nx))
    
    if K.shape != (ny, nx):
        raise ValueError(f"K的形状必须为 ({ny}, {nx})")
    
    dx = Lx / (nx - 1)
    dy = Ly / (ny - 1)
    
    # 总节点数
    N = nx * ny
    
    # 构建稀疏矩阵
    A = lil_matrix((N, N))
    b = np.zeros(N)
    
    # 节点编号函数
    def node_index(i: int, j: int) -> int:
        """将二维索引转换为一维索引"""
        return i * nx + j
    
    # 遍历所有节点
    for i in range(ny):
        for j in range(nx):
            idx = node_index(i, j)
            
            # 边界节点
            is_boundary = False
            
            # 左边界
            if j == 0:
                bc = boundary_conditions.get('left', {'type': 'dirichlet', 'value': 0.0})
                if bc['type'] == 'dirichlet':
                    A[idx, idx] = 1.0
                    value = bc['value']
                    b[idx] = value[i] if hasattr(value, '__len__') else value
                    is_boundary = True
            
            # 右边界
            elif j == nx - 1:
                bc = boundary_conditions.get('right', {'type': 'dirichlet', 'value': 0.0})
                if bc['type'] == 'dirichlet':
                    A[idx, idx] = 1.0
                    value = bc['value']
                    b[idx] = value[i] if hasattr(value, '__len__') else value
                    is_boundary = True
            
            # 下边界
            if i == 0 and not is_boundary:
                bc = boundary_conditions.get('bottom', {'type': 'neumann', 'value': 0.0})
                if bc['type'] == 'dirichlet':
                    A[idx, idx] = 1.0
                    value = bc['value']
                    b[idx] = value[j] if hasattr(value, '__len__') else value
                    is_boundary = True
            
            # 上边界
            elif i == ny - 1 and not is_boundary:
                bc = boundary_conditions.get('top', {'type': 'neumann', 'value': 0.0})
                if bc['type'] == 'dirichlet':
                    A[idx, idx] = 1.0
                    value = bc['value']
                    b[idx] = value[j] if hasattr(value, '__len__') else value
                    is_boundary = True
            
            # 内部节点
            if not is_boundary:
                # 获取节点处的水力传导度
                K_center = K[i, j]
                
                # x方向
                if j > 0:
                    K_left = 0.5 * (K[i, j] + K[i, j-1])
                    A[idx, node_index(i, j-1)] = K_left / dx**2
                
                if j < nx - 1:
                    K_right = 0.5 * (K[i, j] + K[i, j+1])
                    A[idx, node_index(i, j+1)] = K_right / dx**2
                
                # y方向
                if i > 0:
                    K_bottom = 0.5 * (K[i, j] + K[i-1, j])
                    A[idx, node_index(i-1, j)] = K_bottom / dy**2
                
                if i < ny - 1:
                    K_top = 0.5 * (K[i, j] + K[i+1, j])
                    A[idx, node_index(i+1, j)] = K_top / dy**2
                
                # 对角线系数
                A[idx, idx] = -(
                    (K_left if j > 0 else 0) / dx**2 +
                    (K_right if j < nx - 1 else 0) / dx**2 +
                    (K_bottom if i > 0 else 0) / dy**2 +
                    (K_top if i < ny - 1 else 0) / dy**2
                )
                
                # 源汇项
                if source is not None:
                    b[idx] = source[i, j]
    
    # 转换为CSR格式并求解
    A_csr = A.tocsr()
    h_flat = spsolve(A_csr, b)
    
    # 转换为二维数组
    h = h_flat.reshape((ny, nx))
    
    return h


def compute_darcy_velocity(
    h: np.ndarray,
    K: np.ndarray,
    dx: float,
    dy: float
) -> tuple[np.ndarray, np.ndarray]:
    """
    根据水头分布计算达西速度
    
    Darcy定律：
        vx = -K * ∂h/∂x
        vy = -K * ∂h/∂y
    
    参数：
        h: np.ndarray
            水头分布 [m]，形状为 (ny, nx)
        K: np.ndarray
            水力传导度 [m/day]，形状为 (ny, nx) 或标量
        dx: float
            x方向网格间距 [m]
        dy: float
            y方向网格间距 [m]
    
    返回：
        vx: np.ndarray
            x方向达西速度 [m/day]，形状为 (ny, nx-1)
        vy: np.ndarray
            y方向达西速度 [m/day]，形状为 (ny-1, nx)
    """
    ny, nx = h.shape
    
    if np.isscalar(K):
        K = K * np.ones((ny, nx))
    
    # x方向速度（使用中心差分）
    vx = np.zeros((ny, nx - 1))
    for i in range(ny):
        for j in range(nx - 1):
            K_avg = 0.5 * (K[i, j] + K[i, j+1])
            vx[i, j] = -K_avg * (h[i, j+1] - h[i, j]) / dx
    
    # y方向速度
    vy = np.zeros((ny - 1, nx))
    for i in range(ny - 1):
        for j in range(nx):
            K_avg = 0.5 * (K[i, j] + K[i+1, j])
            vy[i, j] = -K_avg * (h[i+1, j] - h[i, j]) / dy
    
    return vx, vy
