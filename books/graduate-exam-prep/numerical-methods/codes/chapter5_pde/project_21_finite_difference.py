#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目15: 偏微分方程求解
案例：一维热传导方程（地下水温度）
"""
import numpy as np

def explicit_heat_1d(u0, alpha, dx, dt, nt):
    """显式差分法求解热传导方程"""
    nx = len(u0)
    u = np.copy(u0)
    r = alpha * dt / dx**2
    
    print(f"  稳定性参数 r = {r:.4f} (需要 r ≤ 0.5)")
    
    for n in range(nt):
        u_new = u.copy()
        for i in range(1, nx-1):
            u_new[i] = u[i] + r * (u[i+1] - 2*u[i] + u[i-1])
        u = u_new
    
    return u

def main():
    print("="*60)
    print("项目15: 偏微分方程求解")
    print("="*60)
    
    print("\n工程案例：地下水温度扩散")
    print("热传导方程：∂T/∂t = α·∂²T/∂x²")
    
    # 参数
    L = 10.0  # 长度
    nx = 21   # 空间节点数
    nt = 100  # 时间步数
    alpha = 0.01  # 热扩散系数
    dx = L / (nx - 1)
    dt = 0.01
    
    # 初始条件（阶跃函数）
    x = np.linspace(0, L, nx)
    u0 = np.zeros(nx)
    u0[nx//2:] = 20.0
    
    # 边界条件
    u0[0] = 0.0
    u0[-1] = 20.0
    
    print(f"\n初始温度分布:")
    print(f"  左边界: {u0[0]:.1f}°C")
    print(f"  右边界: {u0[-1]:.1f}°C")
    print(f"  初始跃变位置: x = {L/2:.1f}m")
    
    # 求解
    u_final = explicit_heat_1d(u0, alpha, dx, dt, nt)
    
    print(f"\n最终温度分布（t = {nt*dt:.2f}s）:")
    print(f"  中心温度: {u_final[nx//2]:.2f}°C")
    print(f"  温度梯度减小，趋于线性分布")
    
    print("\n✅ 项目15完成！")

if __name__ == "__main__":
    main()
