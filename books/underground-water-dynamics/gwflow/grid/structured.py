"""
structured.py - 结构化网格生成
================================

提供一维、二维和三维结构化网格生成功能。
"""

import numpy as np
from typing import Tuple, Optional


def create_1d_grid(L: float, nx: int) -> Tuple[np.ndarray, float]:
    """
    创建一维均匀网格
    
    参数：
        L: float
            区域长度 [m]
        nx: int
            网格数量
    
    返回：
        x: np.ndarray
            网格节点坐标 [m]
        dx: float
            网格间距 [m]
    
    示例：
        >>> x, dx = create_1d_grid(L=1000.0, nx=50)
        >>> print(f"Grid spacing: {dx:.2f} m")
    """
    if nx < 2:
        raise ValueError("网格数量必须至少为2")
    if L <= 0:
        raise ValueError("区域长度必须大于0")
    
    x = np.linspace(0, L, nx)
    dx = L / (nx - 1)
    
    return x, dx


def create_2d_grid(
    Lx: float, 
    Ly: float, 
    nx: int, 
    ny: int
) -> Tuple[np.ndarray, np.ndarray, float, float]:
    """
    创建二维均匀矩形网格
    
    参数：
        Lx: float
            x方向区域长度 [m]
        Ly: float
            y方向区域长度 [m]
        nx: int
            x方向网格数量
        ny: int
            y方向网格数量
    
    返回：
        X: np.ndarray, shape (ny, nx)
            x坐标网格 [m]
        Y: np.ndarray, shape (ny, nx)
            y坐标网格 [m]
        dx: float
            x方向网格间距 [m]
        dy: float
            y方向网格间距 [m]
    
    示例：
        >>> X, Y, dx, dy = create_2d_grid(Lx=1000.0, Ly=800.0, nx=50, ny=40)
        >>> print(f"Grid spacing: dx={dx:.2f} m, dy={dy:.2f} m")
    """
    if nx < 2 or ny < 2:
        raise ValueError("网格数量必须至少为2")
    if Lx <= 0 or Ly <= 0:
        raise ValueError("区域尺寸必须大于0")
    
    x = np.linspace(0, Lx, nx)
    y = np.linspace(0, Ly, ny)
    X, Y = np.meshgrid(x, y)
    
    dx = Lx / (nx - 1)
    dy = Ly / (ny - 1)
    
    return X, Y, dx, dy


def create_3d_grid(
    Lx: float,
    Ly: float,
    Lz: float,
    nx: int,
    ny: int,
    nz: int
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float, float, float]:
    """
    创建三维均匀长方体网格
    
    参数：
        Lx: float
            x方向区域长度 [m]
        Ly: float
            y方向区域长度 [m]
        Lz: float
            z方向区域长度（深度）[m]
        nx: int
            x方向网格数量
        ny: int
            y方向网格数量
        nz: int
            z方向网格数量
    
    返回：
        X: np.ndarray, shape (nz, ny, nx)
            x坐标网格 [m]
        Y: np.ndarray, shape (nz, ny, nx)
            y坐标网格 [m]
        Z: np.ndarray, shape (nz, ny, nx)
            z坐标网格（深度）[m]
        dx: float
            x方向网格间距 [m]
        dy: float
            y方向网格间距 [m]
        dz: float
            z方向网格间距 [m]
    
    示例：
        >>> X, Y, Z, dx, dy, dz = create_3d_grid(
        ...     Lx=1000.0, Ly=800.0, Lz=50.0, 
        ...     nx=50, ny=40, nz=10
        ... )
    """
    if nx < 2 or ny < 2 or nz < 2:
        raise ValueError("网格数量必须至少为2")
    if Lx <= 0 or Ly <= 0 or Lz <= 0:
        raise ValueError("区域尺寸必须大于0")
    
    x = np.linspace(0, Lx, nx)
    y = np.linspace(0, Ly, ny)
    z = np.linspace(0, Lz, nz)
    
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    X = np.transpose(X, (2, 1, 0))  # 转换为 (nz, ny, nx)
    Y = np.transpose(Y, (2, 1, 0))
    Z = np.transpose(Z, (2, 1, 0))
    
    dx = Lx / (nx - 1)
    dy = Ly / (ny - 1)
    dz = Lz / (nz - 1)
    
    return X, Y, Z, dx, dy, dz


def refine_grid_2d(
    X: np.ndarray,
    Y: np.ndarray,
    refinement_factor: int = 2
) -> Tuple[np.ndarray, np.ndarray]:
    """
    对二维网格进行加密
    
    参数：
        X: np.ndarray
            原始x坐标网格
        Y: np.ndarray
            原始y坐标网格
        refinement_factor: int
            加密因子（每个网格单元分割为 factor x factor 个子网格）
    
    返回：
        X_refined: np.ndarray
            加密后的x坐标网格
        Y_refined: np.ndarray
            加密后的y坐标网格
    """
    from scipy.interpolate import interp2d
    
    ny, nx = X.shape
    Lx = X[0, -1]
    Ly = Y[-1, 0]
    
    nx_new = (nx - 1) * refinement_factor + 1
    ny_new = (ny - 1) * refinement_factor + 1
    
    x_new = np.linspace(0, Lx, nx_new)
    y_new = np.linspace(0, Ly, ny_new)
    
    X_refined, Y_refined = np.meshgrid(x_new, y_new)
    
    return X_refined, Y_refined
