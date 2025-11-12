#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目12: 非线性方程求解
案例：Manning公式隐式求解
"""
import numpy as np

def bisection(f, a, b, tol=1e-6):
    """二分法"""
    while abs(b - a) > tol:
        c = (a + b) / 2
        if f(a) * f(c) < 0:
            b = c
        else:
            a = c
    return (a + b) / 2

def newton_raphson(f, df, x0, max_iter=100, tol=1e-6):
    """牛顿法"""
    x = x0
    for i in range(max_iter):
        fx = f(x)
        if abs(fx) < tol:
            print(f"  牛顿法收敛于第{i+1}次迭代")
            return x
        x = x - fx / df(x)
    return x

def secant(f, x0, x1, max_iter=100, tol=1e-6):
    """割线法"""
    for i in range(max_iter):
        fx0, fx1 = f(x0), f(x1)
        if abs(fx1) < tol:
            print(f"  割线法收敛于第{i+1}次迭代")
            return x1
        x_new = x1 - fx1 * (x1 - x0) / (fx1 - fx0)
        x0, x1 = x1, x_new
    return x1

def main():
    print("="*60)
    print("项目12: 非线性方程求解")
    print("="*60)
    
    # Manning方程求解水深
    print("\n工程案例：Manning公式求解水深")
    print("给定：Q=50m³/s, b=10m, i=0.001, n=0.025")
    print("求解：h (水深)")
    
    Q, b, i, n = 50.0, 10.0, 0.001, 0.025
    
    def manning_eq(h):
        A = b * h
        P = b + 2 * h
        R = A / P
        Q_calc = (1/n) * A * (R**(2/3)) * (i**0.5)
        return Q_calc - Q
    
    def manning_derivative(h):
        eps = 1e-6
        return (manning_eq(h + eps) - manning_eq(h)) / eps
    
    # 二分法
    h_bisect = bisection(manning_eq, 0.5, 5.0)
    print(f"\n二分法: h = {h_bisect:.4f} m")
    
    # 牛顿法
    h_newton = newton_raphson(manning_eq, manning_derivative, 3.0)
    print(f"牛顿法: h = {h_newton:.4f} m")
    
    # 割线法
    h_secant = secant(manning_eq, 2.0, 4.0)
    print(f"割线法: h = {h_secant:.4f} m")
    
    print("\n✅ 项目12完成！")

if __name__ == "__main__":
    main()
