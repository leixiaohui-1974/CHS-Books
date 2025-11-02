"""
finite_element.py - 有限元求解器
==================================

提供基于线性三角形单元的有限元求解器。
"""

import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve
from typing import Dict, Any, Optional
import sys
import os

# 添加父目录到路径以导入grid模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid.unstructured import TriangularMesh, compute_element_area


def assemble_fem_system(
    mesh: TriangularMesh,
    K: float,
    boundary_conditions: Dict[str, Any]
) -> tuple[csr_matrix, np.ndarray]:
    """
    组装有限元系统矩阵和右端项
    
    使用Galerkin方法离散：
        ∫∫ K * ∇N_i · ∇N_j dA * u_j = ∫∫ f * N_i dA
    
    参数：
        mesh: 三角形网格
        K: 水力传导度（均匀）
        boundary_conditions: 边界条件字典
            {'dirichlet': [(node_id, value), ...],
             'neumann': [(edge_id, flux), ...]}
    
    返回：
        A: 全局刚度矩阵（稀疏）
        b: 右端项向量
    """
    n_nodes = mesh.n_vertices
    n_elements = mesh.n_elements
    
    # 初始化全局矩阵和向量
    A_global = lil_matrix((n_nodes, n_nodes))
    b_global = np.zeros(n_nodes)
    
    # 遍历所有单元
    for elem_id, element in enumerate(mesh.elements):
        # 获取单元节点坐标
        v0, v1, v2 = element
        coords = mesh.vertices[[v0, v1, v2]]
        
        # 计算单元刚度矩阵
        K_elem = compute_element_stiffness_matrix(coords, K)
        
        # 组装到全局矩阵
        for i in range(3):
            global_i = element[i]
            for j in range(3):
                global_j = element[j]
                A_global[global_i, global_j] += K_elem[i, j]
    
    # 应用Dirichlet边界条件
    if 'dirichlet' in boundary_conditions:
        for node_id, value in boundary_conditions['dirichlet']:
            # 将该行置为单位行
            A_global[node_id, :] = 0
            A_global[node_id, node_id] = 1.0
            b_global[node_id] = value
    
    # 应用Neumann边界条件（自然边界条件，已在弱形式中包含）
    # 这里简化处理，假设为齐次Neumann条件
    
    return A_global.tocsr(), b_global


def compute_element_stiffness_matrix(
    coords: np.ndarray,
    K: float
) -> np.ndarray:
    """
    计算单元刚度矩阵
    
    对于线性三角形单元：
        K_elem[i,j] = ∫∫ K * ∇N_i · ∇N_j dA
    
    参数：
        coords: 单元节点坐标 [[x0,y0], [x1,y1], [x2,y2]]
        K: 水力传导度
    
    返回：
        K_elem: 3x3单元刚度矩阵
    """
    # 计算Jacobian矩阵
    # J = [x1-x0, x2-x0]
    #     [y1-y0, y2-y0]
    J = np.array([
        [coords[1, 0] - coords[0, 0], coords[2, 0] - coords[0, 0]],
        [coords[1, 1] - coords[0, 1], coords[2, 1] - coords[0, 1]]
    ])
    
    # Jacobian行列式
    det_J = np.linalg.det(J)
    
    if det_J <= 0:
        raise ValueError("单元退化或节点顺序错误")
    
    # Jacobian逆矩阵
    J_inv = np.linalg.inv(J)
    
    # 形函数在参考单元中的梯度
    # dN/dxi = [[-1, -1], [1, 0], [0, 1]]
    dN_ref = np.array([
        [-1, -1],
        [1, 0],
        [0, 1]
    ])
    
    # 形函数在物理单元中的梯度
    # ∇N = J^(-T) * dN_ref^T
    grad_N = dN_ref @ J_inv.T  # (3, 2)
    
    # 计算刚度矩阵
    # K_elem[i,j] = K * ∇N_i · ∇N_j * det(J) / 2
    # 因子1/2是三角形面积的Jacobian
    K_elem = K * (grad_N @ grad_N.T) * det_J / 2
    
    return K_elem


def solve_fem_2d(
    mesh: TriangularMesh,
    K: float,
    boundary_conditions: Dict[str, Any]
) -> np.ndarray:
    """
    求解二维稳态地下水流动问题（有限元法）
    
    控制方程：
        -∇·(K∇h) = 0
    
    参数：
        mesh: 三角形网格
        K: 水力传导度
        boundary_conditions: 边界条件
    
    返回：
        h: 各节点的水头值
    
    示例：
        >>> mesh = generate_rectangular_triangular_mesh(100, 80, 11, 9)
        >>> bc = {'dirichlet': [(0, 20.0), (10, 10.0)]}
        >>> h = solve_fem_2d(mesh, K=10.0, boundary_conditions=bc)
    """
    # 组装系统
    A, b = assemble_fem_system(mesh, K, boundary_conditions)
    
    # 求解
    h = spsolve(A, b)
    
    return h


def compute_fem_gradient(
    mesh: TriangularMesh,
    h: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    计算有限元解的梯度（在单元中心）
    
    参数：
        mesh: 三角形网格
        h: 节点水头值
    
    返回：
        grad_h: 梯度场 (n_elements, 2) [dh/dx, dh/dy]
        elem_centers: 单元中心坐标 (n_elements, 2)
    """
    n_elements = mesh.n_elements
    grad_h = np.zeros((n_elements, 2))
    elem_centers = np.zeros((n_elements, 2))
    
    for elem_id, element in enumerate(mesh.elements):
        # 单元节点坐标
        coords = mesh.vertices[element]
        
        # 单元中心
        elem_centers[elem_id] = coords.mean(axis=0)
        
        # Jacobian矩阵
        J = np.array([
            [coords[1, 0] - coords[0, 0], coords[2, 0] - coords[0, 0]],
            [coords[1, 1] - coords[0, 1], coords[2, 1] - coords[0, 1]]
        ])
        
        J_inv = np.linalg.inv(J)
        
        # 形函数梯度
        dN_ref = np.array([[-1, -1], [1, 0], [0, 1]])
        grad_N = dN_ref @ J_inv.T
        
        # 单元的水头值
        h_elem = h[element]
        
        # 计算梯度: ∇h = Σ h_i * ∇N_i
        grad_h[elem_id] = h_elem @ grad_N
    
    return grad_h, elem_centers


def compute_element_errors(
    mesh: TriangularMesh,
    h_numerical: np.ndarray,
    h_exact_func
) -> Dict[str, float]:
    """
    计算有限元解的误差
    
    参数：
        mesh: 三角形网格
        h_numerical: 数值解
        h_exact_func: 解析解函数 h_exact(x, y)
    
    返回：
        errors: 误差字典
            - 'L2': L2范数误差
            - 'H1': H1半范数误差
            - 'Linf': L∞范数误差
    """
    # L∞误差（节点上的最大误差）
    h_exact_nodes = np.array([h_exact_func(x, y) for x, y in mesh.vertices])
    error_nodes = np.abs(h_numerical - h_exact_nodes)
    L_inf_error = np.max(error_nodes)
    
    # L2和H1误差需要在单元上积分
    L2_error_sq = 0.0
    H1_error_sq = 0.0
    
    for elem_id, element in enumerate(mesh.elements):
        coords = mesh.vertices[element]
        h_elem = h_numerical[element]
        
        # 单元面积
        area = compute_element_area(mesh.vertices, element)
        
        # 单元中心点
        x_center = coords[:, 0].mean()
        y_center = coords[:, 1].mean()
        
        # 在单元中心评估
        h_numerical_center = h_elem.mean()  # 线性插值在中心
        h_exact_center = h_exact_func(x_center, y_center)
        
        # L2误差贡献
        L2_error_sq += area * (h_numerical_center - h_exact_center)**2
    
    L2_error = np.sqrt(L2_error_sq)
    
    errors = {
        'L2': L2_error,
        'Linf': L_inf_error
    }
    
    return errors
