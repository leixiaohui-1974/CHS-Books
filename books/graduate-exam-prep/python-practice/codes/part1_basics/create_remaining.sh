#!/bin/bash

# 项目8: Pandas
cat > project_08_pandas.py << 'PYEOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目8: Pandas数据处理
案例：水质监测数据分析
"""
import pandas as pd
import numpy as np

def main():
    print("="*60)
    print("项目8: Pandas数据处理 - 水质监测分析")
    print("="*60)
    
    # 创建数据
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    data = {
        '日期': dates,
        '水温(°C)': np.random.uniform(10, 25, 30),
        'pH值': np.random.uniform(6.5, 8.5, 30),
        '溶解氧(mg/L)': np.random.uniform(5, 10, 30),
        'COD(mg/L)': np.random.uniform(10, 30, 30)
    }
    df = pd.DataFrame(data)
    
    print("\n水质数据（前5行）:")
    print(df.head())
    
    print("\n统计描述:")
    print(df.describe())
    
    print("\n相关性分析:")
    print(df[['水温(°C)', 'pH值', '溶解氧(mg/L)', 'COD(mg/L)']].corr())
    
    # 水质评价
    df['水质等级'] = pd.cut(df['COD(mg/L)'], 
                           bins=[0, 15, 20, 30, 100],
                           labels=['优', '良', '中', '差'])
    
    print("\n水质等级分布:")
    print(df['水质等级'].value_counts())
    
    print("\n✅ 项目8完成！")

if __name__ == "__main__":
    main()
PYEOF

# 项目9: SciPy
cat > project_09_scipy.py << 'PYEOF'
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
PYEOF

# 项目10: SymPy
cat > project_10_sympy.py << 'PYEOF'
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
PYEOF

echo "✅ Pandas, SciPy, SymPy项目创建完成"
