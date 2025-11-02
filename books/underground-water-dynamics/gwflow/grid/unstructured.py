"""
unstructured.py - 非结构化网格生成
=====================================

提供三角形网格生成功能（简化版本）。
"""

import numpy as np
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class TriangularMesh:
    """三角形网格数据结构"""
    vertices: np.ndarray  # 顶点坐标 (n_vertices, 2)
    elements: np.ndarray  # 单元连接 (n_elements, 3)
    boundary_edges: np.ndarray  # 边界边 (n_boundary_edges, 2)
    
    @property
    def n_vertices(self) -> int:
        return len(self.vertices)
    
    @property
    def n_elements(self) -> int:
        return len(self.elements)


def generate_rectangular_triangular_mesh(
    Lx: float,
    Ly: float,
    nx: int,
    ny: int
) -> TriangularMesh:
    """
    生成矩形区域的结构化三角形网格
    
    参数：
        Lx: x方向长度 [m]
        Ly: y方向长度 [m]
        nx: x方向节点数
        ny: y方向节点数
    
    返回：
        mesh: 三角形网格对象
    
    示例：
        >>> mesh = generate_rectangular_triangular_mesh(100, 80, 11, 9)
        >>> print(f"顶点数: {mesh.n_vertices}, 单元数: {mesh.n_elements}")
    """
    if nx < 2 or ny < 2:
        raise ValueError("节点数必须至少为2")
    
    # 生成顶点
    x = np.linspace(0, Lx, nx)
    y = np.linspace(0, Ly, ny)
    X, Y = np.meshgrid(x, y)
    
    vertices = np.column_stack([X.ravel(), Y.ravel()])
    
    # 生成单元（每个矩形格子分为两个三角形）
    elements = []
    
    for j in range(ny - 1):
        for i in range(nx - 1):
            # 矩形的四个角点索引
            v0 = j * nx + i
            v1 = j * nx + (i + 1)
            v2 = (j + 1) * nx + (i + 1)
            v3 = (j + 1) * nx + i
            
            # 第一个三角形 (v0, v1, v3)
            elements.append([v0, v1, v3])
            # 第二个三角形 (v1, v2, v3)
            elements.append([v1, v2, v3])
    
    elements = np.array(elements, dtype=int)
    
    # 生成边界边
    boundary_edges = []
    
    # 下边界
    for i in range(nx - 1):
        boundary_edges.append([i, i + 1])
    
    # 右边界
    for j in range(ny - 1):
        v0 = j * nx + (nx - 1)
        v1 = (j + 1) * nx + (nx - 1)
        boundary_edges.append([v0, v1])
    
    # 上边界
    for i in range(nx - 1):
        v0 = (ny - 1) * nx + (nx - 1 - i)
        v1 = (ny - 1) * nx + (nx - 2 - i)
        boundary_edges.append([v0, v1])
    
    # 左边界
    for j in range(ny - 1):
        v0 = (ny - 1 - j) * nx
        v1 = (ny - 2 - j) * nx
        boundary_edges.append([v0, v1])
    
    boundary_edges = np.array(boundary_edges, dtype=int)
    
    return TriangularMesh(vertices, elements, boundary_edges)


def compute_element_area(vertices: np.ndarray, element: np.ndarray) -> float:
    """
    计算三角形单元面积
    
    使用向量叉积公式：
    Area = 0.5 * |AB × AC|
    
    参数：
        vertices: 网格顶点坐标
        element: 单元节点索引 [v0, v1, v2]
    
    返回：
        area: 单元面积
    """
    v0, v1, v2 = element
    p0 = vertices[v0]
    p1 = vertices[v1]
    p2 = vertices[v2]
    
    # 向量AB和AC
    AB = p1 - p0
    AC = p2 - p0
    
    # 叉积（在2D中等于z分量）
    cross = AB[0] * AC[1] - AB[1] * AC[0]
    
    area = 0.5 * abs(cross)
    
    return area


def compute_shape_functions(
    xi: float,
    eta: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    计算线性三角形单元的形函数及其导数
    
    参考单元坐标系：
        (0, 0) - (1, 0) - (0, 1)
    
    形函数：
        N1 = 1 - xi - eta
        N2 = xi
        N3 = eta
    
    参数：
        xi, eta: 参考单元坐标
    
    返回：
        N: 形函数值 [N1, N2, N3]
        dN: 形函数导数 [[dN1/dxi, dN1/deta],
                       [dN2/dxi, dN2/deta],
                       [dN3/dxi, dN3/deta]]
    """
    # 形函数
    N = np.array([
        1 - xi - eta,
        xi,
        eta
    ])
    
    # 形函数在参考单元中的导数
    dN = np.array([
        [-1, -1],
        [1, 0],
        [0, 1]
    ])
    
    return N, dN


def compute_element_quality(vertices: np.ndarray, element: np.ndarray) -> float:
    """
    计算三角形单元质量
    
    质量指标：最小角度（度）
    
    参数：
        vertices: 网格顶点坐标
        element: 单元节点索引
    
    返回：
        quality: 最小角度（度）
    """
    v0, v1, v2 = element
    p0 = vertices[v0]
    p1 = vertices[v1]
    p2 = vertices[v2]
    
    # 计算三条边长
    a = np.linalg.norm(p1 - p2)  # 对面边
    b = np.linalg.norm(p2 - p0)
    c = np.linalg.norm(p0 - p1)
    
    # 使用余弦定理计算三个角
    angle0 = np.arccos((b**2 + c**2 - a**2) / (2 * b * c))
    angle1 = np.arccos((a**2 + c**2 - b**2) / (2 * a * c))
    angle2 = np.arccos((a**2 + b**2 - c**2) / (2 * a * b))
    
    # 转换为度并返回最小角
    angles_deg = np.array([angle0, angle1, angle2]) * 180 / np.pi
    
    return np.min(angles_deg)


def plot_mesh(mesh: TriangularMesh, ax=None):
    """
    绘制三角形网格
    
    参数：
        mesh: 三角形网格对象
        ax: matplotlib轴对象（可选）
    """
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    
    # 绘制所有三角形边
    edges = []
    for elem in mesh.elements:
        edges.append([mesh.vertices[elem[0]], mesh.vertices[elem[1]]])
        edges.append([mesh.vertices[elem[1]], mesh.vertices[elem[2]]])
        edges.append([mesh.vertices[elem[2]], mesh.vertices[elem[0]]])
    
    lc = LineCollection(edges, colors='gray', linewidths=0.5, alpha=0.5)
    ax.add_collection(lc)
    
    # 绘制边界边（加粗）
    boundary_edges = []
    for edge in mesh.boundary_edges:
        boundary_edges.append([mesh.vertices[edge[0]], mesh.vertices[edge[1]]])
    
    lc_boundary = LineCollection(boundary_edges, colors='blue', linewidths=2)
    ax.add_collection(lc_boundary)
    
    # 绘制顶点
    ax.plot(mesh.vertices[:, 0], mesh.vertices[:, 1], 'ko', markersize=3)
    
    ax.set_xlabel('x (m)', fontsize=12)
    ax.set_ylabel('y (m)', fontsize=12)
    ax.set_title('三角形网格', fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    return ax
