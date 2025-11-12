#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目14: 常微分方程求解
案例：水库调洪演算
"""
import numpy as np

def euler(f, y0, t):
    """Euler法"""
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(len(t) - 1):
        dt = t[i+1] - t[i]
        y[i+1] = y[i] + dt * f(t[i], y[i])
    return y

def runge_kutta_4(f, y0, t):
    """四阶Runge-Kutta法"""
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(len(t) - 1):
        dt = t[i+1] - t[i]
        k1 = f(t[i], y[i])
        k2 = f(t[i] + dt/2, y[i] + dt*k1/2)
        k3 = f(t[i] + dt/2, y[i] + dt*k2/2)
        k4 = f(t[i] + dt, y[i] + dt*k3)
        y[i+1] = y[i] + dt * (k1 + 2*k2 + 2*k3 + k4) / 6
    return y

def main():
    print("="*60)
    print("项目14: 常微分方程求解")
    print("="*60)
    
    print("\n工程案例：水库调洪演算")
    print("水量平衡方程：dV/dt = I(t) - Q(t)")
    
    # 简化：假设入流过程和出流与水位关系
    def reservoir_balance(t, V):
        # 入流（三角形洪水过程）
        if t < 12:
            I = 1000 + 2000 * (t / 12)
        else:
            I = 3000 - 2000 * ((t - 12) / 12)
        
        # 出流（简化为水位的函数）
        Q = 500 + 0.1 * V
        
        return I - Q
    
    # 时间序列
    t = np.linspace(0, 24, 100)
    V0 = 10000  # 初始库容
    
    # Euler法
    V_euler = euler(reservoir_balance, V0, t)
    
    # RK4法
    V_rk4 = runge_kutta_4(reservoir_balance, V0, t)
    
    print(f"\n初始库容: {V0} m³")
    print(f"最大库容（Euler）: {np.max(V_euler):.0f} m³")
    print(f"最大库容（RK4）: {np.max(V_rk4):.0f} m³")
    print(f"最终库容（RK4）: {V_rk4[-1]:.0f} m³")
    
    print("\n✅ 项目14完成！")

if __name__ == "__main__":
    main()
