#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目1: 线性方程组直接求解法
项目11: 线性方程组求解

课程目标:
1. 掌握高斯消元法的实现
2. 理解LU分解原理
3. 学习主元选择策略
4. 应用于管网水力计算

工程案例:
供水管网节点水头计算

工程案例:
供水管网水力计算 - 求解节点水头

作者: Python编程实战教材组
日期: 2025-11-12
"""

import numpy as np

def gauss_elimination(A, b):
    """高斯消元法求解线性方程组"""
    n = len(b)
    A = A.astype(float)
    b = b.astype(float)
    
    # 前向消元
    for i in range(n):
        # 选主元
        max_row = i + np.argmax(np.abs(A[i:, i]))
        if max_row != i:
            A[[i, max_row]] = A[[max_row, i]]
            b[[i, max_row]] = b[[max_row, i]]
        
        # 消元
        for j in range(i+1, n):
            factor = A[j, i] / A[i, i]
            A[j, i:] -= factor * A[i, i:]
            b[j] -= factor * b[i]
    
    # 回代
    x = np.zeros(n)
    for i in range(n-1, -1, -1):
        x[i] = (b[i] - np.dot(A[i, i+1:], x[i+1:])) / A[i, i]
    
    return x


def lu_decomposition(A):
    """LU分解"""
    n = A.shape[0]
    L = np.eye(n)
    U = A.copy().astype(float)
    
    for i in range(n):
        for j in range(i+1, n):
            factor = U[j, i] / U[i, i]
            L[j, i] = factor
            U[j, i:] -= factor * U[i, i:]
    
    return L, U


def solve_lu(L, U, b):
    """用LU分解求解方程组"""
    n = len(b)
    
    # 前向替代求y (Ly = b)
    y = np.zeros(n)
    for i in range(n):
        y[i] = b[i] - np.dot(L[i, :i], y[:i])
    
    # 后向替代求x (Ux = y)
    x = np.zeros(n)
    for i in range(n-1, -1, -1):
        x[i] = (y[i] - np.dot(U[i, i+1:], x[i+1:])) / U[i, i]
    
    return x


def jacobi_iteration(A, b, x0=None, max_iter=100, tol=1e-6):
    """Jacobi迭代法"""
    n = len(b)
    if x0 is None:
        x0 = np.zeros(n)
    
    x = x0.copy()
    
    for k in range(max_iter):
        x_new = np.zeros(n)
        for i in range(n):
            s = np.dot(A[i, :], x) - A[i, i] * x[i]
            x_new[i] = (b[i] - s) / A[i, i]
        
        # 检查收敛
        if np.linalg.norm(x_new - x) < tol:
            print(f"  Jacobi收敛于第{k+1}次迭代")
            return x_new
        
        x = x_new
    
    print(f"  Jacobi未收敛，达到最大迭代次数{max_iter}")
    return x


def gauss_seidel(A, b, x0=None, max_iter=100, tol=1e-6):
    """Gauss-Seidel迭代法"""
    n = len(b)
    if x0 is None:
        x0 = np.zeros(n)
    
    x = x0.copy()
    
    for k in range(max_iter):
        x_old = x.copy()
        for i in range(n):
            s = np.dot(A[i, :i], x[:i]) + np.dot(A[i, i+1:], x[i+1:])
            x[i] = (b[i] - s) / A[i, i]
        
        # 检查收敛
        if np.linalg.norm(x - x_old) < tol:
            print(f"  Gauss-Seidel收敛于第{k+1}次迭代")
            return x
    
    print(f"  Gauss-Seidel未收敛，达到最大迭代次数{max_iter}")
    return x


def pipe_network_example():
    """工程案例：供水管网水力计算"""
    print("="*60)
    print("工程案例：供水管网节点水头计算")
    print("="*60)
    
    print("""
    管网拓扑：
         Q1=10    Q2=8     Q3=12
    1 ----→ 2 ----→ 3 ----→ 4
    H1=100  ↓       ↓       ↓
            Q4=5    Q5=6    Q6=7
    
    节点水量平衡方程（已知H1=100m）：
    节点2: -Q1 + Q2 + Q4 = 0
    节点3: -Q2 + Q3 + Q5 = 0
    节点4: -Q3 + Q6 = 0
    
    管道流量与水头损失关系：
    Qij = K * sqrt(Hi - Hj)  简化为线性
    """)
    
    # 简化的线性系统（系数矩阵）
    # 3个未知节点：H2, H3, H4
    A = np.array([
        [1.5, -0.5, 0],      # 节点2
        [-0.5, 1.8, -0.8],   # 节点3
        [0, -0.8, 1.5]       # 节点4
    ])
    
    b = np.array([85.0, 72.0, 50.0])  # 常数项
    
    print("\n系数矩阵A:")
    print(A)
    print("\n常数向量b:")
    print(b)
    
    # 方法1: 高斯消元
    print("\n" + "="*60)
    print("方法1: 高斯消元法")
    print("="*60)
    x_gauss = gauss_elimination(A.copy(), b.copy())
    print(f"\n节点水头:")
    print(f"  H2 = {x_gauss[0]:.2f} m")
    print(f"  H3 = {x_gauss[1]:.2f} m")
    print(f"  H4 = {x_gauss[2]:.2f} m")
    
    # 方法2: LU分解
    print("\n" + "="*60)
    print("方法2: LU分解")
    print("="*60)
    L, U = lu_decomposition(A)
    print("\nL矩阵:")
    print(L)
    print("\nU矩阵:")
    print(U)
    
    x_lu = solve_lu(L, U, b)
    print(f"\n节点水头:")
    print(f"  H2 = {x_lu[0]:.2f} m")
    print(f"  H3 = {x_lu[1]:.2f} m")
    print(f"  H4 = {x_lu[2]:.2f} m")
    
    # 方法3: Jacobi迭代
    print("\n" + "="*60)
    print("方法3: Jacobi迭代法")
    print("="*60)
    x_jacobi = jacobi_iteration(A, b)
    print(f"\n节点水头:")
    print(f"  H2 = {x_jacobi[0]:.2f} m")
    print(f"  H3 = {x_jacobi[1]:.2f} m")
    print(f"  H4 = {x_jacobi[2]:.2f} m")
    
    # 方法4: Gauss-Seidel迭代
    print("\n" + "="*60)
    print("方法4: Gauss-Seidel迭代法")
    print("="*60)
    x_gs = gauss_seidel(A, b)
    print(f"\n节点水头:")
    print(f"  H2 = {x_gs[0]:.2f} m")
    print(f"  H3 = {x_gs[1]:.2f} m")
    print(f"  H4 = {x_gs[2]:.2f} m")
    
    # 验证
    print("\n" + "="*60)
    print("结果验证")
    print("="*60)
    residual = np.dot(A, x_gauss) - b
    print(f"残差（Ax - b）:")
    print(residual)
    print(f"残差范数: {np.linalg.norm(residual):.2e}")
    
    # 计算管道流量
    print("\n管道流量计算:")
    H1 = 100.0
    H2, H3, H4 = x_gauss
    print(f"  Q12 = f(H1-H2) = f({H1:.1f}-{H2:.2f}) ≈ {(H1-H2)*0.5:.2f} m³/s")
    print(f"  Q23 = f(H2-H3) = f({H2:.2f}-{H3:.2f}) ≈ {(H2-H3)*0.5:.2f} m³/s")
    print(f"  Q34 = f(H3-H4) = f({H3:.2f}-{H4:.2f}) ≈ {(H3-H4)*0.5:.2f} m³/s")


def main():
    """主函数"""
    print("╔" + "═"*58 + "╗")
    print("║" + " "*16 + "线性方程组求解" + " "*18 + "║")
    print("║" + " "*13 + "案例：供水管网水力计算" + " "*14 + "║")
    print("╚" + "═"*58 + "╝")
    
    # 简单示例
    print("\n" + "="*60)
    print("简单示例：3×3方程组")
    print("="*60)
    
    A = np.array([
        [3, 2, 1],
        [2, 3, 2],
        [1, 2, 3]
    ], dtype=float)
    
    b = np.array([10, 14, 14], dtype=float)
    
    print("\n方程组: Ax = b")
    print("A =")
    print(A)
    print("\nb =")
    print(b)
    
    # 求解
    x = gauss_elimination(A.copy(), b.copy())
    print("\n解: x =")
    print(x)
    print(f"\nx1 = {x[0]:.4f}")
    print(f"x2 = {x[1]:.4f}")
    print(f"x3 = {x[2]:.4f}")
    
    # 工程案例
    pipe_network_example()
    
    print("\n" + "="*60)
    print("项目11完成！")
    print("="*60)


if __name__ == "__main__":
    main()
