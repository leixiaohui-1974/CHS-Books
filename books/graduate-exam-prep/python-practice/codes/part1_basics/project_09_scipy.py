#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目9: SciPy科学计算
案例：水面线插值与拟合
"""
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import fsolve, minimize_scalar

def main():
    print("="*60)
    print("项目9: SciPy科学计算 - 水面线插值")
    print("="*60)
    
    # 1. 插值
    x_data = np.array([0, 100, 200, 300, 400, 500])
    z_data = np.array([100.0, 98.5, 97.2, 96.1, 95.3, 94.8])
    
    f_linear = interp1d(x_data, z_data, kind='linear')
    f_cubic = interp1d(x_data, z_data, kind='cubic')
    
    x_new = np.array([50, 150, 250, 350, 450])
    z_linear = f_linear(x_new)
    z_cubic = f_cubic(x_new)
    
    print("\n插值结果:")
    for i in range(len(x_new)):
        print(f"  x={x_new[i]}m: 线性={z_linear[i]:.2f}m, 三次={z_cubic[i]:.2f}m")
    
    # 2. 方程求解 - Manning公式
    def manning_equation(h):
        """Manning方程: Q = (1/n) * A * R^(2/3) * sqrt(i)"""
        n, b, i, Q_target = 0.025, 10.0, 0.001, 50.0
        A = b * h
        P = b + 2 * h
        R = A / P
        Q = (1/n) * A * (R**(2/3)) * (i**0.5)
        return Q - Q_target
    
    h_solution = fsolve(manning_equation, 3.0)[0]
    print(f"\nManning方程求解:")
    print(f"  目标流量: 50 m³/s")
    print(f"  所需水深: {h_solution:.3f} m")
    
    # 3. 优化 - 最优断面
    def hydraulic_radius(b_h_ratio):
        """给定断面积，求最大水力半径的宽深比"""
        A = 100  # 给定断面积
        b = (A * b_h_ratio) ** 0.5
        h = A / b
        P = b + 2 * h
        R = A / P
        return -R  # 求最大值，返回负值
    
    result = minimize_scalar(hydraulic_radius, bounds=(1, 10), method='bounded')
    optimal_ratio = result.x
    
    print(f"\n最优断面设计:")
    print(f"  给定断面积: 100 m²")
    print(f"  最优宽深比: {optimal_ratio:.2f}")
    
    print("\n✅ 项目9完成！")

if __name__ == "__main__":
    main()
