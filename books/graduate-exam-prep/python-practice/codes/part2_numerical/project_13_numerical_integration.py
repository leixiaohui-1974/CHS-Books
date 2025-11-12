#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目13: 数值积分
案例：水库库容计算
"""
import numpy as np

def trapezoidal(f, a, b, n):
    """梯形法则"""
    h = (b - a) / n
    x = np.linspace(a, b, n+1)
    y = f(x)
    integral = h * (0.5*y[0] + np.sum(y[1:-1]) + 0.5*y[-1])
    return integral

def simpson(f, a, b, n):
    """Simpson法则"""
    if n % 2 == 1:
        n += 1
    h = (b - a) / n
    x = np.linspace(a, b, n+1)
    y = f(x)
    integral = h/3 * (y[0] + 4*np.sum(y[1:-1:2]) + 2*np.sum(y[2:-1:2]) + y[-1])
    return integral

def main():
    print("="*60)
    print("项目13: 数值积分")
    print("="*60)
    
    print("\n工程案例：水库库容计算")
    print("已知水库断面面积与高程关系，求库容")
    
    # 断面积-高程关系（简化为多项式）
    def area(z):
        return 1000 + 500 * z + 10 * z**2
    
    z_min, z_max = 100, 150
    
    # 梯形法
    V_trap = trapezoidal(area, z_min, z_max, 50)
    print(f"\n梯形法（n=50）: V = {V_trap/1e6:.2f}百万m³")
    
    # Simpson法
    V_simp = simpson(area, z_min, z_max, 50)
    print(f"Simpson法（n=50）: V = {V_simp/1e6:.2f}百万m³")
    
    # 精确解（可计算）
    V_exact = (1000*(z_max-z_min) + 250*(z_max**2-z_min**2) + 
               10/3*(z_max**3-z_min**3))
    print(f"精确解: V = {V_exact/1e6:.2f}百万m³")
    
    print("\n✅ 项目13完成！")

if __name__ == "__main__":
    main()
