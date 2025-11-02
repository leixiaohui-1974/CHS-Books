"""
transient.py - 瞬态地下水流动求解器
====================================

提供瞬态地下水流动的隐式和显式求解器。
"""

import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
from typing import Optional, Dict, Any, List


def solve_2d_transient_gw(
    K: np.ndarray,
    S: np.ndarray,
    Lx: float,
    Ly: float,
    nx: int,
    ny: int,
    dt: float,
    nt: int,
    initial_h: np.ndarray,
    boundary_conditions: Dict[str, Any],
    source: Optional[np.ndarray] = None,
    method: str = 'implicit'
) -> List[np.ndarray]:
    """
    求解二维瞬态地下水流动问题
    
    控制方程：
        S * ∂h/∂t = ∂/∂x(K * ∂h/∂x) + ∂/∂y(K * ∂h/∂y) + Q(x,y,t)
    
    参数：
        K: np.ndarray
            水力传导度场 [m/day]，形状为 (ny, nx) 或标量
        S: np.ndarray
            储水系数场 [-]，形状为 (ny, nx) 或标量
        Lx: float
            x方向区域长度 [m]
        Ly: float
            y方向区域长度 [m]
        nx: int
            x方向网格数量
        ny: int
            y方向网格数量
        dt: float
            时间步长 [day]
        nt: int
            时间步数
        initial_h: np.ndarray
            初始水头分布 [m]，形状为 (ny, nx)
        boundary_conditions: dict
            边界条件字典
        source: np.ndarray, optional
            源汇项 [m/day]，形状为 (nt, ny, nx) 或 (ny, nx)
        method: str
            时间离散方法：'implicit' 或 'explicit'
    
    返回：
        h_history: List[np.ndarray]
            各时间步的水头分布
    
    示例：
        >>> K = 10.0 * np.ones((40, 50))
        >>> S = 0.001 * np.ones((40, 50))
        >>> initial_h = 15.0 * np.ones((40, 50))
        >>> bc = {
        ...     'left': {'type': 'dirichlet', 'value': 20.0},
        ...     'right': {'type': 'dirichlet', 'value': 10.0},
        ...     'bottom': {'type': 'neumann', 'value': 0.0},
        ...     'top': {'type': 'neumann', 'value': 0.0}
        ... }
        >>> h_history = solve_2d_transient_gw(
        ...     K, S, 1000.0, 800.0, 50, 40, dt=1.0, nt=100,
        ...     initial_h=initial_h, boundary_conditions=bc
        ... )
    """
    if nx < 2 or ny < 2:
        raise ValueError("网格数量必须至少为2")
    if Lx <= 0 or Ly <= 0:
        raise ValueError("区域尺寸必须大于0")
    if dt <= 0:
        raise ValueError("时间步长必须大于0")
    if nt < 1:
        raise ValueError("时间步数必须至少为1")
    
    # 处理K和S为标量的情况
    if np.isscalar(K):
        K = K * np.ones((ny, nx))
    if np.isscalar(S):
        S = S * np.ones((ny, nx))
    
    dx = Lx / (nx - 1)
    dy = Ly / (ny - 1)
    
    # 初始化
    h = initial_h.copy()
    h_history = [h.copy()]
    
    # 总节点数
    N = nx * ny
    
    # 节点编号函数
    def node_index(i: int, j: int) -> int:
        return i * nx + j
    
    if method == 'implicit':
        # 隐式欧拉法（向后欧拉）
        for t in range(nt):
            # 构建系数矩阵
            A = lil_matrix((N, N))
            b = np.zeros(N)
            
            # 获取当前时间步的源汇项
            if source is not None:
                if source.ndim == 3:
                    Q = source[t, :, :]
                else:
                    Q = source
            else:
                Q = np.zeros((ny, nx))
            
            # 遍历所有节点
            for i in range(ny):
                for j in range(nx):
                    idx = node_index(i, j)
                    
                    # 边界条件处理
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
                        K_ij = K[i, j]
                        S_ij = S[i, j]
                        
                        # 时间项
                        A[idx, idx] += S_ij / dt
                        b[idx] = S_ij * h[i, j] / dt + Q[i, j]
                        
                        # 空间项（x方向）
                        if j > 0:
                            K_left = 0.5 * (K[i, j] + K[i, j-1])
                            A[idx, node_index(i, j-1)] -= K_left / dx**2
                            A[idx, idx] += K_left / dx**2
                        
                        if j < nx - 1:
                            K_right = 0.5 * (K[i, j] + K[i, j+1])
                            A[idx, node_index(i, j+1)] -= K_right / dx**2
                            A[idx, idx] += K_right / dx**2
                        
                        # 空间项（y方向）
                        if i > 0:
                            K_bottom = 0.5 * (K[i, j] + K[i-1, j])
                            A[idx, node_index(i-1, j)] -= K_bottom / dy**2
                            A[idx, idx] += K_bottom / dy**2
                        
                        if i < ny - 1:
                            K_top = 0.5 * (K[i, j] + K[i+1, j])
                            A[idx, node_index(i+1, j)] -= K_top / dy**2
                            A[idx, idx] += K_top / dy**2
            
            # 求解
            A_csr = A.tocsr()
            h_flat = spsolve(A_csr, b)
            h = h_flat.reshape((ny, nx))
            h_history.append(h.copy())
    
    elif method == 'explicit':
        # 显式欧拉法（向前欧拉）
        # 检查CFL条件
        alpha_x = np.max(K) * dt / (S.min() * dx**2)
        alpha_y = np.max(K) * dt / (S.min() * dy**2)
        if alpha_x + alpha_y > 0.5:
            import warnings
            warnings.warn(
                f"显式方法可能不稳定！CFL数: {alpha_x + alpha_y:.3f} > 0.5。"
                "建议减小时间步长或使用隐式方法。"
            )
        
        for t in range(nt):
            h_new = h.copy()
            
            # 获取当前时间步的源汇项
            if source is not None:
                if source.ndim == 3:
                    Q = source[t, :, :]
                else:
                    Q = source
            else:
                Q = np.zeros((ny, nx))
            
            # 内部节点更新
            for i in range(1, ny - 1):
                for j in range(1, nx - 1):
                    K_ij = K[i, j]
                    S_ij = S[i, j]
                    
                    # 二阶中心差分
                    d2h_dx2 = (K[i, j+1] * (h[i, j+1] - h[i, j]) / dx -
                               K[i, j-1] * (h[i, j] - h[i, j-1]) / dx) / dx
                    
                    d2h_dy2 = (K[i+1, j] * (h[i+1, j] - h[i, j]) / dy -
                               K[i-1, j] * (h[i, j] - h[i-1, j]) / dy) / dy
                    
                    # 更新
                    h_new[i, j] = h[i, j] + (dt / S_ij) * (d2h_dx2 + d2h_dy2 + Q[i, j])
            
            # 应用边界条件
            # 左边界
            bc = boundary_conditions.get('left', {'type': 'dirichlet', 'value': 0.0})
            if bc['type'] == 'dirichlet':
                value = bc['value']
                h_new[:, 0] = value if np.isscalar(value) else value
            
            # 右边界
            bc = boundary_conditions.get('right', {'type': 'dirichlet', 'value': 0.0})
            if bc['type'] == 'dirichlet':
                value = bc['value']
                h_new[:, -1] = value if np.isscalar(value) else value
            
            # 下边界
            bc = boundary_conditions.get('bottom', {'type': 'neumann', 'value': 0.0})
            if bc['type'] == 'dirichlet':
                value = bc['value']
                h_new[0, :] = value if np.isscalar(value) else value
            
            # 上边界
            bc = boundary_conditions.get('top', {'type': 'neumann', 'value': 0.0})
            if bc['type'] == 'dirichlet':
                value = bc['value']
                h_new[-1, :] = value if np.isscalar(value) else value
            
            h = h_new
            h_history.append(h.copy())
    
    else:
        raise ValueError(f"未知的时间离散方法: {method}")
    
    return h_history


def compute_drawdown(
    h_history: List[np.ndarray],
    initial_h: np.ndarray
) -> List[np.ndarray]:
    """
    计算降落漏斗（drawdown）
    
    参数：
        h_history: List[np.ndarray]
            各时间步的水头分布
        initial_h: np.ndarray
            初始水头分布
    
    返回：
        drawdown_history: List[np.ndarray]
            各时间步的降深
    """
    drawdown_history = [initial_h - h for h in h_history]
    return drawdown_history
