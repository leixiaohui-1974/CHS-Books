#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目10: SymPy符号计算
案例：水力学公式推导
"""
import sympy as sp

def main():
    print("="*60)
    print("项目10: SymPy符号计算 - 水力学公式推导")
    print("="*60)
    
    # 定义符号
    Q, v, A, b, h, g, H = sp.symbols('Q v A b h g H', positive=True, real=True)
    
    # 1. 连续性方程
    print("\n1. 连续性方程:")
    continuity = sp.Eq(Q, v * A)
    print(f"  {continuity}")
    
    # 求解流速
    v_solution = sp.solve(continuity, v)[0]
    print(f"  v = {v_solution}")
    
    # 2. Bernoulli方程
    print("\n2. Bernoulli方程:")
    z1, p1, v1, z2, p2, v2, rho = sp.symbols('z1 p1 v1 z2 p2 v2 rho')
    bernoulli = sp.Eq(z1 + p1/(rho*g) + v1**2/(2*g), 
                      z2 + p2/(rho*g) + v2**2/(2*g))
    print(f"  {bernoulli}")
    
    # 3. 矩形断面水力半径
    print("\n3. 矩形断面水力半径:")
    A_rect = b * h
    P_rect = b + 2 * h
    R = A_rect / P_rect
    print(f"  A = {A_rect}")
    print(f"  P = {P_rect}")
    print(f"  R = {sp.simplify(R)}")
    
    # 4. 临界水深
    print("\n4. 临界水深公式:")
    q = sp.Symbol('q', positive=True)  # 单宽流量
    hc = (q**2 / g) ** sp.Rational(1, 3)
    print(f"  hc = {hc}")
    
    # 5. 微积分应用 - 流量积分
    print("\n5. 流量积分:")
    x, v_max = sp.symbols('x v_max')
    # 假设流速分布: v(y) = v_max * (y/h)^(1/7)
    y = sp.Symbol('y')
    v_profile = v_max * (y/h) ** sp.Rational(1, 7)
    Q_integral = sp.integrate(v_profile * b, (y, 0, h))
    print(f"  v(y) = {v_profile}")
    print(f"  Q = ∫v(y)·b·dy = {Q_integral}")
    
    # 6. 方程求解
    print("\n6. 方程求解示例:")
    # Manning公式: v = (1/n) * R^(2/3) * i^(1/2)
    n, i, R_sym = sp.symbols('n i R_sym', positive=True)
    manning = sp.Eq(v, (1/n) * R_sym**(sp.Rational(2,3)) * i**(sp.Rational(1,2)))
    print(f"  Manning: {manning}")
    
    # 求解R
    R_solution = sp.solve(manning, R_sym)[0]
    print(f"  R = {R_solution}")
    
    print("\n✅ 项目10完成！")

if __name__ == "__main__":
    main()
